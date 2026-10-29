---
imported_hash: 4c304213c02e6964
title: load corpus
summary: corpus = flatten_corpus(corpus) tokens = nltk.word_tokenize(corpus)
order: 13
kind: notebook
section: Ch06   Text Summarization and Topic Models
source: learn-ai-engineering/data-science/Text Analytics with Python/Ch06 - Text Summarization and Topic Models/Ch06a - Text Keyphrase Extraction.ipynb
---

```python
from nltk.corpus import gutenberg
import text_normalizer as tn
import nltk
from operator import itemgetter
```

```python
# load corpus
alice = gutenberg.sents(fileids='carroll-alice.txt')
alice = [' '.join(ts) for ts in alice]
norm_alice = list(filter(None, tn.normalize_corpus(alice, text_lemmatization=False)))
```

```python
print(alice[0], '\n', norm_alice[0])
```

# Collocations

```python
def compute_ngrams(sequence, n):
    return list(
            zip(*(sequence[index:]
                     for index in range(n)))
    )
```

```python
compute_ngrams([1,2,3,4], 2)
```

```python
compute_ngrams([1,2,3,4], 3)
```

```python
def flatten_corpus(corpus):
    return ' '.join([document.strip()
                     for document in corpus])
```

## N-grams

```python
def get_top_ngrams(corpus, ngram_val=1, limit=5):

    corpus = flatten_corpus(corpus)
    tokens = nltk.word_tokenize(corpus)

    ngrams = compute_ngrams(tokens, ngram_val)
    ngrams_freq_dist = nltk.FreqDist(ngrams)
    sorted_ngrams_fd = sorted(ngrams_freq_dist.items(),
                              key=itemgetter(1), reverse=True)
    sorted_ngrams = sorted_ngrams_fd[0:limit]
    sorted_ngrams = [(' '.join(text), freq)
                     for text, freq in sorted_ngrams]

    return sorted_ngrams
```

```python
get_top_ngrams(corpus=norm_alice, ngram_val=2,
               limit=10)
```

```python
get_top_ngrams(corpus=norm_alice, ngram_val=3,
               limit=10)
```

## N-grams and Pointwise Mututal Information

```python
from nltk.collocations import BigramCollocationFinder
from nltk.collocations import BigramAssocMeasures

finder = BigramCollocationFinder.from_documents([item.split()
                                                for item
                                                in norm_alice])
finder
```

```python
bigram_measures = BigramAssocMeasures()
finder.nbest(bigram_measures.raw_freq, 10)
```

```python
finder.nbest(bigram_measures.pmi, 10)
```

```python
from nltk.collocations import TrigramCollocationFinder
from nltk.collocations import TrigramAssocMeasures

finder = TrigramCollocationFinder.from_documents([item.split()
                                                for item
                                                in norm_alice])
```

```python
trigram_measures = TrigramAssocMeasures()
finder.nbest(trigram_measures.raw_freq, 10)
```

```python
finder.nbest(trigram_measures.pmi, 10)
```

# Weighted Tag-based Phrase Extraction

```python
data = open('elephants.txt', 'r+').readlines()
sentences = nltk.sent_tokenize(data[0])
len(sentences)
```

```python
sentences[:3]
```

```python
norm_sentences = tn.normalize_corpus(sentences, text_lower_case=False,
                                     text_stemming=False, text_lemmatization=False, stopword_removal=False)
norm_sentences[:3]
```

```python
import itertools
stopwords = nltk.corpus.stopwords.words('english')

def get_chunks(sentences, grammar = r'NP: {<DT>? <JJ>* <NN.*>+}', stopword_list=stopwords):

    all_chunks = []
    chunker = nltk.chunk.regexp.RegexpParser(grammar)

    for sentence in sentences:

        tagged_sents = [nltk.pos_tag(nltk.word_tokenize(sentence))]

        chunks = [chunker.parse(tagged_sent)
                      for tagged_sent in tagged_sents]

        wtc_sents = [nltk.chunk.tree2conlltags(chunk)
                         for chunk in chunks]

        flattened_chunks = list(
                            itertools.chain.from_iterable(
                                wtc_sent for wtc_sent in wtc_sents)
                           )

        valid_chunks_tagged = [(status, [wtc for wtc in chunk])
                                   for status, chunk
                                       in itertools.groupby(flattened_chunks,
                                                lambda word_pos_chunk: word_pos_chunk[2] != 'O')]

        valid_chunks = [' '.join(word.lower()
                                for word, tag, chunk in wtc_group
                                    if word.lower() not in stopword_list)
                                        for status, wtc_group in valid_chunks_tagged
                                            if status]

        all_chunks.append(valid_chunks)

    return all_chunks
```

```python
chunks = get_chunks(norm_sentences)
chunks
```

```python
from gensim import corpora, models

def get_tfidf_weighted_keyphrases(sentences,
                                  grammar=r'NP: {<DT>? <JJ>* <NN.*>+}',
                                  top_n=10):

    valid_chunks = get_chunks(sentences, grammar=grammar)

    dictionary = corpora.Dictionary(valid_chunks)
    corpus = [dictionary.doc2bow(chunk) for chunk in valid_chunks]

    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]

    weighted_phrases = {dictionary.get(idx): value
                           for doc in corpus_tfidf
                               for idx, value in doc}

    weighted_phrases = sorted(weighted_phrases.items(),
                              key=itemgetter(1), reverse=True)
    weighted_phrases = [(term, round(wt, 3)) for term, wt in weighted_phrases]

    return weighted_phrases[:top_n]
```

```python
get_tfidf_weighted_keyphrases(sentences=norm_sentences, top_n=30)
```

```python
from gensim.summarization import keywords

key_words = keywords(data[0], ratio=1.0, scores=True, lemmatize=True)
[(item, round(score, 3)) for item, score in key_words][:25]
```
