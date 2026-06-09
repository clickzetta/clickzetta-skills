# Python SDK

`clickzetta-connector` is the official Python SDK for Singdata Lakehouse. It follows the PEP 249 specification and provides four integration methods: SQL queries, SQLAlchemy ORM, bulk writes (Bulkload), and real-time streaming writes. Python 3.10 and above is supported.

---

## Contents

| Page | Description |
|------|-------------|
| [Python SDK Overview](python_reference/python-sdk-summary.md) | pip installation, version notes, and quick connection example |
| [Python Database API Queries](python_reference/connector.md) | PEP 249-compliant SQL execution interface supporting queries, writes, and transactions |
| [Python Connector Usage Examples](python_reference/connector_examples.md) | Code examples for common scenarios: queries, writes, complex types, and batch operations |
| [Python Connector Advanced Usage](python_reference/connector_advanced.md) | Connection pooling, async queries, large result set handling, and error handling |
| [SQLAlchemy Interface](python_reference/sqlalchemy.md) | ORM framework integration, suitable for Pandas and data analysis toolchains |
| [Bulk Data Upload (Bulkload)](bulkloadv1-python-sdk.md) | High-throughput bulk writes, suitable for large-scale historical data import |
| [Real-time Data Writes](python-igs.md) | Row-by-row streaming writes, suitable for scenarios requiring high data freshness |
| [Python SDK Version History](python-sdk-version-history.md) | Change history for each version of clickzetta-connector |
| [Python SQLAlchemy Version History](python-sqlalchemy-version-history.md) | Change history for each version of the SQLAlchemy plugin |

---

## Comparison of Four Integration Methods

| Method | Use Case | Characteristics |
|--------|----------|-----------------|
| Python Database API | SQL queries, data reads and writes | PEP 249 standard interface, highly versatile |
| SQLAlchemy | ORM, Pandas, BI toolchains | Declarative queries, seamless integration with the Python ecosystem |
| Bulkload | Large-scale historical data import | Writes to object storage first, then imports; high throughput |
| Real-time writes | Streaming data, high-frequency writes | Row-by-row commit, low latency |

---

## Related Documentation

| Document | Description |
|----------|-------------|
| [Zettapark Quick Start](zettapark-quick-start.md) | Python DataFrame API for operating Lakehouse data in a Spark-style manner |
| [SQLAlchemy](sqlalchemy.md) | Detailed SQLAlchemy connection configuration |
| [Bulk Data Upload with Python SDK](use-python-sdk-upload-data.md) | Complete Bulkload practice example |
