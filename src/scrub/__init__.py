"""Scrubbing and extractive QA over natural text.

The scrubber strips real-world anchors from raw text so the regime E
natural share carries the shape of language without recoverable world
knowledge. The extractive QA generator builds question-answer pairs whose
answers are verifiable substrings of the scrubbed passage, so the traces
teach extraction rather than recall.
"""

from src.scrub.common_words import COMMON_WORDS
from src.scrub.extractive_qa import (DEFAULT_TYPE_MIX, check_qa, find_spans,
                                     generate_qa, render_qa_trace,
                                     split_sentences)
from src.scrub.scrubber import (FUNCTION_WORDS, ScrubResult, scrub_document,
                                scrub_text)

__all__ = [
    "COMMON_WORDS",
    "DEFAULT_TYPE_MIX",
    "FUNCTION_WORDS",
    "ScrubResult",
    "check_qa",
    "find_spans",
    "generate_qa",
    "render_qa_trace",
    "scrub_document",
    "scrub_text",
    "split_sentences",
]
