# ClickZetta Travel: Data Migration and SQL Translation Tool

## Introduction

ClickZetta Travel is an open-source tool meticulously crafted by the Singdata development team, designed to help users easily migrate from other data systems to ClickZetta Lakehouse. It offers a range of powerful features, including:
- Translating other SQL dialects into SQL compatible with ClickZetta Lakehouse.
- Executing SQL on both the source data system and ClickZetta Lakehouse and comparing the consistency of the result sets.
- An easy-to-use Web UI that provides an intuitive interface.
- Command-line tools that support batch SQL migration.

## Installation and Startup

### Installation Steps

1. Ensure Docker is installed.
2. Obtain the Docker image for ClickZetta Travel using the following command:
```shell
# Get the image
docker pull clickzetta/clickzetta-travel:dev
```
3. Create a folder named `travel` locally to store the configuration and data needed for the evaluation:
```shell
mkdir travel
cd travel
```
### Start Web UI

Run the following command to start the ClickZetta Travel Web UI:
```shell
docker run --rm --name cztravel -v $(pwd):/mnt/userdata -p 8501:8501 clickzetta/clickzetta-travel:dev
```
Access http://localhost:8501/unify to use the Web UI.

## Usage

### Web Page Interactive Evaluation

#### Transpile SQL

1. Open http://localhost:8501/unify in your browser.
2. Select the data platform you are using.
3. Enter the SQL to be transpiled in the input box.
4. Use the shortcut keys (hinted at the bottom right of the input box) or let the input box lose focus. Once the input is effective, the page will automatically display the original and transpiled SQL side by side.

![transpile screenshot](travel_screenshot_transpile.png)

#### Execute SQL and Compare Results

1. Configure the database connection.
   - Expand the config template on the page to see the configuration file template.
   - Upload the edited configuration file through the page, or create a new conf subdirectory in the host machine's data directory and prepare the configuration file there. After refreshing the page, you can select it from the select config file section.
   - If the configuration file is correct, the page will display a connection success message.
2. Select the verification method and click the Validate button to run the SQL and verify the result set.
   - Basic verification: Verification based on limited basic statistical information.
   - Multidimensional verification: Verification based on rich statistical information.
   - Line by line verification: Line-by-line verification.

![validate screenshot](travel_screenshot_validate.png)

### Command Line Batch Evaluation

Collect the SQL statements to be evaluated and store the collected information in one or more files in the data directory. When a file contains multiple SQLs, they need to be separated by semicolons (;).
```shell
# Enter the docker command line environment
docker exec -it cztravel /bin/bash
# Switch to the data directory
cd /mnt/userdata
```
The batch evaluation command provided in the command-line environment is `travel`. This tool
- Accepts one or more SQL files with content separated by semicolons
- Identifies, splits, and numbers the SQL in the input files, translates them into ClickZetta Lakehouse SQL, and attempts to execute these SQL on the Lakehouse
- Produces a data directory, including evaluation summaries and runtime data. The runtime data includes successfully executed SQL, untranslatable SQL, and intelligently categorized execution-failed SQL
- You can get the latest help information through `travel --help`.

Example:
```shell
root@bce68cf855b8:/mnt/userdata#> travel -c conf/cz_conf.json batch-0906.sql

# Screen display continuously outputs running logs until the final running summary is given
summary:
original sql      : 777
transpiled        : 777, 100.00%
transpile failed  : 0, 0.00%
empty or set sql  : 1
valid for running : 776
run succeed       : 763, 98.32%
run failed        : 13, 1.68%

classified failed reasons:
reason_0        1       submit sql job failed:SQL job execute failed.Error:CZLH-00000:Failed to generate call action, function not found: IN(bin,bin...)->b
reason_1        2       submit sql job failed:SQL job execute failed.Error:CZLH-22007:DateTimeFormatter: pattern not supported ZONE_OFFSET_X - z : +0000; -08; -0830; -08:30; -083015; -08:30:15;. Detail  taskId 0, vertex name=stg4, vertexId=2023091814422045379827447_48514-V4
reason_2        2       submit sql job failed:SQL job execute failed.Error:CZLH-22007:DateTimeFormatter: unknown pattern letter: W. Detail  taskId 0, vertex name=stg0, vertexId=2023091814365582826010390_48392-V0
reason_3        2       submit sql job failed:SQL job execute failed.Error:CZLH-42000:[1,170] Semantic analysis exception - operator not found, string - string
...

# 2023-10-10_22-24-24 is the data directory produced by this run
# The last symbolic link always points to the data directory of the last run
root@bce68cf855b8:/mnt/userdata#> ls -l
total 18408
drwxr-xr-x@ 36 robert  staff   1.1K 10 10 22:48 2023-10-10_22-24-24/
-rw-r--r--@  1 robert  staff   9.0M 10 10 22:22 batch-0906.sql
drwxr-xr-x@  6 robert  staff   192B 10  8 19:03 conf/
lrwxr-xr-x@  1 robert  staff    19B 10 10 22:48 last@ -> 2023-10-10_22-24-24

# The data directory structure is shown below, and the data can be directly browsed and processed from the host machine
robert@Roberts-MBP ~/D/travel> tree last
last/
├── log.txt # All execution logs
├── reason_0
├── reason_1
│   ├── run.452.clickzetta.sql # Execution content of SQL No. 452 in Lakehouse
│   ├── run.452.doris.sql      # Original information of SQL No. 452
│   ├── run.776.clickzetta.sql
│   └── run.776.doris.sql
├── reason_2
...
├── success # Successfully executed SQL, can be used for subsequent stress testing
└── summary.txt # Summary

# The .clickzetta.sql file records the transpiled SQL content executed in Lakehouse, job id, reasons for failure, etc.
robert@Roberts-MBP ~/D/travel> cat last/reason_1/run.452.clickzetta.sql
WITH dt AS (SELECT ... DATE_FORMAT(`t1`.`created_at`, '%x') AS p, ... LIMIT 1000

-- exception for job_id: 2023091814422045379827447
-- submit sql job failed:SQL job execute failed.Error:CZLH-22007:DateTimeFormatter: pattern not supported ZONE_OFFSET_X - z : +0000; -08; -0830; -08:30; -083015; -08:30:15;. Detail  taskId 0, vertex name=stg4, vertexId=2023091814422045379827447_48514-V4
```