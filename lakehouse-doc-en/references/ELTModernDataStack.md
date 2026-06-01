# Building an ELT-Oriented Modern Data Stack Based on Singdata Lakehouse

As enterprise data volumes and data architectures become increasingly complex, companies urgently need to find faster, more efficient, and cost-effective methods for data management and analysis. In recent years, the Modern Data Stack (MDS) has been continuously innovating and developing, attracting widespread attention.

## What is MDS?

MDS is a collection of cloud-based data tools and technologies centered around cloud data warehouses, data lakes, or Lakehouses, enabling data storage, processing, analysis, and visualization. Over the past decade, cloud data warehouses represented by Snowflake, AWS Redshift, GCP BigQuery, and MaxCompute have rapidly developed and evolved into Lakehouse architectures that integrate data warehouses and data lakes. They leverage massive parallel processing and SQL support to make big data processing faster and cheaper. On this basis, many low-code, easy-to-integrate, scalable, and economical cloud-native data tools have emerged, such as Fivetran, Airbyte, dbt, dagster, Looker, etc. MDS has changed the way enterprises manage and analyze data, making data more valuable.

Singdata Lakehouse was born in this context. It is a platform focused on data, helping enterprises manage and fully utilize data, providing a new solution for building a modern data stack MDS.

## What are the key features of a modern data stack?

1. Cloud-first. MDS is cloud-based, offering greater scalability and flexibility, and can easily integrate with existing cloud infrastructure.
2. Centered around cloud data warehouses/data lakes/Lakehouses. MDS aims to seamlessly integrate with cloud data warehouses such as Redshift, BigQuery, Snowflake, Databricks, MaxCompute, and Singdata Lakehouse, as well as data lakes and Lakehouses.
3. Modular design. MDS prevents vendor lock-in, providing enterprises with greater flexibility and control over their data stack.
4. Primarily SaaS or open source. While open source is beneficial, it requires a high level of expertise, making the fully managed SaaS model more popular.
5. Lowering the threshold. With MDS, everyone within the enterprise can access and use the data they need, rather than confining data to specific teams or departments. This helps achieve data democratization and fosters a data culture within the enterprise.

## Differences between traditional data stacks and modern data stacks

### Traditional data stack:

* Requires high technical skills
* Relies on extensive infrastructure
* Time-consuming

### Modern data stack:

* Breaks the constraints of cloud and data
* Simple and easy to use
* Toolkits suitable for non-technical personnel and business departments
* Saves time

## Why is the data stack important?

"Time is money." This old saying is true, especially for data-driven companies. The efficiency of the data stack in processing raw data determines the speed at which data analysis and data science teams can derive value from the data. Having the right tools is key to a modern data stack and crucial to a company's success.

## Basic components of MDS

To understand the advantages of MDS tools and make appropriate tool choices, it is first necessary to understand the various components of the data platform and the common functions of the tools that serve each component.

The basic components of a data platform (in the direction of data flow) include:

* Data ingestion (**E**)
* Data storage and processing (**L**, data warehouse/data lake/Lakehouse)
* Data transformation (**T**)
* Metrics layer (Headless BI)
* Business intelligence tools
* Reverse ETL
* Orchestration (workflow engine)
* Data management, quality, and governance
  ![](.topwrite/assets/image_1718933542634.png)

## From ETL to ELT

ETL and ELT both describe the process of integrating data for data analysis, business intelligence, and data science in data warehouses or Lakehouses by cleaning, enriching, and transforming data from various sources.

* **E**xtract refers to the process of extracting data from sources such as SQL or NoSQL databases, XML files, or cloud platforms.
* **T**ransform refers to the process of transforming the format or structure of data sets to match the target system.
* **L**oad refers to the process of loading data sets into the target system (data warehouse, Lakehouse).

![](.topwrite/assets/image_1718933554740.png)

### ETL

#### **ETL stands for Extract > Transform > Load**

In the ETL process, data transformation is performed in a staging area outside the data warehouse, and the entire data must be transformed before loading. Therefore, transforming large data sets can take a long time, but once the ETL process is complete, analysis can be performed immediately.

#### ETL process

1. Extract a predetermined subset of data from the source.
2. Data is transformed in the staging area in some way, such as data mapping, applying concatenation, or calculations. To cope with the limitations of traditional data warehouses, it is necessary to transform the data before loading.
3. Data is loaded into the target data warehouse system and is ready for analysis by BI tools or data analysis tools.

![](.topwrite/assets/image_1718933568004.png)

### ETL
#### **ELT stands for Extract > Load > Transform**

In the ELT process, data transformation is performed as needed within the target system itself. Therefore, the transformation step takes very little time, but if there is not enough processing power in the cloud solution, it may slow down the query and analysis process.

#### ELT Process

1. All data is extracted from the source.
2. All data is immediately loaded into the target system (data warehouse, Lakehouse). This can include raw data, unstructured, semi-structured, and structured data types.
3. Data is transformed within the target system and prepared for analysis by BI tools or data analysis tools.

Typically, the target system for ELT is a cloud-based data warehouse or Lakehouse. Cloud-based platforms like Amazon Redshift, Snowflake, Databricks, and Singdata Lakehouse offer nearly unlimited storage and powerful processing capabilities. This allows users to extract and load any and all data they might need almost in real-time. Cloud platforms can transform any data needed for BI, analysis, or predictive modeling at any time.

![](.topwrite/assets/image_1718933580647.png)

### Why Choose ELT?

* **Real-time, flexible data analysis**. Users can flexibly explore the complete dataset from any direction, including real-time data, without waiting for data engineers to extract, transform, and load more data.
* **Lower costs and less maintenance**. ELT benefits from the powerful ecosystem of cloud-based platforms, which offer lower costs and various options for storing and processing data. Moreover, since all data is always available and the transformation process is usually automated and cloud-based, the ELT process typically requires very little maintenance.

## Building an ELT-oriented Modern Data Stack based on Singdata Lakehouse

### The Position of ELT in MDS

![](.topwrite/assets/image_1718933593607.png)

#### Data Ingestion - Airbyte

Airbyte is a leading data integration platform suitable for ETL/ELT data pipelines from APIs, databases, and files to data warehouses, data lakes, and Lakehouses.

Airbyte already provides over 300 connectors for APIs, databases, data warehouses, and Lakehouses, and developing new connectors is very convenient, known for its support for multiple sources, **especially suitable for long-tail data source scenarios**.

#### Data Storage and Processing - Singdata Lakehouse

Singdata Lakehouse is a fully managed data management and analysis service with a lakehouse architecture. Singdata Lakehouse meets the needs of data warehouse construction, data lake exploration and analysis, offline and real-time data processing and analysis, business reporting, and other scenarios with a single engine. It meets the scalability, cost, and performance needs of enterprises at different stages through storage-compute separation, serverless elastic computing power, and intelligent optimization features. Built-in data integration, development and operations, data asset management, and other services are ready to use, greatly simplifying data development and management work, accelerating enterprise data insights and value realization.

#### Data Transformation - dbt

dbt enables data analysts and engineers to transform data using the same practices that software engineers use to build applications. Analysts using dbt only need to write select statements to transform data, while dbt takes care of turning those statements into tables and views in the data warehouse.

These select statements or "models" form a dbt project. Models often build on each other - dbt can easily *manage relationships between models*, *visualize these relationships*, and ensure the quality of transformations through *testing*.

dbt avoids writing boilerplate *DML* and *DDL* by managing transactions, dropping tables, and managing schema changes. *Simply write **business logic** using SQL select statements or Python DataFrames that return the desired dataset, and dbt takes care of materialization.

dbt generates valuable metadata to find long-running queries and has built-in support for standard transformation models such as full or incremental loads.

#### Data Workflow - dagster

Dagster is an orchestrator designed to develop and maintain data assets such as tables, datasets, machine learning models, and reports.

You can declare the functions to run and the data assets these functions generate or update. Then, Dagster can help you run your functions at the right time and keep your assets up to date.

Dagster is designed for every stage of the data development lifecycle - local development, unit testing, integration testing, staging environments, all the way to production.

Like dbt, it enforces best practices such as writing declarative, abstract, idempotent, and type-checked functions to catch errors early. Dagster also includes simple unit testing and convenient features to make pipelines reliable, testable, and maintainable. It also integrates deeply with Airbyte, allowing *data ingestion as code*.

### ELT Processing Flow

![](.topwrite/assets/image_1718933608199.png)

#### Data Extraction and Loading (Airbyte)

![](.topwrite/assets/image_1718933621645.png)

##### Using Singdata Lakehouse as Airbyte's Destination Connector
![](.topwrite/assets/image_1718933642260.png)

##### Synchronize Employee Database via Incremental | Append + Deduped Method

![](.topwrite/assets/image_1718933652747.png)

##### Synchronize Historical Forex Trading Data in Parquet Format on S3

![](.topwrite/assets/image_1718933682596.png)

#### Data Transformation (dbt)

##### Configure DBT's profile.yml

The target here points to clickzetta\_uat, which means that the data transformations in this project will run on clickzetta\_uat. The target table will be output to the modern\_data\_stack schema in the ql\_ws workspace of the Singdata Lakehouse. The computing resources will use a vcluster named default.
```SQL
mds_dbt:
  target: clickzetta_uat
  outputs:
    mds_source:
      type: postgres
      host: 172.17.1.220
      port: 5432
      user: metabase
      pass: metasample123
      dbname: mds_source
      schema: public
      threads: 2
      keepalives_idle: 0
    clickzetta_uat:
      type: clickzetta
      service: https://api.singdata.com
      workspace: ql_ws
      instance: ***
      vcluster: default
      username: ***
      password: ***
      database: ql_ws
      schema: modern_data_stack
      threads: 8
      keepalives_idle: 0
    mysql_employees:
      type: mysql
      server: 172.17.1.220
      port: 3306
      database: employees
      schema: employees
      username: root
      password: metasample123
      driver: MySQL ODBC 8.0 ANSI Driver
      threads: 2
      keepalives_idle: 0
```
##### Define DBT's source.yml
```SQL
version: 2

sources:
  - name: ql_ws
    database: ql_ws
    schema: modern_data_stack
    tables:
      - name: orders
        identifier: _airbyte_raw_orders
        description: "Orders table, contains all order data."
      - name: users
        identifier: _airbyte_raw_users
        description: "Users table, contains user information."
      - name: departments
        identifier: departments
        description: "Employee information, departments table"
      - name: dept_emp
        identifier: dept_emp
        description: "Employee information, dept_emp table"
      - name: dept_manager
        identifier: dept_manager
        description: "Employee information, dept_manager table"
      - name: employees
        identifier: employees
        description: "Employee information, employees table"
      - name: salaries
        identifier: salaries
        description: "Employee information, salaries table"
      - name: titles
        identifier: titles
        description: "Employee information, titles table"
```
##### Develop DBT Transformation Models

DBT will generate a target table or view with the same name as the file based on the SELECT statement, which is confirmed by the configuration in dbt\_project.yml. For example:

models:

mds\_dbt:

+materialized: "table"

indicates that the data transformation target type is a table, not a view. If a view needs to be generated, it should be set to:

models:

mds\_dbt:

+materialized: "view"

The following is the data transformation model:

user\_augmented.sql
```SQL
select
        cast(from_json(_airbyte_data,'struct<index:bigint,user_id:bigint,is_bot:boolean>').index as int) as index,
        cast(from_json(_airbyte_data,'struct<index:bigint,user_id:bigint,is_bot:boolean>').user_id as string) as user_id,
        cast(from_json(_airbyte_data,'struct<index:bigint,user_id:bigint,is_bot:boolean>').is_bot as boolean) as is_bot
from {{ source('ql_ws', 'users') }}
```

orders\_cleaned.sql

```SQL
select
        cast(from_json(_airbyte_data,'struct<index:bigint,user_id:bigint,order_time:string,order_value:double>').index as int) as index,
        cast(from_json(_airbyte_data,'struct<index:bigint,user_id:bigint,order_time:string,order_value:double>').user_id as string) as user_id,
        cast(from_json(_airbyte_data,'struct<index:bigint,user_id:bigint,order_time:string,order_value:double>').order_time as timestamp) as order_time,
        cast(from_json(_airbyte_data,'struct<index:bigint,user_id:bigint,order_time:string,order_value:double>').order_value as double) as order_value,
from {{ source('ql_ws', 'orders') }}
```

daily\_order\_summary.sql

```SQL
select
        date_trunc('DAY', oc.order_time::timestamp) as order_date,
        sum(oc.order_value) as total_value,
        count(*) as num_orders
from
        {{ ref("orders_cleaned") }} oc
        join
        {{ ref("users_augmented") }} ua
        on oc.user_id = ua.user_id
where not ua.is_bot
group by 1 order by 1
```

employees\_detail\_single\_view\.sql

```SQL
SELECT  e.emp_no,
        e.birth_date,
        e.first_name,
        e.last_name,
        e.gender,
        e.hire_date,
        d.dept_no,
        d.dept_name,
        m.from_date as dept_manager_from_date,
        m.to_date as dept_manager_to_date, 
        de.from_date as dept_emp_from_date,
        de.to_date as dept_emp_to_date,
        t.title,
        t.from_date as title_from_date,
        t.to_date as title_to_date,
        s.salary,
        s.from_date as salary_from_date,
        s.to_date as salary_to_date
FROM {{ source('ql_ws', 'employees') }} e
FULL JOIN {{ source('ql_ws', 'dept_emp') }} de ON e.emp_no = de.emp_no
FULL JOIN {{ source('ql_ws', 'departments') }} d ON de.dept_no = d.dept_no
FULL JOIN {{ source('ql_ws', 'titles') }} t ON e.emp_no = t.emp_no
FULL JOIN {{ source('ql_ws', 'salaries') }} s ON e.emp_no = s.emp_no
FULL JOIN {{ source('ql_ws', 'dept_manager') }} m ON e.emp_no = m.emp_no
order by e.emp_no,d.dept_no,m.from_date desc
```
##### Define DBT's schema.yml
```SQL
version: 2

models:
  - name: daily_order_summary
    description: "Daily metrics for orders placed on this platform."
    columns:
      - name: order_date
        description: "The UTC day for which these orders were aggregated."
        data_type: "date"
      - name: total_value
        description: "The total value of all orders placed on this day."
        data_type: "float"
      - name: num_orders
        description: "The total number of orders placed on this day."
        data_type: "int"
  - name: orders_cleaned
    description: "Filtered version of the raw orders data."
    columns:
      - name: "user_id"
        description: "Platform id of the user that placed this order."
        data_type: "int"
      - name: "order_time"
        description: "The timestamp (in UTC) that this order was placed."
        data_type: "timestamp"
      - name: "order_value"
        description: "The dollar amount that this order was placed for."
        data_type: "float"
  - name: users_augmented
    description: "Raw users data augmented with backend data."
    columns:
      - name: "user_id"
        description: "Platform id for this user."
        data_type: "int"
      - name: "is_spam"
        description: "True if this user has been marked as a fraudulent account."
        data_type: "bool"
  - name: employees_detail_single_view
    description: "Merge data from six tables: departments, dept_emp, dept_manager, employees, salaries, and titles into a single table to form a unified view of employee data."
    columns:
      - name: "emp_no"
        description: "Unique employee number identifier."
        data_type: "bigint"
        tests:
          - not_null

      - name: "birth_date"
        description: "The birth date of the employee."
        data_type: "date"
        tests:
          - not_null

      - name: "first_name"
        description: "First name of the employee."
        data_type: "string"
        tests:
          - not_null

      - name: "last_name"
        description: "Last name of the employee."
        data_type: "string"
        tests:
          - not_null

      - name: "gender"
        description: "Gender of the employee."
        data_type: "string"
        tests:
          - not_null

      - name: "hire_date"
        description: "The date when the employee was hired."
        data_type: "date"
        tests:
          - not_null

      - name: "dept_no"
        description: "Department number that the employee belongs to."
        data_type: "string"

      - name: "dept_name"
        description: "Name of the department."
        data_type: "string"

      - name: "dept_manager_from_date"
        description: "Start date of the employee's tenure as a department manager."
        data_type: "date"

      - name: "dept_manager_to_date"
        description: "End date of the employee's tenure as a department manager."
        data_type: "date"

      - name: "dept_emp_from_date"
        description: "Start date of the employee's membership in a department."
        data_type: "date"

      - name: "dept_emp_to_date"
        description: "End date of the employee's membership in a department."
        data_type: "date"

      - name: "title"
        description: "Title of the employee's position."
        data_type: "string"

      - name: "title_from_date"
        description: "Start date of the employee's tenure in their current title."
        data_type: "date"

      - name: "title_to_date"
        description: "End date of the employee's tenure in their current title."
        data_type: "date"

      - name: "salary"
        description: "The salary of the employee."
        data_type: "bigint"
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 9999999

      - name: "salary_from_date"
        description: "Start date of the employee's current salary."
        data_type: "date"

      - name: "salary_to_date"
        description: "End date of the employee's current salary period."
        data_type: "date"
```

##### DBT debug、compile

```Shell
dbt debug
dbt compile
```
##### Check if the Data Lineage is Correct
```Shell
dbt docs generate
dbt docs serve
```
Automatically opens:http\://localhost:8080/#!/overview

![](.topwrite/assets/image_1718933715885.png)

#### Workflow Orchestration (dagster)

dagster implements a software-defined, ETL pipeline complete data workflow DAG diagram, which is very clear and readable:

![](.topwrite/assets/image_1718933725456.png)

![](.topwrite/assets/image_1718933736456.png)

#### View the Target Table of Data Transformation on Singdata Lakehouse

![](.topwrite/assets/image_1718933747682.png)

## Next Steps

So far, we have reviewed the differences between the modern data stack and the traditional data stack, discussed the differences between ETL and ELT, and how to build a complete ELT-oriented modern data stack based on Singdata Lakehouse, Airbyte, DBT, and Dagster.

  Once the data enters the Singdata Lakehouse, the next step is how to analyze the data. Please read: [Building an Analytics-Oriented Modern Data Stack Based on Singdata Lakehouse](analyticsmoderndatastack.md)

## Appendix

[Airbyte Installation and Deployment Guide](airbyte.md)

[DBT Installation and Deployment Guide](eco_integration/dbt.md)

dagster project: <https://github.com/yunqiqiliang/dagster-clickzetta/tree/master/examples/assets_modern_data_stack>