# DBT Real-Time Data Pipeline in Practice

> The code in this article comes from two directly runnable projects:
> - [clickzetta/snowflake-dbt2lakehouse-dbt](https://github.com/clickzetta/snowflake-dbt2lakehouse-dbt) — TPC-H order data warehouse
> - [clickzetta/dbt-clickzetta](https://github.com/clickzetta/dbt-clickzetta) (`examples/` directory) — feature demonstration project

---

## Two Real-Time Pipeline Modes

dbt + Singdata Lakehouse supports two real-time data pipeline modes for different scenarios:

| Mode | Mechanism | Use Cases |
|---|---|---|
| **Dynamic Table** | Declarative SQL; the system automatically refreshes incrementally on a schedule | Aggregation, transformation, multi-layer data warehouse pipelines |
| **Table Stream + CDC** | Captures row-level changes (INSERT/UPDATE/DELETE) on a table; consumers read the change stream | Audit logs, dimension change tracking, downstream real-time sync |

The two can be combined: use Table Stream to capture source table changes, and use Dynamic Table to aggregate the change data.

---

## Dynamic Table

### What Is a Dynamic Table

A Dynamic Table is Singdata Lakehouse's declarative incremental computation object. You only need to define a SQL statement, and the system automatically computes and maintains the result on the configured refresh schedule — no scheduling scripts to write, no state to manage, and failed refreshes are automatically retried.

**Incremental computation mechanism**: A Dynamic Table does not recompute everything from scratch each time. Instead, it analyzes the SQL's dependency relationships and processes only the changed portions of upstream data. For example, a Dynamic Table that does a GROUP BY on an orders table — when 100 new rows are added to the orders table, the system only recomputes the groups affected by those 100 rows, rather than scanning all data. This is why the first creation requires a full refresh (to establish a baseline), while subsequent refreshes typically take only a few seconds.

Differences from a regular `incremental` model:

| | incremental model | Dynamic Table |
|---|---|---|
| Trigger | Manual `dbt run` | System auto-refreshes on a schedule |
| Refresh logic | You write `{% if is_incremental() %}` filters | System automatically handles incremental computation |
| Suitable for | Need precise control over run timing | Need continuous automatic refresh |
| View refresh status | N/A | `SHOW DYNAMIC TABLE REFRESH HISTORY` |

### Basic Usage

```sql
{{ config(
    materialized='dynamic_table',
    refresh_interval='5 MINUTE',
    refresh_vc='default'
) }}

select
    customer_id,
    count(order_id)  as order_count,
    sum(amount)      as total_amount,
    max(updated_at)  as last_order_time
from {{ ref('stg_orders') }}
group by customer_id
```

Two key parameters:
- `refresh_interval`: Refresh schedule, supports `'5 MINUTE'`, `'1 HOUR'`, `'1 DAY'`, etc. (use singular uppercase for units)
- `refresh_vc`: Name of the compute cluster to use for refreshes. Since Dynamic Tables perform aggregation queries, it is recommended to use an analytics cluster (`default_ap`)

After `dbt build` creates the Dynamic Table, the system immediately begins auto-refreshing on the schedule — no additional action needed.

### Manually Triggering a Refresh

When you need the latest data immediately, you can trigger a manual refresh:

```bash
dbt run-operation refresh_dynamic_table --args '{model_name: customer_stats_dynamic}'
```

### Practical Example: Real-Time Order Aggregation

The following is an actual Dynamic Table running in [snowflake-dbt2lakehouse-dbt](https://github.com/clickzetta/snowflake-dbt2lakehouse-dbt), automatically refreshing order aggregation metrics every hour:

```sql
{{ config(
    materialized='dynamic_table',
    refresh_vc='default',
    refresh_interval='1 HOUR'
) }}

{% set order_statuses = ['O', 'F', 'P'] %}

select
    date_trunc('day', o_orderdate)    as order_date,
    extract(year    from o_orderdate) as order_year,
    extract(quarter from o_orderdate) as order_quarter,
    o_custkey                         as customer_key,
    o_orderstatus                     as order_status,

    count(*)                                      as order_count,
    sum(o_totalprice)                             as total_order_value,
    avg(o_totalprice)                             as avg_order_value,
    count(distinct o_custkey)                     as unique_customers,

    {% for status in order_statuses %}
    sum(case when o_orderstatus = '{{ status }}' then o_totalprice else 0 end)
        as revenue_{{ status.lower() }}_status,
    {% endfor %}

    current_timestamp() as last_updated

from {{ ref('stg_orders_incremental') }}
where processing_type in ('RECENT', 'FULL_LOAD')
group by
    date_trunc('day', o_orderdate),
    extract(year from o_orderdate),
    extract(quarter from o_orderdate),
    o_custkey,
    o_orderstatus
```

Jinja's `{% for %}` loop automatically expands aggregation columns for multiple statuses, avoiding repetitive code.

### Dynamic Table Referencing a Dynamic Table

A Dynamic Table can reference another Dynamic Table, building a multi-layer pipeline:

```sql
-- Silver layer: hourly refresh of order aggregations
{{ config(materialized='dynamic_table', refresh_interval='1 HOUR', refresh_vc='default') }}
select ... from {{ ref('stg_orders_incremental') }} ...

-- Gold layer: references the Silver layer, filters to the last year of data
{{ config(
    materialized='dynamic_table',
    refresh_vc='default',
    refresh_interval='1 hour',
    alias='DIM_CURRENT_YEAR_ORDERS'
) }}

select *
from {{ ref('dim_orders') }}
where order_date >= (
    select dateadd(year, -1, date_trunc('day', max(order_date)))
    from {{ ref('dim_orders') }}
)
order by order_key
```

> ⚠️ **Note**: Singdata Lakehouse does not support Snowflake's `target_lag='DOWNSTREAM'` (downstream-triggered refresh). Each Dynamic Table needs its own `refresh_interval` configured independently.

### Viewing Refresh Status

```sql
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'order_facts_dynamic' LIMIT 5;
```

Returns the start time, end time, status (SUCCEED/FAILED), and refresh mode (INCREMENTAL/FULL) for each refresh.

---

## Table Stream (CDC)

### What Is a Table Stream

Table Stream is Singdata Lakehouse's change data capture (CDC) mechanism. After creating a Stream on a table, every INSERT, UPDATE, and DELETE operation on that table is recorded, and consumers can read these change records.

Core characteristics of a Stream:
- **Does not copy data**: A Stream only records changes; it does not store a full data copy
- **Offset advances automatically**: Only DML operations (INSERT/MERGE, etc.) advance the offset; SELECT does not
- **System columns**: Each change row comes with three system columns: `__change_type`, `__commit_timestamp`, `__commit_version`

### Using Table Stream in DBT

> 💡 **Prerequisite**: `sources.yml` only tells dbt "where this Stream is." The Stream itself must be created in Singdata Lakehouse in advance (`CREATE TABLE STREAM ... ON TABLE ...`), or automatically created at model run time via a dbt macro (see the practical example below).

**Step 1: Declare the Stream in `sources.yml`**

```yaml
sources:
  - name: my_streams
    schema: my_schema
    tables:
      - name: orders_stream
        description: "Change stream for the orders table"
```

**Step 2: Reference it in the model using `source()`**

```sql
{{ config(materialized='view') }}

select
    `__change_type`,
    `__commit_timestamp`,
    order_id,
    customer_id,
    amount,
    status
from {{ source('my_streams', 'orders_stream') }}
```

> ⚠️ **Note**: `__change_type`, `__commit_timestamp`, and `__commit_version` are reserved system names and must be wrapped in backticks when referenced.

### SELECT * EXCEPT to Filter System Columns

When consuming a Stream, you typically only need the business columns, not the system columns. Use `SELECT * EXCEPT(...)` to filter out system columns without hardcoding all business column names:

```sql
select
    * except (`__change_type`, `__commit_timestamp`, `__commit_version`),
    `__change_type`      as cdc_change_type,
    `__commit_timestamp` as cdc_commit_ts
from {{ source('my_streams', 'orders_stream') }}
```

This way, when new columns are added to the source table, the consuming model does not need to be modified.

### Practical Example: Customer Dimension Change Tracking

The following is an actual CDC pipeline running in [snowflake-dbt2lakehouse-dbt](https://github.com/clickzetta/snowflake-dbt2lakehouse-dbt), tracking every change to the `dim_customers` table:

**Step 1: Macro to create the Stream** (`macros/get_table_stream.sql`)

```sql
{%- macro get_table_stream(table, stream_name=( (this.alias or this.name) ~ "_ts" )) -%}
    {%- set stream_full = this.schema ~ "." ~ stream_name -%}
    {% if execute and flags.WHICH in ('run', 'build') %}
        {%- set stream_create_statement -%}
        create table stream if not exists {{ stream_full }}
        on table {{ table }}
        with properties ('TABLE_STREAM_MODE' = 'STANDARD')
        {%- endset -%}
        {%- do run_query(stream_create_statement) -%}
    {%- endif -%}
    {{ return(stream_full) }}
{%- endmacro -%}
```

This macro automatically creates the Stream at model run time (if it does not exist) and returns the Stream name for use in the FROM clause. `TABLE_STREAM_MODE = 'STANDARD'` captures all three types of changes: INSERT/UPDATE/DELETE.

**Step 2: Consume the Stream** (`models/gold/dim_customer_changes.sql`)

```sql
{{ config(
    materialized='incremental',
    alias='DIM_CUSTOMER_CHANGES'
) }}

select
    row_number() over (order by `__commit_timestamp`, customer_key) as log_id,
    * except (`__change_type`, `__commit_timestamp`, `__commit_version`),
    `__change_type`      as cdc_change_type,
    `__commit_timestamp` as cdc_commit_ts,
    `__commit_version`   as cdc_version,
    case when `__change_type` = 'DELETE' then 'Y' else 'N' end as delete_flag
from {{ get_table_stream(ref('dim_customers')) }} as d
where not (`__change_type` = 'DELETE' and `__change_type` != 'UPDATE_BEFORE')
qualify 1 = row_number() over (
    partition by customer_key
    order by `__commit_timestamp` desc, `__change_type` desc
)
```

A few key points:
- `get_table_stream(ref('dim_customers'))` automatically creates a Stream on `dim_customers` and returns the Stream name
- `* except (...)` filters out the three system columns, then aliases them separately
- `where not (__change_type = 'DELETE' and __change_type != 'UPDATE_BEFORE')` — this condition filters out pure DELETE rows (`__change_type = 'DELETE'` and not UPDATE_BEFORE), keeping INSERT, UPDATE_BEFORE, and UPDATE_AFTER
- `qualify row_number() = 1` keeps only the most recent change record for the same `customer_key`

### Stream Offset Management

A Stream's offset records "where the consumer last read up to." The offset only advances after a DML operation (INSERT/MERGE, etc.) succeeds; SELECT does not advance it. This design guarantees **idempotency**: if consumption fails, the same data can be read again on the next attempt without losing any changes.

```sql
-- This SELECT does not advance the offset; the same data can be read again next time
select * from my_schema.orders_stream;

-- This MERGE advances the offset after success; only new changes can be read next time
merge into target_table
using my_schema.orders_stream as src
on target_table.id = src.id
when matched then update ...
when not matched then insert ...;
```

dbt's `incremental` model executes MERGE INTO on each run, so the Stream's offset automatically advances after each successful `dbt run`. If `dbt run` fails midway, the offset does not advance, and the next run will reprocess the same batch of changes — this is the guarantee of "at-least-once" semantics.

---

## Combined Usage: Stream + Dynamic Table

A typical real-time pipeline architecture:

```
Source table (continuously written to)
    ↓ Table Stream (captures changes)
Incremental consumption model (incremental, consumes Stream, advances offset)
    ↓ Dynamic Table (auto-aggregates, refreshes hourly)
Analytics layer (BI queries)
```

Advantages of this architecture:
- Stream guarantees no changes are missed
- Dynamic Table automatically maintains aggregation results without manual scheduling
- The two are decoupled and can have their refresh frequencies adjusted independently

---

## Related Documentation

- [dbt ClickZetta Adapter Usage Guide](eco_integration/dbt.md)
- [DBT Incremental Processing in Practice](dbt-incremental.md)
- [Dynamic Table](dynamic-table.md)
- [Table Stream](table_stream.md)
- [dbt-clickzetta GitHub](https://github.com/clickzetta/dbt-clickzetta)
- [snowflake-dbt2lakehouse-dbt](https://github.com/clickzetta/snowflake-dbt2lakehouse-dbt)
