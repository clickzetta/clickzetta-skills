# External Function Development Guide (Python3)

## Objective

This guide helps developers learn how to write external functions in Python to process data in Singdata Lakehouse.

## Important Notes

> * **Python Version**: Only Python 3.10 is supported. If your dependencies include native libraries with shared object files (.so), such libraries must be compatible with the Python 3.10 ABI (Application Binary Interface).
> * **Deployment Package Format**: Supports standalone `.py` script files or packages archived in `.zip` format.
> * **Large Package Deployment**: If the program and its dependencies exceed 500MB after compression, you must create the function via a container image. For details, refer to the tutorial: [Practical: Using Hugging Face Image Recognition Model to Process Image Data](RemoteFunction-on-acr.md)

## Environment Preparation

Given the above usage constraints of External Functions, the following are specific requirements and recommendations for the development environment:

1. **No Third-party Library Dependencies**:
   If your Python script does not depend on any third-party libraries, you only need to ensure the code conforms to the required code structure described below and can execute correctly in a Python 3.10 environment.

2. **With Third-party Library Dependencies**:
   If the script requires third-party libraries, these dependencies (and their binaries) must be compatible with the Python 3.10 ABI (x86\_64 architecture).

> **Cross-platform Compatibility**: When developing in non-Linux x86\_64 environments such as macOS or Windows, ABI compatibility issues with Python dependency libraries are quite common. To ensure consistency and avoid potential errors, it is strongly recommended to use the following container image as the standard development environment for Python External Functions:
> `quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779`. This image provides a pre-configured, compliant Linux x86\_64 and Python 3.10 environment. For image installation instructions, refer to the appendix at the end of this document: Development Environment Image Installation.
>
> &#x20;If your development environment is already an x86\_64 Linux system, you only need to ensure the Python version is 3.10.

## Code Structure

The code structure of a Python function is divided into the following parts:

* **Import Module**: Required. Must at least include `from cz.udf import annotate` to import the function signature module, so that Singdata Lakehouse can recognize the function signature defined in the subsequent code.
* **Function Signature**: Required. Format: `@annotate(<signature>)`, where `signature` defines the data types of the function's input parameters and return value. See the Function Signature section below for more details.
* **Custom Python Class**: Required. The organizational unit of UDF code, defining the variables and methods that implement business requirements. You can also reference third-party libraries or file and table resources in the code.
* **evaluate Method**: Required. Located inside the custom Python class. The `evaluate` method defines the input parameters and return value. A Python class can only contain one `evaluate` method.

> Based on the above code structure, the following is an example function that converts characters to uppercase:

```Python
#!/usr/bin/env python
try:
    from cz.udf import annotate  # Import module
except ImportError:
    annotate = lambda _: lambda _: _

@annotate("string->string")  # Function signature
class Upper(object):         # Custom Python class
    def evaluate(self, arg):  # evaluate method
        if arg is None:  
            return None
        return arg.upper()
```

## Installing Third-party Libraries

Taking downloading httpx and pydantic as an example, use the following command to download the dependency packages to the directory where the main program file is located (the current directory in this example):

```Shell
pip3 install httpx pydantic -t . 
```

> ⚠️ **Note**: When you use a non-Linux system such as macOS / Windows, or a non-X86-64 device, or when your third-party libraries contain native code, to avoid Python ABI compatibility issues, it is strongly recommended to use a container based on `quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779` to download third-party dependencies. Refer to the appendix: Development Environment Image Installation.

## Uploading Functions

### Upload and Zip Upload

Only applicable for functions smaller than 500MB after packaging. For functions larger than 500MB, refer to the subsequent section: Creating Functions via Container Image.

Package the program files, dependency library files, or model files into a zip format (currently only zip format is supported and must be smaller than 500MB), for example:

```Shell
cd ./deps
zip -rq code.zip ./*
```

Upload code.zip to cloud object storage and grant the cloud role of Singdata Lakehouse access to the corresponding path. The authorization process is not described in this development guide; please refer to [Usage Process: External Function](RemoteFunction-best-practice.md).
You may also specify an internal volume. Although you can use an internal volume, the code bucket parameter when creating an API CONNECTION must still point to an external address.

* **User Volume Format Address**: `volume:user://~/upper.jar`
  * `user` indicates the use of the User Volume protocol.

  * `~` indicates the current user and is a fixed value.

  * `upper.jar` indicates the target filename.
* **Table Volume Format Address**: `volume:table://table_name/upper.jar`
  * `table` indicates the use of the Table Volume protocol.
  * `table_name` indicates the table name; fill in the actual table name.
  * `upper.jar` indicates the target filename.

### Upload via Container Image

Only applicable for functions larger than 500MB after packaging or those requiring GPU resources. Requires enabling Alibaba Cloud Container Registry (free).

Please refer to the document: [Practical: Using Hugging Face Image Recognition Model to Process Image Data](RemoteFunction-on-acr.md)

^

## Example

Objective: Use a Large Language Model (LLM) service to fill in the nationally standardized **primary industry** and **secondary industry** information based on the **company name** column in a Lakehouse customer table. The effect is as follows:

![](.topwrite/assets/20250612-171447.jpeg =675)

> ⚠️ **Note**: To complete this example, you need:
>
> 1. Docker installed (mainly to ensure the development environment is consistent with the environment where Singdata runs functions)
> 2. An Alibaba Cloud account with the Bailian platform API-KEY enabled. Refer to [Alibaba Cloud Bailian](https://www.aliyun.com/product/bailian)
> 3. An API connection already created. Refer to: Creating [API Connection](create-api-connection.md)

### Step 1: Prepare the Development Environment

1. **Install Docker**: Ensure Docker is installed locally: <https://www.docker.com/>

2. **Pull the Docker Image**. Execute in the local command-line terminal (e.g., Terminal on macOS):

   ```
   [Local]# docker pull quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779
   ```

3. **Start the Docker Container**. This container is based on the `manylinux2014_x86_64` image and is configured to use the Python 3.10 environment:

   ```
   [Local]# docker run -it --name cz_func --env PATH="/opt/python/cp310-cp310/bin:$PATH" quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779 bash
   ```

> If the container has stopped, you can start and log in with the following commands:
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

&#x20;    4\.   Create a directory cz\_llm under /root:

```
[root@docker root]# cd /root ; mkdir cz_llm 
[root@docker cz_llm]# cd cz_llm
[root@docker cz_llm]# touch cz_llm.py
```

&#x20;   5\. The program code in `cz_llm.py` is as follows:

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
            # Call model (non-streaming output)
            response = dashscope.Generation.call(
                model=model_name,
                messages=messages,
                stream=False,  # Disable streaming output
                result_format='message',
                temperature=temperature,
                enable_search=enable_search,
                top_p=0.8
            )

            # Process response
            if response.status_code == HTTPStatus.OK:
                # Non-streaming output directly gets full content
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
    test_text = 'Xiaohongshu'
    test_prompt = 'Please return the national standard primary and secondary industry for this company. Output directly: "primary_industry":"xxx","secondary_industry":"xxx", be concise'
    
    print("Calling LLM...")
    result = llm.evaluate(test_text, test_prompt, API_KEY, MODEL_NAME, 0, True)
    
    print(f"\nInput text: {test_text}")
    print(f"System prompt: {test_prompt}")
    print(f"LLM response: {result}")
```

### Step 2: Download Third-party Libraries

The program depends on the third-party package `dashscope`, which needs to be downloaded (the rest are Python built-in libraries; `os`, `http`, `json`, `sys` are Python built-in libraries and do not need downloading. `cz.udf` will be added by the system by default when creating the function.)

Execute in the command-line terminal in the development environment:

```
[root@docker cz_llm]# pwd
/root/cz_llm

[root@docker cz_llm]# pip install dashscope -t .
```

At this point, the directory structure will look similar to:

![](.topwrite/assets/external_func_2.jpeg)

^

### Step 3: Local Debugging

Make modifications on 3 lines, because the current environment does not have the `cz.udf` library loaded:

```
...
2 #from cz.udf import annotate   # Comment out
...
8 #@annotate("*->string")  # Comment out
...
56 API_KEY = "sk-xxxxxx"  # Replace with your API key
```

The API\_KEY is the API-KEY from the Alibaba Cloud Bailian platform. You need to register an Alibaba Cloud account and obtain it here after login: [Alibaba Cloud Bailian](https://bailian.console.aliyun.com/?spm=5176.12818093_47.console-base_search-panel.dtab-product_sfm.60852cc9WIq2Db\&scm=20140722.S_sfm._.ID_sfm-RL_%E5%A4%A7%E6%A8%A1%E5%9E%8B%E6%9C%8D%E5%8A%A1%E5%B9%B3%E5%8F%B0%E7%99%BE%E7%82%BC%E6%8E%A7%E5%88%B6%E5%8F%B0-LOC_console_console-OR_ser-V_4-P0_0\&tab=api#/api)

After commenting out the above two lines, save and exit the editor. Execute:

```
[root@docker cz_llm]# export PYTHONPATH="${_PWD}:${_PWD}/lib"
[root@docker cz_llm]# python cz_llm.py 
Calling LLM...

Input text: Xiaohongshu
System prompt: Please return the national standard primary and secondary industry for this company. Output directly: "primary_industry":"xxx","secondary_industry":"xxx", be concise
LLM response: "primary_industry":"Internet","secondary_industry":"Social Media"
```

### Step 4: Package and Upload

Before packaging, uncomment the two lines commented out above.

```
...
2 from cz.udf import annotate   # Uncomment
...
8 @annotate("*->string")  # Uncomment
```

Execute the packaging command, ensuring the current directory is the program directory (`/root/cz_llm` in this example):

```
[root@docker cz_llm]# pwd
/root/cz_llm
[root@docker cz_llm]# zip -rq ../cz_llm.zip ./
[root@docker cz_llm]# ls ../
```

> 💡 **Tip**: If your environment does not have the zip command, try downloading it with `yum install zip`. If you encounter problems during the download, please refer to the appendix "**Errors When Installing Tools**".

You will find a `cz_llm.zip` file in the `/root` directory. Copy this file to the Lakehouse USER VOLUME storage:

Execute on the Docker host machine:

```
[Local]# docker cp cz_func:/root/cz_llm.zip ~/Downloads
```

Now `cz_llm.zip` is in the host user's `Downloads` directory.

Use the Lakehouse JDBC client (refer to [Lakehouse JDBC Client](connect-with-cli.md)) to put the file into the Lakehouse USER VOLUME:

```
PUT '/Users/derekmeng/Downloads/transform_company_id.zip' to USER VOLUME;
```

![](.topwrite/assets/external_functions_3.jpeg)

### Step 5: Create and Use the Function

This step depends on having an API connection created beforehand. For the creation process, please refer to: [API Connection](create-api-connection.md)

```
CREATE EXTERNAL FUNCTION public.fc_cz_llm
    AS 'cz_llm.llm_call'   -- Main program filename without .py extension.Main class name
    USING ARCHIVE 'volume:user://~/cz_llm.zip' 
    connection sg_fc_api_conn -- API Connection needs to be created beforehand
    WITH PROPERTIES (
        'remote.udf.api' = 'python3.mc.v0'
    )
COMMENT 'Usage: python get_industry_classification.py <text> <prompt> <api_key> <model_name> [temperature] [enable_search]';
```

The creation process takes about 1 minute. After creation is complete, execute the verification function: (Note: Replace `'${api_key}'`)

```
SELECT    public.fc_cz_llm (
          'Singdata Technology',
          'Please return the national standard industry classification in JSON format: {"primary_industry":"xxx","secondary_industry":"xxx"}',
          '${api_key}',
          'qwen-plus',
          '0.4',
          'true'
          ) AS llm_result;
```

Execution result:

![](.topwrite/assets/external_function_4.jpeg =660)

## Appendix

### Function Signature

The function signature format is as follows:

```Python
@annotate(<signature>)
```

`signature` is a string used to identify the data types of input parameters and return values. When executing a UDF, the input parameter types and return value type of the UDF function must be consistent with the types specified in the function signature. The query semantic analysis phase will check for usages that do not conform to the function signature definition and will report an error when a type mismatch is detected. The specific format is as follows:

```Python
'arg_type_list -> type'
```

Where:

* `arg_type_list`: Represents the data type of input parameters. Multiple input parameters are allowed, separated by commas. Supported data types are BIGINT, STRING, DOUBLE, BOOLEAN, DATETIME, DECIMAL, FLOAT, BINARY, DATE, DECIMAL(precision,scale), CHAR, VARCHAR, complex data types (ARRAY, MAP, STRUCT), or nested complex data types.

* `arg_type_list` also supports asterisk (\*) or empty (''):
  * When `arg_type_list` is asterisk (\*), it means any number of input parameters.
  * When `arg_type_list` is empty (''), it means no input parameters.

* `type`: Represents the data type of the return value. UDF returns only one column. Supported data types are: BIGINT, STRING, DOUBLE, BOOLEAN, DATETIME, DECIMAL, FLOAT, BINARY, DATE, DECIMAL(precision,scale), complex data types (ARRAY, MAP, STRUCT), or nested complex data types.

Examples of valid function signatures:

| Function Signature Example                     | Description                                                       |
| --------------------------------------------- | -------------------------------------------------------- |
| `'bigint,double->string'`                     | Input parameter types: BIGINT, DOUBLE; return value type: STRING.                       |
| `'*->string'`                                 | Any number of input parameters; return value type: STRING.                                    |
| `'->double'`                                  | No input parameters; return value type: DOUBLE.                                      |
| `'array<bigint> -> struct<x:string>, y:int>'` | Input parameter type: ARRAY\<BIGINT>; return value type: STRUCT\<x\:string>, y\:int>. |
| '->map\<bigint, string>'                      | No input parameters; return value type: MAP\<BIGINT, STRING>.                        |

### Data Types

To ensure consistency between the data types used in Python UDF development and those supported by Singdata Lakehouse, you need to be aware of the data type mapping relationship between the two:

| Singdata Lakehouse Data Type | Python 3 Data Type          |
| ----------------- | ---------------------- |
| BIGINT            | int                    |
| BOOLEAN           | bool                   |
| CHAR              | unicode                |
| DATE              | datetime.date          |
| DECIMAL           | decimal.Decimal        |
| DOUBLE            | float                  |
| FLOAT             | float                  |
| INT               | int                    |
| SMALLINT          | int                    |
| STRING            | str                    |
| TIMESTAMP\_LTZ    | datetime.datetime      |
| TINYINT           | int                    |
| ARRAY             | list                   |
| MAP               | list                   |
| STRUCT            | collections.namedtuple |
| VARCHAR(n)        | str (write fails if limit exceeded)            |
| VOID              | NoneType               |

### Development Environment Image Installation

> **Applicable Scenario: Avoiding Python ABI compatibility issues when developing on non-Linux / non-X86-64 environments or using third-party libraries containing native code.**

In the software development process, especially when using Python for cross-platform development or interacting with low-level native code, Application Binary Interface (ABI) compatibility is an important aspect that requires attention. When your development or deployment environment is a non-Linux system such as macOS or Windows, or the target device architecture is not X86-64 (e.g., ARM architecture devices), or the project introduces third-party libraries that include compiled native code such as C/C++, the risk of potential ABI incompatibility increases significantly. To ensure the stability and portability of Python applications, it is strongly recommended to use a standardized build environment to download and compile these third-party dependencies.

**Recommended Practice: Use a Container**

For the specific scenarios mentioned in the note, i.e., when using non-Linux systems (such as macOS, Windows), non-X86-64 devices, or third-party libraries containing native code, to avoid Python ABI compatibility issues, it is strongly recommended to use a Docker container based on `quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779` to download and build third-party dependencies.

#### **How to Operate**:

1. **Install Docker**: Ensure Docker is installed on your development machine: <https://www.docker.com/>

2. **Pull the Image**:

   ```
   docker pull quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779
   ```

   ^

3. Start the Docker container. This container is based on the `manylinux2014_x86_64` image and is configured to use the Python 3.10 environment:

   ```
   docker run -it --name cz_func --env PATH="/opt/python/cp310-cp310/bin:$PATH" quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779 bash
   ```

You can now develop your Python External Functions in this environment with Python 3.10.

> If the container has stopped, you can start and log in with the following commands:
>
> 1. **Start the container**:
>
> ```
> docker start cz_func
> ```
>
> 2. **Enter the container**:
>
> ```
> docker exec -it cz_func bash
> ```
>
> ^

^

Then you should see the Bash prompt inside the container (the exact prompt style may vary depending on the image). For example, printing the Python version should display:

```
[root@cfadeae5f8b0 /]# python --version
 Python 3.10.8
```

You should now have successfully "logged in" to your `cz_func` container.

^

#### **Common Image Usage Issues**:

1\. **Errors When Installing Tools**

&#x20;   For example, running `yum install zip` to install the `zip` packaging tool may encounter errors such as:

```
[root@311b32ae3e5f ]# yum install zip
Loaded plugins: fastestmirror, ovl
Determining fastest mirrors
Could not retrieve mirrorlist http://mirrorlist.centos.org/?release=7&arch=x86_64&repo=os&infra=container error was
14: curl#6 - "Could not resolve host: mirrorlist.centos.org; Unknown error"


 One of the configured repositories failed (Unknown),
 and yum doesn't have enough cached data to continue. At this point the only
 safe thing yum can do is fail. There are a few ways to work "fix" this
...
            yum-config-manager --save --setopt=<repoid>.skip_if_unavailable=true

Cannot find a valid baseurl for repo: base/7/x86_64
```

This error occurs because CentOS 7 reached End of Life (EOL) on June 30, 2024, and the official repositories have been moved to the CentOS vault. `mirrorlist.centos.org` no longer provides CentOS 7 repository services.

Here is the solution:

First, check if the network connection is normal.

If the network is normal, update the repository configuration to use the CentOS vault:

```
# Backup current repository files
mkdir -p /etc/yum.repos.d/backup
cp /etc/yum.repos.d/CentOS-*.repo /etc/yum.repos.d/backup/

# Update repository URLs to use vault.centos.org
sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*.repo
sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*.repo

# Clean yum cache
yum clean all

# Now try installing zip again
yum install zip
```

If you are in mainland China or `vault.centos.org` is slow to access, you can use a domestic mirror:

Use Alibaba Cloud mirror:

```
sed -i 's|baseurl=http://vault.centos.org|baseurl=http://mirrors.aliyun.com/centos-vault|g' /etc/yum.repos.d/CentOS-*.repo
```

Or use Tsinghua University mirror:

```
sed -i 's|baseurl=http://vault.centos.org|baseurl=https://mirrors.tuna.tsinghua.edu.cn/centos-vault|g' /etc/yum.repos.d/CentOS-*.repo
```

After making these changes, the `yum install zip` command should work normally.

^

**2**. **Copying Files Between Docker Container and Host Machine**

After generating a program package, if you want to copy it from the container to the host machine, or vice versa, you can use the following commands:

**Copy from Container to Host Machine**:

```
# docker cp <container_name>:<container_path> <host_path>, example:
docker cp cz_func:/root/gen_emmbedings.zip ~/Downloads
```

**Copy from Host Machine to Container**:

```
# docker cp <host_path> <container_name>:<container_path>, example:
docker cp ~/Downloads/file.txt cz_func:/root/
```

**Note**:

* The container can be in a running or stopped state.
* You can use either the container name or container ID.
* Copying both files and directories is supported: `docker cp` automatically recognizes whether it is a file or directory.

```
# Copy an entire directory
docker cp ~/project <container_name>:/root/
# Copy directory contents
docker cp ~/project/. <container_name>:/root/project/
```

^

* `docker cp` automatically recognizes whether it is a file or directory.

* When copying directories, all subdirectories and files are copied recursively.

* The destination path is automatically created if it does not exist.

* Difference between appending `/` or not at the end of the path:

  * `/app/logs` -> Copies the logs directory itself.
  * `/app/logs/.` -> Copies only the contents inside the logs directory.

^
