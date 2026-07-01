# Use Models

After selecting a model in the Model Marketplace, you can view the model's endpoint information and usage examples, and copy the code directly to start calling.

## Finding Model Endpoints

Go to the **Model Marketplace**, click on any model to enter its detail page, where you can see:

- **Endpoint Management**: Lists the available endpoint names, service providers, status, and billing information for that model
- **Model Usage Examples**: Provides curl and Python code examples that can be copied and used directly

The endpoint name format is `{provider}@{model_name}@{interface_type}`, for example:

- `aliyun_bailian_bj@qwen/qwen3.7-max@open_ai` — Alibaba Cloud Bailian-Beijing, OpenAI-compatible interface
- `aws_bedrock_us_east_1@anthropic/claude-opus-4.6@anthropic` — AWS Bedrock US-East-1, Anthropic interface

## Two Interface Formats

AI Gateway supports two calling interfaces, depending on the protocol type of the model:

| Interface Type | Path | Applicable Models |
|----------|------|----------|
| OpenAI-compatible | `/gateway/v1/chat/completions` | Qwen, DeepSeek, GLM, Kimi, Doubao, GPT, etc. |
| Anthropic-compatible | `/gateway/v1/messages` | Claude series |

## curl Calls

### OpenAI-Compatible Interface (Qwen, etc.)

```bash
curl -X POST https://cn-shanghai-alicloud-aimesh.api.clickzetta.com/gateway/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/qwen3.7-max",
    "messages": [{"role": "user", "content": "hello"}]
  }'
```

### Anthropic-Compatible Interface (Claude)

```bash
curl -X POST https://cn-shanghai-alicloud-aimesh.api.clickzetta.com/gateway/v1/messages \
  -H "x-api-key: $API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "anthropic/claude-opus-4.6",
    "messages": [{"role": "user", "content": "hello"}],
    "max_tokens": 256
  }'
```

## Python Calls

### OpenAI-Compatible Interface (Recommended)

Use the `openai` library, pointing `base_url` to the AI Gateway endpoint:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://cn-shanghai-alicloud-aimesh.api.clickzetta.com/gateway/v1",
    api_key="<your-api-key>",
)

response = client.chat.completions.create(
    model="qwen/qwen3.7-max",
    messages=[{"role": "user", "content": "hello"}],
)
print(response.choices[0].message.content)
```

### Anthropic-Compatible Interface (Claude)

Use the `requests` library to call the Anthropic Messages interface directly:

```python
import requests

url = "https://cn-shanghai-alicloud-aimesh.api.clickzetta.com/gateway/v1/messages"
headers = {
    "x-api-key": "${API_KEY}",
    "anthropic-version": "2023-06-01",
    "Content-Type": "application/json",
}
payload = {
    "model": "anthropic/claude-opus-4.6",
    "messages": [{"role": "user", "content": "hello"}],
    "max_tokens": 256,
}

resp = requests.post(url, headers=headers, json=payload, timeout=60)
print(resp.status_code)
print(resp.text)
```

You can also use the official `anthropic` SDK, replacing `base_url` with the AI Gateway address:

```python
import anthropic

client = anthropic.Anthropic(
    base_url="https://cn-shanghai-alicloud-aimesh.api.clickzetta.com/gateway/v1",
    api_key="<your-api-key>",
)

message = client.messages.create(
    model="anthropic/claude-opus-4.6",
    max_tokens=256,
    messages=[{"role": "user", "content": "hello"}],
)
print(message.content)
```

## Notes

- Endpoint addresses differ by deployment region; use the actual example code in the Model Marketplace as the reference
- OpenAI-compatible interface uses `Authorization: Bearer <key>`; Anthropic interface uses `x-api-key: <key>`
- Model names must exactly match the model identifier in the endpoint; copy from the Model Marketplace detail page
- API Keys must be created in advance in **API KEY Management** with calling permissions enabled for the corresponding model

## Related Documents

- [Quick Start](quickstart.md) — Create API Key and configure routing
- [Model Pricing](pricing-ai-gateway.md) — Billing standards for each model
- [Call LLMs in SQL](lakehouse-ai-sql-analysis.md) — Calling via AI_COMPLETE in Lakehouse SQL
