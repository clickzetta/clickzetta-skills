# Exploring and Analyzing Data in JSON Files on Data Lake Volumes

## 1. Introduction to Data Lakes and JSON Data

### 1.1 What is a Data Lake

The data lake is an important component of the Lakehouse, allowing you to store all structured and unstructured data in its original format without needing to define a schema upfront. This fully embodies the advantages of lakehouse unification, extending Lakehouse data management to the unified management of unstructured data, no longer limited to structured data management within the data warehouse. This flexibility makes it an ideal choice for big data analysis, as you can use different analysis methods and tools to process data as needed. A data lake typically consists of the following parts:

* **Storage Layer**: Such as object storage (S3, OSS, COS, etc.)
* **Metadata Management**: Used for organizing and discovering data
* **Processing Engine**: Used for analyzing and transforming data

### 1.2 Volumes in the Data Lake

In modern data platforms like the Lakehouse, a **Volume** is an abstraction that represents a specific location in an external storage system (e.g., a path in object storage). Volumes allow the data platform to seamlessly access data stored in external systems without actually copying or moving that data.

Key features of Volumes:

* Direct connection to external storage systems
* Allows in-place querying without ETL
* Supports multiple file formats (JSON, CSV, Parquet, etc.)
* Can integrate with tables, providing SQL access capabilities

### 1.3 JSON Data Format

JSON (JavaScript Object Notation) is a lightweight data interchange format with the following features:

* **Semi-Structured**: Flexible key-value pair structure
* **Nesting Capability**: Supports complex hierarchical structures and arrays
* **Broad Support**: Almost all programming languages provide JSON parsing support
* **Human Readable**: Easier to understand compared to binary formats

In the big data domain, JSON is widely used for storing event data, API responses, log files, etc. Its flexibility makes it ideal for storing data with varying shapes.

## 2. Case Study: GitHub Event Data

### 2.1 Dataset Overview

GitHub event data is a publicly available dataset recording the time series of all public activities on the GitHub platform. In this case study, we analyze GitHub event data stored in the `gh_archive` Volume.

**Data Source Details**:

* **Volume Name**: `gh_archive`
* **File Path**: `2025-05-14-0.json.gz` (representing events from the 00:00-01:00 period on May 14, 2025)
* **File Format**: Compressed JSON file (using gzip compression)
* **Data Volume**: A single file is approximately 85.6 MB (compressed), containing nearly 200,000 event records

**Data Structure**:
Each record contains the following main fields:

* `id`: Unique event identifier
* `type`: Event type (e.g., PushEvent, PullRequestEvent, etc.)
* `actor`: Information about the user who performed the action
* `repo`: Information about the related code repository
* `org`: Information about the related organization (if applicable)
* `payload`: Detailed event information (varies by event type)
* `created_at`: Event creation time
* `public`: Whether the event is public

## 3. Data Lake Exploration and Analysis via SQL

### 3.1 Directly Querying JSON Files

The Lakehouse data lake platform allows direct SQL queries on files stored on Volumes, without needing to load them into tables first:

```sql
-- Analyze event type distribution
SELECT type, COUNT(*) as count 
FROM VOLUME gh_archive
USING json
OPTIONS('compression'='gzip')
FILES('2025-05-14-0.json.gz')
GROUP BY type
ORDER BY count DESC
```

Query Result:

```
type                         count
----------------------------  ------
PushEvent                     131341
CreateEvent                   21700
PullRequestEvent              12537
IssueCommentEvent             7807
WatchEvent                    7196
DeleteEvent                   4832
PullRequestReviewEvent        3571
IssuesEvent                   3569
PullRequestReviewCommentEvent 2362
ForkEvent                     1537
ReleaseEvent                  1261
...
```

**Features**:

* **Zero ETL**: No need to extract, transform, and load data beforehand
* **Flexible Access**: Direct access to nested fields
* **Ad-Hoc Queries**: Support for immediate data exploration

### 3.2 Handling Nested and Complex JSON Structures

JSON data often contains nested objects and arrays. SQL provides direct access to these complex structures:

```sql
-- Analyze file operation type distribution in PushEvent commits
SELECT 
  CASE 
    WHEN LOWER(payload.commits[0].message) LIKE '%add%' THEN 'Add'
    WHEN LOWER(payload.commits[0].message) LIKE '%fix%' THEN 'Fix'
    WHEN LOWER(payload.commits[0].message) LIKE '%update%' THEN 'Update'
    WHEN LOWER(payload.commits[0].message) LIKE '%remove%' OR LOWER(payload.commits[0].message) LIKE '%delete%' THEN 'Remove'
    WHEN LOWER(payload.commits[0].message) LIKE '%refactor%' THEN 'Refactor'
    WHEN LOWER(payload.commits[0].message) LIKE '%deploy%' THEN 'Deploy'
    WHEN LOWER(payload.commits[0].message) LIKE '%test%' THEN 'Test'
    WHEN LOWER(payload.commits[0].message) LIKE '%doc%' THEN 'Documentation'
    ELSE 'Other'
  END as commit_type,
  COUNT(*) as count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM VOLUME gh_archive
USING json
OPTIONS('compression'='gzip')
FILES('2025-05-14-0.json.gz')
WHERE type = 'PushEvent' 
  AND payload.commits IS NOT NULL 
  AND SIZE(payload.commits) > 0
GROUP BY commit_type
ORDER BY count DESC
```

Query Result:

```
commit_type    count   percentage
------------   ------  ----------
Other          46901   35.75
Update         42211   32.17
Deploy         17513   13.35
Add            11775   8.97
Fix            5027    3.83
Test           3389    2.58
Remove         3174    2.42
Documentation  637     0.49
Refactor       575     0.44
```

**Features**:

* **Path Navigation**: Use dot notation to access nested objects
* **Array Indexing**: Use square brackets to access array elements
* **Array Functions**: Use functions like `SIZE()` to handle arrays
* **Conditional Analysis**: Use CASE statements for classification and pattern recognition

### 3.3 Using JSON Paths to Access Deeply Nested Data

Path expressions can be used to deeply access multi-level nested structures in JSON documents:

```sql
-- Analyze branch information in PR events
SELECT 
  payload.pull_request.base.ref as base_branch,
  payload.pull_request.head.ref as head_branch,
  COUNT(*) as count
FROM VOLUME gh_archive
USING json
OPTIONS('compression'='gzip')
FILES('2025-05-14-0.json.gz')
WHERE type = 'PullRequestEvent'
  AND payload.action = 'opened'
  AND payload.pull_request.base.ref IS NOT NULL
  AND payload.pull_request.head.ref IS NOT NULL
GROUP BY base_branch, head_branch
ORDER BY count DESC
LIMIT 15
```

Query Result:

```
base_branch   head_branch                                               count
------------  --------------------------------------------------------  -----
main          main                                                      508
master        master                                                    499
main          dependabot/bundler/kamal-2.6.0                            93
main          develop                                                   72
main          dev                                                       63
main          github-actions/upgrade-dev-deps-main                      35
dev           dev                                                       27
main          github-actions/upgrade-main                               26
main          prBranch                                                  25
develop       develop                                                   20
main          test                                                      20
...
```

### 3.4 Complex Conditional Filtering and Regular Expressions

Use regular expressions and complex condition combinations to filter JSON data:

```sql
-- Find PRs created by bot accounts and analyze target repositories
SELECT 
  REGEXP_EXTRACT(actor.login, '(.*?)\\[bot\\]') as bot_name,
  repo.name as target_repo,
  COUNT(*) as pr_count
FROM VOLUME gh_archive
USING json
OPTIONS('compression'='gzip')
FILES('2025-05-14-0.json.gz')
WHERE 
  type = 'PullRequestEvent' 
  AND payload.action = 'opened'
  AND actor.login LIKE '%[bot]'
GROUP BY bot_name, target_repo
HAVING pr_count > 5
ORDER BY pr_count DESC
LIMIT 15
```

Query Result:

```
bot_name        target_repo                                       pr_count
--------------  ------------------------------------------------  --------
dependabot      GolfredoPerezFernandez/nodo-blockchain-blockscout  12
renovate        gAmUssA/flink-java-flights                         12
github-actions  hofferkristof/laravel-lang                         12
dependabot      j4v3l/tapo-exporter                                11
dependabot      Sudhanshu-Ambastha/GPT-3-webapp-in-reactjs         10
dependabot      jamespurnama1/new-portfolio                        10
github-actions  zzllbj/lang                                        9
...
```

### 3.5 Advanced Aggregation and Conditional Statistics

Use conditional aggregation to simultaneously analyze multiple metrics:

```sql
-- Analyze repository activity: Calculate the number of different event types per repository
SELECT
  repo.name,
  COUNT(DISTINCT actor.id) as unique_contributors,
  SUM(CASE WHEN type = 'PushEvent' THEN 1 ELSE 0 END) as push_count,
  SUM(CASE WHEN type = 'PullRequestEvent' THEN 1 ELSE 0 END) as pr_count,
  SUM(CASE WHEN type = 'IssueEvent' THEN 1 ELSE 0 END) as issue_count,
  SUM(CASE WHEN type = 'WatchEvent' THEN 1 ELSE 0 END) as watch_count,
  SUM(CASE WHEN type = 'ForkEvent' THEN 1 ELSE 0 END) as fork_count,
  COUNT(*) as total_events
FROM VOLUME gh_archive
USING json
OPTIONS('compression'='gzip')
FILES('2025-05-14-0.json.gz')
GROUP BY repo.name
HAVING total_events > 100
ORDER BY total_events DESC
LIMIT 10
```

Query Result:

```
repo.name                    unique_contributors  push_count  pr_count  issue_count  watch_count  fork_count  total_events
--------------------------   -------------------  ----------  --------  -----------  -----------  ----------  ------------
samgrover/mb-archive         1                    1289        0         0            0            0           1289
chrisxero/bitdepth-microblog 1                    1087        0         0            0            0           1087
iniadittt/iniadittt          1                    877         0         0            0            0           877
0xios/news-momentum-1        1                    730         0         0            0            0           730
JamyJones/Pastebin           1                    636         0         0            0            0           636
SoliSpirit/proxy-list        1                    586         0         0            0            0           586
...
```

### 3.6 Window Function Analysis

Use window functions for more complex ranking and grouping analysis:

```sql
-- Window function analysis: Calculate the most active users within each organization
SELECT
  org_login,
  username,
  event_count,
  rank_in_org
FROM (
  SELECT
    org.login as org_login,
    actor.login as username,
    COUNT(*) as event_count,
    RANK() OVER (PARTITION BY org.login ORDER BY COUNT(*) DESC) as rank_in_org
  FROM VOLUME gh_archive
  USING json
  OPTIONS('compression'='gzip')
  FILES('2025-05-14-0.json.gz')
  WHERE org.login IS NOT NULL
  GROUP BY org_login, username
) t
WHERE rank_in_org <= 3 AND org_login IN (
  SELECT org.login
  FROM VOLUME gh_archive
  USING json
  OPTIONS('compression'='gzip')
  FILES('2025-05-14-0.json.gz')
  WHERE org.login IS NOT NULL
  GROUP BY org.login
  ORDER BY COUNT(*) DESC
  LIMIT 5
)
ORDER BY org_login, rank_in_org
```

Query Result:

```
org_login                  username                            event_count  rank_in_org
-------------------------  ----------------------------------  -----------  -----------
blueprint-house            ChineeWetto                         559          1
curseforge-mirror          github-actions[bot]                 525          1
flyteorg                   github-actions[bot]                 444          1
flyteorg                   flyte-bot                           1            2
microsoft                  wingetbot                           67           1
microsoft                  microsoft-github-policy-service[bot] 57          2
microsoft                  jstarks                             29           3
static-web-apps-testing-org swa-runner-app[bot]                2178         1
static-web-apps-testing-org mkarmark                           164          2
static-web-apps-testing-org github-actions[bot]                28           3
```

### 3.7 Text Analysis and Time Processing

Use string functions and time functions to analyze time patterns in JSON data:

```sql
-- Verify the relationship between event type and hourly activity
SELECT 
  SUBSTR(created_at, 12, 2) as hour_of_day,
  type,
  COUNT(*) as event_count
FROM VOLUME gh_archive
USING json
OPTIONS('compression'='gzip')
FILES('2025-05-14-0.json.gz')
GROUP BY hour_of_day, type
ORDER BY hour_of_day, event_count DESC
```

Query Result:

```
hour_of_day  type                         event_count
-----------  ---------------------------  -----------
00           PushEvent                    131341
00           CreateEvent                  21700
00           PullRequestEvent             12537
00           IssueCommentEvent            7807
00           WatchEvent                   7196
...
```

### 3.8 Analyzing PR Merge Patterns

Analyze Pull Request merge trends:

```sql
-- Analyze PR merge trends: View PRs from creation to merging
SELECT 
  SUBSTRING(payload.pull_request.merged_at, 1, 10) as merge_date,
  COUNT(*) as merged_prs
FROM VOLUME gh_archive
USING json
OPTIONS('compression'='gzip')
FILES('2025-05-14-0.json.gz')
WHERE 
  type = 'PullRequestEvent' 
  AND payload.action = 'closed' 
  AND payload.pull_request.merged = true
  AND payload.pull_request.merged_at IS NOT NULL
GROUP BY merge_date
ORDER BY merge_date
```

Query Result:

```
merge_date  merged_prs
----------  ----------
2025-05-13  3
2025-05-14  4448
```

### 3.9 Loading File Data into Tables for Further Analysis

For data that needs repeated analysis, creating tables can improve query performance:

```sql
CREATE TABLE github_events AS
SELECT 
  id,
  type,
  actor.login as actor_name,
  actor.id as actor_id,
  repo.name as repo_name,
  repo.id as repo_id,
  org.login as org_name,
  created_at,
  public,
  payload
FROM VOLUME gh_archive
USING json
OPTIONS('compression'='gzip')
FILES('2025-05-14-0.json.gz')
```

**Advantages**:
* **Improved Performance**: Tables can use indexes and caching to speed up queries
* **Data Transformation**: Transformations and column renaming can be applied during loading
* **Persistent Access**: Create persistent views to avoid repeated parsing of raw data

## 4. Key Technical Features of Data Lake Analysis

### 4.1 Schema Flexibility

A core advantage of data lake analysis is **schema flexibility**:

* **Schema-on-Read**: Data structure only needs to be defined at query time
* **Partial Field Access**: Only query needed fields, ignoring others
* **Evolution Adaptation**: As data structures change, queries can easily adapt

For example, in our GitHub event analysis, we can focus only on specific event types or specific fields without processing the entire data structure.

### 4.2 Computation Pushdown and Filter Optimization

The Lakehouse data lake technology supports **computation pushdown**, pushing filter and transformation operations to the data source:

```sql
-- Example of an efficient filter query
SELECT actor.login, COUNT(*) as event_count
FROM VOLUME gh_archive
USING json
OPTIONS('compression'='gzip')
FILES('2025-05-14-0.json.gz')
WHERE type = 'PushEvent'
GROUP BY actor.login
ORDER BY event_count DESC
LIMIT 10
```

### 4.3 Unified Data Access and Format Selection

Apply SQL analysis to different types of data files in the same Volume:

```sql
-- 1. Query JSON files
SELECT COUNT(*) FROM VOLUME gh_archive
USING json
OPTIONS('compression'='gzip')
FILES('2025-05-14-0.json.gz');

-- 2. If the Volume has CSV files, similar syntax can be used for querying
-- SELECT * FROM VOLUME volume_name
-- USING csv
-- OPTIONS('header'='true')
-- FILES('data.csv');
```

### 4.4 Distributed Processing Capabilities

Data lake analysis engines are typically based on distributed computing frameworks, capable of processing large-scale datasets:

* **Parallel Processing**: Automatically decomposes queries into parallel execution tasks
* **Memory Management**: Optimizes memory usage, processing data exceeding single-machine memory capacity
* **Fault Tolerance**: Handles node failures and recovery

In GitHub event analysis, even though individual files are relatively small, the same queries can scale to analyze TB-level historical event data.

## 5. Data Analysis Process and Methodology

Through the GitHub event data case study, we can summarize a methodology for analyzing JSON data in a data lake:

### 5.1 Exploratory Data Analysis Process

1. **Initial Preview**: Get data samples to understand the overall structure
   ```sql
   SELECT * FROM VOLUME gh_archive
   USING json
   OPTIONS('compression'='gzip')
   FILES('2025-05-14-0.json.gz')
   LIMIT 10
   ```

2. **Overview Statistics**: Understand data distribution and main dimensions
   ```sql
   SELECT type, COUNT(*) as count 
   FROM VOLUME gh_archive
   USING json
   OPTIONS('compression'='gzip')
   FILES('2025-05-14-0.json.gz')
   GROUP BY type
   ORDER BY count DESC
   ```

3. **Deep Analysis**: Refined analysis targeting specific domains
   ```sql
   SELECT 
     actor.login as username, 
     COUNT(*) as event_count
   FROM VOLUME gh_archive
   USING json
   OPTIONS('compression'='gzip')
   FILES('2025-05-14-0.json.gz')
   GROUP BY username
   ORDER BY event_count DESC
   LIMIT 15
   ```

4. **Correlation Analysis**: Cross-analysis connecting multiple dimensions
   ```sql
   SELECT 
     org.login as organization,
     type,
     COUNT(*) as event_count
   FROM VOLUME gh_archive
   USING json
   OPTIONS('compression'='gzip')
   FILES('2025-05-14-0.json.gz')
   WHERE org.login IS NOT NULL
   GROUP BY organization, type
   ORDER BY organization, event_count DESC
   LIMIT 20
   ```

### 5.2 Data Insight Methods

In the GitHub event analysis, we discovered several key insights:

1. **Activity Distribution**: Understanding the proportion of different event types, discovering that Push events dominate (66%)
2. **Automation Trends**: Through user activity analysis, discovering that automated bot accounts (such as github-actions[bot]) contribute a large amount of activity
3. **Organizational Ecosystem**: Identifying the most active organizations, understanding the composition of the GitHub ecosystem
4. **Development Behavior**: Through commit message analysis, understanding developers' work patterns and focus areas
5. **Branch Usage Patterns**: main and master are still the most common target branch names
6. **Bot Activity**: dependabot, renovate, and github-actions are the most active automation bots

These insights come directly from SQL queries, demonstrating the powerful capability of SQL as a data analysis tool.

## 6. Best Practices and Optimization Tips

### 6.1 JSON Data Analysis Optimization

* **Selective Field Reading**: Only select the fields needed for analysis
  ```sql
  -- Only read necessary fields instead of all fields
  SELECT 
    type, 
    actor.login, 
    repo.name
  FROM VOLUME gh_archive
  USING json
  OPTIONS('compression'='gzip')
  FILES('2025-05-14-0.json.gz')
  LIMIT 10
  ```

* **Predicate Pushdown**: Apply filter conditions as early as possible in the query

* **Predicate Pushdown**: Filter conditions (`WHERE type = 'PushEvent'`) are pushed down to the storage layer, leveraging columnar statistics (such as max/min/bloom filters) to skip data blocks that clearly don't match.
* **Column Pruning**: Only read relevant columns (`actor.login` and `type`), skipping parsing of unrelated fields.
* **Filter Optimization**: After the storage layer loads data in blocks, further filter out non-matching records in memory, ultimately retaining only valid data for computation.

  ```sql
  -- Filter data early to reduce processing volume
  SELECT COUNT(*) 
  FROM VOLUME gh_archive
  USING json
  OPTIONS('compression'='gzip')
  FILES('2025-05-14-0.json.gz')
  WHERE type = 'PushEvent'
  ```

* **Properly Handle NULL Values**: Use `IS NULL` and `IS NOT NULL` to check for missing fields
  ```sql
  -- Identify and handle missing data
  SELECT 
    type,
    COUNT(*) as total_count,
    SUM(CASE WHEN org.login IS NULL THEN 1 ELSE 0 END) as without_org,
    SUM(CASE WHEN org.login IS NOT NULL THEN 1 ELSE 0 END) as with_org
  FROM VOLUME gh_archive
  USING json
  OPTIONS('compression'='gzip')
  FILES('2025-05-14-0.json.gz')
  GROUP BY type
  ORDER BY total_count DESC
  ```

### 6.2 Data Lake Query Best Practices

1. **Avoid Full Table Scans**: Use filter conditions whenever possible
2. **Use Aggregation Wisely**: When data volume is large, prioritize distributed aggregation
3. **Selective Projection**: Only select necessary columns to reduce I/O and memory usage
4. **Appropriate Data Transformation**: For frequently queried data, consider converting to more efficient formats
5. **Leverage Data Partitioning**: Logical partitioning based on file names or paths
6. **Pay Attention to Error Handling**: Handle JSON parsing errors and type conversion issues

## 7. Summary

Key features of data lake exploration and analysis through SQL:

1. **No ETL Needed**: Directly query raw data, reducing data preparation time
2. **Flexibility**: Adapts to semi-structured data without predefined schemas
3. **Ease of Use**: Uses familiar SQL syntax, lowering the learning curve
4. **Scalability**: Handles data from GB to PB levels
5. **Unified Access**: The same interface handles multiple data formats
6. **Exploration-Friendly**: Supports iterative data exploration processes
7. **Performance Optimization**: Provides various optimization techniques and strategies

SQL analysis on the data lake combines the ease of use of traditional SQL with the flexibility and scalability of big data processing, making it a powerful tool for modern data analysis. Through the GitHub event data analysis case study in this article, we demonstrated how to use SQL to directly query and analyze JSON files stored on data lake Volumes, quickly obtaining valuable data insights.

## References

[JSON Data Type](JSON.md)

[JSON Functions](json_function.md)
[External Volume](external_volume.md)
