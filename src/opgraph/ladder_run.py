"""Decoding the six plan representations, and scoring what comes back.

Induction is not touched here. Every condition induces its operators through
`src.opgraph.run.induce_worlds`, with the same prompt and the same greedy
decode the original arms used, so the only thing that varies down the ladder is
how the plan is written.

Three decoders live here.

  plain      one generation per question, for the english, symbolic, opcode and
             typed forms
  goalstack  the same, with an obligation state kept outside the model. The
             state is written into the sequence by the decoder, and the tokens
             that end the plan are removed from the distribution while any
             obligation is open, so termination is a fact about the state
             rather than a token the model may choose
  slots      a fixed graph of slots whose fields are predicted in parallel and
             committed by confidence over several passes, then executed in
             topological order
"""

from __future__ import annotations

import re
from collections import Counter, deque
from dataclasses import dataclass, field

import torch

from src.opgraph.opdef import OpError
from src.opgraph.plan import PlanError, answer_text, run_plan
from src.opgraph.vocab import (F_WIDTH, MAX_REGS, Obligations, RepError, T_END,
                               T_MASK, T_RET, canonical, decode_plan,
                               declarations_agree, decode_typed_full,
                               encode_plan, field_domain, lex,
                               rep_plan_prompt, row_field_positions,
                               slot_row_ids, token_name, well_typed)
from src.rl.sampler import PAD_TOKEN, CachedPolicy, sample_from_logits

EOT = "<|eot|>"


# ------------------------------------------------------------------ decoding

class TokenGenerator:
    """Batched decoding that hands back token ids, with an optional hook.

    Ids rather than text, because the dedicated tokens are what the later
    representations are made of and a text round trip is one more place for
    them to be mangled. The text is returned alongside for the sample dumps.
    """

    def __init__(self, model, tok, device="cuda", batch_size: int = 16,
                 temperature: float = 0.0, top_k: int = 0, seed: int = 0):
        self.model = model
        self.tok = tok
        self.device = device
        self.batch_size = batch_size
        self.temperature = float(temperature)
        self.top_k = int(top_k)
        self.seed = seed
        self.eot_id = tok.token_id(EOT)

    def generate(self, prompts, max_new: int = 192, hooks=None):
        out = []
        for i in range(0, len(prompts), self.batch_size):
            hs = hooks[i:i + self.batch_size] if hooks else None
            out.extend(self._batch(prompts[i:i + self.batch_size], max_new, hs))
        return out

    def _batch(self, prompts, max_new, hooks):
        ids = [self.tok.encode(p) for p in prompts]
        width = max(len(x) for x in ids)
        cap = min(width + max_new + 2, self.model.cfg.max_seq_len)
        policy = CachedPolicy(self.model, self.device, max_len=cap,
                              temperature=self.temperature, top_k=self.top_k,
                              seed=self.seed)
        policy.begin(ids)
        gen = [[] for _ in ids]
        done = [False] * len(ids)
        for _ in range(max_new):
            logits = policy.last_logits.clone()
            free = torch.argmax(logits.float(), dim=-1).tolist()
            for i in range(len(ids)):
                if done[i] or hooks is None or hooks[i] is None:
                    continue
                ban = hooks[i].banned()
                if ban:
                    if free[i] in ban:
                        hooks[i].binds += 1
                    logits[i, ban] = float("-inf")
            picked = sample_from_logits(logits, self.temperature, self.top_k,
                                        policy.generator).tolist()
            step = []
            for i in range(len(ids)):
                if done[i]:
                    step.append(PAD_TOKEN)
                    continue
                h = hooks[i] if hooks else None
                forced = h.forced() if h else None
                t = forced if forced is not None else int(picked[i])
                if forced is None and t == self.eot_id:
                    done[i] = True
                    step.append(PAD_TOKEN)
                    continue
                gen[i].append(t)
                step.append(t)
                if h is not None:
                    h.push(t, forced is not None)
                    if h.finished():
                        done[i] = True
            if all(done):
                break
            policy.advance(step)
        return [(g, self.tok.decode(g).strip()) for g in gen]


class GoalHook:
    """The obligation state, kept outside the model and enforced on the sampler.

    `banned` removes the two tokens that can end a plan while any obligation is
    open. `forced` writes the current state into the sequence at every
    instruction boundary, which is what the goalstack arm is trained to read.

    If an instruction comes back unparseable the state can no longer be
    tracked, so the constraint is released for that item rather than left to
    stall the decoder against the step cap. Both counts are reported.
    """

    def __init__(self, tok, ops, item, flags=None):
        self.tok = tok
        self.ops = ops
        self.ob = Obligations.for_item(item, ops, **(flags or {}))
        self.pending = deque(tok.encode(" " + self.ob.annotation()))
        self.cur: list[int] = []
        self.binds = 0
        self.instructions = 0
        self.released = False
        self.done = False
        self.end_id = tok.token_id(T_END)
        self.ban_ids = [tok.token_id(T_RET), tok.token_id(EOT)]

    def forced(self):
        return self.pending.popleft() if self.pending else None

    def banned(self):
        if self.released or self.done or self.ob.resolved():
            return None
        return self.ban_ids

    def push(self, token: int, was_forced: bool) -> None:
        if was_forced:
            return
        self.cur.append(token)
        if token != self.end_id:
            return
        toks = lex(self.tok.decode(self.cur))
        self.cur = []
        self.instructions += 1
        names = [token_name(t) for t in toks]
        if not names or names[0] not in ("apply", "ret"):
            self._release()
            return
        if names[0] == "ret":
            self.done = True
            return
        if "to" not in names:
            self._release()
            return
        i_to = names.index("to")
        args = []
        for t, n in zip(toks[4:i_to], names[4:i_to]):
            m = re.fullmatch(r"r(\d+)", n)
            if m:
                args.append(("reg", int(m.group(1))))
            elif n == "vtrue":
                args.append(("val", True))
            elif n == "vfalse":
                args.append(("val", False))
            elif re.fullmatch(r"-?\d+", t):
                args.append(("val", int(t)))
        dest = self.ob.applied
        if i_to + 1 < len(names):
            md = re.fullmatch(r"r(\d+)", names[i_to + 1])
            if md:
                dest = int(md.group(1))
        self.ob.apply_step(dest, args)
        if self.instructions >= MAX_REGS:
            self._release()
            return
        self.pending.extend(self.tok.encode(" " + self.ob.annotation()))

    def _release(self) -> None:
        self.released = True
        self.done = True

    def finished(self) -> bool:
        return self.done


def _goal_text(ids, tok) -> str:
    return tok.decode(ids).strip()


# --------------------------------------------------------------- slot decoding

@dataclass
class SlotRun:
    fields: list
    rounds: int
    changed: int
    in_domain: int
    total: int


class SlotDecoder:
    """Mask-predict over the slot graph, committed by confidence.

    Every field is a categorical variable over its own domain, so the argmax is
    taken inside that domain. How often the unrestricted argmax already fell in
    the domain is reported, because that is how much the restriction is doing.
    """

    def __init__(self, model, tok, device="cuda", batch_size: int = 8,
                 rounds: int = 3):
        self.model = model
        self.tok = tok
        self.device = device
        self.batch_size = batch_size
        self.rounds = rounds
        self.domains = [[tok.token_id(n) for n in field_domain(i)]
                        for i in range(F_WIDTH)]
        self.mask_id = tok.token_id(T_MASK)

    def run(self, prompts) -> list[SlotRun]:
        order = sorted(range(len(prompts)), key=lambda i: len(self.tok.encode(prompts[i])))
        out: list[SlotRun | None] = [None] * len(prompts)
        group: list[int] = []
        glen = None
        for i in order:
            n = len(self.tok.encode(prompts[i]))
            if glen is not None and (n != glen or len(group) >= self.batch_size):
                for j, r in zip(group, self._batch([prompts[k] for k in group])):
                    out[j] = r
                group = []
            glen = n
            group.append(i)
        if group:
            for j, r in zip(group, self._batch([prompts[k] for k in group])):
                out[j] = r
        return out

    def _batch(self, prompts) -> list[SlotRun]:
        ids0 = [self.tok.encode(p) for p in prompts]
        plen = len(ids0[0])
        b = len(ids0)
        committed = [[None] * F_WIDTH for _ in range(b)]
        history = [[[None] * F_WIDTH for _ in range(b)]]
        changed = [0] * b
        in_domain = [0] * b
        total = [0] * b
        last = [None] * b
        for r in range(self.rounds):
            seq = []
            for i in range(b):
                row = list(ids0[i])
                for rr in range(r + 1):
                    row.extend(self._row_ids(history[rr][i]))
                seq.append(row)
            ids = torch.tensor(seq, dtype=torch.long, device=self.device)
            with torch.no_grad():
                if self.device.startswith("cuda"):
                    with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                        logits, _ = self.model(ids)
                else:
                    logits, _ = self.model(ids)
            pos = row_field_positions(plen, r)
            probs = torch.softmax(logits[:, [p - 1 for p in pos]].float(), dim=-1)
            free = torch.argmax(probs, dim=-1)
            picks = []
            confs = []
            for f in range(F_WIDTH):
                dom = torch.tensor(self.domains[f], device=self.device)
                sub = probs[:, f].index_select(1, dom)
                best = torch.argmax(sub, dim=-1)
                picks.append(dom[best])
                confs.append(sub.gather(1, best[:, None]).squeeze(1))
            pick = torch.stack(picks, dim=1).tolist()
            conf = torch.stack(confs, dim=1).tolist()
            for i in range(b):
                for f in range(F_WIDTH):
                    total[i] += 1
                    if int(free[i, f]) in self.domains[f]:
                        in_domain[i] += 1
            want = F_WIDTH if r == self.rounds - 1 else \
                int(F_WIDTH * (r + 1) / self.rounds)
            for i in range(b):
                cand = [(conf[i][f], f) for f in range(F_WIDTH)
                        if committed[i][f] is None]
                cand.sort(reverse=True)
                need = max(0, want - sum(1 for v in committed[i] if v is not None))
                for _, f in cand[:need]:
                    committed[i][f] = pick[i][f]
                snap = tuple(pick[i])
                if last[i] is not None and snap != last[i]:
                    changed[i] += 1
                last[i] = snap
            history.append([list(committed[i]) for i in range(b)])
        return [SlotRun([self._name(v) for v in committed[i]], self.rounds,
                        changed[i], in_domain[i], total[i]) for i in range(b)]

    def _row_ids(self, assignment) -> list[int]:
        names = [self._name(v) if v is not None else T_MASK for v in assignment]
        ids, _ = slot_row_ids(self.tok, names,
                              {i for i, v in enumerate(assignment) if v is None})
        return ids

    def _name(self, tid):
        if tid is None:
            return T_MASK
        return self.tok.decode([int(tid)])


# ------------------------------------------------------------------- scoring

@dataclass
class Cell:
    n: int = 0
    correct: int = 0
    parsed: int = 0
    typed: int = 0
    exact: int = 0
    parsed_wrong: int = 0
    declared_ok: int = 0
    reasons: Counter = field(default_factory=Counter)
    # Already-final numbers, not counts: as_dict passes them through untouched.
    extra: dict = field(default_factory=dict)
    samples: list = field(default_factory=list)

    def as_dict(self) -> dict:
        n = max(1, self.n)
        d = {"n": self.n,
             "acc": round(self.correct / n, 4),
             "plan_parses": round(self.parsed / n, 4),
             "well_typed": round(self.typed / n, 4),
             "exact_gold_plan": round(self.exact / n, 4),
             "parsed_but_wrong": round(self.parsed_wrong / n, 4),
             "reasons": dict(self.reasons)}
        if self.declared_ok:
            d["declarations_agree"] = round(self.declared_ok / n, 4)
        if self.extra:
            d["extra"] = {k: round(v, 4) if isinstance(v, float) else v
                          for k, v in self.extra.items()}
        if self.samples:
            d["samples"] = self.samples
        return d


def plan_outputs(rep, gen, slot_dec, items, ops_by_world, use_gold_ops,
                 max_new: int = 192, goal_flags=None):
    """Whatever the model wrote for each item, in this representation."""
    ops_for = (lambda it: it.world.ops) if use_gold_ops else \
        (lambda it: ops_by_world[it.world.seed].ops)
    prompts = [rep_plan_prompt(rep, ops_for(it), it.text) for it in items]
    if rep == "slots":
        runs = slot_dec.run(prompts)
        return [(r.fields, "") for r in runs], runs
    if rep == "goalstack":
        hooks = [GoalHook(gen.tok, ops_for(it), it, goal_flags) for it in items]
        outs = gen.generate(prompts, max_new=max_new, hooks=hooks)
        return [(t, t) for _, t in outs], hooks
    outs = gen.generate(prompts, max_new=max_new)
    return [(t, t) for _, t in outs], None


def score_cell(rep, items, written, ops_by_world, use_gold_plan, use_gold_ops,
               side=None, keep: int = 3) -> Cell:
    """Grade one (condition, kind, depth) cell with its plan level diagnostics."""
    c = Cell()
    for k, it in enumerate(items):
        ops = it.world.ops if use_gold_ops else ops_by_world[it.world.seed].ops
        c.n += 1
        if use_gold_plan:
            try:
                obj = encode_plan(rep, it.plan, it.world.ops, it)
            except RepError as exc:
                c.reasons["gold_encode:" + str(exc)[:40]] += 1
                continue
            raw = obj
        else:
            raw = written[k][0]
        if len(c.samples) < keep:
            c.samples.append(raw if isinstance(raw, str) else " ".join(raw))
        try:
            plan = decode_plan(rep, raw, ops)
        except (RepError, PlanError, OpError, KeyError, IndexError, ValueError) as exc:
            c.reasons["plan_parse"] += 1
            continue
        c.parsed += 1
        if well_typed(plan, ops):
            c.typed += 1
        if canonical(plan) == canonical(it.plan):
            c.exact += 1
        if rep in ("typed", "goalstack"):
            try:
                tp = decode_typed_full(raw, ops, drop_goal=(rep == "goalstack"))
                if declarations_agree(tp, ops):
                    c.declared_ok += 1
            except (RepError, PlanError, KeyError, IndexError):
                pass
        try:
            value = run_plan(plan, ops)
        except (PlanError, OpError) as exc:
            c.reasons["execute"] += 1
            c.parsed_wrong += 1
            continue
        ok = _norm(answer_text(value)) == _norm(it.gold)
        c.correct += int(ok)
        c.reasons["ok" if ok else "wrong_value"] += 1
        if not ok:
            c.parsed_wrong += 1
    if rep == "goalstack" and side and not use_gold_plan:
        n = max(1, len(side))
        c.extra["constraint_bound_rate"] = sum(1 for h in side if h.binds) / n
        c.extra["constraint_bind_events"] = sum(h.binds for h in side)
        c.extra["constraint_released_rate"] = sum(1 for h in side if h.released) / n
        # How tight the obligation actually was. The required application count
        # is read off the question through the operator table the model itself
        # induced, so a failed induction leaves the glyph unrecognised and the
        # obligation collapses to its floor of one. Without this number a weak
        # constraint would be indistinguishable from a strong one.
        tight = sum(1 for h, it in zip(side, items)
                    if h.ob.required == len(it.plan.steps))
        c.extra["obligation_tight_rate"] = tight / n
        c.extra["mean_required"] = round(sum(h.ob.required for h in side) / n, 3)
        c.extra["mean_gold_steps"] = round(
            sum(len(it.plan.steps) for it in items) / max(1, len(items)), 3)
    if rep == "slots" and side and not use_gold_plan:
        c.extra["refinement_passes"] = side[0].rounds if side else 0
        c.extra["assignment_changed_rate"] = sum(1 for r in side if r.changed) / max(1, len(side))
        c.extra["free_argmax_in_domain_rate"] = (
            sum(r.in_domain for r in side) / max(1, sum(r.total for r in side)))
    return c


def _norm(s) -> str:
    return str(s).strip().strip(".").strip().lower()
