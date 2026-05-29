# Lakehouse Time Travel Feature Usage Guide

## Introduction to Time Travel Feature

The Time Travel feature of Lakehouse allows you to easily access data at any point within the time travel window. This means you can view data at different points in time and even restore to a previous data state.

With Time Travel, you can query updated or deleted data, restore deleted tables, or recover expired tables.
![](.topwrite/assets/image_1708936936399.png =740)

As shown in the figure above, the table originally had one piece of data, and operations such as insert, update, and delete were performed on the table, resulting in a total of four versions. When the specified version is between v0 and v1, it will return the data of v0. By specifying the version through Time Travel, you can view historical version data.

## Accessing Data at a Specific Point in Time

[TIME TRAVEL](TIMETRAVEL.md)

## Setting Data Retention Period

You can configure the data retention period for Time Travel to determine how long data is retained within the time travel window. Depending on your needs, you can set different retention periods.

The Time Travel retention period determines how far back you can access data. For example, if the Time Travel retention period is set to 7 days, you can access data from any point within the past 7 days. If it exceeds 7 days, you will no longer be able to use Time Travel to access expired data, and the data will be physically deleted.

Currently, in the Preview version, the default retention period is 7 days, allowing you to query data within 7 days. In the future, Lakehouse will charge storage fees separately for Time Travel.

### Setting Data Retention Period on a Table

You can set the data retention period for a table using the following SQL statement:

```SQL
ALTER TABLE orders SET PROPERTIES ('data_retention_days'='num');
```

The setting range for `num` is 0-90, indicating the number of days the data is retained.

## Restore Deleted Objects

If you accidentally delete an object, you can use the `UNDROP` command to restore it. Here is an example of restoring a deleted table:

```SQL
UNDROP TABLE orders;
```

This command will restore the deleted table named `orders`.

## Restore Data to a Specific Version

Using the `RESTORE` command, you can restore data to a specific version. This is useful for rolling back or fixing erroneous data changes. Below is an example of restoring data to a specified version:

```SQL
RESTORE TABLE orders TO TIMESTAMP AS OF '2023-03-01 10:00:00';
```

This command restores the data of the `orders` table to the version as of 10:00:00 on March 1, 2023.
