# Lakehouse Small File Compaction Optimization Guide (OPTIMIZE)

## Overview

In data warehouses, frequent small-batch writes (such as real-time CDC, streaming ingestion) can cause numerous small files to accumulate at the table storage layer, severely impacting query performance. Singdata Lakehouse provides the `OPTIMIZE` command, which automatically merges small files into larger files, reducing I/O overhead and improving query speed. This guide is organized by business scenario to help you quickly master small file compaction methods.

### Quick Navigation

* [Full Table Small File Compaction](#full-table-small-file-compaction) -- Merge small files across all partitions
* [Partition-level Compaction](#partition-level-compaction) -- Merge small files in specific partitions only
* [View Compaction Results](#view-compaction-results) -- Compare file counts before and after compaction
* [Auto-compaction Configuration](#auto-compaction-configuration) -- Enable automatic compaction after commit

***

## SQL Commands Covered

| Command | Purpose | Use Case |
|------|------|----------|
| `OPTIMIZE table_name` | Full table small file compaction | Regular maintenance to improve overall query performance |
| `OPTIMIZE table_name WHERE ...` | Partition-level compaction | Compact specific partitions only, saving resources |
| `SET cz.sql.compaction.after.commit = true` | Enable auto-compaction | Automatic file health maintenance for real-time write scenarios |

***

## Prerequisites

The following examples use a simulated log table `logs_optimize`:

```sql
-- Create test table
CREATE TABLE IF NOT EXISTS logs_optimize (
    log_id INT,
    message STRING,
    log_date DATE
);

-- Simulate multiple small-batch writes (producing small files)
INSERT INTO logs_optimize VALUES (1, 'Log A', '2024-06-01');
INSERT INTO logs_optimize VALUES (2, 'Log B', '2024-06-01');
INSERT INTO logs_optimize VALUES (3, 'Log C', '2024-06-02');
```

***

## Full Table Small File Compaction

Use the `OPTIMIZE` command to compact small files across the entire table.

```sql
-- Execute full table optimization
OPTIMIZE logs_optimize;
```

**Execution Notes**:
* The system scans all data files in the table and merges files smaller than the threshold into larger files.
* If the table already has few files or is in a healthy state, it may return `No compaction job generated`, indicating no compaction is needed.
* The compaction process does not affect ongoing queries; old and new files are smoothly switched via MVCC.

***

## Partition-level Compaction

If the table is partitioned by date, you can compact only specific partitions to avoid the resource consumption of a full table scan.

```sql
-- Compact only the 2024-06-01 partition (requires table to be partitioned by log_date)
OPTIMIZE logs_optimize WHERE log_date = '2024-06-01';
```

> ⚠️ **Note**: `OPTIMIZE WHERE` only applies to tables with defined partitions. For non-partitioned tables, use the full-table `OPTIMIZE`.

***

## View Compaction Results

After compaction completes, you can view optimization results via `DESC HISTORY` or file statistics.

```sql
-- View table history (including OPTIMIZE operation records)
DESC HISTORY logs_optimize;
```

**Returned Information**:
* `operation`: Operation type (OPTIMIZE)
* `total_rows`: Total row count (unchanged)
* `total_bytes`: Storage size (typically reduced due to compression)

> 💡 **Tip**: Query performance improvements can be verified by comparing the `TableScan` operator cost before and after compaction using `EXPLAIN`.

***

## Auto-compaction Configuration

For real-time write scenarios, manual `OPTIMIZE` execution may not be timely enough. You can enable auto-compaction.

```sql
-- Enable session-level auto-compaction
SET cz.sql.compaction.after.commit = true;
```

**Effect**:
* After each `INSERT` or `DELETE` commit, the system automatically triggers background small file compaction.
* Suitable for streaming data ingestion scenarios (such as Kafka Pipe, CDC synchronization).

> ⚠️ **Note**: Auto-compaction slightly increases write latency; evaluate whether to enable it based on business tolerance.

***

## Clean Up Test Data

After completing optimization verification, it is recommended to clean up the test table:

```sql
-- Drop test table
DROP TABLE IF EXISTS logs_optimize;
```

> 💡 **Tip**: Lakehouse supports `UNDROP TABLE`, allowing recovery of accidentally dropped tables within the retention period.

***

## Notes

1. **Execution Timing**: It is recommended to execute `OPTIMIZE` during off-peak hours to avoid competing for compute resources with high-priority queries.
2. **Frequency Control**: Daily execution is unnecessary. Usually, weekly or monthly execution is sufficient to maintain file health.
3. **Storage Changes**: After compaction, the number of files decreases, but total data volume may vary slightly due to compression algorithms.
4. **Dynamic Tables**: The refresh process of Dynamic Tables automatically handles underlying files; manual `OPTIMIZE` is usually unnecessary.
5. **Resource Consumption**: `OPTIMIZE` is a compute-intensive operation that consumes VCluster CPU and memory resources.

***

## Related Documentation

* [OPTIMIZE](optimize.md)
* [Small File Optimization](small_file_optimization.md)
* [ANALYZE TABLE](analyze-table.md)
