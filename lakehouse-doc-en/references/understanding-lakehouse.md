# Understanding the Lakehouse

When many people first encounter "Lakehouse," they tend to interpret it as a marketing concept: the flexibility of a data lake combined with the analytics capabilities of a data warehouse. That description is accurate, and in today's market, customers have largely accepted this value proposition. For most organizations, the appeal of a Lakehouse is clear: they want the low cost and scalability of a data lake alongside the reliability, performance, and governance of a data warehouse, without maintaining two separate disconnected systems indefinitely.

In other words, the conversation has largely moved from "should we build a Lakehouse" to "which one, how to deploy it, and how to integrate it with our existing data stack." But a few common misconceptions persist: some treat a Lakehouse as an "upgraded data lake" or "a different storage format," underestimating how much it changes governance structures and collaboration patterns. Others equate the Lakehouse with a specific vendor product and overlook the long-term value of open table formats and open ecosystems.

This document focuses on:

**In Singdata Lakehouse, how exactly is "Lakehouse" implemented? How does data in the lake enter the platform, get managed, get analyzed by warehouse-style engines, and continue flowing to data warehouse layers, BI, AI, and Agents?**

Only by clarifying this chain does the Lakehouse stop being an abstract noun and become a data-working approach that can actually be deployed.

## One Prerequisite You Cannot Ignore

If you think of the Lakehouse only as "Iceberg support underneath," it is easy to miss the implementation differences in object models, engineering workflows, and platform boundaries.

For Singdata Lakehouse, one prerequisite is critical:

**Singdata Lakehouse was built on Iceberg from Day 1.**

This differs from many platforms that started with a warehouse and later added Iceberg compatibility. It means:

- Iceberg is not a retroactively added compatibility layer — it is part of the platform foundation.
- Iceberg tables are not peripheral objects — they are part of the core object system.
- SQL, incremental computation, governance, sync, and AI consumption around Iceberg tables all evolved along the same main platform chain.

Singdata is also a **core contributor to the Apache Iceberg C++ implementation**. This means:

- Singdata is not just using Iceberg as a swappable external dependency.
- The team deeply participates in building the underlying open-format ecosystem itself.

This is why Singdata Lakehouse's support for open Iceberg table objects is not a peripheral compatibility feature — it is part of building the platform foundation.

When understanding Singdata Lakehouse, you can view it not just as a complete Lakehouse product, but also place it in the broader evolution of open formats and open ecosystems.

### Why "Built on Iceberg" and "Supports Iceberg" Are Not the Same

These two phrases look similar, but they differ significantly in product implementation.

"Supports Iceberg" typically means: the platform had its own more central table objects or storage system first, and later added read, write, or compatibility capabilities for Iceberg tables. Iceberg can be important in such an architecture, but it remains more like an ingested, adapted, or compatible object type.

"Built on Iceberg" means something different: Iceberg is not a peripheral compatibility layer — it is part of the platform foundation. Table objects, metadata management, incremental computation, data freshness, external catalog integration, data warehouse layer processing, query analytics, and downstream BI/AI consumption all evolved forward around this class of open Iceberg table objects.

For Singdata Lakehouse, the practical implication is:

- Iceberg is not a retrofitted addition — it is part of the core production table system.
- Iceberg tables are not peripheral objects — they are main-chain objects.
- External Catalog, Volume, Dynamic Table, Studio data sync tasks, and Pipe exist not as isolated features, but as connected capabilities around the same data foundation and data flow chain.
- The long-term value shows not just in "can it query Iceberg today," but in whether the platform was built from the start along open formats and open ecosystems.

## The Core Insight: A Lakehouse Is Not "a Lake Next to a Warehouse"

The problem in many traditional architectures is not the absence of a lake or a warehouse — it is the many layers between them:

- Raw files in object storage
- Iceberg tables in external catalogs
- Warehouse tables in a different system
- Sync tasks in peripheral tools
- Development scheduling in a separate workbench
- BI, semantic layers, AI retrieval each working from different data copies

When "lake" and "warehouse" both exist but data needs to flow, it typically has to cross multiple systems:

1. Data enters object storage or an external system.
2. A sync tool copies it into the warehouse.
3. A scheduling system runs layer-by-layer processing.
4. Results are provided to BI, applications, or AI.

The problem is not that any single step is impossible — it is:

- Too many data copies
- Scattered metadata
- Inconsistent permission boundaries
- Ingestion, development, scheduling, governance, and consumption not on the same chain

Singdata Lakehouse's implementation focuses not on presenting "lake capabilities" and "warehouse capabilities" side by side, but on reorganizing these originally scattered objects into a unified foundation.

![](.topwrite/assets/anim-44-understanding-lakehouse.svg)

## Where Singdata Lakehouse's "Integration" First Shows Up

In Singdata Lakehouse, the first things to grasp are not menus — they are a few core objects:

- `Workspace`
- `Schema`
- `Lakehouse Iceberg Table`
- `Volume`
- `External Catalog`
- `VCluster`

Together, these objects form the foundation of the Lakehouse.

### Workspace: Platform Boundary, Not a Lightweight Folder

In Singdata Lakehouse, `Workspace` is not a lightweight folder concept — it is one of the most important boundaries in the platform.

It carries two layers of responsibility:

1. **Data object boundary at the Lakehouse layer**  
   The three-level naming is `workspace.schema.table`.

2. **Development and collaboration boundary at the Studio layer**  
   Under the Workspace, it hosts users, roles, VClusters, task scheduling, Data Integration, operations monitoring, and other development and governance capabilities.

This means in Singdata Lakehouse, "where data lives" and "who develops, schedules, and governs within this boundary" are not two separate questions — they are organized around the same `Workspace`.

This differs from many platforms that use `database` or `catalog` only as a naming namespace. `Workspace` here simultaneously carries the table namespace and the development collaboration boundary — it is a heavier concept.

### Iceberg Tables: Lake and Warehouse Working from a Unified Core Production Table System

Singdata Lakehouse's core production table system is built on `Iceberg tables`.

This matters because it means "data in the lake" and "analytics objects in the warehouse" do not need to naturally split into two separate systems.

These tables simultaneously have several capabilities:

- Data organized in the open Iceberg table format
- Directly queryable with standard SQL
- MVCC, multi-version management, Time Travel, and other warehouse-side capabilities
- Can serve as upstream or downstream objects for Dynamic Tables, Materialized Views, BI, AI retrieval, and Agents

In a traditional architecture, you might distinguish between:

- Files in the lake
- Iceberg tables in external catalogs
- Analytics tables in the warehouse

In Singdata Lakehouse, these objects no longer naturally split into two separate systems. They converge around `Iceberg tables` as the core production table system.

In short, `Iceberg tables` primarily solve: once data enters the main platform chain, how it continues to be processed, analyzed, governed, and consumed.

### Volume: The File Entry Point, Not a Replacement for the Table System

`Volume` is how you access files in Singdata Lakehouse.

It is not an edge feature — it is an important entry point for lake capabilities into the platform's object model. Because in many data stacks, "the lake" does not first appear as tables — it first appears as:

- Files on OSS / S3 / COS
- Raw logs
- CSV / JSON / Parquet files
- Documents and semi-structured data

Singdata Lakehouse brings these file objects into the platform through `Volume`:

- `External Volume`: mounts user-owned object storage, leaving data in place
- `Managed Volume`: platform-managed internal storage
- `User Volume`: user file space
- `Table Volume`: file space associated with each table

This means "files in the lake" do not only exist outside the platform. They can first be managed through `Volume`, then enter subsequent SQL, import, processing, and analytics chains.

More importantly, `Volume` and tables are not disconnected — but they handle different objects:

- `Volume` handles file entry and file access.
- `Iceberg tables` handle structured data processing and analytics.
- The two are connected through `COPY INTO`, Pipe, and import chains.

This is how the "lake" side is pulled into the platform foundation.

Distinguish this from `External Catalog`: file objects typically enter the platform through `Volume`; fully formed external catalogs — and the Iceberg tables managed within them — typically enter through `External Catalog`.

In short, `Volume` primarily solves: how files enter the main platform chain.

### External Catalog: Connecting to Iceberg Tables in External Catalogs, Not a File Entry Point

Many teams already have their own Iceberg table catalog systems, such as:

- Hive Metastore
- Databricks Unity Catalog
- Iceberg REST Catalog
- Snowflake Open Catalog

Requiring "migrate everything first before you can use it" makes a Lakehouse a difficult migration path.

Singdata Lakehouse solves this through `External Catalog`:

- External data stays in its original system.
- Singdata Lakehouse reads metadata from the external catalog and data files needed for queries.
- Users can query tables in the external catalog using standard SQL.

Its significance goes beyond "federated queries." It also means:

**Connect the existing catalog system and query path first, then decide which chains to progressively migrate into Singdata Lakehouse.**

`External Catalog` is one of the key mechanisms for connecting "Iceberg table systems that already exist outside the platform" with "SQL analytics and downstream processing chains inside the platform."

In short, `External Catalog` primarily solves: how existing table systems in external systems can be connected first, queried first, and then progressively decided whether to migrate into the main platform chain.

## How Data in the Lake Flows to the Warehouse Analytics Chain

The most important thread for understanding the Lakehouse is: **how data flows**.

In Singdata Lakehouse, this flow path typically follows several common patterns.

### Path 1: Files Enter a Volume First, Then an Iceberg Table

This is the most typical path from "file lake" to "warehouse-style analytics."

The chain works like this:

1. Raw files remain in object storage.
2. They enter the platform's access scope through `External Volume` or another Volume type.
3. They are written into `Iceberg tables` through `COPY INTO` or related import paths.
4. Standard SQL, Dynamic Tables, and Studio tasks handle subsequent processing.

The key is not "importing files" per se — it is that after import, data has entered the unified table object system. Subsequent processing, scheduling, permissions, and AI all continue around the same type of table.

### Path 2: Sync Tasks and Pipe Continuously Bring Data In

In practice, large amounts of data are not imported once — they arrive continuously.

Singdata Lakehouse provides platform-level capabilities for this, not as peripheral patches but as core capabilities:

- Studio Data Integration
- Offline sync tasks
- Real-time sync tasks
- Multi-table real-time sync
- Pipe

To understand the boundaries of each:

- `Studio data sync tasks` primarily handle continuous ingestion from databases, SaaS, files, and other sources.
- `Offline sync tasks` primarily handle batch, scheduled, and periodic data entry.
- `Real-time sync tasks / multi-table real-time sync` primarily handle CDC continuous ingestion.
- `Pipe` primarily handles continuous data sources such as Kafka or object storage.

This means:

- Offline or CDC ingestion from relational databases does not have to depend entirely on external sync tools.
- Batch sync, real-time sync, and Pipe entry points are all managed within the same Workspace and Studio system.
- After data enters, it can flow directly into downstream development, scheduling, governance, and consumption chains.

This matters for "Lakehouse integration" because if sync tasks are entirely outside the platform, the Lakehouse is absorbing mainly storage and queries — the data flow has not truly entered the platform's main chain.

Looking further at the incremental chain: sync tasks and Pipe bring data continuously into tables, while `Table Stream` passes table changes downstream to incremental processing objects.

### Path 3: Query External Catalog Iceberg Tables Without Moving Data First

When data already exists in another external catalog system, you can start with `External Catalog`:

1. Connect the external catalog to Singdata Lakehouse.
2. Query Iceberg tables in the external catalog using standard SQL.
3. Join with local `Iceberg tables` for analysis.
4. Then decide whether to persist results back into local tables.

This path is most like "applying platform SQL analytics capabilities to an existing external table system."

It shows Singdata Lakehouse does not require all data to be moved into internal tables before analytics can start. It allows external catalog Iceberg tables and local tables to both be brought into analytics at the unified SQL layer.

## How Warehouse-Style Engines Analyze Lake Data

This is where the Lakehouse concept is most often left vague.

Just saying "supports Iceberg" does not answer "how analytics actually happen."

In Singdata Lakehouse, the more accurate description is:

**Singdata Lakehouse builds SQL analytics, continuous processing, and governance capabilities on unified table objects and unified metadata, enabling data that enters the main platform chain to directly enter standard SQL, data warehouse layer processing, and BI analytics chains.**

This shows up in a few specific ways.

### 1. Analyze Iceberg Tables Directly with Standard SQL

Once data enters `Iceberg tables`, there is no need to switch to a separate "table model specifically for the warehouse."

You can directly:

- Query details
- Do joins, aggregations, and window computations
- Continue layer-by-layer modeling
- Provide query objects for BI
- Use as upstream for Dynamic Tables

Data that enters the main platform chain as Iceberg tables is not "can only store, cannot be used well for analytics." SQL analytics and downstream layer processing can act directly on these table objects.

### 2. MVCC and Time Travel Preserve Warehouse-Side Data Management Capabilities

Traditional data warehouses are suited for analytics not just because they can run SQL — also because they usually have more stable data management semantics.

Singdata Lakehouse preserves these capabilities on open Iceberg tables:

- MVCC multi-version concurrency control
- Time Travel historical version queries
- UNDROP / RESTORE recovery capabilities

This means:

- Iceberg tables are not just "collections of files."
- They also have data manageability closer to the warehouse side.

This determines the Lakehouse is not just "can query lake data," but can use lake data as formal production analytics objects.

### 3. Dynamic Tables Continuously Maintain Analytics Processing

After data enters a table, the next step is usually not to manually run a SQL query, but to continuously generate downstream layer results.

The key object here in Singdata Lakehouse is `Dynamic Table`.

Its significance is not a "convenient feature that auto-refreshes." It is:

- Define a downstream table with standard SQL.
- The system continuously refreshes based on an incremental computation model.
- Downstream results are still formal table objects that can continue to be queried, joined, and consumed.

This unifies the chain from "detail data in the lake" to "layered results in the warehouse."

In many traditional architectures, this path might require:

- External sync tools
- External scheduling systems
- A separate streaming compute engine
- An independent data warehouse processing layer

In Singdata Lakehouse, this path is consolidated into:

- Data sync tasks / Pipe
- Iceberg tables
- Table Stream
- Dynamic Table
- Studio scheduling and governance

## The Role of Dynamic Tables in the Lakehouse Goes Beyond "Auto-Refresh"

If this point is written lightly, the entire document retreats back to the conceptual level.

Treating Dynamic Table as just "a table that refreshes on a schedule" underestimates its role in the Lakehouse.

It handles:

- Moving lake data into stable layered processing chains
- Letting standard SQL cover more scenarios that previously required streaming processing or complex incremental pipelines
- Making data freshness a goal that can be declared and managed

The key underlying implementation is GIC (Generic Incremental Computation):

- Decompose SQL queries into operator-level incremental plans
- Each operator processes its own Delta
- Select incremental or full-table plans based on data statistics and cost
- Guarantee results are semantically equivalent to full recomputation

This means Singdata Lakehouse does not "land data in the lake first and then rely on a separate engine for continuous processing." It builds continuous processing capabilities directly into the Lakehouse table system.

Understanding the Lakehouse in Singdata Lakehouse requires including `Dynamic Table`, GIC, and data freshness together.

## Why Studio Is Also Part of the Lakehouse

Many people think of the Lakehouse only as storage and SQL engines.

That is not enough.

If:

- Data objects are in the Lakehouse
- But sync is outside
- Development is outside
- Scheduling is outside
- Operations is outside

Then it is still not a fully integrated platform.

Singdata Lakehouse puts `Studio` into this main chain:

- Data Integration
- Task development
- Scheduling dependencies
- Run monitoring
- Backfill
- Quality governance

This means the Lakehouse is not just "a storage and query foundation" — it is directly connected to the data engineering workflow.

In Singdata Lakehouse, "Lakehouse integration" shows up not just at the data format level, but also as:

**Integration of data objects, sync chains, development scheduling, and governance operations.**

## Why Governance and Permissions Are Always the First Questions When Deploying a Lakehouse

Many teams do not question the Lakehouse direction — what actually slows down projects is a more concrete question: once files, tables, sync tasks, development tasks, and external catalogs progressively converge onto the same platform, how do permission boundaries remain clear?

These concerns are specific:

- Authorization relationships that were scattered across different systems: how are they managed after migration to a single platform?
- Do External Catalog tables, local `Iceberg tables`, sync tasks, and development tasks risk expanding each other's access scope?
- When different teams share the same platform, who can view, modify, and publish — how are boundaries drawn?
- After consolidation, does auditing, recovery, and data protection need to follow?

Governance and permissions are therefore not supplementary work to add after go-live — they appear together with object models and data flow paths as foundational capabilities.

### Singdata Lakehouse Permission Boundaries Start with Workspace

From the product object perspective, `Workspace` itself is the first boundary.

In [Key Concepts](key-concepts.md) and [Studio Object Relationships and Lifecycle](studio-object-lifecycle-guide.md), `Workspace` is not just a SQL namespace — it also carries the development environment isolation of the Studio layer, including users, roles, VClusters, and Studio task scheduling. This means where data objects are placed, who develops and operates within this boundary, and which tasks are published and run here are all naturally organized within the same boundary.

The value of this is direct. Many teams previously had to understand permissions separately across database systems, scheduling platforms, sync tools, and analytics platforms. In Singdata Lakehouse, the data object boundary and the development collaboration boundary are aligned — governance is no longer just a retrofit of several systems forced together.

### Access Control Is a Complete System, Not a Point Feature

Singdata Lakehouse supports two access control models:

- ACL: grant permissions directly to users
- RBAC: grant permissions to roles first, then assign roles to users

The documentation explicitly recommends RBAC, because as teams grow and objects multiply, roles are easier to maintain than granting to each user individually. At the same time, the platform has no super-user concept that bypasses authentication — all access requires explicit authorization, which matters for production environments.

This permission system does not cover only single table objects. According to the permissions documentation, Workspaces, Schemas, Tables, Views, Dynamic Tables, Volumes, VClusters, and other metadata objects can all be permission boundaries. Studio tasks, scripts, task groups, data sources, and data quality objects also have corresponding role capabilities and operation boundaries. In other words, Singdata Lakehouse does not just unify "table query permissions" — it brings both "data object permissions" and "development object permissions" into the platform's governance scope.

### Why This Reduces Lakehouse Governance Friction

When permission boundaries align with object boundaries, many Lakehouse governance questions become easier to explain.

First, platform-internal objects and externally connected objects no longer require entirely different management patterns. External Catalog tables, files entering through `Volume`, and platform-internal tables from sync tasks all ultimately organize their access paths around the Workspace and platform object system.

Second, data development, task scheduling, and run operations no longer float outside data objects. Who can create tasks, who can submit, who can run, who can use VClusters, who can manage data sources — all of this can be constrained through built-in Workspace roles or custom authorization, rather than waiting until after go-live to patch with external policies.

Third, unified platform does not mean relaxed control. Beyond RBAC and granular `GRANT / REVOKE`, Singdata Lakehouse also puts identity authentication, network isolation, data protection, and recovery capabilities in the same security system, including MFA, SSO, IP allowlists, Private Link, private storage BYOS, Dynamic Masking, storage encryption, Time Travel, `RESTORE TABLE`, and `UNDROP TABLE`. This means organizations bringing more chains into the Lakehouse don't need to build a separate, disconnected security foundation.

Fourth, governance is not just "preventing unauthorized access" — it also includes "can problems be traced after they occur." The security and compliance documentation brings operations logs, job history, and recovery capabilities into the audit and tracing scope. For a unified platform, this means when sync, development, queries, and consumption all converge, problem investigation also has a unified observation surface.

### Why This Affects Whether the Lakehouse Can Enter the Production Main Chain

Many teams ultimately deciding whether to migrate production chains to a Lakehouse care not just about query performance or storage formats — they also care about whether they can remain in control after consolidation.

If consolidation makes permission relationships harder to explain, team boundaries harder to draw, and responsibility between tasks and data objects harder to trace, then even a technically complete platform will struggle to host real production main chains. If instead `Workspace` boundaries, role systems, object authorization, security capabilities, and audit/recovery capabilities can work together, the Lakehouse looks more like an enterprise data platform that can run long-term — not just a new foundation that puts data together.

## Why the Lakehouse Naturally Extends to AI

When the lake and warehouse are already organized around the same table objects, metadata, and development workflow, AI should naturally not be bolted on as another isolated system.

Singdata Lakehouse continues forward on this layer:

- `Semantic View`
- `AI Gateway`
- `AI Functions`
- `Analytics Agent`
- `Data Engineering Agent`
- `MCP Server`

This is not off-topic — it is the Lakehouse's natural extension in the modern data stack.

Because once:

- BI uses one copy of data
- Data warehouse processing uses one copy of data
- AI retrieval and Agents also work around the same data context

The data platform truly moves from "storage and analytics platform" to "unified data working platform."

## What Singdata Lakehouse Is Building

Looking at these capabilities together, Singdata Lakehouse is not providing a standalone query engine, a data lake ingestion layer, or an isolated Studio tool. It aims to bring several types of core work in an enterprise data platform — originally scattered — into the same system:

- Use `Workspace / Schema / Table / Volume / External Catalog / VCluster` to organize data objects, file objects, external catalog objects, and compute resources.
- Use `COPY INTO`, Studio Data Integration, offline sync, real-time sync, multi-table real-time sync, and `Pipe` to continuously ingest data from files, databases, message streams, and object storage.
- Use standard SQL, `Table Stream`, `Dynamic Table`, Studio task development and scheduling to process detail data into continuously updatable data warehouse layer results.
- Use unified permission systems, security capabilities, audit and recovery capabilities to put data objects and development objects in the same governance boundary.
- Use JDBC, MySQL protocol, Python/Java SDK, ZettaPark, dbt, Spark, BI tools, and external AI frameworks to connect platform capabilities to the enterprise's existing technology stack.
- On top of this data foundation, continue providing `Semantic View`, `AI Gateway`, `AI Functions`, `Analytics Agent`, `Data Engineering Agent`, and `MCP Server` AI capabilities.

Singdata Lakehouse is therefore trying to consolidate not a single technology point, but an entire data work main chain: where data comes from, how it enters the platform, how it is continuously processed, how it is constrained by permissions and auditing, and how it continues to be used by BI, applications, analysts, and Agents.

This is why it is neither "only a lake," nor "only a warehouse," nor "two separate systems simply placed side by side." It is closer to a unified data working platform: raw files, Iceberg tables in external catalogs, platform-internal tables, sync chains, data warehouse processing, development scheduling, governance operations, ecosystem integration, and AI consumption — all coordinated around the same object model and the same platform chain.

When organizations build data platforms, they typically encounter several types of problems in sequence:

- Existing data lakes, databases, and message streams: how to bring them in at low cost
- Ingested data: how to process it stably with SQL and incremental mechanisms
- Processed data: how to govern, share, and analyze it within the same platform
- Existing BI, dbt, Spark, Python, and AI tools: how to continue reusing them
- As organizations start bringing AI and Agents into production workflows: how to have them work directly on the same data and within the same permission boundaries

This is the concrete meaning of "Lakehouse" in Singdata Lakehouse, and what makes this product more complete than platforms that address only a single link in the chain.

## Further Reading

- [Understanding Singdata Lakehouse from Your Existing Data Stack](how-to-understand-yunqi-lakehouse-from-existing-data-stack.md)
- [Singdata Lakehouse Key Concepts](key-concepts.md)
- [Studio Object Relationships and Lifecycle](studio-object-lifecycle-guide.md)
- [Incremental Computation and Dynamic Tables](incremental-computing.md)
- [Data Freshness and Dynamic Tables](data_freshness.md)
- [Federated Queries](federation-query.md)
