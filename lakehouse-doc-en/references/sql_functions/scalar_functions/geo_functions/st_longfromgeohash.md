### ST_LONGFROMGEOHASH 

####  Description

The ST\_LONGFROMGEOHASH function is used to calculate and return the corresponding longitude value based on the given geohash string. This function can be widely used in map services, location information processing, and other fields.

#### Parameter Description

* hashstr (string type): The input geohash string.

#### Return Result

Returns the calculated longitude value, with a data type of double.

#### Usage Example

The following is an example of using the ST\_LONGFROMGEOHASH function:

1. Get the longitude based on the specified geohash string:
   ```sql
   SELECT ST_LONGFROMGEOHASH('v0gs3y0z') as res;
   +-------------------+
   |        res        |
   +-------------------+
   | 49.99998092651367 |
   +-------------------+
   ```
2. Associate the geohash string with other geographic information data to obtain more accurate location information:
```sql
SELECT
  ST_LONGFROMGEOHASH(geohash column) AS `Longitude`,
  ST_LATFROMGEOHASH(geohash column) AS `Latitude`
FROM your_table;
```
This query will return the query results containing the location name, corresponding longitude, and latitude.

3. Combine with the geocoding function to obtain the latitude and longitude information of a building or address:
```sql
SELECT
  ST_LONGFROMGEOHASH(geohash column) AS `Longitude`,
  ST_LATFROMGEOHASH(geohash column) AS `Latitude`
FROM your_table;
```
This query will return the query results containing the longitude, latitude, and geographic information of the building or address.

#### Notes

* Please ensure that the input geohash string is correct, otherwise it may lead to inaccurate calculation results.
* The longitude and latitude values calculated based on geohash may have a certain error range, depending on the precision of the geohash.
* When using the ST_LONGFROMGEOHASH function, please ensure that the spatial database extension feature is installed and enabled.

^