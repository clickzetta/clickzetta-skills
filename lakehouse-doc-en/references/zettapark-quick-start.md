# Lakehouse Zettapark

Zettapark is a Python library for processing Singdata Lakehouse data. It provides a high-level Python API for executing SQL queries, manipulating data, and processing results in Singdata Lakehouse. Zettapark makes working with Singdata Lakehouse in Python simpler and more efficient. You can use Zettapark to execute SQL queries, manipulate data, and process results, just like using pandas in Python.

You can also [download the corresponding Jupyter Notebook file](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/Zettapark/Zettapark_quickstart.ipynb) to run this demo directly.

Pandas operations executed in Zettapark are translated into SQL and run in Singdata Lakehouse, enabling distributed computing.

For example, the following Python code:

```
df_sorted = df.select("a", "b").filter((F.col("a") + F.col("b")) < 10)
```

The SQL executed in Singdata Lakehouse is:

```
SELECT a, b FROM ( SELECT col1 AS a, col2 AS b FROM  VALUES (CAST(1 AS INT), CAST(3 AS INT)), (CAST(2 AS INT), CAST(10 AS INT))) WHERE ((a + b) < CAST(10 AS INT)) LIMIT 10;
```

## Installing clickzetta_zettapark_python

```
!pip install -q --upgrade clickzetta_zettapark_python -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## Creating a Session

The first step in using Zettapark is to establish a session with Singdata Lakehouse.

Import the Session class.

```python
from clickzetta.zettapark.session import Session
```

Like the Python connector, Zettapark uses the same parameters in its functions (e.g., service, instance, username, etc.) to establish a session with Singdata Lakehouse.
Construct a dictionary containing the names and values of these parameters (username, password, service, instance, workspace, schema, etc.).

To create a session, follow these steps:

```
Create a Python dictionary (dict) containing the names and values of the parameters used to connect to Singdata Lakehouse.

Pass this dictionary to the Session.builder.configs method to return a builder object with these connection parameters.

Call the create method on the builder to establish the session.
```

The following example uses a dict containing connection parameters to create a new session:

```
hints = dict()
hints['sdk.job.timeout'] = 3
hints['query_tag'] = 'test_conn_hints_zettapark'
connection_parameters = {
  "username": "",
  "password": "",
  "service": "<region\_id>
```

Verify that the session was created successfully:

```python
df = session.sql("show schemas;")
df.show(5)
```

```
---------------------------
|`schema_name`            |
---------------------------
|automobile               |
|automv_schema            |
|brazilianecommerce       |
|continues_computing      |
|continues_pipeline_demo  |
---------------------------
```

## Using DataFrames in Zettapark Python

In Zettapark, the primary way to query and process data is through DataFrames. This topic introduces how to use DataFrames.

To retrieve and manipulate data in Singdata Lakehouse tables, use the DataFrame class. A DataFrame represents a lazily evaluated relational dataset: it only performs computation when a specific action is triggered.

To retrieve data into a DataFrame:

```
1. Construct a DataFrame by specifying the dataset's data source.

For example, you can create a DataFrame to hold data from a table, an external CSV file, local data, or the result of a SQL statement.

2. Specify how to transform the dataset in the DataFrame.

For example, you can specify which columns should be selected, how to filter rows, how to sort and group results, etc.

3. Execute a statement to retrieve data into the DataFrame.

To retrieve data into a DataFrame, you must call a method that performs an action (for example, the collect() method).
```

This example uses a DataFrame to query a table named `sample_product_data`. If you want to run these examples, you can create the table and insert some data into it by executing the following SQL statements.

```python
session.sql('CREATE  TABLE if not exists sample_product_data (id INT, parent_id INT, category_id INT, name STRING, serial_number STRING, key INT, third INT)').collect()
```

```
[Row(result_message='OPERATION SUCCEED')]
```

```python
session.sql('CREATE  TABLE if not exists sample_product_data_varchar (id INT, parent_id INT, category_id INT, name STRING, serial_number VARCHAR, key INT, third INT)').collect()
```

```
[Row(result_message='OPERATION SUCCEED')]
```

```python
session.sql("""
... INSERT INTO sample_product_data_varchar VALUES
... (1, 0, 5, 'Product 1', 'prod-1', 1, 10),
... (2, 1, 5, 'Product 1A', 'prod-1-A', 1, 20),
... (3, 1, 5, 'Product 1B', 'prod-1-B', 1, 30),
... (4, 0, 10, 'Product 2', 'prod-2', 2, 40),
... (5, 4, 10, 'Product 2A', 'prod-2-A', 2, 50),
... (6, 4, 10, 'Product 2B', 'prod-2-B', 2, 60),
... (7, 0, 20, 'Product 3', 'prod-3', 3, 70),
... (8, 7, 20, 'Product 3A', 'prod-3-A', 3, 80),
... (9, 7, 20, 'Product 3B', 'prod-3-B', 3, 90),
... (10, 0, 50, 'Product 4', 'prod-4', 4, 100),
... (11, 10, 50, 'Product 4A', 'prod-4-A', 4, 100),
... (12, 10, 50, 'Product 4B', 'prod-4-B', 4, 100)
... """).collect()
```

```
[Row(result_message='OPERATION SUCCEED')]
```

To verify that the data was inserted successfully, run:

```python
session.sql("SELECT count(*) FROM sample_product_data_varchar").collect()
```

```
[Row(`count`(*)=120)]
```

## Constructing DataFrames

To construct a DataFrame, you can use the methods and properties of the Session class. Each of the following methods constructs a DataFrame from a different type of data source.

To create a DataFrame from data in a table, view, or stream, call the `table` method:

```python
# Create a DataFrame from the data in the "sample_product_data" table.
df_table = session.table("sample_product_data")
# To print out the first 10 rows
df_table.show()
```

```
---------------------------------------------------------------------------------------
|`id`  |`parent_id`  |`category_id`  |`name`      |`serial_number`  |`key`  |`third`  |
---------------------------------------------------------------------------------------
|1     |0            |5              |Product 1   |prod-1           |1      |10       |
|2     |1            |5              |Product 1A  |prod-1-A         |1      |20       |
|3     |1            |5              |Product 1B  |prod-1-B         |1      |30       |
|4     |0            |10             |Product 2   |prod-2           |2      |40       |
|5     |4            |10             |Product 2A  |prod-2-A         |2      |50       |
|6     |4            |10             |Product 2B  |prod-2-B         |2      |60       |
|7     |0            |20             |Product 3   |prod-3           |3      |70       |
|8     |7            |20             |Product 3A  |prod-3-A         |3      |80       |
|9     |7            |20             |Product 3B  |prod-3-B         |3      |90       |
|10    |0            |50             |Product 4   |prod-4           |4      |100      |
---------------------------------------------------------------------------------------
```

```python
# Create a DataFrame from the data in the "sample_product_data" table.
df_table = session.table("sample_product_data_varchar")
# To print out the first 10 rows
df_table.show()
```

```
---------------------------------------------------------------------------------------
|`id`  |`parent_id`  |`category_id`  |`name`      |`serial_number`  |`key`  |`third`  |
---------------------------------------------------------------------------------------
|1     |0            |5              |Product 1   |prod-1           |1      |10       |
|2     |1            |5              |Product 1A  |prod-1-A         |1      |20       |
|3     |1            |5              |Product 1B  |prod-1-B         |1      |30       |
|4     |0            |10             |Product 2   |prod-2           |2      |40       |
|5     |4            |10             |Product 2A  |prod-2-A         |2      |50       |
|6     |4            |10             |Product 2B  |prod-2-B         |2      |60       |
|7     |0            |20             |Product 3   |prod-3           |3      |70       |
|8     |7            |20             |Product 3A  |prod-3-A         |3      |80       |
|9     |7            |20             |Product 3B  |prod-3-B         |3      |90       |
|10    |0            |50             |Product 4   |prod-4           |4      |100      |
---------------------------------------------------------------------------------------
```

To create a DataFrame from specified data, call the `create_dataframe` method:

```python
# Create a DataFrame with one column named a from specified values.
df1 = session.create_dataframe([1, 2, 3, 4]).to_df("a")
df1.show()

```

```
-------
|`a`  |
-------
|1    |
|2    |
|3    |
|4    |
-------
```

Create a DataFrame with 4 columns ("a", "b", "c", and "d"):

```python
df2 = session.create_dataframe([[1, 2, 3, 4]], schema=["a", "b", "c", "d"])
df2.show()
```

```
-------------------------
|`a`  |`b`  |`c`  |`d`  |
-------------------------
|1    |2    |3    |4    |
-------------------------
```

Create another DataFrame with 4 columns ("a", "b", "c", and "d"):

```python
from clickzetta.zettapark import Row
df3 = session.create_dataframe([Row(a=1, b=2, c=3, d=4)])
df3.show()
```

```
-------------------------
|`a`  |`b`  |`c`  |`d`  |
-------------------------
|1    |2    |3    |4    |
-------------------------
```

Create a DataFrame and specify a schema:

```python
from clickzetta.zettapark.types import IntegerType, StringType, StructType, StructField
schema = StructType([StructField("a", IntegerType()), StructField("b", StringType())])
df4 = session.create_dataframe([[1, "click"], [3, "zetta"]], schema)
df4.show()
```

```
---------------
|`a`  |`b`    |
---------------
|1    |click  |
|3    |zetta  |
---------------
```

To create a DataFrame containing a range of values, call the `range` method:

```python
df_range = session.range(1, 10, 2).to_df("a")
df_range.show()
```

```
-------
|`a`  |
-------
|1    |
|3    |
|5    |
|7    |
|9    |
-------
```

## Transforming Specified Datasets

To specify which columns to select and how to filter, sort, group, etc. the results, call the DataFrame methods that transform the dataset. To identify columns in these methods, use the `col` function or an expression that evaluates to a column.

For example:
To specify which rows should be returned, call the `filter` method:

```python
from clickzetta.zettapark import functions as F
```

```python
df = session.table("sample_product_data").filter(F.col("id") == 1)
df.show()
```

```
--------------------------------------------------------------------------------------
|`id`  |`parent_id`  |`category_id`  |`name`     |`serial_number`  |`key`  |`third`  |
--------------------------------------------------------------------------------------
|1     |0            |5              |Product 1  |prod-1           |1      |10       |
--------------------------------------------------------------------------------------
```

To specify which columns should be selected, call the `select` method:

```python
# Create a DataFrame that contains the id, name, and serial_number
# columns in the "sample_product_data" table.
df = session.table("sample_product_data").select(F.col("id"), F.col("name"), F.col("serial_number"))
df.show()
```

```
---------------------------------------
|`id`  |`name`      |`serial_number`  |
---------------------------------------
|1     |Product 1   |prod-1           |
|2     |Product 1A  |prod-1-A         |
|3     |Product 1B  |prod-1-B         |
|4     |Product 2   |prod-2           |
|5     |Product 2A  |prod-2-A         |
|6     |Product 2B  |prod-2-B         |
|7     |Product 3   |prod-3           |
|8     |Product 3A  |prod-3-A         |
|9     |Product 3B  |prod-3-B         |
|10    |Product 4   |prod-4           |
---------------------------------------
```

```python
# Import the col function from the functions module.
df_product_info = session.table("sample_product_data")
df1 = df_product_info.select(df_product_info["id"], df_product_info["name"], df_product_info["serial_number"])
df2 = df_product_info.select(df_product_info.id, df_product_info.name, df_product_info.serial_number)
df3 = df_product_info.select("id", "name", "serial_number")
```

## Joining DataFrames

To join DataFrame objects, call the `join` method:

```
# Create two DataFrames to join
df_lhs = session.create_dataframe([["a", 1], ["b", 2]], schema=["key", "value1"])
df_rhs = session.create_dataframe([["a", 3], ["b", 4]], schema=["key", "value2"])
# Create a DataFrame that joins the two DataFrames
# on the column named "key".
df_lhs.join(df_rhs, df_lhs.col("key") == df_rhs.col("key")).select(df_lhs["key"].as_("key"), "value1", "value2").show()
```

```
-------------------------------
|`key`  |`value1`  |`value2`  |
-------------------------------
|a      |1         |3         |
|b      |2         |4         |
-------------------------------
```

```python
import copy

df = session.table("sample_product_data")
# This fails because columns named "id" and "parent_id"
# are in the left and right DataFrames in the join.
df_copy = copy.copy(df)
df_joined = df.join(df_copy, F.col("id") == F.col("parent_id"))
```

## Specifying Columns and Expressions

When calling these transformation methods, you may need to specify columns or use expressions involving columns. For example, when calling the `select` method, you need to specify the columns to select.

```python
df_product_info = session.table("sample_product_data").select(F.col("id"), F.col("name"))
df_product_info.show()
```

```
---------------------
|`id`  |`name`      |
---------------------
|1     |Product 1   |
|2     |Product 1A  |
|3     |Product 1B  |
|4     |Product 2   |
|5     |Product 2A  |
|6     |Product 2B  |
|7     |Product 3   |
|8     |Product 3A  |
|9     |Product 3B  |
|10    |Product 4   |
---------------------
```

When specifying filters, projections, join conditions, etc., you can use Column objects in expressions. For example:
You can use a Column object and the `filter` method to specify a filter condition:

```python
# Specify the equivalent of "WHERE id = 20"
# in a SQL SELECT statement.
df_filtered = df_product_info.filter(F.col("id") == 20)
df_filtered.show()
```

```
-----------------
|`id`  |`name`  |
-----------------
|      |        |
-----------------
```

```python
df = session.create_dataframe([[1, 3], [2, 10]], schema=["a", "b"])
# Specify the equivalent of "WHERE a + b < 10"
# in a SQL SELECT statement.
df_filtered = df.filter((F.col("a") + F.col("b")) < 10)
df_filtered.show()
```

```
-------------
|`a`  |`b`  |
-------------
|1    |3    |
-------------
```

## Closing a Session

```Python
session.close()
```

## References

[Zettapark Samples](https://github.com/yunqiqiliang/clickzetta_quickstart/tree/main/Zettapark-examples/Notebook)

^
