# CDC Sync Troubleshooting & Operations

## Troubleshooting Quick Reference

| Issue | Investigation |
|---|---|
| `CREATE STORAGE CONNECTION TYPE MYSQL` error | ❌ ClickZetta does not support MySQL/PostgreSQL Storage Connections. CDC data sources are configured via **Studio UI Data Source Management**, not SQL commands |
| Task creation failed | Check if a Sync VCluster is available |
| Source connection failed | Check Studio data source configuration, network reachability, account permissions |
| Binlog read failed | Confirm MySQL `log_bin=ON`, `binlog_format=ROW`, `binlog_row_image=FULL` |
| WAL read failed | Confirm PostgreSQL `wal_level=logical`, slot not occupied by another task |
| Slot startup conflict | Different tasks must not reuse the same slot — check if another running task is occupying it |
| Slow full load | Adjust maximum concurrency, check source database load, increase memory parameters |
| Increasing incremental latency | Check Sync VCluster resources, whether source data volume has spiked |
| Schema Evolution exception | Use "View exceptions" to see details — column type changes are not supported |
| Sharded table primary key conflict | Enable extended fields and set as composite primary key |

## Incremental Sync Failures

### Binlog Position Expired

- **Symptom**: `The connector is trying to read binlog starting at ... but this is no longer available on the server`
- **Cause**: binlog file purged by MySQL periodic cleanup, or task stopped too long causing position expiration
- **Resolution**:
  1. Run `SHOW MASTER STATUS` on source to get current latest binlog file and position
  2. Restart sync task with the latest file and position (select "Custom start position")
  3. If lost data needs recovery, run "Re-sync" for affected tables

### Server-id Conflict

- **Symptom**: `A slave with the same server_uuid/server_id as this slave has connected to the master`
- **Cause**: task's assigned server-id (range 5400–6400) conflicts with another sync tool/task on the same database
- **Resolution**: check if other sync tasks or tools are syncing binlog on the same database instance, restart the sync task

### Data Source Timezone Mismatch

- **Symptom**: `The MySQL server has a timezone offset ... which does not match the configured timezone`
- **Cause**: timezone configured in the data source (default Asia/Shanghai) does not match actual database timezone
- **Resolution**: confirm the database's configured timezone, update the data source configuration

### Binlog Event Size Exceeded

- **Symptom**: `log event entry exceeded max_allowed_packet`
- **Cause**: database `max_allowed_packet` is smaller than a binlog event size, or binlog file is corrupted
- **Resolution**:
  1. Ask DBA to increase `max_allowed_packet` (max 1G), re-sync after it takes effect
  2. If still failing (binlog may be corrupted), restart task with a newer position to skip the problematic position
  3. Run "Re-sync" for tables that may have missing data

## Full Load Failures

### PK Length Exceeded

- **Symptom**: `Encoded key size 191 exceeds max size 128`
- **Cause**: source table primary key total field length exceeds 128 bytes, or extended field composite primary key is too long in sharded table merge scenarios
- **Resolution**: add a parameter in the sync task configuration to increase the PK length limit

## Sync Task Failover

### Disconnected from Lakehouse Ingestion Service

- **Symptom**: `Async commit for instance ... failed. rpcProxy call hit final failed after max retry reached`
- **Cause**: typically occurs during Lakehouse service upgrades
- **Resolution**: task usually auto-recovers after service upgrade completes; if failover persists, manually restart

### Binlog Event Deserialization Failed

- **Symptom**: `Failed to deserialize data of EventHeaderV4`
- **Cause**: sudden burst of binlog events from source, write-side backpressure causes read-side to stop consuming, binlog client connection times out
- **Resolution**:
  1. Short-term traffic spike: task usually auto-recovers within limited failover attempts
  2. Persistent: increase MySQL parameters `slave_net_timeout` and `thread_pool_idle_timeout`

## Schema Evolution Failed (Table Enters Blocklist)

- **Symptom**: table status changes to sync stopped, messages like `pk column different`, `pk column type mismatch`
- **Cause**: source table structure changed in a way not supported by Lakehouse (PK column list change, PK column type change)
- **Resolution**: correct source table structure, then run "Re-sync" for the stopped table

---

## cz-cli Alternative Path

Use when cz-cli is available and MCP is not. All operations delegate to the built-in agent via `cz-cli agent run`.

### Quick Path

```bash
# Create CDC multi-table real-time sync task
cz-cli task create "cdc_<database>" --type MULTI_REALTIME --folder <folder_name>
# Returns task_id and studio_url — complete configuration at studio_url

# Deploy (CDC tasks run continuously, no scheduling needed)
cz-cli task deploy "cdc_<database>" -y
```

### Full Database Mirror (agent)

```bash
cz-cli agent run "Create a CDC multi-table real-time sync task, mirror the entire <database> database from MySQL data source <source_ds_name> to Lakehouse, use Sync VCluster, task name cdc_<database>, place in <folder_name> folder" \
  --format a2a --dangerously-skip-permissions
```

### Multi-table Mirror (agent)

```bash
cz-cli agent run "Create a CDC multi-table real-time sync task (task_type=281), pipeline_type multi-table mirror (1), source datasource=<source_ds_name>, sync tables <table1>, <table2>, <table3> from <database>, target Lakehouse, task name cdc_<database>_selected" \
  --format a2a --dangerously-skip-permissions
```

### Sharded Table Merge (agent)

```bash
cz-cli agent run "Create a CDC multi-table real-time sync task (task_type=281), pipeline_type sharded table merge (2), source datasource=<source_ds_name>, merge multiple tables from <database> to Lakehouse target table, task name cdc_<database>_merged" \
  --format a2a --dangerously-skip-permissions
```

### Operations (cz-cli)

```bash
cz-cli runs list --task <task_name> --limit 10
cz-cli runs detail <run_id>
cz-cli attempts log <run_id>
cz-cli task undeploy <task_name> -y
```

---

## Delivery Acceptance Checklist

```sql
-- 1. Row count: after full load, ODS layer matches source
SELECT COUNT(*) FROM <ods_schema>.<table>;

-- 2. Incremental test: insert a record to source, confirm it syncs within 30 seconds

-- 3. Key field null rate
SELECT
  COUNT(*) AS total,
  COUNT(key_field) AS non_null,
  ROUND(COUNT(key_field) * 100.0 / COUNT(*), 2) AS non_null_pct
FROM <ods_schema>.<table>;

-- 4. _op field distribution
SELECT _op, COUNT(*) FROM <ods_schema>.<table> GROUP BY _op;
-- Normal: I (INSERT) records; UPDATE/DELETE scenarios will have U/D
```

**Acceptance criteria:**
- [ ] Full load complete, ODS row count matches source
- [ ] Incremental test data synced to Lakehouse within 30 seconds
- [ ] Key field null rate meets expectations
- [ ] _op field distribution is reasonable
- [ ] Task status is RUNNING, no frequent restarts
- [ ] Column type mapping is correct (watch BIT/ENUM/TEXT heterogeneous types)
