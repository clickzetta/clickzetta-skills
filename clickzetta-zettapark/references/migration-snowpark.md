# Snowpark → ZettaPark Migration Guide

> Covers migrating Snowflake Snowpark Python code to ClickZetta ZettaPark.
> All content verified against **snowflake2lakehouse-data-engineering** (Frostbyte — 2 SPs + 1 UDF → ZettaPark, 37,894 orders validated)
> and **dbt2lakehouse-tpch** (2 Snowpark Python models → dbt-clickzetta Python models).
> For Snowflake SQL-level migration, use the `clickzetta-sql-migration` skill.

## Table of Contents

| Section | Content | Verified | Line |
|---------|---------|:---:|:----:|
| [1](#1-imports--session) | Imports & session | ✅ Frostbyte, TPCH | L18 |
| [2](#2-types--schema-construction) | Types & schema construction | ✅ Frostbyte | L78 |
| [3](#3-stored-procedures--python-scripts) | Stored procedures → Python scripts | ✅ Frostbyte | L101 |
| [4](#4-dataframe-api-changes) | DataFrame API changes | ✅ Frostbyte | L148 |
| [5](#5-functions--builtins) | Functions & builtins | ✅ Frostbyte, TPCH | L192 |
| [6](#6-udf--session-registration) | UDF & session registration | ✅ Frostbyte, TPCH | L236 |
| [7](#7-warehouse--query-tags) | Warehouse & query tags | ✅ Frostbyte, TPCH | L270 |
| [8](#8-dynamic-tables--streams-dbt) | Dynamic Tables & streams (dbt) | ✅ TPCH | L289 |
| [9](#9-complete-sp-example) | Complete SP example | ✅ Frostbyte | L326 |
| [10](#10-python-model-example-dbt) | Python model example (dbt) | ✅ TPCH | L361 |

---

## 1. Imports & Session

### Import Path Change (verified: Frostbyte 6 scripts, TPCH 2 models)

```python
# ❌ Snowpark
from snowflake.snowpark import Session
import snowflake.snowpark.functions as F
import snowflake.snowpark.types as T

# ✅ ZettaPark (verified: Frostbyte, TPCH)
from clickzetta.zettapark.session import Session
from clickzetta.zettapark import functions as F
import clickzetta.zettapark.types as T
```

### Session Creation (verified: Frostbyte, TPCH)

```python
# ❌ Snowpark
session = Session.builder.configs({
    "account":   "xxx.us-east-1",
    "user":      "my_user",
    "password":  "my_password",
    "warehouse": "COMPUTE_WH",
    "database":  "MY_DB",
    "schema":    "PUBLIC",
    "role":      "TRANSFORMER",
}).create()

# ✅ ZettaPark (verified: Frostbyte e2e.py, TPCH profiles.yml)
session = Session.builder.configs({
    "username":  os.environ["CLICKZETTA_USERNAME"],
    "password":  os.environ["CLICKZETTA_PASSWORD"],
    "service":   os.environ["CLICKZETTA_SERVICE"],      # e.g. cn-shanghai-alicloud.api.clickzetta.com
    "instance":  os.environ["CLICKZETTA_INSTANCE"],     # e.g. f8866243
    "workspace": os.environ["CLICKZETTA_WORKSPACE"],    # e.g. quick_start
    "schema":    "frostbyte_harmonized",
    "vcluster":  os.environ.get("CLICKZETTA_VCLUSTER", "default"),
}).create()
```

### Connection Parameter Mapping (verified: Frostbyte, TPCH)

| Snowpark | ZettaPark |
|---|---|
| `account` | `service` — cloud region API endpoint |
| `database` | `workspace` — different concept: Snowflake DB vs ClickZetta workspace |
| `warehouse` | `vcluster` — virtual cluster for compute |
| `role` | Not in session config — RBAC managed at workspace level |
| `schema` | `schema` — same |
| `user` | `username` — slightly different key name |
| `password` | `password` — same |
| — | `instance` — no Snowpark equivalent |

---

## 2. Types & Schema Construction

### T.StructType / T.StructField (verified: Frostbyte daily_city_metrics)

```python
# ❌ Snowpark (01_snowflake/steps/07_daily_city_metrics_update_sp/procedure.py)
import snowflake.snowpark.types as T

SHARED_COLUMNS = [
    T.StructField("DATE", T.DateType()),
    T.StructField("CITY_NAME", T.StringType()),
    T.StructField("COUNTRY_DESC", T.StringType()),
    T.StructField("DAILY_SALES", T.StringType()),
    T.StructField("AVG_TEMPERATURE_FAHRENHEIT", T.DecimalType()),
    T.StructField("AVG_PRECIPITATION_INCHES", T.DecimalType()),
    T.StructField("MAX_WIND_SPEED_100M_MPH", T.DecimalType()),
]
DAILY_CITY_METRICS_SCHEMA = T.StructType(DAILY_CITY_METRICS_COLUMNS)

# ✅ ZettaPark (03_lakehouse/steps/07_daily_city_metrics.py — verified)
import clickzetta.zettapark.types as T

SHARED_COLUMNS = [
    T.StructField("DATE", T.DateType()),
    T.StructField("CITY_NAME", T.StringType()),
    ...
]
DAILY_CITY_METRICS_SCHEMA = T.StructType(DAILY_CITY_METRICS_COLUMNS)
```

`T.StructField`, `T.StructType`, `T.DateType`, `T.StringType`, `T.DecimalType` are available in `clickzetta.zettapark.types` — verified in Frostbyte.

---

## 3. Stored Procedures → Python Scripts

This is the single biggest architectural change. Both Frostbyte SPs were migrated and verified.

### Snowflake SP Deployment Model

```python
# ❌ Snowpark: deploy → register → CALL
# deploy_snowpark_apps.py:
#   snow snowpark build --temporary-connection --account $SNOWFLAKE_ACCOUNT ...
#   snow snowpark deploy --replace ...
def main(session: Session) -> str:
    # ... business logic ...
    return "Success"
# Called via SQL: CALL HARMONIZED.ORDERS_UPDATE_SP();
```

### ZettaPark: Direct Python Script (verified: Frostbyte)

```python
# ✅ ZettaPark (03_lakehouse/steps/06_orders_update.py — verified 37,894 orders)
"""
Snowflake: Python SP (deployed to Snowflake, called via CALL)
Lakehouse: Plain Python script (run directly or via cz-cli task)
    - No CREATE PROCEDURE / CALL needed
    - Logic is identical
    - ALTER WAREHOUSE SIZE = XLARGE → removed; VCluster scales automatically
"""

def create_session():
    return Session.builder.configs({...}).create()

def main():
    session = create_session()
    try:
        if not table_exists(session, 'FROSTBYTE_HARMONIZED', 'ORDERS'):
            session.sql("CREATE TABLE frostbyte_harmonized.orders LIKE frostbyte_harmonized.pos_flattened_v").collect()
            session.sql("CREATE STREAM frostbyte_harmonized.orders_stream ON TABLE frostbyte_harmonized.orders").collect()
        session.sql("""
            MERGE INTO frostbyte_harmonized.orders t
            USING frostbyte_harmonized.pos_flattened_v_stream s
            ON t.order_detail_id = s.order_detail_id
            WHEN MATCHED THEN UPDATE SET *
            WHEN NOT MATCHED THEN INSERT *
        """).collect()
    finally:
        session.close()

if __name__ == '__main__':
    main()
```

| Snowpark SP | ZettaPark Python Script |
|---|---|
| `snow snowpark build` + `deploy` | `cz-cli task create --type PYTHON` + `save-script` |
| `CREATE PROCEDURE ... CALL proc()` | `python script.py` or `cz-cli task execute` |
| `main(session: Session) -> str:` entry | `if __name__ == '__main__': main()` standard Python |
| Session passed by Snowflake runtime | Explicit `create_session()` in script |

---

## 4. DataFrame API Changes

### session.table().merge() → SQL MERGE INTO (verified: Frostbyte)

```python
# ❌ Snowpark (01_snowflake/steps/06_orders_update_sp/procedure.py)
target = session.table('HARMONIZED.ORDERS')
source = session.table('HARMONIZED.POS_FLATTENED_V_STREAM')
cols_to_update = {c: source[c] for c in source.schema.names if "METADATA" not in c}
metadata_col_to_update = {"META_UPDATED_AT": F.current_timestamp()}
updates = {**cols_to_update, **metadata_col_to_update}
target.merge(source, target['ORDER_DETAIL_ID'] == source['ORDER_DETAIL_ID'],
             [F.when_matched().update(updates), F.when_not_matched().insert(updates)])

# ✅ ZettaPark (03_lakehouse/steps/06_orders_update.py — verified)
# session.table().merge() API → standard SQL MERGE INTO
session.sql("""
    MERGE INTO frostbyte_harmonized.orders t
    USING frostbyte_harmonized.pos_flattened_v_stream s
    ON t.order_detail_id = s.order_detail_id
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
""").collect()
```

### session.table() (verified: both projects)

```python
# ❌ Snowpark — 3-level: database.schema.table
df = session.table("HARMONIZED.ORDERS")

# ✅ ZettaPark — 2-level: schema.table (workspace replaces database)
df = session.table("frostbyte_harmonized.orders")
```

### DataFrame Methods (verified: Frostbyte)

These Snowpark methods were used in Frostbyte and migrated to ZettaPark:

| Snowpark | ZettaPark |
|---|---|
| `df.select(F.col("x"))` | `df.select(F.col("x"))` |
| `df.filter(F.col("x"))` | `df.filter(F.col("x"))` |
| `df.group_by(F.col("x"))` | `df.group_by(F.col("x"))` — both snake_case |
| `df.agg(F.sum("x").alias("y"))` | `df.agg(F.sum("x").as_("y"))` — `.alias()`→`.as_()` |
| `df.with_column("x", expr)` | `df.with_column("x", expr)` — both snake_case |
| `df.count()` | `df.count()` |
| `df.show()` / `df.limit(5).show()` | `df.show()` / `df.limit(5).show()` |
| `df.collect()` | `df.collect()` |
| `df.schema.names` | `df.schema.names` |
| `session.create_dataframe(data, schema)` | `session.create_data_frame(data, schema)` — snake_case |

---

## 5. Functions & Builtins

### F.call_builtin() → Standard F functions (verified: Frostbyte)

```python
# ❌ Snowpark
.with_column("DAILY_SALES", F.call_builtin("ZEROIFNULL", F.col("price_nulls")))

# ✅ ZettaPark (verified: Frostbyte daily_city_metrics)
.with_column("DAILY_SALES", F.coalesce(F.col("price_nulls"), F.lit(0)))
```

| Snowpark | ZettaPark |
|---|---|
| `F.call_builtin("ZEROIFNULL", col)` | `F.coalesce(col, F.lit(0))` |

### F.call_udf() → Direct call or inline (verified: Frostbyte)

```python
# ❌ Snowpark — calls a Python UDF registered in Snowflake
F.call_udf("ANALYTICS.FAHRENHEIT_TO_CELSIUS_UDF", F.col("TEMP_F"))

# ✅ ZettaPark (verified: Frostbyte — inline for simple UDFs)
# Inline the formula directly:
df.with_column("celcius", (F.col("temp_f") - F.lit(32)) * F.lit(5.0 / 9.0))
# For complex UDFs: register as ClickZetta EXTERNAL FUNCTION, call via F.expr()
```

### F Functions (verified: Frostbyte, TPCH)

| Snowpark Function | ZettaPark |
|---|---|
| `F.col("x")` | `F.col("x")` |
| `F.lit(v)` | `F.lit(v)` |
| `F.sum("x")` | `F.sum("x")` |
| `F.count("x")` | `F.count("x")` |

---

## 6. UDF & Session Registration

### Snowflake Python UDF → Inline or EXTERNAL FUNCTION (verified: Frostbyte)

```python
# ❌ Snowpark — Python UDF deployed to Snowflake
# 01_snowflake/steps/05_fahrenheit_to_celsius_udf/function.py
def main(temp_f: float) -> float:
    return (float(temp_f) - 32) * (5 / 9)
# Deployed via: snow snowpark build && snow snowpark deploy
# Called via:   F.call_udf("ANALYTICS.FAHRENHEIT_TO_CELSIUS_UDF", F.col("TEMP"))

# ✅ ZettaPark — inline for simple logic (verified: Frostbyte)
df.with_column("celcius", (F.col("temp_f") - F.lit(32)) * F.lit(5.0 / 9.0))
# For complex UDFs: register as ClickZetta EXTERNAL FUNCTION
```

### session.sproc.register() — Removed (verified: TPCH)

```python
# ❌ Snowpark (TPCH 01_snowflake/models/silver/run/async_bulk_operations.py)
self.session.sproc.register(
    func=bulk_thread_runner,
    name="BULK_THREAD_RUNNER",
    is_permanent=False,
    replace=True,
    packages=["snowflake-snowpark-python"],
)

# ✅ ZettaPark (TPCH — sproc.register() removed entirely)
# No equivalent. For parallel execution: Python concurrent.futures or multiple Studio tasks.
```

---

## 7. Warehouse & Query Tags

### ALTER WAREHOUSE — Removed (verified: Frostbyte, TPCH)

```python
# ❌ Snowpark — SPs scale warehouse before heavy operations
_ = session.sql('ALTER WAREHOUSE HOL_WH SET WAREHOUSE_SIZE = XLARGE WAIT_FOR_COMPLETION = TRUE').collect()
# ... heavy MERGE ...
_ = session.sql('ALTER WAREHOUSE HOL_WH SET WAREHOUSE_SIZE = XSMALL').collect()

# ✅ ZettaPark — VCluster auto-scales; ALTER WAREHOUSE lines removed
# Frostbyte migration note: "ALTER WAREHOUSE SIZE = XLARGE → removed; VCluster scales automatically"
```

### session.query_tag — Not a settable property (verified: TPCH)

```python
# ❌ Snowpark
session.query_tag = f"Thread {thread_number} of {total_number_of_threads}"

# ✅ ZettaPark — via session config hints at creation time only
session = Session.builder.configs({
    ...
    "hints": {"query_tag": "my_zettapark_app"},
}).create()
```

---

## 8. Dynamic Tables & Streams (dbt context)

Verified in TPCH migration. Full details in the `clickzetta-sql-migration` skill.

### Dynamic Table Config (verified: TPCH)

```sql
-- Snowflake dbt config
{{ config(materialized='dynamic_table', snowflake_warehouse=target.warehouse, target_lag='1 hour') }}

-- ClickZetta dbt config (verified TPCH silver/order_facts_dynamic.sql)
{{ config(materialized='dynamic_table', refresh_interval='1 hour', refresh_vc='default') }}
```

### Table Stream Metadata (verified: TPCH)

| Snowflake | ClickZetta |
|---|---|
| `METADATA$ACTION` | `` `__change_type` `` (backtick required) |
| `METADATA$ISUPDATE` | `__change_type = 'UPDATE_BEFORE'` |
| `METADATA$ROW_ID` | `__commit_version` |
| `SHOW_INITIAL_ROWS = TRUE` | `TABLE_STREAM_MODE = 'STANDARD'` |

---

## 9. Complete SP Example

### Snowpark SP (before)

From `snowflake2lakehouse-data-engineering/01_snowflake/steps/06_orders_update_sp/procedure.py`:

```python
from snowflake.snowpark import Session
import snowflake.snowpark.functions as F

def table_exists(session, schema='', name=''):
    exists = session.sql(
        "SELECT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES "
        "WHERE TABLE_SCHEMA = '{}' AND TABLE_NAME = '{}') AS TABLE_EXISTS"
        .format(schema, name)
    ).collect()[0]['TABLE_EXISTS']
    return exists

def main(session: Session) -> str:
    if not table_exists(session, schema='HARMONIZED', name='ORDERS'):
        session.sql("CREATE TABLE HARMONIZED.ORDERS LIKE HARMONIZED.POS_FLATTENED_V").collect()
        session.sql("ALTER TABLE HARMONIZED.ORDERS ADD COLUMN META_UPDATED_AT TIMESTAMP").collect()
        session.sql("CREATE STREAM HARMONIZED.ORDERS_STREAM ON TABLE HARMONIZED.ORDERS").collect()

    session.sql('ALTER WAREHOUSE HOL_WH SET WAREHOUSE_SIZE = XLARGE WAIT_FOR_COMPLETION = TRUE').collect()

    source = session.table('HARMONIZED.POS_FLATTENED_V_STREAM')
    target = session.table('HARMONIZED.ORDERS')
    cols_to_update = {c: source[c] for c in source.schema.names if "METADATA" not in c}
    metadata_col_to_update = {"META_UPDATED_AT": F.current_timestamp()}
    updates = {**cols_to_update, **metadata_col_to_update}
    target.merge(source, target['ORDER_DETAIL_ID'] == source['ORDER_DETAIL_ID'],
                 [F.when_matched().update(updates), F.when_not_matched().insert(updates)])

    session.sql('ALTER WAREHOUSE HOL_WH SET WAREHOUSE_SIZE = XSMALL').collect()
    return "Success"
```

### ZettaPark (after — verified, 37,894 orders e2e)

From `03_lakehouse/steps/06_orders_update.py`:

```python
from clickzetta.zettapark.session import Session
import os

def create_session():
    return Session.builder.configs({
        "username":  os.environ["CLICKZETTA_USERNAME"],
        "password":  os.environ["CLICKZETTA_PASSWORD"],
        "service":   os.environ["CLICKZETTA_SERVICE"],
        "instance":  os.environ["CLICKZETTA_INSTANCE"],
        "workspace": os.environ["CLICKZETTA_WORKSPACE"],
        "schema":    "frostbyte_harmonized",
        "vcluster":  os.environ.get("CLICKZETTA_VCLUSTER", "default"),
    }).create()

def table_exists(session, schema, name):
    result = session.sql(f"""
        SELECT COUNT(*) AS cnt FROM information_schema.tables
        WHERE table_schema = '{schema.upper()}' AND table_name = '{name.upper()}'
    """).collect()
    return result[0]['cnt'] > 0

def main():
    session = create_session()
    try:
        if not table_exists(session, 'FROSTBYTE_HARMONIZED', 'ORDERS'):
            session.sql("CREATE TABLE frostbyte_harmonized.orders "
                        "LIKE frostbyte_harmonized.pos_flattened_v").collect()
            session.sql("ALTER TABLE frostbyte_harmonized.orders "
                        "ADD COLUMN META_UPDATED_AT TIMESTAMP").collect()
            session.sql("CREATE STREAM frostbyte_harmonized.orders_stream "
                        "ON TABLE frostbyte_harmonized.orders").collect()

        session.sql("""
            MERGE INTO frostbyte_harmonized.orders t
            USING frostbyte_harmonized.pos_flattened_v_stream s
            ON t.order_detail_id = s.order_detail_id
            WHEN MATCHED THEN UPDATE SET *
            WHEN NOT MATCHED THEN INSERT *
        """).collect()
    finally:
        session.close()

if __name__ == '__main__':
    main()
```

### Verified Changes

| Change | Count |
|--------|:---:|
| Import: `snowflake.snowpark` → `clickzetta.zettapark` | 1 |
| Session config: account/warehouse/database → service/instance/workspace | 6 keys |
| `ALTER WAREHOUSE SET WAREHOUSE_SIZE = XLARGE` → Removed | 2 lines |
| `target.merge(source, cond, [...])` → `session.sql("MERGE INTO ...")` | 1 block |
| `F.when_matched().update({...})` → `WHEN MATCHED THEN UPDATE SET *` | 1 block |
| `main(session: Session) -> str:` → `if __name__ == '__main__': main()` | 1 signature |
| No `CREATE PROCEDURE` / `CALL` | Removed |

---

## 10. Python Model Example (dbt)

### Snowpark dbt Model (before)

From `dbt2lakehouse-tpch/01_snowflake/models/silver/run/customer_clustering.py`:

```python
import snowflake.snowpark as snowpark
def model(dbt, session: snowpark.Session):
    df = dbt.ref('dim_customers').to_pandas()
    # ... scikit-learn clustering ...
    return df
```

### dbt-clickzetta Python Model (after — verified, `dbt run` passed)

From `dbt2lakehouse-tpch/03_lakehouse/models/silver/run/customer_clustering.py`:

```python
def model(dbt, session):
    df = dbt.ref('dim_customers').to_pandas()
    # ⚠️ ZettaPark .to_pandas() returns lowercase column names (Snowpark returns UPPERCASE)
    df.columns = df.columns.str.upper()
    # ... scikit-learn clustering ...
    return df
```

| Snowpark dbt | dbt-clickzetta |
|---|---|
| `import snowflake.snowpark as snowpark` | No import needed |
| `session: snowpark.Session` type hint | No type hint needed |
| `packages=['snowflake-snowpark-python', 'joblib']` | `packages=['scikit-learn', 'pandas', 'numpy']` |
| `.to_pandas()` returns **UPPERCASE** columns | `.to_pandas()` returns **lowercase** columns — add `.str.upper()` |
| `session.sproc.register(...)` | Removed — not supported |
| `session.query_tag = "..."` | Via session config hints at creation time |

---

## Related Skills

| Scenario | Skill |
|----------|-------|
| ZettaPark API reference | `clickzetta-zettapark` |
| PySpark DataFrame → ZettaPark | `clickzetta-zettapark` |
| Studio Python task deployment | `clickzetta-studio-task-manager` |
| Snowflake SQL → ClickZetta SQL | `clickzetta-sql-migration` |
| dbt project migration | `clickzetta-sql-migration` |
| Function mapping | `clickzetta-sql-migration` |
