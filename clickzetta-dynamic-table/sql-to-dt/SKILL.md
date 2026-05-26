---
name: sql-to-dt
description: 将 Hive/Spark 等任意批处理系统的 CREATE TABLE DDL + INSERT OVERWRITE SQL 自动转换为 Dynamic Table DDL 及配套文件（refresh、prev_refresh、backfill）。当用户提供 DDL 和 INSERT OVERWRITE 要求转换为 DT 时触发，或用户说"创建动态表"时主动引导提供输入。Triggers on: "转换DT", "sql to dt", "convert to dynamic table", "INSERT OVERWRITE 转 DT", "DDL 转换", "创建动态表"
---

# SQL → Dynamic Table 自动转换

将 Hive/Spark 等任意批处理系统的 ETL SQL（CREATE TABLE + INSERT OVERWRITE）转换为 Dynamic Table DDL 及配套运维文件。

## 使用方式

提供以下输入：
1. CREATE TABLE DDL（表结构定义）
2. INSERT OVERWRITE SQL（ETL 查询逻辑）

转换工具会自动完成：占位符替换、自引用检测、核心转换、列校验、配套文件生成、转换后改进建议。

详细工作流参见 #[[file:references/sql2dt-workflow.md]]

## references/

- **sql2dt-workflow.md** — 完整转换工作流（6 步：预处理、占位符替换、自引用检测、核心转换、列校验、配套文件生成）
- **sql2dt-conversion-rules.md** — 核心 DDL 转换规则（解析 DDL、解析 INSERT、组装 DT DDL、静态分区注入）
- **sql2dt-placeholder-rules.md** — 占位符替换规则（${var} → SESSION_CONFIGS()）
- **sql2dt-self-reference-rules.md** — 自引用表转换规则
- **sql2dt-column-validation-rules.md** — 列校验规则（schema 列数 = SELECT 列数）
- **sql2dt-refresh-rules.md** — Refresh 与调度文件生成规则
