# Information Schema (Instance Level)

The instance-level Information Schema stores metadata for the entire instance, including object information across all workspaces, user permissions, and billing usage. Access it via `sys.information_schema.<view_name>`.

```sql
-- Example: list all workspaces in the instance
SELECT workspace_name, create_time FROM sys.information_schema.workspaces;

-- Example: list all schemas across workspaces
SELECT catalog_name, schema_name, type FROM sys.information_schema.schemas;
```

## WORKSPACES

Records information about all workspaces in the instance.

| Column | Type | Description |
|--------|------|-------------|
| `workspace_id` | BIGINT | Workspace ID |
| `workspace_name` | STRING | Workspace name |
| `workspace_creator` | STRING | Creator account name |
| `workspace_creator_id` | BIGINT | Creator account ID |
| `create_time` | TIMESTAMP_LTZ | Creation time |
| `last_modify_time` | TIMESTAMP_LTZ | Last modification time |
| `delete_time` | TIMESTAMP_LTZ | Deletion time (NULL if not deleted) |
| `comment` | STRING | Comment |
| `properties` | MAP\<STRING,STRING\> | Properties set at creation |

## SCHEMAS

Records schema information across all workspaces in the instance.

| Column | Type | Description |
|--------|------|-------------|
| `catalog_name` | STRING | Name of the workspace the schema belongs to |
| `schema_id` | BIGINT | Schema ID |
| `schema_name` | STRING | Schema name |
| `type` | STRING | Schema type, e.g. `MANAGED`, `SHARED`, `EXTERNAL` |
| `schema_creator` | STRING | Creator account name |
| `schema_creator_id` | BIGINT | Creator account ID |
| `create_time` | TIMESTAMP_LTZ | Creation time |
| `last_modify_time` | TIMESTAMP_LTZ | Last modification time |
| `delete_time` | TIMESTAMP_LTZ | Deletion time (NULL if not deleted) |
| `comment` | STRING | Comment |
| `properties` | MAP\<STRING,STRING\> | Properties set at creation |

## TABLES

Records table information across all workspaces in the instance.

| Column | Type | Description |
|--------|------|-------------|
| `table_catalog` | STRING | Name of the workspace the table belongs to |
| `table_catalog_id` | BIGINT | Workspace ID |
| `table_schema` | STRING | Schema name |
| `table_schema_id` | BIGINT | Schema ID |
| `table_name` | STRING | Table name |
| `table_id` | BIGINT | Table ID |
| `table_creator` | STRING | Creator account name |
| `table_creator_id` | BIGINT | Creator account ID |
| `table_type` | STRING | Table type, e.g. `MANAGED_TABLE`, `DYNAMIC_TABLE`, `MATERIALIZED_VIEW`, `VIRTUAL_VIEW`, `SEMANTIC_VIEW`, `EXTERNAL_TABLE` |
| `row_count` | BIGINT | Row count (NULL for views) |
| `bytes` | BIGINT | Data size in bytes (NULL for views) |
| `create_time` | TIMESTAMP_LTZ | Creation time |
| `last_modify_time` | TIMESTAMP_LTZ | Last modification time |
| `delete_time` | TIMESTAMP_LTZ | Deletion time (NULL if not deleted) |
| `is_partitioned` | BOOLEAN | Whether the table is partitioned |
| `is_clustered` | BOOLEAN | Whether the table is clustered |
| `comment` | STRING | Comment |
| `properties` | MAP\<STRING,STRING\> | Properties set at creation |
| `data_lifecycle` | INT | Data lifecycle in days; NULL means not set |

## COLUMNS

Records column information for all tables in the instance.

| Column | Type | Description |
|--------|------|-------------|
| `table_catalog` | STRING | Name of the workspace the table belongs to |
| `table_catalog_id` | BIGINT | Workspace ID |
| `table_schema` | STRING | Schema name |
| `table_schema_id` | BIGINT | Schema ID |
| `table_name` | STRING | Table name |
| `table_id` | BIGINT | Table ID |
| `column_name` | STRING | Column name |
| `column_id` | INT | Column ID |
| `column_default` | BOOLEAN | Default value |
| `is_nullable` | BOOLEAN NOT NULL | Whether NULL is allowed |
| `data_type` | STRING | Column data type |
| `comment` | STRING | Column comment |
| `is_primary_key` | BOOLEAN NOT NULL | Whether the column is a primary key |
| `is_clustering_column` | BOOLEAN NOT NULL | Whether the column is a clustering column |
| `create_time` | TIMESTAMP_LTZ | Creation time |
| `delete_time` | TIMESTAMP_LTZ | Deletion time (NULL if not deleted) |

## VIEWS

Records information about all views (regular views) in the instance.

| Column | Type | Description |
|--------|------|-------------|
| `table_catalog` | STRING | Name of the workspace the view belongs to |
| `table_catalog_id` | BIGINT | Workspace ID |
| `table_schema` | STRING | Schema name |
| `table_schema_id` | BIGINT | Schema ID |
| `table_name` | STRING | View name |
| `table_id` | BIGINT | View ID |
| `table_creator` | STRING | Creator account name |
| `table_creator_id` | BIGINT | Creator account ID |
| `view_definition` | STRING | SQL definition used to create the view |
| `create_time` | TIMESTAMP_LTZ | Creation time |
| `last_modify_time` | TIMESTAMP_LTZ | Last modification time |
| `delete_time` | TIMESTAMP_LTZ | Deletion time (NULL if not deleted) |
| `comment` | STRING | Comment |

## USERS

Records user information across all workspaces in the instance.

| Column | Type | Description |
|--------|------|-------------|
| `workspace_id` | BIGINT | Workspace ID |
| `workspace_name` | STRING | Workspace name |
| `user_id` | BIGINT | User ID |
| `user_name` | STRING | User account name |
| `role_names` | STRING | Roles assigned to the user, multiple roles separated by commas |
| `create_time` | TIMESTAMP_LTZ | Time the user joined the workspace |
| `email` | STRING | User email |
| `telphone` | STRING | User phone number |
| `comment` | STRING | Comment |
| `properties` | MAP\<STRING,STRING\> | Properties set at creation |
| `delete_time` | TIMESTAMP_LTZ | Removal time (NULL if not removed) |

## ROLES

Records role information across all workspaces in the instance.

| Column | Type | Description |
|--------|------|-------------|
| `workspace_id` | BIGINT | Workspace ID |
| `workspace_name` | STRING | Workspace name |
| `role_name` | STRING | Role name |
| `role_id` | BIGINT | Role ID |
| `user_names` | STRING | Names of users granted this role, multiple users separated by commas |
| `user_ids` | STRING | IDs of users granted this role, multiple IDs separated by commas |
| `comment` | STRING | Comment |
| `properties` | MAP\<STRING,STRING\> | Properties set at creation |
| `delete_time` | TIMESTAMP_LTZ | Deletion time (NULL if not deleted) |

## CONNECTIONS

Records connection object information across all workspaces in the instance.

| Column | Type | Description |
|--------|------|-------------|
| `workspace_name` | STRING | Workspace name |
| `workspace_id` | BIGINT | Workspace ID |
| `connection_name` | STRING | Connection name |
| `connection_id` | BIGINT | Connection ID |
| `connection_kind` | STRING | Connection kind, e.g. `STORAGE_CONNECTION`, `STORAGE`, `CATALOG`, `API` |
| `type` | STRING | Data source type, e.g. `FILE_SYSTEM`, `CLOUD_FUNCTION`, `OSS`, `KAFKA`, `MESSAGE_QUEUE`, `DATABRICKS_UNITY_CATALOG` |
| `provider` | STRING | Cloud provider, e.g. `OSS`, `COS`, `S3`, `aliyun`, `tencent` |
| `region` | STRING | Connection region, e.g. `cn-shanghai`, `ap-beijing` |
| `source_creator` | STRING | Creator account name |
| `create_time` | TIMESTAMP_LTZ | Creation time |
| `last_modify_time` | TIMESTAMP_LTZ | Last modification time |
| `delete_time` | TIMESTAMP_LTZ | Deletion time (NULL if not deleted) |
| `comment` | STRING | Comment |
| `properties` | MAP\<STRING,STRING\> | Properties set at creation |

## VOLUMES

Records Volume information across all workspaces in the instance.

| Column | Type | Description |
|--------|------|-------------|
| `volume_catalog` | STRING | Name of the workspace the volume belongs to |
| `volume_catalog_id` | BIGINT | Workspace ID |
| `volume_schema` | STRING | Schema name |
| `volume_schema_id` | BIGINT | Schema ID |
| `volume_name` | STRING | Volume name |
| `volume_id` | BIGINT | Volume ID |
| `volume_url` | STRING | Mount path (empty for internal volumes) |
| `volume_region` | STRING | Region where the volume resides |
| `volume_type` | STRING | Volume type: `MANAGED` (internal) or `EXTERNAL` |
| `volume_creator` | STRING | Creator account name |
| `connection_name` | STRING | Referenced connection name (empty for internal volumes) |
| `connection_id` | BIGINT | Referenced connection ID |
| `comment` | STRING | Comment |
| `properties` | MAP\<STRING,STRING\> | Properties set at creation |
| `create_time` | TIMESTAMP_LTZ | Creation time |
| `last_modify_time` | TIMESTAMP_LTZ | Last modification time |
| `delete_time` | TIMESTAMP_LTZ | Deletion time (NULL if not deleted) |

## JOB_HISTORY

Records the execution history of all jobs in the instance.

| Column | Type | Description |
|--------|------|-------------|
| `workspace_name` | STRING | Workspace where the job ran |
| `workspace_id` | BIGINT | Workspace ID |
| `job_id` | STRING | Job ID |
| `job_name` | STRING | Job name |
| `job_creator` | STRING | Account name of the user who submitted the job |
| `job_creator_id` | BIGINT | User ID of the submitter |
| `status` | STRING | Job status, e.g. `SUCCEED`, `FAILED`, `CANCELLED` |
| `cru` | DOUBLE | Compute resources consumed (CRU·hours) |
| `error_message` | STRING | Error message if the job failed |
| `job_type` | STRING | Job type, e.g. `SQL_JOB`, `COMPACTION_JOB` |
| `job_sub_type` | STRING | Job sub-type |
| `job_text` | STRING | SQL text that was executed |
| `start_time` | TIMESTAMP_LTZ | Start time |
| `end_time` | TIMESTAMP_LTZ | End time |
| `execution_time` | DOUBLE | Execution duration in seconds (millisecond precision) |
| `input_bytes` | BIGINT | Actual scanned data volume in bytes |
| `output_bytes` | BIGINT | Output data volume in bytes |
| `input_objects` | STRING | Input object names |
| `output_objects` | STRING | Output object names |
| `input_tables` | STRING | Input table names |
| `output_tables` | STRING | Output table names |
| `cache_hit` | BIGINT | Data read from cache in bytes |
| `rows_produced` | BIGINT | Total rows processed |
| `rows_inserted` | BIGINT | Rows inserted |
| `rows_updated` | BIGINT | Rows updated |
| `rows_deleted` | BIGINT | Rows deleted |
| `virtual_cluster` | STRING | Name of the virtual cluster used |
| `virtual_cluster_id` | BIGINT | ID of the virtual cluster used |
| `job_config` | STRING | Parameters set when the job was submitted |
| `job_priority` | STRING NOT NULL | Job priority |
| `query_tag` | STRING | Query tag set by the user |
| `client_info` | STRING | Client information (from JDBC, CLI, web, etc.) |
| `pt_date` | STRING | Partition date for filtering by day |

## MATERIALIZED_VIEW_REFRESH_HISTORY

Records the refresh history of materialized views.

| Column | Type | Description |
|--------|------|-------------|
| `workspace_id` | BIGINT | Workspace ID |
| `workspace_name` | STRING | Workspace name |
| `schema_id` | BIGINT | Schema ID |
| `schema_name` | STRING | Schema name |
| `materialized_view_id` | BIGINT | Materialized view ID |
| `materialized_view_name` | STRING | Materialized view name |
| `cru` | DOUBLE | Compute resources consumed by the refresh (CRU·hours) |
| `virtual_cluster_id` | BIGINT | Virtual cluster ID used |
| `virtual_cluster_name` | STRING | Virtual cluster name used |
| `status` | STRING | Refresh status, e.g. `SUCCEED`, `FAILED` |
| `scheduled_start_time` | TIMESTAMP_LTZ | Scheduled refresh time |
| `start_time` | TIMESTAMP_LTZ | Actual start time |
| `end_time` | TIMESTAMP_LTZ | End time |
| `error_code` | STRING | Error code |
| `error_message` | STRING | Error message if the refresh failed |
| `pt_date` | DATE | Partition date for filtering by day |

## AUTOMV_REFRESH_HISTORY

Records the refresh history of Auto Materialized Views.

| Column | Type | Description |
|--------|------|-------------|
| `workspace_name` | STRING | Workspace name |
| `schema_name` | STRING | Schema name |
| `materialized_view_name` | STRING | Materialized view name |
| `cru` | DOUBLE | Compute resources consumed by the refresh (CRU·hours) |
| `status` | STRING | `PROCESSING`, `SUCCEEDED`, `FAILED`, `CANCELLED` |
| `mv_process_type` | STRING NOT NULL | `BUILD` (initial build) or `REFRESH` (incremental refresh) |
| `start_time` | TIMESTAMP_LTZ | Start time |
| `end_time` | TIMESTAMP_LTZ | End time |
| `build_from_workspace` | STRING | Workspace name of the source tables |
| `build_from_workspace_id` | BIGINT | Workspace ID of the source tables |
| `job_id` | STRING | Corresponding job ID |
| `error_message` | STRING | Error message if the refresh failed |
| `pt_date` | STRING | Partition date for filtering by day |

## OBJECT_PRIVILEGES

Records privilege grant information for all objects in the instance.

| Column | Type | Description |
|--------|------|-------------|
| `grantee` | STRING | Name of the grantee (user name or role name) |
| `grantor` | STRING | Name of the grantor |
| `granted_to` | STRING NOT NULL | Grantee type, e.g. `user`, `role` |
| `object_catalog` | STRING | Workspace name where the object resides |
| `object_schema` | STRING | Schema name where the object resides |
| `object_name` | STRING | Object name |
| `object_type` | STRING | Object type, e.g. `TABLE`, `SCHEMA`, `VIRTUAL_CLUSTER`, `FUNCTION`, `INDEX` |
| `sub_object_type` | STRING | Sub-object type |
| `privilege_type` | STRING | Privilege type, e.g. `["AT_ALL"]`, `["SELECT"]` (JSON array format) |
| `is_grantable` | BOOLEAN | Whether the privilege can be re-granted |
| `authorization_time` | TIMESTAMP_LTZ | Time the privilege was granted |

## INSTANCE_USAGE

Records compute resource usage and billing details for the instance, aggregated by day.

| Column | Type | Description |
|--------|------|-------------|
| `account_id` | BIGINT | Account ID |
| `account_name` | STRING | Account name |
| `instance_id` | BIGINT | Instance ID |
| `region_name` | STRING NOT NULL | Region where the instance resides |
| `sku_category` | STRING | Billing category, e.g. `compute`, `storage`, `network` |
| `sku_name` | VARCHAR(255) | Billing item name |
| `workspace_id` | BIGINT | Workspace ID |
| `workspace_name` | STRING | Workspace name |
| `measurement_start` | STRING | Measurement period start time |
| `measurement_end` | STRING | Measurement period end time |
| `measurements_unit` | VARCHAR(50) | Measurement unit, e.g. `yuan/GiB/day`, `yuan/CRU/hour` |
| `measurements_consumption` | DOUBLE | Actual usage |
| `price_rate` | DECIMAL(13,7) | Unit price |
| `amount` | DOUBLE | Billing amount |
| `discount_rate` | DOUBLE NOT NULL | Discount rate |
| `total_after_discount` | DOUBLE | Amount after discount |

Common `sku_name` values include `AP-type compute cluster`, `GP-type compute cluster`, `Task Scheduling`, `Data Integration`, and `Streaming Integration`. `measurements_consumption` represents the CRU consumed in the corresponding period; `amount` is the original billing amount; `total_after_discount` is the discounted amount.

## STORAGE_METERING

Records storage usage and billing details for the instance. The column structure is the same as `INSTANCE_USAGE` and is dedicated to querying storage billing items.

| Column | Type | Description |
|--------|------|-------------|
| `account_id` | BIGINT | Account ID |
| `account_name` | STRING | Account name |
| `instance_id` | BIGINT | Instance ID |
| `region_name` | STRING NOT NULL | Region where the instance resides |
| `sku_category` | STRING | Billing category |
| `sku_name` | VARCHAR(255) | Billing item name |
| `workspace_id` | BIGINT | Workspace ID |
| `workspace_name` | STRING | Workspace name |
| `measurement_start` | STRING | Measurement period start time |
| `measurement_end` | STRING | Measurement period end time |
| `measurements_unit` | VARCHAR(50) | Measurement unit |
| `measurements_consumption` | DOUBLE | Actual usage |
| `price_rate` | DECIMAL(13,7) | Unit price |
| `amount` | DOUBLE | Billing amount |
| `discount_rate` | DOUBLE NOT NULL | Discount rate |
| `total_after_discount` | DOUBLE | Amount after discount |

Common `sku_category` values include `storage` and `network`. Common `sku_name` values include `Managed Storage Capacity`, `Multi-version Undeleted Storage`, and `Data Query Internet Data Transfer`.