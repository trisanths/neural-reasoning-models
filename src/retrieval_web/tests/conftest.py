import pytest

from src.retrieval_web.exa import MOCK_FIXTURES
from src.train.tokenizer import load_tokenizer, train_tokenizer


@pytest.fixture(scope="session")
def tok(tmp_path_factory):
    """Small project tokenizer trained on the mock fixture prose, so chunk
    budgets in these tests are measured in realistic subword tokens."""
    base = tmp_path_factory.mktemp("webtok")
    corpus = base / "corpus.txt"
    with open(corpus, "w") as fh:
        for query, results in MOCK_FIXTURES.items():
            fh.write(query + "\n")
            for result in results:
                fh.write(result["title"] + "\n")
                fh.write(result["text"] + "\n")
    path = base / "tokenizer.json"
    train_tokenizer([str(corpus)], out_path=str(path), vocab_size=1024)
    return load_tokenizer(str(path))
