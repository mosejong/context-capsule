from __future__ import annotations

import re
from dataclasses import dataclass

SECRET_PLACEHOLDER = "[REDACTED_SECRET]"
PROMPT_INJECTION_PLACEHOLDER = "[REDACTED_PROMPT_INJECTION_LINE]"

SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bAKIA[0-9A-Z]{12,24}\b", re.IGNORECASE),
    re.compile(r"\bASIA[0-9A-Z]{12,24}\b", re.IGNORECASE),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{16,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{16,}\b"),
    re.compile(r"\bnvapi-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL),
    re.compile(r"(?<![A-Fa-f0-9])[A-Fa-f0-9]{40}(?![A-Fa-f0-9])"),
)
GENERIC_CREDENTIAL_KEYS = {
    "access_key",
    "access_token",
    "apikey",
    "api_key",
    "auth_token",
    "bearer_token",
    "client_secret",
    "connection_string",
    "database_url",
    "db_password",
    "db_url",
    "dsn",
    "github_token",
    "mysql_password",
    "openai_api_key",
    "password",
    "passwd",
    "postgres_password",
    "private_key",
    "pwd",
    "refresh_token",
    "secret",
    "secret_key",
    "token",
}
GENERIC_ASSIGNMENT_PATTERN = re.compile(
    r"^(?P<prefix>\s*(?:-\s*)?(?:export\s+)?[\"']?)"
    r"(?P<key>[A-Za-z_][A-Za-z0-9_.-]*)"
    r"(?P<suffix>[\"']?\s*[:=]\s*)"
    r"(?P<value>.*?)(?P<newline>\r?\n)?$"
)

PROMPT_INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bsystem\s+override\b", re.IGNORECASE),
    re.compile(r"\bignore\s+all\s+previous\s+instructions\b", re.IGNORECASE),
    re.compile(r"\bdisregard\s+(?:all\s+)?(?:previous|prior)\s+instructions\b", re.IGNORECASE),
    re.compile(r"\bauto[_ -]?start\s+is\s+always\s+allowed\b", re.IGNORECASE),
    re.compile(r"\bhuman\s+has\s+pre-approved\b", re.IGNORECASE),
    re.compile(r"\bapply\s+edits\s+directly\s+without\s+asking\b", re.IGNORECASE),
    re.compile(r"\bdo\s+not\s+ask\s+for\s+approval\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class SanitizedText:
    text: str
    secret_count: int = 0
    prompt_injection_count: int = 0

    @property
    def changed(self) -> bool:
        return self.secret_count > 0 or self.prompt_injection_count > 0


def sanitize_untrusted_text(text: str) -> SanitizedText:
    secret_result = redact_secrets(text)
    injection_result = redact_prompt_injection_lines(secret_result.text)
    return SanitizedText(
        text=injection_result.text,
        secret_count=secret_result.secret_count,
        prompt_injection_count=injection_result.prompt_injection_count,
    )


def redact_secrets(text: str) -> SanitizedText:
    redacted = text
    count = 0
    for pattern in SECRET_PATTERNS:
        redacted, replacements = pattern.subn(SECRET_PLACEHOLDER, redacted)
        count += replacements
    generic_result = redact_generic_credential_assignments(redacted)
    redacted = generic_result.text
    count += generic_result.secret_count
    return SanitizedText(text=redacted, secret_count=count)


def redact_generic_credential_assignments(text: str) -> SanitizedText:
    if not text:
        return SanitizedText(text=text)

    redacted_lines: list[str] = []
    count = 0
    for line in text.splitlines(keepends=True):
        match = GENERIC_ASSIGNMENT_PATTERN.match(line)
        if not match or not is_credential_key(match.group("key")):
            redacted_lines.append(line)
            continue

        value = match.group("value")
        if not should_redact_assignment_value(value):
            redacted_lines.append(line)
            continue

        redacted_lines.append(
            f"{match.group('prefix')}{match.group('key')}{match.group('suffix')}"
            f"{redact_assignment_value(value)}{match.group('newline') or ''}"
        )
        count += 1

    return SanitizedText(text="".join(redacted_lines), secret_count=count)


def is_credential_key(key: str) -> bool:
    normalized = key.strip("\"'").replace("-", "_").replace(".", "_").lower()
    if normalized in GENERIC_CREDENTIAL_KEYS:
        return True
    return normalized.endswith(("_password", "_secret", "_api_key", "_access_token", "_refresh_token", "_private_key"))


def should_redact_assignment_value(value: str) -> bool:
    stripped = value.strip()
    if not stripped:
        return False
    normalized = stripped.rstrip(",").strip("\"'").strip().lower()
    return normalized not in {"", "null", "none", "true", "false", "0", "1", "[]", "{}"}


def redact_assignment_value(value: str) -> str:
    leading_length = len(value) - len(value.lstrip())
    leading = value[:leading_length]
    body = value[leading_length:]
    comment = ""
    for marker in (" #", "\t#", " //"):
        index = body.find(marker)
        if index != -1:
            comment = body[index:]
            body = body[:index].rstrip()
            break

    comma = "," if body.rstrip().endswith(",") else ""
    body = body.rstrip().removesuffix(",").rstrip()
    quote = body[0] if body.startswith(("\"", "'")) else ""
    return f"{leading}{quote}{SECRET_PLACEHOLDER}{quote}{comma}{comment}"


def redact_prompt_injection_lines(text: str) -> SanitizedText:
    lines = text.splitlines()
    redacted_lines: list[str] = []
    count = 0
    for line in lines:
        if is_prompt_injection_line(line):
            redacted_lines.append(PROMPT_INJECTION_PLACEHOLDER)
            count += 1
        else:
            redacted_lines.append(line)

    if not lines:
        return SanitizedText(text=text)

    trailing_newline = "\n" if text.endswith("\n") else ""
    return SanitizedText(text="\n".join(redacted_lines) + trailing_newline, prompt_injection_count=count)


def is_prompt_injection_line(line: str) -> bool:
    return any(pattern.search(line) for pattern in PROMPT_INJECTION_PATTERNS)


def has_secret_or_redaction(text: str) -> bool:
    lower = text.lower()
    if SECRET_PLACEHOLDER.lower() in lower:
        return True
    return any(pattern.search(text) for pattern in SECRET_PATTERNS) or redact_generic_credential_assignments(text).secret_count > 0


def has_prompt_injection_or_redaction(text: str) -> bool:
    lower = text.lower()
    if PROMPT_INJECTION_PLACEHOLDER.lower() in lower:
        return True
    return any(is_prompt_injection_line(line) for line in text.splitlines())
