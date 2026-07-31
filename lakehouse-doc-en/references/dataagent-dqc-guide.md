# Data Engineering Agent DQC Data Quality Rules Guide

This guide covers how to use the Data Engineering Agent to view, create, review, and clean up DQC data quality rules. It focuses on rule metadata itself and does not cover the full picture of alert integration and production blocking strategies after rule execution.

## Explore First, Then Create Rules

DQC scenarios are generally not suited to creating rules directly from the start.

The more natural approach is:

- First check whether the target table already has rules
- Confirm whether the rule type, blocking level, and trigger method are appropriate
- Then create test or formal rules

These scenarios are better suited to an exploratory start:

- Help me first check whether this table already has DQC rules.
- Help me decide whether this scenario is better suited to a weak rule or a strong rule.
- Help me check whether there are any duplicate or overlapping rules in the existing rule set.

Once the check target, rule type, and trigger method are all clear, moving into rule creation is more stable.

## What It Can Do

Based on actual operations, the Data Engineering Agent can assist with at least the following:

- Check whether a table already has DQC rules
- Create new DQC rules
- Describe rule type, check target, threshold, blocking level, and trigger method
- Delete test rules

These operations generally modify governance metadata, not the business data itself.

## Check Existing Rules First

Before adding new rules, check whether the target table already has rules to avoid duplicates.

Recommended question:

> Please do read-only operations only: list the DQC data quality rules associated with `{schema}.{table}`, or confirm there are none. Return rule name, rule type, check target, weak/strong/blocking level, and trigger method. Do not create, modify, or delete any rules.

If the result is empty, explain it as "no rules currently exist," not as a feature anomaly.

## Test Rule Example

In actual validation, a test rule was created for table:

```text
public.demo_xe_sales
```

with the following configuration:

| Field | Value |
|---|---|
| Rule type | `table_count` |
| Check target | `public.demo_xe_sales` |
| Threshold condition | Row count `> 0` |
| Weak/strong/blocking level | Weak rule, `level=0` |
| Trigger method | `REST`, manual trigger |

This example shows:

- DQC supports table-level count-type rules
- Rules can be configured as non-blocking
- Manual trigger is supported, rather than automatic schedule blocking

## What to Specify When Creating Rules

To avoid accidental creation, specify in your request:

- Rule name
- Check target
- Rule type
- Threshold
- Weak/strong/blocking level
- Trigger method
- Whether this is only a test rule
- Whether immediate execution is allowed

Recommended question:

> Please create a DQC rule for `{schema}.{table}` for testing purposes only. Rule name: `{rule_name}`. Requirements: check `{rule_condition}`, use `{weak rule/strong rule}`, trigger method `{REST/manual}`. Do not associate with production pipelines. Do not trigger rule execution. Do not modify data. After creation, return the rule ID, rule type, check target, threshold, weak/strong/blocking level, and trigger method.

## Review After Creation

After a rule is created successfully, do not stop at the "created" notification. Review:

- Rule ID
- Rule name
- Rule type
- Check target
- Threshold condition
- Weak/strong/blocking level
- Trigger method

For test rules, also confirm:

- Not bound to production tasks
- Not auto-published
- Not immediately executed

## Delete Test Rules

Clean up test rules promptly after validation to avoid polluting the formal governance rule set.

Recommended question:

> Please delete the test DQC rule just created, with rule ID `{rule_id}`. Only delete this test rule; do not delete other rules. After deletion, query the DQC rules for `{schema}.{table}` again to confirm the cleanup.

After deletion, query again and confirm that the table's related rules are empty, or that only formal rules remain.

## Conclusions from Actual Operations

Based on completed validation, conclusions that can be stated with confidence:

- DQC rules can be queried in read-only mode to check whether they exist
- Weak, non-blocking rules can be created
- Trigger method can be configured as `REST` manual trigger
- Creating rules does not directly modify business table data
- Test rules can be deleted after validation, and cleanup can be confirmed by querying again

## Rules Worth Building First

If the team is new to DQC, start with simple rules:

- Row count > 0
- Key fields are not null
- Primary key or business key deduplication
- Numeric range checks

Build the low-controversy, low-risk, easy-to-explain rules first, then gradually expand to more complex SQL rules.

## Related Documentation

- [Data Engineering Agent](dataagent.md)
- [Safe Operation Guide](dataagent-safe-operation-guide.md)
- [Job Diagnosis Guide](dataagent-job-diagnosis-guide.md)
- [Prompt Examples](dataagent-prompt-examples.md)
