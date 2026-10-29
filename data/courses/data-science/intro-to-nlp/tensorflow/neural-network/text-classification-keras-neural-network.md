---
imported_hash: 559748092c44e3fe
title: Text Classification Using Neural Network
summary: from tensorflow.keras import layers from tensorflow.keras import losses from tensorflow.keras import preprocessing from tensorflow.keras.preprocessing.text import Tokenizer from tensorflow.keras.preprocessing.sequence import pad_sequences
order: 14
kind: notebook
section: tensorFlow / Neural network
source: learn-ai-engineering/data-science/intro-to-nlp/tensorFlow/neural-network/text_classification_keras_neural_network.ipynb
---

# Text Classification Using Neural Network

**Data:** "Movie review" IMDB Dataset

**Steps**
- Load dataset from csv file
- Pre-process data
- Create training and test dataset
- Tokenize the sequences
- Explore the tokenization
- Create a neural network
- Train model and make predictions
- Explore model performance

```python
# importing packages
import matplotlib.pyplot as plt
import io
import os
import re
import shutil
import string
import tensorflow as tf
import pandas as pd
import numpy as np
import timeit, time

from tensorflow.keras import layers
from tensorflow.keras import losses
from tensorflow.keras import preprocessing
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

pd.set_option('display.max_colwidth', None)
%matplotlib inline
```

```python
# reading 50,000 movie reviews labeled as "positive" or "negative"
df = pd.read_csv("./data/IMDB Dataset.csv")
```

```python
# mapping the sentiment (target variable) to numbers
df["sentiment"] = df["sentiment"].map({"positive": 1, "negative":0})
```

```python
# checking first row
df.head(1)
```

```python
# getting the shape of the df
df.shape
```

## Pre-processing the Data

- Convert to lower case
- Remove html tags if found
- Remove puncutations

```python
# definig function to pre-process the data
def preprocess_data(input_data):
    lowercase = input_data.lower()
    stripped_html = lowercase.replace('<br />', ' ')
    retval = re.sub(r'[^\w\s]','', stripped_html)
    return retval
```

```python
# preprocessing the review column
df['review'] = df['review'].map(preprocess_data)
```

```python
# checking first rows
df.head()
```

## Creating Training and Test datasets

```python
# defining train and test dfs
X_train = df["review"].values[:25000]
X_test = df["review"].values[25000:]

y_train = df["sentiment"].values[:25000]
y_test  = df["sentiment"].values[25000:]
```

```python
X_train.shape
```

```python
X_test.shape
```

```python
y_train.shape
```

```python
X_train[0]
```

```python
y_train[0]
```

## Tokenize

```python
# defining hyper parameters that can be modified
vocab_size = 10000
embedding_dim = 16
# for a sentence shorter than max_length it will be padded
# longer sentences will be truncated
max_length = 250
```

```python
# using "Out of Vocabulary" token rather than throwing away unknown words
tokenizer = Tokenizer(num_words=10000, oov_token = "<oov>")
tokenizer.fit_on_texts(X_train)
word_index = tokenizer.word_index
```

```python
# converting words to numbers and pad for the neural network to use as input
# if the sequence length is greater than max length then truncate it at the end
# if the sequence length is less than max length then pad it at the end
train_sequences = tokenizer.texts_to_sequences(X_train)
train_padded = pad_sequences(train_sequences, maxlen=max_length,
                             padding = "post", truncating="post")


# tokenized using the word_index learned from the training data
testing_sequences = tokenizer.texts_to_sequences(X_test)
test_padded = pad_sequences(testing_sequences, maxlen=max_length,
                            padding = "post", truncating="post")
```

```python
train_padded[1]
```

# Explore Tokenization

```python
# reversing keys: keys become the values, and values become the keys so that
# we can look a word up (display padded as ?)
reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])

def decode_review(text):
    return ' '.join([reverse_word_index.get(i, '?') for i in text])

# this is what will be fed in
print(decode_review(train_padded[1]))
```

```python
# this is the original text
print(X_train[1])
```

## Creating Model

**Model Parameters**

`Embedding`

- Embedding layer stores one vector per word
- Converts sequences of word indices to sequences of vectors
- These vectors are trainable
- Once trained, words with similar meanings often have similar vectors
- This approach is more efficient than using a dense layer with one hot encoding

`GlobalAveragePooling1D`

- Returns a fixed length output vector for each example by averaging over the sequence dimension
- Allows the model to handle input of variable length</li>

`Couple of Dense layers`

- Apply the dense layer with ReLU activation</li>

The last output layer use sigmoid to get probability of positive or negative sentiment

```python
# creating model
model = tf.keras.Sequential([
    # the "Embedding" layer is the key to text sentiment analysis
    tf.keras.layers.Embedding(vocab_size, embedding_dim, input_length=max_length),
    tf.keras.layers.GlobalAveragePooling1D(),
    tf.keras.layers.Dense(128, activation = 'relu'),
    tf.keras.layers.Dense(8, activation = 'relu'),
    tf.keras.layers.Dense(1, activation = 'sigmoid')
])
```

```python
# compiling model
model.compile(loss='binary_crossentropy',optimizer='adam',metrics=['accuracy'])
model.summary()
```

```python
# measuring time taken to train the model
start = timeit.default_timer()
```

```python
history = model.fit(train_padded, y_train, epochs=5, validation_split = 0.2)
```

```python
# stopping timer and print training time
stop = timeit.default_timer()
execution_time = stop - start
exectime = time.strftime("%M:%S", time.gmtime(execution_time))
print("To train it took: {} mins".format(exectime))
```

## Explore Embeddings

```python
# checking output from the Embedding layer
embeddings = model.layers[0]
weights = embeddings.get_weights()[0]
print(f"Vocabulary size: {weights.shape[0]},  Embedding dimensions: {weights.shape[1]}")
```

```python
# getting the shape
# (the number of words in the corpus, the embedding dimensions)
weights.shape
```

```python
weights
```

```python
# writing the vectors and their metadata out to file.
# these 2 files ('vecs.tsv', 'meta.tsv') are used by the
# TensorFlow projector (http://projector.tensorflow.org/)
# to plot/visualize the vectors/embeddings in 3D

# outputs the 16 values per word representation (embedding)
#      out_v are the weights (embedding)
#      out_m are the actual words associated with each embedding

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
# plotting
def plot_graphs(history, string):
    plt.plot(history.history[string])
    plt.plot(history.history['val_'+ string])
    plt.xlabel("Epochs")
    plt.ylabel(string)
    plt.legend([string, 'val_'+string])
    plt.show()
```

```python
plot_graphs(history,'accuracy')
```

```python
plot_graphs(history, 'loss')
```

## Evaluating the model

```python
# defining loss and acuracy
test_loss, test_acc = model.evaluate(test_padded, y_test)
print("Test accuracy: ", test_acc)
```

```python
# predicting on a positive sample
sample_text_to_predict = ["The movie was great. The animation and the graphics was excellent. I would recommend this movie."]
train_sequences = tokenizer.texts_to_sequences(sample_text_to_predict)
pos_padded = pad_sequences(train_sequences, maxlen=max_length, padding = "post", truncating="post")

#  making prediction
prediction = model.predict(pos_padded)
print(prediction)
```

```python
# predicting on a negative sample
sample_text_to_predict = ["The movie was horrible. The animation and the graphics were wrost.I would not recommend this movie."]
train_sequences = tokenizer.texts_to_sequences(sample_text_to_predict)
neg_padded = pad_sequences(train_sequences, maxlen=max_length, padding = "post", truncating="post")

#  make prediction
prediction = model.predict(neg_padded)
print(prediction)
```
