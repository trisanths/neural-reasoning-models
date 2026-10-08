import re

from src.mathgen import exercises, textbook, theory

SEEDS = list(range(10))


def _books():
    for seed in SEEDS:
        th = theory.build(seed)
        exs = exercises.build_exercises(th)
        yield th, exs, textbook.build_textbook(th, exs)


def test_determinism_by_seed():
    for seed in SEEDS[:4]:
        th = theory.build(seed)
        a = textbook.to_markdown(textbook.build_textbook(th, exercises.build_exercises(th)))
        th = theory.build(seed)
        b = textbook.to_markdown(textbook.build_textbook(th, exercises.build_exercises(th)))
        assert a == b


def test_page_count_lands_in_the_target_band():
    for _th, _ex, book in _books():
        assert 20 <= book.pages() <= 60, f"{book.pages()} pages"


def test_every_chapter_carries_every_section_slot():
    for _th, _ex, book in _books():
        for chapter in book.chapters:
            kinds = [s.kind for s in chapter.sections]
            for required in textbook.SECTION_ORDER:
                assert required in kinds, f"chapter {chapter.number} lacks {required}"
            assert all(s.text.strip() for s in chapter.sections)


def test_chapters_cover_every_theory_node_exactly_once():
    for th, _ex, book in _books():
        seen = [nid for c in book.chapters for nid in c.node_ids]
        assert sorted(seen) == sorted(th.order)


def test_registers_vary_across_a_book():
    for _th, _ex, book in _books():
        used = {c.register for c in book.chapters}
        assert len(used) >= 3, f"only {used}"
        assert used <= set(textbook.REGISTERS)


def test_worked_examples_recompute():
    for th, _ex, book in _books():
        s = th.structure
        found = 0
        for chapter in book.chapters:
            for record in chapter.worked_examples:
                if record["kind"] == "evaluate":
                    assert s.evaluate(record["expression"]) == record["value"]
                    assert s.eval_trace(record["expression"]) == record["steps"]
                    found += 1
        assert found >= len(book.chapters)


def test_the_tables_printed_agree_with_the_structure():
    for th, _ex, book in _books():
        s = th.structure
        table_section = next(sec for sec in book.chapters[0].sections
                             if sec.kind == "tables")
        for i in range(s.size):
            for j in range(s.size):
                assert s.name(s.op(0, i, j)) in table_section.text
        assert s.op_glyphs[0] in table_section.text
        assert s.rel_glyph in table_section.text


def test_exercise_prompts_appear_and_answers_do_not():
    for _th, exs, book in _books():
        md = textbook.to_markdown(book)
        placed = [e for e in exs if e.prompt in md]
        assert len(placed) == len(exs), "every exercise should be printed"
        for e in exs:
            body = md[:md.index(e.prompt)] + md[md.index(e.prompt) + len(e.prompt):]
            assert f"{e.exercise_id}. {e.answer}" not in body


def test_chunks_carry_the_metadata_a_retriever_needs():
    for _th, _ex, book in _books():
        cs = textbook.chunks(book)
        assert len(cs) >= 60
        ids = [c["chunk_id"] for c in cs]
        assert len(set(ids)) == len(ids)
        for c in cs:
            assert c["text"].strip()
            assert c["section_kind"]
            assert c["chapter"] >= -1
            assert c["words"] == len(c["text"].split())
            assert c["system"] == book.theory.structure.system_name


def test_chunks_respect_the_word_budget():
    for _th, _ex, book in _books():
        for c in textbook.chunks(book, max_words=200):
            assert c["words"] <= 200 + 1


def test_chunks_reassemble_into_the_sections_they_came_from():
    _th, _ex, book = next(_books())
    cs = textbook.chunks(book)
    for chapter in book.chapters:
        for section in chapter.sections:
            parts = [c for c in cs if c["chapter"] == chapter.number
                     and c["section_kind"] == section.kind]
            joined = " ".join(p["text"] for p in sorted(parts, key=lambda p: p["part"]))
            assert joined.split() == section.text.split()


def test_worked_example_lines_survive_wrapping():
    """Reflowing a step by step example destroys it, so indented lines stay put."""
    for _th, _ex, book in _books():
        for chapter in book.chapters:
            section = next(s for s in chapter.sections if s.kind == "example")
            assert any(line.startswith("    ") for line in section.text.split("\n"))


def test_no_placeholder_or_unfilled_text_escapes():
    """Braces do appear, as set notation. An unfilled format field must not.

    A single letter in braces is [x] style set notation the textbook uses on
    purpose; anything longer, or anything with a dot or a bracket inside, is a
    format string that never got substituted.
    """
    placeholder = re.compile(r"\{[a-z_][a-z_0-9]+[}.\[]")
    for _th, _ex, book in _books():
        md = textbook.to_markdown(book)
        found = placeholder.search(md)
        assert not found, f"unfilled placeholder {found.group(0)!r}"
        # "None of these images" is prose; a leaked Python None lands
        # mid sentence, right after a lower case word.
        leaked = re.search(r"(?<=[a-z] )None\b", md)
        assert not leaked, "a Python None reached the page"
        assert not re.search(r"\bTODO\b", md)
        assert "  ." not in md


def test_prose_uses_the_invented_vocabulary():
    for th, _ex, book in _books():
        md = textbook.to_markdown(book)
        assert th.structure.object_plural in md
        for element in th.structure.elements:
            assert element in md
        for notion in th.notion_names.values():
            if any(notion in n.title for n in th.nodes.values()):
                assert notion in md
