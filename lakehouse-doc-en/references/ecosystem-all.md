## Singdata Lakehouse Ecosystem Tool Connections

Singdata Lakehouse, as a powerful data platform, supports seamless connections with numerous ecosystem tools, allowing you to manage and analyze data more conveniently. This includes database client tools, BI and visualization, ETL tools, etc. The currently supported ecosystem tools include:

| Category  | Name                                                             |
| --------- | -------------------------------------------------------------- |
| Client    | [SQL Workbench/J](eco_integration/sqlworkbench-j-lakehouse.md) |
| Client    | [DBeaver](eco_integration/dbeaver-lakehouse.md)                |
| Client    | [DataGrip](eco_integration/datagrip-lakehouse.md)              |
| BI and Visualization | [Metabase](metabase.md)                                        |
| BI and Visualization | [Tableau](<TableauConnectToLakehouse.md>)                                                     |
| BI and Visualization | [Superset](eco_integration/superset.md)                        |
| BI and Visualization | [rath](eco_integration/rath.md)                                |
| BI and Visualization | [Streamlit](eco_integration/streamlit.md)                      |
| BI and Visualization | [Zeppelin](eco_integration/Zeppelin.md)                        |
| BI and Visualization | [FineBI](<FineBI.md>)                                                            |
| ETL       | [DataX](eco_integration/datax.md)                              |
| ETL       | [DBT](eco_integration/dbt.md)                                  |
| ETL       | [Airbyte](airbyte.md)                                          |
| Open Engine | [Trino](eco_integration/trino.md)                              |
| Open Engine | [Spark](spark-connector-summary.md)                            |
| Others    | [MindsDB](mindsdb.md)                                          |

For ecosystem tools not listed, you can consider using JDBC drivers or SQLAlchemy to create custom connections based on the connection methods supported by the client.