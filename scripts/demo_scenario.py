from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.adapters.github_issue_adapter import create_issue_from_packet
from app.generators.capsule_generator import generate_capsule
from app.generators.execution_packet_generator import build_execution_packet
from app.generators.output_writer import save_output_packet
from app.schemas.capsule_schema import CapsuleInput, FileKind, HandoffTarget, RepoFile

LOGIN_BUG_TASK = (
    "로그인 API에서 성공 응답 후 프론트가 사용자 정보를 받지 못하는 오류를 수정하기 위한 "
    "AI handoff packet을 만들어줘. JWT secret과 DB schema는 수정하지 말고, 먼저 수정 계획만 제안하게 해줘."
)


def demo_files() -> list[RepoFile]:
    return [
        RepoFile(
            path="README.md",
            kind=FileKind.DOC,
            content="# Demo Login Service\nFastAPI backend and React frontend login flow.\n" * 120,
            size=8_000,
        ),
        RepoFile(
            path="backend/auth/router.py",
            kind=FileKind.CODE,
            content=(
                "def login():\n"
                "    token = issue_jwt(user)\n"
                "    return {'access_token': token, 'user_id': user.id}\n"
            ),
            size=110,
        ),
        RepoFile(
            path="backend/schemas/user.py",
            kind=FileKind.CODE,
            content="class LoginResponse(BaseModel):\n    access_token: str\n    user_id: int\n",
            size=80,
        ),
        RepoFile(
            path="frontend/src/api/auth.ts",
            kind=FileKind.CODE,
            content="export type LoginResponse = { accessToken: string; user: User };\n",
            size=70,
        ),
        RepoFile(
            path=".env.example",
            kind=FileKind.CONFIG,
            content="JWT_SECRET=change-me\nDATABASE_URL=postgres://example\n",
            size=60,
        ),
    ]


def run_demo(output_root: Path, repository: str) -> dict:
    capsule = generate_capsule(
        CapsuleInput(
            repo_path=Path("."),
            task_request=LOGIN_BUG_TASK,
            forbidden_rules=[
                "JWT secret/env 값 수정 금지",
                "DB schema 변경 전 반드시 확인",
                "자동 적용하지 말고 수정 계획 먼저 제안",
            ],
            top_k=8,
            handoff_target=HandoffTarget.AI_TOOL,
        ),
        demo_files(),
    )
    packet = build_execution_packet(capsule)
    saved = save_output_packet(
        capsule,
        packet,
        output_root=output_root,
        generated_at=datetime(2026, 6, 23, 9, 30, 0),
    )
    dry_run = create_issue_from_packet(saved.output_dir, repository=repository, apply=False)

    return {
        "scenario": "login_api_error_handoff",
        "output_dir": str(saved.output_dir),
        "dry_run": asdict(dry_run),
        "token_budget": capsule.token_budget.model_dump(mode="json"),
        "auto_start_allowed": packet.auto_start_allowed,
        "risk_level": packet.risk_level.value,
        "retrieved_paths": [chunk.path for chunk in capsule.relevant_chunks],
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Run a fixed Context Capsule demo scenario.")
    parser.add_argument("--output-root", type=Path, default=Path("outputs/demo"), help="Directory for demo outputs.")
    parser.add_argument("--repo", default="mosejong/context-capsule", help="Repository used in issue dry-run payload.")
    parser.add_argument("--json", action="store_true", help="Print full JSON result.")
    args = parser.parse_args()

    result = run_demo(args.output_root, args.repo)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(f"Scenario: {result['scenario']}")
    print(f"Output dir: {result['output_dir']}")
    print(f"Dry-run title: {result['dry_run']['title']}")
    print(f"Auto-start allowed: {result['auto_start_allowed']}")
    print(f"Risk level: {result['risk_level']}")
    print(f"Token reduction: {result['token_budget']['estimated_reduction_percent']:.1f}%")
    print("Dry-run only. No GitHub issue was created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
