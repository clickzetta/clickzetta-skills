# Overview

TPC-H is a decision support benchmark developed by the Transaction Processing Performance Council (TPC), which includes a series of business-oriented ad-hoc queries and concurrent data modifications. This test uses 8 tables, with a data size of 100GB, and tests a total of 22 queries. The main performance metric is the response time for each query.

This report provides you with the test results of Singdata Lakehouse and Trino on the TPC-H test set with a scale of 100GB. The conclusions are as follows:
![](.topwrite/assets/tpch.jpeg)

* Singdata Lakehouse outperforms Trino in overall performance across all 22 queries, with Trino's total time being 9.84 times that of Singdata Lakehouse.
* Singdata Lakehouse outperforms Trino in all queries.

# Test Environment

* **Trino Test Environment**

| **Configuration Item** | **Configuration Information**                                                                                                                                                                |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Server                 | Alibaba Cloud EMR Datalake Cluster Service: Master Node: 1 Alibaba Cloud ECS Server (ecs.g8i.xlarge 4 vCPU 16 GiB) Core Nodes: 2 Alibaba Cloud ECS Servers (ecs.g7.16xlarge 64 vCPU 256 GiB) |
| Network Bandwidth      | 32Gbps                                                                                                                                                                                       |
| Software               | Trino(422)                                                                                                                                                                                   |
| Storage Service        | Alibaba Cloud OSS Object Storage                                                                                                                                                             |
| Data Format            | Parquet, LZ4 Compression                                                                                                                                                                     |

* **Singdata Lakehouse Test Environment**

| Configuration Item | Configuration Information                                                 |
| ------------------ | ------------------------------------------------------------------------- |
| Compute Resources  | XLarge specification compute cluster (128vCPU equivalent computing power) |
| Software           | Alibaba Cloud Shanghai Region - Singdata Lakehouse Service                |
| Storage Service    | Managed Storage, Alibaba Cloud OSS Object Storage                         |

# Test Data

| Table Name | Number of Rows |
| ---------- | -------------- |
| customer   | 15 million     |
| lineitem   | 600 million    |
| nation     | 25             |
| orders     | 150 million    |
| part       | 20 million     |
| partsupp   | 80 million     |
| region     | 5              |
| supplier   | 10 million     |

Statistics were collected for the data tables using Analyze.

# Test Process

## Trino

TPC-H data was uploaded to the object storage service in CSV format files and imported into Hive internal tables (Parquet format, LZ4 compression) using the EMR cluster through external tables. The Hive internal tables and Singdata Lakehouse use the same bucketing and sorting settings.

All data tables were analyzed to collect statistics before executing the TPC-H queries.

## Singdata Lakehouse

### Create Cluster

The test was conducted on Alibaba Cloud OSS using the Singdata Lakehouse XLARGE VCluster. All tables used the Parquet storage format and the same bucketing and sorting rules were set.

```SQL
create vcluster if not exists XLARGE_CLUSTER vcluster_size='XLARGE' vcluster_type='Analytics'  AUTO_RESUME=TRUE AUTO_SUSPEND_IN_SECOND=300 min_replicas=1 max_replicas=1;
```

### Create Table Statement

```SQL
CREATE TABLE demo_examples.tpch_100g_cluster.customer(
  `c_custkey` int not null,
  `c_name` varchar(25) not null,
  `c_address` varchar(40) not null,
  `c_nationkey` int not null,
  `c_phone` varchar(15) not null,
  `c_acctbal` decimal(15,2) not null,
  `c_mktsegment` varchar(10) not null,
  `c_comment` varchar(117) not null)
HASH CLUSTERED BY(`c_custkey`)
SORTED BY(`c_custkey` ASC)
INTO 128 BUCKETS;

CREATE TABLE demo_examples.tpch_100g_cluster.lineitem(
  `l_orderkey` int not null,
  `l_partkey` int not null,
  `l_suppkey` int not null,
  `l_linenumber` int not null,
  `l_quantity` decimal(15,2) not null,
  `l_extendedprice` decimal(15,2) not null,
  `l_discount` decimal(15,2) not null,
  `l_tax` decimal(15,2) not null,
  `l_returnflag` char(1) not null,
  `l_linestatus` char(1) not null,
  `l_shipdate` date not null,
  `l_commitdate` date not null,
  `l_receiptdate` date not null,
  `l_shipinstruct` char(25) not null,
  `l_shipmode` char(10) not null,
  `l_comment` varchar(44) not null)
HASH CLUSTERED BY(`l_orderkey`)
SORTED BY(`l_shipdate` ASC,`l_orderkey` ASC)
INTO 128 BUCKETS;

CREATE TABLE demo_examples.tpch_100g_cluster.nation(
  `n_nationkey` int not null,
  `n_name` char(25) not null,
  `n_regionkey` int not null,
  `n_comment` varchar(152));

CREATE TABLE demo_examples.tpch_100g_cluster.orders(
  `o_orderkey` int not null,
  `o_custkey` int not null,
  `o_orderstatus` char(1) not null,
  `o_totalprice` decimal(15,2) not null,
  `o_orderdate` date not null,
  `o_orderpriority` char(15) not null,
  `o_clerk` char(15) not null,
  `o_shippriority` int not null,
  `o_comment` varchar(79) not null)
HASH CLUSTERED BY(`o_orderkey`)
SORTED BY(`o_orderdate` ASC,`o_orderkey` ASC)
INTO 128 BUCKETS;

CREATE TABLE demo_examples.tpch_100g_cluster.part(
  `p_partkey` int not null,
  `p_name` varchar(55) not null,
  `p_mfgr` char(25) not null,
  `p_brand` char(10) not null,
  `p_type` varchar(25) not null,
  `p_size` int not null,
  `p_container` char(10) not null,
  `p_retailprice` decimal(15,2) not null,
  `p_comment` varchar(23) not null)
HASH CLUSTERED BY(`p_partkey`)
SORTED BY(`p_partkey` ASC)
INTO 128 BUCKETS;

CREATE TABLE demo_examples.tpch_100g_cluster.partsupp(
  `ps_partkey` int not null,
  `ps_suppkey` int not null,
  `ps_availqty` int not null,
  `ps_supplycost` decimal(15,2) not null,
  `ps_comment` varchar(199) not null)
HASH CLUSTERED BY(`ps_partkey`)
SORTED BY(`ps_partkey` ASC)
INTO 128 BUCKETS;

CREATE TABLE demo_examples.tpch_100g_cluster.region(
  `r_regionkey` int not null,
  `r_name` char(25) not null,
  `r_comment` varchar(152));

CREATE TABLE demo_examples.tpch_100g_cluster.supplier(
  `s_suppkey` int not null,
  `s_name` char(25) not null,
  `s_address` varchar(40) not null,
  `s_nationkey` int not null,
  `s_phone` char(15) not null,
  `s_acctbal` decimal(15,2) not null,
  `s_comment` varchar(101) not null)
HASH CLUSTERED BY(`s_suppkey`)
SORTED BY(`s_suppkey` ASC)
INTO 128 BUCKETS;
```

### Execute Query

```SQL
--disable result cache
set cz.sql.enable.shortcut.result.cache=false;
-- Q1
select /*Q1*/
    l_returnflag,
    l_linestatus,
    sum(l_quantity) as sum_qty,
    sum(l_extendedprice) as sum_base_price,
    sum(l_extendedprice * (1 - l_discount)) as sum_disc_price,
    sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge,
    avg(l_quantity) as avg_qty,
    avg(l_extendedprice) as avg_price,
    avg(l_discount) as avg_disc,
    count(*) as count_order
from
    clickzetta_sample_data.tpch_100g.lineitem
where
    l_shipdate <= date '1998-12-01' - interval '85' day
group by
    l_returnflag,
    l_linestatus
order by
    l_returnflag,
    l_linestatus;

-- Q2
select /*Q2*/
s_acctbal, -- account balance
s_name, -- name
n_name, -- nation
p_partkey, -- part number
p_mfgr, -- manufacturer
s_address, -- supplier address
s_phone, -- phone number
s_comment -- remarks
from
clickzetta_sample_data.tpch_100g.part,
clickzetta_sample_data.tpch_100g.supplier,
clickzetta_sample_data.tpch_100g.partsupp,
clickzetta_sample_data.tpch_100g.nation,
clickzetta_sample_data.tpch_100g.region
where
p_partkey = ps_partkey
and s_suppkey = ps_suppkey
and p_size = 15 -- specify size, randomly selected from the range [1, 50]
and p_type like '%BRASS' -- specify type, randomly selected from the range specified by the TPC-H standard
and s_nationkey = n_nationkey
and n_regionkey = r_regionkey
and r_name = 'EUROPE' -- specify region, randomly selected from the range specified by the TPC-H standard
and ps_supplycost = (
select
min(ps_supplycost) -- aggregate function
from   -- tables overlap with the parent query
clickzetta_sample_data.tpch_100g.partsupp,
clickzetta_sample_data.tpch_100g.supplier,
clickzetta_sample_data.tpch_100g.nation,
clickzetta_sample_data.tpch_100g.region
where
p_partkey = ps_partkey
and s_suppkey = ps_suppkey
and s_nationkey = n_nationkey
and n_regionkey = r_regionkey
and r_name = 'EUROPE'
)
order by
s_acctbal desc,
n_name,
s_name,
p_partkey
limit 100;

-- Q3
select /*Q3*/
    l_orderkey,
    sum(l_extendedprice * (1 - l_discount)) as revenue, -- potential revenue, aggregate operation
    o_orderdate,
    o_shippriority
from
    clickzetta_sample_data.tpch_100g.customer,
    clickzetta_sample_data.tpch_100g.orders,
    clickzetta_sample_data.tpch_100g.lineitem
where
    c_mktsegment = 'BUILDING' -- randomly selected from the range specified by the TPC-H standard
    and c_custkey = o_custkey
    and l_orderkey = o_orderkey
    and o_orderdate < '1995-03-15' -- specify date range, randomly selected from [1995-03-01, 1995-03-31]
    and l_shipdate > '1995-03-15'  -- specify date range, randomly selected from [1995-03-01, 1995-03-31]
group by
    l_orderkey, -- order identifier
    o_orderdate,  -- order date
    o_shippriority -- shipping priority
order by
    revenue desc, -- descending sort, list highest potential revenue first
    o_orderdate
limit 10;

-- Q4
select /*Q4*/
    o_orderpriority,
    count(*) as order_count
from
    clickzetta_sample_data.tpch_100g.orders
where
    o_orderdate >= date '1993-10-01'
    and o_orderdate < date '1993-10-01' + interval '3' month
    and exists (
        select
            *
        from
            clickzetta_sample_data.tpch_100g.lineitem
        where
            l_orderkey = o_orderkey
            and l_commitdate < l_receiptdate
    )
group by
    o_orderpriority
order by
    o_orderpriority;

-- Q5
select /*Q5*/
    n_name,
    sum(l_extendedprice * (1 - l_discount)) as revenue
from
    clickzetta_sample_data.tpch_100g.customer,
    clickzetta_sample_data.tpch_100g.orders,
    clickzetta_sample_data.tpch_100g.lineitem,
    clickzetta_sample_data.tpch_100g.supplier,
    clickzetta_sample_data.tpch_100g.nation,
    clickzetta_sample_data.tpch_100g.region
where
    c_custkey = o_custkey
    and l_orderkey = o_orderkey
    and l_suppkey = s_suppkey
    and c_nationkey = s_nationkey
    and s_nationkey = n_nationkey
    and n_regionkey = r_regionkey
    and r_name = 'ASIA' -- specify region, randomly selected from the range specified by the TPC-H standard
    and o_orderdate >= '1994-01-01' -- DATE is January 1st of a randomly selected year from 1993 to 1997
    and o_orderdate < date '1996-01-01' + interval '1' year
group by
    n_name -- group by name
order by
    revenue desc; -- sort by revenue descending, note that GROUP BY and ORDER BY clauses differ

-- Q6
select /*Q6*/
    sum(l_extendedprice * l_discount) as revenue -- potential revenue increase
from
    clickzetta_sample_data.tpch_100g.lineitem
where
    l_shipdate >= '1994-01-01' -- DATE is January 1st of a randomly selected year from [1993, 1997]
    and l_shipdate < date '1996-01-01' + interval '1' year -- within one year
    and l_discount between 0.06 - 0.01 and 0.06 + 0.01
    and l_quantity < 24; -- QUANTITY randomly selected from the range [24, 25]

-- Q7
select/*Q7*/
    supp_nation, -- supplier nation
    cust_nation, -- customer nation
    l_year,
    sum(volume) as revenue -- annual, annual shipping revenue
from
    (
        select
            n1.n_name as supp_nation,
            n2.n_name as cust_nation,
            extract(year from l_shipdate) as l_year,
            l_extendedprice * (1 - l_discount) as volume
        from
            clickzetta_sample_data.tpch_100g.supplier,
            clickzetta_sample_data.tpch_100g.lineitem,
            clickzetta_sample_data.tpch_100g.orders,
            clickzetta_sample_data.tpch_100g.customer,
            clickzetta_sample_data.tpch_100g.nation n1,
            clickzetta_sample_data.tpch_100g.nation n2
        where
            s_suppkey = l_suppkey
            and o_orderkey = l_orderkey
            and c_custkey = o_custkey
            and s_nationkey = n1.n_nationkey
            and c_nationkey = n2.n_nationkey
            and ( -- NATION2 and NATION1 values differ, indicating cross-border shipping query
                (n1.n_name = 'FRANCE' and n2.n_name = 'GERMANY')
                or (n1.n_name = 'GERMANY' and n2.n_name = 'FRANCE')
            )
            and l_shipdate between '1995-01-01' and '1996-12-31'
    ) as shipping
group by
    supp_nation,
    cust_nation,
    l_year
order by
    supp_nation,
    cust_nation,
    l_year;

-- Q8
select /*Q8*/
    o_year, -- year
    sum(case
        when nation = 'BRAZIL' then volume -- specify country, randomly selected from the range specified by the TPC-H standard
        else 0
    end) / sum(volume) as mkt_share -- market share: percentage of revenue for a specific product type; aggregate operation
from
    (
        select
            extract(year from o_orderdate) as o_year, -- extract year
            l_extendedprice * (1 - l_discount) as volume, -- revenue for a specific product type
            n2.n_name as nation
        from
            clickzetta_sample_data.tpch_100g.part,
            clickzetta_sample_data.tpch_100g.supplier,
            clickzetta_sample_data.tpch_100g.lineitem,
            clickzetta_sample_data.tpch_100g.orders,
            clickzetta_sample_data.tpch_100g.customer,
            clickzetta_sample_data.tpch_100g.nation n1,
            clickzetta_sample_data.tpch_100g.nation n2,
            clickzetta_sample_data.tpch_100g.region
        where
            p_partkey = l_partkey
            and s_suppkey = l_suppkey
            and l_orderkey = o_orderkey
            and o_custkey = c_custkey
            and c_nationkey = n1.n_nationkey
            and n1.n_regionkey = r_regionkey
            and r_name = 'AMERICA' -- specify region, randomly selected from the range specified by the TPC-H standard
            and s_nationkey = n2.n_nationkey
            and o_orderdate between '1995-01-01' and '1996-12-31' -- only check 1995 and 1996
            and p_type = 'ECONOMY ANODIZED STEEL' -- specify part type, randomly selected from the range specified by the TPC-H standard
    ) as all_nations
group by
    o_year -- group by year
order by
    o_year; -- sort by year

-- Q9
select /*Q9*/
    nation,
    o_year,
    sum(amount) as sum_profit -- total profit of all ordered parts per country per year
from
    (
        select
            n_name as nation, -- nation
            extract(year from o_orderdate) as o_year, -- extract year
            l_extendedprice * (1 - l_discount) - ps_supplycost * l_quantity as amount -- profit
        from
            clickzetta_sample_data.tpch_100g.part,
            clickzetta_sample_data.tpch_100g.supplier,
            clickzetta_sample_data.tpch_100g.lineitem,
            clickzetta_sample_data.tpch_100g.partsupp,
            clickzetta_sample_data.tpch_100g.orders,
            clickzetta_sample_data.tpch_100g.nation
        where
            s_suppkey = l_suppkey
            and ps_suppkey = l_suppkey
            and ps_partkey = l_partkey
            and p_partkey = l_partkey
            and o_orderkey = l_orderkey
            and s_nationkey = n_nationkey
            and p_name like '%green%' -- LIKE operation, query optimizer may optimize
    ) as profit
group by
    nation, -- nation
    o_year  -- year
order by
    nation, 
    o_year desc;

-- Q10
select /*Q10*/
    c_custkey,
    c_name,
    sum(l_extendedprice * (1 - l_discount)) as revenue,
    c_acctbal,
    n_name,
    c_address,
    c_phone,
    c_comment
from
    clickzetta_sample_data.tpch_100g.customer,
    clickzetta_sample_data.tpch_100g.orders,
    clickzetta_sample_data.tpch_100g.lineitem,
    clickzetta_sample_data.tpch_100g.nation
where
    c_custkey = o_custkey
    and l_orderkey = o_orderkey
    and o_orderdate >= date '1993-04-01'
    and o_orderdate < date '1993-04-01' + interval '3' month
    and l_returnflag = 'R'
    and c_nationkey = n_nationkey
group by
    c_custkey,
    c_name,
    c_acctbal,
    c_phone,
    n_name,
    c_address,
    c_comment
order by
    revenue desc
limit 20;

-- Q11
select /*Q11*/
    ps_partkey,
    sum(ps_supplycost * ps_availqty) as value
from
    clickzetta_sample_data.tpch_100g.partsupp,
    clickzetta_sample_data.tpch_100g.supplier,
    clickzetta_sample_data.tpch_100g.nation
where
    ps_suppkey = s_suppkey
    and s_nationkey = n_nationkey
    and n_name = 'CANADA'
group by
    ps_partkey having
        sum(ps_supplycost * ps_availqty) > (
            select
                sum(ps_supplycost * ps_availqty) * 0.000001000000
            from
                clickzetta_sample_data.tpch_100g.partsupp,
                clickzetta_sample_data.tpch_100g.supplier,
                clickzetta_sample_data.tpch_100g.nation
            where
                ps_suppkey = s_suppkey
                and s_nationkey = n_nationkey
                and n_name = 'CANADA'
        )
order by
    value desc;

-- Q12
select/*Q12*/
    l_shipmode,
    sum(case
        when o_orderpriority = '1-URGENT'
            or o_orderpriority = '2-HIGH'
            then 1
        else 0
    end) as high_line_count,
    sum(case
        when o_orderpriority <> '1-URGENT'
            and o_orderpriority <> '2-HIGH'
            then 1
        else 0
    end) as low_line_count
from
    clickzetta_sample_data.tpch_100g.orders,
    clickzetta_sample_data.tpch_100g.lineitem
where
    o_orderkey = l_orderkey
    and l_shipmode in ('RAIL', 'SHIP')
    and l_commitdate < l_receiptdate
    and l_shipdate < l_commitdate
    and l_receiptdate >= date '1994-01-01'
    and l_receiptdate < date '1994-01-01' + interval '1' year
group by
    l_shipmode
order by
    l_shipmode;

-- Q13
select/*Q13*/
    c_count,
    count(*) as custdist
from
    (
        select
            c_custkey,
            count(o_orderkey) as c_count
        from  -- subquery includes left outer join operation
            clickzetta_sample_data.tpch_100g.customer left outer join clickzetta_sample_data.tpch_100g.orders on
                c_custkey = o_custkey
                and o_comment not like '%special%requests%'
                -- WORD1 is any of the following four possible values: special, pending, unusual, express
                -- WORD2 is any of the following four possible values: packages, requests, accounts, deposits
        group by
            c_custkey
    ) c_orders
group by
    c_count
order by
    custdist desc,
    c_count desc;

-- Q14
select/*14*/
    100.00 * sum(case
        when p_type like 'PROMO%'  -- promotional parts
            then l_extendedprice * (1 - l_discount)  -- revenue at a specific time
        else 0
    end) / sum(l_extendedprice * (1 - l_discount)) as promo_revenue
from
    clickzetta_sample_data.tpch_100g.lineitem,
    clickzetta_sample_data.tpch_100g.part
where
    l_partkey = p_partkey
    and l_shipdate >= date '1994-04-01' -- DATE is the 1st of any month of any year from 1993 to 1997
    and l_shipdate < date '1994-04-01' + interval '1' month;    

-- Q15
select/*Q15*/
    s_suppkey,
    s_name,
    s_address,
    s_phone,
    total_revenue
from
    clickzetta_sample_data.tpch_100g.supplier,
    (
        select
            l_suppkey supplier_no,
            sum(l_extendedprice * (1 - l_discount)) total_revenue
        from
            clickzetta_sample_data.tpch_100g.lineitem
        where
                l_shipdate >= date '1994-05-01'
          and l_shipdate < date '1994-05-01' + interval '3' month
        group by
            l_suppkey
    ) as revenue0
where
    s_suppkey = supplier_no
    and total_revenue = (
        select
            max(total_revenue)
        from 
            (
        select
            l_suppkey supplier_no,
            sum(l_extendedprice * (1 - l_discount)) total_revenue
        from
            clickzetta_sample_data.tpch_100g.lineitem
        where
                l_shipdate >= date '1994-05-01'
          and l_shipdate < date '1994-05-01' + interval '3' month
        group by
            l_suppkey
        ) as revenue0
    )
order by
    s_suppkey;

-- Q16
select/*Q16*/
    p_brand,
    p_type,
    p_size,
    count(distinct ps_suppkey) as supplier_cnt -- aggregate and deduplication operation
from
    clickzetta_sample_data.tpch_100g.partsupp,
    clickzetta_sample_data.tpch_100g.part
where
    p_partkey = ps_partkey
    and p_brand <> 'Brand#45' -- BRAND = Brand#MN, M and N are two letters representing two values, independent of each other, with values between 1 and 5
    and p_type not like 'MEDIUM POLISHED%' -- types and sizes the customer is not interested in
    and p_size in (49, 14, 23, 45, 19, 3, 36, 9) -- TYPEX is a set of eight different values arbitrarily selected between 1 and 50
    and ps_suppkey not in ( -- NOT IN subquery, customer excludes certain suppliers
        select
            s_suppkey
        from
            clickzetta_sample_data.tpch_100g.supplier
        where
            s_comment like '%Customer%Complaints%'
    )
group by
    p_brand,
    p_type,
    p_size
order by  -- sort by count descending, and by brand, type, size ascending
    supplier_cnt desc,  
    p_brand,
    p_type,
    p_size;

-- Q17
select /*Q17*/
    sum(l_extendedprice) / 7.0 as avg_yearly
from
    clickzetta_sample_data.tpch_100g.lineitem,
    clickzetta_sample_data.tpch_100g.part
where
    p_partkey = l_partkey
    and p_brand = 'Brand#23'
    and p_container = 'WRAP BAG'
    and l_quantity < (
        select
            0.2 * avg(l_quantity)
        from
            clickzetta_sample_data.tpch_100g.lineitem
        where
            l_partkey = p_partkey
    );

-- Q18
select /*Q18*/
    c_name,
    c_custkey,
    o_orderkey,
    o_orderdate,
    o_totalprice,
    sum(l_quantity) -- total order quantity
from
    clickzetta_sample_data.tpch_100g.customer,
    clickzetta_sample_data.tpch_100g.orders,
    clickzetta_sample_data.tpch_100g.lineitem
where
    o_orderkey in (
        select
            l_orderkey
        from
            clickzetta_sample_data.tpch_100g.lineitem
        group by
            l_orderkey having
                sum(l_quantity) > 300 -- QUANTITY is any value between 312 and 315
    )
    and c_custkey = o_custkey
    and o_orderkey = l_orderkey
group by
    c_name,
    c_custkey,
    o_orderkey,
    o_orderdate,
    o_totalprice
order by
    o_totalprice desc,
    o_orderdate
limit 100;

-- Q19
select/*Q19*/
    sum(l_extendedprice* (1 - l_discount)) as revenue
from
    clickzetta_sample_data.tpch_100g.lineitem,
    clickzetta_sample_data.tpch_100g.part
where
    (
        p_partkey = l_partkey
        and p_brand = 'Brand#12' 
        and p_container in ('SM CASE', 'SM BOX', 'SM PACK', 'SM PKG') 
        and l_quantity >= 1 and l_quantity <= 1 + 10 
        and p_size between 1 and 5 
        and l_shipmode in ('AIR', 'AIR REG') 
        and l_shipinstruct = 'DELIVER IN PERSON'
    )
    or
    (
        p_partkey = l_partkey
        and p_brand = 'Brand#23'
        and p_container in ('MED BAG', 'MED BOX', 'MED PKG', 'MED PACK')
        and l_quantity >= 10 and l_quantity <= 10 + 10 
        and p_size between 1 and 10
        and l_shipmode in ('AIR', 'AIR REG')
        and l_shipinstruct = 'DELIVER IN PERSON'
    )
    or
    (
        p_partkey = l_partkey
        and p_brand = 'Brand#34'
        and p_container in ('LG CASE', 'LG BOX', 'LG PACK', 'LG PKG')
        and l_quantity >= 20 and l_quantity <= 20 + 10 
        and p_size between 1 and 15
        and l_shipmode in ('AIR', 'AIR REG')
        and l_shipinstruct = 'DELIVER IN PERSON'
    );

-- Q20
select/*Q20*/
    s_name,
    s_address
from
    clickzetta_sample_data.tpch_100g.supplier,
    clickzetta_sample_data.tpch_100g.nation
where
    s_suppkey in (
        select
            ps_suppkey
        from
            clickzetta_sample_data.tpch_100g.partsupp
        where
            ps_partkey in (
                select
                    p_partkey
                from
                    clickzetta_sample_data.tpch_100g.part
                where
                    p_name like 'antique%'
            )
            and ps_availqty > (
                select
                    0.5 * sum(l_quantity)
                from
                    clickzetta_sample_data.tpch_100g.lineitem
                where
                    l_partkey = ps_partkey
                    and l_suppkey = ps_suppkey
                    and l_shipdate >= date '1993-01-01'
                    and l_shipdate < date '1993-01-01' + interval '1' year
            )
    )
    and s_nationkey = n_nationkey
    and n_name = 'IRAQ'
order by
    s_name;

-- Q21
select /*Q21*/
    s_name,
    count(*) as numwait
from
    clickzetta_sample_data.tpch_100g.supplier,
    clickzetta_sample_data.tpch_100g.lineitem l1,
    clickzetta_sample_data.tpch_100g.orders,
    clickzetta_sample_data.tpch_100g.nation
where
    s_suppkey = l1.l_suppkey
    and o_orderkey = l1.l_orderkey
    and o_orderstatus = 'F'
    and l1.l_receiptdate > l1.l_commitdate
    and exists ( -- EXISTS subquery
        select
            *
        from
            clickzetta_sample_data.tpch_100g.lineitem l2
        where
            l2.l_orderkey = l1.l_orderkey
            and l2.l_suppkey <> l1.l_suppkey
    )
    and not exists (-- NOT EXISTS subquery
        select
            *
        from
           clickzetta_sample_data.tpch_100g.lineitem l3
        where
            l3.l_orderkey = l1.l_orderkey
            and l3.l_suppkey <> l1.l_suppkey
            and l3.l_receiptdate > l3.l_commitdate
    )
    and s_nationkey = n_nationkey
    and n_name = 'SAUDI ARABIA' -- any value defined by the TPC-H standard
group by
    s_name
order by
    numwait desc,
    s_name
limit 100;

-- Q22
select/*Q22*/
    cntrycode,
    count(*) as numcust,
    sum(c_acctbal) as totacctbal
from
    ( -- first level subquery
        select
            substring(c_phone from 1 for 2) as cntrycode,
            c_acctbal
        from
            clickzetta_sample_data.tpch_100g.customer
        where
            substring(c_phone from 1 for 2) in
                ('13', '31', '23', '29', '30', '18', '17') -- I1...I7 are any non-repeating values from the possible country codes defined in TPC-H
            and c_acctbal > ( -- second level aggregate subquery
                select
                    avg(c_acctbal)
                from
                    clickzetta_sample_data.tpch_100g.customer
                where
                    c_acctbal > 0.00
                    and substring(c_phone from 1 for 2) in
                        ('13', '31', '23', '29', '30', '18', '17')
            )
            and not exists ( -- second level NOT EXISTS subquery
                select
                    *
                from
                    clickzetta_sample_data.tpch_100g.orders
                where
                    o_custkey = c_custkey
            )
    ) as custsale
group by
    cntrycode
order by
    cntrycode;
 ```
# Test Results

Below are the performance test results of Singdata Lakehouse and Trino on 22 queries, measured in milliseconds (ms). Lower values indicate better performance.
- All queries were pre-warmed once, then executed three times, and the average value was taken as the result.

| Query | Singdata Lakehouse | Trino | Trino vs Singdata Lakehouse |
| --- | ----------- | ----- | -------------------- |
| Q1  | 658         | 3240  | 4.92                 |
| Q2  | 180         | 740   | 4.11                 |
| Q3  | 300         | 1840  | 6.13                 |
| Q4  | 177         | 2970  | 16.78                |
| Q5  | 844         | 1670  | 1.98                 |
| Q6  | 89          | 2550  | 28.65                |
| Q7  | 251         | 1190  | 4.74                 |
| Q8  | 441         | 2400  | 5.44                 |
| Q9  | 794         | 12830 | 16.16                |
| Q10 | 308         | 2520  | 8.18                 |
| Q11 | 151         | 300   | 1.99                 |
| Q12 | 122         | 1060  | 8.69                 |
| Q13 | 532         | 4570  | 8.59                 |
| Q14 | 87          | 2480  | 28.51                |
| Q15 | 155         | 4140  | 26.71                |
| Q16 | 177         | 1670  | 9.44                 |
| Q17 | 257         | 8520  | 33.15                |
| Q18 | 726         | 9280  | 12.78                |
| Q19 | 261         | 910   | 3.49                 |
| Q20 | 197         | 2710  | 13.76                |
| Q21 | 462         | 3650  | 7.90                 |
| Q22 | 233         | 1620  | 6.95                 |
| Total | 7402        | 72860 | 9.84                 |

