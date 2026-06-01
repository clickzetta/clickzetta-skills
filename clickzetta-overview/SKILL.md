---
name: clickzetta-overview
description: |
  ClickZetta Lakehouse product overview: core concepts, object model, architecture, and Studio module introduction.
  Covers: Account/Instance/Workspace/Schema object hierarchy, Workspace vs Database/Catalog mapping,
  VCluster three types and CRU billing, Dynamic Table incremental refresh mechanism, Table Stream CDC,
  three-tier cache system, Pipe continuous ingestion, Synonym cross-Schema alias, permission system (RBAC/ACL),
  key differences vs Snowflake/Databricks, storage-compute separation architecture,
  brand relationships (ClickZetta = Yunqi = Singdata) and service endpoints per environment,
  Studio six modules (Data Development IDE, Task Scheduling, Data Integration, Data Catalog, Data Quality, Operations Monitoring).
  Trigger when user asks: "what is a workspace", "what is the relationship between Schema and Database", "what is a Catalog",
  "what is a VCluster", "what is CRU", "difference between internal and external tables", "Lakehouse architecture",
  "object hierarchy", "permission system", "compare concepts with Snowflake", "compare concepts with Databricks",
  "storage-compute separation", "what is Yunqi", "what is Singdata", "relationship between ClickZetta and Yunqi",
  "what is Studio", "what features does Studio have", "how to use task scheduling", "how to use data integration",
  "data catalog", "data quality", "operations monitoring".
  当用户说"工作空间是什么"、"工作空间和 Schema 什么关系"、"Schema 和 Database 什么关系"、
  "Catalog 是什么"、"VCluster 是什么"、"CRU 是什么"、"CRU 怎么计费"、
  "内部表和外部表区别"、"Lakehouse 架构"、"对象层级"、"对象模型"、
  "权限体系"、"权限怎么管理"、"和 Snowflake 概念对比"、"和 Databricks 概念对比"、
  "存算分离"、"云器是什么"、"Singdata 是什么"、"ClickZetta 和云器什么关系"、
  "Studio 是什么"、"Studio 有哪些功能"、"Studio 有哪些模块"、
  "任务调度怎么用"、"数据集成怎么用"、"数据目录"、"数据质量"、"运维监控"、
  "Dynamic Table 是什么"、"Table Stream 是什么"、"Pipe 是什么"、"Synonym 是什么"、
  "三层缓存"、"Time Travel"、"ClickZetta 介绍"、"产品介绍"时触发。
  Not suitable for: specific SQL syntax (use sql-syntax-guide), specific metadata queries (use metadata),
  specific data ingestion operations (use pipeline skill), specific permission operations (use access-control).
  Keywords: concepts, architecture, workspace, schema, VCluster, Studio, overview, object model
---

# ClickZetta Lakehouse Product Overview

## Reference Documents

| Document | Content |
|------|------|
| [references/object-model.md](references/object-model.md) | Object hierarchy, concept comparisons, unique design details |
| [references/brands-and-endpoints.md](references/brands-and-endpoints.md) | Brand relationships, service endpoints per environment |
| [references/studio-modules.md](references/studio-modules.md) | Studio six modules detailed features |

---

## Object Hierarchy Overview

```
Account
└── Instance                      ← Resource isolation unit
    └── Workspace                 ← ≈ Snowflake Database / Databricks Catalog
        ├── Schema                ← Namespace, permission boundary
        │   ├── Managed Table / External Table / View / Dynamic Table / Materialized View
        │   ├── Volume / Table Stream / Pipe / Index / Synonym
        │   └── Function / External Function
        ├── Share / Connection / External Catalog
        └── VCluster (compute cluster)
```

---

## Core Concepts Quick Reference

| Concept | Description |
|------|------|
| CRU | Cross-cloud unified compute unit, billed by CRU×hour; no charge when cluster is stopped |
| VCluster | Three types: General Purpose (GP), Analytics (AP), Integration (INTEGRATION) |
| Dynamic Table | Declarative incremental computation, CBO-adaptive incremental/full refresh, minimum 1-minute interval |
| Table Stream | CDC change capture object, requires enabling `change_tracking` first |
| Pipe | Continuous ingestion object (Kafka/OSS), each Pipe maps to a dedicated Volume |
| Synonym | Cross-Schema alias, no data copying |
| Three-tier Cache | Result cache + metadata cache + local disk cache (AP supports PRELOAD) |

---

## Key Differences vs Snowflake/Databricks

| ClickZetta | Snowflake | Databricks | Difference |
|---|---|---|---|
| Workspace | Database | Catalog | One account can have multiple instances across clouds |
| VCluster (3 types) | Warehouse | SQL Warehouse | GP/AP/INTEGRATION separation |
| Studio (built-in) | Requires 3rd party | Requires 3rd party | Built-in scheduling/integration/quality/catalog |
| Dynamic Table (CBO) | Dynamic Table | Streaming Table | CBO-based, not stream-based |
| Synonym | — | — | ClickZetta-specific |

---

## Studio Six Modules

| Module | Core Capabilities |
|------|---------|
| Data Development | Web IDE, supports SQL/Python/Shell/JDBC/Dynamic Table/Sync tasks |
| Task Scheduling | Cron scheduling + DAG orchestration + task groups + backfill + parameter variables |
| Data Integration | 30+ data sources, no-code sync (batch/realtime/CDC) |
| Data Catalog | Global search, table details, data lineage, data preview |
| Data Quality | 6-dimension rules (completeness/uniqueness/consistency/accuracy/validity/timeliness) |
| Operations Monitoring | Task instance operations + alert rules + Lark/WeCom notifications |

---

## Brand Relationships

ClickZetta (technology brand) = Yunqi (domestic brand) = Singdata (international brand)

See [references/brands-and-endpoints.md](references/brands-and-endpoints.md) for service endpoints per environment.

---

## Storage Architecture

- Storage-compute separation: VCluster suspension incurs no compute charges
- Open format: internal tables based on Apache Iceberg
- Multi-cloud multi-region: Alibaba Cloud / Tencent Cloud / AWS
- Bring Your Own Storage (BYOS): supports your own OSS/S3/COS
