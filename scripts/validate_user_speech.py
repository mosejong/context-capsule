from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.retrievers.persistent_index import build_retrieval_index
from app.scanners.repo_scanner import scan_repo
from app.schemas.capsule_schema import RetrievalMode
from app.services.capsule_service import generate_capsule_result

REPORT_PATH = Path("docs/reports/user_speech_retrieval_qa.md")


@dataclass(frozen=True)
class UserSpeechCase:
    name: str
    task: str
    expected_paths: tuple[str, ...] = ()
    expected_intent: str | None = None
    top_limit: int = 5
    min_hits: int = 1
    protected_hints: tuple[str, ...] = ()
    forbidden_paths: tuple[str, ...] = ()
    expect_clarification: bool = False


@dataclass(frozen=True)
class UserSpeechResult:
    name: str
    task: str
    verdict: str
    expected_paths: list[str]
    intent: str
    confidence: str
    hit_at_1: bool
    hit_at_3: bool
    irrelevant_count: int
    protected_false_positive: bool
    clarification_correct: bool
    protected_hints: list[str]
    retrieval_used_mode: str
    retrieval_fallback_reason: str | None
    baseline_context_scope: str
    top_paths: list[str]
    notes: list[str]


def user_speech_cases() -> list[UserSpeechCase]:
    return [
        UserSpeechCase(
            name="readme_short",
            task="리드미 손보자",
            expected_paths=("README.md",),
            top_limit=3,
        ),
        UserSpeechCase(
            name="readme_portfolio",
            task="README 포폴용으로 다듬자",
            expected_paths=("README.md",),
            top_limit=3,
        ),
        UserSpeechCase(
            name="readme_cleanup",
            task="README 정리해줘",
            expected_paths=("README.md",),
            top_limit=3,
        ),
        UserSpeechCase(
            name="readme_ko_alias",
            task="리드미 포트폴리오 느낌으로",
            expected_paths=("README.md",),
            top_limit=3,
        ),
        UserSpeechCase(
            name="docs_summary",
            task="문서 설명 정리하자",
            expected_paths=("README.md",),
            top_limit=5,
        ),
        UserSpeechCase(
            name="docs_portfolio",
            task="포폴 문서 다듬기",
            expected_paths=("README.md",),
            top_limit=5,
        ),
        UserSpeechCase(
            name="simple_retriever_colloquial",
            task="심플 리트리버 왜 이럼",
            expected_paths=("app/retrievers/simple_retriever.py",),
            top_limit=3,
        ),
        UserSpeechCase(
            name="simple_retriever_vector",
            task="simple_retriever에 벡터 검색 추가",
            expected_paths=("app/retrievers/simple_retriever.py",),
            top_limit=3,
        ),
        UserSpeechCase(
            name="retriever_ranking_bug",
            task="리트리버 랭킹 왜 이럼",
            expected_paths=("app/retrievers/simple_retriever.py",),
            top_limit=3,
        ),
        UserSpeechCase(
            name="retriever_search_quality",
            task="검색 품질 개선하자",
            expected_paths=("app/retrievers/simple_retriever.py",),
            top_limit=3,
        ),
        UserSpeechCase(
            name="retriever_score_suspicious",
            task="retriever 점수 이상함",
            expected_paths=("app/retrievers/simple_retriever.py",),
            top_limit=3,
        ),
        UserSpeechCase(
            name="retriever_test_hint",
            task="simple retriever 테스트 봐줘",
            expected_paths=("app/retrievers/simple_retriever.py",),
            top_limit=3,
        ),
        UserSpeechCase(
            name="github_issue_bug",
            task="깃헙 이슈 생성 안됨",
            expected_paths=("app/cli.py", "app/adapters/github_issue_adapter.py"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="github_issue_dry_run",
            task="create-issue dry-run 안됨",
            expected_paths=("app/cli.py", "app/adapters/github_issue_adapter.py"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="github_issue_payload",
            task="GitHub issue payload 이상함",
            expected_paths=("app/cli.py", "app/adapters/github_issue_adapter.py"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="github_issue_adapter",
            task="깃허브 이슈 어댑터 봐줘",
            expected_paths=("app/cli.py", "app/adapters/github_issue_adapter.py"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="github_issue_skip_labels",
            task="이슈 생성 skip-labels 옵션 확인",
            expected_paths=("app/cli.py", "app/adapters/github_issue_adapter.py"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="github_issue_command_error",
            task="issue 생성 명령 에러",
            expected_paths=("app/cli.py", "app/adapters/github_issue_adapter.py"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="local_launcher_bug",
            task="로컬 실행 안돼",
            expected_paths=("run_context_capsule.bat", "scripts/run_dashboard.ps1", "docs/local_app.md"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="local_dashboard_bug",
            task="대시보드 실행 안됨",
            expected_paths=("run_context_capsule.bat", "scripts/run_dashboard.ps1", "docs/local_app.md"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="local_run_dashboard_error",
            task="run_dashboard 에러",
            expected_paths=("run_context_capsule.bat", "scripts/run_dashboard.ps1", "docs/local_app.md"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="local_bat_bug",
            task="bat 실행 안돼",
            expected_paths=("run_context_capsule.bat", "scripts/run_dashboard.ps1", "docs/local_app.md"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="local_streamlit_bug",
            task="streamlit 대시보드 안 열림",
            expected_paths=("scripts/run_dashboard.ps1", "docs/local_app.md", "app/main.py"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="local_port_bug",
            task="localhost 8501 안떠",
            expected_paths=("run_context_capsule.bat", "scripts/run_dashboard.ps1", "docs/local_app.md"),
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="token_metric_suspicious",
            task="토큰 계산 뻥튀기 같은데?",
            expected_paths=("app/analyzers/token_analyzer.py", "docs/reports/performance_comparison.md"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="token_budget_bug",
            task="token budget 이상해",
            expected_paths=("app/analyzers/token_analyzer.py", "docs/reports/performance_comparison.md"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="token_reduction_suspicious",
            task="토큰 절감률 이상함",
            expected_paths=("app/analyzers/token_analyzer.py", "docs/reports/performance_comparison.md"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="token_usage_check",
            task="토큰 사용량 계산 다시 봐",
            expected_paths=("app/analyzers/token_analyzer.py", "docs/reports/performance_comparison.md"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="performance_report_check",
            task="성능 리포트 수치 확인",
            expected_paths=("scripts/generate_performance_report.py", "docs/reports/performance_comparison.md"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="token_analyzer_adapter_hint",
            task="token analyzer 연결부 봐줘",
            expected_paths=("app/analyzers/token_analyzer.py", "docs/reports/performance_comparison.md"),
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="output_copy",
            task="출력 문구 바꾸자",
            expected_paths=("app/generators/capsule_generator.py", "app/generators/output_writer.py", "app/main.py"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="ai_handoff_copy",
            task="AI handoff 문구 수정",
            expected_paths=("app/generators/capsule_generator.py", "app/generators/output_writer.py", "app/main.py"),
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="github_issue_output_copy",
            task="GITHUB_ISSUE.md 출력 이상함",
            expected_paths=("app/generators/capsule_generator.py", "app/generators/output_writer.py", "app/main.py"),
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="metadata_output",
            task="metadata 저장 출력 확인",
            expected_paths=("app/generators/capsule_generator.py", "app/generators/output_writer.py", "app/main.py"),
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="teammate_brief_copy",
            task="팀원 브리프 출력 문구 다듬자",
            expected_paths=("app/generators/capsule_generator.py", "app/generators/output_writer.py", "app/main.py"),
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="scrum_notes",
            task="스크럼 회의록 정리",
            expected_paths=("app/analyzers/meeting_analyzer.py",),
            top_limit=3,
        ),
        UserSpeechCase(
            name="meeting_next_actions",
            task="회의록에서 다음 작업 뽑아줘",
            expected_paths=("app/analyzers/meeting_analyzer.py",),
            top_limit=3,
        ),
        UserSpeechCase(
            name="kickoff_scope",
            task="프로젝트 착수 정리",
            expected_paths=("app/analyzers/meeting_analyzer.py",),
            top_limit=3,
        ),
        UserSpeechCase(
            name="kickoff_mvp",
            task="킥오프 MVP 범위 잡자",
            expected_paths=("app/analyzers/meeting_analyzer.py",),
            top_limit=3,
        ),
        UserSpeechCase(
            name="kickoff_contest_checklist",
            task="프로젝트 착수 제출 체크리스트 만들자",
            expected_paths=("app/analyzers/meeting_analyzer.py",),
            top_limit=3,
        ),
        UserSpeechCase(
            name="ram_colab_issue",
            task="코랩인데 자꾸 램 터져서 못하겠음",
            expected_intent="runtime_environment_issue",
        ),
        UserSpeechCase(
            name="image_black_screen",
            task="배경이미지가 검은색으로 나와요",
            expected_intent="media_render_bug",
        ),
        UserSpeechCase(
            name="generated_but_not_saved",
            task="생성됐다고 나오는데 저장이 안돼요",
            expected_paths=("app/generators/output_writer.py", "app/main.py", "docs/local_app.md"),
            expected_intent="file_output_bug",
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="check_save_path",
            task="저장 경로 한번 확인해줘",
            expected_paths=("app/generators/output_writer.py", "app/main.py", "docs/local_app.md"),
            expected_intent="file_output_bug",
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="missing_log",
            task="로그가 없는 건 이상한데 봐줘",
            expected_paths=("app/generators/output_writer.py", "app/cli.py", "app/main.py"),
            expected_intent="logging_issue",
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="timeout_generation",
            task="timeout 걸려서 생성이 안됨",
            expected_intent="timeout_issue",
        ),
        UserSpeechCase(
            name="increase_timeout",
            task="timeout 시간 늘려서 다시 테스트하자",
            expected_intent="timeout_issue",
        ),
        UserSpeechCase(
            name="script_review",
            task="대본 완성했는데 확인해줘",
            expected_paths=("app/analyzers/meeting_analyzer.py", "docs/v0.2_scrum_kickoff_modes.md"),
            expected_intent="presentation_review",
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="add_eval_report",
            task="평가 리포트 부분 추가해야 함",
            expected_paths=("app/analyzers/meeting_analyzer.py", "docs/v0.2_scrum_kickoff_modes.md"),
            expected_intent="presentation_review",
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="presentation_feedback",
            task="발표 내용 피드백 보고 수정하자",
            expected_paths=("app/analyzers/meeting_analyzer.py", "docs/v0.2_scrum_kickoff_modes.md"),
            expected_intent="presentation_review",
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="demo_video_saved",
            task="시연영상 저장되는지 봐줘",
            expected_paths=("app/generators/output_writer.py", "app/main.py", "docs/local_app.md"),
            expected_intent="file_output_bug",
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="zoom_audio_low",
            task="소리 조금만 키워주세요",
            expected_paths=("app/analyzers/meeting_analyzer.py", "docs/v0.2_scrum_kickoff_modes.md"),
            expected_intent="presentation_environment_issue",
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="share_audio_missing",
            task="화면공유 소리 안 나와요",
            expected_paths=("app/analyzers/meeting_analyzer.py", "docs/v0.2_scrum_kickoff_modes.md"),
            expected_intent="presentation_environment_issue",
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="ppt_script_mismatch",
            task="ppt랑 대본이랑 안 맞아요",
            expected_paths=("app/analyzers/meeting_analyzer.py", "docs/v0.2_scrum_kickoff_modes.md"),
            expected_intent="presentation_review",
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="slide_page_edit",
            task="ppt 22페이지 사진 제거하고 이미지 추가",
            expected_paths=("app/analyzers/meeting_analyzer.py", "docs/v0.2_scrum_kickoff_modes.md"),
            expected_intent="media_render_bug",
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="presentation_polish",
            task="이거 발표용으로 바꿔줘",
            expected_paths=("app/analyzers/meeting_analyzer.py", "docs/v0.2_scrum_kickoff_modes.md"),
            expected_intent="presentation_review",
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="vague_this_bug",
            task="이거 왜 안됨?",
            expect_clarification=True,
        ),
        UserSpeechCase(
            name="continue_previous_chat",
            task="아까 하던 거 이어서 하자",
            expect_clarification=True,
        ),
        UserSpeechCase(
            name="task_offer",
            task="해야 할 거 있으면 말해주세요",
            expected_paths=("app/analyzers/meeting_analyzer.py", "docs/v0.2_scrum_kickoff_modes.md"),
            expected_intent="team_coordination",
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="rehearsal_schedule",
            task="내일 아침에 대본 맞춰보자",
            expected_paths=("app/analyzers/meeting_analyzer.py", "docs/v0.2_scrum_kickoff_modes.md"),
            expected_intent="presentation_review",
            top_limit=5,
            min_hits=1,
        ),
        UserSpeechCase(
            name="protect_auth_docs_only",
            task="auth는 건드리지 말고 문서만 바꾸자",
            expected_paths=("README.md",),
            top_limit=5,
            protected_hints=("auth",),
            forbidden_paths=("app/auth.py",),
        ),
        UserSpeechCase(
            name="protect_db_output_copy",
            task="DB쪽은 냅두고 출력 문구만 바꾸자",
            expected_paths=("app/generators/capsule_generator.py", "app/generators/output_writer.py", "app/main.py"),
            top_limit=5,
            protected_hints=("db",),
            forbidden_paths=("app/models/user.py",),
        ),
        UserSpeechCase(
            name="protect_jwt_readme",
            task="JWT는 건드리지 말고 README만 고치자",
            expected_paths=("README.md",),
            top_limit=5,
            protected_hints=("auth",),
            forbidden_paths=("app/auth.py",),
        ),
        UserSpeechCase(
            name="protect_secret_token_report",
            task="secret 건드리지 말고 토큰 리포트만 봐줘",
            expected_paths=("app/analyzers/token_analyzer.py", "docs/reports/performance_comparison.md"),
            top_limit=5,
            min_hits=1,
            protected_hints=("secret",),
        ),
        UserSpeechCase(
            name="protect_env_local",
            task=".env는 빼고 로컬 실행만 봐줘",
            expected_paths=("run_context_capsule.bat", "scripts/run_dashboard.ps1", "docs/local_app.md"),
            top_limit=5,
            min_hits=2,
            protected_hints=("secret",),
        ),
        UserSpeechCase(
            name="protect_deploy_docs",
            task="deploy는 제외하고 문서만 정리",
            expected_paths=("README.md",),
            top_limit=5,
            protected_hints=("deploy",),
        ),
        UserSpeechCase(
            name="protect_db_output",
            task="DB schema는 냅두고 출력만 수정",
            expected_paths=("app/generators/capsule_generator.py", "app/generators/output_writer.py", "app/main.py"),
            top_limit=5,
            min_hits=2,
            protected_hints=("db",),
            forbidden_paths=("app/models/user.py",),
        ),
        UserSpeechCase(
            name="ambiguous_this",
            task="이거 왜그래?",
            expect_clarification=True,
        ),
        UserSpeechCase(
            name="ambiguous_previous",
            task="아까 그거 이어서 하자",
            expect_clarification=True,
        ),
        UserSpeechCase(
            name="ambiguous_that",
            task="저거 왜그래?",
            expect_clarification=True,
        ),
        UserSpeechCase(
            name="ambiguous_do_that",
            task="그거 해줘",
            expect_clarification=True,
        ),
        UserSpeechCase(
            name="ambiguous_touch_this",
            task="이거 손보자",
            expect_clarification=True,
        ),
        UserSpeechCase(
            name="ambiguous_continue",
            task="아까 이어서",
            expect_clarification=True,
        ),
    ]


def evaluate_case(repo_path: Path, case: UserSpeechCase) -> UserSpeechResult:
    result = generate_capsule_result(
        repo_path=repo_path,
        task_request=case.task,
        retriever_mode=RetrievalMode.INDEXED,
    )
    capsule = result.capsule
    understanding = capsule.request_understanding
    top_paths = [chunk.path for chunk in capsule.relevant_chunks[: case.top_limit]]
    notes: list[str] = []

    if case.expect_clarification:
        if not understanding.needs_clarification:
            notes.append("expected clarification, but request proceeded")
        if capsule.retrieval_report.used_mode != "clarification_only":
            notes.append(f"expected clarification_only, got {capsule.retrieval_report.used_mode}")
        if capsule.relevant_chunks:
            notes.append("expected no retrieved chunks")
        verdict = "PASS" if not notes else "FAIL"
        return build_result(case, capsule, top_paths, verdict, notes)

    if case.expected_intent and understanding.intent != case.expected_intent:
        notes.append(f"expected intent {case.expected_intent}, got {understanding.intent}")

    hits = sorted(path for path in case.expected_paths if path in top_paths)
    if case.expected_paths and len(hits) < case.min_hits:
        notes.append(f"expected at least {case.min_hits} hit(s), got {hits or 'none'}")

    missing_protected = [hint for hint in case.protected_hints if hint not in understanding.protected_hints]
    if missing_protected:
        notes.append(f"missing protected hint(s): {', '.join(missing_protected)}")

    forbidden_hits = [path for path in case.forbidden_paths if path in top_paths]
    if forbidden_hits:
        notes.append(f"forbidden path(s) retrieved: {', '.join(forbidden_hits)}")

    if capsule.retrieval_report.used_mode != "indexed":
        notes.append(f"indexed fallback used: {capsule.retrieval_report.fallback_reason}")

    if capsule.token_budget.baseline_context_scope != "retrieved_file_contents":
        notes.append(f"unexpected baseline scope: {capsule.token_budget.baseline_context_scope}")

    if not notes:
        verdict = "PASS"
    elif hits:
        verdict = "WARN"
    else:
        verdict = "FAIL"
    return build_result(case, capsule, top_paths, verdict, notes)


def build_result(case, capsule, top_paths, verdict: str, notes: list[str]) -> UserSpeechResult:
    understanding = capsule.request_understanding
    expected_paths = list(case.expected_paths)
    hit_at_1 = bool(expected_paths and top_paths and top_paths[0] in expected_paths)
    hit_at_3 = bool(expected_paths and set(top_paths[:3]) & set(expected_paths))
    irrelevant_count = len([path for path in top_paths if path not in expected_paths]) if expected_paths else 0
    protected_false_positive = bool(case.forbidden_paths and set(top_paths) & set(case.forbidden_paths))
    clarification_correct = bool(case.expect_clarification and understanding.needs_clarification and not top_paths)
    return UserSpeechResult(
        name=case.name,
        task=case.task,
        verdict=verdict,
        expected_paths=expected_paths,
        intent=understanding.intent,
        confidence=understanding.confidence_label,
        hit_at_1=hit_at_1,
        hit_at_3=hit_at_3,
        irrelevant_count=irrelevant_count,
        protected_false_positive=protected_false_positive,
        clarification_correct=clarification_correct,
        protected_hints=understanding.protected_hints,
        retrieval_used_mode=capsule.retrieval_report.used_mode,
        retrieval_fallback_reason=capsule.retrieval_report.fallback_reason,
        baseline_context_scope=capsule.token_budget.baseline_context_scope,
        top_paths=top_paths,
        notes=notes,
    )


def run_validation(repo_path: Path) -> list[UserSpeechResult]:
    files = scan_repo(repo_path)
    build_retrieval_index(files, repo_path)
    return [evaluate_case(repo_path, case) for case in user_speech_cases()]


def build_markdown(results: list[UserSpeechResult], repo_label: str) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pass_count = sum(1 for result in results if result.verdict == "PASS")
    warn_count = sum(1 for result in results if result.verdict == "WARN")
    fail_count = sum(1 for result in results if result.verdict == "FAIL")
    target_results = [result for result in results if result.expected_paths]
    clarification_results = [result for result in results if result.retrieval_used_mode == "clarification_only"]
    hit_at_1_count = sum(1 for result in target_results if result.hit_at_1)
    hit_at_3_count = sum(1 for result in target_results if result.hit_at_3)
    protected_false_positive_count = sum(1 for result in results if result.protected_false_positive)
    clarification_correct_count = sum(1 for result in clarification_results if result.clarification_correct)
    avg_irrelevant = (
        sum(result.irrelevant_count for result in target_results) / len(target_results)
        if target_results
        else 0
    )
    rows = [
        "| Case | Verdict | Intent | hit@1 | hit@3 | Irrelevant | Protected | Retrieval | Baseline | Top Paths | Notes |",
        "| --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for result in results:
        rows.append(
            "| "
            f"{escape_markdown(result.name)} | "
            f"{result.verdict} | "
            f"{escape_markdown(result.intent)} / {escape_markdown(result.confidence)} | "
            f"{format_bool(result.hit_at_1)} | "
            f"{format_bool(result.hit_at_3)} | "
            f"{result.irrelevant_count} | "
            f"{escape_markdown(', '.join(result.protected_hints) or 'None')} | "
            f"{escape_markdown(result.retrieval_used_mode)} | "
            f"{escape_markdown(result.baseline_context_scope)} | "
            f"{escape_markdown(', '.join(result.top_paths) or 'None')} | "
            f"{escape_markdown('; '.join(result.notes) or 'OK')} |"
        )

    return f"""# User-Speech Retrieval QA

Generated at: {generated_at}

Repository path: `{repo_label}`

This report validates real Korean colloquial requests against indexed retrieval.

## Summary

- Cases: {len(results)}
- PASS: {pass_count}
- WARN: {warn_count}
- FAIL: {fail_count}
- Target cases: {len(target_results)}
- hit@1: {hit_at_1_count}/{len(target_results)}
- hit@3: {hit_at_3_count}/{len(target_results)}
- Average irrelevant top-path count: {avg_irrelevant:.2f}
- Protected false positives: {protected_false_positive_count}
- Clarification accuracy: {clarification_correct_count}/{len(clarification_results)}

## What Is Checked

- request understanding intent and confidence
- protected hints such as `auth` and `db`
- indexed retrieval usage and visible fallback
- target file hit@1 and hit@3
- irrelevant retrieved path count
- protected false positives
- clarification-only accuracy
- ambiguous requests stop with one clarification question
- token baseline scope is not whole-repo concat

## Results

{chr(10).join(rows)}

## How To Regenerate

```powershell
.\\.venv\\Scripts\\python.exe scripts\\validate_user_speech.py --repo-path .
```
"""


def escape_markdown(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def format_bool(value: bool) -> str:
    return "yes" if value else "no"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate real user-speech requests against indexed retrieval.")
    parser.add_argument("--repo-path", type=Path, default=Path("."), help="Repository path to scan and index.")
    parser.add_argument("--output", type=Path, default=REPORT_PATH, help="Markdown report output path.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    args = parser.parse_args()

    repo_path = args.repo_path.resolve()
    results = run_validation(repo_path)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_markdown(results, str(args.repo_path)), encoding="utf-8")

    if args.json:
        print(json.dumps([asdict(result) for result in results], ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(f"{result.verdict} {result.name}: {', '.join(result.top_paths) or 'no retrieval'}")
        print(f"wrote {args.output}")

    if any(result.verdict == "FAIL" for result in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
