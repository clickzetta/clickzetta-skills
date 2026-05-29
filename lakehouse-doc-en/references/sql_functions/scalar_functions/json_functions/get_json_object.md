### GET\_JSON\_OBJECT 

#### Description

The GET\_JSON\_OBJECT function is used to extract the value of a specific field from a JSON-formatted string (str). It accepts two parameters: the first parameter is a JSON-formatted string, and the second parameter is a string used to specify the path of the field to be extracted in the JSON object.

#### Parameters

* str (string): A string containing JSON-formatted data.
* path (string): A string path describing the location of the field to be extracted. Refer to the [json path specification](<https://goessner.net/articles/JsonPath/>)
    * "$" represents the root element
    * ".key" or "\['key']" is used to find the key in the JSON object. Specially, "\[\*]" means to get all values, and it must be enclosed in single quotes
    * "\[index]" is used to access elements of a JSON array by index, starting from 0. Specially, "\[\*]" means all elements

#### Return Value

* Returns the value of the specified field, type is string.

#### Example Usage

1. Suppose we have a JSON object as follows:
```json
{
  "name": "Zhang San",
  "age": 30,
  "address": {
    "city": "Beijing",
    "zipcode": "100000"
  },
  "hobbies": ["basketball", "traveling", "reading"]
}
```
We can use the GET\_JSON\_OBJECT function to extract different fields from a JSON object, for example:
* Extract the name:
```sql
SELECT get_json_object('{"name": "Zhang San", "age": 30, "address": {"city": "Beijing", "zipcode": "100000"}, "hobbies": ["basketball", "traveling", "reading"]}', '$.name');
```
Results:
* Extracted city:
```sql
SELECT get_json_object('{"name": "Zhang San", "age": 30, "address": {"city": "Beijing", "zipcode": "100000"}, "hobbies": ["basketball", "traveling", "reading"]}', '$.address.city');
```
Result: Beijing
* Extract all hobbies:
```sql
SELECT get_json_object('{"name": "Zhang San", "age": 30, "address": {"city": "Beijing", "zipcode": "100000"}, "hobbies": ["basketball", "traveling", "reading"]}', '$.hobbies');
```
Result: \["basketball", "traveling", "reading"]

2. Another example, we have a JSON array as follows:
```json
[
  {
    "id": 1,
    "name": "Product A",
    "price": 100
  },
  {
    "id": 2,
    "name": "Product B",
    "price": 200
  }
]
```
We can use the GET\_JSON\_OBJECT function to extract specific elements from an array, for example:
* Extract the price of the first product:
```sql
SELECT get_json_object('[{"id": 1, "name": "Product A", "price": 100}, {"id": 2, "name": "Product B", "price": 200}]', '$[0].price');
```
Result: 100
* Extract the names of all products:
```sql
SELECT get_json_object('[{"id": 1, "name": "Product A", "price": 100}, {"id": 2, "name": "Product B", "price": 200}]', '$[*].name');
```
Result：\["Product A", "Product B"]

Through the above example, you can see the flexibility and practicality of the GET\_JSON\_OBJECT function when handling JSON data. In practical applications, you can freely combine path strings as needed to extract any field from the JSON data.