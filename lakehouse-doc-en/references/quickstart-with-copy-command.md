# Quick Start with Copy Command

Through this lab, experience how to quickly use the Singdata Lakehouse COPY command to load a local CSV file into a table and perform basic data exploration and analysis.

The code in this lab runs in [Zeppelin Notebook](eco_integration/zeppelin.md), and the appendix provides related guidance. Additionally, the lab code can also run in various local [database management tools](data-mamager-tool.md) (which support COPY command access to local files).

## Create a New Schema for This Lab

```sql
CREATE SCHEMA IF NOT EXISTS lakehouse_demo_basic_features_schema;
USE SCHEMA lakehouse_demo_basic_features_schema;
```

## Create a Table

```sql
-- Create table
CREATE TABLE if not exists central_park_weather_observations (
  station_id STRING,
  station_name STRING,
  date DATE,
  precipitation DECIMAL,
  snow_depth DECIMAL,
  snowfall DECIMAL,
  max_temperature DECIMAL,
  min_temperature DECIMAL,
  average_wind_speed DECIMAL
);

```

## Load Data - COPY FROM FILE

```sql
-- Load data
set copy.csv.with.header=false;
set copy.csv.skip.header=true;
copy central_park_weather_observations from '/opt/data/central_park_weather.csv' ;
```

Please download [central_park_weather.csv](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/sample_data/central_park_weather.csv), click "Download raw file" to download it locally, and modify the directory path (`/opt/data/`) in the above code to your download directory.
Then verify whether the data has been loaded successfully:

```sql
select count(1) from central_park_weather_observations;
```

## Explore Data

```sql
SELECT * FROM central_park_weather_observations LIMIT 10;
```

## Analyze Data

```sql
SELECT date, sum(precipitation) FROM central_park_weather_observations
GROUP BY date
ORDER BY date;
```

## Clean Up

```sql
DROP TABLE IF EXISTS central_park_weather_observations;
DROP SCHEMA IF EXISTS lakehouse_demo_basic_features_schema;
```

## Congratulations, Mission Complete!

Enjoy and continue learning!

## Appendix

### Download Zeppelin Notebook Source File

The code in this document is also available to run in [Zeppelin](eco_integration/zeppelin.md). If you want to run the code directly, please follow the documentation instructions to install [Zeppelin](eco_integration/zeppelin.md).

[Quick Start with Copy command.ipynb](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/zeppelin_notebook/01.Quick%20Start%20with%20Copy%20command.ipynb)
