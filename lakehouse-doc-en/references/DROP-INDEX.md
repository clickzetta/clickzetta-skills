# Delete BLOOMFILTER Index

## Description
Delete Index

## Syntax
```
DROP INDEX [IF EXISTS] index_name;
```
Parameter Description:
- `DROP INDEX`: Keyword to delete the index.
- `IF EXISTS`: Optional parameter, no error is reported if the specified index does not exist.
- `index_name`: The name of the BLOOMFILTER index to be deleted.

## Usage Example

Example 1: Delete the BLOOMFILTER index named `bf_index`
```
DROP INDEX bf_index;
```
Example 2: Delete the BLOOMFILTER index named `bf_index`, do not report an error if it does not exist
```
DROP INDEX IF EXISTS bf_index;
```
## Notes
- Deleting an index will not immediately free up the storage occupied by the index. Subsequent new data will not build the index.