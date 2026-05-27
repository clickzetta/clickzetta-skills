# Introduction to Metabase

Metabase is an open-source business intelligence platform that helps you easily ask questions about data and visualize the results. Additionally, Metabase can be embedded into your applications, allowing your customers to explore and analyze their data.

![Metabase Interface Example](.topwrite/assets/image_1704980255033.png)

# Deploying Metabase on Docker

Metabase officially provides a Docker image, making it easy to quickly deploy on any system that supports Docker. This document will guide you on how to deploy Metabase on Docker and connect to the Singdata Lakehouse database.

## Quick Start

Ensure that you have Docker installed and running. Next, follow these steps to run the open-source version of Metabase locally.

1. Pull the latest Docker image:
   ```
   docker pull metabase/metabase:latest
   ```
2. Start the Metabase container:
   ```
   docker run -d -p 3000:3000 --name metabase-clickzetta metabase/metabase:latest
   ```
By default, the Metabase server will start on port 3000.

3. Download the Singdata Lakehouse Metabase driver and COPY it into the docker container:
   [clickzetta.metabase-driver-0.1.1.jar](https://autolake-dev-beijing.oss-cn-beijing.aliyuncs.com/clickzetta-tool/release/clickzetta.metabase-driver-0.1.1.jar)
```
docker cp clickzetta.metabase-driver-0.1.1.jar metabase-clickzetta:/plugins/clickzetta.metabase-driver.jar
```
4. To run Metabase on a different port, such as port 12345, you can use the following command:
   ```
   docker run -d -p 12345:3000 --name metabase-clickzetta metabase/metabase:latest
   ```
5. After starting, visit Metabase: `http://localhost:3000` (or another port you chose).

# Connect to Singdata Lakehouse

## Configure Database Connection

1. Log in to Metabase, then go to the "Admin Settings" page.
2. In the "Databases" section, click the "Add a database" button.
3. Select Singdata Lakehouse as the database type.
4. Fill in the database connection information, including hostname, port, database name, username, and password.
5. Click "Test connection" to ensure the connection is successful.
6. Click the "Save" button to complete the configuration.

![Add Singdata Lakehouse Database Connection](.topwrite/assets/image_1704980374686.png)

## Browse and Analyze Data

1. In Metabase, click the "Browse data" option in the left navigation bar.
2. Select the Singdata Lakehouse database you just configured.
3. You will see all the tables and views in the database. Click any table or view, and Metabase will automatically generate a data browsing interface for you.
4. You can filter, sort, and group the data to better analyze it.
5. To create more complex data visualization reports, click the "Create a dashboard" button in the top navigation bar of Metabase, then select the corresponding data table and visualization type.

![](.topwrite/assets/img_v3_02as_d2178f6d-8dae-430c-bce4-24714aae31ag.gif)

By following the above steps, you can easily connect and analyze data from the Singdata Lakehouse database in Metabase. Metabase provides rich data visualization options to help you better understand and present the data.