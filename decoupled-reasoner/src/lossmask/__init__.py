"""Suppress memorization by weighting factual spans out of the loss.

Regime E removed factual gradients by destroying the corpus: entities
replaced, numbers perturbed. It worked on the probes and it cost reading,
which never got past 0.83 of the natural baseline. The forward pass was
being asked to read text no one wrote.

This package takes the other route. The corpus stays natural. A tagger marks
the factual spans, the shard format carries one tag byte per token beside the
token, and the training step multiplies each token's cross entropy by a weight
looked up from its tag. The model reads real sentences and is simply not paid
for reproducing the names, numbers, and dates inside them.

The tags are stored, the weights are not, so one build of the corpus serves
every arm of a weighting experiment and the arms differ only in a config
block.
"""

from src.lossmask.loss import weighted_cross_entropy
from src.lossmask.shards import (TaggedShardReader, TaggedShardWriter,
                                 WeightedBatchLoader, write_index)
from src.lossmask.tagger import (date_spans, encode_with_tags, factual_spans,
                                 tag_histogram, tag_offsets)
from src.lossmask.tags import (FACTUAL_TAGS, TAG_DATE, TAG_ENTITY, TAG_NUMBER,
                               TAG_PLAIN, TAG_WEB, TAG_NAMES, describe_weights,
                               weight_table)

__all__ = [
    "FACTUAL_TAGS",
    "TAG_DATE",
    "TAG_ENTITY",
    "TAG_NAMES",
    "TAG_NUMBER",
    "TAG_PLAIN",
    "TAG_WEB",
    "TaggedShardReader",
    "TaggedShardWriter",
    "WeightedBatchLoader",
    "date_spans",
    "describe_weights",
    "encode_with_tags",
    "factual_spans",
    "tag_histogram",
    "tag_offsets",
    "weight_table",
    "weighted_cross_entropy",
    "write_index",
]
