"""Why `inverse_chain` is the one corpus family the frame grammar loses.

`QUESTION_TABLES` in `src/corpus/frames_default.py` gives `invert_chain` the
same `Q_INVERSE` template as `inverse`, and that template names only
`q.scopes[0]`. For an inverse chain the scopes are reversed, so `scopes[0]` is
the last hop's page and the earlier hops are never named. The rendered question
therefore asks which key the last page maps to the given value, whose answer is
the token one hop back, while the gold the corpus records is the token at the
start of the chain, `depth` hops back.

This is a property of the frame grammar and of the gold, not of the reader. A
reader that answers the question as written is wrong on every depth two or
deeper item, and a reader that answers the gold has to know from outside the
text how far back to walk. `src/norm/corpuscheck.py` measures it: 1.000 at
depth 1, 0.000 at depths 2, 3, 4, 6 and 8.

Run this to print one witness.
"""

from __future__ import annotations

import json
import random
import sys

from src.corpus import relations
from src.corpus.frames import global_reserved
from src.corpus.lexicon import Lexicon, reserved_words
from src.norm.render import frame_by_id, frames


def witness(fid: str = "abstract.passive_decl.key_first.wh.scope_first",
            seed: int = 7, depth: int = 2) -> dict:
    fr, _ = frames()
    frame = frame_by_id(fid)
    lex = Lexicon(random.Random(seed), reserved_words(frame),
                  global_reserved(fr))
    inst = relations.inverse_chain(random.Random(seed), lex, depth=depth,
                                   width=4, n_problems=3)
    q = inst.questions[0]
    rules = {s: [frame.fact_line(f) for f in facts] for s, facts in inst.pages}
    return {
        "fid": fid, "depth": depth,
        "pages_served": [s for s, _ in inst.pages],
        "scopes_the_question_names": [q.scopes[0]],
        "rule_lines": rules,
        "question": frame.question(q),
        "gold": str(q.answer),
        "stages": [str(s) for s in q.stages],
        "answer_to_the_question_as_written": str(q.stages[1]),
    }


def main() -> int:
    w = witness()
    print(json.dumps(w, indent=2))
    print()
    print("pages served:", ", ".join(w["pages_served"]))
    print("question names only:", w["scopes_the_question_names"][0])
    print("question:", w["question"])
    print("answer to that question as written:",
          w["answer_to_the_question_as_written"])
    print("gold the corpus records:", w["gold"])
    print("same:", w["answer_to_the_question_as_written"] == w["gold"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
