# Overview
**[Preview Release] This feature is currently in public preview.**

External Catalog is a secure object in Lakehouse that maps databases from external data systems, allowing users to perform read-only queries on these data systems within Lakehouse. Through External Catalog, users can leverage Lakehouse's query capabilities to access and analyze data stored in external databases.

# External Catalog Use Cases
* **Unified Metadata Management**: Manage metadata from multiple data sources in a unified manner, simplifying data governance.
- **Data Federation Query**: With External Catalog, users can perform federated queries across different data sources as if they were data within the same database. Through federated queries, users can access and analyze data stored in external systems in real-time without waiting for data synchronization.
- **Data Import**: Import data scattered across different data sources into Lakehouse to build a unified data lake, facilitating big data analysis and machine learning. Retain historical data or infrequently accessed data in external storage and import it into Lakehouse through External Catalog to optimize data warehouse storage and performance.

# Using External Catalog

1. **Create Connection**: First, you need to create a connection in Catalog Connection. This connection is a secure object that specifies the path and authentication information for accessing the external database system.
2. **Create External Catalog**: Using the created connection, you can create an external catalog. This catalog exists as a secure object in External Catalog, mirroring the database structure in the external data system.
3. **Execute Query**: Once the external catalog is created, users can write SQL queries in Lakehouse.

# Supported Data Sources

Lakehouse supports Apache Hive connection access through the Multi-Catalog feature.

# EXTERNAL CATALOG Related Syntax
- Create External Catalog
Refer to [CREATE EXTERNAL CATALOG](<create-external-catalog.md>)
- List Catalog
Refer to [SHOW CATALOG](<show-catalog.md>)
- View SCHEMA under Catalog
Refer to [View SCHEMA under EXTERNAL CATALOG](<show-catalog-schema.md>)
- List Tables under CATALOG
Refer to [List Tables under CATALOG](<show-catalog-table.md>)
- Query Tables under CATALOG
Refer to [Query Tables under CATALOG](<show-catalog-table.md>)
- Create Table Structure under CATALOG
Refer to [View Table Structure under CATALOG](<desc-catalog-table.md>)

# Permissions
Currently, only the instance admin role can query the created CATALOG.
# Use Cases
Refer to [Create HIVE CATALOG](<create-hive-catalog.md>)