"""Real-name replacement pool for the shuffle scrub policy.

The invented-name policy leaves every real-name token untrained: models
raised on it mutate real entities into synthetic morphology and cannot
handle real-world surface forms. The shuffle policy fixes that by
replacing each detected entity with a different real entity surface form
drawn from a pool harvested from the corpus itself. Names are reassigned
at random per document, so the facts still die, while every frequent
real name keeps appearing in training text.

harvest_counts runs the scrubber's own entity detector over sample
documents and counts surface forms. pool_from_counts keeps the most
frequent forms, ordered by descending count then alphabetically, so a
pool built from the same sample is identical everywhere. harvest_pool
composes the two.

Forms are bucketed by word count (one, two, or three) and rough
character length. pick serves a form from the bucket matching the
surface being replaced, walking outward to the nearest nonempty bucket,
and never returns the surface itself, so capitalization shape and rough
length survive while the name always moves.
"""

from collections import Counter

from src.scrub.scrubber import entity_runs

MAX_FORM_WORDS = 3
MAX_FORM_CHARS = 40

# Character thresholds separating the three rough length buckets.
_LENGTH_EDGES = (6, 12)


def _length_bucket(form: str) -> int:
    for i, edge in enumerate(_LENGTH_EDGES):
        if len(form) <= edge:
            return i
    return len(_LENGTH_EDGES)


def _bucket_key(form: str) -> tuple:
    return (min(MAX_FORM_WORDS, len(form.split())), _length_bucket(form))


class EntityPool:
    """Frequency-ordered real entity surface forms, bucketed by shape.

    forms keeps the construction order, so two pools built from the same
    form list behave identically under the same rng draws.
    """

    def __init__(self, forms):
        self.forms = [" ".join(f.split()) for f in forms]
        if len({f.lower() for f in self.forms}) < 2:
            raise ValueError(
                "an entity pool needs at least two distinct forms")
        self.buckets: dict = {}
        for form in self.forms:
            self.buckets.setdefault(_bucket_key(form), []).append(form)

    def __len__(self) -> int:
        return len(self.forms)

    def pick(self, surface: str, rng) -> str:
        """One pool form for surface, drawn by rng from the nearest
        nonempty bucket, never surface itself."""
        surface = " ".join(surface.split())
        want = _bucket_key(surface)
        keys = sorted(self.buckets,
                      key=lambda k: (abs(k[0] - want[0]),
                                     abs(k[1] - want[1]), k))
        low = surface.lower()
        for key in keys:
            bucket = self.buckets[key]
            idx = int(rng.integers(len(bucket)))
            form = bucket[idx]
            if form.lower() == low:
                if len(bucket) == 1:
                    continue
                form = bucket[(idx + 1) % len(bucket)]
            return form
        raise ValueError(f"pool cannot replace {surface!r}")


def harvest_counts(texts) -> Counter:
    """Counter of detected entity surface forms over texts, whitespace
    collapsed, oversized forms skipped."""
    counts: Counter = Counter()
    for text in texts:
        for s, e in entity_runs(text):
            form = " ".join(text[s:e].split())
            if (len(form) > MAX_FORM_CHARS
                    or len(form.split()) > MAX_FORM_WORDS):
                continue
            counts[form] += 1
    return counts


def pool_from_counts(counts: Counter, max_forms: int = 20000,
                     min_count: int = 2) -> EntityPool:
    """Pool of the most frequent forms in counts. When the min_count
    floor leaves fewer than two distinct forms, the floor drops to one so
    small samples still harvest."""
    selected = [(c, f) for f, c in counts.items() if c >= min_count]
    if len({f.lower() for _, f in selected}) < 2:
        selected = [(c, f) for f, c in counts.items()]
    ordered = sorted(selected, key=lambda cf: (-cf[0], cf[1]))
    return EntityPool([f for _, f in ordered[:max_forms]])


def harvest_pool(texts, max_forms: int = 20000,
                 min_count: int = 2) -> EntityPool:
    """Harvest a pool straight from sample texts."""
    return pool_from_counts(harvest_counts(texts), max_forms=max_forms,
                            min_count=min_count)
