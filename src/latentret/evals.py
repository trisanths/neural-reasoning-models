"""What the run has to report: does the gate discriminate, does the query find.

Three questions, and one number each, all measured on held-out episode seeds.

  Does the latent query find the page?
      hit_any is the fraction of episodes where the top scored document at some
      iteration is the gold page. Chance is 1/6 = 0.167 under hard distractors.
      Under easy distractors a retriever that matches the system name and then
      guesses among that system's three pages gets 0.333, so the easy number
      has to clear 0.333 to mean anything and the hard number has to clear
      0.167. Both are reported.

  Does the gate fire when the answer is not yet in state?
      gate_gap is mean max_i g_i over episodes whose gold page is absent from
      the prompt, minus the same over episodes where it was pasted in. gate_auc
      is the probability that a randomly drawn absent-page episode gets a higher
      max gate than a randomly drawn in-context one: 0.5 is no discrimination,
      1.0 is perfect. AUC is the honest one because it does not move when the
      gate saturates.

  Is anything actually flowing through the injection?
      acc_retrieval against acc_corrupted, where the corrupted store has the
      gold page overwritten by a copy of another page from the same episode.
      The store is the same size and the same prose either way, so a drop is
      caused by the content that used to be there. acc_no_inject switches the
      injection off entirely and is the floor: what the model scores from the
      question alone.
"""

from __future__ import annotations

import torch

from src.latentret.data import EpisodeStream, corrupted_store


def _auc(pos: torch.Tensor, neg: torch.Tensor) -> float:
    """P(a random positive scores above a random negative), ties at half."""
    if pos.numel() == 0 or neg.numel() == 0:
        return float("nan")
    diff = pos.view(-1, 1) - neg.view(1, -1)
    return float((torch.sign(diff) + 1.0).mean() / 2.0)


@torch.no_grad()
def measure(model, stream: EpisodeStream, device, n_batches: int = 8,
            query_mode: str = "latent", loops: int | None = None) -> dict:
    model.eval()
    acc_f, acc_h, hit_any, hit_last, p_gold = [], [], [], [], []
    gate_max, gate_mean, in_ctx, halt_step = [], [], [], []
    acc_corrupt, acc_noinj = [], []
    for _ in range(n_batches):
        batch = stream.batch().to(device)
        out = model.episode_forward(
            batch.prompt, batch.ans_pos, batch.docs, batch.doc_mask,
            batch.question, batch.question_mask,
            query_mode=query_mode, loops=loops)
        bsz, n_loops, _ = out.logits.shape
        b = torch.arange(bsz, device=device)
        pred = out.logits.argmax(-1)                             # (B, L)
        correct = (pred == batch.answer.unsqueeze(1)).float()
        acc_f.append(correct[:, -1])
        acc_h.append((out.halt_probs.float() * correct).sum(1))
        halt_step.append((out.halt_probs.float()
                          * torch.arange(n_loops, device=device).float()).sum(1))

        top = out.doc_log_probs.argmax(-1)                       # (B, L)
        is_gold = (top == batch.gold.unsqueeze(1))
        hit_any.append(is_gold.any(dim=1).float())
        hit_last.append(is_gold[:, -1].float())
        p_gold.append(out.doc_log_probs.float().exp()[b, :, batch.gold].mean(1))

        gate_max.append(out.gate_probs.float().amax(1))
        gate_mean.append(out.gate_probs.float().mean(1))
        in_ctx.append(batch.in_context)

        bad = corrupted_store(batch)
        out_c = model.episode_forward(
            bad.prompt, bad.ans_pos, bad.docs, bad.doc_mask,
            bad.question, bad.question_mask, query_mode=query_mode, loops=loops)
        acc_corrupt.append((out_c.logits[:, -1].argmax(-1) == bad.answer).float())

        out_n = model.episode_forward(
            batch.prompt, batch.ans_pos, batch.docs, batch.doc_mask,
            batch.question, batch.question_mask,
            query_mode=query_mode, inject=False, loops=loops)
        acc_noinj.append((out_n.logits[:, -1].argmax(-1) == batch.answer).float())

    cat = lambda xs: torch.cat(xs)
    ctx = cat(in_ctx)
    gmax, gmean = cat(gate_max), cat(gate_mean)
    need = ~ctx
    res = {
        "query_mode": query_mode,
        "n": int(ctx.numel()),
        "acc_final": float(cat(acc_f).mean()),
        "acc_halt_weighted": float(cat(acc_h).mean()),
        "acc_corrupted_store": float(cat(acc_corrupt).mean()),
        "acc_no_injection": float(cat(acc_noinj).mean()),
        "hit_any": float(cat(hit_any).mean()),
        "hit_last": float(cat(hit_last).mean()),
        "p_gold_mean": float(cat(p_gold).mean()),
        "gate_mean": float(gmean.mean()),
        "gate_max_need": float(gmax[need].mean()) if need.any() else float("nan"),
        "gate_max_in_context": float(gmax[ctx].mean()) if ctx.any() else float("nan"),
        "gate_auc": _auc(gmax[need], gmax[ctx]),
        "mean_halt_step": float(cat(halt_step).mean()),
    }
    res["gate_gap"] = res["gate_max_need"] - res["gate_max_in_context"]
    # The same retrieval numbers restricted to episodes that actually need the
    # store, which is where a hit means anything.
    hits = cat(hit_any)
    res["hit_any_need"] = float(hits[need].mean()) if need.any() else float("nan")
    accs = cat(acc_f)
    res["acc_need"] = float(accs[need].mean()) if need.any() else float("nan")
    res["acc_in_context"] = float(accs[ctx].mean()) if ctx.any() else float("nan")
    model.train()
    return res


@torch.no_grad()
def per_iteration(model, stream: EpisodeStream, device, n_batches: int = 4,
                  query_mode: str = "latent", loops: int | None = None) -> dict:
    """Gate and hit rate as a function of iteration index: the curve."""
    model.eval()
    hits, gates_need, gates_ctx, pg = [], [], [], []
    for _ in range(n_batches):
        batch = stream.batch().to(device)
        out = model.episode_forward(
            batch.prompt, batch.ans_pos, batch.docs, batch.doc_mask,
            batch.question, batch.question_mask,
            query_mode=query_mode, loops=loops)
        b = torch.arange(batch.gold.shape[0], device=device)
        hits.append((out.doc_log_probs.argmax(-1) == batch.gold.unsqueeze(1)).float())
        pg.append(out.doc_log_probs.float().exp()[b, :, batch.gold])
        need = ~batch.in_context
        gates_need.append(out.gate_probs.float()[need])
        gates_ctx.append(out.gate_probs.float()[batch.in_context])
    model.train()
    return {
        "hit_by_iter": torch.cat(hits).mean(0).tolist(),
        "p_gold_by_iter": torch.cat(pg).mean(0).tolist(),
        "gate_need_by_iter": torch.cat(gates_need).mean(0).tolist(),
        "gate_in_context_by_iter": torch.cat(gates_ctx).mean(0).tolist(),
    }
