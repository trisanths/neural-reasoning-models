"""Does the library reader survive wording it was not handed by opsay?

Every perturbation below is meaning preserving to a person and leaves the
directories, the question and the operation untouched. Only the definition
page changes.
"""
import gzip, json, re, sys
from src.norm import opread

def defs_lines(text):
    """Return (blocks, index of the definition body block, its lines)."""
    blocks = text.split("\n\n")
    for i, b in enumerate(blocks):
        ls = b.split("\n")
        if any(re.match(r"^(This .+ states one operation, written [a-z][a-z0-9]*\.|"
                        r"Operation: [a-z][a-z0-9]*\.|"
                        r"Use the operation [a-z][a-z0-9]* as set out here\.)$", l)
               for l in ls):
            return blocks, i, ls
    return blocks, -1, []

def rebuild(blocks, i, lines):
    blocks = list(blocks); blocks[i] = "\n".join(lines); return "\n\n".join(blocks)

# ---- perturbations on the definition body lines -------------------------

def p_identity(ls): return list(ls)

def p_then(ls):
    out = []
    for l in ls:
        l2 = re.sub(r"^(If [^,]+,) ", r"\1 then ", l)
        l2 = re.sub(r"^(When [^,]+,) ", r"\1 then ", l2)
        l2 = re.sub(r"^(Rule \d+\. When [^,]+,) ", r"\1 then ", l2)
        out.append(l2)
    return out

def p_both(ls):
    return [l.replace("the two readings are the same", "both readings are the same")
             .replace("all three readings are the same", "all three of the readings are the same")
            for l in ls]

def p_value(ls):
    return [re.sub(r"\bthe reading at the\b", "the value at the", l) for l in ls]

def p_otherwise(ls):
    out = []
    for l in ls:
        l = re.sub(r"^In every other case ", "Otherwise ", l)
        l = re.sub(r"^Otherwise the ", "In every other case the ", l) if l.startswith("Otherwise the ") else l
        l = re.sub(r"^Rule (\d+)\. In any other case, ", r"Rule \1. Otherwise, ", l)
        out.append(l)
    return out

def p_extra(ls):
    return list(ls) + ["That is the whole of it."]

def p_prefix(ls):
    return ["Please note. " + ls[0]] + list(ls[1:])

def p_flip(ls):
    """If X, the op of that item is R.  ->  The op of that item is R if X."""
    out = []
    for l in ls:
        m = re.match(r"^If (.+?), (the .+?) is (.+)\.$", l)
        if m:
            out.append(f"{m.group(2)[0].upper()}{m.group(2)[1:]} is {m.group(3)} if {m.group(1)}.")
            continue
        m = re.match(r"^When (.+?), give (.+?) as (the .+)\.$", l)
        if m:
            out.append(f"Give {m.group(2)} as {m.group(3)} when {m.group(1)}.")
            continue
        out.append(l)
    return out

PERTS = [("identity", p_identity), ("insert then", p_then),
         ("both readings", p_both), ("value for reading", p_value),
         ("otherwise wording", p_otherwise), ("one extra sentence", p_extra),
         ("polite prefix", p_prefix), ("clause order flipped", p_flip)]

items = []
for ln in gzip.open("results/norm/oneshot/items.jsonl.gz", "rt"):
    d = json.loads(ln)
    if d["cond"] == "acq" and d["n_pages"] == 1:
        items.append(d)
print("acq one page items:", len(items))

rows = []
for name, fn in PERTS:
    n = changed = read_ok = right = 0
    for d in items:
        blocks, i, ls = defs_lines(d["text"])
        if i < 0:
            continue
        new = fn(ls)
        txt = rebuild(blocks, i, new)
        n += 1
        if txt != d["text"]:
            changed += 1
        got = opread.answer(txt, d["fid"])
        if got["state"] != "misread":
            read_ok += 1
        if got["state"] == "ran" and got["answer"] == d["gold"]:
            right += 1
    rows.append((name, n, changed, read_ok / n, right / n))
    print(f"{name:24s} n={n:4d} changed={changed:4d} read={read_ok/n:.4f} strict={right/n:.4f}", flush=True)

with open("/tmp/verify_paraphrase.json", "w") as fh:
    json.dump([{"perturbation": r[0], "n": r[1], "n_changed": r[2],
                "read_rate": r[3], "strict": r[4]} for r in rows], fh, indent=2)
