# Dynamic Table 调度方式选择指南

## 两种调度方式对比

| 方式 | 做法 | 优点 | 缺点 |
|------|------|------|------|
| **DDL 内置调度**（REFRESH INTERVAL） | 在 CREATE DYNAMIC TABLE 时写 `REFRESH INTERVAL` 子句，由 Lakehouse 自动触发 | 简单，无需额外配置 | 无告警、无依赖编排、刷新状态只能手动 SQL 查询 |
| **Studio Task 调度**（推荐） | 在 Studio 创建定时任务，任务内容为 `REFRESH DYNAMIC TABLE` 命令 | 支持上下游依赖、统一告警、可视化监控 | 需要额外创建 Task |

**生产环境推荐使用 Studio Task 调度。** DDL 内置调度适合快速验证和开发测试阶段。

---

## DDL 内置调度

在 CREATE 语句中通过 `REFRESH INTERVAL` 子句定义刷新频率，Lakehouse 自动周期性触发：

```sql
CREATE DYNAMIC TABLE sales_daily
REFRESH INTERVAL 1 DAY
VCLUSTER default
AS
SELECT DATE(created_at) AS dt, SUM(amount) AS total
FROM orders
GROUP BY 1;
```

### 弊端

- **无告警**：刷新失败不会主动通知，只能手动执行 SQL 查询状态
- **无依赖编排**：无法声明"等上游任务完成后再刷新"，只能靠时间间隔错开
- **监控成本高**：需要定期手动执行以下命令检查刷新是否正常

```sql
-- 查看刷新历史，确认 state 是否为 SUCCEED
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE name = 'your_dt_name';
```

关键字段说明：

| 字段 | 含义 |
|------|------|
| `state` | SUCCEED / FAILED / RUNNING / QUEUED |
| `refresh_mode` | INCREMENTAL / FULL / NO_DATA |
| `error_message` | 失败时的错误信息 |
| `duration` | 本次刷新耗时 |
| `stats` | 增量行数（rows_inserted / rows_deleted） |

---

## Studio Task 调度（生产推荐）

在 Studio 中创建 SQL 任务，任务内容为 REFRESH 命令，通过 Studio 的调度系统管理执行。

### Task 内容

**非分区 DT：**

```sql
REFRESH DYNAMIC TABLE schema_name.dt_name;
```

**分区 DT（带参数）：**

```sql
SET dt.args.ds = '${bizdate}';
REFRESH DYNAMIC TABLE schema_name.dt_name PARTITION (ds = '${bizdate}');
```

`${bizdate}` 由 Studio 调度引擎在每次执行时自动替换为业务日期。

### 必须配置自依赖

同一张 DT 禁止并发 REFRESH（会导致写冲突或数据不一致）。Task 必须开启**自依赖**，确保上一个实例完成后才启动下一个实例。

### 上游依赖配置

- 如果 DT 的源表数据需要等上游任务产出后才能刷新 → 配置上游依赖
- 如果源表数据不要求同步就绪（如实时写入表）→ 可以不配置上游依赖

### 告警配置

Studio Task 支持以下告警规则，生产环境建议全部配置：

- **失败告警**：任务执行失败时通知
- **超时告警**：刷新耗时超过阈值时通知（用于发现性能回退）
- **未运行告警**：任务在预期时间内未启动时通知

---

## 多级 DT 管道的调度编排

当存在多张 DT 形成上下游依赖时（如 DT_A → DT_B → DT_C），每张 DT 对应一个 Studio Task，通过任务依赖关系保证执行顺序：

```
Task_A (REFRESH DT_A)
    └─ Task_B (REFRESH DT_B，依赖 Task_A)
        └─ Task_C (REFRESH DT_C，依赖 Task_B)
```

不同分区的 REFRESH 可以并行执行（分配到不同 Task 实例），同一分区/非分区 DT 禁止并发。

---

## 判断逻辑：向用户推荐调度方式

在帮助用户创建或配置 DT 时，按以下逻辑推荐：

1. **是否有 Studio？**
   - 有 → 始终推荐 Studio Task 调度，无论是开发还是生产环境
   - 无 → 使用 DDL 内置调度或第三方调度引擎

2. **是否有上下游依赖？**
   - 有（如源表由另一个任务产出）→ 必须用 Studio Task，配置上游依赖
   - 无 → 仍推荐 Studio Task，获得告警能力

3. **用户已经写了 REFRESH INTERVAL 子句？**
   - 提示：可以去掉 REFRESH INTERVAL 子句，改用 Studio Task 调度，获得告警和依赖管理能力
   - REFRESH INTERVAL 和 Studio Task 可以共存，但会导致双重触发，建议二选一

---

## 告警话术模板

当用户使用 DDL 内置调度时，使用以下话术提示：

> 💡 **建议**：您当前使用的是 DDL 内置调度（REFRESH INTERVAL），这种方式存在以下局限：
>
> 1. **无告警**：刷新失败不会主动通知，需要手动执行 `SHOW DYNAMIC TABLE REFRESH HISTORY` 查看状态
> 2. **无依赖编排**：无法声明上下游任务依赖关系，只能靠时间间隔错开
>
> **推荐**：在 Studio 中创建定时调度任务，任务内容为 `REFRESH DYNAMIC TABLE schema.dt_name`，并配置：
> - 自依赖（防止并发刷新）
> - 失败告警 + 超时告警
> - 上游依赖（如果源表由其他任务产出）
