import pytest

from src.mathgen import algebra, theory

SEEDS = list(range(20))


def _theories():
    return [theory.build(seed) for seed in SEEDS]


def test_determinism_by_seed():
    for seed in SEEDS[:6]:
        assert theory.build(seed).to_graph() == theory.build(seed).to_graph()


def test_graph_is_acyclic_and_layers_are_correct():
    for th in _theories():
        for nid in th.order:
            n = th.nodes[nid]
            for dep in n.depends_on:
                assert dep in th.nodes
                assert th.nodes[dep].layer < n.layer, f"{nid} cites {dep}"
            if n.depends_on:
                assert n.layer == 1 + max(th.nodes[d].layer for d in n.depends_on)
            else:
                assert n.layer == 0


def test_dependency_depth_is_at_least_four():
    for th in _theories():
        assert th.depth() >= 4, f"{th.structure.system_name} is only {th.depth()} deep"


def test_node_ids_are_unique():
    for th in _theories():
        assert len(set(th.order)) == len(th.order)
        assert set(th.order) == set(th.nodes)


def test_every_theorem_really_holds_when_rechecked():
    for th in _theories():
        for nid in th.order:
            n = th.nodes[nid]
            if n.kind != "theorem" or n.key not in theory.THEOREM_CHECKERS:
                continue
            holds, _w, _c, _d = theory.THEOREM_CHECKERS[n.key](th.structure)
            assert holds is True, f"{n.key} was asserted but does not hold"
            assert n.payload["verification"]["result"] is True


def test_every_refutation_really_fails_when_rechecked():
    seen = 0
    for th in _theories():
        for nid in th.order:
            n = th.nodes[nid]
            if n.kind != "refutation":
                continue
            seen += 1
            if n.key in theory.THEOREM_CHECKERS:
                holds, _w, _c, _d = theory.THEOREM_CHECKERS[n.key](th.structure)
                assert holds is False, f"{n.key} was refuted but actually holds"
            elif n.key.startswith("axiom_fails:"):
                name = n.key.split(":", 1)[1]
                check = dict(algebra.AXIOM_MENU)[name]
                assert check(th.structure)[0] is False
    assert seen > 0, "no refutations at all across the sample"


def test_every_verification_record_names_a_bounded_domain():
    for th in _theories():
        for nid in th.order:
            n = th.nodes[nid]
            if n.kind not in ("theorem", "refutation"):
                continue
            v = n.payload["verification"]
            assert v["cases_enumerated"] > 0
            assert v["domain"]
            assert "exhaustive" in v["method"]


def test_definition_extensions_match_a_fresh_computation():
    checked = 0
    for th in _theories():
        for nid in th.order:
            n = th.nodes[nid]
            if n.kind != "definition" or n.key not in theory.DEFINITION_EXTENSIONS:
                continue
            fresh = theory.DEFINITION_EXTENSIONS[n.key](th.structure)
            for field, value in fresh.items():
                assert n.payload[field] == value, f"{n.key}.{field}"
                checked += 1
    assert checked > 100


def test_proof_steps_cite_only_earlier_material():
    for th in _theories():
        for nid in th.order:
            n = th.nodes[nid]
            for step in n.payload.get("proof", []):
                cite = step["cites"]
                if cite is None:
                    continue
                assert cite in th.nodes
                allowed = set(n.depends_on) | th.prerequisites(nid)
                assert cite in allowed, f"{nid} proof cites {cite}, not a prerequisite"
                assert th.nodes[cite].layer < n.layer


def test_theorems_have_a_proof_with_at_least_two_cited_steps():
    for th in _theories():
        for nid in th.order:
            n = th.nodes[nid]
            if n.kind != "theorem":
                continue
            steps = n.payload["proof"]
            assert len(steps) >= 2
            assert sum(1 for s in steps if s["cites"]) >= 1
            assert all(s["text"].strip() for s in steps)


def test_refutations_carry_a_concrete_witness():
    for th in _theories():
        s = th.structure
        for nid in th.order:
            n = th.nodes[nid]
            if n.kind != "refutation":
                continue
            w = n.payload["witness"]
            if not w:
                continue
            for key, value in w.items():
                if key in ("x", "y", "z", "a", "anchor", "absorbing", "generator"):
                    assert value in s.elements, f"{n.key} names {value!r}"


def test_chapters_never_cite_forward():
    for th in _theories():
        for nid in th.order:
            n = th.nodes[nid]
            for dep in n.depends_on:
                assert th.nodes[dep].chapter <= n.chapter


def test_chapters_are_contiguous_and_non_empty():
    for th in _theories():
        chapters = theory.chapter_nodes(th)
        assert sorted(chapters) == list(range(max(chapters) + 1))
        assert all(chapters[c] for c in chapters)
        assert max(chapters) + 1 >= 5


def test_later_chapters_actually_need_earlier_ones():
    """Not just consistent ordering: real cross chapter edges have to exist."""
    for th in _theories():
        cross = [(d, nid) for nid in th.order
                 for d in th.nodes[nid].depends_on
                 if th.nodes[d].chapter < th.nodes[nid].chapter]
        assert len(cross) >= 10, f"only {len(cross)} cross chapter dependencies"
        spans = {th.nodes[nid].chapter - th.nodes[d].chapter for d, nid in cross}
        assert max(spans) >= 3


def test_notion_names_are_invented_and_distinct():
    for th in _theories():
        vals = list(th.notion_names.values())
        assert len(set(vals)) == len(vals)
        assert not set(vals) & set(th.structure.elements)


def test_counts_are_reported_and_non_trivial():
    for th in _theories():
        counts = th.to_graph()["counts"]
        assert counts["definition"] >= 8
        assert counts["theorem"] >= 4
        assert counts["axiom"] >= 3


def test_prerequisites_are_transitive():
    th = theory.build(5)
    for nid in th.order:
        pre = th.prerequisites(nid)
        for p in pre:
            assert th.prerequisites(p) <= pre


def test_two_operation_systems_reach_the_second_operation_theme():
    seen = False
    for th in _theories():
        if not th.structure.has_two_ops:
            continue
        seen = True
        themes = {th.nodes[n].theme for n in th.order}
        assert "second_operation" in themes
    assert seen
