`API Key Management` is where you create, maintain, and control the credentials used to call AI Gateway. Business systems must use an API key generated here as the authentication credential when calling AI Gateway.

### Page fields

The API key list contains the following fields:

- `Name`: The display name for the API key. Use a name that reflects the business, environment, or team.
- `API KEY`: A masked view of the key, used to identify the credential.
- `Status`: Shows whether the API key is currently enabled.
- `Quota`: Shows the tokens used and the token limit.
- `Routing Policy`: Shows the provider routing mode assigned to this API key.
- `Actions`: Supports routing policy, edit, copy, disable, delete, and view usage.

The top of the page provides filter options:

- `Status`: Filter by All, Active, or Disabled.
- `Operator`: Filter by All, current user, or a specific user.

### Create an API key

1. Go to `API Key Management`.
2. Click `New` in the upper right corner.
3. Enter the API key name in the dialog.
4. Select the quota period.
5. Enter the token quota.
6. Click `OK` to create.

Field descriptions:

- `Name`: The display name, used to distinguish business use or environment.
- `Quota Period`: Controls the period over which the token quota applies.
- `Token Quota`: The maximum number of tokens this API key can consume.

Create separate API keys for different business units and environments to simplify tracking, quota control, and troubleshooting.

### Edit an API key

Click `Edit` in the API key list to modify:

- Name
- Quota period
- Token quota

Editing does not change the key's authentication identity, but may affect quota control. Before adjusting the quota of a production API key, confirm the current call volume.

### Copy an API key

Click `Copy` to clone an existing API key and create a new one. The following settings are copied:

- Routing policy
- Quota
- Quota period

Use this when you need to quickly create a consistently configured key for a similar workload, test environment, or new team.

### Disable and delete

- `Disable`: Stops the API key. Calls using this key are affected after it is disabled.
- `Delete`: Removes the API key. Proceed with caution.

Before disabling or deleting an API key, use `View Usage` to confirm whether any active workloads still use it.

### View usage

Click `View Usage` to go to the `Usage Statistics` page filtered by that API key.

Common use cases:

- Check the call volume for a specific key.
- View token consumption trends.
- Identify abnormal requests or sudden spikes.

### Routing policy

Click `Routing Policy` in the API key row to configure how calls from this key are routed to model providers.

Three routing modes are available:

- `Default`: The system automatically ranks and calls platform built-in providers and your BYOK providers.
- `Specified Provider`: Manually select providers and drag to set priority order.
- `BYOK Only`: Uses only your BYOK keys; returns an error only when all BYOK keys are unavailable.

In default mode, three provider ranking strategies are available:

- `Price Priority`: Prefers the lowest-cost provider. If unavailable, tries providers in ascending price order. Multiple platform built-in providers at the same price are called randomly.
- `Throughput Priority`: Prefers high-throughput providers, suited for workloads that prioritize concurrency and processing capacity.
- `Latency Priority`: Prefers low-latency providers, suited for online workloads that prioritize response speed.

Default mode and specified provider mode both cover platform built-in providers and your BYOK providers. When a provider has both a BYOK key and a platform built-in option, the system prefers the BYOK key. If the BYOK call fails, it falls back to the platform built-in provider.

In specified provider mode, the order of the provider list determines call priority. Higher-priority providers are called first; when they are unavailable, the system fails over in order.

BYOK Only mode selects providers only from your BYOK keys, using list order as priority. It does not fall back to platform built-in providers. If all BYOK keys are unavailable, the call returns an error.

### Recommendations

- Use default routing for most workloads.
- Use specified provider when you have specific requirements for provider, cost, or stability.
- Use BYOK Only when the workload must use your organization's own keys.
- Use separate API keys for production and test environments.
- Do not expose the full API key in code repositories, logs, or screenshots.
