# Zettapark Functions Reference

This guide lists common functions from the Zettapark `functions` module.

Import before use:

```python
from clickzetta.zettapark import functions as F
from clickzetta.zettapark.session import Session

session = Session.builder.configs({
    "username": "your_username",
    "password": "your_password",
    "service":  "cn-shanghai-alicloud.api.clickzetta.com",
    "instance": "your_instance",
    "workspace": "your_workspace",
    "schema":   "public",
    "vcluster": "DEFAULT"
}).create()
```

Examples in each section use `create_dataframe` to create DataFrames directly from Python data — no table setup required, run immediately.

---

## String Functions

Create sample data

```python
df = session.create_dataframe(
    [(1, "Alice"), (2, "  hello world  "), (3, "bob")],
    schema=["id", "name"]
)

F.upper(F.col("name"))                          # Convert to uppercase
F.lower(F.col("name"))                          # Convert to lowercase
F.trim(F.col("name"))                           # Remove leading/trailing whitespace
F.length(F.col("name"))                         # String length
F.substr(F.col("name"), 1, 3)                   # Extract substring (1-based index)
F.replace(F.col("name"), "old", "new")          # Replace substring
F.concat(F.lit("Hello, "), F.col("name"))       # Concatenate strings
F.concat_ws("-", F.col("a"), F.col("b"))        # Concatenate with separator
F.regexp_replace(F.col("name"), r"\s+", "_")    # Regex replace
F.lpad(F.col("name"), 10, " ")                  # Left-pad
F.rpad(F.col("name"), 10, " ")                  # Right-pad
F.ltrim(F.col("name"))                          # Remove leading whitespace
F.rtrim(F.col("name"))                          # Remove trailing whitespace
F.initcap(F.col("name"))                        # Capitalize first letter of each word
F.reverse(F.col("name"))                        # Reverse string
F.repeat(F.col("name"), 3)                      # Repeat N times
F.startswith(F.col("name"), "A")                # Check if starts with string
F.endswith(F.col("name"), "z")                  # Check if ends with string
F.contains(F.col("name"), "abc")                # Check if contains substring
F.charindex("abc", F.col("name"))               # Substring position (1-based; 0 if not found)
F.md5(F.col("name"))                            # MD5 hash
F.sha1(F.col("name"))                           # SHA1 hash
```

**Example:**

```python
data = [(1, "  hello world  "), (2, "Alice"), (3, "bob")]
df = session.create_dataframe(data, schema=["id", "name"])

df.select(
    F.col("id"),
    F.upper(F.col("name")).alias("upper"),
    F.trim(F.col("name")).alias("trim"),
    F.length(F.trim(F.col("name"))).alias("len"),
    F.replace(F.col("name"), "world", "Lakehouse").alias("replaced"),
    F.regexp_replace(F.col("name"), r"\s+", "_").alias("no_space"),
).show()
```

```Plain
+---+---------------+------------+---+------------------+---------------+
| id|          upper|        trim|len|          replaced|       no_space|
+---+---------------+------------+---+------------------+---------------+
|  1|  HELLO WORLD  | hello world| 11|  hello Lakehouse |_hello_world_  |
|  2|          ALICE|       Alice|  5|             Alice|          Alice|
|  3|            BOB|         bob|  3|               bob|            bob|
+---+---------------+------------+---+------------------+---------------+
```

---

## Numeric Functions

```python
F.round(F.col("price"), 2)          # Round to 2 decimal places
F.ceil(F.col("price"))              # Round up
F.floor(F.col("price"))             # Round down
F.abs(F.col("amount"))              # Absolute value
F.sqrt(F.col("value"))              # Square root
F.pow(F.col("base"), F.col("exp"))  # Power
F.log(F.lit(10.0), F.col("value")) # Logarithm
F.exp(F.col("value"))               # e to the power
F.sign(F.col("amount"))             # Sign (-1/0/1)
F.greatest(F.col("a"), F.col("b")) # Maximum across columns
F.least(F.col("a"), F.col("b"))    # Minimum across columns
F.div0(F.col("a"), F.col("b"))     # Division (returns 0 when divisor is 0, no error)
```

**Example:**

```python
data = [(1, 3.14159, 100, 200), (2, -2.718, 50, 300)]
df = session.create_dataframe(data, schema=["id", "num", "a", "b"])

df.select(
    F.round(F.col("num"), 2).alias("round"),
    F.ceil(F.col("num")).alias("ceil"),
    F.floor(F.col("num")).alias("floor"),
    F.abs(F.col("num")).alias("abs"),
    F.greatest(F.col("a"), F.col("b")).alias("max_ab"),
    F.least(F.col("a"), F.col("b")).alias("min_ab"),
).show()
```

```Plain
+-----+----+-----+-------+------+------+
|round|ceil|floor|    abs|max_ab|min_ab|
+-----+----+-----+-------+------+------+
| 3.14|   4|    3|3.14159|   200|   100|
|-2.72|  -2|   -3|  2.718|   300|    50|
+-----+----+-----+-------+------+------+
```

---

## Date and Time Functions

```python
F.current_date()                                    # Current date
F.current_timestamp()                               # Current timestamp
F.to_date(F.col("dt_str"))                         # String to date
F.to_timestamp(F.col("ts_str"))                    # String to timestamp
F.year(F.col("dt"))                                # Extract year
F.month(F.col("dt"))                               # Extract month
F.dayofmonth(F.col("dt"))                          # Extract day of month
F.dayofweek(F.col("dt"))                           # Day of week (1=Sunday)
F.hour(F.col("ts"))                                # Extract hour
F.minute(F.col("ts"))                              # Extract minute
F.second(F.col("ts"))                              # Extract second
F.date_add(F.col("dt"), 7)                         # Add N days to date
F.date_sub(F.col("dt"), 7)                         # Subtract N days from date
F.add_months(F.col("dt"), 1)                       # Add N months to date
F.datediff(F.col("end_dt"), F.col("start_dt"))     # Date difference (days)
F.date_format(F.col("dt"), "yyyy/MM/dd")           # Format date
F.last_day(F.col("dt"))                            # Last day of the month
F.months_between(F.col("dt1"), F.col("dt2"))       # Months between two dates
F.unix_timestamp(F.col("ts"))                      # Convert to Unix timestamp (seconds)
F.from_unixtime(F.col("ts_sec"))                   # Unix timestamp to string
```

**Example:**

```python
data = [("2024-01-15",), ("2024-03-31",)]
df = session.create_dataframe(data, schema=["dt_str"])

df.select(
    F.to_date(F.col("dt_str")).alias("date"),
    F.year(F.to_date(F.col("dt_str"))).alias("year"),
    F.month(F.to_date(F.col("dt_str"))).alias("month"),
    F.date_add(F.to_date(F.col("dt_str")), 7).alias("plus_7d"),
    F.date_format(F.to_date(F.col("dt_str")), "yyyy/MM/dd").alias("formatted"),
    F.last_day(F.to_date(F.col("dt_str"))).alias("last_day"),
    F.add_months(F.to_date(F.col("dt_str")), 1).alias("next_month"),
).show()
```

```Plain
+----------+----+-----+----------+-----------+----------+----------+
|      date|year|month|   plus_7d|  formatted|  last_day|next_month|
+----------+----+-----+----------+-----------+----------+----------+
|2024-01-15|2024|    1|2024-01-22|2024/01/15 |2024-01-31|2024-02-15|
|2024-03-31|2024|    3|2024-04-07|2024/03/31 |2024-03-31|2024-04-30|
+----------+----+-----+----------+-----------+----------+----------+
```

---

## Conditional Functions

when / otherwise — multi-branch condition (like CASE WHEN)

```python
F.when(F.col("score") >= 90, "A") \
 .when(F.col("score") >= 80, "B") \
 .when(F.col("score") >= 60, "C") \
 .otherwise("F")
```

iff — simple binary condition (like ternary operator)

```python
F.iff(F.col("amount") > 0, "positive", "non-positive")
```

coalesce — return the first non-NULL value

```python
F.coalesce(F.col("value"), F.col("default_value"), F.lit(0))
```

is\_null / is\_not\_null

```python
F.is_null(F.col("name"))
```

**Example:**

```python
data = [(1, 95), (2, 82), (3, 67), (4, 45)]
df = session.create_dataframe(data, schema=["id", "score"])

df.select(
    F.col("id"),
    F.col("score"),
    F.when(F.col("score") >= 90, "A")
     .when(F.col("score") >= 80, "B")
     .when(F.col("score") >= 60, "C")
     .otherwise("F").alias("grade"),
    F.iff(F.col("score") >= 60, "pass", "fail").alias("result"),
).show()
```

```Plain
+---+-----+-----+------+
| id|score|grade|result|
+---+-----+-----+------+
|  1|   95|    A|  pass|
|  2|   82|    B|  pass|
|  3|   67|    C|  pass|
|  4|   45|    F|  fail|
+---+-----+-----+------+
```

---

## Aggregate Functions

```python
F.count(F.col("id"))                    # Count (excludes NULL)
F.count(F.lit(1))                       # Total row count
F.count_distinct(F.col("user_id"))      # Distinct count
F.sum(F.col("amount"))                  # Sum
F.avg(F.col("amount"))                  # Average
F.max(F.col("amount"))                  # Maximum
F.min(F.col("amount"))                  # Minimum
F.stddev(F.col("amount"))               # Standard deviation
F.variance(F.col("amount"))             # Variance
F.median(F.col("amount"))               # Median
F.approx_count_distinct(F.col("id"))    # Approximate distinct count (faster for large data)
F.listagg(F.col("name"), ",")           # String aggregation (like GROUP_CONCAT)
F.any_value(F.col("name"))              # Return any value from the group
```

**Example:**

```python
data = [(1,"A",100),(2,"A",200),(3,"B",300),(4,"B",150),(5,"A",50)]
df = session.create_dataframe(data, schema=["id","category","amount"])

df.group_by("category").agg(
    F.count(F.col("id")).alias("cnt"),
    F.sum(F.col("amount")).alias("total"),
    F.avg(F.col("amount")).alias("avg"),
    F.max(F.col("amount")).alias("max"),
    F.min(F.col("amount")).alias("min"),
).show()
```

```Plain
+--------+---+-----+-----+---+---+
|category|cnt|total|  avg|max|min|
+--------+---+-----+-----+---+---+
|       A|  3|  350|116.7|200| 50|
|       B|  2|  450|225.0|300|150|
+--------+---+-----+-----+---+---+
```

---

## JSON Functions

```python
F.get_json_object(F.col("data"), "$.name")      # Extract a JSON field
F.get_json_object(F.col("data"), "$.addr.city") # Extract a nested field
F.parse_json(F.col("json_str"))                 # Parse a JSON string
F.to_json(F.col("struct_col"))                  # Convert to JSON string
```

**Example:**

```python
data = [(1, '{"name":"Alice","age":30,"addr":{"city":"Beijing"}}')]
df = session.create_dataframe(data, schema=["id", "data"])

df.select(
    F.get_json_object(F.col("data"), "$.name").alias("name"),
    F.get_json_object(F.col("data"), "$.age").alias("age"),
    F.get_json_object(F.col("data"), "$.addr.city").alias("city"),
).show()
```

```Plain
+-----+---+-------+
| name|age|   city|
+-----+---+-------+
|Alice| 30|Beijing|
+-----+---+-------+
```

---

## Other Common Functions

```python
F.lit(42)                           # Literal value
F.col("name")                       # Column reference
F.expr("amount * 1.13")             # Raw SQL expression
F.cast(F.col("str_col"), "int")     # Type cast
F.try_cast(F.col("str_col"), "int") # Safe type cast (returns NULL on failure)
F.hash(F.col("id"))                 # Hash value
F.random()                          # Random number (0–1)
F.monotonically_increasing_id()     # Monotonically increasing ID (not guaranteed to be consecutive)
F.typeof(F.col("value"))            # Return the data type name of a column
```

---

## Notes

- **Always use `F.col("column_name")` to reference columns** — avoid passing raw strings, as some functions treat strings as literal values rather than column names
- `F.split()` has a known issue in the current version (0.1.5); use `session.sql()` as a workaround
- `F.date_trunc()` has a known issue in the current version; use `F.date_format()` + `F.to_date()` as a workaround

---

## Related Documentation

| Document | Description |
|------|------|
| [Zettapark DataFrame API Guide](zettapark-dataframe-guide.md) | Complete DataFrame operations guide |
| [Zettapark Quick Start](zettapark-quick-start.md) | Installation and basic examples |
| [SQL Functions Reference](sql_functions/) | Complete list of Lakehouse built-in SQL functions |
