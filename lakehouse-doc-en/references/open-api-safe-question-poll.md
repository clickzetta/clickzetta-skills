# SafeQuestionPoll - Poll for Question Results

Poll to query the analysis execution status and results for a specified question.

## Interface Description

After submitting a question via [Text2InsightQuery](open-api-text2insight-query), the client must call this interface in a loop to retrieve the analysis progress and final results. Each call returns all `responses` messages produced so far.

### Polling Strategy

| Parameter | Recommended Value |
|-----------|-------------------|
| Polling interval | 2 seconds |
| Single request timeout | 60 seconds |
| Total timeout | 360 seconds |

### Termination Condition

On each poll, check the `dataType` of the last message in the `responses` array. Stop polling when the value is one of the following:

- `finish` — Analysis completed normally
- `finish_stop` — User actively stopped the analysis
- `error` — Execution error occurred

## Request Method

```
POST /open/safe_question_poll?tenantId={tenantId}&userId={userId}&loginToken={loginToken}
```

> 💡 **Note**: `tenantId`, `userId`, and `loginToken` must appear **both** in the URL query parameters and in the request body. Missing query parameters will cause the request to fail.

## Request Parameters

| Parameter | Location | Type | Required | Description |
|-----------|----------|------|----------|-------------|
| tenantId | Query + Body | Integer | Yes | Tenant ID |
| userId | Query + Body | Integer | Yes | User ID |
| domainId | Body | Integer | Yes | Data domain ID |
| questionId | Body | Integer | Yes | Question ID, obtained via Text2InsightQuery |
| loginToken | Query + Body | String | Yes | Authentication Token |

## Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| success | Boolean | Whether the request was successful |
| data.responses | Array | Message list containing all messages produced during the analysis |
| data.responses[].id | String | Message ID |
| data.responses[].dataType | String | Message type, see description below |
| data.responses[].message | String | Message text content |
| data.responses[].modelRes | Object | Raw structure returned by the model |
| data.responses[].modelRes.code | Integer | Model response code |
| data.responses[].modelRes.data | Object | Business data returned by the model |

## Message Type Description (dataType)

| Type | Description | Key Fields |
|------|-------------|------------|
| message | General message; may contain knowledge details or execution logs | message, knowledgeData |
| notify | Progress notification (e.g., "Thinking") | message |
| summary | Analysis summary containing the final answer | summaryData |
| metric | Metric calculation result | message, metricDsl, physicalMetricDsl |
| echarts_plus | Chart data | message, chartType, columns, calculateSql |
| code | Code block (e.g., generated SQL) | message, codeType, code |
| finish | Analysis ended normally | message |
| finish_stop | User actively stopped | message |
| error | Execution error | message |

## Field Read Priority

Business fields in each `responses` message may appear at different levels. Read in the following priority order:

1. Top level: `response[fieldName]`
2. modelRes: `response.modelRes.data[fieldName]`
3. rawRes: parse `response.rawRes` (JSON string) and retrieve `data[fieldName]`

## Request Example

```http
POST /open/safe_question_poll
Content-Type: application/json

{
  "tenantId": 10,
  "userId": 1,
  "domainId": 106,
  "questionId": 34339,
  "loginToken": "eyJhbGciOiJIUzI1NiJ9..."
}
```

## Response Examples

### Analysis In Progress

```json
{
  "success": true,
  "data": {
    "responses": [
      {
        "id": "745601",
        "dataType": "notify",
        "message": "Thinking next step"
      }
    ]
  }
}
```

### Analysis Complete (with metric results)

```json
{
  "success": true,
  "data": {
    "responses": [
      {
        "id": "745618",
        "dataType": "message",
        "message": "Viewed knowledge details: Beijing Second-hand Housing 10-year Transaction Data",
        "modelRes": {
          "code": 200,
          "data": {
            "dataType": "message",
            "message": "Viewed knowledge details: Beijing Second-hand Housing 10-year Transaction Data",
            "knowledgeData": {
              "detailItems": [
                {
                  "id": 51,
                  "keys": "Beijing Second-hand Housing 10-year Transaction Data",
                  "value": "{\"desc\": \"If no time is explicitly specified in the question, use yesterday\", \"type\": \"time_range_func\"}",
                  "type": "TEXT"
                }
              ]
            }
          }
        }
      },
      {
        "id": "745620",
        "dataType": "metric",
        "message": "Metric: Total Transaction Amount by District in the Past 6 Years",
        "modelRes": {
          "code": 200,
          "data": {
            "dataType": "metric",
            "message": "Metric: Total Transaction Amount by District in the Past 6 Years",
            "metricDsl": "{\"useDefaultLimit\":true,\"metricId\":{\"metricType\":\"SQL_SIMPLE\",\"id\":631},\"name\":\"Total Transaction Amount by District in the Past 6 Years\"}",
            "physicalMetricDsl": "{\"useDefaultLimit\":true,\"metricId\":{\"metricType\":\"SQL_SIMPLE\",\"id\":631}}"
          }
        }
      },
      {
        "id": "745625",
        "dataType": "echarts_plus",
        "message": "Beijing Second-hand Housing Total Transaction Amount by District in the Past 6 Years (2015-2021)",
        "modelRes": {
          "code": 200,
          "data": {
            "dataType": "echarts_plus",
            "chartType": "ECHARTS",
            "columns": "District (STRING), Total Transaction Amount (10K CNY) (LONG)",
            "calculateSql": "SELECT region AS district, SUM(transaction_price) AS total_transaction_amount FROM ... GROUP BY region"
          }
        }
      },
      {
        "id": "745630",
        "dataType": "summary",
        "message": "Analysis complete",
        "modelRes": {
          "code": 200,
          "data": {
            "dataType": "summary",
            "summaryData": "**Beijing Second-hand Housing Total Transaction Amount by District in the Past 6 Years:**\n- Chaoyang District: CNY 103.49 billion\n- Haidian District: CNY 58.50 billion\n..."
          }
        }
      },
      {
        "id": "745631",
        "dataType": "finish",
        "message": "Analysis complete"
      }
    ]
  }
}
```

## Error Codes

| Error Code | Description |
|------------|-------------|
| success=false | Token is invalid, questionId does not exist, or insufficient permissions |

## Related Documentation

- [Text2InsightQuery](open-api-text2insight-query) — Previous step: submit a data analysis request
- [Understanding Response Results](open-api-response-guide) — Meaning and reading method for each message type in responses
- [Quick Start](open-api-quick-start) — Complete end-to-end example
