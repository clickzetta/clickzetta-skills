### ST_LATFROMGEOHASH 

####  Description

The `ST_LATFROMGEOHASH` function is used to calculate and return the corresponding latitude value based on a given geohash string. This function can be widely used in map services, location queries, and geographic information systems.

#### Function Syntax
```
ST_LATFROMGEOHASH(hashstr)
```
#### Parameter Description

* `hashstr` (string): The geohash string for which the latitude needs to be calculated.

#### Return Result

Returns the calculated latitude value, with the data type being double.

#### Usage Example

1. Calculate the latitude value of a geohash string:
   ```sql
   SELECT ST_LATFROMGEOHASH('v0gs3y0z') as res;
   +-------------------+
   |        res        |
   +-------------------+
   | 50.00006675720215 |
   +-------------------+
   ```
2. Use in conjunction with other geographic information functions in query statements:
   ```sql
   SELECT ST_LATFROMGEOHASH(ST_GEOHASH(116.397428, 39.90923,3)) as res;
   +-----------+
   |    res    |
   +-----------+
   | 40.078125 |
   +-----------+
   ```
3. For batch calculation of latitude values for a set of geohash strings:
   ```sql
   SELECT ST_LATFROMGEOHASH('v0gs3y0z')as res1, ST_LATFROMGEOHASH('wh5g5jc3d') as res2, ST_LATFROMGEOHASH('4s7qfj9p0') as res3;
   +-------------------+--------------------+--------------------+
   |       res1        |        res2        |        res3        |
   +-------------------+--------------------+--------------------+
   | 50.00006675720215 | 23.059208393096924 | -64.87579107284546 |
   +-------------------+--------------------+--------------------+
   ```
#### Precautions

* Ensure that the input geohash string is valid, otherwise it may lead to inaccurate calculation results.
* When using this function, make sure that the relevant geographic information extension plugin is installed and enabled.

Through the above example, you can see that the `ST_LATFROMGEOHASH` function can conveniently extract latitude information from the geohash string, thereby providing convenience for geographic information systems and location services.