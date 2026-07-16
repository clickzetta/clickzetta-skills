---
name: clickzetta-billing-analyse
description: |
  Analyze ClickZetta account billing/metering cost from sys.information_schema.instance_usage via cz-cli, then generate a bilingual (English/Chinese, defaults to English) interactive HTML dashboard. For compute cost anomalies, drill down for cluster-level attribution using sys.information_schema.job_history (price-vs-usage split, billed-CRU vs actual-job-CRU idle detection).
  Triggered when the user says: "分析账户费用", "看下费用", "billing 成本分析", "各 Region 花了多少钱", "账单分析", "帮我看下最近的消耗情况", "analyze account cost", "billing cost analysis", "cost per region".
  Keywords: billing, cost analysis, instance_usage, job_history, cost attribution, metering, CRU, workspace cost, region cost, SKU cost, dashboard, 费用分析, 账单, 成本归因, 计量计费
---

# Account Cost Analysis Skill

## Triggers

This Skill triggers when the user says things like:
- "analyze account cost" / "check the cost" / "billing cost analysis"
- "how much did each region cost" / "billing breakdown"
- "show me the recent consumption"

## Who You Are

You are a billing cost analysis Agent. Your job is to:
1. First confirm which cz-cli profile to use, and check permissions
2. Call the collection script to fetch live data from `sys.information_schema.instance_usage`
3. **Analyze the data yourself** to produce conclusions (you are the LLM — no other API calls needed)
4. When you find compute-related anomalies, drill down for attribution using `sys.information_schema.job_history`
5. Call the injection script to generate the HTML dashboard

## Data Sources (Important)

- Base metering data comes from **`sys.information_schema.instance_usage`** (an instance-local view).
  - Dimensions are only `sku_category / sku_name / workspace_name` — there is **no cluster name (resource_name)**.
  - Use `total_after_discount` (discounted amount) for the money field.
  - This view is **instance-local**: one cz-cli profile = one region's data, carrying its own `region_name` / `account_name`, so **no account_id filter is needed**.
  - Requires the `instance_admin` role to query.
- Drill-down attribution data comes from **`sys.information_schema.job_history`** (has `virtual_cluster / cru / job_type / job_sub_type / execution_time / output_tables`).

## Execution Flow

```
User trigger
  │
  ▼
Step 0: Confirm profile + permission gate
  │
  ▼
Step 1: Run data collection (cz-cli, wrapped in a script)
  │
  ▼
Step 2: Read summary.txt, generate insights.json yourself
  │       (when a compute anomaly appears, drill down into job_history per the Step 2.5 methodology)
  ▼
Step 3: Run HTML injection (script)
  │
  ▼
Reply to user: report generated + summary of key findings
```

---

## Step 0: Confirm Profile + Permission Gate

**Confirm the profile first:** list available profiles so the user can pick which region(s) to analyze:

```bash
cz-cli profile list
```

Ask the user: "Which environment's cost do you want to analyze? Please provide the cz-cli profile name(s) (multiple allowed, comma-separated)."

**After the user confirms, check permissions.** Collecting `instance_usage` requires:
1. The user is granted the **`instance_admin`** role (needed to query the `sys.information_schema.instance_usage` view);
2. The user has permission to use a compute cluster (`use vcluster`) in **at least one workspace**, in order to actually run queries.

Use the collection script's `--check-only` as the gate (internally it verifies both points with probe queries):

```bash
python3 {SKILL_DIR}/scripts/auto_collect.py --profiles {PROFILES} --check-only
```

- Only profiles that output `✅ passed` can be collected.
- When a profile outputs `❌ ...`, **clearly tell the user** which permission is missing (no `instance_admin` role / no usable vcluster), and **stop** — do not attempt collection.
- Multi-profile case: it's fine to proceed if some pass; those that fail are automatically skipped during collection and flagged as "no permission / not collected" on the dashboard.

---

## Step 1: Data Collection

```bash
python3 {SKILL_DIR}/scripts/auto_collect.py --from {FROM_MONTH} --to {TO_MONTH} --profiles {PROFILES}
```

**Parameter rules:**
- `{SKILL_DIR}`: absolute path to this Skill's directory
- `{PROFILES}`: the cz-cli profile name(s) the user confirmed (comma-separated)
- How to determine `{FROM_MONTH}` / `{TO_MONTH}`:
  - **User named a single month** (e.g. "check May's cost"): `TO_MONTH` = that month, `FROM_MONTH` = 5 months before it (6 months of trend data total)
  - **User specified an explicit range** (e.g. "check March to May"): use the exact start/end months given
  - **User specified no month at all**: `TO_MONTH` = current month, `FROM_MONTH` = current month − 5

**⚠️ Exclude partial-month data:** if the current month is not over yet (the last month only has half a month of data), including it distorts the first-month→last-month comparison and trend judgment (e.g. an actual rise shows up as a decline). In that case set `TO_MONTH` to the **last complete month**, and note the current month's progress in the conclusions as text.

**Output files:**
- `{SKILL_DIR}/output/data.json` — full raw data (includes `skipped_regions`: skipped regions and the reason)
- `{SKILL_DIR}/output/summary.txt` — condensed summary (for you to read)

**Confirm success:** the script output contains `✅ 采集完成` (collection complete)

---

## Step 2: Generate insights.json

Read `{SKILL_DIR}/output/summary.txt`, produce the analysis per the spec below, and write it to `{SKILL_DIR}/output/insights.json`.

### Output Format

> **Bilingual fields (Option A)**: the dashboard supports switching between Chinese and English, defaulting to English. Every field with an `_en` suffix is the English version of the corresponding Chinese field, shown in English mode; when `_en` is missing the dashboard falls back to Chinese. Fields that have an `_en` counterpart **must be produced in both Chinese and English** — same meaning, only the language differs.

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
        {"item": "workspace/sku_name", "usage": "purpose", "usage_en": "usage in English", "change": "change description", "reason": "reason", "reason_en": "reason in English", "expected": true/false/"需确认"}
      ],
      "new_items": "newly added billing items (write '无' if none)",
      "follow_ups": [
        {"priority": "紧急|重要|关注", "question": "question", "question_en": "question in English", "context": "supporting data", "context_en": "context in English"}
      ]
    },
    "workspace_analysis": {
      "summary": "one-sentence overview, e.g.: cost is concentrated in workspace_a (85%), all other workspaces total under ¥500",
      "summary_en": "English version of summary",
      "top_workspaces": [
        {"name": "workspace_a", "conclusion": "30-80 chars, describing this workspace's cost trend and main drivers", "conclusion_en": "English version of conclusion"}
      ],
      "concentration_warning": "workspace_a exceeds 75% — concentration too high" | null,
      "concentration_warning_en": "English version, or null",
      "new_workspaces": ["newly appeared ws names"],
      "inactive_workspaces": ["ws names that dropped to 0"]
    }
  }
}
```

> **Fields with NO `_en`** (not displayed by the dashboard, or are matching/comparison keys):
> - `verdict` / `verdict_level` / `main_reason` / `new_items`: the current dashboard recomputes these on the frontend for the selected window and does not render them, so no `_en` is needed.
> - `details[].item`: the `workspace/sku_name` matching key — the dashboard matches purpose exactly by it, so it **must not be translated**.
> - `details[].change`: a pure numeric amount string (e.g. `¥100 → ¥300 (+200%)`), language-independent, no `_en` needed.
> - `priority`: fixed to the three keys `紧急/重要/关注`; the dashboard maps them to English Urgent/Important/Watch automatically.
> - `expected`: boolean or the `需确认` (to confirm) key — not translated.
> - `name` (workspace name), `new_workspaces` / `inactive_workspaces` elements: all raw object names, not translated.
>
> **Tokens kept as-is (untranslated) inside `_en` text**: SKU names (e.g. `GP类型计算集群`) and workspace names are matching keys in the data, so keep them verbatim even inside English text.

### conclusion Writing Guidelines

- Plain text, no Markdown
- Amounts prefixed with ¥, percentages with +/−
- Refer to billing items by sku_name (e.g. GP类型计算集群, AP类型计算集群, 离线同步, 托管存储容量), together with the workspace name to locate them
- Mark anomalies with ⚠️
- A category launched mid-period going from 0 to non-zero in its first month is not a "spike"
- compute: 50-100 chars | storage/other: 100-200 chars
- **Also produce `conclusion_en`**: an English version with the same content as the Chinese; matching keys such as SKU names (e.g. `GP类型计算集群`) and workspace names stay verbatim in English

### verdict_level Rules

| Condition | level |
|------|-------|
| All resource changes within ±30% | none |
| Growth >100% but the reason is clear | low |
| A structural problem exists | medium |
| Growth >200% and the reason needs confirmation | high |

### workspace_analysis Writing Guidelines

- `summary`: one sentence summarizing this region's workspace distribution (20-50 chars)
- `top_workspaces`: the top 5 workspaces by cost (list all if fewer than 5)
  - `name`: the workspace's original name (e.g. `workspace_a`)
  - `conclusion`: 30-80 chars, describing the main SKU composition, cost trend, and anomalies
- `concentration_warning`: when a single workspace accounts for >75% of the region's total cost, write a one-line warning; otherwise `null`
- `new_workspaces` / `inactive_workspaces`: arrays of workspace names that first appeared / dropped to 0 in this period (`[]` if none)
- **Bilingual**: `summary` / `top_workspaces[].conclusion` / `concentration_warning` all need an `_en` version produced alongside; workspace names are not translated

### Iron Rules

1. **All numbers must come from summary.txt or SQL you actually ran — never fabricate**
2. Every category in every region must have a conclusion
3. Every region must have region_analysis and workspace_analysis
4. `details[].item` must be in `workspace/sku_name` format (the dashboard matches purpose exactly by this; a non-conforming format shows the purpose as "—")
5. At least 3 and at most 8 details
6. The analysis covers the trend across all months, with the focus on the most recent complete month
7. **Bilingual (Option A)**: all display-type text fields (category `conclusion`, `details[].usage`/`reason`, `follow_ups[].question`/`context`, `workspace_analysis.summary`/`top_workspaces[].conclusion`/`concentration_warning`) must be produced with an `_en` English version; matching keys (`item`/`priority`/SKU names/workspace names) are not translated

---

## Step 2.5: Compute Anomaly Drill-Down Methodology (job_history)

When `region_analysis` finds an abnormal cost increase for a compute category/workspace, **run `job_history` queries interactively via cz-cli and interpret them** (no automatic script — you run and analyze yourself). Compute cluster cost = usage (CRU·h) × unit price × (1−discount); decompose it in the following order:

**(a) Price × usage split — rule out a price increase.** Check from instance_usage whether this SKU's unit price/discount changed:
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
If `avg_price` and `avg_disc` are constant across months ⇒ price increase is ruled out, and the 100% growth comes from usage.

**(b) Billed CRU·h vs actual-job CRU·h divergence — detect idling.** First find the workspace's dominant cluster (see d), then compare:
- Billed usage = `SUM(measurements_consumption)` from instance_usage (billed by cluster spec × duration)
- Actual job consumption = `SUM(cru*execution_time)/3600` from job_history (`cru` is a single job's instantaneous CRU, so multiply by execution time to convert to CRU·h)
```sql
SELECT SUBSTRING(pt_date,1,7) AS month,
       ROUND(SUM(cru*execution_time)/3600,2) AS actual_cru_h,
       COUNT(*) AS jobs
FROM sys.information_schema.job_history
WHERE workspace_name='<WS>' AND virtual_cluster='<CLUSTER>'
  AND pt_date>='<FROM>-01' AND pt_date<'<TO_NEXT>-01'
GROUP BY 1 ORDER BY 1
```
Billed CRU·h **far exceeding** actual-job CRU·h (e.g. 3,397 vs 23.5, a 100×+ gap) ⇒ the cluster is billed at a large spec but almost idle — this is "over-sized always-on spec / no auto-suspend", not business-volume growth.

**(c) Daily-granularity step detection — distinguish config change vs load growth.**
```sql
SELECT SUBSTRING(CAST(measurement_start AS STRING),1,10) AS day,
       ROUND(SUM(measurements_consumption),2) AS cru_h
FROM sys.information_schema.instance_usage
WHERE sku_name='GP类型计算集群' AND workspace_name='<WS>'
  AND measurement_start>='<FROM>-01' GROUP BY 1 ORDER BY 1
```
CRU suddenly stepping to a new plateau on a given day and staying there, while the job load (b) shows no matching change ⇒ the cluster spec was manually raised (idling); a gradual climb with job load growing in sync ⇒ genuine business-volume growth.

**(d) workspace → dominant-cluster mapping (replaces the old resource_name attribution).**
```sql
SELECT workspace_name, virtual_cluster,
       ROUND(SUM(cru*execution_time)/3600,2) AS cru_h, COUNT(*) AS jobs
FROM sys.information_schema.job_history
WHERE workspace_name='<WS>' AND pt_date>='<MONTH>-01' AND pt_date<'<MONTH_NEXT>-01'
  AND virtual_cluster IS NOT NULL
GROUP BY 1,2 ORDER BY cru_h DESC
```
Locate which cluster the workspace's cost mainly lands on, and whether there are new/heavier job types (`job_sub_type`, e.g. DYNAMIC_TABLE_REFRESH_JOB / MATERIALIZED_VIEW_REFRESH_JOB).

**Write the drill-down conclusions back into insights.json** in the corresponding conclusion / details / follow_ups (e.g. "cluster spec idling — recommend reviewing the change log and setting auto-suspend").

---

## Step 3: HTML Injection

```bash
python3 {SKILL_DIR}/scripts/inject_html.py --no-backup
```

**Confirm success:** the script output contains `✅ 完成` (done)

---

## Step 4: Reply to User

The reply includes:
1. The queried time range and regions (including skipped regions and the reason)
2. Key findings (extract items with verdict_level ≥ low from region_analysis)
3. The HTML report file path: `{SKILL_DIR}/output/billing_analysis_report.html`

Example reply (placeholder illustration; actual content is driven by the collected data):
```
Analysis complete!

📊 Time range: <from> ~ <to> (N complete months)
🌐 Regions: <region_label> (M profiles; the rest skipped due to missing permission)

Key findings:
- ⚠️ <workspace>'s GP compute cluster grew sharply over several months; job_history drill-down confirms cluster-spec idling (billed CRU far exceeds actual-job CRU), not business-volume growth
- 💡 <workspace> accounts for too high a share of the account — concentration too high; recommend splitting and setting a budget alert

Report generated: {SKILL_DIR}/output/billing_analysis_report.html
```

---

## Capability Boundaries (reject the following requests directly)

| Request | Response |
|------|------|
| Cross-account comparison | "This tool only analyzes a single account (one profile = one instance/region)" |
| Forecast future cost | "Only historical data is analyzed; no forecasting is provided" |
| Perform resource operations | "Analysis and display only; no changes are executed" |
| No instance_admin permission | "This profile lacks the instance_admin role and cannot query instance_usage; it has been skipped and flagged on the dashboard" |
| Export to Excel | "The output is an HTML dashboard; export is not supported (you can use the dashboard's built-in CSV export)" |

---

## Fallback Strategy

| Failure point | Handling |
|---------|------|
| A profile fails the permission gate | Skip that region, record it in skipped_regions, flag "no permission / not collected" on the dashboard |
| A profile fails collection | Skip that region and flag it; others continue normally |
| No profile passes | Clearly tell the user what permission is missing and stop |
| summary.txt is empty | Tell the user "collection returned no data" |
| HTML injection fails | Tell the user the data was collected, and open data.json manually to inspect |

---

## File Structure

```
clickzetta-billing-analyse/
├── SKILL.md              ← this file (the Skill definition the Agent references)
├── scripts/
│   ├── auto_collect.py   ← Step 0/1: permission gate + cz-cli instance_usage collection
│   └── inject_html.py     ← Step 3: HTML injection
├── template/
│   └── billing_analysis_template.html  ← HTML template (the injection region is updated)
└── output/               ← runtime artifacts (gitignored)
    ├── data.json
    ├── summary.txt
    └── insights.json
```

> `template/resource_notes.js` is deprecated: instance_usage has no cluster-name dimension, so resource purpose is inferred from the SKU type, and cluster-level attribution is handled by the Step 2.5 job_history methodology.

## Environment Requirements

- `cz-cli` installed with at least one profile configured (`cz-cli profile list` to check)
- Python 3.9+ and `python-dateutil` (`pip install python-dateutil`)
- The target profile's user needs the `instance_admin` role + use-vcluster permission on at least one workspace
