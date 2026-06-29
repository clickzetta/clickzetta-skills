# Data Engineering Agent DQC Best Practices

This guide covers how to design more reliable data quality rules for Data Engineering Agent usage, with an emphasis on reducing false positives, making rules easy to verify, and enabling gradual rollout.

## Explore First, Then Tighten Gradually

Data quality rules are easy to configure too aggressively from the start. A more stable approach is:

- Check whether existing rules already exist
- Start with simple, weak rules
- Validate rule logic with test rules or manual triggers first
- After validation, gradually upgrade to stronger blocking strategies

These scenarios are better suited to an exploratory start:

- Help me first check whether this table already has any rules.
- Help me identify which rules would be most valuable to build first.
- Help me decide whether this rule is better as a weak rule or a strong rule.

## Start with Simple Rules

When first building DQC, start with low-controversy, easy-to-explain rules:

- Row count > 0
- Key fields are not null
- Primary key or business key deduplication
- Numeric range checks

Do not start with a large number of complex SQL rules — users will find it hard to understand what each rule is actually checking.

## Use Weak Rules First

If the team is new to DQC, start with:

- Weak rules
- Non-blocking level
- Manual triggers

This lets you verify that the rules themselves make sense before deciding whether to promote them to strong rules that affect scheduling.

## Give Test Rules Obvious Names

Test rules should use a clear test prefix, for example:

```text
TempDev_{table_name}_{rule_meaning}_{date}
```

Benefits:

- Immediately identifiable as not a formal rule
- Easy to clean up after validation
- Will not be confused with formal governance rules

## Manual Triggers Are Better During Validation

If rules are still in the validation phase, using `REST` or manual triggers is usually more reliable. This avoids:

- Affecting scheduling as soon as a rule is created
- Blocking production tasks before rules are calibrated

Do not connect test rules into automatic blocking flows before they are mature.

## Always Review After Creation

After a rule is created, confirm:

- Whether the rule type is correct
- Whether the check target is correct
- Whether the threshold is correct
- Whether the blocking level matches expectations
- Whether the trigger method matches expectations

Do not stop at "created successfully."

## Clean Up Test Rules After Validation

Test rules are not long-term assets. After validation:

- Delete test rules
- Query again to confirm rules have been cleaned up
- Keep only formal rules

This prevents the production environment from accumulating large numbers of invalid rules.

## The Most Valuable First Batch of Rules

If you can only build a small number of rules first, prioritize:

- Table row count > 0
- Key business fields are not null
- Deduplication rules

These three rule types are the easiest to explain and quickest to deliver visible value.

## Related Documentation

- [Data Engineering Agent](dataagent.md)
- [DQC Data Quality Rules Guide](dataagent-dqc-guide.md)
- [Safe Operation Guide](dataagent-safe-operation-guide.md)
- [Prompt Examples](dataagent-prompt-examples.md)
