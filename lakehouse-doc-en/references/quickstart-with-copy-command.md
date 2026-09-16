# Quick Start with Copy Command

In this lab, experience how to quickly use the COPY command in Singdata Lakehouse to load a local CSV file into a table, and perform basic data exploration and analysis.

The lab code runs in [Zeppelin Notebook](eco_integration/Zeppelin.md); the appendix provides related guidance. The lab code can also run in various local [database management tools](data-manager-tool.md) (those that support the COPY command for accessing local files).

## Create a New Schema for This Lab

```
CREATE SCHEMA IF NOT EXISTS lakehouse_demo_basic_features_schema;
USE SCHEMA lakehouse_demo_basic_features_schema;
```

## Create a Table

```
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

## Load Data — COPY FROM FILE

```
-- Load data
set copy.csv.with.header=false;
set copy.csv.skip.header=true;
copy central_park_weather_observations from '/opt/data/central_park_weather.csv' ;
```

Download [central\_park\_weather.csv](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/sample_data/central_park_weather.csv), click "Download raw file" to save it locally, and update the directory path (`/opt/data/`) in the code above to match your download location.
Then verify that the data has been loaded successfully:

```
select count(1) from central_park_weather_observations;
```

## Explore Data

```
SELECT * FROM central_park_weather_observations LIMIT 10;
```

## Analyze Data

```
SELECT date, sum(precipitation) FROM central_park_weather_observations
GROUP BY date
ORDER BY date;
```

## Clean Up

```
DROP TABLE IF EXISTS central_park_weather_observations;
DROP SCHEMA IF EXISTS lakehouse_demo_basic_features_schema;
```

## Congratulations, You're Done!

Enjoy and keep learning!

## Appendix

### Download the Zeppelin Notebook Source File

The code in this article is also available as a [Zeppelin](eco_integration/Zeppelin.md) notebook. If you want to run it directly, follow the documentation to install [Zeppelin](eco_integration/Zeppelin.md).

[Quick Start with Copy command.ipynb](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/zeppelin_notebook/01.Quick%20Start%20with%20Copy%20command.ipynb)
