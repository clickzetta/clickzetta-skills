# Visual Data Analysis Platform

### 1. Singdata Insight Product Overview

【**Preview Release】This feature is currently in an invitation-only preview phase. If access is required, please contact our technical support team for assistance**.&#x20;

^

Singdata Insight is a powerful visual data analysis tool designed for data analysis and visualization after data integration and data development. By using Insight, users can easily create data reports and analysis dashboards, thereby understanding data more intuitively and supporting business decisions. The main use cases of Insight are as follows:　　

* **Create Daily Data Reports**: Quickly build the data reports needed for daily business, reducing the complexity of traditional data portal construction, allowing data developers to focus on underlying data development, while business analysts can build various business analysis reports based on data sets.
* **Self-Service Analysis**: Business personnel can directly use the data sets prepared by data developers to perform self-service analysis through simple drag-and-drop operations, improving the efficiency of data analysis and avoiding delays in viewing data due to scheduling issues.

### 2. User Operation Guide

Before using Singdata Insight, please ensure you have a Singdata account. The detailed operation steps are as follows:

#### 2.1 Singdata User Management

* **Log in to the System Management Console**: Log in to the system management console using your Singdata account.
* **Enter Insight**: Find and click Insight on the management console to enter the product.

#### 2.2 Singdata Insight Platform Operations

##### 2.2.1 Create Data Connection

* **Create a New Data Link**: On the data connection page, click the "Create New Data Link" button.
  ![](.topwrite/assets/image_1740572013979.png)

* **Select Data Source Type**: Choose the Singdata Lakehouse data source under Cloud.
  ![](.topwrite/assets/image_1740572033841.png)

* **Fill in JDBC Information**: Enter the necessary JDBC link information, such as database URL, username, and password.
  ![](.topwrite/assets/image_1740572056582.png)

* Name: Required, used as the management name of the data connection

* service: No need to fill in.

* username: Required, the username of the Singdata platform

* password: Required, the password to connect to the Singdata platform

* schema: Optional, the specific schema under the designated workspace of the Singdata account. Note that this database must be consistent with the schema in the JDBC string

* Data Gateway: None

* URL: jdbc\:clickzetta://「instance\_name」.api.singdata.com/「workspace under this account」?schema=specific schema\&virtualCluster=「cluster name under the current space」

* vcluster: Optional

* instance: Optional

* workspace: Workspace in the URL

##### 2.2.2 Create Data Set

* **Create a New Data Package**: On the data marketplace page, click "Create New Data Package" and select "Blank Data Package".
* **Create a New Data Set**: Click the "Create New Data Set" button within the data package.
* **Select Data Source**: Select the data source type and specific data table just created.
  ![](.topwrite/assets/image_1740572084178.png)

![](.topwrite/assets/image_1740572105464.png)

![](.topwrite/assets/image_1740572119991.png)

![](.topwrite/assets/image_1740572153093.png)

##### 2.2.3 Create BI Report

* **Create a New Analysis Application**: On the application creation page, click "Create New Analysis Application".
* **Create Dashboard**: Click "Create New Dashboard" to enter the dashboard building page.
* **Publish Dashboard**: After creation, click "Publish" to publish the dashboard to the application marketplace.

##### 2.2.4 View Report

* **View Data**: On the application marketplace page, click the corresponding report to view the data.

### 3. Usage Examples

Here are some specific examples of using Insight:

* **Sales Analysis**: Create a monthly sales report that includes sales revenue, sales volume, and sales growth rate to analyze the sales performance of various product lines.
* **Customer Behavior Analysis**: Build a dashboard that displays customer visits, dwell time, and conversion rates to analyze the effectiveness of different marketing activities.
* **Inventory Management**: Set up a real-time updated inventory report that includes inventory quantity, inventory turnover rate, and safety stock levels to help managers stay informed about inventory status.

### 4. Frequently Asked Questions (FAQ)

1. Why can't I see features like Data Marketplace and Application Marketplace?
   If you cannot see features like Data Marketplace and Application Marketplace, please confirm whether your user role has the corresponding permissions. If necessary, contact the system administrator to enable them.

2. Why do I have data analysis permissions but cannot create datasets?
   If you have data analysis permissions but cannot create datasets, please ensure you are operating under a data package. Only system administrators have the authority to create data packages.

3. How do I add users to the Insight product?
   To add users to the Insight product, please operate on the Singdata management console. Note that data synchronization may have a delay.

^
