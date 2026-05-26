---
name: clickzetta-dynamic-table
description: |
  ClickZetta Dynamic Table（动态表）使用指南与路由中心。

  【触发场景】
  - 通用咨询：动态表介绍、使用方式、最佳实践、性能优化、增量配置
  - 创建指导：DT 声明策略、SQL 支持矩阵、刷新历史查询
  - 修改操作：检测到后自动委托给 dynamic-table-alter 子技能
  - SQL 转换：检测到后自动委托给 sql-to-dt 子技能

  【触发关键词】
  "动态表怎么用"、"DT 介绍"、"动态表最佳实践"、"动态表性能优化"、
  "增量计算配置"、"维度表 JOIN"、"动态表刷新历史"、"静态分区 DT"、
  "动态分区 DT"、"状态表管理"、"非分区表风险"、"创建动态表"、
  "动态表调度"、"REFRESH INTERVAL"、"动态表告警"

  【不触发场景】
  修改操作（"修改动态表"、"加列"、"改间隔"等）→ 使用 dynamic-table-alter
  SQL转换（"转换DT"、"INSERT OVERWRITE转DT"等）→ 使用 sql-to-dt
---

# Dynamic Table 使用指南 — 路由与索引

本技能是 ClickZetta 动态表的**知识中心和路由器**，根据用户意图提供参考文档或自动委托到专门的操作型子技能。

---

## 使用场景分类

### 1. 通用咨询与学习（本技能处理）

**适用场景：**
- 需要查询最佳实践和性能优化建议
- 寻找特定配置项的说明文档
- 学习如何创建动态表

**触发关键词：**
- "动态表怎么用"、"DT 介绍"、"Dynamic Table 是什么"
- "动态表最佳实践"、"DT 性能优化"、"动态表性能调优"
- "增量计算配置"、"刷新策略"、"状态表管理"
- "维度表 JOIN 怎么配置"、"非分区表风险"
- "动态表刷新历史怎么查"、"REFRESH HISTORY"
- "静态分区 DT"、"动态分区 DT"、"DT 声明策略"
- "动态表支持哪些 SQL"、"动态表 SQL 限制"
- "创建动态表"、"新建动态表"、"CREATE DYNAMIC TABLE"

**处理方式：** 提供相关参考文档的内容和指引。

---

### 2. 修改现有动态表（自动委托给 dynamic-table-alter 子技能）

**适用场景：**
- 需要修改已存在的动态表结构或属性
- 暂停/恢复动态表刷新
- 添加/删除列、修改刷新间隔、修改查询定义

**触发关键词：**
- "修改动态表"、"动态表加列"、"动态表删列"
- "改刷新间隔"、"修改 REFRESH_INTERVAL"
- "暂停动态表"、"恢复动态表"、"SUSPEND"、"RESUME"
- "重命名列"、"修改列注释"、"修改表注释"
- "ALTER DYNAMIC TABLE"、"CREATE OR REPLACE DYNAMIC TABLE"
- "修改 DT 查询定义"、"修改 AS SELECT"

**处理方式：**
> ⚠️ 检测到修改操作意图，应立即加载 dynamic-table-alter 子技能。
> 该子技能提供完整的 10 种修改操作工作流：
> - 5种直接 ALTER：suspend、resume、set_comment、rename_column、set_column_comment
> - 5种 CREATE OR REPLACE：add_column、drop_column、alter_column、set_refresh_interval、set_select

---

### 3. SQL 转换为动态表（自动委托给 sql-to-dt 子技能）

**适用场景：**
- 将 Hive/Spark 等任意批处理系统的 CREATE TABLE + INSERT OVERWRITE 转换为 DT
- 批量迁移传统 ETL 到动态表
- 自动生成 refresh、backfill 等配套文件

**触发关键词：**
- "转换 DT"、"sql to dt"、"convert to dynamic table"
- "INSERT OVERWRITE 转 DT"、"DDL 转换"
- "Hive SQL 转 ClickZetta"、"Spark SQL 转动态表"
- "批量转换 ETL"、"迁移到动态表"
- "创建动态表"、"新建动态表"、"CREATE DYNAMIC TABLE"

**处理方式：**
> ⚠️ 检测到 SQL 转换意图，应立即加载 sql-to-dt 子技能。
> 如果用户说"创建动态表"但未提供 DDL 和 INSERT OVERWRITE，应主动提示：
> "请提供原始的 CREATE TABLE DDL 和 INSERT OVERWRITE 语句，我可以全自动生成对应的 Dynamic Table DDL 及配套的 refresh、backfill 文件。"
> 该子技能提供 6 步自动转换工作流：
> 1. 预处理输入（移除 ALTER、ANALYZE、注释）
> 2. 占位符替换（转换为 SESSION_CONFIGS）
> 3. 自引用检测
> 4. 核心转换（合并 DDL + INSERT 为 CREATE OR REPLACE）
> 5. 列校验
> 6. 生成配套文件（refresh、prev_refresh、backfill）

---

## 知识库目录

### dt-creator/ — 创建动态表参考资料

**包含内容：**
- **dt-declaration-strategy.md** — 静态分区 DT vs 动态分区 DT 的声明策略与选择
  - 静态分区 DT：使用 SESSION_CONFIGS() 传递分区参数，每个分区独立刷新
  - 动态分区 DT：不传递分区参数，一次性处理所有增量数据
  - 决策树：根据数据模式选择合适的分区策略

- **sql-limitations.md** — 增量计算支持的 SQL 模式（JOIN、聚合、窗口函数等的支持情况，以及 VIEW/外部表不支持增量的限制）

- **incremental-config-reference.md** — 增量刷新配置项完整参考
  - 刷新策略：强制全量、尝试增量并回退
  - 源表特征声明：维度表、仅追加表
  - 全量回退触发条件：基于表变更或变更量
  - 状态表管理：启用/禁用、生命周期、重建、schema 指定
  - DT 定义变更：CREATE OR REPLACE 的兼容性检查
  - Backfill：历史分区数据修正
  - 分区表写入行为：覆盖 vs 追加模式

- **refresh-history-guide.md** — 刷新历史查询的 3 种方式
  - SHOW DYNAMIC TABLE REFRESH HISTORY：作业级信息，含 refresh_mode（INCREMENTAL/FULL/NO_DATA）
  - DESC HISTORY：版本级历史，含行数、字节数、操作类型
  - information_schema.materialized_view_refresh_history：批量分析、监控、CRU 统计

**适用问题：**
- "静态分区 DT 和动态分区 DT 有什么区别？ "
- "动态表支持哪些 SQL 语法？"
- "增量计算的配置项有哪些？"
- "怎么查看动态表的刷新历史？"
- "什么时候会触发全量刷新？"

---

### dynamic-table-alter/ — 修改动态表操作指南

**包含内容：**
- 完整的动态表修改工作流（10 种操作）
- 5 种直接 ALTER 操作：suspend、resume、set_comment、rename_column、set_column_comment
- 5 种 CREATE OR REPLACE 操作：add_column、drop_column、alter_column、set_refresh_interval、set_select
- 平台特有语法和限制说明（CHANGE COLUMN、RENAME COLUMN、DML 限制等）
- 详细示例和故障排除

> ⚠️ 此目录对应独立的 **dynamic-table-alter 子技能**。当用户有明确的修改操作意图时，应直接加载该子技能而非本指南。

---

### sql-to-dt/ — SQL 转 DT 自动转换

将 Hive/Spark 等任意批处理系统的 CREATE TABLE DDL + INSERT OVERWRITE 全自动转换为 Dynamic Table DDL 及配套文件（refresh、prev_refresh、backfill）。

详细转换规则参见 sql-to-dt 子技能。

---

### best-practices/ — 最佳实践与避坑指南

**包含内容：**

- **performance-optimization.md** — 性能优化策略
  - 核心原则：变更量占比（< 5% 适合增量）、算子类型（INNER JOIN 快于 OUTER JOIN）、数据局部性
  - SQL 优化技巧：优先 INNER JOIN、减少 DISTINCT、窗口函数必须有 PARTITION BY、使用分区条件限制数据范围
  - 管道拆分：将复杂 DT 拆分为多个阶段

- **dimension-table-join-guide.md** — 维度表 JOIN 场景详解
  - 核心机制：维度表变更被忽略，仅事实表变更触发增量计算
  - 配置方式：TBLPROPERTIES('mv_const_tables'='dim1,dim2') 或 Session 配置
  - 推荐场景：码表/字典表、T+1 维度 + 实时事实表、大事实 JOIN 小维度
  - 不推荐场景：频繁更新的维度且需要实时一致性
  - 数据修正：维度表变更后必须使用全量刷新

- **non-partitioned-merge-into-warning.md** — 非分区 DT + 连续写入风险告警
  - 触发条件：DT 是非分区表 + 源表连续写入 + SQL 含 ROW_NUMBER() 去重
  - 三大风险：存储无限增长、归档引发性能灾难、无法过滤归档删除
  - 推荐替代方案：MERGE INTO + Table Stream（归档免疫、独立生命周期管理）

- **scheduling-guide.md** — 调度方式选择指南
  - 两种方式对比：DDL 内置调度（REFRESH INTERVAL）vs Studio Task 调度
  - 有 Studio 时始终推荐 Studio Task：支持上下游依赖、统一告警、可视化监控
  - DDL 内置调度的弊端：无告警、无依赖编排、只能手动 SQL 查询刷新状态
  - Studio Task 配置要点：必须开启自依赖、配置失败/超时告警、按需配置上游依赖
  - 多级 DT 管道的调度编排方式

**适用问题：**
- "动态表性能怎么优化？"
- "维度表 JOIN 怎么配置？"
- "非分区动态表有什么风险？"
- "什么时候不应该用动态表？"
- "动态表调度用 REFRESH INTERVAL 还是 Studio Task？"
- "动态表刷新失败怎么收到告警？"

---

## 路由决策树

```
用户提问
    │
    ├─ 包含修改操作关键词？
    │   （"修改动态表"、"加列"、"改间隔"、"暂停"、"ALTER DYNAMIC TABLE"）
    │   └─ 是 → 立即加载 dynamic-table-alter 子技能
    │
    ├─ 包含 SQL 转换关键词？
    │   （"转换DT"、"sql to dt"、"INSERT OVERWRITE转DT"、"DDL转换"、"创建动态表"）
    │   └─ 是 → 立即加载 sql-to-dt 子技能
    │
    └─ 通用咨询/学习？
        （"动态表怎么用"、"最佳实践"、"性能优化"、"增量配置"）
        └─ 是 → 提供本指南的参考文档
```

---

## 使用建议

1. **首次学习**：从 dt-creator/ 开始，了解 DT 的声明策略和配置项
2. **迁移场景**：使用 sql-to-dt 子技能批量转换现有 ETL
3. **日常运维**：使用 dynamic-table-alter 子技能修改 DT 结构
4. **性能调优**：参考 best-practices/ 中的优化建议和避坑指南
5. **调度配置**：有 Studio 时始终使用 Studio Task 调度，参考 best-practices/scheduling-guide.md

---

## 相关技能

- **dynamic-table-alter** — 修改动态表的操作型子技能（10 种修改操作）
- **sql-to-dt** — SQL 转 DT 的转换型子技能（6 步自动转换工作流）
