### ST_GEOHASH 

####  Description
The `ST_GEOHASH` function is a geospatial function that calculates the corresponding geohash code based on the specified longitude (lon) and latitude (lat). This function accepts three parameters: longitude, latitude, and precision. The result is a string whose length is determined by the precision parameter, with a maximum length of 12.

#### Parameter Description
- **lon** (double): The specified longitude value.
- **lat** (double): The specified latitude value.
- **precision** (int): The specified length precision of the geohash code, ranging from 1 to 12.

#### Return Result
Returns a string representing the geohash code.

#### Usage Example
1. Calculate the geohash code with a precision of 5 (longitude: 116.3, latitude: 39.9):
```sql
SELECT ST_GEOHASH(116.3, 39.9, 5);
-- Return result: wx4dy
```
2. Geohash encoding with precision 8 (Longitude: 120.0, Latitude: 30.0):
```sql
SELECT ST_GEOHASH(120.0, 30.0, 8);
-- Return result: wtm6dtm6
```
3. Geohash encoding with a precision of 12 (Longitude: 121.5, Latitude: 31.0):
```sql
SELECT ST_GEOHASH(121.5, 31.0, 12);
-- Return result: wtw2kg3s54y7
```
#### Precautions
- Please ensure that the input longitude and latitude values are within a reasonable range, i.e., longitude between -180 and 180, and latitude between -85.05112878 and 85.05112878.
- The precision parameter will affect the length and accuracy of the generated geohash code. The higher the precision, the longer the code, and the more accurate the represented geographic area. However, please note that excessively high precision may lead to unnecessary accuracy, thereby affecting performance.
- Geohash codes can be used for indexing, storing, and querying geospatial data, but please note that it is not a perfect representation method for geospatial data and may have some errors. When using it, please choose the appropriate precision and method according to actual needs and scenarios.