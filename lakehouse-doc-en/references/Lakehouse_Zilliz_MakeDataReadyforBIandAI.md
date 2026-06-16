# (SaaS)²: Singdata Lakehouse + Zilliz, Make Data Ready for BI and AI
## Solution Overview

   * (SaaS)²: Singdata Lakehouse and Zilliz both provide SaaS services based on mainstream cloud services. By combining SaaS services, you can maximize the benefits of fully managed and pay-as-you-go SaaS models.

   * Make Data Ready for BI and AI: Singdata Lakehouse's data warehouse focuses on storing, processing, and analyzing scalar data for BI applications, while Zilliz vector database focuses on enhanced data analysis for AI. By integrating Singdata Lakehouse and Zilliz vector database, a complete production-level BI+AI solution is provided to address the asymmetry between BI and AI:

     * Asymmetry in data freshness between BI and AI: Zilliz Vector Data Pipeline provides batch data embedding services, reducing embedding time by 10x+ compared to non-batch, significantly improving the freshness of AI data.
     * Asymmetry in data scale between BI and AI: Zilliz can still provide stable and fast response and concurrency at the scale of tens of billions of vector data, making vector data no longer a supplementary "niche" data, achieving parity in scale between BI data and AI data.

   * Business Upgrade: Upgrade traditional data analysis to enhanced analysis with the simplest solution, achieving BI+AI integration.

## Solution Components

   ![](.topwrite/assets/image_1734076588760.png)

   * Singdata Lakehouse Platform: Provides management of data lakes and data warehouses, including data management, data integration, task development, task execution, workflow orchestration, task monitoring, and maintenance.
   * Singdata Zettapark: Implements csv file loading through Python+Dataframe programming.
   * Zilliz Vector Database: A high-performance, cost-effective vector database.
   * Zilliz Data Pipeline: Vectorizes and retrieves data such as text, images, and files, supports Chinese and English embedding models, rerank models, and provides an extremely simplified and developer-friendly vector processing method.

## Application Scenario Example: Enhancing Text Search with Semantic Retrieval

   * Scalar Retrieval: Singdata Lakehouse provides text-based like fuzzy matching and keyword search based on text inverted index.
   * Vector Retrieval: Zilliz provides semantic retrieval based on vector data and result reranking with rerank models.

Combining scalar retrieval and vector retrieval improves retrieval performance and accuracy, suitable for product search, product recommendation, and other scenarios.

### Task 1: Load Raw Data into Singdata Lakehouse

Singdata Lakehouse provides multiple ways to load csv data, including offline data synchronization via WEB, loading csv through data lake, etc. This article uses Singdata Zettapark to implement data loading, with Python code running in Singdata Lakehouse's Python task node.

![](.topwrite/assets/image_1734329566767.png)

The code is as follows:
```Python
# ********************************************************************#
# author: qiliang
# create time: 2024-09-14 10:10:26
# ********************************************************************#
from clickzetta.zettapark.session import Session
hints = dict()
hints['sdk.job.timeout'] = 3
hints['query_tag'] = 'test_conn_hints_zettapark'
connection_parameters = {
  "username": "qiliang",
  "password": "",
  "service": "api.clickzetta.com",
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

# Ignore FutureWarning
warnings.filterwarnings("ignore", category=FutureWarning)
# File URL array
urls = [
    'https://raw.githubusercontent.com/wayfair/WANDS/main/dataset/label.csv',
    'https://raw.githubusercontent.com/wayfair/WANDS/main/dataset/product.csv',
    'https://raw.githubusercontent.com/wayfair/WANDS/main/dataset/query.csv'
]
for url in urls:
    # Extract the file name and remove the extension
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

# Close the session
session.close()   
```
Then check the results in the Singdata Lakehouse console:

![](.topwrite/assets/image_1734329595733.png)

![](.topwrite/assets/image_1734329604994.png)

### Task 2: Develop SQL tasks to prepare data for BI

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
### Task Three: Create Zillize Data Ingestion Pipeline

Zilliz Cloud Pipelines can simplify the process of converting unstructured data into embedding vectors and interfacing with the Zilliz Cloud vector database to store vector data, achieving efficient vector indexing and retrieval. Developers often face complex unstructured data conversion and retrieval issues when dealing with unstructured data, which can slow down development speed. Zilliz Cloud Pipelines addresses this challenge by providing an integrated solution that helps developers easily convert unstructured data into searchable vectors and interface with the Zilliz Cloud vector database to ensure high-quality vector retrieval.

![](.topwrite/assets/image_1734329641231.png)

Obtain the client code of the newly created Pipeline as the input for the next step:

![](.topwrite/assets/image_1734329668097.png)

### Task Four: Develop a Python Task to Call the Zilliz Data Ingestion Pipeline API in the Workflow, Preparing Data for AI-Enhanced Analysis and Automating Vector Data ETL

Send the text information of the table named product in Singdata Lakehouse to Zilliz, first perform embedding on the text data, and then store it as vectors.

![](.topwrite/assets/image_1734329678061.png)

After executing the above code in Singdata Lakehouse, go to the Zilliz console to check and verify the vectorization results:

![](.topwrite/assets/image_1734329685817.png)

![](.topwrite/assets/image_1734329699172.png)

### Task Five: Define a Complete Data Flow Through Singdata Lakehouse Workflow Orchestration

Set scheduling properties for the above tasks and submit them to build a data workflow:

![](.topwrite/assets/image_1734329789735.png)

### Task Six: Create Zilliz Data Search Pipeline

Using the Zillize Data Search Pipeline can quickly and efficiently convert query text into embedding vectors, returning the most relevant top-K document blocks (including text and metadata), effectively gaining data insights from search results.

![](.topwrite/assets/image_1734329806523.png)

### Task Seven: Perform Data Analysis Through Zilliz API
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

# Decode the response data
decoded_data = data.decode("utf-8")

# Parse the JSON data
parsed_data = json.loads(decoded_data)

# Pretty-print the JSON data
pretty_json = json.dumps(parsed_data, ensure_ascii=False, indent=4)
print(pretty_json)
```