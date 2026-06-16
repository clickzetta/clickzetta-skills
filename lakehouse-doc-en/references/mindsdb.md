# Connecting MindsDB to Singdata Lakehouse

> ⚠️ **Note:** If your goal with MindsDB is to call AI models on your data, Singdata Lakehouse provides native AI capabilities — no need to deploy or maintain a MindsDB service:
>
> | Scenario | Recommended Solution | Description |
> |----------|---------------------|-------------|
> | Call large language models (LLMs) in SQL | [AI Gateway + AI_COMPLETE](lakehouseai-overview.md) | Call LLMs directly in SQL — text classification, summarization, and extraction in a single SQL statement |
> | Call external AI services (Alibaba Cloud, Tencent Cloud, etc.) | [External Function](remotefunction-intro.md) | Register HTTP APIs as SQL functions and call them directly in queries |
> | Vector semantic search, RAG retrieval | [Vector Index](vector-search.md) | Native vector storage and ANN retrieval, no additional vector database needed |
> | Full-text search + semantic search combined | [Inverted Index + Vector Index](inverted-index.md) | Hybrid retrieval, suitable for knowledge base Q&A scenarios |
> | Python data processing + AI inference | [Zettapark](zettapark-quick-start.md) | PySpark-like interface for running Python scripts on Lakehouse |
>
> If you already have a MindsDB workflow, or need MindsDB's AutoML capabilities specifically, continue reading the integration guide below.

---

**MindsDB enhances SQL with AI building blocks**, allowing developers to create AI applications that need to be coupled with real-time data. One of MindsDB's innovations is the ability to treat AI (models, agents, knowledge bases) as virtual tables, enabling you to SELECT FROM, JOIN, and FINE-TUNE from Singdata Lakehouse data sources using any AI engine.

![](.topwrite/assets/image_1704978508036.png)

## Method 1: Running and Configuring MindsDB on Docker

## Install Docker

If you haven't installed Docker yet, please follow the [instructions](https://docs.docker.com/install) to install Docker on your computer. To ensure Docker has been successfully installed on your computer, test if Docker is running properly as follows:
```bash
docker run hello-world
```

You should see the `Hello from Docker!` message. Otherwise, please refer to the [Docker's getting started](https://www.docker.com/get-started) documentation.

**Docker for Mac Users - RAM Allocation Issue**

By default, Docker for Mac allocates 2 GB of RAM, which is not sufficient to deploy MindsDB using Docker. We recommend increasing the default RAM limit to 8 GB. For more information on how to increase the allocated memory, please refer to the [Docker Desktop for Mac user manual.](https://docs.docker.com/desktop/mac/#resources)

## Install and Start MindsDB

Please note that this MindsDB installation method requires at least 8 GB of RAM and 20 GB of available storage space.

Download the docker compose file locally:

<https://github.com/clickzetta/mindsdb-clickzetta/blob/staging/docker-compose-up-only.yml>

Run the following command to start MindsDB in Docker.

```bash
docker-compose -f docker-compose-up-only.yml up -d
```

Now, you can access the following:

MindsDB Studio:

```bash
http://127.0.0.1:47334/
```

Using MySQL with MindsDB

```bash
mysql -h 127.0.0.1 --port 47335 -u mindsdb -p
```

## Next Steps

Now that you have installed and started MindsDB locally in a Docker container, next, learn how to create and train models using the [CREATE MODEL](https://docs.mindsdb.com/sql/create/model) statement. In the **MindsDB SQL** section, you will find a comprehensive overview of the SQL syntax provided by MindsDB. We also provide the Mongo-QL syntax documented in the **MindsDB Mongo-QL** section.

You can connect MindsDB to different clients, including the [MySQL CLI](https://docs.mindsdb.com/connect/mysql-client).

Check out the [Use Cases](https://docs.mindsdb.com/finetune/anyscale) section for tutorials covering large language models, natural language processing, time series, classification, and regression models.

## Method 2: Setting up MindsDB via pip and GitHub Source Code

This section describes how to deploy MindsDB from the source code. If you want to contribute to our code or debug MindsDB, this is the preferred way to use MindsDB.

To successfully install MindsDB, use the **64-bit version of Python**. Also, ensure **Python >= 3.8** and **pip >= 20.3**.

## Installation

Please note that this MindsDB installation method requires at least 6 GB of available storage space.

1. Clone the MindsDB repository:

   ```bash
   git clone https://github.com/clickzetta/mindsdb-clickzetta.git
   ```

2. Create a new virtual environment:

   ```bash
   python -m venv mindsdb-venv
   ```

3. Activate the virtual environment:

   ```bash
   source mindsdb-venv/bin/activate
   ```

4. Install dependencies:

   ```bash
   cd mindsdb
   pip install -e .
   pip install -r requirements/requirements-dev.txt
   ```

5. Start MindsDB:

   ```bash
   python -m mindsdb  --config=config.json
   ```

By default, MindsDB will always start the `http` and `mysql` APIs.

```bash
python -m mindsdb --api=http,mysql  --config=config.json
```

If you want to use the Mongo API, you need to provide it as a parameter to `--api`. You can do it as follows:

```bash
python -m mindsdb --api=http,mongodb,mysql  --config=config.json
```

6. Now, you can access the following:

MindsDB Studio:

```bash
http://127.0.0.1:47334/
```

Using MySQL with MindsDB

```bash
mysql -h 127.0.0.1 --port 47335 -u mindsdb -p
```

## Dependencies

By default, many data or ML integration dependencies are not installed.

If you want to use data or ML integration dependencies that are not available by default, install them by running the following command:

```
pip install '.[handler_name]'
```

You can find all available [handlers](https://github.com/clickzetta/mindsdb-clickzetta/tree/staging/mindsdb/integrations/handlers) here.

## Troubleshooting

### Pip and Python Versions

Currently, MindsDB supports Python versions 3.8.x, 3.9.x, 3.10.x, and 3.11.x.

To successfully install MindsDB, use the **64-bit version of Python**. Additionally, ensure **Python >= 3.8** and **pip >= 20.3**. You can check the pip and python versions by running the commands `pip --version` and `python --version`.

Please note that depending on your environment and the installed pip and python packages, you may have to use **pip3** instead of **pip** or **python3.x** instead of **py**. For example, `pip3 install mindsdb` instead of `pip install mindsdb`.

### How to Avoid Dependency Issues

**Use pip** to install MindsDB in a virtual environment to avoid dependency issues.

### How to Avoid Common Errors

MindsDB requires approximately 3 GB of available disk space to install all its dependencies. Ensure a minimum of 3 GB of disk space is allocated to avoid the `IOError: [Errno 28] No space left on device while installing MindsDB` error.

First, activate the virtual environment where MindsDB is installed to avoid the `No module named mindsdb` error.

If you encounter the `This site can't be reached. 127.0.0.1 refused to connect.` error, check the MindsDB server console to see if the server is still in the `starting` phase. However, if the server has started but you still receive this error, report it on our [GitHub repository](https://github.com/mindsdb/mindsdb/issues).

### How to Resolve `ImportError: failed to find libmagic` Issue

If you encounter the `ImportError: failed to find libmagic` error, you should manually install `libmagic` by running one of the following commands:

```bash
pip install python-magic-bin  # for linux and windows
brew install libmagic  # for macOS
```

## Check Singdata Lakehouse Handler Status

Visit [MindsDB Studio](http://127.0.0.1:47334/editor)
Check Singdata Lakehouse Handler status

```SQL
select \* from information\_schema.handlers where TITLE="ClickZetta";
```

![](.topwrite/assets/image_1704968631664.png)
IMPORT\_SUCCESS is true, indicating that the Singdata Lakehouse Handler is working properly.

## Create a project and Singdata Lakehouse database

```SQL
CREATE PROJECT IF NOT EXISTS clickzetta;
```

```SQL
CREATE DATABASE if not exists clickzetta\_ai\_demo --- display name for database.

WITH ENGINE = 'clickzetta', --- name of the mindsdb handler

PARAMETERS = {

"service": "region_id.api.singdata.com", --- ClickZetta Lakehouse service address.

"workspace": "qiliang_ws_demo", --- ClickZetta workspace.

"instance": "********", --- account instance id.

"vcluster": "default", --- vcluster

"username": "********", --- your usename.

"password": "********", --- Your password.

"schema": "ai_demo" 

};

```

Check the creation result, showing that it has been created:

```SQL
SHOW databases;
```

![](.topwrite/assets/image_1704968969155.png)

## Application Example

## Predicting House Rental Prices

```SQL
--1. CONNECT ClickZetta Lakehouse
--Let's start by previewing the data we will use to train our model:
SELECT * FROM clickzetta_ai_demo.home_rentals limit 10 ;
```

![](.topwrite/assets/image_1704973236848.png)

```SQL
--2. TRAIN A MACHINE LEARNING MODEL
CREATE MODEL IF NOT EXISTS
  clickzetta.home_rentals_model
FROM clickzetta_ai_demo  (SELECT * FROM home_rentals)
PREDICT rental_price;
DESCRIBE home_rentals_model;
```

![](.topwrite/assets/image_1704973261576.png)

```SQL
--3. MAKE A PREDICTION
SELECT rental_price, 
       rental_price_explain 
FROM clickzetta.home_rentals_model
WHERE sqft = 823
AND location='good'
AND neighborhood='downtown'
AND days_on_market=10;
```

```
rental_price rental_price_explain 4464 {"predicted_value": 4464, "confidence": 0.99, "anomaly": null, "truth": null, "confidence_lower_bound": 4387, "confidence_upper_bound": 4542}
```

```SQL
--4. Bulk predictions by joining a table with your model:
SELECT t.rental_price as real_price, m.rental_price as predicted_price, t.number_of_rooms,  t.number_of_bathrooms, t.sqft, t.location, t.days_on_market 
FROM clickzetta_ai_demo.home_rentals as t 
JOIN clickzetta.home_rentals_model as m
LIMIT 100;
```

![](.topwrite/assets/image_1704973411217.png)

![](.topwrite/assets/image_1704973441296.png)
