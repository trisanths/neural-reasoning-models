# Metric calibration against scripted stand-ins

Each row is a stand-in with exactly one faculty and chance
behaviour in the other six, well formed throughout. A metric
that works is high on its own diagonal cell and flat across the
rest of its column.

| stand-in | intent | gap | acquisition | abstraction | composition | memory | verification |
|---|---|---|---|---|---|---|---|
| blind | +0.11 | +0.13 | +0.00 | -0.04 | 0,0,0 | +0.01 | +0.13 |
| intent | +1.00 | +0.07 | +0.00 | -0.14 | 0,0,0 | +0.03 | +0.05 |
| gap | +0.11 | +1.00 | +0.00 | -0.09 | 0,0,0 | -0.06 | +0.02 |
| acquisition | +0.11 | +0.13 | +1.00 | -0.13 | 0,0,0 | -0.03 | -0.08 |
| abstraction | +0.11 | +0.13 | +0.00 | +0.36 | 0,0,0 | +0.08 | -0.08 |
| composition | +0.11 | +0.13 | +0.00 | -0.04 | 3,3,3 | +0.02 | +0.00 |
| memory | +0.11 | +0.13 | +0.00 | -0.04 | 0,0,0 | +1.00 | -0.02 |
| verification | +0.11 | +0.13 | +0.00 | -0.04 | 0,0,0 | +0.01 | +1.00 |

Composition cells are the three depth thresholds in the order novel, relational, sequential as reported by the runner.
