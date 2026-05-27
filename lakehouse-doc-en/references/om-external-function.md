# External Function

External Function is Lakehouse's **remote custom function**. It allows calling Python or Java code deployed on cloud function services (Alibaba Cloud FC, Tencent Cloud SCF) within SQL queries, handling complex logic that Lakehouse built-in functions cannot complete.

## Comparison with SQL Function

| Aspect | SQL Function | External Function |
|--------|-------------|-------------------|
| Implementation Language | SQL expressions | Python / Java |
| Execution Location | Inside Lakehouse engine | Remote function compute service |
| Applicable Scenarios | Simple calculations, format conversions | Complex algorithms, AI inference, calling external APIs |
| Dependency Configuration | None | Requires API Connection |

## Usage Workflow

```
1. Deploy Python/Java functions on a cloud function service
2. Create an API Connection (configure function compute service authentication)
3. Create an External Function (bind the Connection and function entry point)
4. Call it in SQL like a built-in function
```

## Create Example

```sql
-- Step 1: Create API Connection (see API Connection documentation)

-- Step 2: Create External Function
CREATE EXTERNAL FUNCTION sentiment_analysis(text STRING)
RETURNS STRING
API_INTEGRATION = my_fc_conn
AS 'https://my-fc-endpoint/sentiment';

-- Step 3: Call in SQL
SELECT order_id, sentiment_analysis(review_text) AS sentiment
FROM order_reviews;
```

## Typical Use Cases

- Call AI models for text classification, sentiment analysis, image recognition
- Complex encryption/decryption logic
- Call external APIs to fetch real-time data (exchange rates, weather, etc.)

## Related Documents

- [External Function Details](RemoteFunction-intro.md)
- [API Connection](om-api-connection.md) — configure function compute service authentication
- [Custom Function Overview](user-external-function.md)
