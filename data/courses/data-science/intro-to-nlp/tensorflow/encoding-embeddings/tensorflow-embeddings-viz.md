---
imported_hash: 5da2b801b55a9a81
title: TensorFlow - Embeddings Viz
summary: from tensorflow import keras from tensorflow.keras.preprocessing.text import Tokenizer from tensorflow.keras.preprocessing.sequence import padsequences
order: 5
kind: notebook
section: tensorFlow / Encoding embeddings
source: learn-ai-engineering/data-science/intro-to-nlp/tensorFlow/encoding-embeddings/tensorFlow_embeddings_viz.ipynb
---

# TensorFlow - Embeddings Viz

```python
# importing packages
import tensorflow as tf
import numpy as np
import pandas as pd
import io
import csv

from tensorflow import keras
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
```

### Get IMdb data

```python
# reading 50,000 movie reviews labeled as "positive" or "negative"
imdb_data = pd.read_csv("./data/IMDB Dataset.csv")
```

### Preview Dataframe

```python
# checking first rows
imdb_data.loc[0:5]
```

### Transform categorical target to binary

```python
# processing data
imdb_data["sentiment"] = imdb_data["sentiment"].map({"positive": 1, "negative":0})
```

```python
# checking first rows
imdb_data.loc[0:5]
```

### Train/Test Split

```python
# defining train and test data sets
imdb_train = imdb_data["review"].values[:25000]
imdb_test = imdb_data["review"].values[25000:]
imdb_train_labels = imdb_data["sentiment"].values[:25000]
imdb_test_labels = imdb_data["sentiment"].values[25000:]
```

```python
imdb_train[0]
```

```python
imdb_train_labels[0]
```

### Hyperparameters

```python
# listing hyperparameters makes it easier to quickly test different combinations
vocab_size = 10000
embedding_dim = 16
# a sentence shorter than max_length it will be padded, longer sentences will be truncated
max_length = 120
```

### Tokenize

```python
# tokenizing data
tokenizer = Tokenizer(num_words=10000, oov_token = "<oov>")
tokenizer.fit_on_texts(imdb_train)
word_index = tokenizer.word_index

# converting words to numbers and pad for the neural network to use as input
train_sequences = tokenizer.texts_to_sequences(imdb_train)
train_padded = pad_sequences(train_sequences, maxlen=120, truncating="post")

# tokenized using the word_index learned from the training data
testing_sequences = tokenizer.texts_to_sequences(imdb_test)
test_padded = pad_sequences(testing_sequences, maxlen=120, truncating="post")
```

### Compare Tokenization

```python
# reversing keys: keys become the values, and values become the keys so that we can look a word up
reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])

def decode_review(text):
    return ' '.join([reverse_word_index.get(i, '?') for i in text])

# this is what will be fed in
print(decode_review(train_padded[1]))

# this is the original text
print(imdb_train[1])
```

### Create Embeddings

```python
# defining model
model = tf.keras.Sequential([
    # the "embedding layer" is the key to text sentiment analysis
    tf.keras.layers.Embedding(vocab_size, embedding_dim, input_length=max_length),
    tf.keras.layers.Flatten(),
    #tf.keras.layers.GlobalAveragePooling1D(),
    tf.keras.layers.Dense(6, activation = 'relu'),
    tf.keras.layers.Dense(1, activation = 'sigmoid')
])

model.compile(loss='binary_crossentropy',optimizer='adam',metrics=['accuracy'])
model.summary()
```

```python
model.fit(train_padded, imdb_train_labels, epochs=10, validation_data=(test_padded, imdb_test_labels))
```

### Embeddings

```python
# output from the "embedding layer"
embeddings = model.layers[0]
weights = embeddings.get_weights()[0]
print(f"Vocabulary size: {weights.shape[0]},  Embedding dimensions: {weights.shape[1]}")
```

```python
# getting the shape
weights.shape
```

```python
weights[0]
```

### Visualize the embedding vectors

```python
# writing the vectors and their metadata out to file.
# these 2 files ('vecs.tsv', 'meta.tsv') are used by the
# TensorFlow projector (http://projector.tensorflow.org/)
# to plot/visualize the vectors/embeddings in 3D

# output of the 16 values per word representation (embedding)
#      out_v are the vector/weights (embedding)
#      out_m are the actual words (meta data) associated with each embedding

out_v = io.open('vecs.tsv', 'w', encoding='utf-8')
out_m = io.open('meta.tsv', 'w', encoding='utf-8')
for word_num in range(1, vocab_size):
    word = reverse_word_index[word_num]
    embeddings = weights[word_num]
    out_m.write(word + "\n")
    out_v.write('\t'.join([str(x) for x in embeddings]) + "\n")
out_v.close()
out_m.close()
```

```python
# reading it
with open("vecs.tsv") as file:
    rd = csv.reader(file, delimiter="\t", quotechar='"')
    for row in rd:
        print(row)
```

```python
# reading meta.tsv
with open("meta.tsv") as fd:
    rd = csv.reader(fd, delimiter="\t", quotechar='"')
    for row in rd:
        print(row)
```
