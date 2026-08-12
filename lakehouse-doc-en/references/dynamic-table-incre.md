
# Viewing the Dynamic Table Refresh Mode with the SHOW Command
Use `SHOW DYNAMIC TABLE REFRESH HISTORY` to check the refresh mode. In the output, the `refresh_mode` field indicates whether incremental refresh was used, and the `stats` field records the row counts for incremental refreshes.


**Syntax**

```SQL
 SHOW DYNAMIC TABLE REFRESH HISTORY [where <expr>] [LIMIT num];
```

**Parameters**

* `WHERE <expr>`: (Optional) Filters results based on the fields displayed by the `SHOW JOBS` command. You can use an expression to narrow down the results and find the data you need more precisely.
* `LIMIT num`: (Optional) Limits the number of job records returned. Valid range: 1–10000.

**Return Fields**



|            Field       |                            Description                                        |
| ------------------ | ------------------------------------------------------------------------- |
| workspace\_name    | Workspace name                                                            |
| schema\_name       | Schema name                                                               |
| name               | Dynamic table name                                                        |
| virtual\_cluster   | Compute cluster used                                                      |
| start\_time        | Refresh start time, timestamp type                                        |
| end\_time          | Refresh end time, timestamp type                                          |
| duration           | Refresh duration, interval type                                           |
| state              | Job status                                                                |
| refresh\_trigger   | MANUAL (triggered manually by the user via a refresh call, including Studio scheduled refreshes) or SYSTEM\_SCHEDULED (scheduled by Lakehouse) |
| suspended\_reason   | Reserved field, no special meaning                                        |
| refresh\_mode      | NO\_DATA, FULL, INCREMENTAL                                               |
| error\_message     | Error message if the refresh failed                                       |
| source\_tables     | Names of the base tables used by the dynamic table                        |
| stats              | Incremental refresh row counts and related information                    |
| completion\_target | Reserved field, no special meaning                                        |
| job\_id            | Job ID; click the job ID to view the job profile                          |
