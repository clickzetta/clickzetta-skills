# Update Table Records

## Description

Update records in a database table, modifying specified field values to new values.

## Syntax

```Plain
UPDATE target_table
       SET column_name1 = new_value1 [ , column_name2 = new_value2 , ... ]
  [ WHERE condition ]
  [ ORDER BY ... ]
  [ LIMIT row_count ]
```

**Required Parameters**

- `target_table`: The target table to update, supports `schema.table` format.
- `SET column = value`: Specifies the column to modify and its new value, supports expressions, functions, and subqueries.

**Optional Parameters**

- `WHERE condition`: Filters the rows to update -- when omitted, all rows in the table are updated. Always verify before execution.
- `ORDER BY` + `LIMIT`: Controls the update order and quantity, suitable for batch-updating large tables to avoid long transactions.

## Usage Examples

### Example 1: Update a Single Column

Increase the price of all products in the Electronics category by 10%.

Before update:

```SQL
SELECT product_id, name, price, category
FROM doc_test.products
WHERE category = 'Electronics'
ORDER BY product_id;
```

```
 product_id | name   | price   | category
------------+--------+---------+-------------
 1          | Laptop | 5999.00 | Electronics
 2          | Phone  | 2999.00 | Electronics
 5          | Tablet | 3499.00 | Electronics
```

Execute update:

```SQL
UPDATE doc_test.products
SET price = price * 1.1
WHERE category = 'Electronics';
```

After update:

```SQL
SELECT product_id, name, price, category
FROM doc_test.products
WHERE category = 'Electronics'
ORDER BY product_id;
```

```
 product_id | name   | price   | category
------------+--------+---------+-------------
 1          | Laptop | 6598.90 | Electronics
 2          | Phone  | 3298.90 | Electronics
 5          | Tablet | 3848.90 | Electronics
```

### Example 2: Update Multiple Columns Simultaneously

Increase the salary of the employee with id 4 by 1000 and change their status to active.

Before update:

```SQL
SELECT id, name, dept, salary, is_active
FROM doc_test.employees
WHERE id = 4;
```

```
 id | name  | dept | salary  | is_active
----+-------+------+---------+-----------
 4  | Diana | HR   | 7500.00 | false
```

Execute update:

```SQL
UPDATE doc_test.employees
SET salary = salary + 1000, is_active = true
WHERE id = 4;
```

After update:

```SQL
SELECT id, name, dept, salary, is_active
FROM doc_test.employees
WHERE id = 4;
```

```
 id | name  | dept | salary  | is_active
----+-------+------+---------+-----------
 4  | Diana | HR   | 8500.00 | true
```

### Example 3: Update Using a Subquery

Mark all orders with `pending` status whose product belongs to the Electronics category as `processing`.

Before update:

```SQL
SELECT order_id, product, amount, status
FROM doc_test.orders
ORDER BY order_id;
```

```
 order_id | product | amount  | status
----------+---------+---------+-----------
 1001     | Laptop  | 5999.00 | completed
 1002     | Phone   | 2999.00 | pending
 1003     | Tablet  | 3499.00 | completed
```

Execute update:

```SQL
UPDATE doc_test.orders
SET status = 'processing'
WHERE status = 'pending'
  AND product IN (
    SELECT name
    FROM doc_test.products
    WHERE category = 'Electronics'
  );
```

After update:

```SQL
SELECT order_id, product, amount, status
FROM doc_test.orders
ORDER BY order_id;
```

```
 order_id | product | amount  | status
----------+---------+---------+------------
 1001     | Laptop  | 5999.00 | completed
 1002     | Phone   | 2999.00 | processing
 1003     | Tablet  | 3499.00 | completed
```

### Example 4: ORDER BY + LIMIT for Batch Updates

Deduct 10 units of stock from the 2 cheapest products, simulating batch processing.

Before update:

```SQL
SELECT product_id, name, price, stock
FROM doc_test.products
ORDER BY price;
```

```
 product_id | name   | price   | stock
------------+--------+---------+-------
 4          | Chair  | 499.00  | 80
 3          | Desk   | 899.00  | 30
 2          | Phone  | 2999.00 | 120
 5          | Tablet | 3499.00 | 60
 1          | Laptop | 5999.00 | 50
```

Execute update:

```SQL
UPDATE doc_test.products
SET stock = stock - 10
ORDER BY price
LIMIT 2;
```

After update:

```SQL
SELECT product_id, name, price, stock
FROM doc_test.products
ORDER BY price;
```

```
 product_id | name   | price   | stock
------------+--------+---------+-------
 4          | Chair  | 499.00  | 70
 3          | Desk   | 899.00  | 20
 2          | Phone  | 2999.00 | 120
 5          | Tablet | 3499.00 | 60
 1          | Laptop | 5999.00 | 50
```

## Notes

- Omitting `WHERE` will update all rows in the entire table. It is recommended to first verify the condition using `SELECT` before executing `UPDATE`.
- Using `ORDER BY` together with `LIMIT` controls the number of rows updated per batch, suitable for batch processing of large tables to avoid long transactions.
- Before executing updates in a production environment, it is recommended to first verify the SQL logic in a test environment.
