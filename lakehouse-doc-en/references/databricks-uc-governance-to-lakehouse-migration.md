# Databricks Unity Catalog → Lakehouse Migration Guide: Permissions and Governance

If your data platform uses Databricks Unity Catalog to manage permissions — RBAC roles, column-level masking, row-level access control, data auditing — the migration effort to Singdata Lakehouse is lower than you might expect. GRANT/REVOKE syntax is fully consistent, role management requires no changes, and the `SET MASK` keyword is identical. Changes are concentrated in 3 areas: removing the catalog prefix (three-level → two-level naming), swapping one API in masking functions (`is_account_group_member` → `array_contains(current_roles(),...)`), and replacing declarative ROW FILTER with explicit security views for row-level security.

This article validates this with a financial payment scenario: a user table with PII fields (email/phone/card), an orders table with region-based isolation, and a balance/accounts table — complete migration of RBAC, column masking, row-level security, and audit logs, passing all 16 automated validations.

Full code on GitHub: [databricks2lakehouse-governance](https://github.com/clickzetta/databricks2lakehouse-governance)

---

## Source Project

Demo data is a financial payment scenario with 3 tables:

| Table | Rows | Sensitive Fields | Access Control Requirements |
|----|------|---------|------------|
| `users` | 100 | `email`, `phone`, `ssn_last4` | Masking: non-admin sees masked values |
| `orders` | 300 | `amount`, `region` | Row-level: analyst only sees North America |
| `accounts` | 50 | `balance`, `card_number` | Masking: last 4 digits of card visible |

Migrated code is in the `03_lakehouse/sql/` directory (6 SQL files), comparable file-by-file with `01_source/sql/` (original UC SQL).

## Conclusion First

Most permission SQL can be reused directly with **very few or zero changes**.

| Change | Effort | Notes |
|--------|--------|------|
| Masking function judgment API | Very low | `is_account_group_member('g')` → `array_contains(current_roles(), 'ws.g')` |
| Audit table and column names | Low | `system.access.audit` → `sys.information_schema.job_history`, different column names |

**No changes needed**: `CREATE ROLE`, `GRANT SELECT`, `GRANT ALL PRIVILEGES`, `WITH GRANT OPTION`, `SHOW GRANTS`, `SET MASK`, `SET ROW FILTER`, **three-level naming (workspace.schema.table)** — syntax fully consistent. Row-level security migrates with zero changes!

> 💡 Namespacing: UC uses `catalog.schema.table`; Lakehouse uses `workspace.schema.table` — the structure is identical, just replacing the catalog name with the workspace name (a connection parameter change, no SQL code changes needed).

Lakehouse also has additional capabilities that UC lacks: `mask_inner`/`mask_outer` (built-in string masking functions), `AI_MASK` (AI model semantic masking), `CREATE SHARE` (data sharing, SQL DDL simpler than Delta Sharing).

---

## Tech Stack Comparison

| | Databricks Unity Catalog | Singdata Lakehouse |
|---|---|---|
| Namespace levels | Three-level: `catalog.schema.table` | Three-level: `workspace.schema.table` (same structure) |
| Role management | `CREATE ROLE` (metastore-level) | `CREATE ROLE` (workspace-level) |
| GRANT syntax | `GRANT ... ON TABLE cat.s.t TO ROLE r` | `GRANT ... ON TABLE s.t TO ROLE r` |
| Column masking judgment | `is_account_group_member('group')` | `array_contains(current_roles(), 'ws.role')` |
| Column masking application | `ALTER TABLE ... ALTER COLUMN c SET MASK f` | `ALTER TABLE ... ALTER COLUMN c SET MASK f` |
| Row-level security | `ALTER TABLE ... SET ROW FILTER f ON (col)` | `ALTER TABLE ... SET ROW FILTER f ON (col)` |
| Data sharing | Delta Sharing (UC + REST API) | `CREATE SHARE` / `GRANT select, read metadata ... TO SHARE` |
| String masking | Hand-written REGEXP_REPLACE | `mask_inner()` / `mask_outer()` (built-in functions) |
| AI intelligent masking | — | `AI_MASK()` (Lakehouse exclusive) |
| Tag / ABAC | UC Tag policies (cross-table tagging) | Not yet supported → use role naming + Schema isolation as substitute |
| Audit source | `system.access.audit` (account-level) | `sys.information_schema.job_history` (workspace-level) |

---

![](.topwrite/assets/anim-31-databricks-uc-governance-migration.svg)

---

## Project Background

Three tables covering typical financial scenarios:

- `users`: User registration info with PII fields like email/phone/ssn_last4, requiring column-level masking
- `orders`: Sales orders partitioned by region (North America/Europe/Asia Pacific), requiring row-level isolation
- `accounts`: Account balances and bank card info; balance and card_number are highly sensitive

The original UC design defines 3 roles:
- `payments_admin`: Full access to real data
- `payments_analyst`: Masked data + only North America orders
- `payments_viewer`: Masked data + only Asia orders

---

## Migration Steps

### Step 1: Remove Catalog Prefix

UC uses three-level naming; the Lakehouse workspace itself is the catalog boundary, requiring only two levels:

```sql
-- UC (three-level)
GRANT SELECT ON TABLE payments_catalog.raw.orders TO ROLE payments_analyst;

-- Lakehouse (two-level) — remove catalog prefix
GRANT SELECT ON TABLE gov_raw.orders TO ROLE payments_analyst;
```

### Step 2: RBAC — Syntax Fully Consistent

GRANT/REVOKE/SHOW GRANTS syntax requires zero changes:

```sql
-- Identical on both sides
CREATE ROLE IF NOT EXISTS payments_analyst;
CREATE ROLE IF NOT EXISTS payments_admin;

GRANT SELECT ON TABLE gov_raw.orders TO ROLE payments_analyst;
GRANT ALL PRIVILEGES ON SCHEMA gov_raw TO ROLE payments_admin;
GRANT SELECT ON ALL TABLES IN SCHEMA gov_raw TO ROLE payments_viewer;
GRANT SELECT ON TABLE gov_raw.users TO ROLE payments_admin WITH GRANT OPTION;

SHOW GRANTS TO ROLE payments_analyst;
```

### Step 3: Column Masking — `SET MASK` Identical, One Function API Change

UC uses `is_account_group_member()`; Lakehouse uses `array_contains(current_roles(), 'workspace.role')`:

```python
# UC masking function
CREATE FUNCTION payments_catalog.raw.mask_email(email STRING)
    RETURN CASE
        WHEN is_account_group_member('payments_admin') THEN email
        ELSE CONCAT(LEFT(email, 2), '***@***.***')
    END;
```

```sql
-- Lakehouse masking function (only the judgment API changes, logic identical)
CREATE OR REPLACE FUNCTION gov_raw.mask_email(email STRING)
    RETURNS STRING
    RETURN CASE
        WHEN array_contains(current_roles(), 'quick_start.payments_admin')  -- ← current_roles()
          OR array_contains(current_roles(), 'workspace_admin')
        THEN email
        ELSE CONCAT(LEFT(email, 2), '***@***.***')
    END;

-- SET MASK application syntax is identical
ALTER TABLE gov_raw.users ALTER COLUMN email SET MASK gov_raw.mask_email;
ALTER TABLE gov_raw.users ALTER COLUMN phone SET MASK gov_raw.mask_phone;
ALTER TABLE gov_raw.accounts ALTER COLUMN card_number SET MASK gov_raw.mask_card;
```

Tested masking results (seen by non-admin users):

| Field | Original Value | After Masking |
|------|--------|--------|
| email | `user001@example.com` | `u***@***.***` |
| phone | `+12345678901` | `****8901` |
| card_number | `4866524041574` | `****-****-****-1574` |

### Step 4: Row-Level Security — `SET ROW FILTER` Syntax Fully Consistent

Lakehouse natively supports `SET ROW FILTER`, with syntax **fully consistent with UC, zero changes**:

```sql
-- UC (Databricks)
CREATE FUNCTION payments_catalog.raw.filter_orders_by_region(region STRING)
    RETURN CASE
        WHEN is_account_group_member('payments_admin') THEN TRUE
        WHEN is_account_group_member('payments_analyst')
             AND region = 'North America' THEN TRUE
        ELSE FALSE
    END;

ALTER TABLE payments_catalog.raw.orders
    SET ROW FILTER payments_catalog.raw.filter_orders_by_region ON (region);
```

```sql
-- Lakehouse — syntax fully consistent, only change is is_account_group_member in function body
CREATE OR REPLACE FUNCTION gov_raw.filter_orders_by_role(region STRING)
RETURNS BOOLEAN
AS
    array_contains(current_roles(), 'quick_start.payments_admin')
    OR array_contains(current_roles(), 'workspace_admin')
    OR (array_contains(current_roles(), 'quick_start.payments_analyst')
        AND region = 'North America')
    OR (array_contains(current_roles(), 'quick_start.payments_viewer')
        AND region = 'Asia');

-- SET ROW FILTER syntax is identical
ALTER TABLE gov_raw.orders SET ROW FILTER gov_raw.filter_orders_by_role ON (region);

-- Verify binding
DESC EXTENDED gov_raw.orders;
-- Output includes # Row Filter section at the end

-- Remove
ALTER TABLE gov_raw.orders DROP ROW FILTER;
```

ROW FILTER takes full effect for SELECT, COUNT, UPDATE, DELETE — the current user (workspace_admin) queries 300 rows; a `payments_analyst` role user only sees the 52 North America rows.

### Step 5: Auditing — Table and Column Name Adaptation

UC uses `system.access.audit` (account-level); Lakehouse uses `sys.information_schema.job_history` (workspace-level):

```sql
-- UC auditing
SELECT event_time, user_name, action_name, request_params
FROM system.access.audit
WHERE event_time >= current_timestamp() - INTERVAL 7 DAYS
  AND action_name IN ('createTable','grantPermission','revokePermission');
```

```sql
-- Lakehouse auditing (different column names, date uses literal string)
SELECT
    job_type,
    job_creator,           -- UC: user_name
    LEFT(job_text, 100) AS sql_preview,  -- UC: request_params
    status,
    LEFT(start_time, 19) AS time
FROM sys.information_schema.job_history
WHERE start_time >= '2026-06-07'   -- must be literal, cannot use NOW() - INTERVAL
  AND (UPPER(job_text) LIKE 'GRANT%'
    OR UPPER(job_text) LIKE 'REVOKE%'
    OR UPPER(job_text) LIKE 'CREATE TABLE%')
ORDER BY start_time DESC;
```

---

## Data Sharing

Lakehouse's **Share** is the equivalent of Databricks Delta Sharing — share tables or views with other workspaces or external consumers, with syntax highly similar to UC:

```sql
-- Step 1: Create Share object
CREATE SHARE IF NOT EXISTS analytics_share
    COMMENT 'Analytics data share for partners';

-- Step 2: Add tables/views to Share (dual permissions: select + read metadata)
GRANT select, read metadata ON VIEW gov_marts.orders_by_region TO SHARE analytics_share;
GRANT select, read metadata ON TABLE gov_raw.orders TO SHARE analytics_share;

-- Bulk add all tables in a schema
GRANT SELECT, READ METADATA ON ALL TABLES IN SCHEMA gov_raw TO SHARE analytics_share;

-- Step 3: View Share contents
DESC SHARE analytics_share;

-- Step 4: Consumer access
CREATE SCHEMA partner_schema FROM SHARE analytics_share;
```

`SELECT, READ METADATA` dual permission combination: `select` allows querying data; `read metadata` allows consumers to discover the existence of tables/views. Both are typically granted together. UC Delta Sharing configuration is done via the Databricks UI/REST API; Lakehouse Share uses SQL DDL directly, which is more concise.

---

## Lakehouse-Exclusive Capabilities

**`mask_inner` / `mask_outer`**: Built-in string masking functions not available in UC, usable directly in masking functions without AI connection:

```sql
-- mask_inner: mask middle characters (preserve first n and last m characters)
SELECT mask_inner('user001@example.com', 2, 7);
-- → usXXXXXXXXXXXXX.com (preserve first 2, last 7, mask middle)

-- mask_outer: mask outer characters
SELECT mask_outer('+12345678901', 1, 4);
-- → X1234567XXXX

-- More concise in masking functions than hand-written CONCAT+REGEXP_REPLACE
CREATE OR REPLACE FUNCTION gov_raw.mask_email_v2(email STRING)
    RETURNS STRING
    RETURN CASE
        WHEN array_contains(current_roles(), 'quick_start.payments_admin') THEN email
        ELSE mask_inner(email, 2, 7)
    END;
```

**`AI_MASK`**: AI model-based semantic masking, automatically identifies PII types (names, phones, ID numbers, etc.). UC has no equivalent:

```sql
-- Requires AI connection configuration (Bailian/Tongyi models etc.)
SELECT AI_MASK('conn_bailian:qwen3.5-plus',
               'User Wang Xiaoming, phone: 13800138000',
               ARRAY('Name', 'Phone'));
-- → 'User ***, phone: 138****8000'
```

---

## Validation Results

Tested on AWS Singapore instance (`aws_singapore_prod`), 16/16 all passed:

| Check | Expected | Result |
|--------|--------|------|
| gov_raw.users | 100 | ✅ |
| gov_raw.orders | 300 | ✅ |
| gov_raw.accounts | 50 | ✅ |
| analyst has GRANT records | ≥2 | ✅ |
| admin has GRANT records | ≥1 | ✅ |
| viewer has GRANT records | ≥1 | ✅ |
| email is masked | True | ✅ |
| phone is masked | True | ✅ |
| card_number is masked | True | ✅ |
| mask_email function exists | True | ✅ |
| mask_phone function exists | True | ✅ |
| mask_card function exists | True | ✅ |
| orders_by_region admin sees 300 rows | 300 | ✅ |
| orders_analyst_view only sees North America | 52 | ✅ |
| analyst_view has only 1 region | 1 | ✅ |
| job_history has records | ≥1 | ✅ |

---

## Notes

- **`current_roles()` includes workspace prefix**: Lakehouse's `current_roles()` returns role names with workspace prefix (e.g., `quick_start.payments_admin`). When matching, the full prefix is required — `payments_admin` alone will not work.
- **`SET MASK` becomes invalid after table recreation**: After DROP TABLE + CREATE, column masks are not inherited automatically. `ALTER TABLE ... ALTER COLUMN c SET MASK` must be re-applied.
- **COPY INTO type inference**: External Volume COPY INTO does not support `inferSchema`. Column types must be explicitly declared when creating tables (especially phone/card should use STRING; otherwise inferred as BIGINT causing data loss).
- **job_history date condition**: `WHERE start_time >= '2026-06-07'` must be a literal string. `CURRENT_DATE()` or `INTERVAL` expressions are not supported.
- **Row-level security function judgment API**: The ROW FILTER function body also requires replacing `is_account_group_member('g')` with `array_contains(current_roles(), 'ws.g')`. This is the only change point. `ALTER TABLE ... SET ROW FILTER` / `DROP ROW FILTER` syntax is identical.
- **Tag / ABAC (honest limitation)**: UC supports fine-grained attribute-based access control (ABAC) via Tags — tagging tables/columns and then writing policies. Lakehouse does not currently support Tag-driven ABAC. The recommended approach is to use role naming conventions (e.g., `dept_finance_analyst`) + Schema isolation to simulate ABAC, or keep tag-based permissions managed on the Databricks side.

## Related Documentation

### Permissions and Security

- [GRANT](GRANT.md): Full GRANT syntax reference
- [CREATE ROLE](create-role.md): Role creation and management
- [SET MASK](set-mask.md): Column masking syntax
- [SHOW GRANTS](show-grants.md): View authorization relationships

### Other Migration Guides

- [Databricks Notebook → Lakehouse Migration Guide](databricks-notebook-to-studio-migration.md)
- [Databricks DLT → Lakehouse Migration Guide](databricks-dlt-to-lakehouse-migration.md)
- [dbt-databricks → dbt-clickzetta Migration Guide](dbt-databricks-to-clickzetta-migration.md)
