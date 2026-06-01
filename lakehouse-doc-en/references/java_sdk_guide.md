# Java SDK

`clickzetta-java` is the official Java SDK for Singdata Lakehouse, providing three data access methods: standard JDBC queries, real-time streaming writes, and high-throughput bulk writes (Bulkload). Java 8 and above is supported.

---

## Contents

| Page | Description |
|------|-------------|
| [Java SDK Overview](java_reference/java-sdk-summary.md) | Maven dependency configuration, version retrieval, and notes |
| [Java SDK Release Notes](version-update.md) | Change history for each version |
| [Initialize Client](java_reference/client.md) | Connection parameter configuration, Client creation and management |
| [Using JDBC Queries](java_reference/jdbc.md) | Standard Type 4 JDBC driver for executing SQL queries and writes |
| [Real-time Data Writes](java_reference/realtime-upload.md) | Row-by-row streaming writes, suitable for scenarios requiring high data freshness |
| [Bulk Data Writes (Bulkload)](bulkload-summary.md) | High-throughput bulk writes — data is uploaded to object storage first, then imported into the table; suitable for large-scale data |

---

## Comparison of Three Write Methods

| Method | Use Case | Characteristics |
|--------|----------|-----------------|
| JDBC | SQL execution, small-batch writes | Standard interface, good compatibility |
| Real-time writes | Streaming data, high-frequency writes | Row-by-row commit, low latency |
| Bulkload | Large-scale historical data import | Writes to object storage first, then imports; high throughput |

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [JDBC Driver](jdbc-driver.md) | Connect BI tools and database clients via JDBC |
| [Data Ingestion: Java SDK Bulk and Real-time Loading](comprehensive_guide_to_ingesting_javasdk_bulkload_realtime.md) | Complete Java SDK data ingestion practice guide |
