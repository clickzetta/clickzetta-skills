---
name: clickzetta-compaction-adviser
description: |
  指导用户通过调整 Compaction 参数来控制单分区文件数、提升 tableScan/查询效率。诊断表结构、写入历史与文件数现状，按表模型（IGS / SQL 维护）、写入 pattern（appendOnly / 更新 / 高频更新）和分区方式给出 Compaction 参数建议。

  当用户反馈某张表扫描慢、文件多、小文件多、delta 文件多、Compaction 不生效，需要诊断现状并给出建表/改表参数建议时调用。

  Keywords: compaction, small files, file count, tableScan, delta, minor compaction, IGS, upsert, merge, compaction strategy, target file size, table properties
---

# Compaction 调优顾问

当一张表 tableScan 慢、文件数多、疑似 Compaction 不生效时，按本流程诊断现状、判断表模型与写入 pattern，再给出可落地的 Compaction 参数建议。

## 何时使用

- 用户反馈某张表查询慢、tableScan 慢、扫描文件多
- 单分区小文件数量异常多，怀疑 Compaction 没跟上
- 需要为 IGS 实时写入 / 删改表选择合适的 Compaction 策略
- 需要显式控制目标文件大小
- 频繁更新的表，delta 文件累积过多拖慢查询，需要压制单个 file slice 上的 delta 个数

## 前置说明

- **本 skill 不执行任何 SQL，只给诊断 SQL 和参数建议。** 所有诊断 SQL 都交给用户在目标 Lakehouse 上自行执行，并把结果贴回；基于贴回的结果做判断和推荐。不要调用任何 SQL 执行工具去跑这些语句。
- 参数最终通过建表 `PROPERTIES(...)` 或 `ALTER TABLE ... SET PROPERTIES(...)` 落到表上——同样只给出可执行语句，由用户自行执行。
- 只推荐本文列出的、已确认存在的参数，**不要凭空捏造参数名**。

## 诊断流程

### Step 1 — 读取表结构与现有参数

请用户执行以下 SQL 并贴回结果：

```sql
SHOW CREATE TABLE ${tableName};
```

从结果里提取：
- 输出中 `TBLPROPERTIES(...)` 里已有的 `cz.compaction.*` / `cz.table.*.file.size` 等参数（避免重复建议已设置项）
- bucket 数（`CLUSTERED INTO N BUCKETS`）
- 分区键 / 分区方式（没有 `PARTITIONED BY` 即为**非分区表**，strategy 配置走 7.7）

**1.1** 若 properties 里存在 `'cz.streaming.table'='true'`，标记为 **IGS 正在写的 PK 表**（实时写入的主键表）。

### Step 2 — 扫描写入历史，判断是否有更新类操作

请用户执行以下 SQL 并贴回结果：

```sql
DESC HISTORY ${tableName};
```

看 history 中的操作类型：
- **2.1 存在更新类操作**：`UPLOAD`（IGS 的 Upsert，等同 upsert）、`UPSERT`、`DELETE`、`UPDATE`、`MERGE` 等 → 需要设置 **DML 模式**的 Compaction，定义为**删改表**。
- **2.2 全部是 `INSERT`** → append-only，无需额外设置 DML 模式。

同时观察写入频率与写入量（尤其是 60s 以内的高频更新，见 Step 5）。

### Step 3 — 获取当前文件数现状

请用户执行以下 SQL 并贴回结果。

**分区表：**

```sql
SHOW PARTITIONS EXTENDED ${tableName};
```

关注每个分区的文件数（`total_files`）、以及平均单文件大小（`bytes / total_files`）；`last_compaction_time` 可辅助判断该分区最近是否被合并过。

**非分区表**（`SHOW PARTITIONS` 会报 `not a partitioned table`），只能用 `SHOW FILES` 统计整表文件数：

```sql
SELECT count(*) FROM (SHOW FILES FOR ${tableName});
```

整张表视为一个合并范围。需要平均文件大小或区分 base / delta 文件时，可按 `file_type`（`DATA_FILE` / `DELTA_FILE`）聚合：

```sql
SELECT file_type, count(*) AS file_count, avg(size) AS avg_bytes
FROM (SHOW FILES FOR ${tableName})
GROUP BY file_type;
```

### Step 4 — 确定表模型

结合 1.1：
- **IGS Upsert 表**（`cz.streaming.table=true`，一定是更新表）
- **SQL 维护的表**（普通建表 / 通过 SQL DML 维护）

### Step 5 — 确定写入 pattern

结合 Step 2：
- **appendOnly 表**：只 INSERT
- **更新表**：存在 UPSERT/DELETE/UPDATE/MERGE/UPLOAD
- **高频更新表**：更新频率在 60s 以内（如 IGS 5–10s 一次 UPLOAD）

### Step 6 — 选择调优目标

和用户确认想要哪种取向：

| 目标 | 含义 | 代价 |
| --- | --- | --- |
| **极致性能** | 快速查询，文件激进合并 | 有一定写放大 |
| **常规** | 平衡默认 | — |
| **大表成本优先** | 合并为更大文件，合并相对迟缓 | 瞬时文件数可能偏高 |

### Step 7 — 现状判断 + 参数推荐

**默认配置总览**（按 Step 1 / Step 4 / Step 5 的结论查表）：

| 写入方式 | 分区 | 更新 | 默认建议 |
| --- | --- | --- | --- |
| IGS 表 | 分区 / 非分区 | 有 / 无 | **不配置 `cz.compaction.strategy`**。已配置的建议 unset：`ALTER TABLE ${tableName} UNSET PROPERTIES('cz.compaction.strategy')` |
| 普通表 | 分区 / 非分区 | 无更新 | **不需要配置** |
| 普通表 | 分区表 | 有更新 | `'cz.compaction.strategy' = 'dml\|background'` |
| 普通表 | 非分区表 | 有更新 | `'cz.compaction.strategy' = 'dml\|background'`<br>高频更新、需要严格避免冲突时改用 `'cz.compaction.strategy' = 'dml'` |

> - strategy 含 `dml` 时，系统自动补 `min.interval=3600` 和 `ignore.hot.data.window=3600`，不需要手动配置；不要配已废弃的 `ignore.latest.partition.window`（见 7.4）。
> - 例外：同时有 IGS 写入和 SQL DML（如 MERGE INTO）的表，配 `dml|background`；非分区表还要加 `'cz.compaction.ignore.hot.data.window' = '0'`（见 7.3）。
> - 以上是默认建议。追求查询性能时再叠加 7.2（激进合并文件和 delta）或 7.6（常规压 delta）。

#### 7.1 先判断 Compaction 现状是否有问题

以单个分区为单位（非分区表以整表为单位）：
- **文件数远大于 `bucket数 × 5`** → Compaction 可能存在问题（`min.file.count` 默认 5，是按 bucket 触发的阈值）。
- **平均文件大小远小于 `cz.table.advised.file.size` 或 `cz.table.target.file.size`** → Compaction 可能存在问题。注意：平均文件小于 target 是正常的（target 是合并目标上限，落在其下的可接受区间内很常见），关键看是否**远小于**——例如 advised/target 是 128MB，但 avg 只有 1–10MB，说明大量小文件没被合并起来，才判为异常。
- **history 里写入/更新非常频繁且量很大** → 很可能处于「两次 Compaction 间隙中文件快速增长，直到下一轮 Compaction」的循环周期里。默认约 1h 一轮，此时 Compaction **运行正常**，但不能保证每个瞬时文件数都被压制过。这种情况要向用户说明，避免误判为故障。

#### 7.2 极致性能（任何模型都适用）

激进合并，代价是一定写放大：

```sql
ALTER TABLE ${tableName} SET PROPERTIES (
  'cz.compaction.server.min.file.count' = '2',
  'cz.compaction.server.force.file.count' = '2'
);
```
> `min.file.count` 默认 5、`force.file.count` 默认 64；降到 2 表示两个文件就触发/强制合并。

**若是更新表 / 高频更新表**（history 中有 UPSERT/DELETE/UPDATE/MERGE/UPLOAD），极致性能还要同时极致压制 delta，把 7.6 的两个方向都开到最激进：

```sql
ALTER TABLE ${tableName} SET PROPERTIES (
  'cz.compaction.server.min.file.count' = '2',
  'cz.compaction.server.force.file.count' = '2',
  'cz.compaction.server.delta.count.threshold' = '2',
  'cz.compaction.server.delta.overhead.ratio' = '0.1',
  'cz.compaction.server.delta.size.overhead.ratio' = '0.1'
);
```
> - `delta.count.threshold=2`（默认 3）：单 file slice 攒到 2 个 position-delete delta 就做 minor compaction 合成 1 个。2 已是下限，minor 是把多个 delta 合成一个，1 个 delta 没有可合并的对象，不要设成 1。
> - `delta.overhead.ratio=0.1`（默认 0.5）、`delta.size.overhead.ratio=0.1`（默认 1.0）：被修改 cell 超过 base 的 10%，或 delta 总大小超过 base 的 10%，就把 base+delta 重写成新 base，让查询基本不用叠加 delta 读取。两个条件是 OR 关系。若要做到极限，可把两个 ratio 都设为 `0`：只要有 delta 就重写 base，查询完全不需要叠加 delta，相当于 copy-on-write，写放大最大，只适合更新量小但对查询延迟极敏感的表。
> - 代价：base 被频繁重写，**写放大明显高于 7.6 的常规取值**（0.3 / 0.5），也会占用更多 compaction 资源。高频更新表要同时结合 7.4 / 7.7 控制与写入的冲突窗口；若写放大不可接受，退回 7.6 的常规取值。
> - 前提：`cz.compaction.server.enable.minor.compaction` 保持默认 `true`。
>
> appendOnly 表没有 delta，只用上面前两个参数即可。

#### 7.3 IGS Upsert 表（一定是更新表）

**IGS 表不需要配置 `cz.compaction.strategy`**，保持默认 `background`。分区表、非分区表都一样，7.4 / 7.7 的 DML 模式只适用于 SQL 维护的表。
> - **不要配 `dml`**：IGS 表依赖后台 Compaction，strategy 里没有 `background` 时后台 Compaction 不会运行；DML 模式只在 SQL DML 提交后触发，IGS 写入不会触发。结果是写入正常、Compaction 基本不跑，文件和 delta 一直累积，查询越来越慢。
> - **也不要为 IGS 配 `dml|background`**：strategy 含 `dml` 时系统会自动补 `ignore.hot.data.window=3600`。非分区 IGS 表持续写入，整表一直被判为热表，后台 Compaction 会一直被跳过。
> - 如果表上已经配置了 strategy（如误配 `dml` / `dml|background`），建议 unset：`ALTER TABLE ${tableName} UNSET PROPERTIES('cz.compaction.strategy')`。
> - 例外：表同时有 IGS 写入和 SQL DML（如 MERGE INTO）时，需要 DML 模式就配 `dml|background`，非分区表要同时显式配 `'cz.compaction.ignore.hot.data.window' = '0'`，避免一直被判为热表。

#### 7.4 SQL 维护的表

**更新表 / 高频更新**需要开启 DML 模式，保证 DML 更新后跟随一次 Compaction。只需配置 strategy 一个参数：

```sql
ALTER TABLE ${tableName} SET PROPERTIES ('cz.compaction.strategy' = 'dml|background');
```
> - `cz.compaction.strategy='dml|background'`：DML 同步 Compaction + 后台 Compaction 同时开启。
> - **自动补默认值**：strategy 含 `dml`（`dml` 或 `dml|background`）时，若表上未显式设置，系统会自动配置：
>   - `cz.compaction.min.interval=3600`：同一张表两次 Compaction 最小间隔 1h，防止 compaction 风暴；
>   - `cz.compaction.ignore.hot.data.window=3600`：跳过最近 1h 内改动的数据，避开与活跃写入的冲突。
> - 自动补的值不会写回表属性，`SHOW CREATE TABLE` 里看不到。
> - **不要再额外建议** `min.interval` / `ignore.hot.data.window`；只有当用户明确需要偏离 1h 默认（如希望更频繁合并或更短热数据窗口）时才显式设置，显式值优先于自动默认。
> - **不要配置已废弃的 `cz.compaction.server.ignore.latest.partition.window`**：表上设置了它，系统就不再自动补 `ignore.hot.data.window`。若表上已存在，建议删除（`ALTER TABLE ${tableName} UNSET PROPERTIES('cz.compaction.server.ignore.latest.partition.window')`）。

**appendOnly 表**无需 DML 模式，保持默认或按 7.2 / 7.5 调整。

> 以上针对**分区表**。**非分区表**的 strategy 配置见 7.7。

#### 7.5 需要更大的文件

若明确希望文件比系统自动推荐的 `cz.table.advised.file.size` 更大，手动配置目标文件大小（大表成本优先常用）：

```sql
ALTER TABLE ${tableName} SET PROPERTIES ('cz.table.target.file.size' = '268435456');
```
> **单位必须是纯字节数（bytes），线上版本不支持带单位写法**（不要写 `256MB` / `1GB`）。例如 256MB = `268435456`、128MB = `134217728`、64MB = `67108864`。0 = 用系统默认（约 128MB）。仅在特殊场景显式设置：大表调大、小表调小。

#### 7.6 频繁更新表：压制 delta 文件个数，保证查询效率

适用于**更新表 / 高频更新表**（UPSERT/DELETE/UPDATE/MERGE/UPLOAD）。每次更新会在 base file 上追加一个 delta（position-delete）文件，delta 累积过多会让查询在读取时叠加大量 delta，拖慢 tableScan。可以从两个方向压制单个 file slice 上的 delta 数量：

**方向一：更积极地把 base+delta 合并成新的 base（major compaction）**

降低 delta overhead 阈值，让 delta 更早触发一次 base 重写：

```sql
ALTER TABLE ${tableName} SET PROPERTIES (
  'cz.compaction.server.delta.overhead.ratio' = '0.3',
  'cz.compaction.server.delta.size.overhead.ratio' = '0.5'
);
```
> - `delta.overhead.ratio` 默认 `0.5`：当「被修改 cell 数 / base 总 cell 数」超过该比例时触发 base+delta 合并。调小（如 0.3）→ 更少的更新量就触发合并，delta 更快被吸收进 base。
> - `delta.size.overhead.ratio` 默认 `1.0`：当「delta 总大小 / base 大小」超过该比例时触发合并。调小（如 0.5）→ delta 体积达到 base 的一半就合并。
> - 两个条件是 **OR** 关系，任一满足即触发。调小两者都会更激进地合并、减少 delta 堆积，代价是**写放大增大**（base 被更频繁重写）。

**方向二：单纯用 minor compaction 阈值压制 delta 个数**

minor compaction 只合并 delta 文件本身、不重写 base，代价比方向一小。降低触发阈值即可更早清理 delta：

```sql
ALTER TABLE ${tableName} SET PROPERTIES ('cz.compaction.server.delta.count.threshold' = '2');
```
> `delta.count.threshold` 默认 `3`：单个 file slice 上的 position-delete delta 个数达到该值时触发 minor compaction。调小到 `2` → 攒到 2 个 delta 就合并，把单 slice 的 delta 个数长期压在很低的水位。
>
> 前提：minor compaction 需保持开启（`cz.compaction.server.enable.minor.compaction`，默认 `true`）。若被显式关成 false，本方向不生效，需要先打开。

**如何选择**：优先用方向二（minor，写放大小）压 delta 个数；若查询变慢主要是因为 base 里已经积累了大量被删/被改的「空洞」（更新量大、archive 场景），再叠加方向一让 base 更早重写。两者可同时设置。高频更新表还应结合 7.4 / 7.7 控制与写入的冲突窗口。

#### 7.7 非分区表

非分区表（`SHOW CREATE TABLE` 中没有 `PARTITIONED BY`）整张表就是一个合并范围，后台 Compaction 和写入更容易冲突，按写入 pattern（Step 5）选择：

**1. 无更新表（appendOnly）**：不需要额外配置，保持默认即可。

**2. 有更新的表**：

```sql
ALTER TABLE ${tableName} SET PROPERTIES ('cz.compaction.strategy' = 'dml|background');
```
> - `dml|background`：DML 提交后跟一次 Compaction，同时保留后台 Compaction。
> - 系统自动补 `min.interval=3600`（同表两次 Compaction 至少间隔 1h）和 `ignore.hot.data.window=3600`（表在 1h 内有改动时跳过后台 Compaction，DML 触发的 Compaction 不受影响），不需要手动配置，同 7.4。

**3. 高频更新且需要严格避免冲突的表**：

```sql
ALTER TABLE ${tableName} SET PROPERTIES ('cz.compaction.strategy' = 'dml');
```
> - `strategy='dml'`：**关闭后台 Compaction**，只在 DML 提交后由该 DML 作业自己触发 Compaction，不会有独立的后台 job 和写入并发抢同一张表。
> - 系统自动补 `min.interval=3600`：DML 触发的 Compaction 也受该间隔限制，1h 内最多合并一次，避免每次高频 DML 都跟一次 Compaction。
> - 代价：完全依赖 DML 触发。表长时间没有新的 DML 时不会再合并；如果最后一批写入落在 1h 间隔内被跳过，这批小文件 / delta 会一直留到下一次 DML。要向用户说明这一点。

## 输出建议

- 用中文输出。先给**现状结论**（文件数/文件大小是否异常、是否处于 Compaction 周期间隙），再给**推荐参数**。
- 参数以可直接执行的 `ALTER TABLE ${tableName} SET PROPERTIES(...)` 形式给出，交由用户自行执行；本 skill 不代跑。
- 已在 `SHOW CREATE TABLE` 里存在的参数不要重复建议；如需改值要说明「从 X 改为 Y」。
- 涉及写放大 / 冲突的取舍要显式提示用户。
- 若判断为「Compaction 周期间隙的正常增长」，明确告知这不是故障，避免误改参数。

## 参数速查

| 参数 | 默认 | 作用 |
| --- | --- | --- |
| `cz.compaction.server.min.file.count` | 5 | 触发 Compaction 的最小文件数（按 partition/bucket） |
| `cz.compaction.server.force.file.count` | 64 | 累积到该文件数强制合并 |
| `cz.compaction.server.delta.overhead.ratio` | 0.5 | 被修改 cell / base 总 cell 超过该比例触发 base+delta 合并；调小更激进 |
| `cz.compaction.server.delta.size.overhead.ratio` | 1.0 | delta 总大小 / base 大小超过该比例触发合并；调小更激进 |
| `cz.compaction.server.delta.count.threshold` | 3 | 单 file slice 上 delta 个数达到该值触发 minor compaction；调小压制 delta 个数 |
| `cz.compaction.server.enable.minor.compaction` | true | 是否开启 minor（delta）compaction，关闭则 delta.count.threshold 不生效 |
| `cz.compaction.strategy` | background | background/dml/`background\|dml`/disabled |
| `cz.compaction.min.interval` | 0（strategy 含 dml 时自动为 3600） | 同表两次 Compaction 最小间隔（秒），0=不限制 |
| `cz.compaction.ignore.hot.data.window` | 0（strategy 含 dml 时自动为 3600） | 跳过最近该窗口（秒）内改动的数据 |
| `cz.compaction.server.ignore.latest.partition.window` | 0 | 已废弃，不要配置；设置后系统不再自动补 `ignore.hot.data.window` |
| `cz.table.target.file.size` | 0（默认约128MB） | 目标文件大小，纯 bytes（线上不支持带单位） |
| `cz.table.advised.file.size` | 系统按分区均值推算 | 文件大小软建议值 |
| `cz.streaming.table` | false | true=IGS 实时写入的流式表（PK 表判定依据） |
