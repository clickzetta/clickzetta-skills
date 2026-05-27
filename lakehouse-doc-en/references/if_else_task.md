# Branch Task

The Branch task is used to implement conditional routing in workflow scheduling. It dynamically determines which downstream path to trigger based on the output results of upstream tasks. Similar to the For-each loop task, the Branch task needs to be used in conjunction with an upstream task that has output parameters. By evaluating expressions on the output dataset, results are mapped to different downstream paths.

This document introduces the composition and application logic of the Branch task.

***

## How It Works
![](/.topwrite/assets/image_1778741703249.png)

1. **Upstream Task Output**: The upstream task (SQL, Python, Shell, etc.) passes a dataset to the downstream branch node via the `$[output]` parameter.

2. **Branch Task**: Receives the upstream dataset, performs a series of expression evaluations on it, and determines which downstream path to trigger based on the evaluation results.

   * **Input Parameters**: Configure which upstream task to get the output set from, in the format `${parameter_name}={output}:upstream_task_name`.
   * **Expressions**: Perform logical judgments using built-in functions. When the expression result is `true`, the downstream path corresponding to that branch is triggered.
   * **Branch Output Name**: Each branch condition corresponds to an output name, used to establish dependency relationships with downstream tasks.

3. **Downstream Task Reference**: When a downstream task configures its dependency, it must specify which output name of the upstream branch node to associate with.

***

## Steps

### Creating a Branch Task

In the task list or composite task/task group, click **New Task** and select the task type as **Branch Task**.

The Branch task has a visual configuration page. Each branch requires the following information:

**Branch Condition**

Configure the judgment expression for the current branch. For supported functions, see: Supported Expression Functions.
* If the expression evaluates to `true` at runtime, the corresponding branch condition is met.
* If the expression parsing fails at runtime, the entire branch node status will be set to failed.
* Branch conditions support using global variables and parameters defined in the node context. For example, `${input}` can be a node input parameter defined on the branch node.

**Branch Output Name**

The output identifier after the current branch condition is evaluated, used to establish dependencies with downstream tasks.

* When the branch condition is met: The downstream node associated with the corresponding output name is triggered.
* When the branch condition is not met: The downstream node associated with the corresponding output name is not executed, and its status is set to **Ended because branch condition was not met**.

Output name format requirements: Supports Chinese, English, and underscores `_`, up to 128 characters. **Duplicate output names are not allowed within the same branch task.**

**Branch Description**

Optional. Used to record a brief description of the branch.

### Configuring Downstream Tasks for Branches

After a branch condition is triggered, the downstream nodes expected to run need to be configured accordingly.
Select the downstream node you want to run, click to enter, and configure **Scheduling Configuration**: In the scheduling dependency, select the specific output name within the branch task.

Example:
For instance, a branch node has two downstream associated nodes named `aaa` and `bbb`. When branch condition is 1, the `aaa` node logic runs. When branch condition is 2, the `bbb` node logic runs. When configuring the branch node, the output associations can be set arbitrarily. For example, branch 1 associates with node output `1234`, branch 2 associates with node output `2324` — both will serve as output names of this branch node. The downstream `aaa` node needs to depend on the branch node's output name `1234`, and the `bbb` node needs to depend on the branch node's output name `2324`.

## Supported Expression Functions

> **Note**
>
> * Function names are **case-insensitive**.
> * `and`, `or`, and `concat` support variable arguments (1 or more).
> * `union` and `intersection` require at least 2 arguments.
> * `guid` accepts no arguments.
> * Other functions have a fixed number of arguments. Incorrect argument passing will cause an expression parsing error, and the branch status will be set to failed.

**Boolean conversion rules**: `null`, empty string, blank string, `false`, and the number `0` are treated as `false`; `true` and non-zero numbers are treated as `true`; other non-numeric strings are **not** treated as `true`.

**Currently not supported**: Mathematical operations, date/time, JSON Path / object property access, regular matching, null coalescing, and similar functions.

***

### Logical Functions

| Function Signature                | Return Type | Description                                                                                              |
| --------------------------------- | ----------- | -------------------------------------------------------------------------------------------------------- |
| `and(arg1, arg2, ...)`            | `boolean`   | Returns `true` when all arguments converted to boolean are `true`. Supports 1 or more arguments. Example: `and(true, bool(1), equals('a', 'a'))` |
| `or(arg1, arg2, ...)`             | `boolean`   | Returns `true` when any argument converted to boolean is `true`. Supports 1 or more arguments.            |
| `not(arg)`                        | `boolean`   | Negates the boolean value of the argument.                                                               |

***

### Comparison Functions

When both sides can be converted to numbers, comparison is numeric; otherwise, lexicographic string comparison is used.

| Function Signature                | Return Type | Description                             |
| --------------------------------- | ----------- | --------------------------------------- |
| `equals(left, right)`             | `boolean`   | Returns `true` if the two normalized values are equal. |
| `greater(left, right)`            | `boolean`   | `left > right`                          |
| `greaterOrEquals(left, right)`    | `boolean`   | `left >= right`                         |
| `less(left, right)`               | `boolean`   | `left < right`                          |
| `lessOrEquals(left, right)`       | `boolean`   | `left <= right`                         |

***

### Collection Functions

Collection functions apply to arrays (`List` / `Collection` / `JSONArray`), strings, and some also support dictionaries (`JSONObject` / `Map`).

| Function Signature                 | Return Type       | Description                                                                                      |
| ---------------------------------- | ----------------- | ------------------------------------------------------------------------------------------------ |
| `contains(container, expected)`    | `boolean`         | String: checks if substring is contained; Collection: compares items by normalized value; JSONObject / Map: checks if the specified key is contained. |
| `empty(value)`                     | `boolean`         | Returns `true` for `null`, empty string, empty collection, or empty JSONObject / Map.            |
| `first(value)`                     | First element     | String: returns the first character; List / Collection: returns the first element; returns `null` when empty. |
| `last(value)`                      | Last element      | String: returns the last character; List / Collection: returns the last element; returns `null` when empty. |
| `length(value)`                    | `integer`         | String: returns character count; Collection / Map: returns element count; returns `0` for `null`. |
| `skip(value, count)`               | Same as input type | Skips the first `count` characters or elements; returns the original value directly when `count < 0`, non-integer, or `value` is `null`. |
| `take(value, count)`               | Same as input type | Keeps the first `count` characters or elements; returns the original value directly when `count < 0`, non-integer, or `value` is `null`. |
| `union(list1, list2, ...)`         | `List`            | Merges multiple lists with deduplication, preserving the order of first appearance; all arguments must be convertible to lists, otherwise returns `null`. |
| `intersection(list1, list2, ...)`  | `List`            | Returns the intersection of multiple lists, with order based on the first list; all arguments must be convertible to lists, otherwise returns `null`. |
| `join(list, separator)`            | `String`          | Joins all elements of the list with the separator; the first argument must be convertible to a list, otherwise returns `null`. |

***

### String Functions

| Function Signature                       | Return Type    | Description                                                                                                    |
| ---------------------------------------- | -------------- | -------------------------------------------------------------------------------------------------------------- |
| `concat(arg1, arg2, ...)`                | `String`       | Concatenates all arguments in order; `null` arguments are ignored. Supports 1 or more arguments.               |
| `guid()`                                 | `String`       | Generates a random UUID string. Accepts no arguments.                                                          |
| `indexOf(text, search)`                  | `integer`      | Returns the position of the first occurrence of the substring; returns `-1` if not found.                      |
| `lastIndexOf(text, search)`              | `integer`      | Returns the position of the last occurrence of the substring; returns `-1` if not found.                       |
| `replace(text, oldValue, newValue)`      | `String`       | Replaces all matching substrings; returns empty string if `text` is `null`; treats `oldValue` or `newValue` as empty string when `null`. |
| `split(text, separator)`                 | `List<String>` | Splits the string by the separator; splits by single character when separator is empty; returns empty list if `text` is `null`. |
| `startsWith(text, prefix)`               | `boolean`      | Checks if the string starts with the specified prefix.                                                         |
| `endsWith(text, suffix)`                 | `boolean`      | Checks if the string ends with the specified suffix.                                                           |
| `substring(text, start, length)`         | `String`       | Extracts `length` characters starting from position `start`; returns empty string when `start` is out of bounds, arguments are invalid, or negative; auto-truncates when end exceeds bounds. |
| `toLower(value)`                         | `String`       | Converts to lowercase; returns empty string for `null`.                                                        |
| `toUpper(value)`                         | `String`       | Converts to uppercase; returns empty string for `null`.                                                        |
| `trim(value)`                            | `String`       | Trims leading and trailing whitespace; returns empty string for `null`.                                        |
| `string(value)`                          | `String`       | Converts the value to a string; returns empty string for `null`.                                               |

***

### Conversion Functions

| Function Signature | Return Type | Description                                                   |
| ------------------ | ----------- | ------------------------------------------------------------- |
| `bool(value)`      | `boolean`   | Returns a boolean value according to the built-in boolean conversion rules (see type description at the top of the document). |
