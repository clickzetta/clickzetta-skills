# Storage Connection

A Storage Connection is a type of Connection object in Singdata Lakehouse. It belongs to the workspace level and is used to store authentication credentials and access control information required when the Lakehouse accesses data in cloud object storage (such as Alibaba Cloud OSS, Tencent Cloud COS, Amazon S3), other data platforms (such as Hive), and real-time streaming data (such as Kafka). It is a prerequisite for Lakehouse Volume objects, External Tables, External Catalogs, Autoloader, and other objects to access external data.

> Note: If you have not enabled an object storage service and need to upload data to Singdata Lakehouse via files, you can upload data to [Internal Volume](internal_volume.md). This approach does not require the user to enable a cloud object storage service.

### Usage Restrictions:

* Cross-cloud object storage connections are currently not supported. For example: if the activated Singdata Lakehouse instance is in the Alibaba Cloud Shanghai site, this instance does not support connecting to non-Alibaba Cloud object storage.
* One object storage Storage Connection can be used to create multiple Volume objects.

^
