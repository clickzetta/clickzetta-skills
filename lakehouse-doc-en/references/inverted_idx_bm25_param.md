# Lakehouse Inverted Index BM25 Parameter Tuning

BM25 (Best Matching 25) is one of the most important relevance scoring algorithms in modern full-text search. The Lakehouse inverted index supports BM25 and allows users to adjust key parameters to optimize search effectiveness for different scenarios.

Supported parameters:

`k1` - Term frequency saturation control

* **Value range**: `[0.0, 3.0]`, recommended range `[1.0, 2.0]`

* **Default value**: `1.2`

* **Purpose**: Controls the impact of term frequency on relevance scoring

* **Effect**:

  * **Larger k1**: Greater impact of term frequency on scoring, high-frequency-term documents are more likely to receive high scores
  * **Smaller k1**: Faster term frequency saturation, reducing the excessive influence of high-frequency terms

`b` - Document length normalization

* **Value range**: `[0.0, 1.0]`

* **Default value**: `0.75`

* **Purpose**: Controls the impact of document length on relevance scoring

* **Effect**:

  * **b = 0**: Completely ignore document length, short and long documents treated equally
  * **b = 1**: Full length normalization, short documents gain significant advantage
  * **b = 0.75**: Balanced length influence, suitable for most scenarios

In the Lakehouse, add the following statement before SQL queries:

```
SET cz.storage.parquet.inverted.index.similarity.bm25={"k1": 1.2, "b": 0.75} 
```

to control search effectiveness.

## Example:

### Step 1: Data Preparation

```
-- 1. CREATE TEST TABLE

CREATE TABLE bm25_demo_table (
    id INT,
    title STRING,
    content_en STRING,
    content_cn STRING,
    doc_type STRING
);

-- 2. Create index and insert data
CREATE INVERTED INDEX idx_content_cn_score ON TABLE bm25_demo_table(content_cn) 
     PROPERTIES("analyzer"="chinese", "support_score"="true")
;
CREATE INVERTED INDEX idx_content_en_score ON TABLE bm25_demo_table(content_en) 
     PROPERTIES("analyzer"="english", "support_score"="true")
;

INSERT INTO bm25_demo_table VALUES
-- Short document series: high keyword density
(1, 'AI Intro', 'AI technology.', 'Artificial intelligence technology.', 'short'),
(2, 'AI Applications', 'AI AI applications in business.', 'Artificial intelligence artificial intelligence applications in business.', 'short'),

-- Medium document series: medium keyword density  
(3, 'AI Development History', 'The history of AI technology spans decades. AI researchers developed machine learning algorithms. Modern AI systems use deep learning techniques.', 'The development history of artificial intelligence technology spans decades. Artificial intelligence researchers developed machine learning algorithms. Modern artificial intelligence systems use deep learning techniques.', 'medium'),
(4, 'AI Real-world Applications', 'AI technology revolutionizes industries. Companies implement AI solutions for automation. AI chatbots improve customer service efficiency.', 'Artificial intelligence technology revolutionizes industries. Companies implement artificial intelligence solutions for automation. Artificial intelligence chatbots improve customer service efficiency.', 'medium'),

-- Long document series: low density but multiple occurrences
(5, 'AI Technology Overview', 'Artificial intelligence represents one of the most transformative technologies of our time. AI systems can process vast amounts of data, recognize patterns, and make predictions with remarkable accuracy. The field of AI encompasses machine learning, deep learning, natural language processing, and computer vision. Modern AI applications span across healthcare, finance, transportation, and entertainment industries. As AI technology continues to evolve, researchers are exploring new frontiers in artificial general intelligence and quantum computing integration with AI systems.', 'Artificial intelligence represents one of the most transformative technologies of our time. Artificial intelligence systems can process vast amounts of data, recognize patterns, and make predictions with remarkable accuracy. The field of artificial intelligence encompasses machine learning, deep learning, natural language processing, and computer vision. Modern artificial intelligence applications span across healthcare, finance, transportation, and entertainment industries. As artificial intelligence technology continues to evolve, researchers are exploring new frontiers in artificial general intelligence and quantum computing integration with artificial intelligence systems.', 'long'),

-- Distractor document: does not contain target keywords
(6, 'Blockchain Technology', 'Blockchain technology provides decentralized solutions. Cryptocurrency mining requires significant computational power. Smart contracts automate business processes.', 'Blockchain technology provides decentralized solutions. Cryptocurrency mining requires significant computational power. Smart contracts automate business processes.', 'control'),

-- High-frequency keyword document
(7, 'AI Intensive Discussion', 'AI AI AI is everywhere. AI development, AI research, AI implementation, AI optimization, AI performance, AI scalability, AI security, AI ethics, AI governance, AI regulation.', 'Artificial intelligence artificial intelligence artificial intelligence is everywhere. Artificial intelligence development, artificial intelligence research, artificial intelligence implementation, artificial intelligence optimization, artificial intelligence performance, artificial intelligence scalability, artificial intelligence security, artificial intelligence ethics, artificial intelligence governance, artificial intelligence regulation.', 'high_freq'),

-- Low-frequency but precise match
(8, 'Precise AI Definition', 'The definition of AI varies among experts.', 'The definition of artificial intelligence varies among experts.', 'precise')
;
```

> Note: If data is inserted before index creation, you need to BUILD INDEX for the index to take effect:
>
> ```
> BUILD INDEX idx_content_cn_score ON bm25_demo_table;
> BUILD INDEX idx_content_en_score ON bm25_demo_table;
> ```

We have constructed a test set containing different types of documents:

* **Short documents** (2-20 characters): High keyword density
* **Medium documents** (100-200 characters): Medium keyword density
* **Long documents** (500+ characters): Low keyword density but multiple occurrences
* **High-frequency document**: Many repeated keywords
* **Precise match**: Small number but precise keyword matches

### Step 2: Search Verification:

#### English Search Test

**Case 1: Default parameters** `(using defaults)` - **Balanced configuration**

Search keyword: `"AI"`

```
SELECT score (),
    id,
    title,
    doc_type,
    LENGTH(content_en) AS len,
    REGEXP_COUNT (content_en, 'AI') AS ai_count,
    SUBSTRING(content_en, 1, 50) AS preview
FROM bm25_demo_table
WHERE match_any(content_en, 'AI')
ORDER BY score () DESC, id
LIMIT 50;
```

| score()    | id | title                | doc\_type  | len | ai\_count | preview                                            |
| ---------- | -- | -------------------- | ---------- | --- | --------- | -------------------------------------------------- |
| 0.16484952 | 7  | AI Intensive Discussion | high\_freq | 174 | 13        | AI AI AI is everywhere. AI development, AI researc |
| 0.14495456 | 2  | AI Applications      | short      | 31  | 2         | AI AI applications in business.                    |
| 0.13709007 | 4  | AI Real-world Applications | medium     | 138 | 3         | AI technology revolutionizes industries. Companies |
| 0.13152356 | 1  | AI Intro             | short      | 14  | 1         | AI technology.                                     |
| 0.13141003 | 3  | AI Development History | medium     | 145 | 3         | The history of AI technology spans decades. AI res |
| 0.1138232  | 8  | Precise AI Definition | precise    | 42  | 1         | The definition of AI varies among experts.         |
| 0.10628956 | 5  | AI Technology Overview | long       | 580 | 5         | Artificial intelligence represents one of the most |

**Key observations**:
* High-frequency-term document ranks first (as expected)
* Short documents gain significant length advantage
* Long documents, despite having more matches, are penalized by length

**Case 2**: `b=0.0` - **Ignore document length**

```
SET cz.storage.parquet.inverted.index.similarity.bm25={"k1": 1.2, "b": 0.0};
SELECT score (),
    id,
    title,
    doc_type,
    LENGTH(content_en) AS len,
    REGEXP_COUNT (content_en, 'AI') AS ai_count,
    SUBSTRING(content_en, 1, 50) AS preview
FROM bm25_demo_table
WHERE match_any(content_en, 'AI')
ORDER BY score () DESC, id
LIMIT 10;
```

| score()        | id    | title                   | doc\_type  | len     | ai\_count | preview                                                |
| -------------- | ----- | ----------------------- | ---------- | ------- | --------- | ------------------------------------------------------ |
| 0.16691414     | 7     | AI Intensive Discussion | high\_freq | 174     | 13        | AI AI AI is everywhere. AI development, AI researc     |
| **0.14703354** | **5** | **AI Technology Overview** | **long**   | **580** | **5**     | **Artificial intelligence represents one of the most** |
| 0.13022971     | 3     | AI Development History  | medium     | 145     | 3         | The history of AI technology spans decades. AI res     |
| 0.13022971     | 4     | AI Real-world Applications | medium     | 138     | 3         | AI technology revolutionizes industries. Companies     |
| 0.11395099     | 2     | AI Applications         | short      | 31      | 2         | AI AI applications in business.                        |
| 0.08287345     | 1     | AI Intro                | short      | 14      | 1         | AI technology.                                         |
| 0.08287345     | 8     | Precise AI Definition   | precise    | 42      | 1         | The definition of AI varies among experts.             |

**Key observations**:
* **Long documents benefit significantly**: jumping from last place to second place
* **Short documents lose their advantage**: length advantage is completely eliminated
* **Pure term-frequency ranking**: ranking is entirely based on content relevance

^

### Chinese Search Test

**Case 1: Default parameters** `(using defaults)` - **Balanced configuration**

```
SET cz.storage.parquet.inverted.index.similarity.bm25={"k1": 1.2, "b": 0.75};
SELECT score (),
    id,
    title,
    doc_type,
    LENGTH(content_en) AS len,
    REGEXP_COUNT (content_en, 'Artificial intelligence') AS ai_count,
    SUBSTRING(content_en, 1, 50) AS preview
FROM bm25_demo_table
WHERE match_any(content_en, 'Artificial intelligence')
ORDER BY score () DESC, id
LIMIT 10;
```

| score()     | id | title                | doc\_type  | len | ai\_count | preview                                            |
| ----------- | -- | -------------------- | ---------- | --- | --------- | -------------------------------------------------- |
| 0.16505295  | 7  | AI Intensive Discussion | high\_freq | 89  | 13        | Artificial intelligence artificial intelligence artificial intelligence is everywhere. Artificial intelligence development, artificial intelligence research, artificial intelligence implementation, artificial intelligence optimization, artificial intelligence performance |
| 0.13975275  | 2  | AI Applications      | short      | 16  | 2         | Artificial intelligence artificial intelligence applications in business. |
| 0.13214059  | 4  | AI Real-world Applications | medium     | 54  | 3         | Artificial intelligence technology revolutionizes industries. Companies implement artificial intelligence solutions for automation. Artificial intelligence chatbots improve customer service efficiency |
| 0.1313231   | 1  | AI Intro             | short      | 7   | 1         | Artificial intelligence technology. |
| 0.12937927  | 3  | AI Development History | medium     | 51  | 3         | The development history of artificial intelligence technology spans decades. Artificial intelligence researchers developed machine learning algorithms. Modern artificial intelligence systems use deep learning techniques |
| 0.12602468  | 5  | AI Technology Overview | long       | 161 | 7         | Artificial intelligence represents one of the most transformative technologies of our time. Artificial intelligence systems can process vast amounts of data, recognize patterns, and make predictions with remarkable accuracy |
| 0.113299355 | 8  | Precise AI Definition | precise    | 16  | 1         | The definition of artificial intelligence varies among experts. |

## Parameter Tuning Strategy

### Scenario-Based Parameter Recommendations

#### 1. News Search Scenario

```sql
-- Optimized configuration: balance term frequency and document length
SET cz.storage.parquet.inverted.index.similarity.bm25={"k1": 1.2, "b": 0.8};
```

* **Applicable scenarios**: News articles, blog content
* **Optimization goal**: Give more attention to short documents, preventing long articles from burying important short news
* **Effect**: Improve the visibility of short news

#### 2. Academic Literature Search

```sql
-- Optimized configuration: reduce length penalty, emphasize content quality
SET cz.storage.parquet.inverted.index.similarity.bm25={"k1": 1.0, "b": 0.3};
```

* **Applicable scenarios**: Papers, research reports, technical documentation
* **Optimization goal**: Long documents are not overly penalized, content richness matters more
* **Effect**: Detailed document rankings improve

#### 3. Product Search Scenario

```sql
-- Optimized configuration: strengthen exact matching
SET cz.storage.parquet.inverted.index.similarity.bm25={"k1": 0.8, "b": 0.5};
```

* **Applicable scenarios**: E-commerce search, product catalogs
* **Optimization goal**: Exact matches take priority over high-frequency matches
* **Effect**: Reduce the impact of term frequency stacking on rankings

#### 4. Social Media Search

```sql
-- Optimized configuration: prioritize short content
SET cz.storage.parquet.inverted.index.similarity.bm25={"k1": 1.5, "b": 0.9};
```

* **Applicable scenarios**: Microblogs, comments, short video descriptions
* **Optimization goal**: Short content first, quickly locate key information
* **Effect**: Short content rankings significantly improved

^
