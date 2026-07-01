# Volcengine Models: Overview

This guide explains the unified endpoints, model categories, and section navigation for calling Volcengine / Ark models through AI Gateway.

## 1. Endpoint overview

When calling Volcengine models through AI Gateway, use the AI Gateway endpoint and API key:

```bash
export AI_GATEWAY_VOLC_BASE_URL="https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3"
export API_KEY="<your-api-key>"
```

| Model type | Endpoint | Applicable models |
| --- | --- | --- |
| Responses API (recommended) | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/responses` | Doubao Seed text, code, translation, character, visual understanding models |
| Chat API (legacy compatibility) | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/chat/completions` | Existing workloads using Chat Completions |
| Image generation | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/images/generations` | Seedream image generation / editing models |
| Video generation | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/contents/generations/tasks` | Seedance video generation models |
| 3D generation | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/contents/generations/tasks` | Seed3D, Hyper3D, Hitem3D, and other 3D generation models |
| Multimodal embedding | `https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/api/v3/embeddings/multimodal` | `doubao-embedding-vision` |

Notes:

- Volcengine models use `/gateway/api/v3/...`.
- Alibaba Cloud Bailian, Tencent TokenHub, and other non-Volcengine text models use `/gateway/v1/...`. Do not mix them.
- HappyHorse video generation is an Alibaba Cloud Bailian interface at `/gateway/api/v1/services/aigc/video-generation/video-synthesis`. Do not confuse it with Seedance.
- The API key is the one created in AI Gateway, not the raw Volcengine Ark API key.
- For Volcengine text generation, visual understanding, structured output, and tool calling, use Responses API for new integrations. Use Chat API only for existing Chat Completions code compatibility.

Request headers:

```http
Authorization: Bearer <API_KEY>
Content-Type: application/json
```

## 2. Model categories

| Model type | Models |
| --- | --- |
| Text / reasoning / general conversation | `doubao-seed-2.0-pro`, `doubao-seed-2.0-lite`, `doubao-seed-2.0-mini`, `doubao-seed-1.8`, `doubao-seed-1.6`, `doubao-seed-1.6-lite`, `doubao-seed-1.6-flash`, `doubao-1.5-pro-32k`, `doubao-1.5-lite-32k` |
| Code models | `doubao-seed-2.0-code`, `doubao-seed-code` |
| Character / persona models | `doubao-seed-character` |
| Translation models | `doubao-seed-translation` |
| Visual understanding | `doubao-seed-1.6-vision`, `doubao-1.5-vision-pro` |
| Video generation | `doubao-seedance-2.0`, `doubao-seedance-2.0-fast`, `doubao-seedance-1.5-pro`, `doubao-seedance-1.0-pro`, `doubao-seedance-1.0-pro-fast` |
| Image generation | `doubao-seedream-5.0-lite`, `doubao-seedream-4.5`, `doubao-seedream-4.0` |
| 3D generation | `doubao-seed3d-2.0`, `Hyper3d-Gen2`, `Hitem3d-2.0` |
| Visual embedding | `doubao-embedding-vision` |

Model names are authoritative as shown on the **Model Market** detail page. Some Volcengine Ark model IDs may include a date suffix. AI Gateway may standardize these names. Always copy the name from Model Market.

## 3. Responses API vs Chat API

Volcengine provides both Chat API and Responses API. New integrations should prefer Responses API, because it covers a more complete set of capabilities and advanced features will be added to Responses API first.

| Capability | Chat API | Responses API |
| --- | --- | --- |
| Text generation | Supported | Supported |
| Visual understanding | Supported | Supported |
| Structured output | Beta | Beta |
| Function calling | Supported | Supported |
| Web search | Not supported | Supported |
| Image processing | Not supported | Supported |
| Knowledge search | Not supported | Supported |
| Cloud-deployed MCP | Not supported | Supported |
| Context caching | Not supported | Supported; specific model versions depend on Model Market |

Recommended strategy:

- Use Responses API by default for new workloads.
- Existing workloads using OpenAI Chat Completions can continue using Chat API and migrate to Responses API later.
- Use Responses API when you need web search, image processing, knowledge search, MCP, or context caching.
- If a model in Model Market shows only Chat examples, use Chat API and watch for Responses API support.

## 4. Section guide

| Section | Content |
| --- | --- |
| Responses API | Recommended call method; text, visual, multimodal input, streaming, structured output, tool calling, and advanced capabilities |
| Chat API compatible calls | Migration and compatibility for existing Chat Completions workloads |
| Seedream image generation | Text-to-image, reference image generation, image editing, multi-image output |
| Seedance video generation | Text-to-video, image-to-video, async tasks, polling |
| 3D generation | Text/image to 3D, async tasks, result storage |
| Multimodal embedding | Text, image, video embedding and vector store integration |
| Error troubleshooting and reference | Common errors, path troubleshooting, official reference links |
