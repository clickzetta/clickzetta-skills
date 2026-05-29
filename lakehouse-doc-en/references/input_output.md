Context parameters, in parameter configuration, refer to configuring two special parameters — input parameters and output parameters — to enable automatic data transfer between upstream and downstream nodes.

## Usage Restrictions:

* Output parameters: Only SQL, Python, and Shell task nodes support configuring output parameters.
* Transfer level: Only single-level transfer is supported, i.e., only upstream nodes passing to their immediate downstream dependents.
* Transfer size: A maximum of 2MB of data transfer is supported.

## Usage Guide

* **Upstream Node (Provider)**: Responsible for generating a value and using it as an output parameter.

  * **Configure and Assign Output Parameter**: The system captures the query result of the last line of the node's code (e.g., `SELECT * from table_A;`) and **assigns** it to a built-in output parameter **`outputs`**, then passes the value of this parameter to downstream nodes. The parameter value depends on the code execution result.

* **Downstream Node (Consumer)**: Receives and uses the value provided by the upstream node.

  * **Establish Scheduling Dependency**: Configure a scheduling dependency on the upstream node.
  * **Configure Input Parameter**: In the downstream node's **parameter configuration** area, add an input parameter and set its value source to the upstream node's output parameter.
  * **Reference in Code**: In the downstream node's code, reference the received value using the `${input_parameter_name}` format. For example, if the upstream node passes the value `table_A`, the downstream code `SELECT '${input_parameter_name}';` will print the upstream output result at runtime.

## Configuration Instructions

### Configure Output Parameters
![](/.topwrite/assets/image_1775099138460.png)

If you wish to pass the current node's result to downstream, follow these steps:

1. Click the node, then Parameters > Output Parameters
2. Click "New", and the system will automatically fill in the built-in parameter $[output].

> If the task is of Python/Shell type, the output result defaults to the output of the last line, with result data split by delimiter.
>
> If the task is of SQL type, the output result defaults to the last data result. If there are multiple rows, the data will be converted into a two-dimensional array for output.

### Configure Input Parameters

#### Configure Input Parameters

Open the editing page of the downstream node, click Parameters > Input Parameters, and click New.

Configure the input parameter.

* Parameter Name: The parameter name referenced in the script.

* Parameter Value: Select one of the upstream node's output parameters as the value source for this parameter.

  * Upstream Dependency: From the currently configured upstream tasks, select those that have output parameters as the input parameter value source.
  * Others: To add a task with output parameters from elsewhere, use "Others" to select it. Once selected, the dependency on that task will be automatically configured.

![](/.topwrite/assets/image_1775099157450.png)

#### Reference Parameters

In the downstream node's code, reference the parameter using the `${input_parameter_name}` format.

Below is an example of referencing the input parameter `param` in an SQL node:

```Plain
select "${param}"
```

If the upstream node passes the assigned result to downstream, the parameter value is typically a two-dimensional array or a comma-separated one-dimensional array. Use the following methods to retrieve values within the array:

* If the upstream is an SQL node (two-dimensional array):

  * Row: `${param[i]}`.
  * Cell: `${param[i][j]}`.
  * If the upstream is Python/Shell (one-dimensional array): Row: `${param[i]}`.

> *Indexes start from 0.*
