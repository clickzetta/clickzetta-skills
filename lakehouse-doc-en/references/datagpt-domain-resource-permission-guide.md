# Managing Analytics Domain Resource Permissions

Analytics domain resource permissions define which tables, files, knowledge, metrics, and answer builders a user can use after entering an analytics domain, and how these resources are affected by roles, domain permissions, field configurations, and row-level permissions.

## The Isolation Role of Analytics Domains

An analytics domain itself is a layer of governance boundary. After a user enters an analytics domain, the Analytics Agent performs Q&A around the resources that have been added and configured in that domain, rather than freely selecting from all data assets across the system.

This isolation has direct governance significance:

| Isolation Object | Governance Significance |
| --- | --- |
| Data tables | Different business domains add only the tables they need, reducing cross-business data misuse. |
| Files | Document Q&A is limited to files in the current domain, avoiding mixing documents from different business topics. |
| Knowledge | Business terms and definitions are limited to the current domain, reducing ambiguity caused by the same word having different meanings across departments. |
| Metrics | Finance, operations, and sales can maintain their own metric definitions, avoiding cross-domain mixing of same-name metrics. |
| Answer builders | Complex SQL templates are limited to reuse within the corresponding business scenario, reducing the risk of incorrect invocation. |
| Users | Only users who have been added to an analytics domain can access it, forming a business access boundary. |

Therefore, before configuring resource permissions, determine whether the analytics domain division is reasonable. If the domain division is too coarse, too many tables, metrics, and knowledge will be mixed together, increasing Q&A misselection and permission troubleshooting costs; if the division is too fine, users may need to frequently switch between multiple domains. Generally, it is recommended to divide analytics domains by stable business topic, data user group, and metric definitions.

## Resources in an Analytics Domain

In the "Data" tab of the analytics domain configuration page, the following resources can be configured:

| Resource | Role |
| --- | --- |
| Tables | The foundation of structured Q&A. |
| Metrics | Define aggregation definitions, such as total account count, active account count. |
| Complex Metrics / Answer Builders | Encapsulate complex SQL, dynamic dimensions, dynamic filters, and multi-metric outputs. |
| Knowledge | Supplement business definitions, synonyms, and explanatory text. |
| Files | Support uploading documents for document Q&A. |

These resources together determine what questions an analytics domain can answer.

## Difference Between Adding Resources to a Domain and Resource Authorization

"Resources added to an analytics domain" and "user has permission to use resources" are not the same thing.

| Configuration | Description |
| --- | --- |
| Resource added to domain | Tables, files, knowledge, metrics, and answer builders appear in the current analytics domain. |
| User added to domain | User can access the analytics domain. |
| Role data permissions | Whether the user's role can view or edit the corresponding resource type. |
| Field and row-level permissions | Which fields and data rows the user can see during Q&A. |

Therefore, when troubleshooting unavailable resources, check simultaneously:

1. Whether the resource has been added to the current analytics domain.
2. Whether the user has been added to the current analytics domain.
3. Whether the user's role has data permissions for that resource type.
4. Whether table fields are hidden or semantics are incomplete.
5. Whether row-level permissions have restricted the data scope.

## Table Resources

Tables are the core resource for structured Q&A.

In practice, adding tables has three entry points:

- Import table.
- Upload file to create table.
- Select existing table.

If a table is selected but grayed out in the import table page, it means the table has already been added or already exists in the system. In this case, add it via the "Select Existing Table" entry.

After a table is added to the domain, the table detail page needs to be checked for field configurations including:

- Field aliases.
- Field descriptions.
- Column types.
- Field purposes.
- Hidden status.
- Virtual columns.
- Indexes.
- Table associations.

These configurations affect the accuracy of Q&A field selection, filter generation, dimension selection, and SQL construction.

## File Resources

Files are for document Q&A.

In practice, files can be uploaded from "Data > Files". The page shows support for:

- `.xlsx`
- `.txt`
- `.pdf`

Single file size limit is 10MiB.

After uploading, files enter an import or task list; after processing is complete, they appear in the analytics domain file list. In practice, the file list showed "2 files in total", including:

- `analytics-agent-file-qa-test.txt`
- `data_dictionary.pdf`

In Q&A validation, when a user asked "According to the uploaded files, what does 'active account' mean in the documents?", the system used document knowledge retrieval, with `search_document_knowledge` appearing in the logs, referencing the uploaded file and existing PDF.

If a file is already in the analytics domain, it cannot be added again. When troubleshooting unavailable file Q&A, check whether the file has finished processing and appears in the domain file list.

## Knowledge Resources

Knowledge is used to supplement business semantics that the model cannot directly understand from field names or table structure.

Suitable content to write into knowledge includes:

- Proprietary terms.
- Synonyms.
- Business definitions.
- Metric explanations.
- Field meanings.
- Data usage notes.

In practice, knowledge "test_knowledge_active_user_definition_20260609" was created to explain that active users, current active user count, and active account count are all understood based on `active_subscription = TRUE`.

During Q&A, knowledge may be retrieved together with files. For business definition questions, first check whether the knowledge exists, is enabled, and whether the name and content are sufficiently clear.

## Metric Resources

Metrics are used to define stable aggregation definitions.

Questions suitable for metric configuration include:

- Total count.
- Sum.
- Average.
- Maximum or minimum.
- Simple filtered aggregation.

In practice, "Total Active Accounts" was created with an alias of "Current Active User Count". When natural language matches this definition, the system attempts to use metric calculation; if metric calculation fails, it may fall back to SQL generation.

When troubleshooting unavailable metrics, check:

- Whether the metric belongs to the current analytics domain.
- Whether the metric is enabled.
- Whether metric names, aliases, and descriptions cover common user phrasings.
- Whether the metric's underlying table is added to the current analytics domain.
- Whether related fields are hidden or have incorrectly configured semantics.

## Answer Builder Resources

Answer builders are used to encapsulate complex SQL templates, suitable for multi-metric, dynamic dimension, dynamic filter, and multi-table join scenarios.

In practice, two answer builders were validated:

- `test_answer_builder_active_account_count_20260609`, using `${filters}` to support dynamic filtering.
- `test_answer_builder_account_health_overview_20260609`, using `${dims}` and `${filters}` to support dynamic grouping and filtering.

During Q&A, users can trigger via natural language:

- Group by `plan`.
- Only show `source = Google`.
- Return multiple health metrics.

The availability of answer builders is affected by the following configurations:

| Configuration | Impact |
| --- | --- |
| SQL template | Determines whether calculation logic is correct. |
| `${filters}` | Determines whether natural language filtering is possible. |
| `${dims}` | Determines whether natural language grouping is possible. |
| Filter field configuration | Determines which fields are available for dynamic filtering. |
| Dimension field configuration | Determines which fields are available for dynamic grouping. |
| Output field configuration | Determines how result columns are interpreted as metrics. |
| Role data permissions | Determines whether the user can view or edit the answer builder resource. |

## Impact of Role Data Permissions on Domain Resources

In "Authorization Management > Data Permissions", you can configure by resource type:

- Answer builders
- Data sources
- Knowledge
- Tables
- Files
- Metrics

This configures role-level resource type permissions, not individual resource authorization within a specific analytics domain. Whether a user can use related resources in an analytics domain also depends on whether the user has been added to the analytics domain and whether the resource has been added to it.

Each resource type has a "All Data" option. After selecting, you can choose actions:

- Can view
- Can edit

This means in the same analytics domain, different roles may have different permissions for the same resource type. For example, business users may only have view permissions for metrics and answer builders, while domain maintainers have edit permissions.

## Recommended Configuration Approach

| User Type | Recommended Resource Permissions |
| --- | --- |
| Business viewer | Tables, files, knowledge, metrics, answer builders: can view. |
| Domain maintainer | Tables, knowledge, metrics, answer builders: can edit; files: can edit as needed. |
| System administrator | Can manage roles, users, audit logs, model configurations, and all resource types. |

It is not recommended to give all users edit permissions. Once metrics, answer builders, or knowledge are accidentally modified, Q&A results are directly affected.

## Resource Permission Troubleshooting Checklist

When a user reports "cannot get certain data" or "results are inconsistent with expectations", troubleshoot in the following order:

1. Whether the user has been added to the target analytics domain.
2. Whether the user's role has view permissions for the corresponding resource type.
3. Whether tables, files, knowledge, metrics, or answer builders have been added to the current analytics domain.
4. Whether table fields are hidden.
5. Whether field aliases, descriptions, purposes, and column types are sufficiently clear.
6. Whether row-level permissions have restricted the user's data scope.
7. Whether Q&A logs show the correct knowledge, metrics, or answer builders were found.
8. Whether anyone has recently modified related resources in the audit log.

## Related Documentation

- [Analytics Agent Governance Overview](datagpt-governance-overview.md)
- [Permission Management Guide](datagpt-permission-management-guide.md)
- [Role Authorization Guide](datagpt-role-authorization-guide.md)
- [Answer Builder Best Practices](datagpt-answer-builder-best-practices.md)
- [Knowledge Configuration Best Practices](datagpt-knowledge-config-best-practices.md)
