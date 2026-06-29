# Configure Knowledge

Knowledge helps Analytics Agent understand business vocabulary, metric definitions, proprietary concepts, and implicit rules in users' natural language. It addresses the question of "what does the user mean by this term" rather than directly replacing tables, metrics, or answer builders.

When users frequently use business abbreviations, industry terminology, company-internal definitions, or ambiguous terms, knowledge configuration should be the first consideration.

---

## Value of Knowledge Configuration

Natural language Q&A requires not just table structure but also business context. For example, when a user says "active account count", the system needs to know:

- What does "active account" refer to?
- Is it equivalent to "current active user count"?
- Which field should be used to determine this?
- Should canceled, trial, or legacy plan accounts be excluded?

Without knowledge, the system can only infer from field names, metric names, and table structure, leading to inconsistent definitions.

In practice, when an analytics domain has no knowledge configured, the Q&A log shows 0 knowledge search results; after knowledge is configured, the system first uses `search_knowledge` to match knowledge, then `get_knowledge_detail` to retrieve the definition, before proceeding to select metrics, answer builders, or generate SQL.

---

## Applicable Scenarios

| Scenario | Why Knowledge Configuration Is Suitable | Example |
| --- | --- | --- |
| Business terms don't match field names | Helps the system map user expressions to underlying fields. | "Active account" corresponds to `active_subscription = TRUE`. |
| Same concept has multiple names | Helps the system understand synonyms. | Active account, active user, current active user count, valid subscription account. |
| Metric definitions need explanation | Prevents the system from guessing calculation rules on the fly. | "Conversion rate = converted orders / visitors". |
| Field is prone to ambiguity | Tells the system which field is the correct definition. | `trial_converted` is not equivalent to the current active account. |
| Internal business terminology | Lets the system understand company-internal abbreviations. | "Key Account (KA)", "qualified opportunity", "silent user". |
| Q&A explanation needs business context | Lets answers explain why the result was calculated this way. | "Active accounts are counted based on accounts with currently active subscriptions". |

Knowledge is especially useful for supplementing business rules that cannot be fully expressed by field semantics alone.

---

## Relationship Between Knowledge, Fields, Metrics, and Answer Builders

Knowledge is not configured in isolation — it should be used together with field semantics, metrics, and answer builders.

| Configuration | Problem It Solves | Example |
| --- | --- | --- |
| Field semantics | What this field is and how it should be used | `active_subscription` indicates whether the current subscription is valid. |
| Knowledge | What the business term the user said means | "Active account" refers to accounts where `active_subscription = TRUE`. |
| Metrics | How simple aggregation definitions are consistently calculated | Total active account count. |
| Answer builder | How complex SQL or multi-metric combinations are executed reliably | Account health overview. |

The typical Q&A pipeline is:

1. Search knowledge first to understand business terms.
2. Then look for available metrics, answer builders, and tables.
3. If a metric or answer builder is matched, prioritize the configured logic.
4. If it cannot be executed directly, fall back to table structure and SQL generation.

Therefore, the role of knowledge is "explaining semantics and definitions", while the role of metrics and answer builders is "executing calculations".

---

## Configuration Entry Point

The general path to configure knowledge in an analytics domain:

1. Go to **Administration** -> **Analytics Domain Management**.
2. Open the target analytics domain.
3. Go to the **Data** tab.
4. Click **Knowledge**.
5. Click **Add Knowledge**.

When adding knowledge, the page provides three entry points:

| Entry Point | Description |
| --- | --- |
| Import Knowledge | Batch import knowledge via Excel template, suitable when you already have a knowledge table or terminology list. |
| Create Knowledge | Manually create a single knowledge entry, suitable for adding key definitions or testing. |
| Select Existing Knowledge | Add knowledge that has already been created to the current analytics domain. |

Knowledge import supports Excel files; the page provides a template download. When manually creating knowledge, you need to fill in name, associated analytics domain, description type, and description content.

---

## Text Knowledge vs. Dictionary Knowledge

When creating knowledge, the page provides description types:

| Description Type | Applicable Scenarios |
| --- | --- |
| Text | Explain a concept, definition, or rule. |
| Dictionary | Maintain term mappings, enumeration value definitions, and structured explanations. |

If you only need to explain "what an active account is", text is sufficient.

If you need to maintain multiple term mappings, such as multiple business abbreviations, status code meanings, and category code explanations, consider dictionary format or batch import.

---

## Recommended Writing Style

A good knowledge entry should contain three types of information:

| Information | Description | Example |
| --- | --- | --- |
| Business term | What the user would say | Active account, active user, current active user count |
| Calculation or judgment definition | Which field or rule to use | `v_gpt_accounts.active_subscription = TRUE` |
| Usage boundary | What should not be confused | Not equivalent to trial conversions, not equivalent to uncanceled accounts |

Recommended writing:

> In this analytics domain, active users, current active user count, and active account count all refer to the number of accounts in the `v_gpt_accounts` table where `active_subscription = TRUE`. Questions of this type should prioritize filtering by this field before counting.

Not recommended:

> Active accounts are accounts that are active.

The latter does not specify the field, rule, or boundary, and cannot effectively help the system select SQL.

---

## Practical Validation Case

In an actual validation, a knowledge entry was created:

| Configuration Item | Content |
| --- | --- |
| Name | test_knowledge_active_user_definition_20260609 |
| Description Type | Text |
| Description | In this analytics domain, active users, current active user count, and active account count all refer to the number of accounts in the `v_gpt_accounts` table where `active_subscription = TRUE`. Questions of this type should prioritize filtering by this field before counting. |
| Status | Enabled |

Before configuration, when asking "What is the current active user count?", the log showed 0 knowledge search results, and the system mainly relied on metrics and table structure for inference.

After configuration, when asking "How many active accounts are there?", the log showed:

- `search_knowledge` matched 1 knowledge entry.
- `get_knowledge_detail` retrieved the knowledge details.
- The system explicitly used `active_subscription = TRUE` as the active account definition.
- The final active account count was returned.

This shows that knowledge enters the Q&A execution pipeline rather than just being static documentation.

---

## How Knowledge Affects Q&A

Knowledge affects Q&A primarily at three stages:

| Stage | Role |
| --- | --- |
| Question understanding | Translates business terms in the user's natural language into concepts the system can understand. |
| SQL generation or metric selection | Helps the system select the correct fields, metrics, or answer builders. |
| Answer explanation | Enables the final answer to explain the calculation definition, not just return a number. |

For example, after configuring knowledge in a test environment, the answer can naturally explain:

> The current active account count is 464. The calculation is based on accounts in the `v_gpt_accounts` table where `active_subscription = TRUE`.

This explanatory capability is important to business users because they care not only about the result but also about "how this result was calculated".

---

## Naming Recommendations

Knowledge names should be easy for the system and administrators to understand.

Recommended:

- Active account definition
- Valid order definition
- Customer tier description
- Acquisition source definition
- Trial conversion rules

Not recommended:

- knowledge1
- test
- note
- rule

If knowledge is used for a production analytics domain, avoid using "test" as a prefix and maintain stable naming.

---

## When Not to Use Knowledge

The following scenarios do not necessarily require knowledge:

| Scenario | More Appropriate Configuration |
| --- | --- |
| Single field alias issue | Field alias |
| Single simple aggregate metric | Metric |
| Complex SQL calculation | Answer builder |
| File content Q&A | File or document knowledge |
| Unclear field description | Field description |

If a problem can be solved with field aliases and descriptions, there is no need to write all field explanations into knowledge. Knowledge is better for expressing cross-field, cross-metric, or business-definition-level rules.

---

## Common Issues

| Issue | Possible Cause | Recommended Action |
| --- | --- | --- |
| Knowledge configured but Q&A doesn't match | Knowledge name or description doesn't include common user expressions | Add synonyms and common expressions to the knowledge. |
| Knowledge matched but SQL is still incorrect | Only knowledge, no supporting field semantics or metrics | Also configure field aliases, descriptions, metrics, or answer builders. |
| Too many knowledge entries causing matching confusion | Multiple knowledge entries overlap or contradict each other | Merge duplicate knowledge entries and clarify applicable scope. |
| After business definition change, answers still use old definition | Knowledge not updated | Update knowledge and re-validate typical questions. |
| User says abbreviation but system doesn't understand | Knowledge doesn't include the abbreviation | Write abbreviations, full names, and their relationships into the knowledge description. |

---

## Pre-Launch Checklist

- Have all core business terms been configured with knowledge?
- Are different names for the same business concept included in the same knowledge entry?
- Does the knowledge explicitly specify the field, table, or calculation rule?
- Does the knowledge explain similar concepts that should not be confused?
- Is the knowledge associated with the correct analytics domain?
- Is the knowledge status enabled?
- Have typical natural language questions been used to validate knowledge matching?
- Have logs been reviewed to confirm `search_knowledge` and `get_knowledge_detail` are working?
- Has knowledge been updated after business definition changes?

The goal of knowledge configuration is to enable Analytics Agent to understand questions in business language, execute analysis using the correct definitions, and explain the basis of answers to users.

## Related Documentation

- [Configure Analytics Domain](datagpt-domain-management-guide.md) — Creating and configuring the analytics domain that knowledge belongs to
- [Configure Field Semantics](datagpt-field-semantic-config-guide.md) — Field aliases and descriptions, complementary to knowledge
- [Metrics and Answer Builder](metrics_answer_build.md) — Knowledge explains definitions; metrics execute calculations
- [Improving Q&A Accuracy](answer-accuracy-improve.md) — Overall solution for semantic layer configuration
