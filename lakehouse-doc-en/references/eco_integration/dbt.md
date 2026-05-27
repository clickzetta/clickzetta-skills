# dbt ClickZetta adapter User Guide

## Introduction to dbt

dbt (data build tool) is an open-source data modeling tool designed to bring software engineering methods into the data modeling development process. dbt supports multiple data sources, enabling data developers to achieve cross-platform, quality-controlled data development. dbt has an active community and offers a wealth of extension components, such as data quality and integration with other systems, making data development more convenient.

Singdata has launched the `dbt-clickzetta` adapter to achieve compatibility with dbt, supporting dbt version 1.5+. This article will detail the installation and usage of the plugin, using the dbt standard example [Jaffle Shop](https://github.com/dbt-labs/jaffle-shop-classic).

## Preparing the Environment

1. Install the dbt-clickzetta plugin (which already integrates dbt-core and dbt-extractor):
   ```shell
   pip install dbt-clickzetta
   ```
3. Prepare the dbt project:
   ```shell
   git clone https://github.com/dbt-labs/jaffle-shop-classic.git
   ```
4. Manage and edit the project in the version control system.

## Configuration

In the root directory of the dbt project (i.e., the jaffle\_shop directory), edit the `profiles.yml` file as follows:
```yaml
jaffle_shop:
  target: prod
  outputs:
    prod:
      type: clickzetta
      service: api.singdata.com
      instance: instance_name
      username: user_name
      password: password
      workspace: workspace_name
      schema: jaffle_shop
      vcluster: default
```
Parameter Description:

- For the official dbt profile parameters (such as jaffle\_shop, target, etc. in the example above), please refer to the [dbt official documentation](https://docs.getdbt.com/docs/core/connect-data-platform/connection-profiles).
- Parameters recognized by the dbt-clickzetta plugin include:
  - type: Fixed as clickzetta
  - service: ClickZetta Lakehouse service address
  - instance: Instance name
  - username: Username
  - password: Password
  - workspace: Workspace name
  - schema: Schema name
  - vcluster: Compute cluster name

To facilitate the use of the `dbt` command, copy the `profiles.yml` file to the user directory:
```shell
mkdir ~/.dbt/ && cp profiles.yml ~/.dbt/
```
Run `dbt debug` to verify the configuration is correct.

## Run dbt Project

### 1. Upload Data

Run `dbt seed` to upload the CSV data from the project to ClickZetta Lakehouse.

### 2. Run Models

Use `dbt run`, dbt will automatically generate and execute SQL based on the files described in the models directory.

### 3. Validate Output

Run `dbt test` to validate the output tables. Tests are assertions you make about the models and other resources (such as sources, seeds, and snapshots) in your dbt project. When you run `dbt test`, dbt will tell you whether each test in your project passes or fails.

### 4. Generate and View Reports

Run `dbt docs generate` to generate the documentation website for the project. Run `dbt docs serve` to start a local HTTP service, and open `http://localhost:8080` in your browser to view the report page.

#### View Report

![dbt docs screenshot](dbt_docs_screenshot.png)

#### View Data Lineage

![Data Lineage Screenshot](../.topwrite/assets/image_1697458411669.png)

## More Examples

### Example 1: Create a Model

Create a new file `example_model.sql` under the `models` directory and add the following content:

```sql
-- This is an example model
SELECT 1 AS example_column
```sql
CREATE VIEW example_model AS
SELECT
  customers.first_name,
  customers.last_name,
  SUM(orders.total) AS total_spent
FROM
  {{ ref('customers') }} customers
JOIN
  {{ ref('orders') }} orders
ON
  customers.id = orders.customer_id
GROUP BY
  customers.first_name,
  customers.last_name;
```
### Example 2: Running a Specific Model

Run `dbt run-operation example_model` to execute a specific model.

### Example 3: Using Tests

Add tests in the `schema.yml` file under the `models` directory:
```yaml
models:
  - name: stg_customers
    columns:
      - name: customer_id
        tests:
          - unique
          - not_null
```
Run `dbt test` to execute the tests.

### Example 4: Using Hooks

Add hooks in the `schema.yml` file under the `models` directory:
```yaml
models:
  - name: stg_orders
