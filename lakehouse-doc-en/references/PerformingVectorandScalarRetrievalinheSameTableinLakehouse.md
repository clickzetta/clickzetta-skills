# Performing Vector and Scalar Retrieval in the Same Table in Singdata Lakehouse

## Data Preparation

GitHub provides over 15 types of event types, including new commits and fork events, opening new issues, comments, and adding members to projects. These events are aggregated into hourly archives, which you can access from <https://www.gharchive.org/> using any HTTP client.

* Download archived json.gz files from <https://www.gharchive.org/> to your local machine via wget. This article downloads 24 files for the full day of 2025-01-01.
* Use the Lakehouse PUT command to upload data to the USER VOLUME.
* Read files from the USER VOLUME directory directly via SQL, then write IssuesEvent type events into the `github_event_issuesevent` table.
* Write data from `github_event_issuesevent` into the target table `github_event_issuesevent_embedding`.

## Data Vectorization

The `github_event_issuesevent_embedding` table in Singdata Lakehouse stores text fields that need to be vectorized and saved into vector fields within the same table, enabling convenient fused vector and scalar retrieval.

This solution supports storing text data, vector data, inverted indexes, and vector indexes simultaneously in the same table and the same VCluster. Compared to traditional approaches, it no longer requires three separate systems (data warehouse, text search database, vector database), minimizing the number of data copies to the greatest extent and avoiding data synchronization between the three systems.

![](/.topwrite/assets/image_1768390312153.png)

^
^

### Key Singdata Lakehouse Features Used

* [Vector Storage](vector-type.md): Native Vector data type, allowing you to directly add Vector type fields to regular tables.
* [Vector Index](create-table-ddl.md): Build indexes on Vector type fields to accelerate vector search speed.
* [Inverted Index](create-table-ddl.md): Build inverted indexes on text fields to accelerate text search speed.
* [Bloom Filter Index](create-table-ddl.md): Build indexes on ID fields to accelerate ID filtering.
* [Zettapark](zettaparkquickstart.md)

### Model Service

* xinference, deployed locally to provide embedding and rerank model services.
* This solution uses a 1024-dimensional vector representation.

### Test Dataset Introduction

* The data source is GitHub IssuesEvent events, with the full-text search field being `issue_body`.
* The vector field stores the vectorized data corresponding to `issue_body`.
* The entire table contains 190 million records.

### Data Description

* Table name: `github_event_issuesevent_embedding`
* Text field: `issue_body`, type string
* Vector field: `issue_body_embedding`, type vector(float,1024)
* Vectorization method: The initial value of `issue_body_embedding` is NULL. Call the locally deployed xinference/ollama service to vectorize the text of the `issue_body` field using the bge-m3 model, then save it to the `issue_body_embedding` field.

### issue_body_embedding Field Update Methods

* **Single Record Update Method**
  * Aligns with traditional database developer habits, providing more real-time data with second-level data freshness. However, performing frequent UPDATEs using SQL on a big data platform brings notable drawbacks:
    * Creates large numbers of small files that need timely compaction to optimize performance.
    * Requires the VCluster to be running continuously, resulting in high compute costs.

* **Batch Merge Into Method**
  * Sacrifices data freshness, going from seconds to minutes.
  * Avoids the problem of rapidly increasing small files.
  * Significantly reduces compute costs. Performing MERGE INTO every 5 minutes can reduce compute costs by up to 80%, greatly improving the cost-effectiveness of data vectorization. This is very important for large-scale data vectorization.

## Fused Retrieval

* Refer to and completed vector and scalar storage in the same table in Singdata Lakehouse.
* Retrieval process

![](/.topwrite/assets/image_1768390271906.png)

^

## Source Code

This article provides Notebook-based source code on GitHub:

* [Data Preparation](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/Zettapark/Performing%20Vector%20and%20Scalar%20Retrieval%20in%20the%20Same%20Table%20in%20a%20Cloud%20Data%20Lakehouse-01Data%20Preparation.ipynb)
* [Vectorization](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/Zettapark/Performing%20Vector%20and%20Scalar%20Retrieval%20in%20the%20Same%20Table%20in%20a%20Cloud%20Data%20Lakehouse-02Embedding.ipynb)
* [Fused Retrieval](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/Zettapark/Performing%20Vector%20and%20Scalar%20Retrieval%20in%20the%20Same%20Table%20in%20a%20Cloud%20Data%20Lakehouse-03Search.ipynb)

## References

[Vector Data Type](vector-type.md)
[Create Index](create-table-ddl.md)
[Zettapark Quick Start](zettaparkquickstart.md)

^
