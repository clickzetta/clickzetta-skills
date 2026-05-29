# MERGE INTO

The `MERGE INTO` statement is used to update records in the target table based on values from the source table or subquery. This feature can be used to synchronize data in the target table when the source table contains new rows (to be inserted), modified rows (to be updated), and deleted rows (to be deleted).

MERGE INTO is a SQL statement that performs "update if exists, insert if not, delete if condition matches" operations -- essentially combining INSERT + UPDATE + DELETE into a single atomic transaction, commonly used for data synchronization and CDC consumption scenarios.

## Syntax

```SQL
MERGE INTO target_table 
   USING source_table
   ON merge_condition
   { WHEN MATCHED [ AND matched_condition ] THEN matched_action |
    WHEN  MATCHED [ AND matched_condition ] THEN matched_action |
    -- When both WHEN MATCHED and WHEN NOT MATCHED clauses exist, only one WHEN NOT MATCHED clause is allowed in the MERGE INTO statement
    WHEN NOT MATCHED [ AND not_matched_by_source_condition ] THEN not_matched_by_source_action } 
-- Parameter explanation
matched_action ::=
    UPDATE SET <column_name> = <expr> [ , <column_name2> = <expr2> ... ] 
    | DELETE 
not_matched_action ::=
    INSERT [ ( <column_name> [ , ... ] ) ] VALUES ( <expr> [ , ... ] )
```

## Parameter Description

- `target_table`: The target table to synchronize data into (the table being modified). Aliases can be used.
- `source_table`: The data source, which can be a table, subquery, or Table Stream. Aliases can be used.
- `merge_condition`: The matching condition that determines which row from the source table corresponds to which row in the target table -- typically uses primary key matching and must ensure a one-to-one relationship. Returns a boolean expression.

  > CAUTION: The `ON` condition must ensure that each row in the source table matches at most one row in the target table. If one source row matches multiple target rows, MERGE will report an error (non-deterministic result). It is recommended to use primary keys or unique keys in the ON condition.

- `WHEN MATCHED [ AND matched_condition ]`: Executed when a source row matches a target row -- typically used for UPDATE or DELETE.
  - If no `WHEN MATCHED` condition evaluates to true for a pair of source and target rows matching `merge_condition`, the target row remains unchanged.
  - If multiple `WHEN MATCHED` clauses exist, they are evaluated in the order specified. Each `WHEN MATCHED` clause must have a `matched_condition`.
- `WHEN NOT MATCHED [ AND not_matched_condition ]`: Executed when a row exists in the source table but not in the target table -- typically used for INSERT of new rows.
  - Only one `WHEN NOT MATCHED` clause is allowed.
- `matched_action`:
  - `DELETE`: Deletes the matching target table row.
  - `UPDATE`: Updates the matching target table row. Use `UPDATE SET column1 = source.column1 [, column2 = source.column2 ...]`.
- `not_matched_action`:
  - `INSERT`: Inserts into the target table using the corresponding columns from the source dataset, supports specifying fields for insertion. For unspecified target columns, `NULL` is inserted.

## Notes

When executing the `MERGE INTO` statement may produce non-deterministic results, the system will report an error. The reasons for this situation include:

1. If the `ON` clause causes more than one row from the source table to match a row in the target table, the SQL standard requires an error to be raised.
2. If the `ON` clause causes more than one row from the source table to match a row in the target table, and there are still multiple records after filtering with the `AND case_predicate` condition.
3. When both WHEN MATCHED and WHEN NOT MATCHED clauses exist, only one WHEN NOT MATCHED clause is allowed in the MERGE INTO statement.
4. When multiple WHEN MATCHED clauses exist, the UPDATE clause must precede the DELETE clause.

Deterministic result situations:

1. If the `ON` clause matches exactly 1 row in the source table with a row in the target table.
2. If the `ON` clause matches more than 1 row in the source table with a row in the target table, but only one record remains after filtering with the `AND case_predicate` condition.

## Detailed Usage Examples

### Case 1: Delete Data from the Target Table When Match Condition is Met

**Scenario**: Delete all user records that exist in the source table (mark-for-deletion pattern).

**Table Creation Statements**

```sql
-- Target table: stores user information
CREATE TABLE users_target (
  id INT,
  name STRING,
  value INT,
  updated_at STRING,
  marked_for_deletion BOOLEAN
);

-- Source table: user data to be synchronized
CREATE TABLE users_source (
  id INT,
  name STRING,
  value INT,
  updated_at STRING,
  marked_for_deletion BOOLEAN
);
```

**Data inserted into the target table:**
```sql
INSERT INTO users_target VALUES 
(1, 'Alice', 100, '2024-01-01', false),
(2, 'Bob', 200, '2024-01-02', false),
(3, 'Charlie', 300, '2024-01-03', false);
```

```
+----+---------+-------+------------+---------------------+
| id | name    | value | updated_at | marked_for_deletion |
+----+---------+-------+------------+---------------------+
| 1  | Alice   | 100   | 2024-01-01 | false               |
+----+---------+-------+------------+---------------------+
| 2  | Bob     | 200   | 2024-01-02 | false               |
+----+---------+-------+------------+---------------------+
| 3  | Charlie | 300   | 2024-01-03 | false               |
+----+---------+-------+------------+---------------------+
```

**Data inserted into the source table:**
```sql
INSERT INTO users_source VALUES 
(1, 'Alice', 100, '2024-01-01', false),
(2, 'Bob', 200, '2024-01-02', false);
```

```
+----+-------+-------+------------+---------------------+
| id | name  | value | updated_at | marked_for_deletion |
+----+-------+-------+------------+---------------------+
| 1  | Alice | 100   | 2024-01-01 | false               |
+----+-------+-------+------------+---------------------+
| 2  | Bob   | 200   | 2024-01-02 | false               |
+----+-------+-------+------------+---------------------+
```

**MERGE SQL**

```sql
MERGE INTO users_target t USING users_source s
ON t.id = s.id
WHEN MATCHED THEN DELETE;
```

**Result**

```
+----+---------+-------+------------+---------------------+
| id | name    | value | updated_at | marked_for_deletion |
+----+---------+-------+------------+---------------------+
| 3  | Charlie | 300   | 2024-01-03 | false               |
+----+---------+-------+------------+---------------------+
```

**Explanation**: Records with id 1 and 2 in the source table found matches in the target table and were deleted. The Charlie record (id=3) remains unchanged because it has no match in the source table.

### Case 2: Conditional Update Based on Timestamp

**Scenario**: Only update the target table values when the source table's update timestamp is newer than the target table's update timestamp.

**Table Creation Statements**

```sql
-- Target table: product information
CREATE TABLE products_target (
  id INT,
  name STRING,
  col1 STRING,
  updated_at STRING
);

-- Source table: new product data
CREATE TABLE products_source (
  id INT,
  name STRING,
  col1 STRING,
  updated_at STRING
);
```

**Initial target table data:**
```sql
INSERT INTO products_target VALUES 
(1, 'Product A', 'value_old', '2024-01-01'),
(2, 'Product B', 'value_old', '2024-01-02'),
(3, 'Product C', 'value_old', '2024-01-03');
```

```
+----+------------+-----------+------------+
| id | name       | col1      | updated_at |
+----+------------+-----------+------------+
| 1  | Product A  | value_old | 2024-01-01 |
+----+------------+-----------+------------+
| 2  | Product B  | value_old | 2024-01-02 |
+----+------------+-----------+------------+
| 3  | Product C  | value_old | 2024-01-03 |
+----+------------+-----------+------------+
```

**Initial source table data:**
```sql
INSERT INTO products_source VALUES 
(1, 'Product A', 'value_new', '2024-01-10'),
(2, 'Product B', 'value_old', '2024-01-01'),
(4, 'Product D', 'value_new', '2024-01-04');
```

```
+----+------------+-----------+------------+
| id | name       | col1      | updated_at |
+----+------------+-----------+------------+
| 1  | Product A  | value_new | 2024-01-10 |
+----+------------+-----------+------------+
| 2  | Product B  | value_old | 2024-01-01 |
+----+------------+-----------+------------+
| 4  | Product D  | value_new | 2024-01-04 |
+----+------------+-----------+------------+
```

**MERGE SQL**

```sql
MERGE INTO products_target t USING products_source s
ON t.id = s.id
WHEN MATCHED AND t.updated_at < s.updated_at THEN UPDATE SET t.col1 = s.col1;
```

**Result**

```
+----+------------+-----------+------------+
| id | name       | col1      | updated_at |
+----+------------+-----------+------------+
| 1  | Product A  | value_new | 2024-01-01 |
+----+------------+-----------+------------+
| 2  | Product B  | value_old | 2024-01-02 |
+----+------------+-----------+------------+
| 3  | Product C  | value_old | 2024-01-03 |
+----+------------+-----------+------------+
```

**Explanation**:
- **Product A (id=1)**: Source update time `2024-01-10` > target update time `2024-01-01`, condition satisfied, col1 updated to `value_new`.
- **Product B (id=2)**: Source update time `2024-01-01` <= target update time `2024-01-02`, condition not satisfied, remains unchanged.
- **Product C (id=3)**: No corresponding record in the source table (id=3), no action taken, remains unchanged.
- **Product D (id=4)**: New row in the source table, but no WHEN NOT MATCHED clause exists on the ON condition, so it is not inserted.

### Case 3: Combining Deletion Markers with Conditional Updates

**Scenario**: Operate on user data -- users marked for deletion are directly deleted, while other matched users have their status information updated.

**Table Creation Statements**

```sql
-- Target table: user information
CREATE TABLE users_data_target (
  id INT,
  name STRING,
  marked_for_deletion BOOLEAN,
  updated_at STRING,
  value STRING
);

-- Source table: user data to be synchronized
CREATE TABLE users_data_source (
  id INT,
  name STRING,
  marked_for_deletion BOOLEAN,
  updated_at STRING,
  value STRING
);
```

**Initial target table data:**
```sql
INSERT INTO users_data_target VALUES 
(1, 'User A', false, '2024-01-01', 'active'),
(2, 'User B', true, '2024-01-02', 'inactive'),
(3, 'User C', false, '2024-01-03', 'active'),
(4, 'User D', true, '2024-01-04', 'inactive');
```

```
+----+--------+---------------------+------------+----------+
| id | name   | marked_for_deletion | updated_at | value    |
+----+--------+---------------------+------------+----------+
| 1  | User A | false               | 2024-01-01 | active   |
+----+--------+---------------------+------------+----------+
| 2  | User B | true                | 2024-01-02 | inactive |
+----+--------+---------------------+------------+----------+
| 3  | User C | false               | 2024-01-03 | active   |
+----+--------+---------------------+------------+----------+
| 4  | User D | true                | 2024-01-04 | inactive |
+----+--------+---------------------+------------+----------+
```

**Initial source table data:**
```sql
INSERT INTO users_data_source VALUES 
(1, 'User A', false, '2024-01-15', 'updated'),
(2, 'User B', true, '2024-01-20', 'to_delete'),
(3, 'User C', false, '2024-01-10', 'updated'),
(5, 'User E', false, '2024-01-05', 'new_user');
```

```
+----+--------+---------------------+------------+-----------+
| id | name   | marked_for_deletion | updated_at | value     |
+----+--------+---------------------+------------+-----------+
| 1  | User A | false               | 2024-01-15 | updated   |
+----+--------+---------------------+------------+-----------+
| 2  | User B | true                | 2024-01-20 | to_delete |
+----+--------+---------------------+------------+-----------+
| 3  | User C | false               | 2024-01-10 | updated   |
+----+--------+---------------------+------------+-----------+
| 5  | User E | false               | 2024-01-05 | new_user  |
+----+--------+---------------------+------------+-----------+
```

**MERGE SQL**

```sql
MERGE INTO users_data_target t USING users_data_source s
ON t.id = s.id
WHEN MATCHED AND t.marked_for_deletion = false THEN UPDATE SET t.updated_at = s.updated_at, t.value = s.value
WHEN MATCHED AND t.marked_for_deletion = true THEN DELETE;
```

**Result**

```
+----+--------+---------------------+------------+---------+
| id | name   | marked_for_deletion | updated_at | value   |
+----+--------+---------------------+------------+---------+
| 1  | User A | false               | 2024-01-15 | updated |
+----+--------+---------------------+------------+---------+
| 3  | User C | false               | 2024-01-10 | updated |
+----+--------+---------------------+------------+---------+
| 4  | User D | true                | 2024-01-04 | inactive|
+----+--------+---------------------+------------+---------+
```

**Explanation**:
- **User A (id=1)**: `marked_for_deletion=false`, satisfies the first WHEN MATCHED condition, `updated_at` and `value` are updated.
- **User B (id=2)**: `marked_for_deletion=true`, satisfies the second WHEN MATCHED condition, deleted.
- **User C (id=3)**: `marked_for_deletion=false`, satisfies the first WHEN MATCHED condition, `updated_at` and `value` are updated.
- **User D (id=4)**: No corresponding record in the source table, remains unchanged.
- **User E (id=5)**: New row in the source table, but no WHEN NOT MATCHED clause, not inserted.

---

### Case 4: Full Synchronization with Insert and Update

**Scenario**: Complete data synchronization operation -- both update matching records and insert new records.

**Table Creation Statements**

```sql
-- Target table: data records
CREATE TABLE data_sync_target (
  id INT,
  col1 STRING,
  col2 STRING
);

-- Source table: new data
CREATE TABLE data_sync_source (
  id INT,
  col1 STRING,
  col2 STRING
);
```

**Initial target table data:**
```sql
INSERT INTO data_sync_target VALUES 
(1, 'data_a', 'value_a'),
(2, 'data_b', 'value_b'),
(3, 'data_c', 'value_c');
```

```
+----+--------+---------+
| id | col1   | col2    |
+----+--------+---------+
| 1  | data_a | value_a |
+----+--------+---------+
| 2  | data_b | value_b |
+----+--------+---------+
| 3  | data_c | value_c |
+----+--------+---------+
```

**Initial source table data:**
```sql
INSERT INTO data_sync_source VALUES 
(1, 'updated_a', 'updated_value_a'),
(2, 'updated_b', 'updated_value_b'),
(4, 'new_data', 'new_value'),
(5, 'new_data2', 'new_value2');
```

```
+----+----------+------------------+
| id | col1     | col2             |
+----+----------+------------------+
| 1  | updated_a| updated_value_a  |
+----+----------+------------------+
| 2  | updated_b| updated_value_b  |
+----+----------+------------------+
| 4  | new_data | new_value        |
+----+----------+------------------+
| 5  | new_data2| new_value2       |
+----+----------+------------------+
```

**MERGE SQL**

```sql
MERGE INTO data_sync_target t USING data_sync_source s
ON t.id = s.id
WHEN MATCHED THEN UPDATE SET t.col1 = s.col1, t.col2 = s.col2
WHEN NOT MATCHED THEN INSERT (id, col1, col2) VALUES (s.id, s.col1, s.col2);
```

**Result**

```
+----+----------+------------------+
| id | col1     | col2             |
+----+----------+------------------+
| 1  | updated_a| updated_value_a  |
+----+----------+------------------+
| 2  | updated_b| updated_value_b  |
+----+----------+------------------+
| 3  | data_c   | value_c          |
+----+----------+------------------+
| 4  | new_data | new_value        |
+----+----------+------------------+
| 5  | new_data2| new_value2       |
+----+----------+------------------+
```

**Explanation**:
- **id=1, 2**: Matching records exist in the source table, UPDATE is performed, both col1 and col2 are updated to source table values.
- **id=3**: No corresponding record in the source table, retains its original values.
- **id=4, 5**: New records from the source table, INSERT is performed, inserted into the target table.

---

### Case 5: Consuming Table Stream for Incremental Synchronization

**Scenario**: Use MERGE to consume a STANDARD mode Table Stream, synchronizing changes from the `products` table to the `products_replica` copy table in real time.

**Prerequisites**: A `products_stream` (STANDARD mode) has been created. Each change record in the Stream carries a `__change_type` field with values of `INSERT`, `UPDATE_BEFORE`, `UPDATE_AFTER`, or `DELETE`.

**MERGE SQL**

```sql
MERGE INTO doc_test.products_replica t
USING doc_test.products_stream s ON t.product_id = s.product_id
WHEN MATCHED AND s.__change_type = 'UPDATE_AFTER'
    THEN UPDATE SET t.name = s.name, t.price = s.price, t.stock = s.stock
WHEN MATCHED AND s.__change_type = 'DELETE'
    THEN DELETE
WHEN NOT MATCHED AND s.__change_type = 'INSERT'
    THEN INSERT (product_id, name, price, stock, category)
         VALUES (s.product_id, s.name, s.price, s.stock, s.category);
-- UPDATE_BEFORE rows do not need to be processed; MERGE automatically ignores unmatched conditions
```

**Explanation**:
- `UPDATE_AFTER`: Records the new values after an update. When a matching row exists in the target table, performs UPDATE.
- `DELETE`: Records the deleted row. When a matching row exists in the target table, performs DELETE.
- `INSERT`: Records newly inserted rows. When the row does not exist in the target table, performs INSERT.
- `UPDATE_BEFORE`: Records the old values before an update. No separate handling is needed -- when there is no corresponding WHEN clause, MERGE automatically ignores the row.

This is the standard approach for consuming STANDARD mode Table Streams. See the [Table Stream documentation](table_stream.md) for details.

## Related Guides

- [Upsert Guide](SQL_Upsert_Guide.md): Complete MERGE usage scenarios, including INSERT-only, UPDATE-only, and conditional UPSERT examples.
- [Table Stream Change Data Capture](SQL_Table_Stream_Guide.md): Writing to a target table with MERGE when consuming incremental Stream data.
- [SQL DML Guide](SQL_DML_Considerations.md): Notes and best practices for INSERT/UPDATE/DELETE/MERGE.
