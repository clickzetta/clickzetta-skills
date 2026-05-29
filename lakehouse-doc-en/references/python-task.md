# Python Task

> [Preview Release] This feature is currently in the invite-only preview release phase. To use it, please contact our technical support team for assistance.

In many data analysis and processing scenarios, especially in BI+AI analysis scenarios, combining Python and SQL can greatly improve the efficiency of data analysis and processing. In Singdata Lakehouse, we provide a Python script task type for running Python code.

## Operations Guide

1. **Create a Task**: In the data development interface, click the "Create Task" button to enter the task configuration page.

2. **Select Task Type**: On the task configuration page, select "Python Script" as the task type.

3. **Write Python Code**: In the Python code editor area, write the Python code you need to execute.

4. **Run Task**: Click the "Run" button to execute your Python script. The execution results will be displayed in the results area below.

5. **Task Scheduling**: Like SQL tasks, Python tasks can also be directly configured with periodic scheduling and operations management, and can be orchestrated into workflows with other tasks by setting task dependencies.

## Practical Guidance

For practical guidance on installing dependency packages, customizing environments, importing data, and other operations in Python tasks, please refer to the following documents:

* [Python Task Package Installation and Import Guide](python_package_install_import_guide.md)
* [Python Task Usage Practices](practice_python_task.md)
* [Python Task Development: Periodically Sync gharchive Website Data Files to Cloud Object Storage](python-sample-put-gharchive2oss.md)
* [Python Task Development: Fetch GitHub Events in Real Time and Bulkload into Lakehouse Table](python-sample-put-github-rt-events.md)

^
