# HappyHorse Video Generation

HappyHorse is Alibaba Cloud Bailian's video generation model. In AI Gateway, HappyHorse uses the service-based video generation interface, not `/gateway/v1/chat/completions`.

## 1. Applicable models

| Model | Type | Description |
| --- | --- | --- |
| `happyhorse-1.0-t2v` | Text-to-video | Generates video from a text prompt. |
| `happyhorse-1.0-i2v` | Image-to-video | Generates video from a first-frame image and a text prompt. |
| `happyhorse-1.0-r2v` | Reference-to-video | Generates video using reference images, characters, or style information. |

## 2. Task submission endpoint

```text
POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v1/services/aigc/video-generation/video-synthesis
```

Request headers:

```http
Authorization: Bearer <API_KEY>
Content-Type: application/json
X-DashScope-Async: enable
```

Video generation is an async task. After submitting, the response returns a task ID. Your application then polls the task ID to check the generation status and retrieve the result.

## 3. Text-to-video

Applicable model: `happyhorse-1.0-t2v`.

```bash
curl -X POST "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v1/services/aigc/video-generation/video-synthesis" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-DashScope-Async: enable" \
  -d '{
    "model": "happyhorse-1.0-t2v",
    "input": {
      "prompt": "A 5-second enterprise AI gateway product video: data requests flow from multiple business systems into a unified gateway, then route to different models by policy. Clean, professional, tech aesthetic."
    },
    "parameters": {
      "size": "1280*720",
      "duration": 5,
      "prompt_extend": true
    }
  }'
```

## 4. Image-to-video

Applicable model: `happyhorse-1.0-i2v`.

```bash
curl -X POST "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v1/services/aigc/video-generation/video-synthesis" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-DashScope-Async: enable" \
  -d '{
    "model": "happyhorse-1.0-i2v",
    "input": {
      "prompt": "Let the data stream in the image slowly move and converge toward the AI Gateway console at the center. Camera pushes forward slightly.",
      "img_url": "https://example.com/first-frame.png"
    },
    "parameters": {
      "size": "1280*720",
      "duration": 5,
      "prompt_extend": true
    }
  }'
```

## 5. Reference-to-video

Applicable model: `happyhorse-1.0-r2v`.

Reference-to-video keeps a character, subject, or style consistent with the reference image. Field names may differ across endpoints. The following is a common pattern; use the Model Market example as the authoritative reference.

```bash
curl -X POST "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v1/services/aigc/video-generation/video-synthesis" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-DashScope-Async: enable" \
  -d '{
    "model": "happyhorse-1.0-r2v",
    "input": {
      "prompt": "Keep the product appearance from the reference image unchanged. Generate a video showing the product slowly rotating from left to right.",
      "ref_img_url": "https://example.com/reference.png"
    },
    "parameters": {
      "size": "1280*720",
      "duration": 5,
      "prompt_extend": true
    }
  }'
```

## 6. Request fields

| Field | Type | Required | Applicable models | Description |
| --- | --- | --- | --- | --- |
| `model` | string | Yes | All | Model name, for example `happyhorse-1.0-t2v`. |
| `input` | object | Yes | All | Input content object. |
| `input.prompt` | string | Yes | All | Video generation prompt describing subject, action, camera, style, and quality requirements. |
| `input.img_url` | string | Required for image-to-video | `happyhorse-1.0-i2v` | First-frame image URL. |
| `input.ref_img_url` | string | Common for reference-to-video | `happyhorse-1.0-r2v` | Reference image URL. Field name depends on the model detail page. |
| `parameters` | object | No | All | Generation parameters. |
| `parameters.size` | string | No | All | Video resolution, for example `1280*720`. Supported values depend on the model detail page. |
| `parameters.duration` | integer | No | All | Video duration, typically in seconds. Supported range depends on the model detail page. |
| `parameters.prompt_extend` | boolean | No | All | Whether to enable smart prompt expansion. |
| `parameters.seed` | integer | No | All | Random seed for reproducibility. |
| `parameters.watermark` | boolean | No | All | Whether to add a watermark. Depends on the model. |
| `parameters.fps` | integer | No | All | Frame rate. Depends on the model. |

Prompt writing tips:

- Specify the subject: what is in the scene.
- Specify the action: how the subject moves.
- Specify the camera: zoom in, zoom out, orbit, pan, fixed, and so on.
- Specify the style: realistic, product demo, 3D render, hand-drawn, tech aesthetic, and so on.
- Specify constraints: no text, no distortion, keep the subject consistent, and so on.

## 7. Task submission response

A successful submission typically returns task information.

```json
{
  "output": {
    "task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "task_status": "PENDING"
  },
  "request_id": "xxxxxxxx"
}
```

| Field | Description |
| --- | --- |
| `output.task_id` | Video generation task ID. Used to query task status. |
| `output.task_status` | Current task status: `PENDING`, `RUNNING`, `SUCCEEDED`, or `FAILED`. |
| `request_id` | Request ID for troubleshooting. |

## 8. Query task result

Video generation is async. Poll the `task_id` to get the result.

```bash
curl -X GET "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v1/tasks/<task_id>" \
  -H "Authorization: Bearer $API_KEY"
```

If the Model Market detail page provides a dedicated query example, use the query URL from that page.

Successful response typically contains the video URL:

```json
{
  "output": {
    "task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "task_status": "SUCCEEDED",
    "video_url": "https://example.com/generated-video.mp4"
  },
  "usage": {
    "video_duration": 5,
    "video_count": 1
  },
  "request_id": "xxxxxxxx"
}
```

Failed response typically contains the failure reason:

```json
{
  "output": {
    "task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "task_status": "FAILED",
    "code": "InvalidParameter",
    "message": "Invalid image url."
  },
  "request_id": "xxxxxxxx"
}
```

## 9. Polling guidance

1. Submit the video generation task.
2. Save the `task_id` and the business order ID.
3. Poll the task status every 3 to 5 seconds.
4. If the status is `SUCCEEDED`, save the video URL.
5. If the status is `FAILED`, record `code`, `message`, and `request_id`, and show the failure reason.
6. Set a maximum polling duration, for example 10 minutes, to avoid infinite waiting.

Python example:

```python
import time
import requests

api_key = "<your-api-key>"
submit_url = "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v1/services/aigc/video-generation/video-synthesis"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "X-DashScope-Async": "enable",
}

payload = {
    "model": "happyhorse-1.0-t2v",
    "input": {
        "prompt": "A 5-second enterprise AI Gateway product demo video."
    },
    "parameters": {
        "size": "1280*720",
        "duration": 5,
        "prompt_extend": True,
    },
}

submit_resp = requests.post(submit_url, headers=headers, json=payload, timeout=60)
submit_resp.raise_for_status()
task_id = submit_resp.json()["output"]["task_id"]

query_url = f"https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v1/tasks/{task_id}"

for _ in range(120):
    query_resp = requests.get(query_url, headers={"Authorization": f"Bearer {api_key}"}, timeout=30)
    query_resp.raise_for_status()
    data = query_resp.json()
    status = data.get("output", {}).get("task_status")

    if status == "SUCCEEDED":
        print(data["output"].get("video_url"))
        break
    if status == "FAILED":
        raise RuntimeError(data["output"].get("message", "video generation failed"))

    time.sleep(5)
else:
    raise TimeoutError("video generation task timeout")
```

## 10. FAQ

### Why is `X-DashScope-Async: enable` required?

Video generation takes time and runs as an async task. This header declares async mode.

### Why does image-to-video fail?

Common causes: inaccessible image URL, unsupported format, image too large, or image content violates model safety policies. Use a publicly accessible object storage URL and control image size.

### Why does the generated video not fully match the prompt?

Video generation models use probabilistic generation. Use clearer subject, action, camera, style, and negative constraints in your prompt to improve consistency.

### How do I control costs?

Video models are typically billed by duration, resolution, and model type. In production, limit `duration`, `size`, and concurrency, and monitor costs in Usage Statistics.
