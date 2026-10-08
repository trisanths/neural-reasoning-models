import json
CATS = ("malformed", "refused", "wrong kind", "wrong binding", "wrong content")
SH = ("lookup", "inverse", "priority", "exclusion", "iterate", "precedence",
      "compose", "sum_chain")
for tag, mode in (("xxl167", "greedy"),):
    d = json.load(open("results/norm/gap/class_%s_mode_%s.json" % (tag, mode)))
    sz = d["gold_structure_size"]
    for kp in ("key_first", "value_first"):
        print("### %s %s %s" % (tag, mode, kp))
        print("| shape | n | defs | steps | entries | exact | malformed | refused | wrong kind | wrong binding | wrong content |")
        for sh in SH:
            c = d["by_shape_position"][sh][kp]
            o = c["outcomes"]
            print("| `%s` | %d | %.1f | %.1f | %.1f | %.4f | %.4f | %.4f | %.4f | %.4f | %.4f |"
                  % (sh, c["n"], sz[sh]["mean_defs"], sz[sh]["mean_steps"],
                     sz[sh]["mean_entries"], o["exact"]["share"],
                     o["malformed"]["share"], o["refused"]["share"],
                     o["wrong kind"]["share"], o["wrong binding"]["share"],
                     o["wrong content"]["share"]))
        g = d["group_by_position"][kp]
        o = g["outcomes"]
        print("| all eight | %d | | | | %.4f | %.4f | %.4f | %.4f | %.4f | %.4f |"
              % (g["n"], o["exact"]["share"], o["malformed"]["share"],
                 o["refused"]["share"], o["wrong kind"]["share"],
                 o["wrong binding"]["share"], o["wrong content"]["share"]))
        print()
        print("| shape | failures | of the gap | transposed | answer matches | mean entries wrong | <=2 entries wrong |")
        for sh in SH:
            c = d["by_shape_position"][sh][kp]
            nf = c["n_failures"]
            e = c["entry_error"]
            print("| `%s` | %d/%d | %.4f | %d = %.4f | %d = %.4f | %.4f | %d = %.4f |"
                  % (sh, nf, c["n"], nf / g["n_failures"],
                     c["failures_tables_transposed"]["k"],
                     c["failures_tables_transposed"]["share"],
                     c["failures_answer_matches_gold"]["k"],
                     c["failures_answer_matches_gold"]["share"],
                     e["mean_share_of_entries_wrong"],
                     e["at_most_two_entries_wrong"]["k"],
                     e["at_most_two_entries_wrong"]["share"]))
        e = g["entry_error"]
        print("| all eight | %d/%d | 1.0000 | %d = %.4f | %d = %.4f | %.4f | %d = %.4f |"
              % (g["n_failures"], g["n"],
                 g["failures_tables_transposed"]["k"],
                 g["failures_tables_transposed"]["share"],
                 g["failures_answer_matches_gold"]["k"],
                 g["failures_answer_matches_gold"]["share"],
                 e["mean_share_of_entries_wrong"],
                 e["at_most_two_entries_wrong"]["k"],
                 e["at_most_two_entries_wrong"]["share"]))
        print()
