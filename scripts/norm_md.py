"""Markdown tables for src/norm/TRAIN.md, straight from the summaries."""
import json, os, sys

tags = sys.argv[1:]
d = {}
for t in tags:
    p = f"results/norm/eval/{t}/summary.json"
    if os.path.exists(p):
        d[t] = json.load(open(p))
if not d:
    print("no summaries"); raise SystemExit

any_ = next(iter(d.values()))
shapes = sorted(any_["splits"]["train_frames_eval"]["modes"]["greedy"]["by_shape"])
hdr_names = {t: f"{t} ({d[t]['params']['total']/1e6:.2f}M)" for t in d}

for sp in ("train_frames_eval", "qframe", "lexicon", "mode", "mixed"):
    if sp not in any_["splits"]:
        continue
    print(f"\n#### {sp}\n")
    cols = list(d)
    print("| shape | " + " | ".join(hdr_names[t] for t in cols)
          + " | modal_shape | parser |")
    print("|---" * (len(cols) + 3) + "|")
    rows = []
    for sh in shapes:
        vals = [d[t]["splits"][sp]["modes"]["greedy"]["by_shape"][sh]["exact"]
                for t in cols]
        r0 = d[cols[-1]]["splits"][sp]["modes"]["greedy"]["by_shape"][sh]
        rows.append((-vals[-1], sh, vals, r0["modal_shape_exact"],
                     r0["parser_exact"]))
    for _, sh, vals, ms, pe in sorted(rows):
        print(f"| `{sh}` | " + " | ".join(f"{v:.3f}" for v in vals)
              + f" | {ms:.3f} | {pe:.3f} |")
    print("\n| size | n | exact | malformed | refused | wrong | sampled exact |")
    print("|---|---|---|---|---|---|---|")
    for t in cols:
        g = d[t]["splits"][sp]["modes"]["greedy"]["pooled_do_not_headline"]
        sm = d[t]["splits"][sp]["modes"]["sampled"]["pooled_do_not_headline"]
        print(f"| {t} | {g['n']} | {g['exact']:.4f} | {g['malformed']:.4f} "
              f"| {g['refused']:.4f} | {g['wrong']:.4f} | {sm['exact']:.4f} |")

print("\n#### answer_ok, the lenient companion, greedy, train frames\n")
print("| shape | " + " | ".join(hdr_names[t] for t in d) + " | answer floor |")
print("|---" * (len(d) + 2) + "|")
for sh in shapes:
    vals = [d[t]["splits"]["train_frames_eval"]["modes"]["greedy"]["by_shape"][sh]["answer_ok"] for t in d]
    fl = next(iter(d.values()))["splits"]["train_frames_eval"]["modes"]["greedy"]["by_shape"][sh]["answer_chance_floor"]
    print(f"| `{sh}` | " + " | ".join("n/a" if v is None else f"{v:.3f}" for v in vals)
          + (" | open |" if fl is None else f" | {fl:.3f} |"))
