### CURRENT_USER 

#### Description

The `CURRENT_USER` function is used to obtain the username of the current database session. This function does not require any parameters and returns a value of string type, representing the username of the current session.

#### Syntax
```
CURRENT_USER()
```
#### Return Results

`CURRENT_USER` function returns a string representing the user name of the current database session.

####  Example

Query the user name of the current session:
```sql
SELECT CURRENT_USER();
```
After executing this query, the result may be as follows:
   ```
   user1
   ```