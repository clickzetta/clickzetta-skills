# Using Python Tasks to Synchronize Data from the gharchive Website to Object Storage

The Python node in Lakehouse Studio provides the functionality for developing, testing, running, and scheduling Python code. By leveraging the scheduling feature, you can implement full data backfill tasks and periodic scheduling tasks with a single piece of code. Through scheduling task dependencies, you can orchestrate mixed workflows that include Python tasks, SQL tasks, Shell scripts, data integration, and other task types.

![](.topwrite/assets/image_1718681475743.png)

## Writing Python Code

```py
import os,io

import subprocess

from datetime import datetime, timedelta

import oss2

# Alibaba Cloud OSS configuration, ak\sk are custom parameters. Please modify ENDPOINT according to the actual OSS Region.

ACCESS_KEY_ID = '${ak}'

ACCESS_KEY_SECRET = '${sk}'

BUCKET_NAME = 'YourBucketName'

ENDPOINT = 'oss-cn-shanghai-internal.aliyuncs.com'

ROOT_PATH = 'ghachive'

# Get the current East 8th District time

# beijing_time = datetime.now()

beijing_time = datetime.strptime('${datetime}', "%Y-%m-%d %H:%M:%S")

# Get file time, Beijing time deviates by 9 hours (8 hours time difference, gharchive website produces data files 1 hour late, 8+1)

ny_time = beijing_time - timedelta(hours=9)

# Format time

year = ny_time.strftime('%Y')

month = ny_time.strftime('%m')

day = ny_time.strftime('%d')

hour = ny_time.strftime('%H')

# Print the converted time

print(f"Converted to data file Time and -9 hour: {year}-{month}-{day} {hour}:00:00")

# Determine if the hour is in '0x' format, if so, remove the leading 0

if hour.startswith('0') and len(hour) > 1:

# Remove the leading '0'

hour = hour[1:]


try:

    # Construct wget command
    
    url = f"https://data.gharchive.org/{year}-{month}-{day}-{hour}.json.gz"
    
    cmd = ["wget", "-qO-", url]
    
    print(f"wget cmd: {cmd}")
    
    # Execute wget command and capture output
    
    wget_output = subprocess.check_output(cmd)
    
    print(f"Wget file done...")
    
    # Convert output to in-memory file object
    
    file_obj = io.BytesIO(wget_output)

except Exception as e:

    print(f"An error occurred: {e}")
    
    file_obj = None

    # Add exception throwing, cooperate with task retry. Schedule is set to interval of 10 minutes, retry 3 times, to prevent source file from not being produced on time, improve robustness
    
    raise


if file_obj:

    try:
    
        # Initialize Alibaba Cloud OSS
        
        auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
        
        bucket = oss2.Bucket(auth, ENDPOINT, BUCKET_NAME)
        
        # Upload file to OSS
        
        oss_path = f"{ROOT_PATH}/{year}/{month}/{day}/{year}-{month}-{day}-{hour}.json.gz"
        
        print(f"osspath: {oss_path}")
        
        bucket.put_object(oss_path, file_obj)
        
        print(f"Put file to oss done...")
        
    except Exception as e:
        
        print(f"An error occurred: {e}")
        
    finally:
        
        # Close the in-memory file object
        
        file_obj.close()

```

## Run Test

Click "Run" to test the code and see if the results meet expectations.

## Scheduling Settings and Task Publishing

Since the gharchive website generates a new file every hour, set the scheduling period to 1 hour.

![](.topwrite/assets/image_1718680082074.png =683)

Then click "Submit" to complete the publishing. This way, the Python task can periodically schedule and complete the data synchronization of gharchive files to the cloud object storage OSS.

## Full Synchronization with Backfill

Periodic tasks are executed periodically from a specified time to obtain data. To get the full data before this time, you can directly use the same code and task to execute the "Backfill" task, which batch synchronizes all data before the earliest period of the periodic task, achieving full synchronization. This is very convenient and ensures logical consistency through the same set of code.
Click "Operations" to enter the operations page of the periodic task, and then click "Backfill".
The gharchive website provides files starting from 2012-02-12, so set the start time of the backfill task to 2012-02-12 00:00:00.
The periodic scheduling of this task starts at 11:00 on 2024-06-18, so set the end time of the backfill task to 2024-06-18 11:00:00.

![](.topwrite/assets/image_1718680764715.png)

Preview the instances of the backfill task. A total of 108251 task instances will be generated, which means there are 108251 hours in the above time period, and this backfill will synchronize 108251 files from the gharchive website to the cloud object storage.

![](.topwrite/assets/image_1718680957720.png =419)

## Task Orchestration

In subsequent task development, set this task as a dependent task to achieve workflow orchestration.
