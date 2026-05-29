# Overview

TPC-DS (Transaction Processing Performance Council - Decision Support) is a benchmark standard released by the Transaction Processing Performance Council (TPC) aimed at evaluating the performance of Decision Support Systems (DSS). Compared to TPC-H, which is more suitable for evaluating traditional query and reporting performance, TPC-DS includes complex applications such as data set analysis reports, interactive queries, and data mining, which are closer to real-world data warehouse business analysis scenarios.

This report provides you with the test results of Singdata Lakehouse and Spark SQL on the TPC-DS test set with a scale of 3TB. The conclusions are as follows:
![](.topwrite/assets/image_1758271325167.png)

* In the comparative test on the TPC-DS 3TB scale data set, Singdata Lakehouse showed significant performance advantages over Spark, with performance equivalent to **3.5times** that of AWS EMR Spark.
* Singdata Lakehouse has a significant performance improvement for long-running Spark jobs.

# Test Environment

* **Spark Test Environment**



| Configuration Item | Configuration Information                                                                                                                                                                 |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Server             | AWS EMR - emr-7.10.0 ： Machine Type： m6i.2xlarge （8 vCPU / 32GB / EBS 400 GB） The primary node has 4 vCPU and 32 GB memory and 16 worker nodes have a total of 128 vCPU and 512 GB memory |
| Network Bandwidth  | 12.5Gbps                                                                                                                                                                                  |
| Software           | Hadoop 3.4.1, Hive 3.1.3, JupyterEnterpriseGateway 2.6.0, Livy 0.8.0, Spark 3.5.5                                                                                                         |
| Storage Service    | AWS Cloud S3 Storage                                                                                                                                                                      |
| Data Format        | Default Parquet, Snappy Compression                                                                                                                                                       |

* **Singdata Lakehouse Test Environment**

| Configuration Item  | Configuration Information                                           |
| ------------------- | ------------------------------------------------------------------- |
| Computing Resources | Virtual Cluster - XLarge Size ( 16 CRU = 128 vCore & 512 GB memory) |
| Software            | AWS Singapore Region - Singdata Lakehouse Service                   |
| Storage Service     | Managed Storage, AWS Cloud S3                                       |

# Test Data


| Table                   | Number of Rows |
| ----------------------- | -------------- |
| call\_center            | 48             |
| catalog\_page           | 36,000         |
| catalog\_returns        | 432,018,033    |
| catalog\_sales          | 4,320,078,880  |
| customer                | 30,000,000     |
| customer\_address       | 15,000,000     |
| customer\_demographics  | 1,920,800      |
| date\_dim               | 73,049         |
| household\_demographics | 7,200          |
| income\_band            | 20             |
| inventory               | 1,033,560,000  |
| item                    | 360,000        |
| promotion               | 1,800          |
| reason                  | 67             |
| ship\_mode              | 20             |
| store                   | 1,350          |
| store\_returns          | 863,989,652    |
| store\_sales            | 8,639,936,081  |
| time\_dim               | 86,400         |
| warehouse               | 22             |
| web\_page               | 3,600          |
| web\_returns            | 216,003,761    |
| web\_sales              | 2,159,968,881  |
| web\_site               | 66             |

* **Statistics collected through analysis on data tables**.

# Test Process

In the test, we selected 103 complex SQL queries from the TPC-DS benchmark to perform performance testing on a 3TB dataset. The test results include the execution time of each query in Singdata Lakehouse and AWS EMR Spark SQL, as well as the performance comparison between the two.

## Spark

Create TPC-DS data tables in the metadata service, using Parquet file format, with the same partition settings as Lakehouse.

At the same time, export the TPC-DS 3TB test data from Singdata Lakehouse and save it to the object storage service in the form of data files to ensure that the test data for both parties is the same. Then use the Insert Into method in Spark to read the data files and write them into the data tables defined by Spark.

## Singdata Lakehouse

### Create Cluster and Table

Use Singdata Lakehouse XLARGE VCluster to test on AWS S3, all tables use the default storage format.

```SQL
create vcluster if not exists XLARGE_CLUSTER vcluster_size='XLARGE' vcluster_type='Analytics'  AUTO_RESUME=TRUE AUTO_SUSPEND_IN_SECOND=300 min_replicas=1 max_replicas=1;
```

### Create Table Statement

```SQL
drop table if exists call_center;
drop table if exists catalog_page;
drop table if exists catalog_returns;
drop table if exists catalog_sales;
drop table if exists customer;
drop table if exists customer_address;
drop table if exists customer_demographics;
drop table if exists date_dim;
drop table if exists household_demographics;
drop table if exists income_band;
drop table if exists inventory;
drop table if exists item;
drop table if exists promotion;
drop table if exists reason;
drop table if exists ship_mode;
drop table if exists store;
drop table if exists store_returns;
drop table if exists store_sales;
drop table if exists time_dim;
drop table if exists warehouse;
drop table if exists web_page;
drop table if exists web_returns;
drop table if exists web_sales;
drop table if exists web_site;
Drop table if exists catalog_sales;
Drop table if exists catalog_returns;
Drop table if exists inventory;
Drop table if exists store_sales;
Drop table if exists store_returns;
Drop table if exists web_sales;
Drop table if exists catalog_sales;
Drop table if exists catalog_sales;
create table if not exists catalog_sales
(
      cs_sold_date_sk          int,
      cs_sold_time_sk          int,
      cs_ship_date_sk          int,
      cs_bill_customer_sk      int,
      cs_bill_cdemo_sk         int,
      cs_bill_hdemo_sk         int,
      cs_bill_addr_sk          int,
      cs_ship_customer_sk      int,
      cs_ship_cdemo_sk         int,
      cs_ship_hdemo_sk         int,
      cs_ship_addr_sk          int,
      cs_call_center_sk        int,
      cs_catalog_page_sk       int,
      cs_ship_mode_sk          int,
      cs_warehouse_sk          int,
      cs_item_sk               int,
      cs_promo_sk              int,
      cs_order_number          long,
      cs_quantity              int,
      cs_wholesale_cost        decimal(7,2),
      cs_list_price            decimal(7,2),
      cs_sales_price           decimal(7,2),
      cs_ext_discount_amt      decimal(7,2),
      cs_ext_sales_price       decimal(7,2),
      cs_ext_wholesale_cost    decimal(7,2),
      cs_ext_list_price        decimal(7,2),
      cs_ext_tax               decimal(7,2),
      cs_coupon_amt            decimal(7,2),
      cs_ext_ship_cost         decimal(7,2),
      cs_net_paid              decimal(7,2),
      cs_net_paid_inc_tax      decimal(7,2),
      cs_net_paid_inc_ship     decimal(7,2),
      cs_net_paid_inc_ship_tax decimal(7,2),
      cs_net_profit            decimal(7,2)
)  partitioned by (cs_sold_date_sk);

create table if not exists catalog_returns
(
      cr_returned_date_sk      int,
      cr_returned_time_sk      int,
      cr_item_sk               int,
      cr_refunded_customer_sk  int,
      cr_refunded_cdemo_sk     int,
      cr_refunded_hdemo_sk     int,
      cr_refunded_addr_sk      int,
      cr_returning_customer_sk int,
      cr_returning_cdemo_sk    int,
      cr_returning_hdemo_sk    int,
      cr_returning_addr_sk     int,
      cr_call_center_sk        int,
      cr_catalog_page_sk       int,
      cr_ship_mode_sk          int,
      cr_warehouse_sk          int,
      cr_reason_sk             int,
      cr_order_number          long,
      cr_return_quantity       int,
      cr_return_amount         decimal(7,2),
      cr_return_tax            decimal(7,2),
      cr_return_amt_inc_tax    decimal(7,2),
      cr_fee                   decimal(7,2),
      cr_return_ship_cost      decimal(7,2),
      cr_refunded_cash         decimal(7,2),
      cr_reversed_charge       decimal(7,2),
      cr_store_credit          decimal(7,2),
      cr_net_loss              decimal(7,2)
)  partitioned by (cr_returned_date_sk);

create table if not exists inventory
(
  inv_date_sk          int,
  inv_item_sk          int,
  inv_warehouse_sk     int,
  inv_quantity_on_hand int
)  partitioned by (inv_date_sk);

create table if not exists store_sales
(
  ss_sold_date_sk        int,
  ss_sold_time_sk        int,
  ss_item_sk             int,
  ss_customer_sk         int,
  ss_cdemo_sk            int,
  ss_hdemo_sk            int,
  ss_addr_sk             int,
  ss_store_sk            int,
  ss_promo_sk            int,
  ss_ticket_number       long,
  ss_quantity            int,
  ss_wholesale_cost      decimal(7,2),
  ss_list_price          decimal(7,2),
  ss_sales_price         decimal(7,2),
  ss_ext_discount_amt    decimal(7,2),
  ss_ext_sales_price     decimal(7,2),
  ss_ext_wholesale_cost  decimal(7,2),
  ss_ext_list_price      decimal(7,2),
  ss_ext_tax             decimal(7,2),
  ss_coupon_amt          decimal(7,2),
  ss_net_paid            decimal(7,2),
  ss_net_paid_inc_tax    decimal(7,2),
  ss_net_profit          decimal(7,2)
)  partitioned by (ss_sold_date_sk);

create table if not exists store_returns
(
  sr_returned_date_sk    int,
  sr_return_time_sk      int,
  sr_item_sk             int,
  sr_customer_sk         int,
  sr_cdemo_sk            int,
  sr_hdemo_sk            int,
  sr_addr_sk             int,
  sr_store_sk            int,
  sr_reason_sk           int,
  sr_ticket_number       long,
  sr_return_quantity     int,
  sr_return_amt          decimal(7,2),
  sr_return_tax          decimal(7,2),
  sr_return_amt_inc_tax  decimal(7,2),
  sr_fee                 decimal(7,2),
  sr_return_ship_cost    decimal(7,2),
  sr_refunded_cash       decimal(7,2),
  sr_reversed_charge     decimal(7,2),
  sr_store_credit        decimal(7,2),
  sr_net_loss            decimal(7,2)
)  partitioned by (sr_returned_date_sk);

create table if not exists web_sales
(
  ws_sold_date_sk          int,
  ws_sold_time_sk          int,
  ws_ship_date_sk          int,
  ws_item_sk               int,
  ws_bill_customer_sk      int,
  ws_bill_cdemo_sk         int,
  ws_bill_hdemo_sk         int,
  ws_bill_addr_sk          int,
  ws_ship_customer_sk      int,
  ws_ship_cdemo_sk         int,
  ws_ship_hdemo_sk         int,
  ws_ship_addr_sk          int,
  ws_web_page_sk           int,
  ws_web_site_sk           int,
  ws_ship_mode_sk          int,
  ws_warehouse_sk          int,
  ws_promo_sk              int,
  ws_order_number          long,
  ws_quantity              int,
  ws_wholesale_cost        decimal(7,2),
  ws_list_price            decimal(7,2),
  ws_sales_price           decimal(7,2),
  ws_ext_discount_amt      decimal(7,2),
  ws_ext_sales_price       decimal(7,2),
  ws_ext_wholesale_cost    decimal(7,2),
  ws_ext_list_price        decimal(7,2),
  ws_ext_tax               decimal(7,2),
  ws_coupon_amt            decimal(7,2),
  ws_ext_ship_cost         decimal(7,2),
  ws_net_paid              decimal(7,2),
  ws_net_paid_inc_tax      decimal(7,2),
  ws_net_paid_inc_ship     decimal(7,2),
  ws_net_paid_inc_ship_tax decimal(7,2),
  ws_net_profit            decimal(7,2)
) partitioned by (ws_sold_date_sk);

create table if not exists web_returns
(
  wr_returned_date_sk      int,
  wr_returned_time_sk      int,
  wr_item_sk               int,
  wr_refunded_customer_sk  int,
  wr_refunded_cdemo_sk     int,
  wr_refunded_hdemo_sk     int,
  wr_refunded_addr_sk      int,
  wr_returning_customer_sk int,
  wr_returning_cdemo_sk    int,
  wr_returning_hdemo_sk    int,
  wr_returning_addr_sk     int,
  wr_web_page_sk           int,
  wr_reason_sk             int,
  wr_order_number          long,
  wr_return_quantity       int,
  wr_return_amt            decimal(7,2),
  wr_return_tax            decimal(7,2),
  wr_return_amt_inc_tax    decimal(7,2),
  wr_fee                   decimal(7,2),
  wr_return_ship_cost      decimal(7,2),
  wr_refunded_cash         decimal(7,2),
  wr_reversed_charge       decimal(7,2),
  wr_account_credit        decimal(7,2),
  wr_net_loss              decimal(7,2)
)  partitioned by (wr_returned_date_sk);

create table if not exists call_center
(
  cc_call_center_sk        int,
  cc_call_center_id        string,
  cc_rec_start_date        date,
  cc_rec_end_date          date,
  cc_closed_date_sk        int,
  cc_open_date_sk          int,
  cc_name                  string,
  cc_class                 string,
  cc_employees             int,
  cc_sq_ft                 int,
  cc_hours                 string,
  cc_manager               string,
  cc_mkt_id                int,
  cc_mkt_class             string,
  cc_mkt_desc              string,
  cc_market_manager        string,
  cc_division              int,
  cc_division_name         string,
  cc_company               int,
  cc_company_name          string,
  cc_street_number         string,
  cc_street_name           string,
  cc_street_type           string,
  cc_suite_number          string,
  cc_city                  string,
  cc_county                string,
  cc_state                 string,
  cc_zip                   string,
  cc_country               string,
  cc_gmt_offset            decimal(5,2),
  cc_tax_percentage        decimal(5,2)
);

create table if not exists catalog_page (
  cp_catalog_page_sk       int,
  cp_catalog_page_id       string,
  cp_start_date_sk         int,
  cp_end_date_sk           int,
  cp_department            string,
  cp_catalog_number        int,
  cp_catalog_page_number   int,
  cp_description           string,
  cp_type                  string) ;

create table if not exists customer (
  c_customer_sk             int,
  c_customer_id             string,
  c_current_cdemo_sk        int,
  c_current_hdemo_sk        int,
  c_current_addr_sk         int,
  c_first_shipto_date_sk    int,
  c_first_sales_date_sk     int,
  c_salutation              string,
  c_first_name              string,
  c_last_name               string,
  c_preferred_cust_flag     string,
  c_birth_day               int,
  c_birth_month             int,
  c_birth_year              int,
  c_birth_country           string,
  c_login                   string,
  c_email_address           string,
  c_last_review_date        string) ;

create table if not exists customer_address (
  ca_address_sk             int,
  ca_address_id             string,
  ca_street_number          string,
  ca_street_name            string,
  ca_street_type            string,
  ca_suite_number           string,
  ca_city                   string,
  ca_county                 string,
  ca_state                  string,
  ca_zip                    string,
  ca_country                string,
  ca_gmt_offset             decimal(5,2),
  ca_location_type          string) ;

create table if not exists customer_demographics (
  cd_demo_sk                int,
  cd_gender                 string,
  cd_marital_status         string,
  cd_education_status       string,
  cd_purchase_estimate      int,
  cd_credit_rating          string,
  cd_dep_count              int,
  cd_dep_employed_count     int,
  cd_dep_college_count      int) ;

create table if not exists date_dim (
  d_date_sk                 int,
  d_date_id                 string,
  d_date                    date,
  d_month_seq               int,
  d_week_seq                int,
  d_quarter_seq             int,
  d_year                    int,
  d_dow                     int,
  d_moy                     int,
  d_dom                     int,
  d_qoy                     int,
  d_fy_year                 int,
  d_fy_quarter_seq          int,
  d_fy_week_seq             int,
  d_day_name                string,
  d_quarter_name            string,
  d_holiday                 string,
  d_weekend                 string,
  d_following_holiday       string,
  d_first_dom               int,
  d_last_dom                int,
  d_same_day_ly             int,
  d_same_day_lq             int,
  d_current_day             string,
  d_current_week            string,
  d_current_month           string,
  d_current_quarter         string,
  d_current_year            string) ;

create table if not exists household_demographics (
  hd_demo_sk                int,
  hd_income_band_sk         int,
  hd_buy_potential          string,
  hd_dep_count              int,
  hd_vehicle_count          int) ;

create table if not exists income_band (
  ib_income_band_sk         int,
  ib_lower_bound            int,
  ib_upper_bound            int) using parquet ;

create table if not exists item (
  i_item_sk                 int,
  i_item_id                 string,
  i_rec_start_date          date,
  i_rec_end_date            date,
  i_item_desc               string,
  i_current_price           decimal(7,2),
  i_wholesale_cost          decimal(7,2),
  i_brand_id                int,
  i_brand                   string,
  i_class_id                int,
  i_class                   string,
  i_category_id             int,
  i_category                string,
  i_manufact_id             int,
  i_manufact                string,
  i_size                    string,
  i_formulation             string,
  i_color                   string,
  i_units                   string,
  i_container               string,
  i_manager_id              int,
  i_product_name            string) ;

create table if not exists promotion (
  p_promo_sk                int,
  p_promo_id                string,
  p_start_date_sk           int,
  p_end_date_sk             int,
  p_item_sk                 int,
  p_cost                    decimal(15,2),
  p_response_target         int,
  p_promo_name              string,
  p_channel_dmail           string,
  p_channel_email           string,
  p_channel_catalog         string,
  p_channel_tv              string,
  p_channel_radio           string,
  p_channel_press           string,
  p_channel_event           string,
  p_channel_demo            string,
  p_channel_details         string,
  p_purpose                 string,
  p_discount_active         string) ;

create table if not exists reason (
  r_reason_sk               int,
  r_reason_id               string,
  r_reason_desc             string) ;

create table if not exists ship_mode (
  sm_ship_mode_sk           int,
  sm_ship_mode_id           string,
  sm_type                   string,
  sm_code                   string,
  sm_carrier                string,
  sm_contract               string) ;

create table if not exists store (
  s_store_sk                int,
  s_store_id                string,
  s_rec_start_date          date,
  s_rec_end_date            date,
  s_closed_date_sk          int,
  s_store_name              string,
  s_number_employees        int,
  s_floor_space             int,
  s_hours                   string,
  s_manager                 string,
  s_market_id               int,
  s_geography_class         string,
  s_market_desc             string,
  s_market_manager          string,
  s_division_id             int,
  s_division_name           string,
  s_company_id              int,
  s_company_name            string,
  s_street_number           string,
  s_street_name             string,
  s_street_type             string,
  s_suite_number            string,
  s_city                    string,
  s_county                  string,
  s_state                   string,
  s_zip                     string,
  s_country                 string,
  s_gmt_offset              decimal(5,2),
  s_tax_precentage          decimal(5,2)) ;

create table if not exists time_dim (
  t_time_sk                 int,
  t_time_id                 string,
  t_time                    int,
  t_hour                    int,
  t_minute                  int,
  t_second                  int,
  t_am_pm                   string,
  t_shift                   string,
  t_sub_shift               string,
  t_meal_time               string) ;

create table if not exists warehouse (
  w_warehouse_sk           int,
  w_warehouse_id           string,
  w_warehouse_name         string,
  w_warehouse_sq_ft        int,
  w_street_number          string,
  w_street_name            string,
  w_street_type            string,
  w_suite_number           string,
  w_city                   string,
  w_county                 string,
  w_state                  string,
  w_zip                    string,
  w_country                string,
  w_gmt_offset             decimal(5,2)) ;

create table if not exists web_page (
  wp_web_page_sk           int,
  wp_web_page_id           string,
  wp_rec_start_date        date,
  wp_rec_end_date          date,
  wp_creation_date_sk      int,
  wp_access_date_sk        int,
  wp_autogen_flag          string,
  wp_customer_sk           int,
  wp_url                   string,
  wp_type                  string,
  wp_char_count            int,
  wp_link_count            int,
  wp_image_count           int,
  wp_max_ad_count          int) ;

create table if not exists web_site (
  web_site_sk              int,
  web_site_id              string,
  web_rec_start_date       date,
  web_rec_end_date         date,
  web_name                 string,
  web_open_date_sk         int,
  web_close_date_sk        int,
  web_class                string,
  web_manager              string,
  web_mkt_id               int,
  web_mkt_class            string,
  web_mkt_desc             string,
  web_market_manager       string,
  web_company_id           int,
  web_company_name         string,
  web_street_number        string,
  web_street_name          string,
  web_street_type          string,
  web_suite_number         string,
  web_city                 string,
  web_county               string,
  web_state                string,
  web_zip                  string,
  web_country              string,
  web_gmt_offset           decimal(5,2),
  web_tax_percentage       decimal(5,2)) ;

analyze table call_center compute statistics for all columns;
analyze table catalog_page compute statistics for all columns;
analyze table catalog_returns compute statistics for all columns;
analyze table catalog_sales compute statistics for all columns;
analyze table customer compute statistics for all columns;
analyze table customer_address compute statistics for all columns;
analyze table customer_demographics compute statistics for all columns;
analyze table date_dim compute statistics for all columns;
analyze table household_demographics compute statistics for all columns;
analyze table income_band compute statistics for all columns;
analyze table inventory compute statistics for all columns;
analyze table item compute statistics for all columns;
analyze table promotion compute statistics for all columns;
analyze table reason compute statistics for all columns;
analyze table ship_mode compute statistics for all columns;
analyze table store compute statistics for all columns;
analyze table store_returns compute statistics for all columns;
analyze table store_sales compute statistics for all columns;
analyze table time_dim compute statistics for all columns;
analyze table warehouse compute statistics for all columns;
analyze table web_page compute statistics for all columns;
analyze table web_returns compute statistics for all columns;
analyze table web_sales compute statistics for all columns;
analyze table web_site compute statistics for all columns;
```

### Execute Query

TPC-DS 99 test query statements: [TPC-DS-Query-SQL](https://autolake-dev-beijing.oss-cn-beijing.aliyuncs.com/clickzetta-tool/tpch/TPCDS_10TB_query.sql)

# Test Results

Below are the performance test results of Singdata Lakehouse and SparkSQL on 103 queries, measured in seconds (s). Lower values indicate better performance.

* **All queries were run as first executions**



| Query   | Lakehouse Latency（ms） | EMR Latency（ms） | AWS EMR/SingData |
| ------- | --------------------- | --------------- | ---------------- |
| Q1      | 952                   | 14,049          | 14.76            |
| Q2      | 2,937                 | 15,413          | 5.25             |
| Q3      | 910                   | 6,339           | 6.97             |
| Q4      | 20,978                | 57,691          | 2.75             |
| Q5      | 1,265                 | 23,010          | 18.19            |
| Q6      | 435                   | 4,384           | 10.08            |
| Q7      | 4,131                 | 11,971          | 2.90             |
| Q8      | 547                   | 3,387           | 6.19             |
| Q9      | 15,560                | 31,782          | 2.04             |
| Q10     | 868                   | 5,760           | 6.64             |
| Q11     | 9,908                 | 28,604          | 2.89             |
| Q12     | 401                   | 1,968           | 4.91             |
| Q13     | 7,415                 | 12,413          | 1.67             |
| Q14     | 20,937                | 56,096          | 2.68             |
| Q15     | 17,140                | 49,004          | 2.86             |
| Q16     | 413                   | 4,470           | 10.82            |
| Q17     | 1173                  | 41,781          | 35.62            |
| Q18     | 7,623                 | 10,400          | 1.36             |
| Q19     | 2,120                 | 12,499          | 5.90             |
| Q20     | 1,416                 | 3,331           | 2.35             |
| Q21     | 546                   | 1,957           | 3.58             |
| Q22     | 171                   | 1,694           | 9.91             |
| Q23     | 3,038                 | 2,837           | 0.93             |
| Q24     | 23,572                | 51,067          | 2.17             |
| Q25     | 24,166                | 50,293          | 2.08             |
| Q26     | 9,354                 | 60,723          | 6.49             |
| Q27     | 9,241                 | 57,767          | 6.25             |
| Q28     | 7,171                 | 8,941           | 1.25             |
| Q29     | 875                   | 6,977           | 7.97             |
| Q30     | 1,716                 | 10,400          | 6.06             |
| Q31     | 9,565                 | 44,449          | 4.65             |
| Q32     | 3,473                 | 23,259          | 6.70             |
| Q33     | 807                   | 6,294           | 7.80             |
| Q34     | 1,566                 | 7,753           | 4.95             |
| Q35     | 535                   | 1,707           | 3.19             |
| Q36     | 1,427                 | 4,502           | 3.15             |
| Q37     | 1119                  | 6,737           | 6.02             |
| Q38     | 1,807                 | 8,508           | 4.71             |
| Q39     | 3,267                 | 9,457           | 2.89             |
| Q40     | 1,159                 | 10,688          | 9.22             |
| Q41     | 4,349                 | 16,268          | 3.74             |
| Q42     | 656                   | 2,984           | 4.55             |
| Q43     | 638                   | 2,676           | 4.19             |
| Q44     | 978                   | 6,722           | 6.87             |
| Q45     | 77                    | 772             | 10.03            |
| Q46     | 607                   | 1,694           | 2.79             |
| Q47     | 982                   | 5,663           | 5.77             |
| Q48     | 4,006                 | 7,814           | 1.95             |
| Q49     | 2,054                 | 4,306           | 2.10             |
| Q50     | 1,832                 | 8,244           | 4.50             |
| Q51     | 6,763                 | 16,821          | 2.49             |
| Q52     | 1,895                 | 10,507          | 5.54             |
| Q53     | 4,261                 | 13,118          | 3.08             |
| Q54     | 6,680                 | 28,928          | 4.33             |
| Q55     | 4,344                 | 18,023          | 4.15             |
| Q56     | 564                   | 1,724           | 3.06             |
| Q57     | 764                   | 5,335           | 6.98             |
| Q58     | 4,721                 | 6,371           | 1.35             |
| Q59     | 242                   | 1,871           | 7.73             |
| Q60     | 688                   | 3,601           | 5.23             |
| Q61     | 3,673                 | 11,223          | 3.06             |
| Q62     | 686                   | 3,710           | 5.41             |
| Q63     | 5,099                 | 12,568          | 2.46             |
| Q64     | 1,263                 | 4,624           | 3.66             |
| Q65     | 2,575                 | 4,201           | 1.63             |
| Q66     | 1,144                 | 6,689           | 5.85             |
| Q67     | 1,058                 | 5,424           | 5.13             |
| Q68     | 9,063                 | 49,327          | 5.44             |
| Q69     | 8,298                 | 16,112          | 1.94             |
| Q70     | 1,408                 | 9,908           | 7.04             |
| Q71     | 10,848                | 58,696          | 5.41             |
| Q72     | 1,226                 | 4,377           | 3.57             |
| Q73     | 1076                  | 4,800           | 4.46             |
| Q74     | 5,281                 | 9,483           | 1.80             |
| Q75     | 960                   | 6,023           | 6.27             |
| Q76     | 3,692                 | 17,100          | 4.63             |
| Q77     | 607                   | 3,032           | 5.00             |
| Q78     | 6,994                 | 23,363          | 3.34             |
| Q79     | 10,787                | 45,604          | 4.23             |
| Q80     | 9,065                 | 45,183          | 4.98             |
| Q81     | 682                   | 4,979           | 7.30             |
| Q82     | 24,008                | 49,453          | 2.06             |
| Q83     | 1,864                 | 5,746           | 3.08             |
| Q84     | 5,452                 | 14,909          | 2.73             |
| Q85     | 1651                  | 6,841           | 4.14             |
| Q86     | 8,638                 | 12,687          | 1.47             |
| Q87     | 166                   | 3,004           | 18.10            |
| Q88     | 1275                  | 4,840           | 3.80             |
| Q89     | 2,373                 | 8,819           | 3.72             |
| Q90     | 1,332                 | 3,788           | 2.84             |
| Q91     | 4,619                 | 16,275          | 3.52             |
| Q92     | 14,906                | 17,313          | 1.16             |
| Q93     | 1,089                 | 5,925           | 5.44             |
| Q94     | 1,511                 | 6,508           | 4.31             |
| Q95     | 312                   | 3,530           | 11.31            |
| Q96     | 312                   | 1,365           | 4.38             |
| Q97     | 6870                  | 37581           | 5.47             |
| Q98     | 1,375                 | 18,580          | 13.51            |
| Q99     | 1,020                 | 17,166          | 16.83            |
| Q100    | 3,821                 | 16,158          | 4.23             |
| Q101    | 8,232                 | 27,079          | 3.29             |
| Q102    | 900                   | 2,867           | 3.19             |
| Q103    | 2,581                 | 11,588          | 4.49             |
| Summary | 448,597               | 1,572,252       | 3.50             |

^
