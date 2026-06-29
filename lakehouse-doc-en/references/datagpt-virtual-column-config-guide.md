# Configure Virtual Columns

Virtual columns allow you to add a derived field more suitable for natural language Q&A to Analytics Agent without modifying the underlying table structure. They can encapsulate complex expressions, field concatenation, business labels, or format standardization logic into a single understandable field.

Virtual columns are not physical table fields in the Lakehouse — they are semantic enhancement configurations within the analytics domain. After creation, continue to supplement them with aliases, descriptions, field types, and field usage, just like regular fields.

---

## Why Virtual Columns Are Needed

Fields in underlying data tables often don't fully match the way business users ask questions. For example:

| Existing Fields | What Users Want to Ask About | Value of Virtual Column |
| --- | --- | --- |
| `first_name`, `last_name` | Name, customer name | Concatenate into a full name. |
| `active_subscription` | Account status | Convert to "Active/Inactive" label. |
| `latitude`, `longitude` | Geographic location | Concatenate or derive into a location field. |
| Multiple status fields | Business status | Use CASE WHEN to generate a clearer business status. |

Without virtual columns, the model needs to infer the expression each time on the fly, which can produce inconsistent SQL. Virtual columns lock in commonly used expressions.

---

## Applicable Scenarios

| Scenario | Example |
| --- | --- |
| Field concatenation | Concatenate `first_name` and `last_name` to get a full name. |
| Business labels | Generate "Active Account / Inactive Account" based on `active_subscription`. |
| Status normalization | Convert multiple status codes into a unified business status. |
| Format standardization | Unify casing, remove extra spaces, handle null values. |
| Time derivation | Extract date, month, or year from a timestamp. |
| Complex expression reuse | Encapsulate frequently used CASE WHEN or calculation expressions as a field. |

Virtual columns are especially suitable for scenarios where "users frequently ask about something, but there is no direct field in the underlying table".

---

## Configuration Entry Point

The general path to virtual column configuration:

1. Go to **Administration** -> **Analytics Domain Management**.
2. Open the target analytics domain.
3. Go to the **Data** tab.
4. Click **Tables**.
5. Click the table display name to enter the table detail page.
6. Add or configure virtual columns in **Table Schema**.

The entry point name may differ slightly across page versions, but virtual columns typically appear in the table field configuration area.

---

## Practical Validation Case

In an actual validation, a virtual column was created in the accounts table to concatenate names:

```sql
concat(first_name, ' ', last_name)
```

After running validation, results like the following were returned:

- `Macy Kub`
- `Kim Cormier`

After saving, the field appears as a virtual column in the table schema.

This case shows:

- Virtual column expressions need to be validated by running first.
- Validation results should be checked to confirm sample values meet expectations.
- After saving, field semantic configuration still needs to be supplemented — otherwise the model may not know it represents "full name".

---

## Common Expressions

### Field Concatenation

```sql
concat(first_name, ' ', last_name)
```

Suitable for generating name fields, region hierarchies, codes combined with names, and similar fields.

### Null Value Handling

```sql
coalesce(country, 'Unknown')
```

Suitable for converting null values to a default value understandable by business users.

### Classification Labels

```sql
CASE
  WHEN active_subscription = TRUE THEN 'Active Account'
  ELSE 'Inactive Account'
END
```

Suitable for converting boolean values or status codes into business labels.

### Time Derivation

```sql
date_trunc('month', created_at)
```

Suitable for generating time dimensions like month, quarter, or year.

### Numeric Tiering

```sql
CASE
  WHEN seats >= 100 THEN 'Large Account'
  WHEN seats >= 10 THEN 'Medium Account'
  ELSE 'Small Account'
END
```

Suitable for generating customer tiers, amount tiers, risk levels, and other business dimensions.

---

## Must Supplement Field Semantics After Configuration

After successfully creating a virtual column, only a derived field has been added. For Analytics Agent to use it correctly, field semantics must also be configured.

| Configuration Item | Recommendation |
| --- | --- |
| Field Alias | Write business names that users would say, e.g., "customer name", "account status", "customer tier". |
| Field Description | Explain how the virtual column is calculated and what questions it is suitable for. |
| Field Type | Choose categorical, continuous, time, or other type based on the result. |
| Field Usage | Determine whether it is suitable as a dimension, filter, or measure. |
| Hidden Status | If it is only an intermediate field that users should not directly use, it can be hidden. |

For example, a name concatenation virtual column can be configured as:

| Configuration Item | Example |
| --- | --- |
| Field Alias | Customer name, full name |
| Field Description | Concatenated from `first_name` and `last_name`; used for displaying or querying accounts by name. |
| Field Type | `CATEGORICAL` |
| Field Usage | `DIM`, `FILTER` |

---

## Relationship with Field Semantics

Virtual columns and field semantics should be used together.

| What Virtual Columns Solve | What Field Semantics Solve |
| --- | --- |
| No ready-made field in the underlying table | What this field is called in business terms |
| Expression needs to be reused | How users would ask about it |
| Need to standardize values | Whether the field is suitable as a filter, dimension, or measure |
| Need to derive labels | Whether the field should be used in Q&A |

If you only create a virtual column without configuring semantics, the system may still not be able to use it reliably.

---

## Difference from Answer Builders

Both virtual columns and answer builders can encapsulate logic, but they operate at different levels.

| Comparison | Virtual Column | Answer Builder |
| --- | --- | --- |
| Target | A single field | A SQL template |
| Typical Use | Derived fields, labels, concatenation, standardization | Multi-metrics, JOINs, complex definitions, detail queries |
| Appears in Table Schema | Yes, appears as a field in the table schema | Exists as an independent analysis template |
| How It's Used in Q&A | Selected like a regular field | Called as an executable metric template |

Simple guideline:

- If you just "need a better field", use a virtual column.
- If you "need a complete query logic", use an answer builder.

---

## Design Recommendations

### 1. Virtual Columns Should Express Stable Business Meaning

Do not create virtual columns for one-time questions. Virtual columns are suitable for stable, frequently reused fields.

Recommended:

- Full name
- Account status
- Customer tier
- Month
- Regional hierarchy

Not recommended:

- Temporary filter conditions
- One-time analysis expressions
- Fields that duplicate existing fields without clearer semantics

### 2. Avoid Over-Nesting Virtual Columns

Virtual column expressions should remain clear. If the logic is very long, spans multiple tables, or involves multiple complex aggregations, consider using an answer builder instead of a virtual column.

### 3. Be Careful with Null Values and Data Types

When creating virtual columns, consider:

- Whether input fields may be null.
- Whether string concatenation may produce extra spaces.
- Whether CASE WHEN covers all branches.
- Whether the output type matches expectations.

### 4. Do Not Concatenate Sensitive Fields into More Easily Exposed Fields

If underlying fields contain sensitive information such as phone numbers, emails, or ID numbers, they should not be combined into a virtual column that makes them more easily accessible in Q&A. If necessary, hide the related fields.

---

## Validation Methods

After configuring virtual columns, validate three things:

| Validation Item | Method |
| --- | --- |
| Is the expression correct? | Run validation and check sample results. |
| Are field semantics taking effect? | Ask a natural language question and see if the system uses the virtual column. |
| Does the SQL match expectations? | Check the SQL in the Q&A result. |

Sample validation questions:

- "Show a few customer names"
- "Count accounts by account status"
- "View active rate by customer tier"
- "New account count for each month recently"

If the SQL does not use the virtual column, typically check whether the alias, description, field type, and field usage have been fully configured.

---

## Common Issues

| Issue | Possible Cause | Recommended Action |
| --- | --- | --- |
| Virtual column validation fails | SQL expression syntax error or field name error | Fix the expression according to the underlying data source SQL syntax. |
| Virtual column result is empty | Input field is null or expression doesn't handle nulls | Use `coalesce` or similar functions to handle null values. |
| Q&A doesn't use the virtual column | Missing alias, description, or field usage | Supplement field semantics and re-validate. |
| Virtual column appears in inappropriate groupings | Field usage configuration is unreasonable | Adjust to filter, measure, or hidden. |
| Expression is too complex to maintain | Virtual column is taking on a query template role | Switch to an answer builder. |
| Sensitive information is exposed | Virtual column concatenated sensitive fields | Hide fields or delete the virtual column, and review permission configuration. |

---

## Pre-Launch Checklist

- Has the virtual column expression been successfully validated?
- Do sample results match business expectations?
- Have null values been handled?
- Has a business-friendly alias been set?
- Has a field description been added?
- Is the field type correct?
- Is the field usage reasonable?
- Will it expose sensitive information?
- Has it been validated with a natural language question?
- Has the SQL been checked to confirm the virtual column is used correctly?

The goal of virtual columns is to transform expressions in the underlying table that are "not convenient for users to directly understand or use" into business fields that Analytics Agent can reliably understand.

## Related Documentation

- [Configure Analytics Domain](datagpt-domain-management-guide.md) — Analytics domain and table configuration that virtual columns belong to
- [Configure Field Semantics](datagpt-field-semantic-config-guide.md) — Alias, type, and usage configuration for virtual columns
- [Answer Builder Best Practices](datagpt-answer-builder-best-practices.md) — Differentiating applicable scenarios for virtual columns and answer builders
- [Metrics and Answer Builder](metrics_answer_build.md) — Configuration relationship between fields and metrics
