# LLM Tech Scan

Date: 2026-06-22

Purpose:

> Context Capsule에 붙일 최신 LLM, 로컬 런타임, 임베딩, vector DB, token analyzer 후보를 공식 문서 중심으로 조사하고, 프로젝트 적용 우선순위를 정리한다.

This is not a benchmark claim. It is a technology scouting note for architecture decisions.

## 1. What This Project Actually Needs

Context Capsule의 핵심은 거대한 LLM이 아니다.

필수 계층:

```text
Repo scan
→ Chunking
→ Retrieval
→ Risk analysis
→ Token budget analysis
→ Target-specific handoff generation
```

선택 계층:

```text
Embedding model
Vector DB
Local LLM provider
Cloud model adapter
```

중요한 결론:

- LLM은 MVP 필수 요소가 아니다.
- 먼저 검색/위험 분석/토큰 분석을 로컬 규칙으로 안정화한다.
- LLM은 요약, chat log 의도 추출, target별 문장 다듬기에만 선택적으로 붙인다.
- 특정 런타임에 종속하지 않고 provider adapter로 설계한다.

## 2. Frontier Cloud Models

외부 API 사용이 가능한 환경에서 AI handoff prompt의 품질을 검증할 때 참고한다.

| Provider | Current official direction | Context Capsule usage |
| --- | --- | --- |
| OpenAI | GPT-5.5 is positioned as flagship for complex reasoning/coding. GPT-5.4 mini/nano are lower-cost/latency variants. | 평가용 target model, prompt quality benchmark, token counting reference |
| Anthropic | Claude Fable 5 / Mythos 5 are top tier; Opus 4.8, Sonnet 4.6, Haiku 4.5 remain model family options. | Claude/Codex style handoff prompt target |
| Google Gemini | Gemini 3 family includes Pro/Flash/Flash-Lite variants and coding/agentic positioning. | long-context and coding-agent comparison target |
| Mistral | Mistral Medium 3.5, Small 4, Large 3, Devstral 2, Codestral, Codestral Embed appear in official model overview. | code model / embedding model comparison |
| DeepSeek | DeepSeek API lists V4 Flash and V4 Pro with OpenAI/Anthropic-compatible formats, thinking mode, tool calls, JSON output, FIM beta. | cheap API adapter candidate, but security/geopolitical review needed before enterprise use |

Project stance:

- Do not hard-code any cloud model into the core.
- Store model-specific handoff rules as templates.
- Let users select target style: `codex`, `claude_sonnet`, `claude_opus`, `gemini`, `local_llm`, `teammate`, `future_me`.

## 3. Open / Local Model Families

### Qwen

Qwen docs describe Qwen3 as a family with dense and MoE models, thinking/non-thinking modes, coding/tool-use strength, multilingual support, and local/deployment routes including llama.cpp, Ollama, SGLang, vLLM, TGI, and LM Studio.

Use in this project:

- Strong local/open model candidate for Korean/English mixed repo context.
- Good candidate for closed-network summarization after retrieval.
- Use only after retrieval has already narrowed context.

### Mistral

Mistral official docs list Mistral Small 4, Mistral Large 3, Mistral Medium 3.5, Devstral 2, Codestral, and Codestral Embed.

Use in this project:

- `Codestral Embed` is interesting for code-aware retrieval.
- `Devstral 2` is interesting for software engineering tasks.
- Mistral Small/Medium can be target models for cloud adapter experiments.

### Llama / Meta

Llama remains relevant for local/enterprise workflows, but first-pass project docs should avoid relying on non-official benchmark claims unless verified from official model cards or primary sources.

Use in this project:

- Keep as a possible local model family.
- Do not make it the default recommendation until model card, license, and runtime support are confirmed.

### DeepSeek

DeepSeek API docs list V4 Flash and V4 Pro with OpenAI-compatible and Anthropic-compatible endpoints.

Use in this project:

- Useful for low-cost API experiments and agent tool compatibility.
- Treat as external API, not closed-network mode.
- Require security/data handling review before recommending for private source code.

## 4. Local LLM Runtime / Serving Layer

Do not pick one runtime as the architecture.

Use this abstraction:

```text
LocalLLMProvider
  summarize(chunks) -> str
  extract_task(chat_log) -> str
  rewrite_for_target(prompt, target) -> str
```

| Runtime | Best fit | Notes |
| --- | --- | --- |
| llama.cpp | Offline GGUF execution, simple local/closed-network deployment | Strong default for 폐쇄망 bundle design |
| Ollama | Quick local UX, model pull/run, simple REST API | Convenience layer; not core architecture |
| vLLM | High-throughput GPU serving, OpenAI-compatible server, production serving | Good for lab/server benchmark, overkill for MVP |
| SGLang | Production serving for large language/multimodal models, low-latency/high-throughput focus | Good for later GPU serving comparison |
| Hugging Face TGI | Established LLM serving toolkit, now maintenance mode and recommends vLLM/SGLang/local engines for future direction | Do not prioritize for new implementation |

Decision:

- MVP: no local LLM dependency.
- Closed network prototype: prefer llama.cpp-compatible provider first.
- Ollama: optional adapter only.
- GPU server demo: compare vLLM/SGLang later.

## 5. Embedding / Retrieval Layer

This layer matters more than local generation quality.

Goal:

> Find the right files before sending anything to a model.

Candidate embeddings:

| Candidate | Why it matters |
| --- | --- |
| multilingual-e5-small | Light multilingual baseline for Korean/English text |
| BGE-M3 / bge family | Strong retrieval baseline, multilingual candidate |
| Qwen embeddings | Useful if Qwen stack is selected |
| Codestral Embed | Interesting for code-specific semantic retrieval |
| OpenAI embeddings | Cloud benchmark, not closed-network default |
| TEI-served models | Production-ish embedding serving if GPU/server exists |

Recommended first implementation:

1. Keep keyword retriever.
2. Add embedding retriever behind an interface.
3. Compare `keyword`, `vector`, and `hybrid` output on the same task set.
4. Track top-k relevant-file hit rate.

## 6. Vector DB / Search Storage

| Tool | Best fit | Project use |
| --- | --- | --- |
| Chroma | Fast prototyping, metadata filtering, hybrid/dense/sparse retrieval support | First vector DB to try |
| FAISS | Fast local similarity search, minimal storage layer | Good closed-network/simple index candidate |
| Qdrant | Server-style vector DB with filtering, hybrid queries, local/cloud options | Later if API/server architecture grows |
| LanceDB | Embedded vector DB for local apps | Later candidate if file-based local UX matters |

Decision:

- Phase 2 start with Chroma because metadata/filtering and prototyping are convenient.
- Keep FAISS as closed-network fallback.
- Avoid overengineering DB before token analyzer is done.

## 7. Token Analyzer

This is the highest-value next feature.

Why:

- It makes the value measurable.
- It supports the claim that Context Capsule reduces unnecessary context.
- It helps decide how much retrieved context to include.

Implementation idea:

```text
raw_context_tokens = count_tokens(all_scanned_relevant_text)
retrieved_context_tokens = count_tokens(top_k_chunks)
capsule_tokens = count_tokens(final_markdown_or_prompt)
reduction = 1 - capsule_tokens / raw_context_tokens
```

Provider strategy:

- Use model-specific tokenizer when available.
- Fall back to approximate token estimation when not available.
- Mark estimates clearly as estimates.

## 8. Recommended Roadmap Update

Immediate:

1. Token analyzer integration.
2. Token Budget section in Streamlit.
3. Save `token_budget` in `CapsuleOutput`.
4. Add tests for token reduction calculation.

Next:

1. Embedding retriever interface.
2. Chroma prototype.
3. Hybrid keyword + vector search.
4. Retrieval quality test set.

Later:

1. Local LLM provider interface.
2. llama.cpp adapter.
3. Optional Ollama adapter.
4. vLLM/SGLang serving comparison.
5. Offline bundle.

## 9. Architecture Decision Record

Decision:

> Context Capsule will not depend on Ollama, OpenAI, Claude, Gemini, or any single model provider.

Rationale:

- Core value is context retrieval, compression, risk filtering, and token budgeting.
- Provider lock-in weakens closed-network and portfolio positioning.
- Local LLM quality varies by model, quantization, hardware, and runtime.
- Cloud model quality changes quickly.

Result:

- `LocalLLMProvider` and `CloudModelTarget` are adapters.
- Core pipeline remains deterministic and testable without an LLM.
- Model comparison becomes an evaluation feature, not an architecture dependency.

## 10. Sources

Official or primary sources checked:

- OpenAI model docs: https://platform.openai.com/docs/models
- Anthropic model overview: https://docs.anthropic.com/en/docs/about-claude/models/overview
- Google Gemini model docs: https://ai.google.dev/gemini-api/docs/models
- Mistral model overview: https://docs.mistral.ai/models/overview
- Qwen docs: https://qwen.readthedocs.io/en/latest/
- DeepSeek API docs: https://api-docs.deepseek.com/
- llama.cpp GitHub: https://github.com/ggml-org/llama.cpp
- vLLM docs: https://docs.vllm.ai/en/latest/
- SGLang docs: https://docs.sglang.ai/
- Hugging Face TGI docs: https://huggingface.co/docs/text-generation-inference/index
- Hugging Face TEI docs: https://huggingface.co/docs/text-embeddings-inference/index
- Chroma docs: https://docs.trychroma.com/docs/overview/introduction
- FAISS docs: https://faiss.ai/index.html
- Qdrant docs: https://qdrant.tech/documentation/overview/
