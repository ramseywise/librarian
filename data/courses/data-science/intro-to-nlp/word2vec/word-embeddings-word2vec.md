---
imported_hash: 85cad46bf2590e50
title: Word Embeddings (word2vec)
summary: '%matplotlib inline nltk.download(''gutenberg'')'
order: 25
kind: notebook
section: Word2vec
source: learn-ai-engineering/data-science/intro-to-nlp/word2vec/word_embeddings_word2vec.ipynb
---

# Word Embeddings (word2vec)

**Word embeddings** is **vectors** representations of a word.

**Word2Vec** is one of the most popular technique to learn word embeddings using shallow neural network.

```python
# installing packages
! pip install gensim
```

```python
# importing packages
import nltk
import pandas as pd
import string
import gensim
import bokeh.io
from gensim.models.word2vec import Word2Vec
from sklearn.manifold import TSNE
from bokeh.io import output_notebook, output_file
from bokeh.plotting import show, figure
from bokeh.resources import INLINE

%matplotlib inline
nltk.download('gutenberg')
```

### Get corpus of Project Gutenberg books

```python
# getting public domain books
from nltk.corpus import gutenberg
```

```python
# showing the public domain document names that are in the corpus
gutenberg.fileids()
```

```python
# getting total number of words in the corpus
len(gutenberg.words())
```

## Tokenize

```python
# returning sentences tokenized
gberg_sents = gutenberg.sents()
```

```python
# showing tokenized sents
gberg_sents[1]
```

## Process the corpus

```python
# removing (only) capitalization and punctuation from the corpus
lower_sents = []
for sentence in gberg_sents:
    lower_sents.append([word.lower() for word in sentence if word.lower()
                        not in list(string.punctuation)])
```

## Word embeddings

```python
# using word2vec model
model = Word2Vec(sentences=lower_sents, size=64,
                 sg=1, window=10, iter=5,
                 min_count=10, workers=4)
```

```python
model.wv["dog"]
```

```python
# getting top n words most similar to a given word - using cosine similarity
model.wv.most_similar('father', topn=4)
```

```python
# getting the similarity score between two words
model.wv.similarity('father','dog')
```

## Visualize the word similarities

```python
# reducing the 64 dimensions down to 2 in order to visualize
tsne = TSNE(n_components=2, n_iter=1000)
X_2d = tsne.fit_transform(model.wv[model.wv.vocab])
coords_df = pd.DataFrame(X_2d, columns=['x','y'])
coords_df['token'] = model.wv.vocab.keys()
```

```python
# 2d scatterplot static visualization
_ = coords_df.plot.scatter('x','y', figsize=(12,12),
                    marker='.', s=10, alpha=0.2)
```

```python
# creating a Bokeh interactive visualization
# output_notebook()
bokeh.io.output_notebook(INLINE)
subset_df = coords_df.sample(n=5000)
p = figure(plot_width=800, plot_height=800)
_ = p.text(x=subset_df.x, y=subset_df.y, text=subset_df.token)
show(p)
```
