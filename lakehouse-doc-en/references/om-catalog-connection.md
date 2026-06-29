# Catalog Connection

Catalog Connection is used to connect to **external metadata stores** (such as Hive Metastore), allowing Lakehouse to directly read data from external systems through federated queries without needing to migrate data in.

## Use Cases

When your data resides in a Hive data lake and you want to query it directly in Lakehouse without copying data, establish a connection via Catalog Connection, then create an External Catalog.

```
Lakehouse SQL Query
  └── External Catalog
        └── Catalog Connection (stores Hive Metastore connection info)
              └── Hive Metastore → Data lake files
```

## Create Example

```sql
CREATE CATALOG CONNECTION my_hive_conn
  TYPE HIVE
  METASTORE_URI = 'thrift://hive-metastore-host:9083';
```

## Comparison with Other Connections

| Connection Type | Connection Target | Used With |
|----------------|---------|--------------|
| API Connection | Function compute services | External Function |
| Storage Connection | Object storage | External Volume, external tables |
| **Catalog Connection** | Hive Metastore | External Catalog |

## Related Documents

- [CREATE CATALOG CONNECTION](create-catalog-connection.md) — full syntax
- [External Catalog Federated Queries](external-catalog-concept.md)
- [Connection Overview](create-connection.md)
