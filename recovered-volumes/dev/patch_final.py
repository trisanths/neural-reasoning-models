import sys

def sub(path, old, new):
    t = open(path).read()
    if old not in t:
        sys.exit("NOT FOUND in %s:\n%r" % (path, old[:160]))
    if t.count(old) != 1:
        sys.exit("AMBIGUOUS in %s (%d)" % (path, t.count(old)))
    open(path, "w").write(t.replace(old, new, 1))
    print("patched", path)

sub("src/e3/E3.md",
    """The first two rows were recounted item by item off the `pred` and `gold` fields
of their record files and every cell reproduces. The n=1000 row is on the wiped
instance store and is kept marked rather than deleted.""",
    """The first two rows were recounted item by item off the `pred` and `gold` fields
of their record files and every cell reproduces. The recount is
`src/e3/letters.py`, its output is `results/e3/letters.json`, and it raises
rather than printing if a recounted accuracy disagrees with the one in the file.
The n=1000 row is on the wiped instance store and is kept marked rather than
deleted.""")

sub("src/STATE.md",
    """So the honest statement is narrower than correction 4's: the positional
commitment disappears between 93M and 167M, and the competence it was hiding
does not appear with it.""",
    """So the honest statement is narrower than correction 4's: the positional
commitment disappears between 93M and 167M, and the competence it was hiding
does not appear with it.

`src/norm/GAP.md` decomposes what the 167M rung writes instead on the same eight
shapes, from re-emitted structures gated on reproducing these record files item
by item, 7,000 of 7,000. Of 1,222 key-first failures 0.4804 are the right kind
of structure with the page's own words bound into the wrong slots, against
0.0090 malformed and 0.1047 the wrong kind, and of that last figure 123 of 128
are a transposed table with a compensating `invert` for `lookup` that returns
gold's answer. The whole-table transposition appears on 0 of 514 key-first
failures at 45M and 3 of 607 at 93M against 324 of 1,222 at 167M, while the
value-first rate holds near 0.39 at all three rungs. That is the mechanism
under this claim: the larger rung did not learn which word is the key, it
stopped applying one convention everywhere.""")

print("done")
