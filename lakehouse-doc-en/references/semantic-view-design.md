# Semantic View Design: From Business Questions to Views

Many people ask "how do I build a Semantic View?" But building a Semantic View is not the goal. What you actually want is: **for the same business question, any person at any time can get the same trusted answer without rewriting JOINs and metric definitions from scratch.** Consistency, reuse, and trust — those three things are the reason Semantic View exists.

So the right order is **start with the business question, then work backwards to the view** — not build the view first and then look for questions. This guide covers that reverse-engineering path: when it is worth building, how to derive what to build from the question, how to ensure consistent metric definitions, and how to verify the view actually delivers.

## Step 0: Should You Use a Semantic View?

Semantic Views have a modeling cost. Not every situation justifies one. Assess first:

| Your situation | Better choice |
|---|---|
| A one-off ad hoc query that you'll discard afterward | Write SQL directly |
| You just want to wrap a complex SQL for reuse without standardizing metric definitions | Regular View |
| You want transparent query acceleration for existing queries | Materialized View / Dynamic Table |
| **Multiple people or reports repeatedly use the same set of metrics and definitions must be consistent** | **Semantic View** |
| **You want business users to query cross-table data using business terms without writing JOINs** | **Semantic View** |

Rule of thumb: **build a Semantic View only when the benefit of consistent definitions and repeated reuse outweighs the modeling cost.** For single-user, one-off work with no conflicting definitions, a Semantic View is overhead.

## Work Backwards From the Business Question: Answer Four Questions First

Once you decide to build, do not rush to write `CREATE`. Answer the following four questions first. Each question maps to a clause in Semantic View.

**1. What business questions should this view answer?** — Defines the view's scope.

One view corresponds to one clear analytics domain (for example, "department salary analysis"), not all tables crammed into one large view. Clarifying what is *excluded* is just as important as what is included. A view that covers too many topics is better split into multiple focused views.

**2. What is the exact definition of each metric?** — Determines `METRICS`.

This is the most error-prone step and the one to align on first (see the next section). For each metric, clarify: what are the numerator and denominator, which data is included or excluded, and which timestamp is used.

**3. What dimensions do users want to slice these metrics by?** — Determines `DIMENSIONS`.

List the commonly used grouping dimensions (department, time, region, ...) and confirm the granularity (calendar month or fiscal month? down to city or province?).

**4. Which physical tables are involved and how do they join?** — Determines `TABLES` and foreign keys.

Read the table schemas before designing. Confirm that join column names and **data types match** (mismatched types cause creation to fail immediately). How you define relationships directly affects whether aggregation results are correct; see [Relationship Modeling and Aggregation Granularity](semantic-view-modeling-relationships.md).

## Consistent Definitions: Avoid "Same Name, Different Meaning"

The most common real-world pain point for users is not "can't find a metric" — it is "**found several similar metrics, or my number doesn't match someone else's**." The root cause is almost always inconsistent metric definitions.

The same metric name can mean completely different calculations to different teams:

| Metric name | Business definition A | Business definition B |
|---|---|---|
| Employee count | On roster (including probation) | Active headcount (post-probation only) |
| Order amount | GMV (placed amount) | Net revenue (after refunds) |
| Active users | Logged in this month | Transacted this month |

**The fix is not to pick one definition, but to define each definition as a separate, clearly named metric** and use `COMMENT` to document the difference. Conditional aggregation is the primary way to express different definitions:

```sql
METRICS (
    -- Average salary across all employees
    emps.avg_salary AS AVG(emps.salary)
        COMMENT 'Average salary of all employees (including former employees)',
    -- Average salary of active employees only: use conditional aggregation to scope the definition
    emps.active_avg_salary AS AVG(CASE WHEN emps.is_active THEN emps.salary END)
        COMMENT 'Average salary of active employees only'
)
```

Now "all employees" and "active employees" each have a distinct metric name and comment, and there is no ambiguity for any user. A practical way to surface definition conflicts: take an existing report, and for each number ask repeatedly — "does this include former employees? include probation? based on order date or payment date?" Usually the second or third question reveals the conflict.

## A Complete Example: From Requirements to View

Walk through the method above. The requirement is "analyze salary distribution and headcount by department, for HR analysts."

1. **What questions to answer**: employee count and salary by department and hiring year. Excludes performance and promotion data (that belongs to another domain).
2. **Metric definitions**: total headcount (all employees), average salary (all employees including former), maximum salary.
3. **Dimensions**: department, hiring year (extracted from hire date), department manager (cross-table).
4. **Tables and joins**: `employees` as the main table, `departments` as the dimension table. Joined via `dept` (string) referencing `departments.dept_name` (string) — types match.

Once the reverse-engineering is clear, the clauses are all determined and the view writes itself:

```sql
DROP SEMANTIC VIEW IF EXISTS doc_test.emp_dept_analysis;
CREATE SEMANTIC VIEW doc_test.emp_dept_analysis
TABLES (
    depts AS doc_test.departments PRIMARY KEY (dept_name),
    emps AS doc_test.employees
        PRIMARY KEY (id)
        FOREIGN KEY (dept) REFERENCES depts (dept_name)
)
DIMENSIONS (
    emps.department AS emps.dept COMMENT 'Department',
    emps.hire_year AS YEAR(emps.hire_date) COMMENT 'Hiring year',
    depts.manager_name AS depts.manager COMMENT 'Department manager'
)
METRICS (
    emps.total_employees AS COUNT(emps.id) COMMENT 'Total headcount',
    emps.avg_salary AS AVG(emps.salary) COMMENT 'Average salary (including former employees)',
    emps.max_salary AS MAX(emps.salary) COMMENT 'Maximum salary'
)
COMMENT = 'Employee department analysis: headcount and salary by department and hiring year';
```

For fully runnable table setup, data, and queries, see [Create Semantic View](semantic-view-create.md) and [Query Semantic View](semantic-view-query.md).

## Pre-Delivery Validation: Created Successfully ≠ Usable

A view that can be created does not mean its results are correct. **Validation is the most easily skipped and most important step.** Focus on three types of "silent errors":

- **Does the cross-table dimension work?** Query grouped by department manager (a cross-table dimension) and confirm the foreign key join is correct with no unexpected NULLs.
- **Are the numeric values in the expected range?** Are row counts and values within expected bounds? Do not put metrics from multiple one-to-many branches of the same parent into a single query (this triggers a chasm trap error).
- **Were any unsupported metric types used?** Arithmetic expression metrics, window function metrics, and derived metrics will "create successfully but produce wrong results or query errors." See [Capabilities and Limitations Reference](semantic-view-capabilities-limits.md) for details.

For the full validation checklist and how to use an AI Agent to accelerate this design and validation workflow, see [Using an AI Agent to Generate and Maintain Semantic Views](semantic-view-agent-guide.md).

## Related Documentation

- [Semantic View Overview](semantic-view-overview.md)
- [Relationship Modeling and Aggregation Granularity](semantic-view-modeling-relationships.md): how relationships determine aggregation correctness
- [Create Semantic View](semantic-view-create.md): CREATE syntax and complete examples
- [Capabilities and Limitations Reference](semantic-view-capabilities-limits.md): which metrics and syntax are not supported
- [Using an AI Agent to Generate and Maintain Semantic Views](semantic-view-agent-guide.md): use AI to accelerate modeling and validation
