# Workspace

A workspace is the fundamental unit for **organizing and isolating resources** in Singdata Lakehouse. Multiple workspaces can be created under a single service instance, and workspaces are isolated from each other by default — tables, views, tasks, and compute clusters all belong to a specific workspace and are invisible across different workspaces by default.

You can think of a workspace as a "project space": isolate development and production environments using different workspaces, or let different business teams each use their own independent workspace.

## What a Workspace Does

| Capability | Description |
|------|------|
| Resource Isolation | Tables, views, tasks, and compute clusters all belong to a workspace and do not interfere with each other |
| Permission Management | Control member access scope through workspace roles |
| Multi-Environment Management | Isolate dev/test/prod environments with independent workspaces |
| Cross-Workspace Data Sharing | Enable data access between different workspaces through authorization |

## Organization Hierarchy

```
Service Instance
└── Workspace
    └── Schema
        └── Tables, views, functions, and other data objects
```

Users must join a workspace and be granted a role before they can use its resources.

## Workspace Roles

| Role | Code | Default Permissions |
|------|------|---------|
| Workspace Admin | `workspace_admin` | Full permissions to manage members, roles, tasks, data, and compute clusters |
| Workspace Analyst | `workspace_analyst` | Use development features and compute clusters; metadata read access to data objects is granted by default, and `SELECT` permission is required to query data |
| Workspace Developer | `workspace_dev` | Manage tasks and instances; use permissions for data and compute clusters |
| Workspace SRE | `workspace_sre` | Manage all tasks and jobs in the workspace; no compute resource usage or data object query permissions |

## Related Operations

- [Manage Workspaces](workspace-introduction.md) — Create, join, manage members
- [Schema](om-schema.md) — Namespace within a workspace
- [Cross-Workspace Data Sharing](data_sharing_between_accounts_guide.md)
