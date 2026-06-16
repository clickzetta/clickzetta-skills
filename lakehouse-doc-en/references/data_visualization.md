# Data Visualization

This article explains how to use charts in Singdata to visualize SQL worksheet results. Charts help you communicate patterns in your data, spot anomalies, and make more informed decisions.

Currently supported chart types:

* Line chart
* Bar chart

## Creating a Chart

You can generate a chart from query results while running queries in development.

1. Click Development or Workspace, then create or select a SQL task.
2. Run a SELECT query.
3. In the query results area, click the "Chart" option under the Data tab.

## Configuring a Chart

After clicking "Chart" to visualize the worksheet results, you need to select the required fields based on the chart type before the visualization area will display a chart.

Hover over the chart to view detailed information for each data point. For example, you can view results as a line chart:

^
^

In the "Settings" panel on the right side of the visualization area, configure what to display:

1. Chart type: Line chart or Bar chart.

2. X-axis field: Defines the values shown along the trend axis.

   Note: Aggregation by the selected X-axis field is not currently supported.

3. Y-axis field:

^

The Y-axis supports aggregate functions to derive a single value from multiple data points. The available aggregation methods are:

* Total: sum
* Count: count
* Average: average
* Maximum: maximum
* Minimum: minimum

4. Add Y-axis fields or grouping.

You can add up to 10 Y-axis fields for analysis in the same chart.

Adding a group applies a GROUP BY operation to the Y-axis fields already added.

Note: Grouping is only available when there is exactly one Y-axis field, and only one grouping field can be selected.

## Known Limitations

When there are many X-axis values and you need to view a specific data point on a trend, it is recommended to narrow the range on the chart to see accurate data points.

For example, in the chart below, the accurate value is shown only when hovering over the visualization and the specific timestamp information appears.

^
^

## Use Cases

### Time-based Trend Charts

**Scenario 1**: To preserve time span differences, the result data type should be a timestamp type. For example:

* `order_date` is a timestamp type. The trend chart will automatically display data according to the actual time intervals, which more accurately reflects the "trend."

```
select order_date, count(*) as c from big_data_table group by order_date;
```

^
^

**Scenario 2**: To **ignore** time span differences and keep only the specific result data points, cast the result to a string (`order_date::string`):

```
select order_date::string, count(*) as c from big_data_table group by order_date;
```

^
