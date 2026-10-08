"""Real ProsQA, tokenised with a HuggingFace tokenizer.

This is the benchmark Coconut wins on (97.0 against 77.5 for explicit chain of
thought at GPT-2 scale), because answering requires holding several candidate
paths at once and a written chain has to commit to a branch before it has
searched.

Formatting follows the reference implementation: a newline after the question
and after each reasoning step, and the answer introduced by '### '. The marker
matters for evaluation, since under the curriculum the model emits any remaining
reasoning steps before the answer and we need an unambiguous split.

Note on step counts: ProsQA chains are 3 to 6 steps long. The curriculum keeps
the number of latents uniform across a batch (via pad_latent_to_max) while the
number of skipped steps varies per example, which is what
``dataset.build_batch`` expects.
"""

from __future__ import annotations

import json

from .data import Example

ANSWER_MARKER = "### "


def load_prosqa(path: str, limit: int | None = None) -> list[Example]:
    """Reads a prosqa_*.json file from the Coconut repo."""
    with open(path) as f:
        raw = json.load(f)
    if limit is not None:
        raw = raw[:limit]
    return [
        Example(
            question=r["question"],
            steps=list(r["steps"]),
            answer=r["answer"],
            n_hops=len(r["steps"]),
            meta={"target": r["answer"].rstrip(".").split()[-1]},
        )
        for r in raw
    ]


class ProsQAHFTokenizer:
    """Wraps an HF tokenizer with the spacing convention ProsQA needs.

    Subword tokenizers are whitespace sensitive, so the separators have to be
    part of the encoded string rather than added afterwards, or the curriculum's
    concatenated segments will not tokenise the same way as the full sequence.
    """

    def __init__(self, adapter) -> None:
        self.a = adapter
        self._dummy = self._detect_dummy_prefix(adapter)
        self.pad_id = adapter.pad_id
        self.eos_id = adapter.eos_id
        self.bos_id = adapter.bos_id
        self.bot_id = adapter.bot_id
        self.eot_id = adapter.eot_id
        self.latent_id = adapter.latent_id

    @staticmethod
    def _detect_dummy_prefix(adapter) -> int | None:
        """Finds the phantom leading token SentencePiece adds to every encode().

        Llama-family tokenizers prepend a whitespace marker to any string they
        encode, so a continuation segment would carry a token the full sequence
        does not have. Qwen's byte-level BPE does not do this, and detection
        returns None there.

        Detected rather than hard-coded, so this works across tokenizer families.
        """
        # The probe must start with a non-word character. SentencePiece folds
        # its prefix into the first word ("Tom" -> a single "_Tom" token), so a
        # word probe reveals nothing; after a newline the prefix appears as its
        # own token instead.
        a, b = adapter.encode("\nTom"), adapter.encode("\nxyzzy")
        # Requiring an *empty* decode, not merely whitespace, avoids mistaking
        # a real newline token (Qwen) for a phantom one.
        if a and b and a[0] == b[0] and adapter.decode([a[0]]) == "":
            return a[0]
        return None

    def _strip_dummy(self, ids: list[int]) -> list[int]:
        if self._dummy is not None and ids and ids[0] == self._dummy:
            return ids[1:]
        return ids

    def __len__(self) -> int:
        return len(self.a)

    def encode(self, text: str) -> list[int]:
        return self.a.encode(text)

    def decode(self, ids: list[int]) -> str:
        return self.a.decode(ids)

    # The curriculum builder encodes question / step / answer separately, so
    # each separator *leads* its segment rather than trailing the previous one.
    # SentencePiece assigns a different id to a word at the start of a string
    # than to the same word after a newline, so appending the separator would
    # make the concatenated segments disagree with the full sequence.
    # Separators *trail* their segment. In byte-level BPE a newline followed by
    # a letter is always a pretokeniser boundary, so segments split cleanly;
    # leading separators do not work because BPE merges the preceding character
    # into the newline ('?\n' is one Qwen token).
    def encode_question(self, q: str) -> list[int]:
        return self.a.encode(q + "\n")  # genuinely the start of the sequence

    def encode_step(self, s: str) -> list[int]:
        return self._strip_dummy(self.a.encode(s + "\n"))

    def encode_answer(self, ans: str) -> list[int]:
        return self._strip_dummy(self.a.encode(ANSWER_MARKER + ans))


class TokenizerIncompatible(RuntimeError):
    """Raised when segment-wise encoding disagrees with the full sequence."""


def assert_tokenizer_compatible(
    tok: ProsQAHFTokenizer, examples: list[Example], n: int = 64
) -> None:
    """Gate before training: segments must tokenise as the full sequence does.

    The curriculum builds truncated variants by concatenating separately
    encoded segments. If the tokenizer merges across those boundaries the
    variants silently stop corresponding to the full chain, and every number
    downstream is wrong without anything crashing.

    Byte-level BPE (Qwen, GPT-2) passes: a newline followed by a letter is
    always a pretokeniser boundary. SentencePiece (Llama family) cannot pass,
    because it gives a word different ids at a string start than mid-sequence
    ("Tom" vs "_Tom"), and no amount of prefix stripping fixes that. Supporting
    those would need offset-based splitting of the whole sequence.
    """
    bad = [i for i, e in enumerate(examples[:n]) if not verify_concatenation(tok, e)]
    if bad:
        raise TokenizerIncompatible(
            f"{len(bad)}/{min(n, len(examples))} examples tokenise differently "
            "segment-wise than as a whole sequence. This tokenizer needs "
            "offset-based segment splitting; byte-level BPE tokenizers "
            "(Qwen, GPT-2) work as-is."
        )


def verify_concatenation(tok: ProsQAHFTokenizer, ex: Example) -> bool:
    """Checks that per-segment encoding equals encoding the whole string.

    The reference implementation asserts this, and it is worth keeping: if a
    subword tokenizer merges across a segment boundary, the curriculum's
    truncated variants stop lining up with the full chain and every downstream
    number is quietly wrong.
    """
    whole = tok.encode(
        ex.question + "\n" + "".join(s + "\n" for s in ex.steps) + ANSWER_MARKER + ex.answer
    )
    parts = tok.encode_question(ex.question)
    for s in ex.steps:
        parts += tok.encode_step(s)
    parts += tok.encode_answer(ex.answer)
    return whole == parts
