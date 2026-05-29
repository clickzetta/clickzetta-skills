# Superset Singdata adapter User Guide

## Superset Introduction

Superset is an open-source BI data analysis and visualization platform by Airbnb, originally named Caravel and Panoramix. The main features of this tool include self-service analysis, custom dashboards, visualization (export) of analysis results, and user/role permission control. Superset also integrates an SQL editor, allowing users to perform SQL editing and querying. Initially, Superset was mainly used to support the visualization analysis of Druid, but later it evolved to support various relational databases and big data computing frameworks, such as MySQL, Oracle, PostgreSQL, Presto, SQLite, Redshift, Impala, SparkSQL, Greenplum, and MSSQL. Superset is based on the Python framework and integrates technologies such as Flask, D3, Pandas, and SqlAlchemy.

## Superset Singdata Adapter

`clickzetta-sqlalchemy` is a dialect adapter for SQLAlchemy that provides Singdata Lakehouse, making it easy for code or upper-layer applications written using the SQLAlchemy interface to connect to Singdata Lakehouse. Superset supports URL configuration data source links in the SQLAlchemy specification, so connecting to the Singdata database in Superset only requires configuring the corresponding URL.

## Installation and Configuration

### Using Docker Image

By using the Docker image, you can quickly experience the effect of Superset connecting to Singdata Lakehouse:
```shell
docker pull clickzetta/superset:2.1.0-1
docker run -p 8088:8088 clickzetta/superset:2.1.0-1
```
Open the browser and go to http://localhost:8088.

### Local Installation

1. Install `clickzetta-sqlalchemy`:
   `clickzetta-sqlalchemy` needs to be installed in an environment with Python version 3.7 or above.
Installation command (ensure the current environment does not need to use clickzetta-sqlalchemy and clickzetta-connector, uninstall them to avoid dependency conflicts):
```
pip uninstall -y clickzetta-sqlalchemy clickzetta-connector && pip install clickzetta-connector -U
```
2. Install Superset:
   You can choose to install the same version of Superset as the image, or install a higher version of Superset.
```shell
   # Install the same version of Superset as the image
   pip install -r https://raw.githubusercontent.com/clickzetta/awesome-clickzetta/main/superset/requirements.txt

   # Install a higher version of Superset
   pip install 'apache-superset>=2.1'
   ```
3. Initialize Superset:
```shell
export FLASK_APP=superset

superset db upgrade

# Create an admin user
superset fab create-admin

superset init

# Start the service, bound to port 8088 on localhost. For remote access, add --host 0.0.0.0
superset run -p 8088 --with-threads --reload --debugger
```
## Usage

### Log in to Superset

* If you are using the image, the default username is `admin` and the password is `clickzetta`.
* If you have a local installation, please use the username and password you set during the installation step `superset fab create-admin`.

### Connect to Singdata Database

1. Click on Settings in the upper right corner and then Database Connections to navigate to the Superset database creation page.
2. Click on Database in the upper right corner and select Other as the database type.
3. Fill in the database name and the service URL of Singdata Lakehouse.
4. Click the TESTING CONNECTION button to test if the connection is successful.
5. If the test passes, click the CONNECT button below to complete the database connection.

### Singdata URL Format

The format of the Singdata URL is as follows:
```
clickzetta://username:password@instance.service/workspace?vcluster=vcluster
```
The meanings of each part are as follows:

* username: Username
* password: Password
* instance: Instance name
* service: Service domain name
* workspace: Workspace name
* vcluster: Resource name

The service supports specifying a port. If you do not need to specify a port, you can directly use the domain name. For example:
```
# Specify Port
clickzetta.service:9090
# Do Not Specify Port
clickzetta.service
```
service supports both http and https protocols.

### Using Superset for Visualization Analysis

After successfully connecting to the Singdata database, you can use Superset for data visualization analysis. Here are some usage examples:

1. Create a chart: Click on Charts in the left menu bar and select New Chart. On the chart settings page, select the Singdata database you just connected to, then choose the appropriate table and fields to create the chart.
2. Create a dashboard: Click on Dashboards in the left menu bar and select New Dashboard. On the dashboard settings page, you can add multiple charts and adjust their layout and style.
3. Export and share: On the chart or dashboard page, you can click the export button in the upper right corner to export the analysis results as images,