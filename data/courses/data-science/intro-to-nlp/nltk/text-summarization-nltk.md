---
imported_hash: f354ef44af874750
title: Automatic Text Summarization
summary: from nltk.corpus import stopwords from nltk.tokenize import senttokenize from sklearn.metrics.pairwise import cosinesimilarity
order: 3
kind: notebook
section: Nltk
source: learn-ai-engineering/data-science/intro-to-nlp/nltk/text_summarization_nltk.ipynb
---

# Automatic Text Summarization


**Goal:** Generate a concise summary of the texts.

**How:** Unsupervised text summarization (extractive summarization) using TextRank Alg.

**Data:** Manually Annotated Sub-Corpus First Release.

```python
# importing packages & libraries
import numpy as np
import pandas as pd
import nltk
import re
import networkx as nx

from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from sklearn.metrics.pairwise import cosine_similarity

# nltk.download('punkt')
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', -1)
pd.set_option('max_colwidth', 800)
```

```python
! pip install networkx
```

### Data

```python
# reading data
df = pd.read_csv('./data/all_data_new.csv')
df = df[['file_name','text']]
```

```python
df.head(2)
```

### Getting setences

```python
# splitting text into sentences
sentences = []
for s in df['text']:
    sentences.append(sent_tokenize(s))

sentences = [y for x in sentences for y in x]
```

```python
# printing 2 sentences
sentences[:2]
```

### Word Embeddings

**Good:** GloVe keeps word order.

**Not so good:** Size of 822 MB.

```python
!wget http://nlp.stanford.edu/data/glove.6B.zip
```

```python
!unzip glove*.zip
```

```python
# extracting word vectors
word_embeddings = {}
f = open('glove.6B.100d.txt', encoding='utf-8')
for line in f:
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    word_embeddings[word] = coefs
f.close()
```

```python
# getting the lengh of word embeddings
len(word_embeddings)
```

```python
# removing punctuations, numbers and special characters
clean_sentences = pd.Series(sentences).str.replace("[^a-zA-Z]", " ")

# making alphabets lowercase
clean_sentences = [s.lower() for s in clean_sentences]
```

```python
# defining stop words
stop_words = stopwords.words('english')
```

```python
# removing stopwords
def remove_stopwords(sen):
    sen_new = " ".join([i for i in sen if i not in stop_words])
    return sen_new
```

```python
# removing stopwords from the sentences
clean_sentences = [remove_stopwords(r.split()) for r in clean_sentences]
```

### Vectors

```python
# extracting word vectors
word_embeddings = {}
f = open('glove.6B.100d.txt', encoding='utf-8')
for line in f:
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    word_embeddings[word] = coefs
f.close()
```

```python
# creating vectors for sentences
sentence_vectors = []
for i in clean_sentences:
    if len(i) != 0:
        v = sum([word_embeddings.get(w, np.zeros((100,))) for w in i.split()])/(len(i.split())+0.001)
    else:
        v = np.zeros((100,))
    sentence_vectors.append(v)
```

### Similarity Matrix

```python
# defining a similarity matrix
sim_mat = np.zeros([len(sentences), len(sentences)])
```

```python
# initializing similarity matrix
for i in range(len(sentences)):
    for j in range(len(sentences)):
        if i != j:
            sim_mat[i][j] = cosine_similarity(sentence_vectors[i].reshape(1,100), sentence_vectors[j].reshape(1,100))[0,0]
```

### Text Rank Alg

```python
# converting similarity matrix to a graph
nx_graph = nx.from_numpy_array(sim_mat)
scores = nx.pagerank(nx_graph)
# scores = nx.textrank(nx_graph)
```

```python
# defining ranked sentences
ranked_sentences = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)
```

```python
# extracting top 10 sentences as the summary
for i in range(10):
    print(ranked_sentences[i][1])
```

```python
ranked_sentences
```

```python
len(ranked_sentences)
```
