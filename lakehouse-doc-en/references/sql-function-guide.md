# SQL User-Defined Function Guide

SQL user-defined functions (SQL UDFs) let you encapsulate reusable computation logic in SQL expressions and call them just like built-in functions inside queries.

## Choosing the Right Type

| Type | Best for | Limitations |
|------|---------|-------------|
| **SQL function** (this guide) | Pure SQL logic: data cleansing, calculation formulas, conditional branching | SQL expressions only — cannot call external services |
| **External function** | Calling Python/Java code, external APIs, or ML models | Requires deploying an external service |
| **Built-in function** | Standard math, string, and date operations | Not customizable |

**When to use a SQL function**:
- The same computation logic appears repeatedly across multiple queries
- Business rules need to be maintained in one place (e.g., discount calculations, classification rules)
- You need to encapsulate complex CASE WHEN logic or multi-step calculations

## SQL Commands Involved

| Command | Purpose |
|---------|---------|
| `CREATE FUNCTION` | Create a scalar or table function |
| `CREATE OR REPLACE FUNCTION` | Update an existing function definition |
| `DROP FUNCTION` | Delete a function |
| `DESC FUNCTION` | View a function definition |
| `SHOW EXTERNAL FUNCTIONS` | List user-defined functions in the current SCHEMA |

---

## Prerequisites

```SQL
CREATE TABLE doc_orders (
    order_id   INT,
    order_date DATE,
    amount     DOUBLE,
    category   STRING
);

INSERT INTO doc_orders VALUES
    (1, DATE '2024-01-01', 99.9,  'electronics'),
    (2, DATE '2024-01-03', 299.0, 'clothing'),
    (3, DATE '2024-01-03', 49.5,  'food'),
    (4, DATE '2024-01-05', 199.0, 'electronics'),
    (5, DATE '2024-01-05', 0.0,   'food');
```

---

## Scenario 1: Scalar Function — Encapsulating a Calculation Formula

**Goal**: Centrally manage discount calculation logic so it stays consistent wherever it is called.

```SQL
-- Create a discount price function; rate defaults to 0.9 (10% off)
CREATE OR REPLACE FUNCTION public.discount_price(price DOUBLE, rate DOUBLE DEFAULT 0.9)
RETURNS DOUBLE
RETURN ROUND(price * rate, 2);
```

```SQL
-- Use the default discount (10% off)
SELECT public.discount_price(100.0);
-- 90.0

-- Specify a discount (20% off)
SELECT public.discount_price(100.0, 0.8);
-- 80.0

-- Use inside a query
SELECT order_id, amount, public.discount_price(amount) AS discounted
FROM doc_orders
WHERE category = 'electronics';
```

| order_id | amount | discounted |
|---------|--------|-----------|
| 1 | 99.9 | 89.91 |
| 4 | 199.0 | 179.1 |

---

## Scenario 2: Scalar Function — Encapsulating Classification Rules

**Goal**: Tier orders by amount with rules maintained in one place.

```SQL
CREATE OR REPLACE FUNCTION public.order_tier(amount DOUBLE)
RETURNS STRING
RETURN CASE
    WHEN amount >= 200  THEN 'Premium'
    WHEN amount >= 50   THEN 'Standard'
    WHEN amount > 0     THEN 'Basic'
    ELSE                     'Free'
END;
```

```SQL
SELECT order_id, amount, public.order_tier(amount) AS tier
FROM doc_orders
ORDER BY amount DESC;
```

| order_id | amount | tier |
|---------|--------|------|
| 2 | 299.0 | Premium |
| 4 | 199.0 | Standard |
| 1 | 99.9 | Standard |
| 3 | 49.5 | Basic |
| 5 | 0.0 | Free |

---

## Scenario 3: Scalar Function — Data Cleansing

**Goal**: Clean phone numbers by stripping non-numeric characters.

```SQL
CREATE OR REPLACE FUNCTION public.clean_phone(phone STRING)
RETURNS STRING
RETURN REGEXP_REPLACE(TRIM(phone), '[^0-9]', '');
```

```SQL
SELECT public.clean_phone('  138-1234-5678 ');
-- 13812345678

SELECT public.clean_phone('+86 (010) 8888-9999');
-- 8601088889999
```

---

## Scenario 4: Table Function — Returning Multiple Rows

A table function returns a virtual table and can be used in a `FROM` clause just like a regular table.

**Goal**: Generate a consecutive date sequence to populate a calendar dimension.

```SQL
CREATE OR REPLACE FUNCTION public.date_range(start_date DATE, end_date DATE)
RETURNS TABLE (dt DATE)
RETURN
    SELECT DATE_ADD(start_date, pos) AS dt
    FROM (SELECT POSEXPLODE(SPLIT(SPACE(DATEDIFF(end_date, start_date)), ' '))) t(pos, v);
```

```SQL
-- Direct call
SELECT * FROM public.date_range(DATE '2024-01-01', DATE '2024-01-05');
```

| dt |
|----|
| 2024-01-01 |
| 2024-01-02 |
| 2024-01-03 |
| 2024-01-04 |
| 2024-01-05 |

```SQL
-- LEFT JOIN with the orders table to find dates with no orders
SELECT d.dt, COALESCE(SUM(o.amount), 0) AS daily_revenue
FROM public.date_range(DATE '2024-01-01', DATE '2024-01-05') d
LEFT JOIN doc_orders o ON o.order_date = d.dt
GROUP BY d.dt
ORDER BY d.dt;
```

| dt | daily_revenue |
|----|--------------|
| 2024-01-01 | 99.9 |
| 2024-01-02 | 0 |
| 2024-01-03 | 348.5 |
| 2024-01-04 | 0 |
| 2024-01-05 | 199 |

---

## Function Management

### View a Function Definition

```SQL
DESC FUNCTION public.order_tier;
```

Returns the function name, creation time, full SQL definition, and more.

### Update a Function

Use `CREATE OR REPLACE FUNCTION` to overwrite in place — no need to drop first:

```SQL
CREATE OR REPLACE FUNCTION public.order_tier(amount DOUBLE)
RETURNS STRING
RETURN CASE
    WHEN amount >= 300  THEN 'VIP'      -- new VIP tier
    WHEN amount >= 200  THEN 'Premium'
    WHEN amount >= 50   THEN 'Standard'
    WHEN amount > 0     THEN 'Basic'
    ELSE                     'Free'
END;
```

> ⚠️ **Note**: `CREATE OR REPLACE` must be executed on its own. You cannot immediately follow it with a SELECT in the same statement to verify the new definition — the SELECT in the same statement still uses the old version (bound at compile time). Run the SELECT separately after the update to see the new result.

### Delete a Function

```SQL
DROP FUNCTION IF EXISTS public.order_tier;
```

---

## Notes

- **Schema prefix is required**: You must write `schema_name.function_name` when calling a function, otherwise you will get a "function not found" error. You can change the resolution policy with `SET cz.sql.remote.udf.lookup.policy = builtin_first` — see [SET (session parameters)](set-command.md).
- **Default parameters must come last**: Parameters with default values must be placed after parameters without default values.
- **Table functions must use a query**: The body of a `RETURNS TABLE` function must be a `SELECT` statement, not an expression.
- **DML is not supported in function bodies**: SQL functions cannot execute INSERT/UPDATE/DELETE.
- **Recursion is not supported**: A function body cannot call itself — doing so results in a "function not found" error.
- **Calling other user-defined functions**: A function body can call other SQL functions in the same SCHEMA; use the SCHEMA prefix.
- **Name collision with built-in functions**: Call your custom function with the SCHEMA prefix; call the built-in function without a prefix. The two do not interfere with each other.
- **NULL input**: A NULL argument participates in CASE WHEN evaluation. `NULL >= 200` is false, so the ELSE branch is taken.
- **`OR REPLACE` and `IF NOT EXISTS` cannot be used together**: Combining them causes a syntax error.

## Related Documentation

- [CREATE SQL FUNCTION](create-sql-function.md)
- [DROP FUNCTION](drop-function.md)
- [DESC FUNCTION](desc-function.md)
- [Developing External Functions](RemoteFunction-as-udf.md)
- [SET (session parameters)](set-command.md)
