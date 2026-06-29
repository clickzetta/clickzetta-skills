# HR Employee Lifecycle Data Warehouse Best Practices

This guide integrates HRIS system, performance evaluation, and attendance data to build an analytics data warehouse covering the full employee lifecycle from hire to departure. It produces attrition risk predictions, pay equity analysis, and organizational effectiveness diagnostic reports. Using the Kaggle HR Analytics dataset (1,470 employee records), it demonstrates the full **ODS → DWD → DWS → ADS** four-layer architecture end to end, covering Column Masking (salary field masking), Dynamic Table (automatic monthly metric aggregation), and window functions (LEAD/LAG promotion analysis).

![](/.topwrite/assets/anim-29-hr-analytics.svg)

---

## Overview

The core challenge in an HR data warehouse is that the data is highly sensitive (salaries, performance ratings, attrition reasons) while also needing to support different roles with different analysis needs (HR BPs see full data, employees see their own data, analysts see masked data). Singdata Lakehouse addresses these core challenges with the following combination:

| Problem | Solution |
|---|---|
| Salary and performance fields are highly sensitive; different roles see different data | Column Masking bound to columns; non-privileged users automatically receive masked values |
| Multi-layer aggregation across ODS → DWD → ADS needs automatic monthly refresh | Dynamic Table with declarative SQL; the system automatically maintains the dependency chain |
| Need to identify employees with stalled promotions and pay below same-level benchmarks | Window functions `RANK / AVG OVER / LAG` computed directly in the DWD layer |
| Refresh scheduling needs to attach data quality rules and alerts | Studio Task manages scheduling; alerts and quality check rules can be attached to the same task |
| High-cardinality employee ID with frequent point lookups | Add a Bloomfilter Index on demand to speed up department filtering |

---

## SQL Commands Used

| Command / Function | Purpose | Notes |
|---|---|---|
| `CREATE TABLE` | Create the ODS raw employee table | Regular static table used as upstream source for Dynamic Tables |
| `CREATE FUNCTION` | Create the salary masking UDF `mask_salary` | Used for Column Masking policy binding |
| `ALTER TABLE ... CHANGE COLUMN ... SET MASK` | Bind Column Masking to `monthly_income` | Non-privileged users automatically get -1 |
| `CREATE DYNAMIC TABLE` | Create incremental computation tables for DWD / DWS / ADS layers | System detects upstream changes and refreshes incrementally |
| `REFRESH DYNAMIC TABLE` | Trigger a manual refresh | Use during initial build or debugging |
| `AVG() OVER (PARTITION BY ...)` | Calculate the average salary for the same department and level | Used for pay equity analysis |
| `RANK() OVER (ORDER BY ...)` | Calculate an employee's salary rank within their department | Used for pay competitiveness reports |
| `LAG()` | Calculate relative change in promotion intervals | Identify employees with stalled promotions |

---

## Prerequisites

All examples in this guide run under the `best_practice_hr_analytics` Schema.

```sql
CREATE SCHEMA IF NOT EXISTS best_practice_hr_analytics;
```

The dataset comes from the [Kaggle HR Analytics Case Study](https://www.kaggle.com/datasets/bhanupratapbiswas/hr-analytics-case-study) (Apache 2.0), with 1,470 records and 35 columns covering employee age, department, job level, annual salary, performance rating, attrition label, and other core fields. This guide uses the first 40 rows as the demonstration dataset.

---

## ODS (Raw Data Layer): Raw Employee Data

### Create Tables

```sql
CREATE TABLE IF NOT EXISTS best_practice_hr_analytics.doc_ods_employees (
    emp_id                   INT,
    age                      INT,
    attrition                STRING,    -- 'Yes'/'No'，是否已离职
    business_travel          STRING,
    daily_rate               INT,
    department               STRING,
    distance_from_home       INT,
    education                INT,       -- 1=Below College ... 5=Doctor
    education_field          STRING,
    employee_number          INT,
    env_satisfaction         INT,       -- 1-4
    gender                   STRING,
    hourly_rate              INT,
    job_involvement          INT,       -- 1-4
    job_level                INT,       -- 1=Entry ... 5=C-Level
    job_role                 STRING,
    job_satisfaction         INT,       -- 1=Low 4=Very High
    marital_status           STRING,
    monthly_income           INT,       -- 敏感字段，将绑定 Column Masking
    monthly_rate             INT,
    num_companies_worked     INT,
    overtime                 STRING,    -- 'Yes'/'No'
    pct_salary_hike          INT,       -- 上次调薪幅度（%）
    performance_rating       INT,       -- 3=Excellent 4=Outstanding
    relationship_satisfaction INT,      -- 1-4
    stock_option_level       INT,
    total_working_years      INT,
    training_times_last_year INT,
    work_life_balance        INT,       -- 1-4
    years_at_company         INT,
    years_in_current_role    INT,
    years_since_last_promo   INT,
    years_with_curr_mgr      INT
);
```

### Import Data

This guide loads data from a local CSV file (first 40 rows downloaded from Kaggle) via INSERT. In production, use MySQL batch sync or COPY INTO from a Volume to import the full dataset:

```bash
kaggle datasets download -d bhanupratapbiswas/hr-analytics-case-study \
  --unzip -p /tmp/hr_analytics/
```

Import from a local CSV file (recommended):

```sql
-- 第一步：通过 SQL PUT 将本地 CSV 文件上传到 User Volume
PUT '/path/to/your/data.csv' TO USER VOLUME FILE 'data.csv';
```

```sql
-- 第二步：从 User Volume COPY INTO 表
COPY INTO best_practice_hr_analytics.doc_ods_employees
FROM USER VOLUME
USING csv
OPTIONS('header'='true', 'sep'=',', 'nullValue'='')
FILES ('data.csv');
```

You can also insert a small batch of test data inline (no CSV file required):

```sql
-- 通过 INSERT INTO 载入前 40 行演示数据（实际执行，共 40 行）
INSERT INTO best_practice_hr_analytics.doc_ods_employees VALUES
  (1,41,'Yes','Travel_Rarely',1102,'Sales',1,2,'Life Sciences',1,2,
   'Female',94,3,2,'Sales Executive',4,'Single',5993,19479,8,'Yes',11,3,1,0,8,0,1,6,4,0,5),
  (2,49,'No','Travel_Frequently',279,'Research & Development',8,1,'Life Sciences',2,3,
   'Male',61,2,2,'Research Scientist',2,'Married',5130,24907,1,'No',23,4,4,1,10,3,3,10,7,1,7),
  (3,37,'Yes','Travel_Rarely',1373,'Research & Development',2,2,'Other',4,4,
   'Male',92,2,1,'Laboratory Technician',3,'Single',2090,2396,6,'Yes',15,3,2,0,7,3,3,0,0,0,0),
  (4,33,'No','Travel_Frequently',1392,'Research & Development',3,4,'Life Sciences',5,4,
   'Female',56,3,1,'Research Scientist',3,'Married',2909,23159,1,'Yes',11,3,3,0,8,3,3,8,7,3,0),
  (5,27,'No','Travel_Rarely',591,'Research & Development',2,1,'Medical',7,1,
   'Male',40,3,1,'Laboratory Technician',2,'Married',3468,16632,9,'No',12,3,4,1,6,3,3,2,2,2,2),
  (6,32,'No','Travel_Frequently',1005,'Research & Development',2,2,'Life Sciences',8,4,
   'Male',79,3,1,'Laboratory Technician',4,'Single',3068,11864,0,'No',13,3,3,0,8,2,2,7,7,3,6),
  (7,59,'No','Travel_Rarely',1324,'Research & Development',3,3,'Medical',10,3,
   'Female',81,4,1,'Laboratory Technician',1,'Married',2670,9964,4,'Yes',20,4,1,3,12,3,2,1,0,0,0),
  (8,30,'No','Travel_Rarely',1358,'Research & Development',24,1,'Life Sciences',11,4,
   'Male',67,3,1,'Laboratory Technician',3,'Divorced',2693,13335,1,'No',22,4,2,1,1,2,3,1,0,0,0),
  (9,38,'No','Travel_Frequently',216,'Research & Development',23,3,'Life Sciences',12,4,
   'Male',44,2,3,'Manufacturing Director',3,'Single',9526,8787,0,'No',21,4,2,0,10,2,3,9,7,1,8),
  (10,36,'No','Travel_Rarely',1299,'Research & Development',27,3,'Medical',13,3,
   'Male',94,3,2,'Healthcare Representative',3,'Married',5237,16577,6,'No',13,3,2,2,17,3,2,7,7,7,7),
  (11,35,'No','Travel_Rarely',809,'Research & Development',16,3,'Medical',14,1,
   'Male',84,4,1,'Laboratory Technician',2,'Married',2426,16479,0,'No',13,3,3,1,6,5,3,5,4,0,3),
  (12,29,'No','Travel_Rarely',153,'Research & Development',15,2,'Life Sciences',15,4,
   'Female',49,2,2,'Laboratory Technician',3,'Single',4193,12682,0,'Yes',12,3,4,0,10,3,3,9,5,0,8),
  (13,31,'No','Travel_Rarely',670,'Research & Development',26,1,'Life Sciences',16,1,
   'Male',31,3,1,'Research Scientist',3,'Divorced',2911,15170,1,'No',17,3,4,1,5,1,2,5,2,4,3),
  (14,34,'No','Travel_Rarely',1346,'Research & Development',19,2,'Medical',18,2,
   'Male',93,3,1,'Laboratory Technician',4,'Divorced',2661,8758,0,'No',11,3,3,1,3,2,3,2,2,1,2),
  (15,28,'Yes','Travel_Rarely',103,'Research & Development',24,3,'Life Sciences',19,3,
   'Male',50,2,1,'Laboratory Technician',3,'Single',2028,12947,5,'Yes',14,3,2,0,6,4,3,4,2,0,3),
  (16,29,'No','Travel_Rarely',1389,'Research & Development',21,4,'Life Sciences',20,2,
   'Female',51,4,3,'Manufacturing Director',1,'Divorced',9980,10195,1,'No',11,3,3,1,10,1,3,10,9,8,8),
  (17,32,'No','Travel_Rarely',334,'Research & Development',5,2,'Life Sciences',21,1,
   'Male',80,4,1,'Research Scientist',2,'Divorced',3298,15053,0,'Yes',12,3,4,2,7,5,2,6,2,0,5),
  (18,22,'No','Non-Travel',1123,'Research & Development',16,2,'Medical',22,4,
   'Male',96,4,1,'Laboratory Technician',4,'Divorced',2935,7324,1,'Yes',13,3,2,2,1,2,2,1,0,0,0),
  (19,53,'No','Travel_Rarely',1219,'Sales',2,4,'Life Sciences',23,1,
   'Female',78,2,4,'Manager',4,'Married',15427,22021,2,'No',16,3,3,0,31,3,3,25,8,3,7),
  (20,38,'No','Travel_Rarely',371,'Research & Development',2,3,'Life Sciences',24,4,
   'Male',45,3,1,'Research Scientist',4,'Single',3944,4306,5,'Yes',11,3,3,0,6,3,3,3,2,1,2),
  (21,24,'No','Non-Travel',673,'Research & Development',11,2,'Other',26,1,
   'Female',96,4,2,'Manufacturing Director',3,'Divorced',4011,8232,0,'No',18,3,4,1,5,5,2,4,2,1,3),
  (22,36,'Yes','Travel_Rarely',1218,'Sales',9,4,'Life Sciences',27,3,
   'Male',82,2,1,'Sales Representative',1,'Single',3407,6986,7,'No',23,4,2,0,10,4,3,5,3,0,3),
  (23,34,'No','Travel_Rarely',419,'Research & Development',7,4,'Life Sciences',28,1,
   'Female',53,3,3,'Research Director',2,'Single',11994,21293,0,'No',11,3,3,0,13,4,3,12,6,2,11),
  (24,21,'No','Travel_Rarely',391,'Research & Development',15,2,'Life Sciences',30,3,
   'Male',96,3,1,'Research Scientist',4,'Single',1232,19281,1,'No',14,3,4,0,0,6,3,0,0,0,0),
  (25,34,'Yes','Travel_Rarely',699,'Research & Development',6,1,'Medical',31,2,
   'Male',83,3,1,'Research Scientist',1,'Single',2960,17102,2,'No',11,3,3,0,8,2,3,4,2,1,3),
  (26,53,'No','Travel_Rarely',1282,'Research & Development',5,3,'Other',32,3,
   'Female',58,3,5,'Manager',3,'Divorced',19094,10735,4,'No',11,3,4,1,26,3,2,14,13,4,8),
  (27,32,'Yes','Travel_Frequently',1125,'Research & Development',16,1,'Life Sciences',33,2,
   'Female',72,1,1,'Research Scientist',1,'Single',3919,4681,1,'Yes',22,4,2,0,10,5,3,10,2,6,7),
  (28,42,'No','Travel_Rarely',691,'Sales',8,4,'Marketing',35,3,
   'Male',48,3,2,'Sales Executive',2,'Married',6825,21173,0,'No',11,3,4,1,10,2,3,9,7,4,2),
  (29,44,'No','Travel_Rarely',477,'Research & Development',7,4,'Medical',36,1,
   'Female',42,2,3,'Healthcare Representative',4,'Married',10248,2094,3,'No',14,3,4,1,24,4,3,22,6,5,17),
  (30,46,'No','Travel_Rarely',705,'Sales',2,4,'Marketing',38,2,
   'Female',83,3,5,'Manager',1,'Single',18947,22822,3,'No',12,3,4,0,22,2,2,2,2,2,1),
  (31,33,'No','Travel_Rarely',924,'Research & Development',2,3,'Medical',39,3,
   'Male',78,3,1,'Laboratory Technician',4,'Single',2496,6670,4,'No',11,3,4,0,7,3,3,1,1,0,0),
  (32,44,'No','Travel_Rarely',1459,'Research & Development',10,4,'Other',40,4,
   'Male',41,3,2,'Healthcare Representative',4,'Married',6465,19121,2,'Yes',13,3,4,0,9,5,4,4,2,1,3),
  (33,30,'No','Travel_Rarely',125,'Research & Development',9,2,'Medical',41,4,
   'Male',83,2,1,'Laboratory Technician',3,'Single',2206,16117,1,'No',13,3,4,0,10,5,3,10,0,1,8),
  (34,39,'Yes','Travel_Rarely',895,'Sales',5,3,'Technical Degree',42,4,
   'Male',56,3,2,'Sales Representative',4,'Married',2086,3335,3,'No',14,3,3,1,19,6,4,1,0,0,0),
  (35,24,'Yes','Travel_Rarely',813,'Research & Development',1,3,'Medical',45,2,
   'Male',61,3,1,'Research Scientist',4,'Married',2293,3020,2,'Yes',16,3,1,1,6,2,2,2,0,2,0),
  (36,43,'No','Travel_Rarely',1273,'Research & Development',2,2,'Medical',46,4,
   'Female',72,4,1,'Research Scientist',3,'Divorced',2645,21923,1,'No',12,3,4,2,6,3,2,5,3,1,4),
  (37,50,'Yes','Travel_Rarely',869,'Sales',3,2,'Marketing',47,1,
   'Male',86,2,1,'Sales Representative',3,'Married',2683,3810,1,'Yes',14,3,3,0,3,2,3,3,2,0,2),
  (38,35,'No','Travel_Rarely',890,'Sales',2,3,'Marketing',49,4,
   'Female',97,3,1,'Sales Representative',4,'Married',2014,9687,1,'No',13,3,1,0,2,3,3,2,2,2,2),
  (39,36,'No','Travel_Rarely',852,'Research & Development',5,4,'Life Sciences',51,2,
   'Female',82,2,1,'Research Scientist',1,'Married',3419,13072,9,'Yes',14,3,4,1,6,3,4,1,1,0,0),
  (40,33,'No','Travel_Frequently',1141,'Sales',1,3,'Life Sciences',52,3,
   'Female',42,4,2,'Sales Executive',1,'Married',5376,3193,2,'No',19,3,1,2,10,3,3,5,3,1,3)
;
```

Verify row count:

```sql
SELECT COUNT(*) AS ods_row_count
FROM best_practice_hr_analytics.doc_ods_employees;
```

```
ods_row_count
-------------
40
```

### Column Masking: Salary Field Masking

`monthly_income` is a highly sensitive field. The approach: HR administrators see original values; other users get -1 in query results.

```sql
-- 创建脱敏函数
CREATE OR REPLACE FUNCTION best_practice_hr_analytics.mask_salary(salary INT)
RETURNS INT
AS CASE
    WHEN current_user() IN ('privileged_user') THEN salary  -- 替换为实际获授权的用户名
    ELSE -1
END;

-- 绑定到 monthly_income 列
ALTER TABLE best_practice_hr_analytics.doc_ods_employees
CHANGE COLUMN monthly_income
SET MASK best_practice_hr_analytics.mask_salary;
```

Replace `'privileged_user'` with the actual usernames that need to see plaintext data. Column Masking matches the current connection's username via `current_user()`; all authorized usernames must be explicitly listed in the `IN()` list.

> ⚠️ **Note**: Column Masking takes effect transparently for all queries (including Dynamic Tables). When the DWD layer inherits  from ODS, non-privileged users receive the masked value -1.

Verify the masking effect (admin account sees the original values):

```sql
SELECT emp_id, department, job_role, monthly_income
FROM best_practice_hr_analytics.doc_ods_employees
LIMIT 5;
```

```
emp_id | department               | job_role               | monthly_income
-------+--------------------------+------------------------+---------------
31     | Research & Development   | Laboratory Technician  | 2496
32     | Research & Development   | Healthcare Representative | 6465
33     | Research & Development   | Laboratory Technician  | 2206
34     | Sales                    | Sales Representative   | 2086
35     | Research & Development   | Research Scientist     | 2293
```

---

## DWD (Detail Data Layer): Employee Event Timeline

The DWD layer derives three types of analysis fields from ODS raw data: tenure segmentation (`tenure_band`), promotion stall flag (`promotion_stalled_flag`), and retention risk score (`retention_risk_score`).

### Create Tables

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_hr_analytics.doc_dwd_employee_timeline
AS
SELECT
    emp_id,
    department,
    job_role,
    job_level,
    age,
    gender,
    marital_status,
    education,
    education_field,
    years_at_company,
    years_in_current_role,
    years_since_last_promo,
    years_with_curr_mgr,
    total_working_years,
    monthly_income,
    pct_salary_hike,
    performance_rating,
    job_satisfaction,
    work_life_balance,
    env_satisfaction,
    overtime,
    business_travel,
    attrition,
    -- 任期分层，便于分组分析
    CASE
        WHEN years_at_company <= 1  THEN 'New'
        WHEN years_at_company <= 3  THEN 'Junior'
        WHEN years_at_company <= 7  THEN 'Mid'
        WHEN years_at_company <= 15 THEN 'Senior'
        ELSE 'Veteran'
    END AS tenure_band,
    -- 晋升停滞标志：2 年以上未晋升且绩效评分 >= 3
    CASE
        WHEN years_since_last_promo >= 2 AND performance_rating >= 3 THEN 1
        ELSE 0
    END AS promotion_stalled_flag,
    -- 留任风险评分（0.0 ~ 1.0，越高越危险）
    ROUND(
        CASE WHEN overtime = 'Yes' THEN 0.25 ELSE 0.0 END
        + CASE WHEN job_satisfaction <= 2 THEN 0.25 ELSE 0.0 END
        + CASE WHEN work_life_balance <= 2 THEN 0.20 ELSE 0.0 END
        + CASE WHEN years_since_last_promo >= 3 THEN 0.15 ELSE 0.0 END
        + CASE WHEN pct_salary_hike <= 12 THEN 0.15 ELSE 0.0 END
    , 2) AS retention_risk_score
FROM best_practice_hr_analytics.doc_ods_employees;
```

> ⚠️ **Note**: Do not write `REFRESH INTERVAL` in `CREATE DYNAMIC TABLE` DDL. Manage refresh scheduling through Studio Task (see the "Scheduling Configuration" section); monitoring alerts and data quality rules can be attached to the same task.

### Configure Studio Refresh Tasks

> 💡 **Tip**: The examples below use **cz-cli** (the Singdata Lakehouse command-line tool). If cz-cli is not installed, see the [cz-cli Installation and Usage Guide](../setup_cz_cli.md). You can also run SQL in **Development → SQL Editor** in Singdata Studio and configure or trigger scheduled tasks under **Studio → Tasks**.

```bash
# 在 Studio best_practices/hr_analytics/ 路径下创建任务
cz-cli task create-folder hr_analytics --parent 186117 -p skill_test
# 返回 folder_id: 186127

cz-cli task create refresh_hr_dwd_timeline --type SQL --folder 186127 -p skill_test
cz-cli task save-content refresh_hr_dwd_timeline \
  --content "REFRESH DYNAMIC TABLE best_practice_hr_analytics.doc_dwd_employee_timeline;" \
  -p skill_test
cz-cli task save-cron refresh_hr_dwd_timeline --cron "0 1 * * *" -p skill_test
```

Task path: `best_practices/hr_analytics/refresh_hr_dwd_timeline`, triggered daily at 01:00. Additional configurations can be added to this task: row count alerts (notify when DWD row count drops sharply), data quality rules (`retention_risk_score` must not all be 0), and so on.

### Trigger the Initial Refresh Manually

```sql
REFRESH DYNAMIC TABLE best_practice_hr_analytics.doc_dwd_employee_timeline;

SELECT COUNT(*) AS dwd_count
FROM best_practice_hr_analytics.doc_dwd_employee_timeline;
```

```
dwd_count
---------
40
```

### Attrition Risk Analysis by Tenure Segment

Tenure segmentation helps HR identify which stage has the highest employee attrition risk:

```sql
SELECT
    tenure_band,
    COUNT(*) AS emp_count,
    ROUND(AVG(retention_risk_score), 2) AS avg_risk,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) AS attrition_cnt
FROM best_practice_hr_analytics.doc_dwd_employee_timeline
GROUP BY tenure_band
ORDER BY avg_risk DESC;
```

```
tenure_band | emp_count | avg_risk | attrition_cnt
------------+-----------+----------+--------------
Senior      | 10        | 0.39     | 1
Mid         | 13        | 0.36     | 4
Junior      | 7         | 0.32     | 2
New         | 8         | 0.26     | 2
Veteran     | 2         | 0.15     | 0
```

Senior (7–15 years) and Mid (3–7 years) employees have the highest average retention risk at 0.39 and 0.36 respectively, suggesting these groups face more pressure from overtime and stalled promotions. Veteran (15+ years) employees have the lowest risk, likely having reached stable positions.

---

## DWS (Summary Data Layer): Department Workforce Metrics Aggregation

The DWS layer aggregates DWD layer data at `department` granularity, outputting department-level attrition rate, average tenure, salary benchmarks, and risk index.

### Create Tables

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_hr_analytics.doc_dws_dept_headcount_metrics
AS
SELECT
    department,
    COUNT(*)                                              AS headcount,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END)   AS attrition_count,
    ROUND(SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2)                          AS attrition_rate_pct,
    ROUND(AVG(years_at_company), 2)                       AS avg_tenure_years,
    ROUND(AVG(monthly_income), 0)                         AS avg_monthly_income,
    ROUND(AVG(performance_rating), 2)                     AS avg_performance,
    ROUND(AVG(job_satisfaction), 2)                       AS avg_job_satisfaction,
    ROUND(AVG(retention_risk_score), 2)                   AS avg_retention_risk,
    SUM(CASE WHEN overtime = 'Yes' THEN 1 ELSE 0 END)     AS overtime_headcount,
    SUM(promotion_stalled_flag)                           AS promotion_stalled_count
FROM best_practice_hr_analytics.doc_dwd_employee_timeline
GROUP BY department;
```

```bash
cz-cli task create refresh_hr_dws_dept_metrics --type SQL --folder 186127 -p skill_test
cz-cli task save-content refresh_hr_dws_dept_metrics \
  --content "REFRESH DYNAMIC TABLE best_practice_hr_analytics.doc_dws_dept_headcount_metrics;" \
  -p skill_test
cz-cli task save-cron refresh_hr_dws_dept_metrics --cron "30 1 * * *" -p skill_test
```

Trigger a manual refresh and query:

```sql
REFRESH DYNAMIC TABLE best_practice_hr_analytics.doc_dws_dept_headcount_metrics;

SELECT department, headcount, attrition_count, attrition_rate_pct,
       avg_tenure_years, avg_monthly_income, avg_performance, avg_retention_risk
FROM best_practice_hr_analytics.doc_dws_dept_headcount_metrics
ORDER BY attrition_rate_pct DESC;
```

```
department                 | headcount | attrition_count | attrition_rate_pct | avg_tenure_years | avg_monthly_income | avg_performance | avg_retention_risk
---------------------------+-----------+-----------------+--------------------+------------------+--------------------+-----------------+-------------------
Sales                      | 9         | 4               | 44.44              | 6.44             | 6973               | 3.11            | 0.29
Research & Development     | 31        | 5               | 16.13              | 5.77             | 4650               | 3.16            | 0.34
```

Results interpretation:

- Sales department attrition rate (44.44%) is far higher than R&D (16.13%), but Sales average salary (6,973) is higher than R&D (4,650), indicating salary is not the main driver of Sales attrition. Looking at `avg_retention_risk`, R&D's overall risk average (0.34) is actually higher than Sales (0.29), likely because overtime and promotion stalls are more prevalent in R&D.
- Performance rating averages are similar across both departments (3.11 vs 3.16), indicating that employees who leave are not low performers. HR should prioritize organizational culture and career development paths.

---

## ADS (Application Data Layer): Attrition Risk Report and Pay Analysis

### Attrition Risk Report

```sql
CREATE DYNAMIC TABLE IF NOT EXISTS best_practice_hr_analytics.doc_ads_attrition_risk_report
AS
SELECT
    emp_id,
    department,
    job_role,
    job_level,
    tenure_band,
    years_at_company,
    years_since_last_promo,
    overtime,
    job_satisfaction,
    work_life_balance,
    performance_rating,
    monthly_income,
    pct_salary_hike,
    promotion_stalled_flag,
    retention_risk_score,
    attrition,
    -- 风险等级
    CASE
        WHEN retention_risk_score >= 0.6 THEN 'HIGH'
        WHEN retention_risk_score >= 0.3 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS risk_level,
    -- 主要离职信号
    CASE
        WHEN overtime = 'Yes' AND job_satisfaction <= 2 THEN 'Overwork+LowSatisfaction'
        WHEN overtime = 'Yes'                           THEN 'Overwork'
        WHEN job_satisfaction <= 2                      THEN 'LowSatisfaction'
        WHEN years_since_last_promo >= 3                THEN 'PromotionStalled'
        WHEN pct_salary_hike <= 12                      THEN 'LowPayRaise'
        ELSE 'Normal'
    END AS primary_risk_signal
FROM best_practice_hr_analytics.doc_dwd_employee_timeline;
```

```bash
cz-cli task create refresh_hr_ads_risk_report --type SQL --folder 186127 -p skill_test
cz-cli task save-content refresh_hr_ads_risk_report \
  --content "REFRESH DYNAMIC TABLE best_practice_hr_analytics.doc_ads_attrition_risk_report;" \
  -p skill_test
cz-cli task save-cron refresh_hr_ads_risk_report --cron "0 2 * * *" -p skill_test
```

View the risk distribution after refresh:

```sql
REFRESH DYNAMIC TABLE best_practice_hr_analytics.doc_ads_attrition_risk_report;

SELECT risk_level,
       COUNT(*) AS emp_count,
       ROUND(AVG(retention_risk_score), 2) AS avg_risk,
       SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) AS actual_attrition
FROM best_practice_hr_analytics.doc_ads_attrition_risk_report
GROUP BY risk_level
ORDER BY avg_risk DESC;
```

```
risk_level | emp_count | avg_risk | actual_attrition
-----------+-----------+----------+-----------------
HIGH       | 5         | 0.68     | 2
MEDIUM     | 16        | 0.43     | 2
LOW        | 19        | 0.15     | 5
```

View HIGH risk employee details:

```sql
SELECT emp_id, department, job_role, years_at_company,
       years_since_last_promo, monthly_income,
       pct_salary_hike, retention_risk_score, risk_level, primary_risk_signal
FROM best_practice_hr_analytics.doc_ads_attrition_risk_report
WHERE risk_level = 'HIGH'
ORDER BY retention_risk_score DESC;
```

```
emp_id | department               | job_role             | years_at_company | years_since_last_promo | monthly_income | pct_salary_hike | retention_risk_score | risk_level | primary_risk_signal
-------+--------------------------+----------------------+------------------+------------------------+----------------+-----------------+----------------------+------------+--------------------------
17     | Research & Development   | Research Scientist   | 6                | 0                      | 3298           | 12              | 0.85                 | HIGH       | Overwork+LowSatisfaction
7      | Research & Development   | Laboratory Technician| 1                | 0                      | 2670           | 20              | 0.70                 | HIGH       | Overwork+LowSatisfaction
27     | Research & Development   | Research Scientist   | 10               | 6                      | 3919           | 22              | 0.65                 | HIGH       | Overwork+LowSatisfaction
30     | Sales                    | Manager              | 2                | 2                      | 18947          | 12              | 0.60                 | HIGH       | LowSatisfaction
1      | Sales                    | Sales Executive      | 6                | 0                      | 5993           | 11              | 0.60                 | HIGH       | Overwork
```

Results interpretation:

- emp_id=17 (R&D Research Scientist) has the highest risk (0.85), triggered by the combination of overtime and low job satisfaction, plus a salary increase of only 12% — at the LowPayRaise threshold. Priority one-on-one conversations and compensation review are recommended.
- emp_id=27 (R&D Research Scientist, 10 years tenure) has not been promoted for 6 consecutive years (`years_since_last_promo=6`). Although the salary increase rate is relatively reasonable (22%), the stalled career progression is the primary risk signal.
- emp_id=30 (Sales Manager, salary 18,947) has a high salary but low job satisfaction, indicating that retention for management must address non-monetary factors.

### Overtime × Job Satisfaction Cross-Analysis

```sql
SELECT
    overtime,
    job_satisfaction,
    COUNT(*)                                               AS emp_count,
    ROUND(AVG(retention_risk_score), 2)                   AS avg_risk,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END)   AS attrition_cnt
FROM best_practice_hr_analytics.doc_dwd_employee_timeline
GROUP BY overtime, job_satisfaction
ORDER BY avg_risk DESC
LIMIT 8;
```

```
overtime | job_satisfaction | emp_count | avg_risk | attrition_cnt
---------+------------------+-----------+----------+--------------
Yes      | 2                | 1         | 0.85     | 0
Yes      | 1                | 3         | 0.62     | 1
Yes      | 4                | 5         | 0.43     | 2
No       | 1                | 5         | 0.41     | 2
No       | 2                | 5         | 0.37     | 0
Yes      | 3                | 5         | 0.34     | 3
No       | 3                | 8         | 0.22     | 0
No       | 4                | 8         | 0.12     | 1
```

The `overtime=Yes` + `job_satisfaction <= 2` combination has significantly higher average risk (0.62–0.85) than other combinations — the highest-priority cross-dimension for intervention. Notably, no-overtime but low-satisfaction (`overtime=No, satisfaction=1`) employees have an average risk of 0.41, close to the overtime + medium-satisfaction group, showing that job satisfaction has a substantial independent effect.

---

## Pay Equity Analysis (Window Functions)

The following queries do not build a Dynamic Table; they run directly against the DWD layer as ad-hoc analysis requests.

### Same-Level Pay Equity Analysis

```sql
SELECT
    emp_id,
    department,
    job_role,
    job_level,
    monthly_income,
    years_at_company,
    pct_salary_hike,
    AVG(monthly_income) OVER (PARTITION BY department, job_level) AS dept_level_avg_income,
    ROUND(
        (monthly_income - AVG(monthly_income) OVER (PARTITION BY department, job_level))
        / AVG(monthly_income) OVER (PARTITION BY department, job_level) * 100
    , 1) AS income_vs_peer_pct,
    RANK() OVER (PARTITION BY department ORDER BY monthly_income DESC) AS income_rank_in_dept
FROM best_practice_hr_analytics.doc_dwd_employee_timeline
WHERE department = 'Sales'
ORDER BY job_level DESC, monthly_income DESC;
```

```
emp_id | department | job_role              | job_level | monthly_income | years_at_company | pct_salary_hike | dept_level_avg_income | income_vs_peer_pct | income_rank_in_dept
-------+------------+-----------------------+-----------+----------------+------------------+-----------------+-----------------------+--------------------+--------------------
30     | Sales      | Manager               | 5         | 18947          | 2                | 12              | 18947                 | 0                  | 1
19     | Sales      | Manager               | 4         | 15427          | 25               | 16              | 15427                 | 0                  | 2
28     | Sales      | Sales Executive       | 2         | 6825           | 9                | 11              | 5070                  | 34.6               | 3
1      | Sales      | Sales Executive       | 2         | 5993           | 6                | 11              | 5070                  | 18.2               | 4
40     | Sales      | Sales Executive       | 2         | 5376           | 5                | 19              | 5070                  | 6.0                | 5
34     | Sales      | Sales Representative  | 2         | 2086           | 1                | 14              | 5070                  | -58.9              | 8
22     | Sales      | Sales Representative  | 1         | 3407           | 5                | 23              | 2701                  | 26.1               | 6
37     | Sales      | Sales Representative  | 1         | 2683           | 3                | 14              | 2701                  | -0.7               | 7
38     | Sales      | Sales Representative  | 1         | 2014           | 2                | 13              | 2701                  | -25.4              | 9
```

Results interpretation:

- emp_id=34 (Sales Representative, job_level=2) earns 58.9% below the same-level average with only 1 year at the company — a low-pay, high-risk employee. Check whether the initial compensation was set appropriately at hire.
- emp_id=28 (Sales Executive) earns 34.6% above the same-level average. Given their 9-year tenure, this is a normal seniority premium; however, their salary increase rate (11%) is below peers, and if it continues, dissatisfaction may build up.

### Promotion Lag Analysis (LAG)

```sql
SELECT
    emp_id,
    department,
    job_role,
    job_level,
    years_at_company,
    years_since_last_promo,
    performance_rating,
    LAG(performance_rating) OVER (
        PARTITION BY department ORDER BY years_at_company
    ) AS prev_emp_perf,
    years_since_last_promo - LAG(years_since_last_promo) OVER (
        PARTITION BY department ORDER BY years_at_company
    ) AS promo_lag_delta
FROM best_practice_hr_analytics.doc_dwd_employee_timeline
WHERE department = 'Research & Development'
ORDER BY years_since_last_promo DESC
LIMIT 10;
```

```
emp_id | department               | job_role                    | job_level | years_at_company | years_since_last_promo | performance_rating | prev_emp_perf | promo_lag_delta
-------+--------------------------+-----------------------------+-----------+------------------+------------------------+--------------------+---------------+----------------
16     | Research & Development   | Manufacturing Director      | 3         | 10               | 8                      | 3                  | 4             | 7
10     | Research & Development   | Healthcare Representative   | 2         | 7                | 7                      | 3                  | 3             | 4
27     | Research & Development   | Research Scientist          | 1         | 10               | 6                      | 4                  | 3             | -2
29     | Research & Development   | Healthcare Representative   | 3         | 22               | 5                      | 3                  | 3             | 1
13     | Research & Development   | Research Scientist          | 1         | 5                | 4                      | 3                  | 3             | 4
26     | Research & Development   | Manager                     | 5         | 14               | 4                      | 3                  | 3             | 2
```

Results interpretation:

- emp_id=16 (Manufacturing Director) has not been promoted for 8 years with performance rating consistently at 3 (Excellent). `promo_lag_delta=7` means their promotion wait time is 7 years longer than the preceding employee with similar tenure in the department — a clear promotion anomaly.
- emp_id=27 (Research Scientist, 10 years tenure, no promotion for 6 consecutive years, performance rating 4 = Outstanding) is the most typical "high-performer blocked from promotion" case. Already appearing on the HIGH risk list, this requires HR BP intervention to evaluate the promotion path.

---

## Data Warehouse Object Summary

After the full build, all objects under the `best_practice_hr_analytics` Schema:

```sql
SHOW TABLES IN best_practice_hr_analytics;
```

```
schema_name                    | table_name                       | is_dynamic
-------------------------------+----------------------------------+-----------
best_practice_hr_analytics     | doc_ads_attrition_risk_report    | true
best_practice_hr_analytics     | doc_dwd_employee_timeline        | true
best_practice_hr_analytics     | doc_dws_dept_headcount_metrics   | true
best_practice_hr_analytics     | doc_ods_employees                | false
```

Studio task path (`best_practices/hr_analytics/`):

| Task Name | Refresh Target | Schedule |
|---|---|---|
| `refresh_hr_dwd_timeline` | `doc_dwd_employee_timeline` | Daily 01:00 |
| `refresh_hr_dws_dept_metrics` | `doc_dws_dept_headcount_metrics` | Daily 01:30 |
| `refresh_hr_ads_risk_report` | `doc_ads_attrition_risk_report` | Daily 02:00 |

---

## Notes

- **Column Masking applies transparently to Dynamic Tables**: After the DWD layer inherits `monthly_income` from ODS, non-privileged users see the salary field as the masked value (-1) across DWD / DWS / ADS. To run pay equity analysis, you must use an account authorized in the Column Masking policy (explicitly listed in the mask function's `IN()` list) to see the original unmasked values.

- **Do not write REFRESH INTERVAL in Dynamic Table DDL**: All Dynamic Table DDLs omit the `REFRESH INTERVAL` parameter; refresh scheduling is managed centrally through Studio Task. This lets you attach data quality rules (such as checking whether `retention_risk_score` is all 0) and alert notifications to the same task node.

- **Retention risk score is a heuristic model**: `retention_risk_score` is based on accumulated rules for overtime, satisfaction, promotion stalls, and salary increase rates. It is suitable for quickly screening high-risk groups but does not replace a professional statistical prediction model. For production, use a ZettaPark Python Task to run a machine learning model and write results back to the ADS layer.

- **Dynamic Table incremental refresh depends on ODS change tracking**: The first `REFRESH` performs a full snapshot. Subsequent incremental refreshes process only rows added or changed in the ODS layer since the last refresh. Using `INSERT OVERWRITE` or full rewrites in the ODS layer causes the Dynamic Table to degrade to a full refresh, significantly increasing computation cost.

- **Window semantics for the LAG promotion lag analysis**: The `LAG` with `PARTITION BY department ORDER BY years_at_company` sorts employees within the same department by tenure, comparing promotion-stall differences between employees with similar tenure — not a single employee's historical timeline. For comparing a single employee at different points in time, you need an employee history snapshot table with a time dimension.

---

## Related Documentation

- [CREATE DYNAMIC TABLE](../create-dynamic-table.md) — Syntax reference and incremental refresh mechanism
- [Dynamic Data Masking](../dynamic-mask.md) — Column Masking policy creation and binding
- [Window Functions Comprehensive Guide](../sql_data_transform_windows.md) — Full parameter reference for RANK / LAG / LEAD / AVG OVER
- [Medallion Architecture: Pure SQL Dynamic Table Approach](../lakehouse-medallion-sql-dt-guide.md) — Large-scale three-layer data warehouse reference
- [Slowly Changing Dimensions (SCD2) and MERGE INTO](../scd2-product-dimension-with-merge-into.md) — SCD2 implementation for employee history snapshots

> ⚠️ **Note**: Column Masking currently matches authorized usernames via `current_user()`. Add all usernames that need plaintext access to the masking function's allowlist. If your Lakehouse version supports role-based dynamic evaluation (such as `HAS_ROLE('role_name')`), use roles instead. Contact Singdata technical support to confirm whether your version supports this function.