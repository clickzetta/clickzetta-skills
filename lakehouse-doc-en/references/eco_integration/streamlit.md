# Developing Singdata Lakehouse Applications with Streamlit

## Introduction to Streamlit

Streamlit is a powerful Python framework designed for data scientists and engineers to quickly create interactive web applications. With Streamlit, you can easily integrate data analysis, machine learning models, and data visualization into one application without deep knowledge of front-end technologies. The main features of Streamlit include:

* Simple and clear API, easy to get started, no front-end knowledge required.
* Supports Markdown and HTML text rendering for rich text effects.
* Provides a variety of interactive components, such as tables and charts, supporting responsive layouts.
* Active community support and continuous updates.

## Overview of the Development Process

The development process of a Streamlit application is very simple. This document will demonstrate, through an example, how to combine Streamlit and the clickzetta-sqlalchemy library to create a simple application that queries the Singdata Lakehouse and displays the results.

### Environment Preparation

First, ensure that `streamlit` and `clickzetta-sqlalchemy` are installed in your Python environment. Use the following commands to install them:

```bash
pip install streamlit clickzetta-sqlalchemy
```
Next, in the Streamlit `secrets.toml` configuration file (project directory or `$HOME/.streamlit/secrets.toml`), add the SQLAlchemy style connection string:
```toml
# .streamlit/secrets.toml

[connections.connection_name]
url = "clickzetta://username:password@instance.api.singdata.com/quickstart_ws?schema=public&virtualcluster=default"
```
### Writing Application Code

Create a file named `demo.py` and write the following code:
```python
# demo.py
import streamlit as st

# Create an SQL connection based on the configuration in secrets.toml.
conn = st.experimental_connection('connection_name', type='sql')

# Enter the SQL query statement.
sql = st.text_area('Enter your SQL query statement here')

# Execute the query and display the results.
if st.button('Run Query') and sql:
    result = conn.query(sql)
    st.dataframe(result)
```
### Running the Application

Use the following command to run the application:
```bash
streamlit run demo.py
```
Streamlit will automatically open the local browser and visit <http://localhost:8501>. You can also manually enter this address in the browser.

### Example SQL Query

The following is an example SQL query to retrieve purchase event data from the last 24 hours from Singdata Lakehouse:
```sql
SELECT
  brand,
  COUNT(DISTINCT user_id) AS unique_user_count,
  SUM(price) AS sum_price
FROM
  clickzetta_sample_data.ecommerce_events_history.ecommerce_events_multicategorystore_live
WHERE
  event_time >= (NOW() - INTERVAL '24' HOUR)
  AND event_type = 'purchase'
GROUP BY
  brand
ORDER BY
  sum_price DESC
LIMIT 10;
```
![Screenshot of Streamlit application running](streamlit-demo.png)

## Advanced Examples

### Adding Chart Display

To better display the data, you can use Streamlit's `st.plotly_chart` function to present the query results in chart form. First, install the `pandas` and `plotly` libraries:
```bash
pip install pandas plotly
```
Then, add the following code in `demo.py`:
```python
import pandas as pd
import plotly.express as px

# ...

if st.button('Generate Chart') and sql:
    result = conn.query(sql)
    df = pd.DataFrame(result)

    fig = px.bar(df, x='brand', y='sum_price', title='Sales by Brand')
    st.plotly_chart(fig)
```
## Reference Resources

* [Streamlit Official Documentation](https://docs.streamlit.io/library/get-started)
* [Singdata Lakehouse Official Documentation](https://docs.singdata.com/lakehouse/)

^