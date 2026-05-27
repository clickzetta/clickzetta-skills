## Description

`SHOW COLUMNS` is a SQL command used to view column information in a table. With this command, users can quickly obtain the column names and data types of a table.

## Syntax

```sql
SHOW COLUMNS
[ IN | FROM ]                 -- Use the IN or FROM keyword
[<schema_name>.]<table_name>  -- Table name with optional Schema prefix
[IN <schema_name>]            -- Separated Schema and table name
```

## Parameter Details

### Core Parameters

| Parameter Format | Required | Description |
|------------------|----------|-------------|
| `<table_name>` | Required | The name of the target table |
| `<schema_name>` | Optional | Schema name, supported in two forms:<br>1. As a table name prefix: `schema.table`<br>2. Via the `IN` clause |

## Usage Guidelines

### Schema Specification Methods (choose one)

```sql
-- Method 1: Schema and table name combined
SHOW COLUMNS IN sales.orders;

-- Method 2: Schema and table name separated
SHOW COLUMNS FROM orders IN sales;
```

### Invalid Usage Examples

```sql
-- Error! Schema specified twice
SHOW COLUMNS IN sales.orders IN sales;

-- Error! Mixing the two syntax forms
SHOW COLUMNS FROM sales.orders IN production;
```

## Usage Examples

View column information of a table in the current schema:

```sql
SHOW COLUMNS IN household_demographics;
+-------------+------------------------+-------------------+-----------+---------+
| schema_name |       table_name       |    column_name    | data_type | comment |
+-------------+------------------------+-------------------+-----------+---------+
| tpcds_10tb  | household_demographics | hd_demo_sk        | int       |         |
| tpcds_10tb  | household_demographics | hd_income_band_sk | int       |         |
| tpcds_10tb  | household_demographics | hd_buy_potential  | string    |         |
| tpcds_10tb  | household_demographics | hd_dep_count      | int       |         |
| tpcds_10tb  | household_demographics | hd_vehicle_count  | int       |         |
+-------------+------------------------+-------------------+-----------+---------+
```

## FAQ

Q1: How to view detailed information about a table (such as table structure)?

* Use the `DESCRIBE` or `SHOW CREATE TABLE` command:
  ```sql
  DESCRIBE public.household_demographics;
  SHOW CREATE TABLE public.household_demographics;
  ```

Q2: Does `SHOW COLUMNS` support filtering conditions?

* Direct filtering is not supported, but can be achieved by querying `INFORMATION_SCHEMA.COLUMNS`:
  ```sql
  SELECT * FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_NAME = 'household_demographics' AND COLUMN_NAME LIKE 'name%';
  ```
