---
imported_hash: 68c1a54768cabfdc
title: Movie Recommendations with Document Similarity
summary: Recommender systems are one of the popular and most adopted applications of machine learning.
order: 19
kind: notebook
section: Ch07   Text Similarity and Clustering
source: learn-ai-engineering/data-science/Text Analytics with Python/Ch07 - Text Similarity and Clustering/Ch07b - Movie Recommender with Document Similarity.ipynb
---

# Movie Recommendations with Document Similarity

Recommender systems are one of the popular and most adopted applications of machine learning. They are typically used to recommend entities to users and these entites can be anything like products, movies, services and so on.

Popular examples of recommendations include,
- Amazon suggesting products on its website
- Amazon Prime, Netflix, Hotstar recommending movies\shows
- YouTube recommending videos to watch

Typically recommender systems can be implemented in three ways:

- Simple Rule-based Recommenders: Typically based on specific global metrics and thresholds like movie popularity, global ratings etc.
- Content-based Recommenders: This is based on providing similar entities based on a specific entity of interest. Content metadata can be used here like movie descriptions, genre, cast, director and so on
- Collaborative filtering Recommenders: Here we don't need metadata but we try to predict recommendations and ratings based on past ratings of different users and specific items.

We will be building a movie recommendation system here where based on data\metadata pertaining to different movies, we try and recommend similar movies of interest!

![](../assets/ch07-text-similarity-and-clustering/netflix_rec.png)

Since our focus in not really recommendation engines but NLP, we will be leveraging the text-based metadata for each movie to try and recommend similar movies based on specific movies of interest. This falls under content-based recommenders.

# Load Dataset

```python
import pandas as pd

df = pd.read_csv('tmdb_5000_movies.csv.gz', compression='gzip')
df.info()
```

```python
df.head()
```

```python
df = df[['title', 'tagline', 'overview', 'genres', 'popularity']]
df.tagline.fillna('', inplace=True)
df['description'] = df['tagline'].map(str) + ' ' + df['overview']
df.dropna(inplace=True)
df.info()
```

```python
df.head()
```

# Build a Movie Recommender System

Here you will build your own movie recommender system. We will use the following pipeline:
- Text pre-processing
- Feature Engineering
- Document Similarity Computation
- Find top similar movies
- Build a movie recommendation function


## Document Similarity

Recommendations are about understanding the underlying features which make us favour one choice over the other. Similarity between items(in this case movies) is one way to understanding why we choose one movie over another. There are different ways to calculate similarity between two items. One of the most widely used measures is __cosine similarity__ which we have already used in the previous unit.

### Cosine Similarity

Cosine Similarity is used to calculate a numeric score to denote the similarity between two text documents. Mathematically, it is defined as follows:

$$ cosine(x,y) = \frac{x. y^\intercal}{||x||.||y||} $$

## Text pre-processing

We will do some basic text pre-processing on our movie descriptions before we build our features

```python
import nltk
import re
import numpy as np

stop_words = nltk.corpus.stopwords.words('english')

def normalize_document(doc):
    # lower case and remove special characters\whitespaces
    doc = re.sub(r'[^a-zA-Z0-9\s]', '', doc, re.I|re.A)
    doc = doc.lower()
    doc = doc.strip()
    # tokenize document
    tokens = nltk.word_tokenize(doc)
    # filter stopwords out of document
    filtered_tokens = [token for token in tokens if token not in stop_words]
    # re-create document from filtered tokens
    doc = ' '.join(filtered_tokens)
    return doc

normalize_corpus = np.vectorize(normalize_document)

norm_corpus = normalize_corpus(list(df['description']))
len(norm_corpus)
```

## Extract TF-IDF Features

```python
from sklearn.feature_extraction.text import TfidfVectorizer

tf = TfidfVectorizer(ngram_range=(1, 2), min_df=2)
tfidf_matrix = tf.fit_transform(norm_corpus)
tfidf_matrix.shape
```

## Compute Pairwise Document Similarity

```python
from sklearn.metrics.pairwise import cosine_similarity

doc_sim = cosine_similarity(tfidf_matrix)
doc_sim_df = pd.DataFrame(doc_sim)
doc_sim_df.head()
```

## Get List of Movie Titles

```python
movies_list = df['title'].values
movies_list, movies_list.shape
```

## Find Top Similar Movies for a Sample Movie

Let's take __Minions__ the most popular movie the the dataframe above and try and find the most similar movies which can be recommended

#### Find movie ID

```python
movie_idx = np.where(movies_list == 'Minions')[0][0]
movie_idx
```

#### Get movie similarities

```python
movie_similarities = doc_sim_df.iloc[movie_idx].values
movie_similarities
```

#### Get top 5 similar movie IDs

```python
similar_movie_idxs = np.argsort(-movie_similarities)[1:6]
similar_movie_idxs
```

#### Get top 5 similar movies

```python
similar_movies = movies_list[similar_movie_idxs]
similar_movies
```

### Build a movie recommender function to recommend top 5 similar movies for any movie

The movie title, movie title list and document similarity matrix dataframe will be given as inputs to the function

```python
def movie_recommender(movie_title, movies=movies_list, doc_sims=doc_sim_df):
    # find movie id
    movie_idx = np.where(movies == movie_title)[0][0]
    # get movie similarities
    movie_similarities = doc_sims.iloc[movie_idx].values
    # get top 5 similar movie IDs
    similar_movie_idxs = np.argsort(-movie_similarities)[1:6]
    # get top 5 movies
    similar_movies = movies[similar_movie_idxs]
    # return the top 5 movies
    return similar_movies
```

## Sort Dataset by Popular Movies

```python
pop_movies = df.sort_values(by='popularity', ascending=False)
pop_movies.head()
```

```python
popular_movies = ['Minions', 'Interstellar', 'Deadpool', 'Jurassic World', 'Pirates of the Caribbean: The Curse of the Black Pearl',
              'Dawn of the Planet of the Apes', 'The Hunger Games: Mockingjay - Part 1', 'Terminator Genisys',
              'Captain America: Civil War', 'The Dark Knight', 'The Martian', 'Batman v Superman: Dawn of Justice',
              'Pulp Fiction', 'The Godfather', 'The Shawshank Redemption', 'The Lord of the Rings: The Fellowship of the Ring',
              'Harry Potter and the Chamber of Secrets', 'Star Wars', 'The Hobbit: The Battle of the Five Armies',
              'Iron Man']
```

## Get Popular Movie Recommendations

```python
for movie in popular_movies:
    print('Movie:', movie)
    print('Top 5 recommended Movies:', movie_recommender(movie_title=movie))
    print()
```

# BM25 Similarity

```python
"""
Data:
-----
.. data:: PARAM_K1 - Free smoothing parameter for BM25.
.. data:: PARAM_B - Free smoothing parameter for BM25.
.. data:: EPSILON - Constant used for negative idf of document in corpus.
"""

import math
from six import iteritems
from six.moves import xrange

PARAM_K1 = 2.5
PARAM_B = 0.85
EPSILON = 0.2

class BM25(object):
    """Implementation of Best Matching 25 ranking function.
    Attributes
    ----------
    corpus_size : int
        Size of corpus (number of documents).
    avgdl : float
        Average length of document in `corpus`.
    corpus : list of list of str
        Corpus of documents.
    f : list of dicts of int
        Dictionary with terms frequencies for each document in `corpus`. Words used as keys and frequencies as values.
    df : dict
        Dictionary with terms frequencies for whole `corpus`. Words used as keys and frequencies as values.
    idf : dict
        Dictionary with inversed terms frequencies for whole `corpus`. Words used as keys and frequencies as values.
    doc_len : list of int
        List of document lengths.
    """

    def __init__(self, corpus):
        """
        Parameters
        ----------
        corpus : list of list of str
            Given corpus.
        """
        self.corpus_size = len(corpus)
        self.avgdl = sum(float(len(x)) for x in corpus) / self.corpus_size
        self.corpus = corpus
        self.f = []
        self.df = {}
        self.idf = {}
        self.doc_len = []
        self.initialize()

    def initialize(self):
        """Calculates frequencies of terms in documents and in corpus. Also computes inverse document frequencies."""
        for document in self.corpus:
            frequencies = {}
            self.doc_len.append(len(document))
            for word in document:
                if word not in frequencies:
                    frequencies[word] = 0
                frequencies[word] += 1
            self.f.append(frequencies)

            for word, freq in iteritems(frequencies):
                if word not in self.df:
                    self.df[word] = 0
                self.df[word] += 1

        for word, freq in iteritems(self.df):
            self.idf[word] = math.log(self.corpus_size - freq + 0.5) - math.log(freq + 0.5)

    def get_score(self, document, index, average_idf):
        """Computes BM25 score of given `document` in relation to item of corpus selected by `index`.
        Parameters
        ----------
        document : list of str
            Document to be scored.
        index : int
            Index of document in corpus selected to score with `document`.
        average_idf : float
            Average idf in corpus.
        Returns
        -------
        float
            BM25 score.
        """
        score = 0
        for word in document:
            if word not in self.f[index]:
                continue
            idf = self.idf[word] if self.idf[word] >= 0 else EPSILON * average_idf
            score += (idf * self.f[index][word] * (PARAM_K1 + 1)
                      / (self.f[index][word] + PARAM_K1 * (1 - PARAM_B + PARAM_B * self.doc_len[index] / self.avgdl)))
        return score

    def get_scores(self, document, average_idf):
        """Computes and returns BM25 scores of given `document` in relation to
        every item in corpus.
        Parameters
        ----------
        document : list of str
            Document to be scored.
        average_idf : float
            Average idf in corpus.
        Returns
        -------
        list of float
            BM25 scores.
        """
        scores = []
        for index in xrange(self.corpus_size):
            score = self.get_score(document, index, average_idf)
            scores.append(score)
        return scores


def get_bm25_weights(corpus):
    """Returns BM25 scores (weights) of documents in corpus.
    Each document has to be weighted with every document in given corpus.
    Parameters
    ----------
    corpus : list of list of str
        Corpus of documents.
    Returns
    -------
    list of list of float
        BM25 scores.
    Examples
    --------
    >>> from gensim.summarization.bm25 import get_bm25_weights
    >>> corpus = [
    ...     ["black", "cat", "white", "cat"],
    ...     ["cat", "outer", "space"],
    ...     ["wag", "dog"]
    ... ]
    >>> result = get_bm25_weights(corpus)
    """
    bm25 = BM25(corpus)
    average_idf = sum(float(val) for val in bm25.idf.values()) / len(bm25.idf)

    weights = []
    for doc in corpus:
        scores = bm25.get_scores(doc, average_idf)
        weights.append(scores)

    return weights
```

```python
norm_corpus_tokens = np.array([nltk.word_tokenize(doc) for doc in norm_corpus])
norm_corpus_tokens[:3]
```

```python
%%time
wts = get_bm25_weights(norm_corpus_tokens)
```

```python
bm25_wts_df = pd.DataFrame(wts)
bm25_wts_df.head()
```

```python
for movie in popular_movies:
    print('Movie:', movie)
    print('Top 5 recommended Movies:', movie_recommender(movie_title=movie, doc_sims=bm25_wts_df))
    print()
```
