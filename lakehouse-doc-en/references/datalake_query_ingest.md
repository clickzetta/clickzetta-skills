# Data Lake Query

After creating a Volume object, you can directly query data files in CSV, Parquet, and ORC formats from the external storage path through this object without relying on any metadata system.

## Prerequisites:

1. If the data is in the cloud vendor's object storage, please complete the creation of the storage connection and external volume objects first.
2. Before querying files in the volume in Lakehouse, please confirm whether you have read permission (READ) for the target volume object. If you also need to use the [PUT command](PUT.md) to upload files, you need to have read and write permissions. You can use `show grants to user <user_name>` to check whether the current user has the above permissions.

## Usage Restrictions:

* Supported external storage includes: Alibaba Cloud OSS, Tencent Cloud COS, and AWS S3.
* Only CSV, PARQUET, and ORC file formats are supported.
* Only gzip, zstd, and zlib compression formats are supported.

^
^
^
