"""The accuracy against parameters curve, per shape, never pooled."""
import json, os, sys, glob
sizes = sys.argv[1:] or ["xs","s","m","l"]
d = {}
for s in sizes:
    p = f"results/norm/eval/{s}/summary.json"
    if os.path.exists(p):
        d[s] = json.load(open(p))
if not d:
    print("no summaries"); raise SystemExit
shapes = sorted(next(iter(d.values()))["splits"]["train_frames_eval"]["modes"]["greedy"]["by_shape"])
for sp in ("train_frames_eval","qframe","lexicon","mode","mixed"):
    print("="*8, sp)
    hdr = "  %-18s" % "shape" + "".join("  %10s" % (f"{s}({d[s]['params']['total']/1e6:.2f}M)") for s in d)
    print(hdr)
    for sh in shapes:
        row = "  %-18s" % sh
        for s in d:
            r = d[s]["splits"][sp]["modes"]["greedy"]["by_shape"][sh]
            row += "  %10.3f" % r["exact"]
        print(row)
    # safe vs dangerous
    for s in d:
        g = d[s]["splits"][sp]["modes"]["greedy"]["pooled_do_not_headline"]
        sm = d[s]["splits"][sp]["modes"]["sampled"]["pooled_do_not_headline"]
        print("   %-3s pooled(do not headline) n=%d greedy exact=%.4f malformed=%.4f refused=%.4f wrong=%.4f | sampled exact=%.4f malformed=%.4f refused=%.4f wrong=%.4f"
              % (s, g["n"], g["exact"], g["malformed"], g["refused"], g["wrong"],
                 sm["exact"], sm["malformed"], sm["refused"], sm["wrong"]))
