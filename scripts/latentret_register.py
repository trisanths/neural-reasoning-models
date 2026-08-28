"""Emit one `exp add` command per latent-retrieval condition.

    python scripts/latentret_register.py results/latentret | bash

Prints rather than runs, so the belief-changed lines can be read before they are
committed to an append-only file. Every row carries the four numbers the
experiment turns on and the chance rate each is read against, because a registry
row that says hit_gate 0.55 without saying chance is 0.167 is a row that will be
misread later.
"""

from __future__ import annotations

import glob
import json
import os
import shlex
import sys

LANE = {
    "latent": "explore",
    "decoded": "explore",
    "question": "explore",
    "uniform": "falsify",
    "latent_notask": "falsify",
    "latent_gated_notask": "falsify",
    "latent_lm": "falsify",
    "latent_easy": "explore",
    "latent_gated": "explore",
}

OBJECTIVE = (
    "PonderNet weighted task loss over a looped core, plus a noisy-or reward for "
    "retrieving the known gold page at any iteration through an open gate, plus a "
    "retrieval budget"
)


def belief(name: str, f: dict) -> str:
    hit, auc, chance = f["hit_gate"], f["gate_auc"], f["chance_hit_one"]
    acc, noinj = f["acc_final"], f["acc_no_injection"]
    if name == "latent":
        return (f"a query projected from the recurrent state retrieves the gold page "
                f"at {hit:.3f} against {chance:.3f} chance and the gate separates "
                f"page-absent from page-present episodes at auc {auc:.3f}, so both "
                f"halves of the mechanism train; but the in-loop injection is inert, "
                f"accuracy {acc:.3f} against {noinj:.3f} with it switched off, so what "
                f"works is retrieval plus a selection readout and not a change to the "
                f"recurrent state")
    if name == "question":
        return (f"the preprocessing text query is much the stronger retriever at "
                f"{hit:.3f} against the latent query, and carries the task with it at "
                f"{acc:.3f}; on this family the discriminating word is in the question, "
                f"so forming the query from the state buys nothing and costs a lot")
    if name == "decoded":
        return (f"a query decoded from the model's own output distribution retrieves at "
                f"{hit:.3f}, statistically level with the latent query and far below the "
                f"question tokens, so latent versus decoded is not where the difference "
                f"on this task lies")
    if name == "uniform":
        return (f"with no query at all the same injection retrieves at {hit:.3f} against "
                f"{chance:.3f} chance, so the hit rates in the other arms are the query "
                f"working and not cross-attention over a pile of pages; task accuracy "
                f"{acc:.3f} nonetheless beats the latent arm, which is evidence against "
                f"the latent query rather than for it")
    if name == "latent_lm":
        return (f"generation cannot say an invented word at this scale, accuracy "
                f"{acc:.3f} while the same run retrieves at {hit:.3f}, so a zero task "
                f"score in an earlier version of this experiment was a readout failure "
                f"and not a retrieval failure")
    if name in ("latent_notask", "latent_gated_notask"):
        return (f"the retrieval term buys gate discrimination and costs everything else: "
                f"without it the gate does not discriminate at all, auc {auc:.3f}, while "
                f"retrieval improves to {hit:.3f} and accuracy to {acc:.3f}, both well "
                f"above the supervised arm; the noisy-or is actively hurting the query "
                f"it is supposed to teach")
    if name == "latent_easy":
        return (f"distractors keeping their own system name leave the hit rate at "
                f"{hit:.3f}, level with the hard condition, so the retrieval numbers are "
                f"not an artefact of how the distractor was named either way")
    if name == "latent_gated":
        return (f"making the gate load bearing for the answer as well as the injection "
                f"keeps the discrimination, auc {auc:.3f}, and collapses accuracy to "
                f"{acc:.3f}: on in-context episodes the gate correctly shuts, which "
                f"removes the copy route, and generation cannot replace it")
    return "none"


def main() -> None:
    directory = sys.argv[1] if len(sys.argv) > 1 else "results/latentret"
    for path in sorted(glob.glob(os.path.join(directory, "*.json"))):
        with open(path) as fh:
            blob = json.load(fh)
        cfg, f, p = blob["config"], blob["final"], blob["params"]
        stem = os.path.basename(path).rsplit(".", 1)[0]
        args = [
            "uv", "run", "python", "-m", "scripts.exp", "add",
            "--run-id", f"latentret-{stem}",
            "--lane", LANE.get(cfg["name"], "explore"),
            "--family", "latentret", "--branch", "A",
            "--objective", OBJECTIVE,
            "--arch", (f"{p['unique_layers']}L looped core, {cfg['d_model']}d, "
                       f"{p['loops']} iterations, effective depth "
                       f"{p['effective_depth']}, retrieval gate and in-loop "
                       f"cross-attention injection ({p['latentret_params']} "
                       f"parameters of that), {cfg['readout']} readout"),
            "--arch-field", f"params_total={p['params_total']}",
            "--arch-field", f"params_non_embedding={p['params_non_embedding']}",
            # The schema's axes, mapped where they genuinely mean the same
            # thing. acc_wrong_evidence is the corrupted store: the gold page
            # overwritten by a duplicate of another page from the same episode,
            # so the wrong evidence is as long, as well formed and as
            # retrievable as the right evidence, which is the strict test the
            # schema asks for. novel_system_acquisition is accuracy on the
            # in-context half, where the page is given and the system was
            # invented from a seed range disjoint from training. There is no
            # no-evidence condition here, so evidence_lift stays underived.
            "--metric", f"reasoning={f['acc_final']:.4f}",
            "--metric", f"acc_correct_evidence={f['acc_final']:.4f}",
            "--metric", f"acc_wrong_evidence={f['acc_corrupted_store']:.4f}",
            "--metric", f"novel_system_acquisition={f['acc_in_context']:.4f}",
            "--compute", f"wall_clock_s={blob['minutes'] * 60.0:.0f}",
            "--source", os.path.abspath(path),
            # The mechanism numbers have no axis in the schema, which steers on
            # task accuracy, so they live here rather than being forced into a
            # field that means something else.
            "--notes", (f"retrieval_hit_at_gate {f['hit_gate']:.3f} against "
                        f"{f['chance_hit_one']:.3f} chance; gate_auc {f['gate_auc']:.3f} "
                        f"against 0.500; gate open {f['gate_max_need']:.3f} when the page "
                        f"is absent and {f['gate_max_in_context']:.3f} when it is in the "
                        f"prompt; answer_vs_foil {f['acc_vs_foil']:.3f} against 0.500, "
                        f"{f['acc_vs_foil_corrupted']:.3f} on the corrupted store; "
                        f"accuracy {f['acc_no_injection']:.3f} with the in-loop injection "
                        f"switched off. query_mode {cfg['query_mode']}, readout "
                        f"{cfg['readout']}, gate_copy {cfg.get('gate_copy')}, alpha "
                        f"{cfg['weights']['alpha']}, gamma {cfg['weights']['gamma']}, "
                        f"{cfg['steps']} steps on one L40S, seed {cfg['seed']}, "
                        f"hard_distractors {cfg['hard']}, n={f['n']} eval episodes"),
            "--belief-changed", belief(cfg["name"], f),
        ]
        print(" ".join(shlex.quote(a) for a in args))
        print()


if __name__ == "__main__":
    main()
