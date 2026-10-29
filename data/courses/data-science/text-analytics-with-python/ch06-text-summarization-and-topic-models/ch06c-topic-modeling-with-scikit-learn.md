---
imported_hash: ee60342360803f4b
title: Load and Pre-process Data
summary: DATA_PATH = 'nipstxt/' print(os.listdir(DATA_PATH))
order: 15
kind: notebook
section: Ch06   Text Summarization and Topic Models
source: learn-ai-engineering/data-science/Text Analytics with Python/Ch06 - Text Summarization and Topic Models/Ch06c - Topic Modeling with scikit-learn.ipynb
---

# Load and Pre-process Data

```python
import os
import numpy as np
import pandas as pd

DATA_PATH = 'nipstxt/'
print(os.listdir(DATA_PATH))
```

```python
folders = ["nips{0:02}".format(i) for i in range(0,13)]
# Read all texts into a list.
papers = []
for folder in folders:
    file_names = os.listdir(DATA_PATH + folder)
    for file_name in file_names:
        with open(DATA_PATH + folder + '/' + file_name, encoding='utf-8', errors='ignore', mode='r+') as f:
            data = f.read()
        papers.append(data)
len(papers)
```

```python
print(papers[0][:1000])
```

## Basic Text Wrangling

```python
%%time
import nltk

stop_words = nltk.corpus.stopwords.words('english')
wtk = nltk.tokenize.RegexpTokenizer(r'\w+')
wnl = nltk.stem.wordnet.WordNetLemmatizer()

def normalize_corpus(papers):
    norm_papers = []
    for paper in papers:
        paper = paper.lower()
        paper_tokens = [token.strip() for token in wtk.tokenize(paper)]
        paper_tokens = [wnl.lemmatize(token) for token in paper_tokens if not token.isnumeric()]
        paper_tokens = [token for token in paper_tokens if len(token) > 1]
        paper_tokens = [token for token in paper_tokens if token not in stop_words]
        paper_tokens = list(filter(None, paper_tokens))
        if paper_tokens:
            norm_papers.append(paper_tokens)

    return norm_papers

norm_papers = normalize_corpus(papers)
print(len(norm_papers))
```

# Text Representation with Feature Engineering

```python
from sklearn.feature_extraction.text import CountVectorizer

cv = CountVectorizer(min_df=20, max_df=0.6, ngram_range=(1,2),
                     token_pattern=None, tokenizer=lambda doc: doc,
                     preprocessor=lambda doc: doc)
cv_features = cv.fit_transform(norm_papers)
cv_features.shape
```

```python
vocabulary = np.array(cv.get_feature_names())
print('Total Vocabulary Size:', len(vocabulary))
```

# Topic Models with Latent Semantic Indexing (LSI)

```python
%%time
from sklearn.decomposition import TruncatedSVD

TOTAL_TOPICS = 20

lsi_model = TruncatedSVD(n_components=TOTAL_TOPICS, n_iter=500, random_state=42)
document_topics = lsi_model.fit_transform(cv_features)
```

```python
topic_terms = lsi_model.components_
topic_terms.shape
```

```python
top_terms = 20
topic_key_term_idxs = np.argsort(-np.absolute(topic_terms), axis=1)[:, :top_terms]
topic_keyterm_weights = np.array([topic_terms[row, columns]
                             for row, columns in list(zip(np.arange(TOTAL_TOPICS), topic_key_term_idxs))])
topic_keyterms = vocabulary[topic_key_term_idxs]
topic_keyterms_weights = list(zip(topic_keyterms, topic_keyterm_weights))
for n in range(TOTAL_TOPICS):
    print('Topic #'+str(n+1)+':')
    print('='*50)
    d1 = []
    d2 = []
    terms, weights = topic_keyterms_weights[n]
    term_weights = sorted([(t, w) for t, w in zip(terms, weights)],
                          key=lambda row: -abs(row[1]))
    for term, wt in term_weights:
        if wt >= 0:
            d1.append((term, round(wt, 3)))
        else:
            d2.append((term, round(wt, 3)))

    print('Direction 1:', d1)
    print('-'*50)
    print('Direction 2:', d2)
    print('-'*50)
    print()
```

```python
dt_df = pd.DataFrame(np.round(document_topics, 3),
                     columns=['T'+str(i) for i in range(1, TOTAL_TOPICS+1)])
dt_df.T
```

```python
document_numbers = [13, 250, 500]

for document_number in document_numbers:
    top_topics = list(dt_df.columns[np.argsort(-np.absolute(dt_df.iloc[document_number].values))[:3]])
    print('Document #'+str(document_number)+':')
    print('Dominant Topics (top 3):', top_topics)
    print('Paper Summary:')
    print(papers[document_number][:500])
    print()
```

# Topic Models with Latent Dirichlet Allocation (LDA)

```python
%%time
from sklearn.decomposition import LatentDirichletAllocation

lda_model = LatentDirichletAllocation(n_components =TOTAL_TOPICS, max_iter=500, max_doc_update_iter=50,
                                      learning_method='online', batch_size=1740, learning_offset=50.,
                                      random_state=42, n_jobs=16)
document_topics = lda_model.fit_transform(cv_features)
```

```python
topic_terms = lda_model.components_
```

```python
topic_key_term_idxs = np.argsort(-np.absolute(topic_terms), axis=1)[:, :top_terms]
topic_keyterms = vocabulary[topic_key_term_idxs]
topics = [', '.join(topic) for topic in topic_keyterms]
pd.set_option('display.max_colwidth', -1)
topics_df = pd.DataFrame(topics,
                         columns = ['Terms per Topic'],
                         index=['Topic'+str(t) for t in range(1, TOTAL_TOPICS+1)])
topics_df
```

```python
pd.options.display.float_format = '{:,.3f}'.format
dt_df = pd.DataFrame(document_topics,
                     columns=['T'+str(i) for i in range(1, TOTAL_TOPICS+1)])
dt_df.T
```

```python
pd.options.display.float_format = '{:,.5f}'.format
pd.set_option('display.max_colwidth', 200)

max_contrib_topics = dt_df.max(axis=0)
dominant_topics = max_contrib_topics.index
contrib_perc = max_contrib_topics.values
document_numbers = [dt_df[dt_df[t] == max_contrib_topics.loc[t]].index[0]
                       for t in dominant_topics]
documents = [papers[i] for i in document_numbers]

results_df = pd.DataFrame({'Dominant Topic': dominant_topics, 'Contribution %': contrib_perc,
                          'Paper Num': document_numbers, 'Topic': topics_df['Terms per Topic'],
                          'Paper Name': documents})
results_df
```

# Topic Models with Non-Negative Matrix Factorization (NMF)

```python
%%time
from sklearn.decomposition import NMF

nmf_model = NMF(n_components=TOTAL_TOPICS, solver='cd', max_iter=500,
                random_state=42, alpha=.1, l1_ratio=.85)
document_topics = nmf_model.fit_transform(cv_features)
```

```python
topic_terms = nmf_model.components_
topic_key_term_idxs = np.argsort(-np.absolute(topic_terms), axis=1)[:, :top_terms]
topic_keyterms = vocabulary[topic_key_term_idxs]
topics = [', '.join(topic) for topic in topic_keyterms]
pd.set_option('display.max_colwidth', -1)
topics_df = pd.DataFrame(topics,
                         columns = ['Terms per Topic'],
                         index=['Topic'+str(t) for t in range(1, TOTAL_TOPICS+1)])
topics_df
```

```python
pd.options.display.float_format = '{:,.3f}'.format
dt_df = pd.DataFrame(document_topics,
                     columns=['T'+str(i) for i in range(1, TOTAL_TOPICS+1)])
dt_df.head(10)
```

```python
pd.options.display.float_format = '{:,.5f}'.format
pd.set_option('display.max_colwidth', 200)

max_score_topics = dt_df.max(axis=0)
dominant_topics = max_score_topics.index
term_score = max_score_topics.values
document_numbers = [dt_df[dt_df[t] == max_score_topics.loc[t]].index[0]
                       for t in dominant_topics]
documents = [papers[i] for i in document_numbers]

results_df = pd.DataFrame({'Dominant Topic': dominant_topics, 'Max Score': term_score,
                          'Paper Num': document_numbers, 'Topic': topics_df['Terms per Topic'],
                          'Paper Name': documents})
results_df
```

# Predicting Topics for New Research Papers

```python
import glob
# papers manually downloaded from NIPS 16
# https://papers.nips.cc/book/advances-in-neural-information-processing-systems-29-2016

new_paper_files = glob.glob('./test_data/nips16*.txt')
new_papers = []
for fn in new_paper_files:
    with open(fn, encoding='utf-8', errors='ignore', mode='r+') as f:
        data = f.read()
        new_papers.append(data)

print('Total New Papers:', len(new_papers))
```

```python
norm_new_papers = normalize_corpus(new_papers)
cv_new_features = cv.transform(norm_new_papers)
cv_new_features.shape
```

```python
topic_predictions = nmf_model.transform(cv_new_features)
best_topics = [[(topic, round(sc, 3))
                    for topic, sc in sorted(enumerate(topic_predictions[i]),
                                            key=lambda row: -row[1])[:2]]
                        for i in range(len(topic_predictions))]
best_topics
```

```python
results_df = pd.DataFrame()
results_df['Papers'] = range(1, len(new_papers)+1)
results_df['Dominant Topics'] = [[topic_num+1 for topic_num, sc in item] for item in best_topics]
res = results_df.set_index(['Papers'])['Dominant Topics'].apply(pd.Series).stack().reset_index(level=1, drop=True)
results_df = pd.DataFrame({'Dominant Topics': res.values}, index=res.index)
results_df['Topic Score'] = [topic_sc for topic_list in
                                        [[round(sc*100, 2)
                                              for topic_num, sc in item]
                                                 for item in best_topics]
                                    for topic_sc in topic_list]

results_df['Topic Desc'] = [topics_df.iloc[t-1]['Terms per Topic'] for t in results_df['Dominant Topics'].values]
results_df['Paper Desc'] = [new_papers[i-1][:200] for i in results_df.index.values]

results_df
```

# Persisting Model and Transformers

### This is just for visualizing the topics in the other notebook (since PyLDAViz expands the notebook size)

```python
import dill

with open('nmf_model.pkl', 'wb') as f:
    dill.dump(nmf_model, f)
with open('cv_features.pkl', 'wb') as f:
    dill.dump(cv_features, f)
with open('cv.pkl', 'wb') as f:
    dill.dump(cv, f)
```
