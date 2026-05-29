# **Model Pricing Overview**

AI Gateway lets you call virtually all mainstream large models on the market (Claude, GPT, Gemini, Qwen, DeepSeek, GLM, Kimi, Doubao, and more) through **a single interface and a single bill** — no need to register, integrate, or top up accounts on each provider's platform separately. The table below lists the **official list prices** for each model, organized by currency zone — domestic (CNY) and international (USD) — with a separate table per vendor for easy comparison.

---

## **Billing in Three Minutes**

**Billing dimension descriptions**

| Dimension | Description |
| --- | --- |
| Input | Unit price per prompt token in the user's request |
| Output | Unit price per token of model-generated content |
| Explicit cache write | Unit price for writing a prompt into the context cache for the first time |
| Explicit cache write · 5m / 1h | Anthropic's two cache write price tiers |
| Cache hit | Discounted price for reusing a cached prompt on subsequent requests |

Large models are not billed per call — they are billed by **the volume of text processed**, measured in units called **tokens**.

> 💡 **Tip:** How to estimate cost? Example: using a model for Q&A with 1,000 characters of input and 2,000 characters of output ≈ 1,000 input tokens + 2,000 output tokens. If the input price is ¥2/million and the output price is ¥8/million, the cost is approximately `1000÷1,000,000×2 + 2000÷1,000,000×8 = ¥0.018`.

---

## **What Is Caching and Why Does It Save Money?**

If you **repeatedly send the same opening content** (for example, the same long system prompt or the same knowledge base document every time), the model can "remember" that content and reuse it directly on subsequent calls without recomputing it — this is **caching**. The cached portion is priced far below the normal input price, resulting in significant savings.

There are two types of caching:

| Cache type | Plain-language explanation | Billing characteristics |
| --- | --- | --- |
| **Explicit cache** (manual) | You actively tell the model "store this segment." Like **renting a locker**: storing it incurs a one-time **write/create fee** (slightly above the input price); each subsequent retrieval incurs a low **hit fee**; long-term storage may also incur a **storage fee**. | Write fee + hit fee (+ storage fee) |
| **Implicit cache** (automatic) | The system **automatically** detects repeated prefixes and caches them for you — no action required. Like a **store automatically giving a discount to regular customers**: no write fee; you simply enjoy the lower price on a cache hit. | Hit fee only, no write fee |

> ⚠️ **Note:** Not every provider supports both types! This directly determines which cache columns appear in the pricing tables:

| Provider | Explicit cache | Implicit cache | Notes |
| --- | --- | --- | --- |
| **Alibaba Cloud · Qwen** | ✅ Supported | ✅ Supported | Both types, highest flexibility |
| **OpenAI · GPT** | ❌ Not supported | ✅ Supported | **Automatic implicit cache only**, no manual operation needed |
| **Anthropic · Claude** | ✅ Supported | ❌ Not supported | **Manual explicit cache only**, write available in 5-minute / 1-hour tiers |
| **Google · Gemini** | ✅ Supported | ❌ Not supported | Explicit cache, **additional hourly storage fee** |
| **DeepSeek** | Partial | Partial | v3.2 supports both; r1 / v3.1 implicit only; v4 series not yet available |
| **Zhipu · GLM** | Partial | ✅ Supported | GLM-5.1 supports both; others implicit only |
| **Moonshot · Kimi** | ✅ Supported | ✅ Supported | Both types |
| **MiniMax** | ❌ Not supported | ✅ Supported | Implicit only |
| **ByteDance · Doubao** | ✅ Supported | ✅ Supported | Explicit incurs storage fee; implicit takes effect in batch mode |

*When reading the tables: **a "Explicit·Write/Create" column = explicit cache supported; an "Implicit·Hit" column = implicit cache supported; `—` or a missing column = that model does not support that cache type.***

---

# **Domestic Zone (CNY · ¥ / million tokens)**

## **Alibaba Cloud · Qwen Series**

*> Positioning: China's all-around model, covering general conversation, coding, vision, speech, and multimodal, with a context window up to 1 million tokens. Both explicit and implicit caching are supported.*

| Model | Context window | Input | Output | Explicit·Create | Explicit·Hit | Implicit·Hit |
| --- | --- | --- | --- | --- | --- | --- |
| **qwen3.6-max-preview** (strongest) | 0–128K | 9 | 54 | 11.25 | 0.9 | — |
| | 128K–256K | 15 | 90 | 18.75 | 1.5 | — |
| **qwen3.6-plus** (flagship general) | 0–256K | 2 | 12 | 2.5 | 0.2 | — |
| | 256K–1M | 8 | 48 | 10 | 0.8 | — |
| **qwen3.6-flash** (fast & low-cost) | 0–256K | 1.2 | 7.2 | 1.5 | 0.12 | — |
| | 256K–1M | 4.8 | 28.8 | 6 | 0.48 | — |
| **qwen3.5-plus** | 0–128K | 0.8 | 4.8 | 1 | 0.08 | 0.16 |
| | 128K–256K | 2 | 12 | 2.5 | 0.2 | 0.4 |
| | 256K–1M | 4 | 24 | 5 | 0.4 | 0.8 |
| **qwen3.5-flash** | 0–128K | 0.2 | 2 | 0.25 | 0.02 | — |
| | 128K–256K | 0.8 | 8 | 1 | 0.08 | — |
| | 256K–1M | 1.2 | 12 | 1.5 | 0.12 | — |
| **qwen3-max** | 0–32K | 2.5 | 10 | 3.125 | 0.25 | 0.5 |
| | 32K–128K | 4 | 16 | 5 | 0.4 | 0.8 |
| | 128K–256K | 7 | 28 | 8.75 | 0.7 | 1.4 |
| **qwen3-coder-plus** (coding) | 0–32K | 4 | 16 | 5 | 0.4 | 0.8 |
| | 32K–128K | 6 | 24 | 7.5 | 0.6 | 1.2 |
| | 128K–256K | 10 | 40 | 12.5 | 1 | 2 |
| | 256K–1M | 20 | 200 | 25 | 2 | 4 |


## **DeepSeek Series**

*> Positioning: Known for exceptional cost-effectiveness and strong reasoning capabilities, suitable for budget-sensitive scenarios that still demand quality. Cache support varies by model version (see table below; missing columns indicate no support).*

| Model | Input | Output | Explicit·Create | Explicit·Hit | Implicit·Hit |
| --- | --- | --- | --- | --- | --- |
| **deepseek-v4-pro** (flagship) | 12 | 24 | — | — | 2.4 |
| **deepseek-v4-flash** (fast) | 1 | 2 | — | — | 0.2 |
| **deepseek-v3.2** | 2 | 3 | 2.5 | 0.2 | 0.4 |
| **deepseek-r1** (deep reasoning) | 4 | 16 | — | — | 0.8 |


## **Zhipu · GLM Series**

*> Positioning: Balanced domestic general-purpose model; GLM-5 series is the new flagship generation. Most versions support implicit cache only; GLM-5.1 additionally supports explicit cache.*

| Model | Context window | Input | Output | Explicit·Create | Explicit·Hit | Implicit·Hit |
| --- | --- | --- | --- | --- | --- | --- |
| **glm-5.1** (flagship) | 0–32K | 6 | 24 | 7.5 | 0.6 | 1.2 |
| | 32K–200K | 8 | 28 | 10 | 0.8 | 1.6 |
| **glm-5** | 0–32K | 4 | 18 | — | — | 0.8 |
| | 32K–198K | 6 | 22 | — | — | 1.2 |
| **glm-4.7** | 0–32K | 3 | 14 | — | — | 0.6 |
| | 32K–166K | 4 | 16 | — | — | 0.8 |

## **Moonshot · Kimi Series**

*> Positioning: Excels at understanding and processing ultra-long text. Both explicit and implicit caching are supported.*

| Model | Input | Output | Explicit·Create | Explicit·Hit | Implicit·Hit |
| --- | --- | --- | --- | --- | --- |
| **kimi-k2.6** | 6.5 | 27 | 8.125 | 0.65 | 1.3 |
| **kimi-k2.5** | 4 | 21 | 5 | 0.4 | 0.8 |

## **MiniMax Series**

*> Positioning: Cost-effective general-purpose model. Implicit cache only (system discounts automatically, no action required).*

| Model | Input | Output | Implicit·Hit |
| --- | --- | --- | --- |
| **MiniMax-M2.7** | 2.1 | 8.4 | 0.42 |
| **MiniMax-M2.5** | 2.1 | 8.4 | 0.42 |


## **Volcano Engine (Doubao)**

*> Positioning: China's high-value all-in-one suite, covering text, vision, video, images, and 3D. Explicit cache (additional storage fee of ¥0.017/million token·hour) and implicit cache (effective in batch mode) are both supported. The table below shows standard "online inference" prices; Doubao also offers approximately 50% off for batch inference.*

| Model | Context window | Input | Output | Explicit·Hit |
| --- | --- | --- | --- | --- |
| **doubao-seed-2.0-pro** (flagship) | [0, 32K] | 3.2 | 16 | 0.64 |
| | (32K, 128K] | 4.8 | 24 | 0.96 |
| | (128K, 256K] | 9.6 | 48 | 1.92 |
| **doubao-seed-2.0-code** (coding) | [0, 32K] | 3.2 | 16 | 0.64 |
| | (32K, 128K] | 4.8 | 24 | 0.96 |
| | (128K, 256K] | 9.6 | 48 | 1.92 |
| **doubao-seed-2.0-lite** | [0, 32K] | 0.6 | 3.6 | 0.12 |
| | (32K, 128K] | 0.9 | 5.4 | 0.18 |
| | (128K, 256K] | 1.8 | 10.8 | 0.36 |
| **doubao-seed-2.0-mini** (cheapest) | [0, 32K] | 0.2 | 2 | 0.04 |
| | (32K, 128K] | 0.4 | 4 | 0.08 |
| | (128K, 256K] | 0.8 | 8 | 0.16 |
| **doubao-seed-1.6** | [0, 32K] | 0.8 | 2 / 8 ※ | 0.16 |
| | (32K, 128K] | 1.2 | 16 | 0.16 |
| | (128K, 256K] | 2.4 | 24 | 0.16 |
| **doubao-seed-1.6-flash** (fast) | [0, 32K] | 0.15 | 1.5 | 0.03 |
| | (32K, 128K] | 0.3 | 3 | 0.03 |
| | (128K, 256K] | 0.6 | 6 | 0.03 |
| **doubao-seed-1.6-vision** (vision) | [0, 32K] | 0.8 | 8 | 0.16 |
| | (32K, 128K] | 1.2 | 16 | 0.16 |
| | (128K, 256K] | 2.4 | 24 | 0.16 |
| **doubao-1.5-pro-32k** | — | 0.8 | 2 | 0.16 |
| **doubao-1.5-lite-32k** | — | 0.3 | 0.6 | 0.06 |
