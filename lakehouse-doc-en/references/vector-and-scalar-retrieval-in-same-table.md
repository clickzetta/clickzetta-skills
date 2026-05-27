# Performing Vector and Scalar Retrieval in the Same Table in Singdata Lakehouse

## Data Preparation

GitHub provides over 15 event types, including new commits and fork events, opening new issues, comments, and adding members to projects. These events are aggregated into hourly archives, which you can access from <https://www.gharchive.org/> using any HTTP client.

* Download the archived json.gz files locally from <https://www.gharchive.org/> via wget. This article downloads 24 files for the full day of 2025-01-01.
* Use the Lakehouse PUT command to PUT the data onto the USER VOLUME.
* Directly read files in the USER VOLUME directory via SQL, then write IssuesEvent type events into the `github_event_issuesevent` table.
* Write data from github\_event\_issuesevent into the target table github\_event\_issuesevent\_embedding.

## Data Vectorization

The `github_event_issuesevent_embedding` table in Singdata Lakehouse stores text fields. These text fields need to be vectorized and stored in the vector field of the same table to facilitate fused vector and scalar retrieval.

This solution supports storing text data, vector data, as well as inverted indexes and vector indexes simultaneously in the same table and the same VCluster. Compared to traditional approaches, it no longer requires three separate systems (data warehouse, text retrieval database, vector database), minimizing the number of data copies and avoiding data synchronization across three systems.

![](/.topwrite/assets/image_1768390312153.png)

^
^

### Key Singdata Lakehouse Features Used

* [Vector Storage](vector-type.md): Native Vector data type, allowing Vector type fields to be added directly to regular tables.
* [Vector Index](create-table-ddl.md): Create indexes on Vector type fields to accelerate vector retrieval speed.
* [Inverted Index](create-table-ddl.md): Create inverted indexes on text fields to accelerate text retrieval speed.
* [Bloom Filter Index](create-table-ddl.md): Create indexes on ID fields to accelerate ID filtering.
* [Zettapark](zettapark-quick-start.md)

### Model Services

* xinference: Deploy xinference locally to provide embedding and rerank model services.
* This solution uses 1024-dimensional vector representations.

### Test Dataset Introduction

* The data source is GitHub IssuesEvent events; the full-text retrieval field is the `issue_body`.
* The vector field stores the vectorized data corresponding to `issue_body`.
* The entire table contains 190 million records.

### Data Description

* Table Name: `github_event_issuesevent_embedding`
* Text Field: `issue_body`, string type
* Vectorized Field: `issue_body_embedding`, vector(float,1024) type
* Vectorization Method: `issue_body_embedding` initially is NULL. Call the xinference/ollama local service, vectorize the text of the `issue_body` field using the bge-m3 model, then save it to the `issue_body_embedding` field.

### issue\_body\_embedding Field Update Methods

* **Single Update Method**
  * Conforms to the habits of traditional database developers, with fresher data achieving second-level data freshness. However, performing frequent UPDATEs with SQL on a big data platform brings significant drawbacks:
    * Generates a large number of small files that need timely merging to optimize performance.
    * Requires the VCluster to remain running, resulting in high compute costs.

* **Batch Merge Into Method**
  * Sacrifices data freshness, from seconds to minutes.
  * Avoids the problem of rapidly increasing small files.
  * Significantly reduces compute costs. Performing MERGE INTO every 5 minutes can reduce compute costs by up to 80%, greatly improving the cost-effectiveness of data vectorization. This is very important for large-scale data vectorization.

## Fused Retrieval

* Refer to and complete the vector and scalar storage in the same table in the Singdata Lakehouse.
* Retrieval Process

![](/.topwrite/assets/image_1768390271906.png)

^

## Source Code

This article provides Notebook-based source code on GitHub as follows:

* [Data Preparation](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/Zettapark/Performing%20Vector%20and%20Scalar%20Retrieval%20in%20the%20Same%20Table%20in%20a%20Cloud%20Data%20Lakehouse-01Data%20Preparation.ipynb)
* [Vectorization](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/Zettapark/Performing%20Vector%20and%20Scalar%20Retrieval%20in%20the%20Same%20Table%20in%20a%20Cloud%20Data%20Lakehouse-02Embedding.ipynb)
* [Fused Retrieval](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/Zettapark/Performing%20Vector%20and%20Scalar%20Retrieval%20in%20the%20Same%20Table%20in%20a%20Cloud%20Data%20Lakehouse-03Search.ipynb)

## References

[Vector Data Type](vector-type.md)
[Creating Indexes](create-table-ddl.md)
[Zettapark Quick Start](zettapark-quick-start.md)

^
