## Quick Start

This chapter will guide you through real business scenario cases to quickly get started with the core functional modules of Singdata Studio, and guide you to complete the end-to-end workflow from business database to data application. Through this chapter, you will understand:

* How to configure data sources
* How to create data integration tasks
* How to create data development tasks
* How to configure and publish task scheduling
* How to operate task instances
* How to connect to BI tools via JDBC
* How to create and call UDF functions

^

## Scenario 1: BI Analysis Scenario

^

### Scenario Introduction

The business intelligence BI of a company is generally provided by the company's business system with raw data. The backend database of the business system is generally a relational database, such as MySQL, Oracle, etc. This scenario takes the MySQL database as an example, and completes ① data source configuration, ② data integration, ③ data development, ④ task scheduling configuration and publishing, ⑤ task instance operation, and ⑥ connection to BI tools via JDBC through Singdata Studio, to meet the business requirements of BI data analysis.

^

### Workflow Diagram

![](.topwrite/assets/image_1692343510673.png)

### Business Requirements

The business requirements in this example simulate the common BI analysis scenario in the e-commerce scene, through user behavior log data, associated with product, store, time zone and other dimension table data, to generate a wide table of the data warehouse detail layer, provided to the downstream data application layer, and then through BI tools for sales, order count statistics, funnel conversion model, popular product display, etc.
![](.topwrite/assets/image_1692975150801.png)

^

The overall workflow construction idea is to complete the creation of data integration tasks for these 4 tables >> create 4 Lakehouse target tables, 1 real-time business table, and 3 dimension tables >> create data development tasks >> through SQL associated queries, merge the fields of the four tables into a wide table, write into a DWD layer result table >> configure task dependencies in the order of data integration tasks first, SQL tasks later >> bring all tasks to the production environment.
![](.topwrite/assets/image_1693020935459.png)

^

### Review of Preparation

Refer to the **Preparation** in the previous chapter, before "Quick Start", you need to make sure that your company has already opened the Singdata Lakehouse service, and you can log in to the Studio product homepage.

^

![](.topwrite/assets/9865a42db031a5516b4caf79bf0f4bb.png)

^

In the initialized product environment, you may already have the following object resources:

* Default user (User): **Your username** —— Figure 1
* Default workspace: **quickstart\_ws** —— Figure 2
* Default Schema: **public** —— Figure 3
* Default computing cluster: **General cluster: DEFAULT**, **Analytical cluster: DEFAULT**\_**AP**  —— Figure 4

Figure 1 —— User (User)
![](.topwrite/assets/image_1692348046212.png)

^

Figure 2 —— Workspace: QuickStart\_WorkSpace
![](.topwrite/assets/image_1692586908866.png)

^

Figure 3 —— Schema: Public
![](.topwrite/assets/image_1692583856135.png)

^

Figure 4 —— Computing Cluster: Default
![](.topwrite/assets/image_1692586859163.png)

^

### Start Working

Next, we will unfold the work step by step, starting from connecting to the business system's database.

^

#### 【Configure Data Source】

Studio provides two ways to create a new data source:

* Method one: You can create a new data source by following the steps ① \[Management] → ② \[Data Source] → ③ \[New Data Source];
* Method two: You can also create a new data source through ① \[Development] → ② \["✙" button] → ③ \[Offline Sync] → ④ \["✙" button].

^

Figure 1 —— Method one
![](.topwrite/assets/image_1692588245122.png)

^

Figure 2 —— Method two
![](.topwrite/assets/image_1692588445515.png)

^

![](.topwrite/assets/image_1692589881885.png)

^

In the new data source page, select the MySQL type data source and click Next.

^

![](.topwrite/assets/image_1692605359674.png)

^

Enter the database connection information and click the connectivity test. If the configuration is correct, a green \[√ connection is normal] will be displayed. If the connection test fails, you need to check the configuration information or change the database access whitelist policy. *If you need to add a specific IP whitelist, please contact Singdata customer service or account manager*.
![](.topwrite/assets/image_1692605303319.png)

^

After successful creation, you can see this data source in the list.
![](.topwrite/assets/image_1692605636158.png)

^

#### 【Create Data Integration Task】

^

Let's go back to the \[Development] menu and create an \[Offline Sync Task]

^

![](.topwrite/assets/image_1692588445515.png)

^

The task name here is temporarily named "MYSQL Data Integration Task", click OK.

^

![](.topwrite/assets/image_1692605970219.png)

^

In the list at ①, you can see the task we just created. Click at ② to select the data source type as MYSQL at ③, and select the data source name we just created: BizData\_Demo

^

![](.topwrite/assets/image_1692606182111.png)

^

Select the library at ①, select the table at ②, add filter conditions at ③, and click the button at ④ to preview the data. *splitPk is a split key used for multi-concurrent data extraction. It needs to split data according to the INT type primary key in the database table. It is not a necessary item, and it is not demonstrated in depth here*.

^

![](.topwrite/assets/image_1692608687809.png)

^

After clicking the \[Preview] button, a small amount of data will be previewed according to the configured filter conditions.

^

![](.topwrite/assets/image_1692608871867.png)

^

Since we are synchronizing data from the MySQL data source to Singdata Lakehouse, the target data source naturally selects the Lakehouse type, as shown in the steps ① → ② → ③

^

![](.topwrite/assets/image_1692609388901.png)

^

The namespace at ① can first select the default public, and since it is the first time to create a task, the data object has not been created in the Lakehouse, so ② provides a convenient one-click table creation function.

^

![](.topwrite/assets/image_1692610106739.png)

^

In the pop-up one-click table creation window, if you click the \[OK] button, it will directly create the Lakehouse table; in addition, it also supports copying the table creation statement, which is convenient for users to modify and create separately.

^
***Note***: *The DDL statement created by the one-click table creation does not create a [partitioned table] and does not include partition fields. If you want to create a partitioned table in Lakehouse, please modify the DDL statement for table creation. For the syntax of creating partitioned tables, please refer to the [SQL Reference] chapter*.

^

![](.topwrite/assets/image_1692610369991.png)

^

After creating the target table, the data object at ① will directly select this table, the computing cluster at ② does not need to be changed, and the default cluster is selected by default. The output mode is selected at ③. Since we are doing full data synchronization, we generally choose the [write overwrite] mode at ④.

^

![](.topwrite/assets/image_1692610656866.png)

^

After selecting the source table and the target table, the field mapping configuration below will be displayed. At ①, you can directly modify the target field name, at ②, you can enable or temporarily disable the field mapping of this row (other fields are not affected), and at ③, you can delete the field mapping of a single row to reduce some clearly useless fields.

^

![](.topwrite/assets/image_1692611229942.png)

^

At the bottom of the field mapping, you can also manually add fields or constant columns. The manually added fields can repeatedly obtain the value of a certain field in the source table and assign it to another field in the target table. Constant columns support some lightweight processing and conversion during data synchronization, and can assign fixed values or function expressions to target fields. This operation is not involved in this example, so it is not demonstrated.

^

![](.topwrite/assets/image_1692611971563.png)

^

So what if the field mapping is filled in incorrectly and you want to reset the field mapping relationship? Here we have also prepared reset and refresh functions, which are ① same-name mapping ② reset refresh ③ clear mapping ④ full screen.

^

![](.topwrite/assets/image_1692868770187.png)

^

After the task configuration is completed, the [save] at ① can save the task, and the [version] at ② can view the historical version information, which will not be elaborated here. It is worth mentioning that after the [schedule] at ③ is configured, the [submit] button can be unlocked. Only when the task is submitted to the production environment will the job be scheduled according to the schedule configuration, so the [operation and maintenance] button will be unlocked after the task [submit].

^

But after the task is saved, we usually click the [run] button at ④ to try to manually run the task and complete the data initialization integration.

^

![](.topwrite/assets/image_1692869115260.png)

^

After clicking [run] to start the task, the [run] button at ① will become the [stop] button, and a new item will be added to the running history below. The task instance that is running is marked at ②, and under the operation column on the right, you can usually view the task running details by looking at the [log] at ③.

^

![](.topwrite/assets/image_1692869694189.png)

^

The log information is as follows:

^

![](.topwrite/assets/image_1692869803721.png)

^

Next, wait for the task to complete. At this point, the data has been written into the Singdata Lakehouse.

^

![](.topwrite/assets/image_1692877068479.png)

^

#### [Configure Schedule Dependency]

Let's not rush to check the data count, continue to complete the configuration on the schedule. Click the [schedule] button on the function menu above, and the schedule menu will slide out on the right. We fast forward to the [schedule time] section: in the offline T+1 scenario, the schedule cycle is configured as [daily schedule], [execute once], [start scheduling at 00:00], start effective today, [never expire].

^

At ①, you can also choose [specified day every month], [specified day every week], and at ②, you can choose [execute multiple times] X minutes of scheduling cycle interval.

^

In the [instance information] section, since we have just run the task, the instance generation method at ③ can be selected as [effective the next day]. (Note: Tasks that run multiple times a day should choose [effective after release] after release, otherwise they will have to wait until the next day to start running)

^

[Instance error rerun] is the strategy for handling task error reruns. Usually we choose [can be rerun after success or failure], and will not elaborate here.

^

![](.topwrite/assets/image_1692877280440.png)

^

Finally, we come to ① [schedule dependency] and ② [task output] part, after the configuration is completed, we click the ③ [confirm] button, and the [submit] button can be unlocked, and we have the conditions to submit the task to the production environment for job scheduling.

^

About [schedule dependency], we all know that a standard warehouse processing process starts from data access, so data integration tasks are usually the starting nodes of the entire link, and there are no upstream dependent tasks, so the [schedule dependency] at ① does not make any settings. Of course, data integration tasks generally do not last for a day, so the [self-dependency] below does not need to be checked.

^

![](.topwrite/assets/image_1692929739481.png)

^

About [task output], first of all, we need to explain what the task output is for: the purpose of the currently completed data integration task configuration is to write the data of the corresponding table in the source database into the target table of the target end, so in the entire scheduling system, it needs to declare that this target table is "produced" by this task, that is, "task output".

^

The table name defined here as the task output is not only the "physical real name" of the target table, but also can be other "aliases" that are artificially changed, or even multiple different aliases. Its main function is to make the table produced by this task searchable by other tasks in the entire scheduling dependency system, thereby forming an upstream and downstream dependency relationship. Its biggest application is that it can be depended on by other tasks in the scheduling system.

^

Therefore, here provides manual custom addition of table names, and system [smart parsing] function button. In this example, there is no special adjustment of aliases, so just choose [smart parsing] directly, as shown in the figure.

^

![](.topwrite/assets/image_1692930975096.png)

^

After the configuration is completed, click [confirm] to unlock the [submit] button.

^

![](.topwrite/assets/image_1692931241963.png)

^

#### [Submit and Release Task]

Click the [submit] button, a confirmation window comparing with the historical version will pop up, this is the first submission in this example, just click [confirm].
![](.topwrite/assets/image_1692931416038.png)

^

After the submission is successful, a prompt will pop up, and the task status will change: [not submitted] → [submitted]

^

![](.topwrite/assets/image_1692931479995.png)

^

At this point, a data integration task has been released.
Next, we may have two questions:
1. I just synchronized the data, should I check the data volume and preview it?
2. The data integration task is published to the scheduling system, how to operate and view these tasks.
For the above 2 questions, we will explain them separately in the following [Data Development] chapter and [Task Instance Operation and Maintenance] chapter.

^

#### [Create Data Development Task]

^

Create a SQL task as shown in the figure, you can enter the SQL editor page, we first do some basic data exploration, such as checking the data volume of the just accessed table, previewing some data, etc.

^

![](.topwrite/assets/image_1692947107206.png)

^

The task name is tentatively set as "SQL Data Development Task", click confirm.

^

![](.topwrite/assets/image_1692947166405.png)

^
After successful creation, enter the SQL editor. The function buttons are roughly the same as the data integration tasks, with an additional [Format] button for beautifying SQL.
![](.topwrite/assets/image_1692947217040.png)

^

By using the statement to count the number of table entries, query the result. At ①, you can execute the Query locally / line by line, and at ②, all scripts will run tasks. Regardless of whether you use ① or ②, the results are viewed at ③.

^

![](.topwrite/assets/image_1692953836250.png)

^

Then we go to the source database to query the number of entries in this table, and we can find that the number of entries on both sides is consistent. (Don't forget that we added event\_id is not null in the [Filter] of data integration, and this condition should also be added when querying the source database)

^

![](.topwrite/assets/image_1692954920520.png)

^

Good, the amount of data on both sides is consistent. You can preview the data through a script similar to the following to see if the data format is correct, etc.

```
select * from tablename[Your table name] limit 10
```

^

Up to this step, the basic data exploration has been completed, and next we will build the entire workflow.

^

Let's confirm the business goal again: we have completed the configuration of the data source in order from left to right, and have learned how to create data integration tasks and data development tasks.
![](.topwrite/assets/image_1693020935459.png)

^

So, we only need to repeat the [Create Data Integration Task] multiple times to create these 4 tables and connect the data to Singdata Lakehouse.

^

Through the [Copy] function in the [More] option on the right side of the task name, you can quickly copy 4 tasks from the same data source, make slight modifications to the configuration, create the target table with one click, and complete the task creation very conveniently.

^

![](.topwrite/assets/image_1693016680123.png)

^

The name of the copied task is by default to add "\_copy" to the original task name, here you just need to change it to the name we want as needed.

^

![](.topwrite/assets/image_1693016822970.png)

^

Next, modify the script content in the data development task, complete the associated query of the user\_log table with the shop, goods, and timezone 3 dimension tables, and write the result into dwd\_user\_charac. If it is the first time to create a table, you can use the create table xxx as select... statement, and run it once. Of course, if you need to schedule tasks every day, the write method in the final submitted task should be [Overwrite Write] (insert overwrite).
![](.topwrite/assets/image_1693034692564.png)
![](.topwrite/assets/image_1693034727649.png)

^

Select the upstream scheduling dependency through fuzzy search.
![](.topwrite/assets/image_1693186498403.png)

^

We can only execute the SQL processing task after all the data integration tasks are completed, so just add four upstream tasks.
![](.topwrite/assets/image_1693188053947.png)

^

Other configurations are the same as the methods mentioned above, and finally don't forget to [Save] and [Submit], all submitted task icons should be with a green circle superscript style.
![](.topwrite/assets/image_1693188429895.png)

^

Okay, so far, we have completed the creation of all data integration tasks and data development tasks, and have run a round of tasks. Next, we will introduce how to check these task instances and bloodline relationships in the [Operation Center].

^

#### [Task Operation]

^

After the task is submitted to production, let's introduce some basic operation work. Click on [Task Operation] at ① to enter the operation center through the left menu bar. According to the tabs ②③④⑤ above, they represent [Periodic Tasks], [Real-time Tasks], [Supplemental Tasks], and [Task Instances].

^

When we click to enter the [Task Operation] function module, the page defaults to ④ [Task Instance], because operation personnel generally care about the running status and results of task instances every day. And task instances are divided into ⑥ [Periodic Instances], ⑦ [Temporary Instances], and the running status of task instances are: ⑧ [Run Successfully], ⑨ [Running], ⑩ [Run Failed] 3 kinds.

^

![](.topwrite/assets/image_1693193833131.png)

^

Here we need to understand the difference between [Task] and [Instance]: Task refers to a preset workflow configuration, while Instance is the instantiation of these workflow configurations, that is, the actual execution case.

^

We click on the periodic task tab to view our published SQL data development task, and we can enter the task details page.
![](.topwrite/assets/image_1693202818256.png)

^

In addition to its own information ①[Task Details], the task details page also provides ② [Task Instances], ③ [Node Code], ④ [Operation Log] viewing tabs, here only the task details tab is displayed.
The upper half of the task details shows some metadata information of the task.
![](.topwrite/assets/image_1693203132344.png)

^

The lower half shows the dependency relationship between this task and the upstream and downstream tasks.
![](.topwrite/assets/image_1693202961210.png)

^

So the above is the details of the task, in the details of the instance, you can also see the running status of the instance, similar to the task details, the difference is that the node displays the actual running situation of the instance, and supports some operations such as setting success, setting failure, rerunning, etc., here is not redundant.

^

#### [Connect BI Tools]

Based on the above content, we assume that all data preparation work has been completed, and the next step is data application. In this case, the data processed by the data warehouse is finally displayed on the BI dashboard.

^

The first point we need to understand is that Singdata Lakehouse provides a rich SDK, allowing BI tools to directly connect to Lakehouse via JDBC or Python SqlAlchemy, so most of the conventional BI tools on the market, such as: FineReport BI, SuperSet, Tableau, Hengshi BI, Power BI, etc., can be supported.

^

Taking FineReport BI as an example, first we can go to the < [JAVA SDK Introduction](java_reference/java-sdk-summary.md)>  section to get the JDBC Driver .
![](.topwrite/assets/image_1693290887172.png)

^

After downloading the JAVA SDK, we need to add this Driver to the third-party data connection driver in the system settings of FineReport BI.
FineReport BI is a bit special, by default, it does not allow users to upload drivers locally, you need to turn on the switch in the background. The operation steps refer to the official website documentation:
<https://help.fanruan.com/finebi/doc-view-1540.html>

^

After being allowed to manage the driver, we enter the data connection management through system settings.
![](.topwrite/assets/image_1693207507345.png)

^

In the page on the right, select [Driver Management] → [New Driver]
![](.topwrite/assets/image_1693207760197.png)
The driver name can be customized.
![](.topwrite/assets/image_1693207884575.png)

^

Upload the file at the location marked ① in the image. After the file is uploaded and parsed, select the class at location ② and ③.
![](.topwrite/assets/image_1693208001316.png)

^

Click the top right corner to save the driver.
![](.topwrite/assets/image_1693208098173.png)

After the configuration is complete, we return to data connection management, and we can create a new Lakehouse data source.
![](.topwrite/assets/image_1693209222368.png)

^

Since we are still a third-party connection driver, we choose [Other] → [Other JDBC]
![](.topwrite/assets/image_1693209282780.png)

^

Here, we select [Custom] in the driver type.
![](.topwrite/assets/image_1693209346360.png)

^

If you can find the driver option we just added, select it directly. If you can't find it, click [Add Driver] on the right.
![](.topwrite/assets/image_1693209431798.png)

^

We only need to define a [Database Name], and fill in the [Username], [Password], [Data Connection URL], etc. Users who are unsure about how to fill in the URL can refer to the SDK section of the help document or contact your account manager.
![](.topwrite/assets/image_1693209540889.png)

^

After filling in, click [Test Connection]. If the configuration is correct, it will display [Connection Successful]. Click the [Save] button to complete the creation.
![](.topwrite/assets/image_1693209771680.png)

^

If the connection name is affected by the URL, you can also customize it by [Rename].
![](.topwrite/assets/image_1693211182568.png)

^

After the data connection is successfully created, BI tools can access the Singdata Lakehouse just like other databases. Create data sets based on data sources, add database tables, and you can access the tables in Lakehouse.
![](.topwrite/assets/image_1693211916144.png)

^

![](.topwrite/assets/image_1693212056036.png)
Create a dashboard to reference the data set for arrangement. Interested students can refer to the FineBI help document.
<https://help.fanruan.com/finebi/>

^

Through certain dashboard style design, we can create a rich and colorful BI dashboard.
*The following images are demo examples based on mock data*
![](.topwrite/assets/image_1693211438223.png)

^

——————————————————————————

## Scenario 2: AI Analysis Scenario

^

### Scenario Introduction

This article will introduce how to use the "Lakehouse" architecture of Singdata Lakehouse to call AI algorithm models to process unstructured data, and associate and combine it with the structured data in the data warehouse to serve innovative data applications.

^

*Content is still under construction, please stay tuned*...
