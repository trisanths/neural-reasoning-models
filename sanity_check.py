"""Quick sanity check: load everything, run one forward pass, report VRAM."""

import torch
from config import PipelineConfig, TrainingConfig, resolve_module
from models.adapters import AdapterPair, collect_activations, initialize_adapters_procrustes
from models.pipeline import LatentTranslationPipeline
from data.gsm8k import GSM8KDataset, get_probe_texts

def main():
    config = PipelineConfig()
    tconfig = TrainingConfig()

    def build_large_ids(prompt_text: str, target_len: int):
        ids = tok_l.encode(prompt_text, add_special_tokens=False)
        if len(ids) < target_len:
            ids = ids + [tok_l.pad_token_id] * (target_len - len(ids))
        else:
            ids = ids[:target_len]
        tensor = torch.tensor([ids], device="cuda")
        return tensor, torch.ones_like(tensor)

    # ── Load models ──────────────────────────────────────────────────────────
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print("Loading models...")
    tok_s = AutoTokenizer.from_pretrained(config.small_model.name)
    tok_l = AutoTokenizer.from_pretrained(config.large_model.name)
    if tok_s.pad_token is None:
        tok_s.pad_token = tok_s.eos_token
    if tok_l.pad_token is None:
        tok_l.pad_token = tok_l.eos_token

    model_s = AutoModelForCausalLM.from_pretrained(
        config.small_model.name, dtype=torch.float16, device_map="cuda"
    )
    model_l = AutoModelForCausalLM.from_pretrained(
        config.large_model.name, dtype=torch.float16, device_map="cuda"
    )
    model_s.eval()
    model_l.eval()

    # ── VRAM check ───────────────────────────────────────────────────────────
    print("\n== VRAM after loading models ==")
    alloc = torch.cuda.memory_allocated() / 1e9
    reserved = torch.cuda.memory_reserved() / 1e9
    total = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"  Allocated: {alloc:.2f} GB")
    print(f"  Reserved:  {reserved:.2f} GB")
    print(f"  Total:     {total:.2f} GB")
    print(f"  Free:      {total - reserved:.2f} GB")

    # ── Init adapters ────────────────────────────────────────────────────────
    print("\nInitializing adapters...")
    adapter_pair = AdapterPair(config.small_model.hidden_dim, config.large_model.hidden_dim)

    probe_texts = get_probe_texts(50)
    small_layer = resolve_module(
        model_s, config.small_model.layer_template.format(i=config.small_extract_layer - 1)
    )
    large_layer = resolve_module(
        model_l, config.large_model.layer_template.format(i=config.large_inject_layer - 1)
    )
    h_s = collect_activations(model_s, tok_s, probe_texts, small_layer)
    h_l = collect_activations(model_l, tok_l, probe_texts, large_layer)
    initialize_adapters_procrustes(adapter_pair, h_s, h_l)
    adapter_pair = adapter_pair.to("cuda")

    # ── Build pipeline ───────────────────────────────────────────────────────
    print("\nBuilding pipeline...")
    pipeline = LatentTranslationPipeline(
        small_model=model_s,
        large_model=model_l,
        small_tokenizer=tok_s,
        large_tokenizer=tok_l,
        adapter_pair=adapter_pair,
        config=config,
    )

    # ── Single forward pass ──────────────────────────────────────────────────
    print("\n== Running single forward pass ==")
    question = "Janet's ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells every duck egg at the farmers' market daily for $2. How much in dollars does she make every day at the farmers' market?"

    messages = [{"role": "user", "content": question}]

    # Tokenize for small model
    prompt_s = tok_s.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
    ids_s = tok_s.encode(prompt_s + "The answer is 18", add_special_tokens=False)
    ids_s = torch.tensor([ids_s], device="cuda")
    mask_s = torch.ones_like(ids_s)

    # Tokenize for large model
    prompt_l = tok_l.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
    ids_l, mask_l = build_large_ids(prompt_l, ids_s.shape[1])

    print(f"  Small model input: {ids_s.shape}")
    print(f"  Large model input: {ids_l.shape}")

    try:
        outputs = pipeline(ids_s, mask_s, ids_l, mask_l)
        print(f"  Logits shape: {outputs['logits'].shape}")
        print(f"  h_small shape: {outputs['h_small'].shape}")
        print(f"  h_translated shape: {outputs['h_translated'].shape}")
        print(f"  h_final_large shape: {outputs['h_final_large'].shape}")
        print(f"  h_reconstructed shape: {outputs['h_reconstructed'].shape}")

        # Check the predicted token
        pred_token = outputs["logits"][0, -1].argmax().item()
        print(f"  Predicted next token: '{tok_s.decode([pred_token])}' (id={pred_token})")
        print("\n  Forward pass: OK")
    except Exception as e:
        print(f"\n  Forward pass FAILED: {e}")
        import traceback
        traceback.print_exc()
        return

    # ── Generation test ──────────────────────────────────────────────────────
    print("\n== Running generation ==")
    # Re-tokenize without the answer for generation
    ids_s_gen = tok_s.encode(prompt_s, add_special_tokens=False)
    ids_s_gen = torch.tensor([ids_s_gen], device="cuda")
    mask_s_gen = torch.ones_like(ids_s_gen)

    try:
        ids_l_gen, mask_l_gen = build_large_ids(prompt_l, ids_s_gen.shape[1])
        gen_ids = pipeline.generate(ids_s_gen, mask_s_gen, ids_l_gen, mask_l_gen, max_new_tokens=32)
        gen_text = tok_s.decode(gen_ids[0], skip_special_tokens=True)
        print(f"  Generated text: {gen_text[-200:]}")
        print("\n  Generation: OK")
    except Exception as e:
        print(f"\n  Generation FAILED: {e}")
        import traceback
        traceback.print_exc()

    # ── Final VRAM ───────────────────────────────────────────────────────────
    print("\n== VRAM after forward pass ==")
    alloc = torch.cuda.memory_allocated() / 1e9
    reserved = torch.cuda.memory_reserved() / 1e9
    print(f"  Allocated: {alloc:.2f} GB")
    print(f"  Reserved:  {reserved:.2f} GB")
    print(f"  Free:      {total - reserved:.2f} GB")


if __name__ == "__main__":
    main()
