## AI\_EMBEDDING

Uses a supported embedding model to convert text into high-dimensional vector representations. The generated vectors can be used for downstream tasks such as semantic search, text similarity computation, cluster analysis, and recommendation systems.

### Syntax

```sql
AI_EMBEDDING(<model>, <input> [ , <model_parameters> ])
```

This function contains **2 required parameters** and **1 optional parameter**, supporting both positional and named parameter syntax.

### Parameter Description

**Required Parameters**

**`model`**

Specifies the embedding model to invoke. Consistent with `AI_COMPLETE`, models come from two sources: API Gateway Endpoints and API Connection objects.

When calling via an API Gateway endpoint, use the `endpoint` prefix followed by the endpoint name:

```scheme
'endpoint:<endpoint_name>'
```

When calling via an API Connection object, first create the connection using `CREATE API CONNECTION`, then reference it with the `connection/` prefix:

```scheme
'connection:<connection_object_name>'
```

> **Note**: Ensure the specified model is an Embedding Model, not a chat completion model. Embedding models are specifically designed to map text to fixed-dimension numerical vectors. Common embedding models include OpenAI's `text-embedding-3-small`, `text-embedding-3-large`, Alibaba Cloud Bailian's `text-embedding-v4`, and others.

**`input`**

The input text to be converted into a vector. This can be a single word, a sentence, a paragraph, or a value from a table column. The maximum length of the input text is limited by the context window of the selected model; exceeding the limit may cause text truncation or call failure.

**Optional Parameters**

**`model_parameters`**

Model hyperparameters passed in as a JSON object, used to control the behavior of the embedding model. Supported parameters may vary by model. Common parameters are as follows:

| Parameter               | Type     | Description                                                                                                                                                                                                                                                                                                                  |
| ----------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `input`                 | STRING   | Specifies the input content type. Common values are `'text'` (plain text) and `'query'` (query text). Some models perform targeted vector optimization based on input type. For example, in retrieval scenarios, using `'text'` for document content and `'query'` for user queries can improve retrieval accuracy.           |
| `dimensions`            | STRING   | Specifies the output vector dimension. Higher dimensions typically preserve richer semantic information but consume more storage space and computational resources. Common values include `'256'`, `'512'`, `'1024'`, `'1536'`, etc. The exact supported dimension range depends on the selected model.                       |

Parameter Example:

```sql
JSON '{
    "input": "text",
    "dimensions": "1024"
}'
```

### Examples

```
SELECT AI_EMBEDDING(
    'endpoint:lis_openai_embedding',
    'What is the capital of China?',
    JSON '{
        "input": "text",
        "dimensions": "1024"
    }'
);
```
