# Notebook PySpark Mode

Notebook PySpark mode runs Python cells through the PySpark interpreter. Studio initializes and injects the `spark` session, so cell code should use `spark` directly.

Do not import or create `SparkSession` in the notebook.

Each block below is a separate cell and can be pasted into a PySpark notebook.

## Test Case 1: Create and Display a DataFrame

```python
data = [(1, "Alice", 28), (2, "Bob", 35), (3, "Charlie", 22), (4, "Diana", 45)]
df = spark.createDataFrame(data, ["id", "name", "age"])
df.show()
df.printSchema()
```

`df.show()` displays the rows, and `df.printSchema()` displays the column types. The `spark` object is provided by Studio.

## Test Case 2: Filter, Select, and Order

```python
df.filter(df.age > 25).select("name", "age").orderBy("age", ascending=False).show()
```

This case depends on `df` from Test Case 1. Run the creating cell first if you run this cell separately.

## Test Case 3: Group and Aggregate

```python
from pyspark.sql import functions as F

data2 = [
    ("sales", "Alice", 5000),
    ("sales", "Bob", 7000),
    ("engineering", "Charlie", 8000),
    ("engineering", "Diana", 9000),
    ("engineering", "Eve", 6000),
]
df2 = spark.createDataFrame(data2, ["dept", "name", "salary"])

df2.groupBy("dept").agg(
    F.count("*").alias("count"),
    F.avg("salary").alias("avg_salary"),
    F.max("salary").alias("max_salary")
).show()
```

The result contains the row count, average salary, and maximum salary for each department. Importing `pyspark.sql.functions` is normal; importing or creating `SparkSession` is not.

## Constraints

* Use the injected `spark` object. Do not call `SparkSession.builder.getOrCreate()`.
* `pip show pyspark-client` only proves that the client package is installed; it does not prove that the notebook has an injected `spark` session.
* If you get `NameError: name 'spark' is not defined`, verify that the notebook is in PySpark mode, open a new session, and run the cells in order.
* PySpark mode is not a full Spark runtime. Prefer `spark.createDataFrame()`, Lakehouse tables, and DataFrame/SQL operations that can be converted to Lakehouse SQL. Plans that cannot be converted, such as `spark.range()` in the current implementation, may fail with `PLAN_NOT_FULLY_PUSHABLE`.
* Avoid `collect()` and `toPandas()` for large results. Filter, aggregate, or limit data before returning it to the notebook.

## Related Documentation

* [Notebook](notebook.md)
* [Virtual Cluster](virtual-cluster.md)
* [Spark SQL Migration Guide](migration-spark-sql.md)
* [PySpark to ZettaPark Migration](pyspark-to-zettapark-migration-f1.md)
