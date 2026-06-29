# Analytics Domain Planning Guide

An analytics domain is the core unit in the Analytics Agent for organizing Q&A capabilities, data assets, business definitions, and user access scope. For enterprise-scale scenarios, planning analytics domains is not simply "adding tables" — it determines which users analyze which business questions within which data boundaries.

If an enterprise has tens of thousands of tables, hundreds of business departments, and thousands of users, analytics domain planning directly affects Q&A accuracy, permission governance complexity, metric definition consistency, and long-term maintenance costs.

## Core Conclusion

Do not put all tables and all users into one "large comprehensive" analytics domain.

The recommended approach is to plan multiple analytics domains based on "business topic + user group + data definitions + sensitivity boundaries", then configure tables, field semantics, knowledge, metrics, answer builders, recommended questions, and permissions within each domain.

Analytics domains should handle the first layer of business isolation; role authorization, field hiding, row-level permissions, and audit logs then handle more fine-grained governance.

From an agent design perspective, analytics domain planning is designing working boundaries for the large language model. Instead of letting the model freely select from all tables, all definitions, and all knowledge across the entire company, first tell it: this domain serves whom, answers which business questions, uses which data assets, and follows which definitions and permissions. The clearer the boundaries, the more easily the model can complete analytical tasks stably.

## Why You Cannot Build Just One Large Domain

A "large comprehensive" analytics domain seems simple: add all tables, allow all users in, users ask whatever they want. But in real enterprise environments, this typically leads to higher governance and troubleshooting costs.

| Problem | Impact |
| --- | --- |
| Too many tables and fields | The model needs to choose from too many candidate tables and fields, making misselection more likely. |
| Mixed business context | Finance, sales, operations, and HR semantics mixed together make user questions more likely to be misunderstood. |
| Conflicting metric definitions | Different departments may have different definitions for the same metric, such as "revenue", "active users", or "valid orders". |
| Complex permission rules | Different user groups all in the same domain require extensive roles, field hiding, and row-level permission workarounds. |
| Knowledge interference | The same term has different meanings in different departments; when placed in the same knowledge space, conflicts easily arise. |
| Difficult answer builder maintenance | Large numbers of complex SQL templates concentrated in one domain make naming, scope management, and change impact difficult to manage. |
| Difficult Q&A troubleshooting | When answers are wrong, it is hard to tell whether the issue is domain size, table misselection, field ambiguity, knowledge conflict, metric error, or permission restriction. |

Therefore, large organizations should treat analytics domains as governance boundaries, not as containers for all data assets.

## Analytics Domain Planning Principles

### Plan by Business Questions, Not by Table Lists

When planning analytics domains, do not start from "what tables do I have" — start from "which users need to analyze which business questions".

Recommended questions to ask:

- Who does this analytics domain serve?
- What are the 5 to 10 questions users ask most frequently every day or every week?
- Are these questions centered around the same business topic?
- Do these questions use the same or compatible metric definitions?
- What tables, files, knowledge, and metrics do these questions require?

If a domain's core capabilities cannot be described using 5 to 10 recommended questions, the domain's boundaries are usually not yet clear.

### Divide by Stable Business Topics

An analytics domain should be organized around stable business topics, such as:

- Sales performance analysis.
- Customer renewal analysis.
- Contract collections analysis.
- Financial expense analysis.
- HR recruitment analysis.
- Member operations analysis.

If the questions in a domain span multiple unrelated topics, user questions are more likely to trigger incorrect resources.

### Divide by User Group

Analytics domains should serve relatively clearly defined user groups.

For example:

| User Group | Recommended Domain |
| --- | --- |
| Management | Business overview analytics domain. |
| Sales team | Sales performance domain, leads analysis domain, collections domain. |
| Finance team | Financial performance domain, expense domain, collections reconciliation domain. |
| Operations team | User operations domain, campaign effectiveness domain. |
| HR team | Recruitment analysis domain, headcount structure domain. |

If a single analytics domain has multiple user groups with very different permission requirements, it typically needs to be split, or at least split into a "overview domain" and "department domains".

### Divide by Metric Definitions

Metric definitions are an important basis for analytics domain boundaries.

The same term may have different definitions across business departments:

| Metric Term | Possible Differences |
| --- | --- |
| Revenue | Finance-recognized revenue, order payment amount, contract signed amount. |
| Active users | Logged-in users, paid active users, valid subscription users. |
| Valid orders | Successfully paid orders, non-refunded orders, fulfilled orders. |
| Customer count | Registered customers, paid customers, enterprise customers, active customers. |

If two departments have different definitions for key metrics, it is recommended to split analytics domains, maintain knowledge, metrics, and answer builders separately, and avoid same-name metrics being mixed across domains.

### Divide by Data Sensitivity

Sensitive data should be prioritized for independent domains.

Data suitable for independent domains includes:

- Payroll data.
- Financial vouchers and details.
- Customer privacy data.
- Sensitive contract terms.
- Employee performance data.
- Data involved in compliance audits.

Sensitive domains should be configured more strictly with:

- Domain membership.
- Role data permissions.
- Field hiding.
- Row-level permissions.
- Audit log checks.

Do not mix sensitive tables into ordinary business analytics domains and then rely entirely on field hiding or row-level permissions as remediation.

### Divide by Launch Phase

Enterprise-scale rollout should not put all business scenarios into a production domain at once.

Recommended approach:

1. Pilot domain  
   Validate core scenarios with a small number of high-quality tables, knowledge, metrics, and answer builders.

2. Production domain  
   After validation, open to target business users.

3. Expansion domain  
   Gradually expand for new business topics, departments, or question sets.

This approach reduces the risk of a single large launch, and makes it easier to continuously optimize using audit logs and Q&A records.

## Recommended Architecture Patterns

### Cross-Department Business Overview Domain

Suitable for management, business analysis teams, or data teams.

Recommended to include only:

- Core summary tables shared across departments.
- Core metrics with unified definitions.
- A small number of validated answer builders.
- Recommended questions commonly used by management.

Do not add all department detail tables to the overview domain. The focus of the overview domain is unified definitions and high-level overview, not replacing all department domains.

### Department Analytics Domain

Suitable for each business department to maintain their own high-frequency analysis scenarios.

For example:

- Finance analytics domain.
- Sales analytics domain.
- Operations analytics domain.
- HR analytics domain.

Department analytics domains should include the tables, files, knowledge, metrics, and answer builders commonly used by that department. If the scenarios within a department are still complex, they can be further split into topic domains.

### Topic Analytics Domain

Suitable for departments with long business chains, large data volumes, and complex definitions.

For example, the sales department can be split into:

- Sales leads analytics domain.
- Opportunity progression analytics domain.
- Contract signing analytics domain.
- Collections analytics domain.
- Customer renewal analytics domain.

The advantage of topic domains is clearer question boundaries, and field semantics and answer builders are easier to maintain.

### Sensitive Data Independent Domain

Suitable for data scenarios with higher permission requirements.

For example:

- Payroll analytics domain.
- Financial vouchers analytics domain.
- Customer privacy analytics domain.

Sensitive domains should use stricter member management and field governance, and regularly check access and change situations in combination with audit logs.

### Shared Base Tables Across Multiple Domains

When the same table serves multiple business scenarios, it is not necessary to put all users in one large domain.

Better approach:

- Add the same table to multiple relevant analytics domains.
- Configure field semantics, knowledge, and metrics in each domain to match the current business scenario.
- Configure domain permissions and role permissions separately for different user groups.

For example, the customer master table can appear simultaneously in:

- Sales customer analytics domain.
- Operations member analytics domain.
- Finance collections analytics domain.

But the focus, metrics, and recommended questions for "customer" can differ across domains.

## Common Anti-Patterns

### One Large Comprehensive Domain

Putting all tables, all metrics, all knowledge, and all users in one domain.

Risks:

- Q&A misselects tables.
- Metric definitions are mixed up.
- Permission rules become complex.
- Knowledge conflicts arise.
- Issues are difficult to troubleshoot.

### One Table Per Analytics Domain

Treating analytics domains as single-table Q&A entry points.

Risks:

- Users need to switch between domains frequently.
- Multi-table business questions cannot be expressed naturally.
- Metrics, knowledge, and answer builders cannot be organized around complete business scenarios.

Unless it is a very clear single-table experiment or temporary validation, this approach is not recommended for long-term use.

### Building Domains Directly by Database Catalog

Mechanically dividing analytics domains by Catalog, Schema, or database name.

Risks:

- Technical catalogs do not equal business boundaries.
- A single business topic may span multiple Schemas.
- A single Schema may contain multiple departments or business topics.

Analytics domains should be oriented toward business questions, not copying the underlying database structure.

### Delegating All Permission Isolation to Row-Level Permissions

Row-level permissions are suitable for controlling which rows different users can see in the same table, but are not suitable for replacing analytics domain isolation.

If different departments have different questions, metrics, knowledge, and answer builders, analytics domains should be split first, and then row-level permissions used to handle data scope differences within a domain.

### Keeping Conflicting Metric Definitions in the Same Domain

If "revenue", "active users", and "customer count" have different meanings for different user groups, relying only on knowledge explanations as a remedy is not sufficient.

A more robust approach is to split analytics domains, or to keep only uniformly governed definitions in the overview domain.

## Analytics Domain Split Decision Table

Use the following questions to determine whether to create or split an analytics domain:

| Decision Question | If the Answer Is "Yes" |
| --- | --- |
| Is there an independent business topic? | Lean toward creating a separate domain. |
| Is there an independent user group? | Lean toward a separate domain or at least separate domain permission configuration. |
| Is there an independent metric definition? | Lean toward creating a separate domain. |
| Does it contain sensitive data? | Lean toward creating a separate sensitive domain. |
| Is there a need for independent knowledge and answer builders? | Lean toward creating a separate domain. |
| Can it be clearly described with 5 to 10 recommended questions? | If not, the domain boundaries need to be re-examined. |
| Are many exception permission rules needed? | Lean toward splitting, to reduce exception configurations. |
| Does Q&A frequently misselect tables or mix up fields? | Lean toward splitting or reducing the resource scope within the domain. |

## Recommended Implementation Steps

### Step 1: Inventory Business Questions

Start by collecting the questions target users ask most frequently, not by inventorying all tables.

Recommended output:

- Target user groups.
- High-frequency business questions.
- Involved metrics.
- Involved dimensions and filter conditions.
- Involved documents and business definitions.

### Step 2: Design Analytics Domain Boundaries

Based on business questions, categorize scenarios into:

- Overview domain.
- Department domain.
- Topic domain.
- Sensitive domain.
- Pilot domain.

Each domain should have a clear name, applicable user group, and business scope.

### Step 3: Select Core Resources

Do not add all tables at once. Prioritize adding core resources that can support high-frequency questions:

- High-frequency fact tables.
- Commonly used dimension tables.
- Metrics with confirmed definitions.
- Necessary knowledge.
- Necessary files.
- High-value answer builders.

Gradually expand based on Q&A validation.

### Step 4: Configure Semantics and Definitions

Configure for each domain:

- Field aliases.
- Field descriptions.
- Column types.
- Field purposes.
- Hidden fields.
- Knowledge.
- Metrics.
- Answer builders.
- Recommended questions.

These configurations should be centered around the current domain's business scenario, not mechanically reusing all field descriptions.

### Step 5: Configure Permissions

Configure user membership by domain, then use role authorization, resource data permissions, field hiding, and row-level permissions to further restrict access scope.

Recommendations:

- Business users should only be added to the analytics domains they need.
- Domain maintainers should have edit permissions for the corresponding domain resources.
- Sensitive domain membership should require individual approval and periodic review.
- Row-level permissions handle data scope differences between different users within the same domain.

### Step 6: Validate with Recommended Questions

Before launching each analytics domain, prepare at least 5 to 10 recommended questions covering:

- Overview questions.
- Core metric questions.
- Grouped analysis questions.
- Filtered analysis questions.
- Document or definition explanation questions.
- Complex analysis questions.

Validate each question's Q&A results, generated SQL, and whether the metrics, knowledge, files, and answer builders were found.

## Example: Large Enterprise Analytics Domain Planning

Assume an enterprise has:

- Over 10,000 tables.
- Over 100 business departments.
- Over 2,000 users.

The following planning can be adopted:

| Level | Domain Type | Examples | User Groups |
| --- | --- | --- | --- |
| 1 | Business overview domain | Company business overview | Management, business analysis team. |
| 2 | Department domain | Finance analysis, sales analysis, operations analysis, HR analysis | Business users in each department. |
| 3 | Topic domain | Sales leads, contract collections, customer renewal, recruitment funnel | Topic owners and analysts. |
| 4 | Sensitive domain | Payroll analysis, financial vouchers, customer privacy | Authorized small user group. |
| 5 | Pilot domain | New business pilot analysis, temporary validation domain | Data team and pilot users. |

This approach allows each analytics domain to maintain clear boundaries while supporting cross-department overviews and in-depth departmental analysis.

## Determining Whether an Analytics Domain Is Healthy

A healthy analytics domain typically has these characteristics:

- Clear business topic.
- Defined user group.
- Manageable number of tables.
- Maintainable field semantics.
- Consistent metric definitions.
- Non-conflicting knowledge.
- Recommended questions covering core scenarios.
- Permission rules that do not require extensive exceptions.
- Q&A issues that can be located and troubleshot.
- Audit logs that can track key changes.

If an analytics domain long-term relies on extensive exception permissions, frequently experiences Q&A misselection, and maintainers cannot explain the purpose of resources in the domain, it is time to re-evaluate whether a split is needed.

## Related Documentation

- [Governance Overview](datagpt-governance-overview.md)
- [Configuring Analytics Domains](datagpt-domain-management-guide.md)
- [Analytics Domain Resource Permission Guide](datagpt-domain-resource-permission-guide.md)
- [Field Semantics Configuration Guide](datagpt-field-semantic-config-guide.md)
- [Recommended Questions Configuration Guide](datagpt-recommended-questions-guide.md)
- [Validating Q&A Effectiveness After Domain Configuration](datagpt-domain-qa-validation-guide.md)
