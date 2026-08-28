"""What the run has to report: does the gate discriminate, does the query find.

Three questions, and one number each, all measured on held-out episode seeds.

  Does the latent query find the page?
      hit_gate is the fraction of episodes where the top scored document at the
      iteration the gate opened widest is the gold page. That is the one the
      mechanism would actually act on, and its chance rate is 1/6 = 0.167,
      because it is a single choice among six documents. hit_last is the same
      at the final iteration, also 1/6.

      hit_any, the fraction where some iteration lands on the gold page, is
      reported but is NOT comparable to 1/6: six independent guesses hit at
      1 - (5/6)^6 = 0.665. chance_hit_any carries that number so the two are
      never read against the wrong baseline. It is in the file because a large
      gap between hit_any and hit_gate says the query wandered across
      iterations, which is worth seeing, not because 'it found the page at
      least once' is evidence of anything on its own.

  Does the gate fire when the answer is not yet in state?
      gate_gap is mean max_i g_i over episodes whose gold page is absent from
      the prompt, minus the same over episodes where it was pasted in. gate_auc
      is the probability that a randomly drawn absent-page episode gets a higher
      max gate than a randomly drawn in-context one: 0.5 is no discrimination,
      1.0 is perfect. AUC is the honest one because it does not move when the
      gate saturates.

  Did the content of the right page reach the output?
      acc_vs_foil is P(answer) > P(foil) at the answer position, where the foil
      is the answer the same question would have under the distractor system.
      Both words sit in the same document store, both are invented words from
      the same pool, and neither is in the prompt, so this is a two-way choice
      with a chance rate of one half that a model can win only by having read
      the right page. It exists because full vocabulary accuracy over 701 types
      cannot distinguish 'retrieved nothing' from 'retrieved the page and could
      not produce a word it has never emitted', and at this scale the second is
      a live possibility.

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
from src.skillacq.simple import SIMPLE_FAMILIES


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
    acc_f, acc_h, hit_any, hit_last, hit_gate, p_gold = [], [], [], [], [], []
    gate_max, gate_mean, in_ctx, halt_step, fam = [], [], [], [], []
    acc_corrupt, acc_noinj, foil_win, foil_win_c = [], [], [], []
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

        last = out.logits[:, -1].float()
        foil_win.append((last[b, batch.answer] > last[b, batch.foil]).float())

        top = out.doc_log_probs.argmax(-1)                       # (B, L)
        is_gold = (top == batch.gold.unsqueeze(1))
        hit_any.append(is_gold.any(dim=1).float())
        hit_last.append(is_gold[:, -1].float())
        widest = out.gate_probs.float().argmax(1)                # (B,)
        hit_gate.append(is_gold[b, widest].float())
        p_gold.append(out.doc_log_probs.float().exp()[b, :, batch.gold].mean(1))

        gate_max.append(out.gate_probs.float().amax(1))
        gate_mean.append(out.gate_probs.float().mean(1))
        in_ctx.append(batch.in_context)
        fam.append(batch.family)

        bad = corrupted_store(batch)
        out_c = model.episode_forward(
            bad.prompt, bad.ans_pos, bad.docs, bad.doc_mask,
            bad.question, bad.question_mask, query_mode=query_mode, loops=loops)
        acc_corrupt.append((out_c.logits[:, -1].argmax(-1) == bad.answer).float())
        last_c = out_c.logits[:, -1].float()
        foil_win_c.append((last_c[b, bad.answer] > last_c[b, bad.foil]).float())

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
        "acc_vs_foil": float(cat(foil_win).mean()),
        "acc_vs_foil_corrupted": float(cat(foil_win_c).mean()),
        "acc_no_injection": float(cat(acc_noinj).mean()),
        "hit_gate": float(cat(hit_gate).mean()),
        "hit_last": float(cat(hit_last).mean()),
        "hit_any": float(cat(hit_any).mean()),
        "chance_hit_one": 1.0 / int(batch.docs.shape[1]),
        "chance_hit_any": 1.0 - (1.0 - 1.0 / int(batch.docs.shape[1])) ** n_loops,
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
    hits = cat(hit_gate)
    res["hit_gate_need"] = float(hits[need].mean()) if need.any() else float("nan")
    res["hit_gate_in_context"] = float(hits[ctx].mean()) if ctx.any() else float("nan")
    fw = cat(foil_win)
    res["acc_vs_foil_need"] = float(fw[need].mean()) if need.any() else float("nan")
    res["acc_vs_foil_in_context"] = float(fw[ctx].mean()) if ctx.any() else float("nan")
    # Per family, because the three are not the same problem: threshold_rule
    # repeats its upper label on the worked example, so half of its answers can
    # be read off a page that is not the gold one, and an average over the
    # three hides that. The other two families put the answer on the gold page
    # and nowhere else.
    families = sorted(SIMPLE_FAMILIES)
    fams, hg, accs_all, fws = cat(fam), cat(hit_gate), cat(acc_f), cat(foil_win)
    res["by_family"] = {
        name: {
            "n": int((fams == i).sum()),
            "hit_gate": float(hg[fams == i].mean()),
            "acc_final": float(accs_all[fams == i].mean()),
            "acc_vs_foil": float(fws[fams == i].mean()),
            "gate_auc": _auc(gmax[(fams == i) & need], gmax[(fams == i) & ctx]),
        }
        for i, name in enumerate(families) if (fams == i).any()
    }
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
