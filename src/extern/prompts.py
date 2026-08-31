"""The prompt formulations tried for every external model.

Each variant is a function from an item to a chat message list. The episode
text is the same bytes the project's own network was handed in
`src/norm/opneural.py`: the definition page or pages, the directory pages and
the question, in the order `src/norm/opsay.py:episode_text` wrote them.

`options_shown` is recorded per variant because a variant that prints the
option set hands the model something the library system never got, and a cell
built on it is an advantaged cell rather than a matched one.
"""
from __future__ import annotations

SINGLE = ("Reply with the single word that answers the question, "
          "and nothing else.")

SYS_READER = (
    "You read a document and answer a question about it. The document "
    "defines an operation you have not seen before and gives the lookup "
    "tables it reads. Apply the definition exactly as written."
)

SYS_WORKED = (
    "You read a document and answer a question about it. The document "
    "defines an operation you have not seen before and gives the lookup "
    "tables it reads. Work through the definition step by step, then give "
    "the answer."
)

WORKED = (
    "Answer the question by following the definition given above.\n"
    "Work through it in this order:\n"
    "1. Find the sentence that defines the operation named in the question, "
    "and note which maps it reads and in what order.\n"
    "2. Look up the token named in the question in each of those maps, and "
    "write down the value each map sends it to.\n"
    "3. Take the clauses of the definition in the order they are written, "
    "and find the first one whose condition holds of those values.\n"
    "4. Give what that clause says to answer. If no clause holds, give what "
    "the definition says to answer in every other case.\n"
    "Finish with a final line of the form:\nAnswer: <word>"
)


def v_bare(item):
    """The episode as written, with one line asking for one word."""
    return [{"role": "user",
             "content": item["text"].rstrip() + "\n\n" + SINGLE}]


def v_reader(item):
    """A system prompt that says what kind of document this is."""
    return [{"role": "system", "content": SYS_READER},
            {"role": "user",
             "content": item["text"].rstrip() + "\n\n" + SINGLE}]


def v_worked(item):
    """A scaffold naming the steps the definition asks for."""
    return [{"role": "system", "content": SYS_WORKED},
            {"role": "user", "content": item["text"].rstrip() + "\n\n" + WORKED}]


def v_options(item):
    """The scaffold, plus the option set printed.

    This hands the model the candidate list, which is strictly more than the
    library system is given, so it is reported as an advantaged condition and
    never as the matched one.
    """
    opts = ", ".join(sorted(item["options"]))
    tail = (WORKED + "\n\nThe answer is one of: " + opts + ".")
    return [{"role": "system", "content": SYS_WORKED},
            {"role": "user", "content": item["text"].rstrip() + "\n\n" + tail}]


VARIANTS = {
    "bare": (v_bare, False),
    "reader": (v_reader, False),
    "worked": (v_worked, False),
    "options": (v_options, True),
}


def build(name, item):
    return VARIANTS[name][0](item)


def options_shown(name):
    return VARIANTS[name][1]
