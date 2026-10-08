"""Real questions and the real passages that answer them, in one schema.

Three sources, downloaded as parquet from the Hub and normalised into one
jsonl per source and split. Nothing here is generated; every question was
written by a person and every document is text somebody else published.

  hotpot_qa   hotpotqa/hotpot_qa, config distractor. Ten titled Wikipedia
              paragraphs per question, two of them supporting. The eight
              distractors are the dataset's own, retrieved by its authors
              against the gold pair, so the bundle is a retrieval corpus
              the dataset supplies rather than one assembled here. Two hops
              by construction, which is why this source carries the weight.

  natural_questions  MRQA 2019's NaturalQuestionsShort. A real Google query
              and the Wikipedia passage a human annotator marked as holding
              the short answer.

  trivia_qa   MRQA 2019's TriviaQA-web. A trivia writer's question and a web
              document a search engine returned for it.

MRQA is used for the two single-hop sources because it ships question,
passage and answer span in one uniform schema at a size this box can hold;
the underlying questions and passages are the original ones. Its contexts
are split into passages here, so the bundle a question is asked against is
that document's own passages, which are on-topic negatives rather than
random ones.

Splits come from the datasets' own train and validation files. A question
never crosses between them, which is the leakage control that matters; the
content-hash check in split.py is the audit on top of it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re

SOURCES = ("hotpot_qa", "natural_questions", "trivia_qa")

MRQA_SUBSET = {
    "natural_questions": "NaturalQuestionsShort",
    "trivia_qa": "TriviaQA-web",
}

MRQA_REPO = "mrqa-workshop/mrqa"
HOTPOT_REPO = "hotpotqa/hotpot_qa"

MRQA_FILES = {
    "train": [f"plain_text/train-0000{i}-of-00009.parquet" for i in range(9)],
    "validation": ["plain_text/validation-00000-of-00001.parquet"],
}
HOTPOT_FILES = {
    "train": ["distractor/train-00000-of-00002.parquet",
              "distractor/train-00001-of-00002.parquet"],
    "validation": ["distractor/validation-00000-of-00001.parquet"],
}

# Passage length. 90 words lands near 120 tokens on this tokenizer, so four
# served passages plus the queries and the answer stay inside the 1024 token
# training window that src/corpus/sft.py packs to.
PASSAGE_WORDS = 90
MAX_PASSAGES = 12

_SENT = re.compile(r"(?<=[.!?])\s+")
_WS = re.compile(r"\s+")
_WORD = re.compile(r"[a-z0-9]+")


def norm(text: str) -> str:
    return " ".join(_WORD.findall(str(text).lower()))


def content_hash(question: str, answer: str) -> str:
    """Identity of a question, independent of which file it came from."""
    return hashlib.blake2b(
        (norm(question) + "\x00" + norm(answer)).encode(), digest_size=12
    ).hexdigest()


def clean(text: str) -> str:
    """Whitespace normalised, with MRQA's inline markup removed."""
    text = str(text or "")
    text = text.replace("[TLE]", " ").replace("[DOC]", " ").replace("[PAR]", " ")
    text = text.replace("<P>", " ").replace("</P>", " ")
    text = text.replace("<Table>", " ").replace("</Table>", " ")
    text = text.replace("<Tr>", " ").replace("</Tr>", " ")
    text = text.replace("<Td>", " ").replace("</Td>", " ")
    text = text.replace("<Th>", " ").replace("</Th>", " ")
    text = text.replace("<Li>", " ").replace("</Li>", " ")
    text = text.replace("<Ul>", " ").replace("</Ul>", " ")
    text = text.replace("<Ol>", " ").replace("</Ol>", " ")
    text = text.replace("<H1>", " ").replace("</H1>", " ")
    text = text.replace("<H2>", " ").replace("</H2>", " ")
    text = text.replace("<H3>", " ").replace("</H3>", " ")
    text = text.replace("<Dt>", " ").replace("</Dt>", " ")
    text = text.replace("<Dd>", " ").replace("</Dd>", " ")
    return _WS.sub(" ", text).strip()


def passages(text: str, words: int = PASSAGE_WORDS) -> list[str]:
    """Greedy sentence packing to a word budget, document order kept."""
    out: list[str] = []
    cur: list[str] = []
    n = 0
    for sent in _SENT.split(text):
        sent = sent.strip()
        if not sent:
            continue
        w = sent.count(" ") + 1
        if n and n + w > words:
            out.append(" ".join(cur))
            cur, n = [], 0
        if w > 2 * words:
            # A sentence longer than two budgets is a table or a run-on;
            # cut it on words so no passage dwarfs the rest.
            parts = sent.split(" ")
            for i in range(0, len(parts), words):
                out.append(" ".join(parts[i:i + words]))
            continue
        cur.append(sent)
        n += w
    if cur:
        out.append(" ".join(cur))
    return [p for p in out if p]


def answer_span(text: str, answer: str):
    """The answer standing as a whole token in a passage, as the passage
    writes it.

    The word-boundary rule is the one src/corpus/sft.py grades a served page
    by, so a passage counted as gold here is one that path would also count.
    Returning the matched surface rather than the dataset's string means the
    training target is spelled the way the document spells it, which is what
    a model copying out of a served page has to produce. MRQA lowercases
    some TriviaQA answers, and training on the lowercase form would teach a
    spelling no document contains.
    """
    if not answer:
        return None
    m = re.search(rf"(?<![A-Za-z0-9]){re.escape(answer)}(?![A-Za-z0-9])",
                  text, re.I)
    return m.group(0) if m else None


def answer_in(text: str, answer: str) -> bool:
    return answer_span(text, answer) is not None


# ------------------------------------------------------------------ hotpot

def hotpot_items(rows) -> list[dict]:
    out = []
    for r in rows:
        ctx = r["context"]
        titles = list(ctx["title"])
        docs = []
        for t, sents in zip(titles, ctx["sentences"]):
            body = clean(" ".join(sents))
            if not body:
                continue
            docs.append({"title": clean(t), "text": f"{clean(t)}. {body}"})
        if len(docs) < 4:
            continue
        title_at = {}
        for i, d in enumerate(docs):
            title_at.setdefault(d["title"], i)
        support = []
        for t in dict.fromkeys(r["supporting_facts"]["title"]):
            i = title_at.get(clean(t))
            if i is not None:
                support.append(i)
        if len(support) != 2:
            continue
        answer = clean(r["answer"])
        if not answer:
            continue
        out.append({
            "source": "hotpot_qa",
            "qid": r["id"],
            "question": clean(r["question"]),
            "answer": answer,
            "answers": [answer],
            "docs": docs,
            "gold": support,
            "hops": 2,
            "kind": r.get("type", ""),
            "level": r.get("level", ""),
            "hash": content_hash(r["question"], answer),
        })
    return out


# -------------------------------------------------------------------- mrqa

def mrqa_items(rows, source: str) -> list[dict]:
    out = []
    for r in rows:
        answers = [clean(a) for a in (r["answers"] or [])]
        answers = [a for a in dict.fromkeys(answers) if a]
        if not answers:
            continue
        ctx = clean(r["context"])
        if len(ctx) < 200:
            continue
        ps = passages(ctx)[:MAX_PASSAGES]
        if len(ps) < 2:
            continue
        gold = None
        gold_answer = None
        for i, p in enumerate(ps):
            for a in answers:
                hit = answer_span(p, a)
                if hit is not None:
                    gold, gold_answer = i, hit
                    break
            if gold is not None:
                break
        if gold is None:
            continue
        question = clean(r["question"])
        if not question:
            continue
        out.append({
            "source": source,
            "qid": r["qid"],
            "question": question,
            "answer": gold_answer,
            "answers": answers,
            "docs": [{"title": "", "text": p} for p in ps],
            "gold": [gold],
            "hops": 1,
            "kind": "",
            "level": "",
            "hash": content_hash(question, gold_answer),
        })
    return out


# ------------------------------------------------------------------- fetch

def _download(repo: str, path: str, raw: str) -> str:
    from huggingface_hub import hf_hub_download
    return hf_hub_download(repo, path, repo_type="dataset", local_dir=raw)


def cmd_fetch(args) -> int:
    import pyarrow.parquet as pq

    os.makedirs(args.out, exist_ok=True)
    os.makedirs(args.raw, exist_ok=True)
    counts: dict = {}

    for split in ("train", "validation"):
        # hotpot
        if "hotpot_qa" in args.sources:
            fh = open(os.path.join(args.out, f"hotpot_qa.{split}.jsonl"), "w")
            n = 0
            for f in HOTPOT_FILES[split]:
                p = _download(HOTPOT_REPO, f, args.raw)
                pf = pq.ParquetFile(p)
                for batch in pf.iter_batches(batch_size=2000):
                    for it in hotpot_items(batch.to_pylist()):
                        fh.write(json.dumps(it) + "\n")
                        n += 1
                del pf
                if args.drop_raw:
                    os.remove(p)
                print(f"hotpot_qa {split} {f}: {n} items", flush=True)
            fh.close()
            counts[f"hotpot_qa/{split}"] = n

        # mrqa sources
        want = {MRQA_SUBSET[s]: s for s in args.sources if s in MRQA_SUBSET}
        if not want:
            continue
        handles = {s: open(os.path.join(args.out, f"{s}.{split}.jsonl"), "w")
                   for s in want.values()}
        n = dict.fromkeys(want.values(), 0)
        for f in MRQA_FILES[split]:
            p = _download(MRQA_REPO, f, args.raw)
            pf = pq.ParquetFile(p)
            for batch in pf.iter_batches(
                    batch_size=1000,
                    columns=["subset", "qid", "question", "context", "answers"]):
                rows = batch.to_pylist()
                for sub, src in want.items():
                    sel = [r for r in rows if r["subset"] == sub]
                    if not sel:
                        continue
                    for it in mrqa_items(sel, src):
                        handles[src].write(json.dumps(it) + "\n")
                        n[src] += 1
            del pf
            if args.drop_raw:
                os.remove(p)
            print(f"mrqa {split} {f}: " + json.dumps(n), flush=True)
        for h in handles.values():
            h.close()
        for s, c in n.items():
            counts[f"{s}/{split}"] = c

    summary = {"counts": counts, "passage_words": PASSAGE_WORDS,
               "max_passages": MAX_PASSAGES, "out": os.path.abspath(args.out)}
    with open(os.path.join(args.out, "fetch.summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps(summary, indent=1), flush=True)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--out", default="/home/ec2-user/realret/items")
    f.add_argument("--raw", default="/home/ec2-user/realret/raw")
    f.add_argument("--sources", nargs="+", default=list(SOURCES))
    f.add_argument("--drop-raw", action="store_true")
    f.set_defaults(fn=cmd_fetch)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
