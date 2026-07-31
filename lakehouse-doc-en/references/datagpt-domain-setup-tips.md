# Analytics Domain Configuration Tips and FAQ

This document summarizes key principles, common issues, and recommended workflows for configuring analytics domains, drawn from real-world page operation validation. It is recommended to read through the principles section before configuring for the first time to avoid common pitfalls.

## Configuration Principles

The following principles come from actual page operations. It is recommended to understand these concepts before starting configuration.

### Analytics Domains Are Not the Only Table Configuration Entry Point

An analytics domain organizes tables, metrics, answer builders, knowledge, files, and permissions into a business context. But the deep configuration for each table is not done in the analytics domain table list.

The correct path is:

1. Go to "Analytics Domain Management > Data > Tables".
2. Click the "Table Display Name" of a table already in the domain.
3. Navigate to the table detail page in "Data > Tables".
4. In the table detail page, continue configuring table display name, table description, fields, virtual columns, indexes, hiding, column types, purposes, table associations, data preview, and statistical analysis.

Therefore, completing "Add Table" does not mean table configuration is done. Before launch, you must enter each table's detail page to check field configuration.

### "Import Table" and "Select Existing Table" Are Not the Same Action

"Import Table" is for first-time generation of a queryable table asset from a Lakehouse physical table. "Select Existing Table" is for adding an already-existing table asset to the current analytics domain.

If a table in the import list is grayed out and unselectable, it means the table has already been imported or an existing queryable table asset already exists. In this case, switch to "Select Existing Table" to reuse the existing asset — do not import again.

Reusing an existing table usually preserves existing field configurations, descriptions, indexes, metrics, or other governance results, and is suitable for multiple analytics domains sharing the same business table.

### Auto-Detection Results Must Be Reviewed

The system automatically detects field types, column types, and purposes, and may recommend metrics or table associations. But these results are only initial suggestions and should not be directly equated with business definitions.

In practice:

- String fields are often detected as `CATEGORICAL` with purposes `DIM` and `FILTER`.
- Numeric fields may be detected as `CONTINUOUS` with purposes `FILTER` and `MEASURE`.
- Virtual columns after saving may be detected as `OTHER` and `FILTER`.
- Field detection or refresh operations update the refresh time.

Therefore, after a table is added to the domain, check each column: whether the alias is business-readable, whether the description is clear, whether the column type is correct, and whether the purpose fits the analysis scenario.

### What the System Automatically Configures

Field configuration, metric creation, and table associations are all fairly tedious. The Analytics Agent will automatically complete some foundational work and provide suggestions at key points, reducing the cost of configuring from scratch.

In practice, the system handles or prompts the following automatically:

| Stage | System Auto Behavior | What You Need to Do |
| --- | --- | --- |
| After creating analytics domain | Shows "Creation Successful" configuration guide, prompting to add tables, metrics, and other data. | Click "Add Data" to continue configuration, or click "Not Now" to configure later. |
| Empty domain Basic Information page | Shows "Data Health" empty state and "Click to Go" entry point. | Go to the data configuration page to add tables. |
| After importing table | Generates a queryable table asset, typically a `v_gpt_*` table or view. | Check table display name, table description, and field configurations. |
| Table structure generation | Automatically detects field types, column types, purposes, index status, etc. | Review field aliases, descriptions, column types, purposes, hiding, and indexes. |
| Simple metric suggestions | Provides simple metric suggestions based on fields, e.g., count, sum, average, max, min. | Select and adopt reasonable metrics; delete or skip those that do not fit business definitions. |
| Virtual column Run | Executes SQL expression and returns sample data. | Determine whether sample data meets expectations, then save and review field configuration. |
| Multi-table scenario | "Auto-Association" attempts to detect candidate table associations. | Manually confirm in the "Confirm Association" dialog; do not save blindly. |
| Health scan | Scans for configuration items that may affect Q&A accuracy. | Address warnings and anomalies; re-scan if necessary. |

A special note: what the system automatically generates are "initial configurations" and "candidate suggestions", not final business confirmations. Metrics and table associations in particular must be confirmed by someone who understands the business definitions.

### Simple Metric Suggestions Are Not Final Metric Definitions

After importing tables and completing field configuration, the system may automatically recommend simple metrics. In testing, importing the account table automatically generated 5 metric suggestions:

- Total account count: `COUNT(id)`
- Total seat count: `SUM(seats)`
- Average seat count: `AVG(seats)`
- Latest creation time: `MAX(created_at)`
- Earliest trial end time: `MIN(trial_ends_at)`

These metrics are suitable for quick Q&A startup, but still check:

- Whether metric names match business phrasing.
- Whether aggregation functions are correct.
- Whether fields are appropriate as metrics.
- Whether filter conditions are needed, such as excluding test data or counting only valid records.
- Whether max/min values for time fields are actually of business value.
- Whether metrics need to be converted to answer builders or complex SQL.

Simple metric suggestions can improve configuration efficiency, but cannot replace business definition review.

### Virtual Columns Follow "Validate First, Then Save, Then Review"

Creating a virtual column is not just writing SQL and saving. The actual process should be:

1. Enter the field name.
2. Write the SQL expression.
3. Click `Run`.
4. Check whether "Run successful" is shown and whether sample data meets expectations.
5. Click "Confirm" to save.
6. Return to the table structure list to check the saved field name, type, column type, purpose, and refresh time.

`Run` succeeding only means the expression can execute — it does not mean the semantic configuration after saving is completely correct.

### Auto-Association Only Detects Candidate Relationships

Auto-association does not automatically generate necessarily correct JOINs. In practice:

- When the domain has only 1 table, the "Auto-Association" button is grayed out.
- When the domain has 2 or more tables, the button is enabled.
- After clicking, a "Confirm Association" dialog opens.
- If the system did not identify a relationship, the dialog shows "No table associations found".

This shows that auto-association is a candidate relationship detection tool, not a forced JOIN tool. Even if the system detects candidate relationships, manual confirmation is needed for source table, source column, target table, and target column to match business reality.

### Health Scan Is a Pre-Publication Check Entry Point

The "Data Health" on the Basic Information page scans configuration items that may affect Q&A accuracy, such as missing field descriptions, field controls, table association relationships, and whether metrics and answer builders are defined.

When a new empty domain is created, the health area shows "You have no data yet, please add data" and a "Click to Go" link to the data configuration page. After adding data, the health area shows status, update time, re-scan entry, and issue list.

Before publishing an analytics domain, at least one health scan should be run, and warnings or anomalies should be addressed.

### The Creation Success Dialog Is a Configuration Guide

After successfully creating an analytics domain, the system shows a "Creation Successful" guide dialog. This is not just an ordinary notification — it guides you to continue configuring data.

The dialog text in practice is:

```text
Creation Successful
Please add tables, metrics, and other data to the analytics domain to get more accurate results in sessions. Learn more
Not Now
Add Data
```

Button behavior:

| Button | Behavior |
| --- | --- |
| Not Now | Close the guide, stay on the analytics domain list. |
| Add Data | Enter the detail page of the newly created analytics domain. |

After clicking "Add Data", you enter the "Basic Information" page of the new domain. The page still shows the "Data Health" empty state, and at the bottom shows a "What data can be added to analytics domains" guide section including descriptions of tables, metrics, answer builders, files, and a "Start Adding" button.

Therefore, the recommended action order after creating a new domain is: first click "Add Data" to enter the new domain detail page, then use "Start Adding" or the "Data" tab to enter table, metric, answer builder, and file configuration.

## Common Questions

### Why Is a Table Grayed Out and Unselectable?

The table has already been added or already exists in the system. Switch to the "Select Existing Table" entry to add it — do not import again.

### Why Is the "Auto-Association" Button Unavailable?

Usually the current domain has too few tables, or the system has not yet identified associatable fields. Add multiple tables with common join keys first, then try auto-association.

### Why Is Q&A Quality Unstable?

Common reasons include missing field descriptions, unclear metric definitions, overly technical table and field names, missing business knowledge, and unclear JOIN relationships. It is recommended to add field aliases, field descriptions, metrics, and knowledge.

### Why Does the System Prompt That Workspace Data Is Invisible?

If the Add Table dialog prompts that Lakehouse Workspace data is not visible, the system user `sysservice_decision` may not have been added to the target workspace. Authorization must be granted by a user with the `workspace_admin` role.

Reference SQL:

```sql
create user sysservice_decision;
grant role workspace_admin to user sysservice_decision;
```

### Will Deleting a Domain Delete the Physical Tables?

Deleting an analytics domain typically only deletes the domain configuration and associated relationships in the domain, and should not directly delete Lakehouse physical tables. But the deletion prompt and scope of impact in the current system should still be confirmed before deleting.

### Why Check the Field List After Virtual Column Run Succeeds?

`Run` only means the SQL expression can execute, and sample data is shown. After saving, the system also detects field type, column type, and purpose. In this test, after saving, the virtual column showed as "Virtual Column", type as `string`, column type as `OTHER`, and purpose as `FILTER`. If the field should actually be used as a dimension or measure, continue checking and adjusting the field configuration.

## Health Check and Quality Recommendations

The system performs health checks on analytics domains. Common checks include:

- Whether data table field descriptions are missing.
- Whether fields have garbled characters.
- Whether table association fields are duplicated.
- Whether JOIN relationships are reasonable.
- Whether field definitions are ambiguous.
- Whether physical tables or fields have changed.
- Whether metrics exist in the domain.
- Whether knowledge definitions conflict or overlap.

Before publishing an analytics domain, it is recommended to complete the following checks:

- At least 1 usable table is configured.
- At least 1 core metric is configured.
- Key fields have clear aliases and descriptions.
- Multi-table analysis scenarios have correct JOIN relationships configured.
- Recommended questions can return results normally.
- SQL statements conform to business definitions.
- Permission scope meets data security requirements.

## Recommended Configuration Workflow

For ordinary business analysis scenarios, it is recommended to configure in the following order:

1. Create the analytics domain with a clear name and notes.
2. Add core business tables.
3. Check field types, aliases, descriptions, and purposes.
4. Adopt or manually create core metrics.
5. If multi-table analysis is involved, configure table associations.
6. Add business knowledge and term explanations.
7. Configure user permissions.
8. Add recommended questions.
9. Enter "Start Analysis" to validate typical questions.
10. Review SQL to confirm results match business definitions.

## Related Documentation

- [Configuring Analytics Domains](datagpt-domain-management-guide.md) — Operations guide for creating and configuring data in analytics domains
- [Metrics and Answer Builders](metrics_answer_build.md) — Precise configuration and SQL templates for complex metrics
- [Improving Q&A Accuracy](answer-accuracy-improve.md) — Using semantic layer configuration to make answers more accurate
- [Model Selection and Configuration](datagpt-model-config.md) — Switching or configuring the LLM model used for Q&A
- [Quick Start](datagpt_quickstart.md) — Run your first data Q&A in 5 minutes
- [Improving Q&A Accuracy](answer-accuracy-improve.md) — Using semantic layer configuration to make answers more accurate
