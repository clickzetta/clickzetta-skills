# CreateSession - Create a Conversation Session

Create a new conversation session (Session) to organize one or more question-and-answer interactions.

## Interface Description

A Session represents a conversation context. After creation, a `sessionId` is returned. Subsequent question requests must be associated with a Session.

If the client already has a reusable `sessionId`, this step can be skipped and a question can be submitted directly.

### Usage Notes

- A single Session can contain multiple questions.
- A Session can be reused multiple times; you do not need to create a new one for every question.

## Request Method

```
POST /open/session/safe_new?tenantId={tenantId}&userId={userId}&loginToken={loginToken}
```

> 💡 **Note**: `tenantId`, `userId`, and `loginToken` must appear **both** in the URL query parameters and in the request body. Missing query parameters will cause the request to fail.

## Request Parameters

| Parameter | Location | Type | Required | Description |
|-----------|----------|------|----------|-------------|
| tenantId | Query + Body | Integer | Yes | Tenant ID |
| userId | Query + Body | Integer | Yes | User ID |
| domainId | Body | Integer | Yes | Data domain ID, corresponding to a dataset |
| title | Body | String | No | Session title, used to identify the Session |
| loginToken | Query + Body | String | Yes | Authentication Token obtained via GenerateAuthToken |

## Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| success | Boolean | Whether the request was successful |
| data | Integer | The sessionId of the newly created session |

## Request Example

```http
POST /open/session/safe_new
Content-Type: application/json

{
  "tenantId": 10,
  "userId": 1,
  "domainId": 106,
  "title": "Q1 Sales Analysis",
  "loginToken": "eyJhbGciOiJIUzI1NiJ9..."
}
```

## Response Example

Successful response:

```json
{
  "success": true,
  "data": 4729
}
```

The value `4729` in `data` is the newly created `sessionId`.

## Error Codes

| Error Code | Description |
|------------|-------------|
| success=false | Token is invalid, parameters are missing, or insufficient permissions |

## Related Documentation

- [GenerateAuthToken](open-api-generate-auth-token) — Previous step: obtain authentication Token
- [Text2InsightQuery](open-api-text2insight-query) — Next step: submit a data analysis request
- [Quick Start](open-api-quick-start) — Complete end-to-end example
