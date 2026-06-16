# Built-in Sample Datasets

`clickzetta_sample_data` is a public dataset built into Singdata Lakehouse via the data sharing mechanism. It is available out of the box for every tenant — no application or import required, and it does not count against your storage quota.

Query it directly in SQL using three-part naming:

```sql
SELECT * FROM clickzetta_sample_data.tpch_100g.orders LIMIT 10;
```

It contains 5 schemas covering performance benchmarking, business analytics practice, and AI vector retrieval:

| Schema | Data Content | Scale |
|--------|-------------|-------|
| `tpch_100g` | TPC-H standard benchmark, supply-chain order data | 100 GB, 600 million rows in lineitem |
| `tpcds_10tb` | TPC-DS standard benchmark, retail multi-channel sales data | 10 TB, 28.8 billion rows in store_sales |
| `ecommerce_events_history` | E-commerce user behavior event stream | 110 million rows in history table, 370 million rows in live table |
| `nyc_taxi_tripdata` | New York City ride-hailing trip records | 1.49 billion rows |
| `clickzetta_doc_kb` | Singdata product documentation vector knowledge base | Contains 1024-dimensional embeddings |

## tpch_100g

**Data source**: [TPC-H](https://www.tpc.org/tpch/) is the industry-standard database benchmark, simulating a supply-chain scenario with 8 tables covering orders, parts, suppliers, customers, and more.

**Scale**: 100 GB, 8 tables total.

| Table | Row Count | Description |
|-------|-----------|-------------|
| `lineitem` | 600 million | Order line items, the largest table |
| `orders` | 150 million | Order master table |
| `customer` | 15 million | Customer information |
| `supplier` | 1 million | Supplier information |
| `part` | 2 million | Part information |
| `partsupp` | 8 million | Part-supplier relationships |
| `nation` | 25 | Country dimension |
| `region` | 5 | Region dimension |

**Use cases**:
- Test SQL query performance and compare response times across different VCluster sizes
- Learn multi-table JOIN, aggregation, window function, and other SQL syntax
- Validate index effectiveness (Bloomfilter, inverted index)

**Example query**: Calculate annual revenue by region (TPC-H Q5)

```sql
SELECT
    n.n_name,
    SUM(l.l_extendedprice * (1 - l.l_discount)) AS revenue
FROM
    clickzetta_sample_data.tpch_100g.customer c
    JOIN clickzetta_sample_data.tpch_100g.orders o ON c.c_custkey = o.o_custkey
    JOIN clickzetta_sample_data.tpch_100g.lineitem l ON o.o_orderkey = l.l_orderkey
    JOIN clickzetta_sample_data.tpch_100g.supplier s ON l.l_suppkey = s.s_suppkey
    JOIN clickzetta_sample_data.tpch_100g.nation n ON c.c_nationkey = n.n_nationkey
    JOIN clickzetta_sample_data.tpch_100g.region r ON n.n_regionkey = r.r_regionkey
WHERE
    r.r_name = 'ASIA'
    AND o.o_orderdate >= '1994-01-01'
    AND o.o_orderdate < '1995-01-01'
GROUP BY n.n_name
ORDER BY revenue DESC;
```

## tpcds_10tb

**Data source**: [TPC-DS](https://www.tpc.org/tpcds/) is a more complex retail benchmark than TPC-H, simulating multi-channel (store, catalog, web) sales scenarios with 24 tables and 99 standard queries.

**Scale**: 10 TB, 24 tables total.

| Table | Row Count | Description |
|-------|-----------|-------------|
| `store_sales` | 28.8 billion | Store sales line items |
| `catalog_sales` | 14.4 billion | Catalog sales line items |
| `web_sales` | 7.2 billion | Web sales line items |
| `store_returns` | 2.88 billion | Store return records |
| `inventory` | 1.31 billion | Inventory records |
| `customer` | 65 million | Customer information |
| `item` | 402,000 | Product information |
| `date_dim` | 73,000 | Date dimension |
| Other 16 tables | — | Dimension tables (store, promotion, address, etc.) |

**Use cases**:
- Large-scale stress testing to validate query performance at the 10 TB level
- Test execution plans for complex multi-table JOINs and subqueries
- Compare different VCluster sizes under heavy queries

**Example query**: Calculate quarterly sales by store

```sql
SELECT
    s.s_store_name,
    d.d_year,
    d.d_qoy,
    SUM(ss.ss_net_paid) AS total_sales
FROM
    clickzetta_sample_data.tpcds_10tb.store_sales ss
    JOIN clickzetta_sample_data.tpcds_10tb.store s ON ss.ss_store_sk = s.s_store_sk
    JOIN clickzetta_sample_data.tpcds_10tb.date_dim d ON ss.ss_sold_date_sk = d.d_date_sk
WHERE
    d.d_year = 2001
GROUP BY s.s_store_name, d.d_year, d.d_qoy
ORDER BY d.d_qoy, total_sales DESC
LIMIT 20;
```

> ⚠️ **Note**: The tpcds_10tb dataset is extremely large. It is recommended to use a Large or larger VCluster to avoid query timeouts.

## ecommerce_events_history

**Data source**: From a [Kaggle public dataset](https://www.kaggle.com/datasets/mkechinov/ecommerce-behavior-data-from-multi-category-store), recording user behavior events on a multi-category e-commerce platform, including browsing, adding to cart, and purchasing.

**Scale**: 2 tables.

| Table | Row Count | Description |
|-------|-----------|-------------|
| `ecommerce_events_multicategorystore` | 110 million | Historical event snapshot table |
| `ecommerce_events_multicategorystore_live` | 370 million | Continuously updated live event table with `change_tracking` enabled; supports creating a Table Stream |

**Field descriptions**:

| Field | Type | Description |
|-------|------|-------------|
| `event_time` | varchar | Event occurrence time |
| `event_timestamp` | timestamp_ltz | Event timestamp |
| `event_type` | varchar | Event type: view / cart / purchase |
| `product_id` | varchar | Product ID |
| `category_id` | varchar | Category ID |
| `category_code` | varchar | Category path, e.g. `electronics.smartphone` |
| `brand` | varchar | Brand |
| `price` | decimal(10,2) | Product price |
| `user_id` | varchar | User ID |
| `user_session` | varchar | Session ID |
| `event_date` | date | Event date (partition key) |

**Use cases**:
- Funnel analysis (view → add to cart → purchase conversion rate)
- User retention and repeat purchase analysis
- Category and brand sales ranking
- Incremental data processing practice based on Table Stream

**Example query**: Calculate the conversion funnel by event type

```sql
SELECT
    event_type,
    COUNT(DISTINCT user_id) AS users,
    COUNT(*) AS events
FROM clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore
GROUP BY event_type
ORDER BY events DESC;
```

## nyc_taxi_tripdata

**Data source**: Publicly released trip data from the [New York City Taxi and Limousine Commission (TLC)](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page), covering ride-hailing trips from platforms such as Uber and Lyft (FHVHV: For-Hire Vehicle High Volume).

**Scale**: 1 table, 1.49 billion rows.

**Key fields**:

| Field | Type | Description |
|-------|------|-------------|
| `hvfhs_license_num` | varchar | Platform license number (HV0003=Uber, HV0005=Lyft) |
| `pickup_datetime` | timestamp_ltz | Pickup time |
| `dropoff_datetime` | timestamp_ltz | Dropoff time |
| `trip_miles` | double | Trip distance (miles) |
| `trip_time` | bigint | Trip duration (seconds) |
| `base_passenger_fare` | double | Base passenger fare |
| `tips` | double | Tips |
| `driver_pay` | double | Driver earnings |
| `shared_request_flag` | varchar | Shared ride request (Y/N) |
| `wav_request_flag` | varchar | Wheelchair-accessible vehicle request (Y/N) |

**Use cases**:
- Time-series aggregation analysis (trip volume by hour, by day of week)
- Large-table aggregation performance testing
- Platform comparison analysis (Uber vs Lyft)
- Geospatial data analysis (combined with pickup/dropoff zone fields)

**Example query**: Average trip distance and fare by platform

```sql
SELECT
    hvfhs_license_num,
    COUNT(*) AS trips,
    ROUND(AVG(trip_miles), 2) AS avg_miles,
    ROUND(AVG(trip_time) / 60, 1) AS avg_minutes,
    ROUND(AVG(base_passenger_fare), 2) AS avg_fare
FROM clickzetta_sample_data.nyc_taxi_tripdata.fhvhv_tripdata
GROUP BY hvfhs_license_num
ORDER BY trips DESC;
```

> ⚠️ **Note**: This table has 1.49 billion rows. Full table scans take a long time. It is recommended to add a time range filter in your query, or use a Large or larger VCluster.

## clickzetta_doc_kb

**Data content**: A vector knowledge base of Singdata Lakehouse product documentation. Document content is converted into 1024-dimensional vectors using Alibaba Cloud DashScope's text embedding model, for use in semantic retrieval and AI question answering.

**Scale**: 1 table, `dashscope_clickzetta_elements`.

**Key fields**:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique record ID |
| `type` | string | Element type (Title / NarrativeText / Table, etc.) |
| `filename` | string | Source document filename |
| `text` | string | Raw text content |
| `embeddings` | vector(float, 1024) | 1024-dimensional vector representation of the text |
| `element_type` | string | Document element classification |
| `documents_source` | string | Document source identifier |
| `date_processed` | timestamp_ltz | Vector processing timestamp |

**Use cases**:
- Experience vector similarity retrieval (the `cosine_distance` function)
- Build a RAG (Retrieval-Augmented Generation) Q&A system based on product documentation
- Learn how to use the `AI_EMBEDDING` function together with vector indexes

**Example query**: Retrieve document fragments most relevant to "dynamic table" using vector similarity

```sql
SELECT
    filename,
    type,
    text,
    cosine_distance(embeddings, AI_EMBEDDING('ai_gateway_conn:text-embedding-v4', 'What is a dynamic table')) AS distance
FROM clickzetta_sample_data.clickzetta_doc_kb.dashscope_clickzetta_elements
ORDER BY distance ASC
LIMIT 5;
```

## Related Documentation

- [Get Started with TPC-H Queries Using Sample Data](get-started-with-sample-data.md)
- [TPC-H Performance Benchmark](tpch-benchmark.md)
- [Table Stream](om-table-stream.md)
- [Vector Index](om-inverted-index.md)
- [AI_EMBEDDING Function](sql_functions/ai_embedding.md)
