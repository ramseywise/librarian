---
imported_hash: a55a570803da4a61
title: Ch06d   Visualizing Topic Models with pyLDAvis
summary: warnings.filterwarnings('ignore') pyLDAvis.enable_notebook()
order: 16
kind: notebook
section: Ch06   Text Summarization and Topic Models
source: learn-ai-engineering/data-science/Text Analytics with Python/Ch06 - Text Summarization and Topic Models/Ch06d - Visualizing Topic Models with pyLDAvis.ipynb
---

```python
import pyLDAvis
import pyLDAvis.sklearn
import dill
import warnings

warnings.filterwarnings('ignore')
pyLDAvis.enable_notebook()
```

```python
with open('nmf_model.pkl', 'rb') as f:
    nmf_model = dill.load(f)
with open('cv_features.pkl', 'rb') as f:
    cv_features = dill.load(f)
with open('cv.pkl', 'rb') as f:
    cv = dill.load(f)
```

```python
import pandas as pd
import numpy as np

top_terms = 20
TOTAL_TOPICS = 20
vocabulary = np.array(cv.get_feature_names())
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
pyLDAvis.sklearn.prepare(nmf_model, cv_features, cv, mds='mmds')
```

```python
pyLDAvis.sklearn.prepare(nmf_model, cv_features, cv, mds='tsne')
```

```python
pyLDAvis.sklearn.prepare(nmf_model, cv_features, cv, mds='pcoa')
```
