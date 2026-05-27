# A Comprehensive Guide to Importing Data into Singdata Lakehouse

## Data Ingestion: Using ZettaPark PUT File to Ingest Data

#### Overview

Using the Zettapark Python library provided by Singdata Lakehouse, you can upload the data generated in the test data generation step to the data lake managed by Singdata Lakehouse through Python programming, achieving data ingestion.

Data lake operations require creating a new data lake connection and Volume, and then you can Put data into the data lake.

#### Use Cases

Suitable for those familiar with Python programming, leveraging Python's powerful programming capabilities and flexibility to perform data cleaning, transformation, and other data engineering and preparation tasks using Python and Dataframe, especially tasks closely related to AI analysis.

#### Implementation Steps

You can also [download the file directly](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/a_comprehensive_guide_to_ingesting_data_into_clickzetta/put_data_to_datalake_by_Zettapark.ipynb) to your local machine.

##### **Put Local Files into the Data Lake Managed by Singdata Lakehouse (Volume) via Zettapark**
```Python
# !pip install clickzetta_zettapark_python  -i https://pypi.tuna.tsinghua.edu.cn/simple
```
```Python
from clickzetta.zettapark.session import Session
import json,requests
import os
from datetime import datetime
```
##### **Create a Session to Singdata Lakehouse**
```Python
# Read parameters from the configuration file
with open('config/config-ingest.json', 'r') as config_file:
    config = json.load(config_file)

print("Connecting to Singdata Lakehouse.....\n")

# Create session
session = Session.builder.configs(config).create()

print("Connection successful!...\n")
```
Connecting to Singdata Lakehouse.....

Connection successful!...

##### **PUT file to Singdata Lakehouse Data Lake Volume**

Please change 'data/' to the directory where the data generated in the 'Test Data Generation' step is stored.
```Python
for filename in os.listdir("data/"):
        if filename.endswith(".gz"):
            file_path = os.path.join("data/", filename)
            session.file.put(file_path,"volume://ingest_demo/gz/")
        if filename.endswith(".csv"):
            file_path = os.path.join("data/", filename)
            session.file.put(file_path,"volume://ingest_demo/csv/")
        if filename.endswith(".json"):
            file_path = os.path.join("data/", filename)
            session.file.put(file_path,"volume://ingest_demo/json/")
```
```Python
# Or upload all files in the directory
# session.file.put("../data/","volume://ingest_demo/gz/")
##### **Resynchronize the Data Lake Volume Directory to the Lakehouse**
```Python
session.sql(alter_datalake_sql).show()
```
\---------------------

|result\_message |

\---------------------

|OPERATION SUCCEED |

\---------------------

##### **Check the files on the Singdata Lakehouse data lake Volume again, the data has been successfully ingested**
```Python
results = session.sql("select * from directory(volume ingest_demo)").show()
```
\----------------------------------------------------------------------------------------------------------------------------

|relative\_path |url |size |last\_modified\_time |

\----------------------------------------------------------------------------------------------------------------------------

|gz/lift\_tickets\_data.csv.gz |oss\://yourbucketname/ingest\_demo/gz/lift\_ticket... |9717050 |2024-12-27 19:24:21+08:00 |

|gz/lift\_tickets\_data.json.gz |oss\://yourbucketname/ingest\_demo/gz/lift\_ticket... |11146044 |2024-12-27 19:24:19+08:00 |

\----------------------------------------------------------------------------------------------------------------------------

##### **Test pulling files from the data lake back to local**
```Python
session.file.get("volume://ingest_demo/gz/lift_tickets_data.json.gz","tmp/gz/")
```
\[GetResult(file='tmp/gz/lift\_tickets\_data.json.gz', size=11146044, status='DOWNLOADED', message='')]

##### Verify the number of rows in the data lake file

Data validation, check the number of rows in the file. The query result is 100000, which is the same as the number of rows in the original file. From the perspective of the number of rows, the data has been correctly ingested into the lake.
```Python
datalake_data_verify_sql = """
select count() from volume ingest_demo (txid string) using csv
 options(
    'header'='true',
    'sep'=',',
    'compression' = 'gzip'
 ) files('gz/lift_tickets_data.csv.gz')
 limit 10
"""
```
```Python
session.sql(datalake_data_verify_sql).show()
```
\-------------

|`count`() |

\-------------

|100000 |

\-------------

##### Query data in the data lake file
```Python
datalake_data_analytics_sql = """
select * from volume ingest_demo (txid string,name string, address_state string) using csv
 options(
    'header'='true',
    'sep'=',',
    'compression' = 'gzip'
 ) files('gz/lift_tickets_data.csv.gz')
 limit 10
"""
```
```Python
session.sql(datalake_data_analytics_sql).show()
```
\-------------------------------------------------------------------------------------

|txid |name |address\_state |

\-------------------------------------------------------------------------------------

|80a7a77b-4941-46f3-bf1a-760bb46f12da |0xbb6eabaf2eb3c3d2ea164eba |Xin Rong Ji |

|976b4512-1b07-43f4-a8e4-1fe86a7e1ee4 |0xa08ab7945cf87fc0b5095dc |Da Dong Roast Duck |

|4c49f5cc-0bd4-4a7e-8f61-f4a501a0dd24 |0xdf7bd805b890815a4e0a008c |Jing Ya Tang |

|8579071f-1c8b-4214-9a4d-096e6403bc52 |0x3113aa5ae86c522f3176829e |New Mainland Chinese Restaurant |

|31962471-ad3b-463d-ab36-d1b1ab041a36 |0x28c6168f44e09cacd82ecfe9 |Shun Feng Seafood Restaurant |

|f253d271-092d-4261-8703-a440cc149c39 |0xab306bea9de6a13426361153 |Chang An No.1 |

|5e52e443-2c03-4ce2-a95d-992d7cb3f54e |0x52000c48116d3a4667c3b607 |Yu Bao Xuan |

|e45f3806-972c-4617-b4ab-f2cbfc449de1 |0x247dd8c03cab559125a63d1b |Dian Ke Dian Lai |

|9abeadfa-ecac-42fb-9dd7-33377e2e5387 |0x9824bf4d4f7e12590f692148 |Chuan Ban Restaurant |

|c8938377-27a0-4f1f-9800-00c169729fd3 |0x4b65182989de9a3d13943b10 |Nan Men Hotpot |

\-------------------------------------------------------------------------------------

##### Close Zettapark Session
```Python
session.close()
```
#### Next Steps Recommendations

* Clean and transform data using Zettapark in Dataframe format
* Call ML and LLM related interfaces in Python code to deeply integrate Data+AI
* Analyze data in data lake files using SQL in Singdata Lakehouse Studio

#### Documentation

[Zettapark Quick Start](ZettaparkQuickStart.md)

^