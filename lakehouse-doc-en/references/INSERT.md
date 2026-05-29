## Description

The `INSERT INTO` statement is used to insert data into a table. You can explicitly specify values for each column in the table, or use the result of a `SELECT` query as the data source for the insertion.

## Syntax

```SQL
INSERT INTO|OVERWRITE [TABLE] table_name 
[ PARTITION partition_spec] 
[ (column1, column2, ...)]
{VALUES(value1 [,...],(value2 [,...]),...) | subquery}

partition_spec ::=
    partition_column_name = partition_column_val [ , ... ]
```

## Parameter Details

1. **INSERT INTO**: Append write mode, does not affect existing data in the table -- the standard way to write data on a daily basis.
2. **INSERT OVERWRITE**: Overwrite write mode, clears the target table (or specified partition) before writing new data -- suitable for full-refresh scenarios, use with caution.
   * For partitioned tables, it will overwrite the data of the specified partition.
   * For non-partitioned tables, it will overwrite the entire table's data.
3. **TABLE**: (Optional) Keyword used to specify the target table.
4. **partition\_spec**: Specifies which partition to write to -- required for partitioned tables, not needed for non-partitioned tables.
   * Static partition: Directly specify the partition column value, e.g., `PARTITION (order_date='2024-01-01')`.
   * Dynamic partition: The system automatically maps the values from the `VALUES` or `SELECT` statement to the corresponding partitions.
   * If no partition specification is provided, the system will automatically select the partition based on the partition column values.
5. **column\_list**: Specifies the columns to insert data into, ensuring that the column order in the input query matches the column order in the table.

## Usage Guide

* **Data Type Matching**: Ensure that the data types being inserted match the column types defined in the table.

* **Query Result Matching**: When using a `SELECT` statement to insert data, the number and order of columns returned by the query should match the columns in the target table.

* **Partition Specification**: When inserting data into a partitioned table, if no partition specification is provided, the system will automatically select the partition based on the values of the partition columns. Ensure that the data being inserted contains valid partition values.

* **INSERT OVERWRITE**: When using this statement to insert data, ensure that the target table or partition exists, otherwise the operation will fail.

* **Data Check**: Before performing the insert operation, check whether the data types and the number of columns match the target table to avoid data insertion errors. **In particular, note that Apache Hive requires partition columns to be in the last position. There is no such mandatory requirement in Lakehouse, so when adding columns, be especially careful: adding columns the Hive way may place them in the last position, so you must specify the position when adding columns. Otherwise, it may cause data errors.**

* **Automatic Partition Handling**: When using a table where partition fields are functions, there is no need to specify the `PARTITION` clause; the system will automatically handle the partition based on the function's return value.

* **Bulk Data Import**: In a lakehouse environment, it is not recommended to use the `INSERT INTO...VALUES` method for bulk data import, as this method is more suitable for testing scenarios. For bulk data import, please refer to the [Data Import Guide](data-load-summary.md).

## Usage Examples

**1. Basic VALUES Insertion**

Append single-row and multi-row data to `doc_test.products`.

```SQL
-- Insert a single row
INSERT INTO doc_test.products VALUES (101, 'Wireless Mouse', 89.90, 200, 'Electronics');

-- Insert multiple rows (single commit)
INSERT INTO doc_test.products VALUES
  (102, 'USB-C Hub',    149.00, 150, 'Electronics'),
  (103, 'Desk Lamp',     59.50, 300, 'Office');

-- Verify
SELECT product_id, name, price, stock FROM doc_test.products WHERE product_id IN (101, 102, 103);
```

```Plain
+------------+----------------+--------+-------+
| product_id | name           | price  | stock |
+------------+----------------+--------+-------+
| 101        | Wireless Mouse |  89.90 |   200 |
| 102        | USB-C Hub      | 149.00 |   150 |
| 103        | Desk Lamp      |  59.50 |   300 |
+------------+----------------+--------+-------+
```

**2. Insert with Specified Column Names (Omitting Some Columns)**

Unspecified columns are filled with NULL (or the default value if the column has one).

```SQL
-- Only specify product_id and name, remaining columns will be NULL
INSERT INTO doc_test.products (product_id, name) VALUES (104, 'Notebook');

-- Verify
SELECT product_id, name, price, stock, category FROM doc_test.products WHERE product_id = 104;
```

```Plain
+------------+----------+-------+-------+----------+
| product_id | name     | price | stock | category |
+------------+----------+-------+-------+----------+
| 104        | Notebook |  NULL |  NULL | NULL     |
+------------+----------+-------+-------+----------+
```

**3. SELECT Insertion (Write Query Results to Another Table)**

Archive high-salary employee information to another backup table with the same structure.

```SQL
-- Write employees with salary greater than 15000 to the archive table
INSERT INTO doc_test.employees_archive
SELECT * FROM doc_test.employees WHERE salary > 15000;

-- Verify: number of rows in the archive table
SELECT COUNT(*) AS archived_count FROM doc_test.employees_archive;
```

```Plain
+----------------+
| archived_count |
+----------------+
|              5 |
+----------------+
```

You can also write only a subset of columns:

```SQL
INSERT INTO doc_test.employees_archive (id, name, dept)
SELECT id, name, dept FROM doc_test.employees WHERE is_active = false;
```

**4. Inserting Data into a Partitioned Table**

`doc_test.orders` is partitioned by `order_date`. Provide the partition column value at the end of VALUES, and the system automatically routes to the corresponding partition.

```SQL
-- Dynamic partition: system automatically selects the partition based on order_date values
INSERT INTO doc_test.orders VALUES
  (5001, 1001, 'Wireless Mouse', 89.90,  'paid',    '2024-03-01'),
  (5002, 1002, 'USB-C Hub',     149.00,  'pending', '2024-03-01'),
  (5003, 1003, 'Desk Lamp',      59.50,  'paid',    '2024-03-02');

-- Static partition: explicitly specify the partition, no need to provide the partition column in VALUES
INSERT INTO doc_test.orders PARTITION (order_date='2024-03-03') (order_id, customer_id, product, amount, status)
VALUES (5004, 1004, 'Notebook', 35.00, 'paid');

-- Verify
SELECT order_id, product, amount, order_date FROM doc_test.orders WHERE order_date IN ('2024-03-01','2024-03-02','2024-03-03');
```

```Plain
+----------+----------------+--------+------------+
| order_id | product        | amount | order_date |
+----------+----------------+--------+------------+
|     5001 | Wireless Mouse |  89.90 | 2024-03-01 |
|     5002 | USB-C Hub      | 149.00 | 2024-03-01 |
|     5003 | Desk Lamp      |  59.50 | 2024-03-02 |
|     5004 | Notebook       |  35.00 | 2024-03-03 |
+----------+----------------+--------+------------+
```

**5. INSERT OVERWRITE (Overwrite Mode)**

Suitable for daily full-refresh scenarios -- clears the target partition first, then writes the latest data for the day. The following example overwrites the `2024-03-01` partition (existing data will be cleared):

```SQL
-- Overwrite a single partition
INSERT OVERWRITE doc_test.orders PARTITION (order_date='2024-03-01') (order_id, customer_id, product, amount, status)
VALUES
  (5001, 1001, 'Wireless Mouse', 99.90, 'paid'),   -- amount updated
  (5005, 1005, 'Keyboard',       199.00, 'paid');   -- new order, row 5002 is cleared

-- Verify: the 2024-03-01 partition now contains only the two newly written rows
SELECT order_id, product, amount FROM doc_test.orders WHERE order_date = '2024-03-01';
```

```Plain
+----------+----------------+--------+
| order_id | product        | amount |
+----------+----------------+--------+
|     5001 | Wireless Mouse |  99.90 |
|     5005 | Keyboard       | 199.00 |
+----------+----------------+--------+
```

Using `INSERT OVERWRITE` on a non-partitioned table clears the entire table before rewriting, suitable for full-refreshing dimension tables:

```SQL
-- Fully replace the products table with the latest dataset
INSERT OVERWRITE doc_test.products
SELECT * FROM doc_test.products_staging;
```

**6. Inserting Different Data Types**

Demonstrates the literal syntax for various built-in types, serving as a type mapping reference.

```SQL
CREATE TABLE doc_test.type_demo(
  `c_bigint` bigint,
  `c_boolean` boolean,
  `c_binary` binary,
  `c_char` char(1),
  `c_date` date,
  `c_decimal` decimal(20,6),
  `c_double` double,
  `c_float` float,
  `c_int` int,
  `c_smallint` smallint,
  `c_string` string,
  `c_timestamp` timestamp,
  `c_tinyint` tinyint,
  `c_array` array<int>,
  `c_map` map<string,string>,
  `c_struct` struct<a:int,b:string,c:double>,
  `c_varchar` varchar(100),
  `c_json` json);
INSERT INTO doc_test.type_demo
VALUES (
    1l, -- c_bigint
    true, -- c_boolean
    X'7A', -- c_binary
    'A', -- c_char
    date'2025-05-21' , -- c_date
    1.1bd, -- c_decimal
    1.1d, -- c_double
    1.1f, -- c_float
    1, -- c_int
    1s, -- c_smallint
    'This is a string', -- c_string
    timestamp'2025-05-21 12:00:00', -- c_timestamp
    127, -- c_tinyint
    ARRAY(1,2,3), -- c_array
    MAP('key1', 'value1', 'key2', 'value2'), -- c_map
    STRUCT(1, 'a', 3.14), -- c_struct
    'This is a varchar string', -- c_varchar
    json'123' -- c_json
);
```
