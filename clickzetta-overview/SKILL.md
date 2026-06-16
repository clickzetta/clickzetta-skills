---
name: clickzetta-overview
description: |
  ClickZetta Lakehouse product overview: core concepts, object model, architecture, and Studio module introduction.
  Covers: Account/Instance/Workspace/Schema hierarchy, VCluster types and CRU billing, Dynamic Table,
  Table Stream CDC, Pipe, Synonym, permission system (RBAC/ACL), storage-compute separation,
  brand relationships (ClickZetta = Yunqi = Singdata), and Studio six modules.
  Trigger when user asks: "what is a workspace", "what is a VCluster", "what is CRU",
  "Lakehouse architecture", "object hierarchy", "permission system", "compare concepts with Snowflake",
  "what is Studio", "storage-compute separation", "ClickZetta introduction".
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
