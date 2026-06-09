# Data Engineering Based on Singdata Zettapark

This is a very basic data engineering example that demonstrates basic DataFrame operations such as reading, grouping, and writing data through Singdata [Zettapark](zettaparkquickstart.md) Python code. This example uses the built-in free sample database (clickzetta\_sample\_data.tpch\_100g) in Singdata Lakehouse as the data source.

Steps are as follows:

```
1. Connect to Singdata Lakehouse through Zettapark

2. Connect 2 large tables through SupplierKey (LINEITEMS has 600 million rows & SUPPLIER has 1 million rows)

3. Demonstrate on-demand scaling by adjusting the virtual compute cluster to different specifications: XSMALL, MEDIUM

4. Compare the execution time of the same task with different specifications of virtual compute clusters

    Summarize the data of suppliers and part numbers to calculate the sum, minimum, and maximum values (35 million rows)

    Write the result dataframe into the Singdata Lakehouse physical table (80 million rows)
```

You can also run this example directly by [downloading the Jupyter Notebook file](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/Zettapark/Zettapark_Data_Engineering_Demo.ipynb).

**The entire operation, from adjusting computing resources, reading data, connecting, and summarizing, takes about 30 seconds, demonstrating the powerful capabilities, instant scalability, and performance of Singdata Lakehouse**.

## Install Singdata Zettapark

```python
# !pip install clickzetta-zettapark-python
```

## Connect to Singdata Lakehouse through ZettaPark (& without PySpark)

```python
import time
from clickzetta.zettapark.session import Session
import clickzetta.zettapark.functions as f
from clickzetta.zettapark import Session, DataFrame
from clickzetta.zettapark.functions import udf, col
from clickzetta.zettapark.types import IntegerType
from clickzetta.zettapark.functions import call_udf
```

<----- Make these changes before running the notebook --------------------
Change Connection params to match your environment
<----------------------------------------------------------------------------

VCLUSTER\_Name = 'default\_ap'
VCLUSTER\_Size = "XSMALL"
VCLUSTER\_ReSize = "MEDIUM"
Workspace\_Name = 'gharchive'
Schema\_Name = 'Public'

```python
import json
from clickzetta.zettapark.session import Session
# 1- Create a session to connect to Singdata Lakehouse
# Read parameters from the configuration file
with open('config.json', 'r') as config_file:
config = json.load(config_file)

print("Connecting to Singdata Lakehouse.....n")


# Create a session
session = Session.builder.configs(config).create()

print("Connection successful！...n")


```

Connecting to Singdata Lakehouse.....
Connection successful!...

```python
sql_cmd = f"CREATE VCLUSTER IF NOT EXISTS {VCLUSTER_Name} VCLUSTER_SIZE = {VCLUSTER_Size} AUTO_SUSPEND_IN_SECOND = 10 "
print("XSMALL VCLUSTER creation ready n")

session.sql(sql_cmd).collect()

session.use_schema(Schema_Name)
```

# XSMALL VCLUSTER Creation Ready

Sample config.json file ([Parameter Description](jdbc-driver.md)):

```json
{

  "username": "Please replace with your username",

  "password": "Please replace with your password",

  "service": "Please replace with your service address",

  "instance": "Please replace with your instance ID",

  "workspace": "Please replace with your workspace",

  "schema": "Please replace with your schema",

  "vcluster": "Please replace with your virtual cluster",

  "sdk_job_timeout": 60,

  "hints": {

    "sdk.job.timeout": 60,

    "query_tag": "test_conn_hints_zettapark"

  }

}
```

## Start Data Engineering Process

```python
from clickzetta.zettapark.functions import col, sum, min, max

print("Joining, Aggregating with 2 large tables(600M & 1M rows) & Writing results to new table(80M rows) ..n")

# 2- define table
dfLineItems = session.table("clickzetta_sample_data.tpch_100g.LINEITEM") # 600 Million Rows
dfSuppliers = session.table("clickzetta_sample_data.tpch_100g.SUPPLIER") # 100K Rows

print('Lineitems Table: %s rows' % dfLineItems.count())
print('Suppliers Table: %s rows' % dfSuppliers.count())

# 3 - JOIN TABLES
dfJoinTables = dfLineItems.join(dfSuppliers, dfLineItems["L_SUPPKEY"] == dfSuppliers["S_SUPPKEY"])

# 4 - SUMMARIZE THE DATA BY SUPPLIER, PART, SUM, MIN & MAX
dfSummary = dfJoinTables.groupBy("S_NAME", "L_PARTKEY").agg(
sum(col("L_QUANTITY")).alias("TOTAL_QTY"),
min(col("L_QUANTITY")).alias("MIN_QTY"),
max(col("L_QUANTITY")).alias("MAX_QTY")
)

dfSummary.show()

```

```
Joining, Aggregating with 2 large tables(600M & 1M rows) & Writing results to new table(80M rows) ..
Lineitems Table: 600037902 rows
Suppliers Table: 1000000 rows
------------------------------------------------------------------
|         s_name         |   l_partkey    | total_qty | min_qty | max_qty |
------------------------------------------------------------------
| Supplier#000102785     |  18602748      |   156.00  |  12.00  |  49.00  |
| Supplier#000268783     |   8268782      |   228.00  |   1.00  |  44.00  |
| Supplier#000680518     |  12680517      |   107.00  |   8.00  |  47.00  |
| Supplier#000981141     |   1731139      |   228.00  |   5.00  |  48.00  |
| Supplier#000172390     |   1172389      |   192.00  |   1.00  |  38.00  |
| Supplier#000763964     |   1763963      |   174.00  |   1.00  |  47.00  |
| Supplier#000087125     |  16337076      |   168.00  |   4.00  |  50.00  |
| Supplier#000092530     |   1842528      |   169.00  |   1.00  |  48.00  |
| Supplier#000366762     |  18866725      |   156.00  |   3.00  |  41.00  |
| Supplier#000785842     |   4285833      |   238.00  |   2.00  |  40.00  |
------------------------------------------------------------------
```

```python
# 2 - READ & JOIN 2 LARGE TABLES (600M & 1M rows)
from clickzetta.zettapark.functions import col, sum, min, max

print("Merging and aggregating two large tables (600 million rows and 1 million rows), and writing the result into a new table (80 million rows)..n")

dfLineItems = session.table("clickzetta_sample_data.tpch_100g.LINEITEM") # 600 Million Rows
dfSuppliers = session.table("clickzetta_sample_data.tpch_100g.SUPPLIER") # 1 Million Rows

print('Lineitems Table: %s rows' % dfLineItems.count())
print('Suppliers Table: %s rows' % dfSuppliers.count())

# 3 - JOIN TABLES
dfJoinTables = dfLineItems.join(dfSuppliers, dfLineItems["L_SUPPKEY"] == dfSuppliers["S_SUPPKEY"])

# 4 - SUMMARIZE THE DATA BY SUPPLIER, PART, SUM, MIN & MAX
dfSummary = dfJoinTables.groupBy("S_NAME", "L_PARTKEY").agg(
sum("L_QUANTITY").alias("TOTAL_QTY"),
min("L_QUANTITY").alias("MIN_QTY"),
max("L_QUANTITY").alias("MAX_QTY")
)

dfSummary.show()
```

```
Merging and aggregating two large tables (600 million rows and 1 million rows), and writing the results into a new table (80 million rows)..
Lineitems Table: 600037902 rows
Suppliers Table: 1000000 rows
------------------------------------------------------------------
|         s_name         |  l_partkey   | total_qty | min_qty | max_qty |
------------------------------------------------------------------
| Supplier#000543332     |  14043303    |   164.00  |  17.00  |  50.00  |
| Supplier#000162101     |   6412082    |   243.00  |   3.00  |  49.00  |
| Supplier#000170221     |   9920211    |   204.00  |  10.00  |  48.00  |
| Supplier#000652699     |   4402694    |   215.00  |   3.00  |  46.00  |
| Supplier#000635296     |   1635295    |   153.00  |   3.00  |  29.00  |
| Supplier#000915082     |   3665078    |   228.00  |   3.00  |  42.00  |
| Supplier#000624767     |  15624766    |   149.00  |  11.00  |  37.00  |
| Supplier#000899746     |   4399737    |   202.00  |   1.00  |  48.00  |
| Supplier#000285255     |   6285254    |   274.00  |  10.00  |  48.00  |
| Supplier#000052105     |  19552066    |   307.00  |   1.00  |  48.00  |
------------------------------------------------------------------
```

## 3. Completing the same computing task with different computing resources (virtual clusters) requires different amounts of time, observe the effect of elastic scaling.

```python
start_time = time.time()

# 4 - Adjust the virtual compute cluster size to XSMALL
print(f"Adjusting to {VCLUSTER_Size} ..")

sql_cmd = f"ALTER VCLUSTER {VCLUSTER_Name} SET VCLUSTER_SIZE = '{VCLUSTER_Size}' "
session.sql(sql_cmd).collect()

print("Done!...nn")


# 5 - Write the result to a new table (80 million rows)
# <-- This is when all previous operations are compiled and executed as a single job
print("Creating target SALES_SUMMARY table...nn")
dfSummary.write.mode("overwrite").saveAsTable("SALES_SUMMARY")
print("Target table created!...")

# 6 - Query the result (80 million rows)
print("Querying the result...n")
dfSales = session.table("SALES_SUMMARY")
dfSales.show()
end_time = time.time()

print("--- It took %s seconds to connect, summarize, and write the result to the new table --- n" % int(end_time - start_time))
print("--- Wrote %s rows to the SALES_SUMMARY table" % dfSales.count())

# 7 - Reduce the virtual compute cluster size to XSMALL
print("Reducing VCLUSTER to XS...n")
sql_cmd = "ALTER VCLUSTER {} SET VCLUSTER_SIZE = 'XSMALL'".format(VCLUSTER_Name)
session.sql(sql_cmd).collect()

print("Done!...n")

```

```
Adjusting to XSMALL ..
Done!...
Creating target SALES_SUMMARY table...
Target table created!...
Querying results...
------------------------------------------------------------------
|         s_name         |   l_partkey   | total_qty | min_qty | max_qty |
------------------------------------------------------------------
| Supplier#000966043     |   1216039     |   173.00  |  9.00   |  50.00  |
| Supplier#000986803     |  17236751     |   164.00  |  5.00   |  41.00  |
| Supplier#000081344     |    81343      |   112.00  |  7.00   |  50.00  |
| Supplier#000905118     |  12405093     |   184.00  |  1.00   |  48.00  |
| Supplier#000922670     |  14172627     |   179.00  |  6.00   |  46.00  |
| Supplier#000873089     |  12373064     |   126.00  |  9.00   |  37.00  |
| Supplier#000389530     |   9889511     |   253.00  |  1.00   |  48.00  |
| Supplier#000668325     |  14668324     |   192.00  |  4.00   |  45.00  |
| Supplier#000788387     |  11538375     |   222.00  |  7.00   |  49.00  |
| Supplier#000196264     |  13946250     |   277.00  |  5.00   |  45.00  |
------------------------------------------------------------------

--- Connecting, aggregating, and writing results to the new table took 75 seconds ---
--- 79975543 rows written to the SALES_SUMMARY table
Scaling down VCLUSTER to XS...
Done!...
```

```python
start_time = time.time()

# 4 - Increase the size of the virtual compute cluster to MEDIUM
print(f"Adjusting {VCLUSTER_Size} to {VCLUSTER_ReSize} ..")

sql_cmd = f"ALTER VCLUSTER {VCLUSTER_Name} SET VCLUSTER_SIZE = '{VCLUSTER_ReSize}'"
session.sql(sql_cmd).collect()

print("Done! ...nn")


# 5 - Write the results to a new table (80 million rows)
# <-- This is when all previous operations are compiled and executed as a single job
print("Creating target SALES_SUMMARY table...nn")
dfSummary.write.mode("overwrite").saveAsTable("SALES_SUMMARY")
print("Target table created! ...")

# 6 - Query the results (80 million rows)
print("Querying results...n")
dfSales = session.table("SALES_SUMMARY")
dfSales.show()
end_time = time.time()
print("--- Connecting, summarizing, and writing results to the new table took %s seconds --- n" % int(end_time - start_time))
print("--- Wrote %s rows to the SALES_SUMMARY table" % dfSales.count())

# 7 - Reduce the size of the virtual compute cluster to XSMALL
print("Reducing VCLUSTER to XSMALL...n")
sql_cmd = f"ALTER VCLUSTER {VCLUSTER_Name} SET VCLUSTER_SIZE = {VCLUSTER_Size}"
session.sql(sql_cmd).collect()

print("Done! ...n")

```

```
Adjusting XSMALL to MEDIUM ..
Done!...
Creating target SALES_SUMMARY table...
Target table created!...
Querying results...
------------------------------------------------------------------
|         s_name         | l_partkey  | total_qty | min_qty | max_qty |
------------------------------------------------------------------
| Supplier#000577084     |  3327080   |   220.00  |  15.00  |  49.00  |
| Supplier#000971635     | 12721622   |   263.00  |   4.00  |  50.00  |
| Supplier#000914390     |  5664384   |   113.00  |   5.00  |  38.00  |
| Supplier#000158186     |  2908183   |   241.00  |   7.00  |  46.00  |
| Supplier#000842304     | 13842303   |   180.00  |  12.00  |  40.00  |
| Supplier#000024822     |  9524803   |   181.00  |   1.00  |  48.00  |
| Supplier#000851711     |  7351696   |   346.00  |   3.00  |  50.00  |
| Supplier#000512255     |  6512254   |   250.00  |   3.00  |  50.00  |
| Supplier#000392018     | 18141999   |   164.00  |   1.00  |  48.00  |
| Supplier#000020477     |  9770467   |    81.00  |   4.00  |  25.00  |
------------------------------------------------------------------

--- Connecting, aggregating, and writing results to new table took 18 seconds ---
--- 79975543 rows written to SALES_SUMMARY table
Scaling down VCLUSTER to XSMALL...
Done!...
```

# **Advantages of Zettapark over Spark and PySpark**

* **Quick Migration** Because the code is basically the same, there is no need to learn a new language
* **Cheaper** Because the computation is completely serverless. It can scale up/down in seconds and only runs when in use (incurring costs).
* **Instant Scaling in Seconds** For the same computing task, the XSMALL virtual computing cluster VCluster takes about 75 seconds, while the MEDIUM specification only takes 20 seconds.
* **Faster** Because all unnecessary data movement is eliminated = less time spent on computation = lower costs
* **Easier to Use** = Less manpower required because computation and storage require almost no maintenance.

**Appendix**:

* [Get the Source Code From Github Repository](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/Zettapark/Zettapark_Data_Engineering_Demo.ipynb)
* [Get the more Zettapark Python API Samples](https://github.com/yunqiqiliang/clickzetta_quickstart/tree/main/Zettapark-examples/Notebook)

^
