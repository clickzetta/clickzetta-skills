# Multi-Channel Ad Attribution Data Warehouse Best Practices

This guide shows how to integrate impression, click, and conversion events from multiple channels — Google, WeChat, Douyin, and Weibo — to build a unified user touchpoint journey. It produces comparison reports for three attribution models (Last Touch, Linear, and Position-Based) along with ad ROI analysis. Using a main dataset of 5 users and 20 multi-channel ad events, the guide demonstrates the full **OSS PIPE + Kafka PIPE → ODS → DWD → DWS → ADS** pipeline end to end. An additional 3 temporary events are used to verify Table Stream capture, covering three key platform capabilities: Dynamic Table incremental attribution, Inverted Index campaign name search, and Table Stream conversion event capture.

![](/.topwrite/assets/anim-17-ad-attribution.svg)

---

## Overview

The core challenge in multi-channel ad attribution is that event data formats differ across channels, user ID systems are inconsistent, and a single conversion may be claimed by multiple channels.

Singdata Lakehouse addresses these challenges with the following combination:

| Problem | Solution |
|---|---|
| Raw event schemas differ across channels; unified ingestion is needed | OSS PIPE (GA file import) + Kafka PIPE (real-time clickstream), both writing to the Bronze layer |
| Automatic incremental computation across ODS → DWD → DWS → ADS | Dynamic Table with CTE-based attribution models; the system schedules refreshes along the dependency chain |
| Same conversion must be computed in parallel under three attribution models | Three independent DWS Dynamic Tables holding Last Touch / Linear / Position-Based results in parallel |
| Keyword search on campaign names (for example, all "video" campaigns) | Inverted Index for sub-second full-text search on `campaign_name` |
| New conversion events must trigger attribution recomputation | Table Stream capturing new records in `bronze_ad_events` to drive downstream refreshes |

---

## SQL Commands Used

| Command / Function | Purpose | Notes |
|---|---|---|
| `CREATE TABLE` | Create the ODS event table and campaign metadata table | Regular tables used as upstream sources for Dynamic Tables |
| `CREATE BLOOMFILTER INDEX` | Create a Bloomfilter Index on the `user_id` column | Speeds up high-cardinality column point lookups during DWD layer JOINs |
| `CREATE INVERTED INDEX` | Create an Inverted Index on the `campaign_name` column | Enables `MATCH_ALL` full-text search on campaign name keywords |
| `CREATE PIPE` | Create OSS / Kafka continuous ingestion pipelines | Handle GA daily file auto-import and real-time clickstream ingestion respectively |
| `CREATE TABLE STREAM` | Capture new records in `bronze_ad_events` | APPEND_ONLY mode, drives incremental attribution refreshes |
| `CREATE DYNAMIC TABLE` | Create incremental computation tables for DWD / DWS / ADS layers | All three layers refresh incrementally along the dependency chain |
| `REFRESH DYNAMIC TABLE` | Trigger a manual refresh | Use during initial build or debugging |

---

## Prerequisites

All examples in this guide run under the `best_practice_ad_attribution` Schema.

```sql
CREATE SCHEMA IF NOT EXISTS best_practice_ad_attribution;
```

---

## ODS (Raw Data Layer): Multi-Channel Raw Event Table

### Create Tables

```sql
CREATE TABLE IF NOT EXISTS best_practice_ad_attribution.bronze_ad_events (
    event_id     STRING,
    user_id      STRING,
    channel      STRING,
    event_type   STRING,                                -- impression / click / conversion
    event_time   TIMESTAMP,
    campaign_id  STRING,
    creative_id  STRING,
    platform     STRING,                                -- web / app
    region       STRING,
    ingest_time  TIMESTAMP DEFAULT CURRENT_TIMESTAMP() -- auto-filled when PIPE writes
);
```

```sql
CREATE TABLE IF NOT EXISTS best_practice_ad_attribution.bronze_campaign_meta (
    campaign_id   STRING,
    campaign_name STRING,
    channel       STRING,
    budget        DOUBLE,
    start_date    DATE,
    end_date      DATE,
    creative_id   STRING,
    creative_type STRING  -- text / image / video
);
```

### Create Bloomfilter Index

Attribution SQL in the DWD layer performs many JOIN filters on `user_id`, which is a high-cardinality column. A Bloomfilter Index is well-suited for this.

```sql
CREATE BLOOMFILTER INDEX IF NOT EXISTS idx_bf_user_id
ON TABLE bronze_ad_events (user_id);
```

> ⚠️ **Note**: `CREATE BLOOMFILTER INDEX` requires the same Schema context as the target table. Run `USE SCHEMA best_practice_ad_attribution` first, or add `-s best_practice_ad_attribution` to the cz-cli command, otherwise you will see an "index and table must in the same schema" error.

> 💡 **Tip**: The examples below use **cz-cli** (the Singdata Lakehouse command-line tool). If cz-cli is not installed, see the [cz-cli Installation and Usage Guide](../setup_cz_cli.md). You can also run the SQL in **Development → SQL Editor** in Singdata Studio and configure or trigger scheduled tasks under **Studio → Tasks**.

### Create Inverted Index

The operations team needs to search campaigns by keyword — for example, finding all campaigns containing "video". The `PROPERTIES('analyzer'='english')` option enables English tokenization.

Insert the campaign metadata first. The DWD layer uses it to enrich events with campaign name, creative type, and budget; it also serves as the target for Inverted Index search.

```sql
INSERT INTO best_practice_ad_attribution.bronze_campaign_meta
  (campaign_id, campaign_name, channel, budget, start_date, end_date, creative_id, creative_type)
VALUES
  ('camp_001','Google Search Spring Promo',      'google',  50000,  CAST('2024-01-01' AS DATE), CAST('2024-01-31' AS DATE), 'cr_g1',  'text'),
  ('camp_001','Google Search Spring Promo',      'google',  50000,  CAST('2024-01-01' AS DATE), CAST('2024-01-31' AS DATE), 'cr_g2',  'text'),
  ('camp_002','WeChat Moments Brand Awareness',  'wechat',  80000,  CAST('2024-01-01' AS DATE), CAST('2024-01-31' AS DATE), 'cr_w1',  'video'),
  ('camp_002','WeChat Moments Brand Awareness',  'wechat',  80000,  CAST('2024-01-01' AS DATE), CAST('2024-01-31' AS DATE), 'cr_w2',  'image'),
  ('camp_003','Douyin Short Video Retargeting',  'douyin', 120000,  CAST('2024-01-01' AS DATE), CAST('2024-01-31' AS DATE), 'cr_d1',  'video'),
  ('camp_003','Douyin Short Video Retargeting',  'douyin', 120000,  CAST('2024-01-01' AS DATE), CAST('2024-01-31' AS DATE), 'cr_d2',  'video'),
  ('camp_004','Weibo Topic Engagement',          'weibo',   30000,  CAST('2024-01-01' AS DATE), CAST('2024-01-31' AS DATE), 'cr_wb1', 'image');
```

```sql
CREATE INVERTED INDEX IF NOT EXISTS idx_inv_campaign_name
ON TABLE bronze_campaign_meta (campaign_name)
PROPERTIES('analyzer'='english');
```

Build the index so that existing data becomes searchable:

```sql
BUILD INDEX idx_inv_campaign_name ON bronze_campaign_meta;
```

> ⚠️ **Note**: `BUILD INDEX` only accepts table names without a Schema prefix. Run it in the `best_practice_ad_attribution` Schema context or use the `-s best_practice_ad_attribution` parameter. `CREATE INDEX` only applies to data written after the index is created; run `BUILD INDEX` to make existing data searchable.

Verify the full-text search:

```sql
SELECT campaign_id, campaign_name, channel
FROM best_practice_ad_attribution.bronze_campaign_meta
WHERE MATCH_ALL(campaign_name, 'video');
```

```
campaign_id  campaign_name                       channel
-----------  ----------------------------------  -------
camp_003     Douyin Short Video Retargeting      douyin
camp_003     Douyin Short Video Retargeting      douyin
```

The two rows correspond to two creatives under the same campaign (`cr_d1` and `cr_d2`), both matching the "video" keyword.

### Configure OSS PIPE (GA File Import)

Google Analytics daily export log files land in an OSS bucket. The OSS PIPE in LIST_PURGE mode automatically scans for new files and writes them to the Bronze layer.

```sql
-- Create an OSS Storage Connection (replace with your actual AK/SK and endpoint)
CREATE STORAGE CONNECTION IF NOT EXISTS conn_oss_ga
    TYPE = 'OSS'
    ACCESS_ID  = '<your-access-id>'
    ACCESS_KEY = '<your-access-key>'
    ENDPOINT   = 'oss-cn-hangzhou.aliyuncs.com';

-- Mount the bucket to a Volume
CREATE EXTERNAL VOLUME IF NOT EXISTS vol_ga_exports
    TYPE = 'OSS'
    BUCKET = '<your-bucket>'
    PATH   = 'ga-exports/'
    CONNECTION = conn_oss_ga;

-- Create an OSS PIPE; LIST_PURGE mode scans for new CSV files
CREATE PIPE IF NOT EXISTS best_practice_ad_attribution.pipe_ga_events
    VIRTUAL_CLUSTER = 'DEFAULT'
    INGEST_MODE = 'LIST_PURGE'
AS
COPY INTO best_practice_ad_attribution.bronze_ad_events
FROM (
    SELECT
        $1 AS event_id,
        $2 AS user_id,
        'google' AS channel,
        $3 AS event_type,
        CAST($4 AS TIMESTAMP) AS event_time,
        $5 AS campaign_id,
        $6 AS creative_id,
        $7 AS platform,
        $8 AS region,
        CURRENT_TIMESTAMP() AS ingest_time
    FROM @vol_ga_exports
)
USING csv
OPTIONS('header'='true', 'sep'=',');
```

> 💡 **Tip**: LIST_PURGE mode marks a file as processed after it is successfully written, preventing duplicate imports. This suits the GA daily full-file scenario. If you need precise deduplication or support for file replays, use LIST_RETAIN mode and handle idempotency in a downstream Dynamic Table.

### Configure Kafka PIPE (Real-Time Clickstream)

Real-time web and app clickstream events are ingested via Kafka into the same Bronze table.

```sql
-- Create a Kafka Storage Connection
CREATE STORAGE CONNECTION IF NOT EXISTS conn_kafka_clickstream
    TYPE = 'KAFKA'
    KAFKA_BROKERS = '<kafka-broker>:9092';

-- Create a Kafka PIPE; batch consume every 60 seconds
CREATE PIPE IF NOT EXISTS best_practice_ad_attribution.pipe_kafka_clickstream
    VIRTUAL_CLUSTER    = 'DEFAULT'
    BATCH_INTERVAL_IN_SECONDS = '60'
AS
COPY INTO best_practice_ad_attribution.bronze_ad_events
FROM (
    SELECT
        get_json_object(value, '$.event_id')                         AS event_id,
        get_json_object(value, '$.user_id')                          AS user_id,
        get_json_object(value, '$.channel')                          AS channel,
        get_json_object(value, '$.event_type')                       AS event_type,
        CAST(get_json_object(value, '$.event_time') AS TIMESTAMP)    AS event_time,
        get_json_object(value, '$.campaign_id')                      AS campaign_id,
        get_json_object(value, '$.creative_id')                      AS creative_id,
        get_json_object(value, '$.platform')                         AS platform,
        get_json_object(value, '$.region')                           AS region,
        CURRENT_TIMESTAMP()                                          AS ingest_time
    FROM READ_KAFKA(
        '<kafka-broker>:9092',
        'ad_clickstream',  -- topic name
        '', 'cz_ad_consumer',
        '','','','',
        'json', 'json', 0, map()
    )
);
```

### Load Sample Data

**Import from a local CSV file (recommended)**

```sql
-- Step 1: Upload the local CSV file to User Volume via SQL PUT
PUT '/path/to/your/bronze_ad_events.csv' TO USER VOLUME FILE 'bronze_ad_events.csv';
```

```sql
-- Step 2: COPY INTO the table from User Volume
COPY INTO best_practice_ad_attribution.bronze_ad_events
FROM USER VOLUME
USING csv
OPTIONS('header'='true', 'sep'=',', 'nullValue'='')
FILES ('bronze_ad_events.csv');
```

You can also insert a small batch of test data inline (no CSV file required):

```sql
INSERT INTO best_practice_ad_attribution.bronze_ad_events
  (event_id, user_id, channel, event_type, event_time, campaign_id, creative_id, platform, region)
VALUES
  ('e001','u001','google',     'impression', CAST('2024-01-01 08:00:00' AS TIMESTAMP),'camp_001','cr_g1','web','cn-north'),
  ('e002','u001','google',     'click',      CAST('2024-01-01 08:05:00' AS TIMESTAMP),'camp_001','cr_g1','web','cn-north'),
  ('e003','u001','wechat',     'impression', CAST('2024-01-01 09:00:00' AS TIMESTAMP),'camp_002','cr_w1','app','cn-north'),
  ('e004','u001','wechat',     'click',      CAST('2024-01-01 09:10:00' AS TIMESTAMP),'camp_002','cr_w1','app','cn-north'),
  ('e005','u001','wechat',     'conversion', CAST('2024-01-01 10:30:00' AS TIMESTAMP),'camp_002','cr_w1','app','cn-north'),
  ('e006','u002','douyin',     'impression', CAST('2024-01-01 10:00:00' AS TIMESTAMP),'camp_003','cr_d1','app','cn-south'),
  ('e007','u002','douyin',     'click',      CAST('2024-01-01 10:15:00' AS TIMESTAMP),'camp_003','cr_d1','app','cn-south'),
  ('e008','u002','google',     'click',      CAST('2024-01-01 11:00:00' AS TIMESTAMP),'camp_001','cr_g2','web','cn-south'),
  ('e009','u002','google',     'conversion', CAST('2024-01-01 11:45:00' AS TIMESTAMP),'camp_001','cr_g2','web','cn-south'),
  ('e010','u003','weibo',      'impression', CAST('2024-01-01 12:00:00' AS TIMESTAMP),'camp_004','cr_wb1','web','cn-east'),
  ('e011','u003','weibo',      'click',      CAST('2024-01-01 12:20:00' AS TIMESTAMP),'camp_004','cr_wb1','web','cn-east'),
  ('e012','u003','douyin',     'impression', CAST('2024-01-01 13:00:00' AS TIMESTAMP),'camp_003','cr_d2','app','cn-east'),
  ('e013','u003','douyin',     'click',      CAST('2024-01-01 13:10:00' AS TIMESTAMP),'camp_003','cr_d2','app','cn-east'),
  ('e014','u003','douyin',     'conversion', CAST('2024-01-01 14:00:00' AS TIMESTAMP),'camp_003','cr_d2','app','cn-east'),
  ('e015','u004','google',     'impression', CAST('2024-01-01 14:00:00' AS TIMESTAMP),'camp_001','cr_g1','web','cn-north'),
  ('e016','u004','google',     'click',      CAST('2024-01-01 14:05:00' AS TIMESTAMP),'camp_001','cr_g1','web','cn-north'),
  ('e017','u004','wechat',     'impression', CAST('2024-01-01 15:00:00' AS TIMESTAMP),'camp_002','cr_w2','app','cn-north'),
  ('e018','u004','wechat',     'conversion', CAST('2024-01-01 16:00:00' AS TIMESTAMP),'camp_002','cr_w2','app','cn-north'),
  ('e019','u005','douyin',     'click',      CAST('2024-01-01 16:00:00' AS TIMESTAMP),'camp_003','cr_d1','app','cn-west'),
  ('e020','u005','douyin',     'conversion', CAST('2024-01-01 17:00:00' AS TIMESTAMP),'camp_003','cr_d1','app','cn-west');
```

### Enable Change Tracking and Create Table Stream

Table Stream captures new conversion events in `bronze_ad_events` and triggers incremental attribution recomputation in downstream Dynamic Tables. Enable `change_tracking` on the table before use.

```sql
ALTER TABLE best_practice_ad_attribution.bronze_ad_events
SET TBLPROPERTIES ('change_tracking' = 'true');

CREATE TABLE STREAM IF NOT EXISTS best_practice_ad_attribution.stream_conversion_events
ON TABLE best_practice_ad_attribution.bronze_ad_events
WITH PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY');
```

> 💡 **Tip**: Use APPEND_ONLY mode because the ad event table is append-only (no UPDATEs or DELETEs). This mode performs better than STANDARD mode. The Stream only records rows written after it is created; historical data that existed before the Stream was created does not appear in it.

Verify Stream capture. The following 3 events for `u006` are used only to confirm that the Stream captures INSERTs made after its creation. They do not participate in subsequent DWD / DWS / ADS attribution calculations.

```sql
INSERT INTO best_practice_ad_attribution.bronze_ad_events
  (event_id, user_id, channel, event_type, event_time, campaign_id, creative_id, platform, region)
VALUES
  ('e021','u006','google','impression', CAST('2024-01-02 09:00:00' AS TIMESTAMP),'camp_001','cr_g1','web','cn-north'),
  ('e022','u006','google','click',      CAST('2024-01-02 09:05:00' AS TIMESTAMP),'camp_001','cr_g1','web','cn-north'),
  ('e023','u006','google','conversion', CAST('2024-01-02 09:30:00' AS TIMESTAMP),'camp_001','cr_g1','web','cn-north');

SELECT __change_type, event_id, user_id, channel, event_type
FROM best_practice_ad_attribution.stream_conversion_events;
```

```
__change_type  event_id  user_id  channel  event_type
-------------  --------  -------  -------  ----------
INSERT         e021      u006     google   impression
INSERT         e022      u006     google   click
INSERT         e023      u006     google   conversion
```

The Stream captured 3 new records. To keep the main sample for the subsequent attribution sections at 5 users and 20 events, delete these 3 temporary verification records after querying the Stream.

```sql
DELETE FROM best_practice_ad_attribution.bronze_ad_events
WHERE event_id IN ('e021', 'e022', 'e023');
```

Downstream Dynamic Tables automatically detect new upstream data on the next refresh cycle and compute incrementally. The attribution results in the remainder of this guide are based on the cleaned main dataset, so the Last Touch google conversion count remains 1.

---

## DWD (Detail Data Layer): User Touchpoint Journey Table

### Create Table

The DWD layer JOINs the Bronze event table with the campaign metadata to add `campaign_name` and `creative_type`. It uses `ROW_NUMBER` to assign a `touch_seq` number to each touchpoint in a user's sequence.

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_ad_attribution.dwd_user_journey
REFRESH INTERVAL 5 MINUTE VCLUSTER DEFAULT
AS
SELECT
    e.user_id,
    e.channel,
    e.event_type,
    e.event_time,
    e.campaign_id,
    e.creative_id,
    e.platform,
    e.region,
    m.campaign_name,
    m.creative_type,
    m.budget,
    ROW_NUMBER() OVER (PARTITION BY e.user_id ORDER BY e.event_time) AS touch_seq
FROM best_practice_ad_attribution.bronze_ad_events e
LEFT JOIN best_practice_ad_attribution.bronze_campaign_meta m
    ON e.campaign_id = m.campaign_id AND e.creative_id = m.creative_id;
```

Trigger the initial refresh manually:

```sql
REFRESH DYNAMIC TABLE best_practice_ad_attribution.dwd_user_journey;
```

Query results (first 10 rows):

```sql
SELECT user_id, channel, event_type, event_time, campaign_name, touch_seq
FROM best_practice_ad_attribution.dwd_user_journey
ORDER BY user_id, touch_seq
LIMIT 10;
```

```
user_id  channel  event_type   event_time            campaign_name                     touch_seq
-------  -------  ----------   -------------------   --------------------------------  ---------
u001     google   impression   2024-01-01T08:00:00   Google Search Spring Promo        1
u001     google   click        2024-01-01T08:05:00   Google Search Spring Promo        2
u001     wechat   impression   2024-01-01T09:00:00   WeChat Moments Brand Awareness    3
u001     wechat   click        2024-01-01T09:10:00   WeChat Moments Brand Awareness    4
u001     wechat   conversion   2024-01-01T10:30:00   WeChat Moments Brand Awareness    5
u002     douyin   impression   2024-01-01T10:00:00   Douyin Short Video Retargeting    1
u002     douyin   click        2024-01-01T10:15:00   Douyin Short Video Retargeting    2
u002     google   click        2024-01-01T11:00:00   Google Search Spring Promo        3
u002     google   conversion   2024-01-01T11:45:00   Google Search Spring Promo        4
u003     weibo    impression   2024-01-01T12:00:00   Weibo Topic Engagement            1
```

`touch_seq` is numbered in chronological order. Before converting on WeChat, u001 first saw Google ad impressions and clicks (`touch_seq=1,2`), then WeChat impressions and clicks (`touch_seq=3,4`), and finally converted on WeChat (`touch_seq=5`).

---

## DWS (Summary Data Layer): Three Attribution Models

The DWS layer maintains three attribution models in parallel using three independent Dynamic Tables, without interference, so the operations team can compare results as needed.

### Last Touch Attribution

Attributes 100% of conversion value to the channel of the most recent touchpoint (click or impression) before the conversion.

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_ad_attribution.dws_attribution_last_touch
REFRESH INTERVAL 5 MINUTE VCLUSTER DEFAULT
AS
WITH conversions AS (
    SELECT user_id, event_time AS conv_time, campaign_id, channel
    FROM best_practice_ad_attribution.dwd_user_journey
    WHERE event_type = 'conversion'
),
last_touch AS (
    SELECT
        c.user_id,
        c.conv_time,
        j.channel       AS attributed_channel,
        j.campaign_name AS attributed_campaign_name
    FROM conversions c
    JOIN best_practice_ad_attribution.dwd_user_journey j
        ON c.user_id = j.user_id
        AND j.event_type IN ('click', 'impression')
        AND j.event_time <= c.conv_time
    WHERE j.touch_seq = (
        SELECT MAX(touch_seq)
        FROM best_practice_ad_attribution.dwd_user_journey j2
        WHERE j2.user_id = c.user_id
          AND j2.event_type IN ('click', 'impression')
          AND j2.event_time <= c.conv_time
    )
)
SELECT
    attributed_channel,
    attributed_campaign_name,
    COUNT(*)       AS conversions,
    1.0 * COUNT(*) AS attributed_value
FROM last_touch
GROUP BY attributed_channel, attributed_campaign_name;
```

```sql
REFRESH DYNAMIC TABLE best_practice_ad_attribution.dws_attribution_last_touch;
SELECT *
FROM best_practice_ad_attribution.dws_attribution_last_touch
ORDER BY conversions DESC, attributed_channel DESC;
```

```
attributed_channel  attributed_campaign_name           conversions  attributed_value
------------------  --------------------------------   -----------  ----------------
wechat              WeChat Moments Brand Awareness     2            2.0
douyin              Douyin Short Video Retargeting     2            2.0
google              Google Search Spring Promo         1            1.0
```

The Last Touch model attributes conversions entirely to the last touchpoint. WeChat and Douyin each get 2 conversions. This understates Google's role earlier in the user decision path — u001 saw Google ads before ultimately converting on WeChat.

### Linear Attribution

Distributes conversion value equally across all touchpoints in the path.

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_ad_attribution.dws_attribution_linear
REFRESH INTERVAL 5 MINUTE VCLUSTER DEFAULT
AS
WITH conversions AS (
    SELECT user_id, event_time AS conv_time
    FROM best_practice_ad_attribution.dwd_user_journey
    WHERE event_type = 'conversion'
),
touchpoints AS (
    SELECT
        c.user_id,
        j.channel,
        j.campaign_name,
        j.event_time,
        COUNT(*) OVER (PARTITION BY c.user_id) AS total_touches
    FROM conversions c
    JOIN best_practice_ad_attribution.dwd_user_journey j
        ON c.user_id = j.user_id
        AND j.event_type IN ('click', 'impression')
        AND j.event_time <= c.conv_time
)
SELECT
    channel             AS attributed_channel,
    campaign_name       AS attributed_campaign_name,
    COUNT(*)            AS touch_count,
    ROUND(SUM(1.0 / total_touches), 4) AS attributed_value
FROM touchpoints
GROUP BY channel, campaign_name
ORDER BY attributed_value DESC;
```

```sql
REFRESH DYNAMIC TABLE best_practice_ad_attribution.dws_attribution_linear;
SELECT * FROM best_practice_ad_attribution.dws_attribution_linear ORDER BY attributed_value DESC;
```

```
attributed_channel  attributed_campaign_name           touch_count  attributed_value
------------------  --------------------------------   -----------  ----------------
douyin              Douyin Short Video Retargeting     5            2.1667
google              Google Search Spring Promo         5            1.5000
wechat              WeChat Moments Brand Awareness     3            0.8333
weibo               Weibo Topic Engagement             2            0.5000
```

The Linear model reflects cross-channel contribution: Douyin has the most touchpoints (5) and receives the highest attributed value; Google also has 5 touchpoints but longer user paths reduce its per-touch share to 1.5. Weibo drove no direct conversions but participated in users' decision paths, earning 0.5 in attributed value.

### Position-Based Attribution (U-Shaped Attribution)

First touch and last touch each receive 40% weight; middle touchpoints share the remaining 20%. This model emphasizes the dual value of acquiring new users (first touch) and closing conversions (last touch).

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_ad_attribution.dws_attribution_position_based
REFRESH INTERVAL 5 MINUTE VCLUSTER DEFAULT
AS
WITH conversions AS (
    SELECT user_id, event_time AS conv_time
    FROM best_practice_ad_attribution.dwd_user_journey
    WHERE event_type = 'conversion'
),
touchpoints AS (
    SELECT
        c.user_id,
        j.channel,
        j.campaign_name,
        j.touch_seq,
        j.event_time,
        MIN(j.touch_seq) OVER (PARTITION BY c.user_id) AS first_touch,
        MAX(j.touch_seq) OVER (PARTITION BY c.user_id) AS last_touch_seq,
        COUNT(*) OVER (PARTITION BY c.user_id)          AS total_touches
    FROM conversions c
    JOIN best_practice_ad_attribution.dwd_user_journey j
        ON c.user_id = j.user_id
        AND j.event_type IN ('click', 'impression')
        AND j.event_time <= c.conv_time
),
with_weight AS (
    SELECT
        user_id,
        channel,
        campaign_name,
        CASE
            WHEN touch_seq = first_touch AND touch_seq = last_touch_seq THEN 1.0
            WHEN touch_seq = first_touch OR touch_seq = last_touch_seq  THEN 0.4
            ELSE 0.2 / GREATEST(total_touches - 2, 1)
        END AS weight
    FROM touchpoints
)
SELECT
    channel             AS attributed_channel,
    campaign_name       AS attributed_campaign_name,
    COUNT(*)            AS touch_count,
    ROUND(SUM(weight), 4) AS attributed_value
FROM with_weight
GROUP BY channel, campaign_name
ORDER BY attributed_value DESC;
```

```sql
REFRESH DYNAMIC TABLE best_practice_ad_attribution.dws_attribution_position_based;
SELECT * FROM best_practice_ad_attribution.dws_attribution_position_based ORDER BY attributed_value DESC;
```

```
attributed_channel  attributed_campaign_name           touch_count  attributed_value
------------------  --------------------------------   -----------  ----------------
douyin              Douyin Short Video Retargeting     5            2.1000
google              Google Search Spring Promo         5            1.5000
wechat              WeChat Moments Brand Awareness     3            0.9000
weibo               Weibo Topic Engagement             2            0.5000
```

Compared with Linear, Position-Based gives WeChat a higher weight (0.9 vs 0.83) because WeChat is the last touchpoint for multiple conversions (40% weight), rather than sharing equally. This model suits marketing strategies that emphasize both user acquisition and conversion closure.

---

## ADS (Application Data Layer): Campaign ROI Report

The ADS layer aggregates the output of all three attribution models. Combined with campaign budgets, it produces a complete set of ROI metrics for BI tools to consume.

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_ad_attribution.ads_campaign_roi
REFRESH INTERVAL 10 MINUTE VCLUSTER DEFAULT
AS
WITH evt_stats AS (
    SELECT
        campaign_id,
        campaign_name,
        channel,
        creative_type,
        budget,
        COUNT(CASE WHEN event_type = 'impression' THEN 1 END) AS impressions,
        COUNT(CASE WHEN event_type = 'click'      THEN 1 END) AS clicks,
        COUNT(CASE WHEN event_type = 'conversion' THEN 1 END) AS conversions,
        COUNT(DISTINCT user_id)                                AS unique_users
    FROM best_practice_ad_attribution.dwd_user_journey
    GROUP BY campaign_id, campaign_name, channel, creative_type, budget
)
SELECT
    campaign_id,
    campaign_name,
    channel,
    creative_type,
    budget,
    impressions,
    clicks,
    conversions,
    unique_users,
    ROUND(CASE WHEN impressions > 0 THEN 100.0 * clicks / impressions ELSE 0 END, 2) AS ctr_pct,
    ROUND(CASE WHEN clicks > 0 THEN 100.0 * conversions / clicks ELSE 0 END, 2)      AS cvr_pct,
    ROUND(CASE WHEN conversions > 0 THEN budget / conversions ELSE NULL END, 2)       AS cost_per_conversion
FROM evt_stats
ORDER BY conversions DESC;
```

```sql
REFRESH DYNAMIC TABLE best_practice_ad_attribution.ads_campaign_roi;
SELECT campaign_name, channel, impressions, clicks, conversions, ctr_pct, cvr_pct, cost_per_conversion
FROM best_practice_ad_attribution.ads_campaign_roi
ORDER BY conversions DESC, channel, clicks DESC;
```

```
campaign_name                       channel  impressions  clicks  conversions  ctr_pct  cvr_pct  cost_per_conversion
----------------------------------  -------  -----------  ------  -----------  -------  -------  -------------------
Douyin Short Video Retargeting      douyin   2            3       2            150.00   66.67    60000
Google Search Spring Promo          google   2            3       1            150.00   33.33    50000
WeChat Moments Brand Awareness      wechat   1            1       1            100.00   100.00   80000
WeChat Moments Brand Awareness      wechat   1            0       1            0.00     0.00     80000
Weibo Topic Engagement              weibo    1            1       0            100.00   0.00     null
```

> 💡 **Tip**: The WeChat campaign appears in two rows because two creatives (`cr_w1` video and `cr_w2` image) each have their own impression/click/conversion data, and `creative_type` is included in the GROUP BY. To aggregate at the campaign level, remove the `creative_type` dimension and re-aggregate.

Douyin's `cost_per_conversion = 60000` (budget 120,000 / 2 conversions); Google's is 50,000. The two channels have similar cost per conversion, but Douyin delivers twice as many conversions, making its overall ROI stronger. Weibo drove no direct conversions and would appear to have no contribution under the Last Touch model, but it has path value under Linear and Position-Based models — which shows why comparing multiple attribution models is essential for evaluating assist channels.

---

## Notes

- **Bloomfilter Index Schema context**: Both `CREATE BLOOMFILTER INDEX` and `BUILD INDEX` require the same Schema context as the target table. Run `USE SCHEMA best_practice_ad_attribution` first, or use the `-s best_practice_ad_attribution` parameter.
- **Inverted Index and existing data**: `CREATE INVERTED INDEX` applies only to data written after the index is created. Run `BUILD INDEX` to make existing data searchable via `MATCH_ALL`.
- **Table Stream and historical data**: A Stream only captures writes that occur after it is created; records that existed before the Stream was created are not included. To run attribution on historical data, query `bronze_ad_events` directly rather than the Stream.
- **Dynamic Table refresh order**: The three DWS Dynamic Tables consume new data only after `dwd_user_journey` in the DWD layer has finished refreshing; the ADS layer depends on DWS results in turn. The system determines the refresh order automatically from the reference graph; no manual orchestration is needed.
- **Attribution window**: All three attribution models in this guide count all touchpoints for a user before the conversion, with no lookback window. In practice, add a time window filter (for example, touchpoints within 30 days before conversion) by adding `AND j.event_time >= c.conv_time - INTERVAL 30 DAY` to the JOIN condition.
- **NULL cost_per_conversion**: When a campaign has no conversions in the reporting window, `cost_per_conversion` returns NULL by design. BI tools can display this as "—".

---

## Related Documentation

- [CREATE DYNAMIC TABLE](../create-dynamic-table.md)
- [CREATE PIPE](../create-pipe.md)
- [CREATE TABLE STREAM](../create-table-stream.md)
- [CREATE BLOOMFILTER INDEX](../bloomfilter-index.md)
- [CREATE INVERTED INDEX](../inverted-index.md)
- [Medallion Architecture: Pure SQL Dynamic Table Approach](../lakehouse-medallion-sql-dt-guide.md)
