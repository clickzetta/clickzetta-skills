# Clickzetta Lakehouse Constraint Properties Overview

Clickzetta Lakehouse supports various constraint properties to meet user needs during data writing, updating, and maintenance processes. This document will detail the constraint properties of Clickzetta Lakehouse and demonstrate how to use these properties through examples.

## ANSI SQL Constraint Properties

ANSI SQL constraint properties mainly involve the following aspects:

1. **ENFORCED | NOT ENFORCED**: Specifies whether the constraint is enforced. ENFORCED means the constraint is enforced, NOT ENFORCED means the constraint is not enforced.
2. **DEFERRABLE | NOT DEFERRABLE**: Specifies deferred and non-deferred execution. DEFERRABLE means the constraint can be deferred, NOT DEFERRABLE means the constraint is executed immediately.
3. **INITIALLY { DEFERRED | IMMEDIATE** }: Specifies the timing of the validation. If the constraint property is NOT DEFERRABLE, it can only be INITIALLY IMMEDIATE.

### Usage Example

Suppose we have an orders table `orders` with the following fields:

- `order_id`: Order ID, which is the primary key.
- `customer_id`: Customer ID, which is a foreign key.
- `order_date`: Order date.
- `total_amount`: Total order amount.

We can define the following constraints for the `orders` table:
```sql
CREATE TABLE orders (
  order_id INT PRIMARY KEY ENFORCED,
  customer_id INT REFERENCES customers DEFERRABLE INITIALLY DEFERRED,
  UNIQUE (customer_id, order_date) ENFORCED
);
```
In this example, we specify the ENFORCED attribute for `order_id` to ensure that each order has a unique ID. For `customer_id`, we use the DEFERRABLE and INITIALLY DEFERRED attributes, allowing temporary violation of foreign key constraints when inserting data. Finally, we define a unique constraint for `customer_id` and `order_date` to ensure that each customer can only have one order per day.

## Extended Constraint States

The extended constraint states in Clickzetta Lakehouse are mainly used for primary keys, foreign keys, and unique keys. These constraint states include:

1. **ENABLE | DISABLE**: Specifies whether the constraint is disabled or enabled. ENABLE means the constraint is enabled, DISABLE means the constraint is disabled.
2. **VALIDATE | NOVALIDATE**: Specifies whether to validate the existing data on the table and create an index. VALIDATE means validation and index creation are required, NOVALIDATE means validation and index creation are not required.
3. **RELY | NORELY**: When NOVALIDATE is specified as RELY, the query optimizer will use this attribute to improve query performance.

### Usage Example

Suppose we have a sales record table `sales` with the following fields:

- `sale_id`: Sales record ID, which is the primary key.
- `product_id`: Product ID, which is a foreign key.
- `sale_date`: Sale date.
- `amount`: Sale amount.

We can define the following constraints for the `sales` table:

<Notes>
```sql
CREATE TABLE sales (
  sale_id INT PRIMARY KEY ENABLE VALIDATE RELY,
  product_id INT REFERENCES products DISABLE NOVALIDATE NORELY
);
```
In this example, we specify the ENABLE, VALIDATE, and RELY attributes for `sale_id` to ensure that each sales record has a unique ID and to validate the foreign key constraint when inserting data. For `product_id`, we use the DISABLE, NOVALIDATE, and NORELY attributes, indicating that the foreign key constraint is not validated when inserting data, while the query optimizer can improve query performance.

## Singdata Lakehouse Constraint Attributes

Singdata Lakehouse constraint attributes are ENABLE, VALIDATE, and RELY, enforcing constraint validation. It is important to note that these constraint attributes only support writing using the Java SDK and do not support inserting using SQL.

### Usage Example

Suppose we have a user table `users` with the following fields:

- `user_id`: User ID, which is the primary key.
- `username`: Username.
- `email`: Email address.

We can use the Java SDK to define the following constraints for the `users` table:
```java
Table table = session.getTable("users");
TableSchema schema = table.getSchema();
PrimaryKeyConstraint primaryKeyConstraint = new PrimaryKeyConstraint("user_id");
schema.addConstraint(primaryKeyConstraint);
UniqueConstraint uniqueConstraint = new UniqueConstraint("username");
schema.addConstraint(uniqueConstraint);
session.createTable("users", schema, true);
```
In this example, we use the Java SDK to create a `users` table and define a primary key constraint and a unique constraint for it. These constraints will be enforced to ensure that each user has a unique ID and username. Due to the use of Singdata Lakehouse constraint properties, we cannot insert data through SQL and can only write using the Java SDK.