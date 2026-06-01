# Singdata Lakehouse Product Introduction

Singdata Lakehouse is a fully managed, cloud-native lakehouse data platform equipped with a newly designed vectorized SQL compute engine, delivering industry-leading performance on [TPC-DS 10TB](tpcds-benchmark.md), [TPC-H 100GB](tpch-benchmark.md), and [SSB 100GB](ssb-benchmark.md) benchmarks. The platform features a proprietary [Generic Incremental Computation (GIC)](incremental-computing.md) model that unifies batch and stream processing into a single incremental computation paradigm — Dynamic Tables defined with standard SQL automatically detect upstream changes and incrementally refresh.

Lakehouse unification solved the fragmentation between data storage and processing, but it did not solve the new challenges of the AI era: vector databases, LLM calls, and unstructured data processing remain outside the data platform, forcing AI teams and data teams to use two separate toolsets on the same data. Singdata defines this direction as **[AI Lakehouse](lakehouse-ai.md)** — GIC-driven incremental refresh allows AI processing results to flow back into the data processing pipeline in real time, rather than sitting in an external system; AI capabilities become native to the data platform, completing the full cycle within the same platform as data processing.

The platform is delivered as SaaS, currently available on Alibaba Cloud (East China Shanghai), Tencent Cloud (East China Shanghai, North China Beijing, South China Guangzhou), Amazon Cloud (Beijing), and more — on-demand activation, no infrastructure management required. See [Supported Cloud Platforms and Regions](supported-cloud-platforms.md).

## Architecture Overview

For years, data platforms served only two types of users: **humans** (data analysts and engineers operating through [Studio](lakehouse-studio-101.md)) and **applications** (business systems fetching data via JDBC/API). That assumption is breaking down.

With the rise of AI coding tools like ChatGPT, Claude, Cursor, and Codex, more and more enterprises are letting AI Agents directly participate in data work — automatically generating ETL tasks, analyzing data quality, diagnosing slow queries, and answering business questions. This is not a future trend; it is happening now.

But AI Agents participating in data work is fundamentally different from humans doing so: **humans can read UIs, consult documentation, and rely on experience; Agents can only operate through programmatic interfaces. They don't know which table and field "GMV" refers to. They cannot accept "the data is from yesterday." Their concurrent requests can surge to hundreds per second**. This cannot be solved by simply adding a CLI tool to an old platform — it requires the data platform to be redesigned at four levels:

* **Programmable interfaces**: Traditional platform Web UIs are designed for humans; having an Agent operate them is like asking someone to click on a screenshot — inefficient and unreliable. Singdata provides [cz-cli](setup_cz_cli.md) for AI Agents: deterministic command formats, structured output, and complete data warehouse operation coverage, enabling tools like Codex, Claude Code, Cursor, and Kiro to complete full workflows of table creation, SQL writing, task submission, and log inspection.
* **Real-time data**: When Agents execute tasks, they need current state — is inventory sufficient? Has the order been paid? If data is yesterday's batch snapshot, the Agent's decisions are built on stale information and cannot be trusted. GIC-driven Dynamic Tables refresh the entire warehouse processing pipeline in minutes, so Agents query current state, not yesterday's snapshot.
* **Understandable semantics**: Agents facing raw table structures can only guess at field meanings — does "order\_amt" include tax? What is the definition of "active\_user"? [Semantic Views](semantic-view-overview.md) build a business semantic layer on top of physical tables. Agents understand business concepts like "GMV" and "active users" through Semantic Views, generating SQL with accurate metric definitions.
* **Elastically scalable compute**: Human access to data platforms has limited concurrency, but AI Agents can simultaneously issue tens or even hundreds of concurrent queries. With storage-compute separation, analytical clusters support automatic horizontal scaling based on concurrent load, automatically scaling back when pressure subsides, with scale-out latency measured in seconds — no impact on online services.

Today, Singdata Lakehouse serves three types of users, each equally important as a first-class citizen:

* **Human**: Operates through the [Studio](lakehouse-studio-101.md) Web interface, covering data development, scheduling, analysis Notebooks, and [DataGPT](lakehousedatagpt-tour.md) conversational queries
* **App**: Connects via JDBC, Python SDK, MySQL protocol, REST API, using Lakehouse as the data backend for applications
* **AI Agent**: Connects via [cz-cli](setup_cz_cli.md), autonomously completing data warehouse development, operations, and data consumption

![](/.topwrite/assets/01-architecture_1779606768355.svg)

Vertically, data is persisted from the bottom-most object storage layer, unified through metadata and federation layers, organized into various tables and pipelines in the data object layer, driven by the SQL compute engine for processing, and finally exposed to all three user types through the access layer.

The following three sections explain Singdata's underlying architectural choices for storage, compute, and data freshness; programmable interfaces, semantic capabilities, multimodal storage, and other AI-layer capabilities are covered in the AI Lakehouse section.

***

## Technical Foundations

### Lakehouse Unification

Most enterprise data architectures face the same dilemma: raw data lives in a data lake (low cost, flexible formats, but slow queries and weak governance), while processed data lives in a data warehouse (high performance, strong governance, but high cost and closed formats). Two systems mean two storage layers, two permission systems, two metadata stores, and endless data sync pipelines — data moves from lake to warehouse and back, with delays and errors as constants. The proliferation of AI applications makes the fragmentation worse: BI consumes structured data from the warehouse, AI applications need raw files from the lake, and the same business data must be maintained in two copies.

Singdata Lakehouse unifies structured tables, semi-structured data, and unstructured files on a single platform: sharing the same SQL engine, metadata service, and permission system. Data is stored only once; BI and AI read from the same table. The SQL compute engine features a proprietary [Generic Incremental Computation (GIC)](incremental-computing.md) model that unifies batch and stream processing into a single incremental computation paradigm — Dynamic Tables automatically detect upstream changes and incrementally refresh.

GIC is the underlying engine driving Dynamic Tables. Traditional incremental computation approaches degrade to full recomputation when encountering JOINs, nested subqueries, or UPDATE/DELETE; GIC decomposes any standard SQL into operator-level incremental plans, with Filter, Join, Aggregate, and Window all supporting incremental execution. GIC has three core properties: **generality** (no restriction on query complexity), **cost-awareness** (dynamically selects incremental or full execution plan at each refresh based on data statistics, automatically falling back to full recomputation when incremental data volume is too large), and **semantic consistency** (based on MVCC version management, incremental results are strictly consistent with full recomputation, guaranteeing Exactly-Once semantics).

The storage layer is built on Apache Iceberg. Singdata engineers are the first contributors to the [Apache Iceberg C++ implementation (iceberg-cpp)](https://github.com/apache/iceberg-cpp), leading the core development of this official C++ library from scratch to production-ready. Singdata engineers serve as Apache Iceberg Committers and are PMC members of Apache Arrow, Apache ORC, and Apache Parquet. Singdata Lakehouse is one of the earliest lakehouse products to fully support Iceberg V3 (Deletion Vectors, Row Lineage, VARIANT type). Deletion Vectors dramatically reduce write amplification in UPDATE/DELETE-intensive scenarios (such as CDC writes and GDPR deletions), eliminating the need to rewrite entire data files; Row Lineage makes the origin of every row traceable, supporting fine-grained auditing; the VARIANT type natively supports semi-structured data, enabling queries on nested JSON without predefined schemas.

![](/.topwrite/assets/00-lakehouse-unified.svg)

**What this means for you**: BI reports and AI applications no longer each maintain a separate copy of data — both read from the same table, with permissions and metadata managed in a single system. Historical data in Hive, Delta Lake, and Hudi is directly queryable via external tables; existing data assets can be onboarded without migration. A single SQL can simultaneously process raw files in object storage and processed wide tables, aligning BI and AI data definitions for the first time.

### Storage-Compute Separation

Traditional data warehouses couple storage and compute: storage and compute are bound to the same machines, with ETL, BI queries, and AI inference sharing the same resources — one large job saturates the CPU and all other queries queue up; scaling compute requires scaling storage simultaneously, with unavoidable cost waste.

Singdata Lakehouse persists data to object storage (OSS / S3 / COS), with compute handled by independent [VClusters](compute-overview.md) — completely decoupled. **Data exists only once; compute can scale to any number of instances** — multiple VClusters simultaneously read and write the same data without interference, each independently scaling and billed separately. When there are no queries, compute clusters pause and stop billing, but data remains online and queryable at any time.

The compute layer is split into three cluster types by workload. GP and AP scale differently because their workload characteristics differ: ETL batch processing has high per-job resource requirements but low concurrency, making vertical scaling (larger nodes) more effective; BI queries have low per-job resource requirements but high concurrency, requiring horizontal scaling (more instances) to linearly increase throughput.

* [General Purpose (GP)](compute-overview.md): ETL batch processing, Dynamic Table incremental refresh, AI\_COMPLETE / Embedding and other AI compute tasks. Jobs share resources with fair scheduling; supports vertical elastic scaling
* [Analytical (AP)](compute-overview.md): BI reports, ad-hoc queries, high-concurrency online analytics, and latency-sensitive AI inference scenarios. Jobs have dedicated resources; supports multi-instance horizontal scaling with built-in result cache acceleration
* [Integration](compute-overview.md): Offline batch sync and CDC real-time sync share one cluster, completely isolated from query traffic

The proliferation of AI Agents places higher demands on elastic scaling. AI Agents can simultaneously issue tens or even hundreds of concurrent queries, far exceeding the concurrency limits of human operations. With storage-compute separation, analytical clusters support automatic horizontal instance scaling based on concurrent load, automatically scaling back when pressure subsides, with scale-out latency measured in seconds — no data migration involved.

![](/.topwrite/assets/02-compute-separation_1779606809686.svg)

**What this means for you**: Compute and storage are billed and scaled independently: when business data volume grows, only compute needs to scale; during query off-peak hours, compute clusters pause and stop billing while data remains online. Batch jobs and BI queries use separate independent clusters without competing for resources — a single large job cannot overwhelm all queries. When AI Agents begin concurrent access to the data platform, analytical clusters automatically scale out horizontally to handle peak load and scale back when pressure subsides — the entire process requires no manual intervention and no data migration.

### Unified Real-Time and Batch

In traditional data architectures, real-time pipelines use Flink and offline pipelines use Spark — two codebases, two operations teams, and the same business metric must be written twice in two places, with results that frequently diverge. The more fundamental problem: even if the ODS layer has real-time CDC, downstream DWD and DWS layers are still T+1 batch processing — the freshness of the entire pipeline is determined by its slowest node. When AI Agents execute tasks, they need current state; overnight batch snapshots cause Agents to make decisions based on stale information.

Singdata Lakehouse uses [Dynamic Tables](dynamic-table-introduce.md) to enable incremental refresh throughout the entire processing pipeline. Most incremental computation approaches degrade to full recomputation when encountering JOINs or UPDATE/DELETE; GIC's design goal is generality — decomposing the execution of any SQL into operator-level incremental plans, with Filter, Join, Aggregate, and Window all supporting incremental execution, each operator processing only the changed portion from upstream. Define a SQL in a Dynamic Table, and GIC automatically detects upstream table changes, computing only the incremental portion and refreshing the result. ODS → DWD → DWS → ADS — every layer is a Dynamic Table, every layer automatically triggers after upstream refresh, with end-to-end freshness measured in minutes. Whether upstream is scheduled batch writes or CDC real-time streams, downstream processing logic is identical — one codebase covers both scenarios.

The cost of traditional full recomputation is proportional to total data volume; Dynamic Tables process only the incremental data since the last refresh, with refresh time proportional to the volume of changes — minute-level refresh costs are not in the same order of magnitude as full recomputation. GIC does not statically bind incremental plans; instead, it dynamically selects the execution approach at each refresh based on data statistics — automatically falling back to full recomputation when incremental data volume is too large, always optimizing cost without manual intervention.

Dynamic Tables support three scheduling modes, switchable without modifying the SQL: **real-time trigger** (computes immediately on upstream data changes, second-level latency, suitable for risk control and monitoring), **periodic scheduling** (batch processing at minute/hour intervals, suitable for most near-real-time scenarios), and **DAG dependency trigger** (downstream automatically triggers after upstream Dynamic Table refresh completes; configure only leaf nodes and the entire pipeline chains automatically).

![](/.topwrite/assets/03-unified-pipeline_1779606830577.svg)

**What this means for you**: No more maintaining a dual-pipeline Lambda architecture with Flink + data warehouse; warehouse layering logic is written once and reused for both batch and real-time scenarios; AI Agents query processing results fresh to the minute; switching upstream data sources from batch to real-time CDC requires no changes to downstream Dynamic Tables.

***

## AI Lakehouse

The three technical foundations solve the data platform's own problems, but there is a larger fragmentation that remains unresolved: **the fragmentation between the data platform and AI systems**. Data must be repeatedly moved between two systems, vector databases and data warehouses each maintain separate permissions and metadata, and AI processing results cannot flow directly back into the data processing pipeline.

Singdata AI Lakehouse's answer: rather than building an AI system alongside the data platform, make AI capabilities native to the data platform. GIC is the key — precisely because incremental refresh is cheap enough, AI processing results can flow back into the data processing pipeline in real time, rather than sitting in an external system waiting for the next batch run. AI capabilities span four layers:

**Data Layer: Multimodal Storage + AI Processing**

The same table natively supports three data types and their corresponding indexes, with BI and AI reading from the same data:

![](/.topwrite/assets/22-multimodal_1779617786266.svg)

| Data type                             | Index               | Typical query                                             | Use case                                        |
| ------------------------------------- | ------------------- | --------------------------------------------------------- | ----------------------------------------------- |
| Scalar (numbers, strings, timestamps) | Bloomfilter index   | WHERE col = value · WHERE col IN (...)                    | BI reports, exact filtering                     |
| Text (articles, logs, reviews)        | Inverted index      | match\_any(col, 'keyword') · multi\_match(c1, c2, 'term') | Full-text search, log analysis                  |
| Vector (Embeddings)                   | Vector index (HNSW) | L2\_DISTANCE(vec, query\_vec) < threshold LIMIT K         | Semantic search, RAG retrieval, recommendations |

A single SQL can simultaneously filter scalar fields, match keywords, and retrieve semantically similar vectors, fusing rankings with the RRF algorithm — no need to separately maintain Elasticsearch or a vector database. See [Full-Text + Vector Hybrid Search Best Practices](rrf-fulltext-vector-hybrid-search-best-practices.md).

[AI Functions](ai_function_best_practice.md) embed LLM capabilities into the SQL engine, performing OCR, summarization, classification, and vectorization on unstructured data (contracts, images, tickets) in [Volumes](volume-overview.md), writing results directly into the table's vector or text columns for unified consumption by BI and AI.

**Understanding Layer: AI Reads Business Semantics**

[Semantic Views](semantic-view-overview.md) build a business semantic layer on top of physical tables, centralizing metric definitions and entity relationships. AI understands business concepts like "active users" and "GMV" through Semantic Views, rather than guessing at field meanings from raw table structures. [Data Analytics Agent (DataGPT)](lakehousedatagpt-tour.md) implements natural language data queries based on Semantic Views — users describe business questions, the Agent generates SQL, executes queries, and interprets results.

**Operations Layer: AI Autonomously Completes Warehouse Development**

[cz-cli](setup_cz_cli.md) is the standard interface for AI Agents to operate Lakehouse, encapsulating table creation, SQL writing, task submission, log inspection, and performance diagnostics as structured commands. **The Data Engineering Agent built into** [Studio](lakehouse-studio-101.md) participates directly in the development interface — understanding table structures and business context, automatically generating ETL SQL, debugging data quality issues, and explaining slow query causes. AI coding tools like Codex, Claude Code, Cursor, and Kiro can complete full data warehouse development and operations workflows through cz-cli.

**Governance Layer: Unified Management of AI Model Resources**

[AI Gateway (Model Management)](ai_gateway.md) is the enterprise's unified LLM access point, aggregating Alibaba Cloud Qwen, OpenAI, self-hosted models, and other sources. It provides RBAC permission isolation, call rate limiting, token usage statistics, and multi-tenant cost allocation — AI Functions and various Agents share the same model governance mechanism.

**Overall value**: Data is stored only once; BI reports and AI applications read from the same table with unified permissions and metadata management; AI processing results flow back into the data processing pipeline in real time via GIC incremental refresh, no longer sitting in external systems waiting for batch runs; from data ingestion, processing, AI handling to analytics consumption, the full pipeline closes within a single platform — data teams need not switch tools or maintain multiple systems.

***

## Lakehouse Studio

Singdata chose an integrated approach from the very beginning of product design — bringing the complete lifecycle of data development into a single platform, allowing ingestion, development, scheduling, operations, and governance to share the same metadata and permission system. [Studio](lakehouse-studio-101.md) was built in parallel with the compute engine, not as an add-on module.

Studio's main modules:

* **Data Sync**: Offline batch sync and CDC real-time sync for 40+ data sources, visually configured with no code required
* **Task Development and Scheduling**: Unified management of SQL / Python / Shell tasks, DAG dependency orchestration, supports backfill and rerun
* **Operations Monitoring**: Instance logs, run alerts, resource usage — troubleshoot without leaving the platform
* **Data Catalog**: Metadata management, data lineage, data quality rules — governance and development in the same interface
* **Analysis Notebook**: Interactive SQL and Python analysis, results directly connectable to BI

Quick start: [Lakehouse Studio Getting Started Guide](lakehouse-studio-101.md)

***

## Core Object Relationships

Relationships between data objects:

![](/.topwrite/assets/04-object-relationship_1779606899090.svg)

* [Dynamic Table](dynamic-table.md): Define a SQL; the system automatically detects upstream table changes and incrementally refreshes. Suitable for building ODS→DWD→ADS data pipelines. Does not depend on Table Stream.
* [Table Stream](table_stream.md): An independent CDC capture mechanism that records every row's insert/update/delete changes for downstream custom consumption. Suitable for scenarios requiring fine-grained control over MERGE logic.
* Both start from a Table and are two parallel paths — choose one based on your scenario.

Dynamic Table's incremental computation is driven by Singdata's proprietary GIC (Generic Incremental Computation) model, supporting second-level trigger, minute-level periodic, and DAG dependency scheduling modes. Defined with standard SQL, no stream processing framework required. See [Incremental Computing Mechanism and Dynamic Tables](incremental-computing.md).

***

## Typical Use Cases

### Enterprise Knowledge Base and RAG System

Store unstructured documents (contracts, research reports, tickets, product manuals) in a [Volume](volume-overview.md), batch-vectorize them with `AI_EMBEDDING()` and write into the same table, while building an inverted index for exact keyword matching. At retrieval time, a single SQL simultaneously retrieves semantically similar content (vector index) and exact matches for proper nouns (inverted index), fuses rankings with the RRF algorithm, then calls `AI_COMPLETE()` to generate answers. The entire RAG pipeline closes within Lakehouse — no need to separately maintain a vector database and Elasticsearch.

Reference: [Full-Text + Vector Hybrid Search Best Practices](rrf-fulltext-vector-hybrid-search-best-practices.md)

### Real-Time Data Backend for AI Applications

AI applications executing tasks depend on real-time business state: is inventory sufficient? Has the order been paid? Has the user profile been updated? Use CDC real-time sync to write business database changes into Lakehouse; Dynamic Tables refresh DWD/DWS layers in minutes; [Semantic Views](semantic-view-overview.md) unify metric definitions. AI applications query Semantic Views via REST API or JDBC, receiving results that are business-readable and fresh to the minute — not overnight batch snapshots.

Reference: [Semantic Views](semantic-view-overview.md)

### AI Agent-Driven Autonomous Data Engineering

Using AI coding tools like Claude Code, Cursor, or Codex, operate Lakehouse directly through [cz-cli](setup_cz_cli.md): describe requirements, and the Agent automatically creates tables, writes ETL SQL, submits scheduling tasks, inspects run logs, and identifies performance bottlenecks. Data warehouse development shifts from "humans write code" to "humans describe goals, Agents execute."

Reference: [cz-cli Configuration Guide](setup_cz_cli.md)

### Replacing Spark or Traditional Big Data Architectures

Migrate existing Spark ETL jobs to Lakehouse, replace Spark Streaming with Dynamic Tables, and replace PySpark scripts with SQL tasks. No Spark cluster to maintain, compute is pay-per-use, dramatically reducing total cost.

Reference: [Spark SQL Migration Guide](migration-spark-sql.md)

### Real-Time Data Platform

Use multi-table real-time sync (CDC) to write business database changes into Lakehouse in real time; use Dynamic Tables to build ODS→DWD→ADS layered data pipelines with minute-level refresh, replacing the dual-pipeline Lambda architecture of Flink + data warehouse.

Reference: [Real-Time Pipeline Selection Guide](realtime-pipeline-selection-guide.md)

### Connected Vehicle / IoT Data Platform

Massive device data continuously written via Kafka; Dynamic Tables aggregate device status and alert metrics in real time; analytical clusters support high-concurrency online queries — one architecture covers real-time ingestion, processing, and analytics end-to-end. Device anomaly data is processed by AI Functions for pattern recognition, with results written back to structured tables for real-time consumption by operations Agents.

***

## Ecosystem Compatibility

Singdata Lakehouse natively supports Apache Iceberg format and supports direct read/write of Delta Lake, Hudi, and Paimon as external tables — existing data lake assets can be onboarded without migration. On the compute ecosystem side, [Spark Connector](spark-connector-summary.md), [Flink Connector](flink-write-connector.md), and Trino Connector are provided for smooth integration with existing big data pipelines. On the BI side, FineBI, Tableau, Superset, Metabase, and PowerBI have all completed integration certification.

## Start Here

| Your goal                                   | Recommended starting point                                                                             |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Understand all platform concept definitions | [Key Concepts](key-concepts.md)                                                                        |
| Hands-on with your first complete workflow  | [Quick Start](lakehouse-quick-experience_guide.md)                                                     |
| Understand the full AI Lakehouse picture    | [AI Lakehouse](lakehouse-ai.md)                                                                        |
| Build RAG or vector search                  | [Full-Text + Vector Hybrid Search Best Practices](rrf-fulltext-vector-hybrid-search-best-practices.md) |
| Understand AI data analytics capabilities   | [Data Analytics Agent Tour](lakehousedatagpt-tour.md)                                                  |
| Let AI Agents operate the data warehouse    | [cz-cli Configuration Guide](setup_cz_cli.md)                                                          |
| Learn common SQL commands                   | [SQL Reference](sql-reference.md)                                                                      |
| Design data models and object relationships | [Object Model Design](object_model_design.md)                                                          |

^
