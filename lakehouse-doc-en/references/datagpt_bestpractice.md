# Best Practices

Analytics Agent best practices help you avoid common pitfalls in data semantic configuration, Q&A accuracy optimization, and analysis domain governance.

## Going to Production

When your team is ready to move from PoC to real business use, read these documents first:

- **[From PoC to Production: Analytics Agent Adoption Guide](datagpt-production-adoption-guide.md)** — Data boundaries, semantics, permissions, validation, feedback, and operations mechanisms required for production

## Configuration Phase

Before going live with an analysis domain, use the following documents to complete configuration optimization:

- **[Analysis Domain Configuration Tips and FAQs](datagpt-domain-setup-tips.md)** — 9 lessons learned, 6 FAQs, health checks, and recommended workflow
- **[Answer Builder Best Practices](datagpt-answer-builder-best-practices.md)** — SQL template design, using `${dims}` and `${filters}`, output metric configuration
- **[Configure Field Semantics](datagpt-field-semantic-config-guide.md)** — Correct methods for configuring field aliases, descriptions, types, and usage
- **[Configure Virtual Columns](datagpt-virtual-column-config-guide.md)** — Creating and configuring semantics for derived fields
- **[Configure Knowledge](datagpt-knowledge-config-best-practices.md)** — Best practices for writing business definitions and terminology explanations
- **[File and Document Q&A](datagpt-file-knowledge-qa-guide.md)** — File uploads, Q&A matching, and knowledge coordination
- **[Recommended Questions Configuration](datagpt-recommended-questions-guide.md)** — Designing high-quality guided questions

## Validation Phase

After configuration is complete, use the following documents to validate Q&A quality:

- **[Validate Q&A Quality](datagpt-domain-qa-validation-guide.md)** — Step-by-step validation of knowledge, metrics, Answer Builders, virtual columns, and table relationships
- **[Launch Checklist for Analysis Domain](datagpt-domain-health-check-and-launch-checklist.md)** — Health check + manual pre-launch checklist

## Troubleshooting Phase

When Q&A results are unsatisfactory, use the following documents to identify the root cause:

- **[Troubleshoot Q&A Accuracy Issues](datagpt-qa-accuracy-troubleshooting-guide.md)** — Complete investigation chain from answer to SQL to records
- **[Analytics Agent Q&A Accuracy Improvement](answer-accuracy-improve.md)** — Detailed explanation of four semantic layer capabilities

## Governance Phase

After an analysis domain goes live, continuously manage permissions and auditing:

- **[Governance Overview](datagpt-governance-overview.md)** — Permission layering, domain isolation, and audit loop
- **[Manage Permissions](datagpt-permission-management-guide.md)** — Account management, authorization management, and analysis domain permissions
- **[Configure Row-Level Permissions](datagpt-row-level-permission-guide.md)** — Define permission points and user data ranges
- **[View Audit Logs](datagpt-audit-log-guide.md)** — Track configuration changes and user operations
