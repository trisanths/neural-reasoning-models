"""The frame seam.

Another workflow is building a programmatic frame generator in `src/frames/`.
It did not exist when this corpus was built, so `src/corpus/frames_default.py`
supplies a bank of its own and this module is the single place that decides
which bank is in use. When `src/frames/` lands, the only change needed is that
it expose `build_frames()` returning objects with the methods listed in
`REQUIRED_METHODS`; `load_frames` will then prefer it, and nothing downstream
moves.

Nothing here writes to `src/frames/`.
"""

from __future__ import annotations

import importlib

REQUIRED_METHODS = (
    "page",             # (scope, facts, preamble_level) -> str
    "question",         # (Question) -> str
    "fact_line",        # (Fact) -> str
    "lookup_regex",     # (key) -> str, the shortcut reader's pattern
    "template_corpus",  # () -> list[str], for the per frame reserved vocabulary
)

REQUIRED_ATTRS = ("fid", "lexicon", "mode", "key_pos", "qform", "scope_pos")


def _conforms(frame) -> bool:
    return (all(callable(getattr(frame, m, None)) for m in REQUIRED_METHODS)
            and all(hasattr(frame, a) for a in REQUIRED_ATTRS))


def load_frames(prefer_external: bool = True) -> tuple:
    """Return (frames, source). Source names which bank actually supplied them.

    The corpus manifest records the source, so a run built on the internal bank
    is never mistaken for one built on `src/frames/`.
    """
    if prefer_external:
        try:
            mod = importlib.import_module("src.frames")
            builder = getattr(mod, "build_frames", None)
            if builder is not None:
                frames = list(builder())
                bad = [f for f in frames if not _conforms(f)]
                if frames and not bad:
                    return frames, "src.frames"
        except ImportError:
            pass
    from src.corpus import frames_default
    return list(frames_default.FRAMES), "src.corpus.frames_default"


def global_reserved(frames) -> frozenset:
    """The union of every frame's own English words.

    An invented word is drawn to avoid its own frame's reserved set, which is
    the correctness requirement, and also this union, which keeps one seed's
    invented vocabulary usable in every frame so the cross frame gold agreement
    check compares like with like.
    """
    from src.corpus.lexicon import reserved_words
    out: set = set()
    for f in frames:
        out |= reserved_words(f)
    return frozenset(out)
