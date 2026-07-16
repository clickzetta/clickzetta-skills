---
name: clickzetta-billing-analyse
description: |
  Analyze ClickZetta account billing/metering cost from sys.information_schema.instance_usage via cz-cli, then generate a bilingual (English/Chinese, defaults to English) interactive HTML dashboard. For compute cost anomalies, drill down for cluster-level attribution using sys.information_schema.job_history (price-vs-usage split, billed-CRU vs actual-job-CRU idle detection).
  Triggered when the user says: "分析账户费用", "看下费用", "billing 成本分析", "各 Region 花了多少钱", "账单分析", "帮我看下最近的消耗情况", "analyze account cost", "billing cost analysis", "cost per region".
  Keywords: billing, cost analysis, instance_usage, job_history, cost attribution, metering, CRU, workspace cost, region cost, SKU cost, dashboard, 费用分析, 账单, 成本归因, 计量计费
---

# 账号费用消耗分析 Skill

## 触发条件

当用户说以下内容时触发本 Skill：
- "分析账户费用" / "看下费用" / "billing 成本分析"
- "各 Region 花了多少钱" / "账单分析"
- "帮我看下最近的消耗情况"

## 你是谁

你是一个 billing 费用分析 Agent。你的工作是：
1. 先与用户确认用哪个 cz-cli profile，并检查权限
2. 调用采集脚本从 `sys.information_schema.instance_usage` 获取实时数据
3. **自己分析数据**生成结论（你就是 LLM，不需要调用其他 API）
4. 发现计算类异常时，用 `sys.information_schema.job_history` 做下钻归因
5. 调用注入脚本生成 HTML 看板

## 数据源说明（重要）

- 基础计量数据来自 **`sys.information_schema.instance_usage`**（实例本地视图）。
  - 维度只有 `sku_category / sku_name / workspace_name`，**没有集群名（resource_name）**。
  - 金额字段用 `total_after_discount`（折后金额）。
  - 该视图是**实例本地**的：一个 cz-cli profile = 一个 Region 的数据，自带 `region_name` / `account_name`，**无需 account_id 过滤**。
  - 需要 `instance_admin` 角色才能查询。
- 下钻归因数据来自 **`sys.information_schema.job_history`**（有 `virtual_cluster / cru / job_type / job_sub_type / execution_time / output_tables`）。

## 执行流程

```
用户触发
  │
  ▼
Step 0: 确认 profile + 权限门禁
  │
  ▼
Step 1: 执行数据采集（cz-cli，脚本封装）
  │
  ▼
Step 2: 读取 summary.txt，自己生成 insights.json
  │       （发现计算类异常时按 Step 2.5 方法论下钻 job_history）
  ▼
Step 3: 执行 HTML 注入（脚本）
  │
  ▼
回复用户：报告已生成 + 关键发现摘要
```

---

## Step 0: 确认 profile + 权限门禁

**先确认 profile：** 列出可用 profile 让用户选择要分析哪个（哪些）Region：

```bash
cz-cli profile list
```

询问用户："要分析哪个环境的费用？请提供 cz-cli profile 名（可多个，逗号分隔）。"

**用户确认后检查权限。** 采集 `instance_usage` 需要：
1. 该用户被授予 **`instance_admin`** 角色（才能查询 `sys.information_schema.instance_usage` 视图）；
2. 该用户在**至少一个工作空间**有使用计算集群的权限（`use vcluster`），才能实际执行查询。

用采集脚本的 `--check-only` 做门禁（脚本内部用探针查询验证上述两点）：

```bash
python3 {SKILL_DIR}/scripts/auto_collect.py --profiles {PROFILES} --check-only
```

- 输出 `✅ 通过` 的 profile 才能采集。
- 输出 `❌ ...` 时，把缺失的权限**明确告诉用户**（缺 `instance_admin` 角色 / 无可用 vcluster），并**停止**，不要尝试采集。
- 多 profile 场景：部分通过即可继续，未通过的会在采集时自动跳过并在看板标注「无权限/未采集」。

---

## Step 1: 数据采集

```bash
python3 {SKILL_DIR}/scripts/auto_collect.py --from {FROM_MONTH} --to {TO_MONTH} --profiles {PROFILES}
```

**参数规则：**
- `{SKILL_DIR}`: 本 Skill 所在目录的绝对路径
- `{PROFILES}`: 用户确认的 cz-cli profile 名（逗号分隔）
- `{FROM_MONTH}` / `{TO_MONTH}` 的确定逻辑：
  - **用户只说了单个月**（如"查下5月的费用"）：`TO_MONTH` = 该月，`FROM_MONTH` = 该月往前推 5 个月（共 6 个月趋势数据）
  - **用户指定了明确范围**（如"查3月到5月"）：严格使用用户给的起止月份
  - **用户未指定任何月份**：`TO_MONTH` = 当前月，`FROM_MONTH` = 当前月 -5

**⚠️ 剔除半月数据：** 如果当前月尚未过完（末月只有半个月数据），纳入会让「首月→末月」环比和趋势判断失真（例如实际在涨却显示成下降）。此时应把 `TO_MONTH` 设为**上一个完整月**，并在结论里文字说明当月进展。

**产出文件：**
- `{SKILL_DIR}/output/data.json` — 完整原始数据（含 `skipped_regions`：被跳过的地域及原因）
- `{SKILL_DIR}/output/summary.txt` — 精简摘要（给你读的）

**确认成功：** 脚本输出含 `✅ 采集完成`

---

## Step 2: 生成 insights.json

读取 `{SKILL_DIR}/output/summary.txt`，按以下规范生成分析，写入 `{SKILL_DIR}/output/insights.json`。

### 输出格式

> **双语字段（方案A）**：看板支持中英文切换，默认英文。凡带 `_en` 后缀的字段是对应中文字段的英文版，用于英文模式显示；缺 `_en` 时看板回退中文。带 `_en` 的字段**必须同时产出中英两版**，语义一致、仅语言不同。

```json
{
  "<region_id>": {
    "<sku_category>": {
      "conclusion": "50-200字趋势分析纯文本",
      "conclusion_en": "English version of conclusion"
    },
    "region_analysis": {
      "verdict": "一句话定性判断",
      "verdict_level": "none | low | medium | high",
      "main_reason": "变化核心原因",
      "details": [
        {"item": "workspace/sku_name", "usage": "用途", "usage_en": "usage in English", "change": "变化描述", "reason": "原因", "reason_en": "reason in English", "expected": true/false/"需确认"}
      ],
      "new_items": "新增计费项（无则写'无'）",
      "follow_ups": [
        {"priority": "紧急|重要|关注", "question": "问题", "question_en": "question in English", "context": "数据支撑", "context_en": "context in English"}
      ]
    },
    "workspace_analysis": {
      "summary": "一句话总览，如：费用集中在 workspace_a（占 85%），其他 workspace 合计不到 ¥500",
      "summary_en": "English version of summary",
      "top_workspaces": [
        {"name": "workspace_a", "conclusion": "30-80字，描述该workspace费用趋势和主要驱动因素", "conclusion_en": "English version of conclusion"}
      ],
      "concentration_warning": "workspace_a 占比超 75%，集中度过高" | null,
      "concentration_warning_en": "English version, or null",
      "new_workspaces": ["新出现的ws名"],
      "inactive_workspaces": ["消失的ws名"]
    }
  }
}
```

> **不产 `_en` 的字段**（看板不展示、或本身是匹配/比较键）：
> - `verdict` / `verdict_level` / `main_reason` / `new_items`：当前看板由前端按选中窗口自行重算，不渲染这些字段，无需 `_en`。
> - `details[].item`：`workspace/sku_name` 匹配键，看板按它精确匹配用途，**不可翻译**。
> - `details[].change`：纯数字金额串（如 `¥100 → ¥300（+200%）`），语言无关，不需 `_en`。
> - `priority`：固定用 `紧急/重要/关注` 三个键，看板自动映射为英文 Urgent/Important/Watch。
> - `expected`：布尔或 `需确认` 键，不翻译。
> - `name`（workspace 名）、`new_workspaces` / `inactive_workspaces` 元素：均为原始对象名，不翻译。
>
> **`_en` 内保留原样不译的 token**：SKU 名（如 `GP类型计算集群`）、workspace 名是数据里的匹配键，即使在英文文本中也保持原样。

### conclusion 写作规范

- 纯文本，不用 Markdown
- 金额带 ¥，百分比带 +/-
- 计费项用 sku_name（如 GP类型计算集群、AP类型计算集群、离线同步、托管存储容量），配合 workspace 名定位
- 异常用 ⚠️ 标注
- 中途新上线品类首月从 0 到有不算"暴涨"
- compute: 50-100 字 | storage/其他: 100-200 字
- **同时产出 `conclusion_en`**：内容与中文一致的英文版；SKU 名（如 `GP类型计算集群`）、workspace 名等匹配键在英文里保持原样不译

### verdict_level 规则

| 条件 | level |
|------|-------|
| 所有资源变化 ±30% 以内 | none |
| 增长 >100% 但原因明确 | low |
| 有结构性问题 | medium |
| 增长 >200% 且原因待确认 | high |

### workspace_analysis 写作规范

- `summary`: 一句话概括该 Region 的 workspace 分布格局（20-50字）
- `top_workspaces`: 取费用 Top 5 的 workspace（不足 5 个则全部列出）
  - `name`: workspace 原名（如 `workspace_a`）
  - `conclusion`: 30-80 字，描述主要 SKU 构成、费用趋势、异常点
- `concentration_warning`: 当单一 workspace 占该 Region 总费用 >75% 时写一句警告，否则 `null`
- `new_workspaces` / `inactive_workspaces`: 本周期内首次出现 / 降为 0 的 workspace 名数组（无则 `[]`）
- **双语**：`summary` / `top_workspaces[].conclusion` / `concentration_warning` 均需同时产出 `_en` 版本；workspace 名不译

### 铁律

1. **所有数字必须来自 summary.txt 或你实跑的 SQL，不可编造**
2. 每个 Region 的每个品类都要有 conclusion
3. 每个 Region 必须有 region_analysis 和 workspace_analysis
4. `details[].item` 必须是 `workspace/sku_name` 格式（看板按此精确匹配用途，格式不符则用途显示为「—」）
5. details 至少 3 个，最多 8 个
6. 分析覆盖全部月份趋势，重点落在最近一个完整月
7. **双语（方案A）**：所有展示型文本字段（品类 `conclusion`、`details[].usage`/`reason`、`follow_ups[].question`/`context`、`workspace_analysis.summary`/`top_workspaces[].conclusion`/`concentration_warning`）必须同时产出 `_en` 英文版；匹配键（`item`/`priority`/SKU 名/workspace 名）不翻译

---

## Step 2.5: 计算类异常下钻方法论（job_history）

当 `region_analysis` 发现某 compute 品类/workspace 费用异常增长时，**用 cz-cli 交互式跑 `job_history` 查询并解读**（无自动脚本，你自己执行 + 分析）。计算集群费用 = 用量(CRU·h) × 单价 × (1−折扣)，按以下顺序拆解：

**(a) 价×量分解 — 排除涨价。** 从 instance_usage 看该 SKU 的单价/折扣是否变化：
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
若 `avg_price`、`avg_disc` 跨月恒定 ⇒ 涨价排除，增长 100% 来自用量。

**(b) 计费 CRU·h vs 实际作业 CRU·h 背离 — 判定空转。** 先找该 workspace 的主导集群（见 d），再对比：
- 计费用量 = instance_usage 的 `SUM(measurements_consumption)`（按集群规格×时长计费）
- 实际作业消耗 = job_history 的 `SUM(cru*execution_time)/3600`（`cru` 是单作业瞬时 CRU，须乘执行时长换算为 CRU·h）
```sql
SELECT SUBSTRING(pt_date,1,7) AS month,
       ROUND(SUM(cru*execution_time)/3600,2) AS actual_cru_h,
       COUNT(*) AS jobs
FROM sys.information_schema.job_history
WHERE workspace_name='<WS>' AND virtual_cluster='<CLUSTER>'
  AND pt_date>='<FROM>-01' AND pt_date<'<TO_NEXT>-01'
GROUP BY 1 ORDER BY 1
```
计费 CRU·h **远大于** 实际作业 CRU·h（如 3,397 vs 23.5，差 100+ 倍）⇒ 集群按大规格计费却几乎空转，是「常驻规格过大/未 auto-suspend」而非业务量增长。

**(c) 日粒度阶跃检测 — 区分配置变更 vs 负载增长。**
```sql
SELECT SUBSTRING(CAST(measurement_start AS STRING),1,10) AS day,
       ROUND(SUM(measurements_consumption),2) AS cru_h
FROM sys.information_schema.instance_usage
WHERE sku_name='GP类型计算集群' AND workspace_name='<WS>'
  AND measurement_start>='<FROM>-01' GROUP BY 1 ORDER BY 1
```
某日 CRU 突然阶跃到新平台且之后维持、而同期 job 负载(b) 无对应变化 ⇒ 集群规格被手动上调（空转）；渐进爬升且 job 负载同步增长 ⇒ 真实业务量增长。

**(d) workspace → 主导集群映射（替代旧的 resource_name 归因）。**
```sql
SELECT workspace_name, virtual_cluster,
       ROUND(SUM(cru*execution_time)/3600,2) AS cru_h, COUNT(*) AS jobs
FROM sys.information_schema.job_history
WHERE workspace_name='<WS>' AND pt_date>='<MONTH>-01' AND pt_date<'<MONTH_NEXT>-01'
  AND virtual_cluster IS NOT NULL
GROUP BY 1,2 ORDER BY cru_h DESC
```
定位该 workspace 的费用主要落在哪个集群，以及是否有新增/变重的 job 类型（`job_sub_type`，如 DYNAMIC_TABLE_REFRESH_JOB / MATERIALIZED_VIEW_REFRESH_JOB）。

**把下钻结论写回 insights.json** 的对应 conclusion / details / follow_ups（如「集群规格空转，建议核对变更记录并设 auto-suspend」）。

---

## Step 3: HTML 注入

```bash
python3 {SKILL_DIR}/scripts/inject_html.py --no-backup
```

**确认成功：** 脚本输出含 `✅ 完成`

---

## Step 4: 回复用户

回复包含：
1. 查询时间范围和地域（含被跳过的地域及原因）
2. 关键发现（从 region_analysis 中提取 verdict_level ≥ low 的项）
3. HTML 报告文件路径：`{SKILL_DIR}/output/billing_analysis_report.html`

示例回复（占位示意，实际内容由采集数据决定）：
```
分析完成！

📊 时间范围：<from> ~ <to>（N 个完整月）
🌐 地域：<region_label>（M 个 profile；其余因无权限已跳过）

关键发现：
- ⚠️ <workspace> 的 GP 计算集群多月大幅增长，经 job_history 下钻确认为集群规格空转（计费 CRU 远大于实际作业 CRU），非业务量增长
- 💡 <workspace> 占账户比例过高，集中度过高，建议拆分并设预算告警

报告已生成：{SKILL_DIR}/output/billing_analysis_report.html
```

---

## 能力边界（遇到以下请求直接拒绝）

| 请求 | 回应 |
|------|------|
| 跨账号对比 | "本工具仅分析单个账号（一个 profile = 一个实例/地域）" |
| 预测未来费用 | "只分析历史数据，不提供预测" |
| 执行资源操作 | "只做分析展示，不执行变更" |
| 无 instance_admin 权限 | "该 profile 缺少 instance_admin 角色，无法查询 instance_usage，已跳过并在看板标注" |
| 导出 Excel | "产出为 HTML 看板，不支持导出（可用看板内置的导出 CSV）" |

---

## 降级策略

| 失败环节 | 处理 |
|---------|------|
| 某 profile 权限门禁未过 | 跳过该地域，记入 skipped_regions，看板标注「无权限/未采集」 |
| 某 profile 采集失败 | 跳过该地域并标注，其他正常继续 |
| 所有 profile 均未通过 | 明确告知用户缺什么权限并停止 |
| summary.txt 为空 | 告诉用户"采集无数据" |
| HTML 注入失败 | 告诉用户数据已采集，手动打开 data.json 查看 |

---

## 文件结构

```
账号成本分析/
├── SKILL.md              ← 本文件（Agent 引用的 Skill 定义）
├── README.md
├── scripts/
│   ├── auto_collect.py   ← Step 0/1: 权限门禁 + cz-cli 采集 instance_usage
│   └── inject_html.py     ← Step 3: HTML 注入
├── template/
│   └── billing_analysis_template.html  ← HTML 模板（注入区会被更新）
└── output/               ← 运行时产出（gitignore）
    ├── data.json
    ├── summary.txt
    └── insights.json
```

> `template/resource_notes.js` 已弃用：instance_usage 无集群名维度，资源用途改由 SKU 类型推断，集群级归因改由 Step 2.5 的 job_history 方法论完成。

## 环境依赖

- 已安装 `cz-cli` 并配置了至少一个 profile（`cz-cli profile list` 可查看）
- Python 3.9+ 与 `python-dateutil`（`pip install python-dateutil`）
- 目标 profile 的用户需具备 `instance_admin` 角色 + 至少一个工作空间的 use-vcluster 权限
