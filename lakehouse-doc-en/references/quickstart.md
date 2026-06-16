# AI Gateway Quick Start

This section guides you through the complete initial setup of AI Gateway in **10 minutes** — from logging into the platform to successfully calling your first large model API.

---

## Prerequisites

Before you start using AI Gateway, make sure you have completed the following preparations:

1. You have a Singdata platform enterprise account (personal accounts cannot use the enterprise-grade AI Gateway service)
2. You have completed enterprise real-name verification
3. You have activated the AI Gateway service

---

## Log In to the Singdata Console

1. Open a browser and visit the Singdata platform official website:

   - Production address: <https://singdata.com/>

2. Click the **Login** button in the upper-right corner of the page

3. On the login page, enter your enterprise account and password, then click "Login"

4. After a successful login, the system will automatically redirect you to the **Singdata platform account home page**

![](.topwrite/assets/screenshot-20260525-221156.png)

---

## Create Your First API Key

An API Key is the unique identity credential for calling AI Gateway services. All model invocation requests must carry a valid API Key for authentication.

1. On the Singdata platform account home page, find the **AI Gateway** service card and click it to enter the product page

2. After entering the AI Gateway product interface, the system displays the **API KEY Management** page by default

3. Click the **New** button in the upper-right corner of the page

4. In the **New API KEY** dialog that appears, fill in the following information:

   - **Name**: Enter an identifying name for the API Key. The recommended naming convention is "business line - environment - purpose", for example "Customer Service - Production - General Chat"

   - **Quota period**: Select the reset cycle for the Token quota from the dropdown menu. Four options are supported:

     - Day: Token quota resets automatically at midnight every day
     - Natural week: Token quota resets automatically at midnight every Monday
     - Month: Token quota resets automatically at midnight on the 1st of each month
     - Long-term: Token quota is permanently valid and will not reset automatically; it is consumed until exhausted

   - **Token quota**: Enter the maximum number of tokens allowed to be consumed within the period

5. After confirming the information is correct, click the **Confirm** button in the lower-right corner of the dialog

6. The system will automatically generate the API Key and display it in the list. Click the **eye icon** in the API Key column to view the full key string

> ⚠️ **Note**: Never share your API Key with others, and do not hard-code it in source code or commit it to a public repository. If you discover that an API Key has been leaked, immediately revoke it in the console and generate a new one.

![](.topwrite/assets/2.jpeg)

---

## Configure a Routing Policy (Optional)

The routing policy determines which models your API Key can call and the priority order for model invocation. By default, a newly created API Key can call all built-in models provided by the platform and uses a "price priority" sorting strategy.

If you need to use a custom routing policy or BYOK models, follow these steps:

1. In the API Key list, find the API Key you just created
2. Click the **Routing Policy** button in the actions column
3. In the **Routing Policy Configuration** dialog that appears, you can configure the following:

### Option A: Use Platform Built-in Models (Default)

- **Provider scope**:

  - All providers (default): you can use all built-in models provided by the platform
  - Select specific providers: check the providers you need; only models from those providers will be available

- **Provider sorting strategy**:

  - Price priority: preferentially calls the lowest-priced available provider
  - Throughput priority: preferentially calls the highest-throughput available provider
  - Latency priority: preferentially calls the lowest-latency available provider

![](.topwrite/assets/3.png)

### Option B: Use Only Your Own BYOK Models

- Check the **Use my BYOK Key only** checkbox
- Select the BYOK Key you have already created from the dropdown list (if you have not created a BYOK Key yet, refer to the relevant documentation first)
- Once checked, this API Key can only call the BYOK models you have bound, and billing will go directly through your own provider account

4. After completing the configuration, click the **Save** button in the lower-right corner of the dialog

![](.topwrite/assets/1.jpeg)

---

## Test a Model Call

After completing the above configuration, you can use the API Key you created to call large model APIs. You can use an OpenAI or Anthropic compatible client or SDK depending on the model you choose.

Using Qwen3.6 Plus as an example, here are the two most common calling methods:

### Method 1: Call using curl

Open a terminal and run the following curl command, replacing `YOUR_API_KEY` with your actual API Key:

```bash
curl -X POST https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/qwen3.6-plus",
    "messages": [{"role":"user","content":"hello"}]
  }'
```

### Method 2: Call using Python

```python
import requests

url = "https://cn-shanghai-alicloud-aimesh.api.singdata.com/gateway/v1/chat/completions"
headers = {
    "Authorization": "Bearer ${API_KEY}",
    "Content-Type": "application/json",
}
payload = {
    "model": "qwen/qwen3.6-plus",
    "messages": [{"role": "user", "content": "hello"}],
}

resp = requests.post(url, headers=headers, json=payload, timeout=60)
print(resp.status_code)
print(resp.text)
```

### Example of a Successful Response

If the call succeeds, you will see a response similar to the following:

```json
{"text":"Hello! How can I help you today?","type":"text"}
```

---

## Related Documentation

- [AI Gateway Overview](Introduction.md) — AI Gateway feature overview and architecture
- [Model Pricing](pricing-ai-gateway.md) — Pricing and Token calculation rules for each model
- [AI-Enhanced Data Analysis: Calling LLMs in SQL](lakehouse-ai-sql-analysis.md) — Call LLMs via AI Gateway in SQL
