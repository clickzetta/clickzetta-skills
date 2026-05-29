# (SaaS)^2: Singdata Lakehouse + Zilliz, Make Data Ready for BI and AI
## Solution Overview

   * (SaaS)^2: Both Singdata Lakehouse and Zilliz provide SaaS-mode services based on mainstream cloud services. By combining SaaS services, you can maximize the benefits of fully-managed and pay-as-you-go SaaS models.

   * Make Data Ready for BI and AI: Singdata Lakehouse's data warehouse focuses on providing scalar data storage, processing, and analysis for BI applications; Zilliz vector database focuses on AI-enhanced data analytics. Through the integration of Singdata Lakehouse and Zilliz vector database, a complete production-grade BI+AI solution is provided, addressing the BI/AI asymmetry problem:

     * Asymmetry in BI data and AI data freshness: Zilliz Vector Data Pipeline provides batch data embedding services, reducing embedding time by more than 10x compared to non-batch processing, greatly improving AI data freshness.
     * Asymmetry in BI data and AI data scale: Zilliz still provides stable fast response and concurrency at the tens-of-billions vector data scale. Vector data is no longer a supplementary "niche" data type, achieving parity with BI data in terms of scale.

   * Business Upgrade: Upgrade traditional data analytics to augmented analytics with the simplest solution, achieving BI+AI integration.


## Solution Components

   ![](.topwrite/assets/image_1734076588760.png)

   * Singdata Lakehouse Platform: Provides data lake and data warehouse management, including data management, data integration, task development, task execution, workflow orchestration, task monitoring and operations, etc.
   * Singdata Zettapark: Loads CSV files through Python + DataFrame programming.
   * Zilliz Vector Database: High-performance, cost-effective vector database.
   * Zilliz Data Pipeline: Vectorizes and stores text, images, files, and other data, supports Chinese and English embedding models and reranking models, providing extremely simplified and developer-friendly vector processing.

## Application Scenario Example: Enhancing Text Search via Semantic Retrieval

   * Scalar retrieval: Singdata Lakehouse provides text-based LIKE fuzzy matching and keyword search based on text inverted indexes.
   * Vector retrieval: Zilliz provides semantic retrieval based on vector data and result fine-ranking via reranking models.

Combining scalar and vector retrieval improves search performance and accuracy, suitable for product search, product recommendation, and other scenarios.

### Task 1: Load Raw Data into Singdata Lakehouse

Singdata Lakehouse provides multiple ways to load CSV data, including web-based offline data sync and loading CSV through the data lake. This article uses Singdata Zettapark for data loading, with Python code running on Singdata Lakehouse's Python task nodes.

![](.topwrite/assets/image_1734329566767.png)

The code is as follows:

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*#:

author: qiliang:

create time: 2024-09-14 10:10:26:

\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*#:

```Python
from clickzetta.zettapark.session import Session
hints = dict()
hints['sdk.job.timeout'] = 3
hints['query_tag'] = 'test_conn_hints_zettapark'
connection_parameters = {
  "username": "qiliang",
  "password": "",
  "service": "<region_id>.api.singdata.com",
  "instance": "",
  "workspace": "ql_ws",
  "schema": "wayfair_wans",
  "vcluster": "default",
  "sdk_job_timeout": 10,
  "hints": hints,
}
session = Session.builder.configs(connection_parameters).create()
import os
import pandas as pd
import warnings

```

Ignore FutureWarning:

```Python
warnings.filterwarnings("ignore", category=FutureWarning)
```

File URL array:

```Python
urls = [
    'https://raw.githubusercontent.com/wayfair/WANDS/main/dataset/label.csv',
    'https://raw.githubusercontent.com/wayfair/WANDS/main/dataset/product.csv',
    'https://raw.githubusercontent.com/wayfair/WANDS/main/dataset/query.csv'
]
for url in urls:
    # Extract file name and remove extension
    table_name = os.path.basename(url).split('.')[0]
    data = pd.read_csv(url, delimiter='\t')  # Specify the delimiter as tab
    # Replace spaces in column names with underscores and convert to lowercase
    data.columns = [col.replace(" ", "_").lower() for col in data.columns]
    # Check if the table exists
    try:
        session.table(table_name)
        table_exists = True
    except Exception:
        table_exists = False
    # Create the table if it doesn't exist
    if not table_exists:
        column_definitions = ", ".join([f"{col} STRING" for col in data.columns])
        session.sql(f"CREATE TABLE {table_name} ({column_definitions})")
    df = session.create_dataframe(data)
    df.write.save_as_table(table_name, mode="overwrite", table_type="transient")
    print(f"Data from {filepath} written to table {table_name}")

 # Drop tables starting with 'zettapark_temp_table_'
try:
    tables = session.sql("SHOW TABLES LIKE 'zettapark_temp_table_%'").collect()
    
    for table in tables:
        table_name = table['table_name']
        session.sql(f"DROP TABLE IF EXISTS {table_name}").collect()
        print(f"temp Table {table_name} dropped")
except Exception as e:
    print(f"Error dropping temp tables: {e}")

```

Close the session:

```Python
session.close()   
```

Then check the result in the Singdata Lakehouse console:

![](.topwrite/assets/image_1734329595733.png)

![](.topwrite/assets/image_1734329604994.png)

### Task 2: Develop SQL Tasks to Prepare Data for BI

![](.topwrite/assets/image_1734329614774.png)

The code is as follows:

```SQL
--LAKEHOUSE SQL
--********************************************************************--
-- author: qiliang
-- create time: 2024-09-12 15:17:34
--********************************************************************--
-- DROP TABLE if exists product_cleaned;
CREATE TABLE if not exists product_cleaned(
  `product_id` bigint,
  `product_name` string,
  `product_class` string,
  `category_hierarchy` string,
  `product_description` string,
  `product_features` string,
  `rating_count` double,
  `average_rating` double,
  `review_count` double,
  `product_text` string,
  `product_full_text` string,
  `product_features_json` json,
   index inverted_index_product_text (product_text) using inverted,
   index inverted_index_product_full_text (product_full_text) using inverted,
);
INSERT OVERWRITE product_cleaned
SELECT
       *,
       COALESCE(product_description, product_name) as product_text,
       CONCAT(
        COALESCE(product_name, ''), ';',
        COALESCE(product_description, ''), ';',
        COALESCE(product_class, ''), ';',
        COALESCE(category_hierarchy, ''), ';',
        COALESCE(product_features, '')
       ) as product_full_text,
       JSON_PARSE(
       to_json(
           map_from_entries(
               transform(
                   split(product_features, '\\|'),
                   entry -> struct(
                       trim(split(entry, ':')[0]),
                       trim(split(entry, ':')[1])
                   )
               )
           )
       ) AS product_features_json,
FROM product);
```

### Task 3: Create Zilliz Data Ingestion Pipeline

Zilliz Cloud Pipelines simplify the process of converting unstructured data into embedding vectors and connecting to Zilliz Cloud vector database for storing vector data, enabling efficient vector indexing and retrieval. When processing unstructured data, developers often face complex unstructured data transformation and retrieval challenges, which can slow down development. Zilliz Cloud Pipelines address this challenge by providing an all-in-one solution, helping developers easily convert unstructured data into searchable vectors and ensuring high-quality vector retrieval after connecting to Zilliz Cloud vector database.

![](.topwrite/assets/image_1734329641231.png)

Get the client code for the newly created Pipeline as input for the next step:

![](.topwrite/assets/image_1734329668097.png)

### Task 4: Develop a Python Task to Call Zilliz Data Ingestion Pipeline API in the Workflow, Preparing Data for AI-Enhanced Analytics and Automating Vector Data ETL.

Send the text information from the table named `product` in Singdata Lakehouse to Zilliz, first embedding the text data, then storing it as vectors.

![](.topwrite/assets/image_1734329678061.png)

After executing the above code in Singdata Lakehouse, check the Zilliz console to verify the vectorization results:

![](.topwrite/assets/image_1734329685817.png)

![](.topwrite/assets/image_1734329699172.png)

### Task 5: Define the Complete Data Flow via Singdata Lakehouse Workflow Orchestration

Set scheduling properties for each of the above tasks and submit them to build the data workflow:

![](.topwrite/assets/image_1734329789735.png)

### Task 6: Create Zilliz Data Search Pipeline

Using the Zilliz Data Search Pipeline, you can quickly and efficiently convert query text into embedding vectors and return the most relevant top-K document chunks (including text and metadata), effectively extracting data insights from search results.

![](.topwrite/assets/image_1734329806523.png)

### Task 7: Perform Data Analysis via Zilliz API

```SQL
import http.client
import json
conn = http.client.HTTPSConnection("controller.api.gcp-us-west1.zillizcloud.com")
headers = {
    'Authorization': "Bearer ******",
    'Accept': "application/json",
    'Content-Type': "application/json"
}
search_without_rerank_payload = "{\"data\":{\"query_text\":\"black 5 drawer dresser by guilford\"},\"params\":{\"limit\":20,\"offset\":0,\"outputFields\":[],\"filter\":\"id >= 0\"}}"

conn.request("POST", "/v1/pipelines/pipe-e46ae76b70773f85543c93/run", search_without_rerank_payload, headers)

res = conn.getresponse()
data = res.read()

```

Decode the response data:

```SQL
decoded_data = data.decode("utf-8")

```

Parse the JSON data:

```SQL
parsed_data = json.loads(decoded_data)

```

Pretty-print the JSON data:

```SQL
pretty_json = json.dumps(parsed_data, ensure_ascii=False, indent=4)
print(pretty_json)
```
