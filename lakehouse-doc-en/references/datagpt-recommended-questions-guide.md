# Recommended Questions Configuration Guide

Recommended questions help users quickly understand what questions an analytics domain can answer. They appear in the guidance area of the domain's Q&A entry point, suitable as first-question examples for business users and for validating Q&A effectiveness before the domain goes live.

Recommended questions are not decorative copy. A good recommended question can guide users to tables, metrics, knowledge, files, and answer builders that are already configured, reducing the problem of users not knowing what to ask when first using the system.

## Value of Recommended Questions

| Value | Description |
| --- | --- |
| Lower the barrier for first questions | After entering the analytics domain, users can click or reference recommended questions directly to start analysis. |
| Expose analytics domain capability boundaries | Recommended questions tell users what business questions this domain is suitable for. |
| Guide use of correct definitions | Recommended questions can use configured metric names, field aliases, and business terminology. |
| Support launch validation | Recommended questions can serve as a standard set of validation questions to check whether Q&A is stable. |
| Reduce invalid questions | Prevent users in a Sales Analytics domain from asking about financial vouchers, compensation details, and other topics that don't belong to the current domain. |

## Configuration Entry Point

Navigate to the target analytics domain configuration page:

1. Open the analytics domain.
2. Go to "Basic Information".
3. Find the Recommended Questions section.
4. Click "Add Question".
5. Enter the recommended question in the text box.
6. Press Enter to save the question.

In practice, after clicking "Add Question", an inline input box appears with the prompt:

```text
Please enter a recommended question and press Enter to add
```

Press Enter after entering the question to add it. After saving, the analytics domain's update time is updated.

## Where Recommended Questions Are Displayed

In practice, after adding recommended questions, they appear in the welcome area of the new analytics page and can also be seen in the popular question search.

For example, after adding:

```text
Show account health overview by plan
```

and then entering the analytics domain Q&A page, that question appears in the recommended or popular questions area.

This shows that recommended questions not only appear on the configuration page — they also affect the question guidance shown to end users when they enter the analytics domain.

## How to Design High-Quality Recommended Questions

### Cover Core Business Scenarios

Recommended questions should center around the core business objectives of the analytics domain, not randomly list fields.

For example, an account analytics domain could configure:

- What is the total number of accounts?
- What is the current active user count?
- Show account health overview by plan.
- Show account health overview for Google source only.
- How are account counts distributed across different countries?

These questions cover overall metrics, business definitions, multi-dimensional analysis, filter analysis, and distribution analysis respectively.

### Use User's Natural Language

Recommended questions should use the language business users actually speak, not pure technical field names.

Recommended:

```text
Show active account count and account active rate by subscription plan
```

Not recommended:

```text
group by plan count active_subscription
```

If field aliases and knowledge configuration are sufficiently clear, when users use expressions like "subscription plan", "active accounts", and "account active rate", the system can more easily map to the correct fields or metrics.

### Align with Configured Capabilities

Recommended questions should be answerable reliably by the current analytics domain. Do not include questions as recommended questions if the corresponding tables, metrics, knowledge, or answer builders are not yet configured.

| Recommended Question Type | What to Confirm First |
| --- | --- |
| Metric questions | Metric created, enabled, name and alias covers user expressions. |
| Dimension analysis questions | Table fields configured with dimension usage, field semantics clear. |
| Filter questions | Field suitable as filter, field aliases and values clear. |
| Complex analysis questions | Answer builder has run validation, preview, and been verified in Q&A. |
| Document explanation questions | Files added to domain, knowledge or document content retrievable. |

### Control the Number of Questions

Recommended questions should not be too many. Start with 5 to 8 high-quality questions covering the most common analysis paths.

If there are too many recommended questions, users may find it hard to decide where to start. Prioritize by:

1. One overall overview question.
2. Two to three core metric questions.
3. Two to three dimension or filter analysis questions.
4. One definition explanation or document Q&A question.

## Types of Recommended Questions

| Type | Example | Capabilities to Validate |
| --- | --- | --- |
| Overview question | "What is the total number of accounts?" | Tables, metrics, basic SQL generation. |
| Metric question | "What is the current active user count?" | Metrics, knowledge, synonyms. |
| Grouping question | "Show account health overview by plan." | Dimension fields, answer builder `${dims}`. |
| Filter question | "Show account health overview for Google source only." | Filter fields, answer builder `${filters}`. |
| Trend question | "What is the trend of new accounts in the last month?" | Time fields, date understanding, chart generation. |
| Document question | "What does active account mean in the documentation?" | File retrieval, knowledge retrieval. |
| Anomaly investigation question | "Which accounts have a high seat count but are not activated?" | Detail query, filter conditions, and field explanations. |

## Recommended Questions and Q&A Validation

Recommended questions can serve directly as the launch validation question set.

Before launch, it is recommended to click or copy each recommended question to validate:

1. Whether it can return a normal answer.
2. Whether it uses the correct tables, metrics, knowledge, or answer builders.
3. Whether it generates SQL that meets expectations.
4. Whether it uses the correct dimensions and filter conditions.
5. Whether it does not reference unrelated files or knowledge.
6. Whether it can generate appropriate charts.
7. Whether the business definition matches expectations.

If recommended questions cannot be answered consistently, it is not recommended to open the domain to business users directly.

## Recommended Questions and Analytics Domain Governance

Recommended questions can also help govern analytics domain boundaries.

If a recommended question needs to span multiple unrelated business topics, it usually indicates the analytics domain scope may be too large; if recommended questions frequently need to access tables or knowledge not in the current domain, it indicates resource configuration is incomplete or domain segmentation needs adjustment.

Recommended questions can be used to reverse-check analytics domain design:

| Symptom | Possible Cause |
| --- | --- |
| Recommended questions cover many departmental topics | Analytics domain is too large; consider splitting. |
| Recommended questions frequently answer with the wrong table | Too many tables, insufficient field semantics, or unclear domain topic. |
| Recommended questions depend on multiple different definitions | Metrics and knowledge need governance; consider splitting domains if necessary. |
| Recommended questions require many permission exceptions | User groups are too diverse; split the user group or analytics domain. |

## Common Issues

### Where can I see recommended questions after saving?

In practice, saved recommended questions appear in the welcome area of the new analytics page and can also be seen in the popular question search.

### Do recommended questions force the system to answer according to fixed logic?

No. Recommended questions are primarily user question guidance. Whether they can be answered consistently still depends on table, field semantics, knowledge, metrics, answer builders, and permission configuration.

If you want to lock in complex SQL logic, use answer builders; if you want to lock in metric definitions, configure metrics or knowledge.

### Should recommended questions be written as technical questions or business questions?

Write business questions. Technical field names can appear in field configuration, metric configuration, and answer builders, but recommended questions are for end users and should use business language as much as possible.

### Can recommended questions be used to test document Q&A?

Yes. For analytics domains that include files, it is recommended to configure at least one document explanation recommended question, for example:

```text
What does active account mean in the documentation?
```

This helps users know the domain can not only look up numbers but also explain documents and definitions.

## Related Documentation

- [Configure Analytics Domain](datagpt-domain-management-guide.md)
- [How to Validate Q&A Effectiveness After Configuring an Analytics Domain](datagpt-domain-qa-validation-guide.md)
- [Answer Builder Best Practices](datagpt-answer-builder-best-practices.md)
- [File & Document Q&A Guide](datagpt-file-knowledge-qa-guide.md)
