# Singdata Lakehouse MCP Server Use Case: Cost Anomaly Analysis and Troubleshooting

## Core Q&A Process Demo

### User Question Sequence

```
👤 User: "Analyze the data in sys.information_schema.instance_usage table, check the costs for September 4th and September 5th"

🤖 MCP Server: [Auto analyze table structure] → [Generate intelligent query] → [Output cost report]
   Found: September 4 cost ¥85.77, September 5 cost ¥66.65, mainly from GP compute cluster

👤 User: "Why are the costs so high on these two days?"

🤖 MCP Server: [Historical data comparison] → [Anomaly pattern recognition] → [Trend analysis]
   Found: Normal daily cost ¥1-6, surged 15x during the anomaly period, GP cluster usage duration abnormal

👤 User: "Check which instance and which workspace's cluster"

🤖 MCP Server: [Multi-dimensional analysis] → [Responsible party identification] → [Job history tracking]
   Found: Instance 270397's quick_start workspace, caused by frequent refresh of the mcp_test_daily_summary dynamic table
```

### Key Insights

* **Issue location time**: <= '2025-09-08'
   GROUP BY date(measurement_start)
   ORDER BY usage_date
   ```

2. **Anomaly Pattern Recognition**

**Historical Cost Trend Analysis**:

| Time Period     | Average Daily Cost | Cost Range           | Status                    |
| --------------- | ------------------ | -------------------- | ------------------------- |
| Aug 25-Sep 2    | ¥1.8               | ¥0.99-¥6.06          | ✅ Normal baseline        |
| Sep 3           | ¥25.13             | -                    | ⚠️ First anomaly         |
| **Sep 4-5**     | **¥76.21**         | **¥66.65-¥85.77**    | 🚨 **Severe anomaly**     |
| After Sep 6     | ¥0.73              | ¥0.53-¥1.05          | ✅ Returned to normal     |

3. **Usage Pattern Change Analysis**

   ```sql
   SELECT 
       date(measurement_start) as usage_date,
       sku_name,
       count(*) as record_count,
       sum(measurements_consumption) as total_consumption_hours,
       avg(measurements_consumption) as avg_consumption_per_record,
       sum(total_after_discount) as total_cost
   FROM sys.information_schema.instance_usage 
   WHERE sku_category = 'compute'
   GROUP BY date(measurement_start), sku_name
   ```

**GP Cluster Usage Pattern Comparison**:

| Date         | Average Hourly Consumption | Record Count     | Total Consumption Duration | Per-Instance Cost |
| ------------ | -------------------------- | ---------------- | -------------------------- | ----------------- |
| Sep 1-2      | 0.03-0.04 hours            | 14-20 records    | 0.37-0.76 hours            | ¥1-3              |
| **Sep 4**    | **0.57 hours**             | **42 records**   | **24.05 hours**            | **¥3.5**          |
| **Sep 5**    | **0.58 hours**             | **32 records**   | **18.71 hours**            | **¥3.5**          |
| After Sep 6  | 0.02 hours                 | 12 records       | 0.20 hours                 | ¥0.7              |

**Key Findings**:

* GP cluster changed from short query mode to long-running mode
* Hourly consumption duration increased **15x** (0.04 → 0.57 hours)
* Nearly full 1-hour billing, indicating the cluster was running continuously

### Step 3: Precise Responsible Party Identification

**User continues to ask**:

```
Check which instance and which workspace's cluster
```

**MCP Server Multi-Dimensional Analysis**:

1. **Instance and Workspace Cost Distribution**

   ```sql
   SELECT 
       instance_id,
       workspace_name,
       sku_name,
       sum(total_after_discount) as total_cost
   FROM sys.information_schema.instance_usage 
   WHERE date(measurement_start) IN ('2025-09-04', '2025-09-05')
     AND sku_category = 'compute'
   GROUP BY instance_id, workspace_name, sku_name
   ORDER BY total_cost DESC
   ```

**Responsible Party Analysis Results**:

| Instance ID   | Workspace                       | Sep 4 Cost     | Sep 5 Cost     | Anomaly Severity               |
| ------------- | ------------------------------- | -------------- | -------------- | ------------------------------ |
| **270397**    | **quick\_start**                | **¥83.48**     | **¥64.77**     | 🚨 **Primary responsible party** |
| 270397        | lakehouse\_quick\_experience    | ¥0.71          | ¥0.71          | ✅ Normal                      |
| 270397        | ns227206                        | ¥0.17          | ¥0.17          | ✅ Normal                      |

2. **Specific Cluster Usage Details**

   ```sql
   SELECT 
       date(measurement_start) as usage_date,
       hour(measurement_start) as usage_hour,
       measurements_consumption,
       amount
   FROM sys.information_schema.instance_usage 
   WHERE workspace_name = 'quick_start' 
     AND sku_name = 'GP Compute Cluster'
     AND amount >

**GP Cluster Runtime Analysis**:

**Sep 4 Anomaly Pattern**:

* **00:00-23:59**: 24 hours continuous runtime
* **Hourly consumption**: ~1.00 hours (nearly full hourly billing)
* **Per-hour cost**: Around ¥3.5

**Sep 5 Anomaly Pattern**:

* **00:00-18:59**: 19 hours continuous runtime
* **Cost pattern**: Similarly close to full hourly billing

**Key Findings**:

* Issue identified in the GP cluster of `quick_start` workspace
* Cluster shows nearly 24-hour continuous runtime
* **Not** a normal short query pattern

### Step 4: Root Cause Tracking

**MCP Server Auto Deep Investigation**:

1. **Job History Analysis**

   <= '2025-09-06 23:59:59'
   ```

**Normal Period Job Characteristics**:

* Query execution time: seconds to minutes
* Cluster auto-suspend: quick release after query completion
* Cost pattern: billed by actual usage time

## Root Cause Deep Analysis

### Technical Analysis

**1. Dynamic Table Configuration Error**

```sql
-- Problematic configuration (speculated)
CREATE DYNAMIC TABLE mcp_test_daily_summary
REFRESH_INTERVAL = '5 MINUTES'  -- ❌ Too frequent
AS SELECT ...
```

**2. Cluster Resource Management Failure**

* **Normal mode**: Query completes → Cluster idle → Auto-suspend (within minutes)
* **Anomaly mode**: Query completes → New query after 5 minutes → Cluster stays active → Cannot suspend

**3. Billing Calculation Logic**

* **Hourly billing**: GP cluster billed by usage duration, ¥3.5/hour
* **Minimum billing unit**: Even if used for minutes, the active state accumulates billing time
* **Cumulative effect**: 5-minute refresh interval → Nearly full 24-hour billing

### Business Impact Assessment

**1. Direct Cost Loss**

* **Anomaly period**: 2-day total cost ¥152.42
* **Normal period**: 2-day expected cost ¥2-12
* **Direct loss**: ¥140-150

**2. Potential Risks**

* **If not discovered in time**: Daily additional cost ¥80+
* **Monthly impact**: Could generate ¥2400+ additional costs
* **Resource waste**: Cluster resources not effectively utilized

**3. Systemic Issues**

* **Configuration management**: Dynamic table refresh policy lacks reasonableness checks
* **Monitoring alerts**: Cost anomalies not discovered in time
* **Resource optimization**: Cluster auto-management policy needs optimization

## Solutions and Best Practices

### Immediate Remediation Measures

**1. Dynamic Table Configuration Correction**

```sql
-- Check current configuration
DESC DYNAMIC TABLE mcp_test_daily_summary;

-- Option 1: Adjust refresh interval (recommended)
ALTER DYNAMIC TABLE mcp_test_daily_summary 
SET REFRESH_INTERVAL = '1 HOUR';

-- Option 2: Adjust based on business requirements
ALTER DYNAMIC TABLE mcp_test_daily_summary 
SET REFRESH_INTERVAL = '4 HOURS';  -- or other reasonable intervals

-- Option 3: Suspend dynamic table (emergency)
ALTER DYNAMIC TABLE mcp_test_daily_summary SUSPEND;
```

**2. Cluster Configuration Optimization**

```sql
-- Check cluster auto-suspend settings
SHOW VIRTUAL_CLUSTERS;

-- Ensure reasonable auto-suspend time
ALTER VIRTUAL_CLUSTER your_gp_cluster 
SET AUTO_SUSPEND_IN_SECOND = 300;  -- 5-minute auto-suspend
```

### Preventive Measures

**1. Monitoring and Alerting**

```sql
-- Create cost monitoring view
CREATE VIEW daily_cost_monitor AS
SELECT 
    date(measurement_start) as cost_date,
    sum(total_after_discount) as daily_cost,
    CASE 
        WHEN sum(total_after_discount) >

**2. Dynamic Table Best Practices**

* **Refresh interval recommendation**: Set based on data update frequency, minimum no less than 30 minutes
* **Resource consideration**: Evaluate refresh impact on compute resources
* **Business alignment**: Refresh frequency should match actual business requirements

**3. Resource Management Strategy**

* **Cluster separation**: Separate scheduled tasks and interactive queries into different clusters
* **Time window**: Execute resource-intensive tasks during off-peak hours
* **Cost budget**: Set workspace-level cost budget and alerts

## Case Value and Technical Highlights

### 1. MCP Server Intelligent Analysis Capability

**Natural Language Understanding**

* No need for users to master complex SQL syntax
* Intelligently understand analysis intent and convert to precise queries
* Support multi-turn conversations, progressively dig deeper into issues

**Automated Data Analysis**

```
User intent: "Analyze costs" → Auto table structure identification → Intelligent query generation → Multi-dimensional data correlation → Anomaly pattern recognition → Visualized result presentation
```

**Context Memory Capability**

* Remember previous analysis results
* Conduct deeper investigation based on existing findings
* Maintain analytical logic continuity

### 2. Systematic Approach to Troubleshooting

**Hierarchical Analysis Framework**

1. **Overview layer**: Overall cost trend identification
2. **Decomposition layer**: Break down cost composition by dimensions
3. **Localization layer**: Precisely identify responsible parties
4. **Root cause layer**: Trace to specific technical causes

**Multi-Dimensional Correlation Analysis**

* Time dimension: Historical comparison, trend analysis
* Spatial dimension: Instance, workspace, cluster
* Business dimension: Job type, execution frequency
* Technical dimension: Resource usage, configuration parameters

### 3. Practical Value

**Rapid Response Capability**

* **Issue discovery to localization**: < 5 minutes
* **Solution output**: Immediately executable SQL commands
* **Effect verification**: Real-time review of fix results

**Economic Value**

* **Direct savings**: ¥80+/day cost savings
* **Avoid losses**: Prevent ongoing losses from long-term configuration errors
* **Efficiency improvement**: Significantly reduce manual investigation time

**Knowledge Accumulation**

* **Reusable process**: Analysis method applicable to other similar issues
* **Best practices**: Form standardized troubleshooting processes
* **Prevention guide**: Provide experience reference for other users

## Result Verification and Effectiveness Evaluation

### Resolution Effectiveness Confirmation

**Cost Recovery Verification**

```sql
-- Create cost monitoring view
CREATE VIEW daily_cost_monitor AS
SELECT 
    date(measurement_start) as cost_date,
    sum(total_after_discount) as daily_cost,
    CASE 
        WHEN sum(total_after_discount) >

**Results**:

* Sep 6: ¥1.05 ✅ Returned to normal
* Sep 7: ¥0.96 ✅ Continuously normal
* Sep 8: ¥0.53 ✅ Further optimized

**Cluster Usage Pattern Recovery**

* Average usage duration per instance: 0.02 hours (returned to normal short query mode)
* Per-instance cost: ¥0.02-0.7 (returned to reasonable range)
* Cluster auto-suspend: Working normally

### Lessons Learned

**Technical Lessons**

1. **Dynamic table design**: Refresh interval should balance business needs and cost considerations
2. **Resource monitoring**: Establish multi-level cost and resource usage monitoring
3. **Configuration management**: Important configuration changes should be evaluated and tested

**Operations Lessons**

1. **Timely discovery**: Establish automated anomaly detection mechanisms
2. **Rapid localization**: Master systematic troubleshooting methods
3. **Prevention first**: Avoid similar issues through best practices

**Business Lessons**

1. **Cost awareness**: Technical decisions should consider cost implications
2. **Requirement assessment**: Balance between functional requirements and resource consumption
3. **Continuous optimization**: Regularly review and optimize resource usage

## Summary

This real-world case perfectly demonstrates the core value of Singdata Lakehouse MCP Server in enterprise-level data platform operations:

### 🚀 Technological Innovation

* **AI-driven natural language analysis**: Making complex data analysis simple and intuitive
* **Intelligent issue diagnosis**: Automatically identify anomaly patterns and root causes
* **Multi-dimensional correlation analysis**: Quickly extract key information from massive data

### 💰 Business Value

* **Immediate cost savings**: Single case save ¥80+/day
* **Significant operations efficiency improvement**: Troubleshooting time reduced from hours to minutes
* **Risk prevention capability**: Avoid long-term losses from configuration errors

### 🛠️ Practicality

* **Zero barrier usage**: No SQL knowledge needed, natural language completes complex analysis
* **Immediately executable solutions**: Not just diagnosing issues, but providing specific solutions
* **Knowledge transfer**: Analysis processes and methods reusable for similar scenarios

Through this case, we see the enormous potential of AI technology in data platform operations. Singdata Lakehouse MCP Server is not just a tool, but an intelligent operations partner, helping users quickly locate issues, optimize costs, and improve efficiency in complex data environments.

***

*This case is based on real user scenarios with anonymized data, demonstrating the practical value of Singdata Lakehouse MCP Server in cost management, troubleshooting, and operations optimization.*

^

## Reference

[Instance-level Information Schema](instance-information_schema.md)

[Dynamic Table](dynamic-table.md)
