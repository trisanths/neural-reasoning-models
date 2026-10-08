"""Domain rule modules for episode generation.

Each domain class provides four static pieces: generate builds entities,
rules, facts, and questions from an rng; sentence renders one fact as text;
corrupt produces a contradictory variant of a fact; filler produces an
irrelevant sentence. The engine composes these into full episodes.

Facts follow the SPEC schema: {"id", "s", "p", "o", "t"} where s is an entity
id and o is an entity id or a literal string. Questions carry machine
checkable answers, the derivation fact ids, and a hop count.

Document templates follow one surface convention: each sentence restates the
entity on the side of the relation that questions anchor on (the acquiree,
the child, the route's origin, the restricted substance, the adopting
jurisdiction). Bag-of-words retrieval cannot see argument roles, so a
sentence mentioning each entity once is indistinguishable from a reversed
statement of the same relation over the same names. The restatement puts the
role into term frequency: the supporting document carries the anchored name
twice while a document using that name in the opposite role carries it once,
which is exactly the signal a query built from question terms can use.
"""

from src.worldgen import names


def _pick(rng, seq):
    return seq[int(rng.integers(len(seq)))]


def _sample_idx(rng, n, k):
    """Return k distinct indices in [0, n) in random order."""
    return [int(i) for i in rng.permutation(n)[:k]]


def _other_entity(rng, entities, etype, exclude_id):
    pool = [e for e in entities if e["type"] == etype and e["id"] != exclude_id]
    if not pool:
        return None
    return _pick(rng, pool)


class Corporate:
    name = "corporate"
    rules = [
        "an acquisition transfers the target and its subsidiaries to the acquirer",
        "each company has exactly one chief executive",
    ]

    # Restated anchors: the acquiree (questions ask who acquired it), the
    # company in ceo_of (questions ask for its chief executive), and the
    # company in hq_in (questions ask where it is headquartered).
    TEMPLATES = {
        "acquired": [
            "{s} acquired {o} in period {t}, taking {o} as a subsidiary.",
            "In period {t}, {s} completed its takeover of {o}, bringing "
            "{o} under new ownership.",
            "A filing dated period {t} records that {o} was purchased by "
            "{s}; owners of {o} approved the sale.",
        ],
        "ceo_of": [
            "{s} serves as chief executive of {o}, leading {o} day to day.",
            "The board of {o} confirmed {s} as chief executive of {o}.",
            "{o} lists {s} as its chief executive officer; the {o} board "
            "minutes record the vote.",
        ],
        "hq_in": [
            "{s} is headquartered in {o}, where {s} keeps its main office.",
            "The head office of {s} is located in {o}; {s} files from "
            "that address.",
            "{s} operates from its base in {o}, and {s} maintains that site.",
        ],
    }

    FILLER = [
        "{a} announced a routine audit for period {t}.",
        "Analysts met with representatives of {a} during period {t}.",
        "{a} published its quarterly newsletter in period {t}.",
    ]

    @staticmethod
    def generate(rng):
        n_comp = int(rng.integers(6, 10))
        companies = names.unique_names(rng, "company", n_comp)
        people = names.unique_names(rng, "person", n_comp)
        places = names.unique_names(rng, "place", 3)
        entities = []
        comp_ids, person_ids, place_ids = [], [], []
        for name in companies:
            eid = f"e{len(entities) + 1}"
            entities.append({"id": eid, "type": "company", "name": name})
            comp_ids.append(eid)
        for name in people:
            eid = f"e{len(entities) + 1}"
            entities.append({"id": eid, "type": "person", "name": name})
            person_ids.append(eid)
        for name in places:
            eid = f"e{len(entities) + 1}"
            entities.append({"id": eid, "type": "place", "name": name})
            place_ids.append(eid)

        facts = []

        def add_fact(s, p, o, t):
            fid = f"f{len(facts) + 1}"
            facts.append({"id": fid, "s": s, "p": p, "o": o, "t": int(t)})
            return fid

        hq_fact = {}
        for cid in comp_ids:
            hq_fact[cid] = add_fact(cid, "hq_in", _pick(rng, place_ids), 0)
        ceo_fact = {}
        for cid, pid in zip(comp_ids, person_ids):
            ceo_fact[cid] = add_fact(pid, "ceo_of", cid, 1)

        # Acquisitions form a forest: a company with index i can be acquired
        # by any earlier company, so chains of length two or more can occur.
        acquired_by = {}
        acq_fact = {}
        for i in range(1, n_comp):
            if rng.random() < 0.6:
                j = int(rng.integers(0, i))
                acquirer, target = comp_ids[j], comp_ids[i]
                acquired_by[target] = acquirer
                acq_fact[target] = add_fact(acquirer, "acquired", target, 2 + i)

        name_of = {e["id"]: e["name"] for e in entities}
        questions = []

        def add_q(text, answer, qtype, derivation, hops):
            qid = f"q{len(questions) + 1}"
            questions.append({
                "qid": qid, "text": text, "answer": answer, "type": qtype,
                "derivation": derivation, "hops": int(hops),
            })

        for cid in _sample_idx(rng, n_comp, 2):
            comp = comp_ids[cid]
            fid = ceo_fact[comp]
            person = next(f["s"] for f in facts if f["id"] == fid)
            add_q(f"Who is the chief executive of {name_of[comp]}?",
                  name_of[person], "lookup", [fid], 1)

        targets = sorted(acquired_by)
        for comp in targets[:2]:
            add_q(f"Which company acquired {name_of[comp]}?",
                  name_of[acquired_by[comp]], "lookup", [acq_fact[comp]], 1)

        # Multi hop: follow the acquisition chain to the root owner.
        for comp in targets:
            chain = []
            cur = comp
            while cur in acquired_by:
                chain.append(acq_fact[cur])
                cur = acquired_by[cur]
            if len(chain) >= 2:
                add_q(
                    "Following the chain of acquisitions, which company is "
                    f"the ultimate parent of {name_of[comp]}?",
                    name_of[cur], "multi_hop", chain, len(chain))
                break

        comp = comp_ids[_sample_idx(rng, n_comp, 1)[0]]
        fid = hq_fact[comp]
        place = next(f["o"] for f in facts if f["id"] == fid)
        add_q(f"In which city is {name_of[comp]} headquartered?",
              name_of[place], "lookup", [fid], 1)

        return entities, list(Corporate.rules), facts, questions

    @staticmethod
    def sentence(fact, name_of, rng):
        tpl = _pick(rng, Corporate.TEMPLATES[fact["p"]])
        return tpl.format(s=name_of.get(fact["s"], fact["s"]),
                          o=name_of.get(fact["o"], fact["o"]), t=fact["t"])

    @staticmethod
    def corrupt(fact, entities, rng):
        etype = {"acquired": "company", "ceo_of": "company", "hq_in": "place"}[fact["p"]]
        other = _other_entity(rng, entities, etype, fact["o"])
        if other is None:
            return None
        wrong = dict(fact)
        wrong["o"] = other["id"]
        return wrong

    @staticmethod
    def filler(entities, name_of, rng):
        comp = _other_entity(rng, entities, "company", "")
        tpl = _pick(rng, Corporate.FILLER)
        return tpl.format(a=name_of[comp["id"]], t=int(rng.integers(0, 9)))


class Regulatory:
    name = "regulatory"
    rules = [
        "a restriction in a jurisdiction applies in every jurisdiction that "
        "adopts its code",
        "adoption of a code is transitive",
    ]

    # Restated anchors: the substance in restricts (questions name the
    # substance), and the adopting jurisdiction in adopts_code_of (a
    # propagation hop reaches the adoption fact from that jurisdiction).
    TEMPLATES = {
        "restricts": [
            "The authority of {s} prohibits {o} as of period {t}; all "
            "sales of {o} must cease.",
            "{s} placed {o} on its restricted register in period {t}, "
            "so {o} is barred there.",
            "A notice from {s} bans the sale of {o} effective period {t}; "
            "stocks of {o} must be withdrawn.",
        ],
        "adopts_code_of": [
            "{s} adopts the regulatory code of {o} in period {t}, which "
            "binds {s} directly.",
            "In period {t}, {s} incorporated the code of {o} into its "
            "law, amending the statutes of {s}.",
            "The legislature of {s} enacted the framework of {o} in "
            "period {t}, making it law across {s}.",
        ],
    }

    FILLER = [
        "The council of {a} met in period {t} without new rulings.",
        "{a} reappointed its standards committee in period {t}.",
        "Inspectors from {a} completed training in period {t}.",
    ]

    @staticmethod
    def generate(rng):
        n_jur = int(rng.integers(5, 8))
        n_sub = int(rng.integers(4, 7))
        jur_names = names.unique_names(rng, "place", n_jur)
        sub_names = [w.lower() for w in names.unique_names(rng, "place", n_sub)]
        entities = []
        jur_ids, sub_ids = [], []
        for name in jur_names:
            eid = f"e{len(entities) + 1}"
            entities.append({"id": eid, "type": "jurisdiction", "name": name})
            jur_ids.append(eid)
        for name in sub_names:
            eid = f"e{len(entities) + 1}"
            entities.append({"id": eid, "type": "substance", "name": name})
            sub_ids.append(eid)

        facts = []

        def add_fact(s, p, o, t):
            fid = f"f{len(facts) + 1}"
            facts.append({"id": fid, "s": s, "p": p, "o": o, "t": int(t)})
            return fid

        direct = {}
        for j in jur_ids:
            for s in sub_ids:
                if rng.random() < 0.3:
                    direct[(j, s)] = add_fact(j, "restricts", s, int(rng.integers(1, 6)))

        # Adoption edges point from a later jurisdiction to an earlier one,
        # which keeps the relation acyclic.
        adopts = {}
        for i in range(1, n_jur):
            if rng.random() < 0.5:
                j = int(rng.integers(0, i))
                adopts[jur_ids[i]] = (jur_ids[j],
                                      add_fact(jur_ids[i], "adopts_code_of", jur_ids[j],
                                               int(rng.integers(1, 6))))

        def closure(j):
            """All substances restricted in j, with one derivation each."""
            out = {}
            chain = []
            cur = j
            while True:
                for s in sub_ids:
                    if (cur, s) in direct and s not in out:
                        out[s] = chain + [direct[(cur, s)]]
                if cur in adopts:
                    parent, fid = adopts[cur]
                    chain = chain + [fid]
                    cur = parent
                else:
                    return out

        name_of = {e["id"]: e["name"] for e in entities}
        questions = []

        def add_q(text, answer, qtype, derivation, hops):
            qid = f"q{len(questions) + 1}"
            questions.append({
                "qid": qid, "text": text, "answer": answer, "type": qtype,
                "derivation": derivation, "hops": int(hops),
            })

        n_direct = 0
        n_prop = 0
        n_neg = 0
        for j in jur_ids:
            cl = closure(j)
            for s in sub_ids:
                text = f"Is {name_of[s]} restricted in {name_of[j]}?"
                if (j, s) in direct and n_direct < 2:
                    add_q(text, "yes", "yes_no", [direct[(j, s)]], 1)
                    n_direct += 1
                elif s in cl and (j, s) not in direct and n_prop < 2:
                    add_q(text, "yes", "multi_hop", cl[s], len(cl[s]))
                    n_prop += 1
                elif s not in cl and n_neg < 1:
                    add_q(text, "no", "yes_no", [], 1)
                    n_neg += 1

        return entities, list(Regulatory.rules), facts, questions

    @staticmethod
    def sentence(fact, name_of, rng):
        tpl = _pick(rng, Regulatory.TEMPLATES[fact["p"]])
        return tpl.format(s=name_of.get(fact["s"], fact["s"]),
                          o=name_of.get(fact["o"], fact["o"]), t=fact["t"])

    @staticmethod
    def corrupt(fact, entities, rng):
        etype = "substance" if fact["p"] == "restricts" else "jurisdiction"
        other = _other_entity(rng, entities, etype, fact["o"])
        if other is None:
            return None
        wrong = dict(fact)
        wrong["o"] = other["id"]
        return wrong

    @staticmethod
    def filler(entities, name_of, rng):
        jur = _other_entity(rng, entities, "jurisdiction", "")
        tpl = _pick(rng, Regulatory.FILLER)
        return tpl.format(a=name_of[jur["id"]], t=int(rng.integers(0, 9)))


class Logistics:
    name = "logistics"
    rules = [
        "routes are directional and carry at most their stated capacity",
        "freight may pass through intermediate hubs",
    ]

    # Restated anchor: the origin hub. Relay questions walk the route
    # forward, so each hop knows the origin and seeks the destination.
    TEMPLATES = {
        "route_to": [
            "The route from {s} to {o} carries {c} containers per "
            "period, loading at {s}.",
            "A corridor links {s} to {o} with capacity {c}; departures "
            "leave {s} on schedule.",
            "Schedules show {s} shipping to {o} at {c} containers each "
            "period, outbound from {s}.",
        ],
    }

    FILLER = [
        "The {a} hub renewed its safety certificate in period {t}.",
        "Crews at {a} completed maintenance in period {t}.",
        "The terminal at {a} reported normal operations in period {t}.",
    ]

    @staticmethod
    def generate(rng):
        n_hub = int(rng.integers(6, 9))
        hub_names = names.unique_names(rng, "place", n_hub)
        entities = []
        hub_ids = []
        for name in hub_names:
            eid = f"e{len(entities) + 1}"
            entities.append({"id": eid, "type": "hub", "name": name})
            hub_ids.append(eid)

        facts = []
        edges = {}

        def add_route(a, b):
            cap = int(rng.integers(10, 100))
            fid = f"f{len(facts) + 1}"
            facts.append({"id": fid, "s": a, "p": "route_to", "o": b,
                          "t": 0, "cap": cap})
            edges[(a, b)] = (cap, fid)

        n_edges = int(1.6 * n_hub)
        attempts = 0
        while len(edges) < n_edges and attempts < 200:
            attempts += 1
            a, b = (_pick(rng, hub_ids), _pick(rng, hub_ids))
            if a != b and (a, b) not in edges:
                add_route(a, b)

        name_of = {e["id"]: e["name"] for e in entities}
        questions = []

        def add_q(text, answer, qtype, derivation, hops):
            qid = f"q{len(questions) + 1}"
            questions.append({
                "qid": qid, "text": text, "answer": answer, "type": qtype,
                "derivation": derivation, "hops": int(hops),
            })

        pairs = sorted(edges)
        for a, b in pairs[:3]:
            cap, fid = edges[(a, b)]
            add_q(f"What is the capacity of the route from {name_of[a]} "
                  f"to {name_of[b]}?", str(cap), "lookup", [fid], 1)

        # Multi hop: a pair with exactly one intermediate hub and no direct
        # route has a unique relay answer.
        for a in hub_ids:
            for c in hub_ids:
                if a == c or (a, c) in edges:
                    continue
                mids = [b for b in hub_ids
                        if (a, b) in edges and (b, c) in edges]
                if len(mids) == 1:
                    b = mids[0]
                    add_q(f"Freight from {name_of[a]} to {name_of[c]} must "
                          "pass through which hub?",
                          name_of[b], "multi_hop",
                          [edges[(a, b)][1], edges[(b, c)][1]], 2)
                    break
            else:
                continue
            break

        return entities, list(Logistics.rules), facts, questions

    @staticmethod
    def sentence(fact, name_of, rng):
        tpl = _pick(rng, Logistics.TEMPLATES[fact["p"]])
        return tpl.format(s=name_of.get(fact["s"], fact["s"]),
                          o=name_of.get(fact["o"], fact["o"]),
                          c=fact.get("cap", 0))

    @staticmethod
    def corrupt(fact, entities, rng):
        wrong = dict(fact)
        # A contradictory route report misstates the capacity.
        cap = fact.get("cap", 50)
        delta = int(rng.integers(5, 40))
        wrong["cap"] = cap + delta if cap + delta < 100 else cap - delta
        return wrong

    @staticmethod
    def filler(entities, name_of, rng):
        hub = _other_entity(rng, entities, "hub", "")
        tpl = _pick(rng, Logistics.FILLER)
        return tpl.format(a=name_of[hub["id"]], t=int(rng.integers(0, 9)))


class Kinship:
    name = "kinship_temporal"
    rules = [
        "each recorded person has at most one recorded parent",
        "a grandparent is the parent of a parent",
    ]

    # Restated anchors: the child in parent_of (parent and grandparent
    # questions walk outward from the child), and the person in
    # born_in_year. Neither relation's templates borrow the other's
    # vocabulary, so the born/parent synonym folds stay disjoint.
    TEMPLATES = {
        "parent_of": [
            "{s} is the parent of {o}, and {o} grew up in the family home.",
            "Records list {o} as the child of {s}, naming {o} in the "
            "family register.",
            "{o} was raised by {s}, who brought {o} up at home.",
        ],
        "born_in_year": [
            "{s} was born in the year {o}; the entry for {s} is preserved.",
            "The registry gives {o} as the birth year of {s}, in the "
            "file kept under {s}.",
            "{s}'s recorded year of birth is {o}, per the ledger page "
            "for {s}.",
        ],
    }

    FILLER = [
        "{a} moved to a nearby village in {t}.",
        "A letter from {a} survives from the year {t}.",
        "{a} attended the harvest festival of {t}.",
    ]

    @staticmethod
    def generate(rng):
        n_chains = int(rng.integers(2, 4))
        entities = []
        facts = []

        def add_fact(s, p, o, t):
            fid = f"f{len(facts) + 1}"
            facts.append({"id": fid, "s": s, "p": p, "o": o, "t": int(t)})
            return fid

        chains = []
        used = set()
        for _ in range(n_chains):
            people = []
            while len(people) < 3:
                name = names.person_name(rng)
                if name not in used:
                    used.add(name)
                    people.append(name)
            base_year = int(rng.integers(1800, 1950))
            ids = []
            years = []
            for gen, name in enumerate(people):
                eid = f"e{len(entities) + 1}"
                entities.append({"id": eid, "type": "person", "name": name})
                year = base_year + gen * int(rng.integers(18, 35))
                ids.append(eid)
                years.append(year)
            born = [add_fact(ids[g], "born_in_year", str(years[g]), years[g])
                    for g in range(3)]
            parent = [add_fact(ids[g], "parent_of", ids[g + 1], years[g + 1])
                      for g in range(2)]
            chains.append({"ids": ids, "years": years, "born": born,
                           "parent": parent})

        name_of = {e["id"]: e["name"] for e in entities}
        questions = []

        def add_q(text, answer, qtype, derivation, hops):
            qid = f"q{len(questions) + 1}"
            questions.append({
                "qid": qid, "text": text, "answer": answer, "type": qtype,
                "derivation": derivation, "hops": int(hops),
            })

        for chain in chains:
            g = int(rng.integers(0, 3))
            add_q(f"In what year was {name_of[chain['ids'][g]]} born?",
                  str(chain["years"][g]), "lookup", [chain["born"][g]], 1)
        chain = chains[0]
        add_q(f"Who is the parent of {name_of[chain['ids'][1]]}?",
              name_of[chain["ids"][0]], "lookup", [chain["parent"][0]], 1)
        chain = chains[-1]
        # The derivation walks outward from the questioned person: first the
        # fact naming their parent, then the fact naming that parent's parent.
        # Retrieval traces follow derivation order, and only the grandchild's
        # name is in the question, so the anchored fact must come first.
        add_q(f"Who is the grandparent of {name_of[chain['ids'][2]]}?",
              name_of[chain["ids"][0]], "multi_hop",
              [chain["parent"][1], chain["parent"][0]], 2)

        return entities, list(Kinship.rules), facts, questions

    @staticmethod
    def sentence(fact, name_of, rng):
        tpl = _pick(rng, Kinship.TEMPLATES[fact["p"]])
        return tpl.format(s=name_of.get(fact["s"], fact["s"]),
                          o=name_of.get(fact["o"], fact["o"]))

    @staticmethod
    def corrupt(fact, entities, rng):
        wrong = dict(fact)
        if fact["p"] == "born_in_year":
            wrong["o"] = str(int(fact["o"]) + int(rng.integers(1, 15)))
            return wrong
        other = _other_entity(rng, entities, "person", fact["o"])
        if other is None or other["id"] == fact["s"]:
            return None
        wrong["o"] = other["id"]
        return wrong

    @staticmethod
    def filler(entities, name_of, rng):
        person = _other_entity(rng, entities, "person", "")
        tpl = _pick(rng, Kinship.FILLER)
        return tpl.format(a=name_of[person["id"]],
                          t=1800 + int(rng.integers(0, 150)))


DOMAINS = {d.name: d for d in (Corporate, Regulatory, Logistics, Kinship)}
DOMAIN_ORDER = [Corporate.name, Regulatory.name, Logistics.name, Kinship.name]
