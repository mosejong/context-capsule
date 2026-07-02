from app.retrievers.hybrid_retriever import retrieve_hybrid_chunks
from app.schemas.capsule_schema import FileKind, RepoFile


class FakeEmbeddingProvider:
    name = "fake"

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        lower = text.lower()
        if "payment outage" in lower or "billing handler" in lower:
            return [1.0, 0.0, 0.0]
        if "unrelated" in lower:
            return [0.0, 1.0, 0.0]
        return [0.0, 0.0, 1.0]


class RecordingEmbeddingProvider:
    def __init__(self, name: str) -> None:
        self.name = name
        self.calls: list[list[str]] = []

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(texts)
        return [[1.0, 0.0, 0.0] for _ in texts]


def test_hybrid_retriever_can_rank_by_embedding_provider():
    files = [
        RepoFile(path="app/billing.py", kind=FileKind.CODE, content="billing handler accepts cards", size=29),
        RepoFile(path="docs/unrelated.md", kind=FileKind.DOC, content="unrelated release notes", size=23),
    ]

    chunks = retrieve_hybrid_chunks(files, "payment outage", top_k=2, embedding_provider=FakeEmbeddingProvider())

    assert chunks[0].path == "app/billing.py"


def test_hybrid_retriever_keeps_mentioned_file_mandatory_first():
    files = [
        RepoFile(path="app/billing.py", kind=FileKind.CODE, content="billing handler accepts cards", size=29),
        RepoFile(path="README.md", kind=FileKind.DOC, content="payment outage demo docs", size=24),
    ]

    chunks = retrieve_hybrid_chunks(
        files,
        "README를 payment outage 데모용으로 정리해줘",
        top_k=2,
        embedding_provider=FakeEmbeddingProvider(),
    )

    assert chunks[0].path == "README.md"


def test_hybrid_retriever_falls_back_to_keyword_when_embedding_fails():
    class BrokenEmbeddingProvider:
        name = "broken"

        def embed(self, texts: list[str]) -> list[list[float]]:
            raise RuntimeError("embedding unavailable")

    files = [
        RepoFile(path="README.md", kind=FileKind.DOC, content="portfolio guide", size=15),
        RepoFile(path="app/main.py", kind=FileKind.CODE, content="portfolio guide", size=15),
    ]

    chunks = retrieve_hybrid_chunks(
        files,
        "README를 포트폴리오용으로 다듬어줘",
        top_k=2,
        embedding_provider=BrokenEmbeddingProvider(),
    )

    assert chunks[0].path == "README.md"


def test_hybrid_retriever_formats_multilingual_e5_inputs():
    provider = RecordingEmbeddingProvider("sentence_transformers:intfloat/multilingual-e5-large:input_e5_v1")
    files = [RepoFile(path="docs/payment.md", kind=FileKind.DOC, content="payment checkout docs", size=21)]

    retrieve_hybrid_chunks(files, "결제 실패 고쳐줘", top_k=1, embedding_provider=provider)

    assert provider.calls[0][0].startswith("query: ")
    assert provider.calls[1][0].startswith("passage: ")


def test_hybrid_retriever_formats_qwen3_query_only():
    provider = RecordingEmbeddingProvider("sentence_transformers:Qwen/Qwen3-Embedding-0.6B:input_qwen3_instruct_v1")
    files = [RepoFile(path="docs/payment.md", kind=FileKind.DOC, content="payment checkout docs", size=21)]

    retrieve_hybrid_chunks(files, "결제 실패 고쳐줘", top_k=1, embedding_provider=provider)

    assert provider.calls[0][0].startswith("Instruct: ")
    assert "\nQuery: 결제 실패 고쳐줘" in provider.calls[0][0]
    assert not provider.calls[1][0].startswith("Instruct: ")
