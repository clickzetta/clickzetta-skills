# Quick Start with Copy command

Through this experiment, experience quickly loading local csv files into tables using the Singdata Lakehouse Copy command and performing the most basic data exploration and analysis.

The experiment code runs on [Zeppelin Notebook](eco_integration/zeppelin.md), with relevant guidance provided in the appendix. Additionally, the experiment code can also run on various local [database management tools](data-mamager-tool.md) (which support the Copy command to access local files).

## Create a new schema for this experiment
```
CREATE SCHEMA IF NOT EXISTS lakehouse_demo_basic_features_schema;
USE SCHEMA lakehouse_demo_basic_features_schema;
```
## Create Table
```
--Create table
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
## Load Data - Copy from File
Sure, here is the translated content:

```
-- Load data
set copy.csv.with.header=false;
set copy.csv.skip.header=true;
Please download [central\_park\_weather.csv](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/sample_data/central_park_weather.csv), click "Download raw file" to download it locally and modify the directory (/opt/data/) in the above code to the directory where you downloaded it.
And verify if the data has been successfully loaded:
```
select count(1) from central_park_weather_observations;
```
## Explore Data
```
SELECT * FROM central_park_weather_observations LIMIT 10;
```
## Analyzing Data
```
SELECT date, sum(precipitation) FROM central_park_weather_observations
GROUP BY date
ORDER BY date;
```
## Cleanup
```
DROP TABLE IF EXISTS central_park_weather_observations;
DROP SCHEMA IF EXISTS lakehouse_demo_basic_features_schema;
```
## Congratulations, it's done.

Please enjoy and learn more!

## Appendix

### Download Zeppelin Notebook Source File

The code in this article is also available in a version that runs on [Zeppelin](eco_integration/zeppelin.md). If you want to run the code directly, please follow the documentation to install [Zeppelin](eco_integration/zeppelin.md).

[Quick Start with Copy command.ipynb](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/zeppelin_notebook/01.Quick%20Start%20with%20Copy%20command.ipynb)