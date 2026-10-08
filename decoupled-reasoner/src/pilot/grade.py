"""The strict grader for free-generation pilot items, and its lenient twin.

Three answer kinds, and one rule for all of them: find the answer line, list
every candidate it names, and score correct only when exactly the gold is
named. Naming more than the gold is a hedge and scores wrong, which is the
DISCOVERY.md rule against containment graders.

  int     the gold is one whole number. Every integer on the answer line is a
          candidate named; a "mod 101" style clause is removed first when it
          names the item's own modulus, because it restates the modulus
          rather than offering a second answer. A mod clause naming any
          other number counts that number as a candidate.
  names   the gold is one or more names from a closed candidate list (object
          names of an algebra, labels of a rule family). The set of
          candidates named must equal the gold set.

The lenient score is recorded beside the strict one and never instead of it:
first integer on the line for int items, gold set contained in the named set
for names items.

The answer line is the last line that starts with "Answer:" (markdown
emphasis allowed), or, for a base model continuing a prompt that already
ends in "Answer:", the first non-empty line of the continuation. When an
instruct reply has no answer line the last non-empty line stands in and
answer_found is False, so the rate of replies that ignored the format is
visible rather than folded into accuracy. A base model's first line always
counts as found, so answered (the line names at least one candidate) is the
column that shows how often a reply gives any answer at all.
"""

from __future__ import annotations

import re

_ANSWER_RE = re.compile(
    r"^[\s>*_#`-]*(?:final\s+)?answer[\s*_`]*[:=]\s*(.*)$", re.I)
_INT_RE = re.compile(r"(?<![\w.])-?\d+(?![\w])")
_MOD_RE = re.compile(r"\(?\s*(?:mod(?:ulo)?|\\pmod|\\bmod)\s*\{?\s*(\d+)\s*\}?\s*\)?",
                     re.I)
_BOXED_RE = re.compile(r"\\boxed\s*\{([^{}]*)\}")


def _clean(line: str) -> str:
    line = _BOXED_RE.sub(r"\1", line)
    line = re.sub(r"[*`$]", " ", line)
    line = line.replace("\\(", " ").replace("\\)", " ")
    return " ".join(line.split())


def answer_line(text: str, completion: bool = False) -> tuple[str, bool]:
    """(the answer line, whether an explicit answer line was found)."""
    lines = [ln for ln in (text or "").splitlines()]
    if completion:
        for ln in lines:
            if ln.strip():
                return _clean(ln), True
        return "", False
    found = None
    for i, ln in enumerate(lines):
        m = _ANSWER_RE.match(ln)
        if m:
            content = m.group(1).strip()
            if not _clean(content):
                # "Answer:" alone on its line, the answer on the next one.
                for nxt in lines[i + 1:]:
                    if nxt.strip():
                        content = nxt
                        break
            found = content
    if found is not None:
        return _clean(found), True
    for ln in reversed(lines):
        if ln.strip():
            return _clean(ln), False
    return "", False


def named_ints(line: str, modulus: int | None = None) -> list[str]:
    """Every distinct integer on the line. A "mod M" clause naming the
    item's own modulus restates it and is removed first; a mod clause with
    any other number names that number like any other integer."""
    if modulus:
        line = _MOD_RE.sub(lambda m: " " if int(m.group(1)) == int(modulus)
                           else m.group(0), line)
    out: list[str] = []
    for tok in _INT_RE.findall(line):
        v = str(int(tok))
        if v not in out:
            out.append(v)
    return out


def named_candidates(line: str, candidates) -> list[str]:
    low = line.lower()
    out = []
    for c in candidates:
        if re.search(rf"(?<![\w]){re.escape(c.lower())}(?![\w])", low):
            out.append(c)
    return out


def gold_set(answer: str) -> set[str]:
    return {a.strip().lower() for a in answer.split(",") if a.strip()}


def grade(text: str, item: dict, completion: bool = False) -> dict:
    """Grade one reply against one item. item needs answer, answer_kind,
    and candidates for names items."""
    line, found = answer_line(text, completion=completion)
    kind = item["answer_kind"]
    if kind == "int":
        named = named_ints(line, item.get("modulus"))
        gold = str(int(item["answer"]))
        hedge = len(named) > 1
        parsed = named[0] if len(named) == 1 else (",".join(named) or None)
        correct = (not hedge) and named == [gold]
        lenient = bool(named) and named[0] == gold
    elif kind == "names":
        cands = item["candidates"]
        named = named_candidates(line, cands)
        want = gold_set(item["answer"])
        got = {n.lower() for n in named}
        hedge = len(got) > len(want)
        parsed = ", ".join(sorted(got)) if got else None
        correct = got == want
        lenient = want <= got
    else:
        raise ValueError(f"unknown answer kind {kind!r}")
    return {"answer_line": line[:300], "answer_found": found,
            "answered": bool(named),
            "parsed": parsed, "n_named": len(named), "hedge": hedge,
            "correct": bool(correct), "correct_lenient": bool(lenient)}


def canary_reply(item: dict) -> str:
    """The hedging canary: a reply naming every candidate at once."""
    if item["answer_kind"] == "names":
        return "Answer: " + ", ".join(item["candidates"])
    space = int(item.get("answer_space") or 100)
    return "Answer: " + " ".join(str(v) for v in range(space))
