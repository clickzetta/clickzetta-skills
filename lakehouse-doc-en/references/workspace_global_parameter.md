# Workspace Global Parameters

Workspace global parameters are parameters maintained uniformly at the Workspace level. They are suited for storing configuration values that multiple task groups, composite tasks, or tasks will reuse — such as database addresses, environment identifiers, and business date variables.

If you need to repeatedly maintain the same parameter across multiple task groups or composite tasks, and each change requires updating each one individually (which risks omissions and inconsistency), use workspace global parameters.

With global parameters, you maintain one shared value in the workspace and have downstream parameters reference it, achieving "change once, take effect everywhere."

The core mechanism of global parameters is **layer-by-layer reference and override**: global parameters serve as the top-level parameters, referenced by task group parameters; composite task parameters and task parameters then reference higher-level parameters in turn. When a task runs, the system resolves parameters by hierarchy and stops looking upward when it encounters an explicit value assignment.

> ⚠️ **Note**: If there is no **Workspace Settings → Global Parameters** entry in the current interface, the feature is not yet open for this workspace. Refer to the actual page for availability.

## Applicable Scenarios

Global parameters are suited for shared configuration reused across task groups and tasks.

| Scenario | Example | Value of using global parameters |
|---|---|---|
| Database connection config | `db_host = prod.singdata.com` | Only one place to update when the production database address changes |
| Environment identifier | `env = prod` | Multiple task groups use a consistent environment context |
| Shared date variable | `biz_date = $[yyyy-MM-dd, -1d]` | Multiple pipelines use the same business date definition |
| Shared Schema name | `target_schema = ads_prod` | Avoids each task group maintaining different target schemas |

Temporary values used only within a single task should not be placed in global parameters. For single-task configurations, continue using [Task Parameters](task_param.md).

## Parameter Hierarchy

Parameter priority from highest to lowest:

```
Task parameter > Composite task parameter > Task group parameter > Global parameter
```

Parameters closer to a specific task have higher priority. If a task parameter has an explicit value already set, the system uses that value at runtime and does not look upward to task group parameters or global parameters.

## Global Parameter Types

### Regular Parameters

Regular parameters store a fixed value or expression. After a downstream parameter references a regular parameter, the downstream receives the current value of the global parameter at runtime.

Example:

```
Global regular parameter: env = prod
Global regular parameter: biz_date = $[yyyy-MM-dd, -1d]
Global regular parameter: db_host = prod.singdata.com
```

Regular parameters are suited for:

- Fixed strings, numbers, booleans, and date values
- Date expressions calculable at task scheduling time
- Configuration items shared across multiple task groups

### Input Parameters

Input parameters receive output values from upstream tasks. Rather than just holding a fixed default value, an input parameter is a definition of "a parameter that takes its value from upstream output."

Input parameters are commonly used to pass run results between upstream and downstream tasks. For example:

```
Upstream SQL output: SELECT 'ods.order_source' AS table_name;
Downstream input parameter: source_table
Downstream code reference: SELECT * FROM ${source_table};
```

After referencing an input parameter, you must also configure the parameter source, including the upstream task and its output parameter. Otherwise the system knows the parameter name but not where to get the value at runtime.

## Create Global Parameters

1. Enter **Workspace Settings**.
2. Open the **Global Parameters** tab.
3. Click **New**.
4. Select parameter type: **Regular Parameter** or **Input Parameter**.
5. Fill in the parameter name, data type, value or source description, and description.
6. Save the parameter.

:-: ![](/.topwrite/assets/image_1781606339782.png =502)

Global parameters include the following fields:

| Field | Required | Description |
|---|---|---|
| Parameter name | Yes | Unique identifier. Supports English letters, numbers, and underscores; max 64 characters |
| Parameter type | Yes | Select **Regular Parameter** or **Input Parameter** |
| Parameter value | Yes | Different for regular vs. input parameters. 1) Regular parameter: enter the value directly — can be a system built-in or a constant. See [Task Parameters](task_param.md). 2) Input parameter: select the output value from an upstream task. See [Context Parameters](input_output.md) |
| Default value | Required for input parameters | When the global parameter is an input parameter and the scheduling chain has not configured a reference to the required upstream task, the parameter cannot retrieve its output value. In this case, the default value is used as the global parameter value. |

> ⚠️ **Note**: A parameter name cannot be modified after creation. Modifying a parameter name would break existing references — if you need to change the name, create a new parameter and gradually migrate the references.

## Reference Global Parameters

### Regular Parameter Reference Example

Referencing a regular parameter is straightforward. A task group parameter, composite task parameter, or task parameter can reference a global regular parameter.

1. In **Workspace → Parameters**, configure the global parameter with name `workspacename`.

:-: ![](/.topwrite/assets/image_1781606888648.png =633)

2. In the task script, enter the custom variable `${workspacename}`. In the parameter config, set the value source to "Workspace."

:-: ![](/.topwrite/assets/image_1781606850600.png =636)

At runtime, the task receives the current configured value of the global parameter `workspacename`.

### Input Parameter Reference Example

1. Create a standard task (SQL, Python, or Shell type). In the parameter config, configure an output parameter.

:-: ![](/.topwrite/assets/image_1781607992676.png =632)

2. In global parameters, configure parameter `city_name` with its value sourced from the upstream task's output. Also configure a default value — if the step 1 task is not linked in the scheduling chain, the parameter value comes from "default value."

:-: ![](/.topwrite/assets/image_1781608035245.png =622)

3. Configure the scheduling chain.

Reference the global parameter value in the scheduling chain, and actively add the upstream task whose output feeds the input parameter to the scheduling chain at the root node.

If the upstream output task is not added to the task chain, the global input parameter `city_name` defaults to the fixed value `beijing` for the entire task chain.

:-: ![](/.topwrite/assets/image_1781607967045.png =737)

## Edit and Delete Global Parameters

### Edit a Global Parameter

You can modify a global parameter's value and description.

The parameter name cannot be modified. If you need to change the name, create a new global parameter and switch downstream references to the new one.

For input parameters, after modifying the parameter definition also check whether the upstream source configuration at downstream references is still valid.

### Delete a Global Parameter

Before deleting a global parameter, the system checks for downstream references.

If there are no downstream references, you can delete directly.

If downstream references exist, the system shows the impact scope and requires a second confirmation. After deletion, downstream parameter references become invalid and related task runs may fail.

> ⚠️ **Note**: Do not silently delete a referenced global parameter. Before deleting, confirm that the task groups, composite tasks, and tasks referencing it have completed migration.

## Limitations

| Limitation | Description |
|---|---|
| No circular references | Global parameters cannot reference other parameters; they can only be referenced by downstream parameters |
| Parameter names must be unique | Parameter names are unique within the workspace |
| Parameter names cannot be modified | Prevents breaking existing references |
| Input parameters require an upstream source | After referencing an input parameter, configure the upstream task and output parameter |
| Input parameters support only one level of passing | Upstream output passes only to directly dependent downstream |
| Input parameter value size limit | Context parameters support a maximum of 2 MB |
| Deletion requires impact confirmation | Deleting a referenced global parameter requires a second confirmation |
| Permissions align with workspace | Workspace members can read; workspace administrators can create, edit, and delete |
| Does not affect unreferenced tasks | Task groups or tasks that do not reference global parameters continue to behave normally |

## FAQ

### What is the difference between a regular parameter and an input parameter?

A regular parameter directly maintains a value or expression; downstream receives this value at runtime. An input parameter does not just hold a fixed value — it takes its value from an upstream task's output parameter, so referencing it requires additionally configuring the upstream source.

### After modifying a regular global parameter, do tasks need to be reconfigured?

No. As long as downstream parameters have already established a reference relationship, the next run will use the new value after the global parameter changes.

### Why does referencing an input parameter require configuring an upstream source?

Because an input parameter's value comes from upstream task output. The global input parameter only defines the parameter name and reuse relationship. The specific upstream task and output parameter to pull from must be configured at the reference site.

### When a task parameter and a global parameter have the same name, which value is used?

If the task parameter has an explicit value set, that value takes priority. An explicit assignment stops the upward lookup chain.

### Can global parameters be referenced directly in SQL?

It is recommended to pass them through task group parameters, composite task parameters, or task parameters first, then reference them in code. This keeps the parameter source clear and lets the interface display the full reference chain.

### Does deleting a global parameter affect already-completed run instances?

No — it does not affect completed historical run results. However, if downstream tasks still reference that global parameter, subsequent runs may fail because the parameter cannot be resolved.

## Related Documentation

| Document | Description |
|---|---|
| [Task Parameters](task_param.md) | Use dynamic parameters in a single task |
| [Task Parameter Syntax Reference](task_param_reference.md) | Syntax for built-in parameters, time expressions, and time functions |
| [Task Parameter Examples](task_param_examples.md) | Common task parameter usage scenarios |
| [Task Group](task_group.md) | Manage tasks and task group parameters centrally |
| [Composite Task](composite_task.md) | Manage multi-node workflows and composite task parameters |
