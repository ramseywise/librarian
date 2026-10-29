---
imported_hash: 0a3d0504a1bf3365
title: Import necessary dependencies
summary: stop_words = nltk.corpus.stopwords.words('english') stop_words.remove('no') stop_words.remove('but') stop_words.remove('not')
order: 28
kind: notebook
section: Ch09   Sentiment Analysis
source: learn-ai-engineering/data-science/Text Analytics with Python/Ch09 - Sentiment Analysis/Ch09d - Sentiment Causal Analysis - Model Interpretation.ipynb
---

# Import necessary dependencies

```python
import pandas as pd
import numpy as np
import text_normalizer as tn
import nltk

stop_words = nltk.corpus.stopwords.words('english')
stop_words.remove('no')
stop_words.remove('but')
stop_words.remove('not')
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
norm_train_reviews = tn.normalize_corpus(train_reviews, stopwords=stop_words)
norm_test_reviews = tn.normalize_corpus(test_reviews, stopwords=stop_words)
```

# Build Text Classification Pipeline with The Best Model

```python
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import warnings
warnings.filterwarnings("ignore")

# build BOW features on train reviews
cv = CountVectorizer(binary=False, min_df=0.0, max_df=1.0, ngram_range=(1,2))
cv_train_features = cv.fit_transform(norm_train_reviews)
# build Logistic Regression model
lr = LogisticRegression()
lr.fit(cv_train_features, train_sentiments)

# Build Text Classification Pipeline
lr_pipeline = make_pipeline(cv, lr)

# save the list of prediction classes (positive, negative)
classes = list(lr_pipeline.classes_)
```

# Analyze Model Prediction Probabilities

```python
new_corpus = ['The Lord of the Rings is an Excellent movie!',
              'I didn\'t like the recent movie on TV. It was NOT good and a waste of time!']
norm_new_corpus = tn.normalize_corpus(new_corpus, stopwords=stop_words)
norm_new_corpus
```

```python
lr_pipeline.predict(norm_new_corpus)
```

```python
pd.DataFrame(lr_pipeline.predict_proba(norm_new_corpus), columns=classes)
```

# Interpreting Model Decisions

```python
from skater.core.local_interpretation.lime.lime_text import LimeTextExplainer

explainer = LimeTextExplainer(class_names=classes)
def interpret_classification_model_prediction(doc_index, norm_corpus, corpus,
                                              prediction_labels, explainer_obj):
    # display model prediction and actual sentiments
    print("Test document index: {index}\nActual sentiment: {actual}\nPredicted sentiment: {predicted}"
      .format(index=doc_index, actual=prediction_labels[doc_index],
              predicted=lr_pipeline.predict([norm_corpus[doc_index]])))
    # display actual review content
    print("\nReview:", corpus[doc_index])
    # display prediction probabilities
    print("\nModel Prediction Probabilities:")
    for probs in zip(classes, lr_pipeline.predict_proba([norm_corpus[doc_index]])[0]):
        print(probs)
    # display model prediction interpretation
    exp = explainer.explain_instance(norm_corpus[doc_index],
                                     lr_pipeline.predict_proba, num_features=10,
                                     labels=[1])
    exp.show_in_notebook()
```

```python
doc_index = 100
interpret_classification_model_prediction(doc_index=doc_index, norm_corpus=norm_test_reviews,
                                         corpus=test_reviews, prediction_labels=test_sentiments,
                                         explainer_obj=explainer)
```

```python
doc_index = 2000
interpret_classification_model_prediction(doc_index=doc_index, norm_corpus=norm_test_reviews,
                                         corpus=test_reviews, prediction_labels=test_sentiments,
                                         explainer_obj=explainer)
```

```python
doc_index = 347
interpret_classification_model_prediction(doc_index=doc_index, norm_corpus=norm_test_reviews,
                                         corpus=test_reviews, prediction_labels=test_sentiments,
                                         explainer_obj=explainer)
```
