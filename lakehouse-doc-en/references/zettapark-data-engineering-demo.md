# Data Engineering with Lakehouse Zettapark

This is a very basic data engineering example demonstrating how to perform fundamental DataFrame operations such as reading, grouping, and writing data using Singdata Zettapark Python code. This example uses the free sample database built into Singdata Lakehouse (clickzetta\_sample\_data.tpch\_100g) as the data source.

The steps are as follows:

```
1. Connect to Singdata Lakehouse via Zettapark

2. Join 2 large tables via SupplierKey (LINEITEMS with 600 million rows & SUPPLIER with 1 million rows)

3. Demonstrate on-demand scaling by adjusting the virtual compute cluster to different sizes

4. Compare the execution time of the same task on different virtual compute cluster sizes

    Summarize data by supplier and part number to calculate sum, min, and max (35 million rows)

    Write the resulting DataFrame to a Singdata Lakehouse physical table (80 million rows)
```

You can also run this example directly by [downloading the Jupyter Notebook file](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/Zettapark/Zettapark_Data_Engineering_Demo.ipynb).

**The entire operation -- from adjusting compute resources, reading data, joining, to summarizing -- takes approximately 30 seconds, demonstrating the powerful capabilities, instant scalability, and performance of Singdata Lakehouse.**

## Installing Singdata Zettapark

```python
# !pip install clickzetta-zettapark-python
```

## Connecting to Singdata Lakehouse via Zettapark (Without PySpark)

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
# Read parameters from configuration file
with open('config.json', 'r') as config_file:
config = json.load(config_file)

print("Connecting to Singdata Lakehouse.....\n")


# Create session
session = Session.builder.configs(config).create()

print("Connected successfully!...\n")


```

Connecting to Singdata Lakehouse.....
Connected successfully!...

```python
sql_cmd = f"CREATE VCLUSTER IF NOT EXISTS {VCLUSTER_Name} VCLUSTER_SIZE = {VCLUSTER_Size} AUTO_SUSPEND_IN_SECOND = 10 "
print("XSMALL VCLUSTER ready\n")

session.sql(sql_cmd).collect()

session.use_schema(Schema_Name)
```

XSMALL VCLUSTER ready

> ⚠️ **Note**: The vcluster\_size parameter for compute clusters supports both T-shirt sizes (XSMALL, SMALL, Large, etc.) and numeric values (1, 2, 4, 16, etc.) to provide a richer range of compute cluster specifications for different scenarios. For more information, see: [VCluster Size Specification Change Description](vcluster_size_description.md)

`config.json` file sample ([parameter description](https://doc.clickzetta.com/JDBC-Driver)):

```json
{

  "username": "Replace with your username",

  "password": "Replace with your password",

  "service": "Replace with your service address",

  "instance": "Replace with your instance ID",

  "workspace": "Replace with your workspace",

  "schema": "Replace with your schema",

  "vcluster": "Replace with your virtual cluster",

  "sdk_job_timeout": 60,

  "hints": {

    "sdk.job.timeout": 60,

    "query_tag": "test_conn_hints_zettapark"

  }

}
```

## Starting the Data Engineering Process

```python
from clickzetta.zettapark.functions import col, sum, min, max

print("Joining, Aggregating with 2 large tables(600M & 1M rows) & Writing results to new table(80M rows) ..\n")

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

print("Joining and aggregating two large tables (600M rows and 1M rows), and writing results to new table (80M rows) ..\n")

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
Joining and aggregating two large tables (600M rows and 1M rows), and writing results to new table (80M rows) ..\n
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

## 3. The Same Computation Task Takes Different Time with Different Compute Resources (Virtual Clusters), Demonstrating Elastic Scaling

```python
start_time = time.time()

# 4 - Resize the virtual compute cluster to XSMALL
print(f"Resizing to {VCLUSTER_Size} ..")

sql_cmd = f"ALTER VCLUSTER {VCLUSTER_Name} SET VCLUSTER_SIZE = '{VCLUSTER_Size}' "
session.sql(sql_cmd).collect()

print("Done!...\n\n")


# 5 - Write results to a new table (80 million rows)
# <-- This is when all previous operations compile and execute as a single job
print("Creating target SALES_SUMMARY table...\n\n")
dfSummary.write.mode("overwrite").saveAsTable("SALES_SUMMARY")
print("Target table created!...")

# 6 - Query results (80 million rows)
print("Querying results...\n")
dfSales = session.table("SALES_SUMMARY")
dfSales.show()
end_time = time.time()

print("--- Joining, summarizing, and writing results to new table took %s seconds --- \n" % int(end_time - start_time))
print("--- Wrote %s rows to SALES_SUMMARY table" % dfSales.count())

# 7 - Scale the virtual compute cluster down to XSMALL
print("Scaling VCLUSTER down to XS...\n")
sql_cmd = "ALTER VCLUSTER {} SET VCLUSTER_SIZE = 'XSMALL'".format(VCLUSTER_Name)
session.sql(sql_cmd).collect()

print("Done!...\n")

```

```
Resizing to XSMALL ..
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

--- Joining, summarizing, and writing results to new table took 75 seconds ---
--- Wrote 79975543 rows to SALES_SUMMARY table
Scaling VCLUSTER down to XS...
Done!...
```

```python
start_time = time.time()

# 4 - Increase the virtual compute cluster size to MEDIUM
print(f"Resizing {VCLUSTER_Size} to {VCLUSTER_ReSize} ..")

sql_cmd = f"ALTER VCLUSTER {VCLUSTER_Name} SET VCLUSTER_SIZE = '{VCLUSTER_ReSize}'"
session.sql(sql_cmd).collect()

print("Done!...\n\n")


# 5 - Write results to a new table (80 million rows)
# <-- This is when all previous operations compile and execute as a single job
print("Creating target SALES_SUMMARY table...\n\n")
dfSummary.write.mode("overwrite").saveAsTable("SALES_SUMMARY")
print("Target table created!...")

# 6 - Query results (80 million rows)
print("Querying results...\n")
dfSales = session.table("SALES_SUMMARY")
dfSales.show()
end_time = time.time()
print("--- Joining, summarizing, and writing results to new table took %s seconds --- \n" % int(end_time - start_time))
print("--- Wrote %s rows to SALES_SUMMARY table" % dfSales.count())

# 7 - Scale the virtual compute cluster down to XSMALL
print("Scaling VCLUSTER down to XSMALL...\n")
sql_cmd = f"ALTER VCLUSTER {VCLUSTER_Name} SET VCLUSTER_SIZE = {VCLUSTER_Size}"
session.sql(sql_cmd).collect()

print("Done!...\n")

```

```
Resizing XSMALL to MEDIUM ..
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

--- Joining, summarizing, and writing results to new table took 18 seconds ---
--- Wrote 79975543 rows to SALES_SUMMARY table
Scaling VCLUSTER down to XSMALL...
Done!...
```

# **Advantages of Zettapark over Spark and PySpark**

*   **Quick Migration**: Code is essentially the same as Spark/PySpark, with no need to learn a new language.
*   **Cheaper**: Computation is fully serverless, allowing sub-second scaling (up/down), and only running (incurring costs) when in use.
*   **Sub-Second Instant Scaling**: For the same computation task, the XSMALL virtual compute cluster (VCluster) takes about 75 seconds, while the MEDIUM size takes only about 20 seconds.
*   **Faster**: Eliminates all unnecessary data movement, resulting in shorter computation times and lower costs.
*   **Easier to Use**: Means less human effort, as both compute and storage require almost no maintenance.

^
