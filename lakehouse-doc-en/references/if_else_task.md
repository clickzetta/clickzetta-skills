# Branch Task

## Concept

A branch task implements conditional routing in workflow scheduling. It dynamically determines which downstream path to trigger based on the output of an upstream task. Similar to a For-each loop task, a branch task must be used together with an upstream task that produces output parameters. It evaluates expressions against the output dataset and maps results to different downstream paths.

This article describes the structure and logic of branch tasks.

***

## Use Cases

If you are designing a workflow and need to decide how to proceed based on the output of a specific node, you can use a branch task node to select the execution path.

## How It Works

^

1. **Upstream task output**: The upstream task (SQL, Python, Shell, etc.) passes a dataset to the downstream branch node via the `$[output]` parameter.

2. **Branch task**: Receives the upstream dataset, evaluates a series of expressions against it, and determines which downstream path to trigger based on the results.

   * **Input parameters**: Configure which upstream task to receive the output from, in the format `${parameter_name}={output}:upstream_task_name`.
   * **Expressions**: Use built-in functions to perform logical evaluation. When an expression evaluates to `true`, the downstream path for that branch is triggered.
   * **Branch output name**: Each branch condition has a corresponding output name, which is used to establish dependencies with downstream tasks.

3. **Downstream task reference**: When a downstream task configures its dependency, it must specify which output name of the upstream branch node to associate with.

***

## Steps

### Creating a Branch Task

In the task list or within a composite task/task group, click New Task and select the task type as **Branch Task**.

The branch task uses a visual configuration page. Each branch requires the following:

**Branch Condition**

Configure the evaluation expression for the current branch. For supported functions, see the Supported Expression Functions section below.

* If the expression evaluates to `true` at runtime, the branch condition is met.
* If the expression fails to parse at runtime, the entire branch node is set to failed.
* Branch conditions support global variables and parameters defined in the node context. For example, `${input}` can be a node input parameter defined on the branch node.

**Branch Output Name**

The output identifier produced after the branch condition is evaluated. Used to establish dependencies with downstream tasks.

* When the branch condition is met: The downstream node associated with the corresponding output name is triggered.
* When the branch condition is not met: The downstream node associated with the corresponding output name is not executed, and its status is set to **Ended because branch condition was not met**.

Output name format: Supports Chinese characters, English letters, and underscores `_`. Maximum 128 characters. **Duplicate output names are not allowed within the same branch task**.

**Branch Description**

Optional. A brief description of the branch.

### Configuring Downstream Tasks for a Branch

After a branch condition is triggered, the downstream nodes that should run need to be configured accordingly.

Select the downstream node you want to run, open it, and configure "Scheduling Configuration": in the scheduling dependencies, select the specific output name within the branch task.

Example: A branch node has two downstream nodes named `aaa` and `bbb`. When branch condition 1 is met, the `aaa` node runs. When branch condition 2 is met, the `bbb` node runs. When configuring the branch node, the output names can be set freely — for example, branch 1 maps to output name `1234` and branch 2 maps to output name `2324`. Both become output names of this branch node. The downstream `aaa` node must depend on output name `1234`, and the `bbb` node must depend on output name `2324`.

## Supported Expression Functions

> **Note**
>
> * Function names are **case-insensitive**.
> * `and`, `or`, and `concat` support variable arguments (1 or more).
> * `union` and `intersection` require at least 2 arguments.
> * `guid` accepts no arguments.
> * All other functions have a fixed number of arguments. Passing the wrong number of arguments will cause an expression parsing error and set the branch status to failed.

**Boolean conversion rules**: `null`, empty string, blank string, `false`, and the number `0` are treated as `false`. `true` and non-zero numbers are treated as `true`. Other non-numeric strings are **not** treated as `true`.

**Currently not supported**: Mathematical operations, date/time functions, JSON Path / object property access, regular expression matching, null coalescing, and similar functions.

***

### Logical Functions

| Function Signature     | Return Type | Description                                                                                                                        |
| ---------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `and(arg1, arg2, ...)` | `boolean`   | Returns `true` when all arguments convert to `true`. Supports 1 or more arguments. Example: `and(true, bool(1), equals('a', 'a'))` |
| `or(arg1, arg2, ...)`  | `boolean`   | Returns `true` when any argument converts to `true`. Supports 1 or more arguments.                                                 |
| `not(arg)`             | `boolean`   | Returns the boolean negation of the argument.                                                                                      |

***

### Comparison Functions

When both sides can be converted to numbers, comparison is numeric; otherwise, lexicographic string comparison is used.

| Function Signature             | Return Type | Description                                            |
| ------------------------------ | ----------- | ------------------------------------------------------ |
| `equals(left, right)`          | `boolean`   | Returns `true` if the two normalized values are equal. |
| `greater(left, right)`         | `boolean`   | `left > right`                                         |
| `greaterOrEquals(left, right)` | `boolean`   | `left >= right`                                        |
| `less(left, right)`            | `boolean`   | `left < right`                                         |
| `lessOrEquals(left, right)`    | `boolean`   | `left <= right`                                        |

***

### Collection Functions

Collection functions apply to arrays (`List` / `Collection` / `JSONArray`) and strings. Some also support dictionaries (`JSONObject` / `Map`).

| Function Signature                | Return Type        | Description                                                                                                                                        |
| --------------------------------- | ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `contains(container, expected)`   | `boolean`          | String: checks if the substring is contained. Collection: compares items by normalized value. JSONObject / Map: checks if the key exists.          |
| `empty(value)`                    | `boolean`          | Returns `true` for `null`, empty string, empty collection, or empty JSONObject / Map.                                                              |
| `first(value)`                    | First element      | String: returns the first character. List / Collection: returns the first element. Returns `null` when empty.                                      |
| `last(value)`                     | Last element       | String: returns the last character. List / Collection: returns the last element. Returns `null` when empty.                                        |
| `length(value)`                   | `integer`          | String: returns character count. Collection / Map: returns element count. Returns `0` for `null`.                                                  |
| `skip(value, count)`              | Same as input type | Skips the first `count` characters or elements. Returns the original value when `count < 0`, non-integer, or `value` is `null`.                    |
| `take(value, count)`              | Same as input type | Keeps the first `count` characters or elements. Returns the original value when `count < 0`, non-integer, or `value` is `null`.                    |
| `union(list1, list2, ...)`        | `List`             | Merges multiple lists with deduplication, preserving first-occurrence order. All arguments must be convertible to lists, otherwise returns `null`. |
| `intersection(list1, list2, ...)` | `List`             | Returns the intersection of multiple lists, ordered by the first list. All arguments must be convertible to lists, otherwise returns `null`.       |
| `join(list, separator)`           | `String`           | Joins all list elements with the separator. The first argument must be convertible to a list, otherwise returns `null`.                            |

***

### String Functions

| Function Signature                  | Return Type    | Description                                                                                                                                                                 |
| ----------------------------------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `concat(arg1, arg2, ...)`           | `String`       | Concatenates all arguments in order. `null` arguments are ignored. Supports 1 or more arguments.                                                                            |
| `guid()`                            | `String`       | Generates a random UUID string. Accepts no arguments.                                                                                                                       |
| `indexOf(text, search)`             | `integer`      | Returns the position of the first occurrence of the substring. Returns `-1` if not found.                                                                                   |
| `lastIndexOf(text, search)`         | `integer`      | Returns the position of the last occurrence of the substring. Returns `-1` if not found.                                                                                    |
| `replace(text, oldValue, newValue)` | `String`       | Replaces all matching substrings. Returns empty string if `text` is `null`. Treats `oldValue` or `newValue` as empty string when `null`.                                    |
| `split(text, separator)`            | `List<String>` | Splits the string by the separator. Splits by single character when separator is empty. Returns empty list if `text` is `null`.                                             |
| `startsWith(text, prefix)`          | `boolean`      | Checks if the string starts with the specified prefix.                                                                                                                      |
| `endsWith(text, suffix)`            | `boolean`      | Checks if the string ends with the specified suffix.                                                                                                                        |
| `substring(text, start, length)`    | `String`       | Extracts `length` characters starting from position `start`. Returns empty string when `start` is out of bounds, arguments are invalid, or negative. Auto-truncates at end. |
| `toLower(value)`                    | `String`       | Converts to lowercase. Returns empty string for `null`.                                                                                                                     |
| `toUpper(value)`                    | `String`       | Converts to uppercase. Returns empty string for `null`.                                                                                                                     |
| `trim(value)`                       | `String`       | Trims leading and trailing whitespace. Returns empty string for `null`.                                                                                                     |
| `string(value)`                     | `String`       | Converts the value to a string. Returns empty string for `null`.                                                                                                            |

***

### Conversion Functions

| Function Signature | Return Type | Description                                                                                                                        |
| ------------------ | ----------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `bool(value)`      | `boolean`   | Returns a boolean value according to the built-in boolean conversion rules (see the type description at the top of this document). |

***

## Related Documentation

* [Task Parameters](task_param.md) — Using dynamic parameter values in condition expressions
* [Task Parameter Syntax Reference](task_param_reference.md) — Full syntax for time expressions and built-in parameters
* [Composite Task](composite_task.md) — Incorporating branch tasks into a DAG
* [Task Development and Scheduling](task-develop.md) — Development and scheduling for SQL tasks

^
