# ALTER SCHEMA

## Description

The `ALTER SCHEMA` statement is used to adjust the name, properties, and comments of a specified schema. With this statement, you can update the comments and properties of a schema to adapt to changes in data processing needs and organizational structure.

## Modify Schema Name

Syntax:

```SQL
ALTER SCHEMA schema_name RENAME TO new_name;
```

## Modify Schema Comments

To modify the schema comments, use the following syntax:

```SQL
ALTER SCHEMA schema_name SET COMMENT 'new_comment';
```

### Example

1. Modify the comment of the `rc4_l` schema to `rc7`:

   ```SQL
   ALTER SCHEMA rc4_l SET COMMENT 'rc7';
   ```

   After executing this statement, use the `DESC` command to verify that the comment was successfully modified:

   ```SQL
   DESC SCHEMA rc4_l;
   ```

   Expected output:

   ```
   +--------------------+-------------------------+
   |     info_name      |       info_value        |
   +--------------------+-------------------------+
   | name               | rc4_l                   |
   | creator            | UAT_TEST                |
   | created_time       | 2023-12-15 20:38:14.126 |
   | last_modified_time | 2023-12-20 14:54:59.826 |
   | comment            | rc7                     |
   +--------------------+-------------------------+
   ```

## Modify Schema Properties

In addition to modifying comments, you can also set or update properties for the schema. Use the following syntax:

```SQL
ALTER SCHEMA schema_name SET PROPERTIES (key1 = 'value1', key2 = 'value2', ...);
```

### Example

1. Set the attribute `custom_property` to `true` for the `rc4_l` schema:

   ```SQL
   ALTER SCHEMA rc4_l SET PROPERTIES (custom_property = 'true');
   ```

   Check whether the schema attribute was set successfully:

   ```SQL
   DESC SCHEMA rc4_l;
   ```

   The properties section in the expected output should contain the newly set properties:

   ```
   +--------------------+-------------------------+
   |     info_name      |       info_value        |
   +--------------------+-------------------------+
   | ...                 | ...                      |
   | properties          | {custom_property='true'} |
   +--------------------+-------------------------+
   ```

## Permission Requirements

The user executing the `ALTER SCHEMA` statement must have the ALTER permission for the corresponding schema. If the user does not have the appropriate permissions, the operation will be denied.
