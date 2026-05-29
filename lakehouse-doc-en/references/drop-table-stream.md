# Delete Table Stream Command

## Description

Delete an existing Table Stream and release related resources.

## Syntax
```SQL
DROP TABLE STREAM [IF EXISTS] stream_name;
```
* `stream_name`: The name of the Table Stream to be deleted.


## Example

1. Delete the Table Stream named `rc3.igs_test_upsert02_stream`:
```SQL
DROP TABLE STREAM IF EXISTS rc3.igs_test_upsert02_stream;
```
2. Delete the Table Stream named `my_stream`, regardless of whether it exists:
```SQL
DROP TABLE STREAM my_stream;
```
3. Delete the Table Stream named `customer_stream` if it exists:
```SQL
DROP TABLE STREAM IF EXISTS customer_stream;
```
## Precautions

* Before deleting a Table Stream, make sure that the data in the Stream is no longer needed.
* The delete operation cannot be undone, so please proceed with caution.