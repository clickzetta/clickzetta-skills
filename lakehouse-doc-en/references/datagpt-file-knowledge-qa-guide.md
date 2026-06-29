# File & Document Q&A Guide

Analytics Agent supports not only structured table-based data Q&A, but also adding files to an analytics domain for document Q&A, metric definition lookup, and business context retrieval.

Files are suitable for unstructured or semi-structured reference materials, such as data dictionaries, business rules, metric definitions, product manuals, operational policies, and department guidelines. Once configured, users can query the file content using natural language within the analytics domain.

## What Problems File Q&A Solves

| Scenario | Example Question | Value of Files |
| --- | --- | --- |
| Explaining business terms | "What does 'active account' mean in the documentation?" | Retrieves explanation text from uploaded files, reducing misinterpretation. |
| Querying data dictionaries | "What are the meanings of the `source` field?" | Helps users understand field origins, values, and applicable contexts. |
| Supplementing metric definitions | "What is the calculation logic for the active rate?" | Complements structured metric configurations with documentation. |
| Querying policy or reference documents | "What are the restrictions on refund rules?" | Enables Q&A around business documents. |
| Assisting with Q&A ambiguity | "Why does current active user count equal active account count?" | Uses documents and knowledge to explain synonyms, definitions, and usage boundaries. |

File Q&A and structured data Q&A are complementary. Tables, metrics, and answer builders are better suited for computing results; files and knowledge are better for explaining rules, terms, and context.

## Uploading Files

Navigate to the analytics domain configuration page:

1. Open the target analytics domain.
2. Go to the "Data" tab.
3. Switch to "Files".
4. Upload the file.
5. Wait for the file to finish processing and appear in the file list.

In practice, the "Data > Files" page supports the following formats:

- `.xlsx`
- `.txt`
- `.pdf`

Single file size limit is 10 MiB.

After uploading, the file first enters an import or task queue. Once processing is complete, the file will appear in the current analytics domain file list. Only files that have been added to the domain and fully processed are suitable for document Q&A validation.

## How Files Appear in the Domain

In practice, the analytics domain file list shows the number of files and file names. For example, a test domain once showed "2 files total", including:

- `analytics-agent-file-qa-test.txt`
- `data_dictionary.pdf`

If a file has already been added to the domain, it cannot be added again. If you encounter a "file already exists" or "cannot add duplicate" error, check the current domain file list first instead of uploading the same file again.

## How File Q&A Works

After a file is added to the analytics domain, users can ask questions related to the file content from the Q&A entry point of that domain.

In validation testing, the question:

```text
Based on the uploaded file, what does 'active account' mean in the documentation?
```

was answered using document retrieval. The Q&A log showed:

- `search_document_knowledge`
- Source file: `analytics-agent-file-qa-test.txt`
- The source file may also include other documents in the same domain, such as `data_dictionary.pdf`

This shows that file Q&A does not simply display a file list — it retrieves file content within the current analytics domain during the Q&A process and uses relevant excerpts as the basis for the answer.

## Relationship Between Files and Knowledge

Both files and knowledge help the system understand business semantics, but they are used differently.

| Configuration | Suitable Content | Characteristics |
| --- | --- | --- |
| Files | Data dictionaries, policy documents, manuals, PDFs, Excel files, text descriptions | Content can be lengthy; suitable for retrieving answers from documents. |
| Knowledge | Key terms, synonyms, stable definitions, concise business rules | Better for directly supplementing Q&A semantics and metric definitions. |

In practice, a question about "active accounts" matched both an uploaded file and a knowledge entry. The knowledge entry "test_knowledge_active_user_definition_20260609" defined active users, current active user count, and active account count based on `active_subscription = TRUE`; the file provided the documentary source of explanation.

Therefore, the recommended approach is:

- Write stable, concise, frequently-asked definitions into knowledge.
- Upload complete data dictionaries, policy documents, and long-form documents as files.
- For key terms, files and knowledge can complement each other, but their descriptions should remain consistent.

## Recommendations for File Content

To make files easier to retrieve and reference, ensure the file content has a clear structure.

### Use Clear Headings

Recommended:

```text
Active Account Definition
Current Active User Count Definition
source Field Description
plan Field Values
```

Not recommended:

```text
Notes
Rules
Supplement
Miscellaneous
```

The closer the heading is to what a user would ask, the easier it is to retrieve.

### Use Business Common Language

If users commonly say "current active user count", do not only write `active_subscription` in the file. It is recommended to include both the technical field and the business term:

```text
Active accounts, current active user count, and active user count all refer to accounts where active_subscription = TRUE.
```

### Avoid Mixing Multiple Definitions

Do not mix multiple similar but distinct metric definitions in the same paragraph. For example, "active accounts", "logged-in users", and "paid users" should be explained separately, otherwise Q&A may get confused.

### Keep File Content Consistent with Field Semantics

Field explanations in files should be consistent with aliases, descriptions, and usage in table field configurations. Otherwise, when a user asks a question, the file content and table field semantics may conflict with each other.

## File Q&A Validation

After adding files to the analytics domain, validate at least the following questions:

| Validation Question | Check Point |
| --- | --- |
| What does a certain term mean in the document? | Whether the correct file was cited. |
| What are the meanings of a certain field? | Whether field descriptions can be retrieved from the data dictionary. |
| What is the calculation logic for a certain metric? | Whether it is consistent with metric configuration and knowledge configuration. |
| Ask a question not present in the file | Whether the system avoids fabricating answers or indicates insufficient basis. |
| Ask using synonyms | Whether the system can map user common expressions to document terminology. |

During validation, it is recommended to check the Q&A log to confirm whether document retrieval was triggered and whether the source file is correct.

## Common Issues

### File Has Been Uploaded, Why Is It Not Referenced in Q&A?

Check in the following order:

1. Has the file finished processing?
2. Does the file appear in the current analytics domain file list?
3. Is the user asking in the correct analytics domain?
4. Does the question clearly point to a heading or term in the file?
5. Does the file content use expressions commonly used by users?
6. Is there a knowledge entry or field semantic that conflicts with the file content?

### What Is the Difference Between File Q&A and Metric Calculation?

File Q&A primarily answers "what it is, how it's defined, and what the rules are". Metric calculation answers "how much, what the trend is, and how to group it".

For example:

| Question | More Suitable Capability |
| --- | --- |
| "What does active account mean?" | File or knowledge. |
| "What is the total number of active accounts?" | Metric or answer builder. |
| "Show active account count by plan" | Metric, answer builder, or structured Q&A. |

### Can Files Replace Table Field Configuration?

No. Files can explain business context, but field aliases, field descriptions, column types, and field usage should still be maintained in the table field configuration. Field configuration directly affects how the system selects fields, generates filter conditions, and constructs SQL.

## Related Documentation

- [Knowledge Configuration Best Practices](datagpt-knowledge-config-best-practices.md)
- [Field Semantic Configuration Guide](datagpt-field-semantic-config-guide.md)
- [Analytics Domain Resource Permission Guide](datagpt-domain-resource-permission-guide.md)
- [How to Validate Q&A Effectiveness After Configuring an Analytics Domain](datagpt-domain-qa-validation-guide.md)
