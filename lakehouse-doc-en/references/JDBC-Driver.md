# JDBC Driver

## Java Environment Requirements

The Clickzetta Lakehouse JDBC driver requires Java version 1.8 or higher. Please ensure that your development environment has the appropriate version of Java installed and configured.

## JDBC Driver Download

You can download and use the Clickzetta Lakehouse JDBC driver in the following two ways:

1. Through Maven Dependency
   Add the following dependency code to your project's `pom.xml` file:
   ```xml
   <dependency>
     <groupId>com.clickzetta</groupId>
     <artifactId>clickzetta-java</artifactId>
     <version>${version}</version>
   </dependency>
   ```
2. Directly download the SDK Jar package, you can find and download the corresponding version of the Jar package on the Maven repository page.

* [Download Link 1](https://central.sonatype.com/artifact/com.clickzetta/clickzetta-java/versions)
* [Download Link 2](https://mvnrepository.com/artifact/com.clickzetta/clickzetta-java)

## Configure JDBC Driver

To use the Clickzetta Lakehouse JDBC driver to connect to Clickzetta Lakehouse, you need to configure it according to the following steps:

### JDBC Driver Class

In your JDBC application, use the `com.clickzetta.client.jdbc.ClickZettaDriver` class to load the driver.

### JDBC Connection String

When using the JDBC driver to connect to Clickzetta Lakehouse, the syntax format of the JDBC connection string is as follows:
```
jdbc:clickzetta://<service_instance_name>.api.singdata.com/<workspace_name>?<connection_params>
```
* Connection Parameters Description:

  * `<service_instance_name>`: Lakehouse service instance name. When a Lakehouse service instance is activated in a specified Region, the system will automatically assign an instance name. You can find the Lakehouse instance name on the Clickzetta product console page.

    ![](.topwrite/assets/image_1739867152425.png)

  * `<workspace_name>`: Workspace name.

  * `<connection_params>`: Supports defining parameters using the `=` format, with multiple parameters separated by the `&` symbol. Common parameters are listed in the table below:

| Parameter       | Value                                                                 |
| -------------- | ---------------------------------------------------------------------- |
| username       | Clickzetta login username                                              |
| password       | Login user password                                                    |
| schema         | Specifies the default schema to connect to, optional                                                       |
| virtualCluster | Configures the virtual cluster used by default for JDBC connections, optional. If not specified, you need to use the SQL command `use vcluster <vc_name>` after connecting to specify it for use |
| use\_http=true | Whether to use the HTTP protocol, default is HTTPS. This parameter needs to be specified when using a private link connection                          |

#### Connection String Example
```
jdbc:clickzetta://lakehouse_instance_name.api.singdata.com/default?username=Alice&password=xxxxx&schema=public&virtualCluster=default
```


