---
name: lakehouse-doc-en
description: "Singdata Lakehouse official documentation knowledge base (English). Consult references/ when writing SQL or answering questions about query syntax, functions, data types, DDL/DML, dynamic tables, permissions, vclusters, data lake, AI functions, and other Lakehouse topics."
---

# lakehouse-doc-en

Singdata Lakehouse official documentation (English). Locate docs by filename under `references/` based on the user's question.

## references/ layout

```
references/
├── *.md                          # Main topic docs (named by topic, see index below)
├── eco_integration/              # Ecosystem integrations
│   ├── dbt.md, superset.md, datagrip-lakehouse.md, trino.md ...
├── java_reference/               # Java SDK
│   ├── java-sdk-summary.md, jdbc.md, realtime-upload.md, client.md ...
├── python_reference/             # Python SDK
│   ├── connector.md, sqlalchemy.md, python-sdk-summary.md
├── opensource/                   # Open-source tools
│   └── travel.md
├── aggregate_functions/          # Top-level aggregate function docs
└── sql_functions/                # SQL function reference
    ├── aggregate_functions/      # count.md, sum.md, avg.md ...
    ├── window_functions/         # row_number.md, rank.md, lag.md ...
    ├── table_functions/          # table_changes.md ...
    ├── context_functions/        # current_user.md ...
    └── scalar_functions/
        ├── datetime_functions/   # date/time
        ├── string_functions/     # string
        ├── math_functions/       # numeric
        ├── nested_functions/     # array/map/struct
        ├── bitmap_functions/     # bitmap
        ├── json_functions/       # JSON
        ├── conditional_functions/# conditional
        ├── high_order_functions/ # high-order
        ├── vector_functions/     # vector
        ├── ip_functions/         # IP
        ├── search_functions/     # search
        ├── hash_functions/       # hash
        ├── geo_functions/        # geo
        ├── bitwise_functions/    # bitwise
        ├── file_functions/       # file
        └── partition/            # partition
```

## Document Index (llms.txt)

# Singdata Lakehouse Documentation (LLM Navigation)

> Singdata Lakehouse is a fully managed lakehouse architecture platform built from the ground up on cloud-native design principles. Through **storage-compute separation**, **Serverless elastic architecture**, **open storage formats**, and **AI-optimized tools**, it provides enterprises with a unified platform for data warehousing, data lakes, real-time processing, and BI reporting. [Free Trial](https://www.singdata.com)


## Quick Start

- [Overview](references/overview.md): Top-level Singdata Lakehouse overview introducing the incremental computation engine, lake acceleration, AI infrastructure, and role-based navigation paths for engineers, analysts, admins, and AI agents.
- [Concept Index](references/concepts.md): Product introduction to Singdata Lakehouse covering its vectorized engine, Generic Incremental Computation, AI Lakehouse vision, Iceberg storage, and serving humans, apps, and AI Agents.
- [Tutorials](references/tutorials.md): A role-based getting-started guide offering onboarding paths for data engineers and data analysts, covering data ingestion, processing pipelines, SQL queries, and tool connections.

## User Guide

- [Object Model](references/object_model_design.md): Comprehensive overview of the Lakehouse object model, describing the Instance/Workspace/Schema hierarchy and categorizing objects: catalogs, tables, volumes, connections, pipes, streams, indexes, partitions, functions, and synonyms.
- [Manage Compute Resources](references/tutorial_virtual_cluster.md): Managing compute resources (VClusters), covering the three cluster types General, Analytical, and Integration, their elasticity models, and common operations like viewing, switching, and starting clusters.
- [Lakehouse Studio](references/studio_manual.md): An overview of Studio, the serverless web console and data services platform for Lakehouse, covering its AI-driven Data Agent and six core modules including data sync, task development, scheduling, and SQL query.
- [Data Ingestion](references/Ingestion.md): Decision-oriented overview of Singdata Lakehouse data ingestion, routing relational database, file, Kafka, custom/programmatic, and warehouse-migration scenarios to the appropriate Studio sync, Pipe, COPY INTO, or SDK approach.
- [Data Transformation via SQL](references/sql_data_transform.md): Navigation guide for data transformation patterns, helping choose between Dynamic Tables, Studio scheduled ETL, Table Stream CDC, and Materialized Views by latency and trigger needs.
- [Data Analysis and SQL Guide](references/Analysis.md): A scenario-based navigation guide to Singdata Lakehouse analytics capabilities, covering SQL querying, BI tool connectivity, data lake file analysis, federated queries, AI-powered analysis, and query performance optimization.
- [Federation Query](references/federation-query.md): Overview of Federation Query for querying external systems (Hive, Databricks, Iceberg, Snowflake) directly via standard SQL using EXTERNAL CATALOG, covering supported sources, core concepts, and quick-start examples.
- [Data Lake Management and Analytics](references/datalake_volume_analytics.md): An overview of data lake management via Volume objects, covering internal and external storage, direct querying, import and export, permissions, and a quick selection guide.
- [Developing Custom Functions](references/RemoteFunction-as-udf.md): An overview of developing External (Remote) Functions in Python or Java that run on cloud function services, covering how they work, supported function types, runtime environments, and the creation workflow.
- [Data Sharing](references/data_sharing_guide.md): Navigation guide for zero-copy cross-instance data sharing, organized by provider and consumer roles, covering Studio UI and SQL workflows, required roles, and sharing limitations.
- [Data Governance](references/time_travel_guide.md): An overview of data governance with Time Travel, covering MVCC-based historical version querying, table rollback, dropped-table recovery, and the difference between data_retention_days and data_lifecycle.
- [Security](references/data_security.md): Navigation hub for Lakehouse security covering user permissions, data masking, network access control, audit compliance, identity authentication, and data recovery with task-oriented reference links.
- [INFORMATION SCHEMA](references/information_schema_guide.md): The INFORMATION_SCHEMA metadata query interface, covering instance-level and workspace-level access scopes, comparison with SHOW and DESC, and common metadata and asset inventory queries.
- [Account and Billing](references/management_guide.md): Account and billing management guide covering account information, users and permissions, account funds and top-ups, billing statements, and cost control, noting the administrator roles required for each operation.
- [Connect Using Ecosystem Tools](references/ecosystem-all.md): A guide to connecting Lakehouse with ecosystem tools, covering SQL clients, BI tools, ETL platforms, and programmatic access via JDBC, Python/Java SDKs, and Spark/Flink connectors.
- [Performance Optimization](references/performance_optimization.md): Overview of Lakehouse performance optimization capabilities including result cache, compute cluster cache, small file optimization, sort-column recommendations, and job profiling, with a quick selection guide.
- [Performance Testing](references/benchmark_guide.md): Summary of Singdata Lakehouse performance benchmarks against ClickHouse (SSB), Trino (TPC-H), and Spark SQL (TPC-DS), with comparison results and links to detailed reports.

## AI Guide

- [Lakehouse AI Overview](references/LakehouseAI-overview.md): Overview of Lakehouse AI capabilities, presenting a selection guide and core features: AI Functions, Vector Search, External Functions, Semantic Views, and Zettapark for in-SQL LLM and RAG workflows.
- [AI + BI Unified Workflow](references/unified-workflow.md): Stub landing page titled Unified Workflow, intended as an overview entry point for Lakehouse unified development and orchestration workflow documentation.
- [AI Gateway](references/AIGateway.md): Introduces Singdata AI Gateway, an enterprise service offering unified multi-model API access, intelligent routing, BYOK integration, and per-key usage control, fully compatible with the OpenAI interface format.
- [Conversational Analytics (Analytics Agent)](references/datagpt_introduction.md): Introduction to Analytics Agent (formerly DataGPT), a conversational agentic analysis assistant, covering when to use it, quick start, core concepts of data assets and analysis domains, user roles, and Agentic RAG architecture.
- [Singdata CLI (cz-cli)](references/cz-cli.md): Introduces cz-cli, the Singdata Lakehouse command-line tool, explaining its advantages for AI agents over JDBC/REST/MCP, the orchestrator-subagent pattern, command overview, and quick-start installation and configuration.
- [AI Ecosystem](references/AI_eco.md): Overview of Singdata Lakehouse AI ecosystem integrations including Dify, N8N, LangChain, Unstructured ETL, and Datus, with a quick selection guide for vector storage and RAG scenarios.

## SQL Manual

- [SQL Statements](references/sql-commands.md): Basic commands reference covering object identifiers, comment syntax, session parameters, and general DDL (CREATE, ALTER, DROP, UNDROP, DESC, SHOW) applicable to all object types.
- [Data Types](references/data-type-guide.md): Overview of Lakehouse data types covering numeric, string, time, boolean, binary, and complex types (ARRAY, MAP, STRUCT, JSON, VECTOR, BITMAP), with quick reference tables and chapter links.
- [SQL Functions](references/functions.md): Catalog of Singdata Lakehouse SQL functions organized by category, covering numeric, string, datetime, complex types, aggregation, window, AI functions, vector, BITMAP, and system functions.

## Development Manual

- [Java SDK](references/java_sdk_guide.md): Overview of the clickzetta-java SDK providing JDBC queries, real-time streaming writes, and high-throughput Bulkload, with a contents table and comparison of the three write methods and their use cases.
- [Python SDK (SQL Interface)](references/python_sdk_guide.md): Overview of the clickzetta-connector Python SDK, covering its four integration methods (Database API, SQLAlchemy, Bulkload, and real-time writes) with a comparison of use cases and links to detailed references.
- [ZettaPark (DataFrame API)](references/LakehousePython-zettapark.md): Overview of ZettaPark, the pandas/PySpark-style Python DataFrame API that lazily translates operations into SQL for distributed execution on Lakehouse, with links to quick start, ETL, and feature engineering guides.

## Practice Tutorials

- [Efficient Object and Data Organization Management](references/data_org.md):
- [Data Import and Export Practice](references/practice_data_import_and_export.md): An empty placeholder page with no substantive content.
- [Data Lake Acceleration](references/datalake-acceleration.md): Brief overview of in-place data lake acceleration, connecting directly to an existing Hive Metastore and object storage via External Schema to replace Spark/Hive ETL and Presto/Trino queries with Serverless compute.
- [Migration Guide](references/tutorial_migration.md): Migration guide hub mapping source systems (Databricks/PySpark, RDD, Spark SQL, Snowflake, Medallion) to recommended Lakehouse migration paths with links and path-selection advice.
- [Data Query and Analysis Practice](references/practice_data_analysis.md): Empty placeholder page containing only a content marker symbol, with no data analysis practice content, examples, or guidance currently present in the file body.
- [Building and Maintaining ELT Processes](references/ELT_practice.md): Placeholder page for ELT practice in Singdata Lakehouse; currently empty with no substantive content.
- [Optimize Computing Resources](references/optimizing-computing-resources.md): Placeholder page for optimizing computing resources in Singdata Lakehouse; currently empty with no substantive content.
- [Performance Experience](references/performence_test.md): Empty placeholder page intended for performance testing content; no substantive material is present beyond a content marker.
- [Modern Data Stack with Ecosystem Tools](references/modern-data-stack-with-ecosystem-tools.md):
- [AI Application Development](references/ai_app_dev_practical.md): Brief landing page introducing practical guides for building AI-powered applications on Singdata Lakehouse.
- [Security Compliance Audit](references/security_compliance_audit_dir_guide.md): A brief section header introducing security and compliance audit topics.
- [Cost Management](references/cost_management.md): Stub page titled Cost Management for Singdata Lakehouse, intended to cover billing and cost control topics but currently without content.

## Release Notes

- [Release Notes](references/release-notes.md): A landing page indexing the release notes history for the Singdata Lakehouse platform.

## Other

- [User Agreement](references/service-aggrement.md): The Singdata Service Agreement (effective January 10, 2025), setting legal terms for account registration, service use, member responsibilities, account security, and liability limitations.
- [Privacy Policy](references/privacy-policy.md): Singdata privacy policy (2024.08) detailing collection, use, disclosure, transfer, retention, and destruction of personal data, plus security measures, cookies, and user rights to access or correct data.
- [Product Trial Agreement](references/product-trial-agreement.md): Legal product trial agreement for Singdata, covering service description, user responsibilities, company rights, intellectual property, disclaimers, and dispute resolution during the testing phase.