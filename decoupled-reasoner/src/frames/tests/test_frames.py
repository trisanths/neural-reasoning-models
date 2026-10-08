"""Tests that pin the generator's guarantees.

The canary test is the one that matters most. A grader that asks whether an
answer contains the gold scores a hedging policy correct on every item; three
graders of that shape were found broken on this project in one day. The canary
is a stand-in that answers with every candidate on every item, and it must
score exactly 0.0 under forced choice.
"""

from __future__ import annotations

import random

from src.disc.renderers import NativeSimple, simple_episode
from src.frames import distance as dist
from src.frames import score as sc
from src.frames.generate import (FAMILIES, FRAMES, NATIVE_FRAME, split_frames)
from src.skillacq.simple import SIMPLE_FAMILIES

SEEDS = [2900000, 2900001, 2900002, 2900003, 2900004]


def _cands(ep):
    return list(ep["candidates"])


def test_canary_scores_zero_forced():
    rows = []
    for fam in FAMILIES:
        for s in SEEDS:
            ep = simple_episode(s, fam, FRAMES[NATIVE_FRAME])
            for q in ep["questions"]:
                rows.append({"ep": s, "qid": q["qid"], "family": fam,
                             "gold": q["answer"], "answer": "",
                             "candidates": _cands(ep), "twin_candidates": [],
                             "chunks": [d["text"] for d in ep["documents"]],
                             "shipped_ok": False})
    canary = sc.canary_rows(rows)
    vocab = sc.nonce_vocab(canary)
    out = sc.summarize(canary, vocab)
    assert out["acc_forced"] == 0.0, out
    assert out["hedge_rate"] == 1.0, out
    # and the shipped-style containment grader would have been fooled
    assert out["acc_shipped"] == 1.0, out


def test_canary_zero_on_every_frame():
    fam = "substitution_rule"
    for name in list(FRAMES)[::7]:
        rows = []
        for s in SEEDS:
            ep = simple_episode(s, fam, FRAMES[name])
            for q in ep["questions"]:
                rows.append({"ep": s, "qid": q["qid"], "family": fam,
                             "gold": q["answer"], "answer": "",
                             "candidates": _cands(ep), "twin_candidates": [],
                             "chunks": [d["text"] for d in ep["documents"]],
                             "shipped_ok": False})
        canary = sc.canary_rows(rows)
        assert sc.summarize(canary, sc.nonce_vocab(canary))["acc_forced"] == 0.0


def test_native_frame_reproduces_published_wording():
    ref = NativeSimple()
    for fam in FAMILIES:
        for s in SEEDS:
            a = simple_episode(s, fam, FRAMES[NATIVE_FRAME])
            b = simple_episode(s, fam, ref)
            assert [d["text"] for d in a["documents"]] == \
                   [d["text"] for d in b["documents"]], (fam, s)
            assert [q["text"] for q in a["questions"]] == \
                   [q["text"] for q in b["questions"]], (fam, s)


def test_gold_answers_agree_across_frames():
    names = sorted(FRAMES)
    for fam in FAMILIES:
        for s in SEEDS:
            base = None
            for n in names:
                ep = simple_episode(s, fam, FRAMES[n])
                key = [(q["qid"], q["answer"]) for q in ep["questions"]]
                if base is None:
                    base = key
                assert key == base, (n, fam, s)


def test_page_count_and_candidate_count_constant():
    for fam in FAMILIES:
        for s in SEEDS:
            pages, cands = set(), set()
            for n in sorted(FRAMES):
                ep = simple_episode(s, fam, FRAMES[n])
                pages.add(len(ep["documents"]))
                cands.add(len(ep["candidates"]))
            assert len(pages) == 1, (fam, s, pages)
            assert len(cands) == 1, (fam, s, cands)


def test_wording_distinct_across_frames():
    fam = "substitution_rule"
    s = SEEDS[0]
    seen = {}
    for n in sorted(FRAMES):
        ep = simple_episode(s, fam, FRAMES[n])
        key = ("\n".join(d["text"] for d in ep["documents"]),
               ep["questions"][0]["text"])
        assert key not in seen, (n, seen.get(key))
        seen[key] = n


def test_skeleton_is_seed_invariant():
    for fam in FAMILIES:
        for n in list(FRAMES)[::11]:
            sigs = [dist.signature(FRAMES[n], fam, seed)["skeleton"]
                    for seed in (11, 4242, 999001)]
            assert sigs[0] == sigs[1] == sigs[2], (n, fam)


def test_distance_axes_are_separable():
    """Same shape different lexicon moves lex, and the reverse moves shape.

    Shape distance between two frames of the same shape is small but not
    exactly zero: a few lexicon roles carry their own preposition ("handled
    by" against "stored in"), and prepositions are closed class, so they
    survive delexicalisation. The separation check below is what matters, and
    `cmd_distance` reports the noise floor and the separation as numbers.
    """
    fam = "substitution_rule"
    a = dist.signature(FRAMES["routing__native"], fam)
    lex_only = dist.signature(FRAMES["depot__native"], fam)
    shape_only = dist.signature(FRAMES["routing__active"], fam)
    d_lex = {"shape": dist.shape_distance(a["skeleton"],
                                          lex_only["skeleton"]),
             "lex": dist.lex_distance(set(a["words"]), set(lex_only["words"]))}
    d_shp = {"shape": dist.shape_distance(a["skeleton"],
                                          shape_only["skeleton"]),
             "lex": dist.lex_distance(set(a["words"]), set(shape_only["words"]))}
    assert d_lex["shape"] < 0.08 and d_lex["lex"] > 0.5, d_lex
    assert d_shp["shape"] > 0.2 and d_shp["lex"] < 0.3, d_shp


def test_shape_noise_floor_is_small():
    """Two frames of one shape differ far less in skeleton than two shapes do.

    Not a strict separation: `postvalue` and `keyphrase` are deliberate
    single-edit shapes sitting closer to `native` than some lexicon swaps do,
    which is the point of having them. The claim is about the bulk.
    """
    fam = "substitution_rule"
    sigs = dist.frame_signatures(sorted(FRAMES), fam)
    same, diff = [], []
    for (a, b), v in dist.pairwise(sigs).items():
        (same if FRAMES[a].shape.name == FRAMES[b].shape.name
         else diff).append(v["shape"])
    med_diff = sorted(diff)[len(diff) // 2]
    assert max(same) < 0.10, max(same)
    assert med_diff > 5 * max(same), (max(same), med_diff)


def test_split_is_disjoint():
    for policy in ("lexicon", "shape", "both"):
        sp = split_frames(policy)
        assert not (set(sp["train"]) & set(sp["test"]))
        assert NATIVE_FRAME in sp["train"]
        assert sp["test"], policy


def test_parser_reads_every_frame():
    from src.frames.parsers import parse_answer, system_and_problems
    for fam in ("substitution_rule", "exception_rule"):
        for n in list(FRAMES)[::5]:
            fr = FRAMES[n]
            for seed in SEEDS[:3]:
                s, problems = system_and_problems(seed, fam)
                pages = "\n\n".join(fr.describe(fam, s))
                for p in problems:
                    got = parse_answer(fr, s, fam, p["key"], pages)
                    assert got == p["answer"], (n, fam, seed, p, got)


def test_named_is_exact_single_choice():
    cands = ["kavor", "mizel", "tubra"]
    assert sc.named("kavor", cands) == ["kavor"]
    assert sc.named("The answer is kavor.", cands) == ["kavor"]
    assert sc.named("kavor or mizel", cands) == ["kavor", "mizel"]
    assert sc.named("kavorish", cands) == []
    assert sc.named("nothing", cands) == []


def test_frame_space_size():
    lex = {f.lexicon.name for f in FRAMES.values()}
    shp = {f.shape.name for f in FRAMES.values()}
    assert len(FRAMES) == len(lex) * len(shp)
    assert len(FRAMES) >= 100
