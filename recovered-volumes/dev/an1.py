import json, sys
CATS = ("exact", "malformed", "refused", "wrong kind", "wrong binding",
        "wrong content", "downstream")
SH = ("lookup", "inverse", "iterate", "compose", "exclusion", "sum_chain",
      "precedence", "priority")
for tag in ("xxl167", "l45", "xl93"):
    try:
        d = json.load(open("results/norm/gap/%s_mode.json" % tag))
    except OSError:
        continue
    for mode, m in d["modes"].items():
        g = m["by_group_position"]["new keys"]
        print("=" * 100)
        print("%s  %s  gate=%s" % (tag, mode, m["gate"]["counts"]))
        print("  group 'new keys', the eight shapes the axis reaches")
        for kp in ("key_first", "value_first"):
            r = g[kp]
            print("    %-12s n=%d  exact %d = %.4f %s" %
                  (kp, r["n"], r["exact"]["k"], r["exact"]["share"],
                   r["exact"]["ci"]))
            for c in CATS[1:]:
                print("        %-14s %4d  %.4f  %s" %
                      (c, r[c]["k"], r[c]["share"], r[c]["ci"]))
            print("        answer_ok %d  wrong_but_right_answer %d  "
                  "refused_that_are_transpositions %d  binding_all_swapped %d"
                  % (r["answer_ok"], r["wrong_but_right_answer"],
                     r["refused_that_are_transpositions"],
                     r["binding_all_swapped"]))
