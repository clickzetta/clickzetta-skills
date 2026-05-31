# Studio Task Engineering SOP

## New Project Launch Process

Agile principle: **verify immediately after each step — don't wait until the full pipeline runs to discover issues.**

```
1. Create task folder
   cz-cli task folder create <business_domain>_dw

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
   cz-cli task save-cron 04_transform_ods_to_dwd --cron '0 30 2 * * ? *'
   cz-cli task deploy 04_transform_ods_to_dwd

6. Create DWS/ADS Dynamic Tables, trigger first refresh
   cz-cli task save-content 03_ddl_dws_ads --content "<dws_ads_ddl_sql>"
   cz-cli task run 03_ddl_dws_ads
   REFRESH DYNAMIC TABLE <dws_schema>.<table>
   ✅ Verify: SHOW DYNAMIC TABLE REFRESH HISTORY <schema>.<table> LIMIT 3
            → status = SUCCESS, row count matches aggregation logic

7. Optional: data quality check task
   cz-cli task save-content 05_dqc_check --content "<dqc_sql>"
   cz-cli task save-cron 05_dqc_check --cron '0 0 3 * * ? *'
   cz-cli task deploy 05_dqc_check
```

> **Fail-fast**: if any step's verification fails, stop and fix — don't continue. If ODS data is wrong, DWD will be wrong too.

---

## Incremental Iteration Guide

### Add Sync Table

```
1. Check lineage (load clickzetta-table-lineage)
2. Add table to existing sync task or create new single-table sync task
3. Manually trigger sync, verify: SELECT COUNT(*) FROM <ods_schema>.<new_table>
4. If DWD processing needed, append ETL SQL to 04_transform, verify, redeploy
```

### Add Field (Schema Evolution)

```
1. Check lineage — identify all affected downstream tasks/DTs
2. Update layer by layer (upstream to downstream):
   ODS: ALTER TABLE <ods_schema>.<table> ADD COLUMN <col> <type>
   ✅ Verify: DESC TABLE <ods_schema>.<table>

   DWD: update ETL SQL, manually execute to verify, redeploy
   ✅ Verify: SELECT <new_col>, COUNT(*) FROM <dwd_schema>.<table> GROUP BY 1 LIMIT 5

   DWS/ADS: Dynamic Table doesn't support ALTER — use CREATE OR REPLACE to rebuild
   REFRESH DYNAMIC TABLE immediately after rebuild
   ✅ Verify: SHOW DYNAMIC TABLE REFRESH HISTORY LIMIT 3 → status = SUCCESS

3. Update Studio task scripts: cz-cli task save-content <task_name> --content "<updated_sql>"
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

---

## Delivery Verification Checklist

- [ ] Row counts at each layer match expectations
- [ ] Dynamic Table VCluster exists and `status = RUNNING` (`SHOW VCLUSTERS`)
- [ ] Dynamic Table refresh history shows SUCCESS
- [ ] Key field NULL rate within acceptable range
- [ ] LEFT JOIN result row count ≥ left table row count
- [ ] All DDL tasks are in DRAFT status
- [ ] DWS/ADS Dynamic Table DDL saved as DRAFT task (code asset), no scheduling configured
- [ ] Scheduling DAG has no circular dependencies
- [ ] ETL task dependency chain is complete (`cz-cli task deps <task>`, `task_dependencies` not empty)
- [ ] Key tables and fields have comments (load `clickzetta-manage-comments`)
