# Complete Guide to Importing Data into Singdata Lakehouse

## Data Ingestion: Real-time Multi-table Synchronization via Singdata Lakehouse Studio (CDC, Public Network Connection)

#### Overview

#### Use Case

Existing data sources (including databases and data warehouses) have publicly accessible addresses (such as through public NAT mapping), require simultaneous multi-table synchronization, have high data freshness requirements (often at the minute or even second level), and can accept higher synchronization costs to synchronize data from source tables to Lakehouse tables.

Singdata Lakehouse Studio's real-time multi-table synchronization supports multi-table merging, allowing data from multiple source tables in a structured system to be merged into a single Singdata Lakehouse target table.

#### Implementation Steps

##### Create a New Real-time Multi-table Synchronization Task

Navigate to Development -> Tasks, click "+", select "Real-time Multi-table Synchronization", and create a new real-time multi-table synchronization task.

:-: ![](.topwrite/assets/image_1736147975347.png =494)

Task Name: 06\_multi\_table\_rt\_sync\_from\_pg

##### Select "PostgreSQL" as the Source Data

:-: ![](.topwrite/assets/image_1736147983573.png =502)

##### Select Synchronization Objects

Singdata Lakehouse Studio will automatically synchronize the source database structure for selection:

:-: ![](.topwrite/assets/image_1736147992225.png =467)

##### Database CDC Configuration

Create a Slot

:-: ![](.topwrite/assets/image_1736148001087.png =459)

Plugin Type: pgoutput

Slot Name: slot\_for\_multi\_table\_ingest\_demo

##### Target Configuration

Rule Expression: multitable\_sync\_{SOURCE\_TABLE}. Add the prefix multitable\_sync\_{SOURCE\_TABLE} to the target table to distinguish it from tables synchronized by other methods.

Check field mapping to ensure all mappings are successful:

:-: ![](.topwrite/assets/image_1736148015509.png =445)

##### Configure Synchronization Rules

:-: ![](.topwrite/assets/image_1736148027202.png =443)

##### Submit

Submit the real-time multi-table synchronization task after configuration:

:-: ![](.topwrite/assets/image_1736148034594.png =427)

##### Operations and Maintenance

Maintain the real-time multi-table synchronization task:

:-: ![](.topwrite/assets/image_1736148045501.png =425)

##### Start

Start the real-time multi-table synchronization task:

:-: ![](.topwrite/assets/image_1736148052375.png =426)

For the first start of this real-time multi-table synchronization task, select "Stateless Start" and "Full Data Synchronization":

:-: ![](.topwrite/assets/image_1736148058726.png =426)

After starting, you can view the detailed status of the task. Once the full synchronization is complete, the system will automatically begin incremental real-time synchronization.

##### Progress Monitoring

Full synchronization in progress:

:-: ![](.topwrite/assets/image_1736148083158.png =446)

Full synchronization complete.

Real-time synchronization begins:

:-: ![](.topwrite/assets/image_1736148107686.png =430)

##### Incremental Real-time Synchronization

Insert incremental data into the PG database for incremental real-time synchronization. Create a new file in VS Code named “[rt\_data\_generate\_insert\_into\_pg.py](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/a_comprehensive_guide_to_ingesting_data_into_clickzetta/rt_data_generate_insert_into_pg.py)” and copy the following code into it:
```py
import os
import sys
import rapidjson as json
import optional_faker as _
import uuid
import random
import time
import psycopg2
from faker import Faker
from datetime import date, datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
fake = Faker('en_US')  # Use English locale
resorts = ["The Golden Duck", "Jing Yaa Tang", "Xin Rong Ji", "Fangshan Restaurant", "Quanjude", 
           "Li Qun Roast Duck", "Din Tai Fung", "Haidilao", "Jiangsu Club", "The Guest House",
           "Zhou Hei Ya", "Night Shanghai", "Xiang Palace", "Chang'an No.1", "Jade Restaurant", "Beijing Hotel",
           "Sichuan Bean Flower", "Haidilao Hot Pot", "Chuanban Restaurant", "Nanmen Hot Pot",
           "Hutong", "Jade Garden", "Lei Garden", "Imperial Treasure", "Jindingxuan", 
           "Grandma's Home", "Da Dong", "Shunfeng Seafood", "Xiaolongkan Hot Pot",
           "New World Chinese", "King's Joy", "Din Tai Fung (Taiwan)", "Dianchi Visitor", 
           "Green Wave Pavilion", "South America Time"]

# Load database credentials from environment variables
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
DB_HOST = 'localhost'
DB_PORT = '5432'

def connect_db():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

def random_date_in_2025():
    start_date = date(2025, 1, 1)
    end_date = date(2025, 12, 31)
    return start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

def random_datetime_between(start_year, end_year):
    start_datetime = datetime(start_year, 1, 1)
    end_datetime = datetime(end_year, 12, 31, 23, 59, 59)
    random_seconds = random.randint(0, int((end_datetime - start_datetime).total_seconds()))
    return start_datetime + timedelta(seconds=random_seconds)

def insert_lift_ticket(cursor, lift_ticket):
    cursor.execute("""
        INSERT INTO ingest_demo.lift_tickets_data (txid, rfid, resort, purchase_time, expiration_time, days, name, address_street, address_city, address_state, address_postalcode, phone, email, emergency_contact_name, emergency_contact_phone)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        lift_ticket['txid'], lift_ticket['rfid'], lift_ticket['resort'],
        lift_ticket['purchase_time'], lift_ticket['expiration_time'],
        lift_ticket['days'], lift_ticket['name'], lift_ticket['address_street'],
        lift_ticket['address_city'], lift_ticket['address_state'],
        lift_ticket['address_postalcode'], lift_ticket['phone'],
        lift_ticket['email'], lift_ticket['emergency_contact_name'],
        lift_ticket['emergency_contact_phone']
    ))

def generate_lift_ticket():
    global resorts, fake
    lift_ticket = {
        'txid': str(uuid.uuid4()),
        'rfid': hex(random.getrandbits(96)),
        'resort': fake.random_element(elements=resorts),
        'purchase_time': random_datetime_between(2021, 2024),
        'expiration_time': random_date_in_2025(),
        'days': fake.random_int(min=1, max=7),
        'name': fake.name(),
        'address_street': fake.street_address(),
        'address_city': fake.city(),
        'address_state': fake.province(),
        'address_postalcode': fake.postcode(),
        'phone': fake.phone_number(),
        'email': fake.email(),
        'emergency_contact_name': fake.name(),
        'emergency_contact_phone': fake.phone_number(),
    }
    return lift_ticket

def main(total_count, batch_size, sleep_time):
    conn = connect_db()
    cursor = conn.cursor()
    
    batch_data = []
    for _ in range(total_count):
        lift_ticket = generate_lift_ticket()
        batch_data.append(lift_ticket)
        
        if len(batch_data) >= batch_size:
            for ticket in batch_data:
                insert_lift_ticket(cursor, ticket)
            conn.commit()
            batch_data = []
            time.sleep(sleep_time)
    
    # Insert any remaining data
    if batch_data:
        for ticket in batch_data:
            insert_lift_ticket(cursor, ticket)
        conn.commit()

    cursor.close()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Please provide total rows, rows per batch, and sleep seconds per batch. For example: python rt_data_generate_insert_into_pg.py 1000 100 10")
        sys.exit(1)
    
    total_count = int(sys.argv[1])
    batch_size = int(sys.argv[2])
    sleep_time = int(sys.argv[3])
    
    main(total_count, batch_size, sleep_time)
```
In VS Code, create a new "Terminal" and run the following command to activate the Python environment created in the "Environment Setup" step. If you are already in the cz-ingest-examples environment, please skip this step.
```Shell
conda activate cz-ingest-examples
```
Then run the following command in the same terminal:

Insert 100,000 rows of data into the ingest\_demo.lift\_tickets\_data table, inserting 100 rows at a time, with a 10-second sleep between each batch.
```Shell
python rt_data_generate_insert_into_pg.py 100000 100 10
```
In Singdata Lakehouse Studio, view the real-time synchronization progress:

:-: ![](.topwrite/assets/image_1736148122833.png =484)

#### Next Steps

Insert new data into the data source to view the results of incremental synchronization.

"Stop" the running of this synchronization task. The virtual compute cluster set for this task has an automatic stop feature, which will stop running within the "auto stop" seconds after the job stops, saving costs and achieving on-demand operation.

#### Resources

[Real-time Data Writing](java_reference/realtime-upload.md)

[Multi-table Real-time Synchronization](realtime_sync.md)

[Capture Change Data (CDC) and Data Processing through Multi-table Real-time Synchronization and Dynamic Tables in Singdata Lakehouse](czguide-intro-to-cdc-using-clickzetta-rtsync-dynamic-tables.md)