---
name: clickzetta-data-ingest-pipeline
description: |
  Router skill: selects the best data ingestion method for ClickZetta Lakehouse based on
  data source, latency, sync scope, and continuity requirements. Routes to specialized skills:
  Kafka Pipe, OSS/S3/COS Pipe, Studio batch sync, Studio real-time sync, Studio CDC,
  file/URL import, or SDK ingestion.
  Trigger: user wants to get external data INTO Lakehouse but hasn't chosen a method, OR
  asks which ingestion approach fits their scenario.
  Covers: Kafka, MySQL, PostgreSQL, SQL Server, TiDB, OSS, S3, COS, local files, URLs,
  Java SDK, Python/ZettaPark. Does NOT cover: querying data, pipeline monitoring/diagnosis,
  Dynamic Table tuning, internal table transformations, or data export.
  Keywords: data ingestion, import, sync, ETL, migrate, load data, ingest, pipeline selection
---

# Lakehouse Data Ingestion Router

Routes users to the correct ingestion skill based on data source, latency requirements, sync scope, and whether continuous sync is needed. Scoped to **external data → Lakehouse** only.

## Applicable Scenarios

- User wants to import data into ClickZetta Lakehouse but is unsure which method to use
- User describes a data source and needs an ingestion recommendation
- User asks about differences between ingestion methods

## Decision Matrix

### Step 1: Collect Requirements

1. **Data source type**: Kafka / Object storage (OSS/S3/COS) / Relational DB (MySQL/PostgreSQL/SQL Server/TiDB) / Local file / URL / Java SDK / Python
2. **Latency**: Real-time (seconds) / Near real-time (minutes) / Batch (hours/days)
3. **Sync scope**: Single table / Multiple tables / Entire database
4. **Continuity**: One-time import / Continuous incremental sync
5. **CDC needed**: Yes / No

### Step 2: Route

| Data Source | Latency | Scope | Route To |
|-------------|---------|-------|----------|
| Kafka | Real-time/Near real-time | Single topic (SQL Pipe) | `clickzetta-kafka-ingest-pipeline` |
| Kafka | Real-time | Single topic (Studio task) | `clickzetta-realtime-sync-pipeline` |
| OSS/S3/COS | Near real-time | Files arriving continuously | `clickzetta-oss-ingest-pipeline` |
| OSS/S3/COS | One-time batch | Bulk files from bucket | `clickzetta-oss-ingest-pipeline` (batch mode) |
| Local file / URL | One-time | Single/multiple files | `clickzetta-file-import-pipeline` |
| MySQL/PG/SQL Server/TiDB | Real-time CDC | Single table | `clickzetta-realtime-sync-pipeline` |
| MySQL/PG/SQL Server/TiDB | Real-time CDC | Multiple tables / Entire DB | `clickzetta-cdc-sync-pipeline` |
| MySQL/PG/SQL Server | Offline batch | Single table | `clickzetta-batch-sync-pipeline` |
| MySQL/PG/SQL Server | Offline batch | Multiple tables / Entire DB | `clickzetta-batch-sync-pipeline` |
| Java application | Real-time/Batch | Programmatic write | `clickzetta-java-sdk` |
| Python/ZettaPark | Batch | DataFrame write | `clickzetta-zettapark` / `clickzetta-app-python-sdk` |
| Small data (manual) | One-time | Few rows | Direct SQL INSERT (see below) |

### How to Choose Between Similar Options

| Scenario | Option A | Option B | Differentiator |
|----------|----------|----------|----------------|
| Kafka → Lakehouse | `clickzetta-kafka-ingest-pipeline` | `clickzetta-realtime-sync-pipeline` | Pipe: SQL-native, flexible transforms, no Studio. Studio task: UI-based JSONPath config. |
| OSS one-time import | `clickzetta-oss-ingest-pipeline` (batch) | `clickzetta-file-import-pipeline` | OSS skill: creates Connection + External Volume. File skill: uses existing/User Volume. |
| Single-table CDC | `clickzetta-realtime-sync-pipeline` | `clickzetta-cdc-sync-pipeline` | Realtime-sync: simpler for single table. CDC: more operational depth, alerting, repair. |
| Batch single vs multi | Same skill | Same skill | `clickzetta-batch-sync-pipeline` handles both; multi-table also supports sharded-table merge. |

### Key Constraints

| Skill | Constraints |
|-------|-------------|
| `clickzetta-kafka-ingest-pipeline` | PLAINTEXT/SASL_PLAINTEXT only (no SSL/mTLS); GP VCluster |
| `clickzetta-realtime-sync-pipeline` | Sync VCluster required; Studio datasource config; no test mode before deployment |
| `clickzetta-cdc-sync-pipeline` | Source tables must have PKs; Studio datasource (not SQL Connection); Sync VCluster |
| `clickzetta-batch-sync-pipeline` | Studio datasource; Sync VCluster; field mapping configured in Studio UI |
| `clickzetta-oss-ingest-pipeline` | Dedicated Volume per Pipe (no sharing); same cloud provider as Lakehouse instance |

## Direct Execution for Simple Scenarios

For trivial imports that don't need a specialized skill:

```bash
# SQL INSERT (small data volume)
cz-cli sql "INSERT INTO schema_name.table_name (col1, col2, col3) VALUES ('val1', 'val2', 'val3')" --sync

# COPY INTO from Volume
cz-cli sql "COPY INTO schema_name.table_name FROM VOLUME volume_name USING CSV OPTIONS('header'='true') FILES('data.csv')" --sync
```

## Error Handling

| Scenario | Resolution |
|----------|-----------|
| User cannot identify data source type | Ask where data currently lives (which system/service) |
| Multiple data sources | Split into separate tasks, route each independently |
| Cloud environment doesn't support a connection | `cz-cli sql "SHOW CONNECTIONS" --sync` to check available types |
| TB-scale data volume | Prefer PIPE or Studio sync tasks (support checkpoint resume) |
| No Sync VCluster available | Studio sync tasks (batch/realtime/CDC) require Sync VCluster — check with `cz-cli sql "SHOW VCLUSTERS" --sync` |

## Notes

- This skill is a routing entry point — it does not execute complex pipeline setup
- Data warehousing (into managed tables) is the default; data lake loading (into Volume/object storage) is for staging or cross-system sharing
- Consider user's cloud environment (Alibaba Cloud/Tencent Cloud/AWS) — cross-cloud ingestion is not supported
