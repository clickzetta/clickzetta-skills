# IP Geolocation and Security Analysis: Practical Guide

> **Scenario**: Perform geolocation analysis (user profiling, traffic distribution) and network security analysis (blocklist/allowlist filtering, anomalous login detection) based on user IP addresses.
>
> **Core functions**: `get_ip_info` (resolve IP to geographic information, requires a self-managed IP database table), `is_ip_address_in_range` (IP range filtering), `ipv4_string_to_num` / `ipv4_num_to_string` (IP numeric conversion).

---

## Quick Selection Guide

| Function | Purpose | Input | Output | Use case |
|---|---|---|---|---|
| `get_ip_info` | Resolve IP to geolocation | IP + table name + field name | VARCHAR | User profiling, regional traffic statistics |
| `is_ip_address_in_range` | Check whether an IP falls within a network range | IP string + CIDR | BOOLEAN | Intranet filtering, security allowlists |
| `ipv4_string_to_num` | Convert IPv4 to integer | IP string | BIGINT | Efficient storage, range queries |
| `ipv4_num_to_string` | Convert integer to IPv4 | BIGINT | VARCHAR | Data display, report restoration |

---

## Prerequisites

### 1. Prepare the IP geolocation database table
The `get_ip_info` function relies on a user-managed IP database table for lookups.

```sql
CREATE TABLE ip_db (
  start_ip STRING COMMENT 'Start address of IP range',
  end_ip   STRING COMMENT 'End address of IP range',
  country  STRING COMMENT 'Country',
  province STRING COMMENT 'Province/State',
  city     STRING COMMENT 'City'
);

-- Insert test data (in production, import a full IP database such as GeoIP or ip2location)
INSERT INTO ip_db VALUES
  ('114.114.114.114', '114.114.114.114', 'China',         'Jiangsu',    'Nanjing'),
  ('8.8.8.8',         '8.8.8.8',         'United States', 'California', 'Mountain View');
```

### 2. Prepare the user access log table

```sql
CREATE TABLE access_logs (
  log_id      BIGINT,
  user_id     BIGINT,
  ip_address  VARCHAR(45),  -- supports IPv4 and IPv6
  action      VARCHAR(50),
  access_time TIMESTAMP_LTZ
);

INSERT INTO access_logs VALUES
  (1, 1001, '114.114.114.114', 'login',       '2026-05-01 10:00:00'),
  (2, 1002, '8.8.8.8',         'view',        '2026-05-01 10:05:00'),
  (3, 1003, '192.168.1.50',    'admin_panel', '2026-05-01 10:10:00'),
  (4, 1004, '10.0.0.1',        'api_call',    '2026-05-01 10:15:00');
```

---

## Scenario 1: User Geolocation Analysis (get_ip_info)

### Problem

Analyze the geographic distribution of users or detect logins from unusual locations.

### SQL Implementation

```sql
-- Resolve IP to country, province, and city
-- Note: get_ip_info requires the IP database table name and the field name to return
SELECT
  user_id,
  ip_address,
  get_ip_info(ip_address, 'ip_db', 'country')  AS country,
  get_ip_info(ip_address, 'ip_db', 'province') AS province,
  get_ip_info(ip_address, 'ip_db', 'city')     AS city
FROM access_logs
WHERE ip_address IS NOT NULL;
```

**Output**:

| user_id | ip_address | country | province | city |
|---------|------------|---------|----------|------|
| 1001 | 114.114.114.114 | China | Jiangsu | Nanjing |
| 1002 | 8.8.8.8 | United States | California | Mountain View |
| 1003 | 192.168.1.50 | NULL | NULL | NULL |
| 1004 | 10.0.0.1 | NULL | NULL | NULL |

> **Notes**:
> - Private IPs (e.g. `192.168.x.x`) and IPs not configured in `ip_db` cannot be resolved to a location and return `NULL`.
> - The second argument to `get_ip_info` is the table name; the third argument is the field name.

### Count users by province

```sql
SELECT
  get_ip_info(ip_address, 'ip_db', 'province') AS province,
  COUNT(DISTINCT user_id) AS user_count
FROM access_logs
WHERE get_ip_info(ip_address, 'ip_db', 'country') = 'China'
GROUP BY 1
ORDER BY user_count DESC;
```

---

## Scenario 2: Network Security Filtering (is_ip_address_in_range)

### Problem

Filter out intranet IP access, or detect whether traffic originates from a trusted network range.

### SQL Implementation

```sql
-- Filter access from intranet ranges (192.168.0.0/16 or 10.0.0.0/8)
SELECT
  log_id,
  user_id,
  ip_address,
  action
FROM access_logs
WHERE is_ip_address_in_range(ip_address, '192.168.0.0/16')
   OR is_ip_address_in_range(ip_address, '10.0.0.0/8');
```

**Output**:

| log_id | user_id | ip_address | action |
|--------|---------|------------|--------|
| 3 | 1003 | 192.168.1.50 | admin_panel |
| 4 | 1004 | 10.0.0.1 | api_call |

### Security alert combined with geolocation

```sql
-- Detect logins from outside mainland China
SELECT
  user_id,
  ip_address,
  access_time,
  get_ip_info(ip_address, 'ip_db', 'country') AS country
FROM access_logs
WHERE action = 'login'
  AND get_ip_info(ip_address, 'ip_db', 'country') != 'China'
  AND get_ip_info(ip_address, 'ip_db', 'country') IS NOT NULL;
```

---

## Scenario 3: IP Numeric Conversion (Storage Optimization and Range Queries)

### Problem

String-form IP addresses are slow to query and difficult to compare by range (e.g. with `BETWEEN`). Converting IPs to integers improves performance.

### SQL Implementation

```sql
-- Convert string to integer
SELECT
  ip_address,
  ipv4_string_to_num(ip_address) AS ip_num
FROM access_logs
WHERE ip_address LIKE '%.%';  -- IPv4 only
```

**Output**:

| ip_address | ip_num |
|------------|--------|
| 114.114.114.114 | 1920399986 |
| 8.8.8.8 | 134744072 |
| 192.168.1.50 | 3232235826 |

### Convert integer back to string (report restoration)

```sql
-- Convert integer back to string
SELECT
  ip_num,
  ipv4_num_to_string(ip_num) AS ip_address
FROM (
  SELECT ipv4_string_to_num('114.114.114.114') AS ip_num
);
```

### Efficient range query example

```sql
-- Query records where IP falls between 192.168.1.0 and 192.168.1.255
SELECT * FROM access_logs
WHERE ipv4_string_to_num(ip_address)
  BETWEEN ipv4_string_to_num('192.168.1.0')
  AND     ipv4_string_to_num('192.168.1.255');
```

---

## Scenario 4: Comprehensive Example — Traffic and Security Monitoring Dashboard

### Problem

Build a comprehensive dashboard that includes:
1. Traffic distribution by ISP
2. Intranet access percentage
3. Anomalous IP alerts (invalid IPs)

### SQL Implementation

```sql
WITH ip_analysis AS (
  SELECT
    log_id,
    user_id,
    ip_address,
    action,
    -- Resolve country
    get_ip_info(ip_address, 'ip_db', 'country') AS country,
    -- Determine whether the IP is intranet
    is_ip_address_in_range(ip_address, '192.168.0.0/16')
    OR is_ip_address_in_range(ip_address, '10.0.0.0/8') AS is_intranet,
    -- Check whether the IP is valid (simple validation: four dot-decimal segments)
    CASE
      WHEN ip_address RLIKE '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$' THEN true
      ELSE false
    END AS is_valid_ipv4
  FROM access_logs
)
SELECT
  -- Country distribution
  COALESCE(country, 'Unknown/Private') AS country_name,
  COUNT(*) AS request_count,
  -- Intranet percentage
  ROUND(SUM(CASE WHEN is_intranet THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS intranet_pct,
  -- Invalid IP alert count
  SUM(CASE WHEN NOT is_valid_ipv4 THEN 1 ELSE 0 END) AS invalid_ip_count
FROM ip_analysis
GROUP BY 1
ORDER BY request_count DESC;
```

**Output**:

| country_name | request_count | intranet_pct | invalid_ip_count |
|--------------|---------------|--------------|------------------|
| China | 1 | 0.0 | 0 |
| United States | 1 | 0.0 | 0 |
| Unknown/Private | 2 | 100.0 | 0 |

---

## Common Issues

### 1. `get_ip_info` requires a self-managed table

```sql
-- Wrong: get_ip_info with only two arguments
SELECT get_ip_info('114.114.114.114', 'country');  -- error

-- Correct: must pass the table name and the field name
SELECT get_ip_info('114.114.114.114', 'ip_db', 'country');
```

### 2. IPv6 support limitations

```sql
-- get_ip_info requires the ip_db table to include IPv6 start_ip and end_ip entries to resolve IPv6 addresses
-- is_ip_address_in_range natively supports IPv6 CIDR
SELECT is_ip_address_in_range('2001:0db8::1', '2001:0db8::/32');  -- result: true
```

### 3. Handling invalid IPs

```sql
-- An invalid IP causes the conversion function to error or return NULL
SELECT ipv4_string_to_num('1.2.3.400');  -- error or NULL

-- Recommendation: filter with a regex first
SELECT ipv4_string_to_num(ip_address)
FROM access_logs
WHERE ip_address RLIKE '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$';
```

### 4. CIDR format for `is_ip_address_in_range`

```sql
-- Wrong: missing mask length
is_ip_address_in_range(ip, '192.168.1.0')

-- Correct: must include /mask
is_ip_address_in_range(ip, '192.168.1.0/24')
```

---

## Performance Optimization Tips

| Scenario | Optimization strategy |
|---|---|
| High-frequency IP resolution | Materialize `get_ip_info` results into a table to avoid repeated calls on every query |
| Range queries | Store IPs as integers using `ipv4_string_to_num` and build a Bloom Filter index |
| Log cleansing | Perform IP resolution at the data ingestion layer (ETL) so the analytics layer can query result columns directly |

```sql
-- Recommended: resolve and store in advance
CREATE TABLE enriched_logs AS
SELECT
  log_id,
  ip_address,
  get_ip_info(ip_address, 'ip_db', 'country') AS country,
  get_ip_info(ip_address, 'ip_db', 'city')    AS city,
  ipv4_string_to_num(ip_address)               AS ip_num
FROM raw_logs;

-- Query with direct filtering — no real-time resolution needed
SELECT * FROM enriched_logs WHERE city = 'Beijing';
```

---

## Related Documents

* [IP Function Reference](ip_functions.md)
* [String Processing](SQL_String_Processing_Guide.md)
* [Data Deduplication](SQL_Deduplication_Guide.md)
