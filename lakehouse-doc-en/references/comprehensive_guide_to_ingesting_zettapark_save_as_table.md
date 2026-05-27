# A Comprehensive Guide to Importing Data into Singdata Lakehouse

## Data Ingestion: Loading Data via Zettapark using SAVE\_AS\_TABLE

#### Overview

#### Use Cases

The SAVE\_AS\_TABLE method automatically creates tables, simplifying the process of loading data via Zettapark using SQL INSERT, which requires manual table creation. Additionally, SAVE\_AS\_TABLE automatically optimizes INSERT INTO, inserting multiple records at once instead of one at a time.

#### Implementation Steps

Open VS Code on your computer, create a file named [py\_zettapark\_save\_as\_table.py](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/a_comprehensive_guide_to_ingesting_data_into_clickzetta/py_zettapark_save_as_table.py), and copy the following code into the py\_zettapark\_save\_as\_table.py file.
```Python
import json
import gzip
from clickzetta.zettapark.session import Session
from datetime import datetime

# Read parameters from the configuration file
with open('config-ingest.json', 'r') as config_file:
    config = json.load(config_file)

print("Connecting to Singdata Lakehouse.....\n")

# Create session
session = Session.builder.configs(config).create()

print("Connection successful!...\n")

target_table_name = "lift_tuckets_import_by_py_save_as_table"

def save_as_table_to_clickzetta(session, schema, data):
    print('Saving data to Clickzetta Lakehouse')

    # Convert data to dataframe
    df = session.create_dataframe(data, schema=schema)
    
    # Save dataframe as table
    df.write.save_as_table(target_table_name, mode="overwrite", table_type="transient")
    print(f"Data saved to table {target_table_name}")

if __name__ == "__main__":
    schema = None
    data = []

    # Open the compressed JSON file and read the content
    with gzip.open('lift_tickets_data.json.gz', 'rt', encoding='utf-8') as file:
        for message in file:
            if message.strip():  # Ensure it's not an empty line
                record = json.loads(message)
                if 'schema' in record:
                    schema = record['schema']
                else:
                    data.append(record)
    
    save_as_table_to_clickzetta(session, schema, data)
    session.close()
    print("Ingest complete")
```
In VS Code, open a new "Terminal" and run the following command to activate the Python environment created in the "Environment Setup" step. If you are already in the cz-ingest-examples environment, please skip this step.
```
conda activate cz-ingest-examples
```
Then run the following command in the same terminal:
```
python py_zettapark_save_as_table.py
```
#### Next Steps Recommendations

#### Resources

[Zettapark Quick Start](ZettaparkQuickStart.md)