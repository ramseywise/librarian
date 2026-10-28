---
imported_hash: 530493e58e3e48fb
title: TensorFlow - Neural Network (NLP)
summary: from tensorflow import keras from tensorflow.keras.preprocessing.text import Tokenizer from tensorflow.keras.preprocessing.sequence import padsequences from sklearn.linearmodel import LogisticRegression from sklearn.svm import SVC
order: 12
kind: notebook
section: tensorFlow / Neural network
source: learn-ai-engineering/data-science/intro-to-nlp/tensorFlow/neural-network/tensorFlow_neural_network_nlp.ipynb
---

# TensorFlow - Neural Network (NLP)

```python
# importing packages
import json
import numpy as np
import tensorflow as tf
import pandas as pd
import matplotlib.pyplot as plt

from tensorflow import keras
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
```

### Sarcasm data

```python
# reading data
with open("./data/sarcasm.json", 'r') as f:
    datastore = json.load(f)

sentences = []
labels = []

for item in datastore:
    sentences.append(item["headline"])
    labels.append(item["is_sarcastic"])
```

### Train/Test Split

```python
# checking number of sentences
len(sentences)
```

```python
# defining training and testing sets
data_size = 20000
training_sentences = sentences[0:data_size]
testing_sentences = sentences[data_size:]
training_labels = np.array(labels[0:data_size])
testing_labels = np.array(labels[data_size:])
```

### Hyperparameters

```python
# modifying the hyperparameters for tuning the model
vocab_size = 10000
embedding_dim = 16
max_length = 32
trunc_type = "post"
padding_type = "post"
oov_token = "<oov>"
```

### Tokenize

```python
# defining tokenizer
tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
tokenizer.fit_on_texts(training_sentences)
word_index = tokenizer.word_index

training_sequences = tokenizer.texts_to_sequences(training_sentences)
training_padded = pad_sequences(training_sequences, maxlen=max_length,
                                padding=padding_type, truncating=trunc_type)

testing_sequences = tokenizer.texts_to_sequences(testing_sentences)
testing_padded = pad_sequences(testing_sequences, maxlen=max_length,
                                padding=padding_type, truncating=trunc_type)
```

```python
# checking shape
training_padded[0].shape
```

## Create a Linear Model

```python
# creating model
log_reg = LogisticRegression(solver="lbfgs")
log_reg.fit(training_padded, training_labels)
```

```python
# checking score
log_reg.score(testing_padded, testing_labels)
```

```python
# creating model using support vector classification
svm = SVC(kernel='rbf', gamma="auto")
svm.fit(training_padded, training_labels)
```

```python
# checking score
svm.score(testing_padded, testing_labels)
```

## Create the Neural Network

```python
# creating a neural network
model = keras.Sequential([
    keras.layers.Flatten(),
    keras.layers.Dense(256, activation='relu'),
    keras.layers.Dense(1, activation='sigmoid')])
```

```python
# compiling model
model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])
```

### Train the model

```python
# training model
history = model.fit(training_padded, training_labels,
                    validation_data=(testing_padded, testing_labels),
                    epochs=5)
```

```python
# plotting learning curves
pd.DataFrame(history.history).plot(figsize=(8, 5))
plt.grid(True)
plt.gca().set_ylim(0, 1)
plt.show()
```

### Plot the loss

```python
# creating a function to plot
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
