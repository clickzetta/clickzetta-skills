# EXPLAIN Command Product Documentation

## Overview

EXPLAIN is a diagnostic command in Singdata Lakehouse used to analyze the execution plan of SQL queries. By examining the execution plan, users can understand query execution flow, identify performance bottlenecks, and perform targeted query optimization. This command supports both basic and extended output modes.

## Command Syntax

```sql
EXPLAIN [EXTENDED] query_statement
```

## Execution Plan Modes

### 1. Basic Execution Plan Mode (EXPLAIN)

The basic mode displays the physical execution plan of the query, used for quickly understanding how the query is executed.

#### Characteristics

* **Lightweight Output**: Shows the core steps of physical execution
* **Quick Diagnosis**: Used for quickly identifying the query execution approach
* **Contents**: Physical table scans, table data output, operator names, and stage information

#### Syntax

```sql
EXPLAIN query_statement
```

#### Example

```sql
EXPLAIN SELECT * FROM a_decimal LIMIT 5
```

**Verification Result (Actual Output)**:

```
Type: DMLPlan: PhysicalTableSink() name=TableSink0 stage=stg0  PhysicalTableScan(a_decimal, a) as [0] name=TableScan1
```

### 2. Extended Execution Plan Mode (EXPLAIN EXTENDED)

The extended mode displays the complete logical execution plan and physical execution plan, including more detailed optimization information.

#### Characteristics

* **Complete Output**: Contains both logical plan and physical plan layers
* **Detailed Analysis**: Shows expression transformations, system columns, optimization processes, etc.

* **Contents**:

  * Logical Execution Plan (LogicalPlan)
  * Physical Execution Plan (DML)
  * System Hidden Column Information
  * Expression Type Conversion

#### Syntax

```sql
EXPLAIN EXTENDED query_statement
```

#### Example

The following command has been verified through Singdata MCP Server:

```sql
EXPLAIN EXTENDED SELECT * FROM a_decimal LIMIT 5
```

**Verification Result (Actual Output)**:

```
[LogicalPlan]Type: LogicalPlanPlan: TableSink()  LogicalSort(_TRY_TO_INT64(5))    LogicalCalc($0 as 0) as [0]      TableScan(a_decimal, a, ORIGINAL__SLICE__ID, ORIGINAL__ROW__OFFSET,        row_offset_in_file, __incremental_deleted, __commit_version,        __change_type, __commit_timestamp, INPUT__FILE__NAME,        FILE__SLICE__ID, __data_source_id, __snapshot_id) as [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11][PhysicalPlan]Type: DMLPlan: PhysicalTableSink() name=TableSink0 stage=stg0  PhysicalTableScan(a_decimal, a) as [0] name=TableScan1
```



## Common Operators in Execution Plans

| Operator              | Description          | Performance Characteristics                         |
| --------------------- | -------------------- | --------------------------------------------------- |
| PhysicalTableScan     | Read data from table | Basic I/O operation                                 |
| PhysicalTableSink     | Output query results | Fixed overhead                                      |
| PhysicalSort          | Sort data            | O(n log n), may become a bottleneck                 |
| PhysicalFilter        | Conditional filter   | Linear operation; early filtering is best practice  |
| PhysicalHashAggregate | Aggregate operation  | Varies based on GROUP BY cardinality                |
| PhysicalJoin          | JOIN operation       | Complexity depends on JOIN strategy and data volume |

