This document aims to guide users on how to efficiently query JSON data using SQL syntax. By mastering these query methods, users can simplify the query process. For the creation of JSON types, please refer to the document [JSON Types](JSON.md).

## **Syntax**

```SQL
--Key name to access fields in JSON object
json_column['key']['key']...
--Access elements in JSON array by index
json_array[index]
```

**Parameter Description**

* json\_column: Represents a JSON field, which is a JSON object. By specifying the key name (`key`) as a string, you can locate and retrieve specific data fields within the JSON object. Use single square brackets `[]` to access the first-level fields of the object; nested use of double square brackets `[][]` allows for deeper retrieval of second-level or deeper fields within the object.
* json\_array: A JSON array type, used to access elements of a JSON array by index, starting from 0.

**Return Value Description**

* The return value is of JSON type. If other types are needed, you can use CAST for forced conversion. For type conversion, please refer to the [JSON Type](JSON.md) document.

# **Example**

Retrieve the first-level structure of JSON

```SQL
SELECT parse_json(s)['firstName'] as j
      FROM VALUES ('{ "firstName": "John", "lastName": "doe", "age": 26, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [] } ] }'),
                  ('{ "firstName": "Ada", "lastName": "doe", "age": 20, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "address2": {"city": "NewYork"}, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [1,2,3] } ] }')
                 as t(s);
```

### Extract json secondary structure

```SQL
SELECT parse_json(s)['address']['streetAddress'] as j
      FROM VALUES ('{ "firstName": "John", "lastName": "doe", "age": 26, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [] } ] }'),
                  ('{ "firstName": "Ada", "lastName": "doe", "age": 20, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "address2": {"city": "NewYork"}, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [1,2,3] } ] }')
                 as t(s);
```

Extract elements from the json array

```SQL
SELECT parse_json(s)['phoneNumbers'][0]['number'] as j
      FROM VALUES ('{ "firstName": "John", "lastName": "doe", "age": 26, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [] } ] }'),
                  ('{ "firstName": "Ada", "lastName": "doe", "age": 20, "address": { "streetAddress": "naist street", "city": "Nara", "postalCode": "630-0192" }, "address2": {"city": "NewYork"}, "phoneNumbers": [ { "type": "iPhone", "number": "0123-4567-8888" }, { "type": "home", "number": "0123-4567-8910", "extra": [1,2,3] } ] }')
                 as t(s);
```

^
