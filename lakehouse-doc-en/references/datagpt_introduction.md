# Conversational Data Analysis (Analytics Agent)

Analytics Agent (formerly known as DataGPT) is a built-in conversational data analysis product in Singdata Lakehouse. Business users ask questions in natural language, and the system automatically generates SQL, executes queries, returns charts and insights — no coding required. Data developers improve Q&A accuracy by configuring a semantic layer (metrics, business terms, knowledge documents, answer builders).

![](.topwrite/assets/anim-13-analytics-agent.svg)

## When to Use

| Scenario | Suitable? |
|------|----------|
| Business users querying data and viewing trends via natural language | ✅ Core use case |
| Quickly generating AI dashboards without writing SQL | ✅ |
| Automatic anomaly detection and alerting | ✅ |
| Scheduled data report delivery | ✅ |
| Precise SQL logic control, complex ETL | ❌ Use Studio SQL tasks |
| Vector search / RAG Q&A | ❌ Use [Vector Search](vector_search_ai.md) + [AI Functions](AI_function_in_SQL.md) |

## Quick Start

**① Activate the service** (1 minute)

Find the Analytics Agent product card on the management center homepage and click "Free Activation". New users are recommended to check "Also activate a Lakehouse instance as the default data source" — the system will automatically configure sample data.

**② Try with sample data** (5 minutes)

Go to the product homepage, find the analysis domain marked "Sample", click "Start Analysis", and ask questions in natural language:

- "What is the average second-hand housing price by district?"
- "Which district has the highest listing volume?"
- "Generate a housing price trend dashboard for me"

**③ Connect your own data** (as needed, completed by data developers)

Add a data source → Create an analysis domain → Configure the semantic layer → Start conversational analysis.

Supported data source types:

| Type | Data Source |
|------|--------|
| Data Warehouse / Lakehouse | Lakehouse (default), Databricks |
| Relational Database | MySQL, StarRocks |
| Files | Excel, CSV upload |

→ [Detailed steps in the Quick Start guide](datagpt_quickstart.md)

## Core Concepts

### Analysis Domain

An analysis domain is the workspace for Q&A, organizing data tables, the semantic layer, and knowledge documents together. It is recommended to create separate analysis domains for different business domains (sales, finance, operations) to reduce cross-domain interference while supporting domain-level data permission isolation.

### Semantic Layer

The semantic layer is key to improving Q&A accuracy. It includes four capabilities:

| Capability | Purpose | When to Use |
|------|------|----------|
| **Schema Description** (table/column descriptions, aliases) | Helps the model understand field meanings and business names | When the model selects the wrong table/column, or field names are ambiguous |
| **Metrics** | Pre-defines precise calculation definitions | When core business metrics need unified definitions |
| **Answer Builders** | Provides fixed SQL templates | For complex multi-table JOINs and fixed calculation logic |
| **Knowledge Documents** | Provides business context, rules, and terminology | When the model does not understand industry terms or business rules |

You can also configure **domain prompts** (role settings, answer standards, business constraints) and **row-level permissions** (control data visibility by user).

### Data Assets

* **Data Tables**: Structured data from Lakehouse, Databricks, MySQL, StarRocks, and other data sources, or uploaded Excel / CSV files
* **Dashboards**: AI-generated visual panels based on the semantic layer, supporting scheduled refresh and version management
* **Knowledge Base**: Document collections supporting RAG retrieval, organized with folders and linked to analysis domains

### User Roles

The responsibilities of the two user types are clearly separated — data developers are responsible for "making data analyzable", and business analysts are responsible for "using data to make decisions":

| Role | Responsibilities | Not Responsible For |
|------|-----------|-------------|
| **Data Developer** | Add data sources, create analysis domains, configure semantic layer (Schema description, metrics, answer builders, knowledge documents), set row-level permissions, optimize Q&A accuracy | Daily queries and data exploration |
| **Business Analyst** | Ask questions in natural language, view charts, generate and share dashboards, submit Q&A feedback | Data source integration, semantic layer configuration |

## How It Works

Analytics Agent uses an Agentic RAG architecture — not a simple "vector retrieval + generation" approach, but one where the LLM actively plans and reasons:

1. **Understand intent**: Interprets the user's question, determining which tables to query, which metrics to read, and which documents to reference
2. **Active orchestration**: Autonomously decides whether to execute a SQL query, read a file, or check a metric definition
3. **Iterative refinement**: Self-corrects when initial results are insufficient, performing multi-step reasoning until the answer is complete and accurate

This enables Analytics Agent to handle multi-hop queries (e.g., "the reason for the sales decline" requires correlating order data and market reports simultaneously).

All LLM models used by Analytics Agent are provided by **[AI Gateway](AIGateway.md)**. AI Gateway handles unified model integration, call routing, and usage management — Analytics Agent does not require a separate model API Key. To switch the underlying model or manage usage, do so in AI Gateway.

## Related Documentation

| Document | Description |
|------|------|
| [Quick Start](datagpt_quickstart.md) | Get started with Analytics Agent in 5 minutes |
| [Data Source Management](datagpt_data_source.md) | Add and manage data sources |
| [User Guide](datagpt_tutorial.md) | Data source configuration, semantic layer setup, dashboard creation |
| [Q&A Accuracy Improvement](answer-accuracy-improve.md) | Detailed explanation of 4 semantic layer capabilities and best practices |
| [AI Gateway](AIGateway.md) | LLM model integration, routing and usage management |
| [Lakehouse DataGPT Tour](LakehouseDataGPT-tour.md) | Feature demo videos and screenshots |

For suggestions or questions, contact us: **Phone** 400-6767-862 · **Email** service@singdata.com

^
