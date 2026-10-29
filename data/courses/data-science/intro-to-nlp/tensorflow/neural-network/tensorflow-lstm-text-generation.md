---
imported_hash: 5b7edb080bb777f7
title: Text Generation
summary: from tensorflow.keras.preprocessing.sequence import pad_sequences from tensorflow.keras.layers import Embedding, LSTM, Dense, Bidirectional from tensorflow.keras.preprocessing.text import Tokenizer from tensorflow.keras.models import Sequen…
order: 10
kind: notebook
section: tensorFlow / Neural network
source: learn-ai-engineering/data-science/intro-to-nlp/tensorFlow/neural-network/tensorFlow_LSTM_text_generation.ipynb
---

# Text Generation

```python
# importing packages & libraries
import tensorflow as tf
import numpy as np

from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Embedding, LSTM, Dense, Bidirectional
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
```

## Get reference corpus

```python
# reading and processing data
data = open('./data/irish-lyrics.txt').read()
corpus = data.lower().split("\n")
```

```python
# defining tokenizer
tokenizer = Tokenizer()
tokenizer.fit_on_texts(corpus)
total_words = len(tokenizer.word_index) + 1

# print(tokenizer.word_index)
print(total_words)
```

## Preprocess

```python
# preprocessing data
input_sequences = []
for line in corpus:
    token_list = tokenizer.texts_to_sequences([line])[0]
    for i in range(1, len(token_list)):
        n_gram_sequence = token_list[:i+1]
        input_sequences.append(n_gram_sequence)

# padding sequences
max_sequence_len = max([len(x) for x in input_sequences])
input_sequences = np.array(pad_sequences(input_sequences, maxlen=max_sequence_len, padding='pre'))

# creating predictors and label
xs, labels = input_sequences[:,:-1],input_sequences[:,-1]

ys = tf.keras.utils.to_categorical(labels, num_classes=total_words)
```

## Create LSTM Model

```python
# creating model
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(total_words, 100, input_length=max_sequence_len-1),
    tf.keras.layers.Bidirectional(LSTM(150)),
    tf.keras.layers.Dense(total_words, activation = 'softmax'),
])

model.compile(loss='categorical_crossentropy',
              optimizer= 'adam',
              metrics=['accuracy'])
```

```python
# training model
history = model.fit(xs, ys, epochs=10, verbose=1)
```

## Generate text sequences

```python
# generating text
seed_text = "I too am a human being and I"
# seed_text = "I've got a bad feeling about this"
next_words = 100

for _ in range(next_words):
    token_list = tokenizer.texts_to_sequences([seed_text])[0]
    token_list = pad_sequences([token_list], maxlen=max_sequence_len-1, padding='pre')
    predicted = model.predict_classes(token_list, verbose=0)
    output_word = ""
    for word, index in tokenizer.word_index.items():
        if index == predicted:
            output_word = word
            break
    seed_text += " " + output_word
print(seed_text)
```
