const modeButtons = document.querySelectorAll(".mode-card");
const panels = {
  work: document.querySelector("#work-panel"),
  scrum: document.querySelector("#scrum-panel"),
  kickoff: document.querySelector("#kickoff-panel"),
  health: document.querySelector("#health-panel"),
};
const result = document.querySelector("#result");
const loading = document.querySelector("#loading");
const loadingStep = document.querySelector("#loading-step");

const loadingSteps = [
  "입력 내용을 정리하고 있습니다.",
  "관련 파일과 회의 신호를 찾고 있습니다.",
  "위험과 누락 항목을 확인하고 있습니다.",
  "결과 패킷을 만들고 있습니다.",
];

modeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const mode = button.dataset.mode;
    modeButtons.forEach((item) => item.classList.toggle("active", item === button));
    Object.entries(panels).forEach(([key, panel]) => panel.classList.toggle("active", key === mode));
    result.className = "result empty";
    result.innerHTML = `<h2>${button.querySelector("span").textContent}</h2><p>${button.querySelector("small").textContent}</p>`;
  });
});

document.querySelector("#work-submit").addEventListener("click", () => runRequest("work"));
document.querySelector("#scrum-submit").addEventListener("click", () => runRequest("scrum"));
document.querySelector("#kickoff-submit").addEventListener("click", () => runRequest("kickoff"));
document.querySelector("#health-submit").addEventListener("click", () => runRequest("health"));

async function runRequest(mode) {
  setBusy(true);
  try {
    const response = await fetch(endpointFor(mode), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payloadFor(mode)),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "요청 처리 중 오류가 났습니다.");
    }
    renderResult(mode, data);
  } catch (error) {
    result.className = "result";
    result.innerHTML = `
      <h2>오류가 났습니다.</h2>
      <p>프로젝트 폴더 경로, 입력 내용, 설치 상태를 확인하세요.</p>
      <pre>${escapeHtml(error.message)}</pre>
    `;
  } finally {
    setBusy(false);
  }
}

function setBusy(isBusy) {
  document.querySelectorAll(".primary").forEach((button) => (button.disabled = isBusy));
  loading.classList.toggle("hidden", !isBusy);
  if (!isBusy) return;
  let index = 0;
  loadingStep.textContent = loadingSteps[index];
  clearInterval(window.__ccLoadingTimer);
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
  return {
    status_text: value("#health-text"),
    project_context: value("#health-context"),
    deadline: value("#health-deadline"),
    my_scope: value("#health-scope"),
  };
}

function value(selector) {
  return document.querySelector(selector).value.trim();
}

function renderResult(mode, data) {
  if (mode === "work") return renderWork(data);
  if (mode === "scrum") return renderScrum(data);
  if (mode === "kickoff") return renderKickoff(data);
  return renderHealth(data);
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
        <h2>작업 패킷 생성 완료</h2>
        <div class="metric-grid">
          <div class="metric"><span>스캔 파일</span><strong>${data.summary.scanned_file_count}</strong></div>
          <div class="metric"><span>위험도</span><strong>${issue.risk_level}</strong></div>
          <div class="metric"><span>자동 시작</span><strong>${issue.auto_start_allowed ? "허용" : "차단"}</strong></div>
          <div class="metric"><span>토큰 추정 감소</span><strong>${formatPercent(token.estimated_reduction_percent)}</strong></div>
        </div>
        <p><strong>요청 의도:</strong> ${escapeHtml(understanding.intent)} / 확신도 ${escapeHtml(understanding.confidence_label)}</p>
        <p><strong>다음에 볼 것:</strong> 먼저 관련 파일이 맞는지 확인하고, Risk & Approval에서 위험 경고를 봅니다.</p>
      `,
    },
    {
      title: "관련 파일",
      body: `
        <h2>먼저 볼 파일</h2>
        <p>AI나 팀원에게 작업 범위를 좁혀주기 위한 후보입니다. 사람이 전부 읽으라는 뜻은 아닙니다.</p>
        <ol class="file-list">${files.map(renderFile).join("") || "<li>관련 파일이 없습니다.</li>"}</ol>
      `,
    },
    {
      title: "AI용 프롬프트",
      body: `<h2>AI에게 줄 프롬프트</h2><pre>${escapeHtml(data.sections.ai_handoff_prompt)}</pre>`,
    },
    {
      title: "팀원용",
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
      title: "GitHub Issue",
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
    { title: "요약", body: `<h2>회의록 패킷</h2><p>${escapeHtml(data.source_summary)}</p>` },
    { title: "결정/질문", body: `<h2>결정사항</h2>${list(data.decisions)}<h3>열린 질문</h3>${list(data.open_questions)}` },
    { title: "다음 작업", body: `<h2>다음 작업</h2>${list(data.next_actions)}<h3>막힌 점</h3>${list(data.blockers)}` },
    { title: "역할 논의", body: `<h2>역할 논의 질문</h2>${list(data.role_discussion_questions)}<p>자동 배정이 아니라 회의에서 확인할 질문입니다.</p>` },
    { title: "Issue 초안", body: renderIssues(data.issue_drafts) },
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
    { title: "Issue 초안", body: renderIssues(data.issue_drafts) },
    { title: "Markdown", body: `<pre>${escapeHtml(data.markdown)}</pre>` },
  ]);
}

function renderHealth(data) {
  result.className = "result";
  result.innerHTML = tabs([
    {
      title: "점수판",
      body: `
        <h2>프로젝트 준비도</h2>
        <p>${escapeHtml(data.summary)}</p>
        <div class="metric-grid">
          <div class="metric"><span>MVP 준비도</span><strong>${data.mvp_completion_percent}%</strong></div>
          <div class="metric"><span>프로토타입</span><strong>${data.prototype_completion_percent}%</strong></div>
          <div class="metric"><span>안정도</span><strong>${escapeHtml(data.stability_label)}</strong></div>
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
      <div class="hint">${escapeHtml(file.kind)} / lines ${escapeHtml(file.lines)} / score ${Number(file.score).toFixed(2)}</div>
      <div>${escapeHtml(file.preview)}</div>
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

