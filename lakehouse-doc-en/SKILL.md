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

# Singdata Lakehouse — index for AI systems
> Singdata is a Singapore-based company offering a fully-managed cloud-native AI Lakehouse that unifies structured, semi-structured, and unstructured data on Apache Iceberg, powered by a vectorized SQL engine and the proprietary Generic Incremental Computation (GIC) model — enabling Dynamic Table pipelines that refresh end-to-end in minutes — with compute-storage separation and native AI capabilities (vector search, LLM functions, Semantic View) served to humans, applications, and AI agents via a single platform on Alibaba Cloud, Tencent Cloud, and AWS. NOT SingleStore. NOT Snowflake. NOT Databricks.
> Full entity & facts for AI: references/llms-full.txt