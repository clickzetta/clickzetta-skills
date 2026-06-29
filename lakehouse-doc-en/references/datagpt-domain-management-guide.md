# Configuring Analytics Domains

## Feature Overview

An analytics domain is a workspace in the Analytics Agent for organizing data analysis capabilities. Within an analytics domain you can configure data tables, metrics, complex metrics, a knowledge base, files, and member permissions, then initiate data analysis, generate charts, view SQL statements, or perform document Q&A using natural language.

An analytics domain typically corresponds to one business topic, such as sales analysis, recruitment analysis, member operations, financial performance, or industry sample data. After configuration, you do not need to write SQL directly — you can ask questions in natural language from the "Start Analysis" entry point.

The goal of analytics domain configuration is not simply adding data resources to the system, but proactively maintaining what business users should not need to understand: which tables belong to this business topic, what fields are called in business terms, how metrics are calculated, which knowledge explains business terminology, which users can see which data, and whether the configuration can be validated through real questions after completion. The more thoroughly the management and maintenance side does this work, the fewer technical details business users need to provide when asking questions, and the more stable answers become.

In other words, analytics domain configuration is transforming a general large language model into a usable, controllable, and verifiable Analytics Agent for the current business scenario. Without an analytics domain, field semantics, metrics, knowledge, permissions, and validation, the large model can only guess user intent based on table names and field names; with configuration complete, the model can answer questions within clear business context, definitions, and permission boundaries.

## Core Concepts

| Concept | Description |
| --- | --- |
| Analytics Domain | A collection of data, metrics, knowledge, files, and permissions; the business context from which you initiate analysis. |
| Data Table | Data objects that can be queried in the domain; can come from Lakehouse imported tables, CSV/Excel uploaded files, or existing tables. |
| Metric | An aggregation metric defined based on table fields, such as total account count, total sales revenue, or average order value. |
| Complex Metric | A metric requiring more complex SQL, detailed definitions, or business rule expressions. |
| Knowledge | A collection that helps the system understand proprietary terms, business definitions, synonyms, and explanatory text. |
| File | Uploaded files that support document Q&A. |
| Permission | Controls which users can view, analyze, or manage the analytics domain. |

## How Management Configuration Affects Q&A Quality

Business users see a natural language input box, but the effectiveness behind it depends on whether the management side has completed sufficient groundwork.

| If Users Want | Management Side Needs to Do in Advance |
| --- | --- |
| Ask about data without knowing table names | Analytics domain boundary is clear; only tables and files needed for the current business topic are added. |
| Be understood without knowing field names | Field aliases, descriptions, types, purposes, and hiding configurations are complete. |
| Not repeat metric definitions every time | Metrics, complex metrics, knowledge, or answer builders have already locked in the definitions. |
| Not worry about seeing unauthorized data | Analytics domain permissions, role authorization, row-level permissions, and column hiding are configured correctly. |
| Know what they can ask upon first entry | Recommended questions cover core business scenarios and have been validated through Q&A. |
| Have answers improve after being wrong | Feedback has someone reviewing, assigning, and fixing it, combined with audit logs to track changes. |

Therefore, launching an analytics domain should not only check "whether there are tables" but also check "whether business users can get correct answers using real-world phrasings". This is the core value of management configuration.

> 💡 **Tip**: Before configuring for the first time, it is recommended to first review [Analytics Domain Configuration Tips and FAQ](datagpt-domain-setup-tips.md) to avoid common pitfalls.

## Accessing Analytics Domain Management

1. Click "Analysis" in the left navigation.
2. The page displays all analytics domain cards, with "All / Mine / Examples" filtering.
3. Use "Search Analytics Domains" to find a target domain by name.
4. Click the analytics domain name to enter the detail page.
5. Click "Start Analysis" on a card to directly enter the Q&A page for that domain.

In the analytics domain list, the "Create New Analytics Domain" card is used to create a new domain; existing domain cards provide Start Analysis, Configure, and More Actions entry points.

## Creating a New Analytics Domain

1. Click "Create New Analytics Domain" in the analytics domain list.
2. Enter the analytics domain name.
3. Select the data source. Currently supports Lakehouse data sources.
4. Enter notes, recommending to describe the business scope, data source, and applicable user group.
5. To adjust answer generation behavior or switch LLM model, expand "Advanced Settings". Default decimal places and prompt configurations can be set here; model selection and team model pool management are in [Model Selection and Configuration](datagpt-model-config.md).
6. After saving, enter the analytics domain management page to continue configuring data and permissions.

When creating a domain, note: the tables in an analytics domain, as well as the underlying tables for metrics and answer builders, can only come from the same data source. Once the data source is selected, subsequent table additions will be within that data source.

After creation, the system shows a configuration guide. It is recommended to click "Add Data" to continue with table, metric, and other configurations; if you click "Not Now", you can later enter domain management from the Configure entry on the analytics domain card.

Naming recommendations:

- Use a clear business topic, such as "Sales Performance Analysis" or "Recruitment Funnel Analysis".
- For test domains, add a date or purpose identifier, such as `test_sales_domain_20260608`.
- Avoid names that only use `demo`, `test`, or other terms that cannot distinguish business content.

## Analytics Domain Detail Page

The top of the analytics domain detail page shows breadcrumbs, Start Analysis, Edit, and More Actions entry points. The main body contains three tabs:

| Tab | Purpose |
| --- | --- |
| Basic Information | View domain name, data source, creator, creation time, notes, recommended questions, and health check information. |
| Data | Configure tables, metrics, complex metrics, knowledge, and files. |
| Permissions | Configure which users can access or manage this analytics domain. |

### Basic Information

The Basic Information tab is for viewing analytics domain metadata and recommended questions.

If a newly created domain has no data added yet, the Basic Information page shows "You have no data yet, please add data" in the "Data Health" area, with a "Click to Go" button. Clicking it switches to the "Tables" module of the "Data" tab, guiding you to add tables.

After entering a newly created domain by clicking "Add Data" from the "Creation Successful" popup, the Basic Information page also shows a "What data can be added to analytics domains" guide area at the bottom:

| Type | Page Description |
| --- | --- |
| Tables | Data Q&A based on CSV/Excel files or imported tables. |
| Metrics | Define aggregation-type metrics. |
| Answer Builders | Define complex or detail metrics. |
| Files | Document Q&A on uploaded files. |

Click "Start Adding" to continue to the data configuration process.

Recommended questions help end users quickly understand what questions the domain can answer. It is recommended to configure at least 3 to 5 high-quality recommended questions before publishing the domain, such as:

- How many accounts are there in total?
- Count accounts by country.
- What is the account distribution across different plans?
- What is the trend of new accounts over the last month?

### Data Tab

The Data tab is the core configuration area for an analytics domain, containing five types of configuration:

| Configuration Type | Purpose |
| --- | --- |
| Tables | Data Q&A based on CSV/Excel files or imported tables. |
| Metrics | Define aggregation-type metrics. |
| Complex Metrics | Define complex or detail metrics. |
| Knowledge | Help the system understand proprietary terms, definition explanations, and synonym expressions. |
| Files | Document Q&A on uploaded files. |

## Adding Tables

Click "Add Table" in "Data > Tables". The system provides three entry points:

| Entry Point | Applicable Scenario |
| --- | --- |
| Import Table | Select physical tables from Lakehouse workspaces, databases, and schemas and import them to the current domain. |
| Upload File | Upload CSV/Excel files and create queryable data tables based on the files. |
| Select Existing Table | Add a data table that has already been created in the system to the current analytics domain. |

### Using "Import Table"

1. Click "Add Table".
2. Select "Import Table".
3. The data source type will be fixed to the data source selected when creating the analytics domain, e.g., `LAKEHOUSE`.
4. Expand the Workspace, e.g., `ns227206`, `quick_start`, `sys`.
5. Select the Namespace / Schema.
6. Check the tables to add in the table list on the right. The drawer bottom shows "Selected objects to add to domain" and the current analytics domain name.
7. Click "Next".
8. The system automatically generates field configurations including field type, column type, purpose, and index suggestions. Auto-detected results may not match business semantics and require manual review later.
9. After confirming the field configuration, click "Next".
10. The system may automatically generate metrics based on fields; check the metrics to adopt.
11. Click "Complete and Start Analysis".

If the target Lakehouse Workspace is not shown in the Add Table drawer, the page will prompt that the system user `sysservice_decision` may not have been added to the target workspace. A user with the `workspace_admin` role needs to execute:

```sql
create user sysservice_decision;
grant role workspace_admin to user sysservice_decision;
```

### Using "Upload File"

After selecting "Upload File" in the "Add Table" drawer, you can click or drag files to the upload area. The page shows support for:

- CSV files.
- TXT files.
- Excel files.
- `gzip` / `zip` compressed format files.

The limit is a single file smaller than 50MiB, with up to 8 files of the same format uploadable at once. After uploading, the system creates a queryable data table from the file. Field names, types, descriptions, and purposes still need to be checked afterwards.

### Using "Select Existing Table"

"Select Existing Table" is used to add existing `v_gpt_*` table assets in the system to the current analytics domain. The list shows:

| Column | Description |
| --- | --- |
| Table Name | System-generated or maintained queryable table name, e.g., `ns227206.public.v_gpt_accounts`. |
| Display Name | Data object name displayed to users, e.g., `ns227206.public.accounts`. |
| Description | Business description of the existing table. |
| Creator | Creator of the table asset. |

This entry point supports search, pagination, and multi-selection. After selecting tables and clicking "Confirm", the tables appear in the "Tables" list of the current analytics domain.

### What to Do When a Table Is Grayed Out and Unselectable

If a table in the table list is grayed out and cannot be checked, it means the table has already been imported or already exists in the system. Do not try adding it again from the "Import Table" entry.

Correct approach:

1. Return to the top of the "Add Table" drawer.
2. Switch to "Select Existing Table".
3. Search for the target table name.
4. Check the existing table.
5. Add to the current analytics domain.

This avoids duplicate importing of the same physical table, and can usually reuse existing table and field configurations. Whether metrics are available still needs to be confirmed in the current analytics domain.

### Table List After Being Added to the Domain

After a table is successfully added to the analytics domain, the "Data > Tables" list shows:

| Column | Description |
| --- | --- |
| Table Display Name | Table name visible to business users. Clicking this name enters the table detail page. |
| Table Name | The actual `v_gpt_*` view or table used for Q&A. |
| Data Source | E.g., `LAKEHOUSE`. |
| Table Association | Association status between the current table and other tables. Shows "None" when there is no association. |
| Creator | Creator of the table asset. |
| Update Time | Most recent update time of the table asset. |
| Notes | Table notes. |
| Actions | Allows removing the table from the current analytics domain. |

Note: "Remove" only dissociates the table from the current analytics domain and does not delete the Lakehouse physical table.

## Configuring Table Details

Tables added to the domain still have many configurable items. Do not stay on the analytics domain's table list page — click "Table Display Name" to enter the table detail page for further configuration.

The table detail page includes:

| Area | Purpose |
| --- | --- |
| Top information | Shows table display name, view name, description. |
| Edit | Modify table display name and table description. |
| Upload | Re-upload or refresh related data. |
| Table Structure | Configure fields, virtual columns, indexes, hiding, column types, purposes, table associations. |
| Data Preview | View the first 10 rows of preview data. |
| Statistical Analysis | View field statistical information. |

### Editing Table Information

Click "Edit" on the table detail page to open the "Edit Table" dialog, where you can configure:

| Configuration | Description |
| --- | --- |
| Table Display Name | The table name visible to users in the analytics domain; recommended to use a business-understandable name. |
| Table Description | Describes the data scope, update frequency, business meaning, and usage notes of the table. |

### Table Structure Field Configuration

The table structure page shows a field list. Practical field columns include:

| Configuration | Review Recommendations |
| --- | --- |
| Name | Confirm the field name matches the physical table. |
| Alias | A more user-friendly name, e.g., `account_id` can be configured as "Account ID". |
| Type | Confirm numeric, string, time, and other types are correctly identified. |
| Description | Add business explanations where possible to reduce Q&A ambiguity. |
| Column Type | Distinguish continuous, categorical, time, and other value types. |
| Purpose | Distinguish dimension, filter condition, and measure fields. |
| Table Association | For multi-table analysis, confirm whether join relationships are reasonable. |
| Index Management | Controls whether a field participates in indexing, affecting retrieval and Q&A recall. |
| Hidden | Controls whether a field participates in Analytics Agent Q&A understanding and result display; does not replace underlying data permissions. |
| Refresh Time | Shows the most recent refresh time of field configuration or detection results. |

Field description quality directly affects natural language Q&A effectiveness. Key fields should have clear descriptions.

Common column type and purpose examples:

| Type or Purpose | Meaning |
| --- | --- |
| `CATEGORICAL` | Categorical field, e.g., `plan`, `country`. |
| `CONTINUOUS` | Continuous numeric field, e.g., `seats`. |
| `DATE_AND_TIME` | Date or time field, e.g., creation time, order time. |
| `PARTITION` | Partition field, used to indicate data partitioning or partition range. |
| `OTHER` | Other types; virtual columns may default to this type. |
| `DIM` | Can be used as an analysis dimension. |
| `FILTER` | Can be used as a filter condition. |
| `MEASURE` | Can be used as a measure field for aggregation. |

Practical column type dropdown options include:

- `CATEGORICAL`
- `CONTINUOUS`
- `DATE_AND_TIME`
- `PARTITION`
- `OTHER`

Practical field purpose options include:

- `DIM`
- `FILTER`
- `MEASURE`

A single field can have multiple purposes. For example, `id` can show both `DIM` and `FILTER`; `seats` can show both `FILTER` and `MEASURE`.

### Table Auto-Association

"Auto-Association" lets the system automatically identify possible table relationship associations based on field information across multiple tables in the domain.

Practical behavior:

1. When the domain has only 1 table, the "Auto-Association" button is grayed out and cannot be clicked.
2. When the domain has 2 or more tables, the button becomes clickable.
3. After clicking, "Associating..." is shown; after detection completes, a "Confirm Association" dialog opens.
4. The dialog table columns include "Source Table", "Source Column", "Target Table", "Column", "Source Column:Target Column".
5. If the system does not identify any association, the dialog shows "No table associations found".

Testing with `ns227206.public.v_gpt_accounts` and `quick_start.cat_litter.v_gpt_category_mapping`, the auto-association dialog showed "No table associations found", indicating that auto-association does not force-generate JOINs — it only provides candidate associations when field names, field semantics, or data relationships meet detection criteria.

In the `gaming_profiles_playstation` domain, which already has multiple tables related to games, players, achievements, and prices, clicking "Auto-Association" detected a candidate relationship:

| Source Table | Source Column | Target Table | Target Column | Relationship |
| --- | --- | --- | --- | --- |
| `quick_start.gaming_profiles_playstation.prices` | `gameid` | `quick_start.gaming_profiles_playstation.games` | `gameid` | `n:1` |

This shows auto-association can detect candidate primary-foreign key relationships, but does not complete business confirmation for you. The administrator needs to determine whether the relationship conforms to the actual data model before deciding whether to save.

Recommendations:

- Auto-association results must be manually confirmed before saving.
- If the dialog shows "No table associations found", manually check whether the two tables actually have joinable fields.
- Do not arbitrarily configure JOINs just to make multi-table Q&A work; incorrect JOINs can cause data bloat or metric definition errors.
- After configuration, validate results using typical questions and SQL to confirm they meet business expectations.

After table associations are configured, the "Table Association" column in the analytics domain table list shows which tables the current table is associated with. You can also enter the table detail page and at the field level see which table and field a specific field is associated with. For example, `purchased_games` table's `playerid` is associated with the player table, and `library` is associated with the games table. Field-level relationships help the system choose the correct JOIN path in multi-table Q&A.

### Creating Virtual Columns

Virtual columns are used to calculate a new analysis field based on existing fields, suitable for concatenation, transformation, classification, and derived label scenarios.

Steps:

1. Enter the table detail page.
2. Open the "Table Structure" tab.
3. Click "Create Virtual Column".
4. Enter the field name.
5. Enter the expression in the SQL editor.
6. Click `Run` to validate.
7. If "Run successful" is shown with sample data, click "Confirm" to save.

Practical example: generate a full name field based on `first_name` and `last_name`.

```sql
concat(first_name, ' ', last_name)
```

After clicking `Run`, the page shows "Run successful" and displays sample data, such as:

```text
Macy Kub
Kim Cormier
Princess Tillman
Jeramie Pfannerstill
Clay Johnston
```

After confirming and saving, the field count changes from 16 to 17. In this test, the new field displayed as "Virtual Column" in the table structure list, type was identified as `string`, column type as `OTHER`, and purpose as `FILTER`. After saving, return to the field list to check whether the field name, alias, description, column type, and purpose meet expectations; if auto-detection results are inappropriate, continue editing the field configuration.

Virtual column SQL recommendations:

- Reference only fields that already exist in the current table.
- Write simple expressions first and validate with `Run`.
- For string concatenation, date conversion, and numeric bucketing scenarios, prioritize Lakehouse-supported SQL functions.
- After saving, add field aliases and descriptions so users understand what the virtual column represents.

### Data Preview

The "Data Preview" tab shows quick table data. The page shows "Preview shows only the first 10 rows of data". If the preview area shows "No data", investigate using table data refresh, permissions, view SQL, and data source status.

### Statistical Analysis

The "Statistical Analysis" tab shows statistical results by field. Practical columns include:

| Statistical Item | Description |
| --- | --- |
| `COUNT` | Field count. |
| `NULL VALUE` | Number of null values. |
| `DISTINCT` | Number of distinct values. |
| `MIN` | Minimum value. |
| `MAX` | Maximum value. |
| `AVERAGE` | Average value. |
| `SUM` | Sum. |
| Partition range | Partition field or partition range information. |

For example, the `id` field statistics show `COUNT` as 2,495, `NULL VALUE` as 0, `DISTINCT` as 2,493, `MIN` as 1, `MAX` as 2,495. Before launch, it is recommended to review statistical analysis to confirm whether key fields have many null values, anomalous minimum/maximum values, or obviously unreasonable distinct counts.

## Configuring Metrics

Metrics are used to stably answer questions like "total count, average, maximum, minimum, proportion, amount total".

After importing tables, the system may automatically generate metrics, such as:

- Total account count: `COUNT(id)`
- Total seat count: `SUM(seats)`
- Average seat count: `AVG(seats)`
- Latest creation time: `MAX(created_at)`
- Earliest trial end time: `MIN(trial_ends_at)`

It is recommended to adopt clearly reasonable auto-generated metrics and manually check names and definitions. For metrics with complex business definitions, use "Complex Metrics" or "Answer Builders" for configuration — see [Metrics and Answer Builders](metrics_answer_build.md).

## Configuring Knowledge

Knowledge is used to supplement business semantics that the system cannot understand from table fields alone, such as:

- Proprietary term explanations.
- Metric definition descriptions.
- Field synonyms.
- Business abbreviations.
- Internal organizational conventions.

Examples:

| Term | Explanation |
| --- | --- |
| Active account | Accounts where `active_subscription` is currently true. |
| Trial conversion | `trial_converted` being true means a trial account has converted to a paid account. |
| Plan | The `plan` field indicates the product plan an account has subscribed to. |

## Configuring Files

Files are for document Q&A scenarios. You can upload product manuals, contracts, policy documents, business specification documents, etc., and then ask questions in the analytics domain about the file contents.

After clicking "Add File" in "Data > Files", the system provides two entry points:

| Entry Point | Description |
| --- | --- |
| Upload File | Upload new document Q&A files. |
| Select Existing File | Select from existing files in the system and associate them with the current analytics domain. |

When uploading files, the page shows support for Excel files `.xlsx`, text files `.txt`, and PDF files `.pdf`, with a maximum of 10MiB. The Excel upload area provides a "Download Template" entry. When selecting existing files, the list shows file names, creators, update times, and supports search and pagination.

Recommendations:

- Confirm file content is relevant to the analytics domain topic before uploading.
- File names should be clear.
- Avoid uploading duplicate, outdated, or unrelated documents.
- Files containing sensitive information should have permission scope confirmed first.

## Permission Management

In the "Permissions" tab, you can configure which users can access or manage the analytics domain.

Permission configuration recommendations:

- Domain owners retain write permissions.
- Users who only need Q&A are granted access or usage permissions.
- Domains with sensitive data should be restricted to the minimum necessary personnel.
- Before revoking a user's permissions, confirm whether they are still responsible for maintaining metrics, fields, or recommended questions.

## Starting Analysis

After completing configuration, you can start analysis through:

1. The "Start Analysis" button on the analytics domain list.
2. The "Start Analysis" button in the upper right corner of the analytics domain detail page.
3. The "Complete and Start Analysis" button after finishing the add table flow.

After entering the analysis page, you can ask questions directly in the input box, such as:

- How many accounts are there in total?
- Count accounts by country.
- How are accounts distributed across different plans?
- What is the average seat count?

The system returns analysis results, which may include numeric cards, charts, text explanations, and SQL statement entry points.

## Viewing SQL and Analysis Logs

After a response is generated, the result area typically provides:

| Action | Description |
| --- | --- |
| SQL Statements | View the SQL generated and executed by the system to verify definitions. |
| Logs | View analysis process or execution logs. |
| Retry | Regenerate the response. |
| Feedback | Provide feedback on response quality. |

It is recommended to check SQL using typical questions before launch to confirm it meets business expectations.

## Editing, Copying, and Deleting Analytics Domains

The upper right corner of the analytics domain detail page provides common management actions:

| Action | Description |
| --- | --- |
| Edit | Modify name, notes, and other basic information. |
| Copy | Copy a new analytics domain based on the current one, suitable for reusing configurations. |
| Delete | Delete the current analytics domain. |

Before deleting, confirm:

- The domain is no longer used by any users.
- Recommended questions, permissions, metrics, and knowledge configurations do not need to be preserved.
- Whether related analysis history still needs to be preserved or exported.
- Delete operations are generally irreversible and should be executed with caution.

## Related Documentation

- [Analytics Domain Configuration Tips and FAQ](datagpt-domain-setup-tips.md) — 9 configuration principles, 6 FAQs, health checks, and recommended flow
- [Metrics and Answer Builders](metrics_answer_build.md) — Precise configuration and SQL templates for complex metrics
- [Improving Q&A Accuracy](answer-accuracy-improve.md) — Using semantic layer configuration to make answers more accurate
- [Model Selection and Configuration](datagpt-model-config.md) — Switching or configuring the LLM model used for Q&A
- [Data Source Management](datagpt_data_source.md) — Adding external data sources such as MySQL, StarRocks, and Databricks
- [Quick Start](datagpt_quickstart.md) — Run your first data Q&A in 5 minutes

## Example: Minimum Configuration for an Account Analytics Domain

Assuming you need to create an account analytics domain, configure it as follows:

| Configuration | Example |
| --- | --- |
| Analytics domain name | Account Operations Analysis |
| Data table | `ns227206.public.v_gpt_accounts` |
| Core metrics | Total account count, total seat count, average seat count |
| Core fields | `id`, `plan`, `country`, `created_at`, `active_subscription` |
| Recommended questions | How many accounts are there in total? Count accounts by country. How are accounts distributed across different plans? |
| Knowledge | Term explanations for active account, trial conversion, plan, etc. |

Validation question example:

```text
How many accounts are there in total?
```

If correctly configured, the system should return the total account count with the corresponding table or SQL evidence.
