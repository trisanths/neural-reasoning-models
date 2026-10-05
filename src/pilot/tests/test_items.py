import json
import random

from src.mathgen.bench import Guard
from src.pilot.grade import canary_reply, grade
from src.pilot.items import (CONDITIONS, SEED_BASE, SMOKE_OFFSET,
                             check_seed_ranges, load_items, manifest_ranges,
                             naive_screen, naive_values, prompt_hash)
from src.pilot.skills import PILOT_FAMILIES, SkillUniverse


def test_manifest_ranges_cover_base_index_and_episode_seeds(manifest_dir):
    ranges = manifest_ranges(manifest_dir)
    whats = {(r["manifest"], r["what"]) for r in ranges}
    assert ("regime_e3.json", "worldgen_index") in whats
    idx = [r for r in ranges if r["what"] == "worldgen_index"
           and r["manifest"] == "regime_e3.json"][0]
    assert idx["hi"] == 398 * 100000


def test_pilot_seed_bases_clear_every_manifest_range(manifest_dir):
    ranges = manifest_ranges(manifest_dir)
    for offset in (0, SMOKE_OFFSET):
        planned = {f: (b + offset, b + offset + 2000) for f, b in SEED_BASE.items()}
        assert check_seed_ranges(planned, ranges) == []
    assert check_seed_ranges({"x": (10, 20)}, ranges)
    assert check_seed_ranges({"x": (51515, 51516)}, ranges)


def test_naive_screen_catches_ordinary_arithmetic():
    class P:
        text = "In the Vor calculus, evaluate 3 & (4 # 5)."
        answer = "27"
    assert naive_screen(P) == "naive_arithmetic"
    P.answer = "88"
    assert 88 not in naive_values(P.text) and naive_screen(P) is None
    P.answer = "kavor"
    assert naive_screen(P) is None


def test_smoke_set_has_every_family_and_condition(smoke_built):
    items = smoke_built["items"]
    fams = {it["family"] for it in items}
    assert fams == {"refuniverse", "algebra", *PILOT_FAMILIES}
    assert sorted(it["level"] for it in items if it["family"] == "refuniverse") \
        == list(range(1, 9))
    for it in items:
        assert set(it["prompts"]) == set(CONDITIONS) == set(it["pages"])
        for c, p in it["prompts"].items():
            assert it["prompt_hashes"][c] == prompt_hash(p)
            assert p.rstrip().endswith("Answer:")
            assert it["question"] in p


def test_every_item_has_a_sibling_that_disagrees(smoke_built):
    for it in smoke_built["items"]:
        assert it["sibling_answer"] != it["answer"], it["item_id"]
        assert it["pages"]["sibling"], it["item_id"]
        assert all(pg["text"] == "" for pg in it["pages"]["blank"])
        assert it["pages"]["closed_book"] == []


def test_floors_follow_the_answer_space(smoke_built):
    for it in smoke_built["items"]:
        assert abs(it["floor"] - 1.0 / it["answer_space"]) < 1e-12
        if it["family"] == "refuniverse":
            assert 97 <= it["modulus"] <= 131
            assert it["answer_kind"] == "int"
            assert 0 <= int(it["answer"]) < it["modulus"]


def test_the_answer_is_absent_from_blank_and_closed_book_prompts(smoke_built):
    for it in smoke_built["items"]:
        for c in ("closed_book", "blank"):
            body = it["prompts"][c].split("Problem.\n", 1)[0]
            assert it["answer"] not in body.split()


def test_canary_scores_zero_on_the_smoke_set(smoke_built):
    for it in smoke_built["items"]:
        assert not grade(canary_reply(it), it)["correct"]


def test_written_items_round_trip_with_a_manifest(smoke_items_path):
    items = load_items(smoke_items_path)
    assert items
    man = json.load(open(smoke_items_path.replace(".jsonl", "") + ".manifest.json"))
    assert man["n_items"] == len(items)
    assert man["smoke"] is True


def test_rule_family_labels_are_balanced_in_a_larger_draw():
    from src.pilot.items import _fill

    for fam in ("threshold_rule", "exception_rule", "substitution_rule"):
        items, *_ = _fill(fam, {None: 10}, 940_000_000, "src.pilot.skills",
                          {"family": fam}, per_level=8, max_seeds=200,
                          per_universe=2, balance_labels=True)
        labels = [it["candidates"].index(it["answer"]) for it in items]
        n_labels = len(items[0]["candidates"])
        assert len(items) == 10
        assert max(labels.count(i) for i in range(n_labels)) <= -(-10 // n_labels)


def test_skill_universe_passes_the_guard_and_its_sibling_reads_differently():
    for fam in PILOT_FAMILIES:
        u = SkillUniverse(940_100_000, fam)
        sib = u.sibling(1)
        g = Guard(u)
        probs = u.problems(1, 20, random.Random(0))
        assert probs
        for p in probs:
            assert u.reference_answer(p) == p.answer
        assert any(sib.reference_answer(p) != p.answer for p in probs)
        assert any(g.check(p).ok for p in probs)
        assert sib.system.name == u.system.name


def test_the_item_set_does_not_depend_on_the_hash_seed():
    import os
    import subprocess
    import sys

    code = ("import hashlib, json; from src.pilot.items import build_items; "
            "b = build_items(smoke=True); "
            "print(hashlib.sha256(json.dumps(b['items'], sort_keys=True)"
            ".encode()).hexdigest())")
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))))
    digests = set()
    for seed in ("1", "2", "3"):
        env = {**os.environ, "PYTHONHASHSEED": seed}
        out = subprocess.run([sys.executable, "-c", code], cwd=root, env=env,
                             capture_output=True, text=True, check=True)
        digests.add(out.stdout.strip())
    assert len(digests) == 1
