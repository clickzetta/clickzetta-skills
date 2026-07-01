# Seedream Image Generation

This guide covers the Volcengine Seedream image generation, reference image generation, and image editing interfaces.

## 1. Seedream image generation

Applicable models:

- `doubao-seedream-5.0-lite`
- `doubao-seedream-4.5`
- `doubao-seedream-4.0`

Request endpoint:

```text
POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/images/generations
```

### Text-to-image

```bash
curl -X POST "$AI_GATEWAY_VOLC_BASE_URL/images/generations" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seedream-4.0",
    "prompt": "A product illustration of a modern data platform console, clean, professional, tech aesthetic",
    "size": "2K",
    "response_format": "url",
    "watermark": false
  }'
```

### Reference image generation / image editing

Seedream supports passing a reference image in the request. Limits on the number, format, and size of reference images vary by model version. Check the model detail page.

```bash
curl -X POST "$AI_GATEWAY_VOLC_BASE_URL/images/generations" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seedream-4.5",
    "prompt": "Keep the product in the image unchanged, replace the background with a clean tech exhibition hall, and enhance the lighting.",
    "image": "https://example.com/product.png",
    "size": "2K",
    "response_format": "url",
    "watermark": false
  }'
```

### Multi-reference / multi-image output

Some Seedream models support multiple reference images and multi-image output.

```json
{
  "model": "doubao-seedream-4.0",
  "prompt": "Generate 3 e-commerce posters of the same product under morning, noon, and night lighting conditions.",
  "image": [
    "https://example.com/reference-1.png",
    "https://example.com/reference-2.png"
  ],
  "sequential_image_generation": "auto",
  "sequential_image_generation_options": {
    "max_images": 3
  },
  "size": "2K",
  "response_format": "url",
  "watermark": false
}
```

### Image generation request fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | string | Yes | Seedream model name. |
| `prompt` | string | Yes | Image generation or editing prompt. |
| `image` | string / array | No | Reference image URL or image array. Used for image-to-image, image editing, and multi-image blending. |
| `size` | string | No | Output size. Common values include `2K`, `4K`, or `1024x1024`, depending on model version. |
| `n` | integer | No | Number of output images. Some models use a multi-image parameter instead. |
| `response_format` | string | No | Return format: `url` or `b64_json`. |
| `watermark` | boolean | No | Whether to add a watermark. |
| `seed` | integer | No | Random seed to improve reproducibility. |
| `stream` | boolean | No | Whether to use streaming image generation. Depends on model capability. |
| `sequential_image_generation` | string | No | Multi-image generation mode: `auto` or `disabled`. Depends on model capability. |
| `sequential_image_generation_options.max_images` | integer | No | Maximum number of images in multi-image output. |
| `optimize_prompt_options` | object | No | Prompt optimization configuration. Supported fields depend on the model detail page. |

### Image generation response

```json
{
  "created": 1710000000,
  "model": "doubao-seedream-4.0",
  "data": [
    {
      "url": "https://example.com/generated.png",
      "size": "2048x2048"
    }
  ],
  "usage": {
    "generated_images": 1,
    "output_tokens": 12000,
    "total_tokens": 12000
  }
}
```

Recommendations:

- Returned image URLs may expire. Download and store them in your own object storage promptly in production.
- Reference image URLs must be publicly accessible and must not require browser login state.
- Image generation is typically billed per successfully generated image. Control the output count and retry count.
