# ﻿Data Catalog

## Overview

The Data Catalog provides powerful data retrieval and visualization capabilities, designed to help users find, understand, and utilize data more easily. It supports two modes: Data Search Mode and Data Management Mode. In Data Search Mode, users can directly search for data, while Data Management Mode allows users to locate and manage data tables through a directory structure. With the data catalog, you can manage and utilize data resources more efficiently.
![](.topwrite/assets/image_1740369561047.png)

* Asset Details: Displays the total data assets of the current tenant.

* Search Box: Click to enter the data search results page.

* Data Management: Click to enter the data management page.

* Upload Data: A lightweight entry for uploading local files.

* Recently Viewed / Newly Created: Shows the top 5 most recently viewed or created data tables under the current tenant. Click to directly access the table details page.

^

## Data Search

Enter keywords in the search box on the data catalog homepage to access the search results page. The search function supports searching by name and description for object types such as **Table, View, and Materialized View**.

The search results page offers multiple filtering options, including **object type, workspace/schema, creation time, and owner**, as well as sorting options by **name, creation time, and update time**.

For search result filtering, users can:

* Filter by **object type, workspace/schema, creation time, and owner**.
* Sort results by **name, creation time, and update time**.

Click on a table name in the search results page to navigate to the corresponding **Table Details Page**.

^

## Data Management

The **Data Management** page displays all data assets that the current user has permission to manage in the service instance, organized in a directory structure. Click “**Data Management**” on the homepage to enter the **Data Management** page, where you will see a list of workspaces that the user has access to within the current service.

^

### Workspace Level

At the **Workspace Level**, you can view all **Schemas** within the workspace. Click the left-side directory tree to expand and browse different levels. The **top section** displays basic workspace information such as **source, creation time, last modified time, and owner**. The **information section** presents details of each **Schema**, including **name, creation time, last update time, and owner**.

Each workspace contains a **default** \`\`.
Schemas within a workspace can be **internally created** or **externally created**.

^

Users can **visually create** schema information within a workspace. Click the **question mark** next to the title to access the **help documentation** for schema creation.

###

### Schema Level

Clicking on a specific **Schema** navigates to its **Schema Details Page**.
At the **Schema Level**, you can view all objects managed within the schema, categorized by object type. The system currently supports the following object types:

* **Table**
* **View**
* **Materialized View**

Users can create objects directly within a schema using either **script-based creation** or **visual creation**. The system provides **built-in templates** for different object types to help users better understand **Lakehouse syntax**.

## \*\*\*\*

## Table Details Page

The **Table Details Page** displays comprehensive information about tables stored in the **Lakehouse**, including:

* Table details
* Field information
* Data preview
* Data lineage
* Job history
* Upload history

This page is divided into two sections:

1. **Top Section** – Displays the **table name, owner, and quick actions**.
2. **Information Section** – Contains six tabs: **Details, Fields, Preview, Lineage, Jobs, and Uploads**.

### Top Section

The **top section** provides:

* The **full table path** (workspace/schema/table name).
* Basic information such as **number of rows, storage size, creation time, last update time, and owner**.
* An **Upload** function, allowing users to upload local files to the **Lakehouse platform**.

### Details Tab

* Displays the **DDL statement** of the current table.
* Supports **one-click copy** of the DDL statement.
* Provides a **one-click** shortcut to the **permission management page** for granting access.

### Fields Tab

* Displays **column names, data types, and descriptions**.
* If primary keys and standardization tags exist, they will also be displayed.

### Preview Tab

* Allows users to **preview up to 100 rows** of data from the current table.
* **Data access permissions apply**—only users with **SELECT permissions** on the table can view the preview.
* To generate a data preview, the user must **manually select a compute cluster** for query execution.

### Lineage Tab

* Displays **upstream and downstream dependencies** of the current table.
* The lineage relationships are derived from **code analysis of the jobs that produced the table**, representing a "**definition-level**" relationship.
* Clicking on an **upstream** or **downstream** table node provides **more detailed information**.

### Jobs Tab

* Displays **SQL jobs** that generated the table.
* Clicking on a **Job ID** allows users to view **job details**.

### Upload Tab

* Lists **all historical uploads** to the table via the **Upload** function.

^

## Upload Data

Please refer to [this document](upload_data.md).
