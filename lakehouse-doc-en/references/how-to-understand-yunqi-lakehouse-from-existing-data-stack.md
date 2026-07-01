# Understanding Singdata Lakehouse from Your Existing Data Stack

If you are already using a mature data stack, the most natural question when encountering Singdata Lakehouse for the first time is usually not "what features does it have" — it is:

**What does each capability in my current data stack correspond to in Singdata Lakehouse?**

For example, you might be using one of these combinations:

* `Spark / PySpark + Airflow + Hive / Iceberg`
* `Databricks + Delta Lake + dbt`
* `BigQuery + dbt + Airbyte / Fivetran + BI`
* `Snowflake + Snowpark + Airbyte / Fivetran + dbt + BI`
* `MaxCompute + DataWorks`
* `Kafka / Flink CDC + data warehouse + BI`
* `BI + semantic layer + RAG + model gateway + AI Agent`

Behind these combinations is not just a set of technologies, but a workflow that is already running: how data comes in, how tasks are developed, how scheduling runs, how reports are produced, and where to look when problems occur.

The most efficient way to understand Singdata Lakehouse is not to memorize a new set of names, but to map it back against the chain you already know.

## Start from Your Familiar Workflow

Regardless of the underlying technology choices, most teams' data workflows include several similar capability layers:

| Your familiar layer | Common representative products or components | Primary responsibility |
| --------- | ------------------------------------------------ | -------------------- |
| Data storage and compute | Spark, Databricks, Snowflake, MaxCompute, Hive | Store data; execute SQL, batch processing, and analytics compute |
| Data ingestion | Airbyte, Fivetran, Flink CDC, Kafka Connect, custom sync | Connect business databases, SaaS, logs, and message streams to the platform |
| Data development and scheduling | Airflow, DataWorks, dbt, PySpark, Snowpark, Notebook | Modeling, orchestration, scheduling, publishing, and maintenance |
| Data analytics and consumption | BI, semantic layer, reporting systems, self-service analytics tools | Provide metrics, reports, and analytics capabilities |
| AI frameworks | Vector stores, RAG, model gateways, knowledge base frameworks | Semantic retrieval, model calls, and knowledge recall |
| Agents | Claude, Codex, Cursor, OpenAI Agents SDK, and other AI Agents | Natural-language-driven data analytics and engineering |

:-: ![](.topwrite/assets/modern-data-stack-reference-architecture.svg =663)

The complexity many teams actually feel is often not that any layer is missing entirely — it is that these layers come from different systems:

* Data ingestion is one system
* Data warehouse processing is another system
* Scheduling and operations is another system
* BI and semantic layer is another system
* AI and vector retrieval is yet another system

The most common feeling in this situation is not "not enough capability," but:

* Switching between multiple consoles for the same chain
* Different teams see different copies of the same business data
* BI semantics and AI semantics are not necessarily consistent
* Boundaries between ingestion, development, scheduling, and governance are unclear

One useful angle for understanding Singdata Lakehouse is seeing how it reorganizes these originally scattered layers.

## A Four-Layer Mapping to Start With

Mapping Singdata Lakehouse back to your familiar data stack, start with four layers:

1. Data foundation layer
2. Data ingestion layer
3. Data engineering layer
4. Analytics and AI layer

### Data Foundation Layer: Bringing Scattered Data Objects Back to One Platform

Many teams start understanding a platform from the engine they know best:

* If you know Spark, you typically look at the compute engine and data lake format first.
* If you know Databricks, you typically look at Lakehouse, unified workflow, and external data first.
* If you know Snowflake, you typically look at warehouse capabilities, SQL experience, and data consumption first.
* If you know MaxCompute, you typically look at integrated development and governance first.

In Singdata Lakehouse, this layer mainly corresponds to:

* Workspace
* Schema
* Lakehouse Iceberg Table
* External Table
* Volume
* External Catalog
* SQL engine
* VCluster
* Apache Iceberg native format

Mapping from an existing data stack, you can think of it as:

**The structured tables, object storage files, external lake formats, and streaming data you are familiar with are no longer naturally scattered across several systems — they are brought back into a data foundation with the Workspace as the boundary.**

For day-to-day work, this means:

* Structured data, files, and external lake formats can coexist in the same platform.
* The Workspace is both the top-level boundary for data objects and the collaboration boundary for Studio development and scheduling.
* SQL, batch processing, and near-real-time processing share the same metadata and permissions system.
* BI and AI do not need to work from separate data copies.

If your most immediate concern is "do not move data first — can I query and accelerate in place first," read further:

For teams that already have existing data catalog and external lake table systems, `External Catalog` is not just a federated query feature — it is an important migration entry point: connect the existing catalog system and query path first, then decide which data and chains to progressively migrate into Singdata Lakehouse.

* [Data Lake Acceleration](datalake-acceleration.md)
* [Lake Acceleration Implementation Guide](lakehouse-acceleration-guide.md)
* [Federated Queries](federation-query.md)
* [Databricks Unity Catalog Federated Query Practice](databricks-external-catalog-practice.md)
* [Accessing Databricks Iceberg Tables via Iceberg REST Catalog](iceberg-rest-catalog-databricks.md)
* [Querying Snowflake OpenCatalog Iceberg Tables via External Catalog](query-snowflake-open-catalog-iceberg-table.md)

### Data Ingestion Layer: Making "Ingestion Complete" the Starting Point for Downstream Chains

Many teams are accustomed to keeping the ingestion layer outside the platform:

* Database sync relies on Airbyte, Fivetran, or custom sync tools
* CDC relies on Flink CDC or Kafka Connect
* File ingestion relies on landing in object storage and subsequent imports

In Singdata Lakehouse, this layer mainly corresponds to:

* Studio Data Integration
* Offline sync tasks
* Real-time sync tasks
* Multi-table real-time sync
* Pipe
* Table Stream

The most commonly underestimated — but most critical for most existing data stacks — is often exactly **Studio's data sync tasks**.

For many teams, migration does not start with "switching SQL engines." It starts with these core requirements:

* Should business database data continue to be synced in continuously?
* Should a batch of SaaS, API, log, and file data be reliably connected?
* Should CDC keep running, tracking schema changes and new tables?
* After ingestion is complete, can data flow directly into downstream development, scheduling, governance, and analytics chains?

In other words, for many existing data stack users, the first thing to confirm is not "can I do modeling here" — it is:

* **Are offline sync, real-time sync, and multi-table real-time sync core capabilities here, not edge features?**

If you are already familiar with standalone ingestion tools, one direct difference is:

**In many standalone sync tools, "ingestion complete" typically means "data has landed somewhere." In Singdata, "ingestion complete" is more like the starting point for downstream development, scheduling, governance, and analytics chains.**

So if you currently use `Airbyte + data warehouse + Airflow`, you can think of Singdata as:

**Ingestion, modeling, scheduling, monitoring, and governance are no longer naturally in different systems.**

### Data Engineering Layer: Bringing Development, Scheduling, and Operations Back to One Complete Workflow

This layer is usually the part data engineering teams know best.

Your current way of working might be:

* SQL modeling depends on `dbt`
* Python or Spark processing depends on `PySpark`
* Python development in the Snowflake ecosystem depends on `Snowpark`
* Scheduling orchestration depends on `Airflow` or `DataWorks`
* Operations and monitoring then go to another system

In Singdata Lakehouse, this layer mainly corresponds to:

* Studio task development
* SQL / Python / JDBC / streaming tasks
* Composite tasks
* Scheduling and dependency configuration
* Operations monitoring, backfill, alerting
* Dynamic Table
* `dbt-clickzetta`
* `ZettaPark`
* Data Engineering Agent

The key point to start with is not "does Singdata have an equivalent to Airflow or dbt" — it is:

**The SQL, Python, scheduling, dependencies, publishing, backfill, and operations actions you know still exist, but they no longer naturally scatter across multiple tools.**

For many teams, the most tangible change at this layer is often:

* Fewer system switches
* Fewer interface relationships to maintain
* Less context switching between development, scheduling, and operations

If you used `Airflow + dbt + various scripts + operations console`, think of Singdata as:

**Reorganizing the data engineering lifecycle into a Lakehouse-native workflow.**

If you want a more concrete component-level comparison:

* `dbt` can continue to be used via [dbt-clickzetta](eco_integration/dbt.md)
* `PySpark / Snowpark` Python data development is closest to the [ZettaPark](LakehousePython-zettapark.md) path in Singdata
* Your familiar task scheduling and run system primarily lands in Studio task development, scheduling, and operations chains

### Analytics and AI Layer: Putting BI, Semantics, and AI on the Same Data Context

This is where many teams most clearly feel the old/new divide.

The common previous approach was:

* BI does reports and analytics through the data warehouse
* A separate semantic layer maintains metrics and definitions
* Vector retrieval, RAG, and knowledge base Q&A are in a separate AI stack
* Model calls go through standalone gateways or application services

In Singdata Lakehouse, this layer mainly corresponds to:

* Semantic View
* Analytics Agent
* AI Gateway
* AI Functions
* Vector, full-text, and hybrid search
* MCP Server
* cz-cli

If you are already using `BI + semantic layer + RAG + model gateway`, think of it as:

**Singdata is not bolting an AI layer onto the side of the data warehouse — it organizes AI as an internal capability of the data platform.**

A few more tangible changes:

* BI and AI no longer naturally work from two different data copies and semantic definitions
* Model calls, vector retrieval, and knowledge recall can be understood within the same platform as SQL and data processing chains
* Agents can participate not just in querying data, but in data engineering and analytics consumption

## Mapping Your Current Data Stack

### If You Currently Use Spark / Hive / Iceberg

Your current work probably looks like this:

* Data lands in Hive, Iceberg, or object storage
* Processing logic is in Spark SQL, PySpark, or scripts
* Scheduling goes to Airflow
* Table governance, task operations, and analytics consumption are in separate places

If this is primarily how you work, when judging whether a platform is comfortable to use, you typically check:

* Whether Workspace, Schema, Table, partition, and file path objects are clear, and whether you can instantly explain where data lives.
* Whether SQL, PySpark, and scripts all end up as Spark jobs, and whether the execution unit is clear.
* Whether scheduling is still in an external orchestrator like Airflow, and whether responsibilities are clearly separated between dependency management and execution.
* Whether metadata, permissions, lineage, and quality are still scattered across multiple systems or consolidated.

Mapping to Singdata Lakehouse, you would first check:

* Can data continue to be stably and continuously synced in?
* Does Workspace, Schema, Table, files, and external lake format all have clear homes here?
* Does Spark / PySpark development continue or require a full rewrite?
* Where do the parts originally handled by the scheduler and surrounding systems land?

If this is your background, focus on:

* How Singdata handles existing lake formats and object storage data
* Whether SQL and Python development habits are preserved
* Whether development, scheduling, operations, and analytics are consolidated into a more complete platform

Component-level comparison:

| Your familiar object | Closest equivalent in Singdata Lakehouse |
| ---------------------- | --------------------------- |
| Hive / Iceberg table | Lakehouse Iceberg Table / External Table |
| File path on HDFS / S3 / OSS | Volume / External Volume |
| Spark SQL | Lakehouse SQL |
| PySpark job | ZettaPark |
| Airflow DAG / scheduled task | Studio tasks and scheduling |
| Custom sync chain / CDC chain | Studio offline sync / real-time sync / multi-table real-time sync |
| External metadata catalog | External Catalog |

For more specific paths if you are on Hive / Spark:

* [Lake Acceleration Implementation Guide](lakehouse-acceleration-guide.md)
* [Spark SQL Syntax Migration Guide](migration-spark-sql.md)
* [Spark Task Smooth Migration to Lakehouse](spark-migration-guide.md)
* [PySpark → ZettaPark Migration: F1 Racing Data Engineering Project](pyspark-to-zettapark-migration-f1.md)

### If You Currently Use Databricks

Your current work probably looks like this:

* Delta Lake manages core data
* SQL, Python, or PySpark in Notebooks
* Jobs Workflows run and schedule tasks
* You want engineering, analytics, and platform capabilities in one environment

When judging whether a platform is as comfortable as Databricks, you typically first check:

* Whether core data objects are stable like Delta tables — table versions, incremental refresh, unified catalog.
* Whether Notebook, Job, SQL Warehouse, catalog objects, and governance objects are still connected in one complete workspace rather than split into separate systems.
* Whether development, run, and governance are still in one chain, or whether you need to switch consoles mid-task.
* Whether incremental, streaming/batch, and layered pipeline production capabilities are seriously handled, not just "can write SQL and Python."

Mapping to Singdata Lakehouse, you would first check:

* Will the integrated experience I am familiar with be broken up?
* What handles the responsibilities Delta, Workflows, Unity Catalog, and Warehouse originally carried?
* How is data ingestion — Auto Loader, DLT, and external ingestion chains — handled?
* Can I maintain the same comfortable working style for real-time, incremental, and data warehouse layering?

Think of Singdata as:

* A platform equally emphasizing integration
* While placing real-time data, semantic layers, AI capabilities, and Agent integration in more explicit positions

Component-level comparison:

| Your familiar object | Closest equivalent in Singdata Lakehouse |
| ------------------------ | -------------------------------------- |
| Delta Lake table | Lakehouse Iceberg Table |
| Unity Catalog | Workspace / Schema / table object organization + permissions / governance system |
| Databricks SQL Warehouse | VCluster |
| Notebook / Job | Studio task |
| Delta Live Tables | Dynamic Table |
| Databricks Workflows | Studio scheduling and dependencies |
| Auto Loader / external ingestion | Studio Data Integration / Pipe / real-time sync |
| dbt-databricks | dbt-clickzetta |
| PySpark | ZettaPark |

For more specific migration paths:

* [Databricks → Lakehouse Migration: Medallion Three-Layer Warehouse](medallion-lakehouse-from-scratch.md)
* [Databricks Notebook → Lakehouse Migration: Retail Data Medallion Pipeline](databricks-notebook-to-studio-migration.md)
* [Databricks DLT → Lakehouse Migration: Apparel Retail Streaming Pipeline](databricks-dlt-to-lakehouse-migration.md)
* [Databricks Unity Catalog → Lakehouse Migration: Permissions and Governance](databricks-uc-governance-to-lakehouse-migration.md)
* [Databricks Unity Catalog Federated Query Practice](databricks-external-catalog-practice.md)
* [Accessing Databricks Iceberg Tables via Iceberg REST Catalog](iceberg-rest-catalog-databricks.md)

### If You Currently Use Snowflake

Your current work probably looks like this:

* Standard SQL and warehouse experience at the center
* Snowpark, dbt, or external tools supplement development
* Airbyte / Fivetran or similar tools connect data
* BI, semantic layer, and external applications complete the analytics consumption chain

When judging whether a warehouse platform is comfortable to use, you typically first check:

* Whether Database, Schema, Table, Stage, Warehouse, Task, Stream are clear, and what each is responsible for.
* What handles Warehouse, since performance, concurrency, and cost judgment often starts with Warehouse.
* Where data lands first and how it enters tables — whether Stage and Snowpipe-style entry points have clear equivalents.
* Whether standard SQL extensions — Snowpark, dbt, Task, Stream, Dynamic Table — are all accessible.
* Whether BI, applications, and semantic layer consumption can be built on a stable, clear warehouse foundation.

Mapping to Singdata Lakehouse, you would first check:

* How do business databases and external data continue to enter continuously — does it require assembling many external tools?
* What does Warehouse correspond to, and what do I use to understand compute resources, performance, and concurrency?
* Do Stage, Snowpipe, Task, Stream, and Dynamic Table all have equivalents?
* Do Snowpark and dbt development paths continue, replace, or require changing my way of working?

Focus on:

* How Singdata handles files, external lake formats, and unstructured data
* Dynamic Table, Pipe, and Stream incremental and real-time capabilities
* AI Gateway, AI Functions, and Analytics Agent — the layer beyond traditional warehouses

Component-level comparison:

| Your familiar object | Closest equivalent in Singdata Lakehouse |
| ------------------------------------------- | ---------------------------------------- |
| Database / Schema / Table | Workspace / Schema / Lakehouse Iceberg Table |
| Virtual Warehouse | VCluster |
| Internal Stage / External Stage | Volume / External Volume |
| Snowpipe | Pipe |
| Snowflake Connector / Snowpipe-based ingest | Studio Data Integration / real-time sync |
| Fivetran / Airbyte external sync | Studio offline sync / real-time sync / multi-table real-time sync |
| Dynamic Tables | Dynamic Table |
| Streams | Table Stream |
| Tasks | Studio tasks and scheduling |
| Snowpark | ZettaPark |
| dbt-snowflake | dbt-clickzetta |
| Cortex / external model gateway | AI Gateway / AI Functions |

For more specific migration paths:

* [Snowpark → ZettaPark Migration: Frostbyte Data Engineering Pipeline](snowflake-snowpark-to-zettapark-migration.md)
* [Snowflake Dynamic Tables Migration: Bronze–Silver–Gold Three-Layer Pipeline](snowflake-dynamic-tables-to-lakehouse.md)
* [Migrating Snowflake Real-Time ETL Pipeline to Singdata Lakehouse](migrate-snowflake-realtime-etl-to-lakehouse.md)
* [Querying Snowflake OpenCatalog Iceberg Tables via External Catalog](query-snowflake-open-catalog-iceberg-table.md)

### If You Currently Use BigQuery

Your current work probably looks like this:

* SQL analytics experience and managed warehouse capabilities at the center
* `dbt` manages modeling and transformation logic
* Airbyte, Fivetran, or other external tools connect data
* BI, Notebooks, or application layer complete analytics consumption

When judging whether an analytics platform is comfortable to use, you typically first check:

* Whether you can get started the same way as a managed SQL service, without needing to understand many platform details upfront.
* Whether Dataset, Table, Scheduled Query, and External Tables have clear equivalents.
* Whether dbt, SQL modeling, and report consumption remain in one straightforward flow without suddenly requiring heavy platform engineering.
* Whether cost, stability, and scalability are still easy to reason about after switching platforms.

Mapping to Singdata Lakehouse, you would first check:

* Will the managed SQL workflow I know suddenly become many low-level platform operations?
* What do `project.dataset.table` and Scheduled Query correspond to?
* Can data ingestion work that depended on external sync tools move back into the main platform?
* Can the chain I assembled with dbt, External Tables, and external sync tools be completed with fewer systems?

Focus on:

* How Singdata handles standard SQL modeling and warehouse workflows
* How [dbt-clickzetta](eco_integration/dbt.md) continues the dbt path you know
* Dynamic Table, real-time sync, and multi-table real-time sync near-real-time capabilities
* How Singdata brings files, external lake formats, and AI capabilities onto the same platform

Component-level comparison:

| Your familiar object | Closest equivalent in Singdata Lakehouse |
| ------------------------------------ | ------------------------- |
| BigQuery `project.dataset.table` | `workspace.schema.table` |
| BigQuery Slots / Reservation compute view | VCluster |
| Scheduled Query | Studio tasks and scheduling |
| Airbyte / Fivetran external ingestion | Studio Data Integration / offline sync / real-time sync |
| dbt-bigquery | dbt-clickzetta |
| External tables / GCS external data | External Tables / External Volume |
| Dataform / SQL modeling tasks | Studio SQL tasks |

For more specific migration paths:

* [dbt BigQuery Migration: Retail Data Warehouse Pipeline](dbt-bigquery-to-clickzetta-migration.md)

### If You Currently Use MaxCompute + DataWorks

Your current work probably looks like this:

* Data development, scheduling, and governance already in one workbench
* The team places more importance on organizational standards, task management, and collaboration boundaries
* Integrated experience in the platform is important to you

When judging whether a data engineering platform is comfortable to use, you typically first check:

* Whether development, scheduling, operations, and governance are still coordinated in one workbench rather than split across different systems.
* Whether project, space, role, process, and standard organizational-level objects are still treated seriously.
* Whether node, workflow, dependency, backfill, go-live, and operations production objects have clear equivalents.
* Whether permissions, standards, and collaboration boundaries are placed on the main track from the start, not retrofitted later.

Mapping to Singdata Lakehouse, you would first check:

* Will the integrated workbench experience I know be broken up?
* Where do the production paths assembled through workflows, nodes, scheduling, and operations each land?
* Is data ingestion capability — originally in sync nodes and integration chains — equally on the main track here?
* Beyond continuing platform engineering capabilities, is the incremental Lakehouse and AI value worth the switch?

You will find it easier to connect with:

* Studio as a unified data engineering workbench
* Integrated path of Workspace, task development, scheduling, operations, and Data Integration

Component-level comparison:

| Your familiar object | Closest equivalent in Singdata Lakehouse |
| --------------------- | ----------------------------------- |
| MaxCompute table | Lakehouse Iceberg Table |
| DataWorks workflow / node | Studio task / composite task |
| DataWorks scheduling | Studio scheduling and dependencies |
| DataWorks Data Integration / sync | Studio Data Integration / offline sync / real-time sync |
| MaxCompute SQL | Lakehouse SQL |
| PyODPS / Python data development | ZettaPark / Python tasks |
| Integrated governance and collaboration workbench | Workspace + Studio + Lakehouse permission governance |

Additional Lakehouse and AI incremental capabilities worth checking:

* Not just data warehousing
* Also bringing near-real-time processing, semantic layers, AI retrieval, and Agents into the same platform capabilities

For more specific migration paths:

* [MaxCompute → Lakehouse Migration: E-Commerce Data Engineering Project](maxcompute-to-lakehouse-ecommerce.md)

## What Can Be Seen as "Continuity" vs. "Reorganization"

One practical way to understand Singdata Lakehouse is to separate capabilities into two categories.

One category is capabilities you know today that can continue:

* SQL
* Python
* JDBC / MySQL protocol / SDK
* Scheduling, dependencies, alerting, backfill
* Offline sync, real-time sync, multi-table real-time sync, object storage ingestion

The other category is the reorganization of relationships in the existing data stack:

* Use one Lakehouse platform to handle both structured and unstructured data
* Use Studio Data Integration and sync tasks to bring the data ingestion chain inside the platform
* Use Studio to consolidate development, scheduling, operations, and governance
* Use Dynamic Table and incremental computation to improve data freshness
* Use Semantic View, AI Gateway, Analytics Agent, and Engineering Agent to connect Data and AI

So the more useful question for building an overall understanding is not:

**Can Singdata Lakehouse replace the specific product I am using today?**

But rather:

**How does Singdata Lakehouse take my current scattered data stack and reorganize it into a more integrated platform?**

![](.topwrite/assets/clickzetta-lakehouse-modern-data-stack-mapping.svg)

## If You Are Worried About "Needing to Learn a Lot When Switching Data Stacks"

This is a common and practical concern.

Many teams' first reaction to switching data stacks is not "is it worth it," but:

* Will what I already know still be useful?
* Do existing tasks and processes need to be rewritten?
* Does the team need to learn a whole new set of approaches before starting to use it?
* During migration, will we be maintaining two systems simultaneously?

If you have these concerns, approach Singdata Lakehouse from three angles.

### First, See What Capabilities Can Continue

For most teams, the most sensitive part of migration cost is not the product name changing, but whether familiar ways of working become obsolete.

In Singdata Lakehouse, many daily capabilities do not require starting over:

* SQL is still there
* `dbt` can continue via [dbt-clickzetta](eco_integration/dbt.md)
* `PySpark / Snowpark` Python data development maps to [ZettaPark](LakehousePython-zettapark.md)
* JDBC, MySQL protocol, SDK, and BI connection methods are still there
* Offline sync, real-time sync, multi-table real-time sync, CDC, scheduling, alerting, and backfill are still there

The change is usually not "everything I know is gone" — these familiar capabilities are brought into a more unified platform.

### Then, See What Complexity Can Be Consolidated

What many teams actually want to reduce is not the learning cost of any single button — it is the long-standing fragmentation in daily work.

For example:

* Data ingestion and sync tasks require one system
* Task development requires another system
* Scheduling and operations require another system
* BI, semantic layer, and AI require yet another system

From this angle, what Singdata Lakehouse brings is often not "learn one more thing" but gradually maintaining fewer things.

This typically shows up in:

* Fewer system switches
* Fewer interface connections to maintain
* Fewer metric definitions to maintain
* Less context switching between development, scheduling, analytics, and AI

### Finally, See Whether Migration Can Be Gradual

What many teams actually worry about is not learning itself — it is all-at-once switching.

If the requirement is to replace everything, migrate everything, and learn everything at once, the pressure is naturally high.

But the more common and realistic approach is gradual entry:

* Start from one data ingestion chain
* Start from one Workspace
* Start from one data modeling scenario
* Start from one analytics scenario

You do not need to learn the full platform before starting to use it.

The more natural path is:

* Continue with familiar SQL, dbt, Python, and BI connection approaches first
* Then progressively understand how Singdata Lakehouse puts these capabilities into the same workflow
* Finally use Dynamic Table, Semantic View, AI Gateway, and Agent — the new capabilities that further reduce fragmentation

If you have an existing running data stack, think of Singdata Lakehouse as:

**Not requiring you to abandon what you know first before accepting a completely unfamiliar new system — but letting familiar capabilities continue while progressively entering a more integrated platform.**

### What Is the More Careful Migration Approach?

If you have decided to start migrating, many teams care less about "can we migrate" and more about "how to migrate with lower risk."

The more careful approach is usually staged progression rather than all-at-once switching:

* Choose one chain with clear boundaries as the starting point
* Migrate one segment of reading, processing, or analytics first
* After running old and new chains in parallel for a period, decide whether to expand scope

Common starting points include:

* One offline sync or real-time sync chain
* One new data ingestion chain
* A set of independent data warehouse layer tasks
* A dbt project
* A PySpark / Snowpark data processing scenario
* A near-real-time analytics or AI scenario

The benefit: the team can build experience in a real but contained scope, rather than moving all historical chains at once from the start.

### What Should Be Verified During Migration?

Migration is not just "tasks are running" — it also requires confirming the new chain can handle existing requirements in daily work.

Typically verify at least these:

* Whether data results are consistent
* Whether scheduling, dependencies, and backfill chains run smoothly
* Whether permissions and access paths match the original team patterns
* Whether BI, semantic layers, or downstream applications can connect smoothly
* Whether operations investigation is clearer than before — at minimum, not more convoluted

If migrating existing code assets like PySpark, Snowpark, or dbt, prioritize scenarios where before/after result comparison is easier. This helps the team build confidence faster.

### What Should Actually Be Reduced After Migration?

Migration goals are usually not just "run tasks on a different platform" but progressively reducing these long-term costs:

* Maintaining the same chain across multiple systems
* Implementing the same logic repeatedly in multiple places
* Different teams collaborating around different data copies and different metric definitions
* BI, data engineering, and AI each maintaining their own data context

If these problems visibly decrease after migration, the team will more naturally accept the new platform's way of working.

## Where Singdata Lakehouse's Additional Value Shows Up

If you only look at names, it is easy to think of Singdata as "also supports SQL, Python, CDC, scheduling, semantics, and AI."

But for day-to-day work, the more important thing is often not "also supports" — it is that it tries to solve several long-standing fragmentations:

* Data fragmentation: structured data, files, external lake formats, and streaming data distributed across different systems
* Workflow fragmentation: ingestion, development, scheduling, operations, and governance switching between different tools
* AI fragmentation: vector retrieval, model calls, knowledge Q&A, and the data platform all externally attached to each other

From this angle, Singdata Lakehouse's value is not just implementing all these capabilities, but reorganizing them back into the same data workflow.

## Which Path You Might Take

If you are already running a data stack, you will typically end up on one of three paths.

### Connect First, Accelerate First, No Rush to Move

If your most immediate concern is:

* Connect existing data first
* Query directly, unify access first
* Improve query and analytics experience first
* Reduce some system fragmentation first

Then starting with in-place connection, federated queries, and lake acceleration is more suitable.

### Migrate One Local Workflow First

If your most immediate concern is:

* Migrate one data source ingestion chain
* Migrate one data warehouse processing chain
* Migrate one dbt / PySpark / Snowpark scenario
* Have the team become familiar with the new development, scheduling, and operations path

Then starting with a partial migration — using one concrete scenario to build real platform experience — is more suitable.

### Put New Projects Directly on Singdata Lakehouse

If your most immediate concern is:

* A new project needs to be built
* You do not want to split data, scheduling, semantics, and AI into multiple systems
* You want to build on an integrated Data + AI path from the start

Then putting the new project directly on Singdata Lakehouse is more suitable.

## Where to Continue Reading

If you already have a clear background, continue reading in the following order:

* To understand the overall platform positioning first: read [Singdata Lakehouse Product Introduction](concepts.md)
* To understand the object model first: read [Key Concepts](key-concepts.md)
* To understand how Studio objects relate and transition: read [Studio Object Relationships and Lifecycle](studio-object-lifecycle-guide.md)
* To understand the integrated development workbench first: read [Lakehouse Studio Overview](lakehouse-studio-concept.md)
* To understand the Data + AI full picture first: read [AI Capabilities Overview](ai-capabilities-overview.md)
* To understand the technology ecosystem and compatibility paths: read [Ecosystem](ecosystem.md)

If your main concern is "no big migration yet — connect first, accelerate, then progressively replace":

* [Data Lake Acceleration](datalake-acceleration.md)
* [Lake Acceleration Implementation Guide](lakehouse-acceleration-guide.md)
* [Multi-Cloud Unified Data Lake Acceleration](lakehouse-multi-cloud-acceleration.md)
* [Federated Queries](federation-query.md)

If you have decided to migrate and want more specific paths aligned with your current stack:

* [Migration Guide](tutorial_migration.md)
* [Spark SQL Syntax Migration Guide](migration-spark-sql.md)
* [Spark Task Smooth Migration to Lakehouse](spark-migration-guide.md)
* [Databricks → Lakehouse Migration: Medallion Three-Layer Warehouse](medallion-lakehouse-from-scratch.md)
* [Snowpark → ZettaPark Migration: Frostbyte Data Engineering Pipeline](snowflake-snowpark-to-zettapark-migration.md)
* [MaxCompute → Lakehouse Migration: E-Commerce Data Engineering Project](maxcompute-to-lakehouse-ecommerce.md)
* [dbt BigQuery Migration: Retail Data Warehouse Pipeline](dbt-bigquery-to-clickzetta-migration.md)
