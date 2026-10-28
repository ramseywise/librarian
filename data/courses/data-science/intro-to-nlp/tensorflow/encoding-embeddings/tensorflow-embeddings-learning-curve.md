---
imported_hash: 2823a4f6ec8466cf
title: Word Embeddings - Learning Curve
summary: from tensorflow.keras.preprocessing.text import Tokenizer from tensorflow.keras.preprocessing.sequence import padsequences
order: 4
kind: notebook
section: tensorFlow / Encoding embeddings
source: learn-ai-engineering/data-science/intro-to-nlp/tensorFlow/encoding-embeddings/tensorFlow_embeddings_learning_curve.ipynb
---

# Word Embeddings - Learning Curve

```python
# importing packages
import json
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
```

### Sarcasm data

```python
# reading data
with open("./data/sarcasm.json", 'r') as f:
    data = json.load(f)

sentences = []
labels = []

for item in data:
    sentences.append(item["headline"])
    labels.append(item["is_sarcastic"])
```

```python
# checking sentences
sentences[:2]
```

```python
# checking labels
labels[:2]
```

### Train/Test Split

```python
# getting len of sentences
len(sentences)
```

```python
# defining training and testing data sets
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

Individual linguistic units.

```python
# tokenizing data
tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
tokenizer.fit_on_texts(training_sentences)
word_index = tokenizer.word_index

# converting words to numbers and pad for the neural network to use as input
training_sequences = tokenizer.texts_to_sequences(training_sentences)
training_padded = pad_sequences(training_sequences, maxlen=max_length,
                                padding=padding_type, truncating=trunc_type)

# tokenized using the word_index learned from the training data
testing_sequences = tokenizer.texts_to_sequences(testing_sentences)
testing_padded = pad_sequences(testing_sequences, maxlen=max_length,
                                padding=padding_type, truncating=trunc_type)
```

### Create the model

```python
# creating model
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, embedding_dim, input_length=max_length),
    tf.keras.layers.GlobalAveragePooling1D(),
    #tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(24, activation = 'relu'),
    tf.keras.layers.Dense(1, activation = 'sigmoid')
])

model.compile(loss='binary_crossentropy',optimizer='adam',metrics=['accuracy'])
model.summary()
```

### Train the model

```python
# training model
history = model.fit(training_padded, training_labels, epochs=3,
                    validation_data=(testing_padded, testing_labels), verbose=2)
```

### Plot the loss

```python
# function to plot
def plot_graphs(history, string):
    plt.plot(history.history[string])
    plt.plot(history.history['val_'+ string])
    plt.title('Training and validation')
    plt.xlabel('Epochs')
    plt.ylabel(string)
    plt.legend([string, 'val_'+ string])
    plt.show()

plot_graphs(history, "accuracy")
plot_graphs(history, "loss")
```
