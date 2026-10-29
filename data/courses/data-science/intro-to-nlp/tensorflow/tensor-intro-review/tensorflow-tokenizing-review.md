---
imported_hash: 82c90acd38c14da0
title: TensorFlow - Tokenizing Review
summary: from tensorflow.keras.preprocessing.text import Tokenizer from tensorflow.keras.preprocessing.sequence import pad_sequences
order: 18
kind: notebook
section: tensorFlow / Tensor intro review
source: learn-ai-engineering/data-science/intro-to-nlp/tensorFlow/tensor-intro-review/tensorFlow_tokenizing_review.ipynb
---

# TensorFlow - Tokenizing Review

```python
# importing packages
import pandas as pd

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
```

## Get data

```python
# reading and processing data
yelp_ratings = pd.read_csv("./data/yelp_ratings.csv") #44530 samples
yelp_reviews = yelp_ratings["text"].values
yelp_reviews_labels = yelp_ratings["sentiment"].values
yelp_reviews_stars = yelp_ratings["stars"].values
```

## Tokenize sentences

```python
# encoding the 1000 most common words from the corpus of text
tokenizer = Tokenizer(num_words = 1000, oov_token = "<oov>")

# fitting the Tokenizer to the data - strips out punctuation and converts to lowercase
tokenizer.fit_on_texts(yelp_reviews)
```

## View the word index

```python
# creating a dictionary (word_index) of key/value using tokenizer - word/token pairs
word_index = tokenizer.word_index
print(word_index)
```

## Generate sequences

```python
# changing sentences into vectors (sequences)
sequences = tokenizer.texts_to_sequences(yelp_reviews)
```

## Sample text

```python
# checking a sample
yelp_reviews[10]
```

## Text to sequence

```python
# printing sequences
print(sequences[10])
```

## Add padding

```python
# adding padding to create a matrix of equal-sized word vectors - padding is "pre" by default
padded = pad_sequences(sequences, padding="post")

print(padded[10])
```

```python
# checking shape
padded.shape
```
