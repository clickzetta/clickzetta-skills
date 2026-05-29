# Semantic View

Semantic View is a logical data model object in Singdata Lakehouse, designed to establish a semantic abstraction layer between physical table structures and business analysis requirements.

Without Semantic View, different reports and applications often have inconsistent calculation definitions, leading to the problem of "same metric, different results." Semantic View addresses two core issues by centrally defining table relationships, dimensions, and metrics:

- **For data analysis**: Business users can query cross-table data using business terminology without writing complex JOIN and GROUP BY statements.
- **For data governance**: Metric definitions are centrally managed, ensuring consistent data definitions across the entire organization.

## Core Components

A Semantic View consists of four core components:

**Logical Tables (TABLES)**: Business entities mapped to physical tables, such as customers, orders, and products. Table relationships are declared through primary and foreign keys, and the engine automatically handles JOINs during queries -- no manual JOINs needed.

**Dimensions (DIMENSIONS)**: Categorical attributes that answer "who, what, where, when" questions. Supports direct mapping to physical columns as well as expression-based computed dimensions (e.g., `YEAR(hire_date)`).

**Metrics (METRICS)**: Quantitative business measures defined through aggregation functions (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`), such as "total employees" or "average salary."

**Filters (FILTERS)**: Predefined reusable filter conditions that encapsulate common business filtering logic, intended for use by the AI/metadata layer.

## Typical Use Cases

| Scenario | Description |
|------|------|
| Cross-table metric analysis | Define multi-table relationships; JOINs are handled automatically during queries without manual writing |
| Unified metric definitions | Centrally define KPI calculation logic to avoid inconsistent definitions across reports |
| Lower query barrier | Business users query using business terminology without needing to understand physical table structures |
| AI Agent data access | Enable AI Agents to directly query semantic data via CZ-CLI or MCP tools |
| Analytics Agent data source | Serve as the semantic layer for conversational analysis, supporting natural language Q&A |

## Documentation Navigation

| Document | Content |
|------|------|
| [Create Semantic View](semantic-view-create.md) | CREATE syntax, parameter descriptions, complete examples |
| [Query Semantic View](semantic-view-query.md) | `semantic_view()` function usage, filtering, sorting |
| [Advanced Query Usage](semantic-view-advanced.md) | Subqueries, CTEs, JOIN with regular tables, CTAS |
| [Manage Semantic View](semantic-view-manage.md) | DROP, ALTER, SHOW, DESC, access control |
| [Integrate with AI](semantic-view-ai.md) | AI_COMPLETE combined queries, CZ-CLI, MCP tools |
| [Generate and Maintain Semantic Views with AI Agent](semantic-view-agent-guide.md) | Information collection, design evaluation, validation methods, common pitfalls |
| [Best Practices](semantic-view-best-practices.md) | Naming conventions, design recommendations, FAQ |
