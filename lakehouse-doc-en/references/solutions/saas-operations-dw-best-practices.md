# Build a SaaS Multi-Tenant Operations Data Warehouse

Integrate feature usage events, account subscription data, and churn records from a SaaS platform into a four-layer data warehouse to produce tenant health scores and churn early-warning signals. This guide uses the RavenStack SaaS dataset (500 tenants, 5,000 subscription records, 5,000 usage events, 600 churn records) to walk through the complete **Kafka PIPE → ODS → DWD → DWS → ADS** pipeline, covering five platform capabilities: Dynamic Table cascading refresh, SQL UDF health scoring, Column Masking, RBAC, and Semantic View.

![](/.topwrite/assets/anim-18-saas-operations.svg)

---

## Overview

The core data challenge for SaaS operations teams is: feature usage events come from a high-frequency Kafka stream, while account and subscription data comes from a MySQL business database. The two data types need to be integrated at the tenant dimension before meaningful churn signals can be produced.

Singdata Lakehouse addresses the core challenges with the following combination:

| Problem | Singdata Solution |
|---|---|
| Feature usage events arrive in real time with high message volumes | Kafka PIPE continuous ingestion — batch writes to ODS raw table every 60 seconds |
| Account, subscription, and churn tables come from MySQL and need CDC sync | Studio MySQL CDC real-time sync task — automatically captures inserts, updates, and deletes |
| ODS → DWD → DWS → ADS long multi-layer computation dependency chain | Dynamic Table cascading refresh with declarative SQL; the system automatically manages the dependency order |
| Health scoring logic is complex and reused across multiple layers | SQL UDF `calc_tenant_health_score` encapsulates the weighted formula |
| Sales, customer success, and analysts need different permissions on the same table | Column Masking + RBAC — field visibility controlled by role |
| Analytics Agent needs natural language queries on tenant data | Semantic View encapsulates business semantics for direct Agent use |

---

## SQL Commands Used

| Command / Function | Purpose | Notes |
|---|---|---|
| `CREATE TABLE` | Create ODS layer raw tables | Static tables, used as upstream sources for Dynamic Tables |
| `CREATE PIPE` | Create a Kafka continuous ingestion pipeline | Bound to the ODS usage raw table |
| `CREATE FUNCTION` | Create SQL UDF `calc_tenant_health_score` | Encapsulates the tenant health scoring weighted formula |
| `ALTER TABLE ... CHANGE COLUMN ... SET MASK` | Bind a Column Masking policy | Masks sensitive fields such as `account_name` |
| `CREATE DYNAMIC TABLE` | Create DWD / DWS / ADS layer incremental computation tables | The system detects upstream changes and refreshes incrementally |
| `REFRESH DYNAMIC TABLE` | Trigger a manual refresh | Use during initial build or debugging |
| `CREATE VIEW` | Create a Semantic View | Encapsulates business semantics for Analytics Agent queries |

---

## Prerequisites

All examples in this guide run under the `best_practice_saas_dw` schema.

```sql
CREATE SCHEMA IF NOT EXISTS best_practice_saas_dw;
```

The dataset is from the [RavenStack SaaS Subscription & Churn Analytics Dataset](https://www.kaggle.com/datasets/rivalytics/saas-subscription-and-churn-analytics-dataset) (MIT license), which contains five tables: `ravenstack_accounts`, `ravenstack_subscriptions`, `ravenstack_feature_usage`, `ravenstack_churn_events`, `ravenstack_support_tickets`. This guide uses the first four.

```bash
kaggle datasets download -d rivalytics/saas-subscription-and-churn-analytics-dataset \
    --unzip -p /tmp/saas_dw/
```

---

## ODS (Raw Data Layer): Raw Data Ingestion

### Create Tables

The ODS layer retains raw data from three source types: Kafka real-time usage events, MySQL CDC account subscription data, and MySQL CDC churn events.

**Feature usage Kafka receiver table**

```sql
CREATE TABLE IF NOT EXISTS best_practice_saas_dw.ods_kafka_raw_usage (
    value       STRING,
    ingest_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

`ods_kafka_raw_usage` receives raw JSON strings from Kafka messages. Downstream processes parse the `value` field and write to `ods_feature_usage`.

**Feature usage detail table**

```sql
CREATE TABLE IF NOT EXISTS best_practice_saas_dw.ods_feature_usage (
    usage_id            STRING,
    subscription_id     STRING,
    usage_date          DATE,
    feature_name        STRING,
    usage_count         INT,
    usage_duration_secs INT,
    error_count         INT,
    is_beta_feature     BOOLEAN,
    ingest_time         TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

**Account master data table**

```sql
CREATE TABLE IF NOT EXISTS best_practice_saas_dw.ods_accounts (
    account_id      STRING,
    account_name    STRING,
    industry        STRING,
    country         STRING,
    signup_date     DATE,
    referral_source STRING,
    plan_tier       STRING,
    seats           INT,
    is_trial        BOOLEAN,
    churn_flag      BOOLEAN,
    ingest_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

**Subscriptions table**

```sql
CREATE TABLE IF NOT EXISTS best_practice_saas_dw.ods_subscriptions (
    subscription_id   STRING,
    account_id        STRING,
    start_date        DATE,
    end_date          DATE,
    plan_tier         STRING,
    seats             INT,
    mrr_amount        DOUBLE,
    arr_amount        DOUBLE,
    is_trial          BOOLEAN,
    upgrade_flag      BOOLEAN,
    downgrade_flag    BOOLEAN,
    churn_flag        BOOLEAN,
    billing_frequency STRING,
    auto_renew_flag   BOOLEAN,
    ingest_time       TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

**Churn events table**

```sql
CREATE TABLE IF NOT EXISTS best_practice_saas_dw.ods_churn_events (
    churn_event_id           STRING,
    account_id               STRING,
    churn_date               DATE,
    reason_code              STRING,
    refund_amount_usd        DOUBLE,
    preceding_upgrade_flag   BOOLEAN,
    preceding_downgrade_flag BOOLEAN,
    is_reactivation          BOOLEAN,
    feedback_text            STRING,
    ingest_time              TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

### Configure Kafka PIPE

Connect the feature usage event stream through Studio's "New Kafka Real-Time Sync Task". Kafka PIPE validates the broker connection at DDL time — replace `KAFKA_BROKER` and `TOPIC` with your actual values before running:

```sql
CREATE PIPE IF NOT EXISTS best_practice_saas_dw.pipe_feature_usage
    VIRTUAL_CLUSTER = 'DEFAULT'
    BATCH_INTERVAL_IN_SECONDS = '60'
AS
COPY INTO best_practice_saas_dw.ods_kafka_raw_usage
FROM (
    SELECT CAST(value AS STRING) AS value
    FROM READ_KAFKA(
        '<kafka-broker>:9092',   -- replace with actual broker address
        'saas_feature_usage',    -- topic name
        '',
        'cz_saas_consumer',      -- consumer group ID
        '', '', '', '',
        'raw', 'raw',
        0,
        map()
    )
);
```

> ⚠️ **Note**: `READ_KAFKA` positional parameters 5–8 (start/end offsets, timestamps) in the PIPE DDL must be left empty — they are managed automatically by the PIPE runtime. After a PIPE is created it runs by default, consuming in batches every 60 seconds.

**Option 1: Write via Kafka (recommended)**

In a real Kafka environment, send messages to the `saas_feature_usage` topic to trigger PIPE ingestion:

```python
from kafka import KafkaProducer
import json, uuid
from datetime import date

producer = KafkaProducer(
    bootstrap_servers=['<kafka-broker>:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Build a feature usage message
message = {
    "usage_id":            f"U-{uuid.uuid4().hex[:6]}",
    "subscription_id":     "S-0fcf7d",
    "usage_date":          str(date.today()),
    "feature_name":        "feature_10",
    "usage_count":         7,
    "usage_duration_secs": 3120,
    "error_count":         0,
    "is_beta_feature":     False
}

producer.send('saas_feature_usage', value=message)
producer.flush()
```

**Option 2: INSERT simulation (when no Kafka environment is available)**

If Kafka is not configured, you can write to `ods_feature_usage` as follows.

**Import from a local CSV file (recommended)**

```sql
-- Step 1: Upload the local CSV file to User Volume via SQL PUT
PUT '/path/to/your/ods_feature_usage.csv' TO USER VOLUME FILE 'ods_feature_usage.csv';
```

```sql
-- Step 2: COPY INTO the table from User Volume
COPY INTO best_practice_saas_dw.ods_feature_usage
FROM USER VOLUME
USING csv
OPTIONS('header'='true', 'sep'=',', 'nullValue'='')
FILES ('ods_feature_usage.csv');
```

You can also insert a small batch of test data inline (no CSV file required):

```sql
INSERT INTO best_practice_saas_dw.ods_feature_usage
    (usage_id, subscription_id, usage_date, feature_name,
     usage_count, usage_duration_secs, error_count, is_beta_feature)
VALUES
    ('U-1c6c24','S-0fcf7d', CAST('2023-07-27' AS DATE),'feature_20',9,5004,0,FALSE),
    ('U-f07cb8','S-c25263', CAST('2023-08-07' AS DATE),'feature_5', 9,369, 0,FALSE),
    ('U-a3b9d1','S-8cec59', CAST('2024-03-15' AS DATE),'feature_10',12,3200,1,TRUE),
    ('U-c4e2f0','S-0f6f44', CAST('2024-06-20' AS DATE),'feature_26',5,2800,0,FALSE);
```

Verify ODS layer data volumes (using the full dataset in this guide as an example):

```sql
SELECT
    (SELECT COUNT(*) FROM best_practice_saas_dw.ods_accounts)      AS accounts,
    (SELECT COUNT(*) FROM best_practice_saas_dw.ods_subscriptions)  AS subscriptions,
    (SELECT COUNT(*) FROM best_practice_saas_dw.ods_feature_usage)  AS feature_usage,
    (SELECT COUNT(*) FROM best_practice_saas_dw.ods_churn_events)   AS churn_events;
```

```
accounts | subscriptions | feature_usage | churn_events
---------+---------------+---------------+-------------
500      | 5000          | 5000          | 600
```

### Column Masking: Account Name De-Identification

`account_name` is the customer company name, which is sensitive data. The approach: administrators see the original name; all other roles see only the first 3 characters plus a mask.

```sql
CREATE OR REPLACE FUNCTION best_practice_saas_dw.mask_account_name(name STRING)
RETURNS STRING
AS CASE
    WHEN current_user() IN ('privileged_user') THEN name  -- replace with actual authorized usernames
    ELSE CONCAT(SUBSTR(name, 1, 3), '****')
END;
```

Replace `'privileged_user'` with the actual usernames that need to see plaintext data. Column Masking matches the current connection's username via `current_user()`; all authorized usernames must be explicitly listed in the `IN()` list.

```sql
ALTER TABLE best_practice_saas_dw.ods_accounts
CHANGE COLUMN account_name
SET MASK best_practice_saas_dw.mask_account_name;
```

> ⚠️ **Note**: Column Masking takes effect transparently for all queries (including Dynamic Tables). When the DWD layer JOINs `ods_accounts`, non-privileged users will see the masked `account_name`.

Verify the masking (admin account sees original names):

```sql
SELECT account_id, account_name, plan_tier
FROM best_practice_saas_dw.ods_accounts
LIMIT 5;
```

```
account_id | account_name | plan_tier
-----------+--------------+----------
A-3be56b   | Company_200  | Pro
A-354f12   | Company_201  | Pro
A-68f37c   | Company_202  | Basic
A-aa9511   | Company_203  | Pro
A-af0cd2   | Company_204  | Enterprise
```

### MySQL CDC Sync Configuration

The account, subscription, and churn tables are continuously ingested through Studio's MySQL CDC real-time sync task. In Studio go to **Data Integration → New Task → MySQL Real-Time CDC** and fill in:

- Source: MySQL address, credentials, tables to sync (`accounts`, `subscriptions`, `churn_events`)
- Target: corresponding tables like `best_practice_saas_dw.ods_accounts`
- Task path: `best_practices/saas_dw/`

After the CDC task starts it performs a full sync of existing data first, then enters incremental capture mode where INSERT / UPDATE / DELETE writes to the ODS layer in real time.

---

## DWD (Detail Data Layer): Tenant-Feature Usage Event Wide Table

The DWD layer JOINs `ods_feature_usage` (usage details), `ods_subscriptions` (subscriptions), and `ods_accounts` (accounts) into a single wide table that the DWS and ADS layers aggregate from directly, without repeating the JOIN.

### Create Tables

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_saas_dw.dwd_tenant_feature_usage
AS
SELECT
    fu.usage_id,
    fu.subscription_id,
    s.account_id,
    a.account_name,
    a.industry,
    a.country,
    a.plan_tier,
    a.seats,
    a.churn_flag        AS account_churn_flag,
    fu.usage_date,
    fu.feature_name,
    fu.usage_count,
    fu.usage_duration_secs,
    fu.error_count,
    fu.is_beta_feature,
    s.mrr_amount,
    s.billing_frequency,
    s.upgrade_flag,
    s.downgrade_flag,
    s.churn_flag        AS subscription_churn_flag,
    fu.ingest_time
FROM best_practice_saas_dw.ods_feature_usage fu
JOIN best_practice_saas_dw.ods_subscriptions  s ON fu.subscription_id = s.subscription_id
JOIN best_practice_saas_dw.ods_accounts       a ON s.account_id = a.account_id;
```

> ⚠️ **Note**: Dynamic Table DDL does not include `REFRESH INTERVAL`. Periodic refresh is scheduled by creating a "Refresh Dynamic Table" task in Studio (see instructions below), which lets you attach monitoring alerts and data quality checks to the same task.

### Create Refresh Task in Studio

In Studio go to **Development → Tasks**, path `best_practices/saas_dw/`, create a new task:

- Task type: **Refresh Dynamic Table**
- Target table: `best_practice_saas_dw.dwd_tenant_feature_usage`
- Schedule: every 5 minutes (adjust based on actual business latency requirements)
- Optional additions on this task: data quality rules (row count fluctuation alert), run timeout alert

### Initial Manual Refresh

```sql
REFRESH DYNAMIC TABLE best_practice_saas_dw.dwd_tenant_feature_usage;
```

```sql
SELECT COUNT(*) AS dwd_row_count
FROM best_practice_saas_dw.dwd_tenant_feature_usage;
```

```
dwd_row_count
-------------
5000
```

Verify the wide table join is correct:

```sql
SELECT account_id, account_name, plan_tier, feature_name, usage_count, usage_date
FROM best_practice_saas_dw.dwd_tenant_feature_usage
LIMIT 5;
```

```
account_id | account_name | plan_tier  | feature_name | usage_count | usage_date
-----------+--------------+------------+--------------+-------------+-----------
A-8b0451   | Company_245  | Enterprise | feature_10   | 7           | 2023-01-11
A-337bc1   | Company_424  | Pro        | feature_36   | 5           | 2023-01-12
A-05d3b3   | Company_213  | Basic      | feature_35   | 13          | 2024-11-08
A-039727   | Company_107  | Pro        | feature_10   | 10          | 2024-08-13
A-bcf664   | Company_248  | Pro        | feature_26   | 12          | 2024-11-09
```

---

## DWS (Summary Data Layer): Tenant Monthly Metric Aggregation

The DWS layer aggregates DWD data at `account_id` + month granularity, computing each tenant's monthly feature usage breadth (`distinct_features_used`), depth (`total_usage_count`), error rate, MRR, and other core metrics as direct input for ADS layer health scoring.

### Create Tables

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_saas_dw.dws_tenant_monthly_metrics
AS
SELECT
    account_id,
    MAX(account_name)                                               AS account_name,
    MAX(industry)                                                   AS industry,
    MAX(country)                                                    AS country,
    MAX(plan_tier)                                                  AS plan_tier,
    MAX(seats)                                                      AS seats,
    DATE_TRUNC('month', usage_date)                                 AS usage_month,
    COUNT(DISTINCT feature_name)                                    AS distinct_features_used,
    COUNT(DISTINCT CASE WHEN is_beta_feature THEN feature_name END) AS beta_features_used,
    SUM(usage_count)                                                AS total_usage_count,
    SUM(usage_duration_secs)                                        AS total_duration_secs,
    ROUND(AVG(usage_duration_secs), 1)                              AS avg_duration_secs,
    SUM(error_count)                                                AS total_errors,
    COUNT(*)                                                        AS usage_event_count,
    MAX(mrr_amount)                                                 AS mrr_amount,
    MAX(CAST(account_churn_flag AS INT))                            AS churn_flag,
    MAX(CAST(upgrade_flag AS INT))                                  AS upgrade_flag,
    MAX(CAST(downgrade_flag AS INT))                                AS downgrade_flag
FROM best_practice_saas_dw.dwd_tenant_feature_usage
GROUP BY account_id, DATE_TRUNC('month', usage_date);
```

Also create a refresh task under the Studio `best_practices/saas_dw/` path; the schedule can be set to hourly (DWS refreshes after DWD).

Trigger the initial refresh manually:

```sql
REFRESH DYNAMIC TABLE best_practice_saas_dw.dws_tenant_monthly_metrics;

SELECT COUNT(*) AS dws_row_count
FROM best_practice_saas_dw.dws_tenant_monthly_metrics;
```

```
dws_row_count
-------------
4032
```

View highly active tenants for the most recent month:

```sql
SELECT account_id, account_name, plan_tier, usage_month,
       distinct_features_used, total_usage_count,
       total_errors, mrr_amount, churn_flag
FROM best_practice_saas_dw.dws_tenant_monthly_metrics
ORDER BY usage_month DESC, total_usage_count DESC
LIMIT 8;
```

```
account_id | account_name | plan_tier  | usage_month         | distinct_features_used | total_usage_count | total_errors | mrr_amount | churn_flag
-----------+--------------+------------+---------------------+------------------------+-------------------+--------------+------------+-----------
A-4ef964   | Company_262  | Pro        | 2024-12-01T00:00:00 | 4                      | 62                | 6            | 3383       | 0
A-81edc3   | Company_236  | Basic      | 2024-12-01T00:00:00 | 3                      | 38                | 2            | 2009       | 0
A-503d5a   | Company_99   | Enterprise | 2024-12-01T00:00:00 | 3                      | 37                | 4            | 2388       | 1
A-a1bbb6   | Company_74   | Basic      | 2024-12-01T00:00:00 | 2                      | 34                | 0            | 2189       | 0
A-9b9fe9   | Company_71   | Basic      | 2024-12-01T00:00:00 | 3                      | 33                | 0            | 3332       | 0
A-9f9299   | Company_133  | Enterprise | 2024-12-01T00:00:00 | 3                      | 31                | 2            | 1372       | 0
A-c7ffc2   | Company_392  | Pro        | 2024-12-01T00:00:00 | 3                      | 31                | 3            | 5970       | 0
A-4c38bc   | Company_55   | Basic      | 2024-12-01T00:00:00 | 3                      | 31                | 2            | 7164       | 1
```

**Result interpretation**: `A-503d5a` and `A-4c38bc` are highly active tenants in the current month (relatively high `total_usage_count`), but both have `churn_flag=1`. High usage is not always a churn safeguard — it may represent a final burst of intensive usage before churn. The ADS layer needs to combine historical trends for a more complete assessment.

---

## ADS (Application Data Layer): Tenant Health Score and Churn Risk Tiers

### Health Score SQL UDF

Encapsulate the scoring logic into a SQL UDF, reusable across all downstream Dynamic Tables and ad-hoc queries.

Scoring formula:

- **Feature breadth** (50 points): more features used means higher engagement; capped at 5 features for full score
- **Usage volume** (20 points): higher monthly usage indicates deeper product integration; capped at 50 events for full score
- **Error rate penalty** (-15 points): higher error proportion means worse user experience; maximum deduction of 15
- **Upgrade bonus** (+20 points): an upgrade indicates high customer satisfaction
- **Downgrade penalty** (-20 points): a downgrade is a leading indicator of churn
- **Base score** (+10 points): any tenant with active usage gets a baseline floor

```sql
CREATE FUNCTION best_practice_saas_dw.calc_tenant_health_score(
    distinct_features_used  DOUBLE,
    total_usage_count       DOUBLE,
    total_errors            DOUBLE,
    usage_event_count       DOUBLE,
    upgrade_flag            DOUBLE,
    downgrade_flag          DOUBLE
)
RETURNS DOUBLE
AS GREATEST(0.0, LEAST(100.0,
    50.0 * LEAST(1.0, distinct_features_used / 5.0)
  + 20.0 * LEAST(1.0, total_usage_count / 50.0)
  - 15.0 * CASE WHEN usage_event_count > 0.0
                THEN LEAST(1.0, total_errors / usage_event_count)
                ELSE 0.0 END
  + 20.0 * upgrade_flag
  - 20.0 * downgrade_flag
  + 10.0
));
```

Verify the function:

```sql
SELECT
    -- High health: 6 features, 80 usage events, no errors, upgrade occurred
    best_practice_saas_dw.calc_tenant_health_score(
        CAST(6 AS INT), CAST(80 AS BIGINT), CAST(0 AS BIGINT),
        CAST(20 AS BIGINT), CAST(1 AS INT), CAST(0 AS INT)
    ) AS high_health,
    -- Medium: 4 features, 40 usage events, 2/15 error rate
    best_practice_saas_dw.calc_tenant_health_score(
        CAST(4 AS INT), CAST(40 AS BIGINT), CAST(2 AS BIGINT),
        CAST(15 AS BIGINT), CAST(0 AS INT), CAST(0 AS INT)
    ) AS mid_health,
    -- Low health: 2 features, 10 usage events, 5/10 error rate, downgrade occurred
    best_practice_saas_dw.calc_tenant_health_score(
        CAST(2 AS INT), CAST(10 AS BIGINT), CAST(5 AS BIGINT),
        CAST(10 AS BIGINT), CAST(0 AS INT), CAST(1 AS INT)
    ) AS low_health;
```

```
high_health | mid_health | low_health
------------+------------+-----------
100         | 64         | 6.5
```

> 💡 **Tip**: When calling the function, parameter types must match the function signature — `distinct_features_used` takes INT, `total_usage_count`/`total_errors`/`usage_event_count` take BIGINT, and `upgrade_flag`/`downgrade_flag` take INT. In a Dynamic Table SELECT clause, the DWS layer columns already have the correct types; you only need `CAST(... AS INT)` for `distinct_features_used`, `upgrade_flag`, and `downgrade_flag`.

### Create Tables

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_saas_dw.ads_tenant_health_score
AS
SELECT
    m.account_id,
    m.account_name,
    m.industry,
    m.country,
    m.plan_tier,
    m.seats,
    m.usage_month,
    m.distinct_features_used,
    m.total_usage_count,
    m.total_errors,
    m.usage_event_count,
    m.beta_features_used,
    m.mrr_amount,
    m.churn_flag,
    m.upgrade_flag,
    m.downgrade_flag,
    ROUND(best_practice_saas_dw.calc_tenant_health_score(
        CAST(m.distinct_features_used AS INT),
        m.total_usage_count,
        m.total_errors,
        m.usage_event_count,
        CAST(m.upgrade_flag AS INT),
        CAST(m.downgrade_flag AS INT)
    ), 1) AS health_score,
    CASE
        WHEN best_practice_saas_dw.calc_tenant_health_score(
            CAST(m.distinct_features_used AS INT),
            m.total_usage_count, m.total_errors, m.usage_event_count,
            CAST(m.upgrade_flag AS INT), CAST(m.downgrade_flag AS INT)
        ) >= 70 THEN 'HEALTHY'
        WHEN best_practice_saas_dw.calc_tenant_health_score(
            CAST(m.distinct_features_used AS INT),
            m.total_usage_count, m.total_errors, m.usage_event_count,
            CAST(m.upgrade_flag AS INT), CAST(m.downgrade_flag AS INT)
        ) >= 40 THEN 'AT_RISK'
        ELSE 'CHURN_RISK'
    END AS health_tier,
    ce.churn_date,
    ce.reason_code AS churn_reason
FROM best_practice_saas_dw.dws_tenant_monthly_metrics m
LEFT JOIN best_practice_saas_dw.ods_churn_events ce
       ON m.account_id = ce.account_id
      AND DATE_TRUNC('month', ce.churn_date) = m.usage_month;
```

Also create an ADS layer refresh task under Studio `best_practices/saas_dw/`, scheduled after the DWS refresh completes (e.g., if DWS refreshes on the hour, set ADS for 10 minutes past the hour).

Trigger the initial refresh manually:

```sql
REFRESH DYNAMIC TABLE best_practice_saas_dw.ads_tenant_health_score;

SELECT COUNT(*) AS ads_count
FROM best_practice_saas_dw.ads_tenant_health_score;
```

```
ads_count
---------
4046
```

### Health Tier Distribution

```sql
SELECT health_tier,
       COUNT(*)              AS tenant_month_count,
       ROUND(AVG(health_score), 1) AS avg_score
FROM best_practice_saas_dw.ads_tenant_health_score
GROUP BY health_tier
ORDER BY avg_score DESC;
```

```
health_tier | tenant_month_count | avg_score
------------+--------------------+----------
HEALTHY     | 9                  | 74.1
AT_RISK     | 487                | 47.4
CHURN_RISK  | 3550               | 20.7
```

**Result interpretation**: The CHURN_RISK proportion is high in this dataset (87.7%), reflecting the nature of the RavenStack dataset — it is dominated by tenants with light feature usage. Most tenants use only 1–2 features per month, which triggers low scores via the `distinct_features_used / 5.0` weight. This is also consistent with real SaaS scenarios: most tenants are in shallow-usage stages, and only deeply engaged head tenants reach the HEALTHY range.

Cross-validation between health tiers and actual churn:

```sql
SELECT health_tier, churn_flag, COUNT(*) AS cnt
FROM best_practice_saas_dw.ads_tenant_health_score
GROUP BY health_tier, churn_flag
ORDER BY health_tier, churn_flag;
```

```
health_tier | churn_flag | cnt
------------+------------+-----
AT_RISK     | 0          | 380
AT_RISK     | 1          | 107
CHURN_RISK  | 0          | 2724
CHURN_RISK  | 1          | 826
HEALTHY     | 0          | 9
```

About 22% of AT_RISK tenants have already churned, and about 23% of CHURN_RISK tenants have churned. The similar churn rates between the two tiers indicate that the current model has room to improve its tier differentiation. Consider incorporating historical trend features (e.g., consecutive months of decline) and an external prediction model (External Function) to further optimize.

### Churn Reason Analysis

```sql
SELECT reason_code,
       COUNT(*)                       AS churn_count,
       ROUND(AVG(refund_amount_usd), 2) AS avg_refund
FROM best_practice_saas_dw.ods_churn_events
GROUP BY reason_code
ORDER BY churn_count DESC;
```

```
reason_code | churn_count | avg_refund
------------+-------------+-----------
features    | 114         | 16.72
budget      | 104         | 12.00
support     | 104         | 11.73
unknown     | 95          | 18.34
competitor  | 92          | 13.08
pricing     | 91          | 14.65
```

Missing features (`features`) is the top churn reason, indicating that product feature competitiveness is the primary improvement direction. The `unknown` reason (95 cases) with its higher average refund amount suggests that collecting more structured feedback at churn time has significant value.

---

## Cross-Plan Churn Rate Analysis

```sql
SELECT plan_tier,
       COUNT(*)                                                   AS accounts,
       ROUND(AVG(seats), 1)                                       AS avg_seats,
       SUM(CAST(churn_flag AS INT))                               AS churned_accounts,
       ROUND(100.0 * SUM(CAST(churn_flag AS INT)) / COUNT(*), 1) AS churn_rate_pct
FROM best_practice_saas_dw.ods_accounts
GROUP BY plan_tier
ORDER BY churn_rate_pct DESC;
```

```
plan_tier  | accounts | avg_seats | churned_accounts | churn_rate_pct
-----------+----------+-----------+------------------+---------------
Enterprise | 154      | 19.7      | 34               | 22.1
Basic      | 168      | 22.0      | 37               | 22.0
Pro        | 178      | 19.9      | 39               | 21.9
```

The churn rates across the three plans are nearly identical (all about 22%), meaning the churn issue is not concentrated in any one plan — it is a systemic product retention challenge. This also means plan-specific discount strategies have limited effect; efforts should focus on feature usage depth and support quality.

---

## Feature Usage Heat Analysis

```sql
SELECT feature_name,
       COUNT(DISTINCT subscription_id)                        AS user_count,
       SUM(usage_count)                                       AS total_usage,
       ROUND(AVG(usage_duration_secs) / 60.0, 1)             AS avg_minutes,
       SUM(error_count)                                       AS total_errors,
       ROUND(100.0 * SUM(CAST(is_beta_feature AS INT)) / COUNT(*), 1) AS beta_pct
FROM best_practice_saas_dw.ods_feature_usage
GROUP BY feature_name
ORDER BY user_count DESC
LIMIT 6;
```

```
feature_name | user_count | total_usage | avg_minutes | total_errors | beta_pct
-------------+------------+-------------+-------------+--------------+---------
feature_26   | 144        | 1438        | 52.9        | 101          | 11.8
feature_12   | 140        | 1358        | 47.6        | 81           | 11.4
feature_10   | 140        | 1456        | 50.1        | 84           | 8.3
feature_6    | 139        | 1423        | 49.2        | 55           | 13.5
feature_17   | 138        | 1388        | 52.1        | 97           | 7.9
feature_3    | 135        | 1327        | 52.6        | 80           | 8.8
```

`feature_26` has the widest user coverage (144 subscriptions) and the highest average usage duration (52.9 minutes) — a core feature. Its 11.8% beta proportion means a significant share of users are on the beta version; closely monitoring beta error rates for timely fixes is recommended.

---

## Semantic View: Encapsulate Business Semantics for Analytics Agent

The Semantic View wraps the ADS layer health score table into a business-facing view, adding a `risk_signal` field that distills complex conditions into a single signal. Analytics Agent can then query "which tenants are at churn risk" directly in natural language.

```sql
CREATE OR REPLACE VIEW best_practice_saas_dw.v_tenant_churn_risk AS
SELECT
    account_id,
    account_name,
    industry,
    country,
    plan_tier,
    seats,
    usage_month,
    ROUND(mrr_amount, 2)     AS mrr_usd,
    distinct_features_used,
    total_usage_count,
    total_errors,
    beta_features_used,
    health_score,
    health_tier,
    churn_flag,
    churn_reason,
    CASE
        WHEN churn_flag = 1 AND churn_reason IS NOT NULL THEN churn_reason
        WHEN health_tier = 'CHURN_RISK' AND churn_flag = 0 THEN 'predicted_risk'
        ELSE 'stable'
    END AS risk_signal
FROM best_practice_saas_dw.ads_tenant_health_score;
```

Query the scale and average MRR of each churn signal (for priority ranking):

```sql
SELECT risk_signal,
       COUNT(*)                AS cnt,
       ROUND(AVG(mrr_usd), 0) AS avg_mrr
FROM best_practice_saas_dw.v_tenant_churn_risk
GROUP BY risk_signal
ORDER BY cnt DESC;
```

```
risk_signal    | cnt  | avg_mrr
---------------+------+--------
predicted_risk | 2724 | 2351
stable         | 1279 | 2828
support        | 12   | 3098
budget         | 11   | 2496
pricing        | 7    | 5459
competitor     | 5    | 1003
unknown        | 4    | 2289
features       | 4    | 7096
```

**Result interpretation**: `pricing` churn has an average MRR of $5,459 and `features` churn is even higher ($7,096), showing that high-value customer churn is driven primarily by product feature competitiveness and price sensitivity — not support quality. The customer success team should prioritize reaching out to these two risk groups with targeted retention plans.

---

## RBAC Permission Configuration

Different roles have different data access requirements for tenant data:

| Role | Accessible Scope | Restrictions |
|---|---|---|
| Data Analysts | All ADS / DWS aggregated data | Cannot view raw account names in ODS (masked version is visible) |
| Customer Success (CS) | `v_tenant_churn_risk` including real account names | Requires admin authorization |
| Sales | `v_tenant_churn_risk` for their own assigned customers only | Row-level filtering implemented at the application layer |
| Operations Admin | All layers including ODS raw data | No restrictions |

Control view access via GRANT:

```sql
-- Grant CS role access to the Semantic View
GRANT SELECT ON VIEW best_practice_saas_dw.v_tenant_churn_risk TO ROLE cs_team;

-- Grant analysts access to DWS / ADS layers
GRANT SELECT ON DYNAMIC TABLE best_practice_saas_dw.dws_tenant_monthly_metrics TO ROLE analyst;
GRANT SELECT ON DYNAMIC TABLE best_practice_saas_dw.ads_tenant_health_score     TO ROLE analyst;

-- ODS layer only accessible by admin
GRANT SELECT ON TABLE best_practice_saas_dw.ods_accounts      TO ROLE admin;
GRANT SELECT ON TABLE best_practice_saas_dw.ods_subscriptions TO ROLE admin;
```

---

## Data Warehouse Object Summary

```sql
SHOW TABLES IN best_practice_saas_dw;
```

```
schema_name             | table_name                 | is_view | is_dynamic
------------------------+----------------------------+---------+-----------
best_practice_saas_dw   | ods_accounts               | false   | false
best_practice_saas_dw   | ods_subscriptions          | false   | false
best_practice_saas_dw   | ods_feature_usage          | false   | false
best_practice_saas_dw   | ods_churn_events           | false   | false
best_practice_saas_dw   | ods_kafka_raw_usage        | false   | false
best_practice_saas_dw   | dwd_tenant_feature_usage   | false   | true
best_practice_saas_dw   | dws_tenant_monthly_metrics | false   | true
best_practice_saas_dw   | ads_tenant_health_score    | false   | true
best_practice_saas_dw   | v_tenant_churn_risk        | true    | false
```

---

## Notes

- **Dynamic Table does not set `REFRESH INTERVAL`**: The DDL does not include `REFRESH INTERVAL`. Refresh scheduling is centrally managed through Studio Tasks. This lets you attach monitoring alerts and data quality checks to the same task and makes it easy to change the refresh schedule without rebuilding the table.

- **Column Masking works transparently on Dynamic Tables**: When the DWD layer JOINs `ods_accounts`, non-privileged users see a masked `account_name` (`Com****`), and DWD / DWS / ADS also store the masked content. If the CS role needs to see original account names, query `v_tenant_churn_risk` directly (the CS role is already authorized on this view) and avoid adding the masking function to `account_name` in the view definition.

- **Health score UDF parameter types**: `calc_tenant_health_score` is defined with DOUBLE parameters. In the Dynamic Table SELECT clause, DWS table columns `distinct_features_used`, `upgrade_flag`, and `downgrade_flag` are BIGINT type and require `CAST(... AS INT)` before being passed in; otherwise you get a type mismatch parse error.

- **Kafka PIPE offset management**: Messages that arrive while the PIPE is stopped are not lost — the PIPE resumes consuming from the last offset when restarted. If you need to reset the consumption offset (e.g., for historical data backfill), configure the start offset in the Studio task or rebuild the PIPE.

- **Dynamic Table incremental refresh limitation**: If the ODS layer uses `INSERT OVERWRITE` for full replacement, Dynamic Tables fall back to a full refresh. Use `INSERT INTO` for append writes with CDC, and retain the `ingest_time` field for incremental identification.

- **Column Masking**: After binding `SET MASK`, all users querying that column through standard SQL will see the masked value — including through Dynamic Tables, views, and ad-hoc queries.

---

## Related Documentation

- [Create Dynamic Table](../references/create-dynamic-table.md) — syntax reference and incremental refresh mechanism
- [Continuous Kafka Data Ingestion with PIPE](../references/pipe-kafka.md) — full Kafka PIPE parameter reference
- [Dynamic Data Masking](../references/dynamic-mask.md) — Column Masking policy creation and binding
- [User Permission Management (RBAC)](../references/rbac.md) — GRANT / REVOKE syntax and role management
- [Create View](../references/create-view.md) — VIEW and Semantic View syntax
- [Medallion Architecture: Pure SQL Dynamic Table Approach](lakehouse-medallion-sql-dt-guide.md) — large-scale three-layer data warehouse reference
- [Industrial IoT Device Health Monitoring Data Warehouse Best Practices](iot-device-health-monitoring-dw-best-practices.md) — similar four-layer data warehouse architecture reference

> ⚠️ **Note (pending manual verification)**: Column Masking currently matches by username via `current_user()`, and all usernames authorized to view plaintext must be added individually to the `IN()` list in the masking function. If your Lakehouse version supports role-based dynamic matching (e.g., `HAS_ROLE('role_name')`), you can use roles instead of a username list for easier maintenance. Contact Singdata technical support to confirm whether your version supports this function.