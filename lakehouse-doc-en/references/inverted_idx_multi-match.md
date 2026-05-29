# Inverted Index Multi-Match Feature

`multi-match` is a powerful query feature that allows users to search a **single query string** across **multiple fields** simultaneously. This is very useful in many real-world scenarios. For example, when a user on an e-commerce website types "durable backpack" into the search box, the system may need to search across multiple fields such as `product_title`, `description`, and `category` at the same time.

When executing a multi-match query, the system performs matching operations on each specified field in the background, then intelligently merges and sorts all results, ultimately returning a unified relevance-ranked list.

^

## Feature Example

### Data Preparation:

Test data table:

```
Table name: dbpedia_entities_1m
Created at: 2025-07-03 12:07:32
Row count: 1,000,000 rows
Storage size: 12.6 GB
```

Table structure:

* `id` (string) - Entity ID
* `title` (string) - Entity title
* `text` (string) - Entity description text
* `vec` (vector(float,1536)) - 1536-dimensional vector

Indexes already built:

|                                    |          |       |         |                           |
| ---------------------------------- | -------- | ----- | ------- | ------------------------- |
| Index Name                         | Index Type | Target Field | Analyzer | Special Configuration      |
| inverted\_multi\_match\_idx\_id    | INVERTED | id    | unicode | -                         |
| inverted\_multi\_match\_idx\_title | INVERTED | title | unicode | -                         |
| inverted\_multi\_match\_idx\_text  | INVERTED | text  | unicode | -                         |
| idx\_dbpedia\_vec\_1536            | VECTOR   | vec   | -       | ef.construction=128, m=64 |

### Feature Examples:

#### Single-Column Match

Search in the `title` field, requiring 'Paris Wisconsin Foster' to match over 67%

```SQL
SELECT    
    id,
    title
FROM dbpedia_entities_1m
WHERE multi_match (
            title,
            'Paris Wisconsin Foster',
            str_to_map('analyzer:unicode,minimum_should_match:67%')
      );
```

![](./topwrite/assets/image_1753846662848.png)

^

#### Multi-Field Combined Search

**Three-Field Combined Search (ID + Title + Text)**

Search across `id, title, text` three fields, requiring at least 3 query terms to match

```SQL
SELECT    id,
          title,
          text
FROM      dbpedia_entities_1m
WHERE     multi_match (
            id,
            title,
            text,
            'French deaf Avenue_Q Robert driver',
            str_to_map('analyzer:unicode,minimum_should_match:3')
          );
```

**Result**: 2 relevant records returned, with semantically accurate content matching.

```
id                         title           text
<dbpedia:Robert_Manzon>  | Robert Manzon  | Robert Manzon (12 April 1917 – 19 January 2015) was a French racing driver. He participated in 29 Formula One World Championship Grands Prix, debuting on 21 May 1950. He achieved two podiums, and scored a total of 16 championship points. At the time of his death, Manzon was the last surviving driver to have taken part in the first Formula One World Championship in 1950.
<dbpedia:Robert_Benoist> | Robert Benoist | Robert Marcel Charles Benoist (20 March 1895 – 9 September 1944) was a French Grand Prix motor racing driver and war hero.
```

^
