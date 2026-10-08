"""The partitioned objective: read the evidence, predict only what we authored.

A training example here has two regions and one rule about them.

    evidence    the retrieved pages. They are in the context, they are read,
                they supply the keys and the states the copy distribution
                points at, and they are never a prediction target.
    authored    the answer we wrote. Every supervised token lives here.

The rule is that the loss is computed only over the authored span. Putting
retrieved document text on the prediction stream would spend the model's
capacity memorizing the corpus, which is the exact thing this project is trying
not to build: the whole thesis is that facts live in the retrieval fabric and
the parameters hold the reasoning. A model that is scored on reproducing a
Britannica paragraph is being taught to be a worse version of the index it is
sitting next to. So evidence tokens are masked to IGNORE_INDEX and the gradient
at those positions is exactly zero, which
src/train/tests/test_pointer_data.py checks by reading the gradient of the
loss with respect to the logits rather than by trusting the mask.

The sequence layout is

    <|doc|> page one <|doc|> page two ... <|q|> question <|a|> answer <|eot|>

with next-token prediction, supervised on the answer tokens and the closing
<|eot|> only. Evidence positions are reported separately as an index tensor so
the pointer head can gather the decoder's own states at those positions; a
position of -1 is padding, so one tensor carries both the index and the mask.

Where the examples come from. The invented-system episodes in src/skillacq are
the honest case for a copy head, because they are regenerated per seed and
memorizing any particular rule has zero expected value across episodes. Within
those, the simple families of src/skillacq/simple.py are the sharpest: the
routing table states that a request of some invented type goes to the tutez
desk, and "tutez" is a nonsense word that appears in the page and nowhere else
in the language. Answering requires locating it and echoing it. The procedure
families of src/skillacq/procedures.py assemble their answer out of a delimiter
and a prefix taken from the card and items taken from the question, so for
those the copy scope is set to the whole read-only prefix rather than the
documents alone. The arithmetic families of src/skillacq/systems.py and the
worldgen episodes are carried too, and they are the control: their answers are
computed, not copied, and a pointer head should not help there.
"""

from dataclasses import dataclass, field

import torch

IGNORE_INDEX = -100
PAD_POSITION = -1

# Which region of the sequence the copy distribution may point into.
COPY_SCOPES = ("evidence", "prefix")


@dataclass
class PointerExample:
    """One episode question, split into what is read and what is authored.

    document_ids   token ids of each evidence document, in bank order
    question_ids   token ids of the question
    answer_ids     token ids of the authored answer
    copy_scope     "evidence" for the documents alone, "prefix" to let the
                   copy distribution also reach the question, which is what
                   the format families need. Empty defers to the collator.
    """

    document_ids: list
    question_ids: list
    answer_ids: list
    copy_scope: str = ""
    question_text: str = ""
    answer_text: str = ""
    family: str = ""
    episode_id: str = ""
    meta: dict = field(default_factory=dict)

    @property
    def n_evidence_tokens(self) -> int:
        return sum(len(d) for d in self.document_ids)


@dataclass
class PointerBatch:
    """Tensors for one training step.

    input_ids           (B, T) the working sequence
    targets             (B, T) IGNORE_INDEX everywhere but the authored span
    evidence_positions  (B, M) indices into input_ids, -1 for padding
    evidence_ids        (B, M) the token id at each of those positions
    authored_positions  (B, K) the supervised positions, for `select`
    authored_targets    (B, K) targets at those positions, IGNORE_INDEX padded
    answer_lengths      (B,) authored tokens per row, the closing eot included
    copy_available      (B,) every authored token id occurs in the copy region
    span_copyable       (B,) the answer occurs in the copy region as a run
    """

    input_ids: torch.Tensor
    targets: torch.Tensor
    evidence_positions: torch.Tensor
    evidence_ids: torch.Tensor
    authored_positions: torch.Tensor
    authored_targets: torch.Tensor
    answer_lengths: torch.Tensor
    copy_available: torch.Tensor
    span_copyable: torch.Tensor

    def to(self, device):
        return PointerBatch(**{k: v.to(device) for k, v in self.__dict__.items()})

    @property
    def evidence_mask(self) -> torch.Tensor:
        return self.evidence_positions >= 0

    @property
    def n_authored_tokens(self) -> int:
        return int((self.targets != IGNORE_INDEX).sum())

    @property
    def n_evidence_tokens(self) -> int:
        return int(self.evidence_mask.sum())


def find_token_runs(haystack: list, needle: list) -> list:
    """Start indices where needle occurs contiguously inside haystack."""
    n = len(needle)
    if n == 0 or n > len(haystack):
        return []
    return [i for i in range(len(haystack) - n + 1) if haystack[i:i + n] == needle]


def answer_token_variants(answer: str, tokenizer) -> list:
    """Tokenizations of the answer as it might appear inside a page.

    A byte-level BPE encodes a leading space into the first token, so an answer
    tokenized on its own and the same answer tokenized mid-sentence are two
    different id sequences. Both are checked before calling an answer
    uncopyable, which keeps the copyability statistics honest rather than
    pessimistic.
    """
    seen = []
    for text in (answer, " " + answer):
        ids = tokenizer.encode(text)
        if ids and ids not in seen:
            seen.append(ids)
    return seen


class PointerCollator:
    """Builds padded batches with the evidence and authored regions marked.

    Documents are laid down in bank order, each behind a <|doc|> marker, then
    the question, then the answer. The marker tokens are deliberately left out
    of the evidence positions: pointing at a structural token is never a useful
    prediction, and including them would put probability mass on <|doc|> in the
    middle of an answer.

    A sequence longer than max_seq_len loses whole documents from the end of
    the bank, never a fragment of one and never a piece of the question or the
    answer, so a truncated example is still a well-formed example.

    Answer tokenization is aligned to the evidence, and it has to be. A byte
    level BPE folds a leading space into the first token, so "tutez" encoded on
    its own and the same word encoded inside "handled by the tutez desk" are
    different id sequences that share no first token. Written the naive way,
    the answer the model is asked to emit is spelled in ids the page does not
    contain, and a copy head has nothing to point at: measured on the three
    simple families, every answer occurs verbatim in its page as text and none
    of them occurs as the ids the naive target uses. So the collator picks,
    among the tokenizations of the answer string, the one that actually occurs
    in the copy region, and falls back to the standalone encoding when none
    does. That is the difference between a pointer head that works on this data
    and one that cannot fire.
    """

    def __init__(self, tokenizer, max_seq_len: int, copy_scope: str = "evidence",
                 pad_id: int | None = None, align_answers: bool = True):
        if copy_scope not in COPY_SCOPES:
            raise ValueError(f"copy_scope must be one of {COPY_SCOPES}")
        self.tokenizer = tokenizer
        self.max_seq_len = max_seq_len
        self.copy_scope = copy_scope
        self.align_answers = align_answers
        sid = tokenizer.special_ids
        self.doc_id = sid["<|doc|>"]
        self.q_id = sid["<|q|>"]
        self.a_id = sid["<|a|>"]
        self.eot_id = sid["<|eot|>"]
        self.pad_id = self.eot_id if pad_id is None else pad_id

    def choose_answer_tokens(self, ex: PointerExample, question: list,
                             scope: str) -> tuple:
        """The tokenization of the answer that the copy region actually holds.

        Variants are tried in order, the standalone encoding first, so an answer
        that already matches is left alone. Returns (ids, aligned), where
        aligned records whether the choice was found in the region or is the
        fallback.
        """
        answer = list(ex.answer_ids)
        if not self.align_answers or not ex.answer_text:
            return answer, bool(answer and find_token_runs(
                [t for doc in ex.document_ids for t in doc], answer))
        region = [t for doc in ex.document_ids for t in doc]
        if scope == "prefix":
            region = region + question
        for variant in answer_token_variants(ex.answer_text, self.tokenizer):
            if find_token_runs(region, variant):
                return variant, True
        return answer, False

    def encode_example(self, ex: PointerExample) -> dict:
        """One row: ids, targets, evidence positions, authored positions.

        Positions index the input sequence, which is the full sequence with its
        last token dropped, so position t is the state that predicts target t.
        """
        scope = ex.copy_scope or self.copy_scope
        if scope not in COPY_SCOPES:
            raise ValueError(f"copy_scope must be one of {COPY_SCOPES}")
        question = list(ex.question_ids)
        answer, aligned = self.choose_answer_tokens(ex, question, scope)
        tail = [self.q_id] + question + [self.a_id] + answer + [self.eot_id]
        budget = self.max_seq_len + 1 - len(tail)
        if budget < 1:
            raise ValueError(
                f"question and answer need {len(tail)} tokens, which leaves no room "
                f"for evidence inside max_seq_len {self.max_seq_len}"
            )

        ids: list = []
        evidence_positions: list = []
        for doc in ex.document_ids:
            if len(ids) + 1 + len(doc) > budget:
                break
            ids.append(self.doc_id)
            evidence_positions.extend(range(len(ids), len(ids) + len(doc)))
            ids.extend(doc)

        question_start = len(ids) + 1  # the position of question token zero
        prefix_len = len(ids) + len(tail) - len(answer) - 1  # through <|a|>
        ids.extend(tail)
        if scope == "prefix":
            evidence_positions.extend(range(question_start, question_start + len(question)))

        inputs = ids[:-1]
        full_targets = ids[1:]
        targets = [IGNORE_INDEX] * len(full_targets)
        # Position prefix_len - 1 holds <|a|> and predicts the first answer
        # token; everything from there to the end is authored.
        authored_positions = list(range(prefix_len - 1, len(inputs)))
        for t in authored_positions:
            targets[t] = full_targets[t]

        copy_ids = [inputs[p] for p in evidence_positions]
        authored_ids = [full_targets[t] for t in authored_positions]
        pool = set(copy_ids)
        copy_available = all(t in pool for t in answer)
        return {
            "inputs": inputs,
            "targets": targets,
            "evidence_positions": evidence_positions,
            "evidence_ids": copy_ids,
            "authored_positions": authored_positions,
            "authored_targets": authored_ids,
            "answer_ids": answer,
            "answer_aligned": aligned,
            "copy_available": copy_available,
            "span_copyable": bool(find_token_runs(copy_ids, answer)),
        }

    def __call__(self, examples: list) -> PointerBatch:
        rows = [self.encode_example(ex) for ex in examples]
        bsz = len(rows)
        width = max(len(r["inputs"]) for r in rows)
        n_ev = max(1, max(len(r["evidence_positions"]) for r in rows))
        n_auth = max(1, max(len(r["authored_positions"]) for r in rows))

        input_ids = torch.full((bsz, width), self.pad_id, dtype=torch.long)
        targets = torch.full((bsz, width), IGNORE_INDEX, dtype=torch.long)
        ev_pos = torch.full((bsz, n_ev), PAD_POSITION, dtype=torch.long)
        ev_ids = torch.full((bsz, n_ev), self.pad_id, dtype=torch.long)
        # Padded authored slots point at position zero and carry IGNORE_INDEX,
        # so they are gathered safely and then dropped by the loss.
        auth_pos = torch.zeros((bsz, n_auth), dtype=torch.long)
        auth_tgt = torch.full((bsz, n_auth), IGNORE_INDEX, dtype=torch.long)
        lengths = torch.zeros(bsz, dtype=torch.long)
        copy_available = torch.zeros(bsz, dtype=torch.bool)
        span_copyable = torch.zeros(bsz, dtype=torch.bool)

        for b, row in enumerate(rows):
            n = len(row["inputs"])
            input_ids[b, :n] = torch.tensor(row["inputs"], dtype=torch.long)
            targets[b, :n] = torch.tensor(row["targets"], dtype=torch.long)
            m = len(row["evidence_positions"])
            if m:
                ev_pos[b, :m] = torch.tensor(row["evidence_positions"], dtype=torch.long)
                ev_ids[b, :m] = torch.tensor(row["evidence_ids"], dtype=torch.long)
            k = len(row["authored_positions"])
            auth_pos[b, :k] = torch.tensor(row["authored_positions"], dtype=torch.long)
            auth_tgt[b, :k] = torch.tensor(row["authored_targets"], dtype=torch.long)
            lengths[b] = k
            copy_available[b] = row["copy_available"]
            span_copyable[b] = row["span_copyable"]

        return PointerBatch(input_ids, targets, ev_pos, ev_ids, auth_pos,
                            auth_tgt, lengths, copy_available, span_copyable)


# ---------------- building examples from episodes ----------------


def examples_from_episode(episode: dict, tokenizer, copy_scope: str = "evidence",
                          max_documents: int | None = None,
                          shuffle_seed: int | None = None) -> list:
    """One PointerExample per question of an episode.

    The episode shape is the one src/skillacq and src/worldgen already emit:
    a documents list of {"text": ...} and a questions list of
    {"text": ..., "answer": ...}. Every document goes in, distractors included,
    because selecting among them is the task.
    """
    docs = list(episode.get("documents", []))
    if shuffle_seed is not None:
        order = _permutation(len(docs), shuffle_seed)
        docs = [docs[i] for i in order]
    if max_documents is not None:
        docs = docs[:max_documents]
    doc_ids = [tokenizer.encode(d["text"]) for d in docs]
    family = episode.get("world", {}).get("domain", "")
    out = []
    for q in episode.get("questions", []):
        out.append(PointerExample(
            document_ids=doc_ids,
            question_ids=tokenizer.encode(q["text"]),
            answer_ids=tokenizer.encode(q["answer"]),
            copy_scope=copy_scope,
            question_text=q["text"],
            answer_text=q["answer"],
            family=family,
            episode_id=episode.get("episode_id", ""),
            meta={"qid": q.get("qid", ""), "type": q.get("type", "")},
        ))
    return out


def _permutation(n: int, seed: int) -> list:
    g = torch.Generator().manual_seed(int(seed))
    return torch.randperm(n, generator=g).tolist()


def skill_episode(seed: int, family: str | None = None, n_problems: int = 8,
                  distractor: bool = True) -> dict:
    """An invented-system episode from src/skillacq/systems.py, episode shaped.

    Covers the arithmetic families of systems.py and, through the merged family
    pool, the computation-free families of simple.py.
    """
    from src.skillacq.episodes import to_rl_episode
    from src.skillacq.systems import generate_episode

    return to_rl_episode(generate_episode(seed, family=family, n_problems=n_problems,
                                          distractor=distractor))


def procedure_episode(seed: int, family: str | None = None, n_problems: int = 6,
                      n_distractors: int = 1) -> dict:
    """A format-convention episode from src/skillacq/procedures.py."""
    from src.skillacq.procedures import build_procedure_episode

    return build_procedure_episode(seed, family=family, n_problems=n_problems,
                                   n_distractors=n_distractors)


def build_examples(tokenizer, seeds, families=None, kind: str = "skill",
                   n_problems: int = 8, copy_scope: str | None = None,
                   shuffle_documents: bool = True) -> list:
    """Examples over a seed range, one system per seed.

    kind "skill" draws from src/skillacq/systems.py and its merged simple
    families; kind "procedure" draws from src/skillacq/procedures.py, whose
    answers mix page material with question material and therefore default to
    the prefix copy scope.
    """
    if kind not in ("skill", "procedure"):
        raise ValueError("kind must be 'skill' or 'procedure'")
    if copy_scope is None:
        copy_scope = "evidence" if kind == "skill" else "prefix"
    fams = list(families) if families else [None]
    out = []
    for i, seed in enumerate(seeds):
        family = fams[i % len(fams)]
        if kind == "skill":
            episode = skill_episode(int(seed), family=family, n_problems=n_problems)
        else:
            episode = procedure_episode(int(seed), family=family, n_problems=n_problems)
        out.extend(examples_from_episode(
            episode, tokenizer, copy_scope=copy_scope,
            shuffle_seed=int(seed) if shuffle_documents else None,
        ))
    return out


def worldgen_examples(episodes, tokenizer, copy_scope: str = "evidence",
                      shuffle_documents: bool = False) -> list:
    """Examples from worldgen episodes, the multi-hop control.

    Worldgen answers are entity values that a supporting document states
    outright, so many of them are copyable, but the derivation is not: a two
    hop question needs the model to read one document to know which other
    document to read. A copy head helps with the last step and not with the
    step before it, which is the shape of result the comparison is looking for.
    """
    out = []
    for episode in episodes:
        out.extend(examples_from_episode(
            episode, tokenizer, copy_scope=copy_scope,
            shuffle_seed=episode.get("seed") if shuffle_documents else None,
        ))
    return out


def pointer_stats(examples: list, collator: PointerCollator) -> dict:
    """Copyability and size statistics for a set of examples.

    copy_available_rate is the fraction of examples whose every authored token
    id occurs somewhere in the copy region, which is what the token-level
    pointer actually needs. span_copyable_rate is the stricter fraction whose
    answer appears as one contiguous run, which is what an extractive span
    reader would need. answer_aligned_rate is the fraction whose target
    tokenization was found in the region rather than fallen back to; a low
    number there means the copy head is being asked to point at ids the
    evidence does not spell, which is a tokenization bug and not a model
    result.
    """
    if not examples:
        return {"examples": 0}
    rows = [collator.encode_example(ex) for ex in examples]
    n = len(rows)
    return {
        "examples": n,
        "copy_available_rate": sum(r["copy_available"] for r in rows) / n,
        "span_copyable_rate": sum(r["span_copyable"] for r in rows) / n,
        "answer_aligned_rate": sum(r["answer_aligned"] for r in rows) / n,
        "mean_evidence_tokens": sum(len(r["evidence_positions"]) for r in rows) / n,
        "mean_authored_tokens": sum(len(r["authored_positions"]) for r in rows) / n,
        "mean_sequence_tokens": sum(len(r["inputs"]) for r in rows) / n,
        "max_sequence_tokens": max(len(r["inputs"]) for r in rows),
    }
