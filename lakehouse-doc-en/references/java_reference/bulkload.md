# Bulk Load Data (Bulkload)

Bulkload is the Java SDK's high-throughput bulk write interface, suitable for importing local files, external system query results, or historical data in bulk into Lakehouse tables.

## Overview

The Bulkload write flow works as follows: the Java application creates Row objects, the SDK stages the data to object storage or a Table Volume, and the application explicitly calls `getCommitRequests()`, `prepareCommit()`, `commit()`, and `future.get()` before the data is loaded into the target table. Finally, call `close()` to release resources. It is suitable for minute-level batch jobs and not suitable for millisecond-level real-time writes.

| Write Method | Use Case | Data Visibility |
| ---- | ---- | ---- |
| `RealtimeStream` | High-frequency small batches, event streams, CDC | Queryable soon after write; visible to downstream after commit |
| Bulkload | Large batch imports, historical data backfill, file-parsed writes | Visible only after explicit `commit()` succeeds |
| JDBC DML | Low-frequency small batch DML | Visible after SQL execution succeeds |

## Usage Restrictions

- Bulkload is not suitable for small batch writes triggered at high frequency within 5-minute intervals; use `RealtimeStream` for real-time scenarios.
- Bulkload data is only visible after an explicit successful commit; calling `close()` alone does not commit data.
- During concurrent writes, different threads or processes should use different shard IDs to avoid overwriting each other.
- Use the Bulkload interface described in this article for all bulk writes.

## Create a Bulk Write Stream

```java
import com.clickzetta.client.BulkloadStreamV2;
import com.clickzetta.client.ClickZettaClient;
import com.clickzetta.platform.bulkload.adapt.Committable;
import com.clickzetta.platform.bulkload.v2.BulkLoadCommitter;
import com.clickzetta.platform.client.api.BulkLoadOperation;
import com.clickzetta.platform.client.api.Row;

import java.util.Arrays;
import java.util.Collection;

public class BulkloadDemo {
    public static void main(String[] args) throws Exception {
        String jdbcUrl = args[0];
        String username = args[1];
        String password = args[2];
        String schema = args[3];
        String table = args[4];

        ClickZettaClient client = ClickZettaClient.newBuilder()
                .url(jdbcUrl)
                .username(username)
                .password(password)
                .build();

        BulkloadStreamV2 stream = null;
        try {
            stream = client.newBulkloadStreamV2Builder()
                    .withOperation(BulkLoadOperation.APPEND)
                    .createStream(client, schema, table);

            Row row = stream.createRow(0);
            row.setValue("id", 1);
            row.setValue("name", "bulkload_001");
            stream.apply(row, 0);

            // Commit this write: collect commit requests -> prepare commit -> commit -> wait for completion.
            Collection<BulkLoadCommitter.CommitRequest<Committable>> commitRequests =
                    stream.getCommitRequests();
            String transactionId = stream.prepareCommit(commitRequests);
            stream.commit(Arrays.asList(transactionId), commitRequests).get();
        } finally {
            if (stream != null) {
                stream.close();
            }
            client.close();
        }
    }
}
```

> ⚠️ **Note**: Bulkload data is only written to the target table after an explicit commit. Calling `close()` only releases resources; it does not commit data. The commit sequence is fixed: `getCommitRequests()` → `prepareCommit()` → `commit()` → `future.get()`, where `future.get()` waits for the commit to complete.

## Write to a Partitioned Table

For static partition writes, specify the target partition using `withPartitionSpecs`:

```java
import com.clickzetta.client.BulkloadStreamV2;
import com.clickzetta.client.ClickZettaClient;
import com.clickzetta.platform.client.api.BulkLoadOperation;

public class BulkloadPartitionDemo {
    public static void main(String[] args) throws Exception {
        ClickZettaClient client = ClickZettaClient.newBuilder()
                .url(args[0])
                .username(args[1])
                .password(args[2])
                .build();

        BulkloadStreamV2 stream = null;
        try {
            stream = client.newBulkloadStreamV2Builder()
                    .withOperation(BulkLoadOperation.APPEND)
                    .withPartitionSpecs("dt=2026-07-14,region=cn")
                    .createStream(client, args[3], args[4]);
        } finally {
            if (stream != null) {
                stream.close();
            }
            client.close();
        }
    }
}
```

For dynamic partition writes, do not specify `withPartitionSpecs` and instead write the actual partition column values in the Row.

> ⚠️ **Note**: Static partitioning loads all data written in this operation into the specified partition. If the data contains other values for the partition column, they will not be automatically routed to other partitions.

## Write Complex Types

```java
import com.clickzetta.client.BulkloadStreamV2;
import com.clickzetta.platform.client.api.Row;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

public class BulkloadComplexTypeDemo {
    public static void writeRow(BulkloadStreamV2 stream) throws Exception {
        Row row = stream.createRow(0);

        row.setValue("tags", Arrays.asList("new", "paid"));

        Map<Integer, String> properties = new HashMap<>();
        properties.put(1, "mobile");
        row.setValue("properties", properties);

        Map<String, Object> profile = new HashMap<>();
        profile.put("level", 3);
        profile.put("city", "Shanghai");
        row.setValue("profile", profile);

        stream.apply(row, 0);
    }
}
```

## Concurrent Writes

When the volume of data to import in a single run is large, you can use multiple threads for concurrent writes. Each concurrent task uses an independent shard ID:

```java
import com.clickzetta.client.BulkloadStreamV2;
import com.clickzetta.platform.client.api.Row;

public class BulkloadConcurrentWriteDemo {
    public static void writeRow(BulkloadStreamV2 stream, int shardId) throws Exception {
        Row row = stream.createRow(shardId);
        row.setValue("id", 10003);
        row.setValue("name", "parallel_003");
        stream.apply(row, shardId);
    }
}
```

After all concurrent tasks finish writing, execute `getCommitRequests()` → `prepareCommit()` → `commit()` → `future.get()` together to commit the import job, then call `stream.close()` to release resources.

> ⚠️ **Note**: Do not let multiple concurrent tasks share the same shard ID, as this may cause shard data to overwrite each other.

## Operation Types

| Operation | Description |
| ---- | ---- |
| `BulkLoadOperation.APPEND` | Append writes to the target table |
| `BulkLoadOperation.OVERWRITE` | Overwrite the target table or target partition |
| `BulkLoadOperation.UPSERT` | Insert-or-update by record keys specified in `recordKeys`; when using `UPSERT`, you must specify record keys via `withRecordKey` or `withRecordKeys`; `partialUpdateColumns` is only supported in `UPSERT` mode |

## Related Documentation

- [Java SDK Introduction](java-sdk-summary.md)
- [Initialize Client](client.md)
- [Real-time Data Writes](realtime-upload.md)
