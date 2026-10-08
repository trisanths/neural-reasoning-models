"""The partitioned objective: layout, masking, and where the gradient is zero.

The claim under test is stronger than "evidence tokens are masked". It is that
no evidence position contributes anything to the gradient, which is checked by
reading the gradient of the loss with respect to the logits at every position
rather than by reading the mask that was supposed to produce it.
"""

import pytest
import torch

from src.train.model import TransformerLM
from src.train.pointer_data import (IGNORE_INDEX, PointerCollator,
                                    PointerExample, build_examples,
                                    examples_from_episode, find_token_runs,
                                    pointer_stats, procedure_episode,
                                    skill_episode, worldgen_examples)
from src.train.tests.evidence_fixtures import StubTokenizer, synthetic_episode
from src.train.tests.pointer_fixtures import (IdTokenizer, copy_task_batch,
                                              copy_task_examples, probe_config,
                                              real_tokenizer, requires_tokenizer)

SIMPLE_FAMILIES = ["threshold_rule", "substitution_rule", "exception_rule"]
ARITHMETIC_FAMILIES = ["binary_op", "units", "procedure"]


def collator(max_seq_len: int = 256, copy_scope: str = "evidence") -> PointerCollator:
    return PointerCollator(IdTokenizer(), max_seq_len=max_seq_len, copy_scope=copy_scope)


# ---------------- layout ----------------


def test_sequence_layout_and_authored_span():
    tokenizer = IdTokenizer()
    example = PointerExample(
        document_ids=[[100, 101], [102]],
        question_ids=[200, 201],
        answer_ids=[300],
    )
    row = collator().encode_example(example)
    sid = tokenizer.special_ids
    assert row["inputs"] == [
        sid["<|doc|>"], 100, 101, sid["<|doc|>"], 102,
        sid["<|q|>"], 200, 201, sid["<|a|>"], 300,
    ]
    # Evidence positions are the document tokens, never the <|doc|> markers.
    assert row["evidence_positions"] == [1, 2, 4]
    assert row["evidence_ids"] == [100, 101, 102]
    # The <|a|> position predicts the answer, the answer position predicts eot.
    assert row["authored_positions"] == [8, 9]
    assert row["authored_targets"] == [300, sid["<|eot|>"]]


def test_targets_are_ignore_index_everywhere_but_the_authored_span():
    batch = copy_task_batch(n_docs=4)
    supervised = batch.targets != IGNORE_INDEX
    assert int(supervised.sum()) == int(batch.answer_lengths.sum())
    for b in range(batch.input_ids.shape[0]):
        for pos in batch.evidence_positions[b].tolist():
            if pos >= 0:
                assert not bool(supervised[b, pos]), pos
        rows = supervised[b].nonzero().flatten().tolist()
        assert rows == batch.authored_positions[b].tolist()


def test_prefix_scope_adds_the_question_and_evidence_scope_does_not():
    example = PointerExample(
        document_ids=[[100, 101]], question_ids=[200, 201], answer_ids=[201],
    )
    narrow = collator(copy_scope="evidence").encode_example(example)
    wide = collator(copy_scope="prefix").encode_example(example)
    assert narrow["evidence_ids"] == [100, 101]
    assert wide["evidence_ids"] == [100, 101, 200, 201]
    assert not narrow["copy_available"]
    assert wide["copy_available"]


def test_the_example_may_override_the_collator_scope():
    example = PointerExample(
        document_ids=[[100]], question_ids=[200], answer_ids=[200],
        copy_scope="prefix",
    )
    assert collator(copy_scope="evidence").encode_example(example)["copy_available"]


def test_truncation_drops_whole_documents_and_never_the_answer():
    example = PointerExample(
        document_ids=[[10] * 8, [11] * 8, [12] * 8],
        question_ids=[200, 201], answer_ids=[300, 301],
    )
    row = collator(max_seq_len=24).encode_example(example)
    assert len(row["inputs"]) <= 24
    assert row["evidence_ids"] == [10] * 8 + [11] * 8
    assert row["authored_targets"][:2] == [300, 301]
    with pytest.raises(ValueError):
        collator(max_seq_len=4).encode_example(example)


def test_padding_rows_are_gathered_safely_and_then_ignored():
    rows = collator()([
        PointerExample(document_ids=[[100]], question_ids=[200], answer_ids=[300]),
        PointerExample(document_ids=[[100, 101, 102]], question_ids=[200, 201],
                       answer_ids=[300, 301, 302]),
    ])
    assert int(rows.evidence_positions[0].min()) == -1
    assert bool((rows.authored_positions >= 0).all())
    padded = rows.authored_targets == IGNORE_INDEX
    assert bool(padded[0, -1]) and not bool(padded[1].any())
    assert rows.answer_lengths.tolist() == [2, 4]


def test_collation_is_deterministic():
    a = copy_task_batch(n_docs=6, seed=3)
    b = copy_task_batch(n_docs=6, seed=3)
    assert torch.equal(a.input_ids, b.input_ids)
    assert torch.equal(a.evidence_positions, b.evidence_positions)


def test_find_token_runs_finds_every_occurrence():
    assert find_token_runs([1, 2, 3, 2, 3], [2, 3]) == [1, 3]
    assert find_token_runs([1, 2], [1, 2, 3]) == []
    assert find_token_runs([1, 2], []) == []


# ---------------- the gradient is zero on the evidence ----------------


def test_evidence_positions_receive_exactly_zero_gradient():
    """Read it off the logits, not off the mask that was meant to cause it."""
    batch = copy_task_batch(n_docs=4)
    torch.manual_seed(0)
    model = TransformerLM(probe_config())
    x = model.trunk(batch.input_ids)
    logits = model.lm_head(x)
    logits.retain_grad()
    loss = torch.nn.functional.cross_entropy(
        logits.float().view(-1, model.cfg.vocab_size), batch.targets.reshape(-1),
    )
    loss.backward()
    per_position = logits.grad.abs().sum(-1)
    for b in range(batch.input_ids.shape[0]):
        for pos in batch.evidence_positions[b].tolist():
            if pos >= 0:
                assert float(per_position[b, pos]) == 0.0, (b, pos)
        for pos in batch.authored_positions[b].tolist():
            assert float(per_position[b, pos]) > 0.0, (b, pos)


def test_the_same_holds_on_the_pointer_path():
    batch = copy_task_batch(n_docs=4)
    torch.manual_seed(0)
    model = TransformerLM(probe_config(pointer={}))
    x = model.trunk(batch.input_ids)
    logits = model.lm_head(x)
    logits.retain_grad()
    states, ids, mask = model._resolve_evidence(
        x, batch.input_ids, batch.evidence_positions, None, None, None
    )
    out = model.pointer(x, states, ids, mask, vocab_logits=logits)
    loss = torch.nn.functional.nll_loss(
        out.log_probs.reshape(-1, model.cfg.vocab_size), batch.targets.reshape(-1),
        ignore_index=IGNORE_INDEX,
    )
    loss.backward()
    per_position = logits.grad.abs().sum(-1)
    for b in range(batch.input_ids.shape[0]):
        for pos in batch.evidence_positions[b].tolist():
            if pos >= 0:
                assert float(per_position[b, pos]) == 0.0, (b, pos)


def test_evidence_still_shapes_the_answer_it_is_never_asked_to_predict():
    """Zero gradient at evidence positions is not the same as evidence being
    inert: change the bank and the supervised loss changes."""
    batch = copy_task_batch(n_docs=4)
    torch.manual_seed(0)
    model = TransformerLM(probe_config(pointer={}))
    model.eval()
    scrambled = batch.input_ids.clone()
    live = batch.evidence_positions[0][batch.evidence_positions[0] >= 0]
    scrambled[0, live] = scrambled[0, live.flip(0)]
    with torch.no_grad():
        _, before = model(batch.input_ids, batch.authored_targets,
                          evidence_positions=batch.evidence_positions,
                          select=batch.authored_positions)
        _, after = model(scrambled, batch.authored_targets,
                         evidence_positions=batch.evidence_positions,
                         select=batch.authored_positions)
    assert not torch.equal(before, after)


# ---------------- building examples from the episode families ----------------


@requires_tokenizer
@pytest.mark.parametrize("family", SIMPLE_FAMILIES)
def test_simple_families_are_copyable_out_of_the_defining_page(family):
    """The measured failure lives here: the answer is a nonsense word that the
    page states and the vocabulary has no reason to prefer."""
    tokenizer = real_tokenizer()
    examples = build_examples(tokenizer, range(8), families=[family], n_problems=4)
    assert len(examples) == 32
    stats = pointer_stats(examples, PointerCollator(tokenizer, max_seq_len=2048))
    assert stats["answer_aligned_rate"] == 1.0, stats
    assert stats["copy_available_rate"] == 1.0, stats
    assert stats["span_copyable_rate"] == 1.0, stats
    assert stats["mean_evidence_tokens"] > 100


@requires_tokenizer
@pytest.mark.parametrize("family", SIMPLE_FAMILIES)
def test_the_naive_tokenization_gives_the_copy_head_nothing_to_point_at(family):
    """The measured reason answer alignment is not optional.

    A byte level BPE folds the leading space into the first token, so the
    answer encoded on its own is spelled in ids the page does not contain. The
    answer is verbatim in the page as text and absent from it as targets.
    """
    tokenizer = real_tokenizer()
    examples = build_examples(tokenizer, range(8), families=[family], n_problems=4)
    naive = pointer_stats(
        examples, PointerCollator(tokenizer, max_seq_len=2048, align_answers=False))
    aligned = pointer_stats(examples, PointerCollator(tokenizer, max_seq_len=2048))
    assert naive["span_copyable_rate"] < 0.5, naive
    assert aligned["span_copyable_rate"] == 1.0, aligned


@requires_tokenizer
def test_alignment_picks_the_spelling_the_page_uses():
    tokenizer = real_tokenizer()
    example = build_examples(tokenizer, [5], families=["substitution_rule"],
                             n_problems=1)[0]
    collator = PointerCollator(tokenizer, max_seq_len=2048)
    row = collator.encode_example(example)
    assert row["answer_aligned"]
    assert row["answer_ids"] == tokenizer.encode(" " + example.answer_text)
    assert row["answer_ids"] != tokenizer.encode(example.answer_text)
    assert find_token_runs(row["evidence_ids"], row["answer_ids"])
    # The authored targets are the aligned spelling, not the standalone one.
    assert row["authored_targets"][:len(row["answer_ids"])] == row["answer_ids"]


@requires_tokenizer
def test_arithmetic_families_are_the_control():
    """Their answers are computed, so a copy head has much less to point at.

    The comparison is the claim, not the absolute number: a two digit result
    does turn up in a page of worked examples now and then, and that is a fact
    about arithmetic rather than a flaw in the metric.
    """
    tokenizer = real_tokenizer()
    collator = PointerCollator(tokenizer, max_seq_len=2048)
    computed = pointer_stats(
        build_examples(tokenizer, range(12), families=ARITHMETIC_FAMILIES, n_problems=4),
        collator)
    stated = pointer_stats(
        build_examples(tokenizer, range(12), families=SIMPLE_FAMILIES, n_problems=4),
        collator)
    assert stated["span_copyable_rate"] == 1.0, stated
    assert computed["span_copyable_rate"] < 0.5, computed


@requires_tokenizer
def test_procedure_families_need_the_prefix_scope():
    tokenizer = real_tokenizer()
    collator = PointerCollator(tokenizer, max_seq_len=2048)
    examples = build_examples(tokenizer, range(6), kind="procedure", n_problems=4)
    assert all(e.copy_scope == "prefix" for e in examples)
    wide = pointer_stats(examples, collator)
    narrow = pointer_stats(
        build_examples(tokenizer, range(6), kind="procedure", n_problems=4,
                       copy_scope="evidence"),
        collator)
    assert wide["copy_available_rate"] > narrow["copy_available_rate"], (wide, narrow)


def test_worldgen_episodes_build_the_same_way():
    tokenizer = StubTokenizer(vocab_size=4096)
    episode = synthetic_episode(n_docs=10, n_questions=3)
    examples = worldgen_examples([episode], tokenizer)
    assert len(examples) == 3
    stats = pointer_stats(examples, PointerCollator(tokenizer, max_seq_len=512))
    assert stats["copy_available_rate"] == 1.0
    assert stats["mean_authored_tokens"] >= 2


def test_every_document_reaches_the_evidence_region_distractors_included():
    tokenizer = StubTokenizer(vocab_size=4096)
    episode = skill_episode(7, family="substitution_rule", n_problems=2)
    assert len(episode["documents"]) > 3  # the distractor system's pages too
    examples = examples_from_episode(episode, tokenizer)
    row = PointerCollator(tokenizer, max_seq_len=2048).encode_example(examples[0])
    expected = sum(len(tokenizer.encode(d["text"])) for d in episode["documents"])
    assert len(row["evidence_positions"]) == expected


def test_document_order_is_seeded_and_stable():
    tokenizer = StubTokenizer(vocab_size=4096)
    episode = procedure_episode(3)
    a = examples_from_episode(episode, tokenizer, shuffle_seed=11)[0]
    b = examples_from_episode(episode, tokenizer, shuffle_seed=11)[0]
    c = examples_from_episode(episode, tokenizer, shuffle_seed=12)[0]
    assert a.document_ids == b.document_ids
    assert a.document_ids != c.document_ids


def test_stats_on_an_empty_set():
    assert pointer_stats([], collator()) == {"examples": 0}


def test_rejects_an_unknown_copy_scope():
    with pytest.raises(ValueError):
        PointerCollator(IdTokenizer(), max_seq_len=64, copy_scope="everything")
    with pytest.raises(ValueError):
        collator().encode_example(
            PointerExample(document_ids=[[1]], question_ids=[2], answer_ids=[3],
                           copy_scope="everything")
        )


def test_copy_task_examples_hold_the_answer_exactly_once():
    examples = copy_task_examples(n_docs=6)
    for i, example in enumerate(examples):
        flat = [t for doc in example.document_ids for t in doc]
        assert flat.count(example.answer_ids[0]) == 1
        assert example.answer_ids[0] not in example.question_ids
