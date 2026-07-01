# Seedance Video Generation

This guide shows how to call Volcengine Seedance video generation models using async tasks, covering text-to-video, image-to-video, and task querying.

## 1. Seedance video generation

Applicable models:

- `doubao-seedance-2.0`
- `doubao-seedance-2.0-fast`
- `doubao-seedance-1.5-pro`
- `doubao-seedance-1.0-pro`
- `doubao-seedance-1.0-pro-fast`

Seedance uses async task endpoints.

```text
POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/contents/generations/tasks
```

### Text-to-video

```bash
curl -X POST "$AI_GATEWAY_VOLC_BASE_URL/contents/generations/tasks" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seedance-2.0",
    "content": [
      {
        "type": "text",
        "text": "Generate a 5-second video: at night in a city, data streams flow from different systems into AI Gateway and are routed by policy. Clean, professional, tech aesthetic."
      }
    ],
    "ratio": "16:9",
    "duration": 5,
    "resolution": "720p",
    "watermark": false
  }'
```

### Image-to-video

```bash
curl -X POST "$AI_GATEWAY_VOLC_BASE_URL/contents/generations/tasks" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seedance-2.0",
    "content": [
      {
        "type": "text",
        "text": "Slowly rotate the product in the image, keep the background clean, and push the camera slightly forward."
      },
      {
        "type": "image_url",
        "image_url": {
          "url": "https://example.com/first-frame.png"
        }
      }
    ],
    "ratio": "adaptive",
    "duration": 5,
    "resolution": "720p",
    "watermark": false
  }'
```

### Video generation request fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | string | Yes | Seedance model name. |
| `content` | array | Yes | Multimodal input array. Common elements include text and images. |
| `content[].type` | string | Yes | Content type: `text` or `image_url`. Seedance 2.0 may support more modalities; check the model detail page. |
| `content[].text` | string | Conditionally required | Text prompt. |
| `content[].image_url.url` | string | Conditionally required | Image URL. |
| `ratio` | string | No | Aspect ratio: `16:9`, `9:16`, `1:1`, `4:3`, `3:4`, `21:9`, or `adaptive`. |
| `duration` | integer | No | Video duration in seconds. Supported range depends on model version. |
| `resolution` | string | No | Resolution: `480p`, `720p`, or `1080p`. |
| `seed` | integer | No | Random seed. |
| `watermark` | boolean | No | Whether to add a watermark. |
| `generate_audio` | boolean | No | Whether to generate audio. Depends on model version. |
| `camera_fixed` | boolean | No | Whether to fix the camera. Depends on model version. |
| `return_last_frame` | boolean | No | Whether to return the last frame. Depends on model version. |
| `callback_url` | string | No | Callback URL when the task completes. Depends on endpoint capability. |

### Task creation response

```json
{
  "id": "cgt-xxxxxxxxxxxxxxxx",
  "model": "doubao-seedance-2.0",
  "status": "queued",
  "created_at": 1710000000
}
```

Field descriptions:

| Field | Description |
| --- | --- |
| `id` | Video generation task ID. |
| `status` | Task status. |
| `created_at` | Creation time. |

### Query task result

```bash
curl -X GET "$AI_GATEWAY_VOLC_BASE_URL/contents/generations/tasks/<TASK_ID>" \
  -H "Authorization: Bearer $API_KEY"
```

Common task statuses:

| Status | Description |
| --- | --- |
| `queued` / `PENDING` | Queued |
| `running` / `RUNNING` | Processing |
| `succeeded` / `SUCCEEDED` | Completed |
| `failed` / `FAILED` | Failed |
| `cancelled` / `CANCELED` | Cancelled |
| `expired` | Expired |

A successful response typically contains the video URL:

```json
{
  "id": "cgt-xxxxxxxxxxxxxxxx",
  "status": "succeeded",
  "content": {
    "video_url": "https://example.com/generated.mp4"
  },
  "usage": {
    "duration": 5
  }
}
```

Notes:

- Volcengine typically supports querying task records from the past 7 days only.
- Video URLs typically expire after 24 hours. Download or transfer them to your own storage promptly after generation.
- Poll at intervals of 5 to 15 seconds to avoid high-frequency queries.
- Use idempotency controls before creating tasks to avoid duplicate charges from repeated submissions.

Python polling example:

```python
import time
import requests

api_key = "<your-api-key>"
base_url = "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

payload = {
    "model": "doubao-seedance-2.0",
    "content": [
        {
            "type": "text",
            "text": "Generate a 5-second AI Gateway product demo video."
        }
    ],
    "ratio": "16:9",
    "duration": 5,
    "resolution": "720p",
    "watermark": False,
}

create_resp = requests.post(
    f"{base_url}/contents/generations/tasks",
    headers=headers,
    json=payload,
    timeout=60,
)
create_resp.raise_for_status()
task_id = create_resp.json()["id"]

for _ in range(120):
    query_resp = requests.get(
        f"{base_url}/contents/generations/tasks/{task_id}",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30,
    )
    query_resp.raise_for_status()
    task = query_resp.json()
    status = task.get("status")

    if status in ("succeeded", "SUCCEEDED"):
        print(task.get("content", {}).get("video_url"))
        break
    if status in ("failed", "FAILED"):
        raise RuntimeError(task)

    time.sleep(5)
else:
    raise TimeoutError("video generation task timeout")
```
