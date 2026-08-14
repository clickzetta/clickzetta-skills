# Building a Content Platform Recommendation System Data Warehouse

This guide uses the Steam game platform dataset (Steam Dataset 2025, approximately 240,000 games and 3.9 million reviews) to combine user interaction behavior (watch, like, share) with content metadata and build a three-layer data warehouse that supports recommendation model feature engineering. The guide demonstrates the full **Kafka PIPE → OSS PIPE → External Function → Bronze → Silver → Gold → ZettaPark** pipeline end to end, covering four key capabilities: Vector Index (IVFPQ vector recall), Inverted Index (Chinese full-text search), Dynamic Table (daily Gold layer refresh), and External Function.

![](/.topwrite/assets/anim-21-content-recommendation.svg)

---

## Overview

The core challenge of a content recommendation system is unifying user behavior signals and content semantic information into the same feature space. Singdata Lakehouse addresses the key data warehouse challenges with the following combination:

| Problem | Solution |
|---|---|
| High-frequency real-time writes of user behavior events; low-latency ingestion required | Kafka PIPE continuous ingestion; no custom consumer code needed |
| Batch import of content metadata (titles, tags, descriptions) | OSS PIPE scan-and-import; triggered automatically when files land |
| Content text needs embeddings for similarity recall | External Function calls a vectorization model; results stored in a VECTOR column |
| Approximate nearest neighbor (ANN) search over large content vector sets | Vector Index IVFPQ with sub-linear time complexity for vector recall |
| Full-text search on Chinese content titles and descriptions | Inverted Index with Chinese Analyzer and the `MATCH_ALL` function |
| Automatic incremental computation across Bronze → Silver → Gold | Dynamic Table with declarative SQL; the system schedules the dependency chain |
| Feature engineering scripts need access to Gold layer data | ZettaPark Python Task with direct access to Lakehouse tables |

---

## SQL Commands Used

| Command / Function | Purpose | Notes |
|---|---|---|
| `CREATE TABLE` | Create the Bronze layer raw tables and embedding storage table | Includes `VECTOR(N)` type columns |
| `CREATE BLOOMFILTER INDEX` | Create a Bloomfilter Index on the `content_id` column | Speeds up high-cardinality column point lookups |
| `CREATE INVERTED INDEX` | Create a Chinese Inverted Index on the `description` column | Uses `analyzer='chinese'` |
| `BUILD INDEX` | Build index on existing data | Required for both Vector and Inverted indexes |
| `CREATE VECTOR INDEX` | IVFPQ vector index for faster ANN search | `PROPERTIES('index_type'='IVFPQ')` |
| `COSINE_DISTANCE` | Calculate cosine distance between two vectors | Used for similarity ranking; smaller means more similar |
| `MATCH_ALL` | Full-text search returning a boolean | Requires a built Inverted Index |
| `CREATE PIPE` | Create a Kafka or OSS continuous ingestion pipeline | Bound to the Bronze layer target table |
| `CREATE DYNAMIC TABLE` | Create incremental computation tables for Silver and Gold layers | Omit REFRESH INTERVAL; schedule via Studio Task |
| `REFRESH DYNAMIC TABLE` | Trigger a manual refresh | Use during initial build or debugging |
| `PARTITIONED BY` | Gold layer Dynamic Table partitioned by date | Use with `TBLPROPERTIES('static_partitions'='true')` |

---

## Prerequisites

All examples in this guide run under the `best_practice_content_rec` Schema.

```sql
CREATE SCHEMA IF NOT EXISTS best_practice_content_rec;
```

---

## Bronze Layer: Interaction Events Table (Kafka PIPE Target)

### Create Table

```sql
CREATE TABLE IF NOT EXISTS best_practice_content_rec.bronze_interaction_events (
    event_id     STRING,
    user_id      STRING,
    content_id   STRING,
    event_type   STRING,          -- watch / like / share
    session_id   STRING,
    duration_sec INT,             -- watch duration in seconds; 0 for like/share
    event_time   TIMESTAMP,
    platform     STRING,          -- pc / mobile / console
    ingest_time  TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

### Create Bloomfilter Index

Silver layer queries frequently filter on `content_id`, which is a high-cardinality column. A Bloomfilter Index is well-suited for this.

```sql
-- Must run in the best_practice_content_rec context
USE SCHEMA best_practice_content_rec;
CREATE BLOOMFILTER INDEX IF NOT EXISTS idx_bf_content_id
ON TABLE bronze_interaction_events (content_id);
```

> ⚠️ **Note**: `CREATE BLOOMFILTER INDEX` requires the same Schema context as the target table. Running it across Schemas produces an "index and table must in the same schema" error. Use `USE SCHEMA` to switch context or specify the `-s` parameter in cz-cli.

> 💡 **Tip**: The examples below use **cz-cli** (the Singdata Lakehouse command-line tool). If cz-cli is not installed, see the [cz-cli Installation and Usage Guide](../setup_cz_cli.md). You can also run the SQL in **Development → SQL Editor** in Singdata Studio and configure or trigger scheduled tasks under **Studio → Tasks**.

### Configure Kafka PIPE

User behavior events collected by the client SDK are sent to a Kafka topic. The PIPE continuously consumes and writes them to the Bronze table.

Create the raw receiving table first (the PIPE writes JSON strings), then create the PIPE:

```sql
CREATE TABLE IF NOT EXISTS best_practice_content_rec.bronze_kafka_raw_events (
    value STRING
);

CREATE PIPE IF NOT EXISTS best_practice_content_rec.pipe_user_events
    VIRTUAL_CLUSTER = 'DEFAULT'
    BATCH_INTERVAL_IN_SECONDS = '30'
AS
COPY INTO best_practice_content_rec.bronze_kafka_raw_events
FROM (
    SELECT CAST(value AS STRING) AS value
    FROM READ_KAFKA(
        '<kafka-broker>:9092',          -- replace with the actual broker address
        'user_behavior_events',          -- topic name
        '',
        'cz_content_rec_consumer',       -- consumer group ID
        '','','','',
        'raw', 'raw',
        0,
        map()
    )
);
```

> 💡 **Tip**: The positional parameters 5–8 of `READ_KAFKA` (start/end offsets and timestamps) must be left empty in PIPE DDL; the PIPE runtime manages them automatically.

**Option 1: Write via Kafka (recommended)**

In production, the client SDK serializes behavior events as JSON and sends them to the Kafka topic. The PIPE automatically consumes and writes them to `bronze_kafka_raw_events`. The following example uses `kafka-python`:

```python
from kafka import KafkaProducer
import json
import time

producer = KafkaProducer(
    bootstrap_servers=['<kafka-broker>:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

event = {
    "event_id": "EVT001",
    "user_id":  "USR001",
    "content_id": "GAME_730",
    "event_type": "watch",
    "session_id": "SES001",
    "duration_sec": 3600,
    "event_time": "2026-05-01 10:00:00",
    "platform": "pc"
}
producer.send('user_behavior_events', value=event)
producer.flush()
```

**Option 2: INSERT simulation (when no Kafka environment is available)**

If Kafka is not yet configured, use either of the following methods to write to `bronze_interaction_events` and simulate parsed Kafka messages. Downstream Silver layer logic can then be validated normally.

**Import from a local CSV file (recommended)**

```sql
-- Step 1: Upload the local CSV file to User Volume via SQL PUT
PUT '/path/to/interaction_events.csv' TO USER VOLUME FILE 'interaction_events.csv';
```

```sql
-- Step 2: COPY INTO the table from User Volume
COPY INTO best_practice_content_rec.bronze_interaction_events
FROM USER VOLUME
USING csv
OPTIONS('header'='true', 'sep'=',', 'nullValue'='')
FILES ('interaction_events.csv');
```

You can also insert a small batch of test data inline (no CSV file required):

```sql
INSERT INTO best_practice_content_rec.bronze_interaction_events
  (event_id, user_id, content_id, event_type, session_id, duration_sec, event_time, platform)
VALUES
  ('EVT001','USR001','GAME_730',    'watch', 'SES001', 3600, CAST('2026-05-01 10:00:00' AS TIMESTAMP), 'pc'),
  ('EVT002','USR001','GAME_570',    'like',  'SES001', 0,    CAST('2026-05-01 10:05:00' AS TIMESTAMP), 'pc'),
  ('EVT003','USR002','GAME_730',    'share', 'SES002', 0,    CAST('2026-05-01 11:00:00' AS TIMESTAMP), 'mobile'),
  ('EVT004','USR002','GAME_292030', 'watch', 'SES002', 7200, CAST('2026-05-01 11:30:00' AS TIMESTAMP), 'mobile'),
  ('EVT005','USR003','GAME_1091500','watch', 'SES003', 1800, CAST('2026-05-01 12:00:00' AS TIMESTAMP), 'pc'),
  ('EVT006','USR003','GAME_730',    'like',  'SES003', 0,    CAST('2026-05-01 12:10:00' AS TIMESTAMP), 'pc'),
  ('EVT007','USR004','GAME_570',    'watch', 'SES004', 5400, CAST('2026-05-01 13:00:00' AS TIMESTAMP), 'console'),
  ('EVT008','USR004','GAME_292030', 'like',  'SES004', 0,    CAST('2026-05-01 13:20:00' AS TIMESTAMP), 'console'),
  ('EVT009','USR005','GAME_1091500','share', 'SES005', 0,    CAST('2026-05-01 14:00:00' AS TIMESTAMP), 'mobile'),
  ('EVT010','USR005','GAME_730',    'watch', 'SES005', 2700, CAST('2026-05-01 14:15:00' AS TIMESTAMP), 'mobile'),
  ('EVT011','USR001','GAME_1091500','watch', 'SES006', 4320, CAST('2026-05-02 09:00:00' AS TIMESTAMP), 'pc'),
  ('EVT012','USR002','GAME_570',    'share', 'SES007', 0,    CAST('2026-05-02 10:00:00' AS TIMESTAMP), 'pc'),
  ('EVT013','USR003','GAME_292030', 'watch', 'SES008', 6600, CAST('2026-05-02 11:00:00' AS TIMESTAMP), 'console'),
  ('EVT014','USR004','GAME_730',    'share', 'SES009', 0,    CAST('2026-05-02 12:00:00' AS TIMESTAMP), 'mobile'),
  ('EVT015','USR005','GAME_570',    'like',  'SES010', 0,    CAST('2026-05-02 13:00:00' AS TIMESTAMP), 'pc');
```

Verify the Bronze layer row count:

```sql
SELECT COUNT(*) AS bronze_event_count
FROM best_practice_content_rec.bronze_interaction_events;
```

```
bronze_event_count
------------------
15
```

---

## Bronze Layer: Content Metadata Table (OSS PIPE Import)

### Create Table

```sql
CREATE TABLE IF NOT EXISTS best_practice_content_rec.bronze_content_metadata (
    content_id    STRING,
    title         STRING,
    description   STRING,      -- Chinese description; supports full-text search
    tags          STRING,      -- comma-separated tags
    category      STRING,
    release_date  DATE,
    language      STRING,
    developer     STRING,
    price         DOUBLE,
    positive_pct  DOUBLE,      -- positive review rate (0–1)
    load_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```


### Create Inverted Index (Chinese Full-Text Search)

The content descriptions are in Chinese. Create an Inverted Index on the `description` column and specify the `chinese` tokenizer:

```sql
USE SCHEMA best_practice_content_rec;
CREATE INVERTED INDEX IF NOT EXISTS idx_inv_description
ON TABLE bronze_content_metadata (description)
WITH PROPERTIES ('analyzer' = 'chinese');
```

Build the index for existing data (`CREATE INDEX` only applies to newly written data; existing data must be manually built):

```sql
USE SCHEMA best_practice_content_rec;
BUILD INDEX idx_inv_description ON bronze_content_metadata;
```

> ⚠️ **Note**: `BUILD INDEX` syntax does not support the `ON TABLE` keyword. The correct form is `BUILD INDEX <index_name> ON <table_name>`, and it must run in the same Schema context.

### Configure OSS PIPE (Bulk Content Metadata Import)

The content operations team periodically uploads new game information in CSV format to OSS. The OSS PIPE uses LIST_PURGE mode to auto-scan and import:

```sql
-- First create a Storage Connection (OSS access credentials)
CREATE STORAGE CONNECTION IF NOT EXISTS best_practice_content_rec.conn_content_oss
TYPE = OSS
ACCESS_ID  = '<your-access-id>'
ACCESS_KEY = '<your-access-key>'
ENDPOINT   = 'oss-cn-hangzhou.aliyuncs.com';

-- Create an External Volume
CREATE EXTERNAL VOLUME IF NOT EXISTS best_practice_content_rec.vol_content_metadata
TYPE = OSS
BUCKET = '<your-bucket>'
PATH   = 'content-rec/metadata/'
CONNECTION = conn_content_oss;

-- Create OSS PIPE (LIST_PURGE: delete source files after import to prevent duplicate ingestion)
CREATE PIPE IF NOT EXISTS best_practice_content_rec.pipe_content_metadata
    VIRTUAL_CLUSTER = 'DEFAULT'
    INGEST_MODE     = 'LIST_PURGE'
AS
COPY INTO best_practice_content_rec.bronze_content_metadata
FROM VOLUME vol_content_metadata
USING csv
OPTIONS('header'='true', 'sep'=',', 'quote'='"');
```

> 💡 **Tip**: LIST_PURGE mode deletes the original files from the Volume after a successful import, which suits ETL scenarios. To retain original files for replay support, use LIST (non-deleting) mode.

### Load Sample Data

Using five classic games from Steam Dataset 2025 as examples:

```sql
INSERT INTO best_practice_content_rec.bronze_content_metadata
  (content_id, title, description, tags, category, release_date,
   language, developer, price, positive_pct)
VALUES
  ('GAME_730',    'Counter-Strike 2',
   'Multiplayer competitive shooter where players join terrorist or counter-terrorist teams',
   'FPS,Shooter,Multiplayer,Competitive,Action',
   'Action', CAST('2023-09-27' AS DATE), 'zh', 'Valve', 0.0, 0.78),
  ('GAME_570',    'Dota 2',
   'Team strategy game where two 5-player teams compete for victory',
   'MOBA,Strategy,Multiplayer,Free to Play',
   'Strategy', CAST('2013-07-09' AS DATE), 'zh', 'Valve', 0.0, 0.84),
  ('GAME_292030', 'The Witcher 3: Wild Hunt',
   'Open-world RPG with a rich storyline',
   'RPG,Open World,Adventure,Story Rich,Fantasy',
   'RPG', CAST('2015-05-18' AS DATE), 'zh', 'CD Projekt Red', 39.99, 0.97),
  ('GAME_1091500','Cyberpunk 2077',
   'Futuristic open-world RPG with a cyberpunk aesthetic',
   'RPG,Open World,Cyberpunk,Action,Sci-fi',
   'RPG', CAST('2020-12-10' AS DATE), 'zh', 'CD Projekt Red', 59.99, 0.79),
  ('GAME_271590', 'Grand Theft Auto V',
   'Open-world action-adventure game',
   'Action,Open World,Multiplayer,Crime',
   'Action', CAST('2015-04-14' AS DATE), 'en', 'Rockstar Games', 29.99, 0.88);
```

Verify Chinese full-text search:

```sql
SELECT content_id, title, description
FROM best_practice_content_rec.bronze_content_metadata
WHERE MATCH_ALL(description, 'open-world');
```

```
content_id   | title                    | description
-------------+--------------------------+----------------------
GAME_292030  | The Witcher 3: Wild Hunt | Open-world RPG with a rich storyline
GAME_1091500 | Cyberpunk 2077           | Futuristic open-world RPG with a cyberpunk aesthetic
GAME_271590  | Grand Theft Auto V       | Open-world action-adventure game
```

3 Open World games are correctly returned.

---

## Bronze Layer: Content Embedding Table (External Function + VECTOR Type)

### Create Tables

```sql
CREATE TABLE IF NOT EXISTS best_practice_content_rec.bronze_content_embedding (
    content_id  STRING,
    title       STRING,
    description STRING,
    tags        STRING,
    embedding   VECTOR(128)    -- 128-dimensional embedding generated by External Function
);
```

### Generate Embeddings with External Function

In production, deploy an External Function to call a vectorization model (such as DashScope text-embedding-v3) to automatically generate embeddings:

```sql
-- Assumes External Function text2vec is already deployed
-- Usage example (run in an ops script or ZettaPark Task)
INSERT INTO best_practice_content_rec.bronze_content_embedding
  (content_id, title, description, tags, embedding)
SELECT
    content_id,
    title,
    description,
    tags,
    CAST(best_practice_content_rec.text2vec(description) AS VECTOR(128))
FROM best_practice_content_rec.bronze_content_metadata;
```

In a test environment where External Function is not yet deployed, use SQL to generate deterministic 128-dimensional test vectors. The `vector_seed` below is only for constructing executable example data and does not represent real model embeddings:

```sql
INSERT INTO best_practice_content_rec.bronze_content_embedding
  (content_id, title, description, tags, embedding)
SELECT
    content_id,
    title,
    description,
    tags,
    CAST(
        CONCAT(
            '[',
            ARRAY_JOIN(
                TRANSFORM(
                    SEQUENCE(1, 128),
                    x -> CAST(ROUND(((x * 37 + vector_seed) % 1000) / 1000.0, 4) AS STRING)
                ),
                ','
            ),
            ']'
        ) AS VECTOR(128)
    ) AS embedding
FROM (
    SELECT 'GAME_730' AS content_id, 'Counter-Strike 2' AS title,
           'Multiplayer competitive shooter where players join terrorist or counter-terrorist teams' AS description,
           'FPS,Shooter,Multiplayer,Competitive,Action' AS tags,
           300 AS vector_seed
    UNION ALL
    SELECT 'GAME_570', 'Dota 2',
           'Team strategy game where two 5-player teams compete for victory',
           'MOBA,Strategy,Multiplayer,Free to Play',
           420
    UNION ALL
    SELECT 'GAME_292030', 'The Witcher 3: Wild Hunt',
           'Open-world RPG with a rich storyline',
           'RPG,Open World,Adventure,Story Rich,Fantasy',
           180
    UNION ALL
    SELECT 'GAME_1091500', 'Cyberpunk 2077',
           'Futuristic open-world RPG with a cyberpunk aesthetic',
           'RPG,Open World,Cyberpunk,Action,Sci-fi',
           190
    UNION ALL
    SELECT 'GAME_271590', 'Grand Theft Auto V',
           'Open-world action-adventure game',
           'Action,Open World,Multiplayer,Crime',
           260
) s;
```

Verify the vector dimensions written:

```sql
SELECT content_id, size(embedding) AS vector_dim
FROM best_practice_content_rec.bronze_content_embedding
ORDER BY content_id;
```

```
content_id   | vector_dim
-------------+-----------
GAME_1091500 | 128
GAME_271590  | 128
GAME_292030  | 128
GAME_570     | 128
GAME_730     | 128
```

To manually construct a single test record, you can also `CAST` a complete 128-dimensional array string directly to `VECTOR(128)`. The following example runs directly:

```sql
INSERT INTO best_practice_content_rec.bronze_content_embedding
  (content_id, title, description, tags, embedding)
VALUES
  ('GAME_730', 'Counter-Strike 2', 'Multiplayer competitive shooter where players join terrorist or counter-terrorist teams',
   'FPS,Shooter,Multiplayer,Competitive,Action',
   CAST('[0.3370,0.3740,0.4110,0.4480,0.4850,0.5220,0.5590,0.5960,0.6330,0.6700,0.7070,0.7440,0.7810,0.8180,0.8550,0.8920,0.9290,0.9660,0.0030,0.0400,0.0770,0.1140,0.1510,0.1880,0.2250,0.2620,0.2990,0.3360,0.3730,0.4100,0.4470,0.4840,0.5210,0.5580,0.5950,0.6320,0.6690,0.7060,0.7430,0.7800,0.8170,0.8540,0.8910,0.9280,0.9650,0.0020,0.0390,0.0760,0.1130,0.1500,0.1870,0.2240,0.2610,0.2980,0.3350,0.3720,0.4090,0.4460,0.4830,0.5200,0.5570,0.5940,0.6310,0.6680,0.7050,0.7420,0.7790,0.8160,0.8530,0.8900,0.9270,0.9640,0.0010,0.0380,0.0750,0.1120,0.1490,0.1860,0.2230,0.2600,0.2970,0.3340,0.3710,0.4080,0.4450,0.4820,0.5190,0.5560,0.5930,0.6300,0.6670,0.7040,0.7410,0.7780,0.8150,0.8520,0.8890,0.9260,0.9630,0.0000,0.0370,0.0740,0.1110,0.1480,0.1850,0.2220,0.2590,0.2960,0.3330,0.3700,0.4070,0.4440,0.4810,0.5180,0.5550,0.5920,0.6290,0.6660,0.7030,0.7400,0.7770,0.8140,0.8510,0.8880,0.9250,0.9620,0.9990,0.0360]' AS VECTOR(128)));
```

> 💡 **Tip**: The `TO_VECTOR` function is not available in the current version. Use `CAST('<array_string>' AS VECTOR(N))` to generate VECTOR column data. The VECTOR dimension N must match the dimension defined at table creation; a mismatch produces a `NULL` vector, and subsequent `COSINE_DISTANCE` calls also return `NULL`.

### Create Vector Index (IVFPQ)

IVFPQ (Inverted File + Product Quantization) is a commonly used ANN index type in recommendation systems. Quantization and partitioning dramatically reduce search time complexity:

```sql
USE SCHEMA best_practice_content_rec;
CREATE VECTOR INDEX IF NOT EXISTS idx_vec_content_embedding
ON TABLE bronze_content_embedding (embedding)
PROPERTIES(
    'index_type'        = 'IVFPQ',
    'distance_function' = 'cosine',
    'nlist'             = '100',      -- number of cluster centroids; increase for larger datasets
    'M'                 = '32',       -- number of sub-quantizers; affects accuracy and speed
    'm'                 = '4'         -- compression bytes
);
```

Build the index on existing data:

```sql
USE SCHEMA best_practice_content_rec;
BUILD INDEX idx_vec_content_embedding ON bronze_content_embedding;
```

> ⚠️ **Note**: `nlist` should be in the range `sqrt(N)` to `4*sqrt(N)` (N is the total number of vectors). For production data in the hundreds of thousands, `nlist=100` and `M=32` are common starting points. Tune based on recall rate and latency metrics.

### Vector Similarity Search

Use The Witcher 3's embedding as the query vector to find the most similar content:

```sql
SELECT
    e.content_id,
    e.title,
    ROUND(COSINE_DISTANCE(e.embedding, q.query_embedding), 6) AS cos_dist
FROM best_practice_content_rec.bronze_content_embedding e
CROSS JOIN (
    SELECT embedding AS query_embedding
    FROM best_practice_content_rec.bronze_content_embedding
    WHERE content_id = 'GAME_292030'
) q
ORDER BY cos_dist ASC
LIMIT 4;
```

```
content_id   | title                    | cos_dist
-------------+--------------------------+---------------------
GAME_292030  | The Witcher 3: Wild Hunt | 0
GAME_1091500 | Cyberpunk 2077           | 0.045093998312950134
GAME_271590  | Grand Theft Auto V       | 0.09233599901199341
GAME_730     | Counter-Strike 2         | 0.16785000264644623
```

`COSINE_DISTANCE` of 0 means identical (the query vector itself). The test vectors are generated with a fixed seed to verify that VECTOR writes, index builds, and similarity SQL execute correctly. In production, use a real embedding model to generate vectors so that semantically similar results have business interpretability.

---

## Silver Layer Dynamic Table: Denoising Cleansing and Interaction Sequences

The Silver layer does two things on top of Bronze behavior events:

1. LEFT JOIN `bronze_content_metadata` to add content title, category, developer, and other dimension fields to each event
2. Calculate normalized interaction weights and filter invalid interactions (`is_valid`) — watch durations under 60 seconds are treated as invalid browsing noise

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_content_rec.silver_user_content_interactions
AS
SELECT
    e.event_id,
    e.user_id,
    e.content_id,
    e.event_type,
    e.session_id,
    e.duration_sec,
    e.event_time,
    e.platform,
    m.title         AS content_title,
    m.tags          AS content_tags,
    m.category      AS content_category,
    m.developer     AS developer,
    -- Normalized interaction weights: signal strength from high to low
    CASE
        WHEN e.event_type = 'share' THEN 3.0
        WHEN e.event_type = 'like'  THEN 2.0
        WHEN e.event_type = 'watch' AND e.duration_sec >= 60 THEN 1.0
        ELSE 0.0
    END AS interaction_weight,
    -- Valid interaction flag (watch duration < 60s treated as noise)
    CASE
        WHEN e.event_type IN ('like','share') THEN 1
        WHEN e.event_type = 'watch' AND e.duration_sec >= 60 THEN 1
        ELSE 0
    END AS is_valid
FROM best_practice_content_rec.bronze_interaction_events e
LEFT JOIN best_practice_content_rec.bronze_content_metadata m
    ON e.content_id = m.content_id;
```

**Interaction weight design notes**:

| Event Type | Weight | Rationale |
|---|---|---|
| `share` | 3.0 | Strong intent signal; active sharing |
| `like` | 2.0 | Clear positive feedback |
| `watch` (≥60s) | 1.0 | Implicit preference; duration threshold filters accidental plays |
| `watch` (<60s) | 0.0 (invalid) | May be accidental click or channel switch; removes noise |

Trigger the initial refresh manually:

```sql
REFRESH DYNAMIC TABLE best_practice_content_rec.silver_user_content_interactions;

SELECT COUNT(*) AS silver_count
FROM best_practice_content_rec.silver_user_content_interactions;
```

```
silver_count
------------
15
```

View sample user-content interaction sequences:

```sql
SELECT user_id, content_id, content_title, event_type, interaction_weight, is_valid
FROM best_practice_content_rec.silver_user_content_interactions
ORDER BY user_id, event_time
LIMIT 10;
```

```
user_id | content_id  | content_title            | event_type | interaction_weight | is_valid
--------+-------------+--------------------------+------------+--------------------+---------
USR001  | GAME_730    | Counter-Strike 2         | watch      | 1.0                | 1
USR001  | GAME_570    | Dota 2                   | like       | 2.0                | 1
USR001  | GAME_1091500| Cyberpunk 2077           | watch      | 1.0                | 1
USR002  | GAME_730    | Counter-Strike 2         | share      | 3.0                | 1
USR002  | GAME_292030 | The Witcher 3: Wild Hunt | watch      | 1.0                | 1
USR002  | GAME_570    | Dota 2                   | share      | 3.0                | 1
USR003  | GAME_1091500| Cyberpunk 2077           | watch      | 1.0                | 1
USR003  | GAME_730    | Counter-Strike 2         | like       | 2.0                | 1
USR003  | GAME_292030 | The Witcher 3: Wild Hunt | watch      | 1.0                | 1
USR004  | GAME_570    | Dota 2                   | watch      | 1.0                | 1
```

All 15 sample records are valid interactions (`is_valid=1`) because all `watch` durations in the INSERT simulated data are ≥ 60 seconds.

---

## Gold Layer Dynamic Table: Content Popularity Metrics

The Gold layer aggregates content popularity metrics from the Silver layer at `content_id` + date granularity, for use as content-side features in recommendation models.

This Dynamic Table is partitioned by `stat_date` and declared in static partition mode:

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_content_rec.gold_content_popularity
PARTITIONED BY (stat_date)
TBLPROPERTIES ('static_partitions' = 'true')
AS
SELECT
    content_id,
    content_title,
    content_category,
    developer,
    CAST(DATE_TRUNC('day', event_time) AS DATE)  AS stat_date,
    COUNT(*)                                     AS total_interactions,
    SUM(CASE WHEN event_type = 'watch' AND duration_sec >= 60 THEN 1 ELSE 0 END) AS watch_count,
    SUM(CASE WHEN event_type = 'like'  THEN 1 ELSE 0 END)                        AS like_count,
    SUM(CASE WHEN event_type = 'share' THEN 1 ELSE 0 END)                        AS share_count,
    SUM(interaction_weight)                      AS weighted_score,
    COUNT(DISTINCT user_id)                      AS unique_users,
    ROUND(AVG(CASE WHEN event_type = 'watch' THEN duration_sec ELSE NULL END), 2) AS avg_watch_sec
FROM best_practice_content_rec.silver_user_content_interactions
WHERE is_valid = 1
GROUP BY
    content_id, content_title, content_category, developer,
    CAST(DATE_TRUNC('day', event_time) AS DATE);
```

> ⚠️ **Note**: A partitioned Dynamic Table must explicitly declare `TBLPROPERTIES ('static_partitions' = 'true')` to use static partition mode. Without this declaration, the system defaults to dynamic partition inference, which may cause abnormal partition data overwriting in incremental refresh scenarios.

Trigger the initial refresh manually and view results:

```sql
REFRESH DYNAMIC TABLE best_practice_content_rec.gold_content_popularity;

SELECT content_id, content_title, content_category, stat_date,
       total_interactions, watch_count, like_count, share_count,
       weighted_score, unique_users
FROM best_practice_content_rec.gold_content_popularity
ORDER BY weighted_score DESC;
```

```
content_id   | content_title            | content_category | stat_date  | total | watch | like | share | weighted_score | unique_users
-------------+--------------------------+------------------+------------+-------+-------+------+-------+----------------+-------------
GAME_730     | Counter-Strike 2         | Action           | 2026-05-01 | 4     | 2     | 1    | 1     | 7.0            | 4
GAME_570     | Dota 2                   | Strategy         | 2026-05-02 | 2     | 0     | 1    | 1     | 5.0            | 2
GAME_1091500 | Cyberpunk 2077           | RPG              | 2026-05-01 | 2     | 1     | 0    | 1     | 4.0            | 2
GAME_730     | Counter-Strike 2         | Action           | 2026-05-02 | 1     | 0     | 0    | 1     | 3.0            | 1
GAME_570     | Dota 2                   | Strategy         | 2026-05-01 | 2     | 1     | 1    | 0     | 3.0            | 2
GAME_292030  | The Witcher 3: Wild Hunt | RPG              | 2026-05-01 | 2     | 1     | 1    | 0     | 3.0            | 2
GAME_1091500 | Cyberpunk 2077           | RPG              | 2026-05-02 | 1     | 1     | 0    | 0     | 1.0            | 1
GAME_292030  | The Witcher 3: Wild Hunt | RPG              | 2026-05-02 | 1     | 1     | 0    | 0     | 1.0            | 1
```

Counter-Strike 2 (GAME_730) has the highest weighted score on 2026-05-01 (7.0) because 4 different users interacted that day (watch×2, like×1, share×1), and the high share weight boosted the total. Cyberpunk 2077's weighted score on May 1 (4.0) exceeds Dota 2 on the same day (3.0), mainly driven by one share (weight 3.0).

---

## Gold Layer Dynamic Table: User Interest Vectors

User interest vectors summarize each user's weighted interaction scores across content categories, serving as user-side features for recommendation models:

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_content_rec.gold_user_interest_profile
AS
SELECT
    user_id,
    CAST(DATE_TRUNC('day', MAX(event_time)) AS DATE)   AS profile_date,
    COUNT(DISTINCT content_id)                         AS content_count,
    SUM(interaction_weight)                            AS total_weight,
    COLLECT_LIST(content_id)                           AS interacted_content_ids,
    -- Accumulate weights by content category to form category interest vector
    SUM(CASE WHEN content_category = 'Action'   THEN interaction_weight ELSE 0 END) AS action_score,
    SUM(CASE WHEN content_category = 'Strategy' THEN interaction_weight ELSE 0 END) AS strategy_score,
    SUM(CASE WHEN content_category = 'RPG'      THEN interaction_weight ELSE 0 END) AS rpg_score
FROM best_practice_content_rec.silver_user_content_interactions
WHERE is_valid = 1
GROUP BY user_id;
```

```sql
REFRESH DYNAMIC TABLE best_practice_content_rec.gold_user_interest_profile;

SELECT user_id, content_count, total_weight,
       action_score, strategy_score, rpg_score,
       interacted_content_ids
FROM best_practice_content_rec.gold_user_interest_profile
ORDER BY total_weight DESC;
```

```
user_id | content_count | total_weight | action_score | strategy_score | rpg_score | interacted_content_ids
--------+---------------+--------------+--------------+----------------+-----------+-----------------------
USR002  | 3             | 7.0          | 3.0          | 3.0            | 1.0       | [GAME_730, GAME_292030, GAME_570]
USR004  | 3             | 6.0          | 3.0          | 1.0            | 2.0       | [GAME_570, GAME_292030, GAME_730]
USR005  | 3             | 6.0          | 1.0          | 2.0            | 3.0       | [GAME_1091500, GAME_730, GAME_570]
USR001  | 3             | 4.0          | 1.0          | 2.0            | 1.0       | [GAME_730, GAME_570, GAME_1091500]
USR003  | 3             | 4.0          | 2.0          | 0.0            | 2.0       | [GAME_1091500, GAME_730, GAME_292030]
```

USR002's category distribution is balanced (action=3.0, strategy=3.0), indicating broad interests. USR005's rpg_score (3.0) is significantly higher than other categories — an RPG-preferring user for whom the recommendation system should prioritize RPG content. The `interacted_content_ids` field can be used directly to construct item-to-item collaborative filtering training samples.

---

## Dynamic Table Refresh Scheduling (Studio Task)

Omit `REFRESH INTERVAL` from DDL and create refresh tasks in Studio to centrally manage scheduling, alerts, and data quality checks.

**Studio Tasks created** (path: `best_practices/content_rec/`):

1. Create a SQL-type task `refresh_gold_content_popularity` under **best_practices/content_rec/** in Studio
2. Task SQL content:

```sql
REFRESH DYNAMIC TABLE best_practice_content_rec.gold_content_popularity;
REFRESH DYNAMIC TABLE best_practice_content_rec.gold_user_interest_profile;
```

3. Configure the schedule (run daily at 02:00):

```bash
cz-cli task save-cron refresh_gold_content_popularity -p skill_test --cron "0 2 * * *"
```

4. Deploy the task (scheduling begins after deployment):

```bash
cz-cli task deploy refresh_gold_content_popularity -p skill_test
```

> 💡 **Tip**: Attach monitoring alert rules (such as refresh failure notifications) and data quality rules (such as alerting when Gold layer row count falls below a threshold) to the Studio Task — all managed in a single task node. This is the core advantage of omitting `REFRESH INTERVAL`.

Create a separate refresh task for the Silver layer Dynamic Table (same path, task name `refresh_silver_interactions`), or merge Silver and Gold refreshes into a single DAG that triggers Gold refresh after Silver completes.

---

## ZettaPark Python Task: Feature Engineering and Sample Export

A ZettaPark Task runs a Python script with direct access to the Gold layer to generate the feature matrix needed for recommendation model training.

Create a VIRTUAL-type task `feature_engineering_export` under `best_practices/content_rec/` in Studio. Example script:

```python
from clickzetta_zettapark.session import Session

session = Session.builder.configs({
    "instance":  "<instance>",
    "workspace": "<workspace>",
    "schema":    "best_practice_content_rec",
    "vcluster":  "DEFAULT",
    "username":  "<username>",
    "password":  "<password>",
}).create()

# Read user interest vectors from the Gold layer
user_profile_df = session.table("gold_user_interest_profile")

# Read content popularity from the Gold layer
content_pop_df = session.table("gold_content_popularity")

# Cross JOIN to build user-content feature pairs
feature_df = user_profile_df.join(
    content_pop_df,
    how="cross"
).select(
    "user_id",
    "content_id",
    "total_weight",
    "action_score",
    "strategy_score",
    "rpg_score",
    "weighted_score",
    "unique_users",
)

# Export as Parquet to Volume
feature_df.write.mode("overwrite").parquet(
    "volume://vol_content_metadata/features/user_content_features.parquet"
)

print(f"Feature matrix exported: {feature_df.count()} rows")
session.close()
```

> 💡 **Tip**: ZettaPark Tasks are created as VIRTUAL type in Studio. Once the connection is configured, they can directly operate on Lakehouse tables. The feature export frequency typically matches the Gold layer refresh task, and it can be configured as a downstream dependency task in Studio to ensure feature data is always based on the latest Gold layer results.

---

## Data Warehouse Object Summary

After the full build, all objects under the `best_practice_content_rec` Schema:

```sql
SHOW TABLES IN best_practice_content_rec;
```

```
schema_name                  | table_name                       | is_dynamic
-----------------------------+----------------------------------+-----------
best_practice_content_rec    | bronze_content_embedding         | false
best_practice_content_rec    | bronze_content_metadata          | false
best_practice_content_rec    | bronze_interaction_events        | false
best_practice_content_rec    | gold_content_popularity          | true
best_practice_content_rec    | gold_user_interest_profile       | true
best_practice_content_rec    | silver_user_content_interactions | true
```

Pipeline structure:

```
Kafka Topic (user_behavior_events)
    │  Kafka PIPE (pipe_user_events · BATCH_INTERVAL=30s)
    ▼
bronze_interaction_events      bronze_content_metadata
  Bloomfilter Index (content_id)  Inverted Index (description, chinese)
         │                                │
         └────────────┬─────────────────┘
                      ▼
         silver_user_content_interactions (Dynamic Table)
         interaction_weight · is_valid denoising
                      │
         ┌────────────┴──────────────────┐
         ▼                               ▼
gold_content_popularity (DT)   gold_user_interest_profile (DT)
PARTITIONED BY (stat_date)     category-level interest vectors
static_partitions=true
                      │
                      ▼
         ZettaPark Python Task
         feature_engineering_export
         → user × content feature matrix → Volume

OSS Volume (vol_content_metadata)
    │  OSS PIPE (pipe_content_metadata · LIST_PURGE)
    ▼
bronze_content_metadata
    │  External Function (text2vec)
    ▼
bronze_content_embedding (VECTOR(128))
    Vector Index IVFPQ (idx_vec_content_embedding)
    → COSINE_DISTANCE ANN recall
```

Studio Task scheduling path: `best_practices/content_rec/`
- `refresh_gold_content_popularity` (daily 02:00, refreshes two Gold Dynamic Tables)
- `feature_engineering_export` (triggered after Gold refresh completes)

---

## Notes

- **Bloomfilter Index does not support BUILD INDEX**: Bloomfilter indexes only apply to data written after creation; `BUILD INDEX` on existing data is not supported (unlike Vector and Inverted Indexes). If the table has substantial historical data that needs to be covered, rebuild the table and re-insert the data.

- **Vector Index and Inverted Index must be explicitly built**: `CREATE INDEX` only processes subsequent new data. For existing data, manually run `BUILD INDEX <index_name> ON <table_name>` (in the same Schema context); otherwise vector search and full-text search results do not include data that existed before the index was created.

- **Partitioned Dynamic Table must declare static_partitions**: A Dynamic Table with `PARTITIONED BY` must set `TBLPROPERTIES ('static_partitions' = 'true')`. Without this declaration, the system uses dynamic partition inference, which may overwrite or lose data in existing partitions during incremental refresh.

- **Do not write REFRESH INTERVAL in Dynamic Table DDL**: Manage refresh scheduling centrally through Studio Task (path `best_practices/content_rec/`). Attach alert rules and data quality checks to the same task node; do not write the `REFRESH INTERVAL` parameter in `CREATE DYNAMIC TABLE` DDL.

- **COSINE_DISTANCE: smaller means more similar**: Unlike cosine similarity (−1 to 1), `COSINE_DISTANCE` returns values in the range 0 to 2, where 0 means identical. Query with `ORDER BY cos_dist ASC` and take the TOP-K as approximate nearest neighbor results.

- **Kafka PIPE DDL validates broker connection**: When running `CREATE PIPE`, the system attempts to connect to the Kafka broker to verify that the topic exists. In development without a Kafka environment, create the target table, simulate data with INSERT to validate downstream Silver/Gold logic, then create the PIPE when Kafka is ready.

- **OSS PIPE LIST_PURGE mode is irreversible**: Original files are deleted from the Volume after a successful import. If business needs require retaining files (such as replay scenarios), use `LIST` mode and add deduplication logic in the Bronze layer (for example, DISTINCT on `content_id` + `load_time`).

---

## Related Documentation

- [CREATE DYNAMIC TABLE](../create-dynamic-table.md) — Syntax reference and incremental refresh mechanism
- [Import Kafka Data Continuously with Pipe](../pipe-kafka.md) — Kafka PIPE full parameter reference
- [CREATE INDEX](../create-index.md) — Bloomfilter / Inverted / Vector index syntax and BUILD INDEX process
- [ZettaPark Python Development Guide](../zettapark-python-guide.md) — Session creation, DataFrame API, task configuration
- [Medallion Architecture: Pure SQL Dynamic Table Approach](lakehouse-medallion-sql-dt-guide.md) — Large-scale three-layer data warehouse reference
- [Industrial IoT Device Health Monitoring Data Warehouse Best Practices](iot-device-health-monitoring-dw-best-practices.md) — Another complete Bronze/Silver/Gold case study