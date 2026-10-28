---
imported_hash: a9f5c222353352bb
title: TensorFlow Encoding Sentences
summary: from tensorflow import keras from nltk import wordtokenize, senttokenize from tensorflow.keras.preprocessing.text import Tokenizer from tensorflow.keras.preprocessing.sequence import padsequences
order: 6
kind: notebook
section: tensorFlow / Encoding embeddings
source: learn-ai-engineering/data-science/intro-to-nlp/tensorFlow/encoding-embeddings/tensorFlow_encoding_sentences_1.ipynb
---

# TensorFlow Encoding Sentences

```python
# importing packages
import tensorflow as tf
import nltk

from tensorflow import keras
from nltk import word_tokenize, sent_tokenize
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
```

### Use the following document:

```python
# defining text
document = "Apple today unveiled completely redesigned Everyone Can Code curriculum to help introduce more elementary and middle school students to the world of coding. Now available, the new curriculum includes even more resources for teachers, a brand new guide for students and updated Swift Coding Club materials. Today millions of students worldwide already use Everyone Can Code curriculum to bring their ideas to life and develop important skills including creativity, collaboration and problem solving. "
document
```

```python
# creating a list of the separate sentences
list_of_sentences = sent_tokenize(document)
```

```python
list_of_sentences
```

### Tokenize the sentences

```python
# encodes the 100 most common words from the corpus of text
tokenizer = Tokenizer(oov_token = "<oov>")

# fit the Tokenizer to the data
# strips out punctuation and converts to lowercase
tokenizer.fit_on_texts(list_of_sentences)
```

###  Create a word index

```python
# tokenizer creates a dictionary of key/value --> word/token pairs
# word_index contains the dictionary
word_index = tokenizer.word_index
print(word_index)
print(len(word_index))
```

### Encode the sentences into sequences

```python
# changing sentences into vectors (sequences)
sequences = tokenizer.texts_to_sequences(list_of_sentences)
print(sequences)
```

###  Add padding to the sequences so that they are of equal length

```python
# adding padding to create a matrix of equal-sized word vectors
# padding is "pre" by default
padded = pad_sequences(sequences, padding="post")
print(padded)
```

### Provide your own Apple-related sentence, and encode it into a sequence

```python
# "oov" (out of vocabulary) words are assigned a 1
my_sentence = "Apple is an incredibly creative company with millions teachers and students using their products."
tokenizer.texts_to_sequences([my_sentence])
```
