from scripts.demo_user_speech import run_user_speech_demo
from tests.test_user_speech_indexed_retrieval import write_user_speech_repo


def test_user_speech_demo_returns_short_v012_story(tmp_path):
    repo = write_user_speech_repo(tmp_path)

    results = run_user_speech_demo(repo)

    assert [result["name"] for result in results] == [
        "readme_short",
        "simple_retriever_colloquial",
        "protect_auth_docs_only",
        "ambiguous_this",
    ]
    assert all(result["verdict"] == "PASS" for result in results)
    assert "README.md" in results[0]["top_paths"][:3]
    assert "app/retrievers/simple_retriever.py" in results[1]["top_paths"][:3]
    assert "auth" in results[2]["protected_hints"]
    assert results[3]["retrieval_used_mode"] == "clarification_only"
