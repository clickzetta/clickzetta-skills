# Create Semantic View

## Syntax

```sql
CREATE SEMANTIC VIEW <view_name>
TABLES (
    <logical_table_definition> [ , ... ]
)
[ FILTERS (
    <filter_definition> [ , ... ]
) ]
[ DIMENSIONS (
    <dimension_definition> [ , ... ]
) ]
[ METRICS (
    <metric_definition> [ , ... ]
) ]
[ COMMENT = '<view_description>' ]
;
```

The definition syntax for each clause is as follows:

### Logical Table Definition

```sql
<table_alias> AS <schema_name>.<physical_table_name>
    PRIMARY KEY ( <column_name> [ , ... ] )
    [ FOREIGN KEY ( <column_name> ) REFERENCES <other_logical_table_alias> [ ( <referenced_column_name> ) ] ]
    [ WITH SYNONYMS ( '<synonym>' [ , ... ] ) ]
    [ COMMENT = '<description>' ]
```

### Filter Definition

```sql
<logical_table_alias>.<filter_name> AS <boolean_expression>
```

### Dimension Definition

```sql
{ <logical_table_alias>.<dimension_name> | <dimension_name> } AS <expression>
    [ WITH SYNONYMS = ( '<synonym>' [ , ... ] ) ]
    [ is_unique = { true | false } ]
    [ is_time = { true | false } ]
    [ enum_values = [ <value1>, <value2>, ... ] ]
    [ COMMENT = '<description>' ]
```

### Metric Definition

```sql
<logical_table_alias>.<metric_name> AS <aggregation_expression>
    [ COMMENT = '<description>' ]
```

## Parameter Descriptions

### Logical Table Parameters

| Parameter | Description |
|------|------|
| `<table_alias> AS <schema_name>.<physical_table_name>` | Assign a logical alias to a physical table; subsequent dimension, metric, and foreign key definitions use this alias |
| `PRIMARY KEY ( <column_name> )` | Specifies the primary key column, used to determine relationship types between tables |
| `FOREIGN KEY ( <column_name> ) REFERENCES <alias> [ ( <referenced_column_name> ) ]` | Defines a foreign key relationship. When the foreign key column name differs from the referenced table's primary key column name, the referenced column name must be specified explicitly. **The foreign key column and referenced column must have the same data type**, otherwise creation will fail |
| `WITH SYNONYMS ( '<synonym>' )` | Defines synonyms for the logical table to enhance discoverability |
| `COMMENT = '<description>'` | Description of the logical table |

### Dimension Parameters

| Parameter | Description |
|------|------|
| `is_unique = true` | Indicates that dimension values are unique, e.g., customer name |
| `is_time = true` | Indicates that the dimension is time-based, e.g., order date |
| `enum_values = [...]` | Constrains the allowed value range for the dimension |
| `WITH SYNONYMS = (...)` | Defines synonyms for the dimension, supporting multiple business terms referencing the same dimension |

### Metric Aggregation Functions

**Supported**: `COUNT`, `AVG`, `SUM`, `MIN`, `MAX`, and conditional aggregations such as `COUNT(CASE WHEN col = value THEN 1 END)`

**Not supported** (do not error at creation but produce incorrect results or compiler errors at query time; do not use):
- Arithmetic expression metrics: `MAX(col) - MIN(col)`, `SUM(col) / COUNT(col)`, etc. -- queries only return the value of the first operand
- Window function metrics: `RANK() OVER (...)` -- abnormal behavior at query time
- Derived metrics (metrics referencing other metrics): `metric_a / metric_b` -- reports `cannot resolve column` at creation time

For composite metrics such as per-capita values or ratios, calculate them in the outer SQL of the `semantic_view()` query:

```sql
SELECT department, total_salary / total_employees AS avg_salary_calc
FROM semantic_view(
    my_view,
    DIMENSIONS department,
    METRICS total_salary,
    METRICS total_employees
);
```

## Usage Notes

- The `TABLES` clause is mandatory and cannot be omitted. `DIMENSIONS` and `METRICS` are optional.
- Logical tables referenced by foreign keys must be defined in the `TABLES` clause before the referencing tables.
- Creating a semantic view that already exists will error. It is recommended to first execute `DROP SEMANTIC VIEW IF EXISTS`.
- Dimensions support expressions (computed dimensions), such as `YEAR(hire_date)`. Query results return integer types.
- Dimension and metric naming supports both **qualified names** (`alias.name`) and **short names** (`name`). When names are unique, the two forms are equivalent.
- Named filters in the `FILTERS` clause are semantic annotations for the AI/metadata layer and cannot be passed directly to the `semantic_view()` function. Filtering must be done via the outer `WHERE` clause.

## Examples

### Basic Example: Single-table Semantic View

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
        COMMENT = 'employee name',
    emps.department AS emps.dept
        COMMENT = 'department',
    emps.hire_year AS YEAR(emps.hire_date)
        is_time = true
        COMMENT = 'year of hire',
    depts.manager_name AS depts.manager
        COMMENT = 'department manager'
)
METRICS (
    emps.total_employees AS COUNT(emps.id)
        COMMENT = 'total number of employees',
    emps.avg_salary AS AVG(emps.salary)
        COMMENT = 'average salary',
    emps.max_salary AS MAX(emps.salary)
        COMMENT = 'highest salary'
)
COMMENT = 'Employee department analysis semantic view';
```

Notes:
- `depts` and `emps` are logical table aliases; the physical tables are `doc_test.departments` and `doc_test.employees` respectively
- `FOREIGN KEY (dept) REFERENCES depts (dept_name)`: `emps.dept` (string) references `depts.dept_name` (string), types match
- `hire_year` is a computed dimension derived from the date column via the `YEAR()` expression

### Semantic View with Filters and Dimension Metadata

The following example demonstrates the full usage of `FILTERS`, `is_unique`, `is_time`, and `enum_values`:

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
        WITH SYNONYMS ('sales orders')
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
        WITH SYNONYMS = ('customer name')
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

## Related Documents

- [Query Semantic View](semantic-view-query.md)
- [Manage Semantic View](semantic-view-manage.md)
- [Best Practices](semantic-view-best-practices.md)
