# CREATE SCHEMA FROM SHARE

## Description

The `CREATE SCHEMA FROM SHARE` statement is used to utilize shared data. This statement extracts the data objects contained in a specified share object on a schema-by-schema basis, allowing you to query or process these data objects within your data warehouse.

## Syntax Format

```SQL
CREATE SCHEMA <new_schema_name> FROM SHARE <instance_name>.<share_name>.<schema_name>;
```

## Parameter Description

**new\_schema\_name**
Specifies the name of the schema to be created in the local data warehouse based on the shared data. Note that this schema must not have the same name as any existing schema in the workspace, and the newly created schema will be read-only. You cannot create additional data objects within this schema.

**instance\_name.share\_name**
Specifies the name of the share to be extracted. Because different service instances might share share objects with the same name, you need to prepend the instance name to the share name to identify a unique share object accurately. You can obtain this information by executing the `SHOW SHARES;` statement as a user with either the instance\_admin or workspace\_admin role.

![](.topwrite/assets/image_1741176178688.png)

**schema\_name**
Indicates the data to be extracted, on a schema-by-schema basis. After execution, the data objects (tables, views, etc.) in **new\_schema\_name** will match the data objects in **schema\_name** of the share. Therefore, you need to fill in the schema\_name of the share you want to extract.

You can obtain this information by executing the `DESC SHARE <instance_name>.<share_name>;` statement as a user with the instance\_admin or workspace\_admin role. A single share object can contain multiple schemas, so use the name of the specific schema you need.

![](.topwrite/assets/img_v3_02k3_b8711160-8e1a-4875-b85f-4052505a27cg.jpg)

## Example

Extract the schema `sample_schema` from the `share_demo` share of the service instance `y237xm2x` into the local workspace schema named `data_from_share_demo`:

```SQL
CREATE SCHEMA data_from_share_demo FROM SHARE y237xm2x.share_demo.sample_schema;
```

## Related Statements

* [SHOW SHARES](show-shares.md)
* [DESC SHARE](desc-share.md)

^
