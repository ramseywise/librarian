---
imported_hash: eb1454fc63e600c7
title: TensorFlow Neural Network (NLP)
summary: The number of neurons in the hidden layer.
order: 13
kind: notebook
section: tensorFlow / Neural network
source: learn-ai-engineering/data-science/intro-to-nlp/tensorFlow/neural-network/tensorFlow_neural_network_nlp_exercise.ipynb
---

# TensorFlow Neural Network (NLP)

**Scenario:** Trainning a model to classify the sentiment of the sentences. Each sentence has been tokenized, and is padded or truncated to be length 25. Each sentence's sentiment is categorized as either "happy", "sad" or "neutral".

```python
# importing packages
from tensorflow import keras
```

### 1)  Model to be trained

```python
model = keras.Sequential([
    keras.layers.Flatten(input_shape=(25,)),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(3, activation='softmax')])
```

### 2)  What does the 128 in the Dense layer mean?

The number of neurons in the hidden layer.

### 3) How many features are input into the neural network mentioned above?

25

### 4) Given the following softmax output, which of the classes listed in the description above would the model predict?
[.516, .081, .403]

"happy"

### 5) Rewrite the model in question #1 above, but add an additional hidden layer.

```python
model = keras.Sequential([
    keras.layers.Flatten(input_shape=(25,)),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dense(3, activation='softmax')])
```

### 6) In the code below, what is an epoch?

model.fit(training_images, training_labels, epochs=5)

The number of times the model trains through the full dataset.
