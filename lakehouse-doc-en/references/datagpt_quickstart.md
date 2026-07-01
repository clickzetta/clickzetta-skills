# Analytics Agent Quick Start

This guide helps you configure Analytics Agent from scratch and run your first data Q\&A. After completing it, you will be able to ask questions about your own data in natural language and receive charts and analysis summaries.

The diagram below shows the complete user journey. This guide covers the core steps of Phase 1 and Phase 2:

:-: ![](/.topwrite/assets/image_1780894528587.png =635)

## Activate Analytics Agent Service

* Find the Analytics Agent product card on the "Home" page of the management center and click the **Activate for Free** button.&#x20;

:-: ![](/.topwrite/assets/image_1780898507274.png =536)

* In the pop-up window, the **cloud service provider** Alibaba Cloud and **region** East China 2 (Shanghai) will be specified by default. The system provides the option "**Simultaneously activate a Singdata Lakehouse instance in Alibaba Cloud - East China 2 (Shanghai) as the default data source**":
  * **Check (recommended for new users**): The system will automatically activate Lakehouse as the default data source with pre-loaded sample data, requiring no manual configuration.
  * **Uncheck**: After the service is activated, manually add a data source on the data source management page. No pre-loaded sample data will be included.&#x20;
* Click **Activate** and after a short wait, you can enter the usage interface.

## Method 1: Use the Sample Analysis Domain

We have prepared a well-configured sample dataset for you, which includes a complete table configuration and metric system. You can start asking questions directly to experience intelligent analysis. This sample can also serve as a template to help you understand how to build your own analysis domain.

Go to the product home page, find the analysis domain labeled "Sample", and click **Start Analysis**.&#x20;

:-: ![](/.topwrite/assets/image_1780898646591.png =583)

## Method 2: Analyze Based on Your Own Data

The system supports importing multiple data formats including CSV, Excel, and PDF. The following uses real data from the Brazilian e-commerce platform Olist to demonstrate the complete workflow.

### Step 1: Create a New Analysis Domain

:-: ![](/.topwrite/assets/image_1780898786853.png =571)

### Step 2: Basic Configuration

* **Analysis domain name**: Enter a name, e.g., "Brazil Olist E-commerce Data Analysis"
* **Data source**: Select the underlying data platform (default is LakeHouse). To connect MySQL, StarRocks, Databricks, or other external databases, refer to [Data Source Management](datagpt_data_source.md).
* **Model**: The system uses the default model; you can switch at any time on the conversation page. To uniformly configure models available to your team, refer to [Model Selection and Configuration](datagpt-model-config.md).

Leave other options as default and click **Confirm** to create the analysis domain.

> **Note**: The tables, metrics, and answer builder base tables in an analysis domain must all come from the same data source.

### Step 3: Add Data

* After creating the analysis domain, click **Add Data → Table**, then click **Start Adding**.
* Select **Upload File**, add the following data files, and click **Next** to start parsing.
* Click **Next** to upload data:      &#x20;

:-: ![](/.topwrite/assets/image_1780898941921.png =683)

> ⚠️ **Note**: In the file parsing interface, all files showing a gray dot must be clicked to confirm (showing green) before you can click "Next".

### Step 4: Automatic Semantic Layer Construction

After upload is complete, the system automatically analyzes the data and constructs the semantic layer, including column descriptions and aliases, column type recognition, table relationship inference, and basic metric recommendations.

:-: ![](/.topwrite/assets/image_1780899052078.png =528)

The semantic layer is the foundation for the Agent to understand your data. If you find that Q\&A results are inaccurate (e.g., wrong metric calculation or wrong table selected), you can improve the semantic layer to resolve it — refer to [Answer Accuracy Improvement](answer-accuracy-improve.md).

### Step 5: Start Q\&A

Once the data is ready, ask questions in natural language directly, e.g., "What is the sales trend by region over the past 6 months?"

After you are satisfied with the results, you can further:

* **Adjust table layout**: Describe the layout and colors you want through conversation — refer to [Table Rendering](table_rendering.md)
* **Save as a dashboard**: Save analysis results with one click; supports multi-version management — refer to [Dashboard Version Management](dashboard-version-management-guide.md)
* **Set up auto-refresh**: Let dashboard data update automatically without manual refresh — refer to [Chart Auto-Refresh](chart-auto-refresh-guide.md)
* **Set up scheduled tasks**: Let the Agent automatically run analysis on a schedule and push results to email — refer to [Scheduled Tasks](scheduled_task.md)
* **Share dashboards and control permissions**: Set visible data ranges for different users — refer to [Row-Level Permissions](row_level_permission.md)
* **Integrate into business systems**: Embed Q\&A capabilities into your own system via API — refer to [Open API](open-api-overview.md)

## Related Documentation

* [Data Source Management](datagpt_data_source.md) — Add more types of data sources (MySQL, StarRocks, Databricks)
* [Model Selection and Configuration](datagpt-model-config.md) — Switch or configure the LLM used for Q\&A
* [Answer Accuracy Improvement](answer-accuracy-improve.md) — Make answers more accurate through semantic layer configuration
* [Row-Level Permissions](row_level_permission.md) — Set data access ranges for different users
* [Open API](open-api-overview.md) — Integrate Q\&A capabilities into your system

^
