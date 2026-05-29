# Reasons for Recommendation

The recommended columns can be used as the sort key for the table

The selected columns frequently appear in filter statements. Setting these columns as the sort key for the table can speed up query execution.

### How to Enable

* You can set the property on the workspace, which will analyze all tables under the workspace

```Plain
ALTER WORKSPACE workspace_name SET properties (auto_index='day[,150,5,100]');

For example:
ALTER WORKSPACE quick_start SET properties (auto_index='day'); 
ALTER WORKSPACE quick_start SET properties (auto_index='day,150,5,100');

--The first parameter is required, specifying whether to collect daily or monthly. Monthly collection is done on the 1st of each month at 6 PM.
--The second parameter specifies the duration of jobs to be used (in minutes), default is 150.
--The third parameter specifies how many times a job needs to be repeated to be used, default is 5.
--The fourth parameter specifies the maximum number of jobs used per column, default is 100.
```

* Automatic Collection

Automatically collects the top 10 tables used in filter statements for each schema

### How to Query

```Plain
SELECT * FROM information_schema.sortkey_candidates;

--The returned results are as follows:
instance_id,workspace_id,workspace_name,schema_id,schema_name,table_id,table_name,col,statement,ratio,insert_time,p_date
11111111111,855911111111,aaaaaaaaaaa,23671111111111,ddddddddd,84465111,aaaaaaaaaaa.ddddddddd.member,brandid,alter table aaaaaaaaaaa.ddddddddd.member set properties("hint.sort.columns"="brandid"), 2.21%,05:49.1,2024/11/7
11111111111,855911111111,aaaaaaaaaaa,23671111111111,ddddddddd,84465111,aaaaaaaaaa.ddddddddd.member,birthday,alter table aaaaaaaaaa.ddddddddd.member set properties("hint.sort.columns"="birthday"),0.01%,05:49.1,2024/11/7
11111111111,855911111111,aaaaaaaaaaa,23671111111111,ddddddddd,84465111,aaaaaaaaaaa.ddddddddd.member,id,alter table aaaaaaaaaaa.ddddddddd.member set properties("hint.sort.columns"="id"),0.01%,05:49.1,2024/11/7

--It can be seen that for the aaaaaaaaaaa.ddddddddd.member table, the improvement effect of brandid is the highest, so set it as the sortkey alter table aaaaaaaaaaa.ddddddddd.member set properties("hint.sort.columns"="brandid"), this setting will
```

The included columns are `instance_id, workspace_id, workspace_name, schema_id, schema_name, table_id, table_name, col, statement, ratio, insert_time, p_date`. Among them:

* `p_date` is the partition column, formatted as yyyy-mm-dd.
* `insert_time` is the time when the collection results are inserted.
* `col` is the recommended column, currently a single column.
* `statement` is the SQL statement on how to set the recommended column as the sorting column.
* `ratio` is the estimated improvement effect, in percentage.

### Usage Recommendations

It is recommended to use the [analyze statement](analyze-table.md) to collect stats for the table columns, which will improve the accuracy of the recommendations.
