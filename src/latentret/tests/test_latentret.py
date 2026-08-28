"""Checks on the parts of this experiment that could be silently wrong.

The failure mode worth guarding against is a measurement that looks like the
mechanism working when it is not: a gold label that points at a page that does
not answer the question, a vocabulary that maps the answer to <unk> so every
prediction is wrong for the same reason, a halting distribution that does not
sum to one so the task loss is scaled by an arbitrary number, or an injection
that is wired up but disconnected from the gradient.
"""

from __future__ import annotations

import random

import torch

from src.latentret.data import (GOLD_PAGE, EpisodeStream, corrupted_store,
                                make_episode)
from src.latentret.gate import halting_distribution, ponder_kl
from src.latentret.loss import LossWeights, latentret_loss, noisy_or_retrieval
from src.latentret.model import LatentRetConfig, LatentRetrievalLM
from src.latentret.train import RunConfig, build_model
from src.latentret.vocab import get_vocab, tokenize
from src.skillacq.simple import SIMPLE_FAMILIES


def test_vocab_covers_every_episode():
    vocab = get_vocab()
    for seed in range(500):
        ep = make_episode(seed, seed % 2 == 0)
        assert vocab.unk_id not in ep.prompt
        assert ep.answer != vocab.unk_id
        for doc in ep.docs:
            assert vocab.unk_id not in doc


def test_gold_page_carries_the_answer():
    for seed in range(400):
        ep = make_episode(seed, False)
        assert ep.answer in ep.docs[ep.gold_doc], f"seed {seed} family {ep.family}"


# threshold_rule ends with a worked example that names the upper label, so
# whenever the answer is that label it is readable off a second page. Measured
# over 3000 episodes: 0.511 in threshold_rule, 0.018 and 0.022 in the other two
# families, 0.183 overall. It is a property of the family in src/skillacq, not
# of the episode builder, and it is the reason measure() reports per family.
ANSWER_LEAK_RATE = {"threshold_rule": 0.55, "substitution_rule": 0.06,
                    "exception_rule": 0.06}


def test_answer_leak_rate_is_where_it_is_expected():
    """Only threshold_rule lets the answer be read off a page that is not gold."""
    seen = {f: [0, 0] for f in ANSWER_LEAK_RATE}
    for seed in range(1500):
        ep = make_episode(seed, False)
        seen[ep.family][0] += 1
        seen[ep.family][1] += any(ep.answer in d for i, d in enumerate(ep.docs)
                                  if i != ep.gold_doc)
    for family, (total, leaked) in seen.items():
        assert leaked / total < ANSWER_LEAK_RATE[family], (family, leaked, total)


# The families draw invented words independently from a pool of 400, so a
# system occasionally draws the same word twice and two words that are supposed
# to differ collide. Roughly 2 percent of episodes, which is why the structural
# claims below are rate bounds rather than universals: a claim that held on
# every one of a few hundred seeds would be a claim about luck.
COLLISION_SLACK = 0.05


def test_answer_is_rarely_copyable_from_the_question():
    """A model that echoes a word from the question cannot score above chance."""
    bad = sum(make_episode(s, False).answer in make_episode(s, False).question
              for s in range(400))
    assert bad / 400 < COLLISION_SLACK


def test_foil_is_a_real_alternative():
    """The foil is in the store, not in the prompt, and is not the answer."""
    differs, on_gold, in_prompt = 0, 0, 0
    for seed in range(400):
        ep = make_episode(seed, True)
        differs += ep.foil != ep.answer
        on_gold += ep.foil in ep.docs[ep.gold_doc]
        in_prompt += ep.foil in ep.prompt
        assert any(ep.foil in doc for doc in ep.docs), f"seed {seed}"
    assert differs / 400 > 1 - COLLISION_SLACK
    assert on_gold / 400 < COLLISION_SLACK
    assert in_prompt / 400 < COLLISION_SLACK


def test_the_name_is_not_on_the_gold_page():
    """The system name in the question points at a title page, never the answer.

    So a retriever scoring hits above chance did it on rule content, not on the
    one word the question and the pages most obviously share.
    """
    vocab = get_vocab()
    on_gold, in_question = 0, 0
    for seed in range(300):
        rng = random.Random(seed)
        system = SIMPLE_FAMILIES[rng.choice(sorted(SIMPLE_FAMILIES))](rng)
        name_id = vocab.encode_word(system.name)
        ep = make_episode(seed, False, hard=True)
        in_question += name_id in ep.question
        on_gold += name_id in ep.docs[ep.gold_doc]
    assert in_question == 300
    assert on_gold / 300 < COLLISION_SLACK


def test_hard_distractors_double_the_pages_carrying_the_name():
    vocab = get_vocab()
    matched = 0
    for seed in range(200):
        rng = random.Random(seed)
        system = SIMPLE_FAMILIES[rng.choice(sorted(SIMPLE_FAMILIES))](rng)
        name_id = vocab.encode_word(system.name)
        hard = sum(name_id in doc for doc in make_episode(seed, False, True).docs)
        easy = sum(name_id in doc for doc in make_episode(seed, False, False).docs)
        matched += hard == 2 * easy
    assert matched / 200 > 1 - COLLISION_SLACK


def test_gold_page_is_unique_per_family():
    for seed in range(300):
        ep = make_episode(seed, False)
        assert 0 <= ep.gold_doc < 6
        # The gold page came from the first system, so its index in the
        # shuffled order must have been one of the first three.
        assert GOLD_PAGE[ep.family] in (1, 2)


def test_in_context_prompt_contains_the_gold_page():
    for seed in range(100):
        with_ctx = make_episode(seed, True)
        without = make_episode(seed, False)
        assert len(with_ctx.prompt) > len(without.prompt)
        assert with_ctx.gold_doc == without.gold_doc
        assert with_ctx.answer == without.answer


def test_halting_distribution_sums_to_one():
    for loops in (1, 3, 8):
        logits = torch.randn(16, loops) * 3.0
        probs = halting_distribution(logits)
        assert torch.allclose(probs.sum(-1), torch.ones(16), atol=1e-4)
        assert (probs >= 0).all()
        assert torch.isfinite(ponder_kl(probs))


def test_noisy_or_rewards_any_iteration():
    """One open gate over a confident correct retrieval is enough."""
    gold = torch.zeros(1, dtype=torch.long)
    log_p = torch.log(torch.tensor([[[0.01, 0.99], [0.99, 0.01]]]))
    shut = noisy_or_retrieval(log_p, torch.tensor([[0.0, 0.0]]), gold)
    late = noisy_or_retrieval(log_p, torch.tensor([[0.0, 1.0]]), gold)
    both = noisy_or_retrieval(log_p, torch.tensor([[1.0, 1.0]]), gold)
    assert late < shut
    assert both <= late + 1e-4


def test_collate_marks_the_answer_position():
    vocab = get_vocab()
    stream = EpisodeStream(0, 1000, 8, pool_size=200)
    batch = stream.batch()
    at_pos = batch.prompt.gather(1, batch.ans_pos.view(-1, 1)).squeeze(1)
    assert (at_pos == vocab.a_id).all()


def test_corrupted_store_keeps_shape_and_drops_the_page():
    stream = EpisodeStream(0, 1000, 8, pool_size=200)
    batch = stream.batch()
    bad = corrupted_store(batch)
    assert bad.docs.shape == batch.docs.shape
    b = torch.arange(batch.docs.shape[0])
    changed = (bad.docs[b, batch.gold] != batch.docs[b, batch.gold]).any(-1)
    assert changed.float().mean() > 0.9


def test_forward_shapes_and_gradient_reaches_the_query():
    cfg = RunConfig(steps=1, batch_size=4, loops=3)
    model = build_model(cfg)
    stream = EpisodeStream(0, 1000, 4, pool_size=100)
    batch = stream.batch()
    out = model.episode_forward(batch.prompt, batch.ans_pos, batch.docs,
                                batch.doc_mask, batch.question, batch.question_mask)
    assert out.logits.shape == (4, 3, len(get_vocab()))
    assert out.gate_probs.shape == (4, 3)
    assert out.doc_log_probs.shape == (4, 3, 6)
    loss, stats = latentret_loss(out, batch, LossWeights())
    loss.backward()
    for name in ("query_proj", "doc_proj"):
        grad = getattr(model.retriever, name).weight.grad
        assert grad is not None and grad.abs().sum() > 0, name
    assert model.gate.fc2.weight.grad.abs().sum() > 0
    assert model.injector.wo.weight.grad.abs().sum() > 0


def test_query_modes_all_run():
    cfg = RunConfig(steps=1, batch_size=3, loops=2)
    model = build_model(cfg)
    stream = EpisodeStream(0, 1000, 3, pool_size=100)
    batch = stream.batch()
    seen = []
    for mode in ("latent", "decoded", "question", "none"):
        out = model.episode_forward(batch.prompt, batch.ans_pos, batch.docs,
                                    batch.doc_mask, batch.question,
                                    batch.question_mask, query_mode=mode)
        seen.append(out.doc_log_probs[:, 0])
        assert torch.isfinite(out.doc_log_probs).all()
        assert torch.allclose(out.doc_log_probs.exp().sum(-1),
                              torch.ones_like(out.doc_log_probs[..., 0]), atol=1e-4)
    assert not torch.allclose(seen[0], seen[2])


def test_uniform_mode_is_uniform():
    """query_mode none must score every document identically."""
    cfg = RunConfig(steps=1, batch_size=3, loops=2)
    model = build_model(cfg)
    batch = EpisodeStream(0, 1000, 3, pool_size=100).batch()
    out = model.episode_forward(batch.prompt, batch.ans_pos, batch.docs,
                                batch.doc_mask, batch.question,
                                batch.question_mask, query_mode="none")
    spread = out.doc_log_probs.max(-1).values - out.doc_log_probs.min(-1).values
    assert float(spread.max()) < 1e-4


def test_injection_off_changes_nothing_downstream_of_the_gate():
    cfg = RunConfig(steps=1, batch_size=3, loops=2)
    model = build_model(cfg)
    batch = EpisodeStream(0, 1000, 3, pool_size=100).batch()
    with torch.no_grad():
        on = model.episode_forward(batch.prompt, batch.ans_pos, batch.docs,
                                   batch.doc_mask, batch.question,
                                   batch.question_mask, inject=True)
        off = model.episode_forward(batch.prompt, batch.ans_pos, batch.docs,
                                    batch.doc_mask, batch.question,
                                    batch.question_mask, inject=False)
        zero = model.episode_forward(batch.prompt, batch.ans_pos, batch.docs,
                                     batch.doc_mask, batch.question,
                                     batch.question_mask, gate_override=0.0)
    assert not torch.allclose(on.logits, off.logits)
    assert torch.allclose(off.logits, zero.logits, atol=1e-5)


def test_copy_readout_can_only_reach_the_store():
    """No token outside the six documents may get a finite copy score."""
    cfg = RunConfig(steps=1, batch_size=4, loops=2, readout="copy")
    model = build_model(cfg)
    batch = EpisodeStream(0, 1000, 4, pool_size=100).batch()
    with torch.no_grad():
        out = model.episode_forward(batch.prompt, batch.ans_pos, batch.docs,
                                    batch.doc_mask, batch.question,
                                    batch.question_mask)
    logits = out.logits[:, -1]
    for row in range(4):
        present = set(batch.docs[row][batch.doc_mask[row]].tolist())
        finite = set((logits[row] > torch.finfo(logits.dtype).min / 2)
                     .nonzero().flatten().tolist())
        assert finite <= present, sorted(finite - present)[:5]
        assert int(batch.answer[row]) in present


def test_copy_readout_respects_the_retrieval_distribution():
    """A page the retriever gave no mass to cannot win the copy readout.

    Without this the copy head would read all six documents directly and the
    gate would stop mattering to the task.
    """
    cfg = RunConfig(steps=1, batch_size=4, loops=1, readout="copy")
    model = build_model(cfg)
    batch = EpisodeStream(0, 1000, 4, pool_size=100).batch()
    doc_emb = model.tok_emb(batch.docs)
    state = torch.randn(4, cfg.d_model)
    b = torch.arange(4)
    sharp = torch.full((4, 6), -30.0)
    sharp[b, batch.gold] = 0.0
    away = torch.full((4, 6), 0.0)
    away[b, batch.gold] = -30.0
    with torch.no_grad():
        on = model.copy_head(state, doc_emb, batch.docs, batch.doc_mask, sharp,
                             model.cfg.vocab_size)
        off = model.copy_head(state, doc_emb, batch.docs, batch.doc_mask, away,
                              model.cfg.vocab_size)
    # Only where the answer word is on the gold page and nowhere else. In
    # threshold_rule the worked example repeats the upper label, so half of
    # that family's answers are reachable from a second page and their score
    # cannot depend on the gold page alone. See ANSWER_LEAK_RATE.
    unique = torch.tensor([
        not any(int(batch.answer[r]) in batch.docs[r][d][batch.doc_mask[r][d]]
                for d in range(6) if d != int(batch.gold[r]))
        for r in range(4)])
    gain = on[b, batch.answer] - off[b, batch.answer]
    assert unique.any(), "no clean row in this batch"
    assert (gain[unique] > 5.0).all(), gain.tolist()


def test_retrieval_heads_are_a_small_share_of_the_model():
    model = build_model(RunConfig())
    d = model.describe_latentret()
    assert d["latentret_params"] < 0.5 * d["params_total"]


def test_tokenizer_round_trips_words_and_numbers():
    assert tokenize("A KaVor reading of 42.") == ["a", "kavor", "reading", "of", "42", "."]
