# Python SDK Real-time Write

## Singdata Lakehouse Python SDK Real-time Write

## Installation

1. **Uninstall Old Versions**

   If you have previously installed an older version of the SDK, uninstall the old versions of the `clickzetta-connector` and `clickzetta-sqlalchemy` packages:

   ```shell
   pip uninstall clickzetta-connector clickzetta-sqlalchemy clickzetta-ingestion-python clickzetta-ingestion-python-v2 -y
   ```


2. **Install clickzetta connector**

   Install the ingestion package, which requires Python version 3.10 or higher:

   ```python
   pip install clickzetta-connector
   ```

## Real-time Write Principle

The real-time write feature of the Lakehouse Python SDK is an efficient data stream processing tool that allows users to upload and store data in Lakehouse in real-time. Here's how it works:

1. **SDK Uploads Data**: Users upload data to the Lakehouse Ingestion Service via the Python SDK.
2. **Ingestion Service Processing**: Upon receiving the data, the Ingestion Service writes it directly to the Lakehouse table. At this stage, the data is stored as temporary intermediate files, known as a **hybrid table**.
3. **Query Real-time Data**: Before the data is committed, users can query (select) the newly written data. However, this data is not visible to table streams, materialized views, or dynamic tables.
4. **Data Commit**: The newly written data is automatically committed after approximately one minute. After commitment, table streams, materialized views, and dynamic tables can read this data.
5. **Hybrid Table Becomes a Regular Table**: After data commitment, a background process merges the hybrid table into a regular table. Once the merge is complete, users can perform update operations (update, merge, delete).

## Applicable Scenarios

The real-time write feature of the Lakehouse Python SDK is suitable for the following scenarios:

- **Short-Interval Data Import**: If your application requires data import at very short intervals (e.g., 5 minutes or less), the real-time write SDK can meet your needs.
- **Frequent Small Data Submissions**: For applications that need to submit data frequently but in small volumes each time, the real-time write SDK provides an efficient solution.
- **Real-time Data Analysis**: The real-time write SDK is suitable for applications that require immediate data analysis and response, such as real-time monitoring, event tracking, and real-time reporting.

## Notes

- Data written in real-time can be queried within seconds.
- Real-time data currently only supports schema change perception through the Flink Connector's sink operator (single concurrency) provided internally. For schema changes in other scenarios, you need to stop the real-time write task, wait for some time after the schema change (approximately 90 minutes), and then restart the task.
- Table streams, materialized views, and dynamic tables can only display committed data. Since real-time task data takes about 1 minute to confirm, table streams also need to wait 1 minute to see the data.

## Data Type Support

The Lakehouse Python SDK supports the following data type mappings:

| SQL Data Type               | Python Internal Data Structure                   |
| --------------------- | ------------------------------ |
| BOOLEAN               | bool                           |
| STRING / JSON         | str                            |
| CHAR(n) / VARCHAR(n)  | str (truncated on overflow)                   |
| BINARY                | bytes                          |
| DECIMAL               | Decimal                        |
| INT8                  | int                            |
| INT16                 | int                            |
| INT32                 | int                            |
| INT64                 | int                            |
| FLOAT                 | float                          |
| DOUBLE                | float                          |
| DATE                  | date                           |
| TIMESTAMP_LTZ         | datetime(tz=timezone)          |
| TIMESTAMP_NTZ         | datetime                       |
| INTERVAL_DAY_TIME     | interval_day_time              |
| INTERVAL_YEAR_MONTH   | -                              |
| ARRAY                 | list                           |
| MAP                   | map                            |
| STRUCT                | json or collections.namedtuple |

## Creating a Real-time Data Stream via Client

To create a real-time data stream, you first need to connect using the Lakehouse client:

```python
from clickzetta.connector.v0.connection import connect
from clickzetta.connector.v0.enums import RealtimeOperation
from clickzetta_ingestion.realtime.realtime_options import RealtimeOptionsBuilder, FlushMode
from clickzetta_ingestion.realtime.arrow_stream import RowOperator


```

Create a connection:

```python
with connect(username='your_username',
             password='your_password',
             service='your_service_endpoint',
             instance='your_instance',
             workspace='your_workspace',
             schema='your_schema',
             vcluster='your_vcluster') as conn:
    
    # Create a real-time data stream
    stream = conn.get_realtime_stream(
        schema="your_schema",
        table="your_table",
        operate=RealtimeOperation.APPEND_ONLY,  # Use APPEND_ONLY for regular tables
        options=RealtimeOptionsBuilder().with_flush_mode(FlushMode.AUTO_FLUSH_BACKGROUND).build()
    )
    
    # Close the stream after use
    stream.close()
```

### Parameter Description:

- **operate**: Pass an enumeration value. The real-time interface supports `RealtimeOperation.APPEND_ONLY` and `RealtimeOperation.CDC`.
  - Use `RealtimeOperation.APPEND_ONLY` for regular tables.
  - Primary key tables must use `RealtimeOperation.CDC`.

- **options**: Used to pass parameters for the real-time write stream. See the detailed options below.

## Options

In the Python SDK, you can configure the parameters of the real-time write stream using the `RealtimeOptionsBuilder` class. These parameters are optional and it is recommended to use the default values.

```python
from clickzetta.ingestion.realtime.realtime_options import RealtimeOptionsBuilder, FlushMode, RetryStatus

options = RealtimeOptionsBuilder()\
        .with_flush_mode(FlushMode.AUTO_FLUSH_BACKGROUND) \
        .with_mutation_buffer_lines_num(50000) \
        .with_mutation_buffer_max_num(50) \
        .with_mutation_buffer_space(20 * 1024 * 1024) \
        .with_flush_interval(10 * 1000) \
        .with_request_failed_retry_enable(True) \
        .with_request_failed_retry_times(5) \
        .with_request_failed_retry_internal_ms(5 * 1000) \
        .with_request_failed_retry_log_debug_enable(True) \
        .with_request_failed_retry_status([
        RetryStatus.THROTTLED,
        RetryStatus.INTERNAL_ERROR,
        RetryStatus.FAILED,
        RetryStatus.PRECHECK_FAILED]) \
        .build()
```

### Flush Control

| Parameter Name               | Default Value                     | Description                                                                                                                                           |
| ----------------- | ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| with_flush_mode | AUTO_FLUSH_BACKGROUND | Data flush policy. Options: - AUTO_FLUSH_SYNC: Synchronous flush (blocking, ensures order) - AUTO_FLUSH_BACKGROUND: Asynchronous flush (high throughput) - MANUAL_FLUSH: Manual trigger flush ⚠️ Primary key table restriction: PK tables must use AUTO_FLUSH_SYNC mode |

### Buffer Configuration

| Parameter Name                                | Default Value               | Unit | Description                              |
| ---------------------------------- | ----------------- | -- | ------------------------------- |
| with_mutation_buffer_lines_num | 1000              | rows | Row threshold: Maximum number of rows per buffer, triggers flush when reached          |
| with_mutation_buffer_space      | 10MB (1010241024) | bytes | Space threshold: Maximum memory usage per buffer, triggers flush when either threshold is reached |
| with_mutation_buffer_max_num   | 50                | buffers  | Buffer pool capacity: Number of buffers allowed to exist simultaneously (similar to connection pool mechanism)     |

### Timed Flush

| Parameter Name                   | Default Value | Description                   |
| --------------------- | --- | -------------------- |
| with_flush_interval | 10 seconds | Maximum delay: Forced flush interval when buffer is not full |

### Retry Mechanism Parameters

| Parameter Name                                        | Default Value    | Description         |
| ------------------------------------------ | ------ | ---------- |
| with_request_failed_retry_enable       | TRUE   | Whether to enable retry mechanism for failed requests |
| with_request_failed_retry_times        | 5      | Maximum retry attempts per operation |
| with_request_failed_retry_internal_ms | 5000ms | Retry interval (milliseconds) |

### Advanced Configuration

| Parameter Name                                              | Default Value                                               | Description                                                                                   |
| ------------------------------------------------ | ------------------------------------------------- | ------------------------------------------------------------------------------------ |
| with_request_failed_retry_status             | THROTTLED,INTERNAL_ERROR,FAILED,PRECHECK_FAILED | Retry trigger conditions: - THROTTLED: Flow control - INTERNAL_ERROR: Server-side error - FAILED: General failure - PRECHECK_FAILED: Pre-check failure |
| with_request_failed_retry_log_debug_enable | TRUE                                              | Whether to log detailed retry information (DEBUG level)                                                                  |

## Writing Data (Row)

Create a specific data object (Row) using the `stream.create_row` method and encapsulate the data into the Row object using the `row.set_value` method.

```python
```

Create a row:

```python
row = stream.create_row(RowOperator.INSERT)  # Regular tables use INSERT

```

Set field values:

```python
row.set_value("id", 1)
row.set_value("name", "test_name")

```

Apply the row to the stream:

```python
stream.apply(row)
```

**Row type description**:

- When the Stream is created with `RealtimeOperation.APPEND_ONLY`, only `RowOperator.INSERT` type Rows can be created.
- When the Stream is created with `RealtimeOperation.CDC`, the following Row types can be used:
  - `RowOperator.UPSERT`: Insert a row, update the row if it already exists.
  - `RowOperator.DELETE_IGNORE`: Delete a row, ignore if the target row does not exist.

**Note**: Primary key tables (PK tables) must use CDC mode and can only use UPSERT and DELETE_IGNORE operation types.

## Data Commit to Server

By calling the `stream.flush()` method, data is immediately committed to the server. If this method is not explicitly called, data will be automatically committed based on one of the following conditions:

1. Reaching the buffer size set by `with_mutation_buffer_space`.
2. Reaching the row count set by `with_mutation_buffer_lines_num`.
3. Reaching the time interval set by `with_flush_interval`.

## Example

### Primary Key Table (PK Table) Write Example

```python
from clickzetta.connector.v0.connection import connect
from clickzetta.connector.v0.enums import RealtimeOperation
from clickzetta_ingestion.realtime.arrow_stream import RowOperator
from clickzetta_ingestion.realtime.realtime_options import RealtimeOptionsBuilder, FlushMode

with connect(username='your_username',
             password='your_password',
             service='your_service_endpoint',
             instance='your_instance',
             workspace='your_workspace',
             schema='your_schema',
             vcluster='DEFAULT') as conn:
    
    # Create a primary key table
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE test_pk (
        id STRING NOT NULL PRIMARY KEY,
        name STRING,
        age INT
    )
    """)
    
    # Create a real-time data stream - PK tables must use CDC
    stream = conn.get_realtime_stream(
        schema=conn.get_schema(),
        table="test_pk",
        operate=RealtimeOperation.CDC,
        options=RealtimeOptionsBuilder().with_flush_mode(FlushMode.AUTO_FLUSH_SYNC)
    )
    
    # Write data - PK tables use UPSERT
    for i in range(10):
        row = stream.create_row(RowOperator.UPSERT)
        row.set_value('id', f"id_{i}")
        row.set_value('name', f"user_{i}")
        row.set_value('age', 20 + i)
        stream.apply(row)
    
    # Update data - PK tables use UPSERT
    for i in range(5):
        row = stream.create_row(RowOperator.UPSERT)
        row.set_value('id', f"id_{i}")
        row.set_value('name', f"updated_user_{i}")
        row.set_value('age', 30 + i)
        stream.apply(row)
    
    # Delete data - PK tables use DELETE_IGNORE
    for i in range(2):
        row = stream.create_row(RowOperator.DELETE_IGNORE)
        row.set_value('id', f"id_{i}")
        stream.apply(row)
    
    # Close the stream
    stream.close()
    
    # Verify the result
    cursor.execute("SELECT COUNT(*) FROM test_pk")
    count = cursor.fetchone()[0]
    print(f"Remaining record count: {count}")  # Should be 8 records (10-2)
```

## Common Issues and Solutions

### 1. Primary Key Table Write Failure

**Issue**: Error when writing data to a primary key table.

**Solution**:

- Ensure the correct operation type is used: Primary key tables must use `RealtimeOperation.CDC` mode and can only use `RowOperator.UPSERT` and `RowOperator.DELETE_IGNORE` operations.
- Ensure the primary key field is correctly set.
- Primary key tables do not support `FlushMode.AUTO_FLUSH_BACKGROUND`; it will automatically reset to `FlushMode.AUTO_FLUSH_SYNC`.
- Partition columns must be a subset of the primary key.

### 2. High Memory Usage

**Issue**: High memory usage when writing large amounts of data.

**Solution**:

- Reduce the values of `with_mutation_buffer_lines_num` and `with_mutation_buffer_space`.
- Call `stream.flush()` regularly to manually flush data, but avoid flushing too frequently as it may result in a large number of small files.
- Consider writing data in batches instead of writing large amounts of data at once.

## Summary

The real-time write feature of the Singdata Python SDK provides an efficient and flexible way to write data, supporting various data types and operation modes. By configuring parameters appropriately, you can optimize write performance for different scenarios.

For primary key tables and regular tables, different operation modes and row operation types are required. Primary key tables must use CDC mode and can only use UPSERT and DELETE_IGNORE operations; regular tables typically use APPEND_ONLY mode and INSERT operations.