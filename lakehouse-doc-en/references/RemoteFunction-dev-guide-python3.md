# External Function Development Guide (Python 3)

## Goal

This guide helps developers learn how to write External Functions in Python to process data in Singdata Lakehouse.

## Important Notes

> * **Python Version**: Only Python 3.10 is supported. If your dependencies include native libraries with shared object files (.so), those libraries must be compatible with the Python 3.10 ABI (Application Binary Interface).
> * **Deployment Package Format**: Supports standalone `.py` script files or packages archived in `.zip` format.
> * **Large Package Deployment**: If the total compressed size of the program and its dependencies exceeds 500 MB, the function must be created via a container image. See the tutorial: [Practice: Processing Image Data with a Hugging Face Image Recognition Model](RemoteFunction-on-acr.md)

## Environment Setup

Given the usage constraints of External Functions described above, the following specific requirements and recommendations apply to the development environment:

1. **No third-party library dependencies**:
   If your Python script does not depend on any third-party libraries, simply ensure the code follows the code structure specified below and can execute correctly in a Python 3.10 environment.

2. **With third-party library dependencies**:
   If the script requires third-party libraries, those dependencies (and their binaries) must be compatible with the Python 3.10 ABI (x86\_64 architecture).

> **Cross-platform compatibility**: When developing on non-Linux x86\_64 environments such as macOS or Windows, Python dependency ABI compatibility issues are common. To ensure consistency and avoid potential errors, it is strongly recommended to use the following container image as the standard development environment for Python External Functions:
> `quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779`. This image provides a pre-configured Linux x86\_64 environment with Python 3.10 that meets all requirements. For image installation, refer to the appendix at the end of this document: Development Environment Image Installation.
>
> If your development environment is already a Linux system with x86\_64 architecture, you only need to ensure the Python version is 3.10.

## Code Structure

The code structure of a Python function consists of the following parts:

* **Import module**: Required. Must include at least `from cz.udf import annotate` to import the function signature module so that Singdata Lakehouse can recognize the function signatures defined in the subsequent code.
* **Function signature**: Required. Format is `@annotate(<signature>)`, where `signature` defines the data types of the input parameters and return value. See the appendix for more on function signatures.
* **Custom Python class**: Required. The organizational unit of UDF code that defines variables and methods implementing business logic. You can also reference third-party libraries or file/table resources in your code.
* **evaluate method**: Required. Located inside the custom Python class. The `evaluate` method defines the input parameters and return value. A Python class can only contain one `evaluate` method.

> Based on the code structure above, an example function that converts a string to uppercase is as follows:

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

Using the download of httpx and pydantic as an example, use the following command to download the dependency packages to the directory where the main program file is located (current directory in this example):

```Shell
pip3 install httpx pydantic -t . 
```

> ⚠️ **Note**: When you are using macOS / Windows or another non-Linux system, using a non-X86-64 device, or using third-party libraries containing native code, to avoid Python ABI compatibility issues it is strongly recommended to download third-party dependencies inside a container based on `quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779`. See the appendix: Development Environment Image Installation.

## Uploading Functions

### Upload, Zip Package Upload

Only applicable to functions whose packaged size is under 500 MB. For packages over 500 MB, refer to the later section: Creating Functions Using a Container Image.

Package the program files, dependency library files, or model files in zip format (currently only zip format is supported and must be under 500 MB), for example:

```Shell
cd ./deps
zip -rq code.zip ./*
```

Upload code.zip to cloud object storage and grant the Singdata Lakehouse cloud role access to the corresponding path. The authorization process is not described in this development guide — refer to [Usage Guide: External Function](RemoteFunction-best-practice.md).
You can also specify an internal volume. Although you can use an internal volume, the code bucket parameter in your API CONNECTION creation must be filled with an external address.

* **User Volume address format**: `volume:user://~/upper.jar`
  * `user` indicates the User Volume protocol.

  * `~` represents the current user and is a fixed value.

  * `upper.jar` is the target filename.
* **Table Volume address format**: `volume:table://table_name/upper.jar`
  * `table` indicates the Table Volume protocol.
  * `table_name` is the table name; fill in as appropriate.
  * `upper.jar` is the target filename.

### Image-based Upload

Only applicable to functions whose packaged size exceeds 500 MB or that use GPU resources. Requires Alibaba Cloud Container Registry (free tier).

See the documentation: [Practice: Processing Image Data with a Hugging Face Image Recognition Model](RemoteFunction-on-acr.md)

^

## Example

Goal: Use a large language model (LLM) service to fill in the standardized **primary industry** and **secondary industry** for each company based on the **company name** column in a Singdata Lakehouse customer table. The result looks like this:

![](.topwrite/assets/20250612-171447.jpeg =675)

> ⚠️ **Note**: To complete this example, you need to:
>
> 1. Have Docker installed (mainly to ensure the development environment matches the environment where Singdata runs functions)
> 2. Have an Alibaba Cloud account with an API KEY for the Bailian platform. See [Alibaba Cloud Bailian](https://www.aliyun.com/product/bailian)
> 3. Have already created an API connection. See: [Create API Connection](create-api-connection.md)

### Step 1: Prepare the Development Environment

1. **Install Docker**: Ensure Docker is installed locally: <https://www.docker.com/>

2. **Pull the Docker image**. Run the following in your local command-line terminal (e.g., macOS Terminal):

   ```
   [Local]# docker pull quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779
   ```

3. **Start the Docker container**. This container is based on the `manylinux2014_x86_64` image and is configured to use the Python 3.10 environment:

   ```
   [Local]# docker run -it --name cz_func --env PATH="/opt/python/cp310-cp310/bin:$PATH" quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779 bash
   ```

> If the container has stopped, use the following commands to start and log in:
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

&#x20;    4\.  Create a folder named cz\_llm under the /root directory:

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

        # Set the API key
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

            # Handle the response
            if response.status_code == HTTPStatus.OK:
                # Non-streaming: directly get the full content
                if hasattr(response.output, 'choices') and len(response.output.choices) > 0:
                    if hasattr(response.output.choices[0].message, 'content'):
                        return response.output.choices[0].message.content
                    else:
                        return "Error: No content in response"
                else:
                    return "Error: No choices in response"
            else:
                # Return error information
                return f"Error: Request id: {response.request_id}, Status code: {response.status_code}, error code: {response.code}, error message: {response.message}"

        except Exception as e:
            # Return error information
            return f"Error: {str(e)}"

```

Test code:

```
if __name__ == "__main__":
    # Create instance
    llm = llm_call()
    
    # Configure parameters
    API_KEY = "sk-xxxxxx"  # Replace with your API key
    MODEL_NAME = "qwen-max"  # Or qwen-plus, qwen-max, etc.
    
    # Test example
    test_text = 'Xiaohongshu'
    test_prompt = 'Please return the standardized primary and secondary industry classification for this company, output directly: "primary industry":"xxx","secondary industry":"xxx", be concise'
    
    print("Calling LLM...")
    result = llm.evaluate(test_text, test_prompt, API_KEY, MODEL_NAME, 0, True)
    
    print(f"\nInput text: {test_text}")
    print(f"System prompt: {test_prompt}")
    print(f"LLM response: {result}")
```

### Step 2: Download Third-party Libraries

The program depends on the third-party package `dashscope`, which needs to be downloaded. (`os`, `http`, `json`, `sys` are Python built-in libraries and do not need to be downloaded. `cz.udf` will be added by the system automatically when the function is created.)

Run the following in the development environment command-line terminal:

```
[root@docker cz_llm]# pwd
/root/cz_llm

[root@docker cz_llm]# pip install dashscope -t .
```

The directory structure will look similar to this:

![](.topwrite/assets/external_func_2.jpeg)

^

### Step 3: Local Debugging

Make the following 3 modifications, since the `cz.udf` library is not loaded in the current environment:

```
...
2 #from cz.udf import annotate   # Comment out
...
8 #@annotate("*->string")  # Comment out
...
56 API_KEY = "sk-xxxxxx"  # Replace with your API key
```

The API\_KEY is the API KEY from the Alibaba Cloud Bailian platform. You need to register an Alibaba Cloud account, log in, and obtain it here: [Alibaba Cloud Bailian](https://bailian.console.aliyun.com/?spm=5176.12818093_47.console-base_search-panel.dtab-product_sfm.60852cc9WIq2Db\&scm=20140722.S_sfm._.ID_sfm-RL_%E5%A4%A7%E6%A8%A1%E5%9E%8B%E6%9C%8D%E5%8A%A1%E5%B9%B3%E5%8F%B0%E7%99%BE%E7%82%BC%E6%8E%A7%E5%88%B6%E5%8F%B0-LOC_console_console-OR_ser-V_4-P0_0\&tab=api#/api)

After commenting out the two lines above, save and exit the editor. Then run:

```
[root@docker cz_llm]# export PYTHONPATH="${_PWD}:${_PWD}/lib"
[root@docker cz_llm]# python cz_llm.py 
Calling LLM...

Input text: Xiaohongshu
System prompt: Please return the standardized primary and secondary industry classification for this company, output directly: "primary industry":"xxx","secondary industry":"xxx", be concise
LLM response: "primary industry":"Internet","secondary industry":"Social Media"
```

### Step 4: Package and Upload

Before packaging, uncomment the two lines commented out above:

```
...
2 from cz.udf import annotate   # Uncomment
...
8 @annotate("*->string")  # Uncomment
```

Run the packaging command, ensuring the current directory is the program directory (in this example, `/root/cz_llm`):

```
[root@docker cz_llm]# pwd
/root/cz_llm
[root@docker cz_llm]# zip -rq ../cz_llm.zip ./
[root@docker cz_llm]# ls ../
```

> 💡 **Tip**: If your environment does not have the zip command, try downloading it with `yum install zip`. If you encounter issues during the download, refer to the appendix "**Error When Installing Tools**".

You will find a `cz_llm.zip` file in the `/root` directory. Copy this file to the Lakehouse USER VOLUME object:

Run on the Docker host machine:

```
[Local]# docker cp cz_func:/root/cz_llm.zip ~/Downloads
```

Now `cz_llm.zip` is in the `Downloads` directory of the host machine's user.

Use the Lakehouse JDBC client (see [Lakehouse JDBC Client](connect-with-cli.md)) to put the file into the Lakehouse USER VOLUME:

```
PUT '/Users/derekmeng/Downloads/transform_company_id.zip' to USER VOLUME;
```

![](.topwrite/assets/external_functions_3.jpeg)

### Step 5: Create and Use the Function

This step requires you to have created an API connection in advance. See: [API Connection](create-api-connection.md)

```
CREATE EXTERNAL FUNCTION public.fc_cz_llm
    AS 'cz_llm.llm_call'   -- Main program filename (without .py extension).main class name
    USING ARCHIVE 'volume:user://~/cz_llm.zip' 
    connection sg_fc_api_conn -- API Connection must be created in advance
    WITH PROPERTIES (
        'remote.udf.api' = 'python3.mc.v0'
    )
COMMENT 'Usage: python get_industry_classification.py <text> <prompt> <api_key> <model_name> [temperature] [enable_search]';
```

The creation process takes about 1 minute. After creation, run the verification function (note: replace `'${api_key}'`):

```
SELECT    public.fc_cz_llm (
          'Singdata Technology',
          'Please return the standard industry classification, return JSON in English: {"primary industry":"xxx","secondary industry":"xxx"}',
          '${api_key}',
          'qwen-plus',
          '0.4',
          'true'
          ) AS llm_result;
```

Result:

![](.topwrite/assets/external_function_4.jpeg =660)

## Appendix

### Function Signatures

The function signature format is as follows:

```Python
@annotate(<signature>)
```

`signature` is a string used to identify the data types of input parameters and return values. When executing a UDF, the input parameter and return value types must match the types specified in the function signature. During query semantic parsing, any usage that does not conform to the function signature definition will be checked and an error will be reported if a type mismatch is detected. The specific format is as follows:

```Python
'arg_type_list -> type'
```

Where:

* `arg_type_list`: Represents the data types of the input parameters. Multiple input parameters are separated by commas (,). Supported data types are: BIGINT, STRING, DOUBLE, BOOLEAN, DATETIME, DECIMAL, FLOAT, BINARY, DATE, DECIMAL(precision,scale), CHAR, VARCHAR, complex data types (ARRAY, MAP, STRUCT), or nested complex data types.

* `arg_type_list` also supports an asterisk (\*) or empty ('')：

  * When `arg_type_list` is an asterisk (\*), it indicates that the function accepts any number of input parameters.
  * When `arg_type_list` is empty (''), it indicates no input parameters.

* `type`: Represents the data type of the return value. A UDF returns only one column. Supported data types are: BIGINT, STRING, DOUBLE, BOOLEAN, DATETIME, DECIMAL, FLOAT, BINARY, DATE, DECIMAL(precision,scale), complex data types (ARRAY, MAP, STRUCT), or nested complex data types.

Valid function signature examples:

| Function Signature Example | Description |
| --------------------------------------------- | -------------------------------------------------------- |
| `'bigint,double->string'` | Input parameter types are BIGINT and DOUBLE; return value type is STRING. |
| `'*->string'` | Accepts any number of parameters; return value type is STRING. |
| `'->double'` | No input parameters; return value type is DOUBLE. |
| `'array<bigint> -> struct<x:string>, y:int>'` | Input parameter type is ARRAY\<BIGINT>; return value type is STRUCT\<x\:string>, y\:int>. |
| '->map\<bigint, string>' | No input parameters; return value type is MAP\<BIGINT, STRING>. |

### Data Types

To ensure that the data types used when writing Python UDFs are consistent with those supported by Singdata Lakehouse, you need to be aware of the data type mapping between the two:

| Singdata Lakehouse Data Type | Python 3 Data Type |
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
| VARCHAR(n)        | str (write fails if over limit) |
| VOID              | NoneType               |

### Development Environment Image Installation

> **Applicable scenario: Avoiding Python ABI compatibility issues in non-Linux/non-X86-64 environments or when using third-party libraries containing native code**

During software development, especially when using Python for cross-platform work or interacting with low-level native code, Application Binary Interface (ABI) compatibility is an important consideration. When your development or deployment environment is a non-Linux system such as macOS or Windows, when the target device architecture is not X86-64 (e.g., ARM-based devices), or when the project uses third-party libraries compiled from C/C++ or other native code, the risk of potential ABI incompatibility increases significantly. To ensure the stability and portability of Python applications, it is strongly recommended to use a standardized build environment to download and compile these third-party dependencies.

**Recommended practice: Use the container**

For the specific scenarios mentioned — developing on a non-Linux system (such as macOS, Windows), a non-X86-64 device, or using third-party libraries containing native code — to avoid Python ABI compatibility issues, it is strongly recommended to use a Docker container based on `quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779` to download and build third-party dependencies.

#### How to proceed

1. **Install Docker**: Ensure Docker is installed on your development machine: <https://www.docker.com/>

2. **Pull the image**:

   ```
   docker pull quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779
   ```

   ^

3. Start the Docker container based on the `manylinux2014_x86_64` image, configured to use the Python 3.10 environment:

   ```
   docker run -it --name cz_func --env PATH="/opt/python/cp310-cp310/bin:$PATH" quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779 bash
   ```

You can now develop your Python External Function in this environment using Python 3.10.

> If the container has stopped, use the following commands to start and log in:
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

You should then see the Bash prompt inside the container (the exact prompt style may vary by image). For example, when printing the Python version, it should show the following:

```
[root@cfadeae5f8b0 /]# python --version
 Python 3.10.8
```

You have now successfully "logged in" to your `cz_func` container.

^

#### Common Issues with the Image

1\. **Error when installing tools**

For example, running `yum install zip` to install the `zip` packaging tool may produce errors like the following:

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

This error occurs because CentOS 7 reached its end of life (EOL) on June 30, 2024, and the official repositories have been moved to the CentOS vault. `mirrorlist.centos.org` no longer provides repository services for CentOS 7.

The solution is as follows:

First, check that the network connection is working normally.

If the network is fine, update the repository configuration to use the CentOS vault:

```
```

Back up the current repository files:

```
mkdir -p /etc/yum.repos.d/backup
cp /etc/yum.repos.d/CentOS-*.repo /etc/yum.repos.d/backup/

```

Update the repository URL to use vault.centos.org:

```
sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*.repo
sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*.repo

```

Clear the yum cache:

```
yum clean all

```

Now try installing zip again:

```
yum install zip
```

If you are in China or **vault.centos.org** is slow to access, you can use a domestic mirror source:

Use the Alibaba Cloud mirror:

```
sed -i 's|baseurl=http://vault.centos.org|baseurl=http://mirrors.aliyun.com/centos-vault|g' /etc/yum.repos.d/CentOS-*.repo
```

Or use the Tsinghua University mirror:

```
sed -i 's|baseurl=http://vault.centos.org|baseurl=https://mirrors.tuna.tsinghua.edu.cn/centos-vault|g' /etc/yum.repos.d/CentOS-*.repo
```

After making these changes, the `yum install zip` command should work normally.

^

**2**. **Copying files between Docker container and host machine**

Once you have generated a package, if you want to copy it from the container to the host machine or vice versa, use the following commands:

**Copy from container to host machine**:

```
```

docker cp container-name:container-path host-path, example:

```
docker cp cz_func:/root/gen_emmbedings.zip ~/Downloads
```

**Copy from host machine to container**:

```
```

docker cp host-path container-name:container-path # Example:

```
docker cp ~/Downloads/file.txt cz_func:/root/
```

**Notes**:

* The container can be running or stopped
* You can use either the container name or container ID
* Supports copying both files and directories: `docker cp` automatically detects whether the source is a file or directory

```
```

Copy an entire directory:

```
docker cp ~/project container-name:/root/
```

Copy directory contents:

```
docker cp ~/project/. container-name:/root/project/
```

^

* `docker cp` automatically detects whether the source is a file or directory

* When copying a directory, all subdirectories and files are copied recursively

* The destination path is created automatically if it does not exist

* Difference between trailing `/` and no trailing `/`:

  * `/app/logs` → copies the logs directory itself
  * `/app/logs/.` → copies only the contents inside the logs directory
