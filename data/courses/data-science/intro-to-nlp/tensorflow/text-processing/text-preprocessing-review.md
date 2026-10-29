---
imported_hash: 2f421076a28410cf
title: Text Preprocessing Review
summary: from nltk import word_tokenize, sent_tokenize from nltk.corpus import stopwords from nltk.stem.porter import  from nltk.stem import WordNetLemmatizer
order: 22
kind: notebook
section: tensorFlow / Text processing
source: learn-ai-engineering/data-science/intro-to-nlp/tensorFlow/text-processing/text_preprocessing_review.ipynb
---

# Text Preprocessing Review

```python
# importing libraries & packages
import nltk
import string
import pandas as pd

from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords')
nltk.download('wordnet')
```

## Text Data

```python
# reading data
yelp_ratings = pd.read_csv("./data/yelp_ratings.csv") #44530 samples
```

```python
# printing first rows
yelp_ratings.head()
```

```python
# processing data
yelp_reviews = yelp_ratings["text"].values
yelp_reviews_labels = yelp_ratings["sentiment"].values
yelp_reviews_stars = yelp_ratings["stars"].values
```

```python
# printing sample of the data
yelp_reviews[:5]
```

```python
# defining sentences
raw_yelp = "Total bill for this horrible service? Over $8Gs. These crooks actually had the nerve to charge us $69 for 3 pills. I checked online the pills can be had for 19 cents EACH!"
raw_yelp
```

## Tokenize sentences

```python
# separating the sentences into a list
tokenized_sentences = sent_tokenize(raw_yelp)
tokenized_sentences
```

## Convert words to lowercase

```python
# using "".lower() from string library to convert string to lowercase
lowercase_yelp = raw_yelp.lower()
lowercase_yelp
```

## Tokenize words

```python
# tokenizing this sentence down to the word level
tokenized_yelp = word_tokenize(lowercase_yelp)
tokenized_yelp
```

## Remove stop words and punctuation

```python
# concatenating together nltk’s list of English stop words with the string library’s list of punctuation
stpwrds = stopwords.words('english') + list(string.punctuation)
```

```python
# printing list comprehension
stpwrds_removed = [w for w in tokenized_yelp if w not in stpwrds]
stpwrds_removed
```

### Stemming

```python
# creating an instance of the PorterStemmer() object to stem words
stemmer = PorterStemmer()
```

```python
# printing list comprehension
stemmed_sentence = [stemmer.stem(w) for w in stpwrds_removed]
stemmed_sentence
```

### Lemmatizing

```python
# lemmatizing
lemmatizer = WordNetLemmatizer()
# "v": verb, "n": noun, "a": adjective (default)
print(lemmatizer.lemmatize("was", pos="v"))
print(lemmatizer.lemmatize("better", pos="a"))
```

```python
# printing list
[lemmatizer.lemmatize(w, pos="v") for w in stpwrds_removed]
```

## Processing the full corpus

- Make lowercase, tokenize/remove puctuation and remove stop words from corpus

- Use sent_tokenize() if you want sentences separated.


```
processed_sentences = []
for s in sent_tokenize(sentences):
     low_tokens = word_tokenize(s.lower())
     processed_sentences.append([w for w in low_tokens if w not in stpwrds])
```

```python
# don't use sent_tokenize() if you want the full string to be processed/tokenized as a whole.
processed_sentences = []
for s in yelp_reviews:
    low_tokens = word_tokenize(s.lower())
    processed_sentences.append([w for w in low_tokens if w
                        not in stpwrds])
```

```python
# printing sentences
processed_sentences[10]
```
