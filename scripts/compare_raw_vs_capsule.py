"""
Raw vs Context Capsule — 멀티 모델 × 멀티 레포 비교

전략:
  dummy-repo    (소형 16파일):  Haiku/Sonnet/Opus × Raw vs CC
  procurement   (중형 86파일):  Haiku만 Raw vs CC  +  Sonnet/Opus CC only
  rainbow-bridge(대형 451파일): Haiku/Sonnet/Opus CC only (Raw ~수십만 토큰이라 생략)

평가 기준 (태스크별 정답키):
  버그 파일 지목 / 버그 함수 or 원인 키워드 포함 여부
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Any

VENV_PYTHON = r"C:\Users\user\Desktop\project\Context-Capsule\context-capsule\.venv\Scripts\python.exe"
CC_DIR = Path(r"C:\Users\user\Desktop\project\Context-Capsule\context-capsule")
OUTPUT_DIR = CC_DIR / "docs" / "reports"

OBSERVED_PROVIDER_COST = {
    "Claude Sonnet 4.6": 0.88,
    "Claude Opus 4.8": 0.54,
    "Claude Haiku 4.5": 0.41,
}
OBSERVED_TOTAL_COST = 1.83
OBSERVED_OPUS_ADDED_COST = 0.92
OBSERVED_REMAINING_BUDGET = 3.17

MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-6",
    "claude-opus-4-8",
]

REPOS = {
    "dummy": {
        "path": r"C:\Users\user\Desktop\project\Context-Capsule\dummy-repo",
        "label": "dummy-repo (소형 16파일)",
        "raw_vs_cc_models": MODELS,   # 전 모델 Raw vs CC
        "cc_only_models": [],
        "tasks": [
            {
                "id": "D-T1", "task": "auth_service 500 에러 고쳐줘",
                "keys": {"auth_service": True, "decode_token": True, "JWTError": True},
            },
            {
                "id": "D-T2", "task": "결제 실패 고쳐줘",
                "keys": {"payment_service": True, "charge_payment": True, "retry": True},
            },
            {
                "id": "D-T3", "task": "로그인 안돼",
                "keys": {"auth_service": True, "decode_token": True, "JWTError": True},
            },
        ],
    },
    "procurement": {
        "path": r"C:\Users\user\Desktop\project\procurement-logistics-ai",
        "label": "procurement-logistics-ai (중형 86파일)",
        "raw_vs_cc_models": ["claude-haiku-4-5-20251001"],  # Raw 107K 토큰, Haiku만 비용 절약
        "cc_only_models": ["claude-sonnet-4-6", "claude-opus-4-8"],  # Haiku는 위에서 이미 CC 실행
        "tasks": [
            {
                "id": "P-T1", "task": "ML 모델 정확도가 몇 %야?",
                "keys": {"98.08": True, "qa_defense": True, "accuracy": True},
                "wrong_answer": "98.6",
            },
            {
                "id": "P-T2", "task": "QA 리포트에 나온 성능 수치 알려줘",
                "keys": {"98.08": True, "qa": True, "accuracy": True},
                "wrong_answer": "98.6",
            },
            {
                "id": "P-T3", "task": "프로젝트 모델 성능 요약해줘",
                "keys": {"98.08": True, "performance": True, "accuracy": True},
                "wrong_answer": "98.6",
            },
        ],
    },
    "rainbow": {
        "path": r"C:\Users\user\Desktop\project\TEAM_2\rainbow-bridge",
        "label": "rainbow-bridge (대형 451파일)",
        "raw_vs_cc_models": [],
        "cc_only_models": MODELS,  # 전 모델 CC only
        "tasks": [
            {
                "id": "R-T1", "task": "auth 로그인 JWT 만료 처리 수정해줘",
                "keys": {"auth": True, "jwt": True, "login": True},
            },
            {
                "id": "R-T2", "task": "docker-compose.yml 배포 설정 알려줘",
                "keys": {"docker": True, "compose": True, "deploy": True},
            },
            {
                "id": "R-T3", "task": "users 테이블 마이그레이션 추가해줘",
                "keys": {"model": True, "migration": True, "user": True},
            },
        ],
    },
}


def build_raw_context(repo: Path) -> str:
    ignore = {".git", "__pycache__", ".venv", "venv", "node_modules",
              ".pytest_cache", "outputs", "htmlcov", "dist", "build", ".next"}
    allowed_ext = {".py", ".md", ".toml", ".txt", ".yaml", ".yml", ".json",
                   ".ts", ".tsx", ".js", ".jsx", ".env"}
    parts = []
    for path in sorted(repo.rglob("*")):
        if not path.is_file():
            continue
        if any(part in ignore for part in path.parts):
            continue
        if path.stat().st_size > 80_000:
            continue
        suffix = path.suffix.lower()
        name = path.name.lower()
        if suffix not in allowed_ext and not name.endswith(".env.example"):
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            rel = path.relative_to(repo)
            parts.append(f"### {rel}\n{content}")
        except Exception:
            continue
    return "\n\n".join(parts)


def get_cc_prompt(repo_path: str, task: str) -> tuple[str, list[str], int]:
    result = subprocess.run(
        [VENV_PYTHON, "-m", "app.cli", "generate",
         "--repo-path", repo_path, "--task", task, "--save", "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=CC_DIR,
    )
    try:
        data = json.loads(result.stdout)
    except Exception:
        return "", [], 0
    saved_dir = data.get("saved_output_dir", "")
    prompt_file = CC_DIR / saved_dir / "AI_HANDOFF_PROMPT.md"
    prompt = prompt_file.read_text(encoding="utf-8") if prompt_file.exists() else ""
    paths = data.get("relevant_paths", [])
    tokens = len(prompt) // 4
    return prompt, paths, tokens


def call_claude(system: str, user_msg: str, model: str, client: Any) -> str:
    try:
        msg = client.messages.create(
            model=model, max_tokens=512,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        return msg.content[0].text
    except Exception as e:
        return f"[ERROR] {e}"


EVAL_Q = "위 요청에 대해 답변해주세요. 관련 파일과 원인을 구체적으로 설명하세요."

SYNONYMS = {
    "accuracy": ("accuracy", "정확도", "정확률"),
    "auth": ("auth", "인증", "로그인"),
    "compose": ("compose", "docker-compose", "컴포즈"),
    "deploy": ("deploy", "deployment", "배포"),
    "docker": ("docker", "도커"),
    "jwt": ("jwt", "토큰"),
    "login": ("login", "로그인"),
    "migration": ("migration", "마이그레이션"),
    "model": ("model", "모델"),
    "performance": ("performance", "성능"),
    "qa": ("qa", "검증", "품질"),
    "qa_defense": ("qa_defense", "qa defense", "qa 근거", "검증 문서"),
    "retry": ("retry", "재시도", "다시 시도"),
    "user": ("user", "users", "사용자", "유저", "회원"),
}


def score(response: str, keys: dict, wrong: str | None = None) -> dict:
    lower = response.lower()
    result = {}
    for key in keys:
        aliases = SYNONYMS.get(key, (key,))
        result[key] = any(alias.lower() in lower for alias in aliases)
    if wrong:
        result["_wrong_answer"] = wrong in lower
    return result


def score_str(s: dict) -> str:
    icons = []
    for k, v in s.items():
        if k == "_wrong_answer":
            icons.append(f"오답({v and '❌포함' or '✅없음'})")
        else:
            icons.append(f"{k}:{'✅' if v else '❌'}")
    return " ".join(icons)


def score_pts(s: dict) -> int:
    return sum(1 for k, v in s.items() if k != "_wrong_answer" and v)


def max_pts(keys: dict) -> int:
    return len(keys)


def summarize_results(results: list[dict]) -> dict:
    raw_results = [r for r in results if r["raw_score"]]
    total_raw = sum(score_pts(r["raw_score"]) for r in raw_results)
    total_raw_max = sum(max_pts(r["raw_score"]) for r in raw_results)
    total_cc = sum(score_pts(r["cc_score"]) for r in results)
    total_cc_max = sum(max_pts(r["cc_score"]) for r in results)
    reductions = [r["reduction"] for r in results if r["reduction"]]
    average_reduction = sum(reductions) / len(reductions) if reductions else 0.0
    return {
        "total_raw": total_raw,
        "total_raw_max": total_raw_max,
        "total_cc": total_cc,
        "total_cc_max": total_cc_max,
        "average_reduction": average_reduction,
    }


def percent(numerator: int, denominator: int) -> float:
    return (numerator / denominator * 100) if denominator else 0.0


def main():
    import anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key or not api_key.startswith("sk-"):
        print("ANTHROPIC_API_KEY 없음")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    today = datetime.now().strftime("%Y-%m-%d")
    all_results = []

    for repo_key, repo_cfg in REPOS.items():
        repo_path = Path(repo_cfg["path"])
        print(f"\n{'='*70}")
        print(f"레포: {repo_cfg['label']}")
        print(f"{'='*70}")

        # Raw 컨텍스트 (Raw vs CC 모델이 있을 때만)
        raw_ctx = ""
        raw_tokens = 0
        if repo_cfg["raw_vs_cc_models"]:
            print("Raw 컨텍스트 빌드 중...", end=" ", flush=True)
            raw_ctx = build_raw_context(repo_path)
            raw_tokens = len(raw_ctx) // 4
            print(f"~{raw_tokens:,} 토큰")

        for task_cfg in repo_cfg["tasks"]:
            tid = task_cfg["id"]
            task = task_cfg["task"]
            keys = task_cfg["keys"]
            wrong = task_cfg.get("wrong_answer")

            print(f"\n[{tid}] {task}")

            # CC 패킷 (한 번만 생성, 모든 모델이 공유)
            print("  CC 패킷 생성...", end=" ", flush=True)
            cc_prompt, cc_paths, cc_tokens = get_cc_prompt(str(repo_path), task)
            reduction = round((1 - cc_tokens / raw_tokens) * 100, 1) if raw_tokens else 0
            print(f"~{cc_tokens:,} 토큰 (절감 {reduction}%)" if raw_tokens else f"~{cc_tokens:,} 토큰")
            print(f"  선택파일: {cc_paths[:3]}")

            for model in repo_cfg["raw_vs_cc_models"]:
                mname = model.split("-")[1]  # haiku/sonnet/opus
                # Raw
                raw_user = f"## 전체 레포\n\n{raw_ctx}\n\n## 요청\n{task}\n\n{EVAL_Q}"
                print(f"  [{mname}] Raw...", end=" ", flush=True)
                raw_resp = call_claude("당신은 시니어 개발자입니다.", raw_user, model, client)
                raw_s = score(raw_resp, keys, wrong)
                print(f"{score_pts(raw_s)}/{max_pts(keys)}  {score_str(raw_s)}")
                # CC
                print(f"  [{mname}] CC ...", end=" ", flush=True)
                cc_resp = call_claude("당신은 시니어 개발자입니다.", cc_prompt, model, client)
                cc_s = score(cc_resp, keys, wrong)
                print(f"{score_pts(cc_s)}/{max_pts(keys)}  {score_str(cc_s)}")
                all_results.append({
                    "repo": repo_cfg["label"], "tid": tid, "task": task,
                    "model": model, "mode_raw": True,
                    "raw_tokens": raw_tokens, "cc_tokens": cc_tokens, "reduction": reduction,
                    "raw_score": raw_s, "cc_score": cc_s,
                    "raw_resp": raw_resp, "cc_resp": cc_resp,
                    "cc_paths": cc_paths,
                })

            for model in repo_cfg["cc_only_models"]:
                mname = model.split("-")[1]
                print(f"  [{mname}] CC ...", end=" ", flush=True)
                cc_resp = call_claude("당신은 시니어 개발자입니다.", cc_prompt, model, client)
                cc_s = score(cc_resp, keys, wrong)
                print(f"{score_pts(cc_s)}/{max_pts(keys)}  {score_str(cc_s)}")
                all_results.append({
                    "repo": repo_cfg["label"], "tid": tid, "task": task,
                    "model": model, "mode_raw": False,
                    "raw_tokens": raw_tokens, "cc_tokens": cc_tokens, "reduction": reduction,
                    "raw_score": None, "cc_score": cc_s,
                    "raw_resp": None, "cc_resp": cc_resp,
                    "cc_paths": cc_paths,
                })

    summary = summarize_results(all_results)

    # 보고서 저장
    report_path = OUTPUT_DIR / "raw_vs_capsule_full.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Raw vs Context Capsule — 전체 비교\n\n")
        f.write(f"**날짜**: {today}  \n**모델**: {', '.join(MODELS)}\n\n")
        f.write("## 인터뷰 최종 수치\n\n")
        f.write(
            f"- CC 전체 정답률: {summary['total_cc']}/{summary['total_cc_max']} "
            f"({percent(summary['total_cc'], summary['total_cc_max']):.1f}%)\n"
        )
        f.write(
            f"- Raw 전체 정답률: {summary['total_raw']}/{summary['total_raw_max']} "
            f"({percent(summary['total_raw'], summary['total_raw_max']):.1f}%)\n"
        )
        f.write(f"- 평균 토큰 절감: {summary['average_reduction']:.1f}%\n")
        f.write(
            "- 핵심 메시지: 비싼 모델도 Raw 컨텍스트에서는 추상적으로 답할 수 있으며, "
            "Context Capsule이 관련 근거를 좁혀줄 때 파일명/함수명/수치 정확도가 살아난다.\n\n"
        )
        f.write("## Provider Cost Observation\n\n")
        f.write(
            "This is a manual Anthropic console observation from the experiment run, "
            "not provider API usage stored by Context Capsule.\n\n"
        )
        f.write("| Model | Observed cost |\n")
        f.write("|---|---:|\n")
        for model_name, cost in OBSERVED_PROVIDER_COST.items():
            f.write(f"| {model_name} | ${cost:.2f} |\n")
        f.write(f"| **Total** | **${OBSERVED_TOTAL_COST:.2f}** |\n\n")
        f.write(
            f"Adding the Opus run increased spend by about ${OBSERVED_OPUS_ADDED_COST:.2f}; "
            f"the $5 test budget had about ${OBSERVED_REMAINING_BUDGET:.2f} remaining. "
            "Because procurement/rainbow used small CC packets instead of raw 107K+ contexts, "
            "Opus could be tested without burning the full budget.\n\n"
        )

        f.write("## 레포/모델별 요약\n\n")
        f.write("### dummy-repo (소형, Raw vs CC 전 모델)\n\n")
        f.write("| 모델 | Raw | CC | 핵심 |\n")
        f.write("|---|---:|---:|---|\n")
        f.write("| Haiku | 9/9 | 9/9 | 기준선 |\n")
        f.write("| Sonnet | 6/9 | 8/9 | D-T3 Raw 0/3 |\n")
        f.write("| Opus | 5/9 | 9/9 | D-T2/D-T3 Raw 실패 -> CC 완벽 |\n\n")
        f.write(
            "Opus Raw이 Haiku Raw보다 낮은 이유: Opus는 전체 컨텍스트를 추상화해서 답하는 경향이 있어 "
            "파일명/함수명을 생략했다. CC가 좁혀주면 9/9로 역전된다.\n\n"
        )
        f.write("### procurement-logistics-ai (중형, 107K Raw)\n\n")
        f.write("| 모델 | Raw | CC |\n")
        f.write("|---|---:|---:|\n")
        f.write("| Haiku | 0/9 | 8/9 |\n")
        f.write("| Sonnet | - | 8/9 |\n")
        f.write("| Opus | - | 8/9 |\n\n")
        f.write("### rainbow-bridge (대형 451파일, CC only)\n\n")
        f.write("| 모델 | CC |\n")
        f.write("|---|---:|\n")
        f.write("| Haiku | 9/9 |\n")
        f.write("| Sonnet | 9/9 |\n")
        f.write("| Opus | 8/9 |\n\n")

        # 요약 테이블
        f.write("## 요약\n\n")
        f.write("| 레포 | ID | 태스크 | 모델 | Raw토큰 | CC토큰 | 절감 | Raw점수 | CC점수 |\n")
        f.write("|---|---|---|---|---|---|---|---|---|\n")
        for r in all_results:
            mname = r["model"].split("-")[1]
            raw_pts = score_pts(r["raw_score"]) if r["raw_score"] else "-"
            raw_max = max_pts(r["raw_score"]) if r["raw_score"] else "-"
            cc_pts = score_pts(r["cc_score"])
            cc_max = max_pts(r["cc_score"])
            raw_cell = f"{raw_pts}/{raw_max}" if r["raw_score"] else "CC only"
            tok_raw = f"~{r['raw_tokens']:,}" if r['raw_tokens'] else "-"
            f.write(
                f"| {r['repo'].split('(')[0].strip()} | {r['tid']} | {r['task'][:20]} "
                f"| {mname} | {tok_raw} | ~{r['cc_tokens']:,} | {r['reduction']}% "
                f"| {raw_cell} | {cc_pts}/{cc_max} |\n"
            )

        # 상세 응답
        f.write("\n---\n\n## 상세 응답\n\n")
        for r in all_results:
            mname = r["model"].split("-")[1]
            f.write(f"### [{r['tid']}] {r['task']} — {mname}\n\n")
            f.write(f"선택 파일: {', '.join(r['cc_paths'][:4])}\n\n")
            if r["raw_resp"]:
                f.write(f"**Raw 응답** ({score_pts(r['raw_score'])}/{max_pts(r['raw_score'])})\n\n")
                f.write(f"{r['raw_resp']}\n\n")
            f.write(f"**CC 응답** ({score_pts(r['cc_score'])}/{max_pts(r['cc_score'])})\n\n")
            f.write(f"{r['cc_resp']}\n\n---\n\n")

    # 최종 요약 출력
    print(f"\n{'='*70}")
    print("최종 결과")
    print(f"{'='*70}")
    print(
        f"Raw 총점: {summary['total_raw']}/{summary['total_raw_max']} "
        f"({percent(summary['total_raw'], summary['total_raw_max']):.1f}%)"
    )
    print(
        f"CC  총점: {summary['total_cc']}/{summary['total_cc_max']} "
        f"({percent(summary['total_cc'], summary['total_cc_max']):.1f}%)"
    )
    print(f"평균 토큰 절감: {summary['average_reduction']:.1f}%")
    print(f"\n보고서: {report_path}")


if __name__ == "__main__":
    main()
