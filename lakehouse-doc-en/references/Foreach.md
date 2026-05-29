The For-each task is primarily used for loop iteration scenarios and must be used in conjunction with an upstream task (SQL, Python, Shell) that has output parameters. By setting the upstream task with output parameters as the For-each task's upstream, and assigning its output results to the For-each task, the values from the upstream task are iterated through one cycle at a time.

This document introduces the composition and application logic of the For-each loop task.

## How It Works

![](/.topwrite/assets/image_1775099011814.png)

1. Special tasks that support output parameters: The For-each loop task must be bound to an upstream task that has output parameters. The system currently supports SQL, Python, and Shell task types for configuring **output parameters**.
2. LoopArray parameter: Configured on the For-each task, this is used to bind to upstream data. The upstream data results determine the number of loop iterations on the For-each task, as well as the specific values to be substituted within the For-each internal tasks.
3. Sub-task reference: If internal tasks of the For-each task need to reference upstream task values, they can obtain the values bound to the LoopArray from upstream via built-in parameters.

## Steps

**Prepare upstream data (configure a Python task)**

Create a new Python task and configure **output parameters** for it.

```Plain
print (1,'abc',2,'djg');
```

> This task node will output an array `[1,'abc',2,'djg']` to the downstream.

**Configure the For-each loop task**

1. Configure For-each input parameters

Click **Scheduling** -> **Loop Info** -> **Input Parameters**, and bind the LoopArray parameter. This parameter is mainly used to receive upstream parameter values and datasets.

> Number of iterations: 4. The upstream node splits the dataset result by comma and determines the number of iterations.
>
> Dataset: `[1,'abc',2,'djg']`

![](/.topwrite/assets/image_1775099035652.png)

The value of LoopArray is determined by binding to the output parameters of the upstream node. At the same time, selecting another task that has output parameters configured will automatically establish a dependency relationship between the two nodes.

2. Loop strategy
![](/.topwrite/assets/image_1775099046547.png)

* Sequential: Runs in order according to the number of iterations.
* Parallel: Allows concurrent execution of internal For-each loops, improving task execution efficiency. In parallel mode, if any individual loop body fails, you can configure the **On Loop Failure** handling strategy to determine whether subsequent loops should be set to failed immediately or continue executing.

3. Maximum number of iterations: Default is **128**, adjustable up to **1024**.

4. On Loop Failure: The execution strategy for subsequent loops when a loop body fails within a For-each instance.

* Stop all: When one loop body fails, all subsequent loops that have not yet run are set to failed by default. The entire For-each instance execution fails.
* Continue subsequent: When one loop body fails, subsequent unexecuted loop bodies are unaffected and continue normal scheduling until all loops finish executing.

5. Empty upstream output parameter: How the current For-each loop handles the case when the upstream output parameter is empty.

* Set to success: The current For-each loop is treated directly as a success state, without actual execution.
* Set to failed: The current For-each loop is treated directly as a failed state.

**Configure internal sub-tasks of the For-each task**

Inside the For-each task, create a new SQL node.

After entering `${aa}` in the script area, configure this custom parameter in **[Parameters]**. During actual execution, parameter value substitution will take place.
![](/.topwrite/assets/image_1775099055895.png)

## Temporary Run

For-each loops support entering LoopArray values for testing and verification during temporary runs. Format support: one-dimensional arrays using commas `,` as separators; two-dimensional arrays using `[[],[\]]` format. For example: `[["1","abc"],\["12","abc2"]]`

## For-each Loop Built-in Parameters

> The upstream output dataset is `[1,2,3,4]`

|                         |                                                |                                                                                  |
| ----------------------- | ---------------------------------------------- | -------------------------------------------------------------------------------- |
| Parameter Name          | Meaning                                        | Example                                                                          |
| dag\_foreach\_current() | Gets the data item currently being processed   | 4 iterations in total. * 1st output: 1
* 2nd output: 2
* 3rd output: 3
* 4th output: 4 |
| dag\_loopArray()        | Gets the complete **result set** from the upstream assignment task | 4 iterations in total. * 1st output: 1,2,3,4
* 2nd output: 1,2,3,4
* 3rd output: 1,2,3,4
* 4th output: 1,2,3,4 |
| dag\_loopTimes()        | Gets the current **iteration number**, starting from **1** | 4 iterations in total. * 1st output: 1
* 2nd output: 2
* 3rd output: 3
* 4th output: 4 |
| dag\_offset()           | Gets the current loop **offset**, starting from **0**. | 4 iterations in total. * 1st output: 0
* 2nd output: 1
* 3rd output: 2
* 4th output: 3 |
