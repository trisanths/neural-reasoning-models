"""External comparison harness, two directions behind one callable.

Direction one scores a public HuggingFace causal LM on our suites: the
naturalized reading suite from src/evals/naturalized.py and held out
worlds with the documents packed into the context. Direction two scores
our own checkpoints, adapted through src/evals/interactive.py, on public
evidence based QA such as SQuAD v2 extractive reading.

Both directions meet at predict_fn(passage, question) -> answer string,
the same interface src/evals/naturalized.evaluate drives. Everything
above that callable is model agnostic: score_qa consumes items shaped as
{"passage", "question", "answers": [gold, ...]} and reports normalized
exact match and the relaxed contains rate using the naturalized suite's
normalization, so numbers are comparable across suites and models.

Public datasets register in PUBLIC_DATASETS as loader callables that
return {"items": [...], "metadata": {...}}. Loaders fetch their raw JSON
from a stable public URL at runtime and cache it under
~/data/public_bench/, so adding a dataset means adding one loader and
one registry line.

The transformers and torch imports live inside the adapter factories so
the scoring core stays importable without either installed.
"""

import json
import os
import posixpath
import random
import re
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

import numpy as np

from src.evals.naturalized import contains_answer, exact_match, normalize

DEFAULT_CACHE_DIR = Path.home() / "data" / "public_bench"

SQUAD_V2_DEV_URL = (
    "https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v2.0.json"
)

QA_INSTRUCTION = (
    "Read the passage and answer the question. Reply with only the "
    "shortest exact answer, taken from the passage when possible."
)


def subsample_items(items, n, seed: int):
    """Deterministically pick n items, preserving the original order.

    Returns the full list when n is None or at least len(items). The
    selection depends only on (len(items), n, seed).
    """
    items = list(items)
    if n is None or n >= len(items):
        return items
    if n < 0:
        raise ValueError(f"n must be non negative, got {n}")
    rng = random.Random(seed)
    picked = sorted(rng.sample(range(len(items)), n))
    return [items[i] for i in picked]


def score_qa(items, predict_fn, keep_predictions: bool = True) -> dict:
    """Score QA items through predict_fn(passage, question) -> str.

    Each item carries a passage, a question, and a list of acceptable
    gold answers. A prediction gets exact match or contains credit when
    it earns it against any gold. An empty gold list means the question
    is unanswerable and credit goes to predictions that normalize to the
    empty string. Items may carry a group key for a per group breakdown
    and an id that is echoed into the prediction records.
    """
    items = list(items)
    if not items:
        raise ValueError("no items to score")
    n_em = 0
    n_contains = 0
    per_group = {}
    records = []
    for item in items:
        pred = predict_fn(item["passage"], item["question"])
        golds = item["answers"]
        if golds:
            em = any(exact_match(pred, g) for g in golds)
            contains = any(contains_answer(pred, g) for g in golds)
        else:
            em = contains = normalize(pred) == ""
        n_em += int(em)
        n_contains += int(contains)
        group = item.get("group")
        if group is not None:
            stats = per_group.setdefault(group, {"n": 0, "em": 0, "contains": 0})
            stats["n"] += 1
            stats["em"] += int(em)
            stats["contains"] += int(contains)
        if keep_predictions:
            records.append({
                "id": item.get("id"),
                "prediction": pred,
                "em": em,
                "contains": contains,
            })
    for stats in per_group.values():
        stats["em"] = round(stats["em"] / stats["n"], 4)
        stats["contains"] = round(stats["contains"] / stats["n"], 4)
    n = len(items)
    result = {
        "n": n,
        "em": round(n_em / n, 4),
        "contains": round(n_contains / n, 4),
        "per_group": per_group,
    }
    if keep_predictions:
        result["predictions"] = records
    return result


# Direction one, our suites for any model behind predict_fn.


def naturalized_items(data_dir=None):
    """The naturalized reading suite as score_qa items, grouped by register."""
    from src.evals.naturalized import load_suite

    suite = load_suite(data_dir)
    items = [{
        "id": item["id"],
        "passage": item["passage"],
        "question": item["question"],
        "answers": [item["answer"]],
        "group": item["register"],
    } for item in suite["items"]]
    return items, suite["metadata"]


def run_naturalized_bench(predict_fn, n_items=None, seed: int = 0,
                          data_dir=None, keep_predictions: bool = True) -> dict:
    """Score predict_fn on the naturalized reading suite."""
    items, metadata = naturalized_items(data_dir)
    items = subsample_items(items, n_items, seed)
    result = score_qa(items, predict_fn, keep_predictions=keep_predictions)
    result.update({
        "suite": "naturalized_reading",
        "version": metadata["version"],
        "n_items_available": metadata["n_items"],
        "seed": seed,
    })
    return result


def episode_passage(episode) -> str:
    """Render one held out episode as plain text, preamble then documents."""
    from src.train.data import render_world_preamble

    parts = [render_world_preamble(episode["world"])]
    parts.extend(doc["text"] for doc in episode["documents"])
    return "\n\n".join(parts)


def heldout_items(episodes):
    """Held out world questions as score_qa items, grouped by question type.

    Documents in context mode: the whole episode text is the passage, so
    any model that reads can answer without the retrieval protocol. Gold
    answers are the generator's short strings, scored the same free form
    way as every other suite here, which is stricter than the multiple
    choice scoring in src/evals/heldout.py and not comparable to it.
    """
    items = []
    for i, ep in enumerate(episodes):
        passage = episode_passage(ep)
        for j, q in enumerate(ep["questions"]):
            items.append({
                "id": f"ep{i:03d}_q{j:02d}",
                "passage": passage,
                "question": q["text"],
                "answers": [q["answer"]],
                "group": q["type"],
            })
    return items


def run_heldout_bench(predict_fn, n_episodes: int = 20, seed: int = 999,
                      episodes=None, keep_predictions: bool = True) -> dict:
    """Score predict_fn on held out worlds in documents in context mode.

    Episodes come from worldgen seeds in the held out range unless the
    caller passes its own list.
    """
    if episodes is None:
        from src.worldgen.engine import generate_episodes

        episodes = list(generate_episodes(seed, n_episodes))
    else:
        episodes = list(episodes)
    items = heldout_items(episodes)
    result = score_qa(items, predict_fn, keep_predictions=keep_predictions)
    result.update({
        "suite": "heldout_worlds_in_context",
        "n_episodes": len(episodes),
        "seed": seed,
    })
    return result


# Direction two, public evidence based QA datasets.


def fetch_cached(url: str, cache_dir=None, filename=None) -> Path:
    """Return a local path for url, downloading once into the cache dir."""
    base = Path(cache_dir) if cache_dir is not None else DEFAULT_CACHE_DIR
    base.mkdir(parents=True, exist_ok=True)
    name = filename or posixpath.basename(urlparse(url).path)
    if not name:
        raise ValueError(f"cannot derive a cache filename from {url!r}")
    path = base / name
    if path.exists() and path.stat().st_size > 0:
        return path
    tmp = path.with_suffix(path.suffix + ".part")
    with urllib.request.urlopen(url) as resp, open(tmp, "wb") as fh:
        while True:
            block = resp.read(1 << 20)
            if not block:
                break
            fh.write(block)
    os.replace(tmp, path)
    return path


def parse_squad_v2(raw: dict, include_impossible: bool = False):
    """Flatten SQuAD v2 JSON into score_qa items.

    Answers deduplicate the annotator spans in first seen order.
    Unanswerable questions carry an empty answers list and are dropped
    unless include_impossible is set, because our decode conventions
    have no abstain marker yet.
    """
    items = []
    n_total = 0
    n_impossible = 0
    for article in raw["data"]:
        title = article.get("title", "")
        for paragraph in article["paragraphs"]:
            context = paragraph["context"]
            for qa in paragraph["qas"]:
                n_total += 1
                impossible = bool(qa.get("is_impossible", False))
                if impossible:
                    n_impossible += 1
                    if not include_impossible:
                        continue
                answers = list(dict.fromkeys(
                    a["text"] for a in qa.get("answers", [])))
                items.append({
                    "id": qa["id"],
                    "passage": context,
                    "question": qa["question"],
                    "answers": [] if impossible else answers,
                    "group": title,
                })
    stats = {"n_total_qas": n_total, "n_impossible": n_impossible,
             "include_impossible": include_impossible}
    return items, stats


def load_squad_v2(cache_dir=None, url: str = SQUAD_V2_DEV_URL,
                  include_impossible: bool = False) -> dict:
    """Load the public SQuAD v2 dev JSON, fetching and caching on first use."""
    path = fetch_cached(url, cache_dir)
    with open(path) as fh:
        raw = json.load(fh)
    items, stats = parse_squad_v2(raw, include_impossible=include_impossible)
    metadata = {
        "dataset": "squad_v2",
        "source_url": url,
        "cache_path": str(path),
        "source_version": raw.get("version"),
        **stats,
    }
    return {"items": items, "metadata": metadata}


PUBLIC_DATASETS = {
    "squad_v2": load_squad_v2,
}


def run_public_qa(predict_fn, dataset: str = "squad_v2", n_items=None,
                  seed: int = 0, cache_dir=None, loader_kwargs=None,
                  keep_predictions: bool = True) -> dict:
    """Score predict_fn on one registered public dataset."""
    if dataset not in PUBLIC_DATASETS:
        raise KeyError(
            f"unknown dataset {dataset!r}, choose from {sorted(PUBLIC_DATASETS)}")
    loaded = PUBLIC_DATASETS[dataset](cache_dir=cache_dir,
                                      **(loader_kwargs or {}))
    items = subsample_items(loaded["items"], n_items, seed)
    result = score_qa(items, predict_fn, keep_predictions=keep_predictions)
    result.update({
        "suite": "public_qa",
        "dataset": dataset,
        "n_items_available": len(loaded["items"]),
        "seed": seed,
        "metadata": loaded["metadata"],
    })
    return result


# Adapters. Direction one wraps a HuggingFace causal LM, direction two
# wraps our trainer checkpoints through src/evals/interactive.py.


_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL)


def clean_generation(text: str) -> str:
    """Reduce raw decoded model output to a one line answer.

    Closed thinking blocks are removed. An unterminated <think> means
    the model spent its whole budget thinking, so everything from the
    marker on is dropped and the answer may come back empty. Of what
    remains, the first non empty line wins.
    """
    text = _THINK_BLOCK.sub(" ", text)
    if "<think>" in text:
        text = text.split("<think>")[0]
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def build_qa_prompt(passage: str, question: str) -> str:
    """The plain text QA prompt shared by both adapters' chat and raw modes."""
    return f"{QA_INSTRUCTION}\n\nPassage:\n{passage}\n\nQuestion: {question}"


def make_hf_predict_fn(model_name: str, device=None, dtype="auto",
                       max_new_tokens: int = 32, prompt_style: str = "auto",
                       seed: int = 0):
    """Adapt a HuggingFace causal LM checkpoint to predict_fn.

    Greedy decode only, so the seed exists for provenance and for future
    sampling variants. prompt_style "chat" pushes the prompt through the
    tokenizer's chat template with thinking disabled where the template
    supports it (Qwen3 does), "plain" appends a bare Answer: cue, and
    "auto" picks chat when the tokenizer ships a template. The returned
    callable carries a metadata dict for report provenance.
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.manual_seed(seed)
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(model_name)
    try:
        model = AutoModelForCausalLM.from_pretrained(model_name, dtype=dtype)
    except TypeError:
        # Older transformers spell the argument torch_dtype.
        model = AutoModelForCausalLM.from_pretrained(model_name,
                                                     torch_dtype=dtype)
    model.to(device).eval()

    if prompt_style not in ("auto", "chat", "plain"):
        raise ValueError(f"unknown prompt_style {prompt_style!r}")
    use_chat = (prompt_style == "chat"
                or (prompt_style == "auto"
                    and getattr(tok, "chat_template", None) is not None))
    pad_id = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id

    def render_prompt(passage: str, question: str) -> str:
        body = build_qa_prompt(passage, question)
        if not use_chat:
            return body + "\nAnswer:"
        messages = [{"role": "user", "content": body}]
        try:
            return tok.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True,
                enable_thinking=False)
        except TypeError:
            return tok.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True)

    def predict_fn(passage: str, question: str) -> str:
        text = render_prompt(passage, question)
        enc = tok(text, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model.generate(**enc, max_new_tokens=max_new_tokens,
                                 do_sample=False, pad_token_id=pad_id)
        gen = out[0, enc["input_ids"].shape[1]:]
        return clean_generation(tok.decode(gen, skip_special_tokens=True))

    import transformers

    predict_fn.metadata = {
        "backend": "hf",
        "model": model_name,
        "transformers_version": transformers.__version__,
        "torch_version": torch.__version__,
        "device": str(device),
        "dtype": str(model.dtype),
        "prompt_style": "chat" if use_chat else "plain",
        "max_new_tokens": max_new_tokens,
        "seed": seed,
    }
    return predict_fn


def chunk_passage(passage: str, chunk_words: int = 60):
    """Split a passage into retrieval chunks of at most chunk_words words.

    Sentences pack greedily into chunks; a single sentence longer than
    the budget is hard split on word boundaries. Deterministic, order
    preserving, and lossless up to whitespace.
    """
    if chunk_words < 1:
        raise ValueError(f"chunk_words must be positive, got {chunk_words}")
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", passage.strip()) if s]
    chunks = []
    current: list[str] = []
    n_current = 0
    for sentence in sentences:
        words = sentence.split()
        if n_current and n_current + len(words) > chunk_words:
            chunks.append(" ".join(current))
            current, n_current = [], 0
        while len(words) > chunk_words:
            if current:
                chunks.append(" ".join(current))
                current, n_current = [], 0
            chunks.append(" ".join(words[:chunk_words]))
            words = words[chunk_words:]
        current.extend(words)
        n_current += len(words)
    if current:
        chunks.append(" ".join(current))
    return chunks


def greedy_answer(step_fn, tokenizer, prompt_ids, max_new_tokens: int = 64) -> str:
    """Greedy decode from prompt_ids until any special token or the budget.

    Argmax with ties toward the lowest id, matching the interactive loop.
    """
    special_ids = set(tokenizer.special_ids.values())
    tokens = list(prompt_ids)
    out: list[int] = []
    for _ in range(max_new_tokens):
        scores = np.asarray(step_fn(tokens), dtype=np.float64).reshape(-1)
        nxt = int(np.argmax(scores))
        if nxt in special_ids:
            break
        tokens.append(nxt)
        out.append(nxt)
    return tokenizer.decode(out).strip()


def make_ours_predict_fn(ckpt_path, tokenizer, device=None,
                         mode: str = "retrieval", max_rounds: int = 4,
                         max_new_tokens: int = 128, chunk_words: int = 60,
                         seed: int = 0):
    """Adapt one of our trainer checkpoints to predict_fn.

    tokenizer is a TrainTokenizer or a path to its json. Mode
    "retrieval" chunks the passage and serves it through the interactive
    emit query read loop from src/evals/interactive.py, so the model
    must drive the protocol itself. Mode "context" packs the passage
    into the prompt as <|doc|> passage <|q|> question <|a|> and greedy
    decodes the answer directly; make_model_step_fn crops to the model's
    context tail, so an oversized passage loses its head. The returned
    callable carries a metadata dict for report provenance.
    """
    from src.evals.interactive import (
        make_checkpoint_step_fn,
        make_retrieval_answer_fn,
    )

    if mode not in ("retrieval", "context"):
        raise ValueError(f"unknown mode {mode!r}")
    if device is None:
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
    if isinstance(tokenizer, (str, Path)):
        from src.train.tokenizer import load_tokenizer

        tokenizer = load_tokenizer(str(tokenizer))
    step_fn, model, state = make_checkpoint_step_fn(ckpt_path, device)

    if mode == "retrieval":
        answer_fn = make_retrieval_answer_fn(
            step_fn, tokenizer, max_rounds=max_rounds,
            max_new_tokens=max_new_tokens, seed=seed)

        def predict_fn(passage: str, question: str) -> str:
            return answer_fn(question, chunk_passage(passage, chunk_words))
    else:
        sid = tokenizer.special_ids

        def predict_fn(passage: str, question: str) -> str:
            prompt = [sid["<|doc|>"], *tokenizer.encode(passage),
                      sid["<|q|>"], *tokenizer.encode(question), sid["<|a|>"]]
            return greedy_answer(step_fn, tokenizer, prompt,
                                 max_new_tokens=max_new_tokens)

    predict_fn.metadata = {
        "backend": "ours",
        "checkpoint": str(ckpt_path),
        "step": int(state.get("step", -1)),
        "mode": mode,
        "max_rounds": max_rounds,
        "max_new_tokens": max_new_tokens,
        "chunk_words": chunk_words,
        "device": str(device),
        "seed": seed,
    }
    return predict_fn
