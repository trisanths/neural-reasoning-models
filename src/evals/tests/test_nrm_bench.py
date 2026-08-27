"""Tests for the NRM task benchmark.

Models are scripted step functions, so every metric is exercised through
the real decode loop and the real retrieval serving: the harness cannot
pass these by accident. PlannedStepFn reads the visible trace and decides
what to emit next, which makes it stateless across calls and safe to reuse
across items and conditions.
"""

import json
import random

import numpy as np
import pytest

from src.evals import nrm_bench as nb
from src.retrieval_web.exa import MOCK_FIXTURES, MockExa
from src.worldgen.engine import generate_episodes

SUBJECTS = ["Varek", "Domel", "Kastor", "Lomira", "Petrin", "Solvag",
            "Tibran", "Quorel", "Mirand", "Helvet", "Norvik", "Ostrel",
            "Palver", "Rukan", "Sellim", "Tarvod"]
PLACES = ["Trelso", "Umbrav", "Vintor", "Wellac", "Xandor", "Yorvel",
          "Zelmat", "Arkano", "Brontel", "Cervak", "Drovin", "Elbram",
          "Fornt", "Grellon", "Hastel", "Ivrock"]
CARGO = [("amber", "resin"), ("basalt", "gravel"), ("cobalt", "ingots"),
         ("verdant", "timber")]


def make_bundle(n=14, seed=3):
    """A bundle of distinctive prose documents, the shape the scrubbed-web
    episode builder expects."""
    rng = random.Random(seed)
    docs = []
    for i in range(n):
        subject = f"{SUBJECTS[i % len(SUBJECTS)]} " \
                  f"{PLACES[(i + 5) % len(PLACES)]}or"
        place = PLACES[i % len(PLACES)]
        c1, c2 = CARGO[i % len(CARGO)]
        year = 1900 + 7 * i + rng.randint(0, 4)
        crates = 100 + 13 * i + rng.randint(0, 6)
        docs.append(
            f"{subject} shipped {crates} crates of {c1} {c2} to "
            f"{place}ia in {year}. The harbor ledger listed the cargo "
            f"beside the customs desk. A clerk from {place}ia counted "
            f"every crate at the gate.")
    return docs


def onehot(vocab_size, token_id):
    row = np.zeros(vocab_size, dtype=np.float32)
    row[token_id] = 1.0
    return row


class PlannedStepFn:
    """Scripted model: n_rounds retrieve-result rounds, then an answer.

    Stateless between calls. The next token is decided from the visible
    trace alone, exactly as a real model would see it, so the harness runs
    the same code path it runs for a checkpoint.
    """

    def __init__(self, tokenizer, query, answer: str, n_rounds: int = 1,
                 echo_chunk: bool = False):
        self.tok = tokenizer
        self.sid = tokenizer.special_ids
        self.vocab_size = tokenizer.vocab_size
        # query None means write the question itself as the query, which is
        # what a well behaved model does on a one-hop item.
        self.query_ids = None if query is None else tokenizer.encode(query)
        self.answer_ids = tokenizer.encode(answer) if answer else []
        self.n_rounds = n_rounds
        self.echo_chunk = echo_chunk

    def __call__(self, tokens):
        tokens = list(tokens)
        sid = self.sid

        def last(tid):
            for i in range(len(tokens) - 1, -1, -1):
                if tokens[i] == tid:
                    return i
            return -1

        q = last(sid["<|q|>"])
        tail = tokens[q + 1:]
        i_ret = last(sid["<|retrieve|>"]) - q - 1
        i_res = last(sid["<|result|>"]) - q - 1
        if i_ret >= 0 and i_ret > i_res:
            if self.query_ids is None:
                first_ret = tail.index(sid["<|retrieve|>"])
                query_ids = tail[:first_ret]
            else:
                query_ids = self.query_ids
            emitted = tail[i_ret + 1:]
            if len(emitted) < len(query_ids):
                return onehot(self.vocab_size, query_ids[len(emitted)])
            return onehot(self.vocab_size, sid["<|result|>"])
        if tail.count(sid["<|result|>"]) < self.n_rounds:
            return onehot(self.vocab_size, sid["<|retrieve|>"])
        i_ans = last(sid["<|a|>"]) - q - 1
        if i_ans < 0:
            return onehot(self.vocab_size, sid["<|a|>"])
        if self.echo_chunk:
            want = tail[i_res + 1:i_ans]
        else:
            want = self.answer_ids
        emitted = tail[i_ans + 1:]
        if len(emitted) < len(want):
            return onehot(self.vocab_size, want[len(emitted)])
        return onehot(self.vocab_size, sid["<|eot|>"])


def ctx_for(tok, step_fn, **kwargs):
    return nb.RunnerContext(step_fn=step_fn, tokenizer=tok, max_rounds=2,
                            max_new_tokens=96, label="scripted", **kwargs)


@pytest.fixture(scope="module")
def bench_episodes():
    return list(generate_episodes(90210, 12))


@pytest.fixture(scope="module")
def synthetic_items(bench_episodes):
    return nb.build_synthetic_suite(bench_episodes, unanswerable_every=3)


# ------------------------------------------------------- suite building


def test_synthetic_suite_covers_every_task(synthetic_items):
    tasks = {item.task for item in synthetic_items}
    for required in ("single_hop", "multi_hop", "temporal", "counting",
                     "arbitration", "unanswerable"):
        assert required in tasks, f"{required} missing from {sorted(tasks)}"
    assert len({item.item_id for item in synthetic_items}) == \
        len(synthetic_items)


def test_multi_hop_items_have_two_to_four_hops(synthetic_items):
    hops = [item.n_hops for item in synthetic_items
            if item.task == "multi_hop"]
    assert hops and all(2 <= h <= 4 for h in hops)


def test_multi_hop_evidence_chain_exceeds_the_answer(synthetic_items):
    multi = [i for i in synthetic_items if i.task == "multi_hop"]
    assert any(len(i.evidence_strings) > 1 for i in multi)


def test_every_answerable_item_binds_documents(synthetic_items):
    for item in synthetic_items:
        assert item.documents, item.item_id
        if not item.unanswerable:
            assert item.oracle_docs, item.item_id


def test_unanswerable_binding_drops_the_supporting_documents(
        bench_episodes, synthetic_items):
    by_id = {ep["episode_id"]: ep for ep in bench_episodes}
    unans = [i for i in synthetic_items if i.task == "unanswerable"]
    assert unans
    for item in unans:
        episode = by_id[item.item_id.split("-unans-")[0]]
        question = next(q for q in episode["questions"]
                        if q["text"] == item.question)
        needed = set(question["derivation"])
        kept_texts = {d["text"] for d in item.documents}
        for doc in episode["documents"]:
            touched = set(doc.get("supports", [])) | \
                set(doc.get("contradicts", []))
            if touched & needed:
                assert doc["text"] not in kept_texts
        assert item.golds == ["unknown"]
        assert item.trap_strings == [question["answer"]]
        assert not any(question["answer"] in t for t in kept_texts)


def test_counting_items_count_the_documents_they_cite(synthetic_items):
    counting = [i for i in synthetic_items if i.task == "counting"]
    assert counting
    for item in counting:
        assert item.golds[0] == str(item.meta["count"])
        assert len(item.evidence_strings) == item.meta["count"]
        assert len(item.oracle_docs) >= item.meta["count"]


def test_temporal_items_name_both_candidates(synthetic_items):
    temporal = [i for i in synthetic_items if i.task == "temporal"]
    assert temporal
    for item in temporal:
        assert item.distractor_strings
        assert item.golds[0] not in item.distractor_strings
        assert len(item.oracle_docs) >= 2


def test_arbitration_items_carry_a_contradicted_value(synthetic_items):
    arb = [i for i in synthetic_items if i.task == "arbitration"]
    assert arb
    for item in arb:
        assert item.distractor_strings
        assert item.golds[0] not in item.distractor_strings


def test_scrubbed_web_suite_answers_are_spans_of_bound_documents():
    bundles = [make_bundle(14, seed=s) for s in range(4)]
    items = nb.build_scrubbed_web_suite(bundles, seed=7,
                                        unanswerable_every=3)
    assert items
    answerable = [i for i in items if not i.unanswerable]
    assert answerable
    for item in answerable:
        texts = [d["text"] for d in item.documents]
        assert any(item.golds[0] in t for t in texts)
        assert item.oracle_docs and item.golds[0] in item.oracle_docs[-1]
    unans = [i for i in items if i.unanswerable]
    assert unans
    for item in unans:
        assert not any(item.trap_strings[0] in d["text"]
                       for d in item.documents)


def test_scrubbed_web_suite_is_deterministic():
    bundles = [make_bundle(14, seed=s) for s in range(3)]
    first = nb.build_scrubbed_web_suite(bundles, seed=11)
    second = nb.build_scrubbed_web_suite(bundles, seed=11)
    assert [i.to_dict() for i in first] == [i.to_dict() for i in second]


def test_real_web_suite_loads_authored_questions():
    items = nb.load_real_web_suite()
    answerable = [i for i in items if not i.unanswerable]
    assert len(answerable) >= 120
    assert len({i.item_id for i in items}) == len(items)
    for item in items:
        assert item.web and item.suite == "real_web"
        if item.unanswerable:
            assert item.golds == ["unknown"] and not item.oracle_docs
        else:
            assert item.oracle_docs
            assert any(g.lower() in item.oracle_docs[0].lower()
                       for g in item.golds)


# --------------------------------------------------------- single items


def episode_item(items, task):
    return next(i for i in items if i.task == task)


def test_retrieval_condition_serves_and_grounds(tok, synthetic_items):
    item = episode_item(synthetic_items, "single_hop")
    step = PlannedStepFn(tok, item.question, item.golds[0], n_rounds=1)
    record = nb.score_record(item, nb.run_item(
        item, ctx_for(tok, step), "retrieval"))
    assert record["n_rounds"] == 1
    assert record["n_queries"] == 1
    assert record["evidence_tokens"] > 0
    assert record["correct"]
    assert record["answer_in_evidence"]
    assert record["gold_in_evidence"]
    assert record["grounded_correct"]
    assert not record["unsupported_correct"]
    assert record["rounds"][0]["query"] == item.question


def test_no_retrieval_condition_serves_nothing(tok, synthetic_items):
    item = episode_item(synthetic_items, "single_hop")
    step = PlannedStepFn(tok, item.question, item.golds[0], n_rounds=1)
    record = nb.score_record(item, nb.run_item(
        item, ctx_for(tok, step), "no_retrieval"))
    assert record["stop_reason"] == "max_rounds"
    assert record["n_rounds"] == 0
    assert record["n_queries"] == 1
    assert record["unserved_retrieve"]
    assert record["evidence_tokens"] == 0
    assert not record["answer_in_evidence"]


def test_oracle_context_puts_the_gold_document_in_the_prompt(
        tok, synthetic_items):
    item = episode_item(synthetic_items, "single_hop")
    step = PlannedStepFn(tok, "", item.golds[0], n_rounds=0)
    prompt = nb.build_prompt(item, tok, "oracle_context")
    assert tok.special_ids["<|doc|>"] in prompt
    assert tok.special_ids["<|doc|>"] not in nb.build_prompt(
        item, tok, "retrieval")
    record = nb.score_record(item, nb.run_item(
        item, ctx_for(tok, step), "oracle_context"))
    assert record["correct"]
    assert record["evidence_tokens"] > 0
    assert record["answer_in_evidence"]
    assert record["n_rounds"] == 0


def test_free_generation_is_correct_but_ungrounded(tok, synthetic_items):
    item = episode_item(synthetic_items, "single_hop")
    step = PlannedStepFn(tok, "", item.golds[0], n_rounds=0)
    record = nb.score_record(item, nb.run_item(
        item, ctx_for(tok, step), "retrieval"))
    assert record["correct"]
    assert record["n_rounds"] == 0
    assert not record["answer_in_evidence"]
    assert record["unsupported_correct"]
    assert not record["grounded_correct"]


def test_chunk_echo_is_grounded_and_gold_bearing(tok, synthetic_items):
    """A model that answers by echoing the served chunk is grounded even
    though its answer is longer than the gold."""
    item = episode_item(synthetic_items, "single_hop")
    step = PlannedStepFn(tok, item.question, "", n_rounds=1, echo_chunk=True)
    record = nb.score_record(item, nb.run_item(
        item, ctx_for(tok, step, ), "retrieval"))
    assert record["answer_in_evidence"]
    assert record["contains"] == nb.contains_answer(record["answer"],
                                                    item.golds[0])


def test_wrong_answer_scores_zero_everywhere(tok, synthetic_items):
    item = episode_item(synthetic_items, "single_hop")
    step = PlannedStepFn(tok, item.question, "zzqqxx", n_rounds=1)
    record = nb.score_record(item, nb.run_item(
        item, ctx_for(tok, step), "retrieval"))
    assert not record["correct"] and not record["exact_match"]
    assert not record["answer_in_evidence"]
    assert record["gold_in_evidence"]


def test_counting_accepts_digits_and_words(tok, synthetic_items):
    item = episode_item(synthetic_items, "counting")
    for form in (str(item.meta["count"]), nb.NUMBER_WORDS[item.meta["count"]]):
        step = PlannedStepFn(tok, item.question, form, n_rounds=1)
        record = nb.score_record(item, nb.run_item(
            item, ctx_for(tok, step), "retrieval"))
        assert record["correct"], form


def test_arbitration_distractor_is_named_as_such(tok, synthetic_items):
    item = episode_item(synthetic_items, "arbitration")
    step = PlannedStepFn(tok, item.question, item.distractor_strings[0],
                         n_rounds=1)
    record = nb.score_record(item, nb.run_item(
        item, ctx_for(tok, step), "retrieval"))
    assert not record["correct"]
    assert record["answered_distractor"]
    block = nb.aggregate([record])
    assert block["arbitration_distractor_rate"] == 1.0
    assert block["arbitration_accuracy"] == 0.0


def test_abstention_on_unanswerable_scores_correct(tok, synthetic_items):
    item = episode_item(synthetic_items, "unanswerable")
    step = PlannedStepFn(tok, item.question, "unknown", n_rounds=1)
    record = nb.score_record(item, nb.run_item(
        item, ctx_for(tok, step), "retrieval"))
    assert record["abstained"] and record["correct"]
    assert not record["answered_trap"]
    block = nb.aggregate([record])
    assert block["abstention_rate_unanswerable"] == 1.0
    assert block["confabulation_rate"] == 0.0
    assert block["explicit_abstention_unanswerable"] == 1.0


def test_confabulating_the_withheld_answer_is_counted(tok, synthetic_items):
    item = episode_item(synthetic_items, "unanswerable")
    step = PlannedStepFn(tok, item.question, item.trap_strings[0], n_rounds=1)
    record = nb.score_record(item, nb.run_item(
        item, ctx_for(tok, step), "retrieval"))
    assert not record["correct"] and not record["abstained"]
    assert record["answered_trap"]
    block = nb.aggregate([record])
    assert block["confabulation_rate"] == 1.0
    assert block["trap_rate_unanswerable"] == 1.0


def test_empty_answer_counts_as_abstention_but_not_explicit(tok,
                                                            synthetic_items):
    item = episode_item(synthetic_items, "unanswerable")
    step = PlannedStepFn(tok, item.question, "", n_rounds=1)
    record = nb.score_record(item, nb.run_item(
        item, ctx_for(tok, step), "no_retrieval"))
    assert record["answer_empty"] and record["abstained"]
    block = nb.aggregate([record])
    assert block["explicit_abstention_unanswerable"] == 0.0
    assert block["empty_answer_rate"] == 1.0


def test_over_abstention_on_answerable_items(tok, synthetic_items):
    item = episode_item(synthetic_items, "single_hop")
    step = PlannedStepFn(tok, item.question, "unknown", n_rounds=1)
    record = nb.score_record(item, nb.run_item(
        item, ctx_for(tok, step), "retrieval"))
    assert not record["correct"]
    assert nb.aggregate([record])["over_abstention_answerable"] == 1.0


def test_multi_hop_evidence_completeness(tok, synthetic_items):
    """Completeness is stricter than a gold hit: one served chunk can carry
    the answer while the chain stays incomplete."""
    item = episode_item(synthetic_items, "multi_hop")
    step = PlannedStepFn(tok, item.question, item.golds[0], n_rounds=1)
    one = nb.score_record(item, nb.run_item(
        item, ctx_for(tok, step), "retrieval"))
    full = nb.score_record(item, nb.run_item(
        item, ctx_for(tok, step), "oracle_context"))
    assert full["evidence_complete"]
    assert not (one["evidence_complete"] and not one["gold_in_evidence"])


# ------------------------------------------------------------ run_bench


def test_run_bench_reports_conditions_suites_tasks_and_gaps(
        tok, synthetic_items):
    items = synthetic_items[:8]
    step = PlannedStepFn(tok, "capacity route", "unknown", n_rounds=1)
    results = nb.run_bench(items, ctx_for(tok, step))
    assert set(results["by_condition"]) == set(nb.CONDITIONS)
    for block in results["by_condition"].values():
        assert block["pooled"]["n_items"]
        assert "synthetic_world" in block["by_suite"]
        assert block["by_task"]
    gaps = results["gaps"]
    assert gaps["paired_items"] > 0
    assert gaps["oracle_minus_retrieval"] == pytest.approx(
        gaps["accuracy_oracle_context"] - gaps["accuracy_retrieval"])
    assert json.loads(json.dumps(results))["n_records"] == \
        results["n_records"]


def test_run_bench_skips_the_oracle_control_for_unanswerable_items(
        tok, synthetic_items):
    items = [i for i in synthetic_items if i.task == "unanswerable"][:2]
    step = PlannedStepFn(tok, "q", "unknown", n_rounds=0)
    results = nb.run_bench(items, ctx_for(tok, step))
    assert "oracle_context" not in results["by_condition"]
    assert results["gaps"] == {}


def test_run_bench_is_deterministic(tok, synthetic_items):
    items = synthetic_items[:6]
    step = PlannedStepFn(tok, "route capacity", "unknown", n_rounds=1)

    def strip(results):
        return [{k: v for k, v in r.items() if k != "seconds"}
                for r in results["records"]]

    assert strip(nb.run_bench(items, ctx_for(tok, step))) == \
        strip(nb.run_bench(items, ctx_for(tok, step)))


def test_format_report_renders_every_condition(tok, synthetic_items):
    step = PlannedStepFn(tok, "route", "unknown", n_rounds=1)
    results = nb.run_bench(synthetic_items[:6], ctx_for(tok, step))
    text = nb.format_report(results)
    assert "pooled by condition" in text
    assert "suite: synthetic_world" in text
    assert "paired controls" in text
    for condition in nb.CONDITIONS:
        assert condition in text


# ------------------------------------------------------------- web tier


def test_budgeted_client_caches_and_stops_at_the_budget(tmp_path):
    query = next(iter(MOCK_FIXTURES))
    client = nb.BudgetedSearchClient(MockExa(), tmp_path / "cache.json",
                                     budget=1)
    first = client.search(query, num_results=5)
    second = client.search(query, num_results=5)
    assert first == second
    assert client.live_calls == 1 and client.cache_hits == 1
    with pytest.raises(nb.ExaBudgetExhausted):
        client.search("byte level bpe tokenizer", num_results=5)

    warm = nb.BudgetedSearchClient(MockExa(), tmp_path / "cache.json",
                                   budget=0)
    assert warm.search(query, num_results=5) == first
    assert warm.live_calls == 0


def test_web_item_runs_against_the_tier(tok, tmp_path):
    item = nb.BenchItem(
        item_id="w1", suite="real_web", task="single_hop",
        question="okapi bm25 ranking function",
        golds=["ranking function"], preamble=nb.REAL_WEB_PREAMBLE,
        oracle_docs=["BM25 is a ranking function used by search engines."],
        web=True)
    client = nb.BudgetedSearchClient(MockExa(), tmp_path / "cache.json",
                                     budget=8)
    factory = nb.make_web_index_factory(client, tok, chunk_tokens=64,
                                        num_results=3)
    step = PlannedStepFn(tok, item.question, item.golds[0], n_rounds=1)
    record = nb.score_record(item, nb.run_item(
        item, ctx_for(tok, step, web_index_factory=factory), "retrieval"))
    assert record["n_rounds"] == 1
    assert record["rounds"][0]["url"]
    assert record["correct"] and record["answer_in_evidence"]
    assert client.live_calls == 1


def test_budget_exhaustion_stops_web_items_and_is_recorded(tok, tmp_path):
    items = [
        nb.BenchItem(item_id=f"w{i}", suite="real_web", task="single_hop",
                     question=q, golds=["ranking"],
                     preamble=nb.REAL_WEB_PREAMBLE,
                     oracle_docs=["a ranking function"], web=True)
        for i, q in enumerate(MOCK_FIXTURES)
    ]
    client = nb.BudgetedSearchClient(MockExa(), tmp_path / "cache.json",
                                     budget=1)
    factory = nb.make_web_index_factory(client, tok, chunk_tokens=64)
    step = PlannedStepFn(tok, None, "ranking", n_rounds=1)
    results = nb.run_bench(items, ctx_for(tok, step, web_index_factory=factory),
                           conditions=("retrieval",))
    assert client.live_calls == 1
    assert results["skipped_for_budget"]["retrieval"] >= 1
    assert results["n_records"] < len(items)


def test_web_items_need_a_factory(tok):
    item = nb.load_real_web_suite(limit=1)[0]
    step = PlannedStepFn(tok, "q", "a", n_rounds=0)
    with pytest.raises(ValueError):
        nb.run_item(item, ctx_for(tok, step), "retrieval")


# ------------------------------------------------------------ scoring


def test_is_abstention_recognizes_declines_not_hedged_prose():
    assert nb.is_abstention("unknown")
    assert nb.is_abstention("  Unknown. ")
    assert nb.is_abstention("")
    assert nb.is_abstention("I do not know")
    assert nb.is_abstention("the acquirer is unknown")
    assert not nb.is_abstention("unknown company acquired Reyner")
    assert not nb.is_abstention("Ostrel Holdings")


def test_number_forms():
    assert nb.number_forms(3) == ["3", "three"]
    assert nb.number_forms(40) == ["40"]


def test_aggregate_of_nothing_is_empty():
    assert nb.aggregate([]) == {"n_items": 0}
