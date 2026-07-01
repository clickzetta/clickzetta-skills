# Singdata Lakehouse Medallion Architecture in Practice: Pure SQL Dynamic Table Approach

The Medallion architecture (Bronze → Silver → Gold) is a data lake organization pattern popularized by Databricks. On Singdata Lakehouse, beyond implementing it with ZettaPark Python API, there is a cleaner alternative: **building all three layers declaratively using SQL Dynamic Tables**—no Python code required, no scheduling platform configuration needed, and all three layers automatically refresh incrementally based on dependency chains.

This article uses the NHL (National Hockey League) real-world dataset (10 tables, ~14 million rows) to fully demonstrate this approach.

> 💡 If you are familiar with Databricks Medallion but prefer not to write Python/ZettaPark, or want to manage data pipelines with pure SQL, this article is your reference. It complements the [ZettaPark migration approach](medallion-lakehouse-from-scratch.md), with the two covering different technical preferences.

### Data Lake Acceleration Overview: Where This Article Fits

A typical data lake acceleration pipeline looks like: **Object storage files → Volume (mount) → Pipe (continuous ingestion) → Target table → Dynamic Table (incremental aggregation)**. The first two steps handle "automatic data loading," while this article focuses on the final step—cleansing, modeling, and aggregation after data is loaded, using Dynamic Tables to declaratively build the Bronze → Silver → Gold three-layer pipeline.

If you have not set up data ingestion yet, start with [Volume + Pipe End-to-End Practice](lakehouse-volume-pipe-acceleration-guide.md) to get file auto-loading working first. If your data is already in Lakehouse tables (like the NHL dataset in this article), start directly here.

---

## Why Use Dynamic Tables to Build Medallion

Traditional Medallion architecture typically relies on scheduling platforms (Airflow/Databricks Workflows) to execute Python Notebooks or SQL scripts sequentially. Dynamic Tables offer a different paradigm:

| Dimension | Traditional ETL Scheduling | Dynamic Table Approach |
|---|---|---|
| Coding style | Python/ZettaPark or SQL scripts | Pure SQL (`CREATE DYNAMIC TABLE ... AS SELECT`) |
| Scheduling config | Requires DAG and Cron configuration | Declarative `REFRESH INTERVAL`, system auto-schedules |
| Incremental computation | Manual incremental logic required | System CBO automatically detects incremental changes |
| Dependency management | Manual orchestration of upstream/downstream order | DT automatically determines refresh order by reference |
| Data lineage | Requires additional tools to track | `SHOW DYNAMIC TABLE REFRESH HISTORY` built-in |
| Code as assets | Notebooks/scripts scattered across management | Centralized in Studio, searchable, comparable, reusable |

The core difference: **you do not need to worry about "when to run" or "what to run"—you only need to declare "what result you want"**. The system handles computation orchestration, incremental detection, and parallel scheduling.

---

## Dataset Overview

NHL hockey data from the `nhl_game_data` schema (Bronze layer, already loaded):

| Table | Rows | Description |
|---|---|---|
| `game` | 26,305 | Main game table (matchups, scores, venues, seasons) |
| `player_info` | 3,925 | Player profiles (name, nationality, position, height/weight) |
| `team_info` | 33 | Team information (name, abbreviation) |
| `game_skater_stats` | 945,830 | Skater stats (goals, assists, shots, hits, +/-, etc.) |
| `game_goalie_stats` | 56,656 | Goalie stats (saves, goals against, save percentage) |
| `game_goals` | 148,992 | Goal details |
| `game_plays` | 5,050,529 | Game events (play-by-play) |
| `game_plays_players` | 7,586,604 | Player participation details per event |
| `game_penalties` | 247,828 | Penalty records |
| `game_teams_stats` | 52,610 | Team game-level statistics |

Data relationships: `game` is the core fact table, linked to other tables via `game_id`, `player_id`, and `team_id`. Covers 10 seasons from 2010 to 2020.

---

## Architecture Design

```
Bronze (nhl_game_data.*)        Silver (silver.*) DT          Gold (gold.*) DT
═══════════════════════          ══════════════════            ══════════════════
Raw data, zero transformation    Cleansed + dimension joins    Business metrics

game ─────────┐                ┌─ dim_team (33)            ┌─ scoring_leaders
team_info ────┤   LEFT JOIN ──→├─ dim_player (3,925)       ├─ player_career_stats
player_info ──┘                ├─ fact_skater_stats        ├─ team_season_summary
skater_stats ── LEFT JOIN ──→  └─ fact_goalie_stats        ├─ goalie_season_rankings
goalie_stats ── LEFT JOIN ──→                               └─ team_home_away_split
```

Three-layer responsibilities:

| Layer | Schema | Table Type | Responsibility |
|---|---|---|---|
| **Bronze** | `nhl_game_data` | Regular table | Raw data, no transformation |
| **Silver** | `silver` | Dynamic Table | JOIN dimension tables for names, cleanse field types (STRING→INT), standardize |
| **Gold** | `gold` | Dynamic Table | Aggregated metrics: top scorers, team records, goalie rankings, career stats |

> ⚠️ Silver and Gold both use Dynamic Tables; **materialized views are not recommended**. DT supports incremental refresh and Time Travel; materialized views do not.

---

## Implementation Steps

### Prerequisites

- Virtual Cluster available (use `DEFAULT`, GP type, Serverless on-demand wake-up)
- Bronze data loaded (`nhl_game_data.*` 10 tables)
- Permissions for CREATE SCHEMA / CREATE DYNAMIC TABLE

### Step 1: Create Schemas

Use separate schemas to physically isolate each layer:

```sql
CREATE SCHEMA IF NOT EXISTS silver COMMENT 'Medallion Silver cleansed layer';
CREATE SCHEMA IF NOT EXISTS gold   COMMENT 'Medallion Gold aggregated metrics layer';
```

### Step 2: Silver Layer — Dimension Tables

The simplest DT: directly filter/transform columns from Bronze tables. These two tables are small (33 rows and 3,925 rows), so even FULL refreshes are effortless.

```sql
-- Team dimension
CREATE OR REPLACE DYNAMIC TABLE silver.dim_team
REFRESH INTERVAL 1 DAY vcluster DEFAULT
COMMENT 'Silver team dimension table'
AS
SELECT
  team_id,
  franchiseid,
  shortname,
  teamname,
  abbreviation,
  link
FROM nhl_game_data.team_info;

-- Player dimension (standardized + full name column added)
CREATE OR REPLACE DYNAMIC TABLE silver.dim_player
REFRESH INTERVAL 1 DAY vcluster DEFAULT
COMMENT 'Silver player dimension table — standardized fields + full name'
AS
SELECT
  player_id,
  firstname,
  lastname,
  CONCAT(firstname, ' ', lastname) AS full_name,
  nationality,
  birthcity,
  primaryposition  AS position,
  birthdate,
  height,
  height_cm,
  CAST(NULLIF(REGEXP_REPLACE(weight, ',', ''), '') AS INT) AS weight_kg,
  shootscatches
FROM nhl_game_data.player_info;
```

> **Why use `REGEXP_REPLACE(weight, ',', '')`?** In NHL raw data, numeric fields (such as hits, weight) may contain thousands separators (e.g., "1,234"). Direct CAST would throw an error. Removing the comma before casting to INT is a necessary cleansing step.

### Step 3: Silver Layer — Fact Tables

The core work of fact tables: **JOIN dimension tables to resolve names + type standardization**. Using skater stats as an example:

```sql
CREATE OR REPLACE DYNAMIC TABLE silver.fact_skater_stats
REFRESH INTERVAL 1 DAY vcluster DEFAULT
COMMENT 'Silver skater stats fact table — joined with player name + team name + season'
AS
SELECT
  s.game_id,
  s.player_id,
  p.full_name        AS player_name,
  p.position,
  s.team_id,
  t.teamname         AS team_name,
  t.abbreviation     AS team_abbr,
  g.season,
  g.date_time_gmt    AS game_date,
  s.timeonice,
  s.goals,
  s.assists,
  s.goals + s.assists AS points,         -- computed field: points
  s.shots,
  CAST(NULLIF(REGEXP_REPLACE(s.hits, ',', ''), '') AS INT) AS hits,
  s.powerplaygoals,
  s.penaltyminutes,
  s.plusminus,
  s.eventimeonice,
  s.powerplaytimeonice
FROM nhl_game_data.game_skater_stats s
LEFT JOIN nhl_game_data.game g
  ON s.game_id = g.game_id
LEFT JOIN silver.dim_player p
  ON s.player_id = p.player_id
LEFT JOIN silver.dim_team t
  ON s.team_id = t.team_id;
```

> ⚠️ **The Silver fact table references Silver dimension tables** (`silver.dim_player`, `silver.dim_team`). This means the system refreshes dimension tables first, then fact tables—DT handles the dependency chain automatically.

Goalie stats fact table follows the same pattern, with additional save percentage calculation:

```sql
CREATE OR REPLACE DYNAMIC TABLE silver.fact_goalie_stats
REFRESH INTERVAL 1 DAY vcluster DEFAULT
COMMENT 'Silver goalie stats fact table — includes save percentage calculation'
AS
SELECT
  gs.game_id,
  gs.player_id,
  p.full_name        AS player_name,
  t.teamname         AS team_name,
  t.abbreviation     AS team_abbr,
  g.season,
  g.date_time_gmt    AS game_date,
  gs.timeonice,
  gs.shots           AS shots_faced,
  gs.saves,
  CASE WHEN gs.shots > 0
    THEN ROUND(gs.saves * 1.0 / gs.shots, 3)
    ELSE NULL
  END                AS save_pct,         -- computed field: save percentage
  gs.decision
FROM nhl_game_data.game_goalie_stats gs
LEFT JOIN nhl_game_data.game g
  ON gs.game_id = g.game_id
LEFT JOIN silver.dim_player p
  ON gs.player_id = p.player_id
LEFT JOIN silver.dim_team t
  ON gs.team_id = t.team_id;
```

### Step 4: Initial Refresh of Silver Layer

After DT creation, only the computation logic is defined—there is no data yet. You need to manually trigger the first refresh:

```sql
REFRESH DYNAMIC TABLE silver.dim_team;
REFRESH DYNAMIC TABLE silver.dim_player;
REFRESH DYNAMIC TABLE silver.fact_skater_stats;
REFRESH DYNAMIC TABLE silver.fact_goalie_stats;
```

> 💡 Refresh dimension tables first, then fact tables—since fact tables reference dimension tables. Although order does not matter when executing manually (the system waits for dependencies to be ready), following the dependency order is recommended for faster initial completion.

### Step 5: Gold Layer — Aggregated Metrics

The Gold layer reads data from the Silver layer and uses aggregate functions to generate business metrics. All tables use a `1 DAY` refresh interval (T+1 scenario).

#### Top Scorers: TOP 20 Scorers Per Season

Use the `RANK()` window function to rank by season:

```sql
CREATE OR REPLACE DYNAMIC TABLE gold.scoring_leaders
REFRESH INTERVAL 1 DAY vcluster DEFAULT
COMMENT 'Gold top 20 scorers per season — ranked by points (goals + assists)'
AS
SELECT season, rank, player_id, player_name, position, team_abbr,
       games_played, goals, assists, points,
       ROUND(points * 1.0 / games_played, 2) AS pts_per_game
FROM (
  SELECT
    season, player_id, player_name, position, team_abbr,
    COUNT(*) AS games_played,
    SUM(goals) AS goals,
    SUM(assists) AS assists,
    SUM(points) AS points,
    RANK() OVER (PARTITION BY season ORDER BY SUM(points) DESC) AS rank
  FROM silver.fact_skater_stats
  GROUP BY season, player_id, player_name, position, team_abbr
) t
WHERE rank <= 20;
```

**Validation results** (2019-20 season):

| rank | player | team | goals | assists | points |
|---|---|---|---|---|---|
| 1 | Nikita Kucherov | TBL | 160 | 316 | 476 |
| 2 | Nathan MacKinnon | COL | 176 | 296 | 472 |
| 3 | Leon Draisaitl | EDM | 181 | 274 | 455 |
| 4 | David Pastrnak | BOS | 204 | 216 | 420 |
| 5 | Connor McDavid | EDM | 153 | 262 | 415 |

> ✅ Rankings match NHL official records, data accuracy validation passed.

#### Team Season Records

Bronze data only has a home/away team perspective per game. Each game needs to be expanded into two rows (one for home team, one for away team), then aggregated by team and season. This is implemented with `UNION ALL` + `CASE WHEN`:

```sql
CREATE OR REPLACE DYNAMIC TABLE gold.team_season_summary
REFRESH INTERVAL 1 DAY vcluster DEFAULT
COMMENT 'Gold team season records — wins/losses/goals/goals-against/points'
AS
SELECT
  g.season, g.team_id,
  t.teamname       AS team_name,
  t.abbreviation   AS team_abbr,
  COUNT(*)         AS games_played,
  SUM(CASE WHEN g.side = 'home' AND g.outcome LIKE 'home win%' THEN 1
           WHEN g.side = 'away' AND g.outcome LIKE 'away win%' THEN 1
           ELSE 0 END) AS wins,
  SUM(CASE WHEN g.side = 'home' AND g.outcome LIKE 'away win%' THEN 1
           WHEN g.side = 'away' AND g.outcome LIKE 'home win%' THEN 1
           ELSE 0 END) AS losses,
  SUM(CASE WHEN g.side = 'home' THEN g.home_goals
           ELSE g.away_goals END) AS goals_for,
  SUM(CASE WHEN g.side = 'home' THEN g.away_goals
           ELSE g.home_goals END) AS goals_against,
  SUM(CASE WHEN g.side = 'home' AND g.outcome LIKE 'home win%' THEN 2
           WHEN g.side = 'away' AND g.outcome LIKE 'away win%' THEN 2
           ELSE 0 END) AS points
FROM (
  SELECT season, home_team_id AS team_id, outcome,
         home_goals, away_goals, 'home' AS side
  FROM nhl_game_data.game
  UNION ALL
  SELECT season, away_team_id AS team_id, outcome,
         home_goals, away_goals, 'away' AS side
  FROM nhl_game_data.game
) g
LEFT JOIN silver.dim_team t ON g.team_id = t.team_id
GROUP BY g.season, g.team_id, t.teamname, t.abbreviation;
```

> ⚠️ **Note**: An early version used `outcome LIKE '%win%'` to match wins, but this caused the away team row to also be counted as a win when the home team won. You must cross-match `side` and `outcome`: home team rows only match `'home win%'`, and away team rows only match `'away win%'`.

**Validation results** (2019-20 season TOP 5):

| team | games | wins | losses | points |
|---|---|---|---|---|
| Lightning (TBL) | 190 | 122 | 68 | 244 |
| Stars (DAL) | 192 | 104 | 88 | 208 |
| Golden Knights (VGK) | 182 | 102 | 80 | 204 |
| Avalanche (COL) | 170 | 102 | 68 | 204 |
| Flyers (PHI) | 170 | 102 | 68 | 204 |

#### Goalie Season Rankings + Player Career Stats + Home/Away Split

Full DDL is in the appendix. The core pattern is the same: aggregate from Silver layer → `RANK() OVER (PARTITION BY season ...)` → filter TOP N.

### Step 6: Validate the Full Pipeline

```sql
-- Row count comparison across layers
SELECT 'Bronze game' AS layer, COUNT(*) FROM nhl_game_data.game
UNION ALL SELECT 'Silver dim_team', COUNT(*) FROM silver.dim_team
UNION ALL SELECT 'Silver fact_skater', COUNT(*) FROM silver.fact_skater_stats
UNION ALL SELECT 'Gold scoring_leaders', COUNT(*) FROM gold.scoring_leaders
UNION ALL SELECT 'Gold team_season', COUNT(*) FROM gold.team_season_summary;

-- View DT refresh history
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'scoring_leaders';
```

**Complete validation results:**

| Layer | Table | Rows | Refresh Mode | Status |
|---|---|---|---|---|
| Silver | dim_team | 33 | FULL | ✅ Matches Bronze |
| Silver | dim_player | 3,925 | FULL | ✅ Matches Bronze |
| Silver | fact_skater_stats | 1,130,682 | FULL | ✅ Includes player_name/team_name/points |
| Silver | fact_goalie_stats | 67,642 | FULL | ✅ Includes computed save_pct |
| Gold | scoring_leaders | 399 | FULL | ✅ TOP 20 per season |
| Gold | player_career_stats | 3,353 | FULL | ✅ Career summary |
| Gold | team_season_summary | 580 | FULL | ✅ 33 teams × 18 seasons |
| Gold | goalie_season_rankings | 294 | FULL | ✅ TOP 15 per season |
| Gold | team_home_away_split | 580 | FULL | ✅ Home/away split |

> 💡 **Why all FULL?** On the first refresh there is no incremental baseline, so DT must perform a full scan of the source tables to establish the initial state. After Bronze layer receives new data, DT will automatically switch to INCREMENTAL mode and process only the changed parts. Source tables need `change_tracking` enabled to support incremental refresh (`ALTER TABLE table_name SET PROPERTIES ('change_tracking' = 'true')`).

---

## Design Principles

### 1. Cross-Layer Reference Rules

| Reference Direction | Allowed | Example |
|---|---|---|
| Silver → Bronze | ✅ | `FROM nhl_game_data.game` |
| Gold → Silver | ✅ | `FROM silver.fact_skater_stats` |
| Gold → Bronze | ⚠️ Not recommended | Should access indirectly through Silver layer |
| Gold → Gold | ⚠️ Use with caution | Only for multi-level aggregation |
| Bronze → Silver | ❌ Forbidden | Lower layers should not depend on upper layers |

### 2. LEFT JOIN Filter Conditions Must Go in ON Clause

```sql
-- ❌ Wrong: WHERE filter degrades LEFT JOIN to INNER JOIN
SELECT * FROM skater_stats s
LEFT JOIN team_info t ON s.team_id = t.team_id
WHERE t.abbreviation = 'TBL';

-- ✅ Correct: filter condition in ON clause
SELECT * FROM skater_stats s
LEFT JOIN team_info t
  ON s.team_id = t.team_id AND t.abbreviation = 'TBL';
```

### 3. First Refresh Baseline Time

`REFRESH INTERVAL 1 DAY` calculates the next trigger based on creation time and does not align to clock hours. It is recommended to immediately execute `REFRESH DYNAMIC TABLE` after creation to manually trigger the first refresh and reset the baseline time:

```sql
CREATE DYNAMIC TABLE gold.scoring_leaders ...;
REFRESH DYNAMIC TABLE gold.scoring_leaders;
```

### 4. String Cleansing

When raw data comes from external systems, numeric fields may contain non-standard characters:

```sql
CAST(NULLIF(REGEXP_REPLACE(hits, ',', ''), '') AS INT)
```

Three-step cleansing: remove commas → NULLIF empty string → CAST to target type. `NULLIF` prevents CAST failures caused by empty strings.

---

## Cost Analysis

| Layer | DT Count | Refresh Frequency | Estimated CRU |
|---|---|---|---|
| Silver | 4 | 1 DAY | Low (full refresh, but small data volume) |
| Gold | 5 | 1 DAY | Medium (involves aggregation, ~14M row scan) |

All use GP type Virtual Cluster (`DEFAULT`), Serverless on-demand billing. In T+1 scenarios with only one refresh per day, this is lower cost than traditional hourly ETL.

> 💡 To reduce Gold layer costs, infrequently used metrics (such as `goalie_season_rankings`, `team_home_away_split`) can be set to `7 DAY` refresh frequency.

---

## Comparison with ZettaPark Approach

| | ZettaPark Approach | Pure SQL DT Approach (this article) |
|---|---|---|
| Target audience | Python developers, Data Scientists | SQL developers, Data Analysts |
| Code volume | Python scripts + Spark API | Pure SQL (DDL) |
| Scheduling | Requires external scheduling (Studio/Notebook) | DT auto-refresh, no scheduling needed |
| Incremental computation | Manual CDC management required | System handles automatically |
| Flexibility | High (Python can call any library) | Medium (within SQL expression capabilities) |
| Learning curve | Pandas/PySpark/ZettaPark | Pure SQL |
| Use cases | Complex transformations, ML feature engineering, external API calls | Standard ETL, aggregation, JOINs, window functions |

**Both approaches coexist without conflict**: use ZettaPark for complex cleansing, use DT for aggregated metrics, leveraging the strengths of each within the same Medallion architecture.

---

## Notes

| Note | Description |
|---|---|
| Bronze data changes trigger DT automatically | All 9 DTs in the pipeline refresh in dependency order, no manual trigger needed |
| DT does not support ALTER to modify SQL | Use `CREATE OR REPLACE` to rebuild |
| Virtual Cluster must be GP type | AP type does not support small file merging, queries slow down over time |
| Silver fact tables reference Silver dimension tables | System automatically ensures dimension tables refresh first |
| String numeric fields need cleansing | Remove commas → NULLIF → CAST, three steps |
| UNION ALL row expansion requires careful business logic | When splitting home/away teams, win/loss determination must cross-match side and outcome |
| Manual REFRESH required after initial creation | `REFRESH INTERVAL` does not immediately trigger the first computation |

---

## Appendix: Complete Gold Layer DDL

### Player Career Stats

```sql
CREATE OR REPLACE DYNAMIC TABLE gold.player_career_stats
REFRESH INTERVAL 1 DAY vcluster DEFAULT
COMMENT 'Gold player career overview — all-season totals + per-game efficiency'
AS
SELECT
  player_id, player_name, position,
  COUNT(*)    AS games_played,
  SUM(goals)  AS total_goals,
  SUM(assists) AS total_assists,
  SUM(points)  AS total_points,
  ROUND(SUM(points) * 1.0 / COUNT(*), 2) AS pts_per_game,
  ROUND(SUM(goals) * 1.0 / NULLIF(SUM(shots), 0), 3) AS shooting_pct,
  AVG(timeonice)    AS avg_timeonice_sec,
  SUM(penaltyminutes) AS total_pim,
  AVG(plusminus)    AS avg_plusminus
FROM silver.fact_skater_stats
GROUP BY player_id, player_name, position;
```

### Goalie Season Rankings

```sql
CREATE OR REPLACE DYNAMIC TABLE gold.goalie_season_rankings
REFRESH INTERVAL 1 DAY vcluster DEFAULT
COMMENT 'Gold goalie season rankings TOP 15 — ranked by wins'
AS
SELECT season, rank, player_id, player_name, team_abbr,
       games_played, wins, saves, shots_faced,
       ROUND(save_pct, 3) AS save_pct
FROM (
  SELECT
    season, player_id, player_name, team_abbr,
    COUNT(*)    AS games_played,
    SUM(CASE WHEN decision = 'W' THEN 1 ELSE 0 END) AS wins,
    SUM(saves)  AS saves,
    SUM(shots_faced) AS shots_faced,
    CASE WHEN SUM(shots_faced) > 0
      THEN SUM(saves) * 1.0 / SUM(shots_faced)
      ELSE NULL END AS save_pct,
    RANK() OVER (PARTITION BY season ORDER BY
      SUM(CASE WHEN decision = 'W' THEN 1 ELSE 0 END) DESC) AS rank
  FROM silver.fact_goalie_stats
  GROUP BY season, player_id, player_name, team_abbr
) t
WHERE rank <= 15;
```

### Home/Away Split

```sql
CREATE OR REPLACE DYNAMIC TABLE gold.team_home_away_split
REFRESH INTERVAL 1 DAY vcluster DEFAULT
COMMENT 'Gold team home vs. away performance — home win% vs away win%'
AS
SELECT
  g.season, g.team_id,
  t.teamname        AS team_name,
  t.abbreviation    AS team_abbr,
  COUNT(CASE WHEN g.side = 'home' THEN 1 END) AS home_games,
  COUNT(CASE WHEN g.side = 'home' AND g.outcome LIKE 'home win%' THEN 1 END) AS home_wins,
  COUNT(CASE WHEN g.side = 'away' THEN 1 END) AS away_games,
  COUNT(CASE WHEN g.side = 'away' AND g.outcome LIKE 'away win%' THEN 1 END) AS away_wins,
  ROUND(
    COUNT(CASE WHEN g.side = 'home' AND g.outcome LIKE 'home win%' THEN 1 END) * 1.0 /
    NULLIF(COUNT(CASE WHEN g.side = 'home' THEN 1 END), 0), 3
  ) AS home_win_pct,
  ROUND(
    COUNT(CASE WHEN g.side = 'away' AND g.outcome LIKE 'away win%' THEN 1 END) * 1.0 /
    NULLIF(COUNT(CASE WHEN g.side = 'away' THEN 1 END), 0), 3
  ) AS away_win_pct
FROM (
  SELECT season, home_team_id AS team_id, outcome, 'home' AS side
  FROM nhl_game_data.game
  UNION ALL
  SELECT season, away_team_id AS team_id, outcome, 'away' AS side
  FROM nhl_game_data.game
) g
LEFT JOIN silver.dim_team t ON g.team_id = t.team_id
GROUP BY g.season, g.team_id, t.teamname, t.abbreviation;
```

---

## Related Documents

Complete data lake acceleration pipeline: Volume mount → Pipe ingestion → Dynamic Table modeling. The following documents cover each stage:

- [Volume + Pipe Data Lake Acceleration](lakehouse-volume-pipe-acceleration-guide.md) — File auto-ingestion, the upstream step for this article
- [Multi-Cloud Unified Data Lake Acceleration](lakehouse-multi-cloud-acceleration.md) — Same SQL runs on Alibaba Cloud/Tencent Cloud/AWS
- [Dynamic Table Introduction](sql_dynamic_table_guide.md) — Incremental computation mechanism and scheduling principles
- [CREATE DYNAMIC TABLE](create-dynamic-table.md) — Complete DDL syntax
- [Incremental Computing Overview](incremental-computing.md) — DT incremental refresh support matrix
- [Medallion from Scratch (ZettaPark Approach)](medallion-lakehouse-from-scratch.md) — Python API version covering the same topic
