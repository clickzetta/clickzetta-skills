# Using UDF in Dynamic Tables



Dynamic tables extend support for user-defined functions. You can use custom functions created with External Function (including UDF, UDAF, and UDTF) in the SELECT clause of a dynamic table DDL. The system will automatically apply incremental computation optimization during refresh.

For information on how to develop custom functions using External Function, refer to the *Custom Function Development Guide*.

## Usage Examples

### Using UDF in a Dynamic Table

During the preview phase, dynamic tables support UDF incremental computation. When creating and refreshing a dynamic table, set the following parameters:

```SQL
-- When using a custom UDF, add the following flags
set cz.sql.mv.support.udf=true;
set cz.optimizer.incremental.enable=true;
```

Example:

```SQL
 /*  1. Incremental computation support for dynamic tables with UDF  */
-- step01: Test running UDF
SELECT public.upper_udf('clickzetta')  as upper_string;

upper_string 
------------ 
CLICKZETTA   


--step02: Create a dynamic table using UDF
-- When using a custom UDF, add the following flags and execute them together during creation
set cz.sql.mv.support.udf=true;
set cz.optimizer.incremental.enable=true;
create or replace dynamic table public.dt_udf_on_demand
refresh
    vcluster default
as
SELECT public.upper_udf(event_type) as event_type
FROM ecommerce_events_multicategorystore_live ;

--Execute dynamic table refresh, run together with the parameter settings above
set cz.sql.mv.support.udf=true;
set cz.optimizer.incremental.enable=true;
REFRESH DYNAMIC TABLE public.dt_udf_on_demand;

--View refresh history: first run is a full refresh, second run is an incremental refresh
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE NAME='dt_udf_on_demand';

workspace_name schema_name name             virtual_cluster start_time          end_time            duration             state   refresh_trigger suspended_reason refresh_mode error_message source_tables                                                                                     stats                                      completion_target job_id                        
-------------- ----------- ---------------- --------------- ------------------- ------------------- -------------------- ------- --------------- ---------------- ------------ ------------- ------------------------------------------------------------------------------------------------- ------------------------------------------ ----------------- ----------------------------- 
ql_ws          public      dt_udf_on_demand DEFAULT         2024-06-08 14:38:56 2024-06-08 14:38:56 0 00:00:00.613000000 SUCCEED MANUAL          (null)           INCREMENTAL  (null)        [{"schema":"public","table_name":"ecommerce_events_multicategorystore_live","workspace":"ql_ws"}] {"rows_deleted":"0","rows_inserted":"50"}  (null)            202406080638559284o0jorqp9tvp 
ql_ws          public      dt_udf_on_demand DEFAULT         2024-06-08 14:37:00 2024-06-08 14:37:00 0 00:00:00.529000000 SUCCEED MANUAL          (null)           FULL         (null)        [{"schema":"public","table_name":"ecommerce_events_multicategorystore_live","workspace":"ql_ws"}] {"rows_deleted":"0","rows_inserted":"100"} (null)            202406080637000414o0jorqp9uf0 
```

### Using UDAF in a Dynamic Table

During the preview phase, dynamic tables support UDAF incremental computation. When creating and refreshing a dynamic table, set the following parameters:

```SQL
-- When using a custom UDAF, add the following flags
set cz.sql.mv.support.udf=true;
set cz.optimizer.incremental.enable=true;
set cz.optimizer.mv.auto.unique.key.enabled=true;
set cz.common.table.enable.hidden.row.key=true;
set cz.optimizer.incremental.extra.recompute.agg.func=<your_udaf_function_name>; --Replace with the name of your UDAF
```

Example:

```SQL
-- step01: Test running UDAF
SELECT public.udaf_sum(c1)  as sum from values (1),(2),(3);
sum 
--- 
6   

--step02: Create a dynamic table using UDAF
-- When using a custom UDAF, add the following flags
set cz.sql.mv.support.udf=true;
set cz.optimizer.incremental.enable=true;
set cz.optimizer.mv.auto.unique.key.enabled=true;
set cz.common.table.enable.hidden.row.key=true;
set cz.optimizer.incremental.extra.recompute.agg.func=udaf_sum; --  Change to your own UDAF name
CREATE OR REPLACE DYNAMIC TABLE public.DT_UDAF_ON_DEMAND
refresh
    vcluster default
AS
SELECT EVENT_TYPE , public.UDAF_SUM(CAST(PRICE AS INT)) AS REVENUE
FROM ECOMMERCE_EVENTS_MULTICATEGORYSTORE_LIVE 
GROUP BY EVENT_TYPE;

--step03: Execute dynamic table refresh, run together with the parameter settings above
set cz.sql.mv.support.udf=true;
set cz.optimizer.incremental.enable=true;
set cz.optimizer.mv.auto.unique.key.enabled=true;
set cz.common.table.enable.hidden.row.key=true;
set cz.optimizer.incremental.extra.recompute.agg.func=udaf_sum; --  Change to your own UDAF name
REFRESH DYNAMIC TABLE public.DT_UDAF_ON_DEMAND;

--step04: View refresh history
SHOW DYNAMIC TABLE REFRESH HISTORY WHERE NAME='dt_udaf_on_demand';
```

### Using UDTF in a Dynamic Table

During the preview phase, dynamic tables support UDTF incremental computation. When creating and refreshing a dynamic table, set the following parameters:

```SQL
-- When using a custom UDTF, add the following flags
set cz.sql.remote.udf.trace.enabled=true;
set cz.sql.mv.support.udf=true;
set cz.common.table.enable.hidden.row.key=false;
set cz.optimizer.incremental.condense.by.version.enable=false;
set cz.optimizer.mv.auto.unique.key.enabled=false;
set cz.optimizer.incremental.extra.recompute.table.func=<your_udtf_function_name>; --Replace with the name of your UDTF
```

Example:

```SQL
-- step01: Test running UDTF
SELECT public.myexplode(array('a','b','c')) as col_name;
col_name 
----- 
a     
b     
c     

--step02: Create a dynamic table using UDTF
-- When using a custom UDTF, add the following flags and execute them together
set cz.sql.remote.udf.trace.enabled=true;
set cz.sql.mv.support.udf=true;
set cz.common.table.enable.hidden.row.key=false;
set cz.optimizer.incremental.condense.by.version.enable=false;
set cz.optimizer.mv.auto.unique.key.enabled=false;
set cz.optimizer.incremental.extra.recompute.table.func=myexplode; --  Change to your own UDTF name
CREATE OR REPLACE DYNAMIC TABLE public.DT_UDTF_ON_DEMAND
refresh
    vcluster default
AS
SELECT public.MYEXPLODE(ARRAY(PRICE::STRING,'1000')) AS PRICE
FROM ECOMMERCE_EVENTS_MULTICATEGORYSTORE_LIVE ;

----step03: Refresh the dynamic table with UDTF, execute together with the parameter settings above
set cz.sql.remote.udf.trace.enabled=true;
set cz.sql.mv.support.udf=true;
set cz.common.table.enable.hidden.row.key=false;
set cz.optimizer.incremental.condense.by.version.enable=false;
set cz.optimizer.mv.auto.unique.key.enabled=false;
set cz.optimizer.incremental.extra.recompute.table.func=myexplode; 
REFRESH DYNAMIC TABLE public.DT_UDF_ON_DEMAND;

--step04: View refresh history
show dynamic table refresh history where name='dt_udtf_on_demand';
```

# Constraints and Limitations

During the feature preview, setting a scheduled refresh in the dynamic table DDL while using UDF (or related custom functions) is not supported. If you need this capability, contact the platform technical team.
