---
imported_hash: f9efd088578ce2f6
title: Neural Network Embeddings - Exercise
summary: from tensorflow.keras.preprocessing.text import Tokenizer from tensorflow.keras.preprocessing.sequence import padsequences
order: 11
kind: notebook
section: tensorFlow / Neural network
source: learn-ai-engineering/data-science/intro-to-nlp/tensorFlow/neural-network/tensorFlow_neural_network_embeddings_exercise.ipynb
---

# Neural Network Embeddings - Exercise

```python
# importing packages
import tensorflow as tf
import pandas as pd
import matplotlib.pyplot as plt

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
```

### Tweet Emotion data

This is a dataset of 40,000 tweets labeled with one of 13 emotions:
['empty', 'sadness', 'enthusiasm', 'neutral', 'worry', 'surprise',
      'love', 'fun', 'hate', 'happiness', 'boredom', 'relief', 'anger']

Tokenize the data and train it, with a neural network, to  predict the category of a given tweet.

```python
# reading data
text_data = pd.read_csv("./data/text_emotion.csv")

# transforming string labels to integers
text_data["sentiment"] = text_data["sentiment"].map({'empty':0, 'sadness':1, 'enthusiasm':2, 'neutral':3, 'worry':4, 'surprise':5,'love':6, 'fun':7, 'hate':8, 'happiness':9, 'boredom':10, 'relief':11, 'anger':12})

# defining data sets for train and test
train_text = text_data["content"].values[:20000]
test_text = text_data["content"].values[20000:]

# defining labels labels sets
train_text_labels = text_data["sentiment"].values[:20000]
test_text_labels = text_data["sentiment"].values[20000:]
```

```python
# checking tweets
print(train_text[:5])
```

### Hyperparameters

```python
# creating a list of hyperparameters for tuning the model
vocab_size = 10000
embedding_dim = 16
max_length = 32
trunc_type = "post"
padding_type = "post"
oov_token = "<oov>"
```

### Tokenize the dataset

```python
# defining tokenizer
tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
tokenizer.fit_on_texts(train_text)

word_index = tokenizer.word_index

training_sequences = tokenizer.texts_to_sequences(train_text)
training_padded = pad_sequences(training_sequences, maxlen=max_length,
                                padding=padding_type, truncating=trunc_type)

testing_sequences = tokenizer.texts_to_sequences(test_text)
testing_padded = pad_sequences(testing_sequences, maxlen=max_length,
                                padding=padding_type, truncating=trunc_type)
```

### Creating a Neural Network with embeddings

```python
# creating the model
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embedding_dim, input_length=max_length),
    tf.keras.layers.GlobalAveragePooling1D(),
    tf.keras.layers.Dense(24, activation = 'relu'),
    tf.keras.layers.Dense(13, activation = 'softmax')
])

model.compile(loss='sparse_categorical_crossentropy',optimizer='adam',metrics=['accuracy'])
model.summary()
```

### Trainning the model

```python
# training the model
history = model.fit(training_padded, train_text_labels, epochs=30,
                    validation_data=(testing_padded, test_text_labels), verbose=2)
```

### Plotting the loss

```python
# creating a fucntion to plot loss and accuracy
def plot_graphs(history, string):
    plt.plot(history.history[string])
    plt.plot(history.history['val_'+string])
    plt.title('Training and validation')
    plt.xlabel('Epochs')
    plt.ylabel(string)
    plt.legend([string, 'val_'+string])
    plt.show()

plot_graphs(history, "accuracy")
plot_graphs(history, "loss")
```
