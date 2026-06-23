from app.retrievers.persistent_index import build_retrieval_index, retrieve_indexed_chunks
from app.schemas.capsule_schema import FileKind, RepoFile


def sample_files():
    return [
        RepoFile(path="README.md", kind=FileKind.DOC, content="# Demo\nProject guide", size=20),
        RepoFile(path="app/retrievers/simple_retriever.py", kind=FileKind.CODE, content="vector search retrieval", size=23),
        RepoFile(path="docs/notes.md", kind=FileKind.DOC, content="unrelated notes", size=15),
    ]


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
