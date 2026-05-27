# Notes

* Please use dbt-core 1.5.11, dbt-clickzetta 0.2.32 and above versions

# Preparation

1. Install DBT and ClickZetta Lakehouse plugin
```PowerShell
pip install dbt-core
```
Note: If you encounter compatibility issues with the latest version, please use dbt-core version 1.5.11.

2. Install the dbt-clickzetta plugin (using version v0.2.32 which supports DYNAMIC TABLE/MV):
```PowerShell
pip install dbt-clickzetta
```
3. Initialize DBT Project
```PowerShell
$ dbt init cz_dbt_project
01:35:39  Running with dbt=1.5.11
Which database would you like to use?
[1] clickzetta

(Don't see the one you want? https://docs.getdbt.com/docs/available-adapters)

Enter a number: 1
base_url (https://singdata.com): uat-api.sindata.com
workspace (dev workspace): ql_ws
instance_name (dev instance name): jnsxwfyr
vc_name (vc name): default
user_name (user name): <user_name>
schema (default schema): dbt_dev
password (password): <your_passwd>
01:37:13  Profile cz_dbt_project written to /Users/username/.dbt/profiles.yml using target's profile_template.yml and your supplied values. Run 'dbt debug' to validate the connection.
01:37:13  
Your new dbt project "cz_dbt_project" was created!

$ cd cz_dbt_project
```
4. Configure ClickZetta dbt project profiles

Open and edit the `~/.dbt/profiles.yml` file, and add the production environment configuration. Refer to the following content:
```PowerShell
cz_dbt_project:
  target: dev
  outputs:
    prod:
      type: clickzetta
      service: api.singdata.com
      instance: <your_instance_name>
      username: <user_name>
      password: <passwd>
      workspace: <your_workspace_name>
      schema: dbt_prod
      vcluster: default
    dev:
      type: clickzetta
      service: api.singdata.com
      instance: <your_instance_name>
      username: <user_name>
      password: <passwd>
      workspace: <your_workspace_name>
      schema: dbt_dev
      vcluster: default
```
```markdown
5. Verify Configuration
```
```PowerShell
$ dbt debug

02:22:03    Connection test: [OK connection ok]

INFO:stdout_log:02:22:03    Connection test: [OK connection ok]

INFO:file_log:10:22:03.153933 [info ] [MainThread]:   Connection test: [OK connection ok]

02:22:03  All checks passed!
```
6. Test Run

By running dbt run, the two test models built into the dbt project will be constructed in the target dev environment:

* model.cz\_dbt\_project.my\_first\_dbt\_model
* model.cz\_dbt\_project.my\_second\_dbt\_model

```PowerShell
$ dbt run
```
Check whether the execution log shows success and verify that data objects my_first_dbt_model and my_second_dbt_model are successfully created in the target environment (e.g., dbt_dev schema).

# Create Incremental Processing Task Based on Table Stream

## Scenario Description

First, define the externally written table as a Source Table and create a Table Stream object for the Source Table to obtain incremental change data;

Second, create an incremental model using Table Stream in DBT ("materialized='incremental' );

Finally, run the model multiple times to observe the incremental processing effect.

![](.topwrite/assets/image_1722603029545.png)

## Prepare Source Table

Create a raw table and continuously import data through a data integration tool:
```SQL
CREATE TABLE public.ecommerce_events_multicategorystore_live(
  `event_time` timestamp,
  `event_type` string,
  `product_id` string,
  `category_id` string,
  `category_code` string,
  `brand` string,
  `price` decimal(10,2),
  `user_id` string,
  `user_session` string)
TBLPROPERTIES(
  'change_tracking'='true');
```
Note: You need to add the 'change_tracking'='true' setting in the table properties to enable incremental data capture capability.

Create a Table Stream object for the original table to track changes in the original table:
```SQL
-- Create stream on source table
CREATE TABLE STREAM public.stream_ecommerce_events 
on table ecommerce_events_multicategorystore_live
with PROPERTIES ('TABLE_STREAM_MODE' = 'APPEND_ONLY')
```
At the same time, create a sources.yml file under the models directory of cz_dbt_project to declare the two source tables that have been created:

![](.topwrite/assets/image_1722603115937.png)

## Develop Model

Create a dbt model named events\_enriched.sql and declare it as an incremental model through configuration:
```SQL
{{
   config(
       materialized='incremental'
   )
}}

SELECT
  event_time,
  CAST(SUBSTRING(event_time,0,19) AS TIMESTAMP) AS event_timestamp, 
  SUBSTRING(event_time,12,2) AS event_hour, 
  SUBSTRING(event_time,15,2) AS event_minute, 
  SUBSTRING(event_time,18,2) AS event_second, 
  event_type,
  product_id, 
  category_id,
  category_code,
  brand,
  CAST(price AS DECIMAL(10,2)) AS price, 
  user_id, 
  user_session,
  CAST(SUBSTRING(event_time,0,19)AS date) AS event_date,
  CURRENT_TIMESTAMP() as loaded_at
FROM
{% if is_incremental() %}
{{source('quning', 'stream_ecommerce_events')}} 
{% else %}
{{source('quning', 'ecommerce_events_multicategorystore_live')}} 
{% endif %}
```
Note:

* When building the model using the dbt build command, the is\_incremental() condition is evaluated as False, and the model will be built using the full data from the original table ecommerce\_events\_multicategorystore\_live;
* When executing the model using dbt run, is\_incremental() will be recognized as True, and incremental processing will be performed;

If you want to build the model using only the incremental data from Table Stream (Table Stream by default only provides the change data after the Table Stream is created) during both the build and subsequent runs, you can define the model as follows:
```Go
{{
   config(
       materialized='incremental'
   )
}}

SELECT 
  `event_time` ,
  `event_type` ,
  `product_id` ,
  `category_id` ,
  `category_code` ,
  `brand` ,
  `price` ,
  `user_id` ,
  `user_session` ,
  CURRENT_TIMESTAMP() as load_time
  FROM 
{{source('public', 'stream_ecommerce_events')}}   
```
## Building Models

Create models in the target environment using the dbt build command:
```PowerShell
dbt build --model events_enriched
```
By observing the logs, the model is built with the following statement during model construction, and the initial processing and transformation of the original table is performed in full:
```SQL
/* {"app": "dbt", "dbt_version": "1.5.11", "profile_name": "cz_dbt_project", "target_name": "dev", "node_id": "model.cz_dbt_project.events_enriched"} */
create table dbt_dev.events_enriched
as
SELECT
  event_time,
  CAST(SUBSTRING(event_time,0,19) AS TIMESTAMP) AS event_timestamp, 
  SUBSTRING(event_time,12,2) AS event_hour, 
  SUBSTRING(event_time,15,2) AS event_minute, 
  SUBSTRING(event_time,18,2) AS event_second, 
  event_type,
  product_id, 
  category_id,
  category_code,
  brand,
  CAST(price AS DECIMAL(10,2)) AS price, 
  user_id, 
  user_session,
  CAST(SUBSTRING(event_time,0,19)AS date) AS event_date,
  CURRENT_TIMESTAMP() as loaded_at
FROM
public.ecommerce_events_multicategorystore_live;
```
Check data objects in the target environment of the Lakehouse:

![](.topwrite/assets/image_1722603148172.png)
```SQL
select count(*)  from events_enriched ;
`count`(*) 
---------- 
3700       
```
Data objects and initial data successfully created and written.

## Running the Model

Run the model using the dbt run command:
```PowerShell
dbt run --model events_enriched
```
According to the logic of the dbt incremental model, dbt will create a temporary view in the target environment to represent the incremental data.
```SQL
/* {"app": "dbt", "dbt_version": "1.5.11", "profile_name": "cz_dbt_project", "target_name": "dev", "node_id": "model.cz_dbt_project.events_enriched"} */

create or replace view dbt_dev.events_enriched__dbt_tmp as
SELECT
  event_time,
  CAST(SUBSTRING(event_time,0,19) AS TIMESTAMP) AS event_timestamp, 
  SUBSTRING(event_time,12,2) AS event_hour, 
  SUBSTRING(event_time,15,2) AS event_minute, 
  SUBSTRING(event_time,18,2) AS event_second, 
  event_type,
  product_id, 
  category_id,
  category_code,
  brand,
  CAST(price AS DECIMAL(10,2)) AS price, 
  user_id, 
  user_session,
  CAST(SUBSTRING(event_time,0,19)AS date) AS event_date,
  CURRENT_TIMESTAMP() as loaded_at
FROM
public.stream_ecommerce_events;
```
At the same time, dbt uses the configuration materialized='incremental' in the model to write the incremental data from the table stream into the target model using MERGE INTO:
```SQL
/* {"app": "dbt", "dbt_version": "1.5.11", "profile_name": "cz_dbt_project", "target_name": "dev", "node_id": "model.cz_dbt_project.events_enriched"} */

    -- back compat for old kwarg name
merge into dbt_dev.events_enriched as DBT_INTERNAL_DEST
      using dbt_dev.events_enriched__dbt_tmp as DBT_INTERNAL_SOURCE
      on FALSE
  when not matched then insert
     (`event_time`,`event_timestamp`,`event_hour`,`event_minute`,`event_second`,`event_type`,`product_id`,`category_id`,`category_code`,`brand`,`price`,`user_id`,`user_session`,`event_date`,`loaded_at`)
  values (
        DBT_INTERNAL_SOURCE.`event_time`,DBT_INTERNAL_SOURCE.`event_timestamp`,DBT_INTERNAL_SOURCE.`event_hour`,DBT_INTERNAL_SOURCE.`event_minute`,DBT_INTERNAL_SOURCE.`event_second`,DBT_INTERNAL_SOURCE.`event_type`,DBT_INTERNAL_SOURCE.`product_id`,DBT_INTERNAL_SOURCE.`category_id`,DBT_INTERNAL_SOURCE.`category_code`,DBT_INTERNAL_SOURCE.`brand`,DBT_INTERNAL_SOURCE.`price`,DBT_INTERNAL_SOURCE.`user_id`,DBT_INTERNAL_SOURCE.`user_session`,DBT_INTERNAL_SOURCE.`event_date`,DBT_INTERNAL_SOURCE.`loaded_at`
    );
```
Each time `dbt run` is executed, data will be read from the table stream and merged into the target model. After a successful write, the change record position of the Table Stream will automatically advance, and the latest incremental data will be automatically processed during the next `dbt run`.

# Create Processing Tasks Based on Dynamic Tables

## Scenario Description

Combining the previous scenario design, we continue to use the Dynamic Table model of `dbt-clickzetta` to aggregate the already transformed tables.

First, create a model in DBT using the Dynamic Table ("materialized='dynamic\_table'"), configure the refresh cycle of the dynamic table, and the computing resources used for the refresh so that the system can automatically refresh according to the scheduling parameters after the model is built.

Next, observe the construction and refresh results of the dynamic table model in the target environment.

![](.topwrite/assets/image_1722603183742.png)

## Develop Model

Create a dynamic table model named `product\_grossing.sql`.

* Code Definition
```SQL
{{
   config(
       materialized = 'dynamic_table',
       vcluster = 'default',
       refresh_interval = '5 minute'
   )
}}

select 
  event_date,
  product_id,
  sum(price) sum_price 
from 
  {{ ref("events_enriched")}}
group by event_date,product_id
```
## Building Models

Create models in the target environment using the dbt build command:
```PowerShell
dbt build --model product_grossing
```
By observing the logs, the model is built with the following statement during model construction, and the initial processing and transformation of the original table is performed in full:
```SQL
/* {"app": "dbt", "dbt_version": "1.5.11", "profile_name": "cz_dbt_project", "target_name": "dev", "node_id": "model.cz_dbt_project.product_grossing"} */
create or replace dynamic table dbt_dev.product_grossing
refresh interval 5 minute
vcluster default
as
select 
  event_date,
  product_id,
  sum(price) sum_price 
from 
  dbt_dev.events_enriched
group by event_date,product_id;
```
By using dbt, you can view the model lineage:

![](.topwrite/assets/image_1722603216025.png)

Check data objects in the target environment of Lakehouse:
```SQL
show tables;

schema_name table_name               is_view is_materialized_view is_external is_dynamic 
----------- ------------------------ ------- -------------------- ----------- ---------- 
dbt_dev     events_enriched          false   false                false       false      
dbt_dev     events_enriched__dbt_tmp true    false                false       false      
dbt_dev     my_first_dbt_model       false   false                false       false      
dbt_dev     my_second_dbt_model      true    false                false       false      
```
At the same time, use the desc command to view the information of the dynamic table, focusing on confirming whether the running cluster and refresh cycle parameters meet expectations:
```SQL
desc extended product_grossing;

column_name                  data_type                                                                                                                                                                                                                                                     
---------------------------- ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
event_date                   date                                                                                                                                                                                                                                                          
product_id                   string                                                                                                                                                                                                                                                        
sum_price                    decimal(20,2)                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                           
# detailed table information                                                                                                                                                                                                                                                               
schema                       dbt_dev                                                                                                                                                                                                                                                       
name                         product_grossing                                                                                                                                                                                                                                              
creator                      xxx                                                                                                                                                                                                                                                        
created_time                 2024-06-22 21:03:40.467                                                                                                                                                                                                                                       
last_modified_time           2024-06-22 21:08:41.184                                                                                                                                                                                                                                       
comment                                                                                                                                                                                                                                                                                    
properties                   (("refresh_vc","default"))                                                                                                                                                                                                                                    
type                         DYNAMIC TABLE                                                                                                                                                                                                                                                 
view_text                    SELECT events_enriched.event_date, events_enriched.product_id, `sum`(events_enriched.price) AS sum_price FROM ql_ws.dbt_dev.events_enriched GROUP BY events_enriched.event_date, events_enriched.product_id;                                                  
view_original_text           select 
  event_date,
  product_id,
  sum(price) sum_price 
from 
  dbt_dev.events_enriched
group by event_date,product_id;                                                                                                                                   
source_tables                [86:ql_ws.dbt_dev.events_enriched=8278006558627319396]                                                                                                                                                                                                        
refresh_type                 on schedule                                                                                                                                                                                                                                                   
refresh_start_time           2024-06-22 21:03:40.418                                                                                                                                                                                                                                       
refresh_interval_second      300                                                                                                                                                                                                                                                           
unique_key_is_valid          true                                                                                                                                                                                                                                                          
unique_key_version_info      unique_key_version: 1, explode_sort_key_version: 1, digest: H4sIAAAAAAAAA3NMT9cx0nEP8g8NUHCKVDBScPb3CfX1C+ZSCE5OzANKBfmHx3u7Riq4Bfn7KqSWpeaVFMen5hVlJmekpnABAIf7bMY+AAAA, unique key infos:[sourceTable: 86:ql_ws.dbt_dev.events_enriched, uniqueKeyType: 1,] 
format                       PARQUET                                                                                                                                                                                                                                                       
format_options               (("cz.storage.parquet.block.size","134217728"),("cz.storage.parquet.dictionary.page.size","2097152"),("cz.storage.parquet.page.size","1048576"))                                                                                                              
statistics                   99 rows 4468 bytes                                                                                                                                                                                                                                            
```
## Running Models

Dynamic Table type dbt models are automatically scheduled by Lakehouse with the periodic refresh parameters set during construction, and do not need to be executed via dbt run.

After the model is built in the target environment, you can check the refresh status of the dynamic table on the Lakehouse platform using the following SQL command:
```SQL
show dynamic table refresh history where name ='product_grossing'

workspace_name schema_name name             virtual_cluster start_time          end_time            duration             state   refresh_trigger  suspended_reason refresh_mode error_message source_tables                                                             stats                                     completion_target job_id                   
-------------- ----------- ---------------- --------------- ------------------- ------------------- -------------------- ------- ---------------- ---------------- ------------ ------------- ------------------------------------------------------------------------- ----------------------------------------- ----------------- ------------------------ 
ql_ws          dbt_dev     product_grossing DEFAULT         2024-06-22 21:08:40 2024-06-22 21:08:41 0 00:00:00.566000000 SUCCEED SYSTEM_SCHEDULED (null)           INCREMENTAL  (null)        [{"schema":"dbt_dev","table_name":"events_enriched","workspace":"ql_ws"}] {"rows_deleted":"0","rows_inserted":"99"} (null)            202406222108406319689694 
```

^
