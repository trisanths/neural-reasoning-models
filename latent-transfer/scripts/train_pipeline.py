"""Stages 1-3: train the cross-model latent handoff.

Stage 1 (up-projector): the big model is frozen and driven from the small
model's projected states. Supervision is the big model's own behaviour when it
reads the question directly -- match its continuous thoughts, and keep its
answer correct through its own head. This isolates "can the big model consume
foreign states" from "can the small model decode foreign thoughts".

Stage 2 (down-projector + adapter): everything upstream is frozen; the answer
loss trains the return path and a LoRA adapter on the small model.

Stage 3 (polish): both projectors and the adapter jointly, at low LR.
"""

import argparse
import json
import os
import sys

import torch
import torch.nn.functional as F

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.coconut import Coconut  # noqa: E402
from src.data import load  # noqa: E402
from src.tasks import get_tokenizer  # noqa: E402
from src.dataset import CurriculumConfig, iterate_batches  # noqa: E402
from src.engine import FINAL_STAGE, evaluate, get_device  # noqa: E402
from src.model import ModelConfig, TinyLM  # noqa: E402
from src.pipeline import CrossModelPipeline  # noqa: E402
from src.projectors import Projector, apply_lora  # noqa: E402


def load_backbone(path: str, device, randomize: bool = False):
    """Loads either a hand-written TinyLM or a HuggingFace checkpoint.

    ``randomize`` builds the same architecture with untrained weights, which is
    the control that shows whether the projectors and the small model simply
    learned the task on their own.
    """
    ck = torch.load(path, map_location="cpu", weights_only=False)
    if "hf_model" in ck:
        return _load_hf_backbone(ck, device, randomize)
    model = TinyLM(ModelConfig(**ck["cfg"]))
    if not randomize:
        model.load_state_dict(ck["model"])
    return model.to(device)


def _load_hf_backbone(ck: dict, device, randomize: bool):
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

    from src.hf_backbone import HFBackbone, HFTokenizerAdapter

    name = ck["hf_model"]
    dtype = getattr(torch, ck.get("args", {}).get("dtype", "float32"))
    hf_tok = AutoTokenizer.from_pretrained(name)
    HFTokenizerAdapter(hf_tok)  # adds the three markers, so len() is correct

    if randomize:
        # Architecture only: no pretrained weights and none of the trained ones.
        model = AutoModelForCausalLM.from_config(AutoConfig.from_pretrained(name))
        model = model.to(dtype)
        model.resize_token_embeddings(len(hf_tok))
        return HFBackbone(model, hf_tok).to(device)

    model = AutoModelForCausalLM.from_pretrained(name, dtype=dtype)
    model.resize_token_embeddings(len(hf_tok))
    if ck.get("lora"):
        # The adapter modules have to exist before their weights can be loaded.
        apply_lora(model, rank=ck["lora"])
    missing, unexpected = model.load_state_dict(ck["model"], strict=False)
    if unexpected:
        raise RuntimeError(f"checkpoint has keys the model lacks: {unexpected[:5]}")
    return HFBackbone(model, hf_tok).to(device)


def adapt_receiver(big, rank: int):
    """Gives the receiver a SEPARATE adapter for reading foreign states.

    When the big model was LoRA-finetuned, its task knowledge lives entirely in
    those adapters. Retraining them for the receiver role therefore destroys the
    ability we are trying to borrow. apply_lora instead freezes everything
    present and wraps a fresh adapter around it, initialised to zero so the
    model starts out behaving exactly as it did before.

    Note that the new adapter sits in the forward path for native inputs too, so
    the receiver's own accuracy is expected to fall as it specialises on
    projected states. That is the cost of adaptation, not a bug; the number that
    matters is end-to-end pipeline accuracy.
    """
    return apply_lora(big, rank=rank)


def set_trainable(params, flag: bool):
    for p in params:
        p.requires_grad = flag


def run_epochs(opt, sched, step_fn, train_ex, tok, cur, bs, n_epochs, log, tag, params, clip=1.0):
    step = 0
    skipped = 0
    for ep in range(n_epochs):
        run, cnt = 0.0, 0
        for batch in iterate_batches(train_ex, tok, FINAL_STAGE, cur, bs, shuffle=True, seed=step):
            loss = step_fn(batch)
            if not torch.isfinite(loss):
                skipped += 1
                opt.zero_grad(set_to_none=True)
                continue
            loss.backward()
            # bf16 backward over 1400-token contexts overflows well before the
            # forward does, so a finite loss can still carry nan gradients.
            gnorm = torch.nn.utils.clip_grad_norm_(params, clip)
            if not torch.isfinite(gnorm):
                skipped += 1
                opt.zero_grad(set_to_none=True)
                continue
            opt.step()
            if sched is not None:
                sched.step()
            opt.zero_grad(set_to_none=True)
            run += loss.item()
            cnt += 1
            step += 1
            if step % 50 == 0:
                sk = f" skipped={skipped}" if skipped else ""
                log(f"  [{tag}] ep {ep} step {step} loss {run / max(cnt, 1):.4f}{sk}")
                run, cnt = 0.0, 0
    return step


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--small_ckpt", required=True)
    p.add_argument("--task", default="prosqa", choices=["prosqa", "compose"])
    p.add_argument("--big_ckpt", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--data", default="data")
    p.add_argument("--benchmark", default="prosqa", choices=["prosqa", "gsm", "hotpot"])
    p.add_argument("--n_train", type=int, default=12000)
    p.add_argument("--n_val", type=int, default=500)
    p.add_argument("--batch_size", type=int, default=32)
    p.add_argument("--max_latent_stage", type=int, default=5)
    p.add_argument("--proj_kind", default="mlp", choices=["linear", "mlp"])
    p.add_argument("--lora_rank", type=int, default=8)
    p.add_argument("--epochs_s1", type=int, default=2)
    p.add_argument("--epochs_s2", type=int, default=3)
    p.add_argument("--epochs_s3", type=int, default=1)
    p.add_argument("--lr_s1", type=float, default=1e-3)
    p.add_argument("--lr_s2", type=float, default=1e-3)
    p.add_argument("--lr_s3", type=float, default=2e-4)
    p.add_argument("--mse_weight", type=float, default=1.0)
    p.add_argument("--ce_weight", type=float, default=1.0)
    p.add_argument("--add_positional_big", type=int, default=1)
    p.add_argument(
        "--n_message",
        type=int,
        default=0,
        help="0 = send all question states; >0 = send only this many compressed states",
    )
    p.add_argument("--random_big", type=int, default=0, help="control: frozen random big model")
    p.add_argument(
        "--lora_big",
        type=int,
        default=0,
        help="also adapt the big model to consume projected states (rank of the "
             "LoRA; 0 = keep it frozen). Interlat and Cache-to-Cache both train "
             "the receiver rather than expecting a frozen model to read a "
             "foreign latent space. Inference cost is unchanged.",
    )
    p.add_argument("--rms_match", type=int, default=1)
    p.add_argument(
        "--tap_layer",
        type=int,
        default=-1,
        help="which small-model layer to send (-1 = final post-LN state); "
             "intermediate features often transfer better between models",
    )
    p.add_argument("--seed", type=int, default=0)
    a = p.parse_args()

    frac = os.environ.get("CUDA_MEM_FRACTION")
    if frac and torch.cuda.is_available():
        # Two arms share one card; without a cap the first to allocate takes
        # almost all of it and the second dies at startup.
        torch.cuda.set_per_process_memory_fraction(float(frac))
    torch.manual_seed(a.seed)
    os.makedirs(a.out, exist_ok=True)
    dev = get_device()
    # The tokenizer must match whatever the checkpoints were trained with, so it
    # is derived from the small checkpoint rather than from --task.
    small_ck = torch.load(a.small_ckpt, map_location="cpu", weights_only=False)
    is_hf = "hf_model" in small_ck
    if is_hf:
        from transformers import AutoTokenizer

        from src.hf_backbone import HFTokenizerAdapter
        from src.benchmarks import load_benchmark
        from src.prosqa import ProsQAHFTokenizer, assert_tokenizer_compatible

        hf_tok = AutoTokenizer.from_pretrained(small_ck["hf_model"])
        tok = ProsQAHFTokenizer(HFTokenizerAdapter(hf_tok))
        train_ex, val_ex, test_ex = load_benchmark(
            a.benchmark, a.data, a.n_train, a.n_val, None
        )
        assert_tokenizer_compatible(tok, train_ex)
    else:
        tok = get_tokenizer(a.task)
        train_ex = load(f"{a.data}/train.json")[: a.n_train]
        val_ex = load(f"{a.data}/val.json")[: a.n_val]
        test_ex = load(f"{a.data}/test.json")
    # ProsQA chains vary from 3 to 6 steps, so the latent count must be padded to
    # keep the latent block aligned across a batch.
    cur = CurriculumConfig(
        max_latent_stage=a.max_latent_stage, c_thought=1, pad_latent_to_max=is_hf
    )

    small = load_backbone(a.small_ckpt, dev)
    big = load_backbone(a.big_ckpt, dev, randomize=bool(a.random_big))
    d_s, d_b = small.cfg.d_model, big.cfg.d_model

    # Measure what each receiver actually expects, rather than assuming unit
    # scale. The two models differ by ~300x here, and a projector initialised at
    # the wrong scale hands the receiver out-of-distribution vectors from step 0.
    with torch.no_grad():
        rms_big = big.get_input_embeddings().weight.float().pow(2).mean().sqrt().item()
        rms_small = small.get_input_embeddings().weight.float().pow(2).mean().sqrt().item()
    log_init = f"embedding RMS: small={rms_small:.5f} big={rms_big:.5f}"
    proj_up = Projector(d_s, d_b, kind=a.proj_kind, rms_match=bool(a.rms_match),
                        target_rms=rms_big).to(dev)
    proj_down = Projector(d_b, d_s, kind=a.proj_kind, rms_match=bool(a.rms_match),
                          target_rms=rms_small).to(dev)

    lora_params = apply_lora(small, rank=a.lora_rank)
    small.to(dev)
    if a.lora_big:
        big_lora_params = adapt_receiver(big, rank=a.lora_big)
        big.to(dev)
    else:
        big_lora_params = []
        for p_ in big.parameters():
            p_.requires_grad = False

    pipe = CrossModelPipeline(
        small,
        big,
        proj_up,
        proj_down,
        add_positional_big=bool(a.add_positional_big),
        n_message=(a.n_message or None),
        tap_layer=(None if a.tap_layer < 0 else a.tap_layer),
    ).to(dev)
    coco_big = Coconut(big)

    logf = open(os.path.join(a.out, "log.txt"), "a")

    def log(m: str) -> None:
        print(m, flush=True)
        logf.write(m + "\n")
        logf.flush()

    log(log_init)
    log(f"=== pipeline d_s={d_s} d_b={d_b} proj={a.proj_kind} random_big={a.random_big} ===")
    log(f"small={small.n_params() / 1e6:.2f}M big={big.n_params() / 1e6:.2f}M "
        f"proj_up={sum(p.numel() for p in proj_up.parameters()) / 1e6:.3f}M "
        f"lora={sum(p.numel() for p in lora_params) / 1e6:.3f}M")

    results = {}

    # ---------------- Stage 1: up-projector ----------------
    # Skippable: under compression the thought-matching target is the only
    # available signal and may be too weak to be worth a separate stage, in
    # which case both projectors are trained jointly by the answer loss below.
    up_params = list(proj_up.parameters()) + big_lora_params
    set_trainable(up_params, True)
    set_trainable(list(proj_down.parameters()), False)
    set_trainable(lora_params, False)

    def s1_step(batch):
        batch = batch.to(dev)
        with torch.no_grad():
            # Teacher: the big model reasoning from the question it read itself.
            # With a big-model adapter active this must be the *pre-adapter*
            # behaviour, otherwise the target drifts with the student.
            for lp in big_lora_params:
                lp.requires_grad_(False)
            scales = [(m, m.scale) for m in big.modules() if hasattr(m, "scale") and hasattr(m, "a")]
            for m, _sc in scales:
                m.scale = 0.0
            _, _, t_thoughts = coco_big(batch)
            for m, sc in scales:
                m.scale = sc
            for lp in big_lora_params:
                lp.requires_grad_(True)
            _, _, h_small = pipe._small_prefix(batch, need_logits=False)
        # Student: the same big model reasoning from projected small-model state.
        s_thoughts = pipe.big_thoughts(h_small, batch)
        loss = a.mse_weight * sum(
            F.mse_loss(s, t) for s, t in zip(s_thoughts, t_thoughts)
        ) / max(len(t_thoughts), 1)
        # Keeping the big model's answer correct through its own head is only
        # well-defined when it sees the full question layout; under compression
        # its positions no longer correspond to the batch.
        if a.ce_weight > 0 and pipe.n_message is None:
            ce, _, _ = coco_big(batch, prefix_embeds=proj_up(h_small))
            loss = loss + a.ce_weight * ce
        return loss

    if a.epochs_s1 > 0:
        opt = torch.optim.AdamW(up_params, lr=a.lr_s1, weight_decay=0.01)
        n_steps = (len(train_ex) // a.batch_size + 1) * a.epochs_s1
        sched = torch.optim.lr_scheduler.OneCycleLR(
            opt, max_lr=a.lr_s1, total_steps=max(n_steps, 1), pct_start=0.05
        )
        run_epochs(opt, sched, s1_step, train_ex, tok, cur, a.batch_size, a.epochs_s1, log, "s1", up_params)

        # Gate: does the big model still answer correctly from projected states?
        m_native = evaluate(coco_big, val_ex, tok, cur, dev, batch_size=8)
        log(f"[gate s1] big-native          val concept={m_native['concept']:.4f}")
        results["s1"] = {"native": m_native}
        if pipe.n_message is None:
            m = eval_big_projected(coco_big, pipe, proj_up, val_ex, tok, cur, dev)
            log(f"[gate s1] big-from-projected  val concept={m['concept']:.4f}")
            results["s1"]["projected"] = m
    else:
        log("[stage 1] skipped; both projectors train jointly in stage 2")

    # ---------------- Stage 2: down-projector + adapter ----------------
    down_params = list(proj_down.parameters())
    set_trainable(down_params, True)
    set_trainable(lora_params, True)
    # If stage 1 ran, the up-projector is already fitted and is held fixed so
    # this stage is a clean test of the return path.
    set_trainable(up_params, a.epochs_s1 == 0)
    s2_params = down_params + lora_params + (up_params if a.epochs_s1 == 0 else [])

    def s2_step(batch):
        batch = batch.to(dev)
        loss, _, _ = pipe(batch)
        return loss

    opt = torch.optim.AdamW(s2_params, lr=a.lr_s2, weight_decay=0.01)
    n_steps = (len(train_ex) // a.batch_size + 1) * a.epochs_s2
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=a.lr_s2, total_steps=max(n_steps, 1), pct_start=0.05)
    run_epochs(opt, sched, s2_step, train_ex, tok, cur, a.batch_size, a.epochs_s2, log, "s2", s2_params)
    m2 = evaluate(pipe, val_ex, tok, cur, dev, batch_size=8)
    log(f"[gate s2] pipeline val exact={m2['exact']:.4f} concept={m2['concept']:.4f}")
    results["s2"] = m2

    # ---------------- Stage 3: joint polish ----------------
    if a.epochs_s3 > 0:
        set_trainable(up_params, True)
        s3_params = up_params + down_params + lora_params
        opt = torch.optim.AdamW(s3_params, lr=a.lr_s3, weight_decay=0.01)
        n_steps = (len(train_ex) // a.batch_size + 1) * a.epochs_s3
        sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=a.lr_s3, total_steps=max(n_steps, 1), pct_start=0.05)
        run_epochs(opt, sched, s2_step, train_ex, tok, cur, a.batch_size, a.epochs_s3, log, "s3", s3_params)
        m3 = evaluate(pipe, val_ex, tok, cur, dev, batch_size=8)
        log(f"[gate s3] pipeline val exact={m3['exact']:.4f} concept={m3['concept']:.4f}")
        results["s3"] = m3

    test = evaluate(pipe, test_ex, tok, cur, dev, batch_size=8)
    log(f"TEST pipeline exact={test['exact']:.4f} concept={test['concept']:.4f}")
    results["test"] = test

    torch.save(
        {
            "proj_up": proj_up.state_dict(),
            "proj_down": proj_down.state_dict(),
            "big_lora": {
                k: v
                for k, v in big.state_dict().items()
                if k.endswith(".a") or k.endswith(".b")
            },
            "small_lora": {
                k: v
                for k, v in small.state_dict().items()
                if k.endswith(".a") or k.endswith(".b")
            },
            "args": vars(a),
        },
        os.path.join(a.out, "pipeline.pt"),
    )
    with open(os.path.join(a.out, "metrics.json"), "w") as f:
        json.dump(results, f, indent=2)
    log(f"saved -> {a.out}")


@torch.no_grad()
def eval_big_projected(coco_big, pipe, proj_up, examples, tok, cur, dev, batch_size=16):
    """Accuracy of the big model when driven from projected small-model states,
    decoding with its own head. This is the Stage 1 gate."""
    from src.dataset import build_batch
    from src.engine import _answer_key, _final_sentence

    n = concept = 0
    for i in range(0, len(examples), batch_size):
        chunk = examples[i : i + batch_size]
        batch = build_batch(chunk, tok, FINAL_STAGE, cur, for_generation=True).to(dev)
        _, _, h_small = pipe._small_prefix(batch, need_logits=False)
        embeds = proj_up(h_small)
        out = generate_big_with_prefix(coco_big, batch, embeds, tok)
        for j, ex in enumerate(chunk):
            ids = out[j].tolist()
            if tok.eos_id in ids:
                ids = ids[: ids.index(tok.eos_id)]
            pred = _final_sentence(tok.decode(ids))
            n += 1
            # Same metric as engine.evaluate; the old positional form assumed a
            # space before the final period and misscores subword tokenisers.
            if _answer_key(pred) and _answer_key(pred) == _answer_key(ex.answer):
                concept += 1
    return {"concept": concept / max(n, 1), "n": n}


@torch.no_grad()
def generate_big_with_prefix(coco_big, batch, prefix_embeds, tok, max_new_tokens=8):
    """Greedy decode from the big model given externally supplied prefix states."""
    ls, k = batch.latent_start, batch.n_latent
    B = batch.input_ids.shape[0]
    dev = batch.input_ids.device
    _, kv, _, _ = coco_big._prefix(batch, None, prefix_embeds, need_logits=False)
    eot_pos = ls + k
    out = coco_big.base(
        input_ids=batch.input_ids[:, eot_pos : eot_pos + 1],
        attention_mask=batch.attention_mask[:, : eot_pos + 1],
        position_ids=batch.position_ids[:, eot_pos : eot_pos + 1],
        past_key_values=kv,
    )
    kv, logits = out.past_key_values, out.logits[:, -1]
    mask = batch.attention_mask[:, : eot_pos + 1]
    tokens = torch.zeros(B, max_new_tokens, dtype=torch.long, device=dev)
    done = torch.zeros(B, dtype=torch.bool, device=dev)
    pos = batch.position_ids[:, eot_pos] + 1
    for t in range(max_new_tokens):
        nxt = logits.argmax(-1)
        nxt = torch.where(done, torch.zeros_like(nxt), nxt)
        tokens[:, t] = nxt
        done = done | (nxt == tok.eos_id)
        if bool(done.all()):
            break
        mask = torch.cat([mask, torch.ones(B, 1, dtype=mask.dtype, device=dev)], 1)
        out = coco_big.base(
            input_ids=nxt.unsqueeze(1),
            attention_mask=mask,
            position_ids=pos.unsqueeze(1),
            past_key_values=kv,
        )
        kv, logits = out.past_key_values, out.logits[:, -1]
        pos = pos + 1
    return tokens


if __name__ == "__main__":
    main()
