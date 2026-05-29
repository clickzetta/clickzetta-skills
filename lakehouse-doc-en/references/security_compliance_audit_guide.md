# Security and Compliance Audit Guide

Singdata Lakehouse provides comprehensive security audit capabilities to help organizations meet compliance requirements such as MLPS 2.0, SOC 2, and GDPR, as well as internal audit needs.

## Audit Capability Overview

| Audit Dimension | Data Source | Query Method |
|---------|---------|---------|
| **Operation Audit** | Job history records | `sys.information_schema.job_history` |
| **Data Access Audit** | Job input/output tables | `job_history.input_tables` / `output_tables` |
| **Data Change Audit** | Table version history | `DESC HISTORY table_name` |
| **Permission Change Audit** | Account Center audit feature | Studio Web interface |
| **Login and Network Audit** | Account Center audit feature | Studio Web interface |

## Two Audit Perspectives

- **Account-level audit**: Use the "Audit" feature in the Account Center to view operation records, login records, and permission change records across the entire instance.
- **Workspace-level audit**: Query `information_schema` via SQL to analyze job execution and data access patterns within a specific workspace.

---

## Operation Audit (Who Did What and When)

### Viewing Operation Audit via Account Center

Log in to the Account Center (accounts.singdata.com) and navigate to **Audit → Operation Audit** to view:

- SQL execution records for all users
- DDL operations (CREATE / DROP / ALTER)
- Permission change operations (GRANT / REVOKE)
- Filter by time range, user, or operation type

### Querying Job History via SQL

```sql
-- Query all job execution records from the past 7 days
SELECT 
    job_id,
    workspace_name,
    job_creator AS operator,
    job_type,
    status,
    start_time,
    end_time,
    execution_time,
    LEFT(job_text, 200) AS sql_preview
FROM sys.information_schema.job_history 
WHERE start_time >= CURRENT_DATE() - INTERVAL 7 DAY
ORDER BY start_time DESC
LIMIT 100;
```

### DDL Change Audit

```sql
-- Query all DDL operations (CREATE / DROP / ALTER) from the past 30 days
SELECT 
    job_id,
    workspace_name,
    job_creator AS operator,
    job_type,
    start_time,
    LEFT(job_text, 300) AS ddl_statement
FROM sys.information_schema.job_history 
WHERE start_time >= CURRENT_DATE() - INTERVAL 30 DAY
  AND job_type IN ('CREATE', 'DROP', 'ALTER')
ORDER BY start_time DESC;
```

### Auditing Operation Records by User

```sql
-- Count the number of jobs and success rate per user
SELECT 
    job_creator AS user_name,
    COUNT(*) AS total_jobs,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) AS success_jobs,
    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) AS failed_jobs,
    ROUND(SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS success_rate
FROM sys.information_schema.job_history 
WHERE start_time >= CURRENT_DATE() - INTERVAL 30 DAY
GROUP BY job_creator
ORDER BY total_jobs DESC;
```

---

## Data Access Audit (Who Accessed What Data)

### Sensitive Table Access Records

```sql
-- Query job records that accessed a specific table
SELECT 
    job_id,
    job_creator AS operator,
    workspace_name,
    start_time,
    status,
    execution_time,
    LEFT(job_text, 200) AS sql_preview
FROM sys.information_schema.job_history 
WHERE start_time >= CURRENT_DATE() - INTERVAL 7 DAY
  AND input_tables LIKE '%sensitive_table_name%'
ORDER BY start_time DESC;
```

### Data Export Audit

```sql
-- Query COPY INTO export operations
SELECT 
    job_id,
    job_creator AS operator,
    workspace_name,
    start_time,
    execution_time,
    LEFT(job_text, 300) AS export_statement
FROM sys.information_schema.job_history 
WHERE start_time >= CURRENT_DATE() - INTERVAL 30 DAY
  AND job_text LIKE '%COPY INTO%'
  AND (job_text LIKE '%VOLUME%' OR job_text LIKE '%LOCATION%')
ORDER BY start_time DESC;
```

### Anomalous Access Pattern Detection

```sql
-- Detect large-scale data reads outside business hours (22:00–06:00)
SELECT 
    job_id,
    job_creator AS operator,
    workspace_name,
    start_time,
    HOUR(start_time) AS access_hour,
    CAST(input_bytes AS BIGINT) / 1024 / 1024 AS data_read_mb,
    LEFT(job_text, 200) AS sql_preview
FROM sys.information_schema.job_history 
WHERE start_time >= CURRENT_DATE() - INTERVAL 30 DAY
  AND HOUR(start_time) NOT BETWEEN 6 AND 22
  AND CAST(input_bytes AS BIGINT) > 1024 * 1024 * 1024  -- reads exceeding 1GB
ORDER BY start_time DESC;
```

### Cross-Workspace Data Access

```sql
-- Query jobs that accessed data across workspaces
SELECT DISTINCT
    j.workspace_name AS source_workspace,
    GET_JSON_OBJECT(j.input_tables, '$.table[0].namespace[0]') AS accessed_workspace,
    GET_JSON_OBJECT(j.input_tables, '$.table[0].tableName') AS accessed_table,
    j.job_creator AS operator,
    j.start_time
FROM sys.information_schema.job_history j
WHERE j.start_time >= CURRENT_DATE() - INTERVAL 7 DAY
  AND j.input_tables IS NOT NULL
  AND j.input_tables != '{"table":[]}'
  AND GET_JSON_OBJECT(j.input_tables, '$.table[0].namespace[0]') != j.workspace_name
ORDER BY j.start_time DESC;
```

---

## Data Change Audit (How Data Was Modified)

### Table Schema Change History

```sql
-- View the change history of a table (DDL operation records)
DESC HISTORY table_name;
```

The result includes:
- Operation type (CREATE / ALTER / DROP)
- Operation time
- Operator
- Change details

### Data Change Traceability (Time Travel)

```sql
-- View a snapshot of the table at a specific point in time
SELECT * FROM table_name TIMESTAMP AS OF '2025-06-01 10:00:00';

-- Compare data differences between two points in time (timestamps must be literals, expressions are not supported)
SELECT * FROM table_name TIMESTAMP AS OF '2025-06-01 10:00:00'
WHERE id NOT IN (
    SELECT id FROM table_name TIMESTAMP AS OF '2025-06-01 09:00:00'
);
```

> ⚠️ **Note**: `TIMESTAMP AS OF` only accepts string literals. Expressions such as `CURRENT_DATE() - INTERVAL 1 DAY` are not supported.

### Accidental Operation Recovery Audit

```sql
-- View all historical versions of a table
DESC HISTORY table_name;

-- Restore to a specific version
RESTORE TABLE table_name TO VERSION version_number;
```

---

## Permission Change Audit

### Viewing Permission Changes via Account Center

Log in to the Account Center and navigate to **Audit → Permission Audit** to view:

- GRANT / REVOKE operation records
- Role creation / deletion records
- User workspace join / removal records
- Filter by time range, operator, or target user

### Current Permission State Snapshot

```sql
-- View role assignments for all users
SELECT 
    user_name,
    role_names,
    workspace_name
FROM information_schema.users
WHERE role_names IS NOT NULL AND role_names != ''
ORDER BY user_name;

-- View the assignment status of all roles
SELECT 
    role_name,
    user_names,
    comment
FROM information_schema.roles
ORDER BY role_name;
```

### High-Privilege User Audit

```sql
-- Query users with admin privileges
SELECT 
    user_name,
    role_names,
    workspace_name
FROM information_schema.users
WHERE role_names LIKE '%admin%'
ORDER BY workspace_name, user_name;
```

---

## Login and Network Access Audit

### Viewing Login Audit via Account Center

Log in to the Account Center and navigate to **Audit → Login Audit** to view:

- User login records (time, IP, client type)
- Failed login records
- Anomalous login detection (logins from unusual locations, repeated failures)

### Network Policy Hit Records

```sql
-- View currently active network policies
SHOW NETWORK POLICY;

-- View network policy details
DESC NETWORK POLICY policy_name;
```

---

## Compliance Report Templates

### MLPS 2.0 Audit Item Mapping

| MLPS Requirement | Lakehouse Implementation | Audit Query |
|---------|-------------------|---------|
| Identity Authentication | MFA / SSO | Account Center → Login Audit |
| Access Control | RBAC / Row-level permissions / Dynamic masking | `SHOW GRANTS` + Permission Audit |
| Security Audit | Operation audit + Data access audit | `job_history` + Account Center Audit |
| Data Integrity | Time Travel + RESTORE | `DESC HISTORY` |
| Data Confidentiality | Storage encryption / BYOK / Network policies | Studio security configuration |

### Generating Periodic Audit Reports

```sql
-- Generate a monthly security audit summary (fill in time range as literals, e.g. '2025-05-01')
SELECT 
    'Audit Period' AS item, '2025-05-01 to 2025-05-31' AS value
UNION ALL
SELECT 'Total Jobs', CAST(COUNT(*) AS STRING)
FROM sys.information_schema.job_history
WHERE start_time >= '2025-05-01' AND start_time < '2025-06-01'
UNION ALL
SELECT 'Successful Jobs', CAST(SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) AS STRING)
FROM sys.information_schema.job_history
WHERE start_time >= '2025-05-01' AND start_time < '2025-06-01'
UNION ALL
SELECT 'Failed Jobs', CAST(SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) AS STRING)
FROM sys.information_schema.job_history
WHERE start_time >= '2025-05-01' AND start_time < '2025-06-01'
UNION ALL
SELECT 'Active Users', CAST(COUNT(DISTINCT job_creator) AS STRING)
FROM sys.information_schema.job_history
WHERE start_time >= '2025-05-01' AND start_time < '2025-06-01'
UNION ALL
SELECT 'DDL Operations', CAST(COUNT(*) AS STRING)
FROM sys.information_schema.job_history
WHERE start_time >= '2025-05-01' AND start_time < '2025-06-01'
  AND job_type IN ('CREATE', 'DROP', 'ALTER')
UNION ALL
SELECT 'Permission Changes', 'View via Account Center Audit feature';
```

> ⚠️ **Note**: Time conditions in `job_history` must use string literals (e.g. `'2025-05-01'`). Expressions like `CURRENT_DATE() - INTERVAL N DAY` are not supported.

### Audit Data Retention Recommendations

| Data Type | Recommended Retention Period | Notes |
|---------|------------|------|
| Job history | 90 days | Default retention for `sys.information_schema.job_history` |
| Table version history | Per `data_retention_days` setting | Default 1 day, adjustable up to 90 days |
| Account Center audit records | Per Account Center configuration | Recommended minimum of 180 days |

---

## Automated Audit Practices

### Creating Audit Monitoring Views

```sql
-- Create a daily audit summary view
CREATE VIEW daily_audit_summary AS
SELECT 
    DATE(start_time) AS audit_date,
    workspace_name,
    COUNT(*) AS total_jobs,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) AS success_jobs,
    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) AS failed_jobs,
    COUNT(DISTINCT job_creator) AS active_users,
    SUM(CASE WHEN job_type IN ('CREATE', 'DROP', 'ALTER') THEN 1 ELSE 0 END) AS ddl_operations,
    SUM(CAST(input_bytes AS BIGINT)) / 1024 / 1024 / 1024 AS total_data_read_gb
FROM sys.information_schema.job_history 
GROUP BY DATE(start_time), workspace_name;
```

### Scheduling Periodic Audit Tasks

Create a recurring SQL task in Studio to run audit queries daily and export results:

```sql
-- Daily security audit task
INSERT INTO audit_log 
SELECT 
    CURRENT_TIMESTAMP() AS audit_time,
    'daily_security_check' AS check_type,
    COUNT(*) AS anomaly_count,
    'Large-scale data reads outside business hours' AS description
FROM sys.information_schema.job_history 
WHERE DATE(start_time) = CURRENT_DATE() - INTERVAL 1 DAY
  AND HOUR(start_time) NOT BETWEEN 6 AND 22
  AND CAST(input_bytes AS BIGINT) > 1024 * 1024 * 1024;
```

### Alert Rule Configuration

| Alert Scenario | Detection Condition | Recommended Action |
|---------|---------|---------|
| Abnormal data export | More than 5 COPY INTO operations in a single day | Notify security administrator |
| High-privilege user anomaly | Admin user executes DDL outside business hours | Immediate review |
| High job failure rate | Single user failure rate > 50% | Check SQL or permission configuration |
| Sensitive table access | Unauthorized user accesses a sensitive table | Trigger permission audit |

---

## Audit Best Practices

1. **Run audits regularly**: Recommended weekly operation audits and monthly full compliance audits.
2. **Retain audit records**: Ensure audit data retention periods meet compliance requirements (typically ≥ 180 days).
3. **Separate audit permissions**: Auditors should have read-only access and must not have data modification permissions.
4. **Automate monitoring**: Configure common audit queries as recurring tasks with automatic alerts on anomalies.
5. **Combine with Account Center**: Use SQL queries together with the Account Center audit feature to cover all audit scenarios.

## Related Documentation

- [Security Feature Overview](security_overview.md)
- [Permission System Inventory Best Practices](security-system-inventory-based-information-schema.md)
- [Job History Analysis](job_history_analysis_with_information_schema.md)
- [Time Travel Concepts](time-travel-concept.md)
