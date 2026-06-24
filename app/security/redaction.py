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
    re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL),
    re.compile(r"(?<![A-Fa-f0-9])[A-Fa-f0-9]{40}(?![A-Fa-f0-9])"),
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
    return SanitizedText(text=redacted, secret_count=count)


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
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)


def has_prompt_injection_or_redaction(text: str) -> bool:
    lower = text.lower()
    if PROMPT_INJECTION_PLACEHOLDER.lower() in lower:
        return True
    return any(is_prompt_injection_line(line) for line in text.splitlines())
