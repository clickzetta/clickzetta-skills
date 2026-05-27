# GET\_IP\_INFO

# Function Overview

```python
 get_ip_info(string ip, string table, string column)
```

This function automatically loads the IP information database at runtime based on the table name specified by the second parameter. The table must have at least `start_ip` and `end_ip` columns, representing the closed interval of the IP range. The return result is the column specified by the third parameter.

# **Parameters**

| Parameter | Type   | Required | Description                                         |
| --------- | ------ | -------- | --------------------------------------------------- |
| `ip`      | string | Yes      | The IP address to query (supports IPv4/IPv6 format). |
| `table`   | string | Yes      | Specifies the Lakehouse table name, and the table structure must include `start_ip` and `end_ip` columns. |
| `column`  | string | Yes      | The target field name to return, of STRING type, must be a field that exists in the table specified by the second parameter. |

# **Return Value**

* Match succeeded: Returns the field value of the specified `column` (STRING type).

# **Examples**

## Example 1

1. Prepare the IP database table

```sql
CREATE TABLE IF NOT EXISTS ip_db(
  start_ip   STRING COMMENT 'IP segment start address',
  end_ip     STRING COMMENT 'IP segment end address',
  geoname_id STRING,
  country    STRING,
  city       STRING
);

INSERT OVERWRITE TABLE ip_db VALUES
  ("2a7:1c44:39f3:1b::", "2a7:1c44:39f3:1b:ffff:ffff:ffff:ffff", "8070", "USA", "LA"),
  ("2c0f:ffb8::", "2c0f:ffb8:ffff:fff:fff:ffff:ff:ffff", "37210", "CHINA", "BJ"),
  ("1.0.0.0", "1.0.0.255", "5987", "JAPAN", "TOKYO"),
  ("2.0.0.0", "2.0.0.255", "8026", "INDIA", "DELHI");
```

2. Execute the query

```sql
SELECT 
  ip, 
  get_ip_info(ip, 'ip_db', 'country') AS country
FROM VALUES
  ('2c0f:ffb8:1b::'),  -- IPv6
  ('1.0.0.2'),         -- IPv4
  ('3.0.0.0')          -- No match
AS t(ip);
```

Expected output

| ip               | country |
| ---------------- | ------- |
| 2c0f\:ffb8:1b::  | CHINA   |
| 1.0.0.2          | JAPAN   |
| 3.0.0.0          | NULL    |

***

## Example 2

### **I. Business Background**

Need to quickly obtain 7-dimensional geographic information based on IP addresses:

| Field            | Description        | Example Value   |
| ---------------- | ------------------ | --------------- |
| `country`        | Country name       | China           |
| `province`       | Province/State     | Beijing         |
| `city`           | City name          | Chaoyang        |
| `timezone`       | Timezone           | Asia/Shanghai   |
| `latitude`       | Latitude           | 39.9042         |
| `longitude`      | Longitude          | 116.4074        |
| `countryCode`    | Country code       | CN              |
| `continentCode`  | Continent code     | AS              |

### II. Technical Implementation

IP resolution is implemented based on the Lakehouse built-in function `get_ip_info(ip, table_name, column)`, using the ip2location technical solution as the underlying layer.

### III. Implementation Process

#### 1. Data Preparation

* **Download the official data package**
  Visit the [MaxMind website](https://dev.maxmind.com/geoip/geoip2/geolite2/) to obtain the latest GeoLite2-City-CSV data package (includes IPv4/IPv6 data).

* **Convert CIDR to IP ranges**
  Use the official conversion tool to generate queryable IP ranges:
  ```bash
  # Convert IPv4 data
  ./geoip2-csv-converter -block-file GeoLite2-City-Blocks-IPv4.csv \
    -include-range -output-file IPv4_Blocks_Converted.csv

  # Convert IPv6 data
  ./geoip2-csv-converter -block-file GeoLite2-City-Blocks-IPv6.csv \
    -include-range -output-file IPv6_Blocks_Converted.csv
  ```
  This document uses the following two CSV files, which are the network IP address range table and the Chinese geographic information table:
  ![](../../../.topwrite/assets/image_1744721445413.png)

#### 2. Data Modeling

##### (1) IP Address Range Table `geoip`

```sql
CREATE TABLE geoip (
  network_start_ip  STRING  COMMENT 'IP segment start address',
  network_last_ip   STRING  COMMENT 'IP segment end address',
  geoname_id        STRING  COMMENT 'Geographic location ID',
  latitude          STRING  COMMENT 'Latitude',
  longitude         STRING  COMMENT 'Longitude'
)
;
```

##### (2) Geographic Information Table `geolocation`

```sql
CREATE TABLE geolocation (
  geoname_id        STRING  COMMENT 'Geographic location ID',
  country_code      STRING  COMMENT 'Country code (ISO 3166)',
  country           STRING  COMMENT 'Country name',
  province          STRING  COMMENT 'Province/State',
  city              STRING  COMMENT 'City name',
  time_zone         STRING  COMMENT 'Timezone',
  continent_code    STRING  COMMENT 'Continent code'
);
```

##### (3) Aggregated View Table `geo_lite_info`

```sql
-- Create the aggregated table
CREATE TABLE geo_lite_info (
  start_ip          STRING  COMMENT 'IP segment start',
  end_ip            STRING  COMMENT 'IP segment end',
  country           STRING,
  province          STRING,
  city              STRING,
  timezone          STRING,
  latitude          STRING,
  longitude         STRING,
  country_code      STRING,
  continent_code    STRING
);

-- Write data via association
INSERT OVERWRITE TABLE geo_lite_info
SELECT 
  a.network_start_ip,
  a.network_last_ip,
  b.country,
  b.province,
  b.city,
  b.time_zone,
  a.latitude,
  a.longitude,
  b.country_code,
  b.continent_code
FROM geoip a
JOIN geolocation b 
  ON a.geoname_id = b.geoname_id;
```

***

### IV. Function Invocation

#### Prerequisites

* The target table `geo_lite_info` is correctly created and data is ready.
* IP addresses must be in a standardized format (supports IPv4/IPv6).

#### Invocation Examples

```sql
-- Single-point query
SELECT 
  get_ip_info('114.246.239.157', 'geo_lite_info', 'city') AS city,
  get_ip_info('2001:4860:4860::8888', 'geo_lite_info', 'timezone') AS tz;

-- Batch query
SELECT 
  ip,
  get_ip_info(ip, 'geo_lite_info', 'country') AS country,
  get_ip_info(ip, 'geo_lite_info', 'province') AS province
FROM VALUES (('8.8.8.8'), ('114.114.114.114')) AS t(ip);
```
