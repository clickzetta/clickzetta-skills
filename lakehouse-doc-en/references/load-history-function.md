#### load\_history function

**Function description**: The load\_history function is used to view the history of COPY job imported files for a table, with a retention period of 7 days. At the same time, Pipe will avoid re-importing existing files based on load\_history during execution, ensuring data uniqueness.

**Function syntax**:
```SQL
load_history('schema_name.table_name')
```
* **schema\_name.table\_name**: Specify the table name to view the import history.

**Use Case**:
```SQL
SELECT * FROM load_history('myschema.mytable');
```