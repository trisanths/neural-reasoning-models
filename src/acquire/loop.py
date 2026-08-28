"""The loop: detect, search, learn, gate, answer or abstain.

One pass over one problem:

  0  a control attempt with plain retrieval over the whole corpus and nothing
     carried in context. This is what the policy does today, and every number
     the loop produces is reported against it.
  1  gap detection from the question and an empty skill memory.
  2  a dependency-aware search from the gap's structural query, recursing only
     into the unknown frontier.
  3  for each acquired notion in teaching order, the acquisition battery with
     that notion's pages withheld. A failure routes to diagnosis and another
     search, and whether to search again is decided by learning progress.
  4  a final attempt carrying the compiled card. When the gate did not pass
     for everything the target needs, the loop abstains instead of answering,
     and records what it would have said so the gate's effect is measurable
     rather than assumed.
  5  the card is discarded.

Every trace keeps the problem's level, chapter and phrasing, so report()
breaks every number out by both and never pools them.

One measurement in here is worth reading carefully. The retrieval cell
compares the question's own words against the structural query by repeating
each one k times. That is a fair test of the first hop and an unfair test of
the rest: the structural query is the seed of a multi-hop search that renames
its target as soon as the preamble arrives, and repeating the seed instead of
following the search understates it. The end-to-end number for the search is
the curriculum score, not this cell.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.acquire import curriculum as curriculum_mod
from src.acquire import selftest
from src.acquire.gap import detect
from src.acquire.lesson import LessonIndex
from src.acquire.reasoner import AnswerRequest
from src.acquire.skill import SkillMemory

ABSTAIN = "<abstain>"


@dataclass
class LoopConfig:
    battery_threshold: float = 0.67
    max_nodes: int = 8
    max_search_rounds: int = 12
    max_repair_rounds: int = 3
    min_progress: float = 0.05
    patience: int = 2
    gate: bool = True
    battery_gates_curriculum: bool = True


@dataclass
class LoopTrace:
    qid: str
    chapter: str
    level: int
    phrasing: str
    gold: str
    baseline_answer: str = ""
    baseline_correct: bool = False
    gap: dict = field(default_factory=dict)
    gap_fired: bool = False
    curriculum: dict = field(default_factory=dict)
    curriculum_score: dict = field(default_factory=dict)
    batteries: list = field(default_factory=list)
    progress: dict = field(default_factory=dict)
    gate_passed: bool = False
    ungated_answer: str = ""
    ungated_correct: bool = False
    final_answer: str = ""
    final_correct: bool = False
    abstained: bool = False
    card_chars: int = 0
    raw_chars: int = 0
    retrieval: dict = field(default_factory=dict)
    n_model_calls: int = 0

    def to_dict(self) -> dict:
        d = dict(self.__dict__)
        return d


def _matches(answer: str, gold: str) -> bool:
    return selftest._matches(answer, gold)


def _closure(skill: SkillMemory, term: str) -> list[str]:
    """Terms in the memory's closure below term, term included."""
    seen: list[str] = []

    def go(t: str) -> None:
        if t in seen:
            return
        seen.append(t)
        c = skill.concepts.get(t)
        if c is None:
            return
        for d in c.depends_on:
            go(d)

    go(term)
    return seen


def _retrieval_probe(index: LessonIndex, query: str, required_pages,
                     k: int, target_page: str = "") -> dict:
    """What one repeated query reaches, measured three ways.

    Bulk coverage says how much of the required material shows up inside a
    budget of k retrievals. It is the friendliest measure, and in a corpus
    where every page of a chapter shares the chapter's attribute words it
    flatters any query that mentions them.

    The first hop and the steps to the target are the sharp measures. A query
    that eventually sweeps the whole chapter is not the same as a query that
    lands on the page that names what is missing, and the cost of a search is
    how many retrievals it takes to get there.
    """
    got: list[str] = []
    used: set[str] = set()
    top1 = {"page_id": "", "kind": ""}
    steps_to_target = None
    for step in range(k):
        hits = index.retrieve(query, k=1, exclude=used)
        if not hits:
            break
        if step == 0:
            top1 = {"page_id": hits[0].page_id, "kind": hits[0].kind}
        for page in hits[0].documents():
            pid = page.get("page_id", "")
            used.add(pid)
            if target_page and pid == target_page and steps_to_target is None:
                steps_to_target = step + 1
            if pid in required_pages and pid not in got:
                got.append(pid)
    need = set(required_pages)
    return {"query": query, "n_required": len(need), "n_hit": len(got),
            "hit_rate": len(got) / len(need) if need else 0.0,
            "top1_page": top1["page_id"], "top1_kind": top1["kind"],
            "top1_required": top1["page_id"] in need,
            "steps_to_target": steps_to_target,
            "reached_target": steps_to_target is not None}


def run_problem(problem, chapter, documents: list[dict], reasoner,
                cfg: LoopConfig | None = None, lexicon=None,
                query_for=None) -> LoopTrace:
    """One problem, start to finish. chapter supplies only its display name;
    nothing here reads the generator's answers or its cites field."""
    cfg = cfg or LoopConfig()
    index = LessonIndex(documents)
    trace = LoopTrace(qid=problem.qid, chapter=problem.chapter,
                      level=problem.level, phrasing=problem.phrasing,
                      gold=problem.answer)
    calls = 0

    # 0 -- the control. Plain retrieval, nothing in context.
    baseline = reasoner.answer_batch(
        [AnswerRequest(question=problem.text, documents=documents, card="",
                       tag="baseline")])[0]
    calls += 1
    trace.baseline_answer = baseline
    trace.baseline_correct = _matches(baseline, problem.answer)

    # 1 -- the gap.
    skill = SkillMemory()
    gap = detect(problem.text, skill, attempted_answer=baseline)
    trace.gap = gap.to_dict()
    trace.gap_fired = gap.fired

    # The two retrieval probes, model-free, for the structural-query claim.
    n_req = max(1, len(problem.required_pages))
    target_page = (chapter.definition_page(problem.notion).page_id
                   if chapter is not None else "")
    trace.retrieval = {
        "naive": _retrieval_probe(index, gap.naive_query,
                                  problem.required_pages, n_req + 2,
                                  target_page),
        "structural": _retrieval_probe(index, gap.query or gap.naive_query,
                                       problem.required_pages, n_req + 2,
                                       target_page),
    }

    if not gap.fired:
        # Nothing to acquire. Answer from what is held.
        answer = reasoner.answer_batch(
            [AnswerRequest(question=problem.text, documents=documents,
                           card=skill.render(), tag="no_gap")])[0]
        calls += 1
        trace.ungated_answer = answer
        trace.ungated_correct = _matches(answer, problem.answer)
        trace.final_answer = answer
        trace.final_correct = trace.ungated_correct
        trace.gate_passed = True
        trace.n_model_calls = calls
        return trace

    # 2 -- the curriculum.
    chapter_name = chapter.name if chapter is not None else ""
    curr = curriculum_mod.build(
        gap.query, index, skill, max_nodes=cfg.max_nodes,
        max_rounds=cfg.max_search_rounds, chapter=chapter_name,
        lexicon=lexicon, query_for=query_for)
    skill.focus(chapter_name)
    trace.curriculum = curr.to_dict()
    trace.curriculum_score = curriculum_mod.score_against(
        curr, chapter.theory_graph(), problem.required_notions)

    # 3 -- the gate, one notion at a time, in teaching order.
    absorbed_pages = {pid for pid in skill.absorbed_pages}
    results = []
    controllers = {}
    for term in curr.order:
        if term not in skill.concepts or not skill.concepts[term].rules:
            continue
        need = _closure(skill, term)
        card = skill.render(only=need)
        pages = [d for d in documents if d.get("page_id") in absorbed_pages]
        probes = selftest.probes_from_pages(pages, term)
        ctrl = selftest.ProgressController(min_gain=cfg.min_progress,
                                           patience=cfg.patience,
                                           max_rounds=cfg.max_repair_rounds)
        result = selftest.run_battery(
            reasoner, probes, card, documents, term,
            threshold=cfg.battery_threshold,
            hide_terms=tuple(t for t in need if t != term))
        calls += result.n
        verdict = ctrl.observe(result.score)
        while not result.passed and verdict == "continue":
            diag = selftest.diagnose(result, skill, chapter_name)
            hits = index.retrieve(diag.query, k=1, exclude=absorbed_pages)
            if not hits:
                break
            for page in hits[0].documents():
                skill.absorb(page, lexicon=lexicon)
                absorbed_pages.add(page.get("page_id", ""))
            need = _closure(skill, term)
            card = skill.render(only=need)
            pages = [d for d in documents if d.get("page_id") in absorbed_pages]
            probes = selftest.probes_from_pages(pages, term) or probes
            result = selftest.run_battery(
                reasoner, probes, card, documents, term,
                threshold=cfg.battery_threshold,
                hide_terms=tuple(t for t in need if t != term))
            calls += result.n
            verdict = ctrl.observe(result.score)
        skill.concepts[term].verified = result.passed
        skill.concepts[term].battery_score = result.score
        results.append(result)
        controllers[term] = ctrl.to_dict()

    trace.batteries = [r.to_dict() for r in results]
    trace.progress = controllers

    # 4 -- answer, or abstain.
    target = gap.named_targets[0] if gap.named_targets else skill.top_term
    if not target:
        target = curr.order[-1] if curr.order else ""
    need = _closure(skill, target) if target else []
    gate_passed = bool(need) and skill.resolvable(target) and all(
        skill.concepts[t].verified for t in need if t in skill.concepts)
    trace.gate_passed = gate_passed

    card = skill.render(only=need) if need else skill.render()
    trace.card_chars = len(card)
    trace.raw_chars = skill.raw_chars
    ungated = reasoner.answer_batch(
        [AnswerRequest(question=problem.text, documents=documents, card=card,
                       tag="final")])[0]
    calls += 1
    trace.ungated_answer = ungated
    trace.ungated_correct = _matches(ungated, problem.answer)

    if cfg.gate and not gate_passed:
        trace.final_answer = ABSTAIN
        trace.abstained = True
        trace.final_correct = False
    else:
        trace.final_answer = ungated
        trace.final_correct = trace.ungated_correct

    trace.n_model_calls = calls
    skill.discard()
    return trace


def run_universe(universe, reasoner, cfg: LoopConfig | None = None,
                 limit: int | None = None, on_trace=None) -> list[LoopTrace]:
    documents = universe.documents()
    by_id = {ch.chapter_id: ch for ch in universe.chapters}
    traces = []
    problems = universe.problems()
    if limit is not None:
        problems = problems[:limit]
    for problem in problems:
        t = run_problem(problem, by_id[problem.chapter], documents, reasoner,
                        cfg)
        traces.append(t)
        if on_trace is not None:
            on_trace(t)
    return traces


# ------------------------------------------------------------------ reporting


def _retrieval_cell(traces: list[LoopTrace]) -> dict:
    """Naive against structural, on all three measures, side by side."""
    have = [t for t in traces if t.retrieval]
    if not have:
        return {}
    out = {}
    for which in ("naive", "structural"):
        rows = [t.retrieval[which] for t in have]
        reached = [r for r in rows if r["reached_target"]]
        out[which] = {
            "bulk_hit_rate": sum(r["hit_rate"] for r in rows) / len(rows),
            "top1_required": sum(r["top1_required"] for r in rows) / len(rows),
            "reached_target": len(reached) / len(rows),
            "mean_steps_to_target": (
                sum(r["steps_to_target"] for r in reached) / len(reached)
                if reached else None),
        }
    return out


def _cell(traces: list[LoopTrace]) -> dict:
    n = len(traces)
    if not n:
        return {}
    fired = [t for t in traces if t.gap_fired]
    blocked = [t for t in traces if not t.baseline_correct]
    unblocked = [t for t in traces if t.baseline_correct]
    gated_off = [t for t in traces if t.abstained]
    saved = [t for t in gated_off if not t.ungated_correct]
    cost = [t for t in gated_off if t.ungated_correct]
    curr = [t.curriculum_score for t in traces if t.curriculum_score]
    return {
        "n": n,
        "baseline_accuracy": sum(t.baseline_correct for t in traces) / n,
        "after_acquisition_accuracy": sum(t.ungated_correct for t in traces) / n,
        "gated_accuracy": sum(t.final_correct for t in traces) / n,
        "abstain_rate": len(gated_off) / n,
        "gap_fire_rate": len(fired) / n,
        "gap_fire_rate_when_blocked": (
            sum(t.gap_fired for t in blocked) / len(blocked)
            if blocked else None),
        "gap_fire_rate_when_not_blocked": (
            sum(t.gap_fired for t in unblocked) / len(unblocked)
            if unblocked else None),
        "gate_saved_a_wrong_answer": len(saved) / n,
        "gate_withheld_a_right_answer": len(cost) / n,
        "gate_pass_rate": sum(t.gate_passed for t in traces) / n,
        "curriculum": curriculum_mod.aggregate(curr),
        "retrieval": _retrieval_cell(traces),
        "card_chars": sum(t.card_chars for t in traces) / n,
        "raw_chars": sum(t.raw_chars for t in traces) / n,
        "model_calls": sum(t.n_model_calls for t in traces) / n,
    }


def report(traces: list[LoopTrace]) -> dict:
    """Per level, per chapter, per phrasing. Nothing pooled across them.

    The registry lesson that produced this rule: a pooled score hid a task
    family sitting at zero. Every cell below therefore carries its own n, and
    a caller that wants one number has to say which cell it means.
    """
    by_level: dict = {}
    by_chapter: dict = {}
    by_phrasing: dict = {}
    for t in traces:
        by_level.setdefault(t.level, []).append(t)
        by_chapter.setdefault(t.chapter, []).append(t)
        by_phrasing.setdefault((t.level, t.phrasing), []).append(t)
    blockages: dict = {}
    for t in traces:
        b = t.gap.get("blockage", "none")
        blockages[b] = blockages.get(b, 0) + 1
    return {
        "n_traces": len(traces),
        "by_level": {str(k): _cell(v) for k, v in sorted(by_level.items())},
        "by_chapter": {k: _cell(v) for k, v in sorted(by_chapter.items())},
        "by_level_and_phrasing": {
            f"L{k[0]}/{k[1]}": _cell(v) for k, v in sorted(by_phrasing.items())},
        "blockage_counts": blockages,
    }
