---
imported_hash: f84b9168506173f7
title: Build your own NER Tagger
summary: Named Entity Recognition (NER) , also known as entity chunking/extraction , is a popular technique used in information extraction to identify and segment the named entities and classify or categorize them under various predefined classes.
order: 23
kind: notebook
section: Ch08   Semantic Analysis
source: learn-ai-engineering/data-science/Text Analytics with Python/Ch08 - Semantic Analysis/Ch08c - Building NER Taggers.ipynb
---

# Build your own NER Tagger

__Named Entity Recognition (NER)__ , also known as entity chunking/extraction , is a popular technique used in information extraction to identify and segment the named entities and classify or categorize them under various predefined classes.

There are various off the shelf solutions which offer capabilites to perform named entity extraction (some of which we discussed in the previous units). Yet there are times when the requirements are beyond the capabilities of off-the-shelf classifiers.

In this notebook, we will go through an exercise to build our own NER using Conditional Random Fields.
We would be utilizing ```sklearn_crfsuite``` to develop our NER.

## Load Dataset

Named Entity Recognition is a sequence modeling problem at it's core. It is more related to classification class of problems where in we need a labeled dataset to train a classifier.

There are various labeled datasets for NER class of problems. We would be utilizing a pre-processed version of __GMB(Groningen Meaning Bank) corpus__ for this notebook. The preprocessed version is availble at the following link : [kaggle/ner](https://www.kaggle.com/abhinavwalia95/entity-annotated-corpus)

We have provided the dataset in the code repository itself using some intelligent compression and you can access it directly from `pandas` as follows.

```python
import pandas as pd

df = pd.read_csv('ner_dataset.csv.gz', compression='gzip', encoding='ISO-8859-1')
df.info()
```

```python
df.T
```

```python
df = df.fillna(method='ffill')
df.info()
```

```python
df.T
```

```python
df['Sentence #'].nunique(), df.Word.nunique(), df.POS.nunique(), df.Tag.nunique()
```

We have 47959 sentences that contain 35178 unique words.

These sentences have a total of 42 unique POS tags and 17 unique NER tags in total.

## Tag Distribution

The GMB dataset utilizes IOB tagging or _Inside, Outside Beginning_. IOB is a common tagging format for tagging tokens which we have discussed earlier. To refresh your memory:

+ __I- prefix__ before a tag indicates that the tag is inside a chunk.
+ __B- prefix__ before a tag indicates that the tag is the beginning of a chunk.
+ __O-  tag__ indicates that a token belongs to no chunk (outside).

The tags in this dataset are explained as follows:

+ __geo__ = Geographical Entity
+ __org__ = Organization
+ __per__ = Person
+ __gpe__ = Geopolitical Entity
+ __tim__ = Time indicator
+ __art__ = Artifact
+ __eve__ = Event
+ __nat__ = Natural Phenomenon

Anything outside these classes is termed as other, denoted as __O__.

The following output shows the unbalanced distribution of different tags in the dataset

```python
df.Tag.value_counts()
```

## Conditional Random Fields

As mentioned above, NER belongs to sequence modeling class of problems. There are different algorithms to tackle sequence modeling, __CRF__ or _Conditional Random Fields_ are one such example. CRFs are proven to perform extremely well on NER and related domains. In this notebook, we will attempt at developing our own NER based on CRFs.

---

__Question__: What is a CRF and how does it work?

__Wikipedia__ :  CRF is an undirected graphical model whose nodes can be divided into exactly two disjoint sets $X$ and $Y$, the observed and output variables, respectively; the conditional distribution $p(Y|X)$ is then modeled.

For more details, checkout the paper [__Conditional Random Fields: Probabilistic Models
for Segmenting and Labeling Sequence Data__](https://repository.upenn.edu/cgi/viewcontent.cgi?article=1162&context=cis_papers)

## Prepare Data

CRF trains upon sequence of input data to learn transitions from one state (label) to another.
To enable such an algorithm, we need to define features which take into account different transitions.
In the function ```word2features()``` below, we transform each word into a feature dictionary depicting the following attributes or features:

+ lower case of word
+ suffix containing last 3 characters
+ suffix containing last 2 characters
+ flags to determine upper-case, title-case, numeric data and POS tag

We also attach attributes related to previous and next words or tags to determine beginning of sentence (BOS) or end of sentence (EOS)

```python
def word2features(sent, i):
    word = sent[i][0]
    postag = sent[i][1]

    features = {
        'bias': 1.0,
        'word.lower()': word.lower(),
        'word[-3:]': word[-3:],
        'word[-2:]': word[-2:],
        'word.isupper()': word.isupper(),
        'word.istitle()': word.istitle(),
        'word.isdigit()': word.isdigit(),
        'postag': postag,
        'postag[:2]': postag[:2],
    }
    if i > 0:
        word1 = sent[i-1][0]
        postag1 = sent[i-1][1]
        features.update({
            '-1:word.lower()': word1.lower(),
            '-1:word.istitle()': word1.istitle(),
            '-1:word.isupper()': word1.isupper(),
            '-1:postag': postag1,
            '-1:postag[:2]': postag1[:2],
        })
    else:
        features['BOS'] = True

    if i < len(sent)-1:
        word1 = sent[i+1][0]
        postag1 = sent[i+1][1]
        features.update({
            '+1:word.lower()': word1.lower(),
            '+1:word.istitle()': word1.istitle(),
            '+1:word.isupper()': word1.isupper(),
            '+1:postag': postag1,
            '+1:postag[:2]': postag1[:2],
        })
    else:
        features['EOS'] = True

    return features


def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def sent2labels(sent):
    return [label for token, postag, label in sent]
```

```python
agg_func = lambda s: [(w, p, t) for w, p, t in zip(s['Word'].values.tolist(),
                                                   s['POS'].values.tolist(),
                                                   s['Tag'].values.tolist())]
```

```python
grouped_df = df.groupby('Sentence #').apply(agg_func)
```

```python
print(grouped_df[grouped_df.index == 'Sentence: 1'].values)
```

```python
grouped_df.shape
```

```python
sentences = [s for s in grouped_df]
sentences[0]
```

```python
sent2features(sentences[0][5:7])
```

```python
sent2labels(sentences[0][5:7])
```

## Prepare Train and Test Datasets

```python
from sklearn.model_selection import train_test_split
import numpy as np

X = np.array([sent2features(s) for s in sentences])
y = np.array([sent2labels(s) for s in sentences])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
X_train.shape, X_test.shape
```

# Building Models with sklearn-crfsuite

__`sklearn-crfsuite`__ is a thin [CRFsuite (python-crfsuite)](https://github.com/scrapinghub/python-crfsuite) wrapper which provides scikit-learn-compatible sklearn_crfsuite.CRF estimator: you can use e.g. scikit-learn model selection utilities (cross-validation, hyperparameter optimization) with it, or save/load CRF models using joblib.

```python
!pip install sklearn-crfsuite
```

# Train the model!

Train the model using the default configurations mentioned in the [sklearn-crfsuite API docs](https://sklearn-crfsuite.readthedocs.io/en/latest/api.html)


- __algorithm:__ the training algorithm. We use [L-BFGS](https://en.wikipedia.org/wiki/Limited-memory_BFGS) for gradient descent for optimization and getting model parameters
- __c1:__ Coefficient for Lasso (L1) regularization
- __c2:__ Coefficient for Ridge (L2) regularization
- __all_possible_transitions:__ Specify whether CRFsuite generates transition features that do not even occur in the training data


__Note:__ If the model is taking too long to train, you can load up the pre-trained model using the code after the training cells and use that for predictions.

```python
import sklearn_crfsuite

crf = sklearn_crfsuite.CRF(algorithm='lbfgs',
                           c1=0.1,
                           c2=0.1,
                           max_iterations=100,
                           all_possible_transitions=True,
                           verbose=True)
```

```python
crf.fit(X_train, y_train)
```

## Use the following to load our pre-trained model if training above takes a lot of time

```python
from sklearn.externals import joblib

#joblib.dump(crf, 'ner_model.pkl')
```

```python
crf = joblib.load('ner_model.pkl')
```

# Model Evaluation

Let's evaluate our model performance for NER Tagging on the test data now!

Try playing around with the following cells and observe the overall model performance.

We use standard classification metrics like precision, recall and f1-score

```python
y_pred = crf.predict(X_test)
print(y_pred[0])
```

```python
print(y_test[0])
```

```python
from sklearn_crfsuite import metrics as crf_metrics

labels = list(crf.classes_)
labels.remove('O')
```

```python
print(crf_metrics.flat_classification_report(y_test, y_pred, labels=labels))
```

We have intentially left out the ___Others___ tag to understand the performance of model on the remaining tags. The above evaluation statistics showcase a model which seems to have learnt the transitions quite well giving us an overall F1-score of 85%!

We can achieve even better results by fine tuning the feature engineering step along with hyper-parameter tuning.

## End-to-End NER Tagger with trained NER Model

There is no fun (or value!) if we cannot use our model to tag new sentences in the future assuming we would want to put this model in production. Let's try and build an end-to-end workflow to perform NER Tagging on our sample document. First we perform NER tagging with SpaCy to remind you how it looks like.

### Prepare Sample Document

```python
import re

text = """Three more countries have joined an “international grand committee” of parliaments, adding to calls for
Facebook’s boss, Mark Zuckerberg, to give evidence on misinformation to the coalition. Brazil, Latvia and Singapore
bring the total to eight different parliaments across the world, with plans to send representatives to London on 27
November with the intention of hearing from Zuckerberg. Since the Cambridge Analytica scandal broke, the Facebook chief
has only appeared in front of two legislatures: the American Senate and House of Representatives, and the European parliament.
Facebook has consistently rebuffed attempts from others, including the UK and Canadian parliaments, to hear from Zuckerberg.
He added that an article in the New York Times on Thursday, in which the paper alleged a pattern of behaviour from Facebook
to “delay, deny and deflect” negative news stories, “raises further questions about how recent data breaches were allegedly
dealt with within Facebook.”
"""

text = re.sub(r'\n', '', text)
text
```

### NER Tagging with SpaCy

```python
import spacy
from spacy import displacy

nlp = spacy.load('en')
text_nlp = nlp(text)
displacy.render(text_nlp, style='ent', jupyter=True)
```

### Pipeline Step 1

- Tokenize Text
- POS Tagging

```python
import nltk

text_tokens = nltk.word_tokenize(text)
text_pos = nltk.pos_tag(text_tokens)
text_pos[:10]
```

### Pipeline Step 2
- Extract Features from the POS tagged text document
- Hint: Use `sent2features`

```python
features = [sent2features(text_pos)]
features[0][0]
```

### Pipeline Step 3
- Use the CRF Model `crf` to predict on the features

```python
labels = crf.predict(features)
doc_labels = labels[0]
doc_labels[10:20]
```

### Pipeline Step 4
- Combine text tokens with NER Tags
- Retrieve relevant named entities from NER Tags

```python
text_ner = [(token, tag) for token, tag in zip(text_tokens, doc_labels)]
print(text_ner)
```

```python
named_entities = []
temp_entity_name = ''
temp_named_entity = None
for term, tag in text_ner:
    if tag != 'O':
        temp_entity_name = ' '.join([temp_entity_name, term]).strip()
        temp_named_entity = (temp_entity_name, tag)
    else:
        if temp_named_entity:
            named_entities.append(temp_named_entity)
            temp_entity_name = ''
            temp_named_entity = None
```

```python
import pandas as pd

pd.DataFrame(named_entities, columns=['Entity', 'Tag'])
```
