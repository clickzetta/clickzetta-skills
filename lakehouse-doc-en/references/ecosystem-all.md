# Ecosystem Tool Connections

Singdata Lakehouse supports multiple integration methods including JDBC drivers, Python/Java SDKs, and Spark/Flink Connectors. All major SQL clients, BI tools, and ETL platforms are supported. Choose the approach that fits your use case.

---

## I want to connect with a SQL client

**Recommended: DBeaver or DataGrip** — connect via the JDBC driver with support for SQL editing, schema browsing, and data export.

| Tool | Description | Reference |
|------|-------------|-----------|
| DBeaver | Free and open-source; the community edition is sufficient for everyday queries and data exploration | [DBeaver Connection Guide](eco_integration/dbeaver-lakehouse.md) |
| DataGrip | From JetBrains; strong code completion and SQL analysis | [DataGrip Connection Guide](eco_integration/datagrip-lakehouse.md) |
| SQL Workbench/J | Lightweight; suitable when you only need basic SQL execution | [SQL Workbench/J Connection Guide](eco_integration/sqlworkbench-j-lakehouse.md) |

All of the above connect via the JDBC driver. Connection string format:

```
jdbc:clickzetta://<instance_name>.<region_id>.api.singdata.com/<workspace_name>?username=<user>&password=<pwd>&virtualCluster=default
```

See [JDBC Driver](jdbc-driver.md) for details.

---

## I want to use a BI tool for data visualization

| Tool | Description | Reference |
|------|-------------|-----------|
| FineBI | A leading domestic BI platform; connects via JDBC and is well-suited for internal enterprise reporting | [FineBI Connection Guide](finebi.md) |
| Tableau | Connects via JDBC; ideal for complex visualizations and exploratory analysis | [Tableau Connection Guide](tableau-connect-to-lakehouse.md) |
| Metabase | Open-source and easy to deploy; suitable for self-service analytics in small to mid-sized teams | [Metabase Connection Guide](metabase.md) |
| Apache Superset | Open-source; supports SQLAlchemy connections; suitable for teams with operational capacity | [Superset Connection Guide](eco_integration/superset.md) |
| Rath | Open-source intelligent analytics tool with automatic insight generation | [Rath Connection Guide](eco_integration/rath.md) |
| Streamlit | Python data application framework; lets data science teams build apps quickly | [Streamlit Connection Guide](eco_integration/streamlit.md) |
| Zeppelin | Notebook-style interface; suitable for data exploration and reporting | [Zeppelin Connection Guide](eco_integration/zeppelin.md) |

> Most BI tools connect via the JDBC driver. If a tool supports SQLAlchemy (e.g., Superset), you can also use the SQLAlchemy interface provided by the Python SDK.

---

## I want to use an ETL tool for data integration

| Tool | Description | Reference |
|------|-------------|-----------|
| DataX | Open-sourced by Alibaba; suitable for offline batch data synchronization with simple configuration | [DataX Integration Guide](eco_integration/datax.md) |
| dbt | Data transformation tool; ideal for SQL modeling and data transformation inside Singdata Lakehouse | [dbt Integration Guide](eco_integration/dbt.md) |
| Airbyte | Open-source ELT platform with a rich connector library; suitable for aggregating data from multiple sources | [Airbyte Integration Guide](airbyte.md) |

**Choosing the right tool**:
- Syncing data from a single source → DataX
- Data modeling and transformation inside Singdata Lakehouse → dbt
- Connecting to multiple SaaS data sources (Salesforce, HubSpot, etc.) → Airbyte

---

## I want to connect programmatically

| Method | Language | Description | Reference |
|--------|----------|-------------|-----------|
| JDBC Driver | Java / any JVM language | Standard JDBC interface; supports SQL queries and DML | [JDBC Driver](jdbc-driver.md) |
| Python SDK | Python | PEP 249-compliant; supports SQL queries, bulk writes (bulkload), and real-time writes | [Python SDK](python_reference/python-sdk-summary.md) |
| Java SDK | Java | Supports bulk writes (BulkLoad) and real-time streaming writes (RealtimeStream) | [Java SDK Bulk Upload](use-java-sdk-upload-data-local.md) · [Java SDK Real-time Upload](use-java-sdk-realtime-uploaddata.md) |

**Choosing a write mode**:
- Offline bulk import (GB-scale or larger) → BulkLoad (Java SDK or Python SDK bulkload)
- Real-time row-by-row writes (millisecond latency) → RealtimeStream (Java SDK) or Python SDK real-time upload
- Standard SQL INSERT → JDBC

---

## I want to process data with a compute engine

| Engine | Description | Reference |
|--------|-------------|-----------|
| Apache Spark | Read and write Singdata Lakehouse tables via the Spark Connector; supports the DataFrame API and spark-sql | [Spark Connector](spark-connector-summary.md) |
| Apache Flink | Write to Singdata Lakehouse via the Flink Connector; supports CDC scenarios and append-only mode; sink tables only (write) | [Flink Connector](flink-write-connector.md) |

**Two Flink Connector modes**:
- `igs-dynamic-table`: supports CDC (insert / update / delete); the target table must have a primary key
- `igs-dynamic-table-append-only`: append only, no updates or deletes; the target table is a regular table

> The Flink Connector currently supports write (sink table) only — it cannot be used as a source table or dimension table.

---

## Other

| Tool | Description | Reference |
|------|-------------|-----------|
| MindsDB | Machine learning platform; run predictions directly on Singdata Lakehouse data | [MindsDB Integration Guide](mindsdb.md) |

For tools not listed here, you can create a custom connection using the JDBC driver or SQLAlchemy, depending on what connection methods the tool supports.

---

## Not sure which approach to use?

```
What is your use case?
├── Interactive SQL queries / data exploration
│   ├── GUI client → DBeaver or DataGrip
│   └── Command line → cz-cli
├── Data visualization / reporting
│   ├── Internal enterprise reporting → FineBI
│   ├── Exploratory analysis → Tableau / Metabase
│   └── Custom applications → Streamlit / Superset
├── Data integration / ETL
│   ├── Offline batch sync → DataX
│   ├── SQL modeling and transformation → dbt
│   └── Multiple SaaS data sources → Airbyte
├── Programmatic access
│   ├── Java applications → JDBC Driver or Java SDK
│   └── Python applications → Python SDK
└── Compute engine
    ├── Batch processing / ML → Spark Connector
    └── Stream processing / CDC → Flink Connector
```
