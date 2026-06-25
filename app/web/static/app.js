const modeButtons = document.querySelectorAll(".mode-card");
const panels = {
  work: document.querySelector("#work-panel"),
  scrum: document.querySelector("#scrum-panel"),
  kickoff: document.querySelector("#kickoff-panel"),
  health: document.querySelector("#health-panel"),
  feedback: document.querySelector("#feedback-panel-main"),
};
const result = document.querySelector("#result");
const loading = document.querySelector("#loading");
const loadingStep = document.querySelector("#loading-step");
const feedbackBox = document.querySelector("#feedback-box");
const feedbackStatus = document.querySelector("#feedback-status");

let currentMode = "work";
let lastPayload = null;
let lastResult = null;

const loadingSteps = [
  "입력 내용을 정리하고 있습니다.",
  "관련 파일과 회의 신호를 찾고 있습니다.",
  "위험과 승인 항목을 확인하고 있습니다.",
  "작업 정리본을 만들고 있습니다.",
];

modeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const mode = button.dataset.mode;
    currentMode = mode;
    modeButtons.forEach((item) => item.classList.toggle("active", item === button));
    Object.entries(panels).forEach(([key, panel]) => panel.classList.toggle("active", key === mode));
    feedbackBox.classList.add("hidden");
    result.className = "result empty";
    result.innerHTML = `<h2>${button.querySelector("span").textContent}</h2><p>${button.querySelector("small").textContent}</p>`;
  });
});

document.querySelector("#work-submit").addEventListener("click", () => runRequest("work"));
document.querySelector("#scrum-submit").addEventListener("click", () => runRequest("scrum"));
document.querySelector("#kickoff-submit").addEventListener("click", () => runRequest("kickoff"));
document.querySelector("#health-submit").addEventListener("click", () => runRequest("health"));
document.querySelector("#feedback-review-submit").addEventListener("click", () => runRequest("feedback"));
document.querySelector("#feedback-submit").addEventListener("click", submitFeedback);

async function runRequest(mode) {
  setBusy(true);
  feedbackBox.classList.add("hidden");
  try {
    const payload = payloadFor(mode);
    const response = await fetch(endpointFor(mode), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "요청 처리 중 오류가 발생했습니다.");
    }
    lastPayload = payload;
    lastResult = data;
    renderResult(mode, data);
    if (mode !== "feedback") {
      showFeedbackBox();
    }
  } catch (error) {
    result.className = "result";
    result.innerHTML = `
      <h2>오류가 발생했습니다.</h2>
      <p>프로젝트 폴더 경로, 입력 내용, 설치 상태를 확인하세요.</p>
      <pre>${escapeHtml(error.message)}</pre>
    `;
  } finally {
    setBusy(false);
  }
}

function setBusy(isBusy) {
  document.querySelectorAll(".primary, .secondary").forEach((button) => (button.disabled = isBusy));
  loading.classList.toggle("hidden", !isBusy);
  clearInterval(window.__ccLoadingTimer);
  if (!isBusy) return;
  let index = 0;
  loadingStep.textContent = loadingSteps[index];
  window.__ccLoadingTimer = setInterval(() => {
    index = (index + 1) % loadingSteps.length;
    loadingStep.textContent = loadingSteps[index];
  }, 850);
}

function endpointFor(mode) {
  return {
    work: "/api/work-handoff",
    scrum: "/api/scrum-notes",
    kickoff: "/api/kickoff",
    health: "/api/health-check",
    feedback: "/api/feedback-review",
  }[mode];
}

function payloadFor(mode) {
  if (mode === "work") {
    return {
      repo_path: value("#work-repo"),
      task_request: value("#work-task"),
      forbidden_rules: value("#work-rules"),
      top_k: Number(value("#work-top-k") || 8),
      retriever_mode: value("#work-retriever"),
      handoff_target: "ai_tool",
      input_mode: value("#work-input-mode"),
    };
  }
  if (mode === "scrum") {
    return {
      meeting_text: value("#scrum-text"),
      project_context: value("#scrum-context"),
      instructor_feedback: value("#scrum-feedback"),
    };
  }
  if (mode === "kickoff") {
    return {
      topic: value("#kickoff-topic"),
      idea_notes: value("#kickoff-notes"),
      deadline: value("#kickoff-deadline"),
      constraints: value("#kickoff-constraints"),
      team_context: "",
    };
  }
  if (mode === "health") {
    return {
      status_text: value("#health-text"),
      project_context: value("#health-context"),
      deadline: value("#health-deadline"),
      my_scope: value("#health-scope"),
    };
  }
  return {
    feedback_root: value("#feedback-root") || "outputs/feedback",
  };
}

function value(selector) {
  return document.querySelector(selector).value.trim();
}

function renderResult(mode, data) {
  if (mode === "work") return renderWork(data);
  if (mode === "scrum") return renderScrum(data);
  if (mode === "kickoff") return renderKickoff(data);
  if (mode === "health") return renderHealth(data);
  return renderFeedbackReview(data);
}

function renderWork(data) {
  const token = data.token_budget;
  const issue = data.github_issue;
  const understanding = data.request_understanding;
  const files = data.relevant_files || [];
  result.className = "result";
  result.innerHTML = tabs([
    {
      title: "요약",
      body: `
        <h2>작업 정리본 생성 완료</h2>
        <div class="metric-grid">
          <div class="metric"><span>스캔 파일</span><strong>${data.summary.scanned_file_count}</strong></div>
          <div class="metric"><span>위험도</span><strong>${issue.risk_level}</strong></div>
          <div class="metric"><span>자동 시작</span><strong>${issue.auto_start_allowed ? "허용" : "차단"}</strong></div>
          <div class="metric"><span>토큰 추정 감소</span><strong>${formatPercent(token.estimated_reduction_percent)}</strong></div>
        </div>
        <p><strong>요청 의도:</strong> ${intentLabel(understanding.intent)} / 확신도 ${escapeHtml(understanding.confidence_label)}</p>
        <div class="read-order">
          <strong>처음 볼 순서</strong>
          <ol>
            <li><strong>먼저 볼 파일</strong>에서 기대한 파일이 잡혔는지 확인합니다.</li>
            <li><strong>위험/승인</strong>에서 건드리면 안 되는 영역이 있는지 확인합니다.</li>
            <li><strong>AI에게 넘길 지시문</strong>을 Claude, Codex, ChatGPT에 복붙합니다.</li>
            <li>왜 이런 결과가 나왔는지 궁금하면 <strong>작업 흐름</strong>을 봅니다.</li>
          </ol>
        </div>
      `,
    },
    {
      title: "먼저 볼 파일",
      body: `
        <h2>먼저 볼 파일</h2>
        <p>AI나 팀원에게 작업 범위를 좁혀주기 위한 후보입니다. 사람이 전부 읽으라는 뜻은 아닙니다.</p>
        <ol class="file-list">${files.map(renderFile).join("") || "<li>관련 파일이 없습니다.</li>"}</ol>
      `,
    },
    {
      title: "작업 흐름",
      body: renderGraphTrace(data.graph_trace),
    },
    {
      title: "AI 지시문",
      body: `<h2>AI에게 넘길 지시문</h2><pre>${escapeHtml(data.sections.ai_handoff_prompt)}</pre>`,
    },
    {
      title: "팀원용 정리",
      body: `<h2>팀원 작업 가이드</h2>${markdownish(data.sections.teammate_brief)}`,
    },
    {
      title: "내일의 나",
      body: `<h2>내일 이어서 볼 메모</h2>${markdownish(data.sections.future_me_letter)}`,
    },
    {
      title: "위험/승인",
      body: `
        <h2>위험과 승인 체크</h2>
        ${riskList(data.risk_findings)}
        <h3>사람이 확인할 것</h3>
        ${list(data.approval_checklist)}
      `,
    },
    {
      title: "GitHub 이슈",
      body: `
        <h2>${escapeHtml(issue.title)}</h2>
        <p><strong>추천 브랜치:</strong> <code>${escapeHtml(issue.recommended_branch)}</code></p>
        <pre>${escapeHtml(issue.body)}</pre>
      `,
    },
  ]);
}

function renderScrum(data) {
  result.className = "result";
  result.innerHTML = tabs([
    { title: "요약", body: `<h2>회의록 정리본</h2><p>${escapeHtml(data.source_summary)}</p>` },
    { title: "결정/질문", body: `<h2>결정사항</h2>${list(data.decisions)}<h3>열린 질문</h3>${list(data.open_questions)}` },
    { title: "다음 작업", body: `<h2>다음 작업</h2>${list(data.next_actions)}<h3>막힌 점</h3>${list(data.blockers)}` },
    { title: "역할 논의", body: `<h2>역할 논의 질문</h2>${list(data.role_discussion_questions)}<p>자동 배정이 아니라 회의에서 확인할 질문입니다.</p>` },
    { title: "이슈 초안", body: renderIssues(data.issue_drafts) },
    { title: "Markdown", body: `<pre>${escapeHtml(data.markdown)}</pre>` },
  ]);
}

function renderKickoff(data) {
  result.className = "result";
  result.innerHTML = tabs([
    { title: "MVP 범위", body: `<h2>${escapeHtml(data.one_line_pitch)}</h2><h3>MVP</h3>${list(data.mvp_scope)}<h3>제외</h3>${list(data.out_of_scope)}` },
    { title: "작업 흐름", body: `<h2>작업 흐름</h2>${list(data.workstreams)}<h3>리스크</h3>${list(data.risks)}` },
    { title: "질문", body: `<h2>열린 질문</h2>${list(data.open_questions)}<h3>역할 논의</h3>${list(data.role_discussion_questions)}` },
    { title: "제출 체크", body: `<h2>제출 체크리스트</h2>${list(data.submission_checklist)}` },
    { title: "이슈 초안", body: renderIssues(data.issue_drafts) },
    { title: "Markdown", body: `<pre>${escapeHtml(data.markdown)}</pre>` },
  ]);
}

function renderHealth(data) {
  result.className = "result";
  result.innerHTML = tabs([
    {
      title: "점수",
      body: `
        <h2>프로젝트 준비도</h2>
        <p>${escapeHtml(data.summary)}</p>
        <div class="metric-grid">
          <div class="metric"><span>MVP 준비도</span><strong>${data.mvp_completion_percent}%</strong></div>
          <div class="metric"><span>프로토타입</span><strong>${data.prototype_completion_percent}%</strong></div>
          <div class="metric"><span>안정성</span><strong>${escapeHtml(data.stability_label)}</strong></div>
          <div class="metric"><span>내 파트 여부</span><strong>${ownershipLabel(data.ownership_status)}</strong></div>
        </div>
      `,
    },
    {
      title: "부족한 회의",
      body: `<h2>부족한 회의 항목</h2>${list(data.missing_meeting_items)}<h3>다음 회의 질문</h3>${list(data.next_meeting_questions)}`,
    },
    {
      title: "내 파트 확인",
      body: `<h2>내 파트인지 확인</h2>${list(data.ownership_notes)}<h3>확인 질문</h3>${list(data.ownership_questions)}`,
    },
    {
      title: "근거",
      body: `<h2>MVP 신호</h2>${signals(data.mvp_signals)}<h2>프로토타입 신호</h2>${signals(data.prototype_signals)}`,
    },
    {
      title: "Markdown",
      body: `<pre>${escapeHtml(data.markdown)}</pre>`,
    },
  ]);
}

function renderFeedbackReview(data) {
  result.className = "result";
  result.innerHTML = tabs([
    {
      title: "요약",
      body: `
        <h2>피드백 리뷰</h2>
        <div class="metric-grid">
          <div class="metric"><span>피드백 수</span><strong>${data.feedback_count}</strong></div>
          <div class="metric"><span>공통 문제</span><strong>${(data.common_issues || []).length}</strong></div>
          <div class="metric"><span>파일 미스</span><strong>${(data.missed_file_cases || []).length}</strong></div>
          <div class="metric"><span>작업 흐름 피드백</span><strong>${(data.workflow_trace_questions || []).length}</strong></div>
        </div>
      `,
    },
    { title: "공통 문제", body: `<h2>공통 문제</h2>${issueList(data.common_issues)}` },
    { title: "작업 흐름", body: `<h2>작업 흐름 피드백</h2>${list(data.workflow_trace_questions)}` },
    { title: "다음 패치", body: `<h2>다음 패치 우선순위</h2>${list(data.next_patch_priorities)}` },
    { title: "회귀 테스트", body: `<h2>회귀 테스트 후보</h2>${list(data.regression_test_candidates)}` },
    { title: "Markdown", body: `<pre>${escapeHtml(data.markdown)}</pre>` },
  ]);
}

async function submitFeedback() {
  if (!lastResult || !lastPayload) {
    feedbackStatus.textContent = "먼저 결과를 생성한 뒤 피드백을 저장할 수 있습니다.";
    return;
  }
  setBusy(true);
  try {
    const response = await fetch("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(buildFeedbackPayload()),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "피드백 저장 중 오류가 발생했습니다.");
    }
    feedbackStatus.textContent = `저장 완료: ${data.output_dir}`;
  } catch (error) {
    feedbackStatus.textContent = `저장 실패: ${error.message}`;
  } finally {
    setBusy(false);
  }
}

function buildFeedbackPayload() {
  return {
    version: "0.2.6",
    mode: currentMode,
    project_name: value("#feedback-project"),
    repo_path: lastPayload.repo_path || "",
    repo_type: "",
    request_text: requestTextForFeedback(),
    expected_files: splitList(value("#feedback-expected")),
    actual_top_files: actualFilesForFeedback(),
    risk_result: riskForFeedback(),
    token_evidence: tokenForFeedback(),
    result_order_feedback: value("#feedback-result-order"),
    workflow_trace_feedback: value("#feedback-workflow"),
    confusing_part: value("#feedback-confusing"),
    reuse_willingness: value("#feedback-reuse"),
    notes: value("#feedback-notes"),
    screenshot_note: "",
  };
}

function requestTextForFeedback() {
  return lastPayload.task_request || lastPayload.meeting_text || lastPayload.idea_notes || lastPayload.status_text || "";
}

function actualFilesForFeedback() {
  if (!lastResult.relevant_files) return [];
  return lastResult.relevant_files.slice(0, 8).map((file) => file.path);
}

function riskForFeedback() {
  if (lastResult.github_issue) {
    return `${lastResult.github_issue.risk_level} / auto_start=${lastResult.github_issue.auto_start_allowed}`;
  }
  return "";
}

function tokenForFeedback() {
  const token = lastResult.token_budget;
  if (!token) return "";
  return `${formatPercent(token.estimated_reduction_percent)} / ${token.method} / ${token.verification_status}`;
}

function splitList(text) {
  return text
    .split(/[,\n]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function showFeedbackBox() {
  feedbackBox.classList.remove("hidden");
  feedbackStatus.textContent = "";
}

function tabs(items) {
  const id = `tabs-${Date.now()}`;
  const buttons = items.map((item, index) => `<button class="tab-button ${index === 0 ? "active" : ""}" data-tab="${id}-${index}">${escapeHtml(item.title)}</button>`).join("");
  const panels = items.map((item, index) => `<section id="${id}-${index}" class="tab-panel ${index === 0 ? "active" : ""}">${item.body}</section>`).join("");
  setTimeout(() => {
    document.querySelectorAll(`#result .tab-button`).forEach((button) => {
      button.addEventListener("click", () => {
        document.querySelectorAll(`#result .tab-button`).forEach((item) => item.classList.remove("active"));
        document.querySelectorAll(`#result .tab-panel`).forEach((item) => item.classList.remove("active"));
        button.classList.add("active");
        document.getElementById(button.dataset.tab).classList.add("active");
      });
    });
  });
  return `<div class="tabs">${buttons}</div>${panels}`;
}

function renderFile(file) {
  return `
    <li>
      <code>${escapeHtml(file.path)}</code>
      <div class="hint">${kindLabel(file.kind)} / lines ${escapeHtml(file.lines)} / score ${Number(file.score).toFixed(2)}</div>
      <details>
        <summary>미리보기</summary>
        <div>${escapeHtml(file.preview)}</div>
      </details>
    </li>
  `;
}

function riskList(findings) {
  if (!findings || findings.length === 0) return "<p>위험 경고가 없습니다.</p>";
  return `<ul class="plain-list">${findings.slice(0, 12).map((item) => `<li><strong>${escapeHtml(item.level)}</strong> / ${escapeHtml(item.kind)}: ${escapeHtml(item.reason)} ${item.path ? `(<code>${escapeHtml(item.path)}</code>)` : ""}</li>`).join("")}</ul>`;
}

function renderIssues(issues) {
  if (!issues || issues.length === 0) return "<p>이슈 초안이 없습니다.</p>";
  return issues.map((issue) => `<article><h3>${escapeHtml(issue.title)}</h3><pre>${escapeHtml(issue.body)}</pre></article>`).join("");
}

function signals(items) {
  return `<ul class="plain-list">${items.map((item) => `<li><strong>${item.detected ? "있음" : "부족"}</strong> ${escapeHtml(item.name)} (+${item.weight})${item.evidence.length ? `<br><span class="hint">${escapeHtml(item.evidence.join(" / "))}</span>` : `<br><span class="hint">${escapeHtml(item.missing_message)}</span>`}</li>`).join("")}</ul>`;
}

function issueList(items) {
  if (!items || items.length === 0) return "<p>반복된 문제가 아직 없습니다.</p>";
  return `<ul class="plain-list">${items.map((item) => `<li><strong>${escapeHtml(item.category)}</strong> (${item.count}) - ${escapeHtml(item.summary)}${item.evidence.length ? `<br><span class="hint">${escapeHtml(item.evidence.join(" / "))}</span>` : ""}</li>`).join("")}</ul>`;
}

function renderGraphTrace(trace) {
  if (!trace || !trace.steps) {
    return "<h2>작업 흐름</h2><p>그래프 추적 정보가 없습니다.</p>";
  }
  const steps = trace.steps
    .map(
      (step) => `
        <li class="graph-step graph-${escapeHtml(step.status)}">
          <div>
            <strong>${escapeHtml(step.label)}</strong>
            <span class="status-pill status-${escapeHtml(step.status)}">${statusLabel(step.status)}</span>
          </div>
          <p>${escapeHtml(step.summary)}</p>
          ${step.evidence && step.evidence.length ? `<details><summary>상세 근거 보기</summary>${renderGraphEvidence(step.evidence)}</details>` : ""}
          ${step.next_action ? `<p class="hint">다음 행동: ${escapeHtml(step.next_action)}</p>` : ""}
        </li>
      `
    )
    .join("");
  return `
    <h2>작업 흐름</h2>
    <p>이 탭은 Context Capsule이 어떤 순서로 판단했는지 보여줍니다. 처음에는 요약, 먼저 볼 파일, 위험/승인 탭을 보고, 이유가 궁금할 때 이 탭을 확인하세요.</p>
    <div class="metric-grid">
      <div class="metric"><span>최종 상태</span><strong>${statusLabel(trace.final_status)}</strong></div>
      <div class="metric"><span>현재 단계</span><strong>${nodeLabel(trace.current_node)}</strong></div>
    </div>
    <ol class="graph-list">${steps}</ol>
    <h3>안전 메모</h3>
    ${list(trace.safety_notes)}
  `;
}

function renderGraphEvidence(items) {
  if (!items || items.length === 0) return "<p>없음</p>";
  return `<ul class="plain-list">${items.map((item) => `<li>${formatGraphEvidence(item)}</li>`).join("")}</ul>`;
}

function formatGraphEvidence(item) {
  const text = String(item ?? "");
  const [key, ...rest] = text.split("=");
  const value = rest.join("=");
  if (!value) return escapeHtml(text);
  const labels = {
    scanned_file_count: "스캔 파일 수",
    intent: "요청 의도",
    confidence: "확신도",
    target_hints: "대상 힌트",
    protected_hints: "보호 영역",
    include_extensions: "포함할 파일 형식",
    exclude_extensions: "제외할 파일 형식",
    question: "확인 질문",
    used_mode: "사용한 검색 방식",
    requested_mode: "요청한 검색 방식",
    path: "후보 파일",
    risk_level: "위험도",
    findings: "위험 신호 수",
    block_reason: "차단 이유",
    sections: "생성 섹션",
    handoff_prompt_tokens: "프롬프트 추정 토큰",
    estimated_reduction: "추정 감소율",
    auto_start_allowed: "자동 시작",
    recommended_branch: "추천 브랜치",
    labels: "이슈 라벨",
    save: "저장 옵션",
    output_dir: "저장 폴더",
    reason: "이유",
  };
  const label = labels[key] || key;
  return `<strong>${escapeHtml(label)}:</strong> ${escapeHtml(value)}`;
}

function statusLabel(status) {
  return {
    completed: "완료",
    skipped: "건너뜀",
    blocked: "차단",
    needs_input: "질문 필요",
  }[status] || status;
}

function nodeLabel(nodeId) {
  return {
    scan_repository: "레포 스캔",
    understand_request: "요청 해석",
    retrieve_context: "관련 파일 찾기",
    analyze_risk: "위험 확인",
    generate_packet: "작업 정리본 생성",
    review_gate: "사람 승인 확인",
    save_output: "출력 저장",
  }[nodeId] || nodeId || "-";
}

function list(items) {
  if (!items || items.length === 0) return "<p>없음</p>";
  return `<ul class="plain-list">${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function markdownish(text) {
  return `<pre>${escapeHtml(text)}</pre>`;
}

function ownershipLabel(status) {
  return {
    likely_my_part: "내 파트 가능성 높음",
    possibly_other_part: "다른 파트 가능성",
    needs_confirmation: "확인 필요",
  }[status] || status;
}

function kindLabel(kind) {
  return {
    doc: "문서",
    code: "코드",
    config: "설정",
    test: "테스트",
    unknown: "기타",
  }[kind] || kind;
}

function intentLabel(intent) {
  return {
    documentation_edit: "문서 수정",
    bug_fix: "버그 조사",
    feature_addition: "기능 추가",
    metric_validation: "지표 검증",
    launcher_bug_investigation: "로컬 실행 문제",
    general: "일반 요청",
  }[intent] || intent;
}

function formatPercent(value) {
  return `${Number(value || 0).toFixed(1)}%`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
