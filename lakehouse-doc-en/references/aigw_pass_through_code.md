---
title: AI Gateway Error Codes
description: Unified error response structure, error codes, upstream retry history, and troubleshooting for AI Gateway
---

# Error Codes

This page explains the unified error structure and error codes returned when an AI Gateway request fails. Regardless of whether the error originates on the gateway side or the upstream model provider side, AI Gateway always returns a consistent JSON structure so that your application can identify and handle errors automatically.

> Error codes such as `GATEWAY_MISSING_VIRTUAL_KEY` are fixed English identifiers. Use error codes as the basis for programmatic handling rather than relying on the error message text.

## 1. Error response structure

All errors return an `error` object:

```json
{
  "error": {
    "code": "GATEWAY_MISSING_VIRTUAL_KEY",
    "message": "[G2] Virtual key not provided. path=/v1/chat/completions, requestId=req-abc",
    "source": "gateway",
    "retry_history": null
  }
}
```

Field descriptions:

| Field | Description |
| --- | --- |
| `code` | Machine-readable error code. Use this for programmatic handling. |
| `message` | Human-readable description, usually including `requestId` and other diagnostic info. The `[G2]` prefix is an internal tracking tag and can be ignored. |
| `source` | Error origin. `gateway` means the request was intercepted before reaching any model. `upstream` means the request was forwarded but all upstream endpoints failed. |
| `retry_history` | Present when `source = upstream`, listing each upstream attempt in order. Otherwise usually `null`. |

## 2. Locate the problem

Check the `source` field first:

| source | Meaning | Where to look |
| --- | --- | --- |
| `gateway` | The request was intercepted at the AI Gateway level before being forwarded to any model provider. | Check API key, quota, request path, model name, and routing configuration. |
| `upstream` | The request was forwarded to one or more provider endpoints, but all failed. | Review `retry_history` for the status code and upstream response body of each attempt. |

## 3. Retry guidance

| HTTP Status | Meaning | Retry? |
| --- | --- | --- |
| `400` | Bad request: incorrect format, path, model, or routing parameters | Do not retry without fixing the request first |
| `401` | Authentication failure | Do not retry; check the API key |
| `403` | Billing, quota, or permission issue | Do not retry; resolve the billing, permission, or quota issue first |
| `429` | Request rate or concurrency limit exceeded | Retry with exponential backoff and reduced concurrency |
| `500` | Internal gateway error | Retry after a delay; contact support if the error persists |
| `502` | All upstream endpoints failed | Retry after a delay; check `retry_history` if the error persists |

## 4. Gateway errors

These errors occur before the request is forwarded to any model. `source` is typically `gateway`.

### Authentication and keys

| Error Code | HTTP | Description | Resolution |
| --- | --- | --- | --- |
| `GATEWAY_MISSING_VIRTUAL_KEY` | 401 | No virtual key was provided in the request. | Add `Authorization: Bearer <API_KEY>` or `x-api-key: <API_KEY>` to the request header. |
| `GATEWAY_INVALID_VIRTUAL_KEY` | 401 | The provided virtual key does not exist or has an invalid format. | Verify the API key and confirm it was created in AI Gateway. |
| `GATEWAY_VIRTUAL_KEY_DISABLED` | 401 | The virtual key exists but is disabled. | Enable the key in `API Key Management`, or use a different active key. |

### Billing and quota

| Error Code | HTTP | Description | Resolution |
| --- | --- | --- | --- |
| `GATEWAY_TENANT_OVERDUE` | 403 | The tenant account has an outstanding balance and calls are suspended. | Clear the outstanding balance to restore service. |
| `GATEWAY_TENANT_OVER_QUOTA` | 403 | The tenant has exceeded the usage quota for the current billing period. | Wait for the next period, reduce call volume, or request a quota increase. |

### Routing and configuration

| Error Code | HTTP | Description | Resolution |
| --- | --- | --- | --- |
| `GATEWAY_MISSING_ACTUAL_PATH` | 400 | The gateway cannot parse a forwarding path from the request URL. | Confirm the request URL matches the gateway address format; check for missing or duplicated path segments. |
| `GATEWAY_MODEL_NOT_RESOLVED` | 400 | The gateway cannot determine which model to route from the request body. | Confirm the request body contains a valid `model` field. |
| `GATEWAY_NO_UPSTREAM_CANDIDATES` | 400 | No available upstream endpoints exist for the requested model and protocol combination. | Check the model name, model type, provider endpoints, and routing policy. |

### Internal errors

| Error Code | HTTP | Description | Resolution |
| --- | --- | --- | --- |
| `GATEWAY_INTERNAL_ENDPOINTS_BAD_REQUEST` | 400 | A required field is missing when calling an internal endpoint. | End users should not encounter this. If you do, contact support. |
| `GATEWAY_INTERNAL_API_EXCEPTION` | 500 | An unexpected error occurred in the gateway's internal API. | Retry; contact support with the `requestId` if the error persists. |

## 5. Upstream errors

These errors occur after the request is forwarded to one or more model endpoints, but all attempts failed. `source` is typically `upstream`.

| Error Code | HTTP | Description | Resolution |
| --- | --- | --- | --- |
| `UPSTREAM_ALL_FAILED` | 502 | All candidate upstream endpoints returned an error or were unreachable. | Review `retry_history` for the provider, status code, and raw error body of each attempt. |

## 6. retry_history structure

When `UPSTREAM_ALL_FAILED` is returned, the response includes a `retry_history` array listing each upstream attempt in order.

```json
{
  "error": {
    "code": "UPSTREAM_ALL_FAILED",
    "message": "[G2] Upstream failed. path=/v1/chat/completions, requestId=req-abc, virtualKey=vk-xxx, tenantId=123",
    "source": "upstream",
    "retry_history": [
      {
        "endpoint_id": 101,
        "slug_name": "aliyun-bailian/qwen3.7-max",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_key_alias": "prod-bailian-key",
        "provider": "aliyun-bailian",
        "model": "qwen3.7-max",
        "status": 429,
        "body": "{\"message\":\"Too many requests\"}"
      },
      {
        "endpoint_id": 202,
        "slug_name": "volcengine/doubao-seed-2.0-pro",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "api_key_alias": "prod-ark-key",
        "provider": "volcengine",
        "model": "doubao-seed-2.0-pro",
        "status": 500,
        "body": "{\"error\":{\"message\":\"Internal server error\"}}"
      }
    ]
  }
}
```

Field descriptions:

| Field | Description |
| --- | --- |
| `endpoint_id` | Internal identifier of the endpoint. |
| `slug_name` | Provider and model identifier for this endpoint. |
| `base_url` | The upstream base URL used for this attempt. |
| `api_key_alias` | The alias of the API key used for this call. |
| `provider` | Provider identifier. |
| `model` | The model identifier used for this attempt. |
| `status` | HTTP status code returned by the upstream. |
| `body` | Raw upstream error response, may be truncated. |

When investigating, focus on:

- `provider`: Which provider failed.
- `model`: Whether it is the expected model.
- `status`: Whether the failure is rate limiting, authentication, bad parameters, or a service error.
- `body`: The raw upstream error message.

## 7. Common troubleshooting scenarios

### 1. Missing or invalid API key

Symptoms:

- HTTP status `401`.
- `code` is `GATEWAY_MISSING_VIRTUAL_KEY`, `GATEWAY_INVALID_VIRTUAL_KEY`, or `GATEWAY_VIRTUAL_KEY_DISABLED`.

Resolution:

- Check that the request header includes `Authorization: Bearer <API_KEY>`.
- Confirm the API key is from AI Gateway, not a raw provider key.
- Go to `API Key Management` and confirm the key is enabled.

### 2. Incorrect model name

Symptoms:

- HTTP status `400`.
- `code` may be `GATEWAY_MODEL_NOT_RESOLVED` or `GATEWAY_NO_UPSTREAM_CANDIDATES`.

Resolution:

- Copy the model name from the model detail page in Model Market.
- Do not guess provider model IDs.
- Verify that the endpoint type matches the model's capabilities; for example, do not call a text model with an image generation endpoint.

### 3. BYOK misconfiguration

Symptoms:

- In default or specified provider mode, the system may try BYOK first and fall back to the platform built-in provider.
- In BYOK Only mode, a direct error is returned when all BYOK endpoints fail.

Resolution:

- Go to `BYOK` and verify that the provider key is valid.
- Confirm that the provider account has the target model enabled.
- If falling back is acceptable, switch from `BYOK Only` to default or specified provider mode.

### 4. Upstream rate limiting

Symptoms:

- HTTP status may be `429` or the final response is `UPSTREAM_ALL_FAILED`.
- `retry_history[].status` contains `429`.

Resolution:

- Reduce concurrency.
- Retry with exponential backoff.
- Adjust the routing policy to add more available providers.
- Contact your administrator to increase the provider quota.

### 5. Duplicate async task submissions

Symptoms:

- Video, image, or 3D generation tasks are submitted multiple times, causing duplicate charges or duplicate results.

Resolution:

- Add idempotency keys on the client side.
- Reuse existing tasks when users click multiple times.
- Do not blindly retry task creation endpoints.

## 8. Troubleshooting checklist

When you encounter an error, work through the following steps:

1. Read `error.code` to determine the error category.
2. Check `source` to determine whether the problem is on the gateway or upstream.
3. If `gateway`: check the API key, quota, model name, endpoint path, and routing policy.
4. If `upstream`: review `retry_history` for the `provider`, `model`, `status`, and `body` of each attempt.
5. Based on the HTTP status, determine whether retrying is appropriate.
6. If you need to contact support, provide the `requestId`, API key name, model name, request time, and error response.
