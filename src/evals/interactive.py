"""Interactive retrieval-serving decode loop, used at evaluation time.

Training renders the emit-query-read loop with an oracle, see
src/train/retrieval.py: each question is followed by <|retrieve|> query
<|result|> chunk <|a|> answer <|eot|>. At evaluation time the model has
to drive that loop itself. This module greedy-decodes until the model
emits <|retrieve|>, collects the query it writes, runs the same BM25 as
training over the episode's documents (reliability-weighted ranking, and
without replacement across the rounds of one call, matching the oracle
contracts in src/train/retrieval.py), splices <|result|> plus the top
chunk's tokens into the stream per the trace conventions shared with
src/train/data.py, and hands control back to the model. Decoding stops
on <|eot|>, on an answer boundary (any special token emitted after the
answer began), on the round cap, or on the new token budget.

Model access goes through a step callable so the loop stays framework
light: step_fn(token_ids) returns next token scores over the whole
vocabulary and the loop takes the argmax, with ties broken toward the
lowest id. make_model_step_fn and make_checkpoint_step_fn adapt
src/train models and trainer checkpoints to that interface. Greedy
decoding uses no randomness; the seed argument is recorded in the
result for provenance and reserved for sampling variants.
"""

import numpy as np

from src.train.retrieval import BM25Index

DEFAULT_QUERY_MAX_TOKENS = 64


def _doc_texts(episode_docs) -> list[str]:
    """Accept worldgen document dicts or plain chunk strings."""
    return [doc["text"] if isinstance(doc, dict) else str(doc)
            for doc in episode_docs]


def _build_index(episode_docs, doc_texts) -> BM25Index:
    """Index the documents exactly as the training oracle does: worldgen
    dicts rank with their stated reliability, plain chunks weigh 1.0."""
    reliabilities = [
        float(doc.get("reliability", 1.0)) if isinstance(doc, dict) else 1.0
        for doc in episode_docs
    ]
    return BM25Index(doc_texts, reliabilities=reliabilities)


def _argmax(scores) -> int:
    arr = np.asarray(scores, dtype=np.float64).reshape(-1)
    return int(np.argmax(arr))


def generate_with_retrieval(
    model_step_fn,
    tokenizer,
    episode_docs,
    prompt_tokens,
    max_rounds: int = 4,
    max_new_tokens: int = 256,
    seed: int = 0,
    query_max_tokens: int = DEFAULT_QUERY_MAX_TOKENS,
) -> dict:
    """Greedy-decode from prompt_tokens, serving retrieval as the model asks.

    When the model emits <|retrieve|>, query tokens are collected until it
    emits <|result|>, until query_max_tokens tokens, or until it emits some
    other special token (which is dropped). The collected query is decoded
    to text, scored with the training oracle's BM25 over episode_docs
    (reliability-weighted, excluding chunks already served in this call),
    and the top chunk's tokens are inserted after <|result|>. A <|result|>
    the model did not emit is inserted on its behalf so the trace always
    matches the training layout.
    Served chunk tokens and inserted markers never count against
    max_new_tokens; every model emission does.

    Stop conditions and the stop_reason they report:
      eot              the model emitted <|eot|> (kept in the trace)
      answer_boundary  a special token other than <|eot|> arrived after the
                       answer began; the boundary token is not appended
      max_rounds       <|retrieve|> arrived with no rounds left, with no
                       documents to serve, or with every document already
                       served in this call
      max_new_tokens   the generation budget ran out

    Returns a dict with keys tokens (full trace), generated (model-emitted
    ids only), n_generated, rounds (one dict per served round with query,
    doc_index, chunk, n_chunk_tokens), n_rounds, answer_start (index into
    tokens of the first token after <|a|>, or None), answer_text,
    stop_reason, and seed.
    """
    sid = tokenizer.special_ids
    retrieve_id = sid["<|retrieve|>"]
    result_id = sid["<|result|>"]
    answer_id = sid["<|a|>"]
    eot_id = sid["<|eot|>"]
    special_ids = set(sid.values())

    doc_texts = _doc_texts(episode_docs)
    index = _build_index(episode_docs, doc_texts) if doc_texts else None

    tokens = list(prompt_tokens)
    generated: list[int] = []
    rounds: list[dict] = []
    answer_start = None
    in_answer = False
    stop_reason = "max_new_tokens"

    while len(generated) < max_new_tokens:
        nxt = _argmax(model_step_fn(tokens))
        if nxt == eot_id:
            tokens.append(nxt)
            generated.append(nxt)
            stop_reason = "eot"
            break
        if in_answer and nxt in special_ids:
            stop_reason = "answer_boundary"
            break
        if nxt == answer_id:
            tokens.append(nxt)
            generated.append(nxt)
            in_answer = True
            answer_start = len(tokens)
            continue
        if nxt == retrieve_id:
            if (index is None or len(rounds) >= max_rounds
                    or len(rounds) >= len(doc_texts)):
                stop_reason = "max_rounds"
                break
            tokens.append(nxt)
            generated.append(nxt)
            query_tokens: list[int] = []
            terminated = None
            while len(generated) < max_new_tokens and len(query_tokens) < query_max_tokens:
                qt = _argmax(model_step_fn(tokens))
                if qt == result_id:
                    terminated = "result"
                    break
                if qt == eot_id:
                    terminated = "eot"
                    break
                if qt in special_ids:
                    terminated = "other_special"
                    break
                tokens.append(qt)
                generated.append(qt)
                query_tokens.append(qt)
            if terminated == "eot":
                tokens.append(eot_id)
                generated.append(eot_id)
                stop_reason = "eot"
                break
            if terminated is None and len(query_tokens) < query_max_tokens:
                break
            tokens.append(result_id)
            if terminated == "result":
                generated.append(result_id)
            query_text = tokenizer.decode(query_tokens)
            served = {r["doc_index"] for r in rounds}
            doc_index = index.top(query_text, exclude=served)
            chunk_text = doc_texts[doc_index]
            chunk_tokens = tokenizer.encode(chunk_text)
            tokens.extend(chunk_tokens)
            rounds.append({
                "query": query_text,
                "doc_index": doc_index,
                "chunk": chunk_text,
                "n_chunk_tokens": len(chunk_tokens),
            })
            continue
        tokens.append(nxt)
        generated.append(nxt)

    if answer_start is None:
        answer_text = ""
    else:
        end = len(tokens)
        if stop_reason == "eot":
            end -= 1
        answer_text = tokenizer.decode(tokens[answer_start:end])

    return {
        "tokens": tokens,
        "generated": generated,
        "n_generated": len(generated),
        "rounds": rounds,
        "n_rounds": len(rounds),
        "answer_start": answer_start,
        "answer_text": answer_text,
        "stop_reason": stop_reason,
        "seed": seed,
    }


def make_model_step_fn(model, device):
    """Adapt a src/train TransformerLM to the step callable interface.

    Crops the token history to the model's max_seq_len tail before each
    forward, so the loop can keep a trace longer than the context window.
    """
    import torch

    max_len = model.cfg.max_seq_len

    def step(token_ids):
        ids = list(token_ids)[-max_len:]
        x = torch.tensor([ids], dtype=torch.long, device=device)
        with torch.no_grad():
            logits, _ = model(x)
        return logits[0, -1].float().cpu().numpy()

    return step


def make_checkpoint_step_fn(ckpt_path, device):
    """Load a trainer checkpoint and return (step_fn, model, state)."""
    from src.evals.mc import load_checkpoint_model

    model, state = load_checkpoint_model(ckpt_path, device)
    return make_model_step_fn(model, device), model, state


def make_retrieval_answer_fn(
    step_fn,
    tokenizer,
    max_rounds: int = 4,
    max_new_tokens: int = 128,
    seed: int = 0,
    query_max_tokens: int = DEFAULT_QUERY_MAX_TOKENS,
):
    """Wrap the loop as answer_fn(question, chunks) -> answer text.

    This is the shape src/evals/noise_axis.py drives, so its corruption of
    an example's chunks lands directly on the documents this loop serves.
    """
    sid = tokenizer.special_ids

    def answer_fn(question: str, chunks) -> str:
        prompt = [sid["<|q|>"], *tokenizer.encode(question)]
        out = generate_with_retrieval(
            step_fn, tokenizer, chunks, prompt,
            max_rounds=max_rounds, max_new_tokens=max_new_tokens,
            seed=seed, query_max_tokens=query_max_tokens)
        return out["answer_text"]

    return answer_fn
