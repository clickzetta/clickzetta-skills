# Overview

Star Schema Benchmark (SSB) is a benchmark used to evaluate the performance of OLAP systems. SSB provides a simplified star schema model dataset based on TPC-H, primarily used to test the performance of multi-table join queries under the star schema model. ClickHouse has flattened the star schema model of SSB into a wide table, transforming it into a single table test set. Refer to the [ClickHouse official documentation](https://clickhouse.com/docs/en/getting-started/example-datasets/star-schema).

This report provides the test results of Singdata Lakehouse and ClickHouse on the SSB single table test set at a 100GB scale. The conclusions are as follows:
![](.topwrite/assets/ssb.png)

* Among the 13 queries executed on the SSB single table test set with a 100G dataset, ClickHouse's total execution time is 1.48 times that of Singdata Lakehouse, indicating that Singdata Lakehouse performs better.

# Test Environment

* **ClickHouse Test Environment**

| **Configuration Item** | **Configuration Details**                                      |
| ---------------------- | -------------------------------------------------------------- |
| Server                 | 1 Alibaba Cloud ECS server (ecs.g7.16xlarge 64 vCPU 256 GiB)   |
| Network Bandwidth      | 32Gbps                                                         |
| Software               | ClickHouse 23.3                                                |
| Storage Service        | ESSD high-efficiency cloud disk 200 GB PL1, single disk IOPS limit 50,000 |
| Hardware Cost          | 17.164 RMB/hour                                                |

* **Singdata Lakehouse Test Environment**

| **Configuration Item** | **Singdata Lakehouse Configuration Details** |
| ---------------------- | -------------------------------------------- |
| Compute Resources      | Large specification compute cluster (64 vCPU equivalent computing power) |
| Software               | Alibaba Cloud Shanghai Region - Singdata Lakehouse service |
| Storage Service        | Managed storage, Alibaba Cloud OSS object storage |

# Test Data

The test used the SSB standard dataset, which includes the following tables and record counts:

* **lineorder**: 600 million records
* **customer**: 3 million records
* **part**: 1.4 million records
* **supplier**: 200,000 records
* **dates**: 2,556 records
* **lineorder_flat**: 600 million records (flattened wide table)

# Test Procedure

## ClickHouse

The DDL and query methods are consistent with the ClickHouse official test methods. For details, refer to the [ClickHouse official documentation](https://clickhouse.com/docs/en/getting-started/example-datasets/star-schema).

## Singdata Lakehouse

### Create Cluster

* Create a virtual cluster with Large specifications in Lakehouse
```SQL
create vcluster if not exists LARGE_CLUSTER vcluster_size='LARGE' vcluster_type='Analytics' AUTO_RESUME=TRUE AUTO_SUSPEND_IN_SECOND=300 min_replicas=1 max_replicas=1;
```
### Create Table Statement
```SQL
  --Create table statement
CREATE TABLE demo_examples.ssb_100g.lineorder_flat(
  `lo_orderkey` int not null,
  `lo_linenumber` int not null,
  `lo_custkey` int not null,
  `lo_partkey` int not null,
  `lo_suppkey` int not null,
  `lo_orderdate` date not null,
  `lo_orderpriority` string not null,
  `lo_shippriority` int not null,
  `lo_quantity` int not null,
  `lo_extendedprice` int not null,
  `lo_ordtotalprice` int not null,
  `lo_discount` int not null,
  `lo_revenue` int not null,
  `lo_supplycost` int not null,
  `lo_tax` int not null,
  `lo_commitdate` date not null,
  `lo_shipmode` string not null,
  `c_name` string not null,
  `c_address` string not null,
  `c_city` string not null,
  `c_nation` string not null,
  `c_region` string not null,
  `c_phone` string not null,
  `c_mktsegment` string not null,
  `s_name` string not null,
  `s_address` string not null,
  `s_city` string not null,
  `s_nation` string not null,
  `s_region` string not null,
  `s_phone` string not null,
  `p_name` string not null,
  `p_mfgr` string not null,
  `p_category` string not null,
  `p_brand` string not null,
  `p_color` string not null,
  `p_type` string not null,
  `p_size` int not null,
  `p_container` string not null)
 CLUSTERED BY(lo_orderkey) SORTED BY(lo_orderdate, lo_orderkey) INTO 64 BUCKETS
  PROPERTIES ('cz.storage.parquet.compression'='lz4');

 --Collect statistics
 analyze table lineorder_flat compute statistics for all columns;
```
### Running Queries
```SQL
--Disable result cache
set cz.sql.enable.shortcut.result.cache=false;

--Q1.1
SELECT /*Q1.1*/ sum(LO_EXTENDEDPRICE * LO_DISCOUNT) AS revenue 
FROM lineorder_flat 
WHERE Year(LO_ORDERDATE) = 1993 AND LO_DISCOUNT BETWEEN 1 AND 3 AND LO_QUANTITY < 25;

--Q1.2
SELECT /*Q1.2*/ sum(LO_EXTENDEDPRICE * LO_DISCOUNT) AS revenue 
FROM lineorder_flat 
WHERE Year(LO_ORDERDATE) = 1994 and Month(LO_ORDERDATE) = 1 AND LO_DISCOUNT BETWEEN 4 AND 6 AND LO_QUANTITY BETWEEN 26 AND 35;

--Q1.3
SELECT /*Q1.3*/ sum(LO_EXTENDEDPRICE * LO_DISCOUNT) AS revenue 
FROM lineorder_flat WHERE WeekOfYear(LO_ORDERDATE) = 6 AND Year(LO_ORDERDATE) = 1994 AND LO_DISCOUNT BETWEEN 5 AND 7 AND LO_QUANTITY BETWEEN 26 AND 35;

--Q2.1
SELECT /*Q2.1*/
    sum(LO_REVENUE),
    Year(LO_ORDERDATE) AS year,
    P_BRAND 
FROM lineorder_flat 
WHERE P_CATEGORY = 'MFGR#12' AND S_REGION = 'AMERICA' 
GROUP BY 
    year,
    P_BRAND 
ORDER BY year,P_BRAND;

--Q2.2
SELECT /*Q2.2*/
    sum(LO_REVENUE),
    Year(LO_ORDERDATE) AS year,
    P_BRAND 
FROM lineorder_flat 
WHERE P_BRAND >= 'MFGR#2221' AND P_BRAND <= 'MFGR#2228' AND S_REGION = 'ASIA' GROUP BY year,P_BRAND ORDER BY year,P_BRAND;

--Q2.3
SELECT /*Q2.3*/ sum(LO_REVENUE),Year(LO_ORDERDATE) AS year,P_BRAND FROM lineorder_flat WHERE P_BRAND = 'MFGR#2239' AND S_REGION = 'EUROPE' GROUP BY year, P_BRAND ORDER BY year,P_BRAND;

--Q3.1
SELECT /*Q3.1*/ C_NATION,S_NATION,Year(LO_ORDERDATE) AS year,sum(LO_REVENUE) AS revenue FROM lineorder_flat WHERE C_REGION = 'ASIA' AND S_REGION = 'ASIA' GROUP BY C_NATION,S_NATION,year HAVING year >= 1992 AND year <= 1997 ORDER BY year ASC,revenue DESC;

--Q3.2
SELECT /*Q3.2*/ C_CITY,S_CITY,Year(LO_ORDERDATE) AS year,sum(LO_REVENUE) AS revenue FROM lineorder_flat WHERE C_NATION = 'UNITED STATES' AND S_NATION = 'UNITED STATES' GROUP BY C_CITY,S_CITY,year HAVING year >= 1992 AND year <= 1997 ORDER BY year ASC,revenue DESC;

--Q3.3
SELECT /*Q3.3*/
    C_CITY,
    S_CITY,
    Year(LO_ORDERDATE) AS year,
    sum(LO_REVENUE) AS revenue 
FROM lineorder_flat 
WHERE (C_CITY = 'UNITED KI1' OR C_CITY = 'UNITED KI5') 
AND (S_CITY = 'UNITED KI1' OR S_CITY = 'UNITED KI5') 
GROUP BY C_CITY,S_CITY,year HAVING year >= 1992 AND year <= 1997 
ORDER BY year ASC,revenue DESC;

--Q3.4
SELECT /*Q3.4*/
    C_CITY,
    S_CITY,
    Year(LO_ORDERDATE) AS year,
    sum(LO_REVENUE) AS revenue FROM lineorder_flat 
WHERE (C_CITY = 'UNITED KI1' OR C_CITY = 'UNITED KI5') AND (S_CITY = 'UNITED KI1' OR S_CITY = 'UNITED KI5') AND Year(LO_ORDERDATE) = 1997 AND Month(LO_ORDERDATE) = 12 GROUP BY C_CITY,S_CITY,year ORDER BY year ASC,revenue DESC;

--Q4.1
SELECT /*Q4.1*/ Year(LO_ORDERDATE) AS year,
    C_NATION,
    sum(LO_REVENUE - LO_SUPPLYCOST) AS profit 
FROM lineorder_flat WHERE C_REGION = 'AMERICA' AND S_REGION = 'AMERICA' AND (P_MFGR = 'MFGR#1' OR P_MFGR = 'MFGR#2') GROUP BY year,C_NATION ORDER BY year ASC,C_NATION ASC;

--Q4.2
SELECT /*Q4.2*/ Year(LO_ORDERDATE) AS year,
    S_NATION,
    P_CATEGORY,
    sum(LO_REVENUE - LO_SUPPLYCOST) AS profit 
FROM lineorder_flat 
WHERE C_REGION = 'AMERICA' AND S_REGION = 'AMERICA' AND (P_MFGR = 'MFGR#1' OR P_MFGR = 'MFGR#2') GROUP BY year,S_NATION,P_CATEGORY HAVING year == 1997 OR year == 1998 ORDER BY year ASC,S_NATION ASC,P_CATEGORY ASC;

SELECT /*Q4.3*/ Year(LO_ORDERDATE) AS year,
    S_CITY,
    P_BRAND,
    sum(LO_REVENUE - LO_SUPPLYCOST) AS profit 
FROM lineorder_flat 
WHERE S_NATION = 'UNITED STATES' AND P_CATEGORY = 'MFGR#14' 
GROUP BY year,S_CITY,P_BRAND 
HAVING year = 1997 OR year = 1998 
ORDER BY year ASC,S_CITY ASC,P_BRAND ASC;
```
# Test Results

Below are the performance test results of Lakehouse and ClickHouse on 13 queries, measured in milliseconds (ms). Lower values indicate better performance.

ClickHouse used the default LZ4 compression, and Singdata Lakehouse also used LZ4 compression. All queries were pre-warmed once, then executed three times, and the average value was taken as the result.

| Query | Singdata Lakehouse | ClickHouse-23.3 | ClickHouse vs Lakehouse |
| ----- | ------------------ | --------------- | ----------------------- |
| Q1.1  | 59                 | 48              | 0.81                    |
| Q1.2  | 30                 | 15              | 0.5                     |
| Q1.3  | 28                 | 14              | 0.5                     |
| Q2.1  | 197                | 301             | 1.53                    |
| Q2.2  | 183                | 273             | 1.49                    |
| Q2.3  | 149                | 255             | 1.71                    |
| Q3.1  | 259                | 398             | 1.54                    |
| Q3.2  | 200                | 319             | 1.6                     |
| Q3.3  | 146                | 227             | 1.55                    |
| Q3.4  | 34                 | 18              | 0.53                    |
| Q4.1  | 281                | 469             | 1.67                    |
| Q4.2  | 117                | 160             | 1.37                    |
| Q4.3  | 101                | 148             | 1.47                    |
| SUM   | 1784               | 2645            | 1.48                    |