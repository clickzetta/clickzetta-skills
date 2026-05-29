# Semantic View (Semantic View)

## Overview

A semantic view is an architecture-level logical data model object in the Singdata Lakehouse, designed to bridge the gap between how business users describe data and how data is actually stored in the data platform.

Without semantic views, different reports and applications may use inconsistent calculation methods, leading to divergent results. Semantic views serve as a business-oriented abstraction layer that addresses the following common issues:

* **For data analysis**: Semantic views provide unified definitions of metrics and dimensions, enabling business users to query cross-table data without writing complex JOIN statements, significantly lowering the SQL complexity barrier.
* **For data governance**: Semantic views centrally manage table relationships, dimension and metric definitions in a declarative manner, ensuring that all stakeholders across the organization -- from data analysts to business users -- operate on the same data definitions.

***

## Concepts in Semantic Views

A semantic view consists of the following core components:

**Logical Tables (TABLES)**: In a semantic view, the logical tables you define typically correspond to business entities such as customers, orders, or line items. Each logical table maps to a physical table, and relationships between tables are declared through primary keys and foreign keys. You can define join relationships between logical tables via foreign keys, enabling cross-entity data analysis -- just like joining physical tables in a database, but without having to manually write JOINs in queries.

**Dimensions (DIMENSIONS)**: Dimensions are categorical attributes that provide contextual meaning to metrics. They answer questions like "who," "what," "where," and "when" by grouping data into meaningful categories, such as order date, customer name, or order year.

**Metrics (METRICS)**: Metrics are quantitative business measures derived from aggregating columns using functions such as `SUM`, `AVG`, `COUNT`. They transform raw data into meaningful business indicators, such as "total number of customers" or "average order value." Metrics represent the KPIs that drive business decisions in reports and dashboards.

**Filters (FILTERS)**: Filters are predefined, reusable filtering conditions that encapsulate commonly used business filtering logic within a semantic view.

***

## Creating a Semantic View

### Syntax

```sql
CREATE SEMANTIC VIEW <view_name>
TABLES (
    <logical_table_definition> [ , ... ]
)
[ FILTERS (
    <filter_definition> [ , ... ]
) ]
DIMENSIONS (
    <dimension_definition> [ , ... ]
)
METRICS (
    <metric_definition> [ , ... ]
)
[ COMMENT = '<view_description>' ]
;
```

The definition syntax for each clause is as follows:

#### Logical Table Definition

```sql
<table_alias> AS <schema_name>.<physical_table_name>
    PRIMARY KEY ( <column_name> [ , ... ] )
    [ FOREIGN KEY ( <column_name> ) REFERENCES <other_logical_table_alias> [ ( <referenced_column_name> ) ] ]
    [ WITH SYNONYMS ( '<synonym>' [ , ... ] ) ]
    [ COMMENT = '<description>' ]
```

#### Filter Definition

```sql
<logical_table_alias>.<filter_name> AS <boolean_expression>
```

#### Dimension Definition

```sql
{ <logical_table_alias>.<dimension_name> | <dimension_name> } AS <expression>
    [ WITH SYNONYMS = ( '<synonym>' [ , ... ] ) ]
    [ is_unique = { true | false } ]
    [ is_time = { true | false } ]
    [ enum_values = [ <value1>, <value2>, ... ] ]
    [ COMMENT = '<description>' ]
```

#### Metric Definition

```sql
<logical_table_alias>.<metric_name> AS <aggregate_expression>
    [ COMMENT = '<description>' ]
```

### Parameter Description

**Logical Table Definition Parameters**:

| Parameter                                                  | Description                                                                                                                                |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `<table_alias> AS <schema_name>.<physical_table_name>`     | Assigns a logical alias to a physical table. This alias is used in subsequent foreign key references, dimension, and metric definitions. |
| `PRIMARY KEY ( <column_name> [ , ... ] )`                  | Specifies one or more columns as the primary key of the logical table. Primary keys help determine the relationship type (one-to-many or one-to-one) between tables. |
| `FOREIGN KEY ( <column_name> ) REFERENCES <other_logical_table_alias> [ ( <referenced_column_name> ) ]` | Defines a foreign key relationship between the current logical table and another logical table. The reference target must use the logical table alias (not the physical table name). When the foreign key column name differs from the primary key column name of the referenced table, you must explicitly specify the referenced column name, e.g., `FOREIGN KEY (dept) REFERENCES depts (dept_name)`. **The data types of the foreign key column and the referenced column must be identical**, otherwise an error will occur at creation time. The semantic view engine automatically handles table joins based on this foreign key relationship at query time. |
| `WITH SYNONYMS ( '<synonym>' )`                            | Defines synonyms for the logical table to enhance discoverability.                                                                      |
| `COMMENT = '<description>'`                                | Adds a descriptive comment to the logical table.                                                                                         |

**Dimension Definition Parameters**:

| Parameter                                    | Description                                                                                                                   |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `is_unique`                                  | Indicates whether the values of this dimension are unique. When set to `true`, it means this dimension column contains no duplicate values, such as customer names. |
| `is_time`                                    | Indicates whether this dimension is a time type. When set to `true`, it means this dimension represents a temporal attribute, such as order date. |
| `enum_values`                                | Defines a list of allowed enumerated values for this dimension. This helps constrain the value range and improve query accuracy. |
| `WITH SYNONYMS = ( '<synonym1>', '<synonym2>' )` | Defines one or more synonyms for the dimension, allowing users to reference the same dimension using different business terms. |

**Metric Aggregation Functions**: `COUNT`, `AVG`, `SUM`, `MIN`, `MAX`

### Usage Notes

* The `TABLES` clause is required and cannot be omitted. The `DIMENSIONS` and `METRICS` clauses are both optional, but at least one should be defined in practice to be meaningful.
* In the `TABLES` clause, a logical table referenced by a foreign key must be defined before the table that references it. For example, if the `orders` table's foreign key references the `customers` table, the `customers` definition must appear before `orders`.
* If the target semantic view already exists, `CREATE SEMANTIC VIEW` will raise an error. It is recommended to use `DROP SEMANTIC VIEW IF EXISTS` first to ensure script idempotency (repeatable execution).
* Dimensions and metrics support two naming styles: **qualified names** (`<logical_table_alias>.<name>`, e.g., `orders.order_date`) and **short names** (using the name directly, e.g., `order_date`). When a dimension or metric name is unique within the semantic view, short names can be used; if naming conflicts exist, qualified names must be used.
* Dimensions support expressions as definitions, known as **computed dimensions**. For example, `YEAR(o_orderdate)` can extract the year from an order date and serve as a standalone dimension.

### Examples

The following example creates a semantic view named `tpch_rev_analysis` using the TPC-H dataset for revenue analysis scenarios. The dataset contains tables such as customers, orders, and line items, representing a simplified business scenario.

This semantic view defines:

* Three logical tables (`orders`, `customers`, and `line_items`), mapped to the orders, customers, and line items tables in TPC-H respectively.
* A foreign key relationship between `orders` and `customers` (via `o_custkey`).
* A foreign key relationship between `line_items` and `orders` (via `l_orderkey`).
* Dimensions for grouping and filtering: customer name, order date, and order year.
* Quantitative business metrics: total customer count and average order value.

#### Basic Semantic View

```sql
DROP SEMANTIC VIEW IF EXISTS tpch_rev_analysis;
CREATE SEMANTIC VIEW tpch_rev_analysis
TABLES (
    customers AS TPCH_SF1.CUSTOMER
        PRIMARY KEY (c_custkey)
        COMMENT = 'Main table for customer data',
    orders AS TPCH_SF1.ORDERS
        PRIMARY KEY (o_orderkey)
        FOREIGN KEY (o_custkey) REFERENCES customers
        WITH SYNONYMS ('sales orders')
        COMMENT = 'All orders table for the sales domain',
    line_items AS TPCH_SF1.LINEITEM
        PRIMARY KEY (l_orderkey, l_linenumber)
        FOREIGN KEY (l_orderkey) REFERENCES orders
        COMMENT = 'Line items in orders'
)
DIMENSIONS (
    customers.customer_name AS customers.c_name
        WITH SYNONYMS = ('customer name')
        COMMENT = 'Name of the customer',
    orders.order_date AS o_orderdate
        COMMENT = 'Date when the order was placed',
    orders.order_year AS YEAR(o_orderdate)
        COMMENT = 'Year when the order was placed'
)
METRICS (
    customers.customer_count AS COUNT(c_custkey)
        COMMENT = 'Count of number of customers',
    orders.order_average_value AS AVG(orders.o_totalprice)
        COMMENT = 'Average order value across all orders'
)
COMMENT = 'Semantic view for revenue analysis';
```

In the example above, the `TABLES` clause defines three logical tables: an `orders` table containing TPC-H order information, a `customers` table containing customer information, and a `line_items` table containing line item details. Each logical table identifies its primary key column(s) via the `PRIMARY KEY` clause and declares associations with other logical tables via the `FOREIGN KEY ... REFERENCES` clause. Synonyms and comments make logical tables easier to discover and understand.

The `DIMENSIONS` clause defines three dimensions: `customer_name` directly maps to the `c_name` column of the customers table; `order_date` maps to the order date column; `order_year` is a computed dimension that extracts the year from the order date using the `YEAR()` function.

The `METRICS` clause defines two metrics: `customer_count` uses the `COUNT` aggregate function to count the number of customers; `order_average_value` uses the `AVG` aggregate function to compute the average order value.

#### Semantic View with Filters and Dimension Metadata

The following example extends the basic version with filters, dimension uniqueness identification, time type identification, and enumerated value constraints, demonstrating the advanced capabilities of semantic views:

```sql
DROP SEMANTIC VIEW IF EXISTS tpch_rev_analysis;
CREATE SEMANTIC VIEW tpch_rev_analysis
TABLES (
    customers AS TPCH_AI.CUSTOMER
        PRIMARY KEY (c_custkey)
        COMMENT = 'Main table for customer data',
    orders AS TPCH_AI.ORDERS
        PRIMARY KEY (o_orderkey)
        FOREIGN KEY (o_custkey) REFERENCES customers
        WITH SYNONYMS ('orders_synonyms')
        COMMENT = 'All orders table for the sales domain',
    line_items AS TPCH_AI.LINEITEM
        PRIMARY KEY (l_orderkey, l_linenumber)
        FOREIGN KEY (l_orderkey) REFERENCES orders
        COMMENT = 'Line items in orders'
)
FILTERS (
    customers.is_ny AS customers.c_city = 'New York'
)
DIMENSIONS (
    customers.customer_name AS customers.c_name
        WITH SYNONYMS = ('customer name', 'dimensions_synonyms')
        is_unique = true
        COMMENT = 'Name of the customer',
    orders.order_date AS o_orderdate
        is_time = true
        enum_values = [date'2025-01-01', date'2025-06-01', date'2025-12-01']
        COMMENT = 'Date when the order was placed',
    orders.order_year AS YEAR(o_orderdate)
        COMMENT = 'Year when the order was placed'
)
METRICS (
    customers.customer_count AS COUNT(c_custkey)
        COMMENT = 'Count of number of customers',
    orders.order_average_value AS AVG(orders.o_totalprice)
        COMMENT = 'Average order value across all orders'
)
COMMENT = 'Semantic view for revenue analysis';
```

In this example, the `FILTERS` clause defines a filter named `is_ny` for filtering customer records whose city is "New York." This filter encapsulates a reusable business filtering condition, avoiding the need to repeat the same `WHERE` clause across multiple queries.

The `customer_name` dimension has `is_unique = true`, indicating that customer names are unique in the dataset. The `order_date` dimension has `is_time = true`, indicating that this field is a temporal attribute, and uses `enum_values` to constrain the allowed values for this dimension to three specific dates.

> ⚠️ **Note**: Named filters defined in the `FILTERS` clause (such as `is_ny`) are semantic annotations for the AI/metadata layer and cannot be passed directly as parameters to the `semantic_view()` function. To apply filtering conditions in queries, define the corresponding column as a `DIMENSION` and use an outer `WHERE` clause for filtering.

***

## Querying Semantic Views

### Syntax

Use the `semantic_view()` table function in a `SELECT` statement to query a semantic view:

```sql
SELECT *
FROM semantic_view(
    <view_name>,
    DIMENSIONS <dimension_name> [ , DIMENSIONS <dimension_name> ... ],
    METRICS <metric_name> [ , METRICS <metric_name> ... ]
);
```

In queries, you can reference dimensions and metrics using either qualified names (`<logical_table_alias>.<name>`) or short names (the name directly). When the name is unique within the semantic view, both methods are equivalent and return the same results.

### Usage Notes

* Query results are automatically grouped by the specified dimensions, and metric values are computed based on the aggregate functions in the metric definitions. The semantic view engine automatically handles the required table joins based on the foreign key relationships defined in the `TABLES` clause -- users do not need to manually write JOIN logic.
* Dimensions appear in the results in the same order as they are specified in the query.
* The `semantic_view()` function must specify at least one `DIMENSIONS` or `METRICS` parameter, otherwise an error will occur.
* You can pass only `DIMENSIONS` without `METRICS` to return a deduplicated list of dimension values; or pass only `METRICS` without `DIMENSIONS` to return a globally aggregated result (one row).
* Query results support `WHERE`, `ORDER BY`, and `LIMIT` clauses, and also support `SELECT col1, col2 FROM semantic_view(...)` to select specific columns.

### Examples

#### Querying Single Dimension and Single Metric Using Qualified Names

The following query returns the average order value grouped by order date:

```sql
SELECT * FROM semantic_view(
    tpch_rev_analysis,
    DIMENSIONS orders.order_date,
    METRICS orders.order_average_value
);
```

Sample output:

```
2021-01-01    125.000000
```

#### Querying with Multiple Dimensions Using Qualified Names

The following query groups by both order date and customer name, returning the average order value:

```sql
SELECT * FROM semantic_view(
    tpch_rev_analysis,
    DIMENSIONS orders.order_date,
    DIMENSIONS customers.customer_name,
    METRICS orders.order_average_value
);
```

Sample output:

```
2021-01-01    Join    125.000000
```

#### Querying with Short Names

When dimension and metric names are unique within the semantic view, you can omit the logical table alias prefix and use short names directly. The following query is equivalent to the previous example:

```sql
SELECT * FROM semantic_view(
    tpch_rev_analysis,
    DIMENSIONS order_date,
    DIMENSIONS customer_name,
    METRICS order_average_value
);
```

#### Filtering Data with WHERE Clause

After defining the column to be filtered as a dimension, you can apply data filtering through an outer `WHERE` clause (corresponding to named conditions in `FILTERS`):

```sql
SELECT * FROM semantic_view(
    tpch_rev_analysis,
    DIMENSIONS customers.customer_city,
    DIMENSIONS customers.customer_name,
    METRICS orders.order_average_value
) WHERE customer_city = 'New York';
```

### Comparison with Traditional SQL Queries

To illustrate how semantic views simplify queries, the following comparison shows the same analytical requirement implemented using traditional SQL versus a semantic view.

**Traditional SQL Query**:

Using the traditional approach, you need to manually write JOIN logic, specify join conditions, and explicitly declare a GROUP BY clause:

```sql
SELECT
    o.o_orderdate,
    c.c_name,
    AVG(o.o_totalprice) AS avg_value
FROM TPCH_SF1.ORDERS o
JOIN TPCH_SF1.CUSTOMER c ON o.o_custkey = c.c_custkey
GROUP BY o.o_orderdate, c.c_name;
```

**Semantic View Query**:

With a semantic view, you only need to specify the desired dimensions and metrics. The semantic view engine automatically handles joins and aggregation based on predefined table relationships:

```sql
SELECT * FROM semantic_view(
    tpch_rev_analysis,
    DIMENSIONS order_date,
    DIMENSIONS customer_name,
    METRICS order_average_value
);
```

Advantages of semantic view queries:

* **No need to write JOIN logic**: Table joins are automatically performed by the semantic view engine based on foreign key definitions.
* **Business terminology**: Uses terms like `customer_name`, `order_average_value` instead of physical column names, improving readability.
* **Dramatically simplified query syntax**: Lowers the barrier for non-technical users.
* **Centrally managed metric definitions**: Ensures consistency in metric calculations across the entire organization.

***

## Complete Example: Employee Department Analysis

The following example uses the `employees` and `departments` tables in the `doc_test` schema to demonstrate the complete workflow from creating to querying a semantic view.

### Prepare Data

```sql
-- employees(id, name, dept, salary, hire_date, is_active)
-- departments(dept_id, dept_name, manager)
-- The dept column (string) matches departments.dept_name (string) type, usable as a foreign key join
```

### Create the Semantic View

```sql
DROP SEMANTIC VIEW IF EXISTS doc_test.emp_dept_analysis;
CREATE SEMANTIC VIEW doc_test.emp_dept_analysis
TABLES (
    depts AS doc_test.departments
        PRIMARY KEY (dept_name),
    emps AS doc_test.employees
        PRIMARY KEY (id)
        FOREIGN KEY (dept) REFERENCES depts (dept_name)
)
DIMENSIONS (
    emps.employee_name AS emps.name
        WITH SYNONYMS = ('employee name', 'staff name')
        is_unique = true
        COMMENT = 'Employee name',
    emps.department AS emps.dept
        COMMENT = 'Department',
    emps.hire_year AS YEAR(emps.hire_date)
        is_time = true
        COMMENT = 'Year of hire',
    depts.manager_name AS depts.manager
        COMMENT = 'Department manager'
)
METRICS (
    emps.total_employees AS COUNT(emps.id)
        COMMENT = 'Total number of employees',
    emps.avg_salary AS AVG(emps.salary)
        COMMENT = 'Average salary',
    emps.max_salary AS MAX(emps.salary)
        COMMENT = 'Maximum salary'
)
COMMENT = 'Employee department analysis semantic view';
```

### Query Examples

**Count employees and average salary by department:**

```sql
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS emps.department,
    METRICS emps.total_employees,
    METRICS emps.avg_salary
);
```

```
+-------------+-----------------+----------------+
| department  | total_employees |   avg_salary   |
+-------------+-----------------+----------------+
| Engineering |        2        | 11500.000000   |
| Marketing   |        2        |  8750.000000   |
| HR          |        1        |  7500.000000   |
+-------------+-----------------+----------------+
```

**Cross-table dimension: group by department manager name** (auto JOIN, no manual SQL needed):

```sql
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS depts.manager_name,
    METRICS emps.total_employees,
    METRICS emps.avg_salary
);
```

```
+--------------+-----------------+--------------+
| manager_name | total_employees |  avg_salary  |
+--------------+-----------------+--------------+
| Frank        |        2        | 11500.000000 |
| Henry        |        1        |  7500.000000 |
| Grace        |        2        |  8750.000000 |
+--------------+-----------------+--------------+
```

**With WHERE filter:**

```sql
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS emps.department,
    METRICS emps.avg_salary
) WHERE department = 'Engineering';
```

```
+-------------+--------------+
| department  |  avg_salary  |
+-------------+--------------+
| Engineering | 11500.000000 |
+-------------+--------------+
```

**METRICS only — returns global aggregation:**

```sql
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    METRICS emps.total_employees,
    METRICS emps.avg_salary
);
```

```
+-----------------+--------------+
| total_employees |  avg_salary  |
+-----------------+--------------+
|        5        | 9600.000000  |
+-----------------+--------------+
```

**Computed dimension (YEAR expression):**

```sql
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS emps.hire_year,
    METRICS emps.total_employees
) ORDER BY hire_year;
```

```
+-----------+-----------------+
| hire_year | total_employees |
+-----------+-----------------+
|   2019    |        1        |
|   2020    |        1        |
|   2021    |        1        |
|   2022    |        1        |
|   2023    |        1        |
+-----------+-----------------+
```

***

### DROP SEMANTIC VIEW

Deletes a specified semantic view. The `IF EXISTS` clause prevents errors when the view does not exist.

**Syntax:**

```sql
DROP SEMANTIC VIEW [ IF EXISTS ] <view_name>;
```

**Example:**

```sql
DROP SEMANTIC VIEW IF EXISTS tpch_rev_analysis;
```

### ALTER SEMANTIC VIEW

Currently only rename operations are supported. **Dynamically adding/removing dimensions, metrics, or modifying comments via SQL is not supported** — to modify the view structure, you must `DROP` and recreate it.

**Syntax:**

```sql
ALTER SEMANTIC VIEW <view_name> RENAME TO <new_name>;
```

**Example:**

```sql
ALTER SEMANTIC VIEW emp_dept_analysis RENAME TO emp_dept_v2;
```

### SHOW SEMANTIC VIEWS

Lists all available semantic views in the current schema, returning `schema_name` and `table_name` columns. It is recommended to always add `IN <schema_name>` to avoid ambiguity.

**Syntax:**

```sql
SHOW SEMANTIC VIEWS [ IN <schema_name> ];
```

**Example:**

```sql
SHOW SEMANTIC VIEWS IN doc_test;
```

```
+-------------+-------------------+
| schema_name |    table_name     |
+-------------+-------------------+
| doc_test    | emp_dept_analysis |
+-------------+-------------------+
```

### DESC EXTENDED

View the detailed definition of a specified semantic view, including logical table structure, dimension metadata, metric definitions, and foreign key relationships.

> ⚠️ **Note**: `DESC <view_name>` (without `EXTENDED`) returns empty results — semantic views have no regular column definitions. You must use `DESC EXTENDED` to view the structure.

**Syntax:**

```sql
DESC EXTENDED <view_name>;
```

**Example:**

```sql
DESC EXTENDED doc_test.emp_dept_analysis;
```

The output covers: basic view information (workspace, schema, creation time, comment), logical table information (physical table mapping, primary and foreign keys), dimension metadata (`isUnique`, `isTime`, `enumValues`, etc.), and metric definitions (aggregation expressions).

### Quick Command Reference

| Command | Description |
| ----------------------------------------------- | ---------------- |
| `CREATE SEMANTIC VIEW` | Create a semantic view |
| `DROP SEMANTIC VIEW IF EXISTS` | Delete a semantic view |
| `ALTER SEMANTIC VIEW ... RENAME TO` | Rename a semantic view |
| `SHOW SEMANTIC VIEWS [ IN schema ]` | List all semantic views |
| `DESC EXTENDED` | View complete semantic view structure (must include EXTENDED) |
| `semantic_view()` | Query a semantic view |

***

## Best Practices

**Use DROP IF EXISTS for idempotency**: Always execute `DROP SEMANTIC VIEW IF EXISTS` before creating a semantic view. This ensures your script can be executed repeatedly in any environment without failing because the view already exists.

```sql
DROP SEMANTIC VIEW IF EXISTS tpch_rev_analysis;
CREATE SEMANTIC VIEW tpch_rev_analysis
    ...
```

**Start small and expand gradually**: It is recommended to start with a focused analysis scenario (e.g., revenue analysis using 3-5 tables), verify the accuracy of dimension and metric definitions, and then gradually expand to more tables and more complex business logic.

**Use meaningful business terminology in naming**: Choose names for logical tables, dimensions, and metrics that align with the everyday language of business users. For example, use `customer_name` instead of `c_name`, and `order_average_value` instead of `avg_o_totalprice`. Additionally, make good use of `WITH SYNONYMS` and `COMMENT` to enhance the discoverability and understandability of semantic views.

**Define dimension metadata appropriately**: Correctly set properties such as `is_unique`, `is_time`, and `enum_values` to help the query engine optimize execution plans and provide richer contextual information for downstream tools and users.

**Pay attention to the order of logical table definitions**: In the `TABLES` clause, logical tables referenced by foreign keys must be defined before the referencing tables. Properly planning the declaration order of tables can avoid reference errors during creation.

***

## MCP Tools -- Semantic View Specialized Capabilities

The Singdata Lakehouse MCP Server provides a set of tools specifically designed for semantic views, supporting the full lifecycle management of semantic views through natural language or structured invocations. The following tools are exposed via the MCP protocol and can be integrated into AI agents, data assistants, and other automation scenarios. Please refer to [Link](LakehouseMCPServer-intro.md).

***

### `LH-create-semantic-view` -- Create a Semantic View from YAML

Creates a semantic view from a YAML definition conforming to the Snowflake Cortex Analyst format, suitable for declarative configuration-driven semantic view creation workflows.

**Main Parameters**:

| Parameter            | Type     | Required | Description                                    |
| -------------------- | -------- | -------- | ---------------------------------------------- |
| `semantic_view_yaml` | string   | Yes      | YAML-formatted semantic view definition        |
| `semantic_view_name` | string   | No       | Semantic view name (can be declared in YAML)   |
| `schema_name`        | string   | No       | Target schema name                             |
| `if_not_exists`      | boolean  | No       | Skip if the view already exists (default `true`) |

**Example**:

```yaml
# semantic_view.yaml
name: tpch_rev_analysis
tables:
  - name: customers
    base_table:
      schema: TPCH_SF1
      table: CUSTOMER
    ...
```

```python
# MCP call example (Python)
result = mcp.call("LH-create-semantic-view",
    semantic_view_yaml=open("semantic_view.yaml").read(),
    schema_name="my_schema"
)
```

***

### `LH-desc-semantic-view` -- Get Semantic View YAML Definition

Returns the complete definition of an existing semantic view in YAML format, facilitating version management, export/backup, or secondary editing.

**Main Parameters**:

| Parameter            | Type     | Required | Description              |
| -------------------- | -------- | -------- | ------------------------ |
| `semantic_view_name` | string   | Yes      | Semantic view name       |
| `schema_name`        | string   | No       | Schema name              |

**Sample Output (YAML fragment)**:

```yaml
name: tpch_rev_analysis
comment: Semantic view for revenue analysis
tables:
  - name: customers
    ...
dimensions:
  - name: customer_name
    expr: c_name
    is_unique: true
    ...
metrics:
  - name: customer_count
    expr: COUNT(c_custkey)
    ...
```

***

### `LH-desc-logical-table` -- View Logical Table Definition

Retrieves the detailed definition of a logical table within a semantic view, including its associated physical table, dimension list, and inter-table relationships.

**Main Parameters**:

| Parameter            | Type     | Required | Description              |
| -------------------- | -------- | -------- | ------------------------ |
| `semantic_view_name` | string   | Yes      | Owning semantic view name |
| `schema_name`        | string   | No       | Schema name              |

***

### `LH-brief-semantic-view` -- Brief Field Description

Lists all available dimension and metric fields in a semantic view in a concise format, suitable for quickly understanding the view structure or obtaining a field inventory during the Agent planning phase.

**Main Parameters**:

| Parameter            | Type     | Required | Description              |
| -------------------- | -------- | -------- | ------------------------ |
| `semantic_view_name` | string   | Yes      | Semantic view name       |
| `schema_name`        | string   | No       | Schema name              |

**Sample Output**:

```
Semantic View: tpch_rev_analysis
DIMENSIONS:
  - customers.customer_name  [is_unique=true]  Name of the customer
  - customers.customer_city  City of the customer
  - orders.order_date        [is_time=true]    Date when the order was placed
  - orders.order_year        Year when the order was placed
METRICS:
  - customers.customer_count        Count of number of customers
  - orders.order_average_value      Average order value across all orders
```

***

### `LH-get_semantic_view_dims` -- Get Dimension List

Retrieves all dimension definitions of a specified semantic view, returning structured dimension information including dimension names, physical column mappings, metadata properties (`is_unique`, `is_time`, `enum_values`), and comments.

**Main Parameters**:

| Parameter       | Type     | Required | Description                            |
| --------------- | -------- | -------- | -------------------------------------- |
| `semantic_view` | string   | Yes      | Semantic view name (e.g., `tpch_rev_analysis`) |
| `schema_name`   | string   | No       | Schema name                            |

***

### `LH-semantic-view-dim-add` -- Dynamically Add Dimensions

Adds one or more dimensions to an existing semantic view without rebuilding the view, supporting specification of synonyms, comments, and metadata properties.

**Main Parameters**:

| Parameter            | Type     | Required | Description                    |
| -------------------- | -------- | -------- | ------------------------------ |
| `semantic_view_name` | string   | Yes      | Target semantic view name      |
| `dimensions`         | array    | Yes      | List of dimensions to add      |

**Array Element Structure**:

| Field            | Type     | Required | Description                         |
| ---------------- | -------- | -------- | ----------------------------------- |
| `logical_table`  | string   | Yes      | Logical table alias                 |
| `dimension_name` | string   | Yes      | Dimension name                      |
| `column_name`    | string   | Yes      | Corresponding physical column name  |
| `synonyms`       | array    | Yes      | Synonym list (can be empty array)   |
| `comment`        | string   | Yes      | Dimension description               |

**Example**:

```python
mcp.call("LH-semantic-view-dim-add",
    semantic_view_name="tpch_rev_analysis",
    dimensions=[{
        "logical_table": "customers",
        "dimension_name": "customer_city",
        "column_name": "c_city",
        "synonyms": ["city", "customer city"],
        "comment": "City of the customer"
    }]
)
```

***

### `LH-semantic-view-dim-del` -- Dynamically Delete Dimensions

Removes specified dimensions from an existing semantic view without rebuilding the view.

**Main Parameters**:

| Parameter              | Type     | Required | Description                    |
| ---------------------- | -------- | -------- | ------------------------------ |
| `semantic_view_name`   | string   | Yes      | Target semantic view name      |
| `dimensions_to_remove` | array    | Yes      | List of dimensions to remove   |

**Array Element Structure**:

| Field            | Type     | Required | Description                     |
| ---------------- | -------- | -------- | ------------------------------- |
| `dimension_name` | string   | Yes      | Name of the dimension to remove |

**Example**:

```python
mcp.call("LH-semantic-view-dim-del",
    semantic_view_name="tpch_rev_analysis",
    dimensions_to_remove=[
        {"dimension_name": "customer_city"}
    ]
)
```

***

### `LH-query-semantic-value` -- Natural Language Semantic Query

Queries data from a semantic view based on natural language descriptions. The caller only needs to specify the desired dimensions, metrics, and filter conditions; the tool automatically generates and executes the underlying SQL without the need to manually write the `semantic_view()` function. This is the **recommended approach** for querying semantic views in AI Agent scenarios.

**Main Parameters**:

| Parameter             | Type     | Required | Description                         |
| --------------------- | -------- | -------- | ----------------------------------- |
| `semantic_view_name`  | string   | Yes      | Semantic view name                  |
| `selected_dimensions` | array    | Yes      | List of dimensions to query         |
| `selected_metrics`    | array    | Yes      | List of metrics to query            |
| `filter_conditions`   | array    | No       | List of filter conditions (default empty) |

**`selected_dimensions` / `selected_metrics` Element Structure**:

| Field                              | Type     | Description                                      |
| ---------------------------------- | -------- | ------------------------------------------------ |
| `logical_table`                    | string   | Logical table name the dimension/metric belongs to |
| `dimensions_name` / `metrics_name` | string   | Dimension or metric name (without logical table prefix) |

**`filter_conditions` Element Structure**:

| Field        | Type     | Description                                                                                         |
| ------------ | -------- | --------------------------------------------------------------------------------------------------- |
| `field_name` | string   | Filter field name (must match exactly with a name in `selected_dimensions` or `selected_metrics`)    |
| `expr`       | string   | Filter expression following SQL syntax, e.g., `= 'New York'`, `> 1000`, `BETWEEN '2025-01-01' AND '2025-12-31'` |

**Example**:

```python
# Query average order value for New York customers
mcp.call("LH-query-semantic-value",
    semantic_view_name="tpch_rev_analysis",
    selected_dimensions=[
        {"logical_table": "customers", "dimensions_name": "customer_name"},
        {"logical_table": "customers", "dimensions_name": "customer_city"}
    ],
    selected_metrics=[
        {"logical_table": "orders", "metrics_name": "order_average_value"}
    ],
    filter_conditions=[
        {"field_name": "customer_city", "expr": "= 'New York'"}
    ]
)
```

**Equivalent SQL**:

```sql
SELECT * FROM semantic_view(
    tpch_rev_analysis,
    DIMENSIONS customers.customer_name,
    DIMENSIONS customers.customer_city,
    METRICS orders.order_average_value
) WHERE customer_city = 'New York';
```

***

### MCP Tool Capability Summary

| Tool Name                    | Operation Type | Core Capability                                      |
| ---------------------------- | -------------- | ---------------------------------------------------- |
| `LH-create-semantic-view`    | Create         | Create a semantic view from YAML definition          |
| `LH-desc-semantic-view`      | View           | Get complete view YAML definition                    |
| `LH-desc-logical-table`      | View           | Get logical table structure and relationships        |
| `LH-brief-semantic-view`     | View           | Quick overview of dimension and metric fields        |
| `LH-get_semantic_view_dims`  | View           | Get structured dimension list                        |
| `LH-semantic-view-dim-add`   | Modify         | Dynamically add dimensions (no rebuild needed)       |
| `LH-semantic-view-dim-del`   | Modify         | Dynamically delete dimensions (no rebuild needed)    |
| `LH-query-semantic-value`    | Query          | Structured parameter-driven semantic query, recommended for Agent use |

### Typical Agent Workflow

```
1. LH-brief-semantic-view        -> Understand available dimensions and metrics in the view
2. LH-query-semantic-value       -> Query on demand, passing dimensions/metrics/filter conditions
3. LH-semantic-view-dim-add      -> If a required dimension is missing, dynamically add it
4. LH-desc-semantic-view         -> Export YAML for backup or version comparison
5. LH-create-semantic-view       -> Recreate the view in a new environment based on YAML
```
