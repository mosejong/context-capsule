# Future Direction

Context Capsule should grow as a handoff system, not as an uncontrolled auto-coding bot.

The product direction is:

```text
conversation / task / error
-> repository context
-> relevant files and risks
-> reviewable work packet
-> human approval
-> AI tool, teammate, or future-me execution
```

## Near-Term Priorities

### 1. Stabilize v0.2 Meeting Modes

Prepare the next demo path:

- Scrum Notes Mode demo
- Project Kickoff Mode demo
- issue draft examples
- team-lead safety boundary
- v0.2 release notes when the feature set is cut

### 2. Discord Input Adapter

Convert meeting decisions into work packets.

Initial behavior:

- accept pasted Discord meeting text or command payload
- extract decision, task, file hints, and constraints
- generate a packet
- preview a GitHub Issue dry-run

Do not auto-merge or auto-deploy.

### Implemented v0.2 Step: Text-Based Scrum/Kickoff

Before Discord automation, Context Capsule now supports text input:

- Scrum Notes Mode
- Project Kickoff Mode
- issue drafts from meeting text
- team-lead notes
- no teammate scoring
- no automatic assignment

This gives the project a safe path for 3rd-project use before adding Discord API permissions or meeting recording workflows.

### 3. External Token-analyzer Adapter

Keep the current provider boundary:

- `ApproxLocalTokenUsageProvider`
- future external provider

The goal is to compare:

- raw prompt tokens
- capsule tokens
- actual provider usage when available
- reduction rate

### 4. Hybrid Retrieval

Improve retrieval quality with:

- keyword/path scoring
- mandatory include rules for mentioned files
- optional local hash embeddings
- optional sentence-transformers model path
- Chroma or FAISS persistent index
- per-file-type chunking

v0.1.1 improved the keyword/path baseline first. v0.2 adds optional hybrid retrieval without making external models mandatory. Persistent Chroma/FAISS indexing remains a future upgrade.

The user should still be able to run No-AI Mode without external APIs.

### 5. Closed Network Bundle

Support restricted environments:

- no external AI API required
- local scan/retrieval/risk/Markdown generation works
- optional local embedding or local LLM install
- credentials and `.env` never included in packets

### 6. Packaging Upgrade

v0.1.0 is a Python/Streamlit ZIP.

Future packaging options:

- PyInstaller executable
- Windows installer
- local FastAPI service
- desktop shell

## Long-Term Vision

Meeting-to-execution:

```text
Discord idea meeting
-> decision fixed
-> Context Capsule packet
-> GitHub Issue dry-run
-> human approval
-> Claude/Codex/teammate starts with scoped context
```

The key rule stays the same:

```text
Automate preparation. Keep risky execution behind human approval.
```
