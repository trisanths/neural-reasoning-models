"""The token tag alphabet and the tag to weight table.

A tagged shard stores one uint8 tag per token. The tag says what kind of
span the token belongs to, not how much it should count: the weight is a
training time decision, so the same corpus serves every arm of a weighting
experiment and the arms differ only in the numbers below.

Tag 0 is plain text and always exists. The other tags name the three
anchor kinds src/scrub already detects plus dates, which the scrubber
handles as a special case of numbers and which this package separates out
so a run can suppress dates without touching names.
"""

import numpy as np

TAG_PLAIN = 0
TAG_ENTITY = 1
TAG_NUMBER = 2
TAG_DATE = 3
TAG_WEB = 4

N_TAGS = 8  # room in the byte for tags a later experiment adds

TAG_NAMES = {
    TAG_PLAIN: "plain",
    TAG_ENTITY: "entity",
    TAG_NUMBER: "number",
    TAG_DATE: "date",
    TAG_WEB: "web",
}
NAME_TAGS = {name: tag for tag, name in TAG_NAMES.items()}

# The spans this project calls factual: every anchor that ties a passage to
# a particular world. Language competence lives in the complement.
FACTUAL_TAGS = (TAG_ENTITY, TAG_NUMBER, TAG_DATE, TAG_WEB)


def weight_table(weights: dict | None) -> np.ndarray:
    """Build the float32 lookup a loader indexes with a tag byte.

    weights maps tag names to floats. Anything left out keeps weight 1.0,
    so {} is the control arm and {"entity": 0.0} suppresses names alone.
    Passing None also gives the control arm.
    """
    table = np.ones(N_TAGS, dtype=np.float32)
    for name, value in (weights or {}).items():
        if name not in NAME_TAGS:
            raise ValueError(
                f"unknown tag {name!r}; known tags are {sorted(NAME_TAGS)}")
        value = float(value)
        if value < 0.0:
            raise ValueError(f"tag {name!r} has negative weight {value}")
        table[NAME_TAGS[name]] = value
    return table


def describe_weights(table: np.ndarray) -> dict:
    """The named form of a weight table, for logs and run metadata."""
    return {name: float(table[tag]) for tag, name in sorted(TAG_NAMES.items())}
