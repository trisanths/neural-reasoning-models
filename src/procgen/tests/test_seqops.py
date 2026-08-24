import numpy as np

from src.procgen import seqops, vocab

OP_TOKENS = {
    vocab.OP_SORT: "sort",
    vocab.OP_REVERSE: "reverse",
    vocab.OP_UNION: "union",
    vocab.OP_DIFF: "diff",
    vocab.OP_DELETE: "delete",
}


def parse(example):
    """Split an example into (task, operand values, output values)."""
    op_positions = [i for i, tok in enumerate(example) if tok in OP_TOKENS]
    assert len(op_positions) == 1
    pos = op_positions[0]
    task = OP_TOKENS[example[pos]]
    head, tail = example[:pos], example[pos + 1:]
    operands = [[]]
    for tok in head:
        if tok == vocab.SEP:
            operands.append([])
        else:
            operands[-1].append(tok - vocab.VALUE_BASE)
    output = [tok - vocab.VALUE_BASE for tok in tail]
    return task, operands, output


def expected_output(task, operands):
    if task == "sort":
        return sorted(operands[0])
    if task == "reverse":
        return operands[0][::-1]
    if task == "union":
        return sorted(set(operands[0]) | set(operands[1]))
    if task == "diff":
        return sorted(set(operands[0]) - set(operands[1]))
    a, (v,) = operands
    return [x for x in a if x != v]


def test_determinism():
    for seed in range(5):
        for task in seqops.TASKS:
            a = seqops.generate_seqop(np.random.default_rng(seed), task, length=10)
            b = seqops.generate_seqop(np.random.default_rng(seed), task, length=10)
            assert a == b
        a = seqops.sample_example(np.random.default_rng(seed))
        b = seqops.sample_example(np.random.default_rng(seed))
        assert a == b


def test_each_task_is_correct():
    rng = np.random.default_rng(11)
    for task in seqops.TASKS:
        for _ in range(30):
            length = int(rng.integers(1, 20))
            example = seqops.generate_seqop(rng, task, length=length)
            parsed_task, operands, output = parse(example)
            assert parsed_task == task
            assert len(operands[0]) == length
            assert output == expected_output(task, operands)


def test_sampled_examples_are_correct_and_in_range():
    rng = np.random.default_rng(12)
    allowed = set()
    for lo, hi in seqops.VOCAB_RANGES:
        allowed.update(range(lo, hi))
    for _ in range(100):
        example = seqops.sample_example(rng)
        assert example[-1] == vocab.EOS
        assert set(example) <= allowed
        task, operands, output = parse(example[:-1])
        assert output == expected_output(task, operands)
