from src.pilot.vllm_model import (MODELS, seed_for, strip_thinking,
                                  user_content)


def test_closed_think_blocks_are_removed():
    assert strip_thinking("<think>\nwork 1+1\n</think>\n\nAnswer: 2") == "Answer: 2"


def test_an_unclosed_think_block_runs_to_the_end():
    assert strip_thinking("Answer: 3\n<think>still going") == "Answer: 3"


def test_a_bare_close_tag_keeps_what_follows():
    assert strip_thinking("rambling\n</think>\nAnswer: 4") == "Answer: 4"


def test_user_content_drops_only_the_trailing_cue():
    p = "Problem.\nWhat?\n\nGive only the answer, on one line, after the word Answer.\nAnswer:"
    got = user_content(p)
    assert got.endswith("after the word Answer.")
    assert user_content("no cue here") == "no cue here"


def test_seed_is_a_stable_function_of_the_prompt():
    assert seed_for("abc") == seed_for("abc") != seed_for("abd")
    assert 0 <= seed_for("abc") < 2 ** 32


def test_model_roster_matches_the_plan():
    assert set(MODELS) == {"lfm2.5-350m-base", "lfm2.5-350m", "qwen3-0.6b-base",
                           "qwen3-0.6b", "qwen3-1.7b-base", "qwen3-1.7b",
                           "qwen3-4b", "qwen3-8b"}
    for name, spec in MODELS.items():
        if spec.kind == "base":
            assert spec.thinking_modes == (False,)
        if name.startswith("qwen3") and spec.kind == "instruct":
            assert spec.thinking_modes == (False, True)


# --------------------------------------------------------------------------
# generate() and loglik() against a scripted engine, no vLLM needed
# --------------------------------------------------------------------------
THINK_END = 9999


class _Ids:
    def __init__(self, ids):
        self.input_ids = ids


class FakeTok:
    """One token per character, a bos token of 1 when special tokens are on."""

    chat_template = "{% if enable_thinking %}{% endif %}"

    def __call__(self, text, add_special_tokens=True):
        return _Ids(([1] if add_special_tokens else []) + [ord(c) for c in text])

    def apply_chat_template(self, msgs, tokenize=False, add_generation_prompt=True,
                            enable_thinking=None):
        return f"<u>{msgs[0]['content']}<a>" + ("" if enable_thinking else "<nt>")

    def get_vocab(self):
        return {"</think>": THINK_END}

    def convert_tokens_to_ids(self, tok):
        return THINK_END


class _Out:
    def __init__(self, text, token_ids, finish_reason="stop", stop_reason=None):
        self.text, self.token_ids = text, token_ids
        self.finish_reason, self.stop_reason = finish_reason, stop_reason


class _Res:
    def __init__(self, out=None, prompt_logprobs=None):
        self.outputs = [out] if out else []
        self.prompt_logprobs = prompt_logprobs


class FakeLLM:
    """Pass one is scripted per prompt length; pass two answers 'Answer: 7'."""

    def __init__(self, script):
        self.script = script
        self.calls = []

    def generate(self, reqs, sps, use_tqdm=False):
        self.calls.append((reqs, sps))
        out = []
        for r in reqs:
            ids = r["prompt_token_ids"]
            key = ids[-1]
            if key in self.script:
                out.append(_Res(self.script[key]))
            else:
                out.append(_Res(_Out("Answer: 7", [55, 56, 57])))
        return out


class _Sp:
    def __init__(self, **kw):
        self.kw = kw


def _model(monkeypatch, script, kind="instruct", thinking=True,
           max_model_len=10_000):
    import sys
    import types

    from src.pilot.vllm_model import VLLMModel

    fake = types.ModuleType("vllm")
    fake.SamplingParams = _Sp
    monkeypatch.setitem(sys.modules, "vllm", fake)
    m = VLLMModel.__new__(VLLMModel)
    m.spec = MODELS["qwen3-0.6b"] if kind == "instruct" else MODELS["qwen3-0.6b-base"]
    m.think_budget = 50
    m.max_model_len = max_model_len
    m.tok = FakeTok()
    m.llm = FakeLLM(script)
    m.think_end = THINK_END
    m.thinking = thinking
    return m


def test_thinking_stopped_at_the_close_tag_is_spliced_and_answered(monkeypatch):
    # The prompt's last token after the chat template is ord('>'); the
    # scripted pass one ends its thinking on </think>, which the engine
    # reports both as the stop reason and as the last token.
    m = _model(monkeypatch, {ord(">"): _Out("plan", [11, 12, THINK_END],
                                            stop_reason=THINK_END)})
    g = m.generate(["Q?\nAnswer:"])[0]
    assert g.n_think_tokens == 2 and not g.think_truncated
    assert g.text == "Answer: 7" and g.n_answer_tokens == 3
    assert "plan\n</think>" in g.raw
    reqs2, sps2 = m.llm.calls[1]
    ids = m.encode("Q?\nAnswer:")
    close = m.tok("\n</think>\n\n", add_special_tokens=False).input_ids
    assert reqs2[0]["prompt_token_ids"] == ids + [11, 12] + close
    seed1 = m.llm.calls[0][1][0].kw["seed"]
    assert sps2[0].kw["seed"] == seed1 + 1
    assert m.llm.calls[0][1][0].kw["stop_token_ids"] == [THINK_END]


def test_truncated_thinking_is_closed_by_force(monkeypatch):
    m = _model(monkeypatch, {ord(">"): _Out("long", list(range(100, 150)),
                                            finish_reason="length")})
    g = m.generate(["Q?\nAnswer:"])[0]
    assert g.think_truncated and g.n_think_tokens == 50
    reqs2, _ = m.llm.calls[1]
    assert reqs2[0]["prompt_token_ids"][-len("\n</think>\n\n"):] == \
        [ord(c) for c in "\n</think>\n\n"]


def test_a_reply_without_a_think_block_is_taken_as_is(monkeypatch):
    m = _model(monkeypatch, {ord(">"): _Out("Answer: 3", [70, 71],
                                            finish_reason="stop")})
    g = m.generate(["Q?\nAnswer:"])[0]
    assert g.text == "Answer: 3" and g.n_think_tokens == 0
    assert len(m.llm.calls) == 1


def test_a_prompt_too_long_is_never_sent(monkeypatch):
    m = _model(monkeypatch, {}, max_model_len=100)
    g = m.generate(["x" * 200 + "\nAnswer:"])[0]
    assert g.finish_reason == "prompt_too_long" and m.llm.calls == []


def test_base_models_complete_greedily_with_the_bos_token(monkeypatch):
    m = _model(monkeypatch, {}, kind="base", thinking=False)
    g = m.generate(["Q?\nAnswer:"])[0]
    reqs, sps = m.llm.calls[0]
    assert reqs[0]["prompt_token_ids"][0] == 1
    assert sps.kw["temperature"] == 0.0 and sps.kw["max_tokens"] == 24
    assert g.text == "Answer: 7"


def test_loglik_sums_the_option_span_only(monkeypatch):
    import types

    m = _model(monkeypatch, {}, kind="base", thinking=False)

    def generate(reqs, sp, use_tqdm=False):
        out = []
        for r in reqs:
            ids = r["prompt_token_ids"]
            # logprob of the token at position i is -(i / 10)
            plp = [None] + [{t: types.SimpleNamespace(logprob=-(i / 10))}
                            for i, t in enumerate(ids) if i > 0]
            out.append(_Res(prompt_logprobs=plp))
        return out
    m.llm.generate = generate
    (nll, n), = m.loglik([("Q: a?\nA:", " bc")])
    n_ctx = 1 + len("Q: a?\nA:")
    assert n == 3
    assert abs(nll - sum(i / 10 for i in range(n_ctx, n_ctx + 3))) < 1e-9
