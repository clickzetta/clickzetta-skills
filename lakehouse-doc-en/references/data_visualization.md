# Data Visualization

This article explains how to use charts in Yunque products to visualize SQL worksheet results. Charts can visualize query results, convey logical relationships, and assist in making informed decisions. They enable you to quickly identify patterns and anomalies in data.

Currently supported chart types include:

* Line charts
* Bar charts

## Creating Charts

When running a query in development, you can generate charts based on the results.

1. Click Development or Workspace, create/select a SQL task.
2. Execute a SELECT query.
3. In the Data tab of the query results, click Charts.

## Modifying Charts

After clicking Charts to visualize the worksheet results, you need to filter and select required fields based on the chart type for the visualization area to display the corresponding chart.

Hovering over the chart allows you to view detailed information for each data point. For instance, you can view results in line chart format.

In the Settings section on the right of the visualization, filter information to be displayed:
1.Chart types: Line charts, Bar charts.
2.X-axis field: Represents the trend of values in the trend chart.
Note: Currently, aggregation by the selected X-axis field is not supported.
3.Y-axis field:
Y-axis supports using aggregate functions to determine a single value from multiple data points. These statistical methods correspond to the following functions:

* Total: sum
* Count: count
* Average: average
* Maximum: maximum
* Minimum: minimum
  4.Add Y-axis or Grouping
  Up to 10 Y-axis fields can be added for analysis in the same table.
  Adding a group involves performing a group by operation on the Y-axis field already added.
  Note: Grouping is only allowed when there is one Y-axis, and only one grouping field can be selected.

## Known Limitations

When there are numerous X-axis values and you need to view a specific data point on a trend, it is recommended to shorten the range on the chart to see accurate data points.

For example, in the chart below, the specific timestamp information displayed when hovering over the visualization is the accurate value.

## Use Cases

### Time-based Trend Charts

**Scenario 1**: To maintain time span differences, the result data type should be timestamp.

```
select order_date, count(*) as c from big_data_table group by order_date;
```

**Scenario 2**: To ignore time span differences and keep only specific result points, convert the result data type to string (order\_date::string).

```
select order_date::string, count(*) as c from big_data_table group by order_date;
```

^
