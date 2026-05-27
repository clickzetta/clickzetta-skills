# Using Explain to View Dynamic Table Refresh Mode

Use the explain command to check if incremental refresh (preview) is possible. You need to enable the switch by setting `set cz.optimizer.explain.can.incrementalize=true;` and execute it together in data development.

**Syntax**
```Plain
set cz.optimizer.explain.can.incrementalize=true;
EXPLAIN REFRESH DYNAMIC TABLE dtname;
```
Usage Instructions

* The explain command is usually used to view the SQL execution plan. When refreshing a dynamic table, adding explain can be used to view the execution plan of the dynamic table. At the same time, Lakehouse will output whether it is an incremental plan field. CanBeIncrementalized, if it is Yes, it means that the incremental plan is executed. If the output is No, it means it is not an incremental plan No because ...

**Specific Case**
```SQL
set cz.optimizer.explain.can.incrementalize=true;
explain refresh dynamic table event_gettime;
```
![](.topwrite/assets/image_1720597444254.png)

# Use the Show Command to View Dynamic Table Refresh Mode
Check by using show dynamic table refresh history. The refresh_mode field in the output can be used to see if it is an incremental refresh, and the stats field records how many rows were incrementally refreshed.

 **Syntax**
```SQL
 SHOW DYNAMIC TABLE REFRESH HISTORY [where <expr>] [LIMIT num];
```
## Parameter Description

* `WHERE <expr>`: (Optional) Allows users to filter based on the fields displayed by the `SHOW JOBS` command. Users can filter the results through expressions to more accurately find the required data.
* `LIMIT num`: (Optional) Limits the number of job records returned, ranging from 1-10000.

**Return Results**

|        Field        |                            Description                                               |
| ------------------ | ------------------------------------------------------------------------- |
| workspace\_name    | Workspace name                                                                    |
| schema\_name       | Schema name                                                                  |
| name               | Dynamic table name                                                                     |
| virtual\_cluster   | Computing cluster used                                                                   |
| start\_time        | Refresh start time, timestamp type                                                        |
| end\_time          | Refresh end time, timestamp type                                                        |
| duration           | Refresh duration, interval type                                                           |
| state              | Job status                                                                      |
| refresh\_trigger   | MANUAL (manually triggered by user calling refresh, including studio scheduled refresh) SYSTEM\_SCHEDULED (scheduled refresh by lakehouse) |
| suspended\_reson   | Reserved field with no special meaning                                                                 |
| refresh\_mode      | NO\_DATA FULL INCREMENTAL                                                 |
| error\_message     | Information on refresh failure                                                                   |
| source\_tables     | Records the base table names used by the dynamic table                                                  |
| stats              | Information such as the number of incremental refreshes                                                                 |
| completion\_target | Reserved field with no special meaning                                                                 |
| job\_id            | Job ID, by clicking the job ID you can see the job profile                                              |