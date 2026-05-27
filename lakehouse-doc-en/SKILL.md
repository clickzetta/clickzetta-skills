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

- [Overview](references/Overview.md): Introduces the storage-compute separation architecture, Serverless computing, open data formats, and key application scenarios of Singdata Lakehouse.
- [Key Concepts](references/Concepts.md): Introduces the storage-compute separation architecture, Serverless computing, open data formats, and key application scenarios of Singdata Lakehouse.
- [Tutorials](references/Tutorials.md): Walks through the complete workflow from data ingestion and SQL querying to data visualization, covering steps from data access to analysis and presentation.

## User Guide

- [Studio](references/studio_manual.md): A web interface for data development and management, supporting data source connections, SQL querying, job orchestration, result visualization, and catalog browsing.
- [Object Model](references/object_model_design.md): Introduces the core concepts of the Singdata Lakehouse object model, including definitions and hierarchical relationships of catalogs, databases, tables, views, materialized views, functions, and shares.
- [Data Ingestion](references/Ingestion.md): Import data from local files, databases, Kafka, and other sources, covering core concepts, configuration steps, and operational examples.
- [Data Transformation](references/Transformation.md): Covers core concepts, key configurations, typical operational steps, examples, and considerations around data transformation.
- [Data Analysis](references/Analysis.md): A complete workflow guide from data import and SQL querying to visual analysis, covering data source connections, SQL syntax, function usage, and result export.
- [Security](references/data_security.md): Provides security features including user management, permission control, and audit logging, covering specific configuration methods for user creation, role authorization, data access policies, and operational auditing.
- [Data Sharing](references/data_share.md): Covers core concepts, key configurations, typical operational steps, examples, and considerations around data sharing.
- [Private Link](references/connect_to_Lakehouse.md): Achieves private network access across VPCs or from on-premises IDC to cloud services by configuring endpoint services and private links.
- [Benchmark](references/benchmark.md): Covers core concepts, key configurations, typical operational steps, examples, and considerations around performance testing.
- [Ecosystem Tools](references/tools_BI.md): Covers core concepts, key configurations, typical operational steps, examples, and considerations around ecosystem tools.
- [Insight](references/Lakehouse_Insight.md): Connects to Singdata Lakehouse data sources, creates datasets, and generates BI reports and dashboards via drag-and-drop for self-service data analysis and visualization.

## SQL Reference

- [SQL Commands](references/sql-reference.md): Provides complete syntax references for DDL, DML, DQL, and other SQL commands, including specific parameters and usage examples for statements like CREATE, SELECT, INSERT, and more.
- [Data Types](references/data-type.md): Introduces the specific data types supported by Singdata Lakehouse, including exact numerics, floating-point numbers, strings, datetime, booleans, and their definitions.
- [SQL Functions](references/functions.md): Covers core concepts, key configurations, typical operational steps, examples, and considerations around SQL functions.
- [SQL Usage Guide](references/considerations-for-using-sql.md): Covers core concepts, key configurations, typical operational steps, examples, and considerations around SQL usage.

## SDK Reference

- [Java SDK Reference](references/java_reference/java-sdk-summary.md): Covers core concepts, key configurations, typical operational steps, examples, and considerations around Java SDK.
- [Python SDK Reference](references/python_reference/python-sdk-summary.md): Covers core concepts, key configurations, typical operational steps, examples, and considerations around Python SDK.

## Practice Tutorials

- [Efficiently Manage Objects and Organize Data](references/data_org.md): Create and manage data objects through various data sources such as object storage, databases, and data lakes, and organize catalogs, set permissions, and configure lifecycle policies.
- [Data Import and Export Practice](references/practice_data_import_and_export.md): Provides specific operational steps and examples for importing data from local files, databases, Kafka, and other sources, and exporting query results to files or databases.
- [Data Query and Analysis Practice](references/practice_data_analysis.md): A complete workflow guide from data import and SQL querying to visual analysis, covering multiple data sources such as local files, databases, and Kafka.
- [Build and Operate ELT Pipelines Practice](references/ELT_practice.md): Build enterprise-grade ELT pipelines using scheduling tools, data quality monitoring, and task orchestration, covering the full lifecycle of development, testing, deployment, and failure recovery.
- [Optimize Computing Resources](references/optimizing-computing-resources.md): Introduces specific methods for optimizing computing resource usage by adjusting compute group configurations, setting elastic scaling policies, and using resource monitoring.
- [Performance Experience](references/performence_test.md): Provides performance testing methods, optimization suggestions, and monitoring metrics, covering specific operations for query acceleration, resource tuning, and bottleneck diagnosis.
- [Build Modern Data Stack](references/ModernDataStackWithEcosystemTools.md): Introduces the core components and architectural patterns of the modern data stack, including selection and integration of key stages such as data integration, transformation, storage, analysis, and visualization.
- [AI Application Development](references/REMOTEFUNCTION.md): Provides a complete guide and toolchain for the AI application development process, from data preparation and model training to service deployment.
- [Security and Compliance Audit](references/security_compliance_audit_guide.md): Provides operational methods and parameter descriptions for user permission management, SQL audit logging, data masking policies, and compliance configuration.
- [Usage and Cost Management](references/cost_management.md): View detailed usage, cost breakdown, and billing models for Singdata Lakehouse, and manage costs through budgets and alerting.

## Lakehouse AI

- [Lakehouse AI Overview](references/LakehouseAI_overview.md): Integrates unstructured data management, AI external functions, multimodal retrieval, Python development framework, and conversational analytics to achieve a closed loop from data to intelligent decision-making.
- [Data Preparation for AI](references/server-data-for-ai.md): Singdata Lakehouse supports vector search, full-text search, and structured data analysis seamlessly combined, providing unified data services for AI applications such as RAG and recommendation systems.
- [AI Functions](references/AI_function_in_SQL.md): Provides methods for creating and using AI functions in Singdata Lakehouse, supporting calls to external online AI services or offline model packages via Python/Java.
- [Lakehouse Python Development Framework (Zettapark)](references/LakehousePython-zettapark.md): API reference for the Zettapark Lakehouse Python development framework, including classes, methods, and parameter descriptions for core modules such as DataFrame, SQL, and Catalog.
- [AI + BI Unified Workflow](references/unifiedWorkflow.md): Generate SQL queries, visual charts, and dashboards through natural language interaction, achieving an end-to-end workflow from data exploration to analysis and presentation.
- [AI Gateway](references/AIGateway.md): AI Gateway supports unified access, route distribution, load balancing, rate limiting, circuit breaking, caching, and monitoring for managing API calls to multiple model providers.
- [Conversational Data Analytics (DataGPT)](references/datagpt_intro.md): Directly generate SQL, execute queries, and obtain visual charts through natural language queries, without writing code.
- [Lakehouse MCP Server](references/LakehouseMCPServer.md): Lakehouse MCP Server exposes data lakehouse capabilities (such as tables, views, and functions) to AI assistants like Claude through the Model Context Protocol, enabling natural language querying and analysis.
- [AI Ecosystem](references/AI_eco.md): Introduces how to integrate Lakehouse with mainstream AI frameworks (such as PyTorch, TensorFlow) and tools (such as MLflow, LangChain) to support model training, inference, and AI application development.

## Product Updates

- [Release Notes](references/releasenotes.md): Introduces new features and optimizations for Singdata Lakehouse in areas such as data import, SQL querying, data lake acceleration, and stream processing.

## Other

- [User Agreement](references/user-aggrement.md): Defines the account registration qualifications, process, usage rules, and security requirements for Singdata's product services, and outlines the rights and obligations between users and Singdata.
- [Privacy Policy](references/privacy-policy.md): Describes how the company collects, uses, and protects personal information, as well as the rights users have and contact methods.
- [Product Trial Agreement](references/product-trial-agreement.md): Product trial agreement, defining user responsibilities during the testing phase, company rights, intellectual property ownership, and disclaimers.