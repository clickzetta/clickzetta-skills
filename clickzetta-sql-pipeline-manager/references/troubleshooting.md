# Troubleshooting & Verification

## Common Errors

| Error | Cause | Solution |
|---|---|---|
| `VCluster not available` | Cluster not started or name wrong | Verify VCLUSTER name, check cluster status |
| Dynamic table refresh failed | SQL error or source schema changed | `SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'xxx'` for details |
| Stream data empty | Already consumed or past retention period | Check source table `data_retention_days`, confirm consumption status |
| Pipe stopped ingesting | Kafka offset issue or connection dropped | `DESC PIPE EXTENDED` for status, check Kafka connection |
| `Cannot ALTER AS clause` | Tried to modify dynamic table SQL via ALTER | Use `CREATE OR REPLACE DYNAMIC TABLE` instead |
| `CREATE OR REPLACE PIPE` syntax error | ClickZetta does not support this syntax | Use `CREATE PIPE` or `DROP PIPE` then `CREATE` |
| `CREATE OR REPLACE MATERIALIZED VIEW` syntax error | Only supports REWRITE DISABLED + BUILD DEFER mode | Use `DROP MATERIALIZED VIEW` + `CREATE MATERIALIZED VIEW` |
| `DROP TABLE` on materialized view fails | Object type mismatch | Use `DROP MATERIALIZED VIEW` (not `DROP TABLE`) |
| Dynamic table DML error `not allowed` | Dynamic tables do not support DML | Correct data in source table, or use regular table + scheduled task |

## Delivery Checklist

After creating a pipeline, verify each item before declaring done:

```sql
-- 1. Row count comparison: each layer matches expectations
SELECT COUNT(*) FROM ods.<table>;   -- ODS ≈ source
SELECT COUNT(*) FROM dwd.<table>;   -- DWD ≤ ODS (after cleansing)
SELECT COUNT(*) FROM dws.<table>;   -- DWS matches aggregation logic

-- 2. Dynamic Table refresh status
SHOW DYNAMIC TABLE REFRESH HISTORY <schema>.<table> LIMIT 5;
-- Confirm latest status = SUCCESS

-- 3. Key field null rate
SELECT
  COUNT(*) AS total,
  COUNT(key_field) AS non_null,
  ROUND(COUNT(key_field) * 100.0 / COUNT(*), 2) AS non_null_pct
FROM <schema>.<table>;
-- Core business fields should have > 99% non-null rate

-- 4. Primary key uniqueness (DWD fact tables)
SELECT key_col, COUNT(*) AS cnt
FROM dwd.<table>
GROUP BY key_col HAVING cnt > 1 LIMIT 10;
-- Empty result = no duplicates

-- 5. Pipe ingestion status (if applicable)
SHOW PIPES;
-- status = RUNNING, last_ingested_timestamp continuously updating
```

**Acceptance criteria:**
- [ ] Row counts match expectations at each layer
- [ ] Dynamic Table latest refresh status is SUCCESS
- [ ] Key field null rate > 99%
- [ ] DWD layer primary keys have no duplicates
- [ ] Pipe status RUNNING (if applicable)
- [ ] All DDL tasks in DRAFT state (if Studio tasks involved)
- [ ] No redundant Studio scheduled tasks for DWS/ADS layer
