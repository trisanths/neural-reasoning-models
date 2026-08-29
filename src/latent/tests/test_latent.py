"""Tests for the latent reasoning channel.

The things that would be invisible in an accuracy number and fatal to it: a
compressed pass that lands on the wrong positions, a cached decoder that does
not agree with a full recompute once it is injecting its own embeddings, a
label that quietly supervises a latent position, and a stream that has drifted
away from the arms it is supposed to be matched against.
"""

from __future__ import annotations

import pytest
import torch

from src.latent import data as ldata
from src.latent.chain import run_chain, span_loss
from src.latent.core import (LatentHead, compress_index, gather_at,
                             measure_scale, scatter_at, trunk_from_embeds,
                             with_depth_recurrence)
from src.latent.infer import (LatentPolicy, latent_generate,
                              latent_generate_slow)
from src.opgraph.data import IGNORE, direct_prompt, training_examples
from src.opgraph.plan import (answer_text, parse_plan, run_plan,
                              serialize_plan, trace_text)
from src.rl.sampler import CachedPolicy
from src.train.model import ModelConfig, TransformerLM

VOCAB = 64
EOT, ANS, LAT = 63, 62, 61


class FakeTok:
    """Enough of the tokenizer interface for the decoder tests, and no more."""

    names = {"<|eot|>": EOT, "<|a|>": ANS, "<|pg0|>": LAT, "<|result|>": 60}

    def token_id(self, name):
        return self.names[name]

    def encode(self, text):
        return [1 + (ord(c) % 55) for c in text]

    def decode(self, ids):
        return " ".join(str(int(i)) for i in ids)


def tiny_model(seed=0):
    torch.manual_seed(seed)
    cfg = ModelConfig(vocab_size=VOCAB, d_model=32, n_layers=2, n_heads=4,
                      d_ff=64, max_seq_len=128)
    return TransformerLM(cfg).eval()


# --------------------------------------------------------------- the trunk

def test_trunk_from_embeds_matches_trunk():
    m = tiny_model()
    ids = torch.randint(0, VOCAB, (3, 17))
    a = m.trunk(ids)
    b = trunk_from_embeds(m, m.tok_emb(ids))
    assert torch.equal(a, b)


def test_trunk_from_embeds_uses_the_looped_core():
    m = tiny_model()
    looped, report = with_depth_recurrence(m, prelude=1, core=1, coda=0, loops=3)
    looped.eval()
    assert report["effective_depth"] == 1 + 1 * 3
    ids = torch.randint(0, VOCAB, (2, 11))
    a = looped.trunk(ids)
    b = trunk_from_embeds(looped, looped.tok_emb(ids))
    assert torch.equal(a, b)
    # the loop count is a runtime dial and the trunk honours it
    with looped.loops_override(1):
        c = trunk_from_embeds(looped, looped.tok_emb(ids))
    assert not torch.equal(a, c)


# ------------------------------------------------------------ the plumbing

def test_compress_index_endpoints():
    first = torch.tensor([3, 5])
    width, n = 12, 4
    full = compress_index(first, n, n, width)
    assert torch.equal(full, torch.arange(width).view(1, -1).expand(2, -1))
    none = compress_index(first, n, 0, width)
    assert none.shape == (2, width - n)
    # row 0: prompt is 0,1,2 then the four slots are dropped and 7.. follows
    assert none[0].tolist() == [0, 1, 2, 7, 8, 9, 10, 11]
    assert none[1].tolist() == [0, 1, 2, 3, 4, 9, 10, 11]


def test_compress_index_middle():
    first = torch.tensor([4])
    idx = compress_index(first, 4, 2, 12)
    assert idx[0].tolist() == [0, 1, 2, 3, 4, 5, 8, 9, 10, 11]


def test_scatter_and_gather_round_trip():
    emb = torch.zeros(2, 6, 4)
    vec = torch.arange(8.0).view(2, 4)
    out = scatter_at(emb, torch.tensor([1, 4]), vec)
    assert torch.equal(gather_at(out, torch.tensor([1, 4])), vec)
    assert out.sum() == vec.sum()


# ------------------------------------------------------------------- head

def test_latent_head_starts_as_the_identity():
    h = LatentHead(8, slots=3, proj="none", scale=2.0)
    x = torch.randn(2, 8)
    assert torch.allclose(h(x, 0), x * 2.0)
    assert torch.allclose(h(x, 99), x * 2.0)  # past the last slot, last row
    lin = LatentHead(8, slots=3, proj="linear", scale=1.0)
    assert torch.allclose(lin(x, 0), x, atol=1e-6)
    assert lin.num_params() == 3 * 16 + 64


def test_measure_scale_is_a_ratio():
    m = tiny_model()
    ids = torch.randint(0, VOCAB, (2, 9))
    s = measure_scale(m, ids)
    assert s > 0 and s < 1e6


# ------------------------------------------------------------------ labels

def test_no_label_ever_lands_on_a_latent_position():
    tok = FakeTok()
    e = ldata.encode(tok, "prompt here", "ans 12", n_latent=3, max_len=256)
    fl, n = e.first_latent, e.n_latent
    for i in range(fl, fl + n + 1):        # the slots and the closing <|a|>
        assert e.labels[i] == IGNORE
    assert e.ids[fl:fl + n] == [LAT] * n
    assert e.ids[fl + n] == ANS
    assert e.labels[fl + n + 1] != IGNORE
    assert e.ids[-1] == EOT and e.labels[-1] == EOT


def test_supervision_starts_after_the_latent_segment():
    tok = FakeTok()
    e = ldata.encode(tok, "abc", "ans 4", n_latent=2, max_len=64)
    src, tgt = ldata.supervised_pairs(e)
    assert min(src) == e.first_latent + e.n_latent
    assert len(src) == len(tgt) == len(tok.encode(" ans 4")) + 1


def test_induction_examples_carry_no_latent_segment():
    """The opgraph arm's induction half rides in the same stream untouched."""
    tok = FakeTok()
    e = ldata.encode(tok, "page text <|a|>", "(defop @ (x y) x)", 0, 256,
                     kind="induce", add_answer_token=False)
    assert e.n_latent == 0
    src, _ = ldata.supervised_pairs(e)
    assert min(src) == e.first_latent - 1
    packed = ldata.collate([e, e])
    assert packed["n_latent"] == 0


def test_collate_rejects_a_mixed_batch():
    tok = FakeTok()
    a = ldata.encode(tok, "abc", "ans 1", 2, 64)
    b = ldata.encode(tok, "abcd", "ans 2", 3, 64)
    with pytest.raises(ValueError):
        ldata.collate([a, b])


def test_encode_returns_none_over_max_len():
    tok = FakeTok()
    assert ldata.encode(tok, "abcdefghij", "ans 1", 4, 8) is None


# -------------------------------------------------------------- the stream

def test_episodes_match_the_direct_arm_exactly():
    """The latent stream must be the arms' stream, question for question."""
    for seed in (0, 1, 7, 41):
        eps = ldata.training_episodes(seed)
        ref = training_examples(seed, "direct")
        assert len(eps) == len(ref)
        for ep, (prompt, gold) in zip(eps, ref):
            assert direct_prompt(ep.item.world, ep.item.text, ep.keys) == prompt
            assert ep.item.gold == gold


def test_latent_prompt_is_the_direct_prompt_with_result_in_place_of_a():
    ep = ldata.training_episodes(3)[0]
    direct = direct_prompt(ep.item.world, ep.item.text, ep.keys)
    latent = ldata.latent_answer_prompt(ep.item.world, ep.item.text, ep.keys)
    assert direct.endswith("<|a|>")
    assert latent == direct[: -len("<|a|>")] + "<|result|>"


def test_stage_curriculum_removes_written_chunks_from_the_front():
    ep = ldata.training_episodes(11)[1]
    steps, tail = ldata.chunks_of(trace_text(ep.item.plan, ep.item.world.ops))
    assert ldata.answer_target(ep, 0).startswith(steps[0])
    assert ldata.answer_target(ep, len(steps)) == tail
    assert tail.startswith("ans ")


def test_gold_plans_execute_to_the_gold_answer():
    """The oracle_both check: if this fails nothing downstream means anything."""
    for seed in (0, 5, 19):
        for ep in ldata.training_episodes(seed):
            plan = parse_plan(serialize_plan(ep.item.plan))
            assert answer_text(run_plan(plan, ep.item.world.ops)) == ep.item.gold


# ------------------------------------------------------------------- chain

def _batch(tok, n_latent, rows=3):
    enc = [ldata.encode(tok, f"prompt number {i} here", "ans 12", n_latent, 128)
           for i in range(rows)]
    return ldata.collate(enc)


def test_chain_loss_at_zero_latents_equals_the_arms_loss():
    """With no latent segment the objective must be the arms' objective."""
    m = tiny_model()
    head = LatentHead(m.cfg.d_model, 2)
    tok = FakeTok()
    b = _batch(tok, 0)
    out = run_chain(m, head, b)
    ids = b["ids"]
    labels = torch.full_like(ids, IGNORE)
    for i in range(ids.shape[0]):
        for p, t in zip(b["sel"][i].tolist(), b["tgt"][i].tolist()):
            if t != IGNORE:
                labels[i, p + 1] = t
    _, ref = m(ids[:, :-1], labels[:, 1:])
    assert torch.allclose(out.loss, ref, atol=1e-5)


def test_chain_pass_and_position_counters():
    m = tiny_model()
    head = LatentHead(m.cfg.d_model, 8)
    tok = FakeTok()
    for r in (0, 1, 4):
        b = _batch(tok, r, rows=2)
        out = run_chain(m, head, b)
        assert out.cost.passes == r + 1
        assert out.cost.reason_passes == r
        width = b["ids"].shape[1]
        want = sum(2 * (width - r + j) for j in range(r + 1))
        assert out.cost.positions == want
        assert out.cost.layer_apps == want * m.cfg.n_layers


def test_chain_backprop_reaches_the_head():
    m = tiny_model()
    head = LatentHead(m.cfg.d_model, 4)
    tok = FakeTok()
    out = run_chain(m, head, _batch(tok, 3))
    out.loss.backward()
    assert head.film.grad is not None
    assert head.film.grad.abs().sum() > 0


def test_ponder_objective_produces_a_distribution():
    from src.latentret.gate import RetrievalGate
    m = tiny_model()
    head = LatentHead(m.cfg.d_model, 4)
    gate = RetrievalGate(m.cfg.d_model)
    out = run_chain(m, head, _batch(FakeTok(), 3), gate=gate)
    assert out.halt_probs.shape == (3, 4)
    assert torch.allclose(out.halt_probs.sum(1), torch.ones(3), atol=1e-4)
    assert out.ponder is not None and float(out.ponder) >= 0.0


def test_span_loss_ignores_padding():
    m = tiny_model()
    h = torch.randn(2, 6, m.cfg.d_model)
    sel = torch.tensor([[1, 2], [1, 0]])
    tgt = torch.tensor([[5, 6], [7, IGNORE]])
    a = span_loss(m, h, sel, tgt)
    rows = span_loss(m, h, sel, tgt, rows=True)
    assert rows.shape == (2,)
    assert torch.isfinite(a)


# ----------------------------------------------------------- the decoders

def test_latent_policy_matches_cached_policy_with_no_injection():
    m = tiny_model()
    prompts = [[3, 4, 5, 6], [7, 8, 9]]
    a = CachedPolicy(m, "cpu", max_len=32, temperature=0.0)
    b = LatentPolicy(m, "cpu", max_len=32, temperature=0.0)
    ta, tb = a.begin(prompts), b.begin(prompts)
    assert ta == tb
    assert torch.allclose(a.last_logits, b.last_logits, atol=1e-5)
    for _ in range(4):
        ta, tb = a.advance(ta), b.advance(tb)
        assert ta == tb
    assert b.last_hidden.shape == (2, m.cfg.d_model)


def test_cached_latent_decoding_matches_full_recompute():
    m = tiny_model(seed=3)
    head = LatentHead(m.cfg.d_model, slots=4, proj="linear", scale=0.7)
    torch.manual_seed(5)
    with torch.no_grad():
        head.film.normal_(0.0, 0.05)
    tok = FakeTok()
    prompts = ["question one", "question two here"]
    fast, cost = latent_generate(m, head, tok, prompts, r_steps=3, max_new=6,
                                 device="cpu", batch_size=2)
    slow = latent_generate_slow(m, head, tok, prompts, r_steps=3, max_new=6,
                                device="cpu")
    assert fast == slow
    assert cost.reason_passes == 3 * len(prompts)
    assert cost.prompt_passes == len(prompts)
    assert cost.layers_per_pass == m.cfg.n_layers


def test_decode_counters_add_up():
    m = tiny_model(seed=4)
    head = LatentHead(m.cfg.d_model, slots=8)
    tok = FakeTok()
    _, cost = latent_generate(m, head, tok, ["a", "b", "c"], r_steps=5,
                              max_new=4, device="cpu", batch_size=3)
    per = cost.per_example()
    assert per["examples"] == 3
    assert per["reason_passes_per_example"] == 5
    assert per["reason_layer_apps_per_example"] == 5 * m.cfg.n_layers
    # one forced <|a|> round plus at most max_new decode rounds
    assert 1 <= per["decode_passes_per_example"] <= 5
    assert cost.total_seconds >= 0.0


def test_r_is_a_runtime_parameter():
    """The same weights answer at any R without being rebuilt."""
    m = tiny_model(seed=6)
    head = LatentHead(m.cfg.d_model, slots=4)
    tok = FakeTok()
    seen = {}
    for r in (0, 1, 2, 8):
        out, cost = latent_generate(m, head, tok, ["x y z"], r_steps=r,
                                    max_new=4, device="cpu")
        seen[r] = cost.reason_passes
    assert seen == {0: 0, 1: 1, 2: 2, 8: 8}


def test_latent_policy_refuses_the_looped_core():
    m = tiny_model()
    looped, _ = with_depth_recurrence(m, 1, 1, 0, 3)
    with pytest.raises(NotImplementedError):
        LatentPolicy(looped, "cpu", max_len=16)


def test_group_batches_are_full_and_shuffled():
    pool = list(range(20))
    gen = ldata.group_batches(pool, 4, key=lambda x: x, rng_seed=2)
    first = [next(gen) for _ in range(5)]
    assert all(len(b) == 4 for b in first)
    assert sorted(x for b in first for x in b) == pool


def test_fit_decay_separates_flat_from_a_cliff():
    from src.latent.eval import fit_decay
    depths = [1, 2, 3, 4, 5, 8]
    flat = fit_decay(depths, [0.6, 0.59, 0.6, 0.58, 0.59, 0.6])
    cliff = fit_decay(depths, [1.0, 0.5, 0.25, 0.02, 0.0, 0.0])
    assert abs(flat["log_slope_per_depth"]) < 0.05
    assert cliff["log_slope_per_depth"] < -0.5
    assert flat["first_depth_below_0.1"] is None
    assert cliff["first_depth_below_0.1"] == 4
