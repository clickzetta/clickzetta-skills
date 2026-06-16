# JSON Data Processing

## Create schema and table

```
CREATE SCHEMA IF NOT EXISTS clickzetta_demo_json_schema;
use schema clickzetta_demo_json_schema;
create table if not exists clickzetta_demo_json_schema.user_infor(info json);
insert into table  clickzetta_demo_json_schema.user_infor values
  (JSON '{"name": "Zhang San","age": 25,"gender": "Male","email": "zhangsan@example.com","phone": "13812xxx","address": "Chaoyang District, Beijing"}'),
  (JSON '{"name": "Li Si","age": 23, "gender": "Female","email": "lisi@example.com","phone": "139876xxx1","address": "Pudong New Area, Shanghai"}'),
  (JSON '{"name": "Wang Wu", "age": 27,"gender": "Male","email": "wangwu@example.com","phone": "1376xxxxx8","address": "Tianhe District, Guangzhou"}'),
  (JSON '{"name": "Zhao Liu","age": 24,"gender": "Female","email": "zhaoliu@example.com","phone": "1369xxxx2","address": "Nanshan District, Shenzhen"}'),
  (JSON '{"name": "Sun Qi","age": 26, "gender": "Male","email": "sunqi@example.com","phone": "1351xxxx679","address": "Xihu District, Hangzhou"}'),
  (JSON '{"name": "Zhou Ba","age": 22,"gender": "Female","email": "zhouba@example.com","phone": "1347xxxx19","address": "Gulou District, Nanjing"}'),
  (JSON '{"name": "Wu Jiu","age": 28,"gender": "Male","email": "wujiu@example.com","phone": "13345xxxx01","address": "Wuhou District, Chengdu"}'),
  (JSON '{"name": "Zheng Shi","age": 21,"gender": "Female","email": "zhengshi@example.com","phone": "1326xxx123","address": "Yubei District, Chongqing"}'),
  (JSON '{"name": "Chen Shiyi","age": 29,"gender": "Male","email": "chenshiyi@example.com","phone": "131xxxx789","address": "Beilin District, Xi'an"}'),
  (JSON '{"name": "Lin Shier", "age": 20,"gender": "Female","email": "linshier@example.com","phone": "130xxxx5432","address": "Siming District, Xiamen"}');
```

## Using json\_extract to Parse Data

```
select json_extract_string(info,"$.address") as address,
      json_extract_int(info,"$.age") as age,
      json_extract_string(info,"$.email") as email
from clickzetta_demo_json_schema.user_infor;
```

![](.topwrite/assets/image_1718703925062.png)

## Cleanup

```
drop schema if exists clickzetta_demo_json_schema;
```

## Congratulations, it's done.

Please enjoy and learn more!

## Appendix

### Download Zeppelin Notebook Source File

The code in this document is also available in a version that runs on [Zeppelin](eco_integration/zeppelin.md). If you want to run the code directly, please follow the instructions in the documentation to install [Zeppelin](eco_integration/zeppelin.md).

[03.JSON_Data_Processing.ipynb](https://github.com/yunqiqiliang/clickzetta_quickstart/blob/main/zeppelin_notebook/03.JSON%E6%95%B0%E6%8D%AE%E5%A4%84%E7%90%86.ipynb)
