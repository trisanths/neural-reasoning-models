"""Where the perception threshold is, and what crossing it costs.

The normalizer of `src/norm/` reads surface text into the typed structure the
interpreter executes. It stops generalising somewhere: at 45M parameters a
held-out lexicon runs 0.5150 to 0.8125 by shape and a held-out sentence shape
does not move at all, while the 350M checkpoint of `src/corpus/RETRAIN.md`
reads held-out frames at 0.990 to 1.000. This package walks the ladder between
those two points and reports where, if anywhere, the line is crossed.
"""
