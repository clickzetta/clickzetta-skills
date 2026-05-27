# **External AI Function**: Create Embedding Function

Objective: Use the Alibaba Cloud Bailian platform's Embedding function to vectorize text and image file data, enabling image-to-image search scenarios. The effect is shown below:

![](.topwrite/assets/image_search.png)

> Note: To complete this example, you need:
>
> 1. Docker installed (mainly to ensure the development environment is consistent with the environment where functions run on the cloud)
> 2. An Alibaba Cloud account with a Bailian platform API-KEY enabled. See [Alibaba Cloud Bailian](https://www.aliyun.com/product/bailian)
> 3. An API connection already created. See: Create [API Connection](create-api-connection.md)

### Step 1: Prepare the Development Environment

1. **Install Docker**: Ensure Docker is installed locally: <https://www.docker.com/>

2. **Pull the Docker image**. Run the following in a local command-line terminal (e.g., macOS Terminal):

   ```
   [Local]# docker pull quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779
   ```

3. **Start the Docker container**: This container is based on the `manylinux2014_x86_64` image and configured to use Python 3.10.

   ```
   [Local]# docker run -it --name cz_func --env PATH="/opt/python/cp310-cp310/bin:$PATH" quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779 bash
   ```

> If the container has stopped, use the following commands to start and enter:
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

4. Create folder `embeddings` under the /root directory:

```
[root@docker root]# cd /root ; mkdir embeddings 
[root@docker embeddings]# cd embeddings
[root@docker embeddings]# touch gen_embeddings.py
```

5. The program code in `gen_embeddings.py` is as follows:

```
import os
from cz.udf import annotate
from openai import OpenAI
import json

@annotate("*->string")
class get_embeddings(object):
    def evaluate(self, model_type, input_string, api_key, model_name, dim=None):

        if model_type == "text":
            # Initialize OpenAI client with the API key provided by the user
            client = OpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
            )

            input_data = input_string
            completion = client.embeddings.create(
                model=model_name,  # Use the text model name provided by the user
                input=input_data,
                dimensions=int(dim),  # Specify vector dimensions
                encoding_format="float"
            )
            result_json = json.loads(completion.model_dump_json())
            embedding_vector = result_json['data'][0]['embedding']

        elif model_type == "multimodal":
            import dashscope
            image = input_string
            dashscope.api_key = api_key  # Use the API key provided by the user
            input = [{'image': image}]
            resp = dashscope.MultiModalEmbedding.call(
                model=model_name,  # Use the multimodal model name provided by the user
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
# Add command-line entry point
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

### Step 2: Download Third-Party Libraries

The program depends on the third-party package `openai`, which needs to be downloaded (the rest `os` and `json` are Python built-in libraries and do not need to be downloaded. `cz.udf` will be added by default when creating the function).

Run the following in the development environment terminal:

```
[root@docker embeddings]# pwd
/root/embeddings

[root@docker embeddings]# pip install openai -t .
```

At this point, the directory structure should look like:

![](.topwrite/assets/vector2.jpeg)

### Step 3: Local Debugging

Make the following modifications to 3 lines of code, since the `cz.udf` library is not yet loaded in the current environment:

```
...
2 #from cz.udf import annotate   # Comment out
...
6 #@annotate("*->string")  # Comment out
...
```

The API\_KEY is the Alibaba Cloud Bailian platform API-KEY. You need to register an Alibaba Cloud account and obtain it here after logging in: [Alibaba Cloud Bailian](https://bailian.console.aliyun.com/?spm=5176.12818093_47.console-base_search-panel.dtab-product_sfm.60852cc9WIq2Db\&scm=20140722.S_sfm._.ID_sfm-RL_%E5%A4%A7%E6%A8%A1%E5%9E%8B%E6%9C%8D%E5%8A%A1%E5%B9%B3%E5%8F%B0%E7%99%BE%E7%82%BC%E6%8E%A7%E5%88%B6%E5%8F%B0-LOC_console_console-OR_ser-V_4-P0_0\&tab=api#/api)

After commenting out the two lines above, save and exit the editor. Replace the image\_url and api\_key below with real values and run:

```
[root@docker embeddings]# export PYTHONPATH="${_PWD}:${_PWD}/lib"
[root@docker embeddings]# python gen_embeddings.py \
    --model_type multimodal \
    --input_string ${image_url} \
    --api_key ${api_key} \
    --model_name multimodal-embedding-v1
```

### Step 4: Package and Upload

Before packaging, uncomment the two lines of code that were commented out above.

```
...
2 from cz.udf import annotate   # Remove comment
...
8 @annotate("*->string")  # Remove comment
```

Before running the packaging command, ensure the current directory is the program directory (in this example, `/root/embeddings`).

```
[root@docker embeddings]# pwd
/root/embeddings
[root@docker embeddings]# zip -rq ../embeddings.zip ./
[root@docker embeddings]# ls ../
```

> Tip: If your environment does not have the zip command, try installing it with `yum install zip`. If you encounter issues during installation, refer to the appendix "**Errors When Installing Tools**."

You will find a `embeddings.zip` file under the `/root ` directory. Copy this file to the Lakehouse USER VOLUME:

Run on the Docker host:

```
[Local]# docker cp cz_func:/root/embeddings.zip ~/Downloads
```

Now the `embeddings.zip ` is in the host's user `Downloads` directory.

Use the Lakehouse JDBC client (see [Lakehouse JDBC Client](connect-with-cli.md)) to put (upload) the file into the Lakehouse USER VOLUME:

```
PUT '/Users/derekmeng/Downloads/embeddings.zip' to USER VOLUME;
```

![](.topwrite/assets/image2.jpeg)

### Step 5: Create and Use the Function

This step depends on having an API Connection created in advance. See: [API Connection](create-api-connection.md)

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
For multimodal: multimodal <input_string> <api_key> <model_name>';
```

```
# Verify
select public.fc_embeddings('multimodal', 'http://viapi-test.oss-cn-shanghai.aliyuncs.com/viapi-3.0domepic/imagerecog/RecognizeFood/RecognizeFood5.jpg', '${api_key}', 'multimodal-embedding-v1');
```

Execution result:

![](.topwrite/assets/images.jpeg)

The next steps are the core steps for implementing the image-to-image search feature. This query takes an image URL, vectorizes it, and then compares it against all image vectors in the data table (`food_images_data_vec`). The contents of the table `food_images_data_vec` are as follows:

![](.topwrite/assets/image_search.jpeg)

Result of vector-based image search:

![](.topwrite/assets/image_vec2.jpeg)
