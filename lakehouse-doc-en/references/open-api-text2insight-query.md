# Text2InsightQuery - Submit a Data Analysis Request

Submit a natural language question to Analytics Agent to initiate a data analysis task.

## Interface Description

This interface is asynchronous. Upon a successful call, it returns a `questionId` and an initial status of `running`, indicating that the analysis task has started. The client must poll for analysis results via the [SafeQuestionPoll](open-api-safe-question-poll) interface.

### Usage Notes

- Questions are described in natural language; the Agent will automatically understand and perform the analysis.
- Supports specifying the model to use via `modelSettings`.
- Multiple questions can be submitted consecutively within the same Session, and the Agent retains conversational context.

### Usage Recommendations

- Make question descriptions as clear and specific as possible, including key information such as time ranges and dimensions.
- If you need the knowledge base to assist with the analysis, you can prompt the Agent in the question to consult the knowledge base.

## Request Method

```
POST /open/text2insight/query?tenantId={tenantId}&userId={userId}&loginToken={loginToken}
```

> 💡 **Note**: `tenantId`, `userId`, and `loginToken` must appear **both** in the URL query parameters and in the request body. Missing query parameters will cause the request to fail.

## Request Parameters

| Parameter | Location | Type | Required | Description |
|-----------|----------|------|----------|-------------|
| tenantId | Query + Body | Integer | Yes | Tenant ID |
| userId | Query + Body | Integer | Yes | User ID |
| domainId | Body | Integer | Yes | Data domain ID |
| sessionId | Body | Integer | Yes | Conversation session ID, obtained via CreateSession or reusing an existing value |
| msg | Body | String | Yes | Question content, an analysis request described in natural language |
| loginToken | Query + Body | String | Yes | Authentication Token |
| modelSettings | Body | Object | No | Model configuration |
| modelSettings.model_name | Body | String | No | Specify the model name to use |

## Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| success | Boolean | Whether the request was successful |
| data.questionId | Integer | Question ID, used for subsequent polling and stop operations |
| data.sessionId | Integer | Session ID |
| data.status | String | Current status; initial value is `running` |

## Request Example

```http
POST /open/text2insight/query
Content-Type: application/json

{
  "tenantId": 10,
  "userId": 1,
  "domainId": 106,
  "sessionId": 4729,
  "msg": "Show me the second-hand housing sales in Beijing over the past 6 years, broken down by district",
  "loginToken": "eyJhbGciOiJIUzI1NiJ9...",
  "modelSettings": {
    "model_name": "qwen/qwen3.6-plus"
  }
}
```

## Response Example

Successful response:

```json
{
  "success": true,
  "data": {
    "questionId": 34339,
    "sessionId": 4729,
    "status": "running"
  }
}
```

## Next Steps

After a successful request, use the returned `questionId` to call [SafeQuestionPoll](open-api-safe-question-poll) and poll until the analysis is complete.

## Error Codes

| Error Code | Description |
|------------|-------------|
| success=false | Token is invalid, Session does not exist, parameters are missing, or model is unavailable |

## Related Documentation

- [CreateSession](open-api-create-session) — Previous step: create a conversation session
- [SafeQuestionPoll](open-api-safe-question-poll) — Next step: poll for analysis results
- [Understanding Response Results](open-api-response-guide) — Message type descriptions and display recommendations
- [Quick Start](open-api-quick-start) — Complete end-to-end example
