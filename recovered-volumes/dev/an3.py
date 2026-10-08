import json, sys
CATS = ("exact", "malformed", "refused", "wrong kind", "wrong binding",
        "wrong content")
SH = ("lookup", "inverse", "iterate", "compose", "exclusion", "sum_chain",
      "precedence", "priority")
for tag, mode in (("xxl167", "greedy"), ("l45", "greedy")):
    d = json.load(open("results/norm/gap/class_%s_mode_%s.json" % (tag, mode)))
    print("#" * 110)
    print(tag, mode, d["record_file"], d["record_mtime"])
    for kp in ("key_first", "value_first"):
        print("  --- %s ---" % kp)
        print("  %-11s %5s %8s %8s %8s %8s %8s %8s  %s"
              % ("shape", "n", "exact", "malf", "refused", "kind", "binding",
                 "content", "binding sub (transposed/other)"))
        for sh in SH:
            c = d["by_shape_position"][sh][kp]
            b = c["binding_sub"]
            print("  %-11s %5d %8.4f %8.4f %8.4f %8.4f %8.4f %8.4f  %d/%d"
                  % (sh, c["n"], c["exact"]["share"], c["malformed"]["share"],
                     c["refused"]["share"], c["wrong kind"]["share"],
                     c["wrong binding"]["share"], c["wrong content"]["share"],
                     b.get("tables transposed", 0),
                     b.get("other re-association", 0)))
        g = d["group"][kp]
        print("  %-11s %5d %8.4f %8.4f %8.4f %8.4f %8.4f %8.4f"
              % ("GROUP", g["n"], g["exact"]["share"], g["malformed"]["share"],
                 g["refused"]["share"], g["wrong kind"]["share"],
                 g["wrong binding"]["share"], g["wrong content"]["share"]))
