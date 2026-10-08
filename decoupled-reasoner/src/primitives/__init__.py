"""The capability-primitive diagnostic suite.

Seven faculties, each with its own generator, its own scorer and its own
contamination argument, reported separately and never pooled. The point of
the suite is that a single number per model size teaches nothing: what the
descending-size experiment needs is a statement of the form "at this size
abstraction construction breaks while retrieval planning and verification
survive", and only per-faculty isolation can support one.

Every primitive is measured twice. In isolated mode the other six
faculties are supplied by oracle, so a failure localises to the faculty
under test. In integrated mode those oracles are withdrawn and the model
must produce its own upstream inputs. The distance between the two curves
is the architecture and training gap; the point where even the isolated
curve fails is evidence of a capacity gap.

On top of the seven, src.primitives.episode runs one end-to-end
acquisition episode and replaces each faculty in turn with an oracle, so a
failure that would otherwise smear downstream can be located by which
single intervention rescues it.
"""

MODES = ("isolated", "integrated")

PRIMITIVES = (
    "intent",
    "gap",
    "acquisition",
    "abstraction",
    "composition",
    "memory",
    "verification",
)
