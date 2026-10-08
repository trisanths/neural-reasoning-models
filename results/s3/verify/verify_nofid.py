"""How much is the frame id worth to the library reader?

opread.answer(text, fid) is handed the frame id. The network is handed the text
alone. This asks what the reader does when it has to find the frame itself.
"""
import gzip, json, random, sys, time
from src.norm import opread
from src.norm.render import frames

fr, _ = frames()
fids = [f.fid for f in fr]
print("frames in bank:", len(fids), flush=True)

items = []
for ln in gzip.open("results/norm/oneshot/items.jsonl.gz", "rt"):
    d = json.loads(ln)
    if d["cond"] == "acq" and d["n_pages"] == 1:
        items.append(d)
random.Random(11).shuffle(items)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 60
items = items[:N]

t0 = time.time()
uniq = 0; amb = 0; none = 0; right_first = 0; right_any = 0; wrong_pick = 0
for d in items:
    hits = []
    for fid in fids:
        got = opread.answer(d["text"], fid)
        if got["state"] == "ran":
            hits.append((fid, got["answer"]))
    if not hits:
        none += 1
        continue
    ans = {a for _, a in hits}
    if len(hits) == 1:
        uniq += 1
    else:
        amb += 1
    # the reader with no frame id has to pick; take the first frame that reads
    if hits[0][1] == d["gold"]:
        right_first += 1
    else:
        wrong_pick += 1
    if d["gold"] in ans:
        right_any += 1
n = len(items)
out = {"n": n, "frames": len(fids), "exactly_one_frame_reads": uniq,
       "several_frames_read": amb, "no_frame_reads": none,
       "strict_taking_first_reading_frame": right_first / n,
       "gold_among_readings": right_any / n, "seconds": round(time.time() - t0, 1)}
print(json.dumps(out, indent=2))
json.dump(out, open("/tmp/verify_nofid.json", "w"), indent=2)
