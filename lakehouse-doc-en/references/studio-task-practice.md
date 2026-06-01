# Studio Task Development and Operations in Practice

Studio tasks are the scheduling execution units of Singdata Lakehouse, supporting multiple types including SQL, Python, and Shell. This series of documents covers practical task development scenarios, with each article containing complete runnable code and verified output.

## Series Articles

- [Studio Python Task Development Guide (ZettaPark)](studio-python-task-zettapark.md) — Read and write Lakehouse data via the ZettaPark DataFrame API, using RFM customer segmentation as a complete development walkthrough
- [Studio Python Task Development Guide (Python Connector)](studio-python-task-connector.md) — Obtain a PEP 249 cursor via `engine.raw_connection()`, use `executemany` for bulk writes and cursor queries, using user behavior funnel analysis as an example
- [Studio Shell Task Development Guide](studio-shell-task.md) — Run Bash scripts in a server-side Linux environment, call HTTP APIs to pull data and write to Lakehouse, including runtime environment details and common patterns
- [Studio JDBC Task Development Guide](studio-jdbc-task.md) — Connect to external databases (MySQL, etc.) via JDBC to execute SQL, covering two scenarios: pre-sync exploration and data source issue investigation

## Practice Scenarios

- [Incremental Sync from External Data Sources (Shell + Python)](studio-incremental-sync-practice.md) — Shell task pulls external API data and writes to the raw layer; Python task cleans and standardizes data and writes to the clean layer; the two tasks are chained via dependency

## Related Documentation

- [Python Tasks](python-task.md)
- [Using Data Sources in Python/Shell Tasks](python_shell_datasource.md)
- [Studio Task Development and Operations](cz-cli-studio-tasks.md)
