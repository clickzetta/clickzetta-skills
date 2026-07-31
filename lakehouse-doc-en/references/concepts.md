# Singdata Lakehouse

Singdata Lakehouse is a fully managed, cloud-native lakehouse data platform with a newly designed vectorized SQL compute engine. It achieves leading results on the [TPC-DS 10TB](tpcds-benchmark.md), [TPC-H 100GB](tpch-benchmark.md), and [SSB 100GB](ssb-benchmark.md) benchmarks. The platform features a proprietary [Generic Incremental Computation (GIC)](incremental-computing.md) model that unifies batch and stream processing under the same incremental computation paradigm: Dynamic Tables defined with standard SQL automatically detect upstream changes and refresh incrementally.

Lakehouse architecture resolves the split between data storage and data processing, but the AI era introduces a new problem: vector stores, LLM calls, and unstructured data processing live outside the data platform, leaving AI teams and data teams using separate tools on the same data. Singdata defines this direction as **[AI Lakehouse](lakehouseai-overview.md)**: GIC-driven incremental refresh lets AI processing results flow back into the data pipeline in real time rather than staying in an external system; AI capabilities become native to the data platform and run within the same platform as data processing.

The platform is delivered as SaaS and is currently available on Amazon Web Services (Beijing), Alibaba Cloud (East China - Shanghai), and Tencent Cloud (East China - Shanghai, North China - Beijing, South China - Guangzhou). You can sign up on demand without managing infrastructure. See [Supported Cloud Platforms and Regions](supported-cloud-platforms.md).

```youtube
<iframe width="560" height="315" src="https\://www\.youtube.com/embed/b31IX3TowpU?si=xgA49XkMr\_ZOaBt4" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
```


## Architecture Overview

For the past several years, data platforms served two audiences: **humans** (data analysts and engineers operating through [Studio](lakehouse-studio-101.md)) and **applications** (business systems accessing data through JDBC/API). That assumption is changing.

As AI coding tools like ChatGPT, Claude, Cursor, and Codex become widespread, more organizations are letting AI Agents participate directly in data work — automatically generating ETL tasks, analyzing data quality, diagnosing slow queries, and answering business questions. This is not a future trend; it is happening now.

AI Agent involvement in data work is fundamentally different from human involvement: **humans can read UIs, read documentation, and apply experience; an Agent can only operate through programmatic interfaces. It does not know which table and column holds "GMV," it cannot tolerate "the data is from yesterday," and its concurrent requests can surge to hundreds within seconds.** Adding a CLI tool to an old platform does not solve this — it requires rethinking the data platform on four levels:

- **Programmable interfaces**: Traditional platform Web UIs are designed for humans. Having an Agent operate them is like having a person click on screenshots — slow and unreliable. Singdata provides [cz-cli](setup_cz_cli.md) for AI Agents: deterministic command formats, structured output, and complete data warehouse operation coverage, letting tools like Codex, Claude Code, Cursor, and Kiro complete full workflows for creating tables, writing SQL, submitting tasks, and viewing logs.
- **Real-time data**: Agents need current state when executing tasks: is inventory sufficient? Is the order paid? If data comes from yesterday's batch snapshot, Agent decisions are built on stale information and are untrustworthy. GIC-driven Dynamic Tables give the entire data warehouse pipeline minute-level freshness, so Agents see current state, not yesterday's snapshot.
- **Understandable semantics**: Facing bare table schemas, an Agent can only guess field meanings: does "order_amt" include or exclude tax? What is the definition of "active_user"? [Semantic Views](semantic-view-overview.md) build a business semantic layer on top of physical tables, centrally defining business concepts like "GMV" and "active users" so Agents generate accurate SQL.
- **Elastically scalable compute**: Human concurrent access to a data platform is limited, but AI Agents can simultaneously issue dozens or hundreds of concurrent queries. With storage-compute separation, Analytics clusters support automatic horizontal scale-out in response to concurrent load and automatic scale-in when demand subsides, with expansion latency measured in seconds and no impact on online services.

Today, Singdata Lakehouse serves three user types, each treated as a primary user group:

- **Human**: operates through [Studio](lakehouse-studio-101.md) Web interface, covering data development, scheduling, analysis Notebooks, and [Data Analytics Agent](datagpt_introduction.md) conversational querying
- **App**: connects through JDBC, Python SDK, MySQL protocol, or REST API, using Lakehouse as the application data backend
- **AI Agent**: connects through [cz-cli](setup_cz_cli.md), autonomously completing data warehouse development, operations, and data consumption

In addition to external AI Agents connecting through `cz-cli`, Singdata provides two built-in Data Agents:

- **[Data Engineering Agent](dataagent.md)**: focused on production data engineering workflows, addressing task development, scheduling and publishing, run monitoring, quality governance, and engineering troubleshooting.
- **[Data Analytics Agent](datagpt_introduction.md)**: focused on analytics consumption and semantic governance, addressing analytics domain configuration, metric semantics, natural language querying, and analytics result consumption.

These two are not redundant — they are upstream and downstream of each other: the first builds and runs the data engineering pipeline; the second turns those data assets into queryable, analyzable, consumable business analytics capabilities.

![](/.topwrite/assets/01-architecture_1779606768355.svg)

From a vertical perspective, data is persisted in the bottom-most object storage layer, managed through metadata and federation layers, organized into various tables and pipelines in the data object layer, processed by the SQL compute engine, and ultimately exposed to all three user types through the access layer.

The following three sections explain Singdata's underlying architectural choices in storage, compute, and data freshness. Programmable interfaces, semantic capabilities, multimodal storage, and other AI-layer capabilities are covered in the AI Lakehouse section.

---

## Technical Foundation

### Lakehouse Architecture

Most enterprise data architectures face the same dilemma: raw data lives in a data lake (low cost, flexible formats, but slow queries and weak governance) while processed data lives in a data warehouse (high performance, strong governance, but high cost and closed formats). Two systems mean two storage layers, two permission systems, two metadata catalogs, and endless data sync pipelines — moving data from lake to warehouse and back, with delays and errors as constants. The proliferation of AI applications makes the split worse: BI consumes structured data in the warehouse, AI applications need raw files in the lake, and the same business data requires two copies.

Singdata Lakehouse unifies structured tables, semi-structured data, and unstructured files on a single platform: they share the same SQL engine, metadata service, and permission system. Data is stored once; BI and AI read from the same table. The SQL compute engine features the proprietary [Generic Incremental Computation (GIC)](incremental-computing.md) model, unifying batch and stream processing under the same incremental computation paradigm. Dynamic Tables automatically detect upstream changes and refresh incrementally.

GIC is the underlying engine driving Dynamic Tables. Traditional incremental computation approaches degrade to full recompute when they encounter JOINs, nested subqueries, or UPDATE/DELETE operations. GIC decomposes any standard SQL into operator-level incremental plans — Filter, Join, Aggregate, and Window all support incremental execution. GIC has three core properties: **generality** (no restriction on query complexity), **cost awareness** (each refresh dynamically selects between incremental and full execution plans, automatically falling back to full refresh when the incremental data volume is too large), and **semantic consistency** (based on MVCC version management, incremental results are strictly consistent with full recompute, guaranteeing Exactly-Once semantics).

The storage layer is built on Apache Iceberg. Singdata engineers are the leading contributors to [Apache Iceberg's C++ implementation (iceberg-cpp)](https://github.com/apache/iceberg-cpp) and led its core development from zero to production-ready. Singdata engineers serve as Apache Iceberg Committers and are PMC members of Apache Arrow, Apache ORC, and Apache Parquet. Singdata Lakehouse is among the earliest lakehouse products to fully support Iceberg V3 (Deletion Vectors, Row Lineage, VARIANT type). Deletion Vectors reduce write amplification in UPDATE/DELETE-intensive scenarios (such as CDC writes and GDPR deletes) without requiring full data file rewrites. Row Lineage makes each row's origin traceable and supports fine-grained auditing. The VARIANT type natively supports semi-structured data, enabling nested JSON queries without predefined schemas.

![](/.topwrite/assets/00-lakehouse-unified.svg)

**What this means for you**: BI reports and AI applications no longer each maintain a separate copy of the data — both read from the same table, with permissions and metadata managed under a single system. Historical data in Hive, Delta Lake, and Hudi is directly queryable through External Tables; existing data assets don't need migration to join the new platform. A single SQL can process both raw files in object storage and processed wide tables. BI and AI data definitions are aligned for the first time.

### Storage-Compute Separation

Traditional data warehouses couple storage and compute: ETL, BI queries, and AI inference all share the same physical machines — one large job saturating the CPU causes all other queries to queue. Scaling compute requires scaling storage simultaneously, making cost waste unavoidable.

Singdata Lakehouse persists data to object storage (S3 / OSS / COS) while compute is handled by independent [VClusters](compute-overview.md), completely decoupled. **Data has one copy; compute can have any number** — multiple VClusters simultaneously read and write the same data without interfering with each other, each independently scaling and billing. When there are no queries, compute clusters suspend and stop billing, but data remains always accessible.

The compute layer is divided into three cluster types by workload. GP and AP scale differently because their workload characteristics differ: ETL batch processing has large per-task resource requirements but low concurrency, making vertical scaling (larger nodes) more effective; BI queries have small per-task resource requirements but high concurrency, requiring horizontal scaling (more instances) to linearly increase throughput.

- **[General Purpose (GP)](compute-overview.md)**: ETL batch processing, Dynamic Table incremental refresh, AI_COMPLETE/Embedding and other AI compute tasks. Jobs share fair-scheduled resources; supports vertical elastic scaling.
- **[Analytics (AP)](compute-overview.md)**: BI reports, ad-hoc queries, high-concurrency online analytics, and latency-sensitive AI inference scenarios. Jobs have dedicated resources; supports multi-instance horizontal scaling with built-in result cache acceleration.
- **[Integration](compute-overview.md)**: offline batch sync and CDC real-time sync share one cluster, completely isolated from query traffic.

AI Agent proliferation places higher demands on elastic scaling. AI Agents can simultaneously issue dozens or hundreds of concurrent queries, far exceeding the concurrency ceiling of manual access. With storage-compute separation, Analytics clusters support automatic horizontal instance scale-out in response to concurrent load, and automatic scale-in when demand subsides, with expansion latency measured in seconds — no data migration required.

![](/.topwrite/assets/02-compute-separation_1779606809686.svg)

**What this means for you**: Compute and storage bill and scale independently: when business data volume grows, only scale compute; when query load is low, suspend compute clusters and stop billing — data remains always online. Batch jobs and BI queries use their own independent clusters and do not contend for resources. When AI Agents begin accessing the data platform concurrently, Analytics clusters automatically scale horizontally to handle peaks and scale back in when demand subsides — no manual intervention, no data migration.

### Unified Real-time and Batch Processing

In traditional data architectures, real-time pipelines use Flink and batch pipelines use Spark — two codebases, two operations teams, and the same business metric written twice in two different places, with results that frequently diverge. The deeper problem: even if the ODS layer receives real-time CDC, the downstream DWD and DWS layers are still T+1 batch jobs — the entire pipeline's freshness is determined by its slowest node. AI Agents executing tasks need current state; overnight batch snapshots make Agent decisions based on stale information.

Singdata Lakehouse uses [Dynamic Tables](dynamic_table_summary.md) to enable incremental refresh throughout the entire processing pipeline. Most incremental computation approaches degrade to full recompute when they encounter JOIN or UPDATE/DELETE operations; GIC is designed for generality — it decomposes the execution of any SQL into operator-level incremental plans, with Filter, Join, Aggregate, and Window all supporting incremental execution, each operator processing only the changed portion from upstream. A Dynamic Table defines one SQL; GIC automatically detects upstream table changes and computes only the incremental portion. ODS → DWD → DWS → ADS — every layer is a Dynamic Table, every layer automatically triggers after the upstream refresh, with end-to-end freshness measured in minutes. Whether upstream writes are scheduled batch or real-time CDC stream, the downstream processing logic is identical — one codebase covers both scenarios.

Traditional full-recompute cost scales proportionally to total data volume. Dynamic Tables process only the incremental data since the last refresh; refresh duration is proportional to the amount of change, putting the cost of minute-level refreshes in an entirely different category from full recompute. GIC does not statically bind to an incremental plan; each refresh dynamically selects the execution mode based on data statistics — when the incremental data volume is too large it automatically falls back to full refresh, always at optimal cost, without human intervention.

Dynamic Tables support three scheduling modes, switchable without modifying the SQL: **real-time trigger** (compute immediately on upstream data change, second-level latency, suited for risk control and monitoring), **periodic scheduling** (batch processing at minute/hour intervals, suited for most near-real-time scenarios), and **DAG dependency trigger** (automatically trigger downstream after an upstream Dynamic Table refresh completes; only configure leaf nodes — the entire pipeline automatically chains together).

![](/.topwrite/assets/03-unified-pipeline_1779606830577.svg)

**What this means for you**: You can replace a combination of Kafka + Spark Streaming + ClickHouse (5 components) with a single Singdata Lakehouse, reducing storage and compute costs as well as operational complexity. Data warehouse layering logic is written once and reused for both batch and real-time processing, so you do not need to maintain separate logic in two systems with numbers that frequently diverge. Dynamic Table minute-level refresh raises the freshness of the entire processing pipeline at the same time: AI Agents see current business state, not yesterday's batch snapshot.

---

## AI Lakehouse

The three technical foundations solve the data platform's own problems, but a larger gap remains unresolved: **the gap between the data platform and AI systems.** Data must be repeatedly moved between two systems, vector stores and data warehouses each maintain separate permissions and metadata, and AI processing results cannot flow directly back into the data processing pipeline.

Singdata AI Lakehouse's answer: instead of building an AI system alongside the data platform, make AI capabilities native to the data platform. AI capabilities cover four layers:

**1. Unified Model Infrastructure**

**[AI Gateway](aigateway.md)** is the enterprise's unified LLM access point: one endpoint and one key provide access to 20+ provider models. It is compatible with both OpenAI and Anthropic interfaces and supports intelligent routing, BYOK (billing goes directly to providers), and per-key, team, or project usage governance. All AI capabilities below share the same model governance: RBAC permission isolation, call rate limiting, token usage statistics, and multi-tenant cost allocation.

**2. AI and Semantic Capabilities within Lakehouse**

**[AI Functions](ai_function_in_sql.md)** bring LLM capabilities into the SQL engine: data never leaves the platform, and no Python is required. A single SQL statement can perform translation, sentiment analysis, classification, information extraction, PII masking, embedding, and multimodal (image/audio) processing. This also applies to unstructured data (contracts, images, work orders) in [Volumes](volume-overview.md); results are written directly into Lakehouse tables for BI and AI to consume from the same source.

The same table natively supports scalar, text, and vector data types with their corresponding indexes. A single SQL can simultaneously filter scalars, perform full-text search, and retrieve by semantic similarity — no need to maintain separate Elasticsearch or vector databases. See [Full-Text Search and Vector Hybrid Search Best Practices](rrf-fulltext-vector-hybrid-search-best-practices.md).

**[Semantic Views](semantic-view-overview.md)** establish a semantic abstraction layer between physical tables and business analytics, centrally defining table relationships, dimensions, and metrics — solving the "same metric, different results" inconsistency problem at its root. They also serve as the semantic foundation that enables AI Agents to answer queries stably and accurately — Agents understand business concepts like "active users" and "GMV" through Semantic Views rather than guessing field meanings from bare table schemas.

**3. Agents for Different Audiences**

**[Data Analytics Agent](datagpt_introduction.md)** serves business users. Its value goes beyond "natural language data queries" — it includes the analytics domain isolation, unified metric definitions, row-level permissions, and auditing that make large models give trustworthy results in a governed enterprise context rather than freely accessing all data.

**[Data Engineering Agent](dataagent.md)** serves data engineers. It covers the full cycle of development, scheduling, publishing, operations, and diagnostics. It is not a conversational SQL generator — it follows an "explore, converge, then execute" approach, with built-in confirmation and impact scope checks as safety boundaries for change operations and high-impact actions.

**[SingClaw](https://www.singclaw.ai/)** targets business owners (especially e-commerce and solo operators) as a desktop, memory-enabled, proactive data Agent. After connecting data, no dashboard setup is required — it proactively reads data and pushes a "business briefing" each day, directly telling you what went wrong, why, and what to do first today. Built on the OpenClaw kernel with enhancements for memory, security, scenarios, and workspaces.

**4. Two Connection Paths for AI Agents to Access Lakehouse**

**[cz-cli](setup_cz_cli.md)** is the command-line entry point and Sub-Agent designed for the Agent era. Compared to JDBC (requires injecting massive schemas), MCP (tool descriptions consume large amounts of context), and REST (requires multi-step assembly), cz-cli is self-describing and discoverable, maps one command to one complete business action, has minimal context overhead, and supports acting as an independent sub-Agent for complex data tasks. Claude Code, Cursor, Kiro, and other AI coding tools can use cz-cli to complete full data warehouse development and operations workflows.

**[MCP Server (Studio-hosted)](MCPServers.md)** connects with zero deployment. No need to build a service process — just create a token to let Claude Desktop, Cherry Studio, and other general AI clients directly operate Lakehouse data, tasks, and operations capabilities, with deep integration into actual Studio workflows (including CDC, data quality, composite tasks, and more).

**Overall value**: Data is stored once; BI reports and AI applications read from the same table with unified permissions and metadata. AI processing results flow back into the data pipeline in real time through GIC incremental refresh. From data integration and processing to AI handling and analytics consumption, the entire pipeline closes within one platform, and data teams do not need to switch tools or maintain multiple systems.

---

## Lakehouse Studio

Singdata chose an integrated approach from the start of product design, bringing the complete lifecycle of data development into a single platform so ingestion, development, scheduling, operations, and governance share the same metadata and permission system. [Studio](lakehouse-studio-101.md) was built alongside the compute engine, not as an add-on module.

Studio's main modules:

- **Data Sync**: offline batch sync and CDC real-time sync for 40+ data sources, configurable visually without writing code
- **Task Development and Scheduling**: SQL / Python / Shell tasks managed together, DAG dependency orchestration, with support for backfill and reruns
- **Operations Monitoring**: instance logs, run alerts, resource usage — diagnose issues without leaving the platform
- **Data Catalog**: metadata management, data lineage, data quality rules — governance and development in one entry point
- **Analysis Notebook**: interactive SQL and Python analysis, results can directly feed BI

Quick start: [Lakehouse Studio Getting Started Guide](lakehouse-studio-101.md)

---

## Core Object Relationships

Relationships between data objects:

![](/.topwrite/assets/04-object-relationship_1779606899090.svg)

- **[Dynamic Table](dynamic-table.md)**: define one SQL; the system automatically detects upstream table changes and refreshes incrementally. Suited for building ODS→DWD→ADS data pipelines. Does not depend on Table Stream.
- **[Table Stream](table_stream.md)**: an independent CDC capture mechanism that records each row's insert/update/delete changes for downstream custom consumption. Suited for scenarios where fine-grained control over MERGE logic is needed.
- Both originate from Tables and are parallel paths — choose one based on your scenario.

Dynamic Table incremental computation is driven by Singdata's proprietary GIC (Generic Incremental Computation) model, supporting second-level triggering, minute-interval periodic scheduling, and DAG dependency triggers. It is defined with standard SQL, with no stream processing framework to learn. See [Incremental Computation and Dynamic Tables](incremental-computing.md).

---

## Typical Use Cases

### Enterprise Knowledge Base and RAG Systems

Store unstructured documents (contracts, research reports, work orders, product manuals) in [Volumes](volume-overview.md), batch vectorize them with `AI_EMBEDDING()`, write the results into the same table, and build an inverted index for precise keyword matching. At retrieval time, a single SQL statement retrieves semantically similar content (Vector Index) and exact-match specialized terms (Inverted Index), fuses rankings with the RRF algorithm, and then calls `AI_COMPLETE()` to generate an answer. The entire RAG pipeline runs within Lakehouse without maintaining a separate vector database or Elasticsearch.

Reference: [Full-Text Search and Vector Hybrid Search Best Practices](rrf-fulltext-vector-hybrid-search-best-practices.md)

### Real-time Data Backend for AI Applications

AI applications depend on real-time business state when executing tasks: is inventory sufficient? Is the order paid? Is the user profile updated? Use CDC real-time sync to write business database changes into Lakehouse, use Dynamic Tables to refresh the DWD/DWS layer at minute intervals, and use [Semantic Views](semantic-view-overview.md) to define metrics consistently. AI applications query Semantic Views through REST API or JDBC and receive business-readable, minute-level fresh, accurate results rather than overnight batch snapshots.

Reference: [Semantic Views](semantic-view-overview.md)

### AI Agent-Driven Autonomous Data Engineering

Use Claude Code, Cursor, or Codex AI coding tools to operate Lakehouse directly through [cz-cli](setup_cz_cli.md): describe requirements and let the Agent assist with creating tables, writing ETL SQL, submitting scheduled tasks, viewing run logs, and locating performance bottlenecks. Whether direct execution is possible depends on current permissions, tool exposure, and confirmation workflows. Data warehouse development is progressively shifting from "people write code" to "people describe goals, Agents assist with execution."

Reference: [cz-cli Setup Guide](setup_cz_cli.md)

### Replace Spark or Traditional Big Data Architecture

Migrate existing Spark ETL jobs to Lakehouse, replace Spark Streaming with Dynamic Tables, and replace PySpark scripts with SQL tasks. There is no Spark cluster to maintain, compute is pay-as-you-go, and overall costs are lower.

Reference: [Spark SQL Migration Guide](migration-spark-sql.md)

### Real-time Data Platform

Use multi-table real-time sync (CDC) to write business database changes into Lakehouse in real time, then build an ODS→DWD→ADS layered data pipeline with Dynamic Tables refreshing at minute intervals — replacing a Flink + data warehouse dual-pipeline Lambda architecture.

Reference: [Real-time Pipeline Selection Guide](realtime-pipeline-selection-guide.md)

### Connected Vehicle / IoT Data Platform

High-volume device data is continuously written through Kafka; Dynamic Tables aggregate device state and alert metrics in real time; Analytics clusters support high-concurrency online queries. One architecture covers real-time ingestion, processing, and analytics end to end. Abnormal device data is processed through AI Functions for pattern recognition, and results are written back into structured tables for real-time consumption by operations Agents.

---

## Ecosystem Compatibility

Singdata Lakehouse natively supports Apache Iceberg format and can directly read and write Delta Lake, Hudi, and Paimon through External Tables — no migration required for existing data lake assets. For compute ecosystems, [Spark Connector](spark-connector-summary.md) and [Flink Connector](flink-write-connector.md) are available for smooth integration with existing big data pipelines. BI tools including FineReport, Tableau, Superset, Metabase, and PowerBI have all completed integration certification.

---

## About the Names

You will see two names used interchangeably in the documentation: **Singdata** and **ClickZetta**. Both refer to the same product, used in different contexts:

- **Singdata** — the product brand name, used in the console interface, technical support, and new documentation
- **ClickZetta** — the brand registered in the open-source community, used in the GitHub organization (`github.com/clickzetta`), PyPI package names (`dbt-clickzetta`), JDBC driver class names (`com.clickzetta.client.jdbc.ClickZettaDriver`), and other technical identifiers. Also appears in some older documentation and historical blog posts.

When you encounter "ClickZetta Lakehouse" in documentation, treat it as "Singdata Lakehouse."

---

## Where to Start

| Your goal | Recommended starting point |
|---------|---------|
| Understand all platform concept definitions | [Key Concepts](key-concepts.md) |
| Try your first complete hands-on workflow | [Quick Start](lakehouse-quick-experience_guide.md) |
| Explore the full AI Lakehouse picture | [AI Lakehouse](lakehouseai-overview.md) |
| Build RAG or vector search | [Full-Text Search and Vector Hybrid Search Best Practices](rrf-fulltext-vector-hybrid-search-best-practices.md) |
| Understand AI data analytics capabilities | [Data Analytics Agent Quick Tour](lakehousedatagpt-tour.md) |
| Let AI Agents operate the data warehouse | [cz-cli Setup Guide](setup_cz_cli.md) |
| Learn common SQL commands | [SQL Reference](sql-reference.md) |
| Design data models and object relationships | [Object Model Design](object_model_design.md) |
