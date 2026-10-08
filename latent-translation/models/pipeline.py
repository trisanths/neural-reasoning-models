"""Full end-to-end pipeline for latent-space translation between models.

Orchestrates: small model extraction -> adapter S->L -> large model Coconut
loop -> adapter L->S -> small model decoding.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Dict, Tuple
from config import PipelineConfig, resolve_module
from models.hooks import HiddenStateCapture, HiddenStateInjector
from models.adapters import AdapterPair
from models.coconut_loop import CoconutTailLoop


class LatentTranslationPipeline(nn.Module):
    """The complete cross-model latent-space translation pipeline.

    Both language models are frozen.  Only the AdapterPair is trainable.
    """

    def __init__(
        self,
        small_model: nn.Module,
        large_model: nn.Module,
        small_tokenizer,
        large_tokenizer,
        adapter_pair: AdapterPair,
        config: PipelineConfig,
    ):
        super().__init__()
        # DESIGN DECISION: Store the frozen models in a plain dict to avoid
        # registering them as nn.Module submodules (which would bloat
        # state_dict and double-count parameters).  Only adapter_pair is
        # registered as a proper submodule since it has trainable params.
        self._models = {
            "small": small_model,
            "large": large_model,
        }
        self.small_tokenizer = small_tokenizer
        self.large_tokenizer = large_tokenizer
        self.adapter_pair = adapter_pair
        self.config = config

        # Freeze both models
        for param in small_model.parameters():
            param.requires_grad = False
        for param in large_model.parameters():
            param.requires_grad = False

        # Set up hooks on the small model
        # Extract from the last transformer block (0-based: extract_layer - 1)
        small_extract_idx = config.small_extract_layer - 1
        small_layer = resolve_module(
            small_model, config.small_model.layer_template.format(i=small_extract_idx)
        )
        self._small_capture = HiddenStateCapture().register(small_layer)

        # Injector for returning the translated state to the small model
        self._small_injector = HiddenStateInjector(mode=config.injection_mode)
        self._small_injector.register(small_layer)

        # DESIGN DECISION: Store resolved module references in a plain dict
        # (not as direct attributes) to avoid nn.Module.__setattr__ registering
        # them as submodules, which would bloat state_dict with the frozen
        # model's weights.  Access via self._ref["key"].
        small_tail_start = config.small_extract_layer - 1  # 0-based
        self._small_tail_indices = list(
            range(small_tail_start + 1, config.small_model.num_layers)
        )
        # After extracting at layer 24 (block index 23), the remaining small
        # model layers are index 24+ (none for a 24-layer model).  Only final
        # norm + LM head remain.  This is correct: the small model's full
        # representation is captured, sent to the large model for reasoning,
        # then only the final projection back to vocabulary space happens.
        self._ref = {
            "small_norm": resolve_module(small_model, config.small_model.norm_path),
            "small_lm_head": resolve_module(small_model, config.small_model.lm_head_path),
            "small_embed": resolve_module(small_model, config.small_model.embed_path),
            "small_layers": resolve_module(small_model, config.small_model.layers_path),
        }

        # Coconut loop for the large model (plain class, not nn.Module)
        self.coconut_loop = CoconutTailLoop(
            large_model=large_model,
            large_config=config.large_model,
            inject_layer=config.large_inject_layer,
            num_iters=config.coconut_num_iters,
            full_loop=config.coconut_full_loop,
        )

    @property
    def small_model(self):
        return self._models["small"]

    @property
    def large_model(self):
        return self._models["large"]

    def forward(
        self,
        input_ids_small: torch.Tensor,
        attention_mask_small: torch.Tensor,
        input_ids_large: torch.Tensor,
        attention_mask_large: torch.Tensor,
        labels: Optional[torch.Tensor] = None,
    ) -> Dict[str, torch.Tensor]:
        """Full forward pass through the pipeline.

        Args:
            input_ids_small: tokenized input for the small model
            attention_mask_small: attention mask for the small model
            input_ids_large: tokenized input for the large model (same text,
                             different tokenizer)
            attention_mask_large: attention mask for the large model
            labels: token-level labels for computing answer loss (optional)

        Returns:
            Dict with keys:
              - logits: (batch, seq, vocab) output logits from the small model
              - h_small: hidden state extracted from the small model (for cycle loss)
              - h_translated: S->L translated hidden state (for alignment loss)
              - h_final_large: final hidden state from the Coconut loop
              - h_reconstructed: L->S translated hidden state
        """
        # ── Step 1: Run small model, extract hidden state at splice point ────
        with torch.no_grad():
            self.small_model(
                input_ids=input_ids_small,
                attention_mask=attention_mask_small,
            )
        h_small = self._small_capture.get(clone=True).float()  # (batch, seq, 896)

        # ── Step 2: Translate small -> large via adapter ─────────────────────
        h_translated = self.adapter_pair.forward_s2l(h_small)  # (batch, seq, 2048)

        # ── Step 3: Coconut loop in the large model ──────────────────────────
        h_final_large = self.coconut_loop.forward(
            input_ids=input_ids_large,
            attention_mask=attention_mask_large,
            injected_state=h_translated,
            injection_mode=self.config.injection_mode,
        )  # (batch, seq, 2048)

        # ── Step 4: Translate large -> small via adapter ─────────────────────
        h_reconstructed = self.adapter_pair.forward_l2s(h_final_large)  # (batch, seq, 896)

        # ── Step 5: Decode through small model's remaining layers + LM head ──
        # The adapters produce float32 tensors.  The frozen norm / lm_head
        # live in float16, and calling their .forward() inserts dtype casts
        # into the autograd graph that break backward.  We do the math
        # manually in float32 so no half↔float conversion sits on the
        # gradient path.
        h_decoded = h_reconstructed  # float32 from adapter

        # Run any remaining small model layers (if extract_layer < num_layers)
        for layer_idx in self._small_tail_indices:
            layer = self._ref["small_layers"][layer_idx]
            layer_out = layer(h_decoded)
            h_decoded = layer_out[0] if isinstance(layer_out, tuple) else layer_out

        # RMSNorm in float32 (mirrors Qwen2RMSNorm but avoids the module)
        norm = self._ref["small_norm"]
        h_float = h_decoded.float()
        variance = h_float.pow(2).mean(-1, keepdim=True)
        h_normed = h_float * torch.rsqrt(variance + norm.variance_epsilon)
        h_normed = norm.weight.float() * h_normed

        # LM head projection in float32
        lm_head = self._ref["small_lm_head"]
        logits = F.linear(
            h_normed,
            lm_head.weight.float(),
            lm_head.bias.float() if lm_head.bias is not None else None,
        )  # (batch, seq, vocab_size)

        return {
            "logits": logits,
            "h_small": h_small,
            "h_translated": h_translated,
            "h_final_large": h_final_large,
            "h_reconstructed": h_reconstructed,
        }

    @torch.no_grad()
    def generate(
        self,
        input_ids_small: torch.Tensor,
        attention_mask_small: torch.Tensor,
        input_ids_large: torch.Tensor,
        attention_mask_large: torch.Tensor,
        max_new_tokens: int = 64,
    ) -> torch.Tensor:
        """Autoregressive generation using the full pipeline.

        Returns:
            generated_ids: (batch, generated_seq_len) token IDs
        """
        # Run the pipeline once to get the initial logits
        outputs = self.forward(
            input_ids_small, attention_mask_small,
            input_ids_large, attention_mask_large,
        )
        logits = outputs["logits"]

        # Greedy decoding from the pipeline output
        generated = []
        next_token = logits[:, -1, :].argmax(dim=-1)  # (batch,)
        generated.append(next_token)

        # DESIGN DECISION: For subsequent tokens, we run the small model
        # autoregressively (without re-entering the large model pipeline).
        # The large model's contribution is "baked in" via the initial pipeline
        # pass.  Re-running the full pipeline for each token would be extremely
        # expensive and doesn't match the intended architecture: the large model
        # does deep reasoning once, then the small model decodes the result.
        #
        # NOTE: We cannot continue from h_reconstructed by appending raw
        # embeddings because when small_tail_indices is empty (extraction at
        # the final layer), no transformer layers process the new token, so
        # input embeddings would be mixed with layer-24 hidden states.
        # Instead we run the small model natively on the accumulated token
        # sequence, which is correct and matches the design intent above.
        accumulated_ids = input_ids_small

        for _ in range(max_new_tokens - 1):
            if next_token.item() == self.small_tokenizer.eos_token_id:
                break

            accumulated_ids = torch.cat(
                [accumulated_ids, next_token.unsqueeze(-1)], dim=1
            )
            sm_out = self.small_model(input_ids=accumulated_ids)
            next_token = sm_out.logits[:, -1, :].argmax(dim=-1)
            generated.append(next_token)

        return torch.cat([input_ids_small, torch.stack(generated, dim=1)], dim=1)

    def remove_hooks(self):
        """Clean up all registered hooks."""
        self._small_capture.remove()
        self._small_injector.remove()
