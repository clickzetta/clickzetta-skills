# Multi-Table Real-Time Sync at Ten-Thousand-Table Scale

[Data Freshness and Dynamic Tables](data_freshness.md) covers the refresh mechanism after data enters the Lakehouse — how dynamic tables detect upstream changes and how the incremental engine recomputes on demand. This article focuses on the layer upstream from that: when data is still on the source side and tables in operational databases continue to grow, how the ingestion pipeline maintains stability. Together, these two topics form the complete freshness chain from source to analytics.

In the early stages of many enterprise data platforms, real-time sync typically deals with a small set of core tables. At this stage, teams can usually accept selecting, configuring, and checking tables one by one — and even having engineers manually update sync configurations when new tables are added or fields are modified on the source side. While this approach is not elegant, it tends to work when the scale is small and the pace of change is slow.

The real pressure usually appears after the business enters an expansion phase. As product lines, tenants, and business modules multiply, source databases no longer consist of a small number of stable operational tables. They gradually evolve into a continuously growing table ecosystem: new business launches bring new tables, feature evolution brings field changes, and historical pipelines require these changes to reach the analytics platform as quickly as possible. At this stage, the problem teams face is no longer "how to sync a few tables" but "how to keep the sync pipeline in step with the continuous changes in business systems."

This document addresses exactly this scenario. It focuses not on moving a fixed set of tables into the Lakehouse once, but on how the sync system remains operable, scalable, and maintainable when source databases continuously add tables, continuously adjust fields, and continuously produce change data.

In Singdata Lakehouse, the multi-table real-time sync capability provided by Studio is built precisely for this kind of scenario. Rather than turning "batch sync" into a larger feature button, it combines historical ingestion, continuous incremental updates, schema change handling, and operational visibility into a single task model — allowing data platforms to keep working as the business continues to evolve.

![](.topwrite/assets/anim-42-multitable-sync.svg)

## Why This Matters in the Modern AI + Data Stack

In the modern AI + Data stack, upper-layer applications increasingly depend on a continuously updated and broader data foundation. Whether it is real-time analytics, intelligent Q&A, operational automation, feature computation, or Analytics Agents targeting business users, these upper-layer capabilities can rarely rely on just a handful of manually curated wide tables once they enter production.

The reason is straightforward. Today's intelligent applications typically need to connect simultaneously to:

- Transaction and order data
- Master data such as users, customers, organizations, and permissions
- Business objects from CRM, ERP, ticketing, finance, configuration, and logs
- Data domains that continuously evolve across multiple product lines, tenants, and modules

This means the underlying data platform no longer just needs to "bring in a batch of tables" — it needs to sustainably absorb a business data ecosystem that is constantly changing and growing. If the underlying sync system cannot keep up with this pace of change, the AI and analytics capabilities built on top will end up with data that is stale, incomplete in coverage, and increasingly expensive to maintain.

From this perspective, the value of multi-table real-time sync at ten-thousand-table scale is not in the "large number" itself, but in the critical capability it gives the data platform: **not only the ability to ingest large-scale business data, but also the ability to keep pace with the continuous change of business systems.**

## When Does the Need for Ten-Thousand-Table Real-Time Sync Arise

Ten-thousand-table real-time sync is not a requirement every system will face. It typically appears in scenarios where business complexity has risen significantly and the data ecosystem has started to be platformized.

Typical scenarios include:

- **Multi-tenant SaaS systems**: as tenant count grows, data objects continuously expand along with customers, modules, and versions
- **Platform-type or mid-platform-type systems**: a single underlying platform serves multiple business lines, and upstream tables and fields are in a state of long-term evolution
- **Large-scale sharded OLTP systems**: after business expansion, data is naturally distributed across a large number of schemas and tables
- **Real-time analytics or real-time data warehouse systems**: not only is data being ingested, it also needs to support analytics, dashboards, metrics, and agents as quickly as possible
- **AI-driven data products**: require broader data coverage and higher data freshness; manual table-by-table ingestion is not an option
- **Enterprise systems after M&A integration, internationalization, or regional deployment**: system boundaries multiply, and both table counts and field complexity expand rapidly

What these scenarios have in common is that the central question has shifted from "do we have sync capability" to "can the sync system continue to operate reliably amid large-scale, continuous change."

## Why "More Tables" Becomes a Qualitative Shift

When the number of tables is still relatively small, the problems caused by change mainly manifest as increased workload. But as the table count grows to a larger scale, the problems gradually shift from workload issues to system capability issues.

This is because at large scale, complexity does not increase linearly. Teams must simultaneously deal with:

- A continuously growing number of sync objects
- Tables with large numbers of fields in their own right
- Source-side table schemas that are still changing
- Full-load and incremental states that do not always advance in lockstep across different tables
- Operations staff who can no longer maintain the entire pipeline through table-by-table inspection

Real-world practice on Singdata Lakehouse has validated data integration capability at the scale of **8,000 tables**, with a focus on verifying **the real-time sync of data changes under schema evolution**. This demonstrates that multi-table real-time sync is not dealing with a small set of static tables, but with a large-scale, continuously changing business data system.

At this scale, maintaining tables one by one becomes a bottleneck in itself. The problems that truly need to be solved have shifted from "building tasks in bulk" to more fundamental questions:

- As the table count continuously grows, avoid having to rebuild tasks or reconfigure the entire sync pipeline every time a new table is added
- As fields continuously change, have the system automatically absorb schema changes rather than requiring users to frequently stop and adjust
- At large numbers of sync objects, still expose running status, change records, and exception boundaries to operations staff

## What Problems Multi-Table Real-Time Sync Is Solving

From the customer requirements perspective, multi-table real-time sync does not address a single-point problem — it addresses three interconnected problems.

The first layer is data ingestion: the large volume of historical data already in operational databases needs to be able to enter the analytics platform.

The second layer is continuous updates: business data is still being continuously added, updated, and deleted, so the sync pipeline cannot remain a one-time import.

The third layer is continuous evolution: the sync objects themselves are still changing — new tables and field changes should not require users to fall back to manual reconfiguration every time.

At the system implementation level, multi-table real-time sync typically needs to handle three types of work simultaneously:

- **Initial full sync**: syncing existing historical data from the source side to the target
- **Subsequent incremental sync**: continuously consuming source-side change logs and writing additions, updates, and deletions to the target in real time
- **Schema change handling**: detecting schema evolution events such as new tables and field changes, and deciding how to incorporate these changes into the existing sync task

Multi-table real-time sync is therefore not simply a "batch sync feature" — it is a sync system that combines historical ingestion, continuous incremental updates, and schema evolution handling.

## Why This Problem Maps to Studio's Multi-Table Real-Time Sync Task

When enterprises truly reach this stage, what they typically need is no longer an "import tool" but a task model capable of running long-term. It must absorb historical data, absorb subsequent incremental changes, and manage the continuous evolution of tables and fields within the same pipeline.

The multi-table real-time sync task provided by Studio is the product-layer answer to this problem. It converges these requirements into a unified task model, allowing users to manage within a single task:

- What the current sync scope is
- How the initial full load and subsequent incremental sync are progressing
- How new tables and field changes enter the existing pipeline
- Where to observe and handle issues when exceptions occur

From this perspective, Studio's multi-table real-time sync is not about making "syncing multiple tables" a larger configuration page — it is about bringing large-scale business data's continuous ingestion, continuous change, and continuous operations into a single work object. For scenarios involving thousands to tens of thousands of tables, this matters more than how convenient a one-time configuration is.

## Why Auto-Adaptation Becomes Important

If the sync system deals with a small number of stable tables, schema changes are typically infrequent events. But in a business environment of thousands to tens of thousands of tables, schema changes become the norm. New module launches bring new tables, existing module evolution brings new fields, and historical tables may continue to expand. At this point, the question is no longer "will there be changes" but "can the system treat changes as a runtime constant."

The importance of auto-adaptation therefore lies not simply in "saving some configuration steps" — it lies in preventing the sync system from becoming increasingly fragile as the frequency of business changes rises.

In multi-table real-time sync tasks, "auto-adaptation" essentially means: when the set of source objects and their schemas change, the system avoids requiring users to rebuild tasks, and instead continues to absorb these changes within the context of the existing sync task.

From a product capability perspective, this typically covers at least two types of changes:

- **New tables**: tables that newly appear on the source side and fall within the current sync scope
- **Field changes**: new fields added, fields deleted, or field structures adjusted in existing source tables

Existing product documentation explicitly places this kind of behavior within the scope of `Schema Evolution` rules. For multi-table mirror/full-database sync tasks, the system handles the behavior after source table and field changes within the sync rules, and allows configuring rules for newly added fields, deleted fields, and deleted tables from the source.

However, it is important to note that auto-adaptation does not mean "all changes require no operational attention." Its meaning is closer to:

- The system will automatically detect and absorb a portion of schema changes
- Users do not need to create new tasks for every change
- But users still need to confirm through the operations page that these changes have successfully entered the full-load or incremental pipeline

## Why Full-Database Mirroring Better Matches This Type of Customer Need

In many large-scale business scenarios, what customers truly need is not "selecting which tables to sync today" but "bringing this entire business database into the sync system and allowing it to continue growing with the business." From this perspective, full-database mirroring more closely matches real needs than table-by-table selection.

The reason is straightforward:

- Table-by-table approaches are better suited for scenarios where the object set is relatively stable and strong selectivity is required
- Full-database mirroring is better suited for scenarios where "the database is still growing, tables are still being added, and fields are still changing"

When the sync scope is an entire business database, the focus of the task is no longer "which tables did I select today" but "as long as this database continues to produce new business tables and schema changes, can the system continue to incorporate them into the sync scope." This is the key transition at large scale — from "selecting objects" to "absorbing changes."

## What Capabilities You Can Expect from the System in This Context

Combining product capabilities and runtime behavior in this type of scenario, the capabilities users truly care about can be summarized into three categories.

### 1. Running Tasks Can Detect New Tables

After a full-database mirror task is running, if a new table is created in the source database that falls within the task scope, the system will automatically detect this change and incorporate the new table into the current sync task.

In this type of task, when a newly added source table enters the current sync scope, common observations during task runtime include:

- The number of sync objects increases from `18` to `19`
- The system automatically generates a sub-task for the new table
- A "new table" event appears in the "source table change records" on the operations page

For full-database mirror tasks, this means a new table is not a purely offline configuration action — it is a dynamic event that is detected and recorded by the system at runtime.

### 2. New Tables Are Not Just Detected — They Also Proceed to Target Table Creation and Data Sync

After the system auto-detects a new table, it does not just add it to the sync object scope — it also continues to drive target-side table creation and data writing.

In this type of scenario, after a new table is detected, users further expect to see:

- The corresponding table automatically appears on the target side
- Data synced from the source can already be queried in the target table

This means "auto-adaptation" in the new-table scenario is not just registering the table name in the task — it connects "detect new table → include in task → create target table → write data" into a continuous pipeline.

### 3. Field Changes on Already-Synced Tables Can Propagate to the Target Schema

For tables already within the sync scope, if new fields are added on the source side, the system can sync those fields to the target table schema during task runtime and continue syncing data changes on those fields.

In field change scenarios, after a new field is added to a source table, common observation points during task runtime include:

- The new field appears in the target table schema
- Data written to that field can also be queried on the target side

This means that in the schema evolution scenario of field additions, the system has the capability to "absorb schema changes and absorb data changes."

## Auto-Adaptation Does Not Mean Zero Maintenance

Auto-adaptation reduces the configuration cost incurred by new table additions and field changes, but it does not mean:

- Every table will unconditionally succeed during its first full sync
- All schema changes require no observation of running status
- No operational involvement is needed after a task is created

In real operation, a common outcome for full-database mirror tasks is that some tables complete full sync and enter incremental mode, while others fail during the initial full-load phase. Auto-adaptation solves "how changes enter the system"; operational capability solves "whether changes that have entered the system complete successfully."

When observing this type of task, the most important thing is not just checking whether the task is "running" — you need to look at several types of information together:

### 1. Whether the Number of Sync Objects Has Changed

In a full-database mirror scenario, after a new table enters the sync scope, the number of sync objects should change. This is the first signal for determining "whether a new table has been incorporated into the current task."

### 2. Whether Events Appear in Source Table Change Records

When the system detects a new table, the operations page will record the corresponding event. This record tells you that the system has identified this change as a runtime event, not a static configuration omission.

### 3. Whether the Target Side Has Actually Created the Table or Added the Field

Seeing an event alone is not enough — you also need to confirm whether a new table has appeared on the target side, or whether a new field has appeared in the target table schema. This step determines "whether auto-adaptation has truly reached the data plane."

### 4. Whether Full-Load and Incremental States Are Progressing Normally

After new tables and field changes are detected, you need to further confirm:

- Whether the initial full load succeeded
- Whether incremental sync has started
- Whether there are tables in a state of "change detected, but still stuck in a failure state"

This step determines "whether auto-adaptation has truly entered a stable running state."

## Related Documentation

- [Data Freshness and Dynamic Tables](data_freshness.md) — the tiered refresh mechanism after data enters the Lakehouse; this article discusses the upstream ingestion stage of that chain
- [Multi-Table Real-Time Sync Task](multitable_realtime_sync.md) — introduction to the multi-table real-time sync feature and configuration overview
- [Multi-Table Real-Time Sync Task Complete Guide](multitable_realtime_sync_sop.md) — the complete operational workflow from task creation to maintenance
- [Real-Time Sync Task](realtime_sync.md) — single-database real-time sync configuration reference
- [Multi-Table Batch Sync Task](multitable_batch_sync.md) — batch ingestion of historical data
- [CDC Data Processing with Multi-Table Real-Time Sync and Dynamic Tables](czguide-intro-to-cdc-using-clickzetta-rtsync-dynamic-tables.md) — end-to-end practice of incremental processing with dynamic tables after ingestion
