# Indexes

Singdata Lakehouse supports multiple index types for accelerating query filtering in different scenarios and reducing data scan volume.

## Index Type Comparison

| Index Type | Applicable Queries | Applicable Fields | Typical Scenario |
|---------|---------|---------|---------|
| [Bloomfilter Index](bloomfilter-summary.md) | Equality queries (`=`, `IN`) | High-cardinality fields, such as user ID, order number | Quickly skip data files that do not contain the target value |
| [Inverted Index](inverted-index.md) | Full-text search (`MATCH`), keyword search | Text fields, JSON fields | Log search, document search, multi-keyword filtering |
| [Vector Index](vector-search.md) | Approximate Nearest Neighbor search (ANN) | VECTOR type fields | Semantic search, image similarity, RAG retrieval |

## Selection Advice

- The field is a high-cardinality ID field with frequent equality queries --> **Bloomfilter Index**
- The field is text content requiring keyword or phrase search --> **Inverted Index**
- The field is a vector embedding requiring similarity search --> **Vector Index**
- Unsure which to use --> Refer to [Index Best Practices](lakehouse-index-best-practice.md)

## Index Management Commands

- [BUILD INDEX](build-inverted-index.md)
- [DROP INDEX](DROP-INDEX.md)
- [SHOW INDEX](SHOW-INDEX.md)
- [DESC INDEX](DESC-INDEX.md)
