# Integrate with AI

Semantic View provides a business-friendly query layer. There are three main ways to integrate with AI capabilities: directly calling AI functions in SQL to process semantic query results, using CZ-CLI to let AI Agents operate on semantic views, and integrating into AI workflows via MCP Server tools.

## AI_COMPLETE Combined Queries

The results of `semantic_view()` are standard result sets and can be passed directly to `AI_COMPLETE` in the `SELECT` list for AI processing of each row.

**Typical scenarios**: Generating natural language interpretations, anomaly analysis, or summaries for metric results returned by semantic views.

```sql
-- Generate AI analysis comments for salary data of each department
SELECT
    department,
    avg_salary,
    AI_COMPLETE(
        '<model-name>',
        'Please evaluate the salary level of this department in one sentence. Department: ' || department
        || ', Average Salary: ' || CAST(avg_salary AS STRING)
    ) AS ai_comment
FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS emps.department,
    METRICS emps.avg_salary
);
```

> You need to configure AI Gateway first and specify a valid model name. See [AI Functions](AI_function_in_SQL.md) for details.

You can also materialize semantic view results before performing batch AI processing:

```sql
-- First, materialize the query results
CREATE TABLE doc_test.dept_stats AS
SELECT * FROM semantic_view(
    doc_test.emp_dept_analysis,
    DIMENSIONS emps.department,
    METRICS emps.avg_salary,
    METRICS emps.total_employees
);

-- Then call AI functions in batch
SELECT department, AI_COMPLETE('<model>', 'Analysis: department ' || department || ' has '
    || CAST(total_employees AS STRING) || ' employees, average salary '
    || CAST(avg_salary AS STRING)) AS insight
FROM doc_test.dept_stats;
```

## Using CZ-CLI

CZ-CLI is the currently recommended method for AI Agent access, supporting natural language-driven operations on semantic views.

```bash
# View semantic views under the current schema
cz-cli agent run "List all semantic views in the doc_test schema" --profile aliyun_shanghai_prod

# Query a semantic view
cz-cli agent run "Query doc_test.emp_dept_analysis, count employees and average salary by department" \
    --profile aliyun_shanghai_prod

# Create a semantic view
cz-cli agent run "Create a semantic view in doc_test to analyze employee salaries, including department dimension and average salary metric" \
    --profile aliyun_shanghai_prod
```

See [CZ-CLI Documentation](CZ-CLI.md) for details.

## MCP Server Tools

The Singdata Lakehouse MCP Server provides a set of tools specifically for semantic views, which can be integrated into AI Agent frameworks (Dify, N8N, Claude Desktop, etc.). See [MCP Server Documentation](MCPServers.md) for details.

### Tool Overview

| Tool Name | Operation | Description |
|----------|------|------|
| `LH-create-semantic-view` | Create | Create a semantic view from a YAML definition |
| `LH-desc-semantic-view` | View | Get the complete YAML definition of a view |
| `LH-desc-logical-table` | View | Get logical table structure and relationships |
| `LH-brief-semantic-view` | View | Quickly browse dimension and metric fields |
| `LH-get_semantic_view_dims` | View | Get structured dimension list |
| `LH-semantic-view-dim-add` | Modify | Dynamically add a dimension (no rebuild needed) |
| `LH-semantic-view-dim-del` | Modify | Dynamically delete a dimension (no rebuild needed) |
| `LH-query-semantic-value` | Query | Structured parameter-driven query, recommended for Agents |

### Typical Agent Workflow

```
1. LH-brief-semantic-view      → Learn what dimensions and metrics the view has
2. LH-query-semantic-value     → Query on demand, passing dimensions/metrics/filter conditions
3. LH-semantic-view-dim-add    → If a required dimension is missing, dynamically add it
4. LH-desc-semantic-view       → Export YAML for backup or version comparison
5. LH-create-semantic-view     → Rebuild the view in a new environment based on YAML
```

### LH-query-semantic-value

This is the recommended way for AI Agents to query semantic views, without needing to manually write `semantic_view()` SQL:

**Parameters**:

| Parameter | Type | Required | Description |
|------|------|------|------|
| `semantic_view_name` | string | Yes | Name of the semantic view |
| `selected_dimensions` | array | Yes | List of dimensions to query |
| `selected_metrics` | array | Yes | List of metrics to query |
| `filter_conditions` | array | No | Filter conditions (default empty) |

**Example**:

```python
mcp.call("LH-query-semantic-value",
    semantic_view_name="tpch_rev_analysis",
    selected_dimensions=[
        {"logical_table": "customers", "dimensions_name": "customer_name"},
        {"logical_table": "customers", "dimensions_name": "customer_city"}
    ],
    selected_metrics=[
        {"logical_table": "orders", "metrics_name": "order_average_value"}
    ],
    filter_conditions=[
        {"field_name": "customer_city", "expr": "= 'New York'"}
    ]
)
```

Equivalent SQL:

```sql
SELECT * FROM semantic_view(
    tpch_rev_analysis,
    DIMENSIONS customers.customer_name,
    DIMENSIONS customers.customer_city,
    METRICS orders.order_average_value
) WHERE customer_city = 'New York';
```

### LH-semantic-view-dim-add

Dynamically add a dimension to an existing semantic view without rebuilding:

```python
mcp.call("LH-semantic-view-dim-add",
    semantic_view_name="tpch_rev_analysis",
    dimensions=[{
        "logical_table": "customers",
        "dimension_name": "customer_city",
        "column_name": "c_city",
        "synonyms": ["city", "customer city"],
        "comment": "City of the customer"
    }]
)
```

### LH-create-semantic-view

Create a semantic view from a YAML definition, suitable for declarative configuration or cross-environment migration:

```python
mcp.call("LH-create-semantic-view",
    semantic_view_yaml=open("semantic_view.yaml").read(),
    schema_name="my_schema"
)
```

The YAML format is compatible with the Snowflake Cortex Analyst specification. Use `LH-desc-semantic-view` to export an existing view as YAML.

## Related Documents

- [AI Functions](AI_function_in_SQL.md)
- [CZ-CLI](CZ-CLI.md)
- [MCP Server](MCPServers.md)
- [Query Semantic View](semantic-view-query.md)
