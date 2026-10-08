"""Scrubbing, extractive QA, and retrieval episodes over natural text.

The scrubber strips real-world anchors from raw text so the regime E
natural share carries the shape of language without recoverable world
knowledge; its shuffle policy reassigns real names through a corpus
pool so real name tokens still train. The extractive QA generator
builds question-answer pairs whose answers are verifiable substrings of
the scrubbed passage, so the traces teach extraction rather than
recall. The web retrieval builder turns bundles of scrubbed documents
into verified multi-hop-lite retrieval traces.
"""

from src.scrub.common_words import COMMON_WORDS
from src.scrub.extractive_qa import (DEFAULT_TYPE_MIX, E2_TYPE_MIX, check_qa,
                                     find_spans, generate_qa,
                                     render_qa_trace, split_sentences)
from src.scrub.name_pool import (EntityPool, harvest_counts, harvest_pool,
                                 pool_from_counts)
from src.scrub.scrubber import (FUNCTION_WORDS, ScrubResult, anchor_spans,
                                scrub_document, scrub_text)
from src.scrub.web_retrieval import (build_web_episode, render_web_episode,
                                     verify_web_episode)

__all__ = [
    "COMMON_WORDS",
    "DEFAULT_TYPE_MIX",
    "E2_TYPE_MIX",
    "EntityPool",
    "FUNCTION_WORDS",
    "ScrubResult",
    "anchor_spans",
    "build_web_episode",
    "check_qa",
    "find_spans",
    "generate_qa",
    "harvest_counts",
    "harvest_pool",
    "pool_from_counts",
    "render_qa_trace",
    "render_web_episode",
    "scrub_document",
    "scrub_text",
    "split_sentences",
    "verify_web_episode",
]
