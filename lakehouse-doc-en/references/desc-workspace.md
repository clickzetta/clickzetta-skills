# DESC WORKSPACE

## Overview

Displays basic information about a specified workspace, including its creator, creation time, and type.

## Syntax

```Plain
DESC WORKSPACE <name>
```

## Parameters

- `<name>`: The workspace name.

## Return Columns

| Column | Description |
|--------|-------------|
| `name` | Workspace name |
| `creator` | Username of the creator |
| `created_time` | Creation time, format `yyyy-mm-dd hh:mm:ss` |
| `last_modified_time` | Last modification time |
| `comment` | Comment or description |
| `type` | Workspace type, e.g. `managed` |

## Examples

```sql
DESC WORKSPACE quick_start;
```

Sample output:

| info_name | info_value |
|-----------|------------|
| name | quick_start |
| creator | admin |
| created_time | 2025-01-15 10:27:21 |
| last_modified_time | 2025-01-15 11:34:39 |
| comment | |
| type | managed |

## Related Documentation

- [SHOW WORKSPACES](show-workspaces.md) — list all workspaces
- [ALTER WORKSPACE](alter-workspace.md) — modify workspace properties
- [Workspace](workspace-introduction.md) — workspace concepts and management
