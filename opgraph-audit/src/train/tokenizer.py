"""32k byte level BPE tokenizer with the special tokens from SPEC.md section 2.

Vocabulary layout, fixed by construction:
  ids 0..6            the seven named special tokens, in SPEC order
  ids 7..262          256 reserved slots for procgen warm up symbols
  ids 263 and up      byte alphabet and learned BPE merges

The reserved slots exist so raw procgen streams can be mapped into the
vocabulary by a constant offset. See src/train/data.py for the convention.
"""

from tokenizers import Tokenizer, decoders, models, pre_tokenizers, trainers

SPECIAL_TOKENS = [
    "<|doc|>",
    "<|q|>",
    "<|a|>",
    "<|retrieve|>",
    "<|result|>",
    "<|world|>",
    "<|eot|>",
]

PROCGEN_OFFSET = len(SPECIAL_TOKENS)
PROCGEN_SYMBOLS = 256
RESERVED_TOKENS = [f"<|pg{i}|>" for i in range(PROCGEN_SYMBOLS)]

DEFAULT_VOCAB_SIZE = 32768


class TrainTokenizer:
    """Thin wrapper that guarantees exact round trips through special tokens."""

    def __init__(self, tokenizer: Tokenizer):
        self.tokenizer = tokenizer
        self.special_ids = {name: tokenizer.token_to_id(name) for name in SPECIAL_TOKENS}
        missing = [name for name, tid in self.special_ids.items() if tid is None]
        if missing:
            raise ValueError(f"tokenizer is missing special tokens: {missing}")
        self._passthrough = {}
        for name in SPECIAL_TOKENS + RESERVED_TOKENS:
            tid = tokenizer.token_to_id(name)
            if tid is not None:
                self._passthrough[tid] = name

    @property
    def vocab_size(self) -> int:
        return self.tokenizer.get_vocab_size()

    def token_id(self, token: str) -> int:
        tid = self.tokenizer.token_to_id(token)
        if tid is None:
            raise KeyError(f"unknown token {token!r}")
        return tid

    def encode(self, text: str) -> list[int]:
        return self.tokenizer.encode(text).ids

    def decode(self, ids: list[int]) -> str:
        # The library decoder can mangle spacing around added tokens, so
        # special and reserved tokens are spliced back in verbatim.
        parts: list[str] = []
        pending: list[int] = []
        for tid in ids:
            name = self._passthrough.get(tid)
            if name is None:
                pending.append(tid)
                continue
            if pending:
                parts.append(self.tokenizer.decode(pending, skip_special_tokens=False))
                pending = []
            parts.append(name)
        if pending:
            parts.append(self.tokenizer.decode(pending, skip_special_tokens=False))
        return "".join(parts)

    def save(self, path: str) -> None:
        self.tokenizer.save(str(path))


def train_tokenizer(
    files: list[str], out_path: str | None = None, vocab_size: int = DEFAULT_VOCAB_SIZE
) -> TrainTokenizer:
    """Train a byte level BPE on the given text files and optionally save it."""
    tokenizer = Tokenizer(models.BPE(unk_token=None))
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tokenizer.decoder = decoders.ByteLevel()
    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size,
        special_tokens=SPECIAL_TOKENS + RESERVED_TOKENS,
        initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
        show_progress=False,
    )
    tokenizer.train([str(f) for f in files], trainer)
    wrapped = TrainTokenizer(tokenizer)
    if out_path is not None:
        wrapped.save(out_path)
    return wrapped


def load_tokenizer(path: str) -> TrainTokenizer:
    return TrainTokenizer(Tokenizer.from_file(str(path)))
