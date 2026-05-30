# Grants Configuration Guide

## Basic Usage

Configure `grants` in the dbt model's `config` block to automatically execute grants after each `dbt run`:

```sql
{{ config(
    materialized='table',
    grants={
        'select': ['workspace_analyst']    -- grant SELECT privilege to the specified role
    }
) }}
select ...
```

## Dynamic Roles (overridden via dbt variables)

Use `var()` to make the role name overridable at runtime, which simplifies multi-environment deployments:

```sql
{{ config(
    materialized='table',
    grants={
        'select': [var('grant_role', 'workspace_analyst')]
    }
) }}
```

Override at runtime:
```bash
dbt run --vars '{"grant_role": "my_custom_role"}' --select my_model
```

## Verifying That Grants Are in Effect

Use a singular test to verify:

```sql
-- tests/assert_grants_my_model.sql
-- Returns 0 rows = grant exists (test passes), returns 1 row = grant missing (test fails)
with grants as (
    show grants on TABLE {{ target.database }}.{{ target.schema }}.my_model
),
matched as (
    select *
    from grants
    where
        granted_type = 'PRIVILEGE'
        and upper(split(privilege, ' ')[0]) = 'SELECT'
        and granted_to = 'ROLE'
        and split(grantee_name, '.')[array_size(split(grantee_name, '.')) - 1]
            = '{{ var("grant_role", "workspace_analyst") }}'
)
select 'grant not found' as reason
where (select count(*) from matched) = 0
```

## When to Use Grants

- Multi-tenant scenarios: analysts from different business domains should only access their own marts
- Data security requirements: sensitive data (finance, user information) needs restricted access
- Production environment standardization: ensures permission configuration is consistent after every deployment, without relying on manual operations

## Notes

- The `grants` configuration only takes effect when `materialized='table'` or `incremental`; views are not supported
- Role names must be created in the ClickZetta workspace in advance; dbt does not create roles automatically
- After a full rebuild (`--full-refresh`), permissions are re-granted and will not be lost
