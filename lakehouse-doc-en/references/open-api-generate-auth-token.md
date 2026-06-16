# GenerateAuthToken - Obtain Authentication Token

Obtain an authentication Token for subsequent API calls using an application secret key (appSecretKey).

## Interface Description

Before calling any business interface in Open Text2Insight, you must first use this interface to obtain a login Token. This Token serves as the identity credential for all subsequent requests.

### Usage Notes

- The appSecretKey is generated and distributed by the platform administrator in the backend.
- The Token has an expiration time; you must obtain a new one after it expires.
- Keep your appSecretKey secure to prevent leakage.

## Request Method

```
GET /open/api/v1/appSecretKey/generateAuthToken
```

## Request Parameters

| Parameter | Location | Type | Required | Description |
|-----------|----------|------|----------|-------------|
| appSecretKey | Query | String | Yes | Application secret key, assigned by the administrator |

## Response Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| success | Boolean | Whether the request was successful |
| data.token | String | Authentication Token, used for subsequent interface calls |

## Request Example

```http
GET /open/api/v1/appSecretKey/generateAuthToken?appSecretKey=your_secret_key_here
```

## Response Example

Successful response:

```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiJ9..."
  }
}
```

## Error Codes

| Error Code | Description |
|------------|-------------|
| success=false | appSecretKey is invalid or has expired |

## Related Documentation

- [Open API Overview](open-api-overview) — Interface list and general description
- [Quick Start](open-api-quick-start) — Complete call flow after obtaining the Token
- [CreateSession](open-api-create-session) — Next step: create a session using the Token
