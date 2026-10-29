---
imported_hash: 3863d74207c96e15
title: Recurrent Neural Network
summary: from tensorflow.keras.preprocessing.text import Tokenizer from tensorflow.keras.preprocessing.sequence import pad_sequences
order: 8
kind: notebook
section: tensorFlow / Neural network
source: learn-ai-engineering/data-science/intro-to-nlp/tensorFlow/neural-network/tensorFlow-RNN-LSTM-sentiment-analysis.ipynb
---

# Recurrent Neural Network

```python
# importing packages & libraries
import tensorflow as tf
import pandas as pd
import matplotlib.pyplot as plt

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

%matplotlib inline
```

## Get IMdb data

```python
# reading and processing data
imdb_data = pd.read_csv("./data/IMDB Dataset.csv")
imdb_data["sentiment"] = imdb_data["sentiment"].map({"positive": 1, "negative":0})
```

```python
# defining train and test data sets
imdb_train = imdb_data["review"].values[:25000]
imdb_test = imdb_data["review"].values[25000:]

imdb_train_labels = imdb_data["sentiment"].values[:25000]
imdb_test_labels = imdb_data["sentiment"].values[25000:]
```

```python
# checking train data
imdb_train[0]
```

## Hyperparameters

```python
# listing hyperparameters makes it easier to quickly test different combinations
# a shorter sentence than max_length it will be padded, longer sentences will be truncated
vocab_size = 10000
embedding_dim = 16
max_length = 120
```

## Tokenize

```python
# defining tokenizer
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

### Simple RNN

```python
# creasting model
embedding_dim = 64

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embedding_dim),
    tf.keras.layers.SimpleRNN(256),
    tf.keras.layers.Dense(1, activation = 'sigmoid')])

model.summary()
```

```python
# compiling model
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
```

### Train the model

```python
# training model
num_epochs = 5
history = model.fit(train_padded, imdb_train_labels, epochs=num_epochs,
                    validation_data=(test_padded, imdb_test_labels), validation_steps=30)
```

### Make predictions on text samples

```python
# predicting on a positive sample
sample_text_to_predict = ["The movie was cool. The animation and the graphics were out of this world. I would recommend this movie."]
train_sequences = tokenizer.texts_to_sequences(sample_text_to_predict)
pos_padded = pad_sequences(train_sequences, maxlen=20, truncating="post")

# making prediction
prediction = model.predict(pos_padded)
print(prediction)
```

```python
# predicting on a negative sample
sample_text_to_predict = ["The movie was not good. The animation and the graphics were terrible. I would not recommend this movie."]
train_sequences = tokenizer.texts_to_sequences(sample_text_to_predict)
neg_padded = pad_sequences(train_sequences, maxlen=20, truncating="post")

# making prediction
prediction = model.predict(neg_padded)
print(prediction)
```

### Plot Learning curves

```python
# defining plot function
def plot_graphs(history, string):
    plt.plot(history.history[string])
    plt.plot(history.history['val_'+ string])
    plt.xlabel("Epochs")
    plt.ylabel(string)
    plt.legend([string, 'val_'+string])
    plt.show()

plot_graphs(history,'accuracy')
plot_graphs(history, 'loss')
```

## LSTM

```python
# creating model
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, 64),
    tf.keras.layers.LSTM(64),
    tf.keras.layers.Dense(64, activation = 'relu'),
    tf.keras.layers.Dense(1, activation = 'sigmoid')])

model.summary()
```

```python
# compiling model
model.compile(loss='binary_crossentropy',
              optimizer=tf.keras.optimizers.Adam(1e-4),
              metrics=['accuracy'])
```

### Train the model

```python
# training model
epochs_num = 5
history = model.fit(train_padded, imdb_train_labels, epochs=epochs_num,
                    validation_data=(test_padded, imdb_test_labels),
                    validation_steps=30)
```

### Make predictions on text samples

```python
# predicting on a positive sample
sample_text_to_predict = ["The movie was cool. The animation and the graphics were out of this world. I would recommend this movie."]
train_sequences = tokenizer.texts_to_sequences(sample_text_to_predict)
pos_padded = pad_sequences(train_sequences, maxlen=20, truncating="post")

# making prediction
prediction = model.predict(pos_padded)
print(prediction)
```

```python
# predicting on a negative sample
sample_text_to_predict = ["The movie was not good. The animation and the graphics were terrible. I would not recommend this movie."]
train_sequences = tokenizer.texts_to_sequences(sample_text_to_predict)
neg_padded = pad_sequences(train_sequences, maxlen=20, truncating="post")

# making prediction
prediction = model.predict(neg_padded)
print(prediction)
```

### Plot learning curves

```python
# plotting loss and accuracy
plot_graphs(history, 'accuracy')
plot_graphs(history, 'loss')
```

### Experimenting the LSTM model

```python
# creating reviews
positive_review = ["The movie was cool. The animation and the graphics were out of this world. I would recommend this movie."]
negative_review = ["The movie was not good. The animation and the graphics were terrible. I would not recommend this movie."]
```

### Test your models on the positive review

```python
# predicting on a positive review
train_sequences = tokenizer.texts_to_sequences(positive_review)
pos_padded = pad_sequences(train_sequences, maxlen=20, truncating="post")

# making prediction
prediction = model.predict(pos_padded)
print(prediction)
```

### Test your models on the negative review

```python
# predicting on a negative review
train_sequences = tokenizer.texts_to_sequences(negative_review)
pos_padded = pad_sequences(train_sequences, maxlen=20, truncating="post")

# making prediction
prediction = model.predict(pos_padded)
print(prediction)
```
