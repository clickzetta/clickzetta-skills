# The Three Building Blocks of a Real-Time Data Pipeline: Pipe, Table Stream, Dynamic Table

Singdata Lakehouse provides three objects for building real-time data pipelines: Pipe, Table Stream, and Dynamic Table. They are often treated as "pick one," but in most cases they are not alternatives — they each handle a different segment and are **assembled into a pipeline together**. Understanding what each block does and how to assemble them matters more than debating "which one to choose" — there is really only one point where a choice is actually required.

---

## One Main Chain, Plus One Optional Branch

![](.topwrite/assets/anim-42-realtime-pipeline.svg)

To understand how data flows, remember one **main chain** first, then treat Table Stream as an **optional branch** layered on top — do not try to fit all three into a single line.

**Main chain (common path)**: External data enters the Lakehouse via **Pipe** (or `COPY INTO` / Studio real-time sync) and becomes an ODS table → **Dynamic Table** declares downstream transformations into DWD/DWS result tables → results are consumed by BI and ad-hoc queries. This is the default form for most real-time pipelines: ingest, transform, query — fully declarative, maintained automatically by the engine. Details for each segment are in later sections.

**Branch: Table Stream — a "change tap" you attach to any table.** It is not a step on the main chain. It is an **on-demand overlay** capability: attach a Table Stream to any table on the main chain (ODS tables or result tables — Dynamic Tables work too, confirmed by testing), and have tasks consume the incremental changes. There are three types of downstream destinations:

1. **Write back into the lakehouse**: `MERGE` into another lakehouse table — for next-layer incremental processing, **audit logging of full change history**, or maintaining **SCD Type 2 slowly changing dimension tables**. This path is also the "write-your-own-MERGE instead of using Dynamic Table" option (see the "One Place You Actually Have to Choose" section below).
2. **Send outside the lakehouse (reverse ETL)**: sync to search (Elasticsearch), OLAP serving (ClickHouse / Doris), low-latency caches (Redis), operational databases (MySQL / PostgreSQL), or message queues (Kafka for redistribution).
3. **Trigger actions**: alerts, risk control, or driving downstream business systems.

> 💡 Table Stream only produces "which rows changed in a given table." **What those changes are written to and what is done with them is decided by the task that consumes the stream** — so it is not a fixed step in the pipeline, but an on-demand branch. The same "change bookmark + task consumer" mechanism, three types of destination: write back into the lakehouse, send outside, trigger actions.

## Tables Come First — Dynamic Table and Stream Come After

Dynamic Table and Table Stream both operate only on **data that is already a table**. Neither is responsible for bringing external data in. So the starting point of every real-time pipeline is always using some import method to turn external data into a table. Singdata Lakehouse provides several ways to ingest data:

- Continuous, automatic capture of data arriving constantly (Kafka, new files in object storage) → **Pipe**
- One-time / batch import → **`COPY INTO`**
- CDC sync from external databases → **Studio real-time sync**

One easy confusion: files in object storage are in "the lake" (Volume), but they are **not yet tables**. Dynamic Table and Table Stream cannot touch them until one of the above methods imports them into a table.

This document covers continuous real-time scenarios, so Pipe is used as the pipeline start. The tradeoff between Pipe and `COPY INTO` is covered in the next section.

## Pipe: Continuously Importing External Data into a Table

Pipe is a **continuously ingesting object** created with SQL: it automatically and continuously writes Kafka messages or files constantly being uploaded to object storage into a regular table. It is essentially **a `COPY INTO` statement wrapped as a resident, auto-scheduled, micro-batch import that automatically records the read position** — files arrive and get ingested, no manual triggering required.

The difference from a one-time `COPY INTO` is "continuous vs. one-time": use `COPY INTO` for a one-shot historical data load; use Pipe when data arrives continuously and you want the system to capture it automatically. Pipe uses `load_history` to record which files have already been imported, preventing the same file from being loaded twice.

> 💡 **Tip**: Pipe only handles importing data into a table — it does not do complex transformation. The table it creates is typically the ODS layer; cleaning and aggregation downstream are handled by Dynamic Table or downstream tasks. Pipe types, parameters, and limitations are in [Pipe](om-pipe.md).

## Table Stream: A Change Bookmark for a Table

Table Stream is not a table that stores data — it is a **"how far have I read" bookmark**: it remembers which version of the source table you last consumed from, and on the next read delivers only the changes since then.

A few rules that form the mental model:

- Querying a Stream adds an extra `__change_type` column: `INSERT` / `UPDATE_BEFORE` / `UPDATE_AFTER` / `DELETE`. A single `UPDATE` produces two rows: `UPDATE_BEFORE` (old value) + `UPDATE_AFTER` (new value).
- **Only DML consumption advances the offset**: no matter how many times you `SELECT`, the data stays. Once an `INSERT INTO ... SELECT ... FROM stream` or `MERGE ... USING stream` successfully commits, the offset advances and that batch of changes is consumed. Transaction rollback leaves the offset unchanged and allows re-consumption — this guarantees exactly-once processing.
- A single Stream can only be fully consumed by one consumer. If multiple downstream consumers each need a copy, create a separate Stream for each (Streams only store the offset, not a copy of data, so creating multiple is low cost).
- `STANDARD` captures inserts, updates, and deletes. `APPEND_ONLY` captures only inserts and is more lightweight.

Streams can also be created on **Dynamic Tables**: changes produced by a Dynamic Table refresh can also be captured by a Stream — so the "optional tap" described earlier can be attached to result tables (even if they are Dynamic Tables themselves), to forward processed result changes downstream. Details on consume offsets, expiry (STALE), and other behavior are in [Table Stream](om-table-stream.md).

## Dynamic Table: A Declaratively Self-Maintaining Derived Table

Dynamic Table is the primary object for transformations inside the lakehouse: you write a `SELECT` statement declaring what the target table "should equal," and the engine automatically handles incremental computation, retractions, and when to refresh. It is designed specifically for building ODS→DWD→DWS processing chains. Design patterns, types of processing, and approach are in [Dynamic Table Design](dynamic-table-design.md).

## The One Place You Actually Have to Choose: Declarative or Procedural

The three objects are mostly a composition, not a competition. The one place where a real choice is required is: **for transformations inside the lakehouse, use Dynamic Table, or Table Stream + task?** Both can process upstream changes into a target table and keep it fresh, but in fundamentally different ways:

- **Dynamic Table = declare the result.** You write one `SELECT`. The engine maintains incremental computation, retractions, scheduling, and dependency ordering automatically.
- **Table Stream + task = write the procedure.** The engine hands you "which rows changed." You write how to `MERGE`, how to subtract refunds, how to handle failures, how to ensure exactly-once — all of that procedure is yours to write.

Put differently, **Table Stream + task is the hand-written version of the procedure Dynamic Table automates for you** (see the "what you have to write without Dynamic Table" opening of [Dynamic Table Design](dynamic-table-design.md)).

If declarative is so much simpler, why would you choose procedural? Because some control cannot be given up in a declarative model. Use Table Stream + task when you need any of the following:

- Custom `MERGE` / composite-key upsert, or a single change must be written to multiple target tables.
- Maintaining SCD Type 2 (history-preserving slowly changing dimensions).
- The transformation needs to call stored procedures or External Functions (not allowed in a Dynamic Table `SELECT`).
- You need to directly insert/update/delete on the result table (for example, GDPR deletion requests — Dynamic Tables are read-only).
- You need CRON-precise scheduling, custom retry, or sub-minute intervals with special logic.

Conversely, if the target can be expressed in a single standard `SELECT` and minute-level freshness is sufficient, hand it to Dynamic Table — do not write that procedure yourself. Complete decision trees and architecture patterns are in [Real-Time Pipeline Selection Guide](realtime-pipeline-selection-guide.md).

## Each Object in Its Place

- External data into the lakehouse: continuous ingestion → **Pipe**; one-time / batch → **`COPY INTO`**; database CDC → **Studio real-time sync**.
- Keeping a lakehouse derived table fresh when the target can be expressed in a single `SELECT` → **Dynamic Table**.
- Transformations requiring control that declarative cannot provide (custom MERGE, SCD slowly changing dimensions, stored procedures / External Functions, direct result modification, precise scheduling) → **Table Stream + task**.
- Capturing changes from a table and having tasks process them (write back into the lakehouse / send outside / trigger actions) → **Table Stream**.

## Related Documents

- [Real-Time Pipeline Selection Guide](realtime-pipeline-selection-guide.md): decision trees, four architecture patterns, complete runnable examples
- [Pipe](om-pipe.md): Pipe types, parameters, and limitations
- [Table Stream](om-table-stream.md): change types, consume offsets, expiry mechanism
- [Dynamic Table Design: From Processing Goal to Incremental Pipeline](dynamic-table-design.md): four forms of declarative incremental processing
- [Why Dynamic Tables Go Full-Table and How to Preserve Incremental](dynamic-table-full-vs-incremental.md): how refresh mode is determined
