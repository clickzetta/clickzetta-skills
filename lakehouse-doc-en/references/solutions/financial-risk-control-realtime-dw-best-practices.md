# Build a Real-Time Financial Risk Control Data Warehouse

This guide shows how to ingest a bank card transaction stream in real time into the Lakehouse and build a four-layer ODS → DWD → DWS → ADS risk control data warehouse that produces a real-time risk score for every transaction, ready for use by an interception system. Using the Kaggle [Credit Card Transactions Fraud Detection Dataset](https://www.kaggle.com/datasets/kartik2112/fraud-detection) as the data foundation, it demonstrates the full **Kafka PIPE real-time ingestion → Dynamic Table sliding-window aggregation → SQL UDF scoring → Column Masking** pipeline.

![](/.topwrite/assets/anim-17-financial-risk-control.svg)

---

## Overview

The core challenge in financial risk control is: **real-time transaction streams at thousands of transactions per second require risk feature computation and an interception decision within milliseconds**. Key pain points and Singdata solutions:

| Problem | Solution |
|---|---|
| Real-time transaction stream ingestion; Kafka messages need second-level landing | Kafka PIPE continuous ingestion, `BATCH_INTERVAL_IN_SECONDS = 60` |
| Automatic incremental computation across ODS → DWD → DWS → ADS | Dynamic Table declarative SQL; system refreshes along the dependency chain |
| Real-time aggregation of user historical features (mean, volatility, fraud count) | DWS layer Dynamic Table, 1-minute refresh |
| Scoring logic reusable across multiple layers | SQL UDF `calc_txn_risk_score()` encapsulating amount deviation + geographic distance + historical risk |
| Credit card numbers, names, and other PII data need differentiated access | Column Masking bound to columns; non-privileged users see masked values automatically |
| Risk analysts, interception systems, and auditors need different permissions | RBAC three-role model with fine-grained authorization |

---

## SQL Commands Used

| Command / Function | Purpose | Notes |
|---|---|---|
| `CREATE TABLE` | Create ODS raw transaction table and customer master table | Regular tables used as upstream sources for Dynamic Tables |
| `CREATE PIPE` | Create a Kafka continuous ingestion pipeline | Bind Kafka topic to ODS target table |
| `CREATE DYNAMIC TABLE` | Build incremental computation tables for DWD, DWS, ADS layers | System refreshes in order based on reference relationships |
| `REFRESH DYNAMIC TABLE` | Trigger a manual refresh | Trigger manually after initial build to verify the pipeline |
| `CREATE FUNCTION` | Create SQL UDF `calc_txn_risk_score` | Encapsulates the risk scoring formula |
| `ALTER TABLE ... CHANGE COLUMN ... SET MASK` | Bind a Column Masking policy | Differentially display PII columns such as `cc_num` |
| `GRANT / REVOKE` | Configure RBAC role permissions | Three-role model (analyst / interception / audit) |

---

## Prerequisites

All examples in this guide run under the `best_practice_financial_risk` Schema.

```sql
CREATE SCHEMA IF NOT EXISTS best_practice_financial_risk;
```

Result:

```
{}
```

---

## ODS (Raw Data Layer): Raw Transaction Table and Customer Master

### Create Tables

The transaction main table records each card swipe event; the customer master table stores cardholder profile information.

```sql
CREATE TABLE IF NOT EXISTS best_practice_financial_risk.ods_transactions (
    txn_id                  STRING,
    cc_num                  STRING,        -- 银行卡号，绑定 Column Masking
    merchant                STRING,
    category                STRING,
    amt                     DOUBLE,
    first_name              STRING,
    last_name               STRING,
    gender                  STRING,
    street                  STRING,
    city                    STRING,
    state                   STRING,
    zip                     STRING,
    lat                     DOUBLE,        -- 持卡人位置（纬度）
    long_                   DOUBLE,        -- 持卡人位置（经度）
    city_pop                BIGINT,
    job                     STRING,
    dob                     STRING,        -- 出生日期（字符串格式）
    trans_num               STRING,
    unix_time               BIGINT,
    merch_lat               DOUBLE,        -- 商户位置（纬度）
    merch_long              DOUBLE,        -- 商户位置（经度）
    is_fraud                INT,           -- 欺诈标签：0 正常 / 1 欺诈
    trans_date_trans_time   TIMESTAMP
);

CREATE TABLE IF NOT EXISTS best_practice_financial_risk.ods_customers (
    cc_num     STRING,
    first_name STRING,
    last_name  STRING,
    gender     STRING,
    street     STRING,
    city       STRING,
    state      STRING,
    zip        STRING,
    lat        DOUBLE,
    long_      DOUBLE,
    city_pop   BIGINT,
    job        STRING,
    dob        STRING
);
```

### Configure Kafka PIPE

In production, transaction data is ingested in real time to the ODS layer via Kafka. The following is a PIPE configuration template; replace the actual broker address and topic name before creating.

```sql
-- 先建 raw 消息接收表（JSON 字符串）
CREATE TABLE IF NOT EXISTS best_practice_financial_risk.kafka_txn_raw (value STRING);

-- 创建 Kafka PIPE
CREATE PIPE IF NOT EXISTS best_practice_financial_risk.pipe_txn_stream
    VIRTUAL_CLUSTER = 'DEFAULT'
    BATCH_INTERVAL_IN_SECONDS = '60'
AS
COPY INTO best_practice_financial_risk.kafka_txn_raw
FROM (
    SELECT CAST(value AS STRING) AS value
    FROM READ_KAFKA(
        '<kafka-broker>:9092',      -- 替换为实际 broker 地址
        'bank_transactions',         -- Kafka topic 名称
        '',
        'cz_fraud_consumer',         -- consumer group ID
        '','','','',
        'raw', 'raw',
        0,
        map()
    )
);
```

> 💡 **Tip**: Positional parameters 5–8 of `READ_KAFKA` (start/end offsets and timestamps) must be left empty in PIPE DDL; the PIPE runtime manages them automatically. After creation, the PIPE runs by default and batch-consumes every 60 seconds.

### Load Test Data

This guide uses a subset of the Kaggle fraud-detection dataset, with INSERT statements simulating the effect of parsed Kafka messages being written.

Import from a local CSV file (recommended):

```sql
-- 第一步：通过 SQL PUT 将本地 CSV 文件上传到 User Volume
PUT '/path/to/your/data.csv' TO USER VOLUME FILE 'data.csv';
```

```sql
-- 第二步：从 User Volume COPY INTO 表
COPY INTO best_practice_financial_risk.ods_customers
FROM USER VOLUME
USING csv
OPTIONS('header'='true', 'sep'=',', 'nullValue'='')
FILES ('data.csv');
```

You can also insert a small batch of test data inline (no CSV file required):

```sql
INSERT INTO best_practice_financial_risk.ods_customers VALUES
('4532117694074009','John','Smith','M','123 Oak St','Austin','TX','78701',30.2672,-97.7431,950000,'Software Engineer','1985-06-15'),
('4716058826889367','Mary','Johnson','F','456 Elm Ave','Dallas','TX','75201',32.7767,-96.7970,1343000,'Accountant','1990-03-22'),
('4929429090508220','Robert','Williams','M','789 Pine Rd','Houston','TX','77001',29.7604,-95.3698,2300000,'Doctor','1978-11-08'),
('4532117691234567','Linda','Brown','F','321 Maple Dr','San Antonio','TX','78205',29.4241,-98.4936,1434000,'Teacher','1995-07-30'),
('4716058821111222','James','Davis','M','654 Birch Ln','Phoenix','AZ','85001',33.4484,-112.0740,1600000,'Manager','1982-09-14'),
('4929429095555666','Patricia','Miller','F','987 Cedar St','Chicago','IL','60601',41.8781,-87.6298,2700000,'Nurse','1988-04-25'),
('4532117697654321','Michael','Wilson','M','147 Spruce Ave','Los Angeles','CA','90001',34.0522,-118.2437,3980000,'Engineer','1975-12-03'),
('4716058828888999','Jennifer','Moore','F','258 Walnut Rd','New York','NY','10001',40.7128,-74.0060,8336000,'Lawyer','1992-08-17'),
('4929429093333444','David','Taylor','M','369 Hickory Dr','Seattle','WA','98101',47.6062,-122.3321,724000,'Data Scientist','1986-02-28'),
('4532117692222333','Barbara','Anderson','F','741 Ash Blvd','Miami','FL','33101',25.7617,-80.1918,460000,'Marketing','1993-11-11');
```

```sql
INSERT INTO best_practice_financial_risk.ods_transactions VALUES
('TXN001','4532117694074009','fraud_Kirlin and Sons','grocery_pos',9.36,'John','Smith','M','123 Oak St','Austin','TX','78701',30.2672,-97.7431,950000,'Software Engineer','1985-06-15','tx001',1325376018,30.4127,-97.8974,0,CAST('2020-01-01 00:00:18' AS TIMESTAMP)),
('TXN002','4716058826889367','fraud_Sporer-Keebler','entertainment',2529.0,'Mary','Johnson','F','456 Elm Ave','Dallas','TX','75201',32.7767,-96.7970,1343000,'Accountant','1990-03-22','tx002',1325376075,33.4897,-96.9132,1,CAST('2020-01-01 00:01:15' AS TIMESTAMP)),
('TXN007','4532117697654321','fraud_Olson, Becker and Koch','shopping_net',1987.40,'Michael','Wilson','M','147 Spruce Ave','Los Angeles','CA','90001',34.0522,-118.2437,3980000,'Engineer','1975-12-03','tx007',1325379440,34.1808,-118.4634,1,CAST('2020-01-01 00:57:20' AS TIMESTAMP)),
('TXN018','4716058828888999','fraud_Sauer-Kessler','entertainment',4500.00,'Jennifer','Moore','F','258 Walnut Rd','New York','NY','10001',40.7128,-74.0060,8336000,'Lawyer','1992-08-17','tx018',1325386200,40.9345,-74.1234,1,CAST('2020-01-01 02:50:00' AS TIMESTAMP))
-- ... 完整 20 条，此处省略
;
```

Verify ODS layer row count:

```sql
SELECT COUNT(*) AS total_txns,
       SUM(is_fraud) AS fraud_count,
       ROUND(SUM(is_fraud)*100.0/COUNT(*), 1) AS fraud_rate_pct
FROM best_practice_financial_risk.ods_transactions;
```

```
total_txns | fraud_count | fraud_rate_pct
-----------+-------------+---------------
20         | 7           | 35.0
```

### Column Masking: Credit Card Number PII Masking

Credit card numbers are highly sensitive PII data that must be masked for unauthorized users (showing only the last 4 digits).

```sql
-- 创建脱敏函数
CREATE OR REPLACE FUNCTION best_practice_financial_risk.mask_cc_num(cc_num STRING)
RETURNS STRING
AS CASE
    WHEN current_user() IN ('privileged_user') THEN cc_num  -- 替换为实际获授权的用户名
    ELSE CONCAT('****-****-****-', SUBSTRING(cc_num, LENGTH(cc_num) - 3, 4))
END;

-- 绑定到 ods_transactions.cc_num 列
ALTER TABLE best_practice_financial_risk.ods_transactions
CHANGE COLUMN cc_num
SET MASK best_practice_financial_risk.mask_cc_num;
```

> 💡 **Tip**: Replace `'privileged_user'` with the actual usernames that need to see plaintext data. Column Masking matches the current connection's username via `current_user()`; all authorized usernames must be explicitly listed in the `IN()` list.

> ⚠️ **Note**: Column Masking takes effect transparently for all queries, including downstream Dynamic Tables. During the DWD layer JOIN, non-privileged users see the card number in `****-****-****-4009` format.

Verify the masking effect (admin account sees the original values):

```sql
SELECT txn_id, cc_num, amt, is_fraud
FROM best_practice_financial_risk.ods_transactions
LIMIT 3;
```

```
txn_id | cc_num             | amt    | is_fraud
-------+--------------------+--------+---------
TXN001 | 4532117694074009   | 9.36   | 0
TXN002 | 4716058826889367   | 2529.0 | 1
TXN003 | 4929429090508220   | 4.23   | 0
```

---

## DWD (Detail Data Layer): Standardized Transaction Events

The DWD layer uses a Dynamic Table to JOIN the ODS transaction stream with the customer master table to add cardholder profile information and compute the geographic distance between the cardholder location and the merchant location in real time (using a simplified Haversine formula).

### Create Tables

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_financial_risk.dwd_txn_events
REFRESH INTERVAL 1 MINUTE VCLUSTER DEFAULT
AS
SELECT
    t.txn_id,
    t.cc_num,
    t.trans_num,
    t.trans_date_trans_time                         AS txn_time,
    t.unix_time,
    t.merchant,
    t.category,
    t.amt,
    t.is_fraud,
    t.merch_lat,
    t.merch_long,
    -- 地理距离：持卡人位置 vs 商户位置（km，Haversine 简化）
    ROUND(
        111.2 * SQRT(
            POWER(t.lat - t.merch_lat, 2) +
            POWER((t.long_ - t.merch_long) * COS(RADIANS(t.lat)), 2)
        ), 2
    )                                               AS dist_km,
    c.first_name,
    c.last_name,
    c.gender,
    c.city,
    c.state,
    c.job,
    c.dob,
    YEAR(t.trans_date_trans_time) -
        CAST(SUBSTRING(c.dob, 1, 4) AS INT)        AS age
FROM best_practice_financial_risk.ods_transactions t
LEFT JOIN best_practice_financial_risk.ods_customers c
    ON t.cc_num = c.cc_num;
```

`dist_km` calculates the straight-line distance between the cardholder registered address and the merchant. A larger distance indicates the cardholder is transacting far from their usual location, which is a higher risk signal.

### Trigger the Initial Refresh Manually

```sql
REFRESH DYNAMIC TABLE best_practice_financial_risk.dwd_txn_events;
```

Verify DWD layer data:

```sql
SELECT txn_id, cc_num, merchant, category, amt, is_fraud, dist_km, city, state, age
FROM best_practice_financial_risk.dwd_txn_events
ORDER BY txn_time
LIMIT 5;
```

```
txn_id | cc_num             | merchant                          | category     | amt    | is_fraud | dist_km | city   | state | age
-------+--------------------+-----------------------------------+--------------+--------+----------+---------+--------+-------+----
TXN001 | 4532117694074009   | fraud_Kirlin and Sons             | grocery_pos  | 9.36   | 0        | 21.94   | Austin | TX    | 35
TXN002 | 4716058826889367   | fraud_Sporer-Keebler              | entertainment| 2529.0 | 1        | 80.03   | Dallas | TX    | 30
TXN003 | 4929429090508220   | fraud_Osinski, Murphey and Carver | shopping_net | 4.23   | 0        | 24.2    | Houston| TX    | 42
TXN004 | 4532117691234567   | Veum-Skiles                       | food_dining  | 316.97 | 0        | 24.03   | San Antonio | TX | 25
TXN005 | 4716058821111222   | fraud_Kertzmann-Shanahan          | gas_transport| 78.85  | 0        | 27.19   | Phoenix| AZ    | 38
```

All 20 DWD layer records are joined to customer information; the `dist_km` and `age` fields are computed.

```sql
SELECT COUNT(*) AS dwd_count FROM best_practice_financial_risk.dwd_txn_events;
```

```
dwd_count
---------
20
```

---

## DWS (Summary Data Layer): User Risk Feature Aggregation

The DWS layer aggregates historical transaction features by cardholder (`cc_num`), including spending mean, volatility, historical fraud count, and high-value transaction frequency. These features are the core inputs for the ADS layer risk scoring.

### Create Tables

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_financial_risk.dws_user_risk_features
REFRESH INTERVAL 1 MINUTE VCLUSTER DEFAULT
AS
SELECT
    cc_num,
    first_name,
    last_name,
    state,
    job,
    age,
    -- 交易统计（全量历史）
    COUNT(*)                                        AS txn_total,
    ROUND(SUM(amt), 2)                              AS amt_total,
    ROUND(AVG(amt), 2)                              AS amt_avg,
    ROUND(MAX(amt), 2)                              AS amt_max,
    ROUND(STDDEV_POP(amt), 2)                       AS amt_stddev,
    -- 历史欺诈记录
    SUM(is_fraud)                                   AS fraud_history_count,
    -- 按品类交易次数
    COUNT(CASE WHEN category = 'shopping_net'  THEN 1 END) AS cat_shopping_net,
    COUNT(CASE WHEN category = 'entertainment' THEN 1 END) AS cat_entertainment,
    COUNT(CASE WHEN category = 'grocery_pos'   THEN 1 END) AS cat_grocery,
    COUNT(CASE WHEN category = 'food_dining'   THEN 1 END) AS cat_food_dining,
    -- 最近一次交易时间
    MAX(txn_time)                                   AS last_txn_time,
    -- 高金额交易次数（单笔 > 1000）
    COUNT(CASE WHEN amt > 1000 THEN 1 END)          AS high_amt_txn_count
FROM best_practice_financial_risk.dwd_txn_events
GROUP BY cc_num, first_name, last_name, state, job, age;
```

```sql
REFRESH DYNAMIC TABLE best_practice_financial_risk.dws_user_risk_features;
```

View high-risk user features (sorted by historical fraud count and total amount):

```sql
SELECT cc_num, first_name, last_name,
       txn_total, amt_total, amt_avg, amt_max, amt_stddev,
       fraud_history_count, high_amt_txn_count
FROM best_practice_financial_risk.dws_user_risk_features
ORDER BY fraud_history_count DESC, amt_total DESC
LIMIT 5;
```

```
cc_num             | first_name | last_name | txn_total | amt_total | amt_avg  | amt_max | amt_stddev | fraud_history_count | high_amt_txn_count
-------------------+------------+-----------+-----------+-----------+----------+---------+------------+---------------------+-------------------
4716058828888999   | Jennifer   | Moore     | 2         | 4521.54   | 2260.77  | 4500.0  | 2239.23    | 1                   | 1
4929429090508220   | Robert     | Williams  | 2         | 3214.73   | 1607.37  | 3210.5  | 1603.14    | 1                   | 1
4716058826889367   | Mary       | Johnson   | 2         | 2564.2    | 1282.1   | 2529.0  | 1246.9     | 1                   | 1
4929429093333444   | David      | Taylor    | 2         | 2356.97   | 1178.49  | 2341.17 | 1162.69    | 1                   | 1
4532117697654321   | Michael    | Wilson    | 2         | 2010.5    | 1005.25  | 1987.4  | 982.15     | 1                   | 1
```

Jennifer Moore has extremely high historical spending variance (`amt_stddev = 2239.23`), indicating highly variable spending behavior — a high-risk signal. The DWS layer generates 10 user risk profiles.

---

## Risk Scoring UDF

The scoring logic is encapsulated as a SQL UDF that the ADS layer can call directly. The formula is concise and auditable.

The score is the sum of four factors (capped at 100, floored at 0):

| Factor | Calculation | Max Points |
|---|---|---|
| Amount deviation | `(amt - hist_avg) / hist_stddev × 10`, max 40 points | 40 points |
| Geographic distance | Distance > 100 km from cardholder adds 20 points; > 50 km adds 10 points | 20 points |
| Historical fraud | Each historical fraud record adds 15 points | No cap (truncated at 100) |
| High-value frequency | Each historical transaction > 1000 adds 5 points | No cap (truncated at 100) |

```sql
CREATE FUNCTION best_practice_financial_risk.calc_txn_risk_score(
    p_amt           DOUBLE,    -- 当前交易金额
    p_hist_avg      DOUBLE,    -- 用户历史均值
    p_hist_stddev   DOUBLE,    -- 用户历史标准差
    p_dist_km       DOUBLE,    -- 持卡人与商户距离（km）
    p_fraud_history DOUBLE,    -- 历史欺诈次数
    p_high_count    DOUBLE     -- 高金额交易次数
)
RETURNS DOUBLE
AS LEAST(100.0, GREATEST(0.0,
    -- 金额偏差因子
    CASE
        WHEN p_hist_stddev > 0.0
            THEN LEAST(40.0, ((p_amt - p_hist_avg) / p_hist_stddev) * 10.0)
        ELSE 0.0
    END
    -- 地理距离因子
    + CASE WHEN p_dist_km > 100.0 THEN 20.0 WHEN p_dist_km > 50.0 THEN 10.0 ELSE 0.0 END
    -- 历史欺诈因子
    + p_fraud_history * 15.0
    -- 高金额频次因子
    + p_high_count * 5.0
));
```

> ⚠️ **Note**: All UDF parameters are defined as `DOUBLE` to avoid overload conflicts with BIGINT parameters. When calling, explicitly cast `fraud_history_count` (a BIGINT column): `CAST(fraud_history_count AS DOUBLE)`.

Verify two typical scenarios:

```sql
SELECT
    best_practice_financial_risk.calc_txn_risk_score(
        2529.0, 1282.1, 1246.9, 80.03, 1.0, 1.0
    ) AS risk_fraud_txn,
    best_practice_financial_risk.calc_txn_risk_score(
        9.36, 200.0, 100.0, 22.0, 0.0, 0.0
    ) AS risk_normal_txn;
```

```
risk_fraud_txn | risk_normal_txn
---------------+----------------
40.0           | 0.0
```

A fraudulent transaction with large amount deviation and 80 km distance scores 40 (MEDIUM). A small normal transaction scores 0 (LOW).

---

## ADS (Application Data Layer): Real-Time Risk Score Output

The ADS layer is the final output of the risk control data warehouse. It JOINs DWD and DWS, calls the UDF to compute the real-time risk score, and tags each transaction with a risk level for direct query by the interception system.

### Create Tables

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_financial_risk.ads_txn_risk_score
REFRESH INTERVAL 1 MINUTE VCLUSTER DEFAULT
AS
SELECT
    t.txn_id,
    t.cc_num,
    t.txn_time,
    t.merchant,
    t.category,
    t.amt,
    t.dist_km,
    t.city,
    t.state,
    t.is_fraud,
    u.amt_avg,
    u.amt_stddev,
    u.fraud_history_count,
    u.high_amt_txn_count,
    -- 实时风险评分
    ROUND(best_practice_financial_risk.calc_txn_risk_score(
        t.amt,
        u.amt_avg,
        u.amt_stddev,
        t.dist_km,
        CAST(u.fraud_history_count AS DOUBLE),
        CAST(u.high_amt_txn_count AS DOUBLE)
    ), 2)                                           AS risk_score,
    -- 风险等级
    CASE
        WHEN best_practice_financial_risk.calc_txn_risk_score(
            t.amt, u.amt_avg, u.amt_stddev, t.dist_km,
            CAST(u.fraud_history_count AS DOUBLE),
            CAST(u.high_amt_txn_count AS DOUBLE)
        ) >= 60 THEN 'HIGH'
        WHEN best_practice_financial_risk.calc_txn_risk_score(
            t.amt, u.amt_avg, u.amt_stddev, t.dist_km,
            CAST(u.fraud_history_count AS DOUBLE),
            CAST(u.high_amt_txn_count AS DOUBLE)
        ) >= 30 THEN 'MEDIUM'
        ELSE 'LOW'
    END                                             AS risk_level
FROM best_practice_financial_risk.dwd_txn_events t
LEFT JOIN best_practice_financial_risk.dws_user_risk_features u
    ON t.cc_num = u.cc_num;
```

```sql
REFRESH DYNAMIC TABLE best_practice_financial_risk.ads_txn_risk_score;
```

View the high-risk transaction rankings:

```sql
SELECT txn_id, merchant, category, amt, dist_km, risk_score, risk_level, is_fraud
FROM best_practice_financial_risk.ads_txn_risk_score
ORDER BY risk_score DESC, is_fraud DESC
LIMIT 10;
```

```
txn_id  | merchant                          | category     | amt    | dist_km | risk_score | risk_level | is_fraud
--------+-----------------------------------+--------------+--------+---------+------------+------------+---------
TXN002  | fraud_Sporer-Keebler              | entertainment| 2529.0 | 80.03   | 40.0       | MEDIUM     | 1
TXN011  | fraud_Kertzmann-Shanahan          | shopping_net | 1456.78| 31.26   | 30.0       | MEDIUM     | 1
TXN018  | fraud_Sauer-Kessler               | entertainment| 4500.0 | 26.56   | 30.0       | MEDIUM     | 1
TXN007  | fraud_Olson, Becker and Koch      | shopping_net | 1987.4 | 24.78   | 30.0       | MEDIUM     | 1
TXN013  | fraud_Sanford and Sons            | entertainment| 3210.5 | 19.48   | 30.0       | LOW        | 1
TXN009  | fraud_Zboncak LLC                 | entertainment| 2341.17| 16.71   | 30.0       | LOW        | 1
TXN015  | fraud_Brekke-LeBsack              | shopping_net | 789.0  | 31.81   | 25.0       | LOW        | 1
TXN012  | Batz LLC                          | gas_transport| 35.2   | 12.97   | 10.0       | LOW        | 0
TXN017  | Anderson-Lesch                    | food_dining  | 23.1   | 29.51   | 10.0       | LOW        | 0
TXN019  | Gleason Inc                       | grocery_pos  | 15.8   | 23.96   | 10.0       | LOW        | 0
```

### Risk Level vs Fraud Rate Cross-Analysis

```sql
SELECT
    risk_level,
    COUNT(*) AS txn_count,
    SUM(is_fraud) AS fraud_in_bucket,
    ROUND(SUM(is_fraud)*100.0/COUNT(*), 1) AS fraud_rate_pct,
    ROUND(AVG(risk_score), 1) AS avg_score
FROM best_practice_financial_risk.ads_txn_risk_score
GROUP BY risk_level
ORDER BY avg_score DESC;
```

```
risk_level | txn_count | fraud_in_bucket | fraud_rate_pct | avg_score
-----------+-----------+-----------------+----------------+----------
MEDIUM     | 4         | 4               | 100.0          | 32.5
LOW        | 16        | 3               | 18.8           | 11.3
```

The MEDIUM risk bucket has a fraud rate of 100%, demonstrating that the scoring model is effective at identifying high-risk transactions. The LOW bucket still has 18.8% fraud because some fraudulent transactions have relatively small amounts and did not trigger the amount deviation factor. Incorporating sequential behavior features can further improve the model.

### Fraud Rate Analysis by Category

```sql
SELECT
    category,
    COUNT(*) AS txn_count,
    SUM(is_fraud) AS fraud_count,
    ROUND(SUM(is_fraud)*100.0/COUNT(*), 1) AS fraud_rate_pct,
    ROUND(AVG(amt), 2) AS avg_amt,
    ROUND(MAX(amt), 2) AS max_amt
FROM best_practice_financial_risk.ads_txn_risk_score
GROUP BY category
ORDER BY fraud_rate_pct DESC;
```

```
category       | txn_count | fraud_count | fraud_rate_pct | avg_amt  | max_amt
---------------+-----------+-------------+----------------+----------+---------
entertainment  | 4         | 4           | 100.0          | 3145.17  | 4500.0
shopping_net   | 4         | 3           | 75.0           | 1059.35  | 1987.4
gas_transport  | 2         | 0           | 0.0            | 57.03    | 78.85
health_fitness | 3         | 0           | 0.0            | 137.45   | 200.0
grocery_pos    | 4         | 0           | 0.0            | 28.03    | 65.43
food_dining    | 3         | 0           | 0.0            | 128.58   | 316.97
```

`entertainment` and `shopping_net` are high-fraud categories, and fraudulent transaction amounts are much higher than normal spending averages. This provides direct evidence for risk control rules: these two categories can have additional transaction limits or secondary verification triggers.

---

## RBAC: Three-Role Permission Model

The risk control scenario involves three types of users that need differentiated access:

| Role | Accessible Data | Permission Notes |
|---|---|---|
| `risk_analyst` | DWD layer, DWS layer | Analyze transaction patterns; `cc_num` auto-masked |
| `risk_interception` | ADS layer | Gets only risk scores and levels; cannot see raw transaction details |
| `audit_admin` | All layers including PII original values | Compliance audit; sees full `cc_num` and names |

```sql
-- 创建角色
CREATE ROLE IF NOT EXISTS risk_analyst;
CREATE ROLE IF NOT EXISTS risk_interception;
CREATE ROLE IF NOT EXISTS audit_admin;

-- risk_analyst：可查 DWD 和 DWS（动态表用 DYNAMIC TABLE 关键字）
GRANT SELECT ON DYNAMIC TABLE best_practice_financial_risk.dwd_txn_events
    TO ROLE risk_analyst;
GRANT SELECT ON DYNAMIC TABLE best_practice_financial_risk.dws_user_risk_features
    TO ROLE risk_analyst;

-- risk_interception：仅查 ADS 输出（动态表）
GRANT SELECT ON DYNAMIC TABLE best_practice_financial_risk.ads_txn_risk_score
    TO ROLE risk_interception;

-- audit_admin：全层访问
GRANT SELECT ON TABLE best_practice_financial_risk.ods_transactions
    TO ROLE audit_admin;
GRANT SELECT ON TABLE best_practice_financial_risk.ods_customers
    TO ROLE audit_admin;
GRANT SELECT ON DYNAMIC TABLE best_practice_financial_risk.dwd_txn_events
    TO ROLE audit_admin;
GRANT SELECT ON DYNAMIC TABLE best_practice_financial_risk.dws_user_risk_features
    TO ROLE audit_admin;
GRANT SELECT ON DYNAMIC TABLE best_practice_financial_risk.ads_txn_risk_score
    TO ROLE audit_admin;
```

> 💡 **Tip**: When the `risk_analyst` role queries `dwd_txn_events`, Column Masking applies automatically — `cc_num` is displayed as `****-****-****-4009` without additional configuration, keeping masking and authorization decoupled.

---

## Notes

- **Dynamic Table parameter format**: The correct syntax is `REFRESH INTERVAL N MINUTE VCLUSTER DEFAULT`, not `REFRESH_MODE = INCREMENTAL` or `REFRESH_INTERVAL = '1 minute'`.
- **Column Masking**: Masking also applies transparently to SELECT queries on downstream Dynamic Tables.
- **UDF parameter types**: All parameters of `calc_txn_risk_score` are defined as `DOUBLE`. When calling it in a Dynamic Table, aggregate columns of type `BIGINT` (`fraud_history_count`, `high_amt_txn_count`) must be explicitly cast: `CAST(col AS DOUBLE)`.
- **Bloomfilter Index use case**: `cc_num` is a high-cardinality column suitable for `CREATE BLOOMFILTER INDEX`. The index must be created in the same Schema context as the target table (`USE SCHEMA best_practice_financial_risk`), otherwise you get an "index and table must in the same schema" error.
- **When to create Kafka PIPE**: PIPE DDL execution attempts to connect to the Kafka broker to verify the subscription. Create it only after the Kafka cluster and topic are ready.
- **Risk scoring formula limitations**: The simple rule-based scoring used in this guide (amount deviation + geographic distance + historical fraud) is suitable for demonstration. For production, call a machine learning model API via an External Function and write the scoring results back to the ADS layer.

---

## Related Documentation

- [CREATE DYNAMIC TABLE](../sql_reference/create-dynamic-table.md) — Full syntax and parameter reference for Dynamic Table
- [CREATE PIPE](../sql_reference/create-pipe.md) — Kafka PIPE configuration and `READ_KAFKA` parameter reference
- [CREATE FUNCTION](../sql_reference/create-function.md) — SQL UDF syntax
- [Column Masking](../security/column-masking.md) — Column-level masking configuration and permissions
- [GRANT / REVOKE](../sql_reference/grant-revoke.md) — RBAC permission management
- [Industrial IoT Device Health Monitoring Data Warehouse Best Practices](iot-device-health-monitoring-dw-best-practices.md) — Reference for similar architectures

> ⚠️ **Note**: Column Masking currently matches authorized usernames via `current_user()`. Add all usernames that need plaintext access to the masking function's allowlist. If your Lakehouse version supports role-based dynamic evaluation (such as `HAS_ROLE('role_name')`), use roles instead of username lists for more flexible maintenance. Contact Singdata technical support to confirm whether your version supports this function.