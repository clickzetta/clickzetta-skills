# Data Import into Lakehouse Practice: Batch Loading via COPY Command

This guide will help you import large amounts of data from public URL Parquet files (such as New York City Taxi and For-Hire Vehicle Data) into Singdata Lakehouse using scripts and the Singdata Lakehouse SQLLine command-line tool.

1. download_raw_data.sh: Downloads public URL Parquet files to local storage. This article uses NYC Taxi Data as an example, containing over 450 files and 60GB of data (Parquet format).

2. initialize_database.sh: Creates the Singdata Lakehouse schema and tables via Lakehouse SQLLine commands.

3. Import taxi and FHV data: Uses R to convert Parquet files to CSV files, then imports the data from local CSV files into Singdata Lakehouse tables via the Lakehouse SQLLine COPY command, supporting batch import of multiple files.

# User Guide

Script download address: <https://github.com/yunqiqiliang/nyc-taxi-data-clickzetta>

## 1. Install [Singdata SQLLine](connect-with-cli.md)

## 2. Install [R](https://www.r-project.org/)

From [CRAN](https://cloud.r-project.org/)

Note that R used to be optional for this repo, but is required starting with the 2022 file format change. The scripts use R to convert Parquet files to CSV before loading into Postgres. There are other ways to convert from Parquet to CSV that wouldn't require R, but I found that R's `arrow` package was faster than some of the other CLI tools I tried

## 3. Download raw data

`./download_raw_data.sh`

When done, modify download_raw_data.sh and run again to download data from 202212:
wget -i setup_files/raw_data_urls_new\.txt -P data/ -w 2

## 4. Initialize database and set up schema

`./initialize_database.sh`

## 5. Import taxi and FHV data

`./import_yellow_taxi_trip_data.sh`

`./import_green_taxi_trip_data.sh`

`./import_fhv_taxi_trip_data.sh`

`./import_fhvhv_trip_data.sh`

Note that the full import process might take several hours or possibly even over a day, depending on computing power.

# Schema

* `trips` table contains all yellow and green taxi trips. Each trip has a `cab_type_id`, which references the `cab_types` table and refers to one of `yellow` or `green`
* `fhv_trips` table contains all for-hire vehicle trip records, including ride-hailing apps Uber, Lyft, Via, and Juno
* `fhv_bases` maps `fhv_trips` to base names and "doing business as" labels, which include ride-hailing app names
* `nyct2010` table contains NYC census tracts plus the Newark Airport. It also maps census tracts to NYC's official neighborhood tabulation areas
* `taxi_zones` table contains the TLC's official taxi zone boundaries. Starting in July 2016, the TLC no longer provides pickup and dropoff coordinates. Instead, each trip comes with taxi zone pickup and dropoff location IDs
* `central_park_weather_observations` has summary weather data by date

# Load Script Example

[Complete Script](https://github.com/clickzetta/nyc-taxi-data-clickzetta/blob/master/readme.md)

```
#!/bin/bash

fhv_schema="(dispatching_base_num, pickup_datetime, dropoff_datetime, pickup_location_id, dropoff_location_id, legacy_shared_ride_flag, affiliated_base_num)"

for parquet_filename in data/fhv_tripdata*.parquet; do
  echo "`date`: converting ${parquet_filename} to csv"
  ./setup_files/convert_parquet_to_csv.R ${parquet_filename}

  csv_filename=${parquet_filename/.parquet/.csv}
  
  sh ../sqlline_cz/sqlline properties ../sqlline_cz/clickzetta.properties -e "set copy.csv.with.header=false;set copy.csv.skip.header=true; copy fhv_trips_staging from '${csv_filename}';"

  echo "`date`: finished raw load for ${csv_filename}"

  rm -f $csv_filename
  echo "`date`: deleted ${csv_filename}"
done;
```

^
