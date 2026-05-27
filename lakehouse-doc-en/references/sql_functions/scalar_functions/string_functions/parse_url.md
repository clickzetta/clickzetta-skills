### PARSE_URL 

#### Description
The PARSE_URL function is used to extract specific parts from a given URL. Depending on the specified partToExtract parameter, information such as the hostname, path, query parameters, reference, protocol, or filename can be extracted from the URL. Note that this function does not validate the URL's validity.

#### Parameters
* **url** (string type): The URL address to be parsed.
* **partToExtract** (string type): The part of the URL to extract. Possible values include: HOST, PATH, QUERY, REF, PROTOCOL, FILE.
* **key** (optional parameter, string type): When partToExtract is QUERY, this specifies the key name of the query parameter to extract.

#### Return Value
The function returns the extracted part of the URL, with the type being string.

#### Usage Example
The following examples demonstrate how to use the PARSE_URL function to extract different parts of the URL:

1. Extract the hostname:
   ```sql
   SELECT PARSE_URL('http://spark.apache.org/path?query=1#ref', 'HOST') AS host;
   ```
Result:
   ```
   spark.apache.org
   ```
2. Extraction Path:
   ```sql
   SELECT PARSE_URL('http://spark.apache.org/path?query=1#ref', 'PATH') AS path;
   ```
Result: 
   ```
   /path
   ```
3. Extract Query Parameters:
   ```sql
   SELECT PARSE_URL('http://spark.apache.org/path?query=1#ref', 'QUERY') AS query;
   ```
Result: 
   ```
   query=1
   ```
4. Extracting References:
   ```sql
   SELECT PARSE_URL('http://spark.apache.org/path?query=1#ref', 'REF') AS ref;
   ```
Result: 
   ```
   ref
   ```
### 5. Extraction Protocol:
   ```sql
   SELECT PARSE_URL('http://spark.apache.org/path?query=1#ref', 'PROTOCOL') AS protocol;
   ```
Result: 
   ```
   http
   ```
6. Extract the file name:
   ```sql
   SELECT PARSE_URL('http://spark.apache.org/path?query=1#ref', 'FILE') AS file;
   ```
Result:
   ```
   /path?query=1
   ```
7. Extract the query parameter value of a specific key:
   ```sql
   SELECT PARSE_URL('http://spark.apache.org/path?query=1&key=value#ref', 'QUERY', 'key') AS key_value;
   ```
Result:
   ```
   value
   ```