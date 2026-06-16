# View Share List

## Description

The view share list is used to query all share objects under the current instance, helping users understand the data sharing situation between the current service instance and other service instances.

## Syntax

```SQL
SHOW SHARES  [LIKE 'pattern' | WHERE expr] [LIMIT num]
```

## Parameters

1. `LIKE pattern`: This option is optional and is used to filter by object name. It supports case-insensitive pattern matching and can use SQL wildcards `%` (represents any number of characters) and `_` (represents a single character). Example: `LIKE '%testing%'`. Note that this filter cannot be used together with a `WHERE` condition.

2. `WHERE expr`: This option is optional and supports filtering based on the fields displayed by the `SHOW SHARES` command, such as: provider, provider\_instance, provider\_workspace, scope, to\_instance, kind

## Return Columns

* **share\_name**: The name of the share object.
* **provider**: The tenant name of the share provider, indicating the source of the shared data.
* **provider\_instance**: The service instance name of the share provider, indicating the service instance of the shared data.
* **provider\_workspace**: The workspace to which the share belongs, indicating the workspace where the share object is located.
* **scope**: The sharing scope of the share, currently only supports PRIVATE -- specified instance sharing. Indicates that the share object is only shared between specified service instances.
* **to\_instance**: The names of the service instances to which the share object is specified to be shared, separated by commas (,). Indicates which service instances the current share object is shared with.
* **kind**: The type of share, OUTBOUND for data shared out from the current service instance, INBOUND for data shared to the current service instance from other service instances. Indicates whether the current share object is the source of the shared data or the destination for receiving data.

## Examples

1. Query all share objects under the current service instance:

   ```SQL
   SHOW SHARES ;
   ```

   Assume the return result is as follows:

   ```
   share_name |provider| provider_instance | provider_workspace | scope | to_instance | kind 
   -----------------------+-------------------+--------------------+-------+---------------+-----
   sample_data |my_tenant | my_service_instance | my_workspace       | PRIVATE | other_instance | OUTBOUND
   another_demo |another_tenant | another_service_instance | another_workspace  | PRIVATE | my_service_instance | INBOUND
   ```

   In this example, we can see that the current service instance has two share objects. The first object is shared by the current service instance to a service instance named other\_instance, with a sharing scope of PRIVATE. The second object is a share from another service instance, with the current service instance as the recipient.

2. Use the **Like** parameter to filter share objects by specific name:

   ```SQL
   SHOW SHARES LIKE '%data';
   ```

   Assume the return result is as follows:

   ```
   share_name |provider| provider_instance | provider_workspace | scope | to_instance | kind 
   -----------------------+-------------------+--------------------+-------+---------------+-----
   sample_data |my_tenant | my_service_instance | my_workspace       | PRIVATE | other_instance | OUTBOUND

   ```

3. Use the **WHERE** parameter to filter output results and query the share objects **shared out** from the current service instance:

   ```SQL
   SHOW SHARES WHERE kind = 'OUTBOUND';
   ```

   Assume the return result is as follows:

   ```
   share_name | provider | provider_instance | provider_workspace | scope | to_instance | kind 
   -----------------------+-------------------+--------------------+-------+---------------+-----
   sample_outbound_share |my_tenant | my_service_instance | my_workspace| PRIVATE | other_instance | OUTBOUND
   ```

   As you can see, the current service instance has shared a share object named sample\_outbound\_share with a service instance named other\_instance.

4. Use the **WHERE** parameter to filter output results and query the share objects **shared to** the current service instance:

```SQL
   SHOW SHARES WHERE kind = 'INBOUND';
```

   Assume the return result is as follows:

```
share_name | provider | provider_instance | provider_workspace | scope | to_instance | kind 
-----------------------+-------------------+--------------------+-------+---------------+-----
sample_inbound_share |other_tenant | other_instance | demo_workspace| PRIVATE | current_instance | INBOUND
```

   As you can see, the current service instance has been shared a share object named sample\_inbound\_share from a service instance named other\_instance.

With the above examples, you can more easily view and manage all share objects under the current service instance.
