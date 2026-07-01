# AI Capabilities Overview

Singdata Lakehouse treats AI capabilities as native to the data platform rather than as an attached system. This overview explains four layers of AI products and how they relate to each other.

![](.topwrite/assets/anim-43-ai-capabilities.svg)

## 1. Unified model foundation: AI Gateway

All AI capabilities share a single model entry point.

**[AI Gateway](AIGateway.md)** — One endpoint, one key, to call 20+ provider LLMs (Alibaba Cloud Bailian, OpenAI, Anthropic, DeepSeek, Kimi, and others), compatible with both OpenAI and Anthropic interface standards. Supports smart routing, BYOK (billing flows directly to the provider), and usage control by key, team, or project. AI Functions, Data Engineering Agent, and Data Analytics Agent all share the same model governance mechanism.

## 2. AI and semantic capabilities inside Lakehouse

**[AI Functions](AI_function_in_SQL.md)** — LLM capabilities embedded in the SQL engine. Data never leaves the platform, and no Python is required. A single SQL statement handles:

| Function | Purpose |
|------|------|
| [AI_COMPLETE](ai_complete.md) | Free-form prompt calls for text generation, Q&A, and analysis |
| [AI_SUMMARIZE](ai_summarize.md) | Long-text summarization |
| [AI_TRANSLATE](ai_translate.md) | Multi-language translation |
| [AI_CLASSIFY](ai_classify.md) | Text classification |
| [AI_SENTIMENT](ai_sentiment.md) | Sentiment analysis |
| [AI_EXTRACT](ai_extract.md) | Structured information extraction |
| [AI_MASK](ai_mask.md) | PII masking |
| [AI_EMBEDDING](ai_embedding.md) | Vectorization |
| [AI_TRANSCRIBE](ai_transcribe.md) | Audio transcription |
| [AI_FIX_GRAMMAR](ai_fix_grammar.md) | Grammar correction |

A single Lakehouse table natively supports scalar, full-text, and vector indexes. One SQL statement can combine filter, full-text search, and semantic recall without attaching an external Elasticsearch or vector database:

- **[Vector search](vector_search_ai.md)** — HNSW-based vector index for semantic search, RAG recall, and recommendation. Structured data and vectors coexist in the same table; BI and AI consume the same source.
- **Full-text search** — Inverted index for keyword matching and multi-field search, suited for log analysis and document search.
- **[Hybrid search (vector + full-text RRF fusion)](rrf-fulltext-vector-hybrid-search-best-practices.md)** — A single SQL statement recalls both semantically similar and keyword-matched results, fused by RRF. Retrieval quality is better than either method alone.
- **[Multi-modal data retrieval](vector-and-scalar-retrieval-in-same-table.md)** — Scalar filter combined with vector recall, for example "find the most similar products within a given category."

**[Semantic View](semantic-view-overview.md)** — A semantic abstraction layer between physical tables and business analysis. It centralizes table relationships, dimensions, and metric definitions, resolving the metric consistency problem at the source. It also provides the stable, accurate semantic foundation that AI agents need to answer questions reliably.

## 3. Agents for different audiences

**[Data Analytics Agent](datagpt_introduction.md)** — Conversational analysis for business users. The value is not just "query data with natural language" — it also includes the analytics domain isolation, unified metric definitions, row-level permissions, and audit controls that are already in place, allowing the LLM to produce trusted results within a controlled enterprise context rather than accessing all data freely.

**[Data Engineering Agent](dataagent.md)** — A production workflow agent for data engineers, covering development, scheduling, publishing, operations, and diagnostics end to end. It follows an explore-first, converge-second, then-execute approach, with built-in confirmation and impact-scope checks for high-impact change operations.

**[SingClaw](https://www.singclaw.ai/)** — A desktop, memory-enabled, proactive data agent for business owners, especially in e-commerce and solo operations. After connecting your data, no dashboard setup is needed. It proactively pushes a daily "business brief" that tells you what went wrong, why, and the first thing you should do today.

## 4. Two channels for AI agents to access Lakehouse

**[cz-cli](setup_cz_cli.md)** — A command-line entry point and sub-agent designed for the agent era. Compared with JDBC (requires injecting large amounts of schema), MCP (tool descriptions consume large amounts of context), and REST (requires multi-step assembly), cz-cli is self-describing and discoverable, maps one command to one complete business action, and has minimal context overhead. It supports acting as an independent sub-agent for complex data tasks. AI coding tools such as Claude Code, Cursor, and Kiro can perform complete data warehouse development and operations workflows through cz-cli.

**[MCP Server (Studio-managed)](MCPServers.md)** — Connect without any deployment. Create a token and AI clients such as Claude Desktop and Cherry Studio can directly access Lakehouse data, tasks, and operations — no self-managed service process required.

## Capability relationships

```
AI Gateway (unified model foundation)
    ↓ Provides model services for all AI capabilities
    ├── AI Functions — use LLMs directly in SQL
    ├── Semantic View — provides a stable semantic layer for agents
    ├── Data Analytics Agent — conversational analysis for business users
    └── Data Engineering Agent — end-to-end agent for engineers

AI agent access channels
    ├── cz-cli — low-context, high-determinism command-line interface
    └── MCP Server — zero-deployment interface for general AI clients
```

## Related documentation

- [Lakehouse AI feature overview](LakehouseAI-overview.md) — Full technical reference for vector search, RAG, and multimodal
- [Data preparation for AI](server-data-for-ai.md) — How to organize and prepare Lakehouse data for AI applications
- [Ecosystem](ecosystem.md) — Integration with third-party AI frameworks (LangChain, LlamaIndex, Dify, and others)
