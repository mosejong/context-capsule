from __future__ import annotations

import argparse
import html
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from app.schemas.capsule_schema import HandoffTarget, RetrievalMode
from app.services.capsule_service import generate_capsule_result, summarize_generation_result


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "assets" / "screenshots"
TEMP_OUTPUT = ROOT / "outputs" / "demo_screenshots"


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture Context Capsule demo screenshots.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--chrome", default=os.environ.get("CHROME_PATH", ""))
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    TEMP_OUTPUT.mkdir(parents=True, exist_ok=True)

    chrome = find_chrome(args.chrome)
    if not chrome:
        raise SystemExit(
            "Chrome was not found. Install Chrome or set CHROME_PATH to the browser executable."
        )

    server = None
    base_url = f"http://127.0.0.1:{args.port}"
    try:
        if not is_healthy(base_url):
            server = start_server(args.port)
            wait_for_health(base_url)

        capture_url(chrome, base_url, output_dir / "01_dashboard_first_screen.png")

        work_result = generate_demo_result("리드미를 포트폴리오용으로 다듬어줘")
        work_page = TEMP_OUTPUT / "work_handoff_summary.html"
        work_page.write_text(render_work_summary_page(work_result), encoding="utf-8")
        capture_url(chrome, work_page.resolve().as_uri(), output_dir / "02_work_handoff_summary.png")

        metric_result = generate_demo_result("README 포트폴리오 수치 확인")
        metric_page = TEMP_OUTPUT / "metric_conflict.html"
        metric_page.write_text(render_metric_conflict_page(metric_result), encoding="utf-8")
        capture_url(chrome, metric_page.resolve().as_uri(), output_dir / "03_metric_conflict_risk.png")
    finally:
        if server and server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=8)
            except subprocess.TimeoutExpired:
                server.kill()

    print(f"wrote screenshots to {output_dir}")
    return 0


def find_chrome(explicit: str) -> str:
    candidates = [
        explicit,
        shutil.which("chrome"),
        shutil.which("chrome.exe"),
        shutil.which("msedge"),
        shutil.which("msedge.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    return ""


def start_server(port: int) -> subprocess.Popen:
    log_dir = ROOT / "outputs" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "demo_screenshot_server.log"
    log = log_path.open("w", encoding="utf-8")
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.web.server:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
    ]
    return subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)


def wait_for_health(base_url: str) -> None:
    deadline = time.time() + 25
    while time.time() < deadline:
        if is_healthy(base_url):
            return
        time.sleep(0.4)
    raise RuntimeError(f"Local UI did not start: {base_url}")


def is_healthy(base_url: str) -> bool:
    try:
        with urllib.request.urlopen(f"{base_url}/api/health", timeout=1.5) as response:
            return response.status == 200
    except Exception:
        return False


def capture_url(chrome: str, url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    profile_dir = TEMP_OUTPUT / "chrome-profile"
    profile_dir.mkdir(parents=True, exist_ok=True)
    command = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-software-rasterizer",
        "--no-sandbox",
        "--no-first-run",
        "--disable-extensions",
        "--hide-scrollbars",
        f"--user-data-dir={profile_dir}",
        "--window-size=1440,1250",
        f"--screenshot={output_path}",
        url,
    ]
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if completed.returncode != 0:
        raise RuntimeError(
            "Chrome screenshot failed.\n"
            f"command: {' '.join(command)}\n"
            f"stdout: {completed.stdout}\n"
            f"stderr: {completed.stderr}"
        )


def generate_demo_result(task: str):
    return generate_capsule_result(
        repo_path=ROOT,
        task_request=task,
        forbidden_rules=[
            "새 브랜치를 자동으로 만들지 말 것",
            "secret/env 값을 읽거나 출력하지 말 것",
            "수정 전 계획부터 제안할 것",
        ],
        top_k=8,
        handoff_target=HandoffTarget.AI_TOOL,
        retriever_mode=RetrievalMode.HYBRID,
        my_scope="README, docs, UI",
    )


def page(title: str, body: str) -> str:
    styles = (ROOT / "app" / "web" / "static" / "styles.css").read_text(encoding="utf-8")
    return f"""<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{e(title)}</title>
    <style>{styles}</style>
  </head>
  <body>
    <main class="shell">
      {body}
    </main>
  </body>
</html>
"""


def render_header(title: str, lead: str) -> str:
    return f"""
      <header class="hero">
        <div>
          <p class="eyebrow">Context Capsule v0.2.15</p>
          <h1>{e(title)}</h1>
          <p class="lead">{e(lead)}</p>
        </div>
        <div class="quick-card">
          <strong>결과를 보는 순서</strong>
          <ol>
            <li>요약</li>
            <li>추천 첫 행동</li>
            <li>근거 파일</li>
            <li>충돌/위험</li>
            <li>복붙 프롬프트</li>
          </ol>
        </div>
      </header>
"""


def render_work_summary_page(result) -> str:
    summary = summarize_generation_result(result)
    capsule = result.capsule
    packet = result.execution_packet
    guide = result.guided_result
    token = capsule.token_budget
    body = render_header(
        "작업 요청을 안전한 작업 정리본으로 바꿉니다.",
        "신입 개발자가 AI에게 바로 맡기기 전에 먼저 볼 파일, 금지 범위, 위험 신호를 좁혀줍니다.",
    )
    body += f"""
      <section class="result">
        <h2>요약</h2>
        <div class="result-flow">
          <span>1. 요약</span><span>2. 추천 첫 행동</span><span>3. 근거 파일</span><span>4. 충돌/위험</span><span>5. 복붙 프롬프트</span>
        </div>
        <div class="metric-grid">
          <div class="metric"><span>스캔 파일</span><strong>{summary["scanned_file_count"]}</strong></div>
          <div class="metric"><span>위험도</span><strong>{e(packet.risk_level.value)}</strong></div>
          <div class="metric"><span>자동 시작</span><strong>{"허용" if packet.auto_start_allowed else "차단"}</strong></div>
          <div class="metric"><span>토큰 추정 감소</span><strong>{token.estimated_reduction_percent:.1f}%</strong></div>
        </div>
        <p><strong>작업 요청:</strong> 리드미를 포트폴리오용으로 다듬어줘</p>
        <section class="first-action">
          <span>추천 첫 행동</span>
          <strong>{e(guide.first_action if guide else "근거 파일과 충돌/위험을 확인하세요.")}</strong>
        </section>
        <section class="evidence-card">
          <h3>근거 파일</h3>
          <p>AI가 먼저 봐야 할 파일 후보입니다. 사람이 전부 읽으라는 뜻이 아니라 작업 범위를 좁히기 위한 근거입니다.</p>
          <h4>우선 파일</h4>
          {file_list((guide.primary_files if guide else []) or [chunk.path for chunk in capsule.relevant_chunks[:3]])}
          <h4>참고 파일</h4>
          {file_list((guide.supporting_files if guide else [])[:4])}
        </section>
        <section class="token-guide">
          <strong>토큰이 줄어드는 방식</strong>
          <p>레포 전체 대신 검색 후보를 작업 정리본으로 압축합니다. 현재 수치는 실제 결제 토큰이 아니라 <code>{e(token.method)}</code> 기준의 <code>{e(token.verification_status)}</code> 추정치입니다.</p>
        </section>
      </section>
"""
    return page("Context Capsule work handoff summary", body)


def render_metric_conflict_page(result) -> str:
    capsule = result.capsule
    packet = result.execution_packet
    conflicts = [finding for finding in capsule.risk_findings if "수치 값" in finding.reason]
    conflict_items = []
    for conflict in conflicts:
        conflict_items.extend([item.strip() for item in (conflict.evidence or "").split(";") if item.strip()])
    body = render_header(
        "충돌하는 수치를 복사하기 전에 멈춥니다.",
        "Raw 에이전트가 오래된 숫자를 고르는 문제를 신뢰도 UX로 바꿉니다.",
    )
    body += f"""
      <section class="result">
        <h2>충돌/위험</h2>
        <section class="trust-alert metric-conflict">
          <span>수치 충돌 확인 필요</span>
          <h3>서로 다른 성능 수치가 발견됐습니다.</h3>
          <p>README, 발표자료, 검증 문서의 숫자가 다를 수 있습니다. 포트폴리오나 면접 답변에 쓰기 전에 원본 검증 문서를 우선 확인하세요.</p>
          {file_list(conflict_items)}
          <p class="hint">추천 행동: 검증 문서 기준 수치를 우선 확인하고, README의 오래된 숫자는 바로 복사하지 마세요.</p>
        </section>
        <section class="risk-preview risk-{"ok" if packet.auto_start_allowed else "blocked"}">
          <span>승인 게이트</span>
          <h3>{e(packet.risk_level.value)} · {"시작 가능" if packet.auto_start_allowed else "승인 전 보류"}</h3>
          <p>Context Capsule은 자동 수정이나 자동 merge를 하지 않습니다. 위험과 충돌을 사람이 먼저 확인하게 합니다.</p>
        </section>
        <section class="prompt-card">
          <h3>복붙 프롬프트</h3>
          <p>AI에게 넘기기 전, 충돌 수치를 확인하라는 지시가 포함된 작업 프롬프트를 만듭니다.</p>
          <pre>{e(capsule.sections.ai_handoff_prompt[:900])}</pre>
        </section>
      </section>
"""
    return page("Context Capsule metric conflict", body)


def file_list(items: list[str]) -> str:
    if not items:
        return "<p>없음</p>"
    return "<ol class=\"compact-list\">" + "".join(f"<li><code>{e(item)}</code></li>" for item in items) + "</ol>"


def e(value: object) -> str:
    return html.escape(str(value), quote=True)


if __name__ == "__main__":
    raise SystemExit(main())
