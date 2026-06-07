# ClickZetta Lakehouse Object Model Reference

> Source: Official product documentation at yunqi.tech
> Reference: clickzetta-lakehouse-architecture.html

---

## ClickZetta Unique Concepts Quick Reference

| Concept | What Makes It Unique | Common Misconceptions |
|---|---|---|
| CRU | Cross-cloud unified compute unit; legacy sizes XS/S/M/L have migrated to numeric 1/2/4/8 | Not Snowflake Credits, not DBUs |
| VCluster (3 types) | GP/AP/Integration each have distinct use cases; Dynamic Table must use GP | AP clusters do not support small file compaction |
| Dynamic Table | CBO-adaptive incremental/full refresh; `OR REPLACE` preserves data | Minimum 1 minute, not second-level streaming |
| Table Stream | Requires `ALTER TABLE SET PROPERTIES ('change_tracking'='true')` first | Newly written data needs ~1 minute before it can be read |
| Pipe | Each Pipe maps to a dedicated Volume, not reusable | Not Snowflake Snowpipe; no auto-trigger |
| Synonym | Supports cross-Schema aliases; VOLUME/FUNCTION types require explicit keyword declaration | Not a view; does not copy data |
| Permission system | No superuser; instance roles and workspace roles are independent | instance_admin cannot directly operate workspace data |
| Workspace | Must be specified at connection time; ≈ Snowflake Database | Not Databricks Workspace (that is instance-level) |
| Schema TYPE | MANAGED (platform-managed storage) / EXTERNAL (external data lake) | EXTERNAL Schema does not support DML |

---

## Complete Object Hierarchy

```
Account
│  Globally unique · SSO/MFA · identity verification
│
└── Instance
    │  Resource isolation · multi-cloud multi-region · Instance Role
    │
    └── Workspace
        │  Business isolation · Workspace Role · VCluster binding · task scheduling
        │
        ├── Schema (database/namespace)
        │   │  MANAGED / EXTERNAL type
        │   │
        │   ├── Managed Table          — Iceberg · ACID · Time Travel · indexes
        │   ├── External Table         — Delta/Hudi/Kafka · read-only
        │   ├── View                   — virtual · no storage
        │   ├── Dynamic Table          — declarative incremental refresh
        │   ├── Materialized View      — pre-computed · scheduled refresh
        │   ├── Volume                 — User/Table/External(OSS/S3/COS)
        │   ├── Table Stream           — CDC change capture
        │   ├── Pipe                   — Kafka/OSS continuous ingestion
        │   ├── Function / External Function  — SQL UDF / Python / Java
        │   ├── Index                  — BloomFilter / Inverted / Vector(HNSW)
        │   └── Synonym                — cross-Schema alias
        │
        ├── Share                      — zero-copy cross-account data sharing
        ├── Connection                 — Storage(OSS/COS/S3) / API(cloud functions)
        └── External Catalog           — Hive HMS / Iceberg REST / Databricks Unity
```

---

## Workspace Details

### Core Role

Workspace is the **minimum unit of business isolation** in ClickZetta, and the object that must be specified at connection time.

- Equivalent to Snowflake's **Database**, or Databricks' **Catalog**
- Each Workspace has its own: user roles, VClusters, task scheduling, INFORMATION_SCHEMA
- The `workspace` field in connection parameters refers to this object

### Management Commands

```sql
-- List all workspaces (requires instance_admin)
SHOW WORKSPACES;

-- View workspace details
DESC WORKSPACE my_workspace;

-- Update comment
ALTER WORKSPACE my_workspace SET COMMENT 'production environment';

-- View properties
SHOW PROPERTIES IN WORKSPACE my_workspace;
```

### DESC WORKSPACE Output Fields

| Field | Description |
|---|---|
| name | Workspace name |
| creator | Creator |
| created_time | Creation time |
| last_modified_time | Last modified time |
| comment | Comment |

---

## Schema Details

### Core Role

Schema is the **namespace** in ClickZetta, used to organize data objects.

- Equivalent to a traditional database's **Database** or **Schema** (note: naming varies across systems)
- The boundary for permission grants (permissions can be granted on an entire Schema)
- Types: `MANAGED` (platform-managed storage) / `EXTERNAL` (external data lake path)

### Management Commands

```sql
-- Create a Schema
CREATE SCHEMA my_schema;

-- Create an external Schema (pointing to an external data lake)
CREATE EXTERNAL SCHEMA ext_schema LOCATION 'oss://bucket/path/';

-- Switch default Schema
USE SCHEMA my_schema;

-- List all Schemas
SHOW SCHEMAS;

-- View Schema details
DESC SCHEMA my_schema;

-- Modify Schema
ALTER SCHEMA my_schema RENAME TO new_schema;
ALTER SCHEMA my_schema SET COMMENT 'data warehouse layer';

-- Drop Schema (must drop all objects inside first)
DROP SCHEMA my_schema;
DROP SCHEMA IF EXISTS my_schema CASCADE;  -- cascade drop all objects
```

---

## VCluster (Compute Cluster) Details

### Three Types Comparison

| Attribute | General Purpose (GENERAL) | Analytics (ANALYTICS) | Integration (INTEGRATION) |
|---|---|---|---|
| Use Case | ETL, batch ingestion, Ad-Hoc | High-concurrency BI, online queries | Data integration, CDC sync |
| Scaling | Vertical (resize) | Horizontal (1–10 replicas) | — |
| Minimum Size | 1 CRU | 1 CRU | 0.25 CRU |
| Maximum Size | 256 CRU | 256 CRU | 256 CRU |
| Size Increment | 1 CRU | 1 CRU | 0.25 CRU |
| Local Cache | Not supported | Supported (PRELOAD) | Not supported |
| Small File Compaction | Supported (recommended for Dynamic Table) | Not supported | — |

### Task Type to Cluster Mapping

| Task Type | Recommended Cluster |
|---|---|
| SQL ETL / batch ingestion | General Purpose |
| Ad-Hoc queries / BI | Analytics |
| Dynamic Table (low-frequency, large volume) | General Purpose |
| Dynamic Table (high-frequency, small volume) | Analytics |
| Offline sync / realtime sync / CDC | Integration |
| Python / Shell / JDBC tasks | No VCluster needed |

### Management Commands

```sql
-- Create a General Purpose cluster
CREATE VCLUSTER my_gp TYPE GENERAL SIZE 4;

-- Create an Analytics cluster (elastic 1–4 replicas)
CREATE VCLUSTER my_ap TYPE ANALYTICS SIZE 8 MIN_INSTANCE 1 MAX_INSTANCE 4;

-- Resume / Suspend
ALTER VCLUSTER my_gp RESUME;
ALTER VCLUSTER my_gp SUSPEND;

-- List all clusters
SHOW VCLUSTERS;
```

---

## User and Permission System

### User Hierarchy

```
Global Account User
│  Managed at account level; user_name is globally unique
│
└── Instance User
    │  Auto-synced from global user; gets instance_user role by default (no data permissions)
    │
    └── Workspace User
        Can operate data only after being granted a workspace role via GRANT ROLE
```

### User Types

| Type | Description |
|---|---|
| Regular user | Represents a real person; can log in via web |
| System service user | Platform built-in, disabled by default (e.g., sysservice_auto_mv) |
| Custom service user | For automation programs; cannot log in via web; can use JDBC |

### Built-in Roles

| Role | Level | Permission Scope |
|---|---|---|
| instance_admin | Instance | Manage all workspaces, users, External Catalogs |
| instance_user | Instance | Default role; no data permissions |
| workspace_admin | Workspace | Manage all objects and users within the workspace |
| workspace_dev | Workspace | Read/write permissions + task management |
| workspace_analyst | Workspace | Read-only permissions |

### Authorization Commands

```sql
-- Grant a role to a user
GRANT ROLE workspace_dev TO USER alice;

-- Grant table permissions
GRANT SELECT ON TABLE my_schema.my_table TO ROLE analyst_role;
GRANT SELECT ON ALL TABLES IN SCHEMA my_schema TO ROLE analyst_role;

-- Grant information_schema query permissions
GRANT ALL ON ALL VIEWS IN SCHEMA information_schema TO ROLE analyst_role;

-- Revoke permissions
REVOKE SELECT ON TABLE my_schema.my_table FROM ROLE analyst_role;

-- Create a custom role (workspace-level only, SQL only)
CREATE ROLE my_custom_role;
```

---

## Data Types Quick Reference

| Category | Types |
|---|---|
| Integer | TINYINT / SMALLINT / INT / BIGINT |
| Floating point | FLOAT / DOUBLE / DECIMAL(p,s) |
| String | CHAR(n) / VARCHAR(n) / STRING (max 16MB) |
| Datetime | DATE / TIMESTAMP (with timezone LTZ) / TIMESTAMP_NTZ / INTERVAL |
| Boolean | BOOLEAN |
| Complex | ARRAY\<T\> / MAP\<K,V\> / STRUCT\<field:type,...\> |
| AI-specific | VECTOR(FLOAT, n) (max 65535 dimensions) / VECTOR(TINYINT, n) |
| Special | JSON / BINARY / BITMAP (Roaring Bitmap) |

---

## Platform Architecture Layers

```
Client layer:  Studio IDE · JDBC/ODBC · Python SDK · ZettaPark · BI tools · MCP Server
    ↓
Compute layer: VCluster (GENERAL / ANALYTICS / INTEGRATION)
    ↓
Service layer: SQL parsing & optimization · vectorized execution engine · Dynamic Table · AI Gateway · Result Cache
    ↓
Storage layer: Managed Table (Iceberg) · External Table · Volume · Time Travel · External Catalog · Share
    ↓
Object storage: Alibaba Cloud OSS · AWS S3 · Tencent Cloud COS
```

**Storage-compute separation**: compute and storage layers scale independently; VCluster suspension incurs no compute charges; storage is billed per GiB.

---

## Data Object Comparison

### Dynamic Table vs Materialized View vs View

| Dimension | Dynamic Table | Materialized View | View |
|---|---|---|---|
| Data storage | Yes (materialized) | Yes (materialized) | No (virtual) |
| Refresh method | Auto incremental/full (CBO decision) | Manual or scheduled full refresh | Executes at query time |
| Minimum refresh interval | 1 minute | No limit (manual) | — |
| Time Travel | Supported | Not supported | Not supported |
| UNDROP | Supported | Not supported | Not supported |
| CREATE OR REPLACE | Supported (preserves data and permissions) | Supported | Supported |
| Recommended cluster | GP (General Purpose) | GP or AP | — |
| Use case | Realtime ETL, multi-level cascading | BI acceleration, fixed aggregations | Simple logic encapsulation |

### Table Stream Two Modes

| Mode | Captured Content | Typical Use |
|---|---|---|
| STANDARD | INSERT + UPDATE_BEFORE + UPDATE_AFTER + DELETE | CDC UPSERT, MERGE INTO consumption |
| APPEND_ONLY | INSERT only | Log append, simple ETL |

**STANDARD mode delta semantics**: records the net change between two offsets. If a row is INSERTed then DELETEd, the delta shows neither record (not INSERT+DELETE).

### Pipe Two Ingestion Modes

| Mode | Trigger | Use Case | Cloud Support |
|---|---|---|---|
| LIST_PURGE | Periodic scan of Volume directory | General, any object storage | All |
| EVENT_NOTIFICATION | Cloud message queue event trigger | Low latency, near-realtime | Alibaba Cloud OSS + AWS S3 only |

---

## Regions and Connection Information

| Cloud Provider | Region | Region Code | API Endpoint |
|---|---|---|---|
| Alibaba Cloud | East China 2 (Shanghai) | cn-shanghai-alicloud | cn-shanghai-alicloud.api.clickzetta.com |
| Tencent Cloud | East China (Shanghai) | ap-shanghai-tencentcloud | ap-shanghai-tencentcloud.api.clickzetta.com |
| Tencent Cloud | North China (Beijing) | ap-beijing-tencentcloud | ap-beijing-tencentcloud.api.clickzetta.com |
| Tencent Cloud | South China (Guangzhou) | ap-guangzhou-tencentcloud | ap-guangzhou-tencentcloud.api.clickzetta.com |
| AWS | Beijing | cn-north-1-aws | cn-north-1-aws.api.clickzetta.com |

JDBC URL format: `jdbc:clickzetta://<instance_name>.<region_id>.api.clickzetta.com/`
