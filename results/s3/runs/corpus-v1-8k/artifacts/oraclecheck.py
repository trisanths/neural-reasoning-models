"""Oracle rows through the scorers, so a scorer bug shows before the model runs."""
import json, sys, random
sys.path.insert(0, "/home/ec2-user/decoupled-reasoner")

# relation: a rollout that answers the gold, and one that answers every candidate
for band in ("heldout", "train"):
    src = f"/home/ec2-user/retrain/relation/rel_{band}.jsonl"
    out = f"/home/ec2-user/retrain/relation/oracle_{band}.jsonl"
    n = 0
    with open(out, "w") as fh:
        for i, line in enumerate(open(src)):
            ep = json.loads(line)
            for q in ep["questions"][:2]:
                fh.write(json.dumps({
                    "decode": "oracle", "ep": i, "qid": q["qid"],
                    "question": q["text"], "gold": q["answer"],
                    "answer": " " + q["answer"], "shipped_ok": True,
                    "n_rounds": len(ep["documents"]), "n_generated": 8,
                    "chunks": [d["text"] for d in ep["documents"]],
                    "candidates": q.get("candidates") or [],
                    "episode_family": ep["family"],
                    "episode_frame": ep.get("frame"),
                    "answer_source": q.get("answer_source"),
                }) + "\n")
                n += 1
    print(band, "oracle rows", n, "->", out)

# transposed: a rollout that answers the page, and one that answers training
src = "/home/ec2-user/retrain/transposed/ep.jsonl"
for which in ("page", "train"):
    out = f"/home/ec2-user/retrain/transposed/oracle_{which}.jsonl"
    with open(out, "w") as fh:
        for i, line in enumerate(open(src)):
            ep = json.loads(line)
            q = ep["questions"][0]
            fh.write(json.dumps({
                "decode": f"oracle_{which}", "ep": i, "qid": q["qid"],
                "question": q["text"], "gold": q["page_answer"],
                "answer": " " + (q["page_answer"] if which == "page"
                                 else q["train_answer"]),
                "n_rounds": 1, "n_generated": 6,
                "chunks": [ep["documents"][0]["text"]],
                "candidates": q["candidates"],
                "page_answer": q["page_answer"], "train_answer": q["train_answer"],
                "depth": ep["depth"],
            }) + "\n")
    print("transposed oracle", which, "->", out)
