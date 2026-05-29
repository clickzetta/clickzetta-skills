# Create an External Catalog
Steps to create an External Catalog:

1. [Create a Storage Connection](<create-storage-connection.md>): First, you need to create a storage connection to access the object storage service.
2. [Create a Catalog Connection](<create-catalog-connection.md>): Use the storage connection information and Hive Metastore address to create a Catalog Connection.
3. Create an External Catalog: Use the Catalog Connection to create an external Catalog for accessing external data in the data lake.
# Syntax
```SQL
CREATE EXTERNAL CATALOG catalog_name
    CONNECTION catalog_api_connection;
```
**Parameter Description**

catalog_api_connection: The name of the catalog connection. Currently, only HIVE is supported. [Refer to creating a catalog connection](<create-catalog-connection.md>)
# Usage Instructions
[EXTERNAL CATALOG Usage Instructions](<external-catalog-summary.md>)
