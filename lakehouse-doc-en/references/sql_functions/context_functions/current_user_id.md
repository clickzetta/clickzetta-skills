# CURRENT_USER_ID 

####  Description
The `CURRENT_USER_ID` function is used to obtain the ID of the current database session user. This function can help you quickly understand the identity of the user performing the operation, thereby enabling permission control or other related operations.

#### Usage
The `CURRENT_USER_ID` function does not require any parameters. You simply call this function in an SQL query, and it will return the ID of the current session user.

#### Return Result
The return value type is an integer (int), representing the ID of the current session user.

####  Example

1. Query the current user's ID and display the result:

```sql
SELECT CURRENT_USER_ID();
```
After executing the above query, you will see an output similar to the following, indicating the ID of the current session user:
```
123
```