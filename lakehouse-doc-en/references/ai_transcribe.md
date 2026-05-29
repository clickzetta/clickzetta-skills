# AI_TRANSCRIBE

## Overview

`AI_TRANSCRIBE` is an AI speech-to-text function provided by Singdata Lakehouse. It transcribes the content of audio files into plain text. Supports Chinese, English, and other languages. Combine it with `AI_CLASSIFY`, `AI_EXTRACT`, and other functions to build a complete pipeline: audio ingestion → transcription → AI analysis.

Singdata pushes AI computation down to the storage and execution engine layer. Data is processed intelligently within the platform without leaving the system, ensuring data security while significantly reducing task latency.

## Syntax

```sql
AI_TRANSCRIBE( <model>, <audio_url> [, <options>] )
```

## Parameters

### Required Parameters

**`model`**

Specifies the ASR model for speech-to-text. Supports two sources:

**Source 1: API Gateway Endpoint (Recommended)**

A platform administrator pre-configures model services in the API Gateway. Regular users reference them with the `endpoint:` prefix, without needing to know the underlying connection details.

```sql
'endpoint:<endpoint_name>'

-- Examples
'endpoint:qwen3-asr-flash'
'endpoint:paraformer-v2'
```

**Source 2: API Connection Object**

Users create their own connection objects via `CREATE API CONNECTION`, suitable for custom service addresses, authentication keys, or private deployment models.

```sql
-- Create a connection object
CREATE API CONNECTION conn_asr
    TYPE ai_function
    PROVIDER = 'bailian'
    BASE_URL = 'https://dashscope.aliyuncs.com/api/v1'
    API_KEY = 'sk-xxxxxxxxxxxxxxxxxxxxxxxx';

-- Reference using <connection_name>:<model_name> format
SELECT AI_TRANSCRIBE('conn_asr:paraformer-v2', GET_PRESIGNED_URL(USER VOLUME, 'audios/meeting.wav', 36000));
```

`CREATE API CONNECTION` field descriptions:

| Field | Description |
|------|------|
| `TYPE` | Fixed as `ai_function` |
| `PROVIDER` | Model provider identifier, e.g. `'bailian'`, `'openai'` |
| `BASE_URL` | Base API URL of the model service |
| `API_KEY` | Authentication key for calling the service |

**`audio_url`**

The access URL for the audio file, type STRING. Must start with `http://` or `https://`. Typically obtained from a Volume using `GET_PRESIGNED_URL()`.

```sql
GET_PRESIGNED_URL(USER VOLUME, 'audios/meeting.wav', 36000)
```

### Optional Parameters

**`options`**

JSON literal for controlling timeout and other behaviors.

| Parameter | Type | Description |
|------|------|------|
| `response.timeout` | STRING (seconds) | HTTP request timeout; set a larger value for long audio files |

```sql
JSON'{"response.timeout":"120"}'
```

## Return Value

STRING type — the plain text transcription of the audio content, without timestamps or speaker information.

## Error Behavior

| Input | Behavior |
|------|------|
| `audio_url` is `NULL` | Returns `NULL` without error |
| `audio_url` is empty string `''` | Error: `AI_TRANSCRIBE: audio_url must start with http:// or https://` |
| `audio_url` does not start with `http://` or `https://` | Error: `AI_TRANSCRIBE: audio_url must start with http:// or https://` |
| Endpoint does not exist | Error: `API request failed` |
| File download fails (e.g. URL expired) | Error: `Download multimodal file timed out` or HTTP error |

## Usage Notes

- **Supported audio formats**: WAV, MP3, FLAC, M4A. **16kHz mono WAV** is recommended — ASR models use 16kHz internally, so matching formats avoids resampling loss and gives the best recognition quality.
- **Use presigned URLs with sufficient expiry**: Set 36000 seconds (10 hours) to avoid URL expiration causing download failures during batch processing.
- **Returns plain text**: `AI_TRANSCRIBE` returns a plain text string without timestamps or speaker diarization. It can be used directly as input to `AI_CLASSIFY`, `AI_EXTRACT`, `AI_SIMILARITY`, and other functions.
- **Use REGEXP to filter in batch processing**: Use `REGEXP = '.*\.wav'` to ensure only audio files are processed, avoiding transcription requests on non-audio files.
- **Confirm files exist first**: Before batch transcription, use `SHOW USER VOLUME DIRECTORY` to confirm the file list and avoid query failures from missing files.
- **Silent files**: Silent or near-silent files may produce a small amount of hallucinated text; apply length filtering in downstream processing.

## Examples

### Basic Usage

```sql
-- Single audio transcription
SELECT AI_TRANSCRIBE(
    'endpoint:qwen3-asr-flash',
    GET_PRESIGNED_URL(USER VOLUME, 'audios/meeting.wav', 36000)
) AS transcription;
```

### Batch Transcription of Audio Files in a Volume

```sql
SELECT
    relative_path,
    AI_TRANSCRIBE(
        'endpoint:qwen3-asr-flash',
        GET_PRESIGNED_URL(USER VOLUME, relative_path, 36000)
    ) AS transcription
FROM (SHOW USER VOLUME DIRECTORY SUBDIRECTORY 'audios' REGEXP = '.*\.wav');
```

### Transcribe Then Classify (Customer Service Recording Analysis)

```sql
SELECT
    relative_path,
    AI_CLASSIFY(
        'endpoint:qwen3.5-plus',
        AI_TRANSCRIBE(
            'endpoint:qwen3-asr-flash',
            GET_PRESIGNED_URL(USER VOLUME, relative_path, 36000)
        ),
        ARRAY('complaint', 'inquiry', 'praise', 'suggestion')
    ) AS category
FROM (SHOW USER VOLUME DIRECTORY SUBDIRECTORY 'audios/calls' REGEXP = '.*\.wav');
```

### Transcribe Then Extract Key Information

```sql
SELECT AI_EXTRACT(
    'endpoint:qwen3.5-plus',
    AI_TRANSCRIBE(
        'endpoint:qwen3-asr-flash',
        GET_PRESIGNED_URL(USER VOLUME, 'audios/interview.wav', 36000)
    ),
    JSON'{"speaker":"speaker", "topic":"discussion topic", "conclusion":"conclusion"}'
) AS info;
```

### Batch Transcription with options

```sql
SELECT
    relative_path,
    AI_TRANSCRIBE(
        'endpoint:qwen3-asr-flash',
        GET_PRESIGNED_URL(USER VOLUME, relative_path, 36000),
        JSON'{"response.timeout":"120"}'
    ) AS transcription
FROM (SHOW USER VOLUME DIRECTORY SUBDIRECTORY 'audios' REGEXP = '.*\.wav')
LIMIT 20;
```

### Using an API Connection

```sql
SELECT AI_TRANSCRIBE(
    'conn_asr:paraformer-v2',
    GET_PRESIGNED_URL(USER VOLUME, 'audios/call.wav', 36000)
) AS transcription;
```

## Limitations

- **`model` parameter is required**: Omitting it causes the error `AI function must have at least two arguments`.
- **`audio_url` must be an HTTP/HTTPS URL**: Only URL-based audio file references are supported; direct file content or local paths are not. Use `GET_PRESIGNED_URL()` to obtain the URL.
- **Limited format support**: Only WAV, MP3, FLAC, M4A are supported; OGG, WEBM, and other formats are not.
- **Returns plain text only**: No timestamps, speaker diarization, or confidence scores.
- **Silent files**: Silent or near-silent files may produce a small amount of hallucinated text.
- **Quota limits**: Subject to AI Gateway tenant token quota limits; confirm remaining quota before large-scale batch transcription.
