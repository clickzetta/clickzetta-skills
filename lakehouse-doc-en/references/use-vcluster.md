
# USE VCLUSTER

Switches the compute resource (Virtual Cluster) used by the current session.

## Syntax

```SQL
USE VCLUSTER vc_name;
```

## Parameters

| Parameter | Required | Description |
|------|------|------|
| `vc_name` | Yes | Name of the compute resource to switch to, case-insensitive |

## Return Value

This command has no return result. Upon successful execution, the current session's compute resource is switched to the specified `vc_name`.

You can confirm the currently active compute resource using `SELECT CURRENT_VCLUSTER()`:

```SQL
SELECT CURRENT_VCLUSTER();
-- Returns the name of the compute resource used by the current session, e.g., "default"
```

## Examples

1. Switch to the general compute resource named `DEFAULT`:

```SQL
USE VCLUSTER DEFAULT;
SELECT CURRENT_VCLUSTER();
```

2. Switch to a high-performance analytics compute resource:

```SQL
USE VCLUSTER DEFAULT_AP;
```

3. After switching, execute a query -- it will run on the new compute resource:

```SQL
USE VCLUSTER DEFAULT_AP;
SELECT COUNT(*) FROM doc_test.orders;
```

## Notes

- When connecting using client tools (such as SQLLine, DBeaver), `USE VCLUSTER` remains in effect for the entire session.
- In the Lakehouse Studio interface, it is recommended to switch compute resources primarily through the dropdown menu at the top of the page. If you execute this command directly in the SQL editor, you must select the `USE VCLUSTER` statement together with the subsequent SQL before executing; otherwise, the switch only takes effect temporarily for the current statement.
- The specified compute resource must already exist and be in an available state. You can view all available compute resources using `SHOW VCLUSTERS`.
- If the compute resource is in `SUSPENDED` state, it will automatically wake up when SQL is first executed after switching, which may cause a brief delay.

