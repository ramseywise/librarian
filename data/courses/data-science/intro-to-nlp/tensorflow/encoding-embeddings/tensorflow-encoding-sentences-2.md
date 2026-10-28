---
imported_hash: 48bd716cbb72d34c
title: TensorFlow - Encoding Sentences
summary: from tensorflow import keras from tensorflow.keras.preprocessing.text import Tokenizer from tensorflow.keras.preprocessing.sequence import padsequences
order: 7
kind: notebook
section: tensorFlow / Encoding embeddings
source: learn-ai-engineering/data-science/intro-to-nlp/tensorFlow/encoding-embeddings/tensorFlow_encoding_sentences_2.ipynb
---

# TensorFlow - Encoding Sentences

```python
# importing packages
import tensorflow as tf
import numpy as np
import json

from tensorflow import keras
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
```

### Tokenize sentences

```python
# defining sentences
sentences = [
    "Machine Learning is great",
    "Online Learning is great",
    "Do you think deep learning is amazing?"]

# encoding the 100 most common words from the corpus of text
# <oov> is the out-of-vocabulary token
tokenizer = Tokenizer(num_words = 100, oov_token = "<oov>")

# fitting the Tokenizer to the list of sentences - strips out punctuation and converts to lowercase
tokenizer.fit_on_texts(sentences)
```

### Create word index

```python
# creating a dictionary (word_index) of key/value using tokenizer - word/token pairs
word_index = tokenizer.word_index
print(word_index)
```

### Generate sequences

```python
# changing sentences into vectors (sequences)
sequences = tokenizer.texts_to_sequences(sentences)
print(sequences)
```

```python
# out of vocabulary words are assigned a 1
test_sentence = "Deep learning loves data"
tokenizer.texts_to_sequences([test_sentence])
```

### Add padding

```python
# adding padding to create a matrix of equal-sized word vectors
padded = pad_sequences(sequences, padding="post")
print(padded)
```

## Get text data

```python
# reading sarcasm data
# https://storage.googleapis.com/laurencemoroney-blog.appspot.com/sarcasm.json
with open("./data/sarcasm.json", 'r') as f:
    datastore = json.load(f)
```

```python
# parsing json file
sentences = []
labels = []

for item in datastore:
    sentences.append(item["headline"])
    labels.append(item["is_sarcastic"])
```

```python
# printing an example sarcastic sentence
print(sentences[15])
print(labels[15])
```

### Tokenize sentences

```python
# instantiate Tokenizer
tokenizer = Tokenizer(oov_token = "<oov>")
tokenizer.fit_on_texts(sentences)

# creating a word/value dictionary
word_index = tokenizer.word_index
print(len(word_index))
print(word_index)

# changing the sentences into vectors (sequences)
sequences = tokenizer.texts_to_sequences(sentences)

# adding padding to create a matrix of equal-sized word vectors
padded = pad_sequences(sequences, padding="post")
print(padded)
```

```python
# printing sentences
print(sentences[2])
print(padded[2])

# printing shape
print(padded.shape)
```
