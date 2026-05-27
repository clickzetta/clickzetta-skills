# Data Lake Storage Connection

Storage Connection is a type of Connection object in Singdata Lakehouse, which is a workspace-level object used to store authentication and access control information needed when accessing cloud object storage (such as Alibaba Cloud OSS, Tencent Cloud COS, Amazon Cloud S3, and Google Cloud GCS) from Lakehouse. It is a prerequisite for Lakehouse Volume objects to access cloud object storage data.

> Note: If you have not activated the object storage service and need to upload data to Singdata Lakehouse via files, you can upload data to the [internal Volume](internal_volume.md). This method does not require users to activate the cloud object storage service.

### Usage Restrictions:

* Currently, cross-cloud object storage connections are not supported. For example, if the Singdata Lakehouse instance is activated at the Alibaba Cloud Shanghai site, it does not support connecting to other non-Alibaba Cloud object storage in this instance.
* One storage connection can support the creation of multiple VOLUME objects

^