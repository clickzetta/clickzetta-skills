# Domestic Model Multimodal and Visual Understanding Capabilities

## Label Definitions

- **Visual Understanding = Yes**: The model can accept visual inputs such as images or video, and outputs text-based recognition, analysis, Q&A, or reasoning results.
- **Visual Understanding = Partial**: The model can process visual semantics, but the output is typically a vector or retrieval feature rather than direct natural language Q&A.
- **Visual Understanding = No**: The model covers text generation, image generation, video generation, 3D generation, or similar capabilities and is not annotated as a visual Q&A / understanding model.
- **Multimodal = Yes**: The model involves two or more input or output modalities, such as text-to-video, image-to-vector, or text/image/video-to-text.

## Model List

### Common Text Models
Language models with text input and text output, suitable for standard tasks such as conversation, writing, coding, translation, reasoning, and Agents.
| Model Name | Provider | Visual Understanding | Multimodal | Input Modalities | Output Modalities | Tags |
|---|---|---:|---:|---|---|---|
| qwen3.7-max | Alibaba Cloud / Qwen | No | No | Text | Text | Text generation, reasoning/coding, Agent |
| qwen3.6-max-preview | Alibaba Cloud / Qwen | No | No | Text | Text | Text generation, reasoning/coding, Agent |
| qwen3-max | Alibaba Cloud / Qwen | No | No | Text | Text | Text generation, reasoning/coding, Agent |
| qwen3-max-preview | Alibaba Cloud / Qwen | No | No | Text | Text | Text generation, reasoning/coding, Agent |
| doubao-seed-character | Volcengine / Doubao | No | No | Text | Text | Text generation |
| doubao-seed-code | Volcengine / Doubao | No | No | Text | Text | Text generation |
| doubao-seed-translation | Volcengine / Doubao | No | No | Text | Text | Text generation |
| doubao-seed-2.0-code | Volcengine / Doubao | No | No | Text | Text | Text generation |
| doubao-seed-1.6-lite | Volcengine / Doubao | No | No | Text | Text | Text generation |
| doubao-1.5-lite-32k | Volcengine / Doubao | No | No | Text | Text | Text generation |
| doubao-1.5-pro-32k | Volcengine / Doubao | No | No | Text | Text | Text generation |
| glm-5.2 | Zhipu AI | No | No | Text | Text | Text generation, Agent/Coding |
| glm-5.1 | Zhipu AI | No | No | Text | Text | Text generation, Agent/Coding |
| glm-5 | Zhipu AI | No | No | Text | Text | Text generation, Agent/Coding |
| glm-4.7 | Zhipu AI | No | No | Text | Text | Text generation, Agent/Coding |
| deepseek-v4-flash | DeepSeek | No | No | Text | Text | Text generation, reasoning/coding |
| deepseek-v4-pro | DeepSeek | No | No | Text | Text | Text generation, reasoning/coding |
| deepseek-v3.2 | DeepSeek | No | No | Text | Text | Text generation, reasoning/coding |
| deepseek-r1 | DeepSeek | No | No | Text | Text | Text generation, reasoning/coding |
| MiniMax-m2.7 | MiniMax | No | No | Text | Text | Text generation, Agent/Coding, tool calling |
| MiniMax-m2.5 | MiniMax | No | No | Text | Text | Text generation, Agent/Coding, tool calling |
### Multimodal / Visual Understanding Models
These models accept visual inputs such as images or video and output text-based understanding results. Suitable for visual Q&A, image-text analysis, screenshot / receipt / table recognition, and similar scenarios.
| Model Name | Provider | Visual Understanding | Multimodal | Input Modalities | Output Modalities | Tags |
|---|---|---:|---:|---|---|---|
| qwen3.7-plus | Alibaba Cloud / Qwen | Yes | Yes | Text, image, video | Text | Multimodal, visual understanding, video understanding, text generation, context |
| qwen3.6-flash | Alibaba Cloud / Qwen | Yes | Yes | Text, image, video | Text | Multimodal, visual understanding, video understanding, text generation, context |
| qwen3.6-plus | Alibaba Cloud / Qwen | Yes | Yes | Text, image, video | Text | Multimodal, visual understanding, video understanding, text generation, context |
| qwen3.5-flash | Alibaba Cloud / Qwen | Yes | Yes | Text, image, video | Text | Multimodal, visual understanding, video understanding, text generation, context |
| qwen3.5-plus | Alibaba Cloud / Qwen | Yes | Yes | Text, image, video | Text | Multimodal, visual understanding, video understanding, text generation, context |
| doubao-seed-2.0-lite | Volcengine / Doubao | Yes | Yes | Text, image, video | Text | Multimodal, visual understanding, video understanding, deep thinking, text generation |
| doubao-seed-2.0-lite (audio input) | Volcengine / Doubao | Yes | Yes | Text, image, video, audio | Text | Multimodal, visual understanding, video understanding, audio input, deep thinking, text generation |
| doubao-seed-2.0-mini | Volcengine / Doubao | Yes | Yes | Text, image, video | Text | Multimodal, visual understanding, video understanding, deep thinking, text generation |
| doubao-seed-2.0-mini (audio input) | Volcengine / Doubao | Yes | Yes | Text, image, video, audio | Text | Multimodal, visual understanding, video understanding, audio input, deep thinking, text generation |
| doubao-seed-2.0-pro | Volcengine / Doubao | Yes | Yes | Text, image, video | Text | Multimodal, visual understanding, video understanding, deep thinking, text generation |
| doubao-seed-1.8 | Volcengine / Doubao | Yes | Yes | Text, image, video | Text | Multimodal, visual understanding, video understanding, deep thinking, text generation |
| doubao-seed-1.6 | Volcengine / Doubao | Yes | Yes | Text, image, video | Text | Multimodal, visual understanding, video understanding, deep thinking, text generation |
| doubao-seed-1.6-flash | Volcengine / Doubao | Yes | Yes | Text, image, video | Text | Multimodal, visual understanding, video understanding, deep thinking, text generation |
| doubao-seed-1.6-vision | Volcengine / Doubao | Yes | Yes | Text, image, video | Text | Multimodal, visual understanding, video understanding, deep thinking, text generation |
| doubao-1.5-vision-pro | Volcengine / Doubao | Yes | Yes | Text, image, video | Text | Multimodal, visual understanding, video understanding, text generation |
| kimi-k2.6 | Moonshot AI / Kimi | Yes | Yes | Text, image, video | Text | Multimodal, visual understanding, video understanding, text generation, Agent/Coding |
| kimi-k2.5 | Moonshot AI / Kimi | Yes | Yes | Text, image | Text | Multimodal, visual understanding, text generation, Agent/Coding |
### Visual Semantic / Embedding Models
Maps text, images, or video to vectors for multimodal retrieval, similarity recall, and image-text / video search. Does not output natural language Q&A directly.
| Model Name | Provider | Visual Understanding | Multimodal | Input Modalities | Output Modalities | Tags |
|---|---|---:|---:|---|---|---|
| qwen3-vl-embedding | Alibaba Cloud / Qwen | Partial | Yes | Text, image, video | Vector | Multimodal, visual semantics, embedding, image-text/video retrieval |
| doubao-embedding-vision | Volcengine / Doubao | Partial | Yes | Text, image, video | Vector | Multimodal, visual semantics, embedding, image-text/video retrieval |
### Image, Video, and 3D Generation Models
Used for text-to-image, image-to-image, text-to-video, image-to-video, and 3D asset generation. Not annotated as visual Q&A models.
| Model Name | Provider | Visual Understanding | Multimodal | Input Modalities | Output Modalities | Tags |
|---|---|---:|---:|---|---|---|
| doubao-seedream-5.0-lite | Volcengine / Doubao | No | Yes | Text, image | Image | Multimodal, image generation, image editing, text-to-image/image-to-image |
| doubao-seedream-4.5 | Volcengine / Doubao | No | Yes | Text, image | Image | Multimodal, image generation, image editing, text-to-image/image-to-image |
| doubao-seedream-4.0 | Volcengine / Doubao | No | Yes | Text, image | Image | Multimodal, image generation, image editing, text-to-image/image-to-image |
| doubao-seed3d-2.0 | Volcengine / Doubao | No | Yes | Text, image | 3D model | Multimodal, 3D generation, text-to-3D, image-to-3D |
| doubao-seedance-2.0 | Volcengine / Doubao | No | Yes | Text, image, video, audio (requires image/video) | Video | Multimodal, video generation, text-to-video, image-to-video, video reference input, audio input |
| doubao-seedance-2.0-fast | Volcengine / Doubao | No | Yes | Text, image, video, audio (requires image/video) | Video | Multimodal, video generation, text-to-video, image-to-video, video reference input, audio input |
| doubao-seedance-2.0-mini | Volcengine / Doubao | No | Yes | Text, image, video, audio (requires image/video) | Video | Multimodal, video generation, text-to-video, image-to-video, video reference input, audio input |
| doubao-seedance-1.5-pro | Volcengine / Doubao | No | Yes | Text, image | Video | Multimodal, video generation, text-to-video, image-to-video |
| doubao-seedance-1.0-pro | Volcengine / Doubao | No | Yes | Text, image | Video | Multimodal, video generation, text-to-video, image-to-video |
| doubao-seedance-1.0-pro-fast | Volcengine / Doubao | No | Yes | Text, image | Video | Multimodal, video generation, text-to-video, image-to-video |
| happyhorse-1.0-i2v | Alibaba Cloud / HappyHorse | No | Yes | Text, image | Video | Multimodal, video generation, image-to-video |
| happyhorse-1.0-r2v | Alibaba Cloud / HappyHorse | No | Yes | Text, reference material | Video | Multimodal, video generation, reference-to-video |
| happyhorse-1.0-t2v | Alibaba Cloud / HappyHorse | No | Yes | Text | Video | Cross-modal generation, video generation, text-to-video |
| Hitem3D-2.0 | Alibaba Cloud / 3D Generation | No | Yes | Text, image | 3D model | Multimodal, 3D generation, text-to-3D, image-to-3D |
| Hyper3D-Gen2 | Alibaba Cloud / 3D Generation | No | Yes | Text, image | 3D model | Multimodal, 3D generation, text-to-3D, image-to-3D |
