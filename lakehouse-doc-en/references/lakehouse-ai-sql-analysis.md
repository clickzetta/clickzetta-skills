# AI Gateway in Practice: Calling LLMs with SQL

Calling large language models (LLMs) directly in SQL queries is the key leap that takes data analysis from "querying data" to "understanding data." Singdata Lakehouse, through **AI Gateway + the AI_COMPLETE function**, lets you complete text analysis, sentiment evaluation, content generation, and intelligent classification within standard SQL — all processing happens inside the same query engine, with no need to export data to a Python environment.

This article uses the Kimi K2.6 (Moonshot AI) model together with NHL hockey data to demonstrate practical patterns for SQL + AI.

---

## Core Capabilities

| Capability | Traditional approach | SQL + AI approach |
|---|---|---|
| Text sentiment analysis | Python + Transformers | `SELECT AI_COMPLETE(model, prompt)` |
| Content classification | Export CSV → Python script | Built-in SQL function, batch processing |
| Intelligent report generation | BI tool with external scripts | SQL query outputs analysis text directly |
| Multilingual translation | API call + ETL write-back | `AI_COMPLETE` join-based translation |
| Data augmentation | Manual annotation | LLM auto-labeling, evaluation, enrichment |

---

## Architecture Overview

![](.topwrite/assets/13-ai-gateway-architecture.svg)

The SQL engine forwards `AI_COMPLETE()` calls to AI Gateway. The Gateway handles authentication, rate limiting, and quota management, then routes requests to the configured LLM. The entire process is transparent to SQL users — you only need to write SQL, with no API Key management or rate-limit retry handling required.

---

## Configuring the AI Gateway Connection

### Option 1: AI Gateway Endpoint (Recommended, requires Studio UI)

In Studio → API Key Management → New API Key; in Model Marketplace → select a model → View → check Endpoint Management and model invocation examples.

```sql
-- Use a pre-configured Endpoint
SELECT AI_COMPLETE('endpoint:kimi-k2.6', 'Hello');
```

### Option 2: API Connection (Create directly in SQL)

```sql
-- Create once, reused by all subsequent queries
CREATE API CONNECTION ai_gateway_conn
    TYPE ai_function
    PROVIDER = 'openai'  -- AI Gateway follows the OpenAI interface specification
    BASE_URL = 'https://<region>-aimesh.api.clickzetta.com/gateway/v1'
    API_KEY = '<your_api_key>';
```

AI Gateway Base URLs vary by region:

| Region | Base URL |
|---|---|
| Alibaba Cloud Shanghai | `https://cn-shanghai-alicloud-aimesh.api.clickzetta.com/gateway/v1` |
| Tencent Cloud Shanghai | `https://ap-shanghai-tencentcloud-aimesh.api.clickzetta.com/gateway/v1` |
| AWS Singapore | `https://ap-southeast-1-aws-aimesh.api.singdata.com/gateway/v1` |

### Format

```sql
-- Format: <connection_name>:<model_name>
'ai_gateway_conn:moonshotai/kimi-k2.6'

-- Full call
SELECT AI_COMPLETE('ai_gateway_conn:moonshotai/kimi-k2.6', 'Your prompt here');
```

> The connection name and model name are separated by an **English colon** with no spaces.

---

## AI_COMPLETE Basic Usage

### Connectivity Test

```sql
SELECT AI_COMPLETE('ai_gateway_conn:moonshotai/kimi-k2.6',
    'hello, introduce yourself in one sentence'
);
```

**Response** (measured at 3.1 seconds):

> I am Kimi, a large language model created by Moonshot AI, here to help you with information, writing, analysis, and conversation.

### General Prompt Templates

```sql
-- Summarization
SELECT AI_COMPLETE('conn:model',
    CONCAT('Summarize in one sentence: ', content)
) FROM articles;

-- Sentiment evaluation
SELECT AI_COMPLETE('conn:model',
    CONCAT('Determine sentiment (positive/negative/neutral), reply with one word only: ', review)
) FROM reviews;

-- Content classification
SELECT AI_COMPLETE('conn:model',
    CONCAT('Classify the following text as sports/finance/tech/health: ', text)
) FROM contents;

-- Translation
SELECT AI_COMPLETE('conn:model',
    CONCAT('Translate the following English text to Chinese: ', english_text)
) FROM docs;
```

> **Tip**: Adding "reply with one word only" or "reply with the category name only" to the prompt controls output format, making downstream GROUP BY or WHERE filtering easier.

---

## Practice: AI-Enhanced NHL Data Analysis

### Scenario 1: Player Scouting Reports

Feed Gold layer aggregated data (career goals, assists, points) into the LLM to generate professional scouting evaluations:

```sql
SELECT
    player_name,
    position,
    total_goals,
    total_points,
    AI_COMPLETE('ai_gateway_conn:moonshotai/kimi-k2.6',
        CONCAT('Summarize this NHL player''s career style in one sentence: ',
               player_name,
               ', position: ', position,
               ', career goals: ', CAST(total_goals AS STRING),
               ', total points: ', CAST(total_points AS STRING))
    ) AS ai_scout_report
FROM gold.player_career_stats
ORDER BY total_points DESC
LIMIT 5;
```

Query results (5 rows, 10.2 seconds):

| Player | AI Scouting Report |
|---|---|
| Alex Ovechkin | A goal-scorer who redefined the left wing position with unstoppable heavy shots and dominant presence in the slot, combining violent aesthetics with remarkable longevity across nearly two decades at the peak |
| Sidney Crosby | A generational center defined by complete two-way play, relentless competitiveness, and exceptional hockey IQ, who set the modern benchmark for an elite NHL core player through intelligence and hard work |
| Joe Thornton | A traditional center renowned for elite playmaking vision and organizational ability, whose career assists far outnumber goals, embodying an unselfish and all-around style of play |
| Patrick Kane | A technically brilliant and highly creative offensive force, who became one of the most entertaining wingers in NHL history with his ghostly puck-handling and clutch game-winning ability |
| Evgeni Malkin | An elite offensive center who blends Eastern European technical finesse with North American physicality, celebrated at his peak for his unstoppable puck possession and improvisational creativity |

> AI-generated evaluations accurately captured each player's style characteristics with fluent language and clear perspectives.

### Scenario 2: Team Season Reviews

Generate season summaries from team standings:

```sql
SELECT
    team_abbr,
    wins, losses, goals_for, goals_against,
    AI_COMPLETE('ai_gateway_conn:moonshotai/kimi-k2.6',
        CONCAT('Summarize this NHL team''s season performance in one sentence: ',
               team_abbr, ', season 2019-20, ',
               'wins: ', CAST(wins AS STRING),
               ', losses: ', CAST(losses AS STRING),
               ', goals for: ', CAST(goals_for AS STRING),
               ', goals against: ', CAST(goals_against AS STRING))
    ) AS season_review
FROM gold.team_season_summary
WHERE season = 20192020
ORDER BY wins DESC
LIMIT 5;
```

Query results (5 rows, 10.1 seconds):

| Team | AI Season Review |
|---|---|
| TBL (Lightning) | An outstanding season with powerful offense and solid defense, ultimately winning the Stanley Cup championship |
| VGK (Golden Knights) | A solid season with offense slightly outpacing defense and an overall winning record above .500 |
| COL (Avalanche) | Decent offensive output but inconsistent defense, with an overall winning rate approaching .500 |

### Scenario 3: Sentiment Analysis + Classification

Perform instant analysis on any text without a pre-trained model:

```sql
SELECT
    AI_COMPLETE('ai_gateway_conn:moonshotai/kimi-k2.6',
        'Determine sentiment (positive/negative/neutral), reply with one word only: '
        || 'The Lightning played an incredible game tonight!'
    ) AS sentiment_1,

    AI_COMPLETE('ai_gateway_conn:moonshotai/kimi-k2.6',
        'Determine sentiment (positive/negative/neutral), reply with one word only: '
        || 'Terrible officiating tonight.'
    ) AS sentiment_2,

    AI_COMPLETE('ai_gateway_conn:moonshotai/kimi-k2.6',
        'Classify the text as sports/finance/tech/health. Reply with category only: '
        || 'NHL playoffs start next week with 16 teams.'
    ) AS category;
```

Query results:

| sentiment_1 | sentiment_2 | category |
|---|---|---|
| positive | negative | sports |

---

## Batch AI Processing Patterns

### Pattern A: Row-by-row Processing

Suitable for small datasets (< 1000 rows) — use SELECT + AI_COMPLETE directly:

```sql
SELECT id, content,
    AI_COMPLETE('conn:model', CONCAT('Summarize: ', content)) AS summary
FROM articles
WHERE created_date = CURRENT_DATE();
```

### Pattern B: Dynamic Table Auto-batch Processing

Persist AI analysis results into a Dynamic Table for zero-latency subsequent queries:

```sql
-- Create an AI-enhanced analysis table
CREATE OR REPLACE DYNAMIC TABLE gold.player_ai_scouting
REFRESH INTERVAL 1 DAY VCLUSTER DEFAULT
COMMENT 'AI scouting reports - auto-updated daily'
AS
SELECT
    player_id,
    player_name,
    position,
    total_goals,
    total_points,
    pts_per_game,
    AI_COMPLETE('ai_gateway_conn:moonshotai/kimi-k2.6',
        CONCAT('Summarize this NHL player in one sentence: ',
               player_name, ', position: ', position,
               ', goals: ', CAST(total_goals AS STRING),
               ', points: ', CAST(total_points AS STRING),
               ', points per game: ', CAST(pts_per_game AS STRING))
    ) AS scouting_report
FROM gold.player_career_stats
WHERE total_points > 500;  -- only analyze players with 500+ points to control cost

-- Application layer queries directly, zero AI call latency
SELECT player_name, scouting_report
FROM gold.player_ai_scouting
WHERE player_name = 'Alex Ovechkin';
```

> **Note**: Each DT REFRESH re-invokes AI_COMPLETE for all rows that satisfy the WHERE condition. Recommendations:
> - Only run AI analysis on key rows (use WHERE filtering)
> - Use a `1 DAY` or longer refresh interval
> - Use a regular table instead of DT to manually control refresh timing

### Pattern C: Materialize AI Results into a Regular Table

More granular cost control — manually trigger only when needed:

```sql
-- Create a results table
CREATE TABLE gold.player_scouting_reports (
    player_id    BIGINT,
    player_name  STRING,
    report       STRING,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Generate once
INSERT INTO gold.player_scouting_reports (player_id, player_name, report)
SELECT
    player_id,
    player_name,
    AI_COMPLETE('ai_gateway_conn:moonshotai/kimi-k2.6',
        CONCAT('Evaluate this NHL player: ', player_name,
               ', ', CAST(total_points AS STRING), ' points')
    )
FROM gold.player_career_stats
WHERE total_points > 1000;
```

---

## Performance and Cost

### Measured Performance (Kimi K2.6, Alibaba Cloud Shanghai)

| Scenario | Rows | Total time | Average per row |
|---|---|---|---|
| Single call | 1 | 1.9-3.1s | ~2.5s |
| Scouting reports (with data concatenation) | 5 | 10.2s | 2.0s |
| Season reviews (with data concatenation) | 5 | 10.1s | 2.0s |
| Sentiment + classification (simple output) | 3 | 2.4s | 0.8s |

> Single-row AI call latency is ~2-3 seconds. Batch processing 100 rows is expected to take 3-5 minutes. For tens of thousands of rows, use the DT materialization pattern to avoid repeated calls.

### Three Cost Control Principles

| Principle | Method |
|---|---|
| **Reduce call count** | Filter key rows with WHERE, materialize results to a table, use DT to only analyze incremental rows |
| **Shorten output length** | Add "in one sentence", "reply with one word only", or set max_tokens in the prompt |
| **Control refresh frequency** | Lower DT refresh from `1 HOUR` to `1 DAY` or `7 DAY` |

### AI Gateway Quota Management

AI Gateway provides tenant-level and Endpoint-level quota controls:

- **Tenant quota**: Monthly total token cap for the organization (e.g., 5 million/month)
- **Endpoint quota**: Independent quota per model (e.g., Kimi 1 million/month)
- **Actual available = min(tenant remaining, Endpoint quota)**

View real-time consumption in Studio → AI Model Management → Usage.

---

## Notes

| Note | Description |
|---|---|
| **AI_COMPLETE does not support OR REPLACE** | The function is built-in and does not need to be created |
| **AI_SUMMARIZE / AI_SENTIMENT and other specialized functions coming soon** | Only `AI_COMPLETE` is available in the current version; other functions will be released in the next version. All capabilities can be implemented in advance using `AI_COMPLETE` + prompts |
| **Output format is non-deterministic** | LLM output may contain extra text; add "reply with one word only" constraints |
| **AI_COMPLETE cost in DT must be evaluated** | DT recomputes everything on each REFRESH; recommend analyzing only incremental rows |
| **Connection name and model name use an English colon** | `'conn:model'`; do not use the `connection:` prefix |
| **Do not SELECT AI_COMPLETE directly on production tables** | Materialize results first then query, to avoid repeated API calls |
| **Function call timeout** | The default SQL timeout may not be sufficient; use asynchronous processing for long text |

---

## Related Documentation

- [AI Gateway Product Overview](AI_Gateway.md) — Endpoint management, quotas, monitoring
- [AI Functions Overview](ai_functions_overview.md) — Detailed parameters for all AI functions
- [AI_COMPLETE Detailed Documentation](ai_complete.md) — options parameters, image mode
- [AI_EMBEDDING Detailed Documentation](ai_embedding.md) — Embedding and semantic search
- [CREATE API CONNECTION](create-api-connection.md) — Full syntax
- [Medallion Pure-SQL DT Architecture](lakehouse-medallion-sql-dt-guide.md) — NHL data layered modeling
- [Multi-cloud Unified Data Lake Acceleration](lakehouse-multi-cloud-acceleration.md) — Volume + Pipe + DT cross-cloud solution
