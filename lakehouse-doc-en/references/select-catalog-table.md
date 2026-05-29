## Description

Query tables in an External Catalog using the three-level naming structure (`catalog.schema.table`), with support for joining with Lakehouse local tables.

## Syntax

```SQL
SELECT <expr> FROM catalog_name.schema_name.table_name [WHERE ...];
```

### Parameter Description

* `catalog_name`: Catalog name, which must have been registered via `CREATE EXTERNAL CATALOG`.
* `schema_name`: Schema name.
* `table_name`: Table name.
* Querying tables in an External Catalog requires the three-level structure; `catalog_name` cannot be omitted.

## Examples

Query the region table in a shared catalog:

```SQL
SELECT * FROM clickzetta_sample_data.tpch_100g.region LIMIT 3;
+-------------+----------+----------------------------------------------------+
| r_regionkey |  r_name  |                     r_comment                      |
+-------------+----------+----------------------------------------------------+
|           0 | AFRICA   | lar deposits. blithely final packages cajole. r... |
|           1 | AMERICA  | hs use ironic, even requests. s                    |
|           2 | ASIA     | ges. thinly even pinto beans ca                    |
+-------------+----------+----------------------------------------------------+
```

Join with a Lakehouse local table:

```SQL
SELECT e.name, r.r_name AS region
FROM doc_test.employees e
JOIN clickzetta_sample_data.tpch_100g.region r
  ON r.r_regionkey = 0
WHERE e.dept = 'Engineering'
LIMIT 3;
```

## Notes

* When querying an External Catalog, read permissions are controlled by the corresponding STORAGE CONNECTION.
* Data in an External Catalog is not stored locally in the Lakehouse. Each query accesses the external data source over the network, so be mindful of network latency and access costs.
* To list available Catalogs, use `SHOW CATALOGS`; to view tables within a Schema, use `SHOW TABLES IN catalog_name.schema_name`.
