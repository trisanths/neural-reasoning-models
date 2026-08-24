"""Integer vocabulary for the procedural warm-up streams.

These streams are consumed directly as token ids during warm-up, bypassing
the text tokenizer, so this layout is a contract. All ranges are half-open
[start, end). Ids 17 through 23 are reserved for future control tokens and
must never appear in a stream.
"""

SPECIALS = {
    "EOS": 0,
    "SEP": 1,
    "PUSH": 2,
    "POP": 3,
    "OBS": 4,
    "EMPTY": 5,
    "OP_SORT": 6,
    "OP_REVERSE": 7,
    "OP_UNION": 8,
    "OP_DIFF": 9,
    "OP_DELETE": 10,
    "ROW": 11,
    "NEXT": 12,
    "EDGE": 13,
    "QUERY": 14,
    "PATH": 15,
    "UNREACH": 16,
}

EOS = SPECIALS["EOS"]
SEP = SPECIALS["SEP"]
PUSH = SPECIALS["PUSH"]
POP = SPECIALS["POP"]
OBS = SPECIALS["OBS"]
EMPTY = SPECIALS["EMPTY"]
OP_SORT = SPECIALS["OP_SORT"]
OP_REVERSE = SPECIALS["OP_REVERSE"]
OP_UNION = SPECIALS["OP_UNION"]
OP_DIFF = SPECIALS["OP_DIFF"]
OP_DELETE = SPECIALS["OP_DELETE"]
ROW = SPECIALS["ROW"]
NEXT = SPECIALS["NEXT"]
EDGE = SPECIALS["EDGE"]
QUERY = SPECIALS["QUERY"]
PATH = SPECIALS["PATH"]
UNREACH = SPECIALS["UNREACH"]

SPECIAL_RANGE = (0, 24)

MAX_K = 16
BRACKET_BASE = SPECIAL_RANGE[1]
BRACKET_RANGE = (BRACKET_BASE, BRACKET_BASE + 2 * MAX_K)

NUM_VALUES = 64
VALUE_BASE = BRACKET_RANGE[1]
VALUE_RANGE = (VALUE_BASE, VALUE_BASE + NUM_VALUES)

BIT_BASE = VALUE_RANGE[1]
BIT_RANGE = (BIT_BASE, BIT_BASE + 2)

NUM_NODES = 64
NODE_BASE = BIT_RANGE[1]
NODE_RANGE = (NODE_BASE, NODE_BASE + NUM_NODES)

VOCAB_SIZE = NODE_RANGE[1]


def open_token(bracket_type):
    if not 0 <= bracket_type < MAX_K:
        raise ValueError(f"bracket type {bracket_type} out of range")
    return BRACKET_BASE + 2 * bracket_type


def close_token(bracket_type):
    if not 0 <= bracket_type < MAX_K:
        raise ValueError(f"bracket type {bracket_type} out of range")
    return BRACKET_BASE + 2 * bracket_type + 1


def value_token(v):
    if not 0 <= v < NUM_VALUES:
        raise ValueError(f"value {v} out of range")
    return VALUE_BASE + v


def bit_token(b):
    if b not in (0, 1):
        raise ValueError(f"bit {b} out of range")
    return BIT_BASE + b


def node_token(n):
    if not 0 <= n < NUM_NODES:
        raise ValueError(f"node {n} out of range")
    return NODE_BASE + n


def describe():
    """Return a json-serializable description of the vocabulary layout."""
    return {
        "vocab_size": VOCAB_SIZE,
        "dtype": "uint16",
        "specials": dict(SPECIALS),
        "reserved_ids": list(range(len(SPECIALS), SPECIAL_RANGE[1])),
        "ranges": {
            "special": list(SPECIAL_RANGE),
            "bracket": list(BRACKET_RANGE),
            "value": list(VALUE_RANGE),
            "bit": list(BIT_RANGE),
            "node": list(NODE_RANGE),
        },
        "encoding": {
            "bracket": "open_i = bracket_base + 2*i, close_i = bracket_base + 2*i + 1, i < 16",
            "value": "value_base + v, v < 64",
            "bit": "bit_base + b, b in {0, 1}",
            "node": "node_base + n, n < 64",
        },
    }
