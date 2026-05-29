## Description

This command is used to view detailed information about a Table Stream, including creation time, modification time, workspace, and more.

## Syntax

```SQL
DESC[RIBE] TABLE STREAM ts_name;
```

**Parameter Description**

* **DESC\[RIBE**]: DESC and DESCRIBE can be used interchangeably; both mean to view or describe.
* **ts\_name**: Specifies the name of the Table Stream to view.

## Usage Examples

**Example 1: View basic information of a Table Stream**

```SQL
DESC TABLE STREAM event_stream;
```

Result:

```
+------------------------+--------------------------------+
| info_name              | info_value                     |
+------------------------+--------------------------------+
| name                   | event_stream                   |
| creator                | qiliang                        |
| created_time           | 2026-05-20 01:07:53.613        |
| last_modified_time     | 2026-05-20 01:07:53.618        |
| comment                | NULL                           |
| properties             | ((table_stream_mode,STANDARD)) |
| workspace              | quick_start                    |
| base_tables            | quick_start.ts_test.base_table |
| stale                  | false                          |
| offset                 | 7724571556140634312            |
| current_offset_time    | 2026-05-20 01:08:22.23         |
| current_offset_version | 4                              |
+------------------------+--------------------------------+
```

**Return Field Description:**

| Field | Description |
|---|---|
| `name` | Table Stream name |
| `creator` | Creator |
| `created_time` | Creation time |
| `last_modified_time` | Last modification time |
| `comment` | Comment |
| `properties` | Property configuration (e.g., `table_stream_mode`) |
| `workspace` | Owning workspace |
| `base_tables` | Source table name |
| `stale` | Whether expired (`true` means the source table's historical versions have been cleaned up) |
| `offset` | Current consumption offset |
| `current_offset_time` | Time corresponding to the current offset |
| `current_offset_version` | Version number corresponding to the current offset |

## Notes

* Before executing this command, ensure that the corresponding Table Stream has been created.
