# Studio Task Engineering SOP

## New Project Launch Process

Agile principle: **verify immediately after each step — don't wait until the full pipeline runs to discover issues.**

```
1. Create task folder
   cz-cli task create-folder <business_domain>_dw

2. Create ODS layer tables, verify immediately
   cz-cli task save-content 01_ddl_ods --content "<ods_ddl_sql>"
   cz-cli task run 01_ddl_ods
   ✅ Verify: SHOW TABLES IN <ods_schema>  → confirm tables created

3. Create data sync task, trigger once manually, verify immediately
   cz-cli task execute 00_sync
   ✅ Verify: SELECT COUNT(*) FROM <ods_schema>.<table>  → compare with source row count
            SELECT * FROM <ods_schema>.<table> LIMIT 5  → sample check fields

4. Create DWD layer tables, verify immediately
   cz-cli task save-content 02_ddl_dwd --content "<dwd_ddl_sql>"
   cz-cli task run 02_ddl_dwd
   ✅ Verify: SHOW TABLES IN <dwd_schema>  → confirm tables created

5. Generate ETL SQL, manually execute once to verify logic, then configure scheduling
   cz-cli task save-content 04_transform_ods_to_dwd --content "<etl_sql>"
   cz-cli task execute 04_transform_ods_to_dwd   ← run manually first
   ✅ Verify: SELECT COUNT(*) FROM <dwd_schema>.<table>
            Check key field non-null rate, LEFT JOIN result rows ≥ left table rows
   After confirmation, configure scheduling:
   cz-cli task save-cron 04_transform_ods_to_dwd --cron '0 30 2 * * * *'
   cz-cli task deploy 04_transform_ods_to_dwd

6. Create DWS/ADS Dynamic Tables, trigger first refresh
   cz-cli task save-content 03_ddl_dws_ads --content "<dws_ads_ddl_sql>"
   cz-cli task run 03_ddl_dws_ads
   REFRESH DYNAMIC TABLE <dws_schema>.<table>
   ✅ Verify: SHOW DYNAMIC TABLE REFRESH HISTORY <schema>.<table> LIMIT 3
            → status = SUCCESS, row count matches aggregation logic

7. Optional: data quality check task
   cz-cli task save-content 05_dqc_check --content "<dqc_sql>"
   cz-cli task save-cron 05_dqc_check --cron '0 0 3 * * * *'
   cz-cli task deploy 05_dqc_check
```

> **Fail-fast**: if any step's verification fails, stop and fix — don't continue. If ODS data is wrong, DWD will be wrong too.

---

## Creating Sync Tasks

### Single-table Offline Sync (INTEGRATION)

```
1. Create task and probe source schema (auto-fetches columns + infers splitPk/WHERE/write_mode)
   cz-cli task create-offline-sync sync_mysql_orders \
     --folder <folder> --source <ds> --source-db <db> --source-table <table> \
     --target-schema <schema> --target-table <table>

2. Review schema + recommendations with Agent
   cz-cli task offline-sync-schema <task_id> \
     --source <ds> --source-db <db> --source-table <table> \
     --target-schema <schema> --target-table <table>
   
   Agent output includes:
   - source_columns (names + native types)
   - recommendations: splitPk (column for parallel reads), write_mode (OVERWRITE/APPEND), WHERE, parallelism
   - source_params_template (use as base for config JSON)
   - partition_suggestion (if source has time column)

3. Agent generates config JSON, then save
   cz-cli task save-offline-sync <task_id> \
     --config '<full JSON>' --vc <integration_vc> --target-schema <schema>

4. If save returns create_table_ddl → create table before deploy
   echo "<ddl>" > /tmp/t.sql && cz-cli sql --file /tmp/t.sql --write
   ✅ Verify: DESC TABLE <schema>.<table>

5. Configure scheduling + deploy
   cz-cli task save-cron <task_id> --cron '0 0 2 * * * *'
   cz-cli task save-schedule <task_id> --vc <integration_vc>
   cz-cli task deploy <task_id> -y

6. Execute and verify
   cz-cli task execute <task_id> --vc <integration_vc>
   ✅ Verify: SELECT COUNT(*) FROM <schema>.<table>  → compare with source
   If source has expected 3 rows and target has 3 rows → sync correct
```

### Multi-table Sync (MULTI_DI)

```
1. Always specify --tables to avoid syncing entire database
   cz-cli task create-batch-sync sync_mysql_batch \
     --folder <folder> --source <ds> --database <db> \
     --tables "orders,products,customers" \
     --pipeline-type 1 \
     --batch-size 4 --parallelism 4 \
     --cron '0 0 2 * * * *' \
     --description "Batch sync core tables"

2. Deploy + execute (--cron now takes effect at creation)
   cz-cli task deploy <task_id> -y
   cz-cli task execute <task_id> --vc <integration_vc>
   ✅ Verify: SELECT COUNT(*) FROM <schema>.<each_table>
```

### Multi-table CDC (MULTI_REALTIME)

```
1. Create (prereq check + create + configure in one step)
   cz-cli task create-realtime-sync cdc_mysql_core \
     --folder <folder> --source <ds> --database <db> \
     --tables "orders,products" \
     --pipeline-type 1 --sync-mode 1

2. Deploy → start
   cz-cli task deploy <task_id> -y
   cz-cli task start <task_id>
```

---

## Creating Python Tasks

Python tasks use `save-script` (not `save-content`) and are deployed as data development tasks.

```
1. Write the Python script locally
   # main.py — Lakehouse Python task
   from clickzetta.zettapark.session import Session
   session = Session.builder.configs({...}).create()
   result = session.sql("SELECT COUNT(*) FROM sync_test.orders").collect()
   print(f"Row count: {result[0][0]}")
   session.close()

2. Create task
   cz-cli task create my_python_etl --type PYTHON --folder <folder>

3. Upload script
   cz-cli task save-script <task_id> --script-file ./main.py

4. Configure + deploy
   cz-cli task save-cron <task_id> --cron '0 0 6 * * * *'
   cz-cli task save-schedule <task_id> --vc default
   cz-cli task deploy <task_id> -y

5. Execute and verify
   cz-cli task execute <task_id>
   cz-cli runs logs <run_id>   ← NOT "task logs"
```

Or use the one-step shortcut:
```bash
cz-cli task create-setup my_python_etl --type PYTHON --folder <folder> \
  --script-file ./main.py --cron '0 0 6 * * * *' --vc default
```

---

## Incremental Iteration Guide

### Add Sync Table

```
1. Check lineage (load clickzetta-table-lineage)
2. Add table to existing sync task or create new single-table sync task
3. Manually trigger sync, verify: SELECT COUNT(*) FROM <ods_schema>.<new_table>
4. If DWD processing needed, append ETL SQL, verify, redeploy
```

### Add Field (Schema Evolution)

```
1. Check lineage — identify all affected downstream tasks/DTs
2. Update layer by layer (upstream to downstream):
   ODS: ALTER TABLE <ods_schema>.<table> ADD COLUMN <col> <type>
   ✅ Verify: DESC TABLE <ods_schema>.<table>

   DWD: update ETL SQL, manually execute, redeploy
   ✅ Verify: SELECT <new_col>, COUNT(*) FROM <dwd_schema>.<table> GROUP BY 1 LIMIT 5

   DWS/ADS: Dynamic Table doesn't support ALTER — use CREATE OR REPLACE to rebuild
   REFRESH DYNAMIC TABLE immediately after rebuild
   ✅ Verify: SHOW DYNAMIC TABLE REFRESH HISTORY LIMIT 3 → status = SUCCESS

3. Update Studio task scripts: cz-cli task save-content <task> --content "<updated_sql>"
```

### Add Metric / DWS Layer

```
1. Confirm metric definition with user (avoid rework)
2. Check if DWD has required fields — if not, follow "Add Field" first
3. CREATE OR REPLACE DYNAMIC TABLE <dws_schema>.<new_metric>
     REFRESH INTERVAL <n> <unit> vcluster <gp_cluster>
   AS SELECT ...;
   REFRESH DYNAMIC TABLE <dws_schema>.<new_metric>
   ✅ Verify: SELECT COUNT(*), SUM(<metric>) FROM <dws_schema>.<new_metric>
4. Save DDL to Studio task: cz-cli task save-content 03_ddl_dws_ads --content "<updated_ddl>"
```

### Modify ETL Logic

```
1. Check lineage — confirm downstream impact scope
2. Update ETL SQL, manually execute to verify:
   cz-cli task execute 04_transform_ods_to_dwd
   ✅ Verify: row count comparison, key field sampling
3. After verification, redeploy:
   cz-cli task save-content 04_transform_ods_to_dwd --content "<new_sql>"
   cz-cli task deploy 04_transform_ods_to_dwd
4. If downstream DTs affected, trigger full refresh:
   SET cz.optimizer.incremental.force.full.refresh = true;
   REFRESH DYNAMIC TABLE <dws_schema>.<table>;
   SET cz.optimizer.incremental.force.full.refresh = false;
```

### Clean Up Sync Tasks

```
# For sync tasks (INTEGRATION/MULTI_DI/etc.) — undeploy first, then delete
cz-cli task undeploy <task_id> -y
cz-cli task delete <task_id> -y

# For SQL/Python tasks — delete directly if DRAFT
# If published: undeploy first, then delete
```

---

## Delivery Verification Checklist

- [ ] Row counts at each layer match expectations (source ↔ ODS ↔ DWD)
- [ ] Sync task VC exists, `vcluster_type=INTEGRATION`, `state != SUSPENDED` (`SHOW VCLUSTERS`)
- [ ] Dynamic Table VCluster exists and `state = RUNNING`
- [ ] Dynamic Table refresh history shows SUCCESS
- [ ] Key field NULL rate within acceptable range
- [ ] LEFT JOIN result row count ≥ left table row count
- [ ] All DDL tasks are in DRAFT status
- [ ] DWS/ADS Dynamic Table DDL saved as DRAFT task (code asset), no scheduling configured
- [ ] Scheduling DAG has no circular dependencies
- [ ] ETL task dependency chain is complete (`cz-cli task deps <task>`, `task_dependencies` not empty)
- [ ] Key tables and fields have comments (refer to `lakehouse-doc-en` for `COMMENT ON TABLE` / `COMMENT ON COLUMN` syntax)
- [ ] Sources with PG columns named `a`/`A` (case collision) → one renamed in sink with `COMMENT` noting original name
- [ ] Sync tasks using `${bizdate}` in WHERE tested with hardcoded date first (manual execute does not resolve variables)
- [ ] OVERWRITE sync tasks confirmed: first run covers full data, incremental runs use WHERE with correct date range
