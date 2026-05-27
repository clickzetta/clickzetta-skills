# Generate and Maintain Semantic Views with AI Agent

Semantic view design involves business understanding, table structure analysis, and semantic modeling -- tasks that are well-suited for AI Agents. This article explains from a practical perspective: what business alignment work needs to be done before getting started, what information the Agent needs to collect, how to evaluate design quality, and which common mistakes can cause a view to be "created successfully but produce incorrect results."

## Why Semantic Views Are Suitable for Agent Generation

Creating semantic views has two main challenges:

1. **Business understanding**: Dimension and metric names, synonyms, and comments need to align with business language rather than directly copying physical column names.
2. **Table structure analysis**: Foreign key relationships, type matching, and primary key selection require understanding the data first before making design decisions.

Agents excel at both -- they can simultaneously query table structures, sample data, understand business descriptions, and generate a complete semantic view definition. But there is one thing Agents cannot do: **proactively discover business definitional discrepancies**. Skipping business alignment and letting the Agent model directly means you will only discover that "employee count" is defined differently across reports after the view goes live -- this is the hardest type of issue to troubleshoot and the most commonly overlooked step.

## Business Alignment: Before Getting Started

**The technical implementation is the easiest part.** Generating a runnable semantic view takes only ten minutes; generating one that is truly useful for the business requires doing the business alignment first.

### Two Failure Modes

| Failure Type | Symptoms | When Discovered |
|---------|------|---------|
| Technical failure | Creation error (type mismatch, foreign key reference error) | Immediately discovered |
| Business failure | Created successfully, but query results do not match business expectations | Only discovered after going live |

Business failures are more dangerous: queries do not error, numbers look plausible, but the calculation definition is inconsistent with business understanding, potentially affecting decisions.

### Five Categories of Business Knowledge to Collect

Before letting the Agent start working, collect the following five categories of information:

**1. Analysis Domain Definition**

What core business questions should this view answer? Not "build me an employee view," but:
- Scenario: Analyze salary distribution by department and hire year
- Users: HR data analysts, department managers
- Common dimensions: department, hire date, employment status
- Excluded: performance data, promotion records (belong to another analysis domain)

Clear boundaries are important. A view covering too many topics is better split into multiple focused views.

**2. Metric Definitions**

The same metric name can have completely different calculation methods across departments:

| Metric Name | HR Definition | Finance Definition | Management Definition |
|-------|--------|---------|----------|
| Employee count | Number on payroll (including probation) | Number on duty (post-probation) | Full-time equivalent (FTE) |
| Average salary | All employees including departed | Active employees only | Regular employees only (excluding interns) |
| Order amount | Order placement amount | Net received amount (after refunds) | Recognized revenue (per accounting standards) |

**You must confirm the definition of each metric before modeling**, including:
- What the numerator and denominator are respectively
- Which data is included or excluded (departed employees, test accounts, refunded orders)
- Which point in time is used for statistics (order time, payment time, confirmation time)

**3. Dimension Granularity**

The same business concept can have different levels of granularity:

| Dimension | Optional Granularity | Needs Confirmation |
|-----|---------|---------|
| Time | Calendar month / fiscal quarter / hire year | Are multiple time dimensions needed? |
| Geography | City / province / region | What is the finest granularity? Is roll-up needed? |
| Organization | Natural department / business line / cost center | Is the roll-up logic in the database or does it require expression implementation? |

**4. Business Rules and Filter Conditions**

Which data should be excluded from normal analysis? These rules are often implicit and need to be actively asked about:
- Test accounts (`is_test = true`)
- Deleted records (`is_deleted = false`)
- Anomalous data from specific time periods (e.g., dirty data during system migration)
- Legal and compliance requirements (certain data cannot appear in reports)

These rules can be designed as FILTERS clauses or directly written into conditional aggregations of metrics.

**5. Glossary**

Physical column names are often abbreviations or technical names; a business term mapping needs to be established:

| Physical Column | Business Meaning | Common Synonyms |
|---------|---------|----------|
| `dept` | Department | department, team |
| `hire_date` | Hire date | onboard date, join date |
| `is_active` | Active status | active status, employed |
| `salary` | Monthly salary (pre-tax) | salary, wage, base salary |

The glossary directly affects whether the Analytics Agent can find the correct dimensions and metrics through natural language.

### Definition Document Template

Fill out the following template completely before handing it to the Agent; it can significantly improve generation quality:

```
## Semantic View Definition Document

### Analysis Domain
- View name:
- Core business questions: (e.g., Analyze employee salary distribution and workforce structure by department)
- Primary users: (e.g., HR data analysts, department managers)
- Common query dimensions: (e.g., department, hire year, employment status)
- Excluded content: (e.g., performance data, promotion records)

### Physical Tables Involved
- Main table: schema.table_name (description: ...)
- Dimension tables: schema.table_name (description: ...)
- Relationships: main_table.column → dim_table.column (type: ...)

### Metric Definitions
| Metric Name | Calculation Formula | Include Criteria | Exclude Criteria | Statistical Time Point |
|-------|---------|---------|---------|----------|
| Total employees | COUNT(id) | All employees | None | Current point in time |
| Active employees | COUNT(id) | is_active=true | Departed employees | Current point in time |
| Average salary | AVG(salary) | All employees | None | Current point in time |

### Dimension Granularity
| Dimension | Granularity | Source Column | Requires Calculation |
|-----|-----|-------|------------|
| Department | Natural department | employees.dept | No |
| Hire year | Year | YEAR(employees.hire_date) | Yes |
| Department manager | Individual | departments.manager | No (cross-table) |

### Business Rules
- Exclusion criteria: (e.g., exclude test accounts with is_test=true)
- Data scope: (e.g., only data from 2019 onward)
- Special handling: (e.g., part-time employees counted as 0.5 FTE)

### Glossary
| Physical Column | Business Term | Synonyms |
|---------|---------|-------|
| dept | Department | department, team |
| hire_date | Hire date | onboard date |
```

### Who to Collect From and How

| Information Type | Who to Ask | Effective Questioning Approach |
|---------|-----|------------|
| Metric definitions | Data analysts, business owners | "How is this number calculated? Who/which orders are included?" |
| Dimension granularity | Report consumers | "What dimensions do you typically view this data by? Down to what level?" |
| Business rules | Data engineers, DBA | "What data in this table should normally be excluded from analysis?" |
| Term mapping | Business users | "Which field in the database corresponds to what you call 'active employees'?" |

**The most practical method**: Take an existing report and trace the calculation logic for each number. This quickly surfaces definitional discrepancies and also makes the existing report the best business documentation reference.

### Typical Definitional Conflict Cases

The following are common definitional discrepancies from real projects, illustrating why business alignment cannot be skipped:

**Case 1: Employee Count**

HR says "we have 500 people," Finance says "480 on duty," Management says "FTE is 460" -- same point in time, all three numbers are correct, but with different definitions. If the semantic view defines only one "total employees" metric, all three departments will think the number is wrong.

Solution: Define three separate metrics, each corresponding to a different definition, with comments explaining the differences.

**Case 2: Order Amount**

Sales looks at "order placement amount" (GMV), Finance looks at "net received amount" (after refunds), Operations looks at "valid order amount" (excluding test orders and anomalous orders). Same order table, three WHERE conditions, three completely different numbers.

Solution: Create three metrics named `gmv`, `net_revenue`, and `valid_order_amount`, and include each department's commonly used terms as synonyms.

**Case 3: Time Dimension**

"Monthly analysis" could mean calendar month (Jan 1 - Jan 31), fiscal month (fiscal year starts in April), or rolling 30 days. Without confirmation, the Agent defaults to calendar month, and the Finance department's numbers will not match.

Solution: Clearly define the time dimension. If multiple time definitions are needed, define multiple time dimensions.

**How to identify definitional conflicts**: Repeatedly ask follow-up questions about the same metric -- "Does it include departed employees?" "Does it include interns?" "Does it include uncompleted statuses?" Discrepancies are usually exposed by the second or third question.

---

## Step 1: Collect Necessary Information

After completing business alignment, move on to the technical information collection phase.

**This is the most critical step.** With insufficient information, the Agent will generate a view that "runs" but is useless for the business.

### Required Information

**1. Analysis Goals**

Not "build me a semantic view," but:
- What business questions should this view answer? ("Analyze salary distribution by department" vs "Analyze employee turnover rate trends")
- Who are the primary users? (Data analysts, business managers, or AI Agent automated queries)
- What are the most common query dimensions? (By department, by time, by region)

**2. Physical Tables Involved**

Let the Agent read the table structure first; don't rely on guesswork:

```bash
cz-cli agent run "Describe the structure of employees and departments tables in doc_test schema, including column names, types, and sample data" \
    --profile aliyun_shanghai_prod
```

The Agent needs to know:
- What the primary key of each table is
- How the tables relate to each other (are the column names and types of the join columns consistent)
- Which columns are suitable as dimensions and which as metrics
- Data volume (affects whether partitioning or filtering is needed)

**3. Business Term Mapping**

Physical column names are often abbreviations or technical names; business meanings must be clarified:

| Physical Column | Business Meaning | Common Aliases |
|---------|---------|---------|
| `dept` | Department | department |
| `hire_date` | Hire date | onboard date |
| `is_active` | Active status | active status |

**4. Metric Calculation Definitions**

The same "average salary" can have different definitions:
- Does it include departed employees?
- Does it include interns?
- Statistics by calendar month or fiscal year?

These definitions determine the filter conditions and dimension design for the metric and must be confirmed before modeling.

### Optional but Valuable Information

- Existing reports or SQL queries (helps the Agent understand actual usage patterns)
- Known data quality issues (a column with many NULLs, a table with duplicate data)
- Downstream tools (Analytics Agent, BI tools, or direct SQL queries)

## Step 2: Let the Agent Analyze Table Structure

Before generating the semantic view, the Agent should first do a round of table structure analysis, rather than jumping straight into writing the CREATE statement.

```bash
cz-cli agent run "
Analyze the two tables doc_test.employees and doc_test.departments:
1. Describe each table's column names, types, and meanings
2. Identify the relationship between the two tables (join column names and types)
3. Determine which columns are suitable as dimensions and which as metrics
4. Check whether the join column types are consistent and can be directly used as foreign keys
5. Sample a few rows to verify data quality
" --profile aliyun_shanghai_prod
```

**The Agent needs to pay special attention to these in this step:**

**Foreign key type matching**: This is the most common cause of creation failures. If `employees.dept` (string) needs to reference `departments.dept_id` (int), the types do not match, and creation will error:
```
CZLH-42000: type string of foreign key column dept does not match type int of referenced column dept_id
```

The correct approach is to find a join column with matching types, or explicitly specify the referenced column during design:
```sql
FOREIGN KEY (dept) REFERENCES depts (dept_name)  -- Explicitly reference dept_name instead of the primary key dept_id
```

**Primary key selection**: The semantic view's primary key does not have to be the physical table's primary key. Choose the column that can uniquely identify the business entity. Using `dept_name` as the primary key for the departments table (rather than `dept_id`) can make foreign key relationships more natural.

## Step 3: Generate the Semantic View

Once information is collected, give the Agent a structured instruction. **Attach the definition document directly to the instruction** -- this is the most effective way to improve generation quality:

```bash
cz-cli agent run "
Based on the following information, create an employee salary analysis semantic view for the doc_test schema:

Analysis goal: Analyze employee salary distribution by department and hire year, with department manager dimension support
Tables involved: doc_test.employees (main table), doc_test.departments (dimension table)
Relationship: employees.dept (string) references departments.dept_name (string)

Required dimensions:
- Employee name (unique identifier)
- Department
- Hire year (extracted from hire_date)
- Department manager (from departments table)
- Active status

Required metrics:
- Total employees (COUNT all employees)
- Active employee count (COUNT employees with is_active=true)
- Average salary (AVG all employees, including departed)
- Maximum salary

Requirements:
- Use bilingual (Chinese and English) synonyms
- Add Chinese comments for each dimension and metric
- View name: emp_salary_analysis
" --profile aliyun_shanghai_prod
```

## Step 4: Validate the Generated Result

**Creation success does not equal usability.** This is the most easily overlooked step.

### Required Validation Queries

```sql
-- 1. Verify basic query returns expected results
SELECT * FROM semantic_view(
    doc_test.emp_salary_analysis,
    DIMENSIONS department,
    METRICS total_employees,
    METRICS avg_salary
);
-- Check: Is the row count reasonable? Are the values within expected ranges?

-- 2. Verify cross-table dimensions (foreign key relationship working)
SELECT * FROM semantic_view(
    doc_test.emp_salary_analysis,
    DIMENSIONS manager_name,
    METRICS total_employees
);
-- Check: Are department manager dimensions returned? Are results correct?

-- 3. Verify computed dimensions
SELECT * FROM semantic_view(
    doc_test.emp_salary_analysis,
    DIMENSIONS hire_year,
    METRICS total_employees
) ORDER BY hire_year;
-- Check: Are years extracted correctly? Any unexpected NULL values?

-- 4. Verify conditional metrics
SELECT * FROM semantic_view(
    doc_test.emp_salary_analysis,
    DIMENSIONS department,
    METRICS total_employees,
    METRICS active_count
);
-- Check: Is active_count <= total_employees?
```

### Common "Silent Errors"

The following situations do not error at creation time, but query results are incorrect and must be discovered through validation:

**Arithmetic expression metrics produce incorrect results**: Metrics like `MAX(salary) - MIN(salary)` only return the first operand's value (the MAX value) at query time; the subtraction is not performed. If the Agent generates such a metric, it must be changed to calculate in outer SQL:

```sql
-- Do NOT define in METRICS: salary_range AS MAX(salary) - MIN(salary)

-- Instead, calculate in the query:
SELECT department, max_salary - min_salary AS salary_range
FROM semantic_view(my_view, DIMENSIONS department, METRICS max_salary, METRICS min_salary);
```

**Foreign key relationship not taking effect**: If cross-table dimension queries return NULL or an abnormal number of rows, it means the foreign key relationship was not correctly established. Check the output of `DESC EXTENDED` to confirm the foreign key definition is correct.

**Dimension deduplication behavior**: When passing only DIMENSIONS without METRICS, the result is a deduplicated list of dimension values, not the original row count. If you expect to see all rows, include a COUNT metric.

## Step 5: Iterative Optimization

The first version of a semantic view is usually not the final version. Common iteration needs:

**Adding missing dimensions**: Discovering a need to analyze by "salary grade" when the view doesn't have that dimension. Since ALTER does not support adding/removing dimensions, a rebuild is needed:

```bash
cz-cli agent run "
Add a salary grade dimension to the doc_test.emp_salary_analysis semantic view:
- Dimension name: salary_level
- Definition: CASE WHEN salary >= 10000 THEN 'High' WHEN salary >= 7000 THEN 'Medium' ELSE 'Low' END
- Comment: Salary grade (High/Medium/Low)
Please export the current view definition first, add the new dimension, then rebuild.
" --profile aliyun_shanghai_prod
```

**Fixing metric definitions**: Discovering that "average salary" should only count active employees. Change `AVG(salary)` to `AVG(CASE WHEN is_active = true THEN salary END)`:

```bash
cz-cli agent run "
Modify the avg_salary metric of doc_test.emp_salary_analysis:
Current definition: AVG(salary)
Change to: AVG(CASE WHEN is_active = true THEN salary END)
Meaning: Average salary of active employees only
Please rebuild the view.
" --profile aliyun_shanghai_prod
```

**Optimizing synonyms**: The Analytics Agent or users report that a certain dimension cannot be found via natural language, requiring additional synonyms.

## Design Quality Checklist

After the Agent generates the semantic view, use this checklist for a final review:

**Business Alignment**
- [ ] Each metric's definition has been confirmed with the business side (include/exclude criteria)
- [ ] Time dimension granularity and start/end range have been confirmed
- [ ] Known definitional discrepancies have been addressed through separate metrics
- [ ] Glossary has been established, synonyms cover major business terms

**Structural Completeness**
- [ ] Each logical table has a clear primary key
- [ ] Column types on both ends of foreign key relationships are consistent
- [ ] Referenced logical tables are defined before referencing tables in the TABLES clause

**Semantic Quality**
- [ ] Dimension and metric names use business terminology, not physical column name abbreviations
- [ ] Key dimensions and metrics have Chinese comments
- [ ] Time-based dimensions have `is_time = true` set
- [ ] Unique-identifier dimensions have `is_unique = true` set
- [ ] When targeting AI Agent usage, important dimensions have synonyms added

**Metric Correctness**
- [ ] No arithmetic expression metrics (`A - B`, `A / B`)
- [ ] No window function metrics (`RANK() OVER`)
- [ ] No derived metrics (metrics referencing other metrics)
- [ ] Conditional aggregation metrics (`COUNT(CASE WHEN ...)`) have been verified for correct results

**Query Validation**
- [ ] Basic dimension + metric query results match expectations
- [ ] Cross-table dimension queries (foreign key relationships) produce correct results
- [ ] Computed dimension (expression) results are correct
- [ ] Numerical magnitudes are reasonable (no unexpected NULLs or zeros)

## Complete Example: Generating a Usable Semantic View from Scratch

Below is a complete Agent conversation flow showing the entire process from requirements to a usable view.

### Conversation 1: Business Alignment

```
User: Help me create a semantic view for employee data to analyze salary by department

Agent: Sure, before starting, let me confirm a few business definitions:

1. Does "average salary" include departed employees (is_active = false)?
2. Do we need separate metrics for "all-employee average salary" and "active-employee average salary"?
3. Time dimension: calendar year or fiscal year?
4. Who is this view primarily for -- BI reports, Analytics Agent, or direct SQL queries?
```

### Conversation 2: Confirming Definitions

```
User: Average salary should count all employees, but I also need a metric for active employees only.
      Time by calendar year, primarily for the Analytics Agent.

Agent: Understood. I will define two salary metrics:
- avg_salary: AVG(salary), all employees
- active_avg_salary: AVG(CASE WHEN is_active = true THEN salary END), active employees only

Since it is primarily for the Analytics Agent, I will add bilingual synonyms for each dimension and metric.

[Query table structure]
doc_test.employees: id(int), name(string), dept(string), salary(decimal), hire_date(date), is_active(boolean)
doc_test.departments: dept_id(int), dept_name(string), manager(string)

Relationship: employees.dept(string) → departments.dept_name(string), types match, direct join possible.

Starting creation...
```

### Conversation 3: Validating Results

```
Agent: View has been created. Let me verify key queries:

[Execute validation queries]
By department: Engineering (2 people, avg 11500, active_avg 11500), Marketing (2 people, avg 8750, active_avg 9000), HR (1 person, avg 7500, active_avg NULL) ✓
Note: Diana from HR has departed, active_avg being NULL is expected (no active employee salary data)

Cross-table dimension (department manager): Frank/Grace/Henry each mapped to the correct department ✓
Hire year dimension: 2019-2023, 1 person each year ✓

Validation passed, the view is ready to use.

Suggestion: If you later need a "salary range" (max - min) metric, calculate it in the query,
not in the view definition (current version limitation):
SELECT dept, max_salary - min_salary AS range FROM semantic_view(...)
```

## Related Documents

- [Create Semantic View](semantic-view-create.md): Complete SQL syntax reference
- [Query Semantic View](semantic-view-query.md): `semantic_view()` function usage
- [Best Practices](semantic-view-best-practices.md): Common issues and limitations
- [Integrate with AI](semantic-view-ai.md): CZ-CLI and MCP tool reference
- [CZ-CLI Documentation](CZ-CLI.md): Agent access configuration
