The COPY command is mainly used for uploading data from local files.

## COPY Command

[COPY Command](use-copy-upload-data.md)

## Usage Restrictions

* Only supports TEXT file upload
* Upload size limit is 2GB
* The command is not supported on the studio page, only supports execution using jdbc client, because this path needs to specify the local path. The studio page cannot read it. You can refer to the database management tools in the ecosystem extension, or the command line tool to connect to Lakehouse

## Supported Parameter Settings

| Parameter                             | Default Value   | Value          | Meaning                                   |
| ------------------------------ | ----- | ----------- | ------------------------------------ |
| set copy.csv.skip.header=false | false | false\|TRUE | Whether to skip the header, if the data contains a header whether to skip                 |
| set copy.csv.with.header=false | false | false\|true | Whether csv contains a header, if it does, use the header in csv to match the fields in the table for insertion |
| set copy.csv.delimiter=','     | ','   | Supports single character delimiter   | csv delimiter                              |
| set copy.csv.escape='\\'       | '\\'  | Supports single character      | csv escape character                              |
| set copy.csv.null.string='\N'  | '\N'  | Supports single character      | Empty string representing null in csv                      |

## Application Scenarios

* Upload a small amount of data locally for simple analysis

## Prerequisites

* Install [Command Line Tool](connect-with-cli.md)
* Have INSERT permission on the table

## Execute Command

```
 copy demo_table from 'c:\data\data.csv'
```

## Code Examples

* Create target table

```SQL
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

* Download file to local /opt/data/ directory
:attachment[taxi_zone_lookup.csv]{src="https://clickzettadoc-attachments.oss-cn-shanghai.aliyuncs.com/taxi%2B_zone_lookup.csv"}
* Load data into target table through copy command

```SQL
set copy.csv.with.header=false;
set copy.csv.skip.header=true;
copy central_park_weather_observations from '/opt/data/central_park_weather.csv' ;
```

* Query data

```SQL
SELECT * FROM central_park_weather_observations LIMIT 10;
```

| station\_id | station\_name               | date       | precipitation | snow\_depth | snowfall | max\_temperature | min\_temperature | average\_wind\_speed |
| ----------- | --------------------------- | ---------- | ------------- | ----------- | -------- | ---------------- | ---------------- | -------------------- |
| USW00094728 | NY CITY CENTRAL PARK, NY US | 2009-01-01 | 11            | 0           | 0        | 0                | 26               | 15                   |
| USW00094728 | NY CITY CENTRAL PARK, NY US | 2009-01-02 | 6             | 0           | 0        | 0                | 34               | 23                   |
| USW00094728 | NY CITY CENTRAL PARK, NY US | 2009-01-03 | 10            | 0           | 0        | 0                | 38               | 29                   |
| USW00094728 | NY CITY CENTRAL PARK, NY US | 2009-01-04 | 8             | 0           | 0        | 0                | 42               | 25                   |
| USW00094728 | NY CITY CENTRAL PARK, NY US | 2009-01-05 | 7             | 0           | 0        | 0                | 43               | 38                   |
| USW00094728 | NY CITY CENTRAL PARK, NY US | 2009-01-06 | 7             | 0           | 0        | 0                | 38               | 31                   |
| USW00094728 | NY CITY CENTRAL PARK, NY US | 2009-01-07 | 11            | 1           | 0        | 0                | 38               | 31                   |
| USW00094728 | NY CITY CENTRAL PARK, NY US | 2009-01-08 | 11            | 0           | 0        | 0                | 38               | 29                   |
| USW00094728 | NY CITY CENTRAL PARK, NY US | 2009-01-09 | 10            | 0           | 0        | 0                | 32               | 26                   |
| USW00094728 | NY CITY CENTRAL PARK, NY US | 2009-01-10 | 7             | 0           | 1        | 0                | 30               | 23                   |
## Reference Cases

* [Load files into Singdata via the copy command in the script](batchloadparquetfileintolakehouse.md).

^
