# How to Use Zeppelin to Operate Singdata Lakehouse

## Introduction

**Zeppelin** is a web-based notebook tool that supports multiple data processing backends and languages, allowing you to easily perform interactive data analysis. By using Zeppelin, you can connect to Singdata Lakehouse, execute SQL queries, and create data-driven interactive documents.

## Preparation

1. **Install Zeppelin**:
   Please visit the [Zeppelin official website](https://zeppelin.apache.org/) and follow the instructions to complete the installation.

2. **Configure Zeppelin to connect to Singdata Lakehouse**:
   You need to complete the following steps to configure Zeppelin's JDBC interpreter to connect to Singdata Lakehouse.

   2.1 First, download the [JDBC driver](../JDBC-Driver.md) for Singdata Lakehouse.

   2.2 Next, click on "anonymous" at the top right of the Zeppelin page, and select "Interpreter" from the dropdown list that appears.

   2.3 Click the "+Create" button at the top right to create a new interpreter. Enter "clickzetta" in the Interpreter Name field, and select "jdbc" from the Interpreter Type dropdown menu.

   2.4 On the configuration page, fill in the following information:
      - **default.url**: Enter the Singdata Lakehouse JDBC connection string in the following format:
        `jdbc:clickzetta://<instanceid>.api.singdata.com/<workspace_name>?virtualCluster=<vcluster>&schema=<schema>`
      - **default.driver**: Enter the class name of the Singdata Lakehouse JDBC driver:
        `com.clickzetta.client.jdbc.ClickZettaDriver`
      - In the Artifact section, click the "Add" button and upload the previously downloaded JDBC driver JAR file.

   2.5 After completing the configuration, click the "Save" button to save the settings, and restart the interpreter named "clickzetta".

## Create a Notebook and Access Singdata Lakehouse

1. Create a new notebook named "Data Exploration" and set the Default Interpreter to "clickzetta".

   ![Create Notebook](../.topwrite/assets/image_1699930695948.png)

2. After saving the notebook, you can enter SQL commands for Singdata Lakehouse in the cells and click the "Run" button to execute the operations.

   ![Execute SQL Commands](../.topwrite/assets/image_1699930908479.png)

   You can refer to the following commands for operations:
   - [show tables](../SHOWTABLES.md): List all tables in the current database.
   - [select](../query-syntax.md): Query data from the table.

## View the Computing Resources (vcluster) and Database Schema in the Current Workspace

1. Use the following command to view the list of computing resources (vcluster) in the current workspace:
   ```
   show vclusters;
   ```
![View vclusters](../.topwrite/assets/image_1699931749633.png)

2. Use the following command to view the list of database schemas in the current workspace:
   ```
   show schemas;
   ```
## Switch the Computing Resources (vcluster) and Data Schema for Job Execution

1. Use the following command to switch the computing resources (vcluster) for job execution:

   ```
   use vcluster <vcluster_name>;
   ```

   For example:
   ```
   use vcluster qiliang_ap;
   ```

2. Use the following command to switch the data schema to be accessed:

   ```
   use schema <schema_name>;
   ```

   For example:
   ```
   use schema nyc_taxi_data;
   ```
Now, you have successfully configured Zeppelin and started using it to operate Singdata Lakehouse. You can continue to explore more SQL commands and data visualization features to analyze and present data more effectively.