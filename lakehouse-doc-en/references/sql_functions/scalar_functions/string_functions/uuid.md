### UUID 

####  Description
The `uuid()` function is used to generate a unique identifier (UUID) that conforms to the UUIDv4 standard. UUID (Universally Unique Identifier) is a standard used in computer systems to ensure global uniqueness. UUIDv4 is generated based on random or pseudo-random numbers, so each call to this function will produce a different result.

#### Syntax
```
uuid()
```
#### Parameters
None

#### Return Result
Returns a string type UUID.

#### Usage Example
1. Generate a UUID and display the result:
```sql
SELECT uuid();
```
 result
```
4d275467-77ee-427f-9d4e-f55078c6b4df
```


2. Used to generate a new associated UUID when updating records:
```sql
UPDATE example_table SET related_id = uuid() WHERE id = 'existing_id';
```
This will generate a new `related_id` for the record in the `example_table` table with the specified `existing_id`.

#### Notes
- UUIDv4 is generated based on random numbers, so it has a high degree of uniqueness, but in some cases, there is still an extremely low probability of duplication.
- The generation of UUIDs may be affected by the quality of the system's random number generator, so it is important to ensure the security and reliability of the system's random number generator during use.

By using the `uuid()` function, you can easily generate unique identifiers in database operations, ensuring the uniqueness and consistency of the data.