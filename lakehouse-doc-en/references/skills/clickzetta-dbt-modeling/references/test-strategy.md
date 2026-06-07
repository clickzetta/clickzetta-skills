# Test Strategy Guide

## Four Built-in Tests

When generating each model, decide which tests to add using the following rules:

| Test | Where to Add | Reason |
|---|---|---|
| `not_null` | All primary keys + core business columns | Null values cause JOINs to fail and aggregation results to be understated |
| `unique` | All primary key columns | Duplicate primary keys cause downstream JOINs to produce a Cartesian product |
| `relationships` | Foreign key columns in fact tables | Ensures referential integrity and prevents orphan records from polluting aggregations |
| `accepted_values` | Enum columns (status/type/region etc.) | Catches upstream data quality issues and prevents invalid values from entering marts |

## Standard schema.yml Template

```yaml
models:
  - name: fct_orders
    columns:
      - name: order_id
        data_tests:
          - not_null
          - unique
      - name: customer_id
        data_tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id
      - name: status
        data_tests:
          - not_null
          - accepted_values:
              values: ['pending', 'completed', 'cancelled']
      - name: amount
        data_tests:
          - not_null
```

## Custom Singular Tests (tests/ directory)

For business rules that cannot be expressed with built-in tests, write SQL files in the `tests/` directory. Returning 0 rows means the test passes:

```sql
-- tests/assert_revenue_positive.sql
-- Verify that completed orders must have a positive amount
select order_id, amount
from {{ ref('fct_orders') }}
where status = 'completed'
  and amount <= 0
```

```sql
-- tests/assert_incremental_no_duplicates.sql
-- Verify that the incremental model has no duplicate primary keys (check after re-run)
select order_id, count(*) as n
from {{ ref('fct_orders_incremental') }}
group by order_id
having count(*) > 1
```

```sql
-- tests/assert_snapshot_no_overlap.sql
-- Verify that snapshot validity intervals do not overlap (SCD Type 2 integrity)
select a.customer_id
from {{ ref('customers_snapshot') }} a
join {{ ref('customers_snapshot') }} b
  on a.customer_id = b.customer_id
 and a.dbt_scd_id != b.dbt_scd_id
 and a.dbt_valid_from < b.dbt_valid_to
 and b.dbt_valid_from < a.dbt_valid_to
where b.dbt_valid_to is not null
```

## Minimum Test Coverage Standards

- staging layer: add `not_null` + `unique` on the primary key of every table
- marts layer: full coverage of primary keys + foreign keys + enum columns
- snapshot: add `assert_snapshot_no_overlap` singular test
- incremental: add `assert_incremental_no_duplicates` singular test
