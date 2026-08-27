import random

import pytest

from src.scrub.extractive_qa import (DEFAULT_TYPE_MIX, E2_TYPE_MIX, check_qa,
                                     find_spans, generate_qa, render_qa_trace,
                                     split_sentences)
from src.scrub.scrubber import scrub_text
from src.train.tokenizer import load_tokenizer, train_tokenizer

RAW = (
    "Bramor Corp acquired Tovin Labs in 1987 for 12,500 dollars. "
    "The merger surprised analysts across the region. "
    "Petra Kolm led the negotiation from an office in Drenal. "
    "Her team wrote the contract in nine days. "
    "Tovin Labs had 340 employees and a warehouse near Selvin. "
    "The warehouse stored equipment for the northern route. "
    "Kolm later joined Vantor Group as an adviser. "
    "The group operated 27 depots along the coast. "
    "A junior clerk kept the ledger updated every week. "
    "Selvin remained the busiest port of the province."
)


@pytest.fixture(scope="module")
def passage():
    # Scrub the raw text so the passage is exactly what regime E feeds the
    # generator: synthetic entities and perturbed numbers.
    return scrub_text(RAW, 41).text


@pytest.fixture(scope="module")
def tok_path(tmp_path_factory):
    base = tmp_path_factory.mktemp("qacorpus")
    rng = random.Random(11)
    words = ["the", "of", "in", "for", "led", "acquired", "contract",
             "warehouse", "office", "employees", "sentence", "mention",
             "passage", "which", "does", "who", "what", "when", "how",
             "many", "where", "yes", "no", "domain"]
    corpus = base / "corpus.txt"
    with open(corpus, "w") as fh:
        for _ in range(1200):
            fh.write(" ".join(rng.choices(words, k=10)) + "\n")
    path = base / "tokenizer.json"
    train_tokenizer([str(corpus)], out_path=str(path), vocab_size=1024)
    return str(path)


def test_all_pairs_pass_checker(passage):
    qas = generate_qa(passage, 5, 24)
    assert len(qas) == 24
    for qa in qas:
        assert check_qa(passage, qa)


def test_deterministic_and_seed_sensitive(passage):
    a = generate_qa(passage, 5, 12)
    b = generate_qa(passage, 5, 12)
    c = generate_qa(passage, 6, 12)
    assert a == b
    assert c != a


def test_mix_tracks_default(passage):
    qas = generate_qa(passage, 5, 20)
    counts = {k: 0 for k in DEFAULT_TYPE_MIX}
    for qa in qas:
        counts[qa["type"]] += 1
    assert counts["span_cloze"] == 14
    assert counts["sentence_select"] == 3
    assert counts["existence"] == 3


def test_custom_mix(passage):
    qas = generate_qa(passage, 5, 10, mix={"existence": 1.0})
    assert len(qas) == 10
    assert all(qa["type"] == "existence" for qa in qas)
    with pytest.raises(ValueError):
        generate_qa(passage, 5, 4, mix={"nonsense": 1.0})


def test_cloze_answers_are_verbatim_spans(passage):
    qas = [qa for qa in generate_qa(passage, 5, 24)
           if qa["type"] == "span_cloze"]
    assert qas
    for qa in qas:
        assert qa["answer"] in passage
        assert passage.count(qa["answer"]) == 1
        # Reconstruct the source sentence by string operations alone.
        q, wh, pos = qa["question"], qa["wh"], qa["wh_pos"]
        base = q[:pos] + qa["answer"] + q[pos + len(wh):-1]
        assert any(base + t in passage for t in (".", "!", "?", ""))


def test_wh_phrases_match_span_types(passage):
    spans = find_spans(passage)
    assert {"entity", "number", "noun_phrase"} <= {s["kind"] for s in spans}
    for span in spans:
        if span["kind"] == "entity" and " " in span["text"]:
            assert span["wh"] == "who"
        if span["kind"] == "noun_phrase":
            assert span["wh"] == "what"
        if span["kind"] == "number":
            assert span["wh"] in ("when", "how many")


def test_sentence_select_answers_are_sentences(passage):
    qas = [qa for qa in generate_qa(passage, 5, 24)
           if qa["type"] == "sentence_select"]
    assert qas
    sentences = {passage[s:e] for s, e in split_sentences(passage)}
    for qa in qas:
        assert qa["answer"] in sentences
        assert qa["subject"] in qa["answer"]


def test_existence_no_uses_absent_name(passage):
    qas = [qa for qa in generate_qa(passage, 5, 40, mix={"existence": 1.0})]
    answers = {qa["answer"] for qa in qas}
    assert answers == {"yes", "no"}
    for qa in qas:
        if qa["answer"] == "no":
            assert qa["subject"].lower() not in passage.lower()
        else:
            assert qa["subject"] in passage


def test_checker_rejects_tampering(passage):
    qas = generate_qa(passage, 5, 6)
    for qa in qas:
        bad = dict(qa)
        bad["answer"] = qa["answer"] + "x"
        if bad["type"] == "existence":
            bad["answer"] = "no" if qa["answer"] == "yes" else "yes"
        assert not check_qa(passage, bad)


def test_empty_passage_yields_nothing():
    assert generate_qa("", 5, 4) == []
    assert generate_qa("   \n", 5, 4) == []


def test_trace_round_trip(passage, tok_path):
    tok = load_tokenizer(tok_path)
    qas = generate_qa(passage, 5, 8)
    ids = render_qa_trace(passage, qas, tok)
    text = tok.decode(ids)
    assert text.startswith("<|world|>domain: extractive_qa<|doc|>")
    head, _, rest = text.partition("<|doc|>")
    got_passage, _, qa_text = rest.partition("<|q|>")
    assert got_passage == passage
    blocks = qa_text.split("<|q|>")
    assert len(blocks) == len(qas)
    for block, qa in zip(blocks, qas):
        q_and_a, _, tail = block.partition("<|a|>")
        answer = tail.partition("<|eot|>")[0]
        assert q_and_a == qa["question"]
        assert answer == qa["answer"]
        # The decoded answer is derivable from the decoded passage.
        if qa["type"] == "span_cloze":
            assert answer in got_passage
        if qa["type"] == "sentence_select":
            assert answer in got_passage


def test_recap_items_copy_specifics_verbatim(passage):
    qas = generate_qa(passage, 7, 12, mix={"recap": 1.0})
    assert qas
    for qa in qas:
        assert qa["type"] == "recap"
        assert qa["text"].startswith("The passage states that ")
        assert "?" not in qa["text"]
        assert qa["answer"] in passage
        assert qa["answer"] in qa["text"]
        assert qa["sentence"] in passage
        assert qa["answer"] in qa["sentence"]
        assert check_qa(passage, qa)


def test_recap_prefers_specific_spans(passage):
    qas = generate_qa(passage, 7, 4, mix={"recap": 1.0})
    assert len(qas) == 4
    assert {qa["span_kind"] for qa in qas} <= {"entity", "number"}


def test_recap_checker_rejects_tampering(passage):
    qas = generate_qa(passage, 7, 3, mix={"recap": 1.0})
    for qa in qas:
        bad = dict(qa)
        bad["answer"] = qa["answer"] + "x"
        assert not check_qa(passage, bad)
        bad = dict(qa)
        bad["text"] = qa["text"].replace(qa["answer"], qa["answer"] + "9")
        assert not check_qa(passage, bad)


def test_recap_render_has_no_question_tokens(passage, tok_path):
    tok = load_tokenizer(tok_path)
    qas = generate_qa(passage, 7, 4, mix={"recap": 1.0})
    ids = render_qa_trace(passage, qas, tok)
    sid = tok.special_ids
    assert sid["<|q|>"] not in ids
    assert sid["<|a|>"] not in ids
    assert ids.count(sid["<|eot|>"]) == 1
    text = tok.decode(ids)
    body = text.partition("<|doc|>")[2]
    got_passage, _, recap = body.partition("\nThe passage states that")
    got_passage = got_passage.partition("<|eot|>")[0]
    assert got_passage == passage
    for qa in qas:
        assert qa["answer"] in got_passage
        assert qa["answer"] in "The passage states that" + recap


def test_mixed_trace_renders_recap_before_questions(passage, tok_path):
    tok = load_tokenizer(tok_path)
    qas = generate_qa(passage, 7, 12, mix=E2_TYPE_MIX)
    assert any(qa["type"] == "recap" for qa in qas)
    ids = render_qa_trace(passage, qas, tok)
    text = tok.decode(ids)
    lead = text.find("The passage states that")
    first_q = text.find("<|q|>")
    assert 0 < lead < first_q
    assert "<|a|>" not in text[:first_q]


def test_e2_bias_targets_specific_spans():
    """The required bias measurement: over 200 generated questions under
    the E2 mix, at least 55 percent target a number or a name span, and at
    least 60 percent of span cloze questions do."""
    from src.scrub.scrubber import scrub_text as scrub
    state = {}
    items = []
    for i in range(50):
        p = scrub(RAW, 900 + i).text
        items.extend(generate_qa(p, (7, i), 6, mix=E2_TYPE_MIX, state=state))
    sample = items[:200]
    assert len(sample) == 200
    specific = sum(1 for qa in sample
                   if qa.get("span_kind") in ("entity", "number"))
    assert specific / len(sample) >= 0.55
    clozes = [qa for qa in sample if qa["type"] == "span_cloze"]
    assert clozes
    cloze_specific = sum(1 for qa in clozes
                         if qa["span_kind"] in ("entity", "number"))
    assert cloze_specific / len(clozes) >= 0.60


def test_e2_state_tracks_type_mix_across_passages():
    from src.scrub.scrubber import scrub_text as scrub
    state = {}
    items = []
    for i in range(50):
        p = scrub(RAW, 700 + i).text
        items.extend(generate_qa(p, (9, i), 6, mix=E2_TYPE_MIX, state=state))
    total = len(items)
    shares = {t: sum(1 for qa in items if qa["type"] == t) / total
              for t in E2_TYPE_MIX}
    assert abs(shares["span_cloze"] - 0.60) < 0.05
    assert abs(shares["sentence_select"] - 0.15) < 0.05
    assert abs(shares["existence"] - 0.10) < 0.05
    assert abs(shares["recap"] - 0.15) < 0.05
