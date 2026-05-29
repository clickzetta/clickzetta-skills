# current_vcluster 

####  Description
The `current_vcluster` function is used to obtain the name of the computing cluster currently being used by the session. This function does not require any parameters and returns a string indicating the computing cluster being used by the current session.

#### Usage Scenarios
In an environment with multiple computing clusters, understanding which computing cluster is being used by the current session is crucial for managing and optimizing resource allocation. By using the `current_vcluster` function, users can easily query and switch the computing cluster used by the current session.

#### Example
Here is an example of using the `current_vcluster` function:

1. Query the computing cluster used by the current session:
```sql
SELECT current_vcluster();
```
After executing the above query, the returned result may be as follows:
```
default
```
2. Switch computing clusters and query:
```sql
USE VCLUSTER test; -- Switch to the compute cluster named test
SELECT current_vcluster();
```
After executing the above query, the returned result may be as follows:
```
test
```
3. Switch between different computing clusters and observe the return value of the `current_vcluster` function:
```sql
-- Switch to the computing cluster named dev
USE VCLUSTER dev;
SELECT current_vcluster();

-- Switch back to the default computing cluster
USE VCLUSTER default;
SELECT current_vcluster();
```