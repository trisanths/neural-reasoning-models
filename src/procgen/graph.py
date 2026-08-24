"""Graph reachability traces.

A trace lists the edges of a random directed graph, poses one query pair,
and answers with a shortest path or an unreachable marker. The stream reads:
EDGE u v ... QUERY s t PATH n1 ... nm EOS, or EDGE u v ... QUERY s t
UNREACH EOS. A path always starts at s and ends at t.
"""

from collections import deque

from src.procgen import vocab

VOCAB_RANGES = [
    [vocab.EOS, vocab.EOS + 1],
    [vocab.EDGE, vocab.UNREACH + 1],
    list(vocab.NODE_RANGE),
]


def shortest_path(num_nodes, edges, s, t):
    """Return the BFS shortest path from s to t as a node list, or None.

    Neighbors expand in ascending order so the result is deterministic.
    """
    adj = {u: [] for u in range(num_nodes)}
    for u, v in edges:
        adj[u].append(v)
    for u in adj:
        adj[u].sort()
    parent = {s: None}
    queue = deque([s])
    while queue:
        u = queue.popleft()
        if u == t:
            path = []
            while u is not None:
                path.append(u)
                u = parent[u]
            return path[::-1]
        for v in adj[u]:
            if v not in parent:
                parent[v] = u
                queue.append(v)
    return None


def generate_reachability(rng, num_nodes=10, num_edges=15):
    """Return one reachability trace over a random directed graph."""
    if not 2 <= num_nodes <= vocab.NUM_NODES:
        raise ValueError(f"num_nodes must be in 2..{vocab.NUM_NODES}, got {num_nodes}")
    max_edges = num_nodes * (num_nodes - 1)
    num_edges = min(num_edges, max_edges)
    if num_edges < 1:
        raise ValueError("num_edges must be positive")
    edges = []
    seen = set()
    while len(edges) < num_edges:
        u = int(rng.integers(num_nodes))
        v = int(rng.integers(num_nodes))
        if u == v or (u, v) in seen:
            continue
        seen.add((u, v))
        edges.append((u, v))
    s = int(rng.integers(num_nodes))
    t = int(rng.integers(num_nodes - 1))
    if t >= s:
        t += 1
    out = []
    for u, v in edges:
        out.extend([vocab.EDGE, vocab.node_token(u), vocab.node_token(v)])
    out.extend([vocab.QUERY, vocab.node_token(s), vocab.node_token(t)])
    path = shortest_path(num_nodes, edges, s, t)
    if path is None:
        out.append(vocab.UNREACH)
    else:
        out.append(vocab.PATH)
        out.extend(vocab.node_token(n) for n in path)
    return out


def sample_example(rng, min_nodes=5, max_nodes=16):
    """Return one EOS-terminated trace with sampled graph size."""
    num_nodes = int(rng.integers(min_nodes, max_nodes + 1))
    num_edges = int(rng.integers(num_nodes, 2 * num_nodes + 1))
    return generate_reachability(rng, num_nodes=num_nodes, num_edges=num_edges) + [vocab.EOS]
