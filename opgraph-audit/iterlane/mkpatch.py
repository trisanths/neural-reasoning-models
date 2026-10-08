"""Copy scripts/planheads_train.py to iterlane/train_iter.py adding periodic checkpoints.

The training computation is untouched: the same seeds, the same schedule, the same
batches. The copy only writes intermediate checkpoints so a per-head convergence
check is possible without paying for a second training run.
"""
import re, sys

src = open("scripts/planheads_train.py").read()

# 1. new argument
src = src.replace(
    '    ap.add_argument("--seed", type=int, default=17)',
    '    ap.add_argument("--seed", type=int, default=17)\n'
    '    ap.add_argument("--ckpt-every", type=int, default=0)')

# 2. a save helper, inserted before main()
helper = '''
def save_blob(path, model, state, args, holdout, kind_counts, dropped, head, step, log):
    blob = {"model": model.state_dict(), "config": state["config"],
            "head": args.head, "step": step, "args": vars(args),
            "holdout": holdout, "corruption_mixture": mixture_for(args.head),
            "corruption_counts": kind_counts, "dropped": dropped}
    if head is not None:
        blob["plan_head"] = head.state_dict()
    torch.save(blob, path)
    with open(path + ".log.json", "w") as fh:
        json.dump({"head": args.head, "step": step, "args": vars(args),
                   "holdout": holdout, "corruption_mixture": mixture_for(args.head),
                   "corruption_counts": kind_counts, "dropped": dropped,
                   "log": log}, fh, indent=1)


def main() -> int:'''
assert "\ndef main() -> int:" in src
src = src.replace("\ndef main() -> int:", helper, 1)

# 3. periodic save inside the loop
anchor = '''        if step % args.log_every == 0 or step == 1:'''
assert anchor in src
src = src.replace(anchor, '''        if args.ckpt_every and step % args.ckpt_every == 0 and step != args.steps:
            p = args.out[:-3] + f"_s{step}.pt" if args.out.endswith(".pt") else args.out + f"_s{step}"
            save_blob(p, model, state, args, holdout, kind_counts, dropped, head, step, log)
            print(f"[ckpt] step={step} -> {p}", flush=True)
''' + anchor, 1)

open("iterlane/train_iter.py", "w").write(src)
print("wrote iterlane/train_iter.py", len(src))
