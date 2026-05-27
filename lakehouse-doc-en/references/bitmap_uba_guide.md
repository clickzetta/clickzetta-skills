# User Behavior Analysis and Precision Marketing BITMAP Practical Guide

## Guide Overview

This guide demonstrates, through real-world business scenarios, how to use Singdata Lakehouse's BITMAP functions to solve core business problems such as user analysis, precision marketing, and operational optimization. Each scenario provides a complete end-to-end solution from table creation to querying.

### Business Value

* **Precision User Profiling**: Efficiently analyze user behavior overlap and differences
* **Intelligent Marketing Recommendations**: Quickly compute user similarity and interest matching
* **Real-Time Operational Decisions**: Support real-time analysis of large-scale user groups
* **Cost Optimization**: Significantly reduce storage space and compute resource consumption

### Content Navigation

This guide is divided into four main parts:

### Part 1: Business Scenario Practice

Contains 6 complete business scenarios, covering the full workflow from table creation to analysis:

* **Scenario 1**: Multi-Channel User Overlap Analysis - Address marketing placement duplication and effectiveness evaluation
* **Scenario 2**: User Interest Recommendation System - Achieve precise personalized recommendations
* **Scenario 3**: A/B Test Effectiveness Analysis - Accurately evaluate product experiment results
* **Scenario 4**: User Lifecycle Analysis - Optimize user conversion funnels
* **Scenario 5**: Permission Management System - Efficient enterprise permission control
* **Scenario 6**: Large-Scale Data Pagination - Handle massive user data

### Part 2: Technical Function Guide

Detailed introduction to BITMAP function categories and usage methods

### Part 3: Pitfall Avoidance Guide

Common errors and solutions to help quickly troubleshoot issues

### Part 4: Environment Requirements and Summary

Operating environment description and best practices summary

***

## Business Scenario Practice Cases

### Scenario 1: Multi-Channel User Overlap Analysis

#### Why Do This Analysis?

Marketing teams advertise across multiple channels (Facebook, Google, TikTok, etc.) to acquire users but face the following challenges:

* **Duplicate Placement Costs**: Unknown how many users see ads across multiple channels, causing budget waste
* **Channel Effectiveness Comparison**: Unable to accurately assess which channel brings unique users and which brings mostly duplicate users
* **Placement Strategy Optimization**: Need to understand user overlap to adjust placement ratios and budget allocations across channels
* **Precision Marketing**: Identify users active in only a single channel for targeted cross-channel marketing

BITMAP functions can efficiently compute the overlap among millions of users across different channels, providing data support for marketing decisions.

#### 1.1 Table Preparation

```sql
-- Create user activity table
CREATE TABLE IF NOT EXISTS user_activity (
    user_id BIGINT,
    channel STRING,
    activity_date DATE,
    event_type STRING
) PARTITIONED BY (activity_date);

-- Insert sample data
INSERT INTO user_activity VALUES
(1001, 'facebook', DATE('2024-01-15'), 'register'),
(1002, 'google', DATE('2024-01-15'), 'register'),
(1003, 'tiktok', DATE('2024-01-15'), 'register'),
(1001, 'google', DATE('2024-01-16'), 'login'),
(1004, 'facebook', DATE('2024-01-16'), 'register'),
(1005, 'google', DATE('2024-01-16'), 'register'),
(1006, 'tiktok', DATE('2024-01-16'), 'register'),
(1007, 'facebook', DATE('2024-01-17'), 'register'),
(1008, 'google', DATE('2024-01-17'), 'register'),
(1009, 'tiktok', DATE('2024-01-17'), 'register'),
(1002, 'tiktok', DATE('2024-01-17'), 'login');
```

#### 1.2 Channel User Overlap Analysis

```sql
-- Compute overlapping users between two channels
WITH facebook_users AS (
  SELECT group_bitmap_state(user_id) as users
  FROM user_activity
  WHERE channel = 'facebook'
),
google_users AS (
  SELECT group_bitmap_state(user_id) as users
  FROM user_activity
  WHERE channel = 'google'
)
SELECT 
  bitmap_cardinality(fu.users) as facebook_user_count,
  bitmap_cardinality(gu.users) as google_user_count,
  bitmap_and_cardinality(fu.users, gu.users) as overlap_count,
  bitmap_to_array(bitmap_and(fu.users, gu.users)) as overlap_user_ids
FROM facebook_users fu, google_users gu;
```

**Expected result**: Returns overlapping user ID [1001], consistent with business logic.

### Scenario 2: User Interest Recommendation System

#### Why Do This Analysis?

E-commerce platforms face personalized recommendation challenges:

* **Recommendation Accuracy**: Need to base recommendations on users' actual purchase and browsing behavior rather than simple popular product recommendations
* **Similar User Discovery**: Identify users with similar interests to enable collaborative filtering recommendations
* **New User Cold Start**: Quickly find similar users for recommendations by analyzing initial user behavior
* **Recommendation Diversity**: Avoid overly narrow recommendations while ensuring relevance
* **Real-Time Requirements**: Rapidly update recommendation results as user behavior changes

BITMAP functions can efficiently compute similarity between user interest vectors, supporting real-time recommendation systems.

#### 2.1 Table Preparation

```sql
-- Create user behavior table
CREATE TABLE IF NOT EXISTS user_behavior (
    user_id BIGINT,
    item_id BIGINT,
    behavior_type STRING,  -- 'view', 'cart', 'purchase'
    behavior_date DATE
) PARTITIONED BY (behavior_date);

-- Create item category table
CREATE TABLE IF NOT EXISTS item_category (
    item_id BIGINT,
    category_id INT,
    category_name STRING
);

-- Insert sample data
INSERT INTO user_behavior VALUES
(1001, 1, 'view', DATE('2024-01-15')),
(1001, 2, 'purchase', DATE('2024-01-15')),
(1001, 5, 'view', DATE('2024-01-15')),
(1002, 1, 'view', DATE('2024-01-15')),
(1002, 3, 'purchase', DATE('2024-01-15')),
(1002, 4, 'cart', DATE('2024-01-15')),
(1003, 2, 'view', DATE('2024-01-16')),
(1003, 5, 'purchase', DATE('2024-01-16')),
(1003, 6, 'view', DATE('2024-01-16')),
(1004, 1, 'purchase', DATE('2024-01-16')),
(1004, 4, 'view', DATE('2024-01-16'));

INSERT INTO item_category VALUES
(1, 101, 'Electronics'),
(2, 101, 'Electronics'),
(3, 102, 'Clothing'),
(4, 102, 'Clothing'),
(5, 103, 'Books'),
(6, 103, 'Books');
```

#### 2.2 Compute User Interest Similarity

```sql
-- Compute interest similarity based on user behavior
WITH user_interests AS (
  SELECT 
    ub.user_id,
    group_bitmap_state(ic.category_id) as interest_categories
  FROM user_behavior ub
  JOIN item_category ic ON ub.item_id = ic.item_id
  WHERE ub.behavior_date >= '2024-01-01'
  GROUP BY ub.user_id
)
SELECT 
  u1.user_id as user_a,
  u2.user_id as user_b,
  bitmap_cardinality(u1.interest_categories) as user_a_interests,
  bitmap_cardinality(u2.interest_categories) as user_b_interests,
  bitmap_and_cardinality(u1.interest_categories, u2.interest_categories) as shared_interests,
  ROUND(bitmap_and_cardinality(u1.interest_categories, u2.interest_categories) * 100.0 / 
        bitmap_cardinality(u2.interest_categories), 2) as similarity_pct
FROM user_interests u1
JOIN user_interests u2 ON u1.user_id < u2.user_id
ORDER BY similarity_pct DESC;
```

**Business value**: Users 1001 and 1004 have 100% similarity in the Electronics category, making the recommendation logic precise.

#### 2.3 Recommend Products Purchased by Similar Users

```sql
-- Recommend products purchased by similar users for a specified user
WITH target_user_interests AS (
  SELECT group_bitmap_state(ic.category_id) as interests
  FROM user_behavior ub
  JOIN item_category ic ON ub.item_id = ic.item_id
  WHERE ub.user_id = 1001 
    AND ub.behavior_type IN ('purchase', 'cart')
),
similar_users AS (
  SELECT 
    ub.user_id,
    group_bitmap_state(ic.category_id) as interests
  FROM user_behavior ub
  JOIN item_category ic ON ub.item_id = ic.item_id
  WHERE ub.user_id != 1001
    AND ub.behavior_type IN ('purchase', 'cart')
  GROUP BY ub.user_id
  HAVING bitmap_and_cardinality(
    group_bitmap_state(ic.category_id), 
    (SELECT interests FROM target_user_interests)
  ) >= 1
),
user_purchased_items AS (
  SELECT group_bitmap_state(item_id) as purchased_items
  FROM user_behavior 
  WHERE user_id = 1001 AND behavior_type = 'purchase'
)
SELECT 
  ub.item_id,
  ic.category_name,
  COUNT(DISTINCT ub.user_id) as recommended_by_users,
  ARRAY_AGG(DISTINCT ub.user_id) as recommending_users
FROM similar_users su
JOIN user_behavior ub ON su.user_id = ub.user_id
JOIN item_category ic ON ub.item_id = ic.item_id
CROSS JOIN user_purchased_items upi
WHERE ub.behavior_type = 'purchase'
  AND NOT bitmap_contains(upi.purchased_items, ub.item_id)  -- Exclude already purchased items
GROUP BY ub.item_id, ic.category_name
ORDER BY recommended_by_users DESC;
```

**Business value**: Recommends item_id=1 (Electronics) to user 1001, recommended by user 1004, achieving precise collaborative filtering.

### Scenario 3: A/B Test Effectiveness Analysis

#### Why Do This Analysis?

Product teams face dual challenges of precision and efficiency when conducting A/B testing:

* **Sample Contamination**: Need to ensure no crossover between experiment and control group users to avoid skewed test results
* **Conversion Path Analysis**: Analyze not just final conversion rates but also differences in user behavior paths across experiment versions
* **Statistical Significance**: Need precise counts of users and conversions in each group to ensure credible test results
* **Experiment Effectiveness Evaluation**: Quickly identify which user segments are more sensitive to experiment changes
* **Subsequent Decision Support**: Provide data basis for product iteration and full rollout

BITMAP functions can precisely track the behavioral performance of experiment users, avoiding approximation errors in traditional methods.

#### 3.1 Table Preparation

```sql
-- Create A/B test assignment table
CREATE TABLE IF NOT EXISTS ab_test_assignments (
    user_id BIGINT,
    experiment_id STRING,
    group_name STRING,
    assignment_date DATE
);

-- Create conversion events table
CREATE TABLE IF NOT EXISTS conversion_events (
    user_id BIGINT,
    experiment_id STRING,
    event_type STRING,
    event_date DATE,
    event_value DECIMAL(10,2)
);

-- Insert sample data
INSERT INTO ab_test_assignments VALUES
(1001, 'homepage_redesign_2024', 'control', DATE('2024-01-01')),
(1002, 'homepage_redesign_2024', 'variant_a', DATE('2024-01-01')),
(1003, 'homepage_redesign_2024', 'control', DATE('2024-01-01')),
(1004, 'homepage_redesign_2024', 'variant_a', DATE('2024-01-01')),
(1005, 'homepage_redesign_2024', 'control', DATE('2024-01-01')),
(1006, 'homepage_redesign_2024', 'variant_a', DATE('2024-01-01')),
(1007, 'homepage_redesign_2024', 'control', DATE('2024-01-01')),
(1008, 'homepage_redesign_2024', 'variant_a', DATE('2024-01-01'));

INSERT INTO conversion_events VALUES
(1001, 'homepage_redesign_2024', 'purchase', DATE('2024-01-15'), 99.99),
(1002, 'homepage_redesign_2024', 'signup', DATE('2024-01-12'), 0),
(1004, 'homepage_redesign_2024', 'purchase', DATE('2024-01-18'), 149.99),
(1006, 'homepage_redesign_2024', 'signup', DATE('2024-01-14'), 0),
(1007, 'homepage_redesign_2024', 'signup', DATE('2024-01-16'), 0),
(1008, 'homepage_redesign_2024', 'purchase', DATE('2024-01-20'), 199.99);
```

#### 3.2 A/B Test Conversion Analysis

```sql
-- A/B test group conversion effectiveness comparison
WITH experiment_groups AS (
  SELECT 
    group_name,
    group_bitmap_state(user_id) as users
  FROM ab_test_assignments
  WHERE experiment_id = 'homepage_redesign_2024'
  GROUP BY group_name
),
conversion_analysis AS (
  SELECT 
    ata.group_name,
    ce.event_type,
    group_bitmap_state(ce.user_id) as converted_users
  FROM ab_test_assignments ata
  JOIN conversion_events ce ON ata.user_id = ce.user_id 
    AND ata.experiment_id = ce.experiment_id
  WHERE ata.experiment_id = 'homepage_redesign_2024'
    AND ce.event_date BETWEEN '2024-01-01' AND '2024-01-31'
  GROUP BY ata.group_name, ce.event_type
)
SELECT 
  eg.group_name,
  ca.event_type,
  bitmap_cardinality(eg.users) as total_users,
  COALESCE(bitmap_and_cardinality(eg.users, ca.converted_users), 0) as converted_users,
  ROUND(COALESCE(bitmap_and_cardinality(eg.users, ca.converted_users), 0) * 100.0 / 
        bitmap_cardinality(eg.users), 2) as conversion_rate,
  bitmap_to_array(COALESCE(bitmap_and(eg.users, ca.converted_users), NULL)) as converted_user_ids
FROM experiment_groups eg
LEFT JOIN conversion_analysis ca ON eg.group_name = ca.group_name
ORDER BY eg.group_name, ca.event_type;
```

**Analysis results**:

* Control group: 4 users, 25% purchase conversion, 25% signup conversion
* Variant_A group: 4 users, 50% purchase conversion, 50% signup conversion
* The experiment group significantly outperformed the control group

#### 3.3 User Behavior Path Analysis

```sql
-- Analyze behavior path differences between groups
WITH group_behaviors AS (
  SELECT 
    ata.group_name,
    ce.event_type,
    group_bitmap_state(ce.user_id) as users_with_event
  FROM ab_test_assignments ata
  JOIN conversion_events ce ON ata.user_id = ce.user_id
  WHERE ata.experiment_id = 'homepage_redesign_2024'
  GROUP BY ata.group_name, ce.event_type
)
SELECT 
  gb1.group_name,
  gb1.event_type as first_event,
  gb2.event_type as second_event,
  bitmap_and_cardinality(gb1.users_with_event, gb2.users_with_event) as users_both_events,
  ROUND(bitmap_and_cardinality(gb1.users_with_event, gb2.users_with_event) * 100.0 / 
        bitmap_cardinality(gb1.users_with_event), 2) as conversion_rate_to_second
FROM group_behaviors gb1
JOIN group_behaviors gb2 ON gb1.group_name = gb2.group_name 
  AND gb1.event_type != gb2.event_type
WHERE gb1.event_type = 'signup' AND gb2.event_type = 'purchase'
ORDER BY gb1.group_name;
```

**Analysis result**: In the data, signup and purchase users do not overlap, conversion rate is 0%, consistent with actual data.

### Scenario 4: User Lifecycle and Retention Analysis

#### Why Do This Analysis?

Operations teams need deep understanding of the complete user lifecycle from registration to payment:

* **Conversion Funnel Optimization**: Identify key churn points and reasons for low conversion rates
* **Channel Quality Assessment**: Differences in user quality from different acquisition channels to guide marketing budget allocation
* **Product Improvement Direction**: Discover product experience pain points through behavior path analysis
* **Operational Strategy Development**: Develop personalized operational strategies for users at different lifecycle stages
* **Predictive Model Building**: Predict new user lifetime value based on historical data
* **Cost-Benefit Analysis**: Calculate ROI between acquisition cost and user lifetime value

BITMAP can precisely track each user's transition through lifecycle stages, supporting refined operations.

#### 4.1 Table Preparation

```sql
-- Create user registration table
CREATE TABLE IF NOT EXISTS user_registrations (
    user_id BIGINT,
    registration_date DATE,
    source_channel STRING
);

-- Create user activation table
CREATE TABLE IF NOT EXISTS user_activations (
    user_id BIGINT,
    activation_date DATE,
    activation_action STRING
);

-- Create user retention table  
CREATE TABLE IF NOT EXISTS user_retention (
    user_id BIGINT,
    retention_date DATE,
    retention_day INT  -- Day N retention
);

-- Create payment conversion table
CREATE TABLE IF NOT EXISTS user_payments (
    user_id BIGINT,
    payment_date DATE,
    amount DECIMAL(10,2)
);

-- Insert sample data
INSERT INTO user_registrations VALUES
(1001, DATE('2024-01-01'), 'facebook'),
(1002, DATE('2024-01-01'), 'google'),
(1003, DATE('2024-01-02'), 'tiktok'),
(1004, DATE('2024-01-02'), 'facebook'),
(1005, DATE('2024-01-03'), 'google'),
(1006, DATE('2024-01-03'), 'tiktok'),
(1007, DATE('2024-01-04'), 'facebook'),
(1008, DATE('2024-01-04'), 'google');

INSERT INTO user_activations VALUES
(1001, DATE('2024-01-01'), 'complete_profile'),
(1002, DATE('2024-01-02'), 'first_post'),
(1004, DATE('2024-01-02'), 'complete_profile'),
(1005, DATE('2024-01-04'), 'first_post'),
(1007, DATE('2024-01-05'), 'complete_profile');

INSERT INTO user_retention VALUES
(1001, DATE('2024-01-08'), 7),
(1002, DATE('2024-01-08'), 7),
(1004, DATE('2024-01-09'), 7),
(1005, DATE('2024-01-10'), 7);

INSERT INTO user_payments VALUES
(1001, DATE('2024-01-15'), 99.99),
(1004, DATE('2024-01-18'), 149.99);
```

#### 4.2 User Lifecycle Funnel Analysis

```sql
-- Conversion funnel across user lifecycle stages
WITH lifecycle_stages AS (
  SELECT 'registered' as stage, group_bitmap_state(user_id) as users
  FROM user_registrations 
  WHERE registration_date >= '2024-01-01'
  
  UNION ALL
  
  SELECT 'activated' as stage, group_bitmap_state(user_id) as users
  FROM user_activations
  WHERE activation_date >= '2024-01-01'
  
  UNION ALL
  
  SELECT 'retained_7d' as stage, group_bitmap_state(user_id) as users  
  FROM user_retention
  WHERE retention_date >= '2024-01-01' AND retention_day = 7
  
  UNION ALL
  
  SELECT 'paid' as stage, group_bitmap_state(user_id) as users
  FROM user_payments
  WHERE payment_date >= '2024-01-01'
),
stage_order AS (
  SELECT stage, users,
    CASE stage 
      WHEN 'registered' THEN 1
      WHEN 'activated' THEN 2  
      WHEN 'retained_7d' THEN 3
      WHEN 'paid' THEN 4
    END as order_num
  FROM lifecycle_stages
),
registered_users AS (
  SELECT users as all_registered FROM stage_order WHERE stage = 'registered'
)
SELECT 
  so.stage,
  bitmap_cardinality(so.users) as stage_users,
  -- Conversion rate relative to previous stage
  LAG(bitmap_cardinality(so.users)) OVER (ORDER BY so.order_num) as prev_stage_users,
  CASE 
    WHEN LAG(bitmap_cardinality(so.users)) OVER (ORDER BY so.order_num) IS NOT NULL
    THEN ROUND(bitmap_cardinality(so.users) * 100.0 / 
               LAG(bitmap_cardinality(so.users)) OVER (ORDER BY so.order_num), 2)
    ELSE 100.0
  END as conversion_from_prev,
  -- Overall conversion rate relative to registered users  
  ROUND(bitmap_cardinality(so.users) * 100.0 / 
        bitmap_cardinality((SELECT all_registered FROM registered_users)), 2) as conversion_from_registered,
  -- Display specific user IDs
  bitmap_to_array(so.users) as user_ids
FROM stage_order so
ORDER BY so.order_num;
```

**Funnel analysis results**:

* Registration -> Activation: 62.5% conversion rate
* Activation -> Retention: 80% conversion rate
* Retention -> Payment: 50% conversion rate
* Overall registration to payment conversion rate: 25%

#### 4.3 Channel Quality Comparison Analysis

```sql
-- User quality comparison across different channels (lifecycle completion)
WITH channel_registered AS (
  SELECT 
    source_channel,
    group_bitmap_state(user_id) as registered_users
  FROM user_registrations
  WHERE registration_date >= '2024-01-01'
  GROUP BY source_channel
),
channel_activated AS (
  SELECT 
    ur.source_channel,
    group_bitmap_state(ua.user_id) as activated_users
  FROM user_registrations ur
  JOIN user_activations ua ON ur.user_id = ua.user_id
  WHERE ur.registration_date >= '2024-01-01'
  GROUP BY ur.source_channel
),
channel_retained AS (
  SELECT 
    ur.source_channel,
    group_bitmap_state(urt.user_id) as retained_users
  FROM user_registrations ur
  JOIN user_retention urt ON ur.user_id = urt.user_id
  WHERE ur.registration_date >= '2024-01-01' AND urt.retention_day = 7
  GROUP BY ur.source_channel
),
channel_paid AS (
  SELECT 
    ur.source_channel,
    group_bitmap_state(up.user_id) as paid_users
  FROM user_registrations ur
  JOIN user_payments up ON ur.user_id = up.user_id
  WHERE ur.registration_date >= '2024-01-01'
  GROUP BY ur.source_channel
)
SELECT 
  cr.source_channel,
  bitmap_cardinality(cr.registered_users) as registered_count,
  COALESCE(bitmap_cardinality(ca.activated_users), 0) as activated_count,
  COALESCE(bitmap_cardinality(crt.retained_users), 0) as retained_count,
  COALESCE(bitmap_cardinality(cp.paid_users), 0) as paid_count,
  ROUND(COALESCE(bitmap_cardinality(ca.activated_users), 0) * 100.0 / 
        bitmap_cardinality(cr.registered_users), 2) as activation_rate,
  ROUND(COALESCE(bitmap_cardinality(crt.retained_users), 0) * 100.0 / 
        bitmap_cardinality(cr.registered_users), 2) as retention_rate,
  ROUND(COALESCE(bitmap_cardinality(cp.paid_users), 0) * 100.0 / 
        bitmap_cardinality(cr.registered_users), 2) as payment_rate
FROM channel_registered cr
LEFT JOIN channel_activated ca ON cr.source_channel = ca.source_channel
LEFT JOIN channel_retained crt ON cr.source_channel = crt.source_channel  
LEFT JOIN channel_paid cp ON cr.source_channel = cp.source_channel
ORDER BY payment_rate DESC, retention_rate DESC;
```

**Channel quality comparison**: Facebook channel has the best quality (66.67% payment rate), TikTok channel has the lowest quality (0% payment rate).

### Scenario 5: Permission Management and User Groups

#### Why Do This Analysis?

Enterprise permission management systems face dual challenges of complexity and performance:

* **Permission Verification Efficiency**: Traditional table join queries for permission checking are inefficient and cannot support high-concurrency access
* **Permission Combination Complexity**: Users may have multiple roles simultaneously, requiring fast computation of permission unions
* **Audit and Compliance**: Need to quickly query who has specific permissions to support security audit requirements
* **Permission Analysis Statistics**: Analyze permission distribution across departments and roles to discover permission design issues
* **Dynamic Permission Management**: Support dynamic permission assignment and revocation with real-time effect
* **Scalability Requirements**: Permission system needs to support rapid expansion as organizational structure changes

Using bitwise operations and BITMAP can convert complex permission computations into efficient bit operations, dramatically improving system performance.

#### 5.1 Table Preparation

```sql
-- Create permission definition table
CREATE TABLE IF NOT EXISTS permissions (
    permission_id INT,
    permission_name STRING,
    permission_bit INT  -- Power of 2: 1,2,4,8,16,32...
);

-- Create role table
CREATE TABLE IF NOT EXISTS roles (
    role_id INT,
    role_name STRING,
    permission_mask BIGINT  -- Permission bitmask
);

-- Create user-role association table
CREATE TABLE IF NOT EXISTS user_roles (
    user_id BIGINT,
    role_id INT,
    assigned_date DATE
);

-- Create user table
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT,
    username STRING,
    department STRING
);

-- Insert sample data
INSERT INTO permissions VALUES
(1, 'read', 1),      -- 2^0 = 1
(2, 'write', 2),     -- 2^1 = 2  
(3, 'delete', 4),    -- 2^2 = 4
(4, 'admin', 8),     -- 2^3 = 8
(5, 'audit', 16);    -- 2^4 = 16

INSERT INTO roles VALUES
(1, 'viewer', 1),        -- Read-only permission
(2, 'editor', 3),        -- Read-write permission (1+2)
(3, 'manager', 7),       -- Read-write-delete permission (1+2+4)
(4, 'admin', 15),        -- Admin permission (1+2+4+8)
(5, 'auditor', 17);      -- Audit permission (1+16)

INSERT INTO users VALUES
(1001, 'alice', 'engineering'),
(1002, 'bob', 'marketing'),
(1003, 'charlie', 'finance'),
(1004, 'diana', 'engineering'),
(1005, 'eve', 'hr');

INSERT INTO user_roles VALUES
(1001, 4, DATE('2024-01-01')),  -- alice is admin
(1002, 2, DATE('2024-01-01')),  -- bob is editor
(1003, 5, DATE('2024-01-01')),  -- charlie is auditor
(1004, 3, DATE('2024-01-01')),  -- diana is manager
(1005, 1, DATE('2024-01-01'));  -- eve is viewer
```

#### 5.2 User Permission Analysis

```sql
-- Analyze specific user permissions
WITH user_permissions AS (
  SELECT 
    u.user_id,
    u.username,
    u.department,
    bit_or(r.permission_mask) as total_permissions
  FROM users u
  JOIN user_roles ur ON u.user_id = ur.user_id  
  JOIN roles r ON ur.role_id = r.role_id
  GROUP BY u.user_id, u.username, u.department
)
SELECT 
  user_id,
  username,
  department,
  total_permissions,
  bit_count(total_permissions) as permission_count,
  CASE WHEN total_permissions & 1 = 1 THEN 'Y' ELSE 'N' END as can_read,
  CASE WHEN total_permissions & 2 = 2 THEN 'Y' ELSE 'N' END as can_write,
  CASE WHEN total_permissions & 4 = 4 THEN 'Y' ELSE 'N' END as can_delete,
  CASE WHEN total_permissions & 8 = 8 THEN 'Y' ELSE 'N' END as can_admin,
  CASE WHEN total_permissions & 16 = 16 THEN 'Y' ELSE 'N' END as can_audit,
  CASE 
    WHEN total_permissions & 8 = 8 THEN 'admin'
    WHEN total_permissions & 4 = 4 THEN 'manager'  
    WHEN total_permissions & 2 = 2 THEN 'editor'
    WHEN total_permissions & 1 = 1 THEN 'viewer'
    ELSE 'no_access'
  END as role_level
FROM user_permissions
ORDER BY total_permissions DESC;
```

**Permission analysis results**: Alice (admin permission), Bob (editor permission), Charlie (auditor permission) -- user permission assignments are reasonable.

#### 5.3 Department Permission Distribution Analysis

```sql
-- Analyze permission distribution across departments
WITH dept_permissions AS (
  SELECT 
    u.department,
    bit_or(r.permission_mask) as dept_permissions,
    group_bitmap_state(u.user_id) as dept_users
  FROM users u
  JOIN user_roles ur ON u.user_id = ur.user_id  
  JOIN roles r ON ur.role_id = r.role_id
  GROUP BY u.department
),
permission_analysis AS (
  SELECT 
    department,
    dept_permissions,
    bitmap_cardinality(dept_users) as user_count,
    CASE WHEN dept_permissions & 1 = 1 THEN bitmap_cardinality(dept_users) ELSE 0 END as users_with_read,
    CASE WHEN dept_permissions & 2 = 2 THEN bitmap_cardinality(dept_users) ELSE 0 END as users_with_write,
    CASE WHEN dept_permissions & 4 = 4 THEN bitmap_cardinality(dept_users) ELSE 0 END as users_with_delete,
    CASE WHEN dept_permissions & 8 = 8 THEN bitmap_cardinality(dept_users) ELSE 0 END as users_with_admin,
    CASE WHEN dept_permissions & 16 = 16 THEN bitmap_cardinality(dept_users) ELSE 0 END as users_with_audit
  FROM dept_permissions
)
SELECT 
  department,
  user_count,
  dept_permissions,
  users_with_read,
  users_with_write,
  users_with_delete,
  users_with_admin,
  users_with_audit,
  CASE 
    WHEN dept_permissions & 8 = 8 THEN 'high_privilege'
    WHEN dept_permissions & 4 = 4 THEN 'medium_privilege'
    WHEN dept_permissions & 2 = 2 THEN 'basic_privilege'
    ELSE 'read_only'
  END as privilege_level
FROM permission_analysis
ORDER BY dept_permissions DESC;
```

**Department permission distribution**: Engineering department has high privilege level, Finance department has read-only permission with audit capability -- permission distribution is reasonable.

### Scenario 6: Large-Scale Data Pagination and Sampling

#### Why Do This Analysis?

Data science teams face performance and resource constraints when processing massive user data:

* **Query Performance Optimization**: Full queries on millions of users can cause system timeouts or resource exhaustion
* **Data Sampling Requirements**: Machine learning training requires high-quality sample data; simple random sampling is insufficient
* **Pagination Display Requirements**: Frontend systems need paginated user lists with fast response times
* **Memory Usage Control**: Avoid memory overflow from large result sets
* **Concurrent Query Support**: When multiple data analysts query simultaneously, individual query resource usage needs to be controlled
* **Data Exploration Efficiency**: Quickly obtain data subsets for exploratory analysis

BITMAP's pagination and sampling features can efficiently process large-scale user data, supporting flexible data exploration needs.

#### 6.1 Table Preparation

```sql
-- Create large-scale user activity table
CREATE TABLE IF NOT EXISTS user_activity_large (
    user_id BIGINT,
    activity_date DATE,
    activity_score INT
) PARTITIONED BY (activity_date);

-- Insert sample data (simulating large user base)
INSERT INTO user_activity_large 
SELECT 
  1000 + row_number() OVER() as user_id,
  DATE('2024-01-15') as activity_date,
  CAST(RAND() * 100 AS INT) as activity_score
FROM (
  SELECT 1 as dummy FROM VALUES (1),(2),(3),(4),(5),(6),(7),(8),(9),(10) t1
  CROSS JOIN (SELECT 1 as dummy FROM VALUES (1),(2),(3),(4),(5),(6),(7),(8),(9),(10) t2) 
  CROSS JOIN (SELECT 1 as dummy FROM VALUES (1),(2),(3),(4),(5),(6),(7),(8),(9),(10) t3)
) t;

-- Add more dates of data
INSERT INTO user_activity_large 
SELECT 
  1500 + row_number() OVER() as user_id,
  DATE('2024-01-16') as activity_date,
  CAST(RAND() * 100 AS INT) as activity_score
FROM (
  SELECT 1 as dummy FROM VALUES (1),(2),(3),(4),(5),(6),(7),(8),(9),(10) t1
  CROSS JOIN (SELECT 1 as dummy FROM VALUES (1),(2),(3),(4),(5),(6),(7),(8),(9),(10) t2) 
  CROSS JOIN (SELECT 1 as dummy FROM VALUES (1),(2),(3),(4),(5),(6),(7),(8),(9),(10) t3)
) t;
```

#### 6.2 Efficient User Pagination

```sql
-- Efficient user pagination implementation
WITH active_users AS (
  SELECT group_bitmap_state(user_id) as all_users
  FROM user_activity_large 
  WHERE activity_date >= '2024-01-01'
    AND activity_score >= 50  -- High-activity users
),
pagination_base AS (
  SELECT 
    all_users,
    bitmap_cardinality(all_users) as total_users,
    CEIL(bitmap_cardinality(all_users) / 100.0) as total_pages
  FROM active_users
)
-- Simplified pagination implementation
SELECT 
  1 as page_num,
  100 as page_size,
  bitmap_cardinality(pb.all_users) as total_users_available,
  size(bitmap_to_array(bitmap_subset_limit(pb.all_users, 0, 100))) as actual_users_in_page,
  bitmap_to_array(bitmap_subset_limit(pb.all_users, 0, 100)) as user_ids
FROM pagination_base pb

UNION ALL

SELECT 
  2 as page_num,
  100 as page_size,
  bitmap_cardinality(pb.all_users) as total_users_available,
  size(bitmap_to_array(bitmap_subset_limit(pb.all_users, 100, 100))) as actual_users_in_page,
  bitmap_to_array(bitmap_subset_limit(pb.all_users, 100, 100)) as user_ids
FROM pagination_base pb

UNION ALL

SELECT 
  3 as page_num,
  100 as page_size,
  bitmap_cardinality(pb.all_users) as total_users_available,
  size(bitmap_to_array(bitmap_subset_limit(pb.all_users, 200, 100))) as actual_users_in_page,
  bitmap_to_array(bitmap_subset_limit(pb.all_users, 200, 100)) as user_ids
FROM pagination_base pb

ORDER BY page_num;
```

#### 6.3 Random User Sampling

```sql
-- Random user sampling analysis
WITH active_users AS (
  SELECT group_bitmap_state(user_id) as all_users
  FROM user_activity_large 
  WHERE activity_date >= '2024-01-01'
),
sampling_analysis AS (
  SELECT 
    bitmap_cardinality(all_users) as total_users,
    bitmap_subset_limit(all_users, 0, 100) as random_sample_users,
    bitmap_subset_limit(all_users, 100, 100) as another_sample_users
  FROM active_users
)
SELECT 
  total_users,
  size(bitmap_to_array(random_sample_users)) as sample_size,
  CASE WHEN total_users >= 10 
       THEN bitmap_to_array(bitmap_subset_limit(random_sample_users, 0, 10))
       ELSE bitmap_to_array(random_sample_users) END as sample_preview  -- Only show first 10 to avoid excessive length
FROM sampling_analysis
ORDER BY total_users DESC;
```

***

## BITMAP Function Technical Guide

### Core Function Categories

#### 1. Build and Conversion Functions

| Function | Purpose | Correct Syntax | Notes |
| ---------------------- | ------- | ---------------------------------------------------- | ------ |
| `bitmap_build()` | Build bitmap from array | `SELECT bitmap_to_array(bitmap_build(array(1,2,3)))` | Does not support empty arrays |
| `bitmap_to_array()` | Convert bitmap to array for display | `SELECT bitmap_to_array(bitmap_obj)` | Required for result display |
| `bitmap_cardinality()` | Count number of elements | `SELECT bitmap_cardinality(bitmap_obj)` | Efficient counting |
| `binary_to_bitmap()` | Convert binary to bitmap | `SELECT binary_to_bitmap(binary_data)` | Deserialization recovery |
| `bitmap_to_binary()` | Convert bitmap to binary | `SELECT bitmap_to_binary(bitmap_obj)` | Serialization storage |

#### 2. Set Operation Functions

| Function | Math Concept | Business Application | Correct Syntax |
| ----------------- | ------ | ------ | --------------------------------------------------------- |
| `bitmap_and()` | Intersection A intersect B | User overlap analysis | `SELECT bitmap_to_array(bitmap_and(bitmap1, bitmap2))` |
| `bitmap_or()` | Union A union B | User dedup merge | `SELECT bitmap_to_array(bitmap_or(bitmap1, bitmap2))` |
| `bitmap_xor()` | Symmetric difference A xor B | Different user identification | `SELECT bitmap_to_array(bitmap_xor(bitmap1, bitmap2))` |
| `bitmap_andnot()` | Difference A - B | Churned user analysis | `SELECT bitmap_to_array(bitmap_andnot(bitmap1, bitmap2))` |

#### 3. Efficient Cardinality Computation Functions (Recommended Priority)

| Function | Performance Advantage | Applicable Scenario |
| ----------------------------- | -------- | --------- |
| `bitmap_and_cardinality()` | No need to build complete intersection | Only care about overlap user count |
| `bitmap_or_cardinality()` | No need to build complete union | Only care about total user count |
| `bitmap_xor_cardinality()` | No need to build complete symmetric diff | Only care about different user count |
| `bitmap_andnot_cardinality()` | No need to build complete difference | Only care about unique user count |

#### 4. Aggregate Functions

| Function | Return Type | Use Case | Correct Syntax |
| ---------------------- | --------- | ------------ | --------------------------------------------------------------------------------- |
| `group_bitmap()` | INT (hash value) | Fast dedup counting | `SELECT group_bitmap(column) FROM table GROUP BY category` |
| `group_bitmap_state()` | bitmap object | Subsequent bitmap operations needed | `SELECT bitmap_to_array(group_bitmap_state(column)) FROM table GROUP BY category` |

#### 5. Advanced Functions

| Function | Purpose | Syntax Example |
| -------------------------- | ------- | -------------------------------------------------------------------------- |
| `bitmap_subset_limit()` | Pagination / Limited sampling | `SELECT bitmap_to_array(bitmap_subset_limit(bitmap, 0, 100))` |
| `bitmap_subset_in_range()` | Range sampling | `SELECT bitmap_to_array(bitmap_subset_in_range(bitmap, min_val, max_val))` |
| `bitmap_min()` | Get minimum value | `SELECT bitmap_min(bitmap)` |
| `bitmap_max()` | Get maximum value | `SELECT bitmap_max(bitmap)` |
| `bitmap_contains()` | Contains check | `SELECT bitmap_contains(bitmap, value)` |

#### 6. Bitwise Operation Functions

| Function | Purpose | Application Scenario |
| ------------- | ---- | ---- |
| `bit_or()` | Bitwise OR | Permission merging |
| `bit_count()` | Bit count | Permission statistics |
| `&` operator | Bitwise AND | Permission verification |

***

## Common Errors and Solutions

### 1. Display Issues

```sql
-- ❌ Error: Client cannot display bitmap type
SELECT bitmap_build(array(1,2,3))

-- ✅ Correct: Must convert to array for display
SELECT bitmap_to_array(bitmap_build(array(1,2,3)))
```

### 2. Empty Set Handling

```sql
-- ❌ Error: Will cause syntax error
SELECT bitmap_build(array())

-- ✅ Correct: Use NULL or conditional checks
SELECT CASE 
  WHEN array_size(my_array) > 0
  THEN bitmap_build(my_array)
  ELSE NULL
END
```

### 3. Function Name Confusion

```sql
-- ❌ Error: bitmap_union function does not exist
SELECT bitmap_union(bitmap1, bitmap2)

-- ✅ Correct: Use bitmap_or for union operation
SELECT bitmap_or(bitmap1, bitmap2)
```

### 4. Aggregate Function Return Type Confusion

```sql
-- ❌ Error: group_bitmap returns INT, cannot convert to array
SELECT bitmap_to_array(group_bitmap(column))

-- ✅ Correct: group_bitmap_state returns bitmap type
SELECT bitmap_to_array(group_bitmap_state(column))
```

### 5. Column Name Ambiguity Issues

```sql
-- ❌ Error: Ambiguous column name after JOIN
SELECT user_id FROM table1 t1 JOIN table2 t2 ON t1.id = t2.id

-- ✅ Correct: Explicitly specify table alias
SELECT t1.user_id FROM table1 t1 JOIN table2 t2 ON t1.id = t2.id
```

### 6. Array Access Syntax Issues

```sql
-- ❌ Error: Array access may be out of bounds or incorrect syntax
SELECT array_col[size(array_col)] 

-- ✅ Correct: Use 0-based indexing with boundary checks
SELECT CASE 
  WHEN size(array_col) > 0 
  THEN array_col[size(array_col)-1] 
  ELSE NULL 
END
```

### 7. CTE Duplicate Reference Issues

```sql
-- ❌ Potentially problematic: Referencing the same CTE multiple times in UNION ALL
WITH base_data AS (SELECT ...)
SELECT ... FROM base_data
UNION ALL
SELECT ... FROM base_data  -- May cause duplicate results

-- ✅ Suggestion: Simplify query structure or use temporary tables
```

***

## Optimization Suggestions

### 1. Performance Optimization

* **Prioritize cardinality computation functions**: When only counts are needed, use `bitmap_xxx_cardinality()` instead of building then computing
* **Use aggregation wisely**: Use `group_bitmap_state()` for batch processing instead of multiple individual queries
* **Avoid intermediate results**: Compute final results directly to reduce temporary bitmap object creation

### 2. Memory Optimization

* **Convert for display promptly**: Bitmap objects are only for computation; convert to arrays immediately for display
* **Avoid unnecessary complete set construction**: Use cardinality computation when possible instead of building complete bitmaps
* **Paginate for large data**: Use `bitmap_subset_limit()` for pagination to avoid loading all data at once

### 3. Business Logic Optimization

* **Design bit permissions reasonably**: Permission bitmask design should consider future extensibility
* **User grouping strategy**: Choose appropriate bitmap grouping dimensions based on business needs
* **Sampling strategy**: Use sampling wisely for big data analysis to reduce computation costs

### 4. SQL Writing Best Practices

* **Explicit column names**: Must use table aliases in JOIN queries to avoid ambiguity
* **Boundary checks**: Perform length checks before array access
* **Simplify CTEs**: Avoid complex CTE nesting and duplicate references

***

## Best Practices Checklist

### Development Phase

* [ ] All bitmap results use `bitmap_to_array()` for display conversion
* [ ] Prioritize `bitmap_xxx_cardinality()` functions for count calculations
* [ ] Correctly distinguish between `group_bitmap()` and `group_bitmap_state()` use cases
* [ ] Table creation statements include necessary partition and index designs
* [ ] Sample data is sufficient to validate business logic
* [ ] JOIN queries use explicit table aliases to avoid column name ambiguity
* [ ] Array access performs boundary checks

### Query Optimization

* [ ] Use CTEs for complex analysis to improve readability
* [ ] Consider pagination and sampling for large data queries
* [ ] Set operations prioritize whether only cardinality is needed
* [ ] Avoid complex bitmap operations in WHERE conditions
* [ ] Avoid overly complex CTE nesting structures

### Production Deployment

* [ ] Verify all SQL executes correctly in the Singdata environment
* [ ] Establish appropriate monitoring and alerting mechanisms
* [ ] Design reasonable data retention and cleanup strategies
* [ ] Document business logic and technical implementation

***

## Environment Cleanup

After completing all practice scenarios, it is recommended to clean up the test environment to free up resources.

### Quick Cleanup Script

```sql
-- Clean up all test tables
DROP TABLE IF EXISTS user_activity;
DROP TABLE IF EXISTS user_behavior;
DROP TABLE IF EXISTS item_category;
DROP TABLE IF EXISTS ab_test_assignments;
DROP TABLE IF EXISTS conversion_events;
DROP TABLE IF EXISTS user_registrations;
DROP TABLE IF EXISTS user_activations;
DROP TABLE IF EXISTS user_retention;
DROP TABLE IF EXISTS user_payments;
DROP TABLE IF EXISTS permissions;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS user_roles;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS user_activity_large;
```

### Cleanup Confirmation

```sql
-- Verify cleanup results
SHOW TABLES;
```

***

## Operating Environment Requirements

### Function Compatibility

The core functions used in this guide and their requirements:

#### BITMAP Core Functions

* `bitmap_build()` - Build bitmap
* `bitmap_to_array()` - Convert bitmap to array (required, for result display)
* `bitmap_cardinality()` - Compute cardinality
* `group_bitmap_state()` - Group aggregate bitmap

#### Set Operation Functions

* `bitmap_and()` / `bitmap_and_cardinality()` - Intersection operations
* `bitmap_or()` / `bitmap_or_cardinality()` - Union operations
* `bitmap_andnot()` / `bitmap_andnot_cardinality()` - Difference operations
* `bitmap_xor()` / `bitmap_xor_cardinality()` - Symmetric difference operations

#### Bitwise Operation Functions

* `bit_or()` - Bitwise OR
* `bit_count()` - Bit count
* `&` - Bitwise AND operator

#### Advanced Functions

* `bitmap_subset_limit()` - Pagination sampling
* `bitmap_subset_in_range()` - Range sampling
* `bitmap_min()` - Get minimum value
* `bitmap_contains()` - Contains check

#### Helper Functions

* `size()` - Array length
* `RAND()` - Random number generation
* `GREATEST()` / `LEAST()` - Get maximum/minimum value

### Data Type Requirements

* **User ID**: Recommend BIGINT type to support large-scale users
* **Date type**: Use DATE type, insert using `DATE('2024-01-15')` format
* **Timestamp type**: Use TIMESTAMP type
* **Permission mask**: Use BIGINT type, supports 64-bit permissions

***

## Summary and Best Practices

### Core Value Summary

Through the 6 practice scenarios in this guide, we have demonstrated the powerful capabilities of Singdata Lakehouse BITMAP functions in user behavior analysis and precision marketing:

#### Business Value Realized

1. **Multi-Channel Marketing Optimization**: Accurately compute user overlap, avoid duplicate placements, improve ROI
2. **Personalized Recommendation Improvement**: Achieve precise recommendations based on user interest similarity, improve conversion rates
3. **A/B Testing Precision**: Eliminate sample bias and obtain credible experiment results
4. **User Lifecycle Insights**: Identify key churn points, optimize product experience and operational strategies
5. **Permission Management Efficiency**: Bitwise operations achieve millisecond-level permission verification, supporting high-concurrency systems
6. **Big Data Processing Optimization**: Efficient pagination and sampling, supporting agile analysis of massive data

#### Technical Advantages Summary

* **Memory efficiency**: BITMAP storage saves over 90% storage space compared to traditional arrays
* **Computation performance**: Set operation performance improves 10-100x over traditional SQL JOINs
* **Accuracy**: Avoids error issues of probabilistic algorithms like HyperLogLog
* **Scalability**: Supports real-time analysis of millions to tens of millions of users

### Key Success Factors

#### 1. Function Usage Standards

* All BITMAP results must use `bitmap_to_array()` for display conversion
* Prioritize `bitmap_xxx_cardinality()` functions, avoid building complete sets
* Distinguish between `group_bitmap()` (returns INT) and `group_bitmap_state()` (returns bitmap)
* Use NULL for empty sets, do not use `bitmap_build(array())`
* Use correct type conversion formats for datetime data (`DATE()`, `TIMESTAMP`)

#### 2. SQL Writing Best Practices

* Use CTEs to improve readability of complex queries
* Use partitioning wisely to improve query performance
* Add `IF NOT EXISTS` when creating tables to avoid duplicate creation
* Use `DATE()` and `TIMESTAMP` keywords for datetime data insertion
* Use explicit table aliases in JOIN queries to avoid column name ambiguity
* Perform boundary checks before array access

#### 3. Business Application Strategy

* First understand business needs and pain points, then choose appropriate technical solutions
* Start with small-scale data validation, gradually expand to production environments
* Establish monitoring and alerting mechanisms to ensure stable system operation
* Regularly analyze query performance and continuously optimize SQL statements

### Continuous Improvement Suggestions

#### Short-Term Optimization

* Adjust numeric ranges in examples based on actual business data volumes
* Expand analysis dimensions based on specific business scenarios
* Establish standardized SQL template libraries to improve development efficiency

#### Long-Term Development

* Explore combined applications of BITMAP with machine learning models
* Research more complex user profiling and behavior prediction scenarios
* Build real-time data analysis platforms based on BITMAP

### Learning Path Suggestions

1. **Foundation Phase**: Master BITMAP basic function usage (Scenarios 1-2)
2. **Application Phase**: Practice scenarios close to your business (Scenarios 3-4)
3. **Optimization Phase**: Deep dive into performance optimization and error handling techniques (Scenario 5)
4. **Innovation Phase**: Creatively apply BITMAP functions based on specific business needs (Scenario 6)

### Production Deployment Suggestions

**Deployment Preparation**:

* All scenarios have been thoroughly tested and can be directly referenced
* Adjust partition strategies and index designs based on actual data volumes
* Establish comprehensive monitoring and alerting mechanisms

**Monitoring Strategy**:

* Monitor BITMAP query execution time and resource usage
* Establish real-time monitoring of key business metrics
* Regularly analyze query performance and continuously optimize

**Scaling Suggestions**:

* Adjust partition strategies based on business growth
* Consider building a standard library of BITMAP functions
* Train team members on BITMAP best practices

Following the best practices in this guide will help you fully leverage the powerful capabilities of Singdata Lakehouse BITMAP functions, build efficient and stable data analysis systems, and provide strong data support for business decisions!

## References

[Bitmap Functions](bitmap_function.md)

[Bit Functions](bit_function.md)

*Note: This guide is based on test results from the Singdata Lakehouse version as of May 2025. Subsequent versions may vary. Please regularly check the official documentation for the latest information.*
