from app.retrievers.persistent_index import (
    build_retrieval_index,
    retrieve_indexed_chunks,
    retrieve_indexed_chunks_with_report,
)
from app.schemas.capsule_schema import FileKind, RepoFile


def sample_files():
    return [
        RepoFile(path="README.md", kind=FileKind.DOC, content="# Demo\nProject guide", size=20),
        RepoFile(path="app/retrievers/simple_retriever.py", kind=FileKind.CODE, content="vector search retrieval", size=23),
        RepoFile(path="docs/notes.md", kind=FileKind.DOC, content="unrelated notes", size=15),
    ]


class RecordingEmbeddingProvider:
    def __init__(self, name: str) -> None:
        self.name = name
        self.calls: list[list[str]] = []

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(texts)
        return [[1.0, 0.0, 0.0] for _ in texts]


def test_build_retrieval_index_writes_json(tmp_path):
    index_path = tmp_path / "index" / "retrieval_index.json"

    result = build_retrieval_index(sample_files(), repo_path=tmp_path, index_path=index_path)

    assert result.index_path == index_path
    assert result.file_count == 3
    assert result.chunk_count == 3
    assert index_path.exists()


def test_indexed_retriever_uses_persistent_index(tmp_path):
    files = sample_files()
    index_path = tmp_path / "index" / "retrieval_index.json"
    build_retrieval_index(files, repo_path=tmp_path, index_path=index_path)

    chunks = retrieve_indexed_chunks(
        files,
        "simple_retriever에 벡터 검색을 추가",
        repo_path=tmp_path,
        index_path=index_path,
        top_k=3,
    )

    assert chunks[0].path == "app/retrievers/simple_retriever.py"


def test_indexed_retriever_falls_back_when_index_is_stale(tmp_path):
    files = sample_files()
    index_path = tmp_path / "index" / "retrieval_index.json"
    build_retrieval_index(files, repo_path=tmp_path, index_path=index_path)
    changed_files = [
        RepoFile(path="README.md", kind=FileKind.DOC, content="# Demo\nChanged guide", size=20),
        *files[1:],
    ]

    chunks = retrieve_indexed_chunks(
        changed_files,
        "README를 포트폴리오용으로 다듬어줘",
        repo_path=tmp_path,
        index_path=index_path,
        top_k=3,
    )

    assert chunks[0].path == "README.md"


def test_indexed_retriever_reports_stale_fallback(tmp_path):
    files = sample_files()
    index_path = tmp_path / "index" / "retrieval_index.json"
    build_retrieval_index(files, repo_path=tmp_path, index_path=index_path)
    changed_files = [
        RepoFile(path="README.md", kind=FileKind.DOC, content="# Demo\nChanged guide", size=20),
        *files[1:],
    ]

    result = retrieve_indexed_chunks_with_report(
        changed_files,
        "README를 포트폴리오용으로 다듬어줘",
        repo_path=tmp_path,
        index_path=index_path,
        top_k=3,
    )

    assert result.used_mode == "hybrid_fallback"
    assert result.fallback_reason == "retrieval index is stale"
    assert result.chunks[0].path == "README.md"


def test_indexed_retriever_uses_embedding_input_format_for_index_and_query(tmp_path):
    files = sample_files()
    index_path = tmp_path / "index" / "retrieval_index.json"
    provider = RecordingEmbeddingProvider("sentence_transformers:intfloat/multilingual-e5-large:input_e5_v1")

    build_retrieval_index(files, repo_path=tmp_path, index_path=index_path, embedding_provider=provider)
    retrieve_indexed_chunks(
        files,
        "리드미 손보자",
        repo_path=tmp_path,
        index_path=index_path,
        top_k=1,
        embedding_provider=provider,
    )

    assert provider.calls[0][0].startswith("passage: ")
    assert provider.calls[1][0].startswith("query: ")


def test_indexed_retriever_deprioritizes_release_notes_for_generic_docs_request(tmp_path):
    files = [
        RepoFile(path="README.md", kind=FileKind.DOC, content="# Project\n문서 설명", size=16),
        RepoFile(path="docs/README.md", kind=FileKind.DOC, content="# Docs\n문서 설명 정리", size=18),
        RepoFile(path="docs/releases/v0.2.8.md", kind=FileKind.DOC, content="# Release\n문서 설명 정리", size=18),
    ]
    index_path = tmp_path / "index" / "retrieval_index.json"
    provider = RecordingEmbeddingProvider("hash_local_v1")

    build_retrieval_index(files, repo_path=tmp_path, index_path=index_path, embedding_provider=provider)
    chunks = retrieve_indexed_chunks(
        files,
        "문서 설명 정리하자",
        repo_path=tmp_path,
        index_path=index_path,
        top_k=3,
        embedding_provider=provider,
    )
    paths = [chunk.path for chunk in chunks]

    assert paths[0] in {"README.md", "docs/README.md"}
    assert "docs/releases/v0.2.8.md" not in paths[:2]


def test_indexed_retriever_keeps_release_notes_for_release_request(tmp_path):
    files = [
        RepoFile(path="README.md", kind=FileKind.DOC, content="# Project\n문서 설명", size=16),
        RepoFile(path="docs/README.md", kind=FileKind.DOC, content="# Docs\n문서 설명 정리", size=18),
        RepoFile(path="docs/releases/v0.2.8.md", kind=FileKind.DOC, content="# Release\nrelease notes patch", size=25),
    ]
    index_path = tmp_path / "index" / "retrieval_index.json"
    provider = RecordingEmbeddingProvider("hash_local_v1")

    build_retrieval_index(files, repo_path=tmp_path, index_path=index_path, embedding_provider=provider)
    chunks = retrieve_indexed_chunks(
        files,
        "릴리즈 노트 정리",
        repo_path=tmp_path,
        index_path=index_path,
        top_k=3,
        embedding_provider=provider,
    )

    assert chunks[0].path == "docs/releases/v0.2.8.md"
