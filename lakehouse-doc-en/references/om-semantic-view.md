# Semantic View

A Semantic View is the **business semantic layer** in the Lakehouse, creating an abstraction layer between physical table structures and business analysis requirements. It solves the problem of "the same metric having different definitions across different reports."

## What Problem Does It Solve

Without a semantic view, different reports and applications write their own JOIN and aggregation logic, and the same "monthly active users" might be calculated differently in different places. A semantic view centrally manages metric definitions, ensuring a unified definition across the entire organization.

![](/.topwrite/assets/13-semantic-view.svg)

## Comparison with Regular Views

| Comparison Item | Regular View | Semantic View |
|--------|----------|----------|
| Definition method | SQL query | Declarative (table relationships + dimensions + metrics) |
| Primary use | Logic encapsulation, permission isolation | Business semantic layer, AI data access |
| JOIN handling | Manual | Engine handles automatically |
| Target audience | Developers | Business users, AI Agents |

## Core Components

- **Logical Tables (TABLES)**: Map to physical tables, declare primary/foreign key relationships, and automatically JOIN during queries
- **Dimensions (DIMENSIONS)**: Categorical attributes such as region, time, and product category
- **Metrics (METRICS)**: Aggregated measures such as sales amount, user count, and conversion rate
- **Filters (FILTERS)**: Reusable predefined filter conditions

## Typical Scenarios

| Scenario | Description |
|------|------|
| Unified metric definitions | Centrally define KPIs to avoid inconsistencies in calculation logic across reports |
| Lower query barrier | Business users query using business terms without needing to understand physical table structures |
| AI Agent data access | Serve as the semantic data source for Analytics Agent, enabling natural language Q&A |

## Related Documentation

- [Semantic View Detailed Introduction](semantic-view-overview.md)
- [Creating Semantic Views](semantic-view-create.md)
- [Integration with AI Features](semantic-view-ai.md)
