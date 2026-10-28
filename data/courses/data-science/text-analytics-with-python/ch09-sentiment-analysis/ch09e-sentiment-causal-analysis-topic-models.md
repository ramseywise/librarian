---
imported_hash: 99a38c09fd883f64
title: Import necessary dependencies
summary: normtrainreviews = tn.normalizecorpus(trainreviews, stopwords=stopwords) normtestreviews = tn.normalizecorpus(testreviews, stopwords=stopwords)
order: 29
kind: notebook
section: Ch09   Sentiment Analysis
source: learn-ai-engineering/data-science/Text Analytics with Python/Ch09 - Sentiment Analysis/Ch09e - Sentiment Causal Analysis - Topic Models.ipynb
---

# Import necessary dependencies

```python
import pandas as pd
import numpy as np
import text_normalizer as tn
import warnings
import nltk

warnings.filterwarnings("ignore")
```

# Load and normalize data

```python
dataset = pd.read_csv(r'movie_reviews.csv')

# take a peek at the data
print(dataset.head())
reviews = np.array(dataset['review'])
sentiments = np.array(dataset['sentiment'])

# build train and test datasets
train_reviews = reviews[:35000]
train_sentiments = sentiments[:35000]
test_reviews = reviews[35000:]
test_sentiments = sentiments[35000:]

# normalize datasets
stop_words = nltk.corpus.stopwords.words('english')
stop_words.remove('no')
stop_words.remove('but')
stop_words.remove('not')

norm_train_reviews = tn.normalize_corpus(train_reviews, stopwords=stop_words)
norm_test_reviews = tn.normalize_corpus(test_reviews, stopwords=stop_words)
```

# Extract features from positive and negative reviews

```python
from sklearn.feature_extraction.text import TfidfVectorizer

# consolidate all normalized reviews
norm_reviews = norm_train_reviews+norm_test_reviews
# get tf-idf features for only positive reviews
positive_reviews = [review for review, sentiment in zip(norm_reviews, sentiments) if sentiment == 'positive']
ptvf = TfidfVectorizer(use_idf=True, min_df=0.02, max_df=0.75, ngram_range=(1, 2), sublinear_tf=True)
ptvf_features = ptvf.fit_transform(positive_reviews)
# get tf-idf features for only negative reviews
negative_reviews = [review for review, sentiment in zip(norm_reviews, sentiments) if sentiment == 'negative']
ntvf = TfidfVectorizer(use_idf=True, min_df=0.02, max_df=0.75, ngram_range=(1, 2), sublinear_tf=True)
ntvf_features = ntvf.fit_transform(negative_reviews)
# view feature set dimensions
print(ptvf_features.shape, ntvf_features.shape)
```

# Topic Modeling on Reviews

```python
import pyLDAvis
import pyLDAvis.sklearn
from sklearn.decomposition import NMF
import topic_model_utils as tmu

pyLDAvis.enable_notebook()
total_topics = 10
```

## Display and visualize topics for positive reviews

```python
# build topic model on positive sentiment review features
pos_nmf = NMF(n_components=total_topics, solver='cd', max_iter=500,
               random_state=42, alpha=.1, l1_ratio=.85)
pos_nmf.fit(ptvf_features)
# extract features and component weights
pos_feature_names = np.array(ptvf.get_feature_names())
pos_weights = pos_nmf.components_
# extract and display topics and their components
pos_feature_names = np.array(ptvf.get_feature_names())
feature_idxs = np.argsort(-pos_weights)[:, :15]
topics = [pos_feature_names[idx] for idx in feature_idxs]
for idx, topic in enumerate(topics):
    print('Topic #'+str(idx+1)+':')
    print(', '.join(topic))
    print()
```

```python
pyLDAvis.sklearn.prepare(pos_nmf, ptvf_features, ptvf, mds='mmds')
```

## Display and visualize topics for negative reviews

```python
# build topic model on negative sentiment review features
neg_nmf = NMF(n_components=total_topics, solver='cd', max_iter=500,
              random_state=42, alpha=.1, l1_ratio=.85)
neg_nmf.fit(ntvf_features)
# extract features and component weights
neg_feature_names = ntvf.get_feature_names()
neg_weights = neg_nmf.components_
# extract and display topics and their components
neg_feature_names = np.array(ntvf.get_feature_names())
feature_idxs = np.argsort(-neg_weights)[:, :15]
topics = [neg_feature_names[idx] for idx in feature_idxs]
for idx, topic in enumerate(topics):
    print('Topic #'+str(idx+1)+':')
    print(', '.join(topic))
    print()
```

```python
pyLDAvis.sklearn.prepare(neg_nmf, ntvf_features, ntvf, mds='mmds')
```
