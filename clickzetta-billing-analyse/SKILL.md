---
name: clickzetta-billing-analyse
description: |
  Analyze ClickZetta account billing/metering cost from sys.information_schema.instance_usage via cz-cli, then generate a bilingual (English/Chinese, defaults to English) interactive HTML dashboard. For compute cost anomalies, drill down for cluster-level attribution using sys.information_schema.job_history (price-vs-usage split, billed-CRU vs actual-job-CRU idle detection).
  Triggered when the user says: "分析账户费用", "看下费用", "billing 成本分析", "各 Region 花了多少钱", "账单分析", "帮我看下最近的消耗情况", "analyze account cost", "billing cost analysis", "cost per region".
  Keywords: billing, cost analysis, instance_usage, job_history, cost attribution, metering, CRU, workspace cost, region cost, SKU cost, dashboard, 费用分析, 账单, 成本归因, 计量计费
---

# Account Billing Cost Analysis Skill

## Trigger

Trigger this skill when the user says things like:
- "analyze account cost" / "check the cost" / "billing cost analysis"
- "how much did each Region spend" / "bill analysis"
- "show me the recent consumption"

## Who you are

You are a billing cost-analysis Agent. Your job is to:
1. Confirm which cz-cli profile to use and check permissions
2. Call the collection script to fetch live data from `sys.information_schema.instance_usage`
3. **Analyze the data yourself** and produce conclusions (you are the LLM; no other API needed)
4. When compute anomalies appear, drill down for attribution using `sys.information_schema.job_history`
5. Call the injection script to generate the HTML dashboard

## Data sources (important)

- Base metering data comes from **`sys.information_schema.instance_usage`** (instance-local view).
  - Dimensions are only `sku_category / sku_name / workspace_name` — **no cluster name (resource_name)**.
  - Use `total_after_discount` for the amount field.
  - This view is **instance-local**: one cz-cli profile = one Region's data, with built-in `region_name` / `account_name`, so **no account_id filtering needed**.
  - Requires the `instance_admin` role to query.
- Drill-down attribution data comes from **`sys.information_schema.job_history`** (has `virtual_cluster / cru / job_type / job_sub_type / execution_time / output_tables`).

## Workflow

```
User trigger
  │
  ▼
Step 0: Confirm profile + permission gate
  │
  ▼
Step 1: Run data collection (cz-cli, wrapped by script)
  │
  ▼
Step 2: Read summary.txt, generate insights.json yourself
  │       (drill into job_history per Step 2.5 when compute anomalies appear)
  ▼
Step 3: Run HTML injection (script)
  │
  ▼
Reply to user: report generated + key findings summary
```

---

## Step 0: Confirm profile + permission gate

**Confirm the profile first.** List available profiles and let the user pick which Region(s) to analyze:

```bash
cz-cli profile list
```

Ask the user: "Which environment's cost do you want to analyze? Please provide the cz-cli profile name(s) (comma-separated for multiple)."

**After the user confirms, check permissions.** Collecting `instance_usage` requires:
1. The user is granted the **`instance_admin`** role (to query the `sys.information_schema.instance_usage` view);
2. The user has permission to use a compute cluster (`use vcluster`) in **at least one workspace**, to actually run the query.

Use the collection script's `--check-only` as the gate (it internally verifies both via a probe query):

```bash
python3 {SKILL_DIR}/scripts/auto_collect.py --profiles {PROFILES} --check-only
```

- Only profiles that print `✅ passed` can be collected.
- When it prints `❌ ...`, **clearly tell the user** the missing permission (missing `instance_admin` role / no usable vcluster) and **stop** — do not attempt collection.
- Multi-profile case: partial pass is fine to continue; failed ones are auto-skipped during collection and flagged as "no permission / not collected" on the dashboard.

---

## Step 1: Data collection

```bash
python3 {SKILL_DIR}/scripts/auto_collect.py --from {FROM_MONTH} --to {TO_MONTH} --profiles {PROFILES}
```

**Parameter rules:**
- `{SKILL_DIR}`: absolute path of this skill's directory
- `{PROFILES}`: the cz-cli profile name(s) the user confirmed (comma-separated)
- `{FROM_MONTH}` / `{TO_MONTH}` logic:
  - **User named a single month** (e.g. "check May's cost"): `TO_MONTH` = that month, `FROM_MONTH` = 5 months before it (6 months of trend data)
  - **User gave an explicit range** (e.g. "check March to May"): use the given start/end months exactly
  - **User named no month**: `TO_MONTH` = current month, `FROM_MONTH` = current month − 5

**⚠️ Drop half-month data:** If the current month is not over yet (the last month has only half a month of data), including it distorts the first→last month-over-month and trend judgment (e.g. an actual rise shown as a drop). In that case set `TO_MONTH` to **the last complete month**, and note the current month's progress in text within the conclusions.

**Output files:**
- `{SKILL_DIR}/output/data.json` — full raw data (including `skipped_regions`: skipped regions and reasons)
- `{SKILL_DIR}/output/summary.txt` — condensed summary (for you to read)

**Confirm success:** the script output contains `✅ Collection complete`

---

## Step 2: Generate insights.json

Read `{SKILL_DIR}/output/summary.txt` and generate the analysis per the spec below, writing it to `{SKILL_DIR}/output/insights.json`.

### Output format

> **Bilingual fields (Option A)**: the dashboard supports English/Chinese switching and defaults to English. Any field with an `_en` suffix is the English version of the corresponding Chinese field, shown in English mode; when `_en` is missing the dashboard falls back to Chinese. Fields marked with `_en` **must be produced in both languages** — same meaning, different language only.

```json
{
  "<region_id>": {
    "<sku_category>": {
      "conclusion": "50-200 char trend analysis, plain text",
      "conclusion_en": "English version of conclusion"
    },
    "region_analysis": {
      "verdict": "one-sentence qualitative judgment",
      "verdict_level": "none | low | medium | high",
      "main_reason": "core reason for the change",
      "details": [
        {"item": "workspace/sku_name", "usage": "usage", "usage_en": "usage in English", "change": "change description", "reason": "reason", "reason_en": "reason in English", "expected": true/false/"需确认"}
      ],
      "new_items": "new billing items (write '无' if none)",
      "follow_ups": [
        {"priority": "紧急|重要|关注", "question": "question", "question_en": "question in English", "context": "supporting data", "context_en": "context in English"}
      ]
    },
    "workspace_analysis": {
      "summary": "one-sentence overview, e.g.: cost concentrated in workspace_a (85%), other workspaces total under ¥500",
      "summary_en": "English version of summary",
      "top_workspaces": [
        {"name": "workspace_a", "conclusion": "30-80 chars describing this workspace's cost trend and main drivers", "conclusion_en": "English version of conclusion"}
      ],
      "concentration_warning": "workspace_a exceeds 75%, over-concentrated" | null,
      "concentration_warning_en": "English version, or null",
      "new_workspaces": ["newly appeared ws names"],
      "inactive_workspaces": ["disappeared ws names"]
    }
  }
}
```

> **Fields with NO `_en`** (not rendered by the dashboard, or are match/compare keys):
> - `verdict` / `verdict_level` / `main_reason` / `new_items`: the dashboard currently recomputes these on the front end per the selected window and does not render these fields, so no `_en` needed.
> - `details[].item`: the `workspace/sku_name` match key — the dashboard matches usage against it exactly, **do not translate**.
> - `details[].change`: pure numeric amount string (e.g. `¥100 → ¥300（+200%）`), language-agnostic, no `_en`.
> - `priority`: fixed to the three keys `紧急/重要/关注`; the dashboard auto-maps them to English Urgent/Important/Watch.
> - `expected`: boolean or the `需确认` key — not translated.
> - `name` (workspace name), `new_workspaces` / `inactive_workspaces` elements: raw object names, not translated.
>
> **Tokens kept verbatim inside `_en`**: SKU names (e.g. `GP类型计算集群`) and workspace names are match keys in the data — keep them as-is even in English text.

### conclusion writing norms

- Plain text, no Markdown
- Amounts with ¥, percentages with +/-
- Refer to billing items by sku_name (e.g. GP类型计算集群, AP类型计算集群, 离线同步, 托管存储容量) together with the workspace name to locate them
- Mark anomalies with ⚠️
- A category newly launched mid-period (first month 0 → nonzero) does not count as a "spike"
- compute: 50-100 chars | storage/others: 100-200 chars
- **Also produce `conclusion_en`**: the English version with the same content; SKU names (e.g. `GP类型计算集群`) and workspace names and other match keys stay verbatim in English

### verdict_level rules

| Condition | level |
|------|-------|
| All resource changes within ±30% | none |
| Growth >100% but the reason is clear | low |
| Structural problem present | medium |
| Growth >200% and reason unconfirmed | high |

### workspace_analysis writing norms

- `summary`: one sentence on the Region's workspace distribution pattern (20-50 chars)
- `top_workspaces`: the top 5 workspaces by cost (list all if fewer than 5)
  - `name`: the original workspace name (e.g. `workspace_a`)
  - `conclusion`: 30-80 chars describing the main SKU composition, cost trend, and anomalies
- `concentration_warning`: write a one-line warning when a single workspace exceeds 75% of the Region's total cost, otherwise `null`
- `new_workspaces` / `inactive_workspaces`: arrays of workspace names that first appeared / dropped to 0 within the period (`[]` if none)
- **Bilingual**: `summary` / `top_workspaces[].conclusion` / `concentration_warning` must each also produce an `_en` version; workspace names are not translated

### Iron rules

1. **Every number must come from summary.txt or a SQL you actually ran — never fabricate**
2. Every category in every Region must have a conclusion
3. Every Region must have region_analysis and workspace_analysis
4. `details[].item` must be in `workspace/sku_name` format (the dashboard matches usage against it exactly; a malformed value shows usage as "—")
5. At least 3 and at most 8 details
6. Cover the trend across all months, with focus on the most recent complete month
7. **Bilingual (Option A)**: all display-type text fields (category `conclusion`, `details[].usage`/`reason`, `follow_ups[].question`/`context`, `workspace_analysis.summary`/`top_workspaces[].conclusion`/`concentration_warning`) must also produce `_en` English versions; match keys (`item`/`priority`/SKU names/workspace names) are not translated

---

## Step 2.5: Compute anomaly drill-down methodology (job_history)

When `region_analysis` finds an abnormal cost increase in some compute category/workspace, **run `job_history` queries interactively via cz-cli and interpret them** (no automated script — you run and analyze yourself). Compute cluster cost = usage (CRU·h) × unit price × (1 − discount). Break it down in this order:

**(a) Price × volume split — rule out a price hike.** From instance_usage, check whether the SKU's unit price/discount changed:
```sql
SELECT SUBSTRING(CAST(measurement_start AS STRING),1,7) AS month,
       ROUND(SUM(total_after_discount),2) AS amt,
       ROUND(SUM(measurements_consumption),2) AS cru_h,
       ROUND(AVG(CAST(price_rate AS DOUBLE)),4) AS avg_price,
       ROUND(AVG(discount_rate),4) AS avg_disc
FROM sys.information_schema.instance_usage
WHERE sku_name='GP类型计算集群' AND workspace_name='<WS>'
  AND measurement_start>='<FROM>-01' AND measurement_start<'<TO_NEXT>-01'
GROUP BY 1 ORDER BY 1
```
If `avg_price` and `avg_disc` are constant across months ⇒ price hike ruled out, the 100% growth comes from usage.

**(b) Billed CRU·h vs actual job CRU·h divergence — detect idling.** First find the workspace's dominant cluster (see d), then compare:
- Billed usage = `SUM(measurements_consumption)` from instance_usage (billed by cluster size × duration)
- Actual job consumption = `SUM(cru*execution_time)/3600` from job_history (`cru` is per-job instantaneous CRU; multiply by execution time to convert to CRU·h)
```sql
SELECT SUBSTRING(pt_date,1,7) AS month,
       ROUND(SUM(cru*execution_time)/3600,2) AS actual_cru_h,
       COUNT(*) AS jobs
FROM sys.information_schema.job_history
WHERE workspace_name='<WS>' AND virtual_cluster='<CLUSTER>'
  AND pt_date>='<FROM>-01' AND pt_date<'<TO_NEXT>-01'
GROUP BY 1 ORDER BY 1
```
Billed CRU·h **far exceeding** actual job CRU·h (e.g. 3,397 vs 23.5, a 100×+ gap) ⇒ the cluster is billed at a large size but nearly idle — "resident size too large / no auto-suspend" rather than workload growth.

**(c) Daily-granularity step detection — distinguish config change vs load growth.**
```sql
SELECT SUBSTRING(CAST(measurement_start AS STRING),1,10) AS day,
       ROUND(SUM(measurements_consumption),2) AS cru_h
FROM sys.information_schema.instance_usage
WHERE sku_name='GP类型计算集群' AND workspace_name='<WS>'
  AND measurement_start>='<FROM>-01' GROUP BY 1 ORDER BY 1
```
If one day CRU suddenly steps up to a new plateau and stays there while the job load (b) shows no matching change ⇒ the cluster size was manually raised (idling); a gradual climb with job load growing in step ⇒ real workload growth.

**(d) workspace → dominant cluster mapping (replaces the old resource_name attribution).**
```sql
SELECT workspace_name, virtual_cluster,
       ROUND(SUM(cru*execution_time)/3600,2) AS cru_h, COUNT(*) AS jobs
FROM sys.information_schema.job_history
WHERE workspace_name='<WS>' AND pt_date>='<MONTH>-01' AND pt_date<'<MONTH_NEXT>-01'
  AND virtual_cluster IS NOT NULL
GROUP BY 1,2 ORDER BY cru_h DESC
```
Locate which cluster the workspace's cost mainly falls on, and whether there are new/heavier job types (`job_sub_type`, e.g. DYNAMIC_TABLE_REFRESH_JOB / MATERIALIZED_VIEW_REFRESH_JOB).

**Write the drill-down conclusions back into insights.json** under the corresponding conclusion / details / follow_ups (e.g. "cluster size idling, recommend reviewing change records and setting auto-suspend").

---

## Step 3: HTML injection

```bash
python3 {SKILL_DIR}/scripts/inject_html.py --no-backup
```

**Confirm success:** the script output contains `✅ Done`

---

## Step 4: Reply to the user

The reply includes:
1. Query time range and regions (including skipped regions and reasons)
2. Key findings (extract items with verdict_level ≥ low from region_analysis)
3. HTML report file path: `{SKILL_DIR}/output/billing_analysis_report.html`

Example reply (placeholder illustration; actual content depends on collected data):
```
Analysis complete!

📊 Time range: <from> ~ <to> (N complete months)
🌐 Regions: <region_label> (M profiles; others skipped due to no permission)

Key findings:
- ⚠️ <workspace>'s GP compute cluster grew sharply over several months; job_history drill-down confirms it is cluster-size idling (billed CRU far exceeds actual job CRU), not workload growth
- 💡 <workspace> is an over-large share of the account — over-concentrated; recommend splitting and setting a budget alert

Report generated: {SKILL_DIR}/output/billing_analysis_report.html
```

---

## Capability boundaries (reject the following requests directly)

| Request | Response |
|------|------|
| Cross-account comparison | "This tool analyzes a single account only (one profile = one instance/region)" |
| Forecast future cost | "Analyzes historical data only, no forecasting" |
| Perform resource operations | "Analysis and display only, does not execute changes" |
| No instance_admin permission | "This profile lacks the instance_admin role and cannot query instance_usage; it was skipped and flagged on the dashboard" |
| Export to Excel | "The output is an HTML dashboard; export is not supported (you can use the dashboard's built-in CSV export)" |

---

## Fallback strategy

| Failure point | Handling |
|---------|------|
| A profile fails the permission gate | Skip that region, record it in skipped_regions, dashboard flags "no permission / not collected" |
| A profile fails collection | Skip that region and flag it, others continue normally |
| All profiles fail the gate | Clearly tell the user what permission is missing and stop |
| summary.txt is empty | Tell the user "no data collected" |
| HTML injection fails | Tell the user data was collected and to open data.json manually |

---

## File structure

```
clickzetta-billing-analyse/
├── SKILL.md              ← this file (the Skill definition the Agent references)
├── README.md
├── scripts/
│   ├── auto_collect.py   ← Step 0/1: permission gate + cz-cli collection of instance_usage
│   └── inject_html.py    ← Step 3: HTML injection
├── template/
│   └── billing_analysis_template.html  ← HTML template (the injection region is updated)
└── output/               ← runtime artifacts (gitignored)
    ├── data.json
    ├── summary.txt
    └── insights.json
```

> `template/resource_notes.js` is deprecated: instance_usage has no cluster-name dimension, so resource purpose is inferred from the SKU type, and cluster-level attribution is handled by the Step 2.5 job_history methodology.

## Requirements

- `cz-cli` installed with at least one profile configured (`cz-cli profile list` to check)
- Python 3.9+ and `python-dateutil` (`pip install python-dateutil`)
- The target profile's user needs the `instance_admin` role + use-vcluster permission on at least one workspace
