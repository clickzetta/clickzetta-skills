# Singdata Insight: Visual Data Analysis Platform

> [Preview Release] This feature is currently in an invited preview release phase. If you need access, please contact our technical support team for assistance.

## 1. Singdata Insight Product Overview

Singdata Insight is a powerful visual data analysis tool designed for data analysis and visualization after data integration and development. By using Insight, users can easily create data reports and analysis dashboards, enabling a more intuitive understanding of data to support business decision-making. The following are the main usage scenarios for Insight:

* **Create Daily Data Reports**: Quickly build data reports needed for daily business operations, reducing the complexity of traditional data portal construction. Data developers can focus on underlying data development, while business analysts can build various business analysis reports based on datasets.
* **Self-Service Analysis**: Business personnel can directly use datasets prepared by data developers and perform self-service analysis through simple drag-and-drop operations, improving the efficiency of data analysis and avoiding situations where data cannot be viewed in a timely manner due to scheduling issues.

## 2. User Operation Guide

Before using Singdata Insight, please ensure you have a Singdata account. The following are detailed operation steps:

### 2.1 Singdata User Management

* **Log into the System Console**: Log into the system console using your Singdata account.
* **Enter Insight**: Find and click Insight on the console to enter the product.

### 2.2 Singdata Insight Platform Operations

#### 2.2.1 Create a Data Connection

* **Create a New Data Connection**: On the Data Connection page, click the "New Data Connection" button.
  ![](.topwrite/assets/image_1732698495607.png =604)

* **Select Data Source Type**: \* Select the Singdata Lakehouse data source under Cloud
  ![](.topwrite/assets/image_1732698470951.png =606)

* **Fill in JDBC Information**: Enter the necessary JDBC connection information, such as database URL, username, and password.
  ![](.topwrite/assets/image_1732698542969.png =514)

* Name: Required; serves as the management name for the data connection

* service: Do not fill in.

* username: Required; the Singdata platform username

* Password: Required; the password for connecting to the Singdata platform

* schema: Not required; the specific schema under the designated workspace of the Singdata account. Note that this database must be consistent with the schema in the JDBC string.

* Data Gateway: None

* URL: jdbc\:clickzetta://「instance_name.<region\_id>.api.clickzetta.com/「the workspace under this account」?schema=specific schema\&virtualCluster=「the cluster name under the current workspace」

* vcluster: May be left blank

* instance: May be left blank

* worspace: The workspace in the URL

#### 2.2.2 Create a Dataset

* **Create a New Data Package**: On the Dataset Market page, click "New Data Package" and select "Blank Data Package."
* **Create a New Dataset**: Click the "New Dataset" button within the data package.
* **Select Data Source**: Select the data source type just created and the specific data table.

  ![](.topwrite/assets/066f996216/a3111473bfd4f6f8f2d75a69f4b05826a0841765.png =728)

  ![](.topwrite/assets/066f996216/06fe9023d84c405e53fa72450406fa6acb512406.png =720)

  ![](.topwrite/assets/066f996216/a6704632ba99a0b514ea39e18d612f9ff52c9c18.png =630)

  ![](.topwrite/assets/066f996216/0c4db444079dcb819274c8653e196916c563bd3b.png =313)

#### 2.2.3 Create BI Reports

* **Create a New Analysis Application**: On the Application Authoring page, click "New Analysis Application."
* **Create a Dashboard**: Click "New Dashboard" to enter the dashboard construction page.
* **Publish the Dashboard**: After creation, click "Publish" to publish the dashboard to the Application Market.

  ![](.topwrite/assets/066f996216/026bda059ee55d9f2051ee2d8d741e97f2dedad9.png)

  ![](.topwrite/assets/066f996216/f6e1e90b6e5cf13e5850ff7697ce7542696881af.png)

  ![](.topwrite/assets/066f996216/9a6fe91f1cba92fb62adb1bbe0adcf17a0b05342.png =190)

#### 2.2.4 View Reports

* **View Data**: On the Application Market page, click the corresponding report to view the data.
  ![](.topwrite/assets/066f996216/86219be367b3bb5667f7cf46875c1e7956337a14.png =361)

## 3. Usage Examples

The following are specific examples of using Insight:

* **Sales Analysis**: Create a monthly sales report containing sales amount, sales volume, and sales growth rate to analyze the sales performance of each product line.
* **Customer Behavior Analysis**: Build a dashboard displaying customer visits, dwell time, and conversion rate to analyze the effectiveness of different marketing campaigns.
* **Inventory Management**: Build a real-time updated inventory report including inventory quantity, inventory turnover rate, and safety stock level to help managers stay informed of inventory status in a timely manner.

## 4. Frequently Asked Questions (FAQ)

1. Why can't I see the Dataset Market, Application Market, and other features?
   If you cannot see features such as Dataset Market or Application Market, please confirm whether your user role has the corresponding permissions. If needed, contact your system administrator for activation.

2. Why do I have data analysis permissions but cannot create a dataset?
   If you have data analysis permissions but cannot create a dataset, please ensure you are operating under a data package. Only system administrators have permission to create data packages.

3. How do I add Insight product users?
   To add Insight product users, please perform the operation on the Singdata console. Please note that data synchronization may have a delay.

^
