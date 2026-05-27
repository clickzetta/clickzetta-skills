# Data Sharing

## What is Data Sharing

Data sharing is a no-copy data sharing feature provided by Singdata Lakehouse, used for data authorization across accounts or service instances within the same service region. In Singdata Lakehouse, users can share specified tables or views with other accounts in the same service region through the share object, without actually copying the data to other accounts.

Based on the data sharing feature, accounts can conveniently and securely share data and associate it with their own data for computation, fully exploring the value of the data.

The data shared through the share object is secured through permission control, and the data provider can cancel the sharing of specified data at any time through permission control of the share.

The data consumer does not need to pay for the storage resources occupied by the shared data but needs to use their own computing resources to process the shared data. When the shared data changes, the data consumer can immediately obtain the latest data without data synchronization.

:-: ![](.topwrite/assets/image_1704779759719.png =752)

## Typical Application Scenarios

Company A needs to provide its data to its customer, Company B, for use, requiring real-time data updates and avoiding the establishment of high-cost real-time data synchronization links. At this time, Company A can create a share object, authorize the data to be provided to the share object, and designate the share to Company B's service instance in Singdata Lakehouse. Company B can immediately use the data shared by Company A.

## Notes

* Shared data is "read-only," and the consumer is not allowed to modify or delete the data.
* The workspace that creates the share object determines the range of data objects that can be added to the share object. Adding data objects across workspaces is not supported.
* A share object can share up to 1000 table or view objects.
* If you need to share part of the data in a table, it is recommended to create a corresponding view based on the data to be shared and then share the view.
* The shared data is prohibited from being re-shared by the data consumer to protect the rights of the data provider.
* Currently, it is not possible to prevent the data consumer from copying the shared data, so the data provider needs to carefully select the range of data to be shared.

## DDL Commands for Data Sharing

[CREATE SHARE](create-share.md)

[ALTER SHARE](alter-share.md)

[GRANT TO SHARE](grant-to-share.md)

[REVOKE FROM SHARE](revoke-from-share.md)

[SHOW SHARES](show-shares.md)

[DESC SHARE](desc-share.md)

[DROP SHARE](drop-share.md)

## Supported Share Data Objects

Currently, the supported share data objects are: table and view objects.

It is supported to use all tables in schema \<schema\_name> and all views in schema \<schema\_name> to add all table and view objects under the specified schema to the share object. This operation includes all table and view objects created in the specified schema in the "future," so please operate with caution.

## Providing Data Sharing Operations

### Web Interface

**1. Create a Share Object**

To ensure data security, the data sharing (share) object must be created by a user with the "instance administrator" (instance\_admin) role. Click "Data Management" - "Data Sharing" in the left menu to enter the data sharing list page.

Click "+ Add Share" to open the new data sharing window:

:-: ![](.topwrite/assets/image_1740742973168.png =563)

1. Fill in the "Share Name" of the data sharing.

2. Select the "Workspace," which is the workspace where the table or view to be shared is located. A data sharing (share) object can only contain data from one workspace.

3. In the data object row, click "Add." Select the table or view to be included in the data sharing, multiple selections are allowed. But please note that tables and views from other data shares cannot be selected, as re-sharing of data is not allowed in the data sharing authorization. Data sharing created using the web interface only supports existing tables and views, and does not support specifying tables or views created in the entire schema in the "future."

4. In the receiving instance row, click "Add." Enter the name of the service instance that needs to receive the data. The service instance name is globally unique in the Lakehouse service. The service consumer user can find their service instance name on the right side of the homepage or in the URL of the service instance and provide it to the sharer for configuration.

:-: ![](.topwrite/assets/image_1740743048351.png =771)

^

*Note*:

1. *To ensure data security with the workspace as the isolation domain, only users with the workspace administrator role can add data objects within their managed workspace to the data sharing (share*).
2. *The "Create" and "Add Data" operations in the Create Data Share (share) Object dialog are two separate actions. Even if all or some of the data to be shared fails to be added, it will not affect the creation of the share object. If any operation fails, an error message will be returned. You can click on the created data share in the data share list to continue adding data objects or service instances to receive the data*.

**2. Query Created Data Share (share) Objects**

All data share (share) objects created within the current service instance are displayed on the "Data Share" list page. Users with the service instance administrator role (instance\_admin) or workspace administrator role (workspace\_admin) can view the data share (share) object list.

:-: ![](.topwrite/assets/image_1740743171507.png =800)

^

**3. Query Data Share (share) Details**

Click on the specific data share name displayed on the "Data Share" list page to query the detailed information of the data share, including basic information, the service instance receiving the share, and the shared data objects. Users with the service instance administrator role (instance\_admin) or workspace administrator role (workspace\_admin) can view the details of the data share (share) object.

:-: ![](.topwrite/assets/image_1740743139795.png =783)

^

**4. Add/Delete Shared Data Objects**

Users with the workspace administrator role of the space to which the data share belongs can add or delete data objects (table or view) in the data share.

On the data share list page, click the name of the share object to which you want to add data objects to enter the share object details page. Click the "Edit" button, and select the data objects to add or delete in the popup window. Click "OK" to complete the update of the shared data objects. Data from other share objects cannot be added.

The added data objects will immediately be visible to the consumers of the share object and will appear in their data extraction schema.

:-: ![](.topwrite/assets/image_1740743227652.png =813)

**5. Configure Share Targets**

The share object needs to be configured with the name of the service instance (instance\_name) to be shared in order to complete the data sharing. The service instance name needs to be provided by the data consumer.

:-: ![](.topwrite/assets/image_1740743268339.png =797)

^

**6. Delete Share Objects**

Users with the service instance administrator role (instance\_admin) or the workspace administrator role (workspace\_admin) of the space to which the data share belongs can delete data share objects.

In the data share list page or data share details, click the "Delete" button in the "Actions" to complete the deletion of the data share object. Once deleted, the share object cannot be recovered. The data consumer will immediately lose access to the shared data.

### Using SQL Operations

**1. Create Share Objects**

To ensure data security, share objects must be created by users with the "instance administrator" (instance\_admin) role. When creating a share object, the following statement needs to be executed in the workspace where the data is planned to be shared:

```SQL
CREATE SHARE <share_name>;
```

***

**2. Add Data Objects to the Share Object**

The created share object initially does not contain any data objects. You need to add the data objects to be shared using the Grant statement. The syntax is:

```SQL
GRANT select, read metadata ON {TABLE <table_name> | VIEW <view_name>} TO SHARE <share_name>;
```

Sure, please provide the document chunk you would like to translate.

```SQL
GRANT select, read metadata ON TABLE share_demo_table TO SHARE share_demo;
```

You can use the method `all tables in schema` or `all views in schema` to add all current and future table or view objects under the specified schema to the share, for example:

```SQL
Grant select, read metadata on ALL tables in SCHEMA share_demo_schema TO SHARE share_demo;
Grant select, read metadata on ALL views in SCHEMA share_demo_schema TO SHARE share_demo;
```

When adding data objects to be shared to a share object, the user performing the operation must have select (query) and read metadata permissions on the table or view objects involved in the share, and must be able to grant these permissions to others (with grant option). The workspace administrator role (workspace\_admin) naturally has these permissions.

To remove data objects from a share object, you can use the revoke statement:

```SQL
REVOKE select, read metadata on {TABLE <name> | VIEW <name>} FROM SHARE <share_name>;
```

Note: When sharing table or view objects, since table or view objects must exist under a schema object, the metadata permissions (read metadata) of that schema will also be automatically added to the share object. When removing table or view objects from the share, the metadata permissions of their respective schema will also be automatically removed.

***

**3. Configure the Share Target**

To complete data sharing, you need to configure the instance name (instance\_name) of the service being shared to the share object. The instance name needs to be provided by the data consumer.

The instance name is globally unique in the Lakehouse service. Data consumer users can find their instance name on the right side of the homepage or in the URL of the service instance and provide it to the sharer for configuration.

:-: ![](.topwrite/assets/image_1740743048351.png =731)

^

The syntax for the data sharer to configure the share target is as follows:

```SQL
ALTER SHARE <share_name> [ADD | REMOVE] INSTANCE <instance_name>; 
```

ADD refers to adding, and REMOVE refers to removing. This operation takes effect immediately, allowing you to add or remove target instances for sharing at any time. A share object can be shared with multiple service instances.

After completing the above three steps, the data is successfully shared with the specified service instance.

^

**4. Query Created Share Objects**

You can query the created share objects by executing the `show` command. The syntax is as follows:

```SQL
SHOW SHARES;
```

Example of the returned result is as follows:

:-: ![](.topwrite/assets/share_img_showshares.png =803)

Among them:

* provider is the tenant name of the share provider;
* provider\_instance is the service instance name of the share provider;
* provider\_workspace is the workspace to which the share belongs;
* scope is the sharing scope of the share, currently only supports PRIVATE - specifying instance sharing;
* to\_instance is the name of the service instance to which the share object is specified to be shared, multiple service instance names are separated by commas (,);
* kind is the type of share, OUTBOUND is the data shared out by the current service instance, INBOUND is the data shared to the current service instance by other service instances.

^

**5. Query the data objects shared by the specified share**

You can execute the following statement to query the data objects granted in the share:

```SQL
DESC SHARE <share_name>;
```

Example of return result is as follows:

:-: ![](.topwrite/assets/share_img_descshare.png =798)

^

**6. Delete share object**

You can execute the following command to delete the share object created by the current service instance:

```SQL
DROP SHARE <share_name>;
```

share objects cannot be recovered once deleted. Data consumers will immediately lose access to the shared data.

## Operations Using Shared Data

### Web Interface

**1. Query Shared Data**

Users with the service instance administrator (instance\_admin) role or workspace administrator (workspace\_admin) role can view all data share objects shared with the current service instance in the "Shared with Me" tab under the "Data Sharing" menu.

Click on the name of the data share object to view the source, reception time, and the data (table or view) currently included in the data share.

:-: ![](.topwrite/assets/image_1740743502071.png =768)

^

**2. Extract Shared Data to Create Schema**

In the "Shared with Me" list page or the details page of the data share object, click the "Extract" button to extract the data from the share.

:-: ![](.topwrite/assets/image_1740743548069.png =579)

^

When extracting data, it can only be extracted by schema, and extracting individual tables or views is not supported at this time.

:-: ![](.topwrite/assets/image_1740743576678.png =449)

First, you need to select the "source schema," which is the schema data you need to extract from the share. If the data share contains multiple schemas, you need to perform multiple extractions.

Then select the target workspace for data extraction and enter the schema name where the data will be stored. The data extraction operation will create a new schema in the workspace and store the data from the source schema. Note that the schema created will be a "read-only" schema, and no other data objects can be created in this schema.

After completing the above selections and inputs, click "OK" to complete the data extraction.

**3. Use Shared Data**

After completing the data extraction operation, you can see all the table and view objects shared under the schema in the specified created schema. You can perform select queries on these table and view objects or join queries with other tables and views.

Shared data is marked with a special icon in the "Data" column for easy identification.

:-: ![](.topwrite/assets/image_1734493884869.png =279)

### Using SQL Operations

**1. Query Shared Data**

Data consumers can query the shared share objects using the show shares command. The usage and return results are consistent with step 3 of providing data sharing.

Furthermore, you can query which schemas and table objects are included in the shared share using the desc shares command.

^

**2. Use Shared Data to Create Schema**

Data shared through a share needs to create a corresponding schema on the consumer side to be queried and used. The operation statement is as follows:

```SQL
CREATE SCHEMA <schema_name> FROM SHARE <provider_instance>.<share_name>.<schema_name>;
```

The `<provider_instance>` and `<share_name>` can be obtained from the query results of the `show shares` command, while `<schema_name>` can be retrieved by specifying the share name using the `desc share <share_name>` command.

The schema name in `Create schema <schema_name>` can be defined freely and does not need to match the schema name in the share.

To execute the above command, the operator must have the permission to create a schema in the workspace where the operation is performed. The workspace administrator role (`workspace_admin`) has this permission by default.

^

**3. Use the Shared Data**

After completing the execution of create schema from share, you can see all the table and view objects shared under the schema in the specified created schema. You can perform select queries on these table and view objects or join queries with other tables and views.

## Permissions of the Share Object

**1. Provider Permissions**

Only users with the service instance administrator (instance\_admin) role can create data sharing (share) objects. The permission points for creating share objects are as follows, and it is not currently supported to use the grant statement to grant share object permissions to other roles or users.

| **Permission Point**                                                 | **Description**                                                                                                                           |
| -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Create share                                                         | Permission to create share objects.                                                                                                       |
| Alter share                                                          | Modify share objects, add or remove shared instance names.                                                                                |
| Drop share                                                           | Delete share instances.                                                                                                                   |
| Read metadata                                                        | Permissions for show shares and desc share. The desc share can return the objects contained in the share and the granted objectPrivilege. |
| Grant objectprivilege to share&#xA;Revoke objectprivilege from share | Add or remove data objects to/from the share: &#xA;Grant objectPrivilege to; &#xA;Revoke objectPrivilege from.                            |

^

**2. Consumer Permissions**

Members in the workspace have the use and read metadata permissions for the share object. However, they must have the create schema permission in the workspace to use the data shared in the share to create a schema.

| **Permission Point** | **Description**                                                                       |
| -------------------- | ------------------------------------------------------------------------------------- |
| Use                  | Permission to use the share.                                                          |
| Read metadata        | Permission to query share metadata, allowing execution of Show shares and desc share. |

^
