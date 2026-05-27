# Batch Upload Data Using Python SDK

This document details how to use the BulkloadStream in the Python SDK to batch load data into Lakehouse. This method is suitable for importing large amounts of data at once, supports custom data sources, and provides flexibility for data import. This example uses a local CSV file as an example. If the data source is within the object storage or the data integration range supported by Lakehouse Studio, it is recommended to use the COPY command or data integration.

## Reference Documentation

[Uploading Data with Python SDK](python_reference/bulkload-upload.md)

### Application Scenarios

* Suitable for business scenarios that require batch data uploads.
* Suitable for developers familiar with Python and needing to customize data import logic.

### Usage Restrictions

* BulkloadStream does not support writing to primary key (pk) tables.
* Not suitable for frequent data upload scenarios with intervals of less than five minutes.

## Use Case

This example uses the `olist_order_payments_dataset` from the [Brazilian E-commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?select=olist_order_items_dataset.csv) public dataset.

### Prerequisites

* Create the target table `bulk_order_payments`:

```SQL

CREATE TABLE bulk_order_payments (
          order_id STRING,
          payment_sequence INT,
          payment_type STRING,
          payment_installments INT,
          payment_value DOUBLE
          );
```

* Have INSERT permission on the target table.

| **Parameter** | **Required** | **Description**                                                                                                                                                                                    |
| ------------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| username      | Y            | Username                                                                                                                                                                                           |
| password      | Y            | Password                                                                                                                                                                                           |
| service       | Y            | Address to connect to the lakehouse, region.api.clickzetta.com. You can see the JDBC connection string in Lakehouse Studio management -> workspace![](../.topwrite/assets/image_1728887857029.png) |
| instance      | Y            | You can see the JDBC connection string in Lakehouse Studio management -> workspace![](../.topwrite/assets/image_1729051500396.png)                                                                 |
| workspace     | Y            | Workspace in use                                                                                                                                                                                   |
| vcluster      | Y            | VC in use                                                                                                                                                                                          |
| schema        | Y            | Name of the schema to access                                                                                                                                                                       |

### Develop with Python Code

Use pip to install the Python package dependencies for Lakehouse. Python version 3.6 or above is required:

```SQL
pip install clickzetta-connector
```

#### Writing Python Code

```SQL
from clickzetta import connect
import csv

def get_lakehouse_connect():
    conn = connect(
        username='',
        password='',
        service='api.singdata.com',
        instance='',
        workspace='',
        schema='public',
        vcluster='default_ap')
    return conn

conn = get_lakehouse_connect()
bulkload_stream = conn.create_bulkload_stream(schema='public', table='bulk_order_payments')
writer = bulkload_stream.open_writer(0)

with open('olist_order_payments_dataset.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    # Skip header row
    next(reader)
    # Upload data
    for record in reader:
        # Use bulkload to create row upload
        bulkloadrow = writer.create_row()
        bulkloadrow.set_value('order_id', record[0])
        bulkloadrow.set_value('payment_sequence', int(record[1]))
        bulkloadrow.set_value('payment_type', record[2])
        bulkloadrow.set_value('payment_installments', int(record[3]))
        bulkloadrow.set_value('payment_value', float(record[4]))
        # Must call, otherwise data cannot be sent to the server
        writer.write(bulkloadrow)
writer.close()
# Commit data import completion
bulkload_stream.commit()
```

^
