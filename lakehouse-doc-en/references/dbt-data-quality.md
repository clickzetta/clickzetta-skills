# DBT Data Quality in Practice

> The code in this article comes from [clickzetta/jaffle-shop-clickzetta](https://github.com/clickzetta/jaffle-shop-clickzetta), with **30/30 tests passing** verified in practice (27 data tests + 3 unit tests).

---

## Two Types of Tests

dbt provides two testing mechanisms to address data quality issues at different levels:

| Type | Test Target | How It Runs | Use Cases |
|---|---|---|---|
| **data test** | Actual data | Executes SQL assertions against real tables | Validates completeness, uniqueness, and referential integrity of production data |
| **unit test** | Model logic | Tests SQL transformation logic with mock data | Validates correctness of computation logic without depending on real data |

The fundamental difference: **data tests ask "is the data correct?", unit tests ask "is the logic correct?"**

Data tests depend on real data, so you must first run `dbt run` to build the tables before running them. They can detect problems that arise after the data pipeline runs, such as null values or duplicate keys caused by poor upstream data quality.

Unit tests are completely independent of real data — they test SQL logic using mock data you write by hand. They run during `dbt build` without needing real data first. This means you can validate logic during development rather than waiting until data has been produced to discover problems.

**What to do when a test fails?**

When `dbt test` fails, dbt prints the failing SQL query, which you can run directly in Studio or cz-cli to see exactly which rows violated the constraint. For example, if a `unique` test fails, running the failing SQL shows you which values are duplicated.

The two types are complementary: data tests find data problems, unit tests find logic problems.

---

## Data Test

### Built-in Test Types

dbt has 4 built-in general-purpose tests, declared in `schema.yml`:

```yaml
models:
  - name: orders
    columns:
      - name: order_id
        data_tests:
          - not_null        # must not be null
          - unique          # values must be unique
      - name: customer_id
        data_tests:
          - relationships:  # foreign key referential integrity
              to: ref('stg_customers')
              field: customer_id
      - name: customer_type
        data_tests:
          - accepted_values: # enum value validation
              values: ["new", "returning"]
```

This is the actual test configuration for the `customers` model in [jaffle-shop-clickzetta](https://github.com/clickzetta/jaffle-shop-clickzetta).

### Cross-Column Expression Tests

Built-in tests can only test a single column. Business rules spanning multiple columns require `dbt_utils.expression_is_true`:

```yaml
models:
  - name: orders
    data_tests:
      - dbt_utils.expression_is_true:
          expression: "order_items_subtotal = subtotal"
      - dbt_utils.expression_is_true:
          expression: "order_total = subtotal + tax_paid"
```

These two tests come from the `orders` model in [jaffle-shop-clickzetta](https://github.com/clickzetta/jaffle-shop-clickzetta), validating the order amount calculation logic:
- The sum of all order item subtotals equals the order subtotal
- The order total equals the subtotal plus tax

`dbt_utils` is an extension package officially maintained by dbt. Declare the dependency in `packages.yml` to use it:

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: [">=1.0.0", "<2.0.0"]
```

### Source Tests

Source tests validate data before it enters the dbt pipeline, catching problems earlier:

```yaml
sources:
  - name: ecom
    schema: raw
    tables:
      - name: raw_orders
        loaded_at_field: ordered_at   # used for source freshness checks
        columns:
          - name: id
            data_tests:
              - not_null
              - unique
```

Once `loaded_at_field` specifies a timestamp field, you can use `dbt source freshness` to check data freshness — if the latest data has not been updated beyond a threshold time, it will issue a warning or error.

### Running Tests

```bash
dbt test                          # run all tests
dbt test --select orders          # test only the orders model
dbt test --select source:ecom     # test only the ecom source
dbt test --select test_type:data  # run only data tests
```

**Verified results** (from [jaffle-shop-clickzetta](https://github.com/clickzetta/jaffle-shop-clickzetta)):

```
Done. PASS=27 WARN=0 ERROR=0 SKIP=0 TOTAL=27
```

All 27 data tests passed in approximately 5 seconds.

---

## Unit Test

### What Is a Unit Test

A unit test uses mock data to test the SQL transformation logic of a model, without depending on data in the real database.

Suitable scenarios:
- Validating complex CASE WHEN logic
- Validating aggregation calculations (SUM, COUNT, etc.)
- Validating timestamp handling (truncation, format conversion)
- Testing logic even when no real data is available

### Basic Syntax

Unit tests are declared in `schema.yml` with a `given` (input mock data) + `expect` (expected output) structure:

```yaml
unit_tests:
  - name: test_does_location_opened_at_trunc_to_date
    description: "Validates that opened_at timestamp is correctly truncated to a date"
    model: stg_locations
    given:
      - input: source('ecom', 'raw_stores')
        rows:
          - { id: 1, name: "Vice City",    tax_rate: 0.2, opened_at: "2016-09-01T00:00:00" }
          - { id: 2, name: "San Andreas",  tax_rate: 0.1, opened_at: "2079-10-27T23:59:59.9999" }
    expect:
      rows:
        - { location_id: 1, location_name: "Vice City",   tax_rate: 0.2, opened_date: "2016-09-01" }
        - { location_id: 2, location_name: "San Andreas", tax_rate: 0.1, opened_date: "2079-10-27" }
```

This is the actual unit test for `stg_locations` in [jaffle-shop-clickzetta](https://github.com/clickzetta/jaffle-shop-clickzetta). It validates that the timestamp `"2079-10-27T23:59:59.9999"` should truncate to `"2079-10-27"`, not `"2079-10-28"`. This kind of edge case is hard to cover with real data, but a unit test can construct it precisely.

### Multiple Input Mocks

When a model references multiple upstream models, mock data must be provided for each input:

```yaml
unit_tests:
  - name: test_supply_costs_sum_correctly
    description: "Validates that supply costs are correctly summed by product"
    model: order_items
    given:
      - input: ref('stg_supplies')
        rows:
          - { product_id: 1, supply_cost: 4.50 }
          - { product_id: 2, supply_cost: 3.50 }
          - { product_id: 2, supply_cost: 5.00 }   # product_id=2 has two supply records
      - input: ref('stg_products')
        rows:
          - { product_id: 1 }
          - { product_id: 2 }
      - input: ref('stg_order_items')
        rows:
          - { order_id: 1, product_id: 1 }
          - { order_id: 2, product_id: 2 }
          - { order_id: 2, product_id: 2 }
      - input: ref('stg_orders')
        rows:
          - { order_id: 1 }
          - { order_id: 2 }
    expect:
      rows:
        - { order_id: 1, product_id: 1, supply_cost: 4.50 }
        - { order_id: 2, product_id: 2, supply_cost: 8.50 }  # 3.50 + 5.00
        - { order_id: 2, product_id: 2, supply_cost: 8.50 }
```

This test validates that `product_id=2` has two supply records (3.50 + 5.00), which should sum to 8.50.

### Running Unit Tests

```bash
dbt test --select test_type:unit   # run only unit tests
dbt build                          # unit tests are automatically included during build
```

**Verified results** (from [jaffle-shop-clickzetta](https://github.com/clickzetta/jaffle-shop-clickzetta)):

```
Done. PASS=3 WARN=0 ERROR=0 SKIP=0 TOTAL=3
```

All 3 unit tests passed in approximately 2 seconds.

> ⚠️ **Note**: Requires dbt-clickzetta >= 1.7.5. Earlier versions had a bug with unit test fixture cleanup (DROP TABLE on a VIEW caused an error), which was fixed in 1.7.5.

---

## Complete Test Strategy

Test distribution in [jaffle-shop-clickzetta](https://github.com/clickzetta/jaffle-shop-clickzetta):

| Layer | Test Content | Count |
|---|---|---|
| Source | `not_null`, `unique` (raw table primary keys) | 6 |
| Staging | `not_null`, `unique` (staging view primary keys) + 1 unit test (timestamp truncation) | 8 |
| Marts | `not_null`, `unique`, `relationships`, `accepted_values`, `expression_is_true` + 2 unit tests | 19 |
| **Total** | | **30** |

**Test coverage principles**:
- Every table's primary key must have `not_null` + `unique`
- Foreign keys must have `relationships` tests
- Enum fields use `accepted_values`
- Cross-column business rules use `expression_is_true`
- Complex transformation logic uses unit tests

---

## Related Documentation

- [dbt ClickZetta Adapter Usage Guide](eco_integration/dbt.md)
- [DBT Incremental Processing in Practice](dbt-incremental.md)
- [jaffle-shop-clickzetta](https://github.com/clickzetta/jaffle-shop-clickzetta)
- [dbt-clickzetta GitHub](https://github.com/clickzetta/dbt-clickzetta)
