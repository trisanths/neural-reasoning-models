
import json, os, time, glob
# Rename any oo_tok result to carry its batch size, so the 256x40k and 512x20k jobs
# that share a --tag cannot overwrite each other. Polls until both of each pair exist.
R = "/home/ec2-user/ca/results_v2"
while True:
    for f in glob.glob(f"{R}/*_oo_tok_s*.json"):
        if "_b256_" in f or "_b512_" in f:
            continue
        try:
            b = json.load(open(f)).get("batch")
        except Exception:
            continue
        if b in (256, 512):
            new = f.replace("_oo_tok_s", f"_oo_tok_b{b}_s")
            os.replace(f, new)
            print("renamed", os.path.basename(f), "->", os.path.basename(new), flush=True)
    n = len(glob.glob(f"{R}/*_oo_tok_b*_s*.json"))
    if n >= 99:
        print("all 4 oo_tok results on this box renamed", flush=True); break
    time.sleep(60)
