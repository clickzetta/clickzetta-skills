# Creating an LLM Function to Analyze Company Industry

Objective: Use large language model (LLM) services to fill in nationally standardized **primary industry** and **secondary industry** information based on the **company name** column in the Lakehouse customer table. The result is as follows:

![](.topwrite/assets/20250612-171447.jpeg =675)

> Note: To complete this example, you need to:
>
> 1. Have Docker installed (primarily to ensure the development environment is consistent with the Singdata environment for running functions)
> 2. Have an Alibaba Cloud account and obtain an API-KEY for the Bailian platform. Refer to [Alibaba Cloud Bailian](https://www.aliyun.com/product/bailian)
> 3. Have already created an API connection. Refer to: Create [API Connection](create-api-connection.md)

### Step 1: Prepare the Development Environment

1. **Install Docker**: Ensure Docker is installed locally: <https://www.docker.com/>

2. **Pull the Docker image**. Execute in a local command-line terminal (such as macOS terminal):

   ```
   [Local]# docker pull quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779
   ```

3. **Start the Docker container**. This container is based on the `manylinux2014_x86_64` image and is configured to use the Python 3.10 environment.

   ```
   [Local]# docker run -it --name cz_func --env PATH="/opt/python/cp310-cp310/bin:$PATH" quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779 bash
   ```

> If the container has already stopped, use the following commands to start and log in:
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

&#x20;    4\.  Create a folder `cz_llm` under the /root directory

```
[root@docker root]# cd /root ; mkdir cz_llm 
[root@docker cz_llm]# cd cz_llm
[root@docker cz_llm]# touch cz_llm.py
```

5. Save the following program code into the `cz_llm.py` file:

```
import os
from cz.udf import annotate
import dashscope
from http import HTTPStatus
import json
import sys

@annotate("*->string")
class llm_call(object):
    def evaluate(self, text, prompt, api_key, model_name, temperature=0.7, enable_search=False):

        # Set API key
        dashscope.api_key = api_key

        # Build messages
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ]

        try:
            # Call the model (non-streaming output)
            response = dashscope.Generation.call(
                model=model_name,
                messages=messages,
                stream=False,  # Disable streaming output
                result_format='message',
                temperature=temperature,
                enable_search=enable_search,
                top_p=0.8
            )

            # Handle response
            if response.status_code == HTTPStatus.OK:
                # Non-streaming output: retrieve the complete content directly
                if hasattr(response.output, 'choices') and len(response.output.choices) > 0:
                    if hasattr(response.output.choices[0].message, 'content'):
                        return response.output.choices[0].message.content
                    else:
                        return "Error: No content in response"
                else:
                    return "Error: No choices in response"
            else:
                # Return error message
                return f"Error: Request id: {response.request_id}, Status code: {response.status_code}, error code: {response.code}, error 
message: {response.message}"

        except Exception as e:
            # Return error message
            return f"Error: {str(e)}"

# Test code
if __name__ == "__main__":
    # Create instance
    llm = llm_call()
    
    # Configure parameters
    API_KEY = "sk-xxxxxx"  # Replace with your API key
    MODEL_NAME = "qwen-max"  # or qwen-plus, qwen-max, etc.
    
    # Test example
    test_text = 'Little Red Book'
    test_prompt = 'Return the nationally standardized primary and secondary industries for this company. Output the result directly as JSON: {"primary_industry":"xxx","secondary_industry":"xxx"}. Be concise.'
    
    print("Calling LLM...")
    result = llm.evaluate(test_text, test_prompt, API_KEY, MODEL_NAME, 0, True)
    
    print(f"\nInput text: {test_text}")
    print(f"System prompt: {test_prompt}")
    print(f"LLM response: {result}")
```

### Step 2: Download Third-party Libraries

The program depends on the third-party package `dashscope`, which needs to be downloaded (the rest are Python built-in libraries, such as `os`, `http`, `json`, `sys`, etc., and do not need to be downloaded. `cz.udf` is automatically added by the system when creating the function).

Execute in the development environment command-line terminal:

```
[root@docker cz_llm]# pwd
/root/cz_llm

[root@docker cz_llm]# pip install dashscope -t .
```

The directory structure at this point will look similar to:

![](.topwrite/assets/external_func_2.jpeg)

^

### Step 3: Local Debugging

The following 3 lines will be modified, because the current environment has not yet loaded the `cz.udf` library:

```
...
2 #from cz.udf import annotate   # Comment out
...
8 #@annotate("*->string")  # Comment out
...
56 API_KEY = "sk-xxxxxx"  # Replace with your API key
```

The API_KEY is the API-KEY of the Alibaba Cloud Bailian platform. You need to register an Alibaba Cloud account, log in, and obtain it here: [Alibaba Cloud Bailian](https://bailian.console.aliyun.com/?spm=5176.12818093_47.console-base_search-panel.dtab-product_sfm.60852cc9WIq2Db\&scm=20140722.S_sfm._.ID_sfm-RL_%E5%A4%A7%E6%A8%A1%E5%9E%8B%E6%9C%8D%E5%8A%A1%E5%B9%B3%E5%8F%B0%E7%99%BE%E7%82%BC%E6%8E%A7%E5%88%B6%E5%8F%B0-LOC_console_console-OR_ser-V_4-P0_0\&tab=api#/api)

After commenting out the above two lines, save and exit the editing script. Execute:

```
[root@docker cz_llm]# export PYTHONPATH="${_PWD}:${_PWD}/lib"
[root@docker cz_llm]# python cz_llm.py 
Calling LLM...

Input text: Little Red Book
System prompt: Return the nationally standardized primary and secondary industries for this company. Output the result directly as JSON: {"primary_industry":"xxx","secondary_industry":"xxx"}. Be concise.
LLM response: {"primary_industry":"Internet","secondary_industry":"Social Media"}
```

### Step 4: Package and Upload

Before packaging, uncomment the two lines commented out above.

```
...
2 from cz.udf import annotate   # Uncomment
...
8 @annotate("*->string")  # Uncomment
```

Execute the packaging command, ensuring the current directory is the program directory (for this example, `/root/cz_llm`):

```
[root@docker cz_llm]# pwd
/root/cz_llm
[root@docker cz_llm]# zip -rq ../cz_llm.zip ./
[root@docker cz_llm]# ls ../
```

> Tip: If your environment does not have the zip command, try installing it with `yum install zip`. If you encounter issues during installation, please refer to the appendix "**Errors When Installing Tools**".

You will find a `cz_llm.zip` file in the `/root` directory. Copy this file to the Lakehouse USER VOLUME object:

Execute on the Docker host machine:

```
[Local]# docker cp cz_func:/root/cz_llm.zip ~/Downloads
```

Now the `cz_llm.zip` file is in the host machine's user `Downloads` directory

Use the Lakehouse JDBC client (please refer to [Lakehouse JDBC Client](connect-with-cli.md)) to put the file into the Lakehouse USER VOLUME:

```
PUT '/Users/derekmeng/Downloads/transform_company_id.zip' to USER VOLUME;
```

![](.topwrite/assets/external_functions_3.jpeg)

### Step 5: Create and Use the Function:

This step depends on having created an API connection in advance. Please refer to: [API Connection](create-api-connection.md) for the creation process.

```
CREATE EXTERNAL FUNCTION public.fc_cz_llm
    AS 'cz_llm.llm_call'   -- Main program file name without .py extension.Main class name
    USING ARCHIVE 'volume:user://~/cz_llm.zip' 
    connection sg_fc_api_conn -- API Connection must be created in advance
    WITH PROPERTIES (
        'remote.udf.api' = 'python3.mc.v0'
    )
COMMENT 'Usage: python get_industry_classification.py <text> <prompt> <api_key> <model_name> [temperature] [enable_search]';
```

The creation process will take approximately 1 minute. After creation, execute the verification function (note: replace `'${api_key}'`):

```
SELECT    public.fc_cz_llm (
          'Singdata Technology',
          'Return the universally used industry classification as JSON in English: {"primary_industry":"xxx","secondary_industry":"xxx"}',
          '${api_key}',
          'qwen-plus',
          '0.4',
          'true'
          ) AS llm_result;
```

The execution result is as follows:

![](.topwrite/assets/external_function_4.jpeg =660)
