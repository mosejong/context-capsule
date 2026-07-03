from app.adapters.llm_provider_adapter import LLMUsage
from scripts.compare_raw_vs_capsule import (
    build_raw_context,
    calc_cost,
    configure_repos,
    default_output_path,
    max_pts,
    parse_args,
    render_repo_model_summary,
    safe_error_message,
    score,
    score_pts,
    short_model_name,
)


def test_score_accepts_korean_synonyms_for_expected_keys():
    result = score(
        "정확도 98.08%이고, 재시도 로직과 배포 설정, 마이그레이션 파일을 확인했습니다.",
        {
            "98.08": True,
            "accuracy": True,
            "retry": True,
            "deploy": True,
            "migration": True,
        },
    )

    assert all(result.values())


def test_score_rewards_absent_wrong_answer():
    result = score(
        "정확도는 98.08%입니다. qa_defense 문서와 accuracy 값을 확인했습니다.",
        {"98.08": True, "qa_defense": True, "accuracy": True},
        wrong="98.6",
    )

    assert result["_wrong_answer"] is False
    assert score_pts(result) == 4
    assert max_pts(result) == 4


def test_score_does_not_reward_present_wrong_answer():
    result = score(
        "정확도 후보로 98.08%와 98.6%가 함께 보입니다.",
        {"98.08": True, "accuracy": True},
        wrong="98.6",
    )

    assert result["_wrong_answer"] is True
    assert score_pts(result) == 2
    assert max_pts(result) == 3


def test_configure_repos_keeps_large_raw_limited_to_first_anthropic_model():
    models = ["nvidia/nemotron-3-ultra-550b-a55b", "deepseek-ai/deepseek-v4-flash"]

    repos = configure_repos(models, "anthropic")

    assert repos["dummy"]["raw_vs_cc_models"] == models
    assert repos["procurement"]["raw_vs_cc_models"] == [models[0]]
    assert repos["procurement"]["cc_only_models"] == [models[1]]
    assert repos["rainbow"]["cc_only_models"] == models


def test_configure_repos_runs_procurement_raw_for_all_nvidia_models():
    models = ["nvidia/nemotron-3-ultra-550b-a55b", "deepseek-ai/deepseek-v4-flash"]

    repos = configure_repos(models, "nvidia")

    assert repos["dummy"]["raw_vs_cc_models"] == models
    assert repos["procurement"]["raw_vs_cc_models"] == models
    assert repos["procurement"]["cc_only_models"] == []
    assert repos["rainbow"]["raw_vs_cc_models"] == []
    assert repos["rainbow"]["cc_only_models"] == models


def test_provider_helpers_keep_nvidia_reports_separate():
    assert short_model_name("nvidia/nemotron-3-ultra-550b-a55b") == "nemotron-3-ultra-550b-a55b"
    assert short_model_name("claude-sonnet-4-6") == "sonnet"
    assert default_output_path("nvidia").name == "raw_vs_capsule_nvidia.md"


def test_calc_cost_returns_zero_without_provider_price_table():
    usage = LLMUsage(input_tokens=100, output_tokens=20)

    assert calc_cost(usage, "nvidia/nemotron-3-ultra-550b-a55b", {}) == 0.0


def test_build_raw_context_ignores_build_virtualenv(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    build_venv = repo / ".build-venv" / "Lib" / "site-packages"
    build_venv.mkdir(parents=True)
    (build_venv / "dependency.py").write_text("SHOULD_NOT_APPEAR = True\n", encoding="utf-8")

    context = build_raw_context(repo)

    assert "README.md" in context
    assert "SHOULD_NOT_APPEAR" not in context
    assert ".build-venv" not in context


def test_parse_args_supports_safe_smoke_limits(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "compare_raw_vs_capsule.py",
            "--provider",
            "nvidia",
            "--repos",
            "dummy",
            "--task-limit",
            "1",
            "--max-tokens",
            "128",
        ],
    )

    args = parse_args()

    assert args.provider == "nvidia"
    assert args.repos == ["dummy"]
    assert args.task_limit == 1
    assert args.max_tokens == 128


def test_render_repo_model_summary_uses_only_measured_rows():
    summary = render_repo_model_summary(
        [
            {
                "repo": "dummy-repo (소형 16파일)",
                "model": "nvidia/nemotron-3-ultra-550b-a55b",
                "raw_score": {"auth_service": True},
                "cc_score": {"auth_service": True},
                "reduction": 47.9,
            }
        ],
        repos=["dummy"],
        task_limit=1,
    )

    assert "Selected repos: dummy" in summary
    assert "Task limit per repo: 1" in summary
    assert "dummy-repo" in summary
    assert "nemotron-3-ultra-550b-a55b" in summary
    assert "procurement-logistics-ai" not in summary
    assert "rainbow-bridge" not in summary
    assert "Haiku | 0/9" not in summary


def test_safe_error_message_redacts_nvidia_api_key():
    error = RuntimeError("request failed with Authorization Bearer nvapi-abcdefghijklmnopqrstuvwxyz123456")

    message = safe_error_message(error)

    assert "nvapi-abcdefghijklmnopqrstuvwxyz123456" not in message
    assert "[REDACTED_SECRET]" in message
