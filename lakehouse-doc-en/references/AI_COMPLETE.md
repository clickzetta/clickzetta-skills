## AI\_COMPLETE

`AI_COMPLETE` is the core scalar function for generative AI tasks on the Singdata Lakehouse platform. It allows users to directly invoke large language models (LLMs) within the SQL environment, generating responses (completions) based on text prompts or multimodal inputs, thereby enabling tasks such as text completion, translation, sentiment analysis, code generation, and complex reasoning.

Singdata pushes AI computation down to the storage layer and execution engine, ensuring that data can be intelligently processed within the platform without needing to be transferred to external environments, thereby safeguarding data security while significantly reducing task latency.

Users can provide the following types of input:

* **Text Prompt**: Provide a prompt in string form, and the model generates a response. See AI\_COMPLETE (Single String).
* **Single Image and Text Prompt**: Provide one image and one text prompt, and the model generates a response based on both the image and the prompt. See AI\_COMPLETE (Single Image).

### Syntax

The function syntax depends on the type of input provided by the user:

* AI\_COMPLETE (Single String)
* AI\_COMPLETE (Single Image)

## AI\_COMPLETE (Single String)

Uses a supported language model to generate a response (completion) based on a text prompt.

### Syntax

sql

```sql
AI_COMPLETE(<model>,<prompt> [,<model_parameters>][,<response_format>][,<show_details>])
```

This function contains **2 required parameters** and **3 optional parameters**, supporting both positional and named parameter syntax.

### Parameter Description

**Required Parameters**

\`\`（STRING）

Specifies the language model to invoke. Models come from two sources: **Endpoints** in [Model Management](AI_Gateway.md) and **API Connection objects**. In the function's first parameter, different prefixes distinguish the model source.

**Source 1**: Endpoints in Model Management:

Model Management is the gateway layer for unified model service management on the Singdata Lakehouse platform. Models registered in the API Gateway can be directly referenced using the `endpoint:` prefix.

**Syntax Format**:

```scheme
'endpoint:<endpoint_name>'
```

**Usage Example**:

```sql
SELECT AI_COMPLETE('endpoint:lis_openai_llm','prompt string',GET_PRESIGNED_URL(VOLUME volume_name, '<relative_file_path>', <expiration_time>));
```

Here, the `lis_openai_llm` model management endpoint is pre-configured by the platform administrator in the API Gateway, containing information such as the model provider, model version, and authentication credentials. Regular users do not need to worry about underlying connection details and can invoke the corresponding model simply by the endpoint name.

***

**Source 2**: API Connection Objects

API Connections are model service connection objects created by users in Lakehouse, suitable for scenarios requiring custom model service addresses, authentication keys, or connections to privately deployed models. After creating a connection object via the `CREATE API CONNECTION` statement, it can be referenced in `AI_COMPLETE`.

**Create Connection Object Syntax**:

sql

```sql
CREATE API CONNECTION <connection_name>
    TYPE ai_function
    PROVIDER = '<provider_name>'
    BASE_URL = '<service_endpoint_url>'
    API_KEY = '<your_api_key>';
```

**Create Connection Object Example**:

```sql
CREATE API CONNECTION conn_bailian
    TYPE ai_function
    PROVIDER = 'bailian'
    BASE_URL = 'https://dashscope.aliyuncs.com/api/v1'
    API_KEY = 'sk-xxxxxxxxxxxxxxxxxxxxxxxx';
```

The meaning of each field is as follows:

`connection_name` is the custom name of the connection object, used to reference it in subsequent `AI_COMPLETE` calls;

`TYPE` is fixed as `ai_function`, indicating this connection is used for AI function calls;

`PROVIDER` specifies the model provider identifier, such as `'bailian'` (Alibaba Bailian), `'openai'`, `'anthropic'`, etc.;

`BASE_URL` is the API base address of the model service; `API_KEY` is the authentication key required to call the service.

***

**Referencing Connection Objects in AI\_COMPLETE**:

```sql
SELECT AI_COMPLETE('connection:conn_bailian','Please briefly introduce the basic principles of quantum computing.');
```

**Syntax Format**:

```scheme
'connection:<connection_object_name>'
```

###

### Examples

**Basic Usage: Single Text Prompt**

```
SELECT AI_COMPLETE(
    'endpoint:aliyun-qwen3max',
    'What is the capital of China?'
);

```

**Image Recognition**:

Uses a supported multimodal language model to generate a response (completion) based on a single image and text prompt. This mode is suitable for Visual Question Answering (VQA), image content description, image information extraction, OCR recognition, and other scenarios requiring the model to understand image content.

```
SELECT 
        a.id, 
        a.question,
        a.answer AS standard_answer,
        -- 1. AI-generated answer
        ai_complete(
            'endpoint:doubao-seed-2-0-pro-260215',
            JSON_OBJECT(
                'system', 'You are a VQA assistant. Answer based on the image in English. Be extremely concise (1-5 words).',
                'user', a.question,
                'images', ARRAY(CONCAT('volume://volumes/datagpt_ws/image_hub/my_images/', LPAD(CAST(a.id AS STRING), 11, '0'), '.jpg'))
            )
        ) AS ai_generated_answer,
        -- 2. Generate image preview URL
        get_presigned_url(
            VOLUME lakehouse_ai.image_hub.my_images,
            LPAD(CAST(a.id AS STRING), 11, '0') || '.jpg',
            7200  
        ) AS image_preview_url,
        -- 3. Image storage path
        CONCAT('volume://volumes/lakehouse_ai/image_hub/my_images/', LPAD(CAST(a.id AS STRING), 11, '0'), '.jpg') AS image_path
    FROM 
        lakehouse_ai.image_hub.evjvqa_annotations_20 AS a
```

Result:

![](/.topwrite/assets/ai_complete_pic.jpeg)
