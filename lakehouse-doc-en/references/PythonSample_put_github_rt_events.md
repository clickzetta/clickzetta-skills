# Use Python Tasks to Fetch GitHub Events in Real-Time and Import into Lakehouse Table

<https://api.github.com/events> provides an API service that allows real-time access to event data from 5 minutes ago. By obtaining real-time data through the API and synchronizing offline data from the gharchive website via file, the data timeliness is improved from hourly to minute-level, further enhancing data freshness to better serve applications with higher requirements for data freshness.
This example also demonstrates how to use Singdata Lakehouse's [Python connect to bulkload data](use-python-sdk-upload-data.md) into a table.

## Create Target Table

Execute the following table creation statement in the SQL script task node.

```
CREATE TABLE IF NOT EXISTS `github_timeline_realtime_events` (

`id` STRING,

`type` STRING,

`repo_id` STRING,

`repo_name` STRING,

`minute` STRING,

`second` STRING,

`created_at` TIMESTAMP,

`data` STRING COMMENT 'record data, json format',

`__last_modified__` STRING COMMENT '__last_modified__'

) PARTITIONED BY (DATE STRING,HOUR STRING) COMMENT 'public GitHub timeline record,real time events, ingested from https://api.github.com/events';

```

## Writing Python Code

```
import requests,json

import time

import pytz

import pandas as pd

from requests.exceptions import RequestException

from datetime import datetime, timedelta

from clickzetta import connect

from clickzetta.bulkload.bulkload_enums import BulkLoadOptions,BulkLoadOperation,BulkLoadCommitOptions

def get_lakehouse_connect():

    conn = connect(

    username='',

    password='',

    service='api.clickzetta.com',

    instance='',

    workspace='gharchive',

    schema='public',

    vcluster='default')

    return conn

def get_lakehouse_queries_data_hints(sql_query,query_tag):

    conn = get_lakehouse_connect()

    # Execute SQL

    cursor = conn.cursor()

    my_param = dict()

    my_param["hints"] = dict()

    my_param["hints"]["query_tag"] =query_tag

    cursor.execute(sql_query, parameters=my_param)

    df = pd.DataFrame(cursor.fetchall(), columns=[i[0] for i in cursor.description])

    return df

def get_data(url, headers, params):

    retry_times = 5

    intervals = [10,30,60, 300, 600]

    

    for i in range(retry_times):

        try:

            response = requests.get(url, headers=headers, params=params)

            response.raise_for_status()

            return response

        except RequestException as e:

            print(f"Github API request {url} failed, attempt {i+1}: {e}")

            if response is None or response.status_code != 200:

                return None

            if i < retry_times - 1:

                time.sleep(intervals[i])

            else:

                return None

            

def bulk_load_data(real_time_events):

    try:

        bulkload_stream_conn = get_lakehouse_connect()

        bulkload_stream = bulkload_stream_conn.create_bulkload_stream(schema='public', table='github_timeline_realtime_events',record_keys=['id'],operation=BulkLoadOperation.UPSERT)

        if bulkload_stream:

            writer = bulkload_stream.open_writer(0)

            print("Successfully connected to the ClickZetta Lakehouse")

        for event in real_time_events:

            event_json = json.dumps(event)

            event_dict = json.loads(event_json)

            # print(f"event_dict is:\n\n{event_dict}")

            row = writer.create_row()

            row.set_value('id', event_dict['id'])

            row.set_value('type', event_dict['type'])

            row.set_value('repo_id', event_dict['repo']['id'])

            row.set\_value('repo_name', event_dict['repo']['name'])

            created_at_utc = datetime.strptime(event_dict['created_at'], '%Y-%m-%dT%H:%M:%SZ')

            created_at_e8 = created_at_utc + timedelta(hours=8)

            # Extract date (string)

            date_e8 = created_at_e8.strftime('%Y-%m-%d')

            # Extract hour (string)

            hour_e8 = created_at_e8.strftime('%H')

            # Extract minute (string)

            minute_e8 = created_at_e8.strftime('%M')

            # Extract second (string)

            second_e8 = created_at_e8.strftime('%S')

            row.set\_value('date', date_e8)

            row.set_value('hour', hour_e8)

            row.set_value('minute', minute_e8)

            row.set_value('second', second_e8)

            row.set_value('created_at', created_at_e8)

            

            row.set_value('data', event_json)

            

            row.set_value('__last\_modified__', created_at_e8)

            writer.write(row)

        writer.close()

        bulkload_stream.commit()

        print(f"{len(events)} events have been written to ClickZetta Lakehouse.")

        

    except Exception  as e:

        print("Error while connecting to ClickZetta Lakehouse,Exception is ", e)

    finally:

        print("finally ClickZetta Lakehouse connection is closed")

# tz = pytz.timezone('Asia/Shanghai')

# Initialize ETag and event list

etag = None

events = []

# Create a dictionary to store unique event IDs

seen_event_ids = {}

response = None

headers = {

    'Authorization': f'please replace your github token'

}

params = {'per_page': 100}

url = 'https://api.github.com/events'

while True:

    if etag:

        headers['If-None-Match'] = etag

    

    response = get_data(url, headers=headers, params = params)

    if response is not None:

        remaining = response.headers.get('X-RateLimit-Remaining')

        print(f"X-RateLimit-Remaining: {remaining}")

        ETag = response.headers.get('ETag')

        print(f"ETag: {ETag}")

        # Check response status

        if response.status_code == 200:

            # Update ETag

            etag = response.headers.get('ETag')

            

            # Get events and add to list

            new_events = response.json()

            

            for event in new_events:

                event_id = event.get('id')

                if event_id not in seen_event_ids:

                    events.append(event)

                    seen_event_ids[event_id] = True

            

            # Print event count

            print(f'Event count: {len(events)}')

            

        elif response.status_code == 304:

            print('response.status_code == 304, no new events.')

        else:

            print(f'response.status_code is {response.status_code}')

        # Sleep according to GitHub's X-Poll-Interval header

        # sleep_time = int(response.headers.get('X-Poll-Interval', 0))

        sleep_time = 0

        # Check if 'Link' header has 'next' keyword, if not, it means it's the last page

        if 'next' not in response.links:

            url = 'https://api.github.com/events'

            # time.sleep(sleep_time)

            if len(events)>=700:

                bulk_load_data(events)

                events.clear()

                seen_event_ids = {}

        else:

            # Update URL to the next page link

            url = response.links['next']['url']

```

## Running Tasks

Since this task is executed in a loop, after clicking "Run", the task will reside in the Python node, continuously fetching the latest events from GitHub and writing them into the Lakehouse table until manually canceled.
