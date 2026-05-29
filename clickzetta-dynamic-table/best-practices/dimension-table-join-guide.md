# Dimension Table JOIN Scenarios — Detailed Guide

## Core Mechanism

After marking a table as a dimension table, the incremental engine treats that table's change data as **empty**. That is:
- Any data changes (INSERT/UPDATE/DELETE) to the dimension table **do not trigger incremental computation**
- During incremental computation, the dimension table always reads its **latest full data**
- Only changes in non-dimension tables (fact tables) drive incremental refresh

## Configuration

```sql
-- Method 1: DT table properties (recommended; follows DT definition)
CREATE DYNAMIC TABLE my_dt
TBLPROPERTIES('mv_const_tables'='dim_table1,dim_table2')
AS SELECT ...;

-- Method 2: Session configuration (set before REFRESH; flexible and dynamically adjustable)
set CZ_OPTIMIZER_INCREMENTAL_DIMENSION_TABLES=dim_table1:dim_table2
```

## Incremental Behavior Under Each JOIN Type

### A LEFT JOIN B (B is dimension table)

This is the most common dimension table JOIN scenario.

**Case 1: A has incremental data, B has no changes**
```
Incremental plan: A's change data LEFT JOIN B's full data
```
- New A rows LEFT JOIN with B's latest data
- If JOIN matches → output complete row
- If no match → B side outputs NULL
- ✅ Result is correct

**Case 2: B has data changes, A has no changes**
```
Incremental plan: no computation triggered (change data is empty)
```
- B's changes are completely ignored
- Previously output `(xxx, NULL)` rows (where A didn't match B) will not be corrected to `(xxx, yyy)`
- Previously output rows with old B data will not be updated to new values
- ⚠️ Result differs from full recomputation, but this is **expected behavior**

**Case 3: Both A and B have changes**
```
Incremental plan: A's change data LEFT JOIN B's full data
```
- Only A's incremental data is processed; B's changes are ignored
- New A rows will JOIN to B's latest data
- But existing A rows will not be updated due to B's changes
- ⚠️ New and old data may be inconsistent

### A INNER JOIN B (B is dimension table)

**Case 1: A has incremental data, B has no changes**
```
Incremental plan: A's change data INNER JOIN B's full data
```
- New A rows INNER JOIN with B
- A rows that don't match are discarded
- ✅ Result is correct

**Case 2: B has data changes, A has no changes**
```
Incremental plan: no computation triggered
```
- B adds data that can match existing A rows → no new results are produced
- B deletes data that matched existing A rows → already-output results are not retracted
- ⚠️ Result differs from full recomputation

### Dimension Tables in Multi-table JOINs

```sql
-- t2, t3 are both dimension tables
CREATE DYNAMIC TABLE dt
TBLPROPERTIES('mv_const_tables'='t2,t3')
AS
SELECT t1.*, t2.v1, t3.v1
FROM t1
LEFT JOIN t2 ON t1.id = t2.id
LEFT JOIN t3 ON t1.id = t3.id;
```

- Only t1's changes trigger incremental computation
- Changes to t2 and t3 are both ignored
- Incremental plan: t1's change data LEFT JOIN t2's full data LEFT JOIN t3's full data

## Scenarios Suitable for Dimension Tables

### ✅ Recommended Scenarios

1. **Lookup/dictionary table JOINs**
   - E.g., region code tables, product category tables, status code mapping tables
   - Characteristics: small data volume, rarely changes, even if it changes it doesn't affect historical analysis
   ```sql
   -- Region code table almost never changes
   TBLPROPERTIES('mv_const_tables'='dim_region')
   ```

2. **T+1 dimension table + real-time fact table**
   - Dimension table updates in batch once per day; fact table writes continuously
   - Between two dimension table updates, the dimension table can be treated as unchanged
   ```sql
   -- User profile table updates daily; order table writes in real-time
   TBLPROPERTIES('mv_const_tables'='dim_user_profile')
   ```

3. **Configuration table JOINs**
   - E.g., business rule configs, threshold configs, weight configs
   - Very low change frequency; after changes, a manual full refresh can correct data
   ```sql
   TBLPROPERTIES('mv_const_tables'='config_rules')
   ```

4. **Large fact table JOIN small dimension table, with low real-time requirements for dimension table changes**
   - Core goal is incremental performance on the fact table
   - Brief inconsistency after occasional dimension table changes is acceptable
   ```sql
   -- Product info table occasionally updates; order table writes continuously
   TBLPROPERTIES('mv_const_tables'='dim_product')
   ```

5. **External tables that don't support time travel as the right side of a JOIN**
   - External tables cannot provide change data; marking as dimension table enables normal incremental computation
   - The incremental engine reads the latest snapshot of the external table
   ```sql
   -- External MySQL table doesn't support time travel
   TBLPROPERTIES('mv_const_tables'='external_mysql_table')
   ```

### ❌ Not Recommended Scenarios

1. **Dimension table updates frequently and real-time consistency is required**
   - E.g., user status table updates every minute, and downstream reports require real-time reflection of the latest status
   - In this case, do not mark as dimension table; let both sides participate in incremental computation

2. **Dimension table changes affect the correctness of aggregation results**
   - E.g., after a price table update, historical order amounts should use the old price
   - But with dimension table marking, new fact rows will JOIN to the new price, while old fact rows keep the old price
   - If business requires all rows to use the latest price uniformly, do not use dimension table

3. **Dimension table has large data volume and changes frequently**
   - The optimization benefit of dimension table marking comes from skipping change data computation
   - If the dimension table itself is large and changes frequently, consider letting it participate in incremental normally

## Data Correction After Dimension Table Changes

Since dimension table changes do not trigger incremental computation, when a dimension table undergoes an important change (e.g., incorrect data was corrected, mapping relationships were updated), existing results in the DT will not be automatically updated. **If data correction is needed, a full refresh must be executed.**

```sql
-- Force full refresh (recommended)
set cz.optimizer.incremental.force.full.refresh=true
REFRESH DYNAMIC TABLE my_dt;
-- Remember to turn it off after refresh; otherwise every subsequent refresh will be full
set cz.optimizer.incremental.force.full.refresh=false

-- For partitioned tables, you can also do a full refresh of only a specific partition
set cz.optimizer.incremental.force.full.refresh=true
set dt.args.ds=2025-01-01
REFRESH DYNAMIC TABLE my_dt PARTITION(ds = '2025-01-01');
set cz.optimizer.incremental.force.full.refresh=false
```

Configuration notes:
- `cz.optimizer.incremental.force.full.refresh`: default `false`. When set to `true`, the next REFRESH ignores incremental logic and does a full scan and recomputation of all source tables.
- This config is Session-level; after the refresh completes, it must be manually reset to `false`; otherwise all subsequent REFRESHes will use full mode.
- Backfill mode (`cz.optimizer.incremental.backfill.enabled=TRUE`) also automatically enables full refresh.

## Performance Benefits

Optimization effects after marking dimension tables:
- **Skip dimension table change data scanning**: no need to read dimension table change logs
- **Simplify incremental plan**: only need to JOIN fact table change data with dimension table full data; no reverse computation needed

## ⚠️ Potential Data Inconsistency and Duplication After Enabling Dimension Tables

Marking dimension tables is a **tradeoff of consistency for performance**. The following are specific scenarios where problems will occur — evaluate whether the business can accept these before using.

### Scenario 1: LEFT JOIN — Dimension Table Update Causes NULL Not to Be Corrected

```sql
-- DT definition
SELECT order.*, product.name
FROM order LEFT JOIN product ON order.pid = product.id;
-- product marked as dimension table
```

| Time | Event | Result in DT | Expected result from full recomputation |
|------|------|------------|------------------|
| T1 | order inserts (pid=100); product has no id=100 | (pid=100, name=NULL) | (pid=100, name=NULL) |
| T2 | product inserts id=100, name='Phone' | (pid=100, name=NULL) **unchanged** | (pid=100, name='Phone') |

**Reason**: product's changes don't trigger incremental computation; the NULL row output at T1 will never be corrected.

### Scenario 2: INNER JOIN — Dimension Table New Data Causes Missing Results

```sql
SELECT order.*, product.name
FROM order INNER JOIN product ON order.pid = product.id;
-- product marked as dimension table
```

| Time | Event | Result in DT | Expected result from full recomputation |
|------|------|------------|------------------|
| T1 | order inserts (pid=200); product has no id=200 | No output (INNER JOIN no match) | No output |
| T2 | product inserts id=200, name='Computer' | **Still no output** | (pid=200, name='Computer') |

**Reason**: product's new data doesn't trigger incremental; existing order rows are not re-JOINed.

### Scenario 3: Dimension Table Delete/Update Causes Stale Data to Remain

```sql
SELECT order.*, product.name, product.price
FROM order LEFT JOIN product ON order.pid = product.id;
-- product marked as dimension table
```

| Time | Event | Result in DT | Expected result from full recomputation |
|------|------|------------|------------------|
| T1 | order inserts (pid=100); product id=100 price=99 | (pid=100, price=99) | (pid=100, price=99) |
| T2 | product updates id=100 price=**199** | (pid=100, price=**99**) old value remains | (pid=100, price=199) |
| T3 | product deletes id=100 | (pid=100, price=**99**) still remains | (pid=100, name=NULL) |

**Reason**: dimension table UPDATE/DELETE are both ignored; already-output rows keep old values.

### Scenario 4: Dimension Table + Aggregation Causes Inconsistent Aggregation Results

```sql
SELECT product.category, SUM(order.amount) as total
FROM order LEFT JOIN product ON order.pid = product.id
GROUP BY product.category;
-- product marked as dimension table
```

| Time | Event | Result in DT | Expected result from full recomputation |
|------|------|------------|------------------|
| T1 | order (pid=1, amount=100); product (id=1, category='A') | category='A', total=100 | Same |
| T2 | product updates id=1 category from 'A' to 'B' | category='A', total=100 **unchanged** | category='B', total=100 |
| T3 | order adds (pid=1, amount=200) | category='B', total=200 (new row JOINs to new category) | category='B', total=300 |

**Reason**: T2's category change doesn't trigger recomputation; T1's old data is still aggregated under the old category. T3's new data is aggregated under the new category. The final result has data for the same pid split across different categories, causing incorrect aggregation.

### Summary: When Results Will Be Inconsistent

| Dimension table change type | LEFT JOIN | INNER JOIN |
|--------------|-----------|------------|
| New matching row added | Old fact rows' NULL is not corrected | Old fact rows don't produce new results |
| Existing row updated | Old fact rows keep old values | Old fact rows keep old values |
| Existing row deleted | Old fact rows keep old values (won't become NULL) | Old fact rows are not retracted |

**Core principle**: any change to a dimension table does not affect already-output result rows. Only new fact table increments will JOIN to the dimension table's latest snapshot.
