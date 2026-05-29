###  JSON_CONTAINS
``` sql
json_contains(target, candidate)
json_contains(target, candidate, jsonPath)
```

#### Description
Checks whether the target JSON object/array contains the candidate JSON object/array.

**Two-parameter version:** Checks if target contains candidate
- For scalar values (strings, numbers, booleans, null): checks for exact equality
- For objects: checks if all key-value pairs of candidate exist in target (target may have extra keys)
- For arrays: checks if all elements of candidate can be found in target (order-independent)

**Three-parameter version:** Checks if the specified jsonPath location in target contains candidate
- jsonPath must be a string literal
- First extracts the element from target at jsonPath, then checks if that element contains candidate

#### Parameters
* target: json - The target JSON object
* candidate: json - The candidate JSON object to check
* jsonPath: string (optional) - JSON path, must be a literal

#### Returns
* boolean - Returns true if contained, otherwise false; returns NULL if any parameter is NULL

#### Examples
```sql
select target, candidate, json_contains(json_parse(target), json_parse(candidate)) as contains
from values
  ('{"a":1,"b":2}', '{"a":1,"b":2}'),              -- Exact match
  ('{"a":1,"b":2}', '{"b":2,"a":1}'),              -- Different order, same content
  ('{"a":1,"b":2,"c":3}', '{"a":1}'),              -- target contains candidate
  ('{"a":1,"b":2,"c":3}', '{"a":1,"b":2}'),        -- target contains multiple keys of candidate
  ('{"a":1,"b":2}', '{"a":1,"b":2,"c":3}'),        -- target lacks a key
  ('{"a":{"b":1,"c":2}}', '{"a":{"b":1}}'),        -- Nested object
  ('{"a":1}', '{}')                                -- Empty object is always contained
  as t(target, candidate);
-- Result:
-- {"a":1,"b":2}	{"a":1,"b":2}	true
-- {"a":1,"b":2}	{"b":2,"a":1}	true
-- {"a":1,"b":2,"c":3}	{"a":1}	true
-- {"a":1,"b":2,"c":3}	{"a":1,"b":2}	true
-- {"a":1,"b":2}	{"a":1,"b":2,"c":3}	false
-- {"a":{"b":1,"c":2}}	{"a":{"b":1}}	true
-- {"a":1}	{}	true
```

```sql
select target, candidate, json_contains(json_parse(target), json_parse(candidate)) as contains
from values
  ('[1,2,3]', '[1,2,3]'),                          -- Exact match
  ('[1,2,3,4,5]', '[1,3,5]'),                      -- Contains all elements (order-independent)
  ('[1,2,3]', '1'),                                 -- Contains a single value
  ('[1,2,3]', '[1,2,3,4]'),                        -- candidate has extra elements
  ('[[1,2],[3,4]]', '[[1,2]]'),                    -- Nested arrays (exact match)
  ('[]', '[]')                                      -- Empty arrays
  as t(target, candidate);
-- Result:
-- [1,2,3]	[1,2,3]	true
-- [1,2,3,4,5]	[1,3,5]	true
-- [1,2,3]	1	true
-- [1,2,3]	[1,2,3,4]	false
-- [[1,2],[3,4]]	[[1,2]]	true
-- []	[]	true
```

```sql
select target, candidate, json_contains(json_parse(target), json_parse(candidate)) as contains
from values
  ('[{"a":1},{"b":2}]', '{"a":1}'),                -- Array contains a complete object element
  ('[{"a":1},{"b":2}]', '{"a":1,"b":2}')           -- Object fields distributed across multiple array elements
  as t(target, candidate);
-- Result:
-- [{"a":1},{"b":2}]	{"a":1}	true
-- [{"a":1},{"b":2}]	{"a":1,"b":2}	true
```

```sql
select target, candidate,
  json_contains(json_parse(target), json_parse(candidate), '$.a') as contains_at_a,
  json_contains(json_parse(target), json_parse(candidate), '$.c') as contains_at_c
from values
  ('{"a": 1, "b": 2, "c": {"d": 4}}', '1'),
  ('{"a": 1, "b": 2, "c": {"d": 4}}', '{"d": 4}')
  as t(target, candidate);
-- Result:
-- {"a": 1, "b": 2, "c": {"d": 4}}	1	true	false
-- {"a": 1, "b": 2, "c": {"d": 4}}	{"d": 4}	false	true
```

