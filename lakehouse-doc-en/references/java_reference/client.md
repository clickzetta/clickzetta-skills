# Client

This document introduces the initialization and usage of ClickZettaClient. ClickZettaClient is a client used to record Lakehouse connection information and can be used to create RowStream and create JDBC connections.

## ClickZettaClient Initialization

ClickZettaClient supports connection via JDBC URL or parameters. Below are examples of the two initialization methods:

### Connect Client via JDBC URL

```java
ClickZettaClient client = ClickZettaClient.newBuilder()
    .url("jdbc:clickzetta://instanceName.service/{0}?schema={1}&username={2}&password={3}&virtualcluster={4}")
    .build();
```

### Connect Client via Parameters

```java
ClickZettaClient client = ClickZettaClient.newBuilder()
    .instance("instanceName")
    .service("service")
    .username("username")
    .password("password")
    .vcluster("cluster")
    .schema("schema")
    .build();
```

| **Parameter** | **Required** | **Description**                                                                                                                                                                                    |
| ------------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| username      | Y            | Username                                                                                                                                                                                           |
| password      | Y            | Password                                                                                                                                                                                           |
| service       | Y            | Address to connect to the lakehouse, region.api.singdata.com. You can see the JDBC connection string in Lakehouse Studio Management -> Workspace ![](../.topwrite/assets/image_1740559132862.png)|
| instance      | Y            | Can be seen in Lakehouse Studio management -> workspace to view the JDBC connection string  ![](../.topwrite/assets/image_1740559198094.png)                          |
| workspace     | Y            | Workspace in use                                                                                                                                                                                   |
| vcluster      | Y            | VC in use                                                                                                                                                                                          |
| schema        | Y            | Name of the schema being accessed                                                                                                                                                                  |

### Close Client Connection

After using the client, be sure to explicitly call the `close()` method to release resources.

```java
clinet.close();
```

^
