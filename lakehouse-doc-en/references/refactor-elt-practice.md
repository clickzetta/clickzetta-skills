# Redefining ELT: A New Approach to ELT with Singdata Lakehouse

## Problems and Challenges

In many data projects, especially those closely related to ML and AI, development often requires a mix of Python and SQL. For example, Python code is developed via Jupyter Notebook, while SQL code is developed using data management and development tools like DBeaver or VS Code. This approach frequently leads to issues such as a lack of version management and the absence of a unified scheduling service, making development and operations complex and difficult.

As modern data stacks evolve, next-generation BI and AI analysis products such as Metabase and MindsDB are also rapidly advancing. How a data platform tightly integrates into the modern data stack to provide a complete solution has become critically important.

For the growing volume of semi-structured data and vector data (such as CSV and JSON), relying on client-side parsing severely impacts overall processing speed. This demands that the data platform be capable of high-performance processing of structured data in tables as well as JSON data and vector data simultaneously. For example, the hourly GitHub event archive dataset provided by GH Archive is delivered in JSON format.

In data engineering tasks involving data cleaning and transformation, many intermediate tables often need to be developed before reaching the final target table. Improving efficiency in this area has become an important topic for boosting data engineer productivity.

## A New ELT Approach with Singdata Lakehouse

The author attempts to use Singdata Lakehouse to find new solutions to the above problems from the following three perspectives.

![](.topwrite/assets/image_1734348544459.png)

### Unified Data Task Development and Scheduling

Simplify the data task development and operations environment through Singdata Lakehouse, achieving unified task version management:

* [Python Task Development](python-task.md): From Jupyter Notebook development to Python task development in Singdata Lakehouse Studio.

* [SQL Task Development](task-develop.md): From DBeaver SQL task development to SQL task development in Singdata Lakehouse Studio.

* [ML/AI Task Development](jdbc_task.md): From MindsDB Web IDE to JDBC task development in Singdata Lakehouse Studio.

* [Task Scheduling and Operations](task-instance-maintenance.md): From Airflow to task scheduling and operations in Singdata Lakehouse Studio.


### [Multi-Data-Type Support](data-type.md)

Singdata Lakehouse supports efficient storage and access for the following data types:

* Common basic data types in tables

* Common complex data types in tables

* JSON

* Vector

* Full-text inverted index


### [Dynamic Table](dynamic-table.md)

The Dynamic Table provided by Singdata has the following typical features:

* Declarative Programming: Use declarative SQL to define pipeline results without having to consider intermediate table logic, reducing complexity.
* Transparent Orchestration: Manage refresh orchestration and scheduling by chaining together Dynamic Tables and regular tables.
* Incremental Processing: Suitable for incremental workloads with excellent Dynamic Table performance.
* Easy Switching: A single command transitions from batch processing to streaming processing, balancing cost and freshness.
* Observability: Dynamic Tables can be managed through the Singdata Lakehouse Web Console Studio, improving observability.


^

## Application Case: GHArchive Data ELT Implementation

![](.topwrite/assets/image_1734348838607.png)

### Data Source Introduction: [GHArchive](http://www.gharchive.org/)

Open-source developers worldwide are engaged in millions of projects covering tasks such as writing code and documentation, fixing bugs, and submitting work. The [GH Archive](http://www.gharchive.org/) project records public GitHub event data, providing over 13 years of GitHub event data archives starting from February 12, 2011, and making the data more accessible for further analysis.

GitHub has over 15 event types, such as new commits (Push), forking a repository (Fork), creating new Issues, commenting, and adding members to projects. These events are aggregated into hourly archive files accessible via any HTTP client. Each archive file encodes events as reported by the GitHub API in JSON format. Users can download the raw data for self-processing, such as writing custom aggregation scripts or importing it into a database.

Example GitHub event data:

```
{"id":"44809399421","type":"CreateEvent","actor":{"id":81469924,"login":"temperature48","display_login":"temperature48","gravatar_id":"","url":"https://api.github.com/users/temperature48","avatar_url":"https://avatars.githubusercontent.com/u/81469924?"},"repo":{"id":903968841,"name":"temperature48/SmashVat","url":"https://api.github.com/repos/temperature48/SmashVat"},"payload":{"ref":null,"ref_type":"repository","master_branch":"master","description":null,"pusher_type":"user"},"public":true,"created_at":"2024-12-16T02:00:00Z"}
```

^

### Development Task: Data Extraction (**E**xtract)

Next, we develop a Python task through Singdata Lakehouse Studio to extract data from the GH Archive website into data lake storage (this solution uses Alibaba Cloud OSS).


^

```py
import os,io
import subprocess
from datetime import datetime, timedelta
import oss2

# Alibaba Cloud OSS configuration
ACCESS_KEY_ID = '${ak}'
ACCESS_KEY_SECRET = '${sk}'
BUCKET_NAME = 'OSS Bucket Name'
ENDPOINT = 'Alibaba Cloud OSS Endpoint'
ROOT_PATH = 'ghachive, replace with the actual root directory under the bucket'

# Get current time in UTC+8
# beijing_time = datetime.now() 
beijing_time = datetime.strptime('${datetime}', "%Y-%m-%d %H:%M:%S")

# Get file time; Beijing time offset by 9 hours (8 hours time zone + 1 hour for gharchive data file delay)
ny_time = beijing_time - timedelta(hours=9)

# Format time
year = ny_time.strftime('%Y')
month = ny_time.strftime('%m')
day = ny_time.strftime('%d')
hour = ny_time.strftime('%H')

# Print converted time
print(f"Converted to data file Time and -9 hour: {year}-{month}-{day} {hour}:00:00")

# Check if hour is in '0x' format, and if so remove leading zero
if hour.startswith('0') and len(hour) > 1:
    # Remove leading '0'
    hour = hour[1:]

try:
    # Build wget command
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
        # Close in-memory file object
        file_obj.close()
```

^

### Development Task: Data Loading (**L**oad)

Singdata Lakehouse Studio supports loading data from data lakes into Lakehouse tables via offline sync tasks, storing it in optimized formats and enabling fine-grained permission management.


^

### Development Task: Data Cleaning and Transformation (**T**ransform)

Singdata Lakehouse Dynamic Tables support incremental refresh optimization by processing only changed data. Compared to traditional ETL tasks, Dynamic Tables eliminate the need for full data computation and do not require specifying incremental logic (such as partition alignment or using max(system/event_time)). Users simply declare the business logic, and the Dynamic Table automatically performs incremental computation optimization.

This article uses Dynamic Tables for data cleaning and transformation.


^

#### Ad Hoc Data Analysis

Singdata Lakehouse has a built-in, convenient SQL query interface where you can freely write SQL code, use variables, select clusters, and perform flexible ad hoc data analysis. It is also convenient for debugging.


^

#### Development Task: AI/ML Enhanced Analysis

Based on the JDBC task nodes provided by Lakehouse Studio, you can conveniently connect to MindsDB for enhanced data analysis.


^

### Incremental Sync Task Scheduling

Configure scheduling and dependency relationships for the ELT tasks just developed, ensuring tasks run on an hourly cycle. Submit and publish the tasks so that GitHub event data can be synced hourly from GHArchive (with a one-hour lag) and cleaned and transformed.


^

### Backfilling Full Data

For data backfill tasks in Singdata Lakehouse Studio, you can fully reuse the incremental tasks. Simply configure and execute the backfill task with the start and end dates for the full data range to backfill historical data.

Taking GHArchive data as an example, its website (http://www.gharchive.org/) has data starting from February 12, 2011. Configure the backfill task as shown below and run it to achieve full data sync. Backfill tasks can run concurrently with incremental data sync tasks, and there is no need to develop a new full sync task.


^
^

### Task Operations

Singdata Lakehouse Studio also provides comprehensive operations interfaces, such as displaying upstream and downstream DAG relationships for tasks, running status, and performing operations like reruns.

^


^
^

## Summary

This article discusses the problems and challenges of traditional development approaches in data projects, especially those closely tied to ML and AI, and how to implement a new ELT approach for GHArchive using Singdata Lakehouse -- enabling unified development, scheduling, and operations, significantly streamlining the product components in the solution, and helping to greatly improve efficiency and reduce management costs. Key takeaways include:

* **Unified Data Task Development and Scheduling**: Simplify development and operations environments; achieve consistent task version management covering Python, SQL, and ML/AI task development, as well as unified task scheduling orchestration and operations control.
* **Multi-Data-Type Support**: Efficient storage and access for common basic data types, complex data types, JSON, Vector, full-text inverted indexes, and more.
* **Dynamic Table**: Features declarative programming, transparent orchestration, incremental processing, easy switching, and observability.
* **Application Case**: Using GHArchive data to demonstrate data extraction, loading, cleaning and transformation, ad hoc data analysis, AI/ML enhanced analysis, incremental sync task scheduling, full data backfilling, and task operations.

## References

* [Singdata Lakehouse Dynamic Table](dynamic_table_summary.md)
* [Singdata Lakehouse Studio Task Development and Scheduling](task-develop.md)
* [Data Backfill Tasks](backfilling_data.md)
* [Singdata Lakehouse JSON Data Type](json.md)
* [Singdata Lakehouse Vector Data Type](vector-type.md)

^
