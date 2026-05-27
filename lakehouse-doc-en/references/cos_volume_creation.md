# Create VOLUME to Access Tencent Cloud's COS Data:

## Prerequisites:

After the STORAGE CONNECTION on Tencent Cloud is completed, you can create a VOLUME object to access the object storage data.

## Create VOLUME Object

```sql
CREATE EXTERNAL VOLUME my_tx_volume
  LOCATION 'cos://cz-volume-sh-1311343935/olist_bz'
  USING CONNECTION my_tx_connection
  DIRECTORY = (ENABLE = TRUE)
  RECURSIVE = TRUE;
```

### View Detailed Information of Created VOLUME Objects

```SQL
DESC VOLUME my_tx_volume
```

### Access COS to View Files Under the VOLUME Path

```SQL
SHOW VOLUME DIRECTORY my_tx_volume;
```

### Store the file metadata of the VOLUME directory to Lakehouse and view it

```
ALTER VOLUME my_tx_volume refresh;

SELECT * FROM DIRECTORY(VOLUME my_tx_volume);
```

^

![](.topwrite/assets/20240625-201914.jpeg)
