#### load_history Function

**Feature Description**: The load_history function is used to view the history of files imported by COPY jobs for a table, with a retention period of 7 days. Additionally, Pipe avoids duplicate imports of existing files based on the load_history, ensuring data uniqueness during execution.

**Function Syntax**:

```SQL
load_history('schema_name.table_name')
```

* **schema_name.table_name**: Specifies the name of the table for which to view the import history.

**Usage Example**:

```SQL
SELECT * FROM load_history('myschema.mytable');
```
