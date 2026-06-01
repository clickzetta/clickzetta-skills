# Getting Started: How to Quickly Run a SQL Query

## Applicable Scenarios

Lakehouse provides an integrated engine for data processing, transformation, and analysis, with SQL as its development language. This guide introduces how to quickly write and run a SQL statement for query analysis using the task development feature in Lakehouse Studio.

## Prerequisites

Before reading this guide, we recommend reviewing the following documents:

* [Lakehouse Product Introduction](what_is_clickzetta_lakehouse.md)
* [Key Concepts](key-concepts.md)
* [Lakehouse Studio Quick Tour](lakehousestudio-tour.md)

## How-to Guide

To quickly run a SQL query in the UI, use the Data Development module in Lakehouse Studio. There are two approaches:

### Method 1: Run with Sample SQL and Sample Data

The product includes ready-to-use sample code and accompanying sample data. In the page navigation, click **Development** to enter the Data Development interface, where you will see sample code files under the `Tpch_100g` folder. These samples demonstrate how to write SQL queries for quick analysis based on the Tpch_100g sample data, as shown below:

![](.topwrite/assets/image_1747993124883.png)

Double-click a sample code file to open it, then click the **Run** button in the upper-right corner of the page to trigger SQL execution. Once execution completes, you can view the results and logs in the lower-right area of the page.

![](.topwrite/assets/image_1747993372483.png)

^

Pay special attention to the **Cluster** option in the upper-right corner of the page. "Cluster" stands for "Compute Cluster," which is the core concept of how Lakehouse provides compute power. See [this document](virtual-cluster.md) for detailed information. When a workspace is created, two clusters are initialized by default: a general-purpose cluster named `DEFAULT` and an analytics cluster named `DEFAULT_AP`. These two types of clusters are optimized for different workloads:

* **General Purpose (GP)**: Suitable for offline job processing. Jobs share compute resources, and new and old jobs are scheduled fairly. Suitable for periodic scheduling tasks to process large volumes of data.
* **Analytics Purpose (AP)**: Features multiple compute instances and auto-scaling, suitable for online and high-concurrency jobs. Choose this cluster type if you want a better query performance experience. In addition, AP clusters perform intelligent data caching. After the first query, subsequent queries run faster. The following diagram illustrates this difference:

  ![](.topwrite/assets/image_1748326696659.png)

^

You can also learn more about query analysis using sample data by reading [Quick Start Query Analysis with Sample Data](sample-data-using.md).

### Method 2: Write and Run Your Own SQL

In addition to using sample code and sample data, you can also write and run your own SQL. In the page navigation bar, click **Development** to enter the Data Development interface. Under **Tasks**, create a SQL task file by selecting **SQL Script** from the new menu.

![](.topwrite/assets/image_1721484292583.png)

In the task file, follow these steps to write and run SQL:

1. Select the correct data Schema on the page. When writing code, you can reference tables under this Schema by their table names directly; otherwise, use the `schema.table` two-part or `workspace.schema.table` three-part format. Usually, the system default Schema is sufficient.

2. Enter the SQL you want to run in the code editing area.

3. Choose the appropriate compute cluster type. For ad-hoc queries or when you need faster query response times, the Analytics Purpose (AP) cluster is recommended. General Purpose (GP) clusters are suitable for large-volume offline, periodically scheduled task processing and analysis.

4. Click the run button on the left or the run button in the upper-right corner to execute the code. The left button only executes the code block where the cursor is located. The upper-right button executes all code by default; you can also select a portion of code first, then click the upper-right run button to execute only the selected portion.

   ![](.topwrite/assets/image_1721484303315.png)

5. After execution completes, you can view the results, duration, and run logs in the area at the bottom of the page:

   ![](.topwrite/assets/image_1721484312151.png)

6. While writing code in the editor, you can also switch to the **Data** tab to quickly browse and use data. After finding the desired table, you can quickly insert the table name, field names, or directly generate a sample query SQL from the action menu:

   ![](.topwrite/assets/image_1721484321409.png)

### Other Common Operations

In addition to the **Run** operation, the system provides the following features as shown below:

1. Global code search: Find files by code keywords
2. Save: Save changes to the current file
3. Format: Format the current code
4. Version history: View the file's version history, with support for comparison and rollback
5. Find: Search for code snippets within the current file by keyword
6. Shortcuts: Display supported common shortcuts

![](.topwrite/assets/image_1721531293556.png)

## Limitations

* Access control: Only users with the `workspace_admin` role or `workspace_dev` role can use the task development feature and run SQL.

## Related Documents

* Read [Task Development](ide.md) to learn more about the detailed features of the task development module.

## Next Steps

* [How to Quickly Upload and Import Local Data for Analysis](quick_start_upload_data.md)

^
