import sys

def sub(path, old, new):
    t = open(path).read()
    if old not in t:
        sys.exit("NOT FOUND in %s:\n%r" % (path, old[:160]))
    if t.count(old) != 1:
        sys.exit("AMBIGUOUS in %s (%d)" % (path, t.count(old)))
    open(path, "w").write(t.replace(old, new, 1))
    print("patched", path)

P = "src/STATE.md"

sub(P, """   copied into `LIQUID.md` on every run. The n=400 record shows 0.2550 emission,
   73 live searches and 255 cache hits. Effect: a retracted claim that
   re-propagates on every regeneration rather than decaying.""",
      """   copied into `LIQUID.md` on every run. The n=400 record shows 0.2550 emission,
   73 live searches and 255 cache hits. Effect: a retracted claim that
   re-propagates on every regeneration rather than decaying.
   Fixed in `435db6f`. The verdict now reports the emission rate, the searches
   and the cache hits, and `src/extern/md.py:check_verdict` binds every numeral
   in the hand-written prose to a record file and a field. It raises when a
   stated value is not what the file holds, when a numeral appears in the prose
   that no line accounts for, when a claimed value has dropped out of the prose,
   and when a cited record file is newer than the verdict quoting it. Two
   further claims in the same file did not survive the recount that came with
   the fix: the family split read below chance on three families and above on
   one where the artifact has two above and two below, and the general cell's
   0.0000 at n=26 now carries its states, 7 ran, 17 malformed, 2 refused.""")

sub(P, """    dropping four words from that sentence reverses whether an untrained relation
    type reads at chance.

Fault 1 has now appeared four times""",
      """    dropping four words from that sentence reverses whether an untrained relation
    type reads at chance.

41. A record selected by sorting file names, where the names carry a number.
    `src/extern/fourcell.py` took its cell 2 record as
    `sorted(glob("cell2_ours_mmlu_retrieval_n*.json"))[-1]`. The sort is
    lexicographic, so `n1000` sorts before `n400` and the larger run is the one
    that would have been dropped, silently, with the table saying only "cell 2"
    and not which run it meant. Checked against three names in a scratch
    directory: the old expression selects n400 where the corrected one selects
    n1000. Effect: no published number is wrong, because only the n=400 file
    exists today. The hazard was live for the next larger run, which is the one
    a reader would most want. Fixed in `3c89cc0`: the n is parsed out of the
    name, the largest wins, the runs not chosen are named under the table, and
    a matching file whose name carries no n raises.

Fault 1 has now appeared four times""")

sub(P, """the falsification lane, which is also the lane that found 11 and 12.""",
      """the falsification lane, which is also the lane that found 11 and 12; 41 was
found while fixing 3, 4 and 5, in the same file as 4.""")

sub(P, """So the best-supported figure is 0.2640 at n=500, and 0.2750 at n=200 is the one
the repository can produce on its own. 0.2450 should be recorded as
unverifiable rather than quoted, and I had been propagating it as the headline.""",
      """So the best-supported figure is 0.2640 at n=500, and 0.2750 at n=200 is the one
the repository can produce on its own. 0.2450 should be recorded as
unverifiable rather than quoted, and I had been propagating it as the headline.

It is now marked in `src/e3/E3.md` at all four places it appears, with the
reason, and kept rather than deleted. Two things were recovered while marking
it. The n=200 and n=500 accuracies and their prediction distributions were
recounted item by item off the `pred` and `gold` fields of the two surviving
record files and reproduce every cell, 146/7/35/12 at n=200 and 353/23/91/33 at
n=500. And the eot-prefix control, whose n=500 arm went with the instance
store, exists at n=200 in the checkout as
`results/extern/bench/ours_mmlu_eotprefix_n200.json`: 0.2700 with 144/8/37/11
against the no-prefix 0.2750 with 146/7/35/12, so the prefix moves accuracy by
0.005 and the modal share by 0.010 and the control can be re-run after all. One
claim was withdrawn rather than marked: that the point estimate walks toward
the floor as n grows was read off three points, can now be checked at two, and
two points are not a trend.""")

sub(P, """holding 0.9644 should replace it with 1.0000 on 850 items over 170 operations,
and read the caveats before quoting either.""",
      """holding 0.9644 should replace it with 1.0000 on 850 items over 170 operations,
and read the caveats before quoting either.

`src/norm/ONESHOT.md` now carries both denominators where it states the
headline, together with the fact that 0.9644 is in no record file, no document
and no commit here. The two denominators were recounted from
`results/norm/oneshot/sys.jsonl.gz`: the one-page acquisition cell holds 850
items over 170 distinct operations at exactly five items each, one frame id per
operation, and the library is exact on 850 of 850.""")

print("done")
