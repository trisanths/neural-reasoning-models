"""Episode environment for reinforcement learning against the verifiers.

The policy answers a worldgen or scrubbed-web question by driving the same
emit-query-read protocol it was pretrained to imitate. The prompt holds the
world preamble, any in-context documents the episode keeps, and the
question:

    <|world|> preamble [<|doc|> text ...] <|q|> question

From there the policy writes tokens. When it emits <|retrieve|> the
environment collects the query it writes, runs the training oracle's BM25
over the episode's documents (reliability weighted, without replacement
across the rounds of one rollout), and splices <|result|> plus the served
chunk back into the stream. The rollout ends on <|eot|>, on a special token
arriving after the answer began, on the round cap, or on the token budget.
The stop conditions, the query collection rules, and the result splicing all
follow src/evals/interactive.py exactly, so a rollout and an evaluation of
the same policy on the same question walk the same trace.

Reward is machine checkable. The answer span is compared against the stored
gold answer with the naturalized normalizer from src/evals/naturalized:
normalized exact match first, then a bounded contains fallback. Nothing is
judged by a model. Shaping terms, all configurable and small by default, add
a bonus for a well formed trace and for using retrieval at all, and subtract
a penalty for degenerate queries (empty, or repeated within one rollout).

Rollouts run in lockstep: every live sequence appends exactly one token per
iteration, either sampled from the policy or taken from a forced queue that
holds the served chunk. Because lengths stay equal across the batch the
sampler's key/value cache needs only a scalar position, which is what makes
the batched GPU path in src/rl/sampler.py simple.
"""

import json
import random
from collections import deque
from dataclasses import dataclass, field

import numpy as np

from src.evals.naturalized import contains_answer, exact_match, normalize
from src.train.data import render_world_preamble
from src.train.retrieval import BM25Index

# Tokens appended to a done sequence purely to keep the batch in lockstep.
PAD_TOKEN = 0


@dataclass
class EnvConfig:
    """Rollout and reward knobs. Every default is deliberate and small."""

    max_rounds: int = 4
    max_new_tokens: int = 128
    query_max_tokens: int = 24
    max_len: int = 640
    # Shaping. correct_reward dominates; the rest nudge trace shape only.
    correct_reward: float = 1.0
    format_bonus: float = 0.05
    retrieval_bonus: float = 0.05
    degenerate_query_penalty: float = 0.05
    # The contains fallback only counts when the prediction is not much
    # longer than the gold answer, so a rollout cannot win by listing
    # every candidate. yes/no answers require exact match.
    contains_slack_tokens: int = 6
    # Token-overlap credit for structured answers. Exact match is an
    # all-or-nothing cliff, and a policy that has never produced the target
    # shape gets no gradient from it. F1 over answer tokens gives a slope to
    # climb without ever paying as much as a correct answer.
    partial_credit: float = 0.0
    # Multi-attempt revision. After a wrong answer the environment says so and
    # lets the policy try again inside the same rollout, so the objective pays
    # for using feedback. An external checker alone is known to give no gain;
    # the checker plus a trained revision loop is what helps.
    revision_attempts: int = 1
    # When true an arithmetic query is answered by an exact calculator
    # through the same channel the model already uses for retrieval.
    calculator: bool = False

    def to_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass
class Task:
    """One question, its prompt, and everything needed to grade it."""

    episode_index: int
    qid: str
    question: str
    gold: str
    prompt: list[int]
    documents: list[dict]
    domain: str = "unknown"
    hops: int = 0


@dataclass
class Rollout:
    """One completed trajectory."""

    task: Task
    tokens: list[int]
    mask: list[int]
    prompt_len: int
    rounds: list[dict] = field(default_factory=list)
    answer_text: str = ""
    stop_reason: str = "max_new_tokens"
    n_generated: int = 0
    reward: float = 0.0
    correct: bool = False
    info: dict = field(default_factory=dict)

    @property
    def n_rounds(self) -> int:
        return len(self.rounds)


def build_prompt(episode: dict, question: dict, tokenizer) -> list[int]:
    """World preamble, the episode's in-context document prefix, question.

    Worldgen episodes keep no documents in context, so every fact has to
    arrive through retrieval. Scrubbed-web episodes carry n_context, and
    that prefix is rendered exactly as src/scrub/web_retrieval does.
    """
    sid = tokenizer.special_ids
    ids = [sid["<|world|>"]]
    ids.extend(tokenizer.encode(render_world_preamble(episode.get("world", {}))))
    for doc in episode.get("documents", [])[: int(episode.get("n_context", 0))]:
        ids.append(sid["<|doc|>"])
        ids.extend(tokenizer.encode(doc["text"]))
    ids.append(sid["<|q|>"])
    ids.extend(tokenizer.encode(question["text"]))
    return ids


def load_tasks(path: str, tokenizer, limit_episodes: int | None = None,
               questions_per_episode: int = 2, min_hops: int = 1,
               max_prompt_tokens: int = 384, seed: int = 0) -> list[Task]:
    """Read an episodes jsonl and build the task list.

    Questions are picked per episode by a seeded shuffle, so the same file
    and seed always yield the same tasks. Questions with fewer than
    min_hops derivation steps are skipped: those are the generator's
    negative yes/no items, which need no retrieval and would teach the
    policy that skipping the retriever is fine. Prompts longer than
    max_prompt_tokens are dropped so the rollout budget is never eaten by
    the preamble.
    """
    rng = random.Random(seed)
    tasks: list[Task] = []
    with open(path) as fh:
        for line_no, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            if limit_episodes is not None and line_no >= limit_episodes:
                break
            episode = json.loads(line)
            questions = list(episode.get("questions", []))
            if not questions:
                continue
            order = list(range(len(questions)))
            rng.shuffle(order)
            taken = 0
            for qi in order:
                if taken >= questions_per_episode:
                    break
                q = questions[qi]
                hops = len(q.get("derivation") or q.get("plan") or [])
                if hops < min_hops:
                    continue
                if not q.get("answer"):
                    continue
                prompt = build_prompt(episode, q, tokenizer)
                if len(prompt) > max_prompt_tokens:
                    continue
                tasks.append(Task(
                    episode_index=line_no,
                    qid=q.get("qid", f"q{qi}"),
                    question=q["text"],
                    gold=q["answer"],
                    prompt=prompt,
                    documents=episode.get("documents", []),
                    domain=episode.get("world", {}).get("domain", "unknown"),
                    hops=hops,
                ))
                taken += 1
    return tasks


class RetrievalService:
    """Per-rollout view of one episode's retriever.

    Wraps a shared BM25Index and remembers which documents this rollout has
    already been served, which is the without-replacement contract the
    training oracle and the eval loop both hold.
    """

    def __init__(self, index: BM25Index, doc_texts: list[str],
                 calculator: bool = False):
        self.index = index
        self.doc_texts = doc_texts
        self.served: set[int] = set()
        self.calculator = calculator

    def exhausted(self) -> bool:
        return len(self.served) >= len(self.doc_texts)

    def top(self, query: str):
        """Serve a computed value for an arithmetic query, else the best
        unserved document, or None when nothing is left."""
        if self.calculator:
            try:
                from src.skillacq.calc import evaluate
                value = evaluate(query)
            except Exception:
                value = None
            if value is not None:
                return -1, f"The value of {query.strip()} is {value}."
        if self.exhausted():
            return None
        try:
            idx = self.index.top(query, exclude=self.served)
        except ValueError:
            return None
        self.served.add(idx)
        return idx, self.doc_texts[idx]


def make_service(documents: list[dict], calculator: bool = False) -> RetrievalService | None:
    """Index one episode's documents the way the training oracle does."""
    if not documents:
        return None
    texts = [d["text"] if isinstance(d, dict) else str(d) for d in documents]
    reliabilities = [
        float(d.get("reliability", 1.0)) if isinstance(d, dict) else 1.0
        for d in documents
    ]
    return RetrievalService(BM25Index(texts, reliabilities=reliabilities), texts,
                            calculator=calculator)


class _SeqState:
    """Bookkeeping for one in-flight rollout."""

    __slots__ = ("task", "service", "tokens", "mask", "prompt_len", "mode",
                 "forced", "query_tokens", "rounds", "in_answer",
                 "answer_start", "n_generated", "done", "stop_reason",
                 "query_lens", "attempts")

    def __init__(self, task: Task, service, prompt: list[int]):
        self.task = task
        self.service = service
        self.tokens = list(prompt)
        self.mask = [0] * len(prompt)
        self.prompt_len = len(prompt)
        self.mode = "free"
        self.forced: deque = deque()
        self.query_tokens: list[int] = []
        self.rounds: list[dict] = []
        self.in_answer = False
        self.answer_start: int | None = None
        self.n_generated = 0
        self.done = False
        self.stop_reason = "max_new_tokens"
        self.attempts = 0
        self.query_lens: list[int] = []

    def append(self, token: int, generated: bool) -> None:
        self.tokens.append(int(token))
        self.mask.append(1 if generated else 0)
        if generated:
            self.n_generated += 1

    def finish(self, reason: str) -> None:
        self.done = True
        self.stop_reason = reason


class EpisodeEnv:
    """Runs batched rollouts and scores them.

    The policy interface is deliberately narrow so a scripted policy and the
    cached GPU sampler are interchangeable. begin(prompts) conditions on each
    prompt and returns one proposed next token per sequence; advance(tokens)
    appends one token to every sequence and returns the next proposals. The
    environment takes a proposal when the sequence is free to speak and
    ignores it while a served chunk is being read back in, which keeps
    sampling batched into one call per step.
    """

    def __init__(self, tokenizer, cfg: EnvConfig | None = None):
        self.tokenizer = tokenizer
        self.cfg = cfg or EnvConfig()
        sid = tokenizer.special_ids
        self.retrieve_id = sid["<|retrieve|>"]
        self.result_id = sid["<|result|>"]
        self.answer_id = sid["<|a|>"]
        self.question_id = sid["<|q|>"]
        self.eot_id = sid["<|eot|>"]
        self.special_ids = set(sid.values())

    # ---------------------------------------------------------------- rollout

    def rollout(self, policy, tasks: list[Task], services=None) -> list[Rollout]:
        """Generate one trajectory per task, all in lockstep.

        services, when given, supplies one RetrievalService per task; that is
        how a group of rollouts over the same question each keep their own
        without-replacement set. When omitted a fresh service is built per
        task.
        """
        if services is None:
            services = [make_service(t.documents, calculator=self.cfg.calculator)
                        for t in tasks]
        states = [_SeqState(t, s, t.prompt) for t, s in zip(tasks, services)]

        proposals = policy.begin([s.tokens for s in states])
        while not all(st.done for st in states):
            chosen: list[int] = []
            for i, st in enumerate(states):
                if st.done:
                    chosen.append(PAD_TOKEN)
                    continue
                chosen.append(self._advance_one(st, int(proposals[i])))
            if all(st.done for st in states):
                break
            proposals = policy.advance(chosen)

        return [self._finalize(st) for st in states]

    def _advance_one(self, st: _SeqState, proposed: int) -> int:
        """Pick and apply this sequence's next token. Returns the token that
        was appended (PAD_TOKEN when the sequence just finished without
        appending), which the policy consumes to advance its cache."""
        cfg = self.cfg
        if st.forced:
            token, generated = st.forced.popleft()
            st.append(token, generated)
            if not st.forced and st.mode == "ingest":
                st.mode = "free"
            self._check_caps(st)
            return token

        token = int(proposed)

        if token == self.eot_id and self._maybe_revise(st):
            return token
        if token == self.eot_id:
            st.append(token, True)
            st.finish("eot")
            return token

        if st.mode == "query":
            if token == self.result_id:
                st.append(token, True)
                self._serve(st, "emitted")
                return token
            if token in self.special_ids:
                # The eval loop drops the stray special token and inserts
                # <|result|> on the model's behalf.
                self._serve(st, "inserted")
                return self.result_id
            st.append(token, True)
            st.query_tokens.append(token)
            if len(st.query_tokens) >= cfg.query_max_tokens:
                # The query cap ends the round. This iteration has already
                # spent its one token on the query, so the inserted
                # <|result|> leads the forced queue instead.
                self._serve(st, "deferred")
            else:
                self._check_caps(st)
            return token

        # free mode
        if st.in_answer and token in self.special_ids:
            st.finish("answer_boundary")
            return PAD_TOKEN
        if token == self.answer_id:
            st.append(token, True)
            st.in_answer = True
            st.answer_start = len(st.tokens)
            self._check_caps(st)
            return token
        if token == self.retrieve_id:
            if (st.service is None or len(st.rounds) >= cfg.max_rounds
                    or st.service.exhausted()):
                st.finish("max_rounds")
                return PAD_TOKEN
            st.append(token, True)
            st.mode = "query"
            st.query_tokens = []
            self._check_caps(st)
            return token
        st.append(token, True)
        self._check_caps(st)
        return token

    def _serve(self, st: _SeqState, marker: str) -> None:
        """Resolve the collected query and queue the served chunk.

        marker says where the <|result|> token comes from. "emitted": the
        policy wrote it and it is already in the trace. "inserted": the
        environment writes it now, in place of a stray special token.
        "deferred": the environment writes it, but on the next iteration,
        because this one already appended a query token.
        """
        if marker == "inserted":
            st.append(self.result_id, False)
        query_text = self.tokenizer.decode(st.query_tokens)
        st.query_lens.append(len(st.query_tokens))
        hit = st.service.top(query_text) if st.service is not None else None
        if hit is None:
            if marker == "deferred":
                st.append(self.result_id, False)
            st.finish("max_rounds")
            return
        doc_index, chunk_text = hit
        chunk_tokens = self.tokenizer.encode(chunk_text)
        if marker == "deferred":
            st.forced.append((self.result_id, False))
        for t in chunk_tokens:
            st.forced.append((t, False))
        st.rounds.append({
            "query": query_text,
            "doc_index": int(doc_index),
            "chunk": chunk_text,
            "n_chunk_tokens": len(chunk_tokens),
        })
        st.mode = "ingest" if st.forced else "free"
        st.query_tokens = []
        self._check_caps(st)

    def _maybe_revise(self, st: _SeqState) -> bool:
        """Judge the answer just written; on a wrong one, invite another try.

        Returns True when the rollout should continue instead of ending. The
        verdict is the same programmatic check that scores the rollout, so no
        model judgement enters the loop.
        """
        if self.cfg.revision_attempts <= 1 or not st.in_answer:
            return False
        st.attempts += 1
        if st.attempts >= self.cfg.revision_attempts:
            return False
        end = len(st.tokens)
        answer = self.tokenizer.decode(st.tokens[st.answer_start:end])
        if self.is_correct(answer, st.task.gold):
            return False
        st.append(self.result_id, False)
        for t in self.tokenizer.encode(
                f"That answer was rejected. Attempt {st.attempts + 1}."):
            st.forced.append((t, False))
        st.forced.append((self.question_id, False))
        st.in_answer = False
        st.answer_start = len(st.tokens)
        st.mode = "ingest" if st.forced else "free"
        self._check_caps(st)
        return True

    def _check_caps(self, st: _SeqState) -> None:
        """Stop the rollout when a budget runs out.

        A chunk being read back in is never cut short: the eval loop splices
        the whole chunk and only then re-checks its budget, so the caps stay
        quiet until the forced queue drains.
        """
        if st.done or st.forced:
            return
        if st.n_generated >= self.cfg.max_new_tokens:
            st.finish("max_new_tokens")
        elif len(st.tokens) >= self.cfg.max_len:
            st.finish("max_len")

    def _finalize(self, st: _SeqState) -> Rollout:
        if st.answer_start is None:
            answer_text = ""
        else:
            end = len(st.tokens)
            if st.stop_reason == "eot":
                end -= 1
            answer_text = self.tokenizer.decode(st.tokens[st.answer_start:end])
        roll = Rollout(
            task=st.task,
            tokens=st.tokens,
            mask=st.mask,
            prompt_len=st.prompt_len,
            rounds=st.rounds,
            answer_text=answer_text,
            stop_reason=st.stop_reason,
            n_generated=st.n_generated,
        )
        roll.info["query_lens"] = list(st.query_lens)
        self.score(roll)
        return roll

    # ----------------------------------------------------------------- reward

    def is_correct(self, prediction: str, gold: str) -> bool:
        """Naturalized normalized exact match, then a bounded contains
        fallback. yes/no answers admit no fallback: 'yes no' would otherwise
        contain both polarities."""
        if exact_match(prediction, gold):
            return True
        gold_tokens = normalize(gold).split()
        if len(gold_tokens) == 1 and gold_tokens[0] in ("yes", "no"):
            return False
        pred_tokens = normalize(prediction).split()
        if not pred_tokens:
            return False
        if len(pred_tokens) > len(gold_tokens) + self.cfg.contains_slack_tokens:
            return False
        return contains_answer(prediction, gold)

    def score(self, roll: Rollout) -> Rollout:
        """Attach reward and its breakdown. Pure string work against gold."""
        cfg = self.cfg
        correct = self.is_correct(roll.answer_text, roll.task.gold)
        reward = cfg.correct_reward if correct else 0.0
        if not correct and cfg.partial_credit > 0.0:
            reward += cfg.partial_credit * _token_f1(roll.answer_text, roll.task.gold)

        well_formed = (roll.stop_reason == "eot"
                       and bool(roll.answer_text.strip()))
        if well_formed:
            reward += cfg.format_bonus
        if roll.n_rounds >= 1:
            reward += cfg.retrieval_bonus

        seen: set[str] = set()
        degenerate = 0
        for r in roll.rounds:
            key = normalize(r["query"])
            if not key or key in seen:
                degenerate += 1
            seen.add(key)
        reward -= cfg.degenerate_query_penalty * degenerate

        roll.correct = bool(correct)
        roll.reward = float(reward)
        roll.info.update({
            "correct": bool(correct),
            "well_formed": bool(well_formed),
            "degenerate_queries": int(degenerate),
        })
        return roll

    # ------------------------------------------------------------- transcript

    def transcript(self, roll: Rollout) -> dict:
        """A human readable dump of one rollout."""
        return {
            "episode_index": roll.task.episode_index,
            "qid": roll.task.qid,
            "domain": roll.task.domain,
            "question": roll.task.question,
            "gold": roll.task.gold,
            "answer": roll.answer_text,
            "correct": roll.correct,
            "reward": round(roll.reward, 4),
            "n_rounds": roll.n_rounds,
            "stop_reason": roll.stop_reason,
            "n_generated": roll.n_generated,
            "rounds": [{"query": r["query"], "doc_index": r["doc_index"],
                        "chunk": r["chunk"]} for r in roll.rounds],
            "text": self.tokenizer.decode(roll.tokens[roll.prompt_len:]),
        }


def _token_f1(prediction: str, gold: str) -> float:
    """Token overlap between prediction and gold, order independent."""
    pred = normalize(prediction).split()
    want = normalize(gold).split()
    if not pred or not want:
        return 0.0
    counts: dict[str, int] = {}
    for t in want:
        counts[t] = counts.get(t, 0) + 1
    hits = 0
    for t in pred:
        if counts.get(t, 0) > 0:
            counts[t] -= 1
            hits += 1
    if hits == 0:
        return 0.0
    precision = hits / len(pred)
    recall = hits / len(want)
    return 2 * precision * recall / (precision + recall)


def rollout_stats(rolls: list[Rollout]) -> dict:
    """Aggregate the numbers the training log reports."""
    if not rolls:
        return {}
    rewards = np.array([r.reward for r in rolls], dtype=np.float64)
    rounds = np.array([r.n_rounds for r in rolls], dtype=np.float64)
    qlens = [n for r in rolls for n in r.info.get("query_lens", [])]
    gen = np.array([r.n_generated for r in rolls], dtype=np.float64)
    stops: dict[str, int] = {}
    for r in rolls:
        stops[r.stop_reason] = stops.get(r.stop_reason, 0) + 1
    return {
        "n_rollouts": len(rolls),
        "reward_mean": float(rewards.mean()),
        "reward_std": float(rewards.std()),
        "accuracy": float(np.mean([r.correct for r in rolls])),
        "mean_rounds": float(rounds.mean()),
        "any_retrieval": float(np.mean(rounds >= 1)),
        "mean_query_len": float(np.mean(qlens)) if qlens else 0.0,
        "mean_generated": float(gen.mean()),
        "well_formed": float(np.mean([r.info.get("well_formed", False)
                                      for r in rolls])),
        "degenerate_queries": float(np.mean([r.info.get("degenerate_queries", 0)
                                             for r in rolls])),
        "stop_reasons": stops,
    }
