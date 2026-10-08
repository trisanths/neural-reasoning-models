"""Job 1d edits: the one-shot denominators, and the unverifiable MMLU row."""
import sys

S3 = "s3://decoupled-reasoner-009398924577"


def sub(path, old, new):
    t = open(path).read()
    if old not in t:
        sys.exit("NOT FOUND in %s:\n%s" % (path, old[:200]))
    if t.count(old) != 1:
        sys.exit("AMBIGUOUS in %s (%d matches)" % (path, t.count(old)))
    open(path, "w").write(t.replace(old, new, 1))
    print("patched", path)


# ------------------------------------------------------ the one-shot headline

sub("src/norm/ONESHOT.tmpl.md",
    """exact at 1.0000 as well, unchanged when the same operation is stated on two
pages and on four. The network, handed the same page in its context and taking""",
    """exact at 1.0000 as well, unchanged when the same operation is stated on two
pages and on four. That 1.0000 is forced choice over 850 items, and the 850
items are 170 distinct operations at five questions each with one frame id per
operation, counted off `results/norm/oneshot/sys.jsonl.gz`. For the question
this lane asks, whether an operation was acquired, the independent unit is the
operation, so the denominator that travels with the headline is 170 as well as
850. A figure of 0.9644 has been quoted for this lane and belongs to nothing:
it is in no record file, no document and no commit in this repository, and what
the records hold is 1.0000 forced choice on 850 items over 170 operations. The
network, handed the same page in its context and taking""")

# --------------------------------------------------- the MMLU n=1000 row, e3

sub("src/e3/E3.md",
    """Status: training is in flight. Numbers below that are marked in flight will be
replaced by measurements, not by estimates. Everything already measured is
final and names its record file.""",
    """Status: training is in flight. Numbers below that are marked in flight will be
replaced by measurements, not by estimates. Everything already measured names
its record file, and the figures whose record file is gone are marked
unverifiable where they appear rather than deleted. Every number this lane read
out of `/mnt/nvme/e3eval/` was on worker 2's instance store; the instance is
terminated and nothing under that path was mirrored to S3, so the MMLU n=1000
row and the n=500 eot-prefix control cannot be recomputed. The MMLU figures the
repository can still produce for this checkpoint are 0.2750 at n=200 and 0.2640
at n=500.""")

sub("src/e3/E3.md",
    """| n | acc | 95% Wilson | contains 0.25 | p vs floor |
| ---: | ---: | --- | --- | ---: |
| 200 | 0.2750 | [0.2178, 0.3407] | yes | 0.229 |
| 500 | 0.2640 | [0.2273, 0.3043] | yes | 0.250 |
| 1000 | 0.2450 | [0.2194, 0.2726] | yes | 0.654 |

The 0.2750 was an n=200 fluctuation. At n=1000 the old checkpoint reads
0.2450, which is below the chance floor and about as flat as a number can be.
Nothing about the comparison changes, but the honest statement of the baseline
is stronger than the brief's: it is not merely that the interval contains
chance, it is that the point estimate walks toward the floor as n grows.

Record files, all newer than this report:
`/mnt/nvme/e3eval/mmlu_ref_n{200,500,1000}.json`.""",
    """| n | acc | 95% Wilson | contains 0.25 | p vs floor | artifact |
| ---: | ---: | --- | --- | ---: | --- |
| 200 | 0.2750 | [0.2178, 0.3407] | yes | 0.229 | `results/extern/bench/ours_corpus-v1-8k_mmlu.json`, in the checkout |
| 500 | 0.2640 | [0.2273, 0.3043] | yes | 0.250 | `""" + S3 + """/runs/real-v1-8k/results/mmlu_closed_corpus-v1-8k_n500.json` |
| 1000 | 0.2450 | [0.2194, 0.2726] | yes | 0.654 | `/mnt/nvme/e3eval/mmlu_ref_n1000.json`, unverifiable |

The n=1000 row is unverifiable and is kept marked rather than deleted.
`/mnt/nvme` was instance store on worker 2, the instance is terminated, and a
recursive listing of `""" + S3 + """` returns no object matching `mmlu_ref` or
`e3eval`, so the file was never mirrored and the row cannot be recomputed. It
must not be quoted without that sentence attached.

The n=200 and n=500 rows were re-read from the two artifacts named beside them
and both reproduce to the digit, so 0.2750 at n=200 and 0.2640 at n=500 are
what this repository supports, and the n=500 figure is the best supported of
the three.

The reading survives without the missing row, in a weaker form. Both verifiable
points have intervals containing the 0.2500 floor, which is what the brief
asked. The stronger claim the third point carried, that the estimate walks
toward the floor as n grows, was read off three points and can now be checked
at two; two points are not a trend and the claim is withdrawn. What replaces it
is the prediction distribution below, which reproduces from surviving artifacts
at both n and says something sharper than the accuracy does.""")

sub("src/e3/E3.md",
    """| n | predictions A / B / C / D | modal share | gold A share | always-A would score | model scored |
| ---: | --- | ---: | ---: | ---: | ---: |
| 200 | 146 / 7 / 35 / 12 | 0.730 | 0.300 | 0.3000 | 0.2750 |
| 500 | 353 / 23 / 91 / 33 | 0.706 | 0.254 | 0.2540 | 0.2640 |
| 1000 | 695 / 48 / 188 / 69 | 0.695 | 0.220 | 0.2200 | 0.2450 |

A model choosing uniformly would sit near 0.25 on each letter. This one puts
0.695 to 0.730 of its mass on the first option, and its accuracy tracks how
often A happens to be the gold answer in the drawn sample: 0.300 gold-A at
n=200 against 0.2750 scored, 0.220 gold-A at n=1000 against 0.2450 scored. The
whole apparent spread from 0.2750 down to 0.2450 across sample sizes is that
one number moving.""",
    """| n | predictions A / B / C / D | modal share | gold A share | always-A would score | model scored | artifact |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 200 | 146 / 7 / 35 / 12 | 0.730 | 0.300 | 0.3000 | 0.2750 | `results/extern/bench/ours_corpus-v1-8k_mmlu.json`, recounted |
| 500 | 353 / 23 / 91 / 33 | 0.706 | 0.254 | 0.2540 | 0.2640 | `""" + S3 + """/runs/real-v1-8k/results/mmlu_closed_corpus-v1-8k_n500.json`, recounted |
| 1000 | 695 / 48 / 188 / 69 | 0.695 | 0.220 | 0.2200 | 0.2450 | `/mnt/nvme/e3eval/mmlu_ref_n1000.json`, unverifiable |

The first two rows were recounted item by item off the `pred` and `gold` fields
of their record files and every cell reproduces. The n=1000 row is on the wiped
instance store and is kept marked rather than deleted.

A model choosing uniformly would sit near 0.25 on each letter. On the two rows
that can be checked this one puts 0.706 and 0.730 of its mass on the first
option, and its accuracy tracks how often A happens to be the gold answer in
the drawn sample: it scores 0.2750 where always answering A would score 0.3000,
and 0.2640 where always A would score 0.2540. On both samples it lands within
0.025 of the always-A baseline, on either side of it, against a 0.2500 floor.""")

sub("src/e3/E3.md",
    """| configuration | n | acc | predictions A / B / C / D | modal share |
| --- | ---: | ---: | --- | ---: |
| completion, no prefix | 500 | 0.2640 | 353 / 23 / 91 / 33 | 0.706 |
| completion, eot prefix | 500 | 0.2620 | 346 / 26 / 98 / 30 | 0.692 |

The prefix moves accuracy by 0.002 and the modal share by 0.014. The pile is a
property of the checkpoint, not of where the harness starts the document.""",
    """| configuration | n | acc | predictions A / B / C / D | modal share | artifact |
| --- | ---: | ---: | --- | ---: | --- |
| completion, no prefix | 500 | 0.2640 | 353 / 23 / 91 / 33 | 0.706 | `""" + S3 + """/runs/real-v1-8k/results/mmlu_closed_corpus-v1-8k_n500.json`, recounted |
| completion, eot prefix | 500 | 0.2620 | 346 / 26 / 98 / 30 | 0.692 | `/mnt/nvme/e3eval/mmlu_ref-eot_n500.json`, unverifiable |
| completion, no prefix | 200 | 0.2750 | 146 / 7 / 35 / 12 | 0.730 | `results/extern/bench/ours_corpus-v1-8k_mmlu.json`, recounted |
| completion, eot prefix | 200 | 0.2700 | 144 / 8 / 37 / 11 | 0.720 | `results/extern/bench/ours_mmlu_eotprefix_n200.json`, recounted |

The n=500 eot-prefix arm is on the same wiped instance store as the n=1000 row
above and cannot be checked, so the pair it forms with the row above it is not
a control this repository can produce. The same control at n=200 is in the
checkout and both its arms were recounted for this table: the prefix moves
accuracy by 0.005 and the modal share by 0.010, in the same direction and at
the same size as the n=500 pair reported. The pile is a property of the
checkpoint rather than of where the harness starts the document, and that now
rests on a pair that can be re-run.""")

sub("src/e3/E3.md",
    """Record files: `mmlu_ref_n{200,500,1000}.json`, `mmlu_ref-eot_n500.json`.""",
    """Record files, with their state. `mmlu_ref_n{200,500,1000}.json` and
`mmlu_ref-eot_n500.json` were written under `/mnt/nvme/e3eval/` on worker 2 and
are gone with the instance; none was mirrored to S3. What can be re-read is
`results/extern/bench/ours_corpus-v1-8k_mmlu.json` and
`results/extern/bench/ours_mmlu_eotprefix_n200.json` in the checkout, and
`""" + S3 + """/runs/real-v1-8k/results/mmlu_closed_corpus-v1-8k_n500.json`.""")

sub("src/e3/E3.md",
    """| corpus-v1-8k | 5.24* | 0.2450 | [0.2194, 0.2726] | 695 / 48 / 188 / 69 | 0.695 | 0.255 |""",
    """| corpus-v1-8k | 5.24* | 0.2450 (unverifiable) | [0.2194, 0.2726] | 695 / 48 / 188 / 69 | 0.695 | 0.255 |""")

sub("src/e3/E3.md",
    """The e3 rows
are exact, being step count times 262,144 over 375,440,384.""",
    """The e3 rows
are exact, being step count times 262,144 over 375,440,384.

The corpus-v1-8k row is the comparison's anchor and its record file is gone:
`/mnt/nvme/e3eval/mmlu_ref_n1000.json` was on worker 2's instance store and was
never mirrored. The row is kept because the e3 rows beside it were measured
against it, and it is marked because only the e3 side of that comparison can be
re-run. At the sample sizes this repository can still produce, the same
checkpoint reads 0.2750 at n=200 and 0.2640 at n=500, both with intervals
containing the floor, so the conclusion the anchor supports does not turn on
the missing file.""")

print("done")
