# Configuration Guide

For data engineers and semantic layer maintainers, covering the complete chain from planning and building to semantic configuration and operational governance.

---

<div style="display:flex; flex-wrap:wrap; gap:16px; margin:8px 0">
<div style="flex:1 1 280px; min-width:0; border:1px solid #DBEAFE; border-radius:8px; padding:20px 24px">

## Semantic Layer Development

**Goal: Help the system correctly understand data and return stable, accurate answers**

**Step 1 — Plan analysis domains**

[Analysis Domain Planning Guide](datagpt-domain-planning-guide.md) — Enterprise-level analysis domain division methodology and best practices

**Step 2 — Connect data and models**

[Data Source Management](datagpt_data_source.md) — Add Lakehouse, MySQL, StarRocks, Databricks, and others
[Model Selection and Configuration](datagpt-model-config.md) — Configure the LLM model used for Q&A

**Step 3 — Build the analysis domain**

[Configure Analysis Domain](datagpt-domain-management-guide.md) — Create analysis domains, add tables, configure table details and permissions

**Step 4 — Configure field semantics**

[Configure Field Semantics](datagpt-field-semantic-config-guide.md) — Aliases, descriptions, types, usage, hidden, indexes
[Configure Virtual Columns](datagpt-virtual-column-config-guide.md) — Create derived fields

**Step 5 — Configure definitions and knowledge**

[Metrics and Answer Builder](metrics_answer_build.md) — Create metrics and Answer Builders to lock in calculation definitions
[Configure Knowledge](datagpt-knowledge-config-best-practices.md) — Configure business definitions and terminology explanations
[File and Document Q&A](datagpt-file-knowledge-qa-guide.md) — Upload documents for document-based Q&A

</div>
<div style="flex:1 1 280px; min-width:0; border:1px solid #DBEAFE; border-radius:8px; padding:20px 24px">

## Operations and Governance

**Goal: Ensure the system is secure, governable, and auditable**

**Permissions and Security**

[Row-Level Permissions](row_level_permission.md) — Control the data range accessible to users
[Bulk Download and Data Export Governance](datagpt-data-export-governance-guide.md) — Manage download permissions, export auditing

**Operations**

[Web Search](web_search.md) — Enable external web retrieval for an analysis domain
[Message Notifications](datagpt-notification-guide.md) — View background task status for file imports, table imports, etc.

**Q&A Quality**

[Troubleshoot Q&A Accuracy Issues](datagpt-qa-accuracy-troubleshooting-guide.md) — Complete investigation from answer to SQL to records
[Launch Checklist for Analysis Domain](datagpt-domain-health-check-and-launch-checklist.md) — Health check and pre-launch checklist
[Validate Q&A Quality](datagpt-domain-qa-validation-guide.md) — Validate whether configurations are effective with typical questions
[Handle Feedback](datagpt-feedback-loop-guide.md) — Admin-side viewing and assignment of user feedback

</div>
</div>
