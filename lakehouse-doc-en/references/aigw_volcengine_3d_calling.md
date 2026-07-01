# 3D Generation

This guide shows how to call Volcengine Seed3D, Hyper3D, and Hitem3D 3D generation models using async tasks.

## 1. 3D generation

Applicable models:

- `doubao-seed3d-2.0`
- `Hyper3d-Gen2`
- `Hitem3d-2.0`

3D generation uses async tasks. Submitting a task returns a task ID; you query the task later to get the 3D file URL.

Request endpoint:

```text
POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/contents/generations/tasks
```

### Text-to-3D

```bash
curl -X POST "$AI_GATEWAY_VOLC_BASE_URL/contents/generations/tasks" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seed3d-2.0",
    "content": [
      {
        "type": "text",
        "text": "Generate a low-poly style tech-aesthetic robot 3D model suitable for display on a data platform product page."
      }
    ]
  }'
```

### Image-to-3D

```json
{
  "model": "Hyper3d-Gen2",
  "content": [
    {
      "type": "image_url",
      "image_url": {
        "url": "https://example.com/object.png"
      }
    }
  ]
}
```

### 3D generation request fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | string | Yes | 3D generation model name. |
| `content` | array | Yes | Input content. Can be text, images, or reference materials depending on the model. |
| `content[].type` | string | Yes | Content type: `text` or `image_url`. |
| `content[].text` | string | Conditionally required | Text description. |
| `content[].image_url.url` | string | Conditionally required | Image URL. |
| `callback_url` | string | No | Async task callback URL. Depends on endpoint capability. |

### Query a 3D task

```bash
curl -X GET "$AI_GATEWAY_VOLC_BASE_URL/contents/generations/tasks/<TASK_ID>" \
  -H "Authorization: Bearer $API_KEY"
```

A successful response typically contains the 3D file URL in formats such as `glb`, `obj`, `fbx`, or a compressed archive. The exact fields depend on the model response.

Notes:

- Volcengine typically supports querying task records from the past 7 days only.
- Generated 3D file URLs are typically cleaned up after 24 hours. Download them promptly.
- Different 3D models have different input methods and output file formats. Before integrating, run a minimal example to verify task creation and task querying.
