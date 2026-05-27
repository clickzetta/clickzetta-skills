## TOKENIZE

```SQL
TOKENIZE(input, option)
```
###  Description

The tokenization function, if you want to check the actual effect of tokenization or tokenize a piece of text, you can use the `tokenize` function.

### Parameter Description

* input: The sentence to be tokenized.

* option: This parameter is required to specify the tokenization settings, `map('analyzer', 'english')`.

  * Currently supported tokenization types are:
  * keyword: No tokenization, no case conversion, no tokenization, directly save the complete text to the inverted index. Must match exactly during search.
  * english: Only recognizes continuous ASCII letters or numbers, converts to lowercase, optimal performance when only English characters are present.
  * chinese: Recognizes Chinese and English characters, filters punctuation, converts English to lowercase.
  * unicode: Recognizes all Unicode symbols, supports tokenization of Western European letters to lowercase and CJK (Chinese, Japanese, Korean) characters, filters punctuation, converts to lowercase.

### Return Result

The return value is an array\<string>

### Example
```SQL
-- Use keyword tokenizer
SELECT TOKENIZE('Lakehouse inverted index',map('analyzer', 'keyword')) as toke;
+--------------------+
|        toke        |
+--------------------+
| ["Lakehouse inverted index"] |
+--------------------+
-- Use chinese tokenizer, not supported yet
SELECT TOKENIZE('Lakehouse inverted index',map('analyzer', 'chinese')) as toke;
+--------------------------------+
|              toke              |
+--------------------------------+
| ["lakehouse","inverted","index"] |
+--------------------------------+
-- Use unicode tokenizer
SELECT TOKENIZE('Lakehouse inverted index',map('analyzer', 'unicode')) as toke;
+--------------------------------+
|              toke              |
+--------------------------------+
| ["lakehouse","inverted","index"] |
+--------------------------------+
-- Use english tokenizer
SELECT TOKENIZE('Lakehouse inverted index',map('analyzer', 'english')) as toke;
+----------------------------------+
|               toke               |
+----------------------------------+
| ["lakehouse","inverted","index"] |
+----------------------------------+
```