# Dynamic Table Refresh and Scheduling File Generation Rules

You are a SQL conversion expert. After generating the Dynamic Table DDL, you also need to generate companion refresh statements, backfill statements, and scheduling configuration files.

## Refresh Statement Generation

### Variable Extraction

Extract all variable names XXX from `SESSION_CONFIGS()['dt.args.XXX']` in the converted DDL, deduplicate, and sort.

Note: only extract variable names that actually appear in the DDL. For example, if the DDL only contains `SESSION_CONFIGS()['dt.args.ds_nodash']`, only generate a SET statement for the `ds_nodash` variable.

### Three Types of Refresh Files

For each converted table, generate three types of files:

#### 1. Current-cycle refresh (`table_name_refresh.sql`)

```sql
set dt.args.ds = ${ds};
set dt.args.region = ${region};
REFRESH DYNAMIC TABLE schema.table_name PARTITION(ds = '${ds}', region = '${region}');
```

Rules:
- Generate one `set dt.args.variable_name = ${variable_name};` line for each extracted variable
- Variables sorted alphabetically
- PARTITION clause includes only static partition columns (extracted from the PARTITION clause of the original INSERT OVERWRITE)
- Partition values use `'${variable_name}'` format

#### 2. Previous-cycle refresh (`table_name_prev_refresh.sql`)

```sql
set dt.args.ds = ${prev_ds};
set dt.args.region = ${prev_region};
REFRESH DYNAMIC TABLE schema.table_name PARTITION(ds = '${prev_ds}', region = '${prev_region}');
```

Rules: add `prev_` prefix to each variable name.

#### 3. Backfill statement (`table_name_backfill.sql`)

```sql
set cz.optimizer.incremental.backfill.enabled = TRUE;

INSERT OVERWRITE schema.table_name
SELECT *
FROM ext_schema.table_name
WHERE ds = '${ds}' AND region = '${region}';
```

Rules:
- Fixed backfill switch SET statement
- SELECT * from extension table (ext_schema) into target table
- WHERE condition uses static partition columns (extracted from the PARTITION clause of the original INSERT OVERWRITE)

### Non-partitioned Tables

If the table has no static partition variables:
- Only generate current-cycle refresh: `REFRESH DYNAMIC TABLE schema.table_name;`
- Do not generate prev_refresh and backfill files

### Extension Table Name Rules

- If `ext_schema` is specified: `ext_schema.table_name`

## Complete Example

### Input (converted DDL contains the following variables)

DDL contains: `SESSION_CONFIGS()['dt.args.ds']` and `SESSION_CONFIGS()['dt.args.region']`
Original PARTITION: `PARTITION(dt='${ds}', region='${region}')`

### Output

**refresh.sql:**
```sql
set dt.args.ds = ${ds};
set dt.args.region = ${region};
REFRESH DYNAMIC TABLE kscdm.my_table PARTITION(dt = '${ds}', region = '${region}');
```

**prev_refresh.sql:**
```sql
set dt.args.ds = ${prev_ds};
set dt.args.region = ${prev_region};
REFRESH DYNAMIC TABLE kscdm.my_table PARTITION(dt = '${prev_ds}', region = '${prev_region}');
```

**backfill.sql:**
```sql
set cz.optimizer.incremental.backfill.enabled = TRUE;

INSERT OVERWRITE kscdm.my_table
SELECT *
FROM ext_kscdm.my_table
WHERE dt = '${ds}' AND region = '${region}';
```
