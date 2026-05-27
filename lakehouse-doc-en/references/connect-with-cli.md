# Singdata Lakehouse Command Line Client User Guide

This document aims to help you understand how to install, configure, and use the Singdata Lakehouse command line client. Through this guide, you will be able to smoothly connect to the Singdata Lakehouse service instance and execute various SQL commands.

## Prerequisites

Before using the client, please ensure the following conditions are met:

1. Your device has Java 8 or a higher version installed.
2. You have registered an account on the Singdata official website and created a Lakehouse service instance.
3. You have created a workspace for connection access.
4. The user identity using the client has been added to the workspace and authorized for access.

## Installing the Client

The Singdata Lakehouse command line client is developed based on the open-source SQL Line project. Please follow the steps below to install and configure the client:

1. Download the client installation package [sqlline\_cz.tar.gz](https://autolake-dev-beijing.oss-cn-beijing.aliyuncs.com/clickzetta-tool/release/sqlline_cz.tar.gz) from the public network or obtain it from Singdata staff.
2. Unzip the installation package file, and you will get the executable file and configuration file of the client tool.
```
% tar -zxvf sqlline_cz.tar.gz
x sqlline_cz/
x sqlline_cz/example.properties
x sqlline_cz/log4j.properties
x sqlline_cz/setup.sh
x sqlline_cz/sqlline
x sqlline_cz/sqlline-2.13.0-SNAPSHOT-jar-with-dependencies.jar
```
## Initialize Connection Environment

1. Enter the working directory:
```
cd sqlline_cz
```
2. Initialize Connection Environment:
   The main purpose is to download the latest JDBC package and place it in the sqlline\_cz directory. You can also download the latest JDBC package from the links below and place it in the sqlline\_cz directory.

* [Download Link One](https://mvnrepository.com/artifact/com.clickzetta/clickzetta-java)
* [Download Link Two](https://central.sonatype.com/artifact/com.clickzetta/clickzetta-java/versions)
```
sh setup.sh
```
## Configure Client Connection

### Method 1: Specify Connection Parameters via Command Line

Command parameters for connecting via specified method:
```
sh sqlline -d com.clickzetta.client.jdbc.ClickZettaDriver -u "<JDBC URL>" -n <user_name> -p <password>
```
JDBC URL format:
```
jdbc:clickzetta://<Lakehouse service instance name>.api.singdata.com/<workspace name>?schema=<default schema name>&virtualCluster=<compute cluster name>
```
Parameter Description:

* `<user_name>`: The username of the workspace member in the target workspace.
* `<password>`: The password of the workspace member in the target workspace.
* `schema`: The schema to be linked must be specified.
* `virtualCluster`: The computing resources to be used must be specified.

Example:
```
sh sqlline -d com.clickzetta.client.jdbc.ClickZettaDriver -u "jdbc:clickzetta://<lakehouse_instance_name>.api.singdata.com/<workspace_name>?schema=<target_schema_name>&vcluster=<your_virtualcluster_name>" -n <user_name> -p <your_password>
```
### Method 2: Specify Configuration File via Command Line

The command line tool provides a configuration file template, which you can modify and then specify the configuration file in the command line to achieve service connection. The sample configuration file format is as follows:
```
url=jdbc:clickzetta://<Lakehouse_instance_name>.api.singdata.com/<workspace_name>?schema=<schma_name>&virtualCluster=<vcluster_name>
driver=com.clickzetta.client.jdbc.ClickZettaDriver
user=<your_user_name>
password=<your_password>
```
After modifying the template configuration file according to your service information and saving it, connect to the service by specifying the configuration file name through command parameters.
```
$ sh sqlline properties <configuration file name>
```
Example:
```
$ sh sqlline properties test.properties
sqlline version 1.13.0-SNAPSHOT
0: jdbc:clickzetta://xxxx.api.singdata.com>show tables;
```
Singdata Lakehouse command line tool can create multiple different service connection configuration files at once. During use, you can quickly switch between service connections corresponding to different configuration files using the `!properties` command. The following example demonstrates switching from the configuration file test.properties to test.properties.1:
```
sqlline> !properties test.properties
Transaction isolation level TRANSACTION_REPEATABLE_READ is not supported. Default (TRANSACTION_READ_COMMITTED) will be used instead.
0: jdbc:clickzetta://xxxx.api.singdata.com> !properties test.properties.1
Transaction isolation level TRANSACTION_REPEATABLE_READ is not supported. Default (TRANSACTION_READ_COMMITTED) will be used instead.
1: jdbc:clickzetta://yyyyy.api.singdata.com> !go 0
0: jdbc:clickzetta://xxxx.api.singdata.com>
```
## Running SQL Commands

After a successful connection, you can execute Lakehouse SQL commands in the command line client. Here are some examples of SQL commands:

Switch the vcluster and schema to use:
```
use vcluster default;
use schema nyc_taxi_data;
```

View the tables in the current schema:
```
show tables;
```
![](.topwrite/assets/image_1699879449976.png)

Query data:
```
select  * from fhv_trips_staging limit 10;
```
![](.topwrite/assets/image_1699879794959.png)

## Exit Client
```
!quit
```
## Notes

By setting the following environment variables in the current environment, you can enable debug mode, output log files, and facilitate troubleshooting.
```
export SQLLINE_DEBUG_ENABLE=TRUE
```

