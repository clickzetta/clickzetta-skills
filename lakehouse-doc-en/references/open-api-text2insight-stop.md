# Text2InsightStop - Stop a Question

Stop a data analysis task that is currently running.

## Interface Description

When an analysis task is taking too long or the user wants to interrupt the current analysis, this interface can be called to stop the execution of a specified question. After stopping, the `dataType` of the last message in the polling results will become `finish_stop`.

### Usage Notes

- Only effective for questions with a status of `running`.
- The stop operation cannot be undone.
- Intermediate results already produced are still available via the polling interface.

## Request Method

```
POST /open/text2insight/stop?tenantId={tenantId}&userId={userId}&loginToken={loginToken}
```

> 💡 **Note**: `tenantId`, `userId`, and `loginToken` must appear **both** in the URL query parameters and in the request body. Missing query parameters will cause the request to fail.

## Request Parameters

| Parameter | Location | Type | Required | Description |
|-----------|----------|------|----------|-------------|
| tenantId | Query + Body | Integer | Yes | Tenant ID |
| userId | Query + Body | Integer | Yes | User ID |
| sessionId | Body | Integer | Yes | Conversation session ID |
| questionId | Body | Integer | Yes | ID of the question to stop |
| loginToken | Query + Body | String | Yes | Authentication Token |

## Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| success | Boolean | Whether the request was successful |

## Request Example

```http
POST /open/text2insight/stop
Content-Type: application/json

{
  "tenantId": 10,
  "userId": 1,
  "sessionId": 4729,
  "questionId": 34339,
  "loginToken": "eyJhbGciOiJIUzI1NiJ9..."
}
```

## Response Example

Successful response:

```json
{
  "success": true
}
```

## Error Codes

| Error Code | Description |
|------------|-------------|
| success=false | Token is invalid, question does not exist, question has already completed, or insufficient permissions |

## Related Documentation

- [Text2InsightQuery](open-api-text2insight-query) — Submit an analysis request to obtain a questionId
- [SafeQuestionPoll](open-api-safe-question-poll) — After stopping, polling can continue; the last message dataType will be finish_stop
- [Quick Start](open-api-quick-start) — Complete end-to-end example
