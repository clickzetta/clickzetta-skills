# JSON Data Processing Guide for Complex Business Scenarios

## Guide Overview

This guide demonstrates the complete technical implementation of Singdata Lakehouse JSON functionality, starting from real-world business scenarios and providing professional solutions for JSON data processing.

**Important Update Notice**: This revised edition is based on comprehensive practical verification, confirming the actual capability boundaries of Singdata Lakehouse JSON functionality. All SQL examples have been tested and verified.

### Guide Structure

* **Chapter 1**: Business Scenario and Challenge Analysis
* **Chapter 2**: Singdata Lakehouse Solutions
* **Chapter 3**: Solutions for Core Technical Challenges
* **Chapter 4**: Deep Technical Implementation and Advanced Optimization
* **Chapter 5**: Chinese and Special Character Handling Guide
* **Chapter 6**: Technical Limitations and Best Practices
* **Chapter 7**: Environment Management and Implementation Recommendations

***

## Chapter 1: Business Scenario and Challenge Analysis

### 1.1 JSON Data Processing Needs of Modern Enterprises

In the digital era, JSON has become the standard format for enterprise data exchange:

* **API Economy**: Under microservice architecture, a vast amount of data exchange adopts the JSON format
* **Real-time Data Streams**: IoT devices, user behaviors, and system logs generate massive amounts of JSON data
* **Diverse Data Sources**: Social media, e-commerce platforms, and financial transactions produce complex nested JSON
* **Internationalization Challenges**: JSON data contains multilingual content including Chinese, emoji, and more

### 1.2 Core Business Scenario Analysis

#### 1.2.1 E-Commerce Scenario: Real-time Analysis of Complex Order Data

**Business Scenario Description**:
An e-commerce platform processes tens of thousands of orders daily, with each order containing complex nested structures such as customer information, product details, payment information, and logistics data:

```json
{
  "order_id": "ORD-2024-001",
  "customer": {
    "id": 10001,
    "name": "Alice",
    "profile": {
      "level": "VIP", 
      "preferences": ["electronics", "gadgets", "books"],
      "purchase_history": [
        {"category": "electronics", "frequency": 15},
        {"category": "books", "frequency": 8}
      ]
    },
    "address": {"city": "Beijing", "district": "Chaoyang District"}
  },
  "items": [
    {
      "sku": "PHONE-001", 
      "name": "iPhone 15", 
      "price": 6999.00, 
      "qty": 1,
      "attributes": {"color": "Blue", "storage": "256GB"},
      "promotion": {"type": "vip_discount", "discount": 500}
    }
  ],
  "payment": {
    "method": "alipay", 
    "amount": 7197.00,
    "promotion_applied": {"code": "VIP500", "discount": 500}
  },
  "logistics": {
    "shipping_method": "express",
    "estimated_delivery": "2024-12-03",
    "tracking_events": [
      {"status": "ordered", "timestamp": "2024-12-01T10:00:00"},
      {"status": "paid", "timestamp": "2024-12-01T10:05:00"}
    ]
  },
  "user_feedback": {
    "rating": "5 Stars",
    "comment": "Great product! Fast delivery!"
  }
}
```

**Core Technical Challenges**:

1. **Personalized Recommendation Challenge**: Need real-time analysis of customer `preferences` arrays and `purchase_history` nested structures
2. **Dynamic Promotion Strategy**: Each item's `promotion` information has an unfixed structure; different promotion types have completely different JSON structures
3. **Real-time Inventory Alerts**: Need to extract all SKUs from the order's `items` array for real-time sales statistics
4. **Customer Behavior Analysis**: Analyze the complete path from browsing to order placement
5. **Multilingual Content Handling**: Customer names, addresses, and reviews contain multiple languages and emoji symbols

#### 1.2.2 IoT Scenario: Real-time Processing of Complex Industrial Equipment Monitoring Data

**Business Scenario Description**:
A manufacturing enterprise has thousands of production devices, each reporting complex monitoring data every minute:

```json
{
  "device_id": "MACHINE-001",
  "timestamp": "2024-12-01T10:30:00Z",
  "location": {
    "building": "Factory-A", 
    "floor": 2, 
    "production_line": "Production-Line-1"
  },
  "sensors": {
    "temperature": {"value": 85.2, "unit": "celsius", "status": "normal"},
    "vibration": {
      "x_axis": {"value": 0.02, "threshold": 0.05, "status": "normal"},
      "y_axis": {"value": 0.03, "threshold": 0.05, "status": "normal"},
      "z_axis": {"value": 0.08, "threshold": 0.05, "status": "warning"}
    }
  },
  "operational_status": {
    "machine_state": "running",
    "production_rate": 85.5,
    "efficiency": 92.3,
    "maintenance": {
      "last_service": "2024-11-15T08:00:00Z",
      "next_scheduled": "2025-02-15T08:00:00Z",
      "parts_status": [
        {"part": "Motor Bearing", "condition": "Good", "life_remaining": 75},
        {"part": "Conveyor Belt", "condition": "Fair", "life_remaining": 45}
      ]
    }
  },
  "alerts": {
    "message": "Device running normally",
    "level": "info"
  }
}
```

**Core Technical Challenges**:

1. **Heterogeneous Device Data Fusion**: Different device models have completely different `sensors` structures
2. **Real-time Anomaly Detection**: Need to monitor multiple nested metrics simultaneously
3. **Complex Maintenance Planning**: Each part in the `maintenance.parts_status` array has a different lifespan
4. **Multi-dimensional Production Analysis**: Need to analyze by production line, floor, device type, and other dimensions

#### 1.2.3 Financial Scenario: Real-time Decision Making for Complex Transaction Risk Control

**Business Scenario Description**:
An internet bank needs to perform real-time risk assessment on every transaction:

```json
{
  "transaction_id": "TXN-20241201-001",
  "timestamp": "2024-12-01T14:35:22Z",
  "user": {
    "id": 30001,
    "name": "Bob",
    "profile": {
      "age": 28,
      "credit_score": 720,
      "account_level": "Gold"
    },
    "behavior_pattern": {
      "typical_amount_range": {"min": 500, "max": 3000},
      "location_history": [
        {"city": "Beijing", "frequency": 85},
        {"city": "Shanghai", "frequency": 10}
      ]
    }
  },
  "transaction": {
    "amount": 8500.00,
    "currency": "CNY",
    "type": "transfer",
    "merchant": {"name": "Luxury Store", "category": "retail"}
  },
  "device": {
    "type": "mobile",
    "fingerprint": "ABC123XYZ789",
    "location": {"city": "Shanghai", "ip": "121.xxx.xxx.xxx"},
    "is_new_device": true,
    "trusted_score": 0.3
  },
  "risk_analysis": {
    "automated_factors": [
      {"factor": "amount_anomaly", "score": 0.8, "reason": "Amount exceeds normal range"},
      {"factor": "location_mismatch", "score": 0.6, "reason": "Transaction in different city"}
    ],
    "final_decision": {
      "action": "manual_review",
      "confidence": 0.85,
      "reason": "Multiple risk factors detected"
    }
  }
}
```

**Core Technical Challenges**:

1. **Complex Risk Factor Real-time Calculation**: Need to simultaneously analyze risk factors from multiple nested objects
2. **Fast Decision Requirements**: Risk control decisions must be completed within a short time frame
3. **Dynamic Rule Engine**: Risk control rules change frequently, and data structures evolve continuously
4. **Compliance Audit Trail**: Need to retain complete decision processes, supporting complex audit queries

### 1.3 Limitations of Traditional Approaches

**Technical Challenges**:

* **Performance Bottleneck**: Traditional databases have limited JSON query performance
* **High Storage Cost**: JSON data is redundant with low storage efficiency
* **Development Complexity**: Complex ETL transformations are required
* **Insufficient Real-time Capability**: Batch processing mode cannot meet real-time requirements
* **Scalability Limitations**: Single-machine architecture struggles to handle large-scale data
* **Multilingual Support**: Chinese, emoji, and other special characters are difficult to handle

***

## Chapter 2: Singdata Lakehouse Solutions

### 2.1 Core Technical Advantages

#### 2.1.1 Native JSON Support

**Solution Features**:

* **Native Data Type Support**: JSON is a first-class citizen, no pre-defined schema required
* **Dynamic Structure Adaptation**: New fields can be added without downtime or table structure modification
* **Zero Transformation Cost**: JSON data is stored and queried directly, no ETL preprocessing needed
* **Multilingual Compatibility**: Full support for Chinese and emoji content

```sql
-- Create sample table
CREATE TABLE IF NOT EXISTS orders (
    id INT,
    order_data JSON
);

-- Directly store JSON data with different structures (including Chinese)
INSERT INTO orders VALUES 
(1, parse_json('{"customer": {"name": "Alice"}, "promotion": {"type": "vip_discount", "amount": 500}}')),
(2, parse_json('{"customer": {"name": "Bob"}, "promotion": {"type": "flash_sale", "percentage": 0.2}}')),
(3, parse_json('{"customer": {"name": "Charlie"}, "promotion": {"type": "bundle_deal", "required_items": 3}}'));

-- Query promotion data with different structures
SELECT 
    id,
    json_extract_string(order_data, "$.customer.name") as customer_name,
    json_extract_string(order_data, "$.promotion.type") as promotion_type
FROM orders;
```

#### 2.1.2 Intelligent Columnar Storage

**Solution Features**:

* **Automatic Field Optimization**: Frequently accessed JSON fields are automatically converted to columnar storage
* **Path Index Optimization**: Efficient indexes are built for commonly used JSON paths
* **Column Pruning Technology**: Only reads the JSON fields needed by the query, reducing I/O overhead

```sql
-- Use the previously created orders table for high-frequency field queries
SELECT 
    json_extract_string(order_data, "$.customer.name") as customer_name,
    json_extract_double(order_data, "$.promotion.amount") as discount_amount
FROM orders 
WHERE json_extract_string(order_data, "$.promotion.type") = 'vip_discount';
```

#### 2.1.3 High-Performance Query Engine

**Solution Features**:

* **Parallel Processing Framework**: Complex JSON queries are automatically parallelized
* **In-Memory Computing Optimization**: Hot JSON data resides in memory
* **Intelligent Caching Mechanism**: Results for frequently accessed JSON paths are cached

#### 2.1.4 Real-time Stream Processing Integration

**Solution Features**:

* **TABLE STREAM Technology**: Captures JSON data changes for incremental processing
* **Dynamic Table Auto-Refresh**: Real-time aggregation of complex JSON data
* **Unified Stream-Batch Processing**: Unified handling of real-time streams and historical batch data

```sql
-- Create IoT sensor data table
CREATE TABLE IF NOT EXISTS iot_sensors (
    device_id STRING,
    device_data JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Insert sample IoT data
INSERT INTO iot_sensors VALUES
('DEVICE-001', parse_json('{"device_id": "DEVICE-001", "sensors": {"temperature": {"value": 86.5}}, "location": "Factory A"}'), CURRENT_TIMESTAMP());

-- Create alert events table
CREATE TABLE IF NOT EXISTS alert_events (
    device_id STRING,
    temp_value DOUBLE,
    alert_time TIMESTAMP
);

-- Real-time anomaly detection (manual simulation)
INSERT INTO alert_events 
SELECT 
    json_extract_string(device_data, "$.device_id") as device_id,
    json_extract_double(device_data, "$.sensors.temperature.value") as temp_value,
    CURRENT_TIMESTAMP() as alert_time
FROM iot_sensors 
WHERE json_extract_double(device_data, "$.sensors.temperature.value") > 85;
```

***

## Chapter 3: Solutions for Core Technical Challenges

This chapter demonstrates in detail how Singdata Lakehouse specifically addresses each core technical challenge raised in Chapter 1. Every solution directly corresponds to a specific business challenge.

### 3.1 E-Commerce Scenario: Solutions to Technical Challenges

#### 3.1.1 Challenge 1: Nested Array Query for Personalized Recommendations

**Technical Challenge Description**:
Real-time analysis of customer `preferences` arrays and `purchase_history` nested structures is required. Traditional relational databases need complex multi-table JOINs or ETL preprocessing and cannot meet the response time requirements for real-time personalized recommendations.

**Singdata Lakehouse Solution**:

```sql
-- Create e-commerce order analysis table with native JSON support
CREATE TABLE IF NOT EXISTS ecommerce_orders_json (
    order_id STRING,
    order_data JSON,
    created_date DATE DEFAULT CURRENT_DATE()
);

-- Directly store complex nested structures, no preprocessing needed
INSERT INTO ecommerce_orders_json VALUES
('ORD-2024-001', parse_json('{
  "customer": {
    "id": 10001, 
    "name": "Alice", 
    "level": "diamond",
    "profile": {
      "preferences": ["electronics", "gadgets", "books"],
      "purchase_history": [
        {"category": "electronics", "frequency": 15},
        {"category": "books", "frequency": 8}
      ]
    }
  },
  "items": [{"sku": "PHONE-001", "category": "electronics", "price": 6999.00}],
  "payment": {"amount": 7098.00}
}'), CURRENT_DATE()),
('ORD-2024-002', parse_json('{
  "customer": {
    "id": 10002, 
    "name": "Bob", 
    "level": "diamond",
    "profile": {
      "preferences": ["books", "sports", "electronics"],
      "purchase_history": [
        {"category": "books", "frequency": 20},
        {"category": "sports", "frequency": 12}
      ]
    }
  },
  "items": [{"sku": "BOOK-001", "category": "books", "price": 299.00}],
  "payment": {"amount": 299.00}
}'), CURRENT_DATE()),
('ORD-2024-003', parse_json('{
  "customer": {
    "id": 10003, 
    "name": "Charlie", 
    "level": "diamond",
    "profile": {
      "preferences": ["gadgets", "electronics", "fashion"],
      "purchase_history": [
        {"category": "gadgets", "frequency": 25},
        {"category": "electronics", "frequency": 18}
      ]
    }
  },
  "items": [{"sku": "GADGET-001", "category": "gadgets", "price": 1599.00}],
  "payment": {"amount": 1599.00}
}'), CURRENT_DATE());

-- Direct access to nested arrays, no JOIN needed
SELECT 
    json_extract_string(order_data, "$.customer.id") as customer_id,
    json_extract_string(order_data, "$.customer.name") as customer_name,
    -- Directly extract the first element of the preferences array (primary preference)
    json_extract_string(order_data, "$.customer.profile.preferences[0]") as primary_preference,
    -- Directly extract the most frequent category from purchase history
    json_extract_int(order_data, "$.customer.profile.purchase_history[0].frequency") as top_frequency,
    -- Real-time customer value calculation
    json_extract_double(order_data, "$.payment.amount") as order_value
FROM ecommerce_orders_json
WHERE json_extract_string(order_data, "$.customer.level") = 'diamond'
ORDER BY json_extract_double(order_data, "$.payment.amount") DESC;
```

**Technical Value**:

1. **Zero ETL Processing**: Complex nested data is stored and queried directly
2. **Native Array Access**: `[0]` syntax directly accesses array elements without table splitting
3. **Real-time Aggregation**: Multi-dimensional customer profile analysis completed in a single query
4. **Automatic Optimization**: High-frequency fields are automatically stored in columnar format, improving query efficiency

#### 3.1.2 Challenge 2: Flexible Querying of Dynamic Promotion Structures

**Technical Challenge Description**:
Different promotion types (VIP discount, flash sale, bundle deal) have completely different JSON structures. Traditional fixed schemas cannot adapt and require pre-defining all possible promotion fields, resulting in high maintenance costs.

**Singdata Lakehouse Dynamic Schema Solution**:

```sql
-- Create promotion data table
CREATE TABLE IF NOT EXISTS promotion_orders_json (
    order_id STRING,
    order_data JSON,
    created_date DATE DEFAULT CURRENT_DATE()
);

-- Store promotion data with different structures in the same table
INSERT INTO promotion_orders_json VALUES
-- VIP discount: fixed amount structure
('ORD-VIP-001', parse_json('{"customer": {"name": "Alice"}, "promotion": {"type": "vip_discount", "amount": 500}}'), CURRENT_DATE()),
-- Flash sale: percentage structure  
('ORD-FLASH-001', parse_json('{"customer": {"name": "Bob"}, "promotion": {"type": "flash_sale", "percentage": 0.2}}'), CURRENT_DATE()),
-- Bundle deal: combined item structure
('ORD-BUNDLE-001', parse_json('{"customer": {"name": "Charlie"}, "promotion": {"type": "bundle_deal", "required_items": 3, "discount_per_item": 50}}'), CURRENT_DATE()),
-- Coupon: code structure
('ORD-COUPON-001', parse_json('{"customer": {"name": "Diana"}, "promotion": {"type": "coupon", "code": "SAVE20", "discount": 200}}'), CURRENT_DATE());

-- Adaptive query: one SQL handles all promotion types
SELECT 
    order_id,
    json_extract_string(order_data, "$.customer.name") as customer_name,
    json_extract_string(order_data, "$.promotion.type") as promotion_type,
    -- Automatically extract corresponding fields based on promotion type
    CASE WHEN json_extract_string(order_data, "$.promotion.type") = 'vip_discount' 
         THEN json_extract_double(order_data, "$.promotion.amount")
         WHEN json_extract_string(order_data, "$.promotion.type") = 'coupon' 
         THEN json_extract_double(order_data, "$.promotion.discount")
         ELSE 0 
    END as discount_amount,
    CASE WHEN json_extract_string(order_data, "$.promotion.type") = 'flash_sale' 
         THEN json_extract_double(order_data, "$.promotion.percentage") 
         ELSE 0 
    END as discount_percentage,
    CASE WHEN json_extract_string(order_data, "$.promotion.type") = 'bundle_deal' 
         THEN json_extract_int(order_data, "$.promotion.required_items")
         ELSE 0 
    END as bundle_items,
    CASE WHEN json_extract_string(order_data, "$.promotion.type") = 'coupon' 
         THEN json_extract_string(order_data, "$.promotion.code")
         ELSE NULL 
    END as coupon_code
FROM promotion_orders_json
WHERE json_extract_string(order_data, "$.promotion.type") IS NOT NULL;
```

**Technical Value**:

1. **Dynamic Schema Adaptation**: New promotion types are automatically supported with zero downtime
2. **Structure-Agnostic Queries**: A single SQL handles multiple data structures
3. **Business Agility**: Promotion rule changes do not require database schema modifications

#### 3.1.3 Challenge 3: Array Aggregation for Real-time Inventory Alerts

**Technical Challenge Description**:
All SKUs need to be extracted from the order's `items` array and sales statistics calculated in real time. Traditional approaches require complex triggers or scheduled ETL jobs, with high latency and resource consumption.

**Singdata Lakehouse Real-time Stream Processing Solution**:

```sql
-- Create inventory order data table
CREATE TABLE IF NOT EXISTS inventory_orders_json (
    order_id STRING,
    order_data JSON,
    created_date DATE DEFAULT CURRENT_DATE()
);

-- Insert order data containing SKUs and quantities
INSERT INTO inventory_orders_json VALUES
('ORD-INV-001', parse_json('{"items": [{"sku": "PHONE-001", "qty": 2}], "payment": {"amount": 13998.00}}'), CURRENT_DATE()),
('ORD-INV-002', parse_json('{"items": [{"sku": "BOOK-001", "qty": 5}], "payment": {"amount": 1495.00}}'), CURRENT_DATE()),
('ORD-INV-003', parse_json('{"items": [{"sku": "PHONE-001", "qty": 1}], "payment": {"amount": 6999.00}}'), CURRENT_DATE()),
('ORD-INV-004', parse_json('{"items": [{"sku": "GADGET-001", "qty": 3}], "payment": {"amount": 4797.00}}'), CURRENT_DATE()),
('ORD-INV-005', parse_json('{"items": [{"sku": "BOOK-001", "qty": 2}], "payment": {"amount": 598.00}}'), CURRENT_DATE());

-- Dynamic table for real-time inventory statistics with automatic refresh
CREATE OR REPLACE DYNAMIC TABLE IF NOT EXISTS real_time_inventory
REFRESH INTERVAL 1 MINUTES
AS SELECT 
    json_extract_string(order_data, "$.items[0].sku") as sku,
    SUM(json_extract_int(order_data, "$.items[0].qty")) as total_sold,
    COUNT(*) as order_count,
    MAX(created_date) as last_order_date,
    -- Real-time inventory alert threshold calculation
    CASE 
        WHEN SUM(json_extract_int(order_data, "$.items[0].qty")) > 5 THEN 'high_demand'
        WHEN SUM(json_extract_int(order_data, "$.items[0].qty")) > 2 THEN 'medium_demand'
        ELSE 'low_demand'
    END as demand_level
FROM inventory_orders_json 
WHERE json_extract_string(order_data, "$.items[0].sku") IS NOT NULL
GROUP BY json_extract_string(order_data, "$.items[0].sku");

-- Real-time query for inventory alerts
SELECT * FROM real_time_inventory 
WHERE demand_level = 'high_demand' 
ORDER BY total_sold DESC;
```

**Technical Value**:

1. **Unified Stream-Batch**: Dynamic tables automatically aggregate data changes
2. **Real-time Aggregation**: No need to manually maintain triggers and aggregation logic
3. **Zero Maintenance Cost**: The system automatically handles complex aggregation computations

### 3.2 IoT Scenario: Unified Processing of Complex Device Data

#### 3.2.1 Challenge 1: Unified Querying of Heterogeneous Device Data

**Technical Challenge Description**:
Different device models have completely different `sensors` structures: old devices only have temperature, while new devices have dozens of sensors. Traditional approaches require creating different table structures for each device type, resulting in severe data silos.

**Singdata Lakehouse Heterogeneous Data Unified Solution**:

```sql
-- Create IoT device monitoring table supporting any device structure
CREATE TABLE IF NOT EXISTS iot_devices_unified (
    device_id STRING,
    sensor_data JSON,
    collected_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Store device data with different structures in the same table
INSERT INTO iot_devices_unified VALUES
-- Basic sensor: temperature only
('BASIC-001', parse_json('{"device_type": "basic", "temp": 22.1, "battery": 85}'), CURRENT_TIMESTAMP()),
-- Standard sensor: temperature + humidity
('STANDARD-001', parse_json('{"device_type": "standard", "readings": {"temperature": 24.5, "humidity": 58.2}}'), CURRENT_TIMESTAMP()),
-- Advanced sensor: complete multi-dimensional data
('ADVANCED-001', parse_json('{"device_type": "advanced", "sensors": {"temperature": {"value": 85.2}, "vibration": {"x_axis": {"value": 0.02}}}}'), CURRENT_TIMESTAMP()),
-- Industrial sensor: most complex structure
('INDUSTRIAL-001', parse_json('{"device_type": "industrial", "sensors": {"temperature": {"value": 78.5}, "vibration": {"x_axis": {"value": 0.01}, "y_axis": {"value": 0.03}, "z_axis": {"value": 0.02}}, "pressure": {"value": 1013.25}}}'), CURRENT_TIMESTAMP());

-- Unified query interface, automatically adapting to different device structures
SELECT 
    device_id,
    json_extract_string(sensor_data, "$.device_type") as device_type,
    -- Compatible with multiple temperature field structures
    COALESCE(
        json_extract_double(sensor_data, "$.sensors.temperature.value"),    -- Advanced device
        json_extract_double(sensor_data, "$.readings.temperature"),         -- Standard device
        json_extract_double(sensor_data, "$.temp")                          -- Basic device
    ) as temperature,
    -- Optional advanced sensor data
    json_extract_double(sensor_data, "$.sensors.vibration.x_axis.value") as vibration_x,
    json_extract_double(sensor_data, "$.sensors.vibration.y_axis.value") as vibration_y,
    json_extract_double(sensor_data, "$.sensors.vibration.z_axis.value") as vibration_z,
    json_extract_double(sensor_data, "$.sensors.pressure.value") as pressure,
    -- Automatic device type identification
    CASE 
        WHEN json_extract_string(sensor_data, "$.sensors.vibration") IS NOT NULL THEN 'high_end_device'
        WHEN json_extract_string(sensor_data, "$.readings.humidity") IS NOT NULL THEN 'standard_device'
        ELSE 'basic_device'
    END as inferred_device_category
FROM iot_devices_unified
ORDER BY collected_time DESC;
```

**Technical Value**:

1. **Device Plug-and-Play**: New device types require no schema changes
2. **Unified Query Interface**: A single SQL supports all device types
3. **Intelligent Field Mapping**: COALESCE automatically adapts to different field structures

### 3.3 Financial Scenario: Real-time Decision Making for Complex Risk Control

#### 3.3.1 Challenge 1: Complex Risk Factor Real-time Calculation

**Technical Challenge Description**:
Multiple nested objects such as user behavior patterns, device trust scores, and geographic locations must be analyzed simultaneously as risk factors. Traditional approaches require multiple database queries and complex business logic calculations, unable to meet fast decision-making requirements.

**Singdata Lakehouse Multi-dimensional Risk Factor Parallel Calculation Solution**:

```sql
-- Create financial risk control data table
CREATE TABLE IF NOT EXISTS financial_risk_analysis (
    transaction_id STRING,
    risk_data JSON,
    analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Insert complex risk control test data
INSERT INTO financial_risk_analysis VALUES
('TXN-001', parse_json('{
  "user": {
    "id": "30001",
    "behavior_pattern": {
      "typical_amount_range": {"min": 500, "max": 3000},
      "location_history": [{"city": "Beijing", "frequency": 85}]
    }
  },
  "transaction": {"amount": 8500.00},
  "device": {"is_new_device": true, "trusted_score": 0.3, "location": {"city": "Shanghai"}}
}'), CURRENT_TIMESTAMP()),
('TXN-002', parse_json('{
  "user": {
    "id": "30002",
    "behavior_pattern": {
      "typical_amount_range": {"min": 1000, "max": 5000},
      "location_history": [{"city": "Shanghai", "frequency": 90}]
    }
  },
  "transaction": {"amount": 2500.00},
  "device": {"is_new_device": false, "trusted_score": 0.9, "location": {"city": "Shanghai"}}
}'), CURRENT_TIMESTAMP()),
('TXN-003', parse_json('{
  "user": {
    "id": "30003",
    "behavior_pattern": {
      "typical_amount_range": {"min": 200, "max": 1500},
      "location_history": [{"city": "Shenzhen", "frequency": 95}]
    }
  },
  "transaction": {"amount": 4500.00},
  "device": {"is_new_device": true, "trusted_score": 0.2, "location": {"city": "Beijing"}}
}'), CURRENT_TIMESTAMP());

-- Complete complex multi-dimensional risk assessment in a single query
SELECT 
    transaction_id,
    json_extract_string(risk_data, "$.user.id") as user_id,
    -- Real-time amount anomaly risk calculation
    CASE 
        WHEN json_extract_double(risk_data, "$.transaction.amount") > 
             json_extract_double(risk_data, "$.user.behavior_pattern.typical_amount_range.max") * 2
        THEN 0.8  -- Exceeds normal amount by 2x: high risk
        WHEN json_extract_double(risk_data, "$.transaction.amount") > 
             json_extract_double(risk_data, "$.user.behavior_pattern.typical_amount_range.max") * 1.5
        THEN 0.5  -- Exceeds normal amount by 1.5x: medium risk
        ELSE 0.2  -- Within normal range: low risk
    END as amount_risk_score,
    
    -- Real-time device trust risk calculation
    CASE 
        WHEN json_extract_string(risk_data, "$.device.is_new_device") = 'true' 
        THEN 1.0 - json_extract_double(risk_data, "$.device.trusted_score")
        ELSE 0.1
    END as device_risk_score,
    
    -- Real-time geographic location risk calculation
    CASE 
        WHEN json_extract_string(risk_data, "$.device.location.city") != 
             json_extract_string(risk_data, "$.user.behavior_pattern.location_history[0].city")
        THEN 0.6  -- Transaction in different city: medium risk
        ELSE 0.1  -- Usual location: low risk
    END as location_risk_score,
    
    -- Comprehensive risk score: weighted algorithm calculated in one pass
    ((CASE 
        WHEN json_extract_double(risk_data, "$.transaction.amount") > 
             json_extract_double(risk_data, "$.user.behavior_pattern.typical_amount_range.max") * 2
        THEN 0.8 ELSE 0.2 END) * 0.4 +  -- Amount risk weight 40%
     (CASE 
        WHEN json_extract_string(risk_data, "$.device.is_new_device") = 'true' 
        THEN 1.0 - json_extract_double(risk_data, "$.device.trusted_score")
        ELSE 0.1 END) * 0.3 +           -- Device risk weight 30%
     (CASE 
        WHEN json_extract_string(risk_data, "$.device.location.city") != 
             json_extract_string(risk_data, "$.user.behavior_pattern.location_history[0].city")
        THEN 0.6 ELSE 0.1 END) * 0.3    -- Location risk weight 30%
    ) as final_risk_score,
    
    -- Real-time decision recommendation
    CASE 
        WHEN ((CASE 
            WHEN json_extract_double(risk_data, "$.transaction.amount") > 
                 json_extract_double(risk_data, "$.user.behavior_pattern.typical_amount_range.max") * 2
            THEN 0.8 ELSE 0.2 END) * 0.4 +
         (CASE 
            WHEN json_extract_string(risk_data, "$.device.is_new_device") = 'true' 
            THEN 1.0 - json_extract_double(risk_data, "$.device.trusted_score")
            ELSE 0.1 END) * 0.3 +
         (CASE 
            WHEN json_extract_string(risk_data, "$.device.location.city") != 
                 json_extract_string(risk_data, "$.user.behavior_pattern.location_history[0].city")
            THEN 0.6 ELSE 0.1 END) * 0.3) > 0.7 THEN 'REJECT'
        WHEN ((CASE 
            WHEN json_extract_double(risk_data, "$.transaction.amount") > 
                 json_extract_double(risk_data, "$.user.behavior_pattern.typical_amount_range.max") * 2
            THEN 0.8 ELSE 0.2 END) * 0.4 +
         (CASE 
            WHEN json_extract_string(risk_data, "$.device.is_new_device") = 'true' 
            THEN 1.0 - json_extract_double(risk_data, "$.device.trusted_score")
            ELSE 0.1 END) * 0.3 +
         (CASE 
            WHEN json_extract_string(risk_data, "$.device.location.city") != 
                 json_extract_string(risk_data, "$.user.behavior_pattern.location_history[0].city")
            THEN 0.6 ELSE 0.1 END) * 0.3) > 0.4 THEN 'MANUAL_REVIEW'
        ELSE 'APPROVE'
    END as recommended_action
FROM financial_risk_analysis
ORDER BY final_risk_score DESC;
```

**Technical Value**:

1. **Multi-dimensional Analysis in a Single Query**: All risk factor calculations completed in one SQL
2. **Parallel Access to Nested Objects**: Simultaneously extract multiple deeply nested fields
3. **Fast Decision Support**: Significantly reduces risk control decision processing time

***

## Chapter 4: Deep Technical Implementation and Advanced Optimization

This chapter demonstrates the advanced technical features of Singdata Lakehouse JSON processing in depth. Each technical implementation provides a deep solution targeting the specific technical challenges raised in Chapter 1.

### 4.1 Time-series Array Processing for the "Customer Behavior Analysis" Challenge

#### 4.1.1 Technical Challenge Review

**Original Challenge**: Analyzing the complete path from browsing to order placement, with data stored in the `logistics.tracking_events` time-series array. Traditional approaches require splitting array data into multiple rows for storage, making queries complex and performance-limited.

#### 4.1.2 Singdata Lakehouse Time-series Array Processing Implementation

**Core Technical Implementation**:

```sql
-- Create customer behavior analysis table
CREATE TABLE IF NOT EXISTS customer_behavior_analysis (
    order_id STRING,
    behavior_data JSON,
    created_date DATE DEFAULT CURRENT_DATE()
);

-- Insert time-series behavior data
INSERT INTO customer_behavior_analysis VALUES
('ORD-BEHAVIOR-001', parse_json('{
  "customer": {"id": 10001, "name": "Alice"},
  "items": [{"sku": "PHONE-001", "price": 6999.00}],
  "behavior_tracking": {
    "source": "search_engine",
    "conversion_funnel": [
      {"event": "product_view", "timestamp": "2024-12-01T09:00:00", "duration": 120},
      {"event": "add_to_cart", "timestamp": "2024-12-01T09:02:00", "duration": 30},
      {"event": "checkout_start", "timestamp": "2024-12-01T09:02:30", "duration": 180},
      {"event": "payment_complete", "timestamp": "2024-12-01T09:05:30", "duration": 45}
    ]
  },
  "logistics": {
    "tracking_events": [
      {"status": "ordered", "timestamp": "2024-12-01T09:05:30", "location": "Beijing"},
      {"status": "paid", "timestamp": "2024-12-01T09:06:00", "location": "Beijing"},
      {"status": "shipped", "timestamp": "2024-12-01T14:00:00", "location": "Beijing Warehouse"},
      {"status": "delivered", "timestamp": "2024-12-02T10:00:00", "location": "Chaoyang District"}
    ]
  }
}'), CURRENT_DATE()),
('ORD-BEHAVIOR-002', parse_json('{
  "customer": {"id": 10002, "name": "Bob"},
  "items": [{"sku": "BOOK-001", "price": 299.00}],
  "behavior_tracking": {
    "source": "direct_visit",
    "conversion_funnel": [
      {"event": "product_view", "timestamp": "2024-12-01T10:00:00", "duration": 200},
      {"event": "add_to_cart", "timestamp": "2024-12-01T10:03:20", "duration": 45},
      {"event": "checkout_start", "timestamp": "2024-12-01T10:04:05", "duration": 90},
      {"event": "payment_complete", "timestamp": "2024-12-01T10:05:35", "duration": 30}
    ]
  },
  "logistics": {
    "tracking_events": [
      {"status": "ordered", "timestamp": "2024-12-01T10:05:35", "location": "Shanghai"},
      {"status": "paid", "timestamp": "2024-12-01T10:06:00", "location": "Shanghai"},
      {"status": "shipped", "timestamp": "2024-12-01T16:00:00", "location": "Shanghai Warehouse"},
      {"status": "delivered", "timestamp": "2024-12-02T14:00:00", "location": "Pudong New Area"}
    ]
  }
}'), CURRENT_DATE());

-- Complex time-series analysis: complete behavior path analysis in a single query
SELECT 
    order_id,
    json_extract_string(behavior_data, "$.customer.id") as customer_id,
    json_extract_string(behavior_data, "$.customer.name") as customer_name,
    -- Extract the complete conversion funnel path
    json_extract_string(behavior_data, "$.behavior_tracking.conversion_funnel[0].event") as funnel_step1,
    json_extract_string(behavior_data, "$.behavior_tracking.conversion_funnel[1].event") as funnel_step2,
    json_extract_string(behavior_data, "$.behavior_tracking.conversion_funnel[2].event") as funnel_step3,
    json_extract_string(behavior_data, "$.behavior_tracking.conversion_funnel[3].event") as funnel_step4,
    
    -- Calculate duration at each stage
    json_extract_int(behavior_data, "$.behavior_tracking.conversion_funnel[0].duration") as view_duration,
    json_extract_int(behavior_data, "$.behavior_tracking.conversion_funnel[1].duration") as cart_duration,
    json_extract_int(behavior_data, "$.behavior_tracking.conversion_funnel[2].duration") as checkout_duration,
    
    -- Logistics status time-series analysis
    json_extract_string(behavior_data, "$.logistics.tracking_events[0].status") as initial_status,
    json_extract_string(behavior_data, "$.logistics.tracking_events[3].status") as final_status,
    
    -- Real-time conversion efficiency calculation
    CASE 
        WHEN json_extract_string(behavior_data, "$.logistics.tracking_events[1].status") = 'paid' 
        THEN 'successful_conversion'
        ELSE 'incomplete_conversion'
    END as conversion_result,
    
    -- Geographic location change tracking
    json_extract_string(behavior_data, "$.logistics.tracking_events[0].location") as order_location,
    json_extract_string(behavior_data, "$.logistics.tracking_events[3].location") as delivery_location,
    
    -- Conversion efficiency analysis
    (json_extract_int(behavior_data, "$.behavior_tracking.conversion_funnel[0].duration") +
     json_extract_int(behavior_data, "$.behavior_tracking.conversion_funnel[1].duration") +
     json_extract_int(behavior_data, "$.behavior_tracking.conversion_funnel[2].duration") +
     json_extract_int(behavior_data, "$.behavior_tracking.conversion_funnel[3].duration")) as total_conversion_time
    
FROM customer_behavior_analysis
WHERE json_extract_string(behavior_data, "$.behavior_tracking.conversion_funnel") IS NOT NULL
ORDER BY total_conversion_time ASC;
```

**Technical Value**:

1. **Zero Data Restructuring**: Time-series arrays are analyzed directly without splitting storage
2. **Single Query Full Chain**: The complete path from browsing to delivery is obtained in one go
3. **Real-time Conversion Analysis**: Quickly calculates conversion rates and user behavior patterns

### 4.2 Dynamic Array Computation for the "Complex Maintenance Planning" Challenge

#### 4.2.1 Technical Challenge Review

**Original Challenge**: Each part in the `maintenance.parts_status` array has a different lifespan, requiring dynamic calculation of maintenance priorities. Traditional approaches need complex stored procedures and scheduled calculations.

#### 4.2.2 Singdata Lakehouse Dynamic Array Calculation Implementation

**Core Technical Implementation**:

```sql
-- Create device maintenance analysis table
CREATE TABLE IF NOT EXISTS device_maintenance_analysis (
    device_id STRING,
    maintenance_data JSON,
    collected_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Store complex part status data
INSERT INTO device_maintenance_analysis VALUES
('MACHINE-COMPLEX-001', parse_json('{
  "device_info": {"type": "production_machine", "location": "Factory A - Production Line 1"},
  "operational_status": {
    "machine_state": "running",
    "production_rate": 85.5,
    "maintenance": {
      "last_service": "2024-11-15T08:00:00Z",
      "next_scheduled": "2025-02-15T08:00:00Z",
      "parts_status": [
        {"part": "Main Motor", "condition": "Good", "life_remaining": 75, "cost": 50000, "priority": 1},
        {"part": "Conveyor Belt", "condition": "Fair", "life_remaining": 45, "cost": 8000, "priority": 2},
        {"part": "Hydraulic System", "condition": "Good", "life_remaining": 30, "cost": 25000, "priority": 1},
        {"part": "Control Panel", "condition": "Excellent", "life_remaining": 90, "cost": 15000, "priority": 3},
        {"part": "Cooling System", "condition": "Needs Attention", "life_remaining": 20, "cost": 12000, "priority": 1}
      ]
    }
  }
}'), CURRENT_TIMESTAMP()),
('MACHINE-COMPLEX-002', parse_json('{
  "device_info": {"type": "assembly_machine", "location": "Factory B - Production Line 2"},
  "operational_status": {
    "machine_state": "running",
    "production_rate": 92.3,
    "maintenance": {
      "last_service": "2024-10-20T08:00:00Z",
      "next_scheduled": "2025-01-20T08:00:00Z",
      "parts_status": [
        {"part": "Assembly Arm", "condition": "Good", "life_remaining": 85, "cost": 35000, "priority": 1},
        {"part": "Sensor", "condition": "Fair", "life_remaining": 55, "cost": 5000, "priority": 2},
        {"part": "Circuit Board", "condition": "Excellent", "life_remaining": 95, "cost": 8000, "priority": 2},
        {"part": "Motor", "condition": "Needs Attention", "life_remaining": 25, "cost": 18000, "priority": 1}
      ]
    }
  }
}'), CURRENT_TIMESTAMP());

-- Intelligent maintenance priority dynamic calculation
SELECT 
    device_id,
    json_extract_string(maintenance_data, "$.device_info.location") as location,
    json_extract_string(maintenance_data, "$.device_info.type") as device_type,
    
    -- Comprehensive analysis of part status array
    json_extract_string(maintenance_data, "$.operational_status.maintenance.parts_status[0].part") as part1_name,
    json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[0].life_remaining") as part1_life,
    json_extract_string(maintenance_data, "$.operational_status.maintenance.parts_status[1].part") as part2_name,
    json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[1].life_remaining") as part2_life,
    json_extract_string(maintenance_data, "$.operational_status.maintenance.parts_status[2].part") as part3_name,
    json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[2].life_remaining") as part3_life,
    
    -- Intelligent maintenance decision algorithm: comprehensive consideration of lifespan, cost, and priority
    CASE 
        -- High-priority parts with less than 30% life remaining: urgent maintenance
        WHEN (json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[0].life_remaining") < 30 AND 
              json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[0].priority") = 1) OR
             (json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[2].life_remaining") < 30 AND 
              json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[2].priority") = 1) OR
             (COALESCE(json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[4].life_remaining"), 100) < 30 AND 
              COALESCE(json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[4].priority"), 2) = 1)
        THEN 'urgent_maintenance'
        -- Any part with less than 50% life remaining: scheduled maintenance
        WHEN json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[0].life_remaining") < 50 OR
             json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[1].life_remaining") < 50 OR
             json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[2].life_remaining") < 50 OR
             COALESCE(json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[3].life_remaining"), 100) < 50 OR
             COALESCE(json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[4].life_remaining"), 100) < 50
        THEN 'scheduled_maintenance'
        ELSE 'normal_operation'
    END as maintenance_priority,
    
    -- Identify the most critical part (high-priority part with shortest life remaining)
    LEAST(
        CASE WHEN json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[0].priority") = 1 
             THEN json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[0].life_remaining") 
             ELSE 100 END,
        CASE WHEN COALESCE(json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[2].priority"), 2) = 1 
             THEN json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[2].life_remaining") 
             ELSE 100 END,
        CASE WHEN COALESCE(json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[4].priority"), 2) = 1 
             THEN COALESCE(json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[4].life_remaining"), 100)
             ELSE 100 END
    ) as critical_part_min_life,
    
    -- Maintenance cost estimation (dynamically calculated based on part status)
    (CASE WHEN json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[0].life_remaining") < 30 
          THEN json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[0].cost") ELSE 0 END +
     CASE WHEN json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[1].life_remaining") < 30 
          THEN json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[1].cost") ELSE 0 END +
     CASE WHEN json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[2].life_remaining") < 30 
          THEN json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[2].cost") ELSE 0 END +
     CASE WHEN COALESCE(json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[3].life_remaining"), 100) < 30 
          THEN COALESCE(json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[3].cost"), 0) ELSE 0 END +
     CASE WHEN COALESCE(json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[4].life_remaining"), 100) < 30 
          THEN COALESCE(json_extract_int(maintenance_data, "$.operational_status.maintenance.parts_status[4].cost"), 0) ELSE 0 END
    ) as estimated_maintenance_cost
    
FROM device_maintenance_analysis
WHERE json_extract_string(maintenance_data, "$.operational_status.maintenance.parts_status") IS NOT NULL
ORDER BY critical_part_min_life ASC;
```

**Technical Value**:

1. **Intelligent Decision Algorithm**: Complex maintenance strategy integrating lifespan, cost, and priority
2. **Native Array Computation**: Complex mathematical operations on arrays without splitting
3. **Real-time Cost Estimation**: Dynamically calculates maintenance budget based on real-time part status

### 4.3 Performance Optimization Techniques

#### 4.3.1 High-Frequency Field Access Pattern Optimization

```sql
-- Create performance optimization demo table
CREATE TABLE IF NOT EXISTS performance_orders (
    id INT,
    order_data JSON,
    created_date DATE DEFAULT CURRENT_DATE()
);

-- Insert test data
INSERT INTO performance_orders VALUES
(1, parse_json('{"customer": {"id": "C001", "level": "VIP"}, "payment": {"amount": 1500.00}, "items": [{"detail": {"description": "Premium Electronics"}}]}'), CURRENT_DATE()),
(2, parse_json('{"customer": {"id": "C002", "level": "regular"}, "payment": {"amount": 2300.00}, "items": [{"detail": {"description": "Home Goods"}}]}'), CURRENT_DATE()),
(3, parse_json('{"customer": {"id": "C003", "level": "VIP"}, "payment": {"amount": 800.00}, "items": [{"detail": {"description": "Daily Necessities"}}]}'), CURRENT_DATE()),
(4, parse_json('{"customer": {"id": "C004", "level": "diamond"}, "payment": {"amount": 3500.00}, "items": [{"detail": {"description": "Luxury Goods"}}]}'), CURRENT_DATE());

-- High-frequency field access pattern optimization
WITH high_performance_query AS (
    SELECT 
        -- Top-level field access: automatic columnar storage optimization
        json_extract_string(order_data, "$.customer.id") as customer_id,
        json_extract_double(order_data, "$.payment.amount") as amount,
        json_extract_string(order_data, "$.customer.level") as level,
        
        -- Batch field extraction: reduce repeated JSON parsing overhead
        order_data as full_order_data,
        created_date
    FROM performance_orders 
    WHERE json_extract_string(order_data, "$.customer.id") IS NOT NULL  -- Efficient top-level field filtering
      AND json_extract_double(order_data, "$.payment.amount") > 1000    -- Efficient numeric field filtering
)

-- Secondary computation optimization: complex analysis based on pre-extracted fields
SELECT 
    customer_id,
    level,
    amount,
    -- Complex nested fields extracted on demand (avoid repeated full-table parsing)
    json_extract_string(full_order_data, "$.items[0].detail.description") as product_description,
    
    -- Aggregation optimization: pre-group to reduce computation
    CASE 
        WHEN amount > 3000 THEN 'high_value'
        WHEN amount > 1500 THEN 'medium_value'
        ELSE 'low_value'
    END as value_segment
FROM high_performance_query
ORDER BY amount DESC;
```

#### 4.3.2 Alternative Solutions for JSON Data Updates

**Important Technical Limitation**: After practical verification, Singdata Lakehouse does not support `json_set`, `json_insert`, `json_remove`, or other JSON modification functions. Below are verified alternative solutions:

**Approach 1: Complete JSON Reconstruction (suitable for simple updates)**

```sql
-- Create transaction demo table
CREATE TABLE IF NOT EXISTS transaction_demo (
    customer_id STRING,
    customer_data JSON,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Insert initial data
INSERT INTO transaction_demo VALUES
('10001', parse_json('{"name": "Alice", "level": "regular", "profile": {"upgrade_date": null}, "payment": {"vip_discount": 0}}'), CURRENT_TIMESTAMP());

-- Use parse_json + CONCAT to reconstruct JSON object for update
UPDATE transaction_demo 
SET customer_data = parse_json(CONCAT(
    '{"name": "', json_extract_string(customer_data, "$.name"), '", ',
    '"level": "VIP", ',
    '"profile": {"upgrade_date": "2024-12-01"}, ',
    '"payment": {"vip_discount": 500.0}}'
)),
updated_time = CURRENT_TIMESTAMP()
WHERE customer_id = '10001'
  AND json_extract_string(customer_data, "$.level") != 'VIP';

-- Verify update result
SELECT 
    customer_id,
    json_extract_string(customer_data, "$.name") as name,
    json_extract_string(customer_data, "$.level") as level,
    json_extract_string(customer_data, "$.profile.upgrade_date") as upgrade_date,
    json_extract_double(customer_data, "$.payment.vip_discount") as vip_discount
FROM transaction_demo
WHERE customer_id = '10001';
```

**Approach 2: Hybrid Storage Strategy (recommended for frequent updates)**

```sql
-- Separate frequently updated fields; use JSON for stable data
CREATE TABLE IF NOT EXISTS hybrid_storage_demo (
    id INT,
    user_level STRING,  -- Frequently updated fields stored separately
    update_count INT,   -- Frequently updated fields stored separately
    user_profile JSON,  -- Stable complex data stored as JSON
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Insert hybrid storage data
INSERT INTO hybrid_storage_demo VALUES
(1, 'VIP', 5, 
 parse_json('{"preferences": ["electronics", "books"], "address": {"city": "Beijing", "district": "Chaoyang District"}}'),
 CURRENT_TIMESTAMP());

-- Query hybrid storage data
SELECT 
    id,
    user_level,  -- Relational field, high update efficiency
    update_count,  -- Relational field, high update efficiency
    json_extract_string(user_profile, "$.preferences[0]") as primary_preference,  -- JSON field, flexible querying
    json_extract_string(user_profile, "$.address.city") as city  -- JSON field, structured storage
FROM hybrid_storage_demo;
```

***

## Chapter 5: Chinese and Special Character Handling Guide

### 5.1 Chinese and Emoji Support Verification

Based on comprehensive testing, Singdata Lakehouse provides complete support for Chinese and emoji symbols:

#### 5.1.1 Fully Supported Scenarios

**Chinese Content Values**:

```sql
-- Create user data table
CREATE TABLE IF NOT EXISTS user_data_chinese (
    id STRING,
    data JSON
);

-- Insert Chinese content
INSERT INTO user_data_chinese VALUES
('user001', parse_json('{"name": "Alice", "city": "Beijing", "message": "Hello World!"}')),
('user002', parse_json('{"name": "Bob", "city": "Shanghai", "message": "Data processing is simple"}')),
('user003', parse_json('{"name": "Charlie", "city": "Shenzhen", "message": "JSON features are powerful"}'));

-- Query Chinese content
SELECT 
    json_extract_string(data, "$.name") as name,
    json_extract_string(data, "$.city") as city,
    json_extract_string(data, "$.message") as message
FROM user_data_chinese;
```

**Emoji Symbols**:

```sql
-- Create social data table
CREATE TABLE IF NOT EXISTS social_data_emoji (
    id STRING,
    data JSON
);

-- Insert emoji data
INSERT INTO social_data_emoji VALUES
('post001', parse_json('{"content": "Feeling great today😊", "reactions": "👍❤️🔥", "rating": "⭐⭐⭐⭐⭐"}')),
('post002', parse_json('{"content": "Product quality is really good👌", "reactions": "👏🎉💯", "rating": "⭐⭐⭐⭐"}')),
('post003', parse_json('{"content": "Very satisfied with the service🙂", "reactions": "😀👍✨", "rating": "⭐⭐⭐⭐⭐"}'));

-- Query emoji data
SELECT 
    json_extract_string(data, "$.content") as content,
    json_extract_string(data, "$.reactions") as reactions,
    json_extract_string(data, "$.rating") as rating
FROM social_data_emoji;
```

**Complex Chinese Content**:

```sql
-- Create feedback data table
CREATE TABLE IF NOT EXISTS feedback_data_complex (
    id STRING,
    data JSON,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Insert complex Chinese and emoji content
INSERT INTO feedback_data_complex VALUES
('fb001', parse_json('{"comment": "Product quality is great, fast delivery, good customer service👍", "sentiment": "positive", "tags": ["quality", "logistics", "service"]}'), CURRENT_TIMESTAMP()),
('fb002', parse_json('{"comment": "Beautiful packaging, powerful features, very satisfied😊", "sentiment": "positive", "tags": ["packaging", "features", "satisfaction"]}'), CURRENT_TIMESTAMP()),
('fb003', parse_json('{"comment": "Great value, recommended purchase🛒", "sentiment": "positive", "tags": ["value", "recommendation"]}'), CURRENT_TIMESTAMP());

-- Query complex content
SELECT 
    id,
    json_extract_string(data, "$.comment") as comment,
    json_extract_string(data, "$.sentiment") as sentiment,
    json_extract_string(data, "$.tags[0]") as first_tag,
    json_extract_string(data, "$.tags[1]") as second_tag
FROM feedback_data_complex
ORDER BY created_time DESC;
```

#### 5.1.2 Querying Chinese and Emoji Data

```sql
-- Create user feedback data table
CREATE TABLE IF NOT EXISTS user_feedback_full (
    id STRING,
    data JSON,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Insert test data containing Chinese and emoji
INSERT INTO user_feedback_full VALUES
('user001', parse_json('{"name": "Alice", "city": "Beijing", "comment": "Product is great😊", "score": 5}'), CURRENT_TIMESTAMP()),
('user002', parse_json('{"name": "Bob", "city": "Shanghai", "comment": "Good service👍", "score": 4}'), CURRENT_TIMESTAMP()),
('user003', parse_json('{"name": "Charlie", "city": "Beijing", "comment": "Fast delivery, beautiful packaging🎉", "score": 5}'), CURRENT_TIMESTAMP()),
('user004', parse_json('{"name": "David", "city": "Shenzhen", "comment": "Powerful features, worth recommending💯", "score": 5}'), CURRENT_TIMESTAMP());

-- Query data containing Chinese and emoji
SELECT 
    json_extract_string(data, "$.name") as user_name,
    json_extract_string(data, "$.city") as city,
    json_extract_string(data, "$.comment") as feedback,
    json_extract_int(data, "$.score") as score
FROM user_feedback_full 
WHERE json_extract_string(data, "$.city") = 'Beijing'
  AND json_extract_string(data, "$.comment") LIKE '%😊%';

-- Group statistics by Chinese field
SELECT 
    json_extract_string(data, "$.city") as city,
    COUNT(*) as user_count,
    AVG(json_extract_int(data, "$.score")) as avg_score
FROM user_feedback_full
GROUP BY json_extract_string(data, "$.city")
ORDER BY user_count DESC;

-- Emoji usage analysis for high-score users
SELECT 
    json_extract_string(data, "$.name") as user_name,
    json_extract_string(data, "$.comment") as comment,
    json_extract_int(data, "$.score") as score,
    CASE 
        WHEN json_extract_string(data, "$.comment") LIKE '%😊%' THEN 'happy'
        WHEN json_extract_string(data, "$.comment") LIKE '%👍%' THEN 'thumbs_up'
        WHEN json_extract_string(data, "$.comment") LIKE '%🎉%' THEN 'celebration'
        WHEN json_extract_string(data, "$.comment") LIKE '%💯%' THEN 'perfect'
        ELSE 'no_emoji'
    END as emoji_sentiment
FROM user_feedback_full
WHERE json_extract_int(data, "$.score") >= 4
ORDER BY json_extract_int(data, "$.score") DESC;
```

### 5.2 Best Practice Recommendations

#### 5.2.1 Field Naming Conventions

**Recommended: Use English field names**

```sql
-- Create best practice demo table
CREATE TABLE IF NOT EXISTS best_practice_demo (
    id STRING,
    data JSON
);

-- Recommended field naming approach
INSERT INTO best_practice_demo VALUES
('demo001', parse_json('{"user_name": "Alice", "user_city": "Beijing", "user_comment": "Product is great😊", "rating_score": 5}'));

-- Query demonstration
SELECT 
    json_extract_string(data, "$.user_name") as name,
    json_extract_string(data, "$.user_city") as city,
    json_extract_string(data, "$.user_comment") as comment,
    json_extract_int(data, "$.rating_score") as score
FROM best_practice_demo;
```

**Use with Caution: Chinese field names**

```sql
-- Create Chinese field name demo table (not recommended)
CREATE TABLE IF NOT EXISTS chinese_field_demo (
    id STRING,
    data JSON
);

-- Chinese field name example (functional but not recommended)
INSERT INTO chinese_field_demo VALUES
('demo001', parse_json('{"user_name_cn": "Alice", "user_city_cn": "Beijing", "user_review_cn": "Product is great😊"}'));

-- Query Chinese field names (syntactically correct but not recommended)
SELECT 
    json_extract_string(data, "$.user_name_cn") as name,
    json_extract_string(data, "$.user_city_cn") as city,
    json_extract_string(data, "$.user_review_cn") as comment
FROM chinese_field_demo;
```

#### 5.2.2 Special Character Handling

**Safe Content Formats**:

```sql
-- Create special character handling demo table
CREATE TABLE IF NOT EXISTS special_char_demo (
    id STRING,
    data JSON
);

-- Insert data containing various special characters
INSERT INTO special_char_demo VALUES
('char001', parse_json('{"message": "Normal text content and emoji😊", "symbols": "!@#$%^&*()_+-=[]{}|;:,.<>?/", "punctuation": "Punctuation marks: ，。；：""''（）【】、？！"}'));

-- Query special character data
SELECT 
    json_extract_string(data, "$.message") as message,
    json_extract_string(data, "$.symbols") as symbols,
    json_extract_string(data, "$.punctuation") as punctuation
FROM special_char_demo;
```

### 5.3 Troubleshooting Guide

If you encounter Chinese or emoji display issues:

1. **Check field naming**: Prefer English field names
2. **Verify JSON format**: Ensure the JSON format is correct with no syntax errors
3. **Use standard functions**: Consistently use json_extract_* functions
4. **Avoid complex escaping**: Minimize the use of complex escape characters in JSON strings
5. **Encoding settings**: Ensure client and database character encoding settings are correct

```sql
-- Troubleshooting demo query
CREATE TABLE IF NOT EXISTS troubleshoot_demo (
    id STRING,
    data JSON
);

-- Correct data insertion method
INSERT INTO troubleshoot_demo VALUES
('test001', parse_json('{"name": "Test User", "message": "This is a test message🔧"}'));

-- Verify that data is correctly stored and queried
SELECT 
    id,
    json_extract_string(data, "$.name") as name,
    json_extract_string(data, "$.message") as message,
    LENGTH(json_extract_string(data, "$.name")) as name_length,
    LENGTH(json_extract_string(data, "$.message")) as message_length
FROM troubleshoot_demo;
```

***

## Chapter 6: Technical Limitations and Best Practices

### 6.1 JSON Type Limitation Summary (Verified and Revised)

Core limitations discovered based on comprehensive verification:

#### 6.1.1 Confirmed Supported Features

**Supported JSON Functions**:

* `parse_json()` - JSON string parsing
* `json_extract_string()` - Extract string values
* `json_extract_int()` - Extract integer values
* `json_extract_double()` - Extract floating-point values
* `json_extract()` - General extraction function

**Supported Syntax**:

* `CREATE TABLE IF NOT EXISTS`
* Complete DDL operations (CREATE/ALTER/DROP)
* Array access syntax `[0]`, `[1]`
* Nested object access `$.path.to.field`
* Full support for Chinese and emoji content

#### 6.1.2 Confirmed Unsupported Features

**Unsupported JSON Functions**:

```sql
-- The following function has been verified as unsupported:
-- json_set() - JSON field update (important limitation)
```

**Unsupported Operations**:

```sql
-- Create limitation demo table
CREATE TABLE IF NOT EXISTS limitation_demo (
    id INT,
    json_data JSON
);

-- Insert test data
INSERT INTO limitation_demo VALUES
(1, parse_json('{"name": "Alice", "score": 85}')),
(2, parse_json('{"name": "Bob", "score": 92}')),
(3, parse_json('{"name": "Charlie", "score": 78}'));

-- The following operations are not supported and will cause errors:
-- JSON type does not support direct comparison
-- SELECT * FROM limitation_demo WHERE json_data = parse_json('{}');

-- JSON type does not support direct ordering
-- SELECT * FROM limitation_demo ORDER BY json_data;

-- JSON type does not support direct GROUP BY
-- SELECT json_data, COUNT(*) FROM limitation_demo GROUP BY json_data;
```

#### 6.1.3 Solutions

```sql
-- Use json_extract functions for comparison
SELECT * FROM limitation_demo 
WHERE json_extract_string(json_data, "$.name") = 'Alice';

-- Extract fields then sort
SELECT 
    id,
    json_extract_string(json_data, "$.name") as name,
    json_extract_int(json_data, "$.score") as score
FROM limitation_demo 
ORDER BY json_extract_int(json_data, "$.score") DESC;

-- Extract fields then group
SELECT 
    CASE 
        WHEN json_extract_int(json_data, "$.score") >= 90 THEN 'excellent'
        WHEN json_extract_int(json_data, "$.score") >= 80 THEN 'good'
        ELSE 'average'
    END as grade,
    COUNT(*) as count
FROM limitation_demo 
GROUP BY CASE 
    WHEN json_extract_int(json_data, "$.score") >= 90 THEN 'excellent'
    WHEN json_extract_int(json_data, "$.score") >= 80 THEN 'good'
    ELSE 'average'
END;
```

### 6.2 Alternative Strategies for JSON Data Updates

#### 6.2.1 Update Strategy Design Principles

1. **Read-Heavy, Write-Light Principle**: JSON is primarily used for read-intensive scenarios
2. **Hybrid Storage Strategy**: Separate frequently updated fields
3. **Application-Layer Processing**: Complex updates are completed at the application layer
4. **Versioned Management**: Important data supports historical versions

#### 6.2.2 Specific Implementation Plans

**Approach 1: Complete JSON Reconstruction**

```sql
-- Suitable for: simple JSON updates, low update frequency scenarios
UPDATE table_name 
SET json_column = parse_json(CONCAT(
    '{"field1": "', json_extract_string(json_column, "$.field1"), '", ',
    '"field2": "new_value", ',
    '"field3": ', json_extract_int(json_column, "$.field3"), '}'
))
WHERE conditions;
```

**Approach 2: Hybrid Storage Strategy**

```sql
-- Recommended for: business scenarios with frequent update requirements
CREATE TABLE IF NOT EXISTS hybrid_table (
    id INT,
    frequently_updated_field STRING,  -- Relational field
    status_field INT,                 -- Relational field
    stable_json_data JSON,           -- JSON field for stable data
    last_updated TIMESTAMP
);
```

**Approach 3: Versioned Storage**

```sql
-- Suitable for: important data requiring historical version retention
CREATE TABLE IF NOT EXISTS versioned_json_data (
    record_id STRING,
    version_number INT,
    json_data JSON,
    created_time TIMESTAMP,
    is_current BOOLEAN DEFAULT TRUE
);
```

### 6.3 Unified Syntax Recommendations

To avoid issues caused by mixing different approaches, it is recommended to consistently use json_extract functions:

```sql
-- Create unified syntax demo table
CREATE TABLE IF NOT EXISTS syntax_demo (
    order_id STRING,
    data JSON
);

-- Insert test data
INSERT INTO syntax_demo VALUES
('ORD001', parse_json('{"customer": {"id": "C001", "name": "Alice", "level": "VIP"}, "payment": {"amount": 1500.00}, "items": [{"qty": 2}]}')),
('ORD002', parse_json('{"customer": {"id": "C002", "name": "Bob", "level": "regular"}, "payment": {"amount": 800.00}, "items": [{"qty": 1}]}')),
('ORD003', parse_json('{"customer": {"id": "C003", "name": "Charlie", "level": "VIP"}, "payment": {"amount": 2200.00}, "items": [{"qty": 3}]}'));

-- Recommended unified syntax pattern
SELECT 
    order_id,
    json_extract_string(data, "$.customer.id") as customer_id,
    json_extract_string(data, "$.customer.name") as customer_name,
    json_extract_string(data, "$.customer.level") as customer_level,
    json_extract_double(data, "$.payment.amount") as amount,
    json_extract_int(data, "$.items[0].qty") as quantity
FROM syntax_demo 
WHERE json_extract_string(data, "$.customer.level") = 'VIP'
ORDER BY json_extract_double(data, "$.payment.amount") DESC;
```

### 6.4 Type-Safe Handling

#### 6.4.1 Safe Default Value Handling

```sql
-- Create type-safety demo table
CREATE TABLE IF NOT EXISTS type_safety_demo (
    order_id STRING,
    order_data JSON
);

-- Insert data containing missing fields
INSERT INTO type_safety_demo VALUES
('ORD001', parse_json('{"customer": {"name": "Alice", "vip_level": "gold"}, "payment": {"discount": 100}}')),
('ORD002', parse_json('{"customer": {"name": "Bob"}, "payment": {}}')),  -- Missing vip_level and discount
('ORD003', parse_json('{"customer": {"name": "Charlie", "vip_level": "silver"}, "payment": {"discount": 50}}'));

-- Safe default value handling
SELECT 
    order_id,
    json_extract_string(order_data, "$.customer.name") as customer_name,
    -- Ensure type-consistent default value handling
    CASE WHEN json_extract_string(order_data, "$.customer.vip_level") IS NOT NULL 
         THEN json_extract_string(order_data, "$.customer.vip_level") 
         ELSE 'regular' 
    END as safe_vip_level,
    -- Safe handling of numeric types
    CASE WHEN json_extract_double(order_data, "$.payment.discount") IS NOT NULL 
         THEN json_extract_double(order_data, "$.payment.discount") 
         ELSE 0.0 
    END as safe_discount,
    -- Use COALESCE to simplify default value handling
    COALESCE(json_extract_string(order_data, "$.customer.vip_level"), 'regular') as vip_level_coalesce,
    COALESCE(json_extract_double(order_data, "$.payment.discount"), 0.0) as discount_coalesce
FROM type_safety_demo;
```

### 6.5 Performance Optimization Strategies

#### 6.5.1 High-Frequency Field Optimization

```sql
-- Create performance optimization demo table
CREATE TABLE IF NOT EXISTS perf_orders (
    id INT,
    order_data JSON,
    created_date DATE DEFAULT CURRENT_DATE()
);

-- Insert test data
INSERT INTO perf_orders VALUES
(1, parse_json('{"customer_id": "C001", "payment_amount": 1500.00, "items": [{"detail": {"description": "Premium Electronics"}}]}'), CURRENT_DATE()),
(2, parse_json('{"customer_id": "C002", "payment_amount": 2300.00, "items": [{"detail": {"description": "Home Goods"}}]}'), CURRENT_DATE()),
(3, parse_json('{"customer_id": "C003", "payment_amount": 800.00, "items": [{"detail": {"description": "Daily Necessities"}}]}'), CURRENT_DATE()),
(4, parse_json('{"customer_id": "C004", "payment_amount": 3200.00, "items": [{"detail": {"description": "Luxury Goods"}}]}'), CURRENT_DATE());

-- Place frequently used fields at the JSON top level to leverage automatic columnar storage optimization
SELECT 
    json_extract_string(order_data, "$.customer_id") as customer_id,          -- High-frequency field
    json_extract_double(order_data, "$.payment_amount") as amount,            -- High-frequency field
    json_extract_string(order_data, "$.items[0].detail.description") as desc  -- Deep-level field
FROM perf_orders 
WHERE json_extract_string(order_data, "$.customer_id") IS NOT NULL          -- Efficient filtering
  AND json_extract_double(order_data, "$.payment_amount") > 1000;           -- Numeric filtering
```

#### 6.5.2 Batch Extraction Optimization

```sql
-- Create batch optimization demo table
CREATE TABLE IF NOT EXISTS batch_orders (
    id INT,
    order_data JSON
);

-- Insert more test data
INSERT INTO batch_orders VALUES
(1, parse_json('{"customer": {"id": "C001", "level": "VIP"}, "payment": {"amount": 3500.00}}')),
(2, parse_json('{"customer": {"id": "C002", "level": "regular"}, "payment": {"amount": 1200.00}}')),
(3, parse_json('{"customer": {"id": "C003", "level": "VIP"}, "payment": {"amount": 4200.00}}')),
(4, parse_json('{"customer": {"id": "C004", "level": "diamond"}, "payment": {"amount": 5800.00}}')),
(5, parse_json('{"customer": {"id": "C005", "level": "regular"}, "payment": {"amount": 900.00}}'));

-- Use CTE to reduce repeated parsing
WITH extracted_data AS (
    SELECT 
        id as order_id,
        json_extract_string(order_data, "$.customer.id") as customer_id,
        json_extract_string(order_data, "$.customer.level") as customer_level,
        json_extract_double(order_data, "$.payment.amount") as payment_amount
    FROM batch_orders
    WHERE json_extract_string(order_data, "$.customer.id") IS NOT NULL
)
SELECT 
    customer_level,
    COUNT(*) as order_count,
    AVG(payment_amount) as avg_amount,
    MAX(payment_amount) as max_amount,
    MIN(payment_amount) as min_amount
FROM extracted_data
GROUP BY customer_level
ORDER BY avg_amount DESC;
```

***

## Chapter 7: Environment Management and Implementation Recommendations

### 7.1 Pre-Implementation Checklist

#### 7.1.1 Technical Preparation

* [ ] Verify character encoding settings (UTF-8)
* [ ] Test Chinese and emoji data processing
* [ ] Prepare data migration plan
* [ ] **New: Develop a JSON data update strategy**

#### 7.1.2 Syntax Specification Check

* [ ] Confirm all CREATE statements include IF NOT EXISTS
* [ ] Verify that json_set/json_insert/json_remove functions are not used
* [ ] Consistently use json_extract functions instead of direct JSON operations
* [ ] Verify that JSON type is not used for direct comparison, sorting, or grouping
* [ ] **New: Design a hybrid storage architecture**

#### 7.1.3 Development Standards

* [ ] Establish JSON field naming conventions (recommend English field names)
* [ ] Consistently use json_extract functions
* [ ] Establish error handling and default value handling standards
* [ ] Design performance monitoring metrics
* [ ] **New: Establish alternative solution standards for JSON data updates**

#### 7.1.4 Verification Testing

```sql
-- Create system verification table
CREATE TABLE IF NOT EXISTS system_verification (
    test_id STRING,
    test_data JSON,
    test_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Basic functionality verification
INSERT INTO system_verification VALUES
('test_001', parse_json('{"basic_test": "Basic functionality test", "emoji_test": "😊👍", "number_test": 123.45}'), CURRENT_TIMESTAMP()),
('test_002', parse_json('{"nested_test": {"level1": {"level2": "Deep nesting test"}}, "array_test": ["Array", "Test", "Items"]}'), CURRENT_TIMESTAMP());

-- Verification query
SELECT 
    test_id,
    json_extract_string(test_data, "$.basic_test") as basic_result,
    json_extract_string(test_data, "$.emoji_test") as emoji_result,
    json_extract_double(test_data, "$.number_test") as number_result,
    json_extract_string(test_data, "$.nested_test.level1.level2") as nested_result,
    json_extract_string(test_data, "$.array_test[0]") as array_result
FROM system_verification
ORDER BY test_time DESC;
```

### 7.2 Phased Implementation Strategy

1. **Proof of Concept Phase**: Select 1-2 key business scenarios for pilot testing
2. **Small-Scale Deployment**: Verify performance and stability in non-core business systems
3. **Architecture Optimization Phase**: Implement hybrid storage strategy and JSON update alternatives
4. **Full Rollout**: Develop a complete migration plan based on pilot experience

```sql
-- Implementation phase tracking table
CREATE TABLE IF NOT EXISTS implementation_tracking (
    phase STRING,
    milestone STRING,
    status STRING,
    completion_date DATE,
    notes JSON
);

-- Record implementation progress
INSERT INTO implementation_tracking VALUES
('Phase1', 'Proof of Concept', 'completed', CURRENT_DATE(), parse_json('{"scenarios": ["E-commerce order analysis", "User behavior tracking"], "success_rate": 0.95}')),
('Phase2', 'Small-scale deployment', 'in_progress', NULL, parse_json('{"target_systems": ["Test environment", "Development environment"], "expected_completion": "2024-12-15"}')),
('Phase3', 'Architecture optimization', 'planned', NULL, parse_json('{"focus": ["Hybrid storage design", "JSON update alternatives"], "expected_start": "2024-12-20"}'));
```

### 7.3 Monitoring and Operations

```sql
-- Create operational monitoring table
CREATE TABLE IF NOT EXISTS operational_monitoring (
    metric_name STRING,
    metric_value DOUBLE,
    metric_metadata JSON,
    measurement_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Insert monitoring data example
INSERT INTO operational_monitoring VALUES
('json_query_performance', 0.95, parse_json('{"avg_response_time_ms": 145, "query_count": 1000, "success_rate": 0.99}'), CURRENT_TIMESTAMP()),
('storage_efficiency', 0.87, parse_json('{"compression_ratio": 0.72, "storage_saved_gb": 250, "cost_reduction": 0.35}'), CURRENT_TIMESTAMP()),
('json_update_performance', 0.78, parse_json('{"avg_update_time_ms": 280, "update_success_rate": 0.95, "method": "json_reconstruction"}'), CURRENT_TIMESTAMP());

-- Performance monitoring query template
SELECT 
    metric_name,
    metric_value,
    json_extract_double(metric_metadata, "$.avg_response_time_ms") as avg_response_time,
    json_extract_int(metric_metadata, "$.query_count") as query_count,
    json_extract_double(metric_metadata, "$.success_rate") as success_rate,
    measurement_time
FROM operational_monitoring 
WHERE metric_name = 'json_query_performance'
ORDER BY measurement_time DESC;
```

### 7.4 Performance Monitoring and Tuning

#### 7.4.1 JSON Query Performance Monitoring

```sql
-- Create performance monitoring demo table
CREATE TABLE IF NOT EXISTS performance_monitor (
    id INT,
    json_column JSON,
    created_date DATE DEFAULT CURRENT_DATE()
);

-- Insert test data
INSERT INTO performance_monitor VALUES
(1, parse_json('{"frequently_accessed_field": "value1", "other_data": "test", "nested": {"deep": {"field": "deep_value1"}}}'), CURRENT_DATE()),
(2, parse_json('{"frequently_accessed_field": "value2", "other_data": "test", "nested": {"deep": {"field": "deep_value2"}}}'), CURRENT_DATE() - INTERVAL 10 DAYS),
(3, parse_json('{"frequently_accessed_field": "value1", "other_data": "test", "nested": {"deep": {"field": "deep_value3"}}}'), CURRENT_DATE() - INTERVAL 2 DAYS),
(4, parse_json('{"frequently_accessed_field": "value3", "other_data": "test", "nested": {"deep": {"field": "deep_value4"}}}'), CURRENT_DATE()),
(5, parse_json('{"frequently_accessed_field": "value2", "other_data": "test", "nested": {"deep": {"field": "deep_value5"}}}'), CURRENT_DATE() - INTERVAL 5 DAYS);

-- Query performance analysis template
SELECT 
    'performance_monitor' as table_name,
    COUNT(*) as total_records,
    AVG(LENGTH(CAST(json_column AS STRING))) as avg_json_size,
    -- High-frequency field distribution analysis
    COUNT(DISTINCT json_extract_string(json_column, "$.frequently_accessed_field")) as unique_values,
    -- Data recency analysis
    COUNT(CASE WHEN created_date >= CURRENT_DATE() - INTERVAL 7 DAYS THEN 1 END) as recent_records,
    -- Field access complexity analysis
    COUNT(CASE WHEN json_extract_string(json_column, "$.nested.deep.field") IS NOT NULL THEN 1 END) as deep_nested_fields
FROM performance_monitor 
WHERE json_column IS NOT NULL;
```

#### 7.4.2 Automatic Optimization Recommendation Generation

```sql
-- Create optimization analysis demo table
CREATE TABLE IF NOT EXISTS optimization_analysis (
    id INT,
    order_data JSON,
    created_date DATE DEFAULT CURRENT_DATE()
);

-- Insert test data
INSERT INTO optimization_analysis VALUES
(1, parse_json('{"customer": {"level": "VIP"}, "payment": {"amount": 1500.00}}'), CURRENT_DATE()),
(2, parse_json('{"customer": {"level": "regular"}, "payment": {"amount": 800.00}}'), CURRENT_DATE()),
(3, parse_json('{"customer": {"level": "VIP"}, "payment": {"amount": 2200.00}}'), CURRENT_DATE()),
(4, parse_json('{"customer": {"level": "diamond"}, "payment": {"amount": 5000.00}}'), CURRENT_DATE()),
(5, parse_json('{"customer": {"level": "VIP"}, "payment": {"amount": 3200.00}}'), CURRENT_DATE()),
(6, parse_json('{"customer": {"level": "regular"}, "payment": {"amount": 600.00}}'), CURRENT_DATE());

-- Automatic optimization recommendations based on usage patterns
WITH query_pattern_analysis AS (
    SELECT 
        json_extract_string(order_data, "$.customer.level") as access_pattern,
        COUNT(*) as usage_frequency,
        AVG(json_extract_double(order_data, "$.payment.amount")) as avg_amount
    FROM optimization_analysis 
    GROUP BY json_extract_string(order_data, "$.customer.level")
)
SELECT 
    access_pattern,
    usage_frequency,
    ROUND(avg_amount, 2) as avg_amount,
    CASE 
        WHEN usage_frequency > 1000 THEN 'recommend_column_optimization'
        WHEN usage_frequency > 100 THEN 'consider_indexing'
        ELSE 'current_performance_sufficient'
    END as optimization_recommendation,
    CASE 
        WHEN avg_amount > 3000 THEN 'high_value_customer_segment'
        WHEN avg_amount > 1500 THEN 'medium_value_customer_segment'
        ELSE 'low_value_customer_segment'
    END as business_insight
FROM query_pattern_analysis
ORDER BY usage_frequency DESC;
```

### 7.5 Environment Cleanup

```sql
-- View all created tables
SHOW TABLES LIKE '%json%';

-- Clean up test tables (optional)
/*
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS ecommerce_orders_json;
DROP TABLE IF EXISTS promotion_orders_json;
DROP TABLE IF EXISTS inventory_orders_json;
DROP TABLE IF EXISTS iot_devices_unified;
DROP TABLE IF EXISTS financial_risk_analysis;
DROP TABLE IF EXISTS customer_behavior_analysis;
DROP TABLE IF EXISTS device_maintenance_analysis;
DROP TABLE IF EXISTS user_data_chinese;
DROP TABLE IF EXISTS social_data_emoji;
DROP TABLE IF EXISTS feedback_data_complex;
DROP TABLE IF EXISTS user_feedback_full;
DROP TABLE IF EXISTS best_practice_demo;
DROP TABLE IF EXISTS chinese_field_demo;
DROP TABLE IF EXISTS special_char_demo;
DROP TABLE IF EXISTS troubleshoot_demo;
DROP TABLE IF EXISTS limitation_demo;
DROP TABLE IF EXISTS syntax_demo;
DROP TABLE IF EXISTS type_safety_demo;
DROP TABLE IF EXISTS perf_orders;
DROP TABLE IF EXISTS batch_orders;
DROP TABLE IF EXISTS performance_monitor;
DROP TABLE IF EXISTS optimization_analysis;
DROP TABLE IF EXISTS system_verification;
DROP TABLE IF EXISTS implementation_tracking;
DROP TABLE IF EXISTS operational_monitoring;
DROP TABLE IF EXISTS transaction_demo;
DROP TABLE IF EXISTS hybrid_storage_demo;
*/

-- Verify cleanup results
SELECT COUNT(*) as remaining_json_tables 
FROM information_schema.tables 
WHERE table_name LIKE '%json%';
```

***

## Summary

### Core Value Summary

Singdata Lakehouse JSON data processing capabilities demonstrate the following core values:

#### Technical Advantages

* **Native JSON Support**: Full compatibility with standard JSON syntax; json_extract function queries are highly efficient
* **Intelligent Storage Optimization**: High-frequency fields are stored in columnar format based on JSON Schema
* **Real-time Processing Capability**: Dynamic tables enable real-time responsiveness
* **Multilingual Support**: Complete support for Chinese, emoji, and other special characters
* **Enterprise-Grade Features**: Complete elastic computing, multi-layer caching, and cluster isolation

#### Business Value

* **E-Commerce**: Implement personalized recommendation systems, improving conversion effectiveness and user experience
* **IoT**: Establish predictive maintenance systems, reducing equipment failures and maintenance costs
* **Financial**: Build real-time risk control engines, enhancing risk management and compliance capabilities

#### Implementation Advantages

* **Quick Start**: Based on standard SQL, significantly improving development efficiency
* **Smooth Migration**: No need to restructure existing JSON data; import and use directly
* **Strong Scalability**: Seamless scaling from GB to PB-level data, supporting long-term enterprise development

### Key Technical Points

#### Syntax Specifications

* **Consistently use json_extract functions**: Avoid mixing different access methods
* **Type Safety**: JSON type does not support direct comparison, sorting, or grouping operations
* **Chinese Support**: Full support for Chinese and emoji; recommend using English field names
* **CREATE Statement Standard**: Consistently use IF NOT EXISTS to avoid duplicate creation errors
* **Important Limitation**: json_set function is not supported

#### JSON Update Strategies

* **Hybrid Storage Design**: Use relational storage for frequently updated fields, JSON for stable data
* **Application-Layer Processing**: Complete complex JSON updates at the application layer before full replacement
* **Version Control**: Retain historical versions for important JSON data changes
* **Batch Updates**: Avoid row-by-row JSON reconstruction; prioritize batch processing

#### Performance Optimization

* **Columnar Design for High-Frequency Fields**: Can significantly improve query efficiency
* **Multi-Layer Cache Utilization**: Query result cache, metadata cache, and compute cluster local cache work together
* **Real-time Stream Processing**: Dynamic tables enable efficient data aggregation

### Action Recommendations

1. **Start Immediately**: Select a key business scenario and launch a proof of concept for JSON data processing
2. **Architecture Design**: Develop a hybrid storage strategy and clearly define JSON usage boundaries
3. **Team Training**: Organize technical team learning of this guide's best practices and syntax specifications
4. **Gradual Expansion**: Based on successful pilot experience, develop a comprehensive JSON data strategy
5. **Continuous Optimization**: Establish performance monitoring and optimization mechanisms to ensure long-term value realization

***

**Singdata Lakehouse JSON Data Processing - Making complex JSON data processing simple and efficient within clearly defined technical boundaries**

*This guide provides a complete solution for enterprise JSON data processing. All SQL statements have been verified in Singdata Lakehouse. Each example includes complete table creation and data preparation statements, using IF NOT EXISTS to ensure repeatable execution. By following the best practices in this revised edition, enterprises can fully leverage the business value of JSON data and accelerate their digital transformation journey within clearly defined technical boundaries*.

## References

[JSON Data Type](JSON.md)

[JSON Functions](json_function.md)

*Note: This guide is based on test results from the Singdata Lakehouse version as of May 2025. Subsequent versions may introduce changes. Please regularly check the official documentation for the latest information*.
