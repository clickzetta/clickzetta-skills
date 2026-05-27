# Python Task

【**Preview Release】This feature is currently in an invitation-only preview phase. If access is required, please contact our technical support team for assistance**.&#x20;

For many data analysis and processing scenarios, especially for BI + AI analysis scenarios, the combination of Python and SQL can greatly improve the efficiency of data analysis and processing. In Singdata Lakehouse, Python code can be run by providing a task type for Python scripts.

## User Guide

1. **Create a New Task**: In the data development interface, click the new task button to enter the task configuration page.

2. **Select Task Type**: On the task configuration page, select "Python Script" as the task type.

3. **Write Python Code**: In the Python code editing area, write the Python statements you need to execute.

4. **Run Task**: Click the "Run" button to execute the SQL script you wrote. The execution results will be displayed in the result display area below.

5. **Task Scheduling**: Like SQL tasks, Python tasks can be scheduled and maintained periodically, and workflow orchestration with other tasks can be achieved by setting task dependencies.

## Practical Guide

For practical usage on how to install dependency packages, customize the environment, import data, etc., in Python tasks, you can refer to the following documents:

* [Practical Use of Python Tasks](practice_python_task.md)
* [Python Task Development: Periodically Sync Data Files from gharchive Website to Cloud Object Storage](PythonSample_put_gharchive2oss.md)
* [Python Task Development: Real-time Fetch GitHub Events and Bulk Load into Lakehouse Table](PythonSample_put_github_rt_events.md)

^
