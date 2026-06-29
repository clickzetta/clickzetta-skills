`Usage Statistics` shows AI Gateway token consumption, request counts, and call details. The page header displays the last updated time.

### Statistics dimensions

Usage Statistics supports five dimensions:

- `Model`
- `Account`
- `API KEY`
- `User`
- `Account Details`

Each dimension suits a different analysis scenario:

- `Model`: View overall consumption by model.
- `Account`: View overall consumption at the account level.
- `API KEY`: View usage for a specific API key.
- `User`: View usage associated with a specific user.
- `Account Details`: View a more granular breakdown of call records.

### Filters

Different dimensions expose different filter options. For example:

- Model dimension: filter by model.
- API KEY dimension: filter by API key.
- User dimension: filter by user.

Time filters:

- Today
- This Week
- This Month
- Custom

### Summary metrics

The model, account, and API key summary views typically include:

- `Time`
- `Token Usage`
- `Cache Hit Tokens`
- `Cache Write Tokens`
- `Input Token Consumption`
- `Output Token Consumption`
- `Request Count`

Metric descriptions:

- `Token Usage`: Total token consumption.
- `Cache Hit Tokens`: Tokens served from cache.
- `Cache Write Tokens`: Tokens written to cache.
- `Input Token Consumption`: Input token usage.
- `Output Token Consumption`: Output token usage.
- `Request Count`: Number of requests made.

### Account details

`Account Details` provides a more granular view of call records.

Fields include:

- `Date`
- `Usage Method`
- `Endpoint`
- `Model`
- `API KEY`
- `User`
- `Usage`
- `Input`
- `Output`
- `Request Count`
- `Tags`

Account details is useful for:

- Tracing the source of usage on a specific day.
- Checking consumption by endpoint.
- Analyzing calls for a specific API key or model.
- Investigating spikes in request counts or token consumption.

### Recommendations

- Review monthly token consumption regularly.
- Watch for abnormal growth in request counts.
- Combine API key and account details views to trace business sources.
- Use the time filter to compare trends across today, this week, and this month.
- When you detect abnormal usage, first filter by API key to narrow down the source, then check account details for the specific endpoint and model.
