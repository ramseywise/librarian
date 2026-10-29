---
imported_hash: 350014baf2c0f622
title: Text Preprocessing and Word Embeddings
summary: from nltk import word_tokenize, sent_tokenize from nltk.corpus import stopwords from gensim.models.word2vec import Word2Vec
order: 21
kind: notebook
section: tensorFlow / Text processing
source: learn-ai-engineering/data-science/intro-to-nlp/tensorFlow/text-processing/text_preprocessing_and_word_embeddings.ipynb
---

# Text Preprocessing and Word Embeddings

```python
# importing packages & libraries
import nltk
import string
import json

from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from gensim.models.word2vec import Word2Vec

nltk.download('stopwords')
```

## Text data

```python
# reading data
with open("./data/sarcasm.json", 'r') as f:
    datastore = json.load(f)
```

```python
# parsing json file
sentences = []

for item in datastore:
    sentences.append(item["headline"])
```

```python
# checking a list of sentences
sentences
```

```python
# checking length of sentences
len(sentences)
```

```python
# getting a sample sentence
sentences[5]
```

### Stop words

```python
# getting a list of stop words and punctuation to be removed
stpwrds = stopwords.words('english') + list(string.punctuation)
```

### Preprocessing sentences
- tokenize
- make lowercase
- remove stop words/puctuation.

```python
# preprocessing sentences
processed_sentences = []
for s in sentences:
    low_tokens = word_tokenize(s.lower())
    processed_sentences.append([w for w in low_tokens if w
                        not in stpwrds])
```

### Using word2vec to make word embeddings from the sentences

```python
# creating model
model = Word2Vec(sentences=processed_sentences, size=32,
                 sg=1, window=10, iter=5,
                 min_count=10, workers=4)
```

### Displaying a sample embedding (weights)

```python
model.wv["woman"]
```

### Exploring the top 4 embeddings most similar to a word of your choice

```python
# getting top 4 words most similar to a given word (using cosine similarity)
model.wv.most_similar('woman', topn=4)
```

### Getting the 5 words most similar to "president" in this corpus

```python
# getting top 5 words most similar to a given word (using cosine similarity)
model.wv.most_similar('president', topn=5)
```
