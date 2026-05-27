## Create Vector Index

**Syntax**
```SQL
CREATE TABLE table_name(
  columns_difinition,
  INDEX index_name (column_name) USING VECTOR  PROPERTIES(
      "property1" = "value1",
      "property2" = "value2"
  )
);
```
**columns\_difinition**: Define the field information of the table, the last field must be separated by a comma

**INDEX**: Keyword

**index\_name**: Custom name for the index

**column\_name**: The name of the field that needs to be indexed

**VECTOR**: Keyword, indicating vector index

**COMMENT**: Specify the description information of the index

**PROPERTIES**: Specify the parameters of the vector INDEX

| Parameter Name             | Optional Values                                                                      | Default Value    | Remarks                                      |
| -------------------------- | ------------------------------------------------------------------------------------ | ---------------- | -------------------------------------------- |
| distance.function          | l2\_distancecosine\_distancenegative\_dot\_productjaccard\_distancehamming\_distance | cosine\_distance | For convenience, please use negative\_dot\_product for dot product scenarios |
| scalar.type                | f32, f16, i8, b1                                                                     | f32              | The type of vector elements in the vector index, which can be different from the vector column |
| m                          | Recommended not to exceed 1000                                                       | 16               | Maximum number of neighbors in the HNSW algorithm |
| ef.construction            | Recommended not to exceed 5000                                                       | 128              | Size of the candidate set when constructing the index in the HNSW algorithm |
| reuse.vector.column        | false/true                                                                           | false            | Whether to reuse the data of the vector column to save storage space |
| compress.codec             | uncompressed/zstd/lz4                                                                | uncompressed     | Compression algorithm for the vector index; not effective when reusing the column |
| compress.level             | fatest/default/best                                                                  | default          | Compression algorithm level                   |
| compress.byte.stream.split | false/true                                                                           | true             | Rearrange float bits before compression       |
| compress.block.size        | Integer greater than 1M                                                                      | 16777216         | Compression block size                                      |
| conversion.rule            | default/as\_bits                                                                     | default          | When indexing vector(tinyint, N) type by bits, use as\_bits |

**Vector Index Scalar Type and Column Type**

Index element type refers to the type specified by scalar.type in properties; when the types are inconsistent, certain conversion rules (mostly cast) will be applied, except when using type b1.

|        |                     |                                                                                                              |
| ------ | ------------------- | ------------------------------------------------------------------------------------------------------------ |
| Index Element Type | Supported Vector Element Types           | Remarks                                                                                                           |
| b1     | tinyint, int, float | When "conversion.rule" = "bits", each bit in vector(tinyint, N) is treated as an element in the vector. When "conversion.rule" = "default", the vector is binarized. |
| i8     | tinyint, int, float | When the vector element type is inconsistent with the index, cast is performed (note that overflow may occur).                                                                       |
| f16    | int, float          | When the vector element type is inconsistent with the index, cast is performed.                                                                                        |
| f32    | int, float          | When the vector element type is inconsistent with the index, cast is performed.                                                                                        |

**Examples**
```SQL
CREATE TABLE test_vector1 (
    vec vector(float, 4),
    id int，
    index test_vector1_vec_idx  (vec) using vector properties (
        "scalar.type" = "f32",
        "distance.function" = "l2_distance"
    )
)
```
## Reference Documentation

* [Build Index](build-inverted-index.md)
* [Drop Index](DROP-INDEX.md)
* [List All Indexes](SHOW-INDEX.md)
* [View Index Details](DESC-INDEX.md)
## User Guide
[Vector Index User Guide](vector-search.md)

### Add Vector Index to Existing Table

**Syntax**
```SQL
CREATE  VECTOR INDEX [IF NOT EXISTS] index_name ON TABLE 
[schema].table_name(col_name) PROPERTIES(
    "property1" = "value1",
    "property2" = "value2"
)
```
**VECTOR**: Index type, vector index

**index\_name**: Table name, located under schema, index name under schema must be unique

**PROPERTIES**: Specify parameters for INDEX

**Description**

Executing CREATE INDEX is only effective for new data

**Example**
```SQL
CREATE TABLE test_vector2 (
    vec vector(float, 512),
    id int
) ;

 CREATE vector INDEX test_vector2_vec_idx on (vec) properties (
        "scalar.type" = "f32",
        "distance.function" = "l2_distance"
 );
```