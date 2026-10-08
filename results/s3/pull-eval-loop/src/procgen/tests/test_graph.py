from collections import deque

import numpy as np

from src.procgen import graph, vocab


def parse(trace):
    """Return (edges, s, t, path or None) decoded from a trace."""
    edges = []
    i = 0
    while trace[i] == vocab.EDGE:
        u = trace[i + 1] - vocab.NODE_BASE
        v = trace[i + 2] - vocab.NODE_BASE
        edges.append((u, v))
        i += 3
    assert trace[i] == vocab.QUERY
    s = trace[i + 1] - vocab.NODE_BASE
    t = trace[i + 2] - vocab.NODE_BASE
    i += 3
    if trace[i] == vocab.UNREACH:
        assert i == len(trace) - 1
        return edges, s, t, None
    assert trace[i] == vocab.PATH
    path = [tok - vocab.NODE_BASE for tok in trace[i + 1:]]
    return edges, s, t, path


def reference_bfs_distance(edges, s, t):
    """Return the shortest hop count from s to t, or None if unreachable."""
    adj = {}
    for u, v in edges:
        adj.setdefault(u, []).append(v)
    dist = {s: 0}
    queue = deque([s])
    while queue:
        u = queue.popleft()
        if u == t:
            return dist[u]
        for v in adj.get(u, []):
            if v not in dist:
                dist[v] = dist[u] + 1
                queue.append(v)
    return None


def test_determinism():
    for seed in range(5):
        a = graph.generate_reachability(np.random.default_rng(seed), num_nodes=10, num_edges=15)
        b = graph.generate_reachability(np.random.default_rng(seed), num_nodes=10, num_edges=15)
        assert a == b
        a = graph.sample_example(np.random.default_rng(seed))
        b = graph.sample_example(np.random.default_rng(seed))
        assert a == b


def test_answers_verified_against_reference_bfs():
    rng = np.random.default_rng(31)
    saw_path = False
    saw_unreach = False
    for _ in range(200):
        trace = graph.sample_example(rng)
        assert trace[-1] == vocab.EOS
        edges, s, t, path = parse(trace[:-1])
        edge_set = set(edges)
        assert len(edge_set) == len(edges), "duplicate edges"
        assert s != t
        dist = reference_bfs_distance(edges, s, t)
        if path is None:
            saw_unreach = True
            assert dist is None
        else:
            saw_path = True
            assert dist is not None
            assert path[0] == s
            assert path[-1] == t
            assert len(path) == dist + 1, "answer is not a shortest path"
            for u, v in zip(path, path[1:]):
                assert (u, v) in edge_set, "path uses a missing edge"
    assert saw_path and saw_unreach, "sampling never produced both outcomes"


def test_tokens_stay_in_declared_ranges():
    rng = np.random.default_rng(32)
    allowed = set()
    for lo, hi in graph.VOCAB_RANGES:
        allowed.update(range(lo, hi))
    for _ in range(20):
        assert set(graph.sample_example(rng)) <= allowed
