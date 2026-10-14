# Feature Objects and Privileges

Feature permissions control whether a role can open a Singdata Lakehouse Studio module and perform specific operations within it. You can think of them as switches for Studio pages and actions: for example, they can allow a role to open **Development**, create a task, run code, or publish a task. Metadata privileges, by contrast, determine which Workspaces, Schemas, Tables, and Virtual Clusters those operations can access.

Use feature permissions when a role needs access to a Studio module without receiving unrestricted access to data objects. Use [metadata object privileges](meta-objects-and-privileges.md) to limit which tables a role can query or which Virtual Clusters it can use. Production roles usually require both types of permission.

> **Note**: Feature permissions do not grant data access. A role that can run a task from **Development** or execute a Notebook still needs permission to use the selected Virtual Cluster and access the referenced data objects.

## Feature Permission Model

Feature permissions use the following hierarchy:

```text
Lakehouse Features
└── Feature domain
    └── Feature object
        ├── READ
        │   └── Read, Download, Copy, and other atomic operations
        └── WRITE
            └── Create, Update, Execute, Publish, and other atomic operations
```

Feature domains and feature objects are authorization targets on the Studio role permissions page. They are not metadata objects that you can manage with SQL `GRANT` or `REVOKE` statements. You can grant only selected READ or WRITE operations on a feature object. `WRITE` does not automatically grant every write operation, and `READ` does not automatically grant every read-related operation.

### Feature Permissions and Metadata Privileges

| Permission type | What it controls | How to configure it | Example |
| --- | --- | --- | --- |
| Feature permission | Studio menus, pages, and specific operations | Configure it on the workspace role details page in the Web UI | Allow a role to create and run tasks in **Development** |
| Metadata privilege | Access to and operations on Singdata Lakehouse objects | Use SQL `GRANT`/`REVOKE` or grant data privileges in the Web UI | Allow a role to use `vcluster default` and query a table |
| Role grant | Whether a user receives the permissions assigned to a role | Use the Web UI or SQL `GRANT ROLE` | Grant `workspace_dev` to user `alice` |

A user's effective permissions are the union of permissions granted directly to the user and permissions inherited from all roles granted to that user. Feature permissions and metadata privileges are evaluated independently; receiving one type does not grant the other.

## Feature Object Summary

The current Studio feature permission tree contains 8 feature domains, 12 feature objects, and 53 atomic operations. The labels below preserve the English strings currently displayed in the role permission page.

| Feature domain (UI label) | Feature object (UI label) | READ operations | WRITE operations |
| --- | --- | --- | --- |
| Development | Development | Download, Read, Copy | Commit, Publish, Create, Update, Delete, Execute |
| Operation Center-Task maintenance | Task maintenance | Read | Suspend, Start, Complement, Force Refresh, Delete |
| Operation Center-Task maintenance | Task Instance maintenance | Read | Suspend, Make Success, Stop, Make Failed, Start, Rerun |
| Operation Center-Task maintenance | Complement Task maintenance | Read | Stop, Force Refresh |
| Operation Center-Task maintenance | Task Pipe maintenance | Read | Suspend, Start, Update, Delete |
| Operation Center-Alert | Alert Events | — | Suspend, Stop |
| Data-Data Quality | Data Quality Rules | — | Create, Update, Delete, Execute |
| Data-Data Quality | Data Validation Result | — | Make Success, Make Failed, Rerun |
| Compute-Virtual Cluster | VCluster-Workspace Environment | — | Update |
| Compute-Job History | Compute-Job History | Read | — |
| Analysis | notebook | Read | Create, Update, Delete, Execute |
| publish center | publish | Read | Commit, Publish, Create, Update, Delete, Execute |

> ⚠️ **Note**: The permission page uses `Read`, `Update`, and `Execute` as labels. In the Studio operation descriptions below, these labels are mapped to the corresponding business action such as view, modify, or run. Keep the UI label when configuring a role.

## Feature Objects and Privilege Points

### Development

**Entry point**: **Development**.

| Privilege point | Studio operation | Permission boundary |
| --- | --- | --- |
| READ / Download | Download data returned by a task run | The available data is still limited by the task result and data privileges |
| READ / Read | Open the task directory and view tasks, scripts, scheduling configurations, and run results | Does not grant permission to modify code, execute tasks, or query data |
| READ / Copy | Copy a task run result | Creating a copy of a task in the directory tree normally also requires `WRITE / Create` |
| WRITE / Commit | Commit development content into the publishing or operations workflow | The permission page label is **Commit**; this is separate from the later **Publish** operation |
| WRITE / Publish | Publish the development content | The permission page label is **Publish**; it controls the formal publishing step |
| WRITE / Create | Create folders, task groups, and SQL, Python, Shell, data integration, or other task nodes | Creating a task does not grant access to the data objects it references |
| WRITE / Update | Modify code, names, directories, schedules, parameters, owners, Virtual Clusters, Schemas, and dependencies | Configuration changes can affect subsequent scheduled instances |
| WRITE / Delete | Delete a development directory, task group, or task node | Taking a published task offline is controlled separately by **Operation Center → Task Maintenance** |
| WRITE / Execute | Run or stop a script, run selected SQL, and view logs and results in the editor | Also requires permission to use the Virtual Cluster and access the referenced data objects |

Task development includes authoring, debugging, scheduling configuration, and committing. Feature permissions control access to Studio operations, while SQL read and write access continues to be controlled by metadata privileges on Tables, Views, Schemas, and other objects.

### Task maintenance

**Feature domain**: **Operation Center-Task maintenance**. **Entry point**: **Operation Center → Task Maintenance**, including the task list and the **Periodic Task** tab.

| Privilege point | Studio operation | Result |
| --- | --- | --- |
| READ / Read | View the task list, task details, upstream and downstream dependencies, instance list, and committed code | Does not allow the role to modify development code |
| WRITE / Suspend | Suspend task scheduling | The scheduler stops generating or running new periodic task instances |
| WRITE / Start | Start a paused task | Normal scheduling resumes and the scheduler can generate task instances |
| WRITE / Complement | Create a data complement task from a periodic task | Configure the business time range, task node range, concurrency, and complement self-dependency |
| WRITE / Force Refresh | Force Studio to refresh task runtime status and operations information | The exact refresh scope follows the prompt displayed in the current Studio version |
| WRITE / Delete | Take a task offline from the Operation Center | The task returns to the unsubmitted state in Development; this does not delete the development file |

The **Complement** operation creates instances for historical or future business times. Viewing and handling an existing complement task is controlled by **Complement Task maintenance**.

### Task Instance maintenance

**Feature domain**: **Operation Center-Task maintenance**. **Entry point**: **Operation Center → Task Maintenance → Instance Maintenance**.

| Privilege point | Studio operation | Applicable state and impact |
| --- | --- | --- |
| READ / Read | View the instance list, instance details, dependency graph, execution code, execution logs, and operation logs | Supports troubleshooting waiting, failed, and slow-running instances |
| WRITE / Suspend | Suspend an instance that has not reached a terminal state | The instance is no longer scheduled to continue running |
| WRITE / Start | Resume a suspended instance | Studio uses **Start** for this operation in the permission page |
| WRITE / Stop | Stop a running instance | The instance is stopped and its status is set to failed |
| WRITE / Rerun | Run a completed instance again | The task's instance rerun configuration still applies |
| WRITE / Make Success | Force a failed instance to success | This can unblock downstream instances; confirm the data impact first |
| WRITE / Make Failed | Force a successful instance to failure | This can affect dependent instances and trigger alerts |

### Complement Task maintenance

**Feature domain**: **Operation Center-Task maintenance**. **Entry point**: **Operation Center → Task Maintenance → Complement Task**.

| Privilege point | Studio operation | Description |
| --- | --- | --- |
| READ / Read | View complement task information, statistics, instances, and instance details | Execution can be reviewed by year, month, or day |
| WRITE / Stop | Stop a running complement task or its execution process | Some business time points might remain incomplete, so reassess the required complement range |
| WRITE / Force Refresh | Force Studio to refresh complement and instance status | The exact refresh scope follows the prompt displayed on the current page |

The permission object uses the exact UI label **Complement Task maintenance**. Existing Studio documentation may use **backfill** or **data supplement** when describing the same business workflow.

### Task Pipe maintenance

**Feature domain**: **Operation Center-Task maintenance**. **Entry point**: the PIPE task tab or a PIPE details page under **Operation Center → Task Maintenance**.

| Privilege point | Studio operation | Corresponding PIPE behavior |
| --- | --- | --- |
| READ / Read | View PIPE configuration, runtime status, consumption latency, and run history | Corresponds to `SHOW PIPES`, `DESC PIPE`, and Job History queries |
| WRITE / Suspend | Suspend continuous ingestion for a PIPE | Corresponds to setting `PIPE_EXECUTION_PAUSED` to `true` |
| WRITE / Start | Resume continuous ingestion for a PIPE | Corresponds to setting `PIPE_EXECUTION_PAUSED` to `false` |
| WRITE / Update | Change the Virtual Cluster, batch interval, batch size, error skip count, or job hint | The COPY statement itself cannot be modified directly; recreate the PIPE when that logic must change |
| WRITE / Delete | Delete the PIPE object | Corresponds to `DROP PIPE` and stops the continuous ingestion pipeline |

### Alert Events

**Feature domain**: **Operation Center-Alert**. **Entry point**: **Operation Center → Alert → Alert Events**.

| Authorization privilege point | Studio page operation | Behavior |
| --- | --- | --- |
| WRITE / Suspend | Suppress | Stop sending repeated notifications for the current alert event for a specified period |
| WRITE / Stop | Close | Close the current alert event and stop receiving notifications for it |

The permission page uses **Suspend** and **Stop**, while the Alert page uses **Suppress** and **Close**. These names are mapped by business meaning: Suspend does not suspend an alert rule, and Stop does not stop a task instance.

### Data Quality Rules

**Feature domain**: **Data-Data Quality**. **Entry point**: **Data → Data Quality → Quality Rules**.

| Privilege point | Studio operation | Description |
| --- | --- | --- |
| WRITE / Create | Create a quality rule | Configure the validation object, built-in metric or custom SQL, expected result, trigger method, execution cluster, and timeout |
| WRITE / Update | Edit a quality rule | Change validation conditions, owner, trigger method, execution cluster, and other settings |
| WRITE / Delete | Delete a quality rule | Stops future validations produced by the rule |
| WRITE / Execute | Test-run or manually trigger a quality rule | Validate the rule configuration or run an on-demand check |

A quality rule must be able to access the validation object and use the selected execution cluster. The feature permission does not grant metadata privileges on Tables, Views, or Virtual Clusters.

### Data Validation Result

**Feature domain**: **Data-Data Quality**. **Entry point**: **Data → Data Quality → Validation Results**.

| Privilege point | Studio operation | Description |
| --- | --- | --- |
| WRITE / Make Success | Manually set a validation result to success | Can unblock an associated scheduled task |
| WRITE / Make Failed | Manually set a validation result to failure | Can trigger a quality alert or affect an associated task's state |
| WRITE / Rerun | Revalidate a validation result | Runs the current rule again; if a previously failed rule passes, no new alert is sent for the earlier failure |

The current feature permission tree does not list separate Read or Stop privileges for validation results. Page visibility and the ability to stop a running validation can also depend on a parent feature permission, role type, or the behavior of the current Studio version.

### VCluster-Workspace Environment

**Feature domain**: **Compute-Virtual Cluster**. **Entry point**: **Compute → Virtual Cluster** or the workspace compute environment configuration page.

| Privilege point | Studio operation | Description |
| --- | --- | --- |
| WRITE / Update | Modify the compute environment or Virtual Cluster configuration for a workspace | Can include specification, auto-scaling, concurrency, auto-resume, and auto-suspend settings |

This permission controls configuration through the workspace environment page. The Virtual Clusters that the role can actually operate on remain subject to Virtual Cluster metadata privileges.

### Compute-Job History

**Feature domain and object**: **Compute-Job History**. **Entry point**: **Compute → Job History**.

| Privilege point | Studio operation | Description |
| --- | --- | --- |
| READ / Read | View and filter Job History and open Job Profile to inspect stages, operators, execution plans, errors, and performance information | This feature object has no WRITE privilege and does not grant permission to stop jobs or update job configuration |

Job History includes JDBC jobs, Studio ad-hoc queries, and Studio scheduled tasks. The visible job scope can also depend on the Workspace, role, and object visibility.

### notebook

**Feature domain**: **Analysis**. **Entry point**: **Analysis → Notebook**. The permission page uses the lowercase object label `notebook`. Notebook is currently available as an invite-only preview feature.

| Privilege point | Studio operation | Description |
| --- | --- | --- |
| READ / Read | View the Notebook directory, Notebook content, cells, and execution results | Objects in the data tree remain subject to data privileges |
| WRITE / Create | Create a Notebook and add SQL, Python, or Markdown cells | Creating folders in the Notebook directory is not currently supported |
| WRITE / Update | Edit code or Markdown, modify parameters, rename or duplicate a Notebook, reorder cells, or clear cell output | Duplicating a Notebook can also require Create permission |
| WRITE / Delete | Delete a Notebook or cell | Changes the Notebook content available for subsequent collaboration |
| WRITE / Execute | Run one cell, run all cells, or stop execution | SQL cells also require permission to use the selected Virtual Cluster and access data objects |

### publish

**Feature domain**: **publish center**. **Entry point**: **publish center**.

| Privilege point | Studio operation | Description |
| --- | --- | --- |
| READ / Read | View content awaiting publication, publication details, publication records, and publication status | Supports pre-publication review and auditing |
| WRITE / Commit | Commit publication content into the publishing workflow | Keep the UI label **Commit** when configuring the role |
| WRITE / Publish | Perform the formal publishing operation | Complements **Development → Publish** while the two permission objects remain separate |
| WRITE / Create | Create a publication record or workflow item | The exact target depends on the current publish center workflow |
| WRITE / Update | Update publication content or workflow settings | The exact target depends on the current publish center workflow |
| WRITE / Delete | Delete a publication item | The exact target depends on the current publish center workflow |
| WRITE / Execute | Execute the publication workflow | The exact target depends on the current publish center workflow |

Development and publish center use separate permission objects. Development **Commit** sends development content into the next stage of the workflow, while publish center **Publish** performs the formal publication step. Granting the two operations to different roles can separate development responsibilities from production publishing.

## Permission Boundaries and Required Combinations

### Feature Permissions Do Not Replace Data Privileges

The following table shows common minimum permission combinations:

| Goal | Required feature permissions | Additional metadata or identity permissions |
| --- | --- | --- |
| Write and run SQL from Development | **Development → Development**: Read, Create/Update, Execute | Workspace membership, Virtual Cluster `USE`, and appropriate Schema and data object privileges |
| Commit a scheduled task from Development | **Development → Development**: Read, Update, Commit | Privileges on the Virtual Cluster and data objects used by the task |
| Operate production task instances | **Task Instance maintenance**: Read and the required handling operations | Access to the Workspace containing the task and instance |
| Create and test-run a quality rule | **Data Quality Rules**: Create, Execute | Metadata and query privileges on the validation object and `USE` on the execution cluster |
| Query data from a Notebook | **notebook**: Read, Create/Update, Execute | Workspace membership, Virtual Cluster `USE`, and appropriate Schema and Table/View privileges |
| Review and publish content | **publish**: Read, Commit, Publish | Membership in the target Workspace and any permissions required by the publish center workflow |

### Feature Permissions Cannot Be Granted with SQL

Feature objects and privilege points belong to Studio feature authorization. They are not SQL metadata objects such as `workspace`, `schema`, `table`, or `vcluster`. Do not use SQL like the following to grant a Studio feature permission:

```sql
-- Incorrect: Development is not a SQL metadata object
GRANT EXECUTE ON DEVELOPMENT TO ROLE role_name;
```

Configure feature permissions on the workspace role details page in the Web UI. Continue to use metadata privileges for data objects and compute resources. See [Configure Access Control](access-control-configuration.md) for role assignment and permission inspection procedures.

### High-Impact Privileges

The following operations can change production schedules, terminal instance states, ingestion pipelines, validation results, or resource costs. Grant them separately where practical and include them in operational reviews:

- Task maintenance: Suspend, Start, Delete, and Complement
- Task Instance maintenance: Stop, Rerun, Make Success, and Make Failed
- Complement Task maintenance: Stop
- Task Pipe maintenance: Suspend, Start, Update, and Delete
- Data Validation Result: Make Success, Make Failed, and Rerun
- VCluster-Workspace Environment: Update
- publish: Commit, Publish, Create, Update, Delete, and Execute

## Related Documentation

- [Metadata Objects and Privilege Points](meta-objects-and-privileges.md)
- [Configure Access Control](access-control-configuration.md)
- [Access Control Overview](access-control-general.md)
- [Explanation of Permissions for Built-in Workspace Level Roles](permissions-of-built-in-workspace-level-roles.md)
- [Task Development and Scheduling Configuration](task-develop.md)
- [Task and Instance Operations](task-instance-maintenance.md)
- [Backfilling Data](backfilling_data.md)
- [Monitoring and Alerting](monitoring_and_alerting.md)
- [Data Quality Management](data-quality.md)
- [Virtual Cluster](virtual-cluster.md)
- [Lakehouse Job History](web-job-history.md)
- [Notebook](Notebook.md)
- [Continuous Data Collection from Kafka Using Pipe](pipe-kafka.md)
