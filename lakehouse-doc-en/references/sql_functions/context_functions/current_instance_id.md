# CURRENT_INSTANCE_ID 

#### Description
The `CURRENT_INSTANCE_ID()` function is used to obtain the unique identifier (ID) of the instance associated with the current session. This function is particularly important in distributed database systems as it helps users identify and track the instance where the current operation is taking place.

#### Usage
The `CURRENT_INSTANCE_ID()` function does not require any input parameters and can be called directly. The return value is an integer (int) representing the ID of the instance associated with the current session.

#### Example
Here are some examples of using the `CURRENT_INSTANCE_ID()` function:

. Get the current instance ID during a query:

   ```sql
   SELECT current_instance_id();
   ```
After executing the above query, the instance ID associated with the current session will be returned, for example: `123`.