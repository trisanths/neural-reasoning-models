"""The tie group, the two tie-break policies, and what each one costs.

The page sets that produced the E0 ladder hold pages built from one template.
These tests pin the property that makes the gate's choice among them a
measurement artifact under "first" and not under "content".
"""

from src.rl.env import RetrievalService, break_tie, make_service
from src.retrieval.rankdiag import diagnose
from src.train.retrieval import BM25Index

PREAMBLE = ("The Wrenzel referral system.\n\nEvery office in the Wrenzel "
            "system routes a request to a desk according to the request's "
            "type.")
TABLE_A = ("The Fexharv routing table.\n\nRequests in the Fexharv office are "
           "routed by their type.\n\nA harvka is handled by the zelmi desk.\n"
           "A wrensol is handled by the xilzel desk.")
TABLE_B = ("The Yuklum routing table.\n\nRequests in the Yuklum office are "
           "routed by their type.\n\nA clomel is handled by the miplo desk.\n"
           "A xilzel is handled by the eskfex desk.")

PAGES = [PREAMBLE, TABLE_A, TABLE_B]
SALAD = "desk handled type routed office requests"


def test_two_templated_pages_tie_exactly():
    index = BM25Index(PAGES)
    tied, _ = index.top_group(SALAD)
    assert tied == [1, 2]
    assert index.score(SALAD, 1) == index.score(SALAD, 2)


def test_top_group_agrees_with_top_on_its_first_element():
    index = BM25Index(PAGES)
    for query in (SALAD, "yuklum", "harvka", "referral system", ""):
        tied, _ = index.top_group(query)
        assert tied[0] == index.top(query)


def test_first_policy_serves_the_earlier_page_every_time():
    for _ in range(5):
        service = make_service([{"text": t} for t in PAGES], tie_break="first")
        assert service.top(SALAD)[0] == 1


def test_content_policy_does_not_read_document_order():
    """The same two pages, swapped, must not swap the answer."""
    forward = [{"text": t} for t in PAGES]
    swapped = [{"text": PREAMBLE}, {"text": TABLE_B}, {"text": TABLE_A}]
    a = make_service(forward, tie_break="content").top(SALAD)[1]
    b = make_service(swapped, tie_break="content").top(SALAD)[1]
    assert a == b


def test_content_policy_is_reproducible():
    runs = {make_service([{"text": t} for t in PAGES],
                         tie_break="content").top(SALAD)[0]
            for _ in range(20)}
    assert len(runs) == 1


def test_content_policy_splits_a_tie_across_queries():
    """Over a spread of queries each tied page wins some of them, which is
    what "first" never allows."""
    served = set()
    for i in range(40):
        q = f"{SALAD} {i}"
        served.add(make_service([{"text": t} for t in PAGES],
                                tie_break="content").top(q)[0])
    assert served == {1, 2}


def test_neither_policy_touches_a_query_that_discriminates():
    for policy in ("first", "content"):
        service = make_service([{"text": t} for t in PAGES], tie_break=policy)
        assert service.top("yuklum clomel miplo")[0] == 2


def test_without_replacement_survives_the_tie_break():
    service = make_service([{"text": t} for t in PAGES], tie_break="content")
    first = service.top(SALAD)[0]
    second = service.top(SALAD)[0]
    assert first != second
    assert {first, second} == {1, 2}


def test_diagnose_names_a_tie_loss():
    index = BM25Index(PAGES)
    d = diagnose(index, SALAD, {2})
    assert d["verdict"] == "tie_loss"
    assert d["gold_rank"] == 2
    assert d["tie_group"] == 2
    assert d["margin"] == 0.0


def test_diagnose_names_a_score_loss():
    index = BM25Index(PAGES)
    d = diagnose(index, "harvka zelmi", {2})
    assert d["verdict"] == "score_loss"
    assert d["margin"] > 0.0


def test_break_tie_rejects_an_unknown_policy():
    try:
        break_tie("q", PAGES, [1, 2], "semantic")
    except ValueError:
        return
    raise AssertionError("unknown policy should raise")


def test_service_records_the_tie_group_size():
    service = make_service([{"text": t} for t in PAGES], tie_break="first")
    service.top(SALAD)
    assert service.last_tie_group == 2
    service2 = make_service([{"text": t} for t in PAGES], tie_break="first")
    service2.top("yuklum clomel miplo")
    assert service2.last_tie_group == 1
