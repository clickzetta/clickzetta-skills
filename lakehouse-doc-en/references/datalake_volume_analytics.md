# Data Lake Management and Analytics

Singdata Lakehouse manages file storage uniformly through Volume objects, supporting both internally managed storage (User Volume, Table Volume, Named Volume) and external object storage mounts (OSS / COS / S3). It provides complete capabilities for direct querying, import/export, and permission management.

For enterprises with existing data lakes, you can mount your existing object storage directly — no data migration required. Use `SELECT FROM VOLUME` or `COPY INTO` to query and process data lake files within Lakehouse.

---

## This Section

| Page | Description |
|------|------|
| [Data Lake Overview](datalake_overview.md) | Volume architecture, positioning and selection between internal and external Volumes |
| [Storage Connection](datalake-storage-connection.md) | Create and manage object storage authentication configurations (OSS / COS / S3 / Hive / Kafka) |
| [Data Lake Volume Objects](datalake_volume_object.md) | Volume object management: creating and operating internal Volumes (User / Table / Named) and external Volumes |
| [Data Import and Export in Object Storage](data_transfer_datalake.md) | Local file upload/download (PUT / GET), import from Volume to table (COPY INTO TABLE), export from table to Volume (COPY INTO VOLUME) |
| [Data Lake Volume Query and Analysis](datalake_query_ingest.md) | Directly query CSV / JSON / Parquet files in Volumes, process unstructured data, invoke AI capabilities |
| [Data Lake Permissions](datalake_privilege.md) | Permission management for Volumes and Storage Connections |

---

## Quick Selection Guide

**I don't have cloud storage and want to temporarily store files**
→ Use [User Volume](internal_volume.md) — created automatically by the system, no configuration needed, upload files directly with PUT

**I have OSS / S3 / COS and want to query data directly**
→ Create a [Storage Connection](datalake-storage-connection.md) → Mount an [External Volume](external_volume.md) → `SELECT FROM VOLUME`

**I want to batch import object storage files into a Lakehouse table**
→ [Import Data from Volume to Table](from_volume_to_table.md) (COPY INTO TABLE)

**I want to export Lakehouse table data to object storage**
→ [Export Data to Volume](from_lakehouse_to_volume.md) (COPY INTO VOLUME)

**I want to operate Volume files with Python**
→ [Zettapark Volume and File Operations](zettapark-volume-guide.md)