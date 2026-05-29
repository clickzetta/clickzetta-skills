# **External AI Functions**: Creating an Embedding Function

Objective: Use the Alibaba Cloud Bailian platform's Embedding functions to vectorize text and image file data, and implement an image search scenario. The result is as follows:

![](.topwrite/assets/image_search.png)

> Note: To complete this example, you need to:
>
> 1. Have Docker installed (primarily to ensure the development environment is consistent with the environment where functions run in the cloud)
> 2. Have an Alibaba Cloud account and obtain an API-KEY for the Bailian platform. Refer to [Alibaba Cloud Bailian](https://www.aliyun.com/product/bailian)
> 3. Have already created an API connection. Refer to: Create [API Connection](create-api-connection.md)

### Step 1: Prepare the Development Environment

1. **Install Docker**: Ensure Docker is installed locally: <https://www.docker.com/>

2. **Pull the Docker image**. Execute in a local command-line terminal (such as macOS Terminal):

   ```
   [Local]# docker pull quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779
   ```

3. **Start the Docker container**: This container is based on the `manylinux2014_x86_64` image and is configured to use the Python 3.10 environment.

   ```
   [Local]# docker run -it --name cz_func --env PATH="/opt/python/cp310-cp310/bin:$PATH" quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779 bash
   ```

> If the container has already stopped, use the following commands to start and enter it:
>
> 1. **Start the container**:
>
> ```
> # docker start cz_func
> ```
>
> 2. **Enter the container**:
>
> ```
> # docker exec -it cz_func bash
> ```

4. Create a folder `embeddings` under the /root directory

```
[root@docker root]# cd /root ; mkdir embeddings 
[root@docker embeddings]# cd embeddings
[root@docker embeddings]# touch gen_embeddings.py
```

5. The program code in `cz_llm.py` is as follows:

```
import os
from cz.udf import annotate
from openai import OpenAI
import json

@annotate("*->string")
class get_embeddings(object):
    def evaluate(self, model_type, input_string, api_key, model_name, dim=None):

        if model_type == "text":
            # Initialize the OpenAI client with the user-provided API key
            client = OpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )

            input_data = input_string
            completion = client.embeddings.create(
                model=model_name,  # Use the user-provided text model name
                input=input_data,
                dimensions=int(dim),  # Specify the vector dimension
                encoding_format="float"
            )
            result_json = json.loads(completion.model_dump_json())
            embedding_vector = result_json['data'][0]['embedding']

        elif model_type == "multimodal":
            import dashscope
            image = input_string
            dashscope.api_key = api_key  # Use the user-provided API key
            input = [{'image': image}]
            resp = dashscope.MultiModalEmbedding.call(
                model=model_name,  # Use the user-provided multimodal model name
                input=input
            )
            result_json = json.loads(json.dumps(resp.output, ensure_ascii=False, indent=4))
            embedding_vector = result_json['embeddings'][0]['embedding']
        else:
            return "Not Valid Model Type"

        if len(embedding_vector) >= 1:
            return str(embedding_vector)
        else:
            return "Not Valid"
# Add command-line invocation entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Get Embeddings using OpenAI or DashScope")
    parser.add_argument('--model_type', required=True, help='Model type: text or multimodal')
    parser.add_argument('--input_string', required=True, help='The input string or image path')
    parser.add_argument('--api_key', required=True, help='Your API key')
    parser.add_argument('--model_name', required=True, help='Model name')
    parser.add_argument('--dim', default=1536, help='Vector dimensions (only for text models)')

    args = parser.parse_args()

    embedder = get_embeddings()
    result = embedder.evaluate(
        model_type=args.model_type,
        input_string=args.input_string,
        api_key=args.api_key,
        model_name=args.model_name,
        dim=args.dim
    )
    print(result)
```

### Step 2: Download Third-party Libraries

The program depends on the third-party package `openai`, which needs to be downloaded (the rest are Python built-in libraries; `os` and `json` are built into Python and do not need to be downloaded. `cz.udf` is automatically added by the system when creating the function).

Execute in the development environment command-line terminal:

```
[root@docker embeddings]# pwd
/root/embeddings

[root@docker embeddings]# pip install openai -t .
```

The directory structure at this point will look similar to:

![](.topwrite/assets/vector2.jpeg)

### Step 3: Local Debugging

The following 3 lines of code need to be modified, because the current environment has not yet loaded the `cz.udf` library:

```
...
2 #from cz.udf import annotate   # Comment out
...
6 #@annotate("*->string")  # Comment out
...
```

The API_KEY is the API-KEY of the Alibaba Cloud Bailian platform. You need to register an Alibaba Cloud account, log in, and obtain it here: [Alibaba Cloud Bailian](https://bailian.console.aliyun.com/?spm=5176.12818093_47.console-base_search-panel.dtab-product_sfm.60852cc9WIq2Db\&scm=20140722.S_sfm._.ID_sfm-RL_%E5%A4%A7%E6%A8%A1%E5%9E%8B%E6%9C%8D%E5%8A%A1%E5%B9%B3%E5%8F%B0%E7%99%BE%E7%82%BC%E6%8E%A7%E5%88%B6%E5%8F%B0-LOC_console_console-OR_ser-V_4-P0_0\&tab=api#/api)

After commenting out the above two lines, save and exit the editing script. Replace the image_url and api_key below with actual parameters and execute:

```
[root@docker embeddings]# export PYTHONPATH="${_PWD}:${_PWD}/lib"
[root@docker embeddings]# python gen_embeddings.py \
    --model_type multimodal \
    --input_string ${image_url} \
    --api_key ${api_key} \
    --model_name multimodal-embedding-v1
```

### Step 4: Package and Upload

Before packaging, uncomment the two lines commented out above.

```
...
2 from cz.udf import annotate   # Uncomment
...
8 @annotate("*->string")  # Uncomment
```

Before executing the packaging command, ensure the current directory is the program directory (for this example, `/root/cz_llm`).

```
[root@docker embeddings]# pwd
/root/embeddings
[root@docker embeddings]# zip -rq ../embeddings.zip ./
[root@docker embeddings]# ls ../
```

> Tip: If your environment does not have the zip command, try installing it with `yum install zip`. If you encounter issues during installation, please refer to the appendix "**Errors When Installing Tools**".

You will find a `cz_llm.zip` file in the `/root` directory. Copy this file to the Lakehouse USER VOLUME:

Execute on the Docker host machine:

```
[Local]# docker cp cz_func:/root/embeddings.zip ~/Downloads
```

Now `cz_llm.zip` is in the host machine's user `Downloads` directory

Use the Lakehouse JDBC client (please refer to [Lakehouse JDBC Client](connect-with-cli.md)) to put the file into the Lakehouse USER VOLUME:

```
PUT '/Users/derekmeng/Downloads/embeddings.zip' to USER VOLUME;
```

![](.topwrite/assets/image2.jpeg)

### Step 5: Create and Use the Function:

This step depends on having created an API Connection in advance. Please refer to: [API Connection](create-api-connection.md) for the creation process.

```
CREATE EXTERNAL FUNCTION public.fc_embeddings
AS 'gen_embeddings.get_embeddings'
USING ARCHIVE 'volume:user://~/embeddings.zip'
connection sg_fc_api_conn
WITH PROPERTIES (
'remote.udf.api' = 'python3.mc.v0'
)
COMMENT 'Examples:
For text: text <input_string> <api_key> <model_name> <dim>
For multimodal:multimodal <input_string> <api_key> <model_name>';
```

```
# Verify
select public.fc_embeddings('multimodal', 'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood5.jpg', '${api_key}', 'multimodal-embedding-v1');
```

Execution result:

![](.topwrite/assets/images.jpeg)

The next step is the core step for implementing the image search functionality. This query takes an image URL, vectorizes it, and then compares it with all image vectors in the data table (`food_images_data_vec`). The contents of the table `food_images_data_vec` are as follows:

![](.topwrite/assets/image_search.jpeg)

Vector image search results:

![](.topwrite/assets/image_vec2.jpeg)
