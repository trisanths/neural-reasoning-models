"""Domain word bundles: the open-class vocabulary a frame is spelled in.

A frame is a lexicon crossed with a set of sentence forms. The lexicon holds
only words; it holds no sentence structure at all. Everything that decides
clause order, voice, or where the key sits relative to the value lives in
`src/frames/forms.py`. The split is what makes the two distance components in
`src/frames/distance.py` mean what they say: swapping a lexicon moves the words
and leaves the skeleton untouched, swapping a form moves the skeleton and
leaves the words untouched.

The `routing` lexicon carries the exact words of `src/skillacq/simple.py`, so
the grammar point (routing, native forms) reproduces the published wording byte
for byte. That check runs in `src/frames/tests/test_frames.py`.

Every noun here is a single word and pluralises by the regular rule, because
the forms build plurals and articles mechanically.
"""

from __future__ import annotations

from dataclasses import dataclass

VOWELS = "aeiou"


def art(word: str) -> str:
    """Indefinite article for a word, by first letter."""
    return "an" if word[:1].lower() in VOWELS else "a"


def cap(word: str) -> str:
    return word[:1].upper() + word[1:]


def plural(word: str) -> str:
    if word.endswith(("s", "x", "ch", "sh")):
        return word + "es"
    if word.endswith("y") and word[-2:-1] not in VOWELS:
        return word[:-1] + "ies"
    return word + "s"


@dataclass(frozen=True)
class SubWords:
    """Words for `substitution_rule`: a stated mapping from keys to values."""

    dom: str      # the document's own noun: "routing table"
    sect: str     # section title over the mapping lines: "Routing"
    site: str     # where it happens: "office"
    ent: str      # the thing being mapped: "request"
    key: str      # the mapping's input role: "type"
    val: str      # the mapping's output role: "desk"
    vpart: str    # past participle of the assignment verb: "handled"
    vprep: str    # preposition that participle takes: "by"
    vact: str     # third person active: "handles"
    vimp: str     # imperative stem, capitalised: "Route"
    vsort: str    # participle for "are routed by their type"
    vsort3: str   # third person of the same: "routes"
    varr: str     # arrival verb phrase: "arrives at"
    vgo: str      # fallback verb phrase: "goes to"


@dataclass(frozen=True)
class ExcWords:
    """Words for `exception_rule`: one general rule and one stated override."""

    dom: str      # "protocol"
    ent: str      # "item"
    key: str      # "category"
    val: str      # "treatment"
    vreach3: str  # "reaches"
    vreachp: str  # "reaching"
    vgivep: str   # participle after the copula: "given"
    vrecv: str    # bare verb in the question: "receive"
    vimp: str     # imperative stem, capitalised: "Send"


@dataclass(frozen=True)
class ThrWords:
    """Words for `threshold_rule`: one stated comparison against a limit."""

    dom: str      # "classification"
    ent: str      # "specimen"
    meas: str     # "reading"
    vcall: str    # participle after the copula: "called"
    vhas: str     # "carries"


@dataclass(frozen=True)
class Lexicon:
    name: str
    sub: SubWords
    exc: ExcWords
    thr: ThrWords

    def words(self, family: str):
        return {"substitution_rule": self.sub,
                "exception_rule": self.exc,
                "threshold_rule": self.thr}[family]


def _lex(name, sub, exc, thr) -> Lexicon:
    return Lexicon(name, SubWords(*sub), ExcWords(*exc), ThrWords(*thr))


# The tuple order matches the dataclass field order above.
LEXICONS: dict[str, Lexicon] = {lx.name: lx for lx in [
    _lex("routing",
         ("routing table", "Routing", "office", "request", "type", "desk",
          "handled", "by", "handles", "Route", "routed", "routes",
          "arrives at", "goes to"),
         ("protocol", "item", "category", "treatment", "reaches", "reaching",
          "given", "receive", "Send"),
         ("classification", "specimen", "reading", "called", "carries")),
    _lex("assembly",
         ("processing table", "Processing", "stage", "item", "grade", "unit",
          "processed", "by", "processes", "Process", "processed", "processes",
          "arrives at", "goes to"),
         ("finishing line", "piece", "class", "finish", "reaches", "reaching",
          "given", "receive", "Pass"),
         ("gauge chart", "part", "measurement", "rated", "carries")),
    _lex("depot",
         ("bay chart", "Storage", "depot", "crate", "label", "bay",
          "stored", "in", "stores", "Store", "stored", "stores",
          "arrives at", "goes to"),
         ("packing line", "crate", "contents", "wrap", "reaches", "reaching",
          "given", "receive", "Send"),
         ("intake", "crate", "weight", "stacked as", "carries")),
    _lex("panel",
         ("assignment sheet", "Assignments", "panel", "case", "grade",
          "reviewer", "assigned", "to", "takes", "Assign", "assigned",
          "assigns", "reaches", "goes to"),
         ("review", "file", "status", "handling", "enters", "entering",
          "given", "receive", "Send"),
         ("panel", "applicant", "score", "ranked", "carries")),
    _lex("clinic",
         ("triage chart", "Triage", "clinic", "sample", "marker", "ward",
          "admitted", "to", "admits", "Admit", "sorted", "sorts",
          "arrives at", "goes to"),
         ("ward round", "patient", "flag", "regimen", "reaches", "reaching",
          "given", "receive", "Refer"),
         ("assay", "sample", "titre", "graded", "carries")),
    _lex("archive",
         ("shelf list", "Filing", "archive", "record", "tag", "shelf",
          "filed", "on", "holds", "File", "filed", "files",
          "reaches", "goes to"),
         ("catalogue", "record", "mark", "binding", "reaches", "reaching",
          "given", "receive", "Send"),
         ("survey", "volume", "length", "listed as", "carries")),
    _lex("kitchen",
         ("ticket board", "Preparation", "kitchen", "order", "ticket",
          "station", "prepared", "at", "prepares", "Send", "sorted", "sorts",
          "arrives at", "goes to"),
         ("pass", "dish", "note", "garnish", "reaches", "reaching",
          "given", "receive", "Send"),
         ("portion scale", "portion", "weight", "called", "carries")),
    _lex("rail",
         ("shunting list", "Shunting", "yard", "wagon", "consist", "siding",
          "shunted", "to", "takes", "Shunt", "shunted", "shunts",
          "arrives at", "goes to"),
         ("works depot", "wagon", "marking", "livery", "reaches", "reaching",
          "given", "receive", "Send"),
         ("loading gauge", "wagon", "load", "classed as", "carries")),
    _lex("mailroom",
         ("delivery chart", "Delivery", "mailroom", "parcel", "class",
          "pigeonhole", "delivered", "to", "holds", "Deliver", "sorted",
          "sorts", "arrives at", "goes to"),
         ("sorting floor", "parcel", "band", "sticker", "reaches", "reaching",
          "given", "receive", "Send"),
         ("postal scale", "parcel", "mass", "banded as", "carries")),
    _lex("registry",
         ("cause list", "Listing", "registry", "petition", "head", "roll",
          "listed", "on", "carries", "List", "listed", "lists",
          "reaches", "goes to"),
         ("chamber", "petition", "heading", "direction", "reaches",
          "reaching", "given", "receive", "Refer"),
         ("registry", "petition", "valuation", "entered as", "carries")),
    _lex("forge",
         ("heat chart", "Working", "forge", "billet", "heat", "hearth",
          "worked", "at", "works", "Work", "worked", "works",
          "enters", "goes to"),
         ("shop floor", "billet", "temper", "quench", "enters", "entering",
          "given", "receive", "Send"),
         ("hardness bay", "billet", "hardness", "stamped", "carries")),
    _lex("observatory",
         ("log chart", "Logging", "observatory", "reading", "band", "log",
          "recorded", "in", "holds", "Record", "recorded", "records",
          "arrives at", "goes to"),
         ("correction desk", "reading", "flag", "correction", "reaches",
          "reaching", "given", "receive", "Send"),
         ("magnitude survey", "reading", "magnitude", "logged as", "carries")),
    _lex("abstract",
         ("table", "Entries", "table", "entry", "type", "value",
          "paired", "with", "matches", "Map", "paired", "pairs",
          "is presented to", "goes to"),
         ("rule set", "input", "class", "outcome", "enters", "entering",
          "given", "take", "Present"),
         ("scheme", "item", "number", "valued as", "carries")),
]}

# The lexicon whose words are the ones the RL stage trained on.
NATIVE_LEXICON = "routing"
