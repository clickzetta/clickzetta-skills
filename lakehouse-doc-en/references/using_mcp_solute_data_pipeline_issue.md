# Using Singdata MCP + Claude for Data Pipeline Issue Troubleshooting

## Problem Background

One afternoon, I received an SMS alert: **A periodically scheduled data update task had failed**.

As the on-call DBA, I immediately logged into Singdata Lakehouse and performed an initial investigation:

* The materialized view `daily_summary_mv` had no new data after 10:00 AM that day;
* Manually refreshing the materialized view could succeed, but the data was not updated;
* The upstream source table was confirmed to have the latest data.

The issue was tricky: the source table had data, but the MV could not sync it, and the MV's SQL definition was over 200 lines, involving multiple CTEs and complex JOIN logic.

**Traditional approach**: Read the MV definition line by line → Manually write diagnostic SQL → Investigate layer by layer → Potentially spend several hours.

**MCP + Claude approach**: Describe the problem, use Singdata MCP + Claude to help analyze, and within minutes obtain the accurate root cause, along with repair suggestions.

***

## Step 1: Switch Environment (30 seconds)

### 👤 Prompt

Use the prompt to switch to the affected environment:

```
Use the Singdata MCP tool to switch to the Tencent Cloud Shanghai environment
```

### 🤖 Claude Response

```
✅ Successfully switched to Tencent Cloud Shanghai environment!

Current connection info:
| Config Item | Value |
|--------|-----|
| Service Endpoint | ap-shanghai-tencentcloud.api.singdata.com |
| Instance ID | 158026 |
| Workspace | data_warehouse |
| Schema | public |
```

> 💡 **Tip**: Singdata MCP supports configuring multiple cloud environments. After setting up the connection environments, you can quickly switch using natural language without memorizing connection parameters.

***

## Step 2: Describe the Problem and Let AI Diagnose Automatically (3 minutes)

### 👤 Prompt

```
Help me analyze the cause of the following issue:

I received a system monitoring alarm that report_schema.daily_summary_mv has had no data since the afternoon of December 13.

I executed SELECT bill_hour, COUNT(1) FROM report_schema.daily_summary_mv 
WHERE bill_date = '20251213' GROUP BY bill_hour; 
and found that there is no data after 10:00 AM.

However, the source table raw_schema.event_details does have data.

After executing REFRESH MATERIALIZED VIEW, there is still no data after 10:00 AM.

Query and analyze the cause of this issue.
```

> 💡 **Question tips**: When describing a problem, the best results come from including the following elements. The more specific and accurate the description, the more efficient the troubleshooting and the less likely the model will hallucinate:
>
> * 📌 **Symptom**: What data is missing
> * 📌 **Time point**: When it started
> * 📌 **Actions already taken**: What investigation has been done
> * 📌 **Contradiction**: Source table has data but MV does not

### 🤖 Claude Automatic Diagnosis Process

After receiving the problem, Claude automatically planned and executed the following diagnostic steps:

***

#### Diagnostic Step 1: Get MV definition, understand the data logic

```sql
-- Claude automatically executed
DESC TABLE EXTENDED report_schema.daily_summary_mv
```

Claude identified the key logic from the returned `view_text`:

```
📍 Key clue found!

The materialized view has a MaxDateHour boundary control logic that takes the minimum value of two data sources as the boundary:

WITH MaxDateHour AS (
    SELECT MIN(max_ts) AS max_ts    -- ⚠ Take the minimum value!
    FROM (
        -- First data source
        SELECT MAX(CONCAT(ds, '-', hh)) AS max_ts
        FROM event_details WHERE event_type = 'type_a'
        UNION ALL
        -- Second data source  
        SELECT MAX(CONCAT(ds, '-', hh)) AS max_ts
        FROM metrics_data
    ) t1
)
```

***

#### Diagnostic Step 2: Check the boundary value

```sql
-- Claude automatically executed
SELECT MIN(max_ts) AS current_boundary
FROM (
    SELECT MAX(CONCAT(ds, '-', hh)) AS max_ts
    FROM raw_schema.event_details WHERE event_type = 'type_a'
    UNION ALL
    SELECT MAX(CONCAT(ds, '-', hh)) AS max_ts
    FROM raw_schema.metrics_data
) t1
```

**Result**:

```
| current_boundary |
|------------------|
| 20251213-10      |
```

```
✅ Problem found! The MaxDateHour boundary is 20251213-10, which exactly matches the data cutoff time.
```

***

#### Diagnostic Step 3: Identify which data source is behind

```sql
-- Claude automatically executed: check each data source separately
SELECT 'source_a (type_a only)' AS source, MAX(CONCAT(ds, '-', hh)) AS max_ts
FROM raw_schema.event_details WHERE event_type = 'type_a'
UNION ALL
SELECT 'source_a (all types)' AS source, MAX(CONCAT(ds, '-', hh)) AS max_ts
FROM raw_schema.event_details WHERE event_type IN ('type_a', 'type_b', 'type_c')
UNION ALL
SELECT 'source_b' AS source, MAX(CONCAT(ds, '-', hh)) AS max_ts
FROM raw_schema.metrics_data
ORDER BY source
```

**Result**:

```
| source                  | max_ts       |
|-------------------------|--------------|
| source_a (type_a only)  | 20251213-10  |  ⬅ The bottleneck is here!
| source_a (all types)    | 20251213-18  |
| source_b                | 20251213-16  |
```

***

#### Diagnostic Step 4: Confirm data characteristics

```sql
-- Claude automatically executed: check data distribution by type
SELECT event_type, MAX(hh) as max_hour, COUNT(1) as record_count
FROM raw_schema.event_details 
WHERE ds = '20251213' AND event_type IN ('type_a', 'type_b', 'type_c')
GROUP BY event_type
ORDER BY event_type
```

**Result**:

```
| event_type | max_hour | record_count |
|------------|----------|--------------|
| type_a     | 10       | 300          |  ⬅ Event-driven, sparse data
| type_b     | 18       | 7,070        |
| type_c     | 18       | 22,215       |
```

***

### 🤖 Claude Output: Root Cause Analysis Report

By executing queries in the Lakehouse and analyzing the returned data, Claude quickly identified the root cause:

The MV definition uses MIN() to take the minimum boundary value from multiple data sources.
type\_a is event-driven data, where records are only generated when users perform specific actions.
After 10:00 AM on December 13, no relevant actions occurred, causing this data type to "stall" and block the entire MV.

Here is Claude's full response:

```
🔍 Root Cause Analysis Report

Problem Location
The materialized view's data is limited by the MaxDateHour boundary condition to 10:00 AM on December 13, 2025.

Data Verification
| Data Source | Latest Data Time | Notes |
|--------|-------------|------|
| event_details (type_a) | 20251213-10 | ⚠ Bottleneck source |
| event_details (all types) | 20251213-18 | Normal |
| metrics_data | 20251213-16 | Normal |

Root Cause
The MV definition uses MIN() to take the minimum boundary value from multiple data sources.
type_a is event-driven data, where records are only generated when users perform specific actions.
After 10:00 AM on December 13, no relevant actions occurred, causing this data type to "stall" and block the entire MV.

Impact Chain
type_a data stopped at 10:00
    ↓
MaxDateHour = MIN(10, 16) = 10
    ↓
WHERE clause filters out all data > 10:00
    ↓
New data from type_b and type_c is also excluded
    ↓
Materialized view has no new data

Proposed Solution
Modify the MaxDateHour calculation logic, changing the boundary condition from only type_a to include all relevant types...
```

***

## Step 3: Iterate and Optimize the Solution Based on Business Requirements (2 minutes)

Claude's initial proposal was to directly modify the boundary logic. Based on experience, modifying boundary conditions in an existing MV DDL would likely affect historical data after rebuilding. This is unacceptable in businesses where historical data must not be changed.

Therefore, I added the following constraint to the prompt, asking for a better solution under the given requirements:

### 👤 Prompt

```
Adopt this approach: modify the MaxDateHour calculation logic, changing the boundary condition from only type_a to include all types.

However, since this is an MV, changing the DDL and re-refreshing would change all past data, causing inconsistency between historical data and processed records.

So the modification needs to be compatible with historical data: only use the new boundary calculation method starting from 20:00 on December 13, 2025. How should we handle this?
```

> 💡 **Iteration tips**: The initial solution from AI may not fully meet business requirements. The background knowledge of business requirements does not exist in the AI's current conversation context, so you must fully consider and supplement these business constraints to the AI yourself. When using AI to assist with operations and troubleshooting, you cannot stop thinking and blindly follow AI's recommendations. In particular, you need to provide "why this constraint exists," as this better leverages the AI's thinking and reasoning capabilities.
>
> By adding constraints, you enable the AI to generate more precise solutions:
>
> * 📌 **Clear constraint**: Cannot affect historical data
> * 📌 **Define boundary**: Starting from what time point
> * 📌 **Explain reason**: Why this constraint exists

### 🤖 Claude Output: Compatibility Modification Plan

After understanding the business constraints, Claude designed a backward-compatible solution:

```
Design Approach

Need to modify the MaxDateHour logic so that:
- Before 20:00 on December 13, 2025: Continue using the original type_a boundary (protect historical data)
- From 20:00 on December 13, 2025 onward: Use the new all-type boundary

Compatibility Modification SQL

WITH MaxDateHour AS (
    SELECT 
        SPLIT(t2.max_ts, '-')[0] AS max_ds,
        SPLIT(t2.max_ts, '-')[1] AS max_hh,
        t2.max_ts
    FROM (
        SELECT MIN(max_ts) AS max_ts
        FROM (
            -- Data source A (compatible with historical logic)
            SELECT GREATEST(
                -- Original logic: only use type_a (protect historical data)
                (SELECT COALESCE(MAX(CONCAT(ds, '-', hh)), '19700101-00') 
                 FROM raw_schema.event_details 
                 WHERE event_type = 'type_a'),
                 
                -- New logic: all-type boundary, only takes effect >= the switch time
                (SELECT CASE 
                    WHEN MAX(CONCAT(ds, '-', hh)) >= '20251213-20' 
                    THEN MAX(CONCAT(ds, '-', hh)) 
                    ELSE '19700101-00' 
                 END
                 FROM raw_schema.event_details 
                 WHERE event_type IN ('type_a', 'type_b', 'type_c'))
            ) AS max_ts
            
            UNION ALL
            
            -- Data source B (unchanged)
            SELECT MAX(CONCAT(ds, '-', hh)) AS max_ts
            FROM raw_schema.metrics_data
        ) t1
    ) t2
)

Logic Explanation

| Scenario | type_a Boundary | All-type Boundary | GREATEST Result | Effect |
|------|-------------|------------|---------------|------|
| Historical data (< switch point) | 20251213-10 | Returns min value | 20251213-10 | ✅ Keeps original logic |
| New data (≥ switch point) | 20251213-10 | 20251213-18 | 20251213-18 | ✅ Uses new logic |
```

***

## Step 4: Fix the Production Logic Based on Claude's Suggested Solution (2 minutes)

In this case, I directly applied the above logic by manually updating the MV's DDL in the production environment. After rebuilding the MV, the production issue was successfully resolved.

In fact, I could have directly asked Claude to modify the MV based on the above solution — the existing tool capabilities fully support this. However, considering the complexity of the production environment, and to avoid operational errors caused by large model hallucinations that could trigger other issues, I personally prefer a more prudent manual approach for operations involving modifying, writing to, or rebuilding production data and tables.

Another approach would be to have Claude create a temporary view based on the above solution, then automatically compare the data between the two views. After verification, update the original MV's DDL. This would be more robust. Since the issue in this case was relatively straightforward, I skipped this step to fix it quickly.

## Full Conversation Flow in Review

:-: ![](/.topwrite/assets/sre_problem.png =622)

***

## Comparison: Traditional Approach vs. MCP Approach

| Traditional Approach             | MCP + Claude   |
| -------------------- | -------------- |
| Manually read a 200-line MV definition | AI auto-parses and identifies key logic |
| Guess the problem point based on experience | Systematic diagnosis, layer-by-layer verification |
| Manually write multiple diagnostic SQL queries | AI auto-generates and executes queries |
| Results require manual analysis | AI directly provides root cause conclusions |
| Solutions require repeated adjustments | Conversational iteration, fast convergence |

***

*This article is based on a real operations scenario. Table names and business details have been anonymized.*
