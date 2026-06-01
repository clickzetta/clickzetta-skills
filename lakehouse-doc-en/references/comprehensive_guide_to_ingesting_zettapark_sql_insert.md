# A Comprehensive Guide to Importing Data into Singdata Lakehouse

## Data Ingestion: Loading Data via SQL INSERT through Zettapark

#### Overview

Singdata Lakehouse provides [Zettapark](zettaparkquickstart.md) compatible with PySpark, allowing data to be loaded into Singdata Lakehouse tables through Python and SQL programming in popular IDEs (such as VS Code).

#### Use Cases

This method allows for easy execution of SQL and file uploads. One way to load data is by executing SQL INSERT statements for each record, suitable for uploading small amounts of data in a Python programming environment. Although this is a convenient way to insert data, it is not efficient for loading large volumes of data, as Singdata Lakehouse is not a traditional database but is optimized for writing large volumes of data.

#### Implementation Steps

Open VS Code on your computer, create a file named [py\_zettapark\_sql\_insert.py ](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/a_comprehensive_guide_to_ingesting_data_into_clickzetta/py_zettapark_sql_insert.py), and copy the following code into the py\_zettapark\_sql\_insert.py file.

```JSON
import json,gzip
from clickzetta.zettapark.session import Session
from datetime import datetime

```

Read parameters from the configuration file:

```JSON
with open('config-ingest.json', 'r') as config_file:
    config = json.load(config_file)

print("Connecting to Singdata Lakehouse.....\n")

```

Create session:

```JSON
session = Session.builder.configs(config).create()

print("Connection successful!...\n")

target_table_name = "lift_tuckets_import_by_py_insert"

create_target_table_query = f"""
CREATE TABLE if not exists ql_ws.ingest.{target_table_name}(
  `txid` string,
  `rfid` string,
  `resort` string,
  `purchase_time` timestamp_ltz,
  `expiration_time` date,
  `days` int,
  `name` string,
  `address_street` string,
  `address_city` string,
  `address_state` string,
  `address_postalcode` string,
  `phone` string,
  `email` string,
  `emergency_contact_name` string,
  `emergency_contact_phone` string)
"""
session.sql(create_target_table_query).collect()

def save_to_clickzetta(session, message):
    record = json.loads(message)
    print('inserting record to Singdata Lakehouse')

    # Convert date and time fields
    purchase_time = datetime.strptime(record['purchase_time'], '%Y-%m-%d %H:%M:%S')
    expiration_time = datetime.strptime(record['expiration_time'], '%Y-%m-%d').date()

    row = (
        f"'{record['txid']}'", f"'{record['rfid']}'", f"'{record['resort']}'", 
        f"timestamp_ltz '{record['purchase_time']}'", f"date '{record['expiration_time']}'", 
        record['days'], f"'{record['name']}'", f"'{record['address_street']}'", 
        f"'{record['address_city']}'", f"'{record['address_state']}'", 
        record['address_postalcode'], record['phone'], 
        f"'{record['email']}'", f"'{record['emergency_contact_name']}'", 
        record['emergency_contact_phone']
    )

    sql_query = f"""
    INSERT INTO ql_ws.ingest.{target_table_name} 
    (TXID, RFID, RESORT, PURCHASE_TIME, EXPIRATION_TIME, DAYS, NAME, ADDRESS_STREET, ADDRESS_CITY, ADDRESS_STATE, ADDRESS_POSTALCODE, PHONE, EMAIL, EMERGENCY_CONTACT_NAME, EMERGENCY_CONTACT_PHONE) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    session.sql(sql_query, row).collect()
    print(f"inserted ticket {record}")

if __name__ == "__main__":
    # Open the JSON file and read the content
    with gzip.open('lift_tickets_data.json.gz', 'rt', encoding='utf-8') as file:
        for message in file:
            if message.strip():  # Ensure it's not an empty line
                save_to_clickzetta(session, message)
    
    session.close()
    print("Ingest complete")

```

In VS Code, open a new "Terminal" and run the following command to activate the Python environment created in the "Environment Setup" step. If you are already in the cz-ingest-examples environment, please skip this step.

```Shell
conda activate cz-ingest-examples
```

Then run the following command in the same terminal:

```Shell
python py_zettapark_sql_insert.py
```

#### Next Steps Recommendations

Optimization: This is not an efficient method for loading large amounts of data. You can improve performance by increasing task concurrency and inserting multiple records with each INSERT INTO.

#### Resources

[SQL Insert Into](insert.md)

[Zettapark Quick Start](zettaparkquickstart.md)
