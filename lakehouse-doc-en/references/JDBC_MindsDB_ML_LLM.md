# Connect to MindsDB for Data Analysis Based on ML and LLM

## Step Overview:

1. Add a MySQL type data source in the "Data Source" section of Singdata Lakehouse, and connect to [MindsDB](mindsdb.md) via the MySQL protocol.
2. Create a new "JDBC Script" task type in Singdata Lakehouse, and select the MindsDB data source created in the first step.
3. This allows you to operate and manage MindsDB using MySQL syntax in Singdata Lakehouse, and perform various predictive analyses on the data in Singdata Lakehouse through models managed by MindsDB (including traditional machine learning models and LLM).
4. Similar to SQL tasks, you can directly schedule and maintain JDBC tasks periodically and achieve workflow orchestration with other tasks by setting task dependencies.

## Create a New MindsDB Connection

Before creating a new connection, please ensure that your MindsDB has opened the MySQL service port 47335.

![](.topwrite/assets/image_1718691461767.png)

## Create a New JDBC Script Task and View MindsDB Metadata

![](.topwrite/assets/image_1718691763216.png)

Execute the following command to view the ML ENGINES deployed in MindsDB:

```sql
-- List ML ENGINES deployed in MindsDB
SHOW ENGINES;
```

## List models deployed in MindsDB

```sql
-- List models deployed in MindsDB
SHOW MODELS;
```

## Make predictions using MindsDB model

Execute the following command to make predictions using a deployed model in MindsDB:

```sql
SELECT * FROM mindsdb.<model_name> WHERE <conditions>;
```

## Task Scheduling and Maintenance

Similar to SQL tasks, JDBC tasks can be scheduled and maintained on a periodic basis. You can orchestrate workflows with other tasks by configuring task dependencies.

## Create a new JDBC script task to connect MindsDB to Singdata Lakehouse

```
CREATE DATABASE if not exists clickzetta_gharchive --- display name for database.

WITH ENGINE = 'clickzetta', --- name of the mindsdb handler

PARAMETERS = {

"service": "api.singdata.com", --- Singdata Lakehouse service address.

"workspace": "", --- Singdata workspace.

"instance": "", --- account instance id.

"vcluster": "default", --- vcluster

"username": "", --- your usename.

"password": "", --- Your password.

"schema": "public" --- common schema PUBLIC.

};

-- query data from Singdata lakehouse

SELECT * FROM clickzetta_gharchive.collections;

```

![](.topwrite/assets/image_1718692091502.png)

## Create a new JDBC script task to perform sentiment classification on text data in the Lakehouse table using the Huggingface sentiment classifier model

### Create a new model

```
CREATE MODEL if not exists proj_gharchive.hf_sentiment_classifier

PREDICT sentiment

USING

engine='huggingface',

model_name= 'cardiffnlp/twitter-roberta-base-sentiment',

task='text-classification',

input_column = 'description',

labels=['negative','neutral','positive'];

DESCRIBE proj_gharchive.hf_sentiment_classifier;

```

By executing the DESCRIBE proj\_gharchive.hf\_sentiment\_classifier command, you can see that the hf\_sentiment\_classifier model has been deployed and activated.

![](.topwrite/assets/image_1718692548739.png)

### Batch Prediction (Sentiment Classification) on Data in Singdata Lakehouse

```
-- Text sentiment classification of the description of Huggingface's 7-day popular Repos

SELECT model.sentiment AS description_sentiment,

        model.sentiment_explain,
        
        input.*

FROM clickzetta_gharchive.github_timeline_past_7_days_hot_repos AS input

JOIN proj_gharchive.hf_sentiment_classifier AS model

WHERE input.description IS NOT NULL

ORDER BY input.star_increase DESC;

```

Running the above SQL, check the query result's description\_sentiment field, and you can see the different classification results for the input\_column = 'description' column, including neutral, positive, or negative (the labels value in the model).

![](.topwrite/assets/image_1718692823877.png)

## Create a new JDBC script task to classify the sentiment of text data in the Lakehouse table using the OpenAI large model

In this section, we will classify the sentiment of text with the help of the OpenAI GPT-3.5 model.

### Create a new model

```
CREATE ML\_ENGINE if not exists openai_engine

FROM openai

USING

openai_api_key = 'sk-';

-- DROP MODEL if exists proj_gharchive.gpt35t_sentiment_classifier_openai;

CREATE MODEL if not exists proj_gharchive.gpt35t_sentiment_classifier_openai

PREDICT sentiment

USING

engine = 'openai_engine',

prompt_template = 'describe the sentiment of the description

strictly as "positive", "neutral", or "negative".

"I love the product":positive

"It is a scam":negative

"{{description}}.":';

```

### Batch Prediction on Data in Singdata Lakehouse (Sentiment Classification)

```
--gpt35t_7-day popular Repo description text sentiment classification

SELECT output.*,

input.*

FROM clickzetta_gharchive.github_timeline_past_7_days_hot_repos AS input

JOIN proj_gharchive.gpt35t_sentiment_classifier AS output

LIMIT 10;

```

## Create a New JDBC Script Task to Forecast Lakehouse Time Series Data Using the StatsForecast Model

### Create a New Model

**StatsForecast** provides a set of widely used univariate time series forecasting models, including `ARIMA` using exponential smoothing and automated modeling optimized for high performance with `numba`.

```
CREATE MODEL if not exists proj_gharchive.quarterly_repo_star_incre_forecaster

FROM clickzetta_gharchive

(SELECT *

FROM github_timeline_from_20220101_repos_star_incre_monthly

WHERE repo_id = 214011414

)

PREDICT star_increase

ORDER BY month_of_date

GROUP BY repo_id

WINDOW 12

HORIZON 3

USING ENGINE = 'statsforecast';

```

### Batch Prediction on Data in Singdata Lakehouse

```
-- statsforecast_monthly star growth forecast

SELECT t.*

FROM clickzetta_gharchive.github_timeline_from_20220101_repos_star_incre_monthly AS t

WHERE t.repo_id = 214011414

UNION ALL

SELECT m.repo_id,

'kingToolboxWindTerm' AS repo_name,

m.month_of_date,

m.star_increase

FROM proj_gharchive.quarterly_repo_star_incre_forecaster AS m

JOIN clickzetta_gharchive.github_timeline_from_20220101_repos_star_incre_monthly AS t

WHERE t.month_of_date > LATEST AND

t.repo_id = 214011414;

```

![](.topwrite/assets/image_1718696051211.png)

## Task Scheduling and Workflow Orchestration

Similar to SQL tasks, JDBC tasks can be directly scheduled and maintained periodically. Workflow orchestration with other tasks can be achieved by setting task dependencies.
