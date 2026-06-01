# clickzetta-skills

[ClickZetta Lakehouse / 云器 Lakehouse](https://www.yunqi.tech) 的 AI Agent Skills 集合，适用于 Codex、Claude Code、czcode 以及其他支持 Skills 机制的 AI 编程助手。

这些 skills 将 ClickZetta 的 SQL 语法、Studio 任务、数据同步、动态表、权限、运维、SDK、BI 集成等经验沉淀为可复用的工作流，帮助 AI 助手在具体场景中自动选择正确文档、命令、SQL 和排查路径。

## Skills 总览

当前仓库包含 31 个顶层 `clickzetta-*` skills，另有官方文档知识库 `lakehouse-doc-en`：

| 类别 | Skill | 适用场景 |
|---|---|---|
| 官方文档 | [lakehouse-doc-en](./lakehouse-doc-en/) | Singdata Lakehouse 官方文档知识库：SQL、函数、权限、VCluster、数据共享、SDK、BI、AI 函数等 |
| 基础与连接 | [clickzetta-overview](./clickzetta-overview/) | ClickZetta 产品全貌、对象模型、架构、Studio 模块、品牌与服务地址 |
| 基础与连接 | [clickzetta-lakehouse-connect](./clickzetta-lakehouse-connect/) | Python SDK、ZettaPark、SQLAlchemy、JDBC 等连接配置 |
| 基础与连接 | [clickzetta-sql-migration](./clickzetta-sql-migration/) | 从 Snowflake / Databricks / Spark SQL 迁移到 ClickZetta 的语法差异、函数对照、隐式转换规则 |
| 基础与连接 | [clickzetta-metadata](./clickzetta-metadata/) | SHOW/DESC 命令族、INFORMATION_SCHEMA 元数据、费用和用量统计 |
| 数据导入与管道 | [clickzetta-data-ingest-pipeline](./clickzetta-data-ingest-pipeline/) | 数据导入方案路由，根据数据源、实时性、范围选择最佳导入方式 |
| 数据导入与管道 | [clickzetta-file-import-pipeline](./clickzetta-file-import-pipeline/) | URL、本地文件、Volume 文件导入，格式推断、建表、COPY INTO |
| 数据导入与管道 | [clickzetta-oss-ingest-pipeline](./clickzetta-oss-ingest-pipeline/) | OSS/S3/COS 对象存储批量导入或 PIPE 持续导入 |
| 数据导入与管道 | [clickzetta-kafka-ingest-pipeline](./clickzetta-kafka-ingest-pipeline/) | Kafka 到 Lakehouse 的 READ_KAFKA Pipe 或外部表接入 |
| 数据导入与管道 | [clickzetta-batch-sync-pipeline](./clickzetta-batch-sync-pipeline/) | Studio 离线同步，支持单表、多表、整库镜像、分库分表合并 |
| 数据导入与管道 | [clickzetta-realtime-sync-pipeline](./clickzetta-realtime-sync-pipeline/) | Studio 单表实时同步，支持 Kafka、MySQL、PostgreSQL 等来源 |
| 数据导入与管道 | [clickzetta-cdc-sync-pipeline](./clickzetta-cdc-sync-pipeline/) | 多表实时 CDC，同步 MySQL/PostgreSQL 整库或多表到 Lakehouse |
| 数据导入与管道 | [clickzetta-sql-pipeline-manager](./clickzetta-sql-pipeline-manager/) | SQL 管道对象管理：Dynamic Table、Materialized View、Table Stream、Pipe |
| 数据导入与管道 | [clickzetta-table-stream-pipeline](./clickzetta-table-stream-pipeline/) | Table Stream 变更捕获、offset 管理、增量 ETL 消费 |
| 数据导入与管道 | [clickzetta-studio-task-manager](./clickzetta-studio-task-manager/) | Studio 任务类型、目录、调度、依赖、cz-cli task 命令族和建管分离规范 |
| 数据导入与管道 | [clickzetta-pipeline-review](./clickzetta-pipeline-review/) | 数据管道 Review、任务/表/运行记录发现、问题诊断与修复建议 |
| 数据导入与管道 | [clickzetta-dbt-studio-pipeline](./clickzetta-dbt-studio-pipeline/) | 将 dbt models 发布为 Studio 资产并配置调度执行 |
| 建模与计算 | [clickzetta-dw-modeling](./clickzetta-dw-modeling/) | 数仓建模、ODS/DWD/DWS/ADS、Medallion 架构、DDL 与管道设计 |
| 建模与计算 | [clickzetta-dbt-project-setup](./clickzetta-dbt-project-setup/) | dbt-clickzetta 项目初始化、profiles.yml、分层规范和项目配置 |
| 建模与计算 | [clickzetta-dbt-modeling](./clickzetta-dbt-modeling/) | dbt-clickzetta 建模向导：sources、models、增量策略和测试 |
| 建模与计算 | [clickzetta-dynamic-table](./clickzetta-dynamic-table/) | Dynamic Table 创建、增量刷新、ALTER、性能优化和最佳实践 |
| 建模与计算 | [clickzetta-query-optimizer](./clickzetta-query-optimizer/) | 慢查询、EXPLAIN、Result Cache、OPTIMIZE、Hints、Sort Key 调优 |
| 建模与计算 | [clickzetta-data-science](./clickzetta-data-science/) | 数据科学工作流：Jupyter、EDA、特征工程、采样、推理、向量检索 |
| 建模与计算 | [clickzetta-semantic-view](./clickzetta-semantic-view/) | Semantic View 语义层、逻辑表、维度、指标、过滤器和查询 |
| SDK 与外部集成 | [clickzetta-zettapark](./clickzetta-zettapark/) | ZettaPark DataFrame API、Session、表读写、文件操作、SQL 执行 |
| SDK 与外部集成 | [clickzetta-spark-flink-connector](./clickzetta-spark-flink-connector/) | Spark Connector 读写、Flink CDC/append-only 写入 |
| SDK 与外部集成 | [clickzetta-ai-function](./clickzetta-ai-function/) | 内置 AI_COMPLETE / AI_EMBEDDING 函数和 AI API Connection |
| SDK 与外部集成 | [clickzetta-external-function](./clickzetta-external-function/) | External Function、Python/Java UDF、AI_COMPLETE、AI_EMBEDDING |
| SDK 与外部集成 | [clickzetta-external-catalog](./clickzetta-external-catalog/) | Hive、Iceberg、Databricks、Snowflake Open Catalog 联邦查询 |
| 运维与治理 | [clickzetta-volume-manager](./clickzetta-volume-manager/) | Volume 创建、OSS/COS/S3 挂载、PUT/GET、文件查询、导入导出 |
| 运维与治理 | [clickzetta-dba-guide](./clickzetta-dba-guide/) | DBA 运维：集群、作业、恢复、存储优化、Schema/对象、成本分析 |
| 运维与治理 | [clickzetta-table-lineage](./clickzetta-table-lineage/) | 基于 job_history 的表血缘和成本可视化 |

## 路由建议

如果你不确定应该使用哪个 skill，优先从这些入口开始：

| 用户意图 | 推荐入口 |
|---|---|
| 了解 ClickZetta、Workspace/Schema/VCluster、Studio 能力 | `clickzetta-overview` |
| 配置连接、写 Python/JDBC/SQLAlchemy/ZettaPark 连接代码 | `clickzetta-lakehouse-connect` |
| 不确定如何把数据导入 Lakehouse | `clickzetta-data-ingest-pipeline` |
| 从文件、URL、对象存储或 Kafka 导入数据 | `clickzetta-file-import-pipeline` / `clickzetta-oss-ingest-pipeline` / `clickzetta-kafka-ingest-pipeline` |
| 做离线同步、实时同步、多表 CDC | `clickzetta-batch-sync-pipeline` / `clickzetta-realtime-sync-pipeline` / `clickzetta-cdc-sync-pipeline` |
| 管理 Studio 任务、调度、依赖、补数、任务目录 | `clickzetta-studio-task-manager` |
| 初始化 dbt 项目、写 dbt model、发布 dbt 调度 | `clickzetta-dbt-project-setup` / `clickzetta-dbt-modeling` / `clickzetta-dbt-studio-pipeline` |
| 设计数据管道、动态表、流式增量 ETL | `clickzetta-sql-pipeline-manager` / `clickzetta-dynamic-table` / `clickzetta-table-stream-pipeline` |
| 诊断管道质量、任务失败、链路缺陷 | `clickzetta-pipeline-review` |
| 写 ClickZetta 原生 SQL、查函数或语法 | `lakehouse-doc-en` |
| 从 Snowflake / Databricks / Spark SQL 迁移 | `clickzetta-sql-migration` |
| 查询元数据、表结构、作业历史、成本归因 | `clickzetta-metadata` / `clickzetta-dba-guide` |
| 查询慢、作业慢、小文件、缓存、执行计划 | `clickzetta-query-optimizer` |
| 用户、角色、授权、脱敏、网络策略 | `lakehouse-doc-en` |
| 集群、恢复、生命周期、数据共享 | `clickzetta-dba-guide` / `lakehouse-doc-en` |
| Volume、对象存储挂载、文件导入导出 | `clickzetta-volume-manager` |
| Python、Java、JDBC、SQLAlchemy、BI 工具连接 | `lakehouse-doc-en` / `clickzetta-lakehouse-connect` / `clickzetta-zettapark` |
| Spark、Flink 写入 Lakehouse | `clickzetta-spark-flink-connector` |
| AI_COMPLETE、AI_EMBEDDING、External Function | `clickzetta-ai-function` / `clickzetta-external-function` |

## Skills 列表

### 官方文档

#### [lakehouse-doc-en](./lakehouse-doc-en/)

Singdata Lakehouse 官方文档知识库，按用户问题在 `references/` 下定位对应官方文档。覆盖 SQL 语法、内置函数、权限、VCluster、数据共享、Time Travel、SDK、BI、AI 函数等已经从专项 skill 收敛到官方文档的知识。

适用于原生语法查询、已删除专项 skill 的知识兜底，以及需要以官方文档为准的问答。

### 基础与连接

#### [clickzetta-overview](./clickzetta-overview/)

ClickZetta Lakehouse 产品全貌入口，帮助新用户建立对象模型和平台能力的整体认知。覆盖账户、实例、Workspace、Schema、表等对象层级，解释 Workspace 与 Database/Catalog 的对应关系、VCluster 类型与 CRU 计费、存算分离架构、权限体系，以及 ClickZetta / 云器 / Singdata 的品牌关系和服务地址。

也包含 Studio 六大模块介绍：数据开发 IDE、任务调度、数据集成、数据目录、数据质量和运维监控。适合回答“ClickZetta 是什么”“Workspace 和 Schema 什么关系”“Studio 有哪些功能”“和 Snowflake/Databricks 有什么差异”等问题。

#### [clickzetta-lakehouse-connect](./clickzetta-lakehouse-connect/)

连接 ClickZetta Lakehouse 的完整指南，覆盖 Python SDK、ZettaPark Session、SQLAlchemy 和 JDBC 四类连接方式。适用于外部应用、Notebook、BI 工具、Java 程序或自动化脚本需要连接 Lakehouse 的场景。

Skill 内包含本地配置文件读取、连接参数说明、国内版与国际版服务地址差异、常见连接报错排查，以及 JDBC/SQLAlchemy/Python/ZettaPark 的参考示例。

#### [clickzetta-sql-migration](./clickzetta-sql-migration/)

ClickZetta Lakehouse SQL 迁移指南，专注于从 Snowflake、Databricks、Spark SQL 迁移到 ClickZetta 时的语法差异、函数对照、隐式类型转换规则。原生 ClickZetta SQL 语法请参考 ClickZetta Lakehouse 官方文档。

适用于查询“ClickZetta 怎么写某个 SQL”“Snowflake/Databricks 语法怎么迁移”“日期/JSON/BOOLEAN/集合运算怎么写”“某个函数是否支持”等问题。

#### [clickzetta-metadata](./clickzetta-metadata/)

ClickZetta 元数据查询入口，统一覆盖 SHOW/DESC 命令族和 INFORMATION_SCHEMA 视图。SHOW/DESC 适合实时查看单个对象状态，INFORMATION_SCHEMA 适合跨对象统计、作业分析、权限审计、费用归因和用量分析。

适用于查看表列表、字段、分区、权限、Volume、作业历史、对象成本、工作空间级或实例级元数据等只读场景。权限变更和授权操作请参考 `lakehouse-doc-en` 官方文档。

### 数据导入与管道

#### [clickzetta-data-ingest-pipeline](./clickzetta-data-ingest-pipeline/)

数据导入总览与路由入口。根据数据源类型、实时性要求、同步范围、是否 CDC、是否持续导入等信息，推荐最合适的导入方式，并引导到对应专项 skill。

常见路由包括：文件/URL 导入走 `clickzetta-file-import-pipeline`，对象存储走 `clickzetta-oss-ingest-pipeline`，Kafka 走 `clickzetta-kafka-ingest-pipeline`，离线同步走 `clickzetta-batch-sync-pipeline`，单表实时同步走 `clickzetta-realtime-sync-pipeline`，多表 CDC 走 `clickzetta-cdc-sync-pipeline`。

#### [clickzetta-file-import-pipeline](./clickzetta-file-import-pipeline/)

从 URL、本地文件或 Volume 路径将数据导入 ClickZetta 表。覆盖文件下载、格式推断、目标表创建、COPY INTO 导入、结果验证等完整流程。

包含 USER VOLUME 机制、CSV/JSON/Parquet/ORC/BSON 等格式处理、create/append/overwrite 写入模式、COPY INTO 和 COPY OVERWRITE INTO 的 ClickZetta 特有语法。

#### [clickzetta-oss-ingest-pipeline](./clickzetta-oss-ingest-pipeline/)

搭建 OSS/S3/COS 对象存储数据导入管道，覆盖持续导入和批量导入两类场景。持续导入支持 LIST_PURGE 扫描模式和 EVENT_NOTIFICATION 消息通知模式；批量导入支持 Volume + INSERT INTO 和 Volume + COPY INTO。

完整流程包括 Storage Connection、External Volume、PIPE/COPY INTO 创建、监控与运维，适合对象存储文件持续到达或一次性批量入仓。

#### [clickzetta-kafka-ingest-pipeline](./clickzetta-kafka-ingest-pipeline/)

Kafka 数据接入管道工作流，覆盖连接验证、数据探查、目标表创建、JSON 多层嵌套解析和 Pipe 持续导入。支持 READ_KAFKA Pipe（推荐）以及 Kafka 外部表 + Table Stream Pipe 两种路径。

包含 SASL 认证配置、消费位点管理、Pipe 重建、BATCH_SIZE/COPY_JOB_HINT/VCluster 生产调优，以及 Kafka 延迟和积压监控。

#### [clickzetta-batch-sync-pipeline](./clickzetta-batch-sync-pipeline/)

创建和管理 Studio 离线同步（批量同步）任务，支持单表离线同步和多表离线同步。单表模式适合简单源表到目标表的周期性同步；多表模式支持整库镜像、多表镜像和分库分表合并。

覆盖数据源配置、字段映射、同步规则、目标表策略、Cron 调度、Sync VCluster 分配、任务提交和运维。适合 MySQL、PostgreSQL、SQL Server、Aurora、PolarDB 等数据库定期同步到 Lakehouse。

#### [clickzetta-realtime-sync-pipeline](./clickzetta-realtime-sync-pipeline/)

创建和管理 Studio 单表实时同步任务，将 Kafka、MySQL、PostgreSQL 等外部数据源实时同步到 Lakehouse。实时同步任务是持续运行的流式任务，提交后持续运行，不需要配置周期调度。

覆盖数据源配置、字段映射、Kafka JSONPath 计算列、Sync VCluster 使用、部署和运维排查。

#### [clickzetta-cdc-sync-pipeline](./clickzetta-cdc-sync-pipeline/)

创建和管理 Studio 多表实时同步（CDC）任务，将 MySQL 或 PostgreSQL 整库、多表或分库分表实时同步到 Lakehouse。支持整库镜像、多表镜像、多表合并三种模式，基于 MySQL Binlog 或 PostgreSQL WALs 实现全量 + 增量同步。

包含源端数据库准备、权限检查、任务创建部署、补全量、加表、数据修复、优先同步、同步告警和常见故障排查，如 Binlog 位点过期、server-id 冲突等。

#### [clickzetta-sql-pipeline-manager](./clickzetta-sql-pipeline-manager/)

通过 SQL 管理 Lakehouse 数据管道对象，不涉及 Studio 图形化界面。覆盖 Dynamic Table、Materialized View、Table Stream、Pipe 的创建、修改、暂停/恢复、删除、状态查看和故障排查。

也可作为端到端 Pipeline Wizard 使用，根据 Kafka、对象存储、已有表或 Table Stream 源生成 Bronze/Silver/Gold、ODS/DWD/DWS 等分层管道 SQL。

#### [clickzetta-table-stream-pipeline](./clickzetta-table-stream-pipeline/)

搭建和管理 Table Stream 变更数据捕获管道。覆盖源表开启 change_tracking、创建 Stream、选择 STANDARD 或 APPEND_ONLY 模式、预览变更、消费 Stream、移动 offset、幂等写入目标表等步骤。

适合构建基于表变更的增量 ETL、审计记录、CDC 消费和下游数据同步。

#### [clickzetta-studio-task-manager](./clickzetta-studio-task-manager/)

管理 ClickZetta Lakehouse Studio 任务，覆盖任务类型、任务目录、任务内容、调度配置、依赖管理、任务状态和常见问题排查。

强调“建管分离”工程规范：DDL 任务草稿化、ETL 任务调度化、Dynamic Table 自动刷新化。适合创建 Studio 任务、管理任务目录、配置调度 DAG、区分离线同步/实时同步/多表 CDC/数据开发任务等场景。

#### [clickzetta-pipeline-review](./clickzetta-pipeline-review/)

数据管道 Review 与诊断工作流。从任务名、schema、表名、业务域关键词或错误信息出发，自主发现 Studio 任务、Lakehouse 表、管道对象和运行记录，形成管道全貌。

重点识别调度依赖缺失、DDL 幂等问题、分层跳层、Dynamic Table 反模式、任务失败、数据不一致等问题，并按优先级给出修复建议。

#### [clickzetta-dbt-studio-pipeline](./clickzetta-dbt-studio-pipeline/)

将 dbt models 发布到 Studio 进行统一代码管理，并为需要周期执行的 models 配置调度。读取 dbt `manifest.json`，将 SQL 重写为适配 Studio 调度参数的任务资产。

适合把 dbt 项目纳入 Studio 资产、调度、依赖、重试策略和运维体系。

### 建模与计算

#### [clickzetta-dw-modeling](./clickzetta-dw-modeling/)

ClickZetta Lakehouse 数仓建模向导。支持传统 ODS/DWD/DWS/ADS 分层、Medallion Bronze/Silver/Gold 架构和混合模式，强调数据管道与建模一体化设计。

适合设计事实表、维度表、宽表、星型/雪花模型、分层 schema、端到端数据流转。核心原则是聚合计算层优先使用 Dynamic Table，不推荐物化视图承载主链路计算。

#### [clickzetta-dbt-project-setup](./clickzetta-dbt-project-setup/)

dbt-clickzetta 项目初始化向导，覆盖安装检查、`profiles.yml` 连接配置、分层规范、`dbt_project.yml` 生成和端到端 ELT 标准。

适合从零创建 dbt 项目、配置 dbt-clickzetta adapter、建立 ODS/DWD/DWS/ADS 或 Bronze/Silver/Gold 分层。

#### [clickzetta-dbt-modeling](./clickzetta-dbt-modeling/)

dbt-clickzetta 建模向导，会先探索 Lakehouse 数据源，再推导建模策略，生成 `sources.yml`、model SQL 和测试配置。

适合把原始表转成可分析的数据集、构建事实表/维度表、设计增量模型、补齐 dbt tests。

#### [clickzetta-dynamic-table](./clickzetta-dynamic-table/)

Dynamic Table 使用指南，覆盖动态表创建、刷新配置、增量计算、ALTER 操作、刷新历史、性能优化和最佳实践。包含静态分区 DT、动态分区 DT、维度表 JOIN、状态表、MERGE INTO、非分区表风险等内容。

目录下还包含子目录：`dt-creator` 用于创建动态表，`sql-to-dt` 用于 SQL 转动态表，`best-practices` 用于最佳实践和性能调优。

#### [clickzetta-query-optimizer](./clickzetta-query-optimizer/)

ClickZetta SQL 性能诊断和优化工作流。覆盖慢查询排查、EXPLAIN 执行计划分析、SHOW JOBS / job_history 作业定位、Result Cache、小文件合并、Map Join、Sort Key 和 Hint 调优。

适用于“查询慢”“作业耗时高”“小文件太多”“执行计划怎么看”“缓存没命中”等性能问题。

#### [clickzetta-data-science](./clickzetta-data-science/)

面向数据科学家的端到端工作流指南。覆盖 Python 环境、Jupyter Notebook、项目结构、数据发现、质量评估、采样、EDA、特征工程、模型推理上线和向量检索。

强调 SQL + ZettaPark 结合使用，适合 Notebook 连接 Lakehouse、pandas 读取、统计函数、BITMAP 用户画像、人群圈选、批量推理等场景。

#### [clickzetta-semantic-view](./clickzetta-semantic-view/)

语义视图（Semantic View）创建和查询指南。Semantic View 是 schema 级逻辑数据模型对象，可声明逻辑表、维度、指标、过滤器，将复杂 JOIN 和聚合封装为业务友好的语义层。

适合统一指标口径、构建业务语义模型、通过 `semantic_view()` 函数查询语义层数据。当前为邀测功能。

### SDK 与外部集成

#### [clickzetta-zettapark](./clickzetta-zettapark/)

ZettaPark Python DataFrame API 使用指南。ZettaPark 提供类 pandas 的开发体验，将 DataFrame 操作翻译为 SQL 在 Lakehouse 中分布式执行。

覆盖 Session 创建、DataFrame 读取、filter/select/join/groupBy、collect/to_pandas/show、save_as_table、PUT/GET 文件操作和 SQL 执行。

#### [clickzetta-spark-flink-connector](./clickzetta-spark-flink-connector/)

Spark Connector 和 Flink Write Connector 集成指南。覆盖 Spark DataFrame 读写配置、Maven 依赖、连接参数、Flink Table API 写入、CDC 模式 `igs-dynamic-table`、append-only 模式、checkpoint 和 flush 调优。

适合 Spark/Flink 作业写入 Lakehouse，尤其是 Flink CDC 主键表写入和 append-only 流式写入。

#### [clickzetta-ai-function](./clickzetta-ai-function/)

AI 函数指南，覆盖 `AI_COMPLETE`、`AI_EMBEDDING`、AI API Connection、模型调用参数、文本生成和向量化等场景。

适合在 SQL 中直接调用 LLM、生成 embeddings、做文本处理或构建向量检索前置数据。

#### [clickzetta-external-function](./clickzetta-external-function/)

外部函数和 AI 函数指南。覆盖 API Connection、External Function、Python/Java UDF 代码结构与打包、阿里云函数计算、腾讯云 SCF、AWS Lambda 等外部服务调用。

也包含内置 `AI_COMPLETE` 和 `AI_EMBEDDING` 函数的使用，适合 LLM 调用、文本向量化、图像识别和自定义算法扩展 SQL 计算能力。

#### [clickzetta-external-catalog](./clickzetta-external-catalog/)

External Catalog 联邦查询指南，支持 Hive、Iceberg、Databricks Unity Catalog、Snowflake Open Catalog 等外部数据目录的只读查询。

完整流程包括 Storage Connection、Catalog Connection、External Catalog 创建，以及 SHOW/DESC/查询外部表操作。适合不迁移数据直接访问外部湖仓数据。

### 运维与治理

#### [clickzetta-volume-manager](./clickzetta-volume-manager/)

Volume 对象管理指南，覆盖外部 Volume、User Volume、Table Volume。支持 OSS/COS/S3 挂载、PUT/GET/REMOVE 文件操作、SELECT FROM VOLUME 查询文件、COPY INTO TABLE 导入和 COPY INTO VOLUME 导出。

适合对象存储挂载、临时文件上传、本地文件导入、数据导出、CSV/Parquet 导出等场景。

#### [clickzetta-dba-guide](./clickzetta-dba-guide/)

DBA 日常运维手册，集中覆盖计算集群运维、作业监控与诊断、数据恢复与保护、存储优化、Schema 与对象管理、成本和资源分析。

提供可直接执行的 SQL，并标注 ClickZetta 特有限制。安全治理类操作请参考 `lakehouse-doc-en` 官方文档。

#### [clickzetta-table-lineage](./clickzetta-table-lineage/)

表血缘可视化工具。基于 `information_schema.job_history` 获取表依赖关系和成本数据，导出 CSV 后嵌入 HTML 模板生成交互式血缘图。

支持表依赖图、上下游分析、数据流向分析、DML CRU/day 和累计成本查看，适合 pipeline 可视化和管道全貌分析。

## Skill 结构

每个 skill 目录通常包含：

```text
clickzetta-xxx/
├── SKILL.md              # 触发条件、工作流、关键语法和执行步骤
├── references/           # 细分参考文档、SQL 片段、API 说明或模板
└── evals/                # 可选，结构化评测数据
```

少数 skill 还包含子 skill 或最佳实践文档，例如 `clickzetta-dynamic-table/dt-creator/`、`clickzetta-dynamic-table/sql-to-dt/` 和 `clickzetta-dynamic-table/best-practices/`。

## 使用方式

将本仓库中的 skill 目录放到 AI 编程助手可识别的 skills 路径下，或在支持插件/技能仓库的环境中直接加载本仓库。使用时直接描述你的 ClickZetta 任务即可，例如：

```text
帮我把 OSS 上的 CSV 持续导入到 public.orders
```

```text
这个动态表刷新很慢，帮我看执行计划并给出优化建议
```

```text
给 analyst 用户授予 ods schema 下所有表的只读权限
```

AI 助手会根据 `SKILL.md` 中的 `description`、触发词和工作流选择对应 skill，并按其中的步骤读取必要参考文档。
