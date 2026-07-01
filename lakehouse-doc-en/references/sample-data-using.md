# Quick Start Query Analysis Using Sample Data

## Tutorial Overview

Through this tutorial, you will learn how to use the built-in sample datasets of the Lakehouse platform to quickly perform query analysis using SQL without the need to prepare data in advance, thereby evaluating its functionality and performance.

The sample datasets are shared by the Singdata platform under the dataset named CLICKZETTA\_SAMPLE\_DATA, available for query by all accounts. This tutorial will use the TPC-H 100GB dataset as an example to demonstrate how to quickly complete TPC-H test set queries in Lakehouse and evaluate processing performance.

The tutorial will be completed through the following steps:

* Environment Preparation: Check the raw data using the sample dataset and create a compute cluster for testing
* Initiate Queries: Use the Studio Web environment to create SQL queries and complete 22 TPC-H SQL queries
* Change Cluster Size: Adjust the cluster size, expanding it to 4 times the previous size
* Initiate Queries: Use the resized cluster to complete the 22 TPC-H SQL queries again
* Observe the changes in query latency under different cluster specifications

## Step01. Preparation

First, after logging into the Lakehouse Web console and entering the specified workspace, go to **Data** and verify that the tables under `clickzetta_sample_data.tpch_100g` appear in the data object list.

Next, create an independent compute cluster for this test. You can do this through **Compute → Clusters** in the Web console, or by running the SQL command below in **Development**.

```sql
-- Create analytical virtual computing resources
create vcluster if not exists TPCH_100GB vcluster_size='Medium' vcluster_type='Analytics'  AUTO_RESUME=TRUE AUTO_SUSPEND_IN_SECOND=300 min_replicas=1 max_replicas=1 comment 'TPCH 100GB TEST';
```

> Note: The vcluster_size parameter of the compute cluster supports both T-shirt size (XSMALL, SMALL, LARGE, etc.) and numeric (1, 2, 4, 16, etc.) expressions, providing richer compute cluster specifications to meet the needs of different scenarios. For more information, see: [Compute Cluster Size Code Changes](vcluster_size_description.md)

^

## Step02. Perform TPC-H Queries on Sample Data

In **Development**, create a new SQL script, select the `TPCH_100GB` cluster from the **Cluster** dropdown, paste all 22 queries below, select all, and click **Run** to execute them serially.

The query script is as follows:

```sql
-- Execute the job using TPCH_100GB computing resources
use vcluster TPCH_100GB;

-- Set the query tag
set query_tag='tpch100g_benchmark';

-- Q1
select
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
select
s_acctbal, -- Account balance
s_name, -- Name
n_name, -- Country
p_partkey, -- Part number
p_mfgr, -- Manufacturer
s_address, -- Supplier address
s_phone, -- Phone number
s_comment -- Comment
from
clickzetta_sample_data.tpch_100g.part,
clickzetta_sample_data.tpch_100g.supplier,
clickzetta_sample_data.tpch_100g.partsupp,
clickzetta_sample_data.tpch_100g.nation,
clickzetta_sample_data.tpch_100g.region
where
p_partkey = ps_partkey
and s_suppkey = ps_suppkey
and p_size = 15 -- Specified size, randomly chosen within the range [1, 50]
and p_type like '%BRASS' -- Specified type, randomly chosen within the range specified by TPC-H standard
and s_nationkey = n_nationkey
and n_regionkey = r_regionkey
and r_name = 'EUROPE' -- Specified region, randomly chosen within the range specified by TPC-H standard
and ps_supplycost = (
select
min(ps_supplycost) -- Aggregate function
from   -- Overlapping tables with the parent query
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
select
    l_orderkey,
    sum(l_extendedprice * (1 - l_discount)) as revenue, -- Potential revenue, aggregate operation
    o_orderdate,
    o_shippriority
from
    clickzetta_sample_data.tpch_100g.customer,
    clickzetta_sample_data.tpch_100g.orders,
    clickzetta_sample_data.tpch_100g.lineitem
where
    c_mktsegment = 'BUILDING' -- Randomly chosen within the range specified by TPC-H standard
    and c_custkey = o_custkey
    and l_orderkey = o_orderkey
    and o_orderdate < '1995-03-15' -- Specified date range, randomly chosen within [1995-03-01, 1995-03-31]
    and l_shipdate > '1995-03-15'  -- Specified date range, randomly chosen within [1995-03-01, 1995-03-31]
group by
    l_orderkey, -- Order identifier
    o_orderdate,  -- Order date
    o_shippriority -- Shipping priority
order by
    revenue desc, -- Descending order, placing the highest potential revenue at the top
    o_orderdate
limit 10;

-- Q4
select
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
select
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
    and r_name = 'ASIA' -- Specified region, randomly chosen within the range specified by TPC-H standard
    and o_orderdate >= '1994-01-01' -- DATE is randomly chosen from a year between 1993 and 1997, January 1st
    and o_orderdate < date '1996-01-01' + interval '1' year
group by
    n_name -- Group by name
order by
    revenue desc; -- Sort by revenue in descending order, note the difference between group and sort clauses

-- Q6
select
    sum(l_extendedprice * l_discount) as revenue -- Potential revenue increase
from
    clickzetta_sample_data.tpch_100g.lineitem
where
    l_shipdate >= '1994-01-01' -- DATE is randomly chosen from a year between 1993 and 1997, January 1st
    and l_shipdate < date '1996-01-01' + interval '1' year -- Within a year
    and l_discount between 0.06 - 0.01 and 0.06 + 0.01
    and l_quantity < 24; -- QUANTITY is randomly chosen within the range [24, 25]

-- Q7
select
    supp_nation, -- Supplier nation
    cust_nation, -- Customer nation
    l_year,
    sum(volume) as revenue -- Annual shipping revenue
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
            and ( -- Different values for NATION2 and NATION1, indicating cross-country shipping
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
select
    o_year, -- Year
    sum(case
        when nation = 'BRAZIL' then volume -- Specified country, randomly chosen within the range specified by TPC-H standard
        else 0
    end) / sum(volume) as mkt_share -- Market share: percentage of revenue from a specific type of product; aggregate operation
from
    (
        select
            extract(year from o_orderdate) as o_year, -- Extract year
            l_extendedprice * (1 - l_discount) as volume, -- Revenue from a specific type of product
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
            and r_name = 'AMERICA' -- Specified region, randomly chosen within the range specified by TPC-H standard
            and s_nationkey = n2.n_nationkey
            and o_orderdate between '1995-01-01' and '1996-12-31' -- Only query data from 1995 and 1996
            and p_type = 'ECONOMY ANODIZED STEEL' -- Specified part type, randomly chosen within the range specified by TPC-H standard
    ) as all_nations
group by
    o_year -- Group by year
order by
    o_year; -- Sort by year

-- Q9
select
    nation,
    o_year,
    sum(amount) as sum_profit -- Total profit of all ordered parts per country per year
from
    (
        select
            n_name as nation, -- Country
            extract(year from o_orderdate) as o_year, -- Extract year
            l_extendedprice * (1 - l_discount) - ps_supplycost * l_quantity as amount -- Profit
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
            and p_name like '%green%' -- LIKE operation, query optimizer may optimize this
    ) as profit
group by
    nation, -- Country
    o_year  -- Year
order by
    nation,
    o_year desc;

-- Q10
select
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
select
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
select
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
select
    c_count,
    count(*) as custdist
from
    (
        select
            c_custkey,
            count(o_orderkey) as c_count
        from  -- Subquery includes a left outer join operation
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
select
        100.00 * sum(case
                when p_type like 'PROMO%'  -- Promotional parts
                        then l_extendedprice * (1 - l_discount)  -- Revenue at a specific time
                else 0
        end) / sum(l_extendedprice * (1 - l_discount)) as promo_revenue
from
        clickzetta_sample_data.tpch_100g.lineitem,
        clickzetta_sample_data.tpch_100g.part
where
        l_partkey = p_partkey
        and l_shipdate >= date '1994-04-01' -- DATE is the 1st of any month from any year between 1993 and 1997
        and l_shipdate < date '1994-04-01' + interval '1' month;

-- Q15
select
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
select
    p_brand,
    p_type,
    p_size,
    count(distinct ps_suppkey) as supplier_cnt -- Aggregate and deduplication operation
from
    clickzetta_sample_data.tpch_100g.partsupp,
    clickzetta_sample_data.tpch_100g.part
where
    p_partkey = ps_partkey
    and p_brand <> 'Brand#45' -- BRAND = Brand#MN, where M and N are two letters representing two independent values, each ranging from 1 to 5
    and p_type not like 'MEDIUM POLISHED%' -- Types and sizes that consumers are not interested in
    and p_size in (49, 14, 23, 45, 19, 3, 36, 9) -- TYPEX is a randomly chosen set of eight distinct values from 1 to 50
    and ps_suppkey not in ( -- NOT IN subquery, consumers exclude certain suppliers
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
order by  -- Sort by count in descending order, and by brand, type, size in ascending order
    supplier_cnt desc,
    p_brand,
    p_type,
    p_size;

-- Q17
select
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
select
    c_name,
    c_custkey,
    o_orderkey,
    o_orderdate,
    o_totalprice,
    sum(l_quantity) -- Total order quantity
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
select
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
select
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
select
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
    and n_name = 'SAUDI ARABIA' -- Any value defined by the TPC-H standard
group by
    s_name
order by
    numwait desc,
    s_name
limit 100;

-- Q22
select
    cntrycode,
    count(*) as numcust,
    sum(c_acctbal) as totacctbal
from
    ( -- First-level subquery
        select
            substring(c_phone from 1 for 2) as cntrycode,
            c_acctbal
        from
            clickzetta_sample_data.tpch_100g.customer
        where
            substring(c_phone from 1 for 2) in
                ('13', '31', '23', '29', '30', '18', '17') -- I1...I7 are any non-repeating values from the possible country codes defined in TPC-H
            and c_acctbal > ( -- Second-level aggregate subquery
                select
                    avg(c_acctbal)
                from
                    clickzetta_sample_data.tpch_100g.customer
                where
                    c_acctbal > 0.00
                    and substring(c_phone from 1 for 2) in
                        ('13', '31', '23', '29', '30', '18', '17')
            )
            and not exists ( -- Second-level NOT EXISTS subquery
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

After execution, check the runtime of each query in the SQL Editor's **Execution History** tab at the bottom of the page.

If you wish to perform performance testing, run the queries at least twice so the cluster can fully warm up its cache. The second run typically shows significantly lower latency than the first. To view per-query execution details, go to **Compute → Job History** and filter by the tag `tpch100g_benchmark`.

## Step03. Expand the Cluster Size and Query the Sample Data with TPC-H Again

Through **Compute → Clusters**, modify the size of the test cluster from Medium to Large (Large provides twice the compute resources of Medium). Or run the SQL command below:

```sql
-- Modify cluster size
alter vcluster TPCH_100GB SET VCLUSTER_SIZE = 'LARGE';
```

After modification, re-run the 22 TPC-H queries with the resized cluster. The first run after scaling establishes a fresh cache; the second run benefits from full cache warmup and shows further improvement. Overall task runtime is significantly reduced compared to the smaller cluster, demonstrating the linear performance scaling of Singdata Lakehouse compute resources.
