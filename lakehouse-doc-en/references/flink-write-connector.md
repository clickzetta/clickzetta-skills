# Function Overview

Lakehouse, through the flink-connector-lakehouse plugin, achieves seamless integration with Flink, enabling efficient data writing into Lakehouse. This plugin uses real-time interfaces for data writing, ensuring the timeliness of data processing.

Lakehouse provides two Flink Connector writing modes: igs-dynamic-table and igs-dynamic-table-append-only, to meet the needs of different scenarios.

1. **igs-dynamic-table**: Supports append mode and Flink CDC scenarios. In this mode, when Flink is used as a data source to access CDC logs, if the source end contains update, delete, and insert operations, and the Lakehouse server-side table is set with primary key attributes, using igs-dynamic-table will trigger data update and delete operations. Supports writing to [primary key tables](primary-key.md) in Lakehouse.
2. **igs-dynamic-table-append-only**: Particularly suitable for scenarios where data updates or deletions are not desired. Even when Flink CDC synchronizes data, this mode ensures that data is only appended, avoiding unnecessary data changes. If your goal is to avoid data deletions and updates, choosing igs-dynamic-table-append-only will be a safer choice. This way, your data will always remain in its original state and will not be affected by subsequent operations. Supports writing to regular tables in Lakehouse.

| **Category** | **Details**            |
| ------------ | ---------------------- |
| Supported Types | Only supports result tables, does not support source tables and dimension tables |
| Running Mode   | Stream mode           |

# Version Compatibility

| Flink Version       | Lakehouse Flink Connector Version |
| ------------------- | --------------------------------- |
| 1.14, 1.15, 1.16, 1.17 | Please contact Lakehouse support  |

When using FLINK-CDC, it is recommended to use version >= 2.3

# Usage

## Maven Introduction

The Maven repository coordinates are as follows:
```Plain
<dependency>
<groupId>com.clickzetta</groupId> 
<artifactId>igs-flink-connector-${corresponding flink version}</artifactId>
<version>Please contact Lakehouse support</version>
</dependency>
```
## Usage

### Writing Using SQL
```Java
// first. define your data source.
...
...

// second. define igs table sink.
String createTableSql =
    "CREATE TABLE MockTable (\n" +
    "  col1 INT,\n" +
    "  col2 INT,\n" +
    "  col3 STRING\n" +
    ") WITH (\n" +
     // For access permissions, please refer to the access instructions
    "   'connector' = 'igs-dynamic-table', \n" +
    "   'curl' = 'jdbc:clickzetta://instance-name.api.singdata.com/default?username=user&password=******&schema=public', \n" +
    "   'schema-name' = 'public', \n" +
    "   'table-name' = 'mock_table', \n" +
    "   'sink.parallelism' = '1'" +
    ")";
tableEnv.executeSql(createTableSql);

// third. execute.
TableResult tableResult = tableEnv.sqlQuery("select * from source").executeInsert("mock_table");
tableResult.print();
env.execute("Igs Mock Test");
```
### General Configuration Options

| Parameter                          | Required | Default Value                                                                  | Description                                                                                                                                                                                                                                                                                       |
| ---------------------------------- | -------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| connector                          | Yes      | -                                                                              | igs-dynamic-table: Supports append mode and Flink CDC scenarios, generally Lakehouse is a primary key table. igs-dynamic-table-append-only: Only supports append, Lakehouse is a regular table.                                                                                                                                           |
| curl                               | Yes      | -                                                                              | Lakehouse Jdbc connection address, can be obtained from the workspace page.                                                                                                                                                                                                                       |
| schema-name                      | Yes    | -                                                                             | Schema to be written                                                                                                                                                                                                                                                                                     |
| table-name                       | Yes    | -                                                                             | Table to be written                                                                                                                                                                                                                                                                                      |
| sink.parallelism                 | Yes    | -                                                                             | Degree of parallelism for writing                                                                                                                                                                                                                                                                                          |
| properites                       | Yes    | -                                                                             | "authentication":"true"                                                                                                                                                                                                                                                                         |
| workspace                        | No    | -                                                                             | Workspace name                                                                                                                                                                                                                                                                                          |
| flush.mode                       | No    | *AUTO\_FLUSH\_BACKGROUND*                                                     | Data flush mode, currently supports AUTO\_FLUSH\_SYNC: Wait for the last flush to complete before proceeding to the next write AUTO\_FLUSH\_BACKGROUND: Asynchronous flush allows multiple writes to proceed simultaneously without waiting for the previous write to complete                                                                                                                                                                                             |
| showDebugLog                     | No    | False                                                                         | Whether to enable debug logs                                                                                                                                                                                                                                                                                     |
| mutation.flush.interval          | No    | 10 \* 1000                                                                    | When this time limit is reached, the data will be actually flushed and submitted to the server. The conditions for data submission to the server are mutation.buffer.lines.num, mutation.buffer.space, and mutation.flush.interval, with any one of the three conditions being met first.                                                                                                                                                              |
| mutation.buffer.space            | No    | 5 \* 1024 \* 1024                                                             | Buffer accumulation size limit. When this limit is reached, the data will be actually flushed and submitted to the server. If the amount of data imported at one time reaches the MB level, this parameter can be increased to speed up the import. The conditions for data submission to the server are that any one of the three conditions: mutation.buffer.lines.num, mutation.buffer.space, or mutation.flush.interval is met first.                                                                                                                 |
| mutation.buffer.max.num          | No    | 5                                                                             | During data submission, mutation.buffer.lines.num specifies the threshold for sending after reaching a certain number of data entries, which triggers asynchronous sending. The mutation.buffer.max.num defines the maximum number of buffers that can exist simultaneously. Even if the data in the previous buffer has not been completely written, as long as the number of buffers does not exceed the limit specified by mutation.buffer.max.num, data can continue to be written to the new buffer. This allows the system to achieve higher concurrency when processing and sending data, as it does not have to wait for all buffers to be emptied before continuing to write new data. In short, mutation.buffer.max.num is equivalent to a JDBC connection pool. |
| mutation.buffer.lines.num        | No    | 100                                                                           | The accumulation limit of the number of data entries in each buffer. When the limit is reached, it will switch to a new buffer to continue accumulating until the mutation.buffer.max.num limit is reached, triggering a flush.                                                                                                                                                                                                                    |
| error.type.handler               | No    | com.clickzetta.platform.client.api.ErrorTypeHandler$TerminateErrorTypeHandler | Default value (terminate program): com.clickzetta.platform.client.api.ErrorTypeHandler$TerminateErrorTypeHandler Optional value (do not terminate program): com.clickzetta.platform.client.api.ErrorTypeHandler$DefaultErrorTypeHandler Potential risk of data loss                                                                                                     |
| request.failed.retry.enable      | No    | false                                                                         | Whether to enable the retry mechanism for mutate failures.                                                                                                                                                                                                                                                                               |
| request.failed.retry.times       | No    | 3                                                                             | Maximum number of retries for mutate failures.                                                                                                                                                                                                                                                                                |
| request.failed.retry.internal.ms | No    | 1000                                                                          | Unit: ms, interval time for retrying failures is 1000ms.                                                                                                                                                                                                                                                                            |
| request.failed.retry.status      | No    | THROTTLED                                                                     | Optional values: THROTTLED, FAILED, NOT\_FOUND, INTERNAL\_ERROR, PRECHECK\_FAILED, STREAM\_UNAVAILABLE                                                                                                                                                                                                            |
| mapping.operation.type.to        | Yes    | None                                                                             | If set to igs-dynamic-table-append-only, you can specify the field name in the LH Table for the CDC operator. Must be of STRING type. Write data enumeration values: INSERT｜UPDATE_BEFORE｜UPDATE_AFTER｜DELETE                                                                                                                                                          |

### Writing using DataStream method
```Java
// first. define your data source.
...
...

// second. define igs data sink.
// For access related to permissions, please refer to the access instructions
IgsWriterOptions writerOptions = IgsWriterOptions.builder()
    .streamUrl("jdbc:clickzetta://instance-name.api.singdata.com/default?username=user&password=******&schema=public")
    .withFlushMode(FlushMode.AUTO_FLUSH_BACKGROUND)
    .withMutationBufferMaxNum(3)
    .withMutationBufferLinesNum(10)
    .build();

IgsSink<Row> sink = new IgsSink<>(
    writerOptions,
    IgsTableInfo.from("public", "mock_table"),
    new RowOperationMapper(
        new String[]{"col1", "col2", "col3"},
        WriteOperation.ChangeType.INSERT)
);

// third. add sink to dataStream & execute.
dataStream.addSink(sink).name("mock-igs");
env.execute("Igs Mock Test");
```
* Parameter meanings and settings refer to general configuration options

## Usage Restrictions

* Currently only supports result tables, does not support source tables and dimension tables

# Specific Use Cases

## Real-time Data Synchronization: Using Flink CDC to Write MySQL Data into Lakehouse Primary Key Table

### Overview

This article details how to use the igs-dynamic-table mode of the Lakehouse flink connector to achieve real-time synchronization of MySQL database change data capture (CDC) logs into the Lakehouse primary key table. In igs-dynamic-table mode, the data in the Lakehouse primary key column can be automatically updated to ensure data consistency and real-time performance.

### STEP 1: Environment Preparation

* Use IntelliJ IDEA as the development tool, and have Flink programming capabilities.
* Obtain Lakehouse connection information, which can be viewed in Lakehouse Studio management -> workspace, and replace the jdbc protocol with igs. Modify as follows
![](../.topwrite/assets/image_1728887857029.png)
```SQL
igs:clickzetta://6861c888.cn-shanghai-alicloud.api.singdata.com/quickstart_ws?username=xxx&password=xxx&schema=public
```
* Locally set up Mysql database

* Download the FLink Connector package provided by Lakehouse (currently supported and provided by Lakehouse for download). Once downloaded, add the jar to the local maven repository for easy reference and packaging in maven projects.
  * ```SQL
    mvn install:install-file -Dfile=igs-flink-connector-15-0.11.0-shaded.jar -DgroupId=com.clickzetta -DartifactId=igs-flink-connector-15 -Dversion=0.11.0 -Dpackaging=jar
    ```
* Modify the pom.xml file and add the following dependencies
  * ```XML
    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <flink.version>1.15.2</flink.version>
        <java.version>1.8</java.version>
        <scala.binary.version>2.12</scala.binary.version>
        <maven.compiler.source>${java.version}</maven.compiler.source>
        <maven.compiler.target>${java.version}</maven.compiler.target>
        <scope-flink>compile</scope-flink>
    </properties>
    <repositories>
        <repository>
            <id>apache.snapshots</id>
            <name>Apache Development Snapshot Repository</name>
            <url>https://repository.apache.org/content/repositories/snapshots/</url>
            <releases>
                <enabled>false</enabled>
            </releases>
            <snapshots>
                <enabled>true</enabled>
            </snapshots>
        </repository>
    </repositories>

    <dependencies>
        <dependency>
            <groupId>com.ververica</groupId>
            <artifactId>flink-connector-mysql-cdc</artifactId>
            <version>2.3.0</version>
        </dependency>
        <dependency>
            <groupId>com.clickzetta</groupId>
            <artifactId>igs-flink-connector-15</artifactId>
            <version>0.11.0</version>
            <exclusions>
                <exclusion>
                    <groupId>org.slf4j</groupId>
                    <artifactId>*</artifactId>
                </exclusion>
            </exclusions>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-log4j12</artifactId>
            <version>1.7.7</version>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-table-planner_2.12</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-connector-base</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-runtime-web</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-table-api-java</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-table-api-java-bridge</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-table-common</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-streaming-java</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-clients</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-java</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-table-common</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-shade-plugin</artifactId>
                <version>3.2.4</version>
                <executions>
                    <execution>
                        <phase>package</phase>
                        <goals>
                            <goal>shade</goal>
                        </goals>
                        <configuration>
                            <createDependencyReducedPom>false</createDependencyReducedPom>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
    ```
### STEP 2: Create a table in Mysql and insert test data
```SQL
create table people (id int primary key,name varchar(100));
insert into people values(1,'a'),(2,'b'),(3,'c');
```
### STEP 3: Create Primary Key Table in Lakehouse
```SQL
create table people (id int,name string,primary key(id));
```
Lakehouse's **PRIMARY KEY** is used to ensure the uniqueness of each record in the table. In the Lakehouse architecture, for tables with a defined primary key, the system will automatically deduplicate data based on the primary key value during real-time data writing. Once a primary key is set, you will not be able to perform insert, delete, or update operations through SQL statements, nor can you add or delete columns.

### STEP 4: Write code and start the task in IDEA
```SQL
import org.apache.flink.api.common.restartstrategy.RestartStrategies;
import org.apache.flink.api.common.time.Time;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.TableResult;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import java.util.concurrent.ExecutionException;
public class MysqlCDCToLakehouse {
    public static void main(String[] args) throws ExecutionException, InterruptedException {

        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment()
                .setParallelism(1);
        env.setRestartStrategy(RestartStrategies.fixedDelayRestart(100, Time.seconds(60)));
        //      env.enableCheckpointing(60000);
//
//
//        env.getCheckpointConfig().setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);
//
//        env.getCheckpointConfig().setMinPauseBetweenCheckpoints(1000);

// checkpoint must be completed within 60s, otherwise it will be discarded, the default is 10 minutes
//        env.getCheckpointConfig().setCheckpointTimeout(60000);
// Only one checkpoint is allowed at a time
//        env.getCheckpointConfig().setMaxConcurrentCheckpoints(1);
// Allow up to 3 checkpoint failures
//        env.getCheckpointConfig().setTolerableCheckpointFailureNumber(3);
// Retain externally saved checkpoint information when Flink job is canceled
//        env.getCheckpointConfig().enableExternalizedCheckpoints(CheckpointConfig.ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION);
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(env);
        String mysqlCdc ="create table mysql_people(\n" +
                "    id int,\n" +
                "    name string,\n" +
                "    primary key(id) NOT ENFORCED)\n" +
                "with(\n" +
                "'connector' = 'mysql-cdc',\n" +
                "'hostname' = 'localhost',\n" +
                "'port' = '3306',\n" +
                "'username' = 'xxx',\n" +
                "'password' = 'xxx',\n" +
                "'database-name' = 'xxxx',\n" +
                "'server-time-zone'='Asia/Shanghai',\n" +
                "'table-name' = 'people'\n" +
                ")";

        tableEnv.executeSql(mysqlCdc);

        // second. define Singdata table sink.
        String lakehouseTable ="create table lakehouse_people(\n" +
                "    id int,\n" +
                "    name string,\n" +
                "    primary key(id) NOT ENFORCED)\n" +
                "with(\n" +
                "'connector'='igs-dynamic-table',\n" +
                "'curl'='igs:clickzetta://jnsxwfyr.api.singdata.com/qingyun?username=xxx&password=xxx&schema=public',\n" +
                "'properties' = 'authentication:true',\n"+
                "'schema-name' = 'public',\n" +
                "'table-name' = 'people',\n" +
                "'sink.parallelism' = '1'\n" +
                ")\n";
        tableEnv.executeSql(lakehouseTable);

        TableResult tableResult = tableEnv.sqlQuery("select * from mysql_people").executeInsert("lakehouse_people");
        tableResult.await();

    }
}
```
### STEP 5: Data Synchronization Verification

* After the startup is completed, the MySQL data will be automatically synchronized to the lakehouse. Query the data in the Lakehouse.
```SQL
select * from people;
+----+------+
| id | name |
+----+------+
| 2  | b    |
| 3  | c    |
| 1  | a    |
+----+------+
```
* Update a record in MySQL
```SQL
update people set name='A' where id=1;
```
* Querying in the Lakehouse will keep the data consistent with MySQL
```SQL
select * from people;
+----+------+
| id | name |
+----+------+
| 2  | b    |
| 3  | c    |
| 1  | A    |
+----+------+
```
## Real-time Data Synchronization: Writing MySQL Data into Lakehouse Regular Tables Using Flink CDC

### Overview

This document provides a detailed introduction on how to use the Lakehouse flink connector with the igs-dynamic-table-append-only mode to achieve real-time synchronization of MySQL database change data capture (CDC) logs into Lakehouse regular tables. In the igs-dynamic-table-append-only mode, Lakehouse will directly record the original CDC logs without updating the data in Lakehouse.

### STEP 1: Environment Preparation

* Use IntelliJ IDEA as the development tool, and have Flink programming capabilities.
* Obtain Lakehouse connection information, which can be viewed in Lakehouse Studio management -> workspace, and replace the jdbc protocol with igs. Modify as follows
![](../.topwrite/assets/image_1728887857029.png)
```SQL
igs:clickzetta://6861c888.cn-shanghai-alicloud.api.singdata.com/quickstart_ws?username=xxx&password=xxx&schema=public
```
* Locally set up Mysql database

* Download the FLink Connector package provided by Lakehouse (currently supported and provided by Lakehouse for download). After downloading, add the jar to the local maven repository for easy reference and packaging in maven projects.
  * ```SQL
    mvn install:install-file -Dfile=igs-flink-connector-15-0.11.0-shaded.jar -DgroupId=com.clickzetta -DartifactId=igs-flink-connector-15 -Dversion=0.11.0 -Dpackaging=jar
    ```
* Modify the pom.xml file and add the following dependencies
  * ```SQL
    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <flink.version>1.15.2</flink.version>
        <java.version>1.8</java.version>
        <scala.binary.version>2.12</scala.binary.version>
        <maven.compiler.source>${java.version}</maven.compiler.source>
        <maven.compiler.target>${java.version}</maven.compiler.target>
        <scope-flink>compile</scope-flink>
    </properties>
    <repositories>
        <repository>
            <id>apache.snapshots</id>
            <name>Apache Development Snapshot Repository</name>
            <url>https://repository.apache.org/content/repositories/snapshots/</url>
            <releases>
                <enabled>false</enabled>
            </releases>
            <snapshots>
                <enabled>true</enabled>
            </snapshots>
        </repository>
    </repositories>

    <dependencies>
        <dependency>
            <groupId>com.ververica</groupId>
            <artifactId>flink-connector-mysql-cdc</artifactId>
            <version>2.3.0</version>
        </dependency>
        <dependency>
            <groupId>com.clickzetta</groupId>
            <artifactId>igs-flink-connector-15</artifactId>
            <version>0.11.0</version>
            <exclusions>
                <exclusion>
                    <groupId>org.slf4j</groupId>
                    <artifactId>*</artifactId>
                </exclusion>
            </exclusions>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-log4j12</artifactId>
            <version>1.7.7</version>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-table-planner_2.12</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-connector-base</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-runtime-web</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-table-api-java</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-table-api-java-bridge</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-table-common</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-streaming-java</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-clients</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-java</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.flink</groupId>
            <artifactId>flink-table-common</artifactId>
            <version>${flink.version}</version>
            <scope>${scope-flink}</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-shade-plugin</artifactId>
                <version>3.2.4</version>
                <executions>
                    <execution>
                        <phase>package</phase>
                        <goals>
                            <goal>shade</goal>
                        </goals>
                        <configuration>
                            <createDependencyReducedPom>false</createDependencyReducedPom>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
    ```
### STEP 2: Create a table in Mysql and insert test data
```SQL
create table people_append (id int primary key,name varchar(100));
insert into people_append values(1,'a'),(2,'b'),(3,'c');
```
### STEP 3: Create a Regular Table in the Lakehouse
```SQL
create table people_append (id int,name string,source_operate string);
```
`source_operate` field is used to record log operations in MySQL. In Lakehouse Flink Connector, you can configure `mapping.operation.type.to` to specify the field name where the CDC operator falls into the Lakehouse table.

### STEP 4: Write code and start the task in IDEA
```SQL
import org.apache.flink.api.common.restartstrategy.RestartStrategies;
import org.apache.flink.api.common.time.Time;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.table.api.TableResult;
import org.apache.flink.table.api.bridge.java.StreamTableEnvironment;
import java.util.concurrent.ExecutionException;

public class MysqlAppendToLakehouse {
    public static void main(String[] args) throws ExecutionException, InterruptedException {

        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment()
                .setParallelism(1);
        env.setRestartStrategy(RestartStrategies.fixedDelayRestart(100, Time.seconds(60)));
        //      env.enableCheckpointing(60000);
//
//
//        env.getCheckpointConfig().setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);
//
//        env.getCheckpointConfig().setMinPauseBetweenCheckpoints(1000);

// checkpoint must be completed within 60s, otherwise it will be discarded, the default is 10 minutes
//        env.getCheckpointConfig().setCheckpointTimeout(60000);
// Only one checkpoint is allowed at the same time
//        env.getCheckpointConfig().setMaxConcurrentCheckpoints(1);
// Allow up to 3 checkpoint failures
//        env.getCheckpointConfig().setTolerableCheckpointFailureNumber(3);
// When the Flink task is canceled, retain the externally saved checkpoint information
//        env.getCheckpointConfig().enableExternalizedCheckpoints(CheckpointConfig.ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION);
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(env);
        String mysqlCdc ="create table mysql_people(\n" +
                "    id int,\n" +
                "    name string,\n" +
                "    primary key(id) NOT ENFORCED)\n" +
                "with(\n" +
                "'connector' = 'mysql-cdc',\n" +
                "'hostname' = 'localhost',\n" +
                "'port' = '3306',\n" +
                "'username' = 'root',\n" +
                "'password' = '123456',\n" +
                "'database-name' = 'mydb',\n" +
                "'server-time-zone'='Asia/Shanghai',\n" +
                "'table-name' = 'people_append'\n" +
                ")";

        tableEnv.executeSql(mysqlCdc);

        // second. define Singdata table sink.
        String lakehouseTable ="create table lakehouse_people(\n" +
                "    id int,\n" +
                "    name string,\n" +
                "    primary key(id) NOT ENFORCED)\n" +
                "with(\n" +
                "'connector'='igs-dynamic-table-append-only',\n" +
                "'curl'='igs:clickzetta://jnsxwfyr.api.singdata.com/qingyun?username=uat_test&password=Abcd123456&schema=public',\n" +
                "'properties' = 'authentication:true',\n"+
                "'schema-name' = 'public',\n" +
                "'table-name' = 'people_append',\n" +
                "'mapping.operation.type.to' = 'source_operate',\n" +
                "'sink.parallelism' = '1'\n" +
                ")\n";
        tableEnv.executeSql(lakehouseTable);

        TableResult tableResult = tableEnv.sqlQuery("select * from mysql_people").executeInsert("lakehouse_people");
        tableResult.await();

    }
}
```
### STEP 5: Data Synchronization Verification

* After the startup is completed, the MySQL data will be automatically synchronized to the lakehouse. Query the data in the Lakehouse.
```SQL
select * from people;
+----+------+
| id | name |
+----+------+
| 2  | b    |
| 3  | c    |
| 1  | a    |
+----+------+
```
* Update a record in MySQL
```SQL
update people set name='A' where id=1;
```
* Querying in the Lakehouse will keep a record of all MySQL operations
```SQL
+----+------+----------------+
| id | name | source_operate |
+----+------+----------------+
| 1  | a    | INSERT         |
| 2  | b    | INSERT         |
| 3  | c    | INSERT         |
| 1  | a    | UPDATE_BEFORE  |
| 1  | A    | UPDATE_AFTER   |
+----+------+----------------+
```