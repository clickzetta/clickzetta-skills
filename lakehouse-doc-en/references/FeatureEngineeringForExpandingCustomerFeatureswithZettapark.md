# Feature Engineering For Expanding Customer Features with Zettapark

## Overview

This is an tutorial of feature engineering code using the [TPCH tables](sample-data-using.md) with [Zettapark](zettaparkquickstart.md). In this tutorial, we illustrate how to build derived (aggregated and transformed) features that could support several machine learning tasks. For instance, you could build:

**Customer Segmentation / Churn Prediction**:

* Feature data: Total spending per customer, number of orders, average order amount, customer demographics (e.g., market segment, account balance), and geographic information (nation/region).

* Methods: Aggregation on orders and enrichment via joins with the customer, nation, and region tables.

**Sales Forecasting**:

* Feature data: Time-based measures like total and average sales, order frequency, and trends per customer or region.

* Methods: Aggregations over orders and lineitem details.

**Supplier Performance / Product Sales Analysis**:

* Feature data: For suppliers—total available quantity, total and average supply cost; for products—sales amount and frequency, possibly with categorical transformation (using CASE WHEN on product type).

* Methods: Grouping and aggregating partsupp, lineitem, and part tables, with CASE WHEN conversions for domain-specific categories.

You could [Get the Source Code (Jupyter Notebook ipynb file) From Github Repository](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/Zettapark/FeatureEngineeringForExpandingCustomerFeatureswithZettapark.ipynb) .

## Environment Setup

```python
# !pip install clickzetta_zettapark_python  -U -i https://pypi.tuna.tsinghua.edu.cn/simple
```

^

```python
from clickzetta.zettapark.session import Session
import json
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import pandas as pd

import json

# Read parameters from config file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

print("Connecting to Lakehouse.....\n")

# Create Session
session = Session.builder.configs(config).create()

print("Connected and context as below...\n")

# print(session.sql("SELECT current_instance_id(), current_workspace(),current_workspace_id(), current_schema(), current_user(),current_user_id(), current_vcluster()").collect())
```

```
Connecting to Lakehouse.....
Connected and context as below...
```

```python
TPCH_SIZE_PARAM = 10
CLICKZETTA_SAMPLE_DB = 'clickzetta_sample_data' # Name of Sample Database might be different...

TPCH_SCHEMA = 'tpch_100g'

customer = session.table(f'{CLICKZETTA_SAMPLE_DB}.{TPCH_SCHEMA}.customer') 
lineitem = session.table(f'{CLICKZETTA_SAMPLE_DB}.{TPCH_SCHEMA}.lineitem')  
nation = session.table(f'{CLICKZETTA_SAMPLE_DB}.{TPCH_SCHEMA}.nation')  
orders = session.table(f'{CLICKZETTA_SAMPLE_DB}.{TPCH_SCHEMA}.orders') 
part = session.table(f'{CLICKZETTA_SAMPLE_DB}.{TPCH_SCHEMA}.part')  
partsupp = session.table(f'{CLICKZETTA_SAMPLE_DB}.{TPCH_SCHEMA}.partsupp') 
region = session.table(f'{CLICKZETTA_SAMPLE_DB}.{TPCH_SCHEMA}.region')  
supplier = session.table(f'{CLICKZETTA_SAMPLE_DB}.{TPCH_SCHEMA}.supplier')  
```

## Feature Engineering

```python
from clickzetta.zettapark.functions import col, when, sum as F_sum, count as F_count, avg as F_avg
from decimal import Decimal
```

### 1. Customer Sales Aggregation\*\*

* **Functionality**:
  This code groups the orders table by customer key and aggregates key metrics—such as total sales (sum of order totals), order count, and average order value—per customer. These aggregated metrics are then renamed and joined with the customer table, integrating customer personal details (name, address, account balance, etc.) with their purchasing behavior.

* **Goal**:
  To construct a customer-level sales metrics dataset that can be used for further analyses or predictive modeling tasks such as customer segmentation or churn prediction.

```python
# -----------------------------------------
# 1. Customer Sales Aggregation (from orders)
# -----------------------------------------
customer_sales_agg = orders.groupBy("O_CUSTKEY") \
    .agg(
        F_sum("O_TOTALPRICE").alias("total_sales"),
        F_count("O_ORDERKEY").alias("order_count"),
        F_avg("O_TOTALPRICE").alias("avg_order_value")
    ) \
    .withColumnRenamed("O_CUSTKEY", "customer_sk")

# Join the aggregated sales with customer details
customer_features = customer.join(
    customer_sales_agg,
    customer["C_CUSTKEY"] == customer_sales_agg["customer_sk"],
    "left"
).select(
    customer["C_CUSTKEY"].alias("customer_sk"),
    customer["C_NAME"],
    customer["C_ADDRESS"],
    customer["C_PHONE"],
    customer["C_ACCTBAL"],
    customer["C_MKTSEGMENT"],
    customer_sales_agg["total_sales"],
    customer_sales_agg["order_count"],
    customer_sales_agg["avg_order_value"],
    customer["C_NATIONKEY"]
)

customer_features = customer_features.na.fill({
    "C_NAME": "",                        # String column: empty string
    "C_ADDRESS": "",                     # String column: empty string
    "C_PHONE": "",                       # String column: empty string
    "C_ACCTBAL": Decimal("0.00"),         # Decimal(15,2) value
    "C_MKTSEGMENT": "",                  # String column: empty string
    "total_sales": Decimal("0.00"),       # Decimal(25, 2) value
    "avg_order_value": Decimal("0.000000"), # Decimal(19,6) value
    "order_count": 0                     # Integer is fine
})


# Show the resulting DataFrame (or continue with further feature engineering)
customer_features.show()
```

```
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
|customer_sk  |c_name              |c_address                                 |c_phone          |c_acctbal  |c_mktsegment  |total_sales  |order_count  |avg_order_value  |c_nationkey  |
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
|467          |Customer#000000467  |amwRkh0nDQ6r6MU                           |21-449-581-5158  |9398.51    |MACHINERY     |1701866.04   |12           |141822.170000    |11           |
|521          |Customer#000000521  |MUEAEA1ZuvRofNY453Ckr4Apqk1GlOe           |12-539-480-8897  |5830.69    |MACHINERY     |1569375.53   |8            |196171.941250    |2            |
|475          |Customer#000000475  |JJMbj6myLUzMlbUmg63hNtFv4pWL8nq           |24-485-422-9361  |9043.55    |BUILDING      |2323455.22   |20           |116172.761000    |14           |
|511          |Customer#000000511  |lQC9KfW W77IYtJjAgSZguNzxjY rYk3t6lcxfSh  |23-247-728-9743  |4571.31    |FURNITURE     |2581114.42   |16           |161319.651250    |13           |
|130          |Customer#000000130  |RKPx2OfZy0Vn 8wGWZ7F2EAvmMORl1k8iH        |19-190-993-9281  |5073.58    |HOUSEHOLD     |3100496.60   |22           |140931.663636    |9            |
|542          |Customer#000000542  |XU2ffxnW3TQasrfF0u2KwKWmMarPyY4q7Q        |26-674-545-2517  |3109.96    |BUILDING      |2042094.45   |10           |204209.445000    |16           |
|270          |Customer#000000270  |,rdHVwNKXKAgREU                           |17-241-806-3530  |9192.50    |AUTOMOBILE    |0.00         |0            |0.000000         |7            |
|345          |Customer#000000345  |dGFK ICPKxnsAzlX4UYOUf,n200yyEWhIeG       |19-209-576-4513  |1936.77    |AUTOMOBILE    |0.00         |0            |0.000000         |9            |
|348          |Customer#000000348  |ciP7BWkhOe1IbbVGlqJePBI6ZwqENkS           |23-986-141-5327  |3310.49    |HOUSEHOLD     |0.00         |0            |0.000000         |13           |
|534          |Customer#000000534  |3PI4ZATXq8yaHFt,sZOQccGl  Fc1TA3Y 2       |11-137-389-2888  |6520.97    |AUTOMOBILE    |0.00         |0            |0.000000         |1            |
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

### 2. Geography Features Extraction\*\*

* **Functionality**:
  This code enriches customer data with geographic information by joining customer features (which include a nation key) with the nation table and then further joining with the region table. This process extracts attributes like nation name and region name for each customer.

* **Goal**:
  To add a geographic dimension to the customer dataset, enabling regional performance analysis and supporting models that might use geographic data (e.g., for market segmentation or location-based trend analysis).

```python
# -----------------------------------------
# 2. Geography Features (using nation and region)
# -----------------------------------------
customer_geo = customer_features.join(
    nation,
    customer_features["C_NATIONKEY"] == nation["N_NATIONKEY"],
    "left"
).join(
    region,
    nation["N_REGIONKEY"] == region["R_REGIONKEY"],
    "left"
).select(
    customer_features["customer_sk"],
    nation["N_NAME"].alias("nation_name"),
    region["R_NAME"].alias("region_name"),
    customer_features["C_ACCTBAL"]
)

# Optionally, aggregate region-level metrics
region_agg = customer_geo.groupBy("region_name") \
    .agg(
        F_count("customer_sk").alias("num_customers"),
        F_avg("C_ACCTBAL").alias("avg_acctbal")
    )
```

### 3. Product Sales Features\*\*

* **Functionality**:
  The code aggregates sales data from the lineitem table by grouping records based on the product key. It calculates the total extended price, average extended price, and order count for each product. It then joins these results with the part table and applies conditional logic (CASE WHEN via the `when` function) to convert the product type into a numeric code.

* **Goal**:
  To generate product-level features that encapsulate key sales metrics and to numerically encode product types. These features can be used for product performance analysis, demand forecasting, or integration into recommendation systems.

```python
# -----------------------------------------
# 3. Product Sales Features (from lineitem and part)
# -----------------------------------------
product_sales = lineitem.groupBy("L_PARTKEY") \
    .agg(
        F_sum("L_EXTENDEDPRICE").alias("total_extended_price"),
        F_avg("L_EXTENDEDPRICE").alias("avg_extended_price"),
        F_count("L_ORDERKEY").alias("order_count")
    ) \
    .withColumnRenamed("L_PARTKEY", "part_sk")

# Join with part table and transform product types using CASE WHEN
product_features = part.join(
    product_sales,
    part["P_PARTKEY"] == product_sales["part_sk"],
    "left"
).select(
    part["P_PARTKEY"].alias("part_sk"),
    part["P_NAME"],
    when(col("P_TYPE").like("%ECONOMY%"), 1)
      .when(col("P_TYPE").like("%STANDARD%"), 2)
      .when(col("P_TYPE").like("%PROMO%"), 3)
      .otherwise(0).alias("product_type_code"),
    product_sales["total_extended_price"],
    product_sales["avg_extended_price"],
    product_sales["order_count"]
)

# Replace nulls with type-appropriate values:
product_features = product_features.na.fill({
    "P_NAME": "",                       # For string column, use empty string.
    "total_extended_price": Decimal("0.00"),  # For DecimalType(25,2), use a Decimal with matching precision.
    "avg_extended_price": Decimal("0.000000"),  # For DecimalType(19,6)
    "product_type_code": 0,               # Integer
    "order_count": 0                      # Integer
})

# For example, display the result
product_features.show()
```

```
--------------------------------------------------------------------------------------------------------------------------------
|part_sk  |p_name                                |product_type_code  |total_extended_price  |avg_extended_price  |order_count  |
--------------------------------------------------------------------------------------------------------------------------------
|270      |mint deep white navajo floral         |3                  |802805.22             |30877.123846        |26           |
|130      |gainsboro powder cyan pale rosy       |0                  |792169.97             |25553.870000        |31           |
|467      |cornflower lime midnight plum forest  |2                  |1245756.06            |32783.054211        |38           |
|348      |blush navajo peru chartreuse dim      |0                  |1016148.76            |33871.625333        |30           |
|475      |coral peru forest thistle khaki       |2                  |1174651.38            |35595.496364        |33           |
|511      |red pale plum orchid moccasin         |2                  |693051.41             |31502.336818        |22           |
|542      |light lace gainsboro coral lavender   |0                  |1103543.10            |38053.210345        |29           |
|521      |grey drab honeydew coral pale         |3                  |1317749.04            |38757.324706        |34           |
|345      |cyan frosted spring orange puff       |1                  |828151.10             |29576.825000        |28           |
|534      |bisque saddle hot steel frosted       |2                  |1326940.25            |41466.882813        |32           |
--------------------------------------------------------------------------------------------------------------------------------
```

### 4. Supplier Features

* **Functionality**: This segment first aggregates supplier-related data from the partsupp table by supplier key, computing metrics such as total available quantity, total supply cost, and average supply cost. It then joins these aggregated values with the supplier table to enrich the data with supplier details (name, address, phone). Note that special attention is given to handling null values using type-appropriate defaults.

* **Goal**: To build a comprehensive dataset of supplier features that reflects both operational metrics (from partsupp) and supplier identity (from the supplier table). This dataset supports downstream tasks such as supplier performance evaluation, risk assessment, and supplier classification.

```python
# -----------------------------------------
# 4. Supplier Features (from partsupp and supplier)
# -----------------------------------------
supplier_metrics = partsupp.groupBy("PS_SUPPKEY") \
    .agg(
        F_sum("PS_AVAILQTY").alias("total_avail_qty"),
        F_sum("PS_SUPPLYCOST").alias("total_supply_cost"),
        F_avg("PS_SUPPLYCOST").alias("avg_supply_cost")
    ) \
    .withColumnRenamed("PS_SUPPKEY", "supplier_sk")
    
supplier_features = supplier.join(
    supplier_metrics,
    supplier["S_SUPPKEY"] == supplier_metrics["supplier_sk"],
    "left"
).select(
    supplier["S_SUPPKEY"].alias("supplier_sk"),
    supplier["S_NAME"],
    supplier["S_ADDRESS"],
    supplier["S_PHONE"],
    supplier_metrics["total_avail_qty"],
    supplier_metrics["total_supply_cost"],
    supplier_metrics["avg_supply_cost"]
)

# Use a dictionary in .na.fill() to specify default values with matching data types.
supplier_features = supplier_features.na.fill({
    "S_NAME": "",                          # String column: use an empty string.
    "S_ADDRESS": "",                       # String column: use an empty string.
    "S_PHONE": "",                         # String column: use an empty string.
    "total_supply_cost": Decimal("0.00"),   # DecimalType(25, 2): use a Decimal with proper scale.
    "avg_supply_cost": Decimal("0.000000"), # DecimalType(19, 6): use a Decimal with proper scale.
    # "total_avail_qty" can remain the same if it is integer type.
})

# Optionally, show the resulting DataFrame
supplier_features.show()

```

```
-----------------------------------------------------------------------------------------------------------------------------------------------
|supplier_sk  |s_name              |s_address                       |s_phone          |total_avail_qty  |total_supply_cost  |avg_supply_cost  |
-----------------------------------------------------------------------------------------------------------------------------------------------
|424          |Supplier#000000424  |uOdFKME6fSAI,rvLcpTL            |32-406-948-7901  |440916           |41351.84           |516.898000       |
|423          |Supplier#000000423  |VCgMjClu4IDaVVMwMW0ARf1ho       |34-577-174-3894  |385330           |39224.80           |490.310000       |
|227          |Supplier#000000227  |Qo959Dll Bd7xvfq3ELtCq          |14-215-994-7949  |401470           |40601.39           |507.517375       |
|89           |Supplier#000000089  |fhtzZcSorhud1                   |19-259-876-1014  |403308           |38926.56           |486.582000       |
|441          |Supplier#000000441  |fvmSClCxNTIEspspva              |24-252-393-5381  |404656           |39053.50           |488.168750       |
|421          |Supplier#000000421  |tXZPR dOYjjbGjarXxKPn,1         |18-360-757-8604  |397487           |41888.22           |523.602750       |
|192          |Supplier#000000192  |Tub1t4UlJwZ5U                   |25-585-189-5975  |387833           |38340.94           |479.261750       |
|425          |Supplier#000000425  |a KnEGf,bqEnGd2Wd9Tl            |10-262-132-6639  |421867           |37923.27           |474.040875       |
|115          |Supplier#000000115  |nJ 2t0f7Ve,wL1,6WzGBJLNBUCKlsV  |33-597-248-1220  |375955           |37680.53           |471.006625       |
|144          |Supplier#000000144  |f8tddEKps816HHqNwsKdn3          |30-726-423-7363  |392087           |38941.69           |486.771125       |
-----------------------------------------------------------------------------------------------------------------------------------------------
```

### 5. Combining Customer Features for a Machine Learning Dataset

* **Functionality**: This code merges the customer sales features with the geographic features using the customer key as the join criterion. It also applies a transformation to the customer market segment field, using a series of CASE WHEN conditions to convert categorical market segmentation into a numeric code.

* **Goal**: To create an integrated, multi-dimensional feature dataset that combines purchasing behavior, account information, and geographic as well as market segment data. This enriched dataset is intended for machine learning tasks such as customer segmentation, predicting customer churn, or credit risk modeling.

```python
# -----------------------------------------
# 5. Combine Customer Features for a Machine Learning Dataset
# -----------------------------------------
# As an example, we combine customer sales and geographic features;
# additional transformations (e.g., converting market segment into a numeric code) can be performed using CASE WHEN.

# Explicitly rename customer_features columns to add a prefix
customer_features_prefixed = customer_features.select(
    col("customer_sk").alias("c_customer_sk"),
    col("total_sales").alias("c_total_sales"),
    col("order_count").alias("c_order_count"),
    col("avg_order_value").alias("c_avg_order_value"),
    col("C_ACCTBAL").alias("c_acctbal"),
    col("C_MKTSEGMENT").alias("c_mktsegment")
)

# Similarly, ensure customer_geo has a unique prefix
customer_geo_prefixed = customer_geo.select(
    col("customer_sk").alias("g_customer_sk"),
    col("nation_name").alias("g_nation_name"),
    col("region_name").alias("g_region_name")
)

customer_ml_features = customer_features_prefixed.join(
    customer_geo_prefixed,
    customer_features_prefixed["c_customer_sk"] == customer_geo_prefixed["g_customer_sk"],
    "left"
).select(
    customer_features_prefixed["c_customer_sk"].alias("customer_sk"),
    customer_features_prefixed["c_total_sales"],
    customer_features_prefixed["c_order_count"],
    customer_features_prefixed["c_avg_order_value"],
    customer_geo_prefixed["g_nation_name"].alias("nation_name"),
    customer_geo_prefixed["g_region_name"].alias("region_name"),
    customer_features_prefixed["c_acctbal"],
    when(customer_features_prefixed["c_mktsegment"] == "AUTOMOBILE", 1)
      .when(customer_features_prefixed["c_mktsegment"] == "BUILDING", 2)
      .when(customer_features_prefixed["c_mktsegment"] == "FURNITURE", 3)
      .when(customer_features_prefixed["c_mktsegment"] == "MACHINERY", 4)
      .otherwise(0).alias("mkt_segment_code")
)

customer_ml_features.show()
```

```
------------------------------------------------------------------------------------------------------------------------------
|customer_sk  |c_total_sales  |c_order_count  |c_avg_order_value  |nation_name  |region_name  |c_acctbal  |mkt_segment_code  |
------------------------------------------------------------------------------------------------------------------------------
|475          |2323455.22     |20             |116172.761000      |KENYA        |AFRICA       |9043.55    |2                 |
|467          |1701866.04     |12             |141822.170000      |IRAQ         |MIDDLE EAST  |9398.51    |4                 |
|511          |2581114.42     |16             |161319.651250      |JORDAN       |MIDDLE EAST  |4571.31    |3                 |
|521          |1569375.53     |8              |196171.941250      |BRAZIL       |AMERICA      |5830.69    |4                 |
|542          |2042094.45     |10             |204209.445000      |MOZAMBIQUE   |AFRICA       |3109.96    |2                 |
|130          |3100496.60     |22             |140931.663636      |INDONESIA    |ASIA         |5073.58    |0                 |
|270          |0.00           |0              |0.000000           |GERMANY      |EUROPE       |9192.50    |1                 |
|345          |0.00           |0              |0.000000           |INDONESIA    |ASIA         |1936.77    |1                 |
|348          |0.00           |0              |0.000000           |JORDAN       |MIDDLE EAST  |3310.49    |0                 |
|534          |0.00           |0              |0.000000           |ARGENTINA    |AMERICA      |6520.97    |1                 |
------------------------------------------------------------------------------------------------------------------------------
```

## Feature Store

```python
customer_ml_features.write.mode('overwrite').save_as_table('customer_ml_features')
```

```python
session.close()
```

## Summary and Analysis

### Machine Learning Scenarios and Data Needs

* **Customer Segmentation / Churn Prediction**: You need per-customer features (total spend, order frequency, average order value, account balance, and encoded market segment) combined with geographic details (nation/region).

* **Sales Forecasting**: The time dimension (order dates from orders/lineitem) may be incorporated later along with the aggregated sales figures to forecast future sales.

* **Supplier Performance Analysis / Product Sales Prognosis**: By calculating aggregate supplier metrics (using partsupp and supplier tables) and product performance (from lineitem and part), you can build models to predict supplier reliability or assess product sales potentials.

### Feature Engineering Details

* **Aggregation**: Use groupBy and aggregation functions (sum, count, avg) to compute metrics (total sales, order count, etc.) from transactional tables.

* **Enrichment and Joins**: Integrate relational information (join customer with nation and region, join partsupp with supplier) to attach demographic or geographic details.

* **Transformation (CASE WHEN**): Use the when function to perform conditional transformations such as encoding product types or market segments into numeric codes. This is crucial when machine learning models require numerical inputs.

* **Data Cleaning**: Apply na.fill(0) or other imputation methods to handle missing values, ensuring a robust machine learning dataset.

This code provides a starting point. Depending on the specific machine learning scenario, you may later add time-based window functions, more granular feature splits, or domain-specific transformations. Enjoy exploring these features and building your models!

***

**Appendix**:

* [Get the Source Code From Github Repository](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/Zettapark/FeatureEngineeringForExpandingCustomerFeatureswithZettapark.ipynb)
* [Get the more Zettapark Python API Samples](https://github.com/yunqiqiliang/clickzetta_quickstart/tree/main/Zettapark-examples/Notebook)

^
