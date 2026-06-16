# AI Gateway

Singdata AI Gateway is an enterprise-grade AI gateway service that provides unified multi-model API management, intelligent routing and scheduling, BYOK model integration, and usage analytics—helping enterprises simplify multi-vendor LLM integration with a single connection that can call all models.

![](.topwrite/assets/anim-12-ai-gateway.svg)

## Access Methods

AI Gateway supports two access scenarios:

**Pre-configured clients (zero configuration, ready out of the box)**: The following clients have AI Gateway integration built in with no additional configuration required:

| Client | Purpose |
|--------|------|
| [Lakehouse SQL](AI_function_in_SQL.md) | Call `AI_COMPLETE()` / `AI_EMBEDDING()` directly in SQL |
| [Data Analytics Agent](datagpt_introduction.md) | Natural language conversational data analysis |
| [Data Engineering Agent](dataagent.md) | Natural language ETL development, task management, and ops diagnostics |
| [cz-cli](setup_cz_cli.md) | CLI command line / MCP tool interface |
| [Singclaw](https://www.singclaw.ai/) | Desktop intelligent agent that understands your business |

Using Lakehouse SQL as an example, simply call `AI_COMPLETE()` or `AI_EMBEDDING()` directly in SQL to use all enabled models:

```sql
-- Text generation, sentiment analysis, translation, summarization...
SELECT AI_COMPLETE('gw:qwen-max', CONCAT('Summarize in one sentence: ', content))
FROM articles;

-- Vectorization for semantic search and RAG
SELECT AI_EMBEDDING('gw:text-embedding-v3', text)
FROM documents;
```

**Custom Agent (one Endpoint + one API Key)**: Use the standard OpenAI SDK, replace `base_url` and `api_key`, no other code changes needed:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://<your-instance>.singdata.com/ai-gateway/v1",
    api_key="<your-api-key>",
)
response = client.chat.completions.create(
    model="moonshotai/kimi-k2.6",
    messages=[{"role": "user", "content": "hello"}],
)
```

## What I Want to Do

| Goal | Where to Go |
|------|--------|
| Understand AI Gateway features and positioning | [Product Introduction](Introduction.md) |
| Complete setup and call the first model in 10 minutes | [Quick Start](quickstart.md) |
| View supported models and pricing | [Model Pricing](pricing-ai-gateway.md) |
| Integrate your own third-party model (BYOK) | [Product Introduction → BYOK](Introduction.md) |
| Manage API Keys, set usage limits | [Product Introduction → API Key Management](Introduction.md) |
| Call LLMs in SQL for data analysis | [Call LLMs in SQL](lakehouse-ai-sql-analysis.md) |
| Analyze images in SQL | [Analyze Images in SQL](lakehouse-multimodal-ai-pipeline.md) |

## Core Capabilities at a Glance

**Unified access**: One API endpoint to call models from 20+ providers including Qwen, DeepSeek, GLM, Kimi, Doubao, GPT, Claude, Gemini, etc. 100% OpenAI interface compatible; existing code only needs endpoint and key replaced.

**Intelligent routing**: Automatically selects the optimal model by price, latency, and throughput, with support for automatic failover and load balancing.

**BYOK**: Bring your own third-party API Key; billing goes directly to the vendor account with no additional platform charges.

**Usage control**: Track token consumption by API Key, team, and project dimensions, with support for limits and alerts, and real-time cost breakdown viewing.

## Quick Start

→ [Complete initial setup and call your first model in 10 minutes](quickstart.md)
