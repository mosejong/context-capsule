from __future__ import annotations

import re
from dataclasses import dataclass

from app.schemas.capsule_schema import RepoFile, RequestUnderstanding


@dataclass(frozen=True)
class AliasRule:
    patterns: tuple[str, ...]
    normalized: str
    file_hints: tuple[str, ...] = ()
    target_hints: tuple[str, ...] = ()
    intent: str | None = None


ALIAS_RULES = [
    AliasRule(
        patterns=("리드미", "readme", "포폴", "포트폴리오"),
        normalized="README.md documentation portfolio",
        file_hints=("README.md",),
        target_hints=("README.md",),
        intent="documentation_edit",
    ),
    AliasRule(
        patterns=(
            "깃헙 이슈",
            "깃허브 이슈",
            "github issue",
            "issue 생성",
            "issue 명령",
            "issue command",
            "issue error",
            "이슈 생성",
            "create-issue",
        ),
        normalized="GitHub issue create-issue",
        file_hints=("app/adapters/github_issue_adapter.py", "app/cli.py"),
        target_hints=("GitHub issue adapter",),
        intent="github_issue_bug_investigation",
    ),
    AliasRule(
        patterns=("심플 리트리버", "simple retriever", "simple_retriever", "retriever", "검색", "리트리버"),
        normalized="simple_retriever retrieval",
        file_hints=("app/retrievers/simple_retriever.py",),
        target_hints=("retriever",),
        intent="retrieval_change",
    ),
    AliasRule(
        patterns=(
            "로컬 실행",
            "대시보드 실행",
            "대시보드",
            "실행 안돼",
            "실행 안됨",
            "안 열림",
            "streamlit",
            "run_dashboard",
            "launcher",
            "localhost",
            "8501",
        ),
        normalized="local launcher dashboard run",
        file_hints=(
            "run_context_capsule.bat",
            "scripts/run_dashboard.ps1",
            "scripts/install_windows.ps1",
            "docker-compose.yml",
            "docs/local_app.md",
        ),
        target_hints=("local launcher",),
        intent="launcher_bug_investigation",
    ),
    AliasRule(
        patterns=(
            "토큰 계산",
            "토큰 뻥튀기",
            "토큰 절감",
            "토큰 사용량",
            "토큰 리포트",
            "성능 리포트",
            "performance report",
            "token analyzer",
            "token budget",
        ),
        normalized="token analyzer metric validation token budget",
        file_hints=(
            "app/analyzers/token_analyzer.py",
            "scripts/generate_performance_report.py",
            "docs/reports/performance_comparison.md",
        ),
        target_hints=("token budget",),
        intent="metric_validation",
    ),
    AliasRule(
        patterns=("코랩", "colab", "램 터", "ram", "gpu", "그래픽카드", "사양"),
        normalized="runtime environment resource memory gpu colab",
        target_hints=("runtime environment",),
        intent="runtime_environment_issue",
    ),
    AliasRule(
        patterns=("배경이미지", "검은색", "이미지", "렌더링", "render"),
        normalized="image render media pipeline",
        target_hints=("image render",),
        intent="media_render_bug",
    ),
    AliasRule(
        patterns=("저장 경로", "저장이 안", "저장 안", "저장되는지", "어디에도 저장", "output directory"),
        normalized="file output save path directory",
        file_hints=("app/generators/output_writer.py", "app/main.py", "docs/local_app.md"),
        target_hints=("file output path",),
        intent="file_output_bug",
    ),
    AliasRule(
        patterns=("로그가", "로그 안", "로그에도", "로그를", "저장 로그", "logging", "debug log"),
        normalized="logging debug trace",
        file_hints=("app/generators/output_writer.py", "app/cli.py", "app/main.py"),
        target_hints=("logging",),
        intent="logging_issue",
    ),
    AliasRule(
        patterns=("timeout", "타임아웃", "시간 늘", "대기시간"),
        normalized="timeout configuration retry generation wait",
        target_hints=("timeout config",),
        intent="timeout_issue",
    ),
    AliasRule(
        patterns=("출력 문구", "출력", "문구", "output copy"),
        normalized="output text copy generator",
        file_hints=("app/generators/capsule_generator.py", "app/generators/output_writer.py", "app/main.py"),
        target_hints=("output text",),
        intent="output_text_edit",
    ),
    AliasRule(
        patterns=("대본", "발표", "ppt", "슬라이드", "평가 리포트", "시연영상"),
        normalized="presentation script slide demo report review",
        file_hints=("app/analyzers/meeting_analyzer.py", "docs/v0.2_scrum_kickoff_modes.md"),
        target_hints=("presentation review",),
        intent="presentation_review",
    ),
    AliasRule(
        patterns=("소리", "오디오", "화면공유", "audio", "zoom"),
        normalized="presentation audio screen share checklist",
        file_hints=("app/analyzers/meeting_analyzer.py", "docs/v0.2_scrum_kickoff_modes.md"),
        target_hints=("presentation audio",),
        intent="presentation_environment_issue",
    ),
    AliasRule(
        patterns=("해야 할 거", "말해주세요", "내일 아침", "리허설", "맞춰보자"),
        normalized="team coordination schedule rehearsal next action",
        file_hints=("app/analyzers/meeting_analyzer.py", "docs/v0.2_scrum_kickoff_modes.md"),
        target_hints=("team coordination",),
        intent="team_coordination",
    ),
    AliasRule(
        patterns=("스크럼", "회의록", "scrum"),
        normalized="scrum notes meeting summary",
        file_hints=("app/analyzers/meeting_analyzer.py",),
        target_hints=("scrum notes",),
        intent="scrum_notes",
    ),
    AliasRule(
        patterns=("킥오프", "프로젝트 착수", "project kickoff"),
        normalized="project kickoff scope planning",
        file_hints=("app/analyzers/meeting_analyzer.py",),
        target_hints=("project kickoff",),
        intent="project_kickoff",
    ),
]

PROTECTED_DOMAIN_RULES = {
    "auth": ("auth", "jwt", "login", "password", "permission"),
    "db": ("db", "database", "schema", "migration", "model", "table"),
    "deploy": ("deploy", "docker", "nginx", "production", "ssl"),
    "secret": ("secret", ".env", "credential", "api_key", "access_token", "refresh_token"),
}

NEGATION_HINTS = (
    "건드리지 말",
    "건들지 말",
    "수정하지 말",
    "변경하지 말",
    "하지 말",
    "냅두",
    "놔두",
    "빼고",
    "제외",
    "금지",
    "do not",
    "don't",
    "dont",
    "avoid",
    "except",
)

EXTENSION_SCOPE_PATTERNS = {
    ".md": (
        r"(?:^|[\s])(?:\.?md|마크다운|markdown)\s*(?:파일|문서)(?:들|만|만을|만 보고|을|를)?",
        r"(?:^|[\s])(?:\.?md|마크다운|markdown)\s*(?:만|만을)\s*(?:확인|봐|보고|읽)",
    ),
}

EXCLUDE_EXTENSION_PATTERNS = {
    ".json": (
        r"(?:\.?json|제이슨)\s*(?:은|는|파일은|파일은)?\s*(?:보지\s*말|제외|빼고|빼줘|빼라|읽지\s*말)",
        r"(?:보지\s*말|제외|빼고|빼줘|빼라|읽지\s*말).{0,12}(?:\.?json|제이슨)",
    ),
}

AMBIGUOUS_PATTERNS = (
    "이거 왜",
    "저거 왜",
    "그거 왜",
    "아까 그거",
    "그거 이어서",
    "아까 하던",
    "아까 이어서",
    "저거 손보",
    "이거 손보",
    "이거 해",
    "그거 해",
)

INTENT_HINTS = [
    ("documentation_edit", ("문서", "설명", "요약", "정리", "다듬", "손보", "readme", "docs", "portfolio")),
    ("bug_investigation", ("안됨", "안돼", "오류", "에러", "왜", "bug", "error", "fix", "고쳐", "고치", "실패", "터져", "죽어", "이상해", "이상함")),
    ("feature_addition", ("추가", "구현", "붙이", "만들", "add", "implement")),
    ("refactor", ("리팩터", "정리", "refactor")),
    ("test_fix", ("테스트", "pytest", "test")),
    ("release_deploy", ("릴리즈", "배포", "release", "deploy")),
    ("security_review", ("보안", "secret", "credential", ".env")),
    ("metric_validation", ("토큰", "성능", "절감률", "뻥튀기", "metric")),
]


def understand_request(request: str, files: list[RepoFile]) -> RequestUnderstanding:
    original = request.strip()
    lower = original.lower()
    repo_paths = {file.path for file in files}
    applied_aliases: list[str] = []
    target_hints: list[str] = []
    protected_hints = extract_protected_hints(lower)
    file_hints: list[str] = []
    normalized_terms: list[str] = []
    intent_votes: list[str] = []
    include_extensions = extract_include_extensions(lower)
    exclude_extensions = extract_exclude_extensions(lower)

    for rule in ALIAS_RULES:
        matched_patterns = [pattern for pattern in rule.patterns if pattern.lower() in lower]
        if not matched_patterns:
            continue
        normalized_terms.append(rule.normalized)
        applied_aliases.extend(f"{pattern}->{rule.normalized}" for pattern in matched_patterns)
        target_hints.extend(rule.target_hints)
        file_hints.extend(resolve_existing_paths(rule.file_hints, repo_paths))
        if rule.intent:
            intent_votes.append(rule.intent)

    intent = infer_intent(lower, intent_votes)
    if intent == "documentation_edit" and not file_hints and any(term in lower for term in ("문서", "docs", "정리")):
        file_hints.extend(resolve_existing_paths(("README.md", "docs/"), repo_paths))
        target_hints.append("documentation")

    protected_terms = flatten_protected_terms(protected_hints)
    target_hints = [hint for hint in dedupe(target_hints) if hint.lower() not in protected_terms]
    file_hints = dedupe(file_hints)
    applied_aliases = dedupe(applied_aliases)
    normalized_terms = dedupe(normalized_terms)
    include_extensions = dedupe(include_extensions)
    exclude_extensions = [extension for extension in dedupe(exclude_extensions) if extension not in include_extensions]

    ambiguous = is_ambiguous_request(lower, file_hints, target_hints, intent)
    confidence = calculate_confidence(ambiguous, file_hints, target_hints, intent)
    confidence_label = label_confidence(confidence)
    clarification_question = build_clarification_question(original) if ambiguous else None

    search_query = build_search_query(
        original,
        intent,
        normalized_terms,
        target_hints,
        file_hints,
        protected_hints,
        include_extensions,
        exclude_extensions,
    )
    normalized_request = build_normalized_request(
        original,
        intent,
        normalized_terms,
        target_hints,
        file_hints,
        protected_hints,
        include_extensions,
        exclude_extensions,
        clarification_question,
    )

    return RequestUnderstanding(
        original_request=original,
        normalized_request=normalized_request,
        search_query=search_query,
        intent=intent,
        confidence=confidence,
        confidence_label=confidence_label,
        target_hints=target_hints,
        protected_hints=protected_hints,
        file_hints=file_hints,
        include_extensions=include_extensions,
        exclude_extensions=exclude_extensions,
        applied_aliases=applied_aliases,
        clarification_question=clarification_question,
        needs_clarification=ambiguous,
    )


def extract_include_extensions(text: str) -> list[str]:
    extensions: list[str] = []
    for extension, patterns in EXTENSION_SCOPE_PATTERNS.items():
        if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns):
            extensions.append(extension)
    return extensions


def extract_exclude_extensions(text: str) -> list[str]:
    extensions: list[str] = []
    for extension, patterns in EXCLUDE_EXTENSION_PATTERNS.items():
        if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns):
            extensions.append(extension)
    return extensions


def extract_protected_hints(text: str) -> list[str]:
    protected: list[str] = []
    for domain, terms in PROTECTED_DOMAIN_RULES.items():
        for term in terms:
            if term in text and is_negated_context(text, term):
                protected.append(domain)
                break
    return dedupe(protected)


def is_negated_context(text: str, term: str) -> bool:
    for match in re.finditer(re.escape(term), text):
        start = max(0, match.start() - 30)
        end = min(len(text), match.end() + 30)
        window = text[start:end]
        if any(hint in window for hint in NEGATION_HINTS):
            return True
    return False


def flatten_protected_terms(protected_hints: list[str]) -> set[str]:
    terms = set(protected_hints)
    for hint in protected_hints:
        terms.update(PROTECTED_DOMAIN_RULES.get(hint, ()))
    return terms


def resolve_existing_paths(path_hints: tuple[str, ...], repo_paths: set[str]) -> list[str]:
    resolved: list[str] = []
    for hint in path_hints:
        if hint.endswith("/"):
            resolved.extend(path for path in repo_paths if path.startswith(hint))
        elif hint in repo_paths:
            resolved.append(hint)
    return sorted(resolved)


def infer_intent(text: str, votes: list[str]) -> str:
    if votes:
        return votes[0]
    for intent, hints in INTENT_HINTS:
        if any(hint in text for hint in hints):
            return intent
    return "general"


def is_ambiguous_request(text: str, file_hints: list[str], target_hints: list[str], intent: str) -> bool:
    if file_hints or target_hints:
        return False
    if any(pattern in text for pattern in AMBIGUOUS_PATTERNS):
        return True
    meaningful_tokens = re.findall(r"[A-Za-z0-9_]+|[\uac00-\ud7a3]+", text)
    return intent == "general" and len(meaningful_tokens) <= 3


def calculate_confidence(ambiguous: bool, file_hints: list[str], target_hints: list[str], intent: str) -> float:
    if ambiguous:
        return 0.2
    if file_hints:
        return 0.88
    if target_hints:
        return 0.76
    if intent != "general":
        return 0.58
    return 0.4


def label_confidence(confidence: float) -> str:
    if confidence >= 0.75:
        return "high"
    if confidence >= 0.5:
        return "medium"
    return "low"


def build_clarification_question(original: str) -> str:
    if original:
        return "대상 파일, 기능명, 또는 오류 로그 중 하나를 알려주세요."
    return "작업 요청을 한 줄로 입력해주세요."


def build_search_query(
    original: str,
    intent: str,
    normalized_terms: list[str],
    target_hints: list[str],
    file_hints: list[str],
    protected_hints: list[str],
    include_extensions: list[str],
    exclude_extensions: list[str],
) -> str:
    scope_terms = [f"include_extension:{extension}" for extension in include_extensions]
    scope_terms.extend(f"exclude_extension:{extension}" for extension in exclude_extensions)
    if file_hints or target_hints or normalized_terms or scope_terms:
        original_terms = [original] if original and not protected_hints else []
        return " ".join([*original_terms, intent, *normalized_terms, *target_hints, *file_hints, *scope_terms])
    if protected_hints:
        return intent
    return original


def build_normalized_request(
    original: str,
    intent: str,
    normalized_terms: list[str],
    target_hints: list[str],
    file_hints: list[str],
    protected_hints: list[str],
    include_extensions: list[str],
    exclude_extensions: list[str],
    clarification_question: str | None,
) -> str:
    lines = [original, "", f"Intent: {intent}"]
    if normalized_terms:
        lines.append(f"Normalized terms: {', '.join(normalized_terms)}")
    if target_hints:
        lines.append(f"Target hints: {', '.join(target_hints)}")
    if file_hints:
        lines.append(f"File hints: {', '.join(file_hints)}")
    if protected_hints:
        lines.append(f"Do not modify: {', '.join(protected_hints)}")
    if include_extensions:
        lines.append(f"Only include file extensions: {', '.join(include_extensions)}")
    if exclude_extensions:
        lines.append(f"Exclude file extensions: {', '.join(exclude_extensions)}")
    if clarification_question:
        lines.append(f"Clarification needed: {clarification_question}")
    return "\n".join(lines)


def dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result
