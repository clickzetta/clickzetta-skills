# External Function Development Guide (Python3)

## Objective:

The objective of this document is to help developers master writing custom functions (UDF) in Python to process data in the Singdata Lakehouse.

## Usage Restrictions:

> * Only supports Python 3.10 version
> * If relying on native libraries (libraries containing .so), they need to be compatible with Python 3.10 ABI
> * Supports zip format program packages
> * If the program and dependency files exceed 500M after compression, you need to create the function using a container image. Please refer to [Practice: Using Hugging Face Image Recognition Model to Process Image Data](remotefunctiononacr.md)

## Code Structure:

The code structure of a Python function is divided into the following parts:

* **Import Modules**: Mandatory. Must at least include `from cz.udf import annotate`, to import the function signature module, so that Singdata Lakehouse can recognize the function signatures defined in the subsequent code.
* **Function Signature**: Mandatory. The format is `@annotate(<signature>)`, `signature` is used to define the data types of the function's input parameters and return values. More function signature information.
* **Custom Python Class**: Mandatory. The organizational unit of UDF code, defining the variables and methods that implement business requirements. You can also reference third-party libraries or reference file and table resources in the code.
* **evaluate** **Method**: Mandatory. Located within the custom Python class. The `evaluate` method defines the input parameters and return values. A Python class can only contain one `evaluate` method.

> Based on the above code structure, the code for a function that converts characters to uppercase is as follows:

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

## 4. Install Third-Party Libraries:

Take downloading httpx and pydantic as an example:

```Shell
mkdir ./deps
pip3 install -t ./deps httpx pydantic
```

> Note: When you are using macOS / Windows or other non-Linux systems, or using non-X86-64 devices, or using third-party libraries that include native code, to avoid Python ABI compatibility issues, it is strongly recommended to use a container based on `quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779` to download third-party dependencies:

```Python
mkdir ./deps
docker run -v `pwd`/deps:/root/deps \
    quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779 \
    /opt/python/cp310-cp310/bin/pip3 install \
        -i https://pypi.tuna.tsinghua.edu.cn/simple \
        -t /root/deps httpx pydantic
```

## Upload Function

### Upload, Compressed Package Upload

Only applicable for functions smaller than 500M after packaging. For functions larger than 500M, please refer to the subsequent chapters: Creating Functions Using Images

Package the program files, dependency library files, or model files into a zip format (currently only zip format files smaller than 500M are supported), for example

```Shell
cd ./deps
zip -rq code.zip ./*
```

Upload `code.zip` to the cloud object storage and authorize the corresponding path to be accessible by the cloud role of Singdata Lakehouse; the authorization process is not described in the development guide, please refer to [Usage Process: External Function](remotefunctionbestpractice.md).

### Upload via Image:

Only applicable for functions larger than 500M after packaging, or functions using GPU resources; you need to enable Alibaba Cloud Container Image Service (free).

Please refer to the document: [Practice: Using Hugging Face Image Recognition Model to Process Image Data](remotefunctiononacr.md)

^

# Appendix:

## Function Signature:

The function signature format is as follows.

```Python
@annotate(<signature>)
```

`signature` is a string used to identify the data types of input parameters and return values. When executing a UDF, the input parameters and return values of the UDF function must match the types specified by the function signature. During the query semantic parsing phase, usages that do not conform to the function signature definition will be checked, and a type mismatch error will be reported if detected. The specific format is as follows.

```Python
'arg_type_list -> type'
```

Where:

* `arg_type_list`：Indicates the data type of the input parameters. Multiple input parameters can be separated by commas (,). Supported data types are BIGINT, STRING, DOUBLE, BOOLEAN, DATETIME, DECIMAL, FLOAT, BINARY, DATE, DECIMAL(precision, scale), CHAR, VARCHAR, complex data types (ARRAY, MAP, STRUCT), or nested complex data types.

* `arg_type_list` also supports asterisk (\*) or empty (''):

  * When `arg_type_list` is an asterisk (\*), it means the input parameters can be of any number.
  * When `arg_type_list` is empty (''), it means there are no input parameters.

* `type`：Indicates the data type of the return value. UDF only returns one column. Supported data types are: BIGINT, STRING, DOUBLE, BOOLEAN, DATETIME, DECIMAL, FLOAT, BINARY, DATE, DECIMAL(precision, scale), complex data types (ARRAY, MAP, STRUCT), or nested complex data types.

Examples of valid function signatures are as follows:

|                                                 |                                                                                           |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Function Signature Example                      | Description                                                                               |
| 'bigint,double->string'                         | Input parameter types are BIGINT, DOUBLE, return value type is STRING.                    |
| '\*->string'                                    | Any number of input parameters, return value type is STRING.                              |
| '->double'                                      | No input parameters, return value type is DOUBLE.                                         |
| 'array\<bigint> -> struct\<x\:string>, y\:int>' | Input parameter type is ARRAY\<BIGINT>, return value type is STRUCT\<x\:string>, y\:int>. |
| '->map\<bigint, string>'                        | No input parameters, return value type is MAP\<BIGINT, STRING>.                           |

## Data Types：

To ensure that the data types used in the process of writing Python UDFs are consistent with the data types supported by Singdata Lakehouse, you need to pay attention to the data type mapping relationship between the two:

| Singdata Lakehouse Data Type | Python 3 Data Type     |
| ---------------------------- | ---------------------- |
| BIGINT                       | int                    |
| BOOLEAN                      | bool                   |
| CHAR                         | unicode                |
| DATE                         | datatime.date          |
| DECIMAL                      | decimal.Decimal        |
| DOUBLE                       | float                  |
| FLOAT                        | float                  |
| INT                          | int                    |
| SMALLINT                     | int                    |
| STRING                       | str                    |
| TIMESTAMP\_LTZ               | datetime.datetime      |
| TINYINT                      | int                    |
| ARRAY                        | list                   |
| MAP                          | list                   |
| STRUCT                       | collections.namedtuple |
| VARCHAR(n)                   | str(write failure on exceeding limit)            |
| VOID                         | NoneType               |

^
