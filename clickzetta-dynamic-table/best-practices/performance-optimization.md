# Dynamic Table Performance Optimization Guide

This document helps users write DTs with better incremental refresh performance from three dimensions: SQL writing, data characteristics, and pipeline design.

## Core Principle: The Cost Model of Incremental Refresh

Incremental refresh performance depends on three factors:
1. **Change ratio**: how much data in the source table changed during each refresh. The smaller the change volume, the more worthwhile incremental is.
2. **Operator type**: different SQL operators have very different incremental costs.
3. **Data locality**: whether the changed data is concentrated on JOIN keys / GROUP BY keys / PARTITION BY keys.

When the change volume exceeds a significant proportion of total data, incremental refresh may actually be slower than full refresh, because incremental has additional overhead for change data computation, deduplication merging, state table read/write, etc.

## SQL Writing Optimization

### 1. Prefer INNER JOIN over OUTER JOIN

INNER JOIN incremental computation is more efficient than OUTER JOIN:
- INNER JOIN: only needs to compute A's change data JOIN B's full data + A's full data JOIN B's change data
- LEFT/RIGHT/FULL OUTER JOIN: also needs to handle NULL filling, reverse retraction, and other logic

If business logic can guarantee referential integrity (i.e., JOIN keys will always match), prefer INNER JOIN.

```sql
-- ❌ Unnecessary LEFT JOIN (if product is guaranteed to exist)
SELECT o.*, p.name FROM orders o LEFT JOIN products p ON o.pid = p.id;

-- ✅ Switch to INNER JOIN
SELECT o.*, p.name FROM orders o INNER JOIN products p ON o.pid = p.id;
```

### 2. Reduce Unnecessary DISTINCT

On every incremental refresh, DISTINCT needs to recompute affected keys. If upstream data is already deduplicated, or uniqueness can be guaranteed another way, remove DISTINCT.

```sql
-- ❌ Redundant DISTINCT
SELECT DISTINCT user_id, user_name FROM user_events;
```

### 3. Window Functions Must Have PARTITION BY

Window functions without PARTITION BY cause every incremental refresh to fully recompute the entire window. With PARTITION BY, only affected partitions need to be recomputed.

```sql
-- ❌ Global window; every incremental refresh does a full recomputation
SELECT *, ROW_NUMBER() OVER (ORDER BY created_at DESC) AS rn FROM events;

-- ✅ Add PARTITION BY; only recompute partitions with changes
SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY created_at DESC) AS rn FROM events;
```

### 4. Use Simple Column References as Aggregation Keys

Compound expressions as GROUP BY keys reduce incremental efficiency, because the engine needs to evaluate the expression before determining which keys are affected.

```sql
-- ❌ Compound expression as GROUP BY key
SELECT DATE_TRUNC('hour', ts) AS hour, SUM(amount)
FROM transactions
GROUP BY DATE_TRUNC('hour', ts);

-- ✅ If possible, pre-compute the key column upstream
-- Or split into two DTs (see "Pipeline Splitting" below)
```

### 5. Use Partition Conditions to Limit Data Range Where Possible

Adding partition filter conditions on source tables in the DT's SQL can significantly reduce the amount of data that needs to be scanned on each incremental refresh.

```sql
-- ❌ No partition condition; scans the full table every time
SELECT o.*, p.name
FROM orders o JOIN products p ON o.pid = p.id;

-- ✅ Limit data range with partition condition
SELECT o.*, p.name
FROM orders o JOIN products p ON o.pid = p.id
WHERE o.ds = SESSION_CONFIGS()['dt.args.ds'];
```

## Pipeline Splitting: Break Complex DTs into Multiple Levels

When a DT's SQL contains multiple JOINs + aggregations + window functions, consider splitting it into multiple DTs, each doing one thing.

Benefits:
- Each DT's incremental computation is simpler and faster
- Intermediate DTs can be reused by multiple downstream DTs
- Easier to pinpoint which layer has a problem when issues arise
- Different layers can use different optimization strategies

## Data Characteristics and Incremental Efficiency

### Change Ratio

Incremental refresh works best when the change volume is a small proportion of total data. Rule of thumb:
- < 5%: incremental refresh is usually significantly better than full
- 5% ~ 20%: depends on specific operators and data distribution
- \> 20%: may need to evaluate whether full refresh is more appropriate

### Append-Only Source Tables

If the source table only has INSERT and no UPDATE/DELETE, significant optimization is possible:
- The incremental engine knows change data only has additions (no retractions), and can skip deduplication merging and other operations
- Aggregation can directly accumulate without maintaining complete intermediate state

### Distribution of Changed Data

If changed data is concentrated on a few keys (e.g., recent time periods), incremental efficiency is high. If changes are spread across many keys, aggregation and window functions need to recompute many partitions, reducing efficiency.
