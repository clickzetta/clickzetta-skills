# Description

Used to return the job history of all ongoing and historical refreshes. Currently, only the most recent 10,000 records from the past 7 days will be displayed. The results can show how many incremental refreshes there are, whether it is an incremental refresh, etc.

# Syntax
```SQL
 SHOW DYNAMIC TABLE REFRESH HISTORY [where <expr>] [LIMIT num];
```
# Parameter Description

* `WHERE <expr>`: (Optional) Allows users to filter based on the fields displayed by the `SHOW JOBS` command. Users can use expressions to filter the results for more precise data retrieval.
* `LIMIT num`: (Optional) Limits the number of job records returned, ranging from 1-10000.

# Return Results

| Field              | Description                                                                 |
| ------------------ | --------------------------------------------------------------------------- |
| workspace\_name    | Workspace name                                                              |
| schema\_name       | Schema name                                                                 |
| name               | Dynamic table name                                                          |
| virtual\_cluster   | Computing cluster used                                                      |
| start\_time        | Refresh start time, timestamp type                                          |
| end\_time          | Refresh end time, timestamp type                                            |
| duration           | Refresh duration, interval type                                             |
| state              | Job status                                                                  |
| refresh\_trigger   | MANUAL (manually triggered by user, including studio scheduling) SYSTEM\_SCHEDULED (scheduled by lakehouse) |
| suspended\_reason   | Reserved field with no special meaning                                      |
| refresh\_mode      | NO\_DATA FULL INCREMENTAL                                                   |
| error\_message     | Information on refresh failure                                              |
| source\_tables     | Records the base table names used by the dynamic table                      |
| stats              | Information on incremental refresh counts                                   |
| completion\_target | Reserved field with no special meaning                                      |
| job\_id            | Job ID, clicking on the job ID allows viewing of the job profile            |

#  Example

* Filter the corresponding refresh history based on the dynamic table name
```SQL
 SHOW DYNAMIC TABLE REFRESH HISTORY  where name='dau';
```
* Filter based on time consumption, filtering out UI elements that take more than one second
```SQL
 SHOW DYNAMIC TABLE REFRESH HISTORY  where name='dau' and duration>interval 1 second;
```
* Filter based on computing cluster
```SQL
 SHOW DYNAMIC TABLE REFRESH HISTORY  where name='dau' and duration>interval 1 second and virtual_cluster='DEFAULT';
```
* Filter by start time
```SQL
 SHOW DYNAMIC TABLE REFRESH HISTORY  where name='dau' and duration>interval 1 second and virtual_cluster='DEFAULT'  and start_time>timestamp'2024-06-12 12:47:07.881';
```

^
