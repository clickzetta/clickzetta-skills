# DataGPT Quick Start

## Activate DataGPT Service

* Find the DataGPT product card on the "Home" page of the management center and click the "Activate for Free" button.&#x20;
* In the pop-up window, the **cloud service provider** Alibaba Cloud and **region** ap-southeast-1 will be specified by default. The system provides the option "**Activate Lakehouse instance** in **Alibaba Cloud** - **ap-southeast-1** **as the default data source**":![](.topwrite/assets/20250218-202455.jpeg)
* * **Check (recommended for new users**): The system will automatically activate the Lakehouse in Alibaba Cloud - **ap-southeast-1** as the default data source, no manual configuration is required.
  * **Uncheck**: The system will not automatically activate the Lakehouse instance in East China 2 (Shanghai). You can manually add it on the data source management page after the service is activated. Please note that in this case, **DataGPT will not include preset sample data**.
* Click "Activate" and after a short wait, you can enter the usage interface

&#x20;      ![](.topwrite/assets/20250218-200517.jpeg =783)

^

After the service is activated, you can start the DataGPT data analysis experience in various ways. To help you get started quickly, we provide the following analysis paths:

## Method 1: Use Sample Analysis Domain

Ask questions using the sample dataset: We have prepared a well-configured sample dataset for you, which includes a complete table configuration and indicator system. You can start asking questions directly to quickly experience the intelligent analysis capabilities. At the same time, this sample can also serve as a template to help you create an analysis domain suitable for your business scenarios.

Enter the product homepage, find the analysis domain marked "Sample" on the main page, click "Start Analysis" to enter the analysis homepage, and you can start asking questions.

![](.topwrite/assets/20250218-200800.jpeg)

## Method 2: Analyze Based on Your Own Data

The system supports importing various data formats, including CSV, Text, Excel, PDF, etc. You can create an independent analysis domain and start intelligent analysis and Q\&A after importing the data.

In this case, we will use the real business data of the famous Brazilian e-commerce platform Olist to demonstrate the system's data analysis capabilities. We will import the following core data files:

**Core Business Data**:

`olist_orders_dataset.csv.gz (Order Main Table)`

`olist_order_items_dataset.csv.gz (Order Item Details)`

`olist_order_payments_dataset.csv.gz (Payment Information)`

`olist_products_dataset.csv.gz (Product Information)`

**User and Seller Data**:

`olist_customers_dataset.csv.gz (Customer Information)`

`olist_sellers_dataset.csv.gz (Seller Information)`

These data files are compressed in gzip format (.gz) to improve transmission efficiency. The system will automatically decompress and recognize them. The data is linked through key fields such as order number (order\_id) and product number (product\_id) to form a complete business analysis data chain.

###

### Step 1: Create a New Analysis Domain

![](.topwrite/assets/20250218-200854.jpeg)

^

### Step 2: Basic Configuration

* **Analysis Domain Name**: Users need to fill in the analysis domain name, such as "Brazil Olist E-commerce Data Analysis"
* **Data Source**: Select LAKEHOUSE as the underlying data platform (default)

> **Data Source Restriction**: The tables, indicators, and base tables of the answer builder in the analysis domain must come from the same data source. Keep other options as default. Click **Confirm** to create the analysis domain.

Keep other options as default. Click **Confirm** to create the analysis domain.

^

### Step 3: Add Data

* After creating a new analysis domain, a prompt to add data will pop up. Click **Add Data -> Table**, then click **Start Adding**
* Select "**Upload File**" and add the above files to the system. Click **Next** to start parsing

:-: ![](.topwrite/assets/20250218-201126.jpeg =759)

* Click **Next** to upload data:![](.topwrite/assets/20250218-201200.jpeg =781)      &#x20;

^

> Note: In the file parsing interface, there is a mandatory verification requirement: all files displayed with gray dots must click the file name and confirm to display green before clicking the "Next" button to proceed to the next steps.
>
> ![](.topwrite/assets/20250218-201423.jpeg =703)

* Automatic Data Semantic Layer Construction:
  * Data Auto-Profiling: Automatically analyze the basic statistical characteristics of the dataset, including data distribution, missing values, outliers, and other key indicators
  * Intelligent Supplement of Column Descriptions and Aliases: Note: For aliases, the system has generated alias suggestions, which will take effect after selection
* Column type auto-recognition: Continuous, Categorical, Date\_And\_Time, Partition, and Other
  * Column usage: FILTER, DATETIME\_FILTER, DIM, MEASURE
  * Relationship auto-recognition: If more than one table is uploaded, the relationships will be automatically determined
  * Automatic metric recommendation: Automatically generate business-meaningful metrics
    ![](.topwrite/assets/20250218-201550.jpeg =775)

**Once the data is ready, you can start asking questions in natural language**.

^

:-: ![](.topwrite/assets/20250218-202239.jpeg =752)

^
^
