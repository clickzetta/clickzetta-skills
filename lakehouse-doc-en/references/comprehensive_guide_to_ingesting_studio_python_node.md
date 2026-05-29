# A Comprehensive Guide to Importing Data into Singdata Lakehouse

## Data Ingestion: Loading Files from the Web into the Lakehouse via Singdata Lakehouse Studio's Built-in Python Node

#### Overview

Singdata Lakehouse Studio comes with a built-in Python node that allows you to develop and run Python code.

#### Use Case

This is suitable for scenarios where third-party Python libraries need to be called to process files during data ingestion. For example, in this case, the Python library for Alibaba Cloud Object Storage Service (OSS) is called.

#### Implementation Steps

##### Create a New Python Task

Navigate to Development -> Tasks, click "+", and create a new Python task.

Task Name: 05_Loading Files from the Web into the Lakehouse via Studio's Built-in Python Node.

:-: ![](.topwrite/assets/image_1736148972084.png =427)

##### Develop Python Task Code

Paste the [following code](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/a_comprehensive_guide_to_ingesting_data_into_clickzetta/py_data_to_datalake_from_web_by_python_node.py) into the code editor of the newly created Python task:

```Python
import os,io
import subprocess
from datetime import datetime, timedelta
import oss2

```

Alibaba Cloud OSS configuration:

```Python
ACCESS_KEY_ID = '${ak}'
ACCESS_KEY_SECRET = '${sk}'
BUCKET_NAME = 'yourbucketname'
ENDPOINT = 'oss-cn-hangzhou-internal.aliyuncs.com'
ROOT_PATH = f'{BUCKET_NAME}/ingest_demo/from_web'

try:
    # Construct wget command
    url = f"https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/a_comprehensive_guide_to_ingesting_data_into_clickzetta/data/lift_tickets_data.csv.gz"
    cmd = ["wget", "-qO-", url]
    print(f"wget cmd: {cmd}")

    # Execute wget command and capture output
    wget_output = subprocess.check_output(cmd)
    print(f"Wget file done...")

    # Convert output to an in-memory file object
    file_obj = io.BytesIO(wget_output)
except Exception as e:
    print(f"An error occurred: {e}")
    file_obj = None
    raise

if file_obj:
    try:
        # Initialize Alibaba Cloud OSS
        auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
        bucket = oss2.Bucket(auth, ENDPOINT, BUCKET_NAME)

        # Upload file to OSS
        oss_path = f"{ROOT_PATH}/lift_tickets_data.csv.gz"
        print(f"osspath: {oss_path}")
        bucket.put_object(oss_path, file_obj)
        print(f"Put file to oss done...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the in-memory file object
        file_obj.close()
```

##### Configure Parameters for the Task

There are two parameters:

ACCESS\_KEY\_ID = '${ak}'ACCESS\_KEY\_SECRET = '${sk}'

Click on the schedule to fill in the default values for the parameters:

:-: ![](.topwrite/assets/image_1736148983636.png =435)

Click "Load Parameters from Code" and fill in the corresponding values:

:-: ![](.topwrite/assets/image_1736148989712.png =431)

##### Run the Test

Click "Run" to execute the Python code.

:-: ![](.topwrite/assets/image_1736148997078.png =427)

##### Check the Upload Results

Log in to Alibaba Cloud Object Storage to view the uploaded files.

:-: ![](.topwrite/assets/image_1736149004171.png =415)

#### Next Steps

* Schedule Python tasks to achieve periodic data lake ingestion.
* Analyze the files loaded into the data lake using SQL.
* Form a complete ELT workflow with other tasks.

#### Resources

[Studio Python Task Node](python-task.md)
