# Singdata Insight: Visual Data Analytics Platform

> [Preview Release] This feature is currently in an invite-only preview release stage. If you need access, please contact our technical support team for assistance.

## Singdata Insight Product Overview

Singdata Insight is a powerful visual data analytics tool designed for data analysis and visualization after data integration and data development. Using Insight, users can easily create data reports and analysis dashboards to understand data more intuitively and support business decisions. The main use cases for Insight are as follows:

* **Create daily data reports**: Quickly build data reports for daily business needs, reducing the complexity of traditional data portal setup. This allows data developers to focus on underlying data development, while business analysts can build various business analysis reports based on datasets.
* **Self-service analysis**: Business users can directly use datasets prepared by data developers, performing self-service analysis through simple drag-and-drop operations, improving data analysis efficiency and avoiding delays caused by scheduling issues.

## User Operation Guide

Before using Singdata Insight, make sure you already have a Singdata account. The detailed operation steps are as follows:

### 1 Singdata User Management

* **Log in to the System Admin Console**: Log in to the system admin console using your Singdata account.
* **Enter Insight**: Find and click Insight in the admin console to enter the product.

### 2 Singdata Insight Platform Operations

#### 2.1 Create a Data Connection

* **Create a new data link**: On the data connection page, click the "New Data Link" button.
  ![](.topwrite/assets/image_1732698495607.png =604)

* **Select the data source type**: Select the Singdata Lakehouse data source under Cloud.
  ![](.topwrite/assets/image_1732698470951.png =606)

* **Fill in JDBC information**: Enter the required JDBC connection details, such as the database URL, username, and password.
  ![](.topwrite/assets/image_1732698542969.png =514)

* Name: Required. Used as the management name for the data connection.

* service: Leave blank.

* username: Required. The username for the Singdata platform.

* password: Required. The password to connect to the Singdata platform.

* schema: Optional. The specific schema under the designated workspace in the Singdata account. Note that this database must match the schema in the JDBC connection string.

* Data gateway: None.

* URL: jdbc\:singdata://`instance_name.<region_id>.api.singdata.com/`[workspace under this account]`?schema=`[specific schema]`&virtualCluster=`[cluster name under current workspace]

* vcluster: Optional.

* instance: Optional.

* workspace: The workspace specified in the URL.

#### 2.2 Create a Dataset

* **Create a new data package**: On the data marketplace page, click "New Data Package" and select "Blank Data Package".
* **Create a new dataset**: Inside the data package, click the "New Dataset" button.
* **Select the data source**: Select the data source type and specific data table you just created.

  ![](.topwrite/assets/066f996216/a3111473bfd4f6f8f2d75a69f4b05826a0841765.png =728)

  ![](.topwrite/assets/066f996216/06fe9023d84c405e53fa72450406fa6acb512406.png =720)

  ![](.topwrite/assets/066f996216/a6704632ba99a0b514ea39e18d612f9ff52c9c18.png =630)

  ![](.topwrite/assets/066f996216/0c4db444079dcb819274c8653e196916c563bd3b.png =313)

#### 2.3 Create a BI Report

* **Create a new analysis application**: On the application authoring page, click "New Analysis Application".
* **Create a dashboard**: Click "New Dashboard" to enter the dashboard building page.
* **Publish the dashboard**: After creation, click "Publish" to publish the dashboard to the application marketplace.

  ![](.topwrite/assets/066f996216/026bda059ee55d9f2051ee2d8d741e97f2dedad9.png)

  ![](.topwrite/assets/066f996216/f6e1e90b6e5cf13e5850ff7697ce7542696881af.png)

  ![](.topwrite/assets/066f996216/9a6fe91f1cba92fb62adb1bbe0adcf17a0b05342.png =190)

#### 2.4 View Reports

* **View data**: On the application marketplace page, click the corresponding report to view data.
  ![](.topwrite/assets/066f996216/86219be367b3bb5667f7cf46875c1e7956337a14.png =361)

## Usage Examples

The following are some specific examples of using Insight:

* **Sales analysis**: Create a monthly sales report containing sales revenue, sales volume, and sales growth rate to analyze the sales performance of each product line.
* **Customer behavior analysis**: Build a dashboard showing customer visit count, dwell time, and conversion rate to analyze the effectiveness of different marketing campaigns.
* **Inventory management**: Set up a real-time inventory report including inventory quantity, inventory turnover rate, and safety stock levels to help managers stay informed about inventory status.

## Frequently Asked Questions (FAQ)

1. Why can't I see features like the data marketplace or application marketplace?
   If you cannot see features such as the data marketplace or application marketplace, please confirm whether your user role has the corresponding permissions. If needed, contact the system administrator to enable access.

2. Why do I have data analysis permissions but cannot create a dataset?
   If you have data analysis permissions but cannot create a dataset, make sure you are operating within a data package. Only system administrators have permission to create data packages.

3. How do I add users for the Insight product?
   To add users for the Insight product, perform the operation in the Singdata admin console. Please note that data synchronization may have a delay.
