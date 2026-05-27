# Lakehouse Column-Level Security (Dynamic Masking) User Guide

## 1. Overview

Column-level Security provides fine-grained data protection capabilities through Dynamic Data Masking, which dynamically modifies the display of sensitive data (such as partial hiding or character replacement) based on user identity or role. We only store the original data and execute the masking function at runtime during data access. This document introduces how to implement this functionality through SQL interfaces.

## 2. Core Syntax

### 2.1 Creating Masking Policy Functions

Refer to the [CREATE FUNCTION (SQL)](create-sql-function.md) syntax.

```sql
CREATE FUNCTION [schema_name.]function_name (col_name column_type) 
RETURNS output_type 
AS 
expression_with_conditional_logic;
```

**Key Elements**:

- Must return the same data type as the original column.
- Use security context functions:
  - `current_user()` to get the current user (note case sensitivity).
  - `current_roles()` to get an array of user roles.

### 2.2 Binding Policies to Columns

**When Creating a Table**:

```sql
CREATE TABLE table_name (
  col1 STRING MASK schema_name.masking_function,
  ...
);
```

**Modifying an Existing Table**:

```sql
ALTER TABLE table_name 
CHANGE COLUMN column_name 
SET MASK schema_name.masking_function;
```

**Adding a Column with Masking**:

```sql
ALTER TABLE table_name ADD COLUMN (column_name column_type MASK schema_name.masking_function);
```

### 2.3 Removing Policy Binding

```sql
ALTER TABLE table_name 
CHANGE COLUMN column_name 
UNSET MASK;
```

***

## 3. Use Case Examples

### 3.1 Basic Masking

**Requirement**: Display the first 6 characters of an ID card number, followed by 4 asterisks, and then the last 4 characters.

```sql
CREATE FUNCTION public.idcard_masking(idcard STRING)
RETURNS STRING
AS concat(substr(idcard, 1, 6), repeat('*', 4), substr(idcard, 10, 4));

ALTER TABLE data CHANGE COLUMN idcard SET MASK public.idcard_masking;
```

**Query Effect**:

```
Original Value: 130183199901011234 → Masked: 130183****9010
```

### 3.2 Dynamic Masking Based on User

**Requirement**: Only the `UAT_TEST` user should see masked data.

```sql
CREATE FUNCTION public.idcard_masking(idcard STRING)
RETURNS STRING
AS 
CASE 
  WHEN current_user() = "UAT_TEST" 
  THEN concat(substr(idcard, 1, 6), repeat('*', 4), substr(idcard, 10, 4))
  ELSE idcard 
END;

-- Ignoring case sensitivity of the username
CREATE FUNCTION public.idcard_masking(idcard STRING)
RETURNS STRING
AS 
CASE 
  WHEN lower(current_user()) = "uat_test" 
  THEN concat(substr(idcard, 1, 6), repeat('*', 4), substr(idcard, 10, 4))
  ELSE idcard 
END;
```

### 3.3 Dynamic Masking Based on Role

**Requirement**: Users with the `user_admin` role can view the full information.

```sql
CREATE FUNCTION public.idcard_masking_role(idcard STRING)
RETURNS STRING
AS 
CASE 
  WHEN array_contains(current_roles(), "user_admin") 
  THEN idcard
  ELSE concat(substr(idcard,1,6), '****', substr(idcard,11,4)) 
END;
```

***

## 4. Complete Operation Example

### 4.1 Initializing the Environment

```sql
CREATE SCHEMA IF NOT EXISTS security_demo;
USE security_demo;

-- General masking function
CREATE FUNCTION security_demo.ssn_mask(ssn STRING)
RETURNS STRING
AS concat('***-**-', substr(ssn, 8, 4));

CREATE TABLE security_demo.user_data (
  name STRING,
  ssn STRING MASK security_demo.ssn_mask,  -- Binding directly when creating the table
  phone STRING
);

INSERT INTO security_demo.user_data VALUES ('James', '123-45-6789', '123456789');
SELECT * FROM security_demo.user_data;
```

### 4.2 Creating Policy Functions

```sql
-- Exemption for privileged roles
CREATE FUNCTION security_demo.admin_ssn_mask(ssn STRING)
RETURNS STRING
AS 
CASE
  WHEN array_contains(current_roles(), 'user_admin') THEN ssn
  ELSE concat('***-**-', substr(ssn,8,4))
END;
```

### 4.3 Modifying Masking Policies

```sql
-- Removing the previous policy
ALTER TABLE security_demo.user_data CHANGE COLUMN ssn UNSET MASK;

-- Adding a new policy
ALTER TABLE security_demo.user_data CHANGE COLUMN ssn SET MASK security_demo.admin_ssn_mask;
```

### 4.4 Verifying the Effect

**Query by a Regular User**:

```sql
SELECT * FROM user_data;
-- Output: John Doe ***-**-6789 138****1234
```

**Query by a USER_ADMIN Role**:

```sql
SELECT * FROM user_data; 
-- Output: John Doe 123-45-6789 138****1234
```

***

## 5. Management Notes

### 5.1 Permission Control

- Only roles with `ALTER TABLE` permissions are allowed to modify masking policies.
- Function creation requires `CREATE FUNCTION` permissions.

### 5.2 Performance Recommendations

- Avoid using complex calculations in masking functions.
- Use conditional logic cautiously for columns with high query frequency.

## 6. Limitations

- Only one masking policy can be bound to a single column. If you want to define multiple masking rules, you can use conditional logic within a single function to apply different policies.