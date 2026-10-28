---
imported_hash: 9cf563ff0ba979f9
title: Text Preprocessing
summary: from nltk import wordtokenize, senttokenize from nltk.corpus import stopwords from nltk.stem.porter import
order: 19
kind: notebook
section: tensorFlow / Text processing
source: learn-ai-engineering/data-science/intro-to-nlp/tensorFlow/text-processing/text_preprocessing_1.ipynb
---

# Text Preprocessing

```python
# importing packages & libraries
import nltk
import string

from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import *

nltk.download('stopwords')
```

### Text Data

```python
# defining sentence
sentences = "Apple today unveiled completely redesigned Everyone Can Code curriculum to help introduce more elementary and middle school students to the world of coding. Now available, the new curriculum includes even more resources for teachers, a brand new guide for students and updated Swift Coding Club materials. Today millions of students worldwide already use Everyone Can Code curriculum to bring their ideas to life and develop important skills including creativity, collaboration and problem solving. "
sentences
```

```python
# tokenizing the corpus into a list of sentences
sentence_tokens = sent_tokenize(sentences)
sentence_tokens
```

### Converting to Lowercase

```python
# using "".lower() from string library to convert string to lowercase
lower_sentence = sentence_tokens[0].lower()
lower_sentence
```

### Tokenization

```python
# tokenizing sentence down to the word level
tokenized_words = word_tokenize(lower_sentence)
tokenized_words
```

### Removing stop words and punctuation

```python
# concatenating together nltk’s list of English stop words with a list of the string library’s punctuation
stpwrds = stopwords.words('english') + list(string.punctuation)
stpwrds
```

```python
# printing list comprehension
stpwrds_removed = [word for word in tokenized_words if word not in stpwrds]
stpwrds_removed
```

### Stemming

```python
# creating an instance of the PorterStemmer() object to stem words
stemmer = PorterStemmer()
```

```python
# printing list comprehension
[stemmer.stem(word) for word in stpwrds_removed]
```

## Processing the full corpus

```python
# making lowercase, tokenize/remove puctuation and remove stop words from corpus
processed_sentences = []

for sentence in sent_tokenize(sentences):
    low_tokens = word_tokenize(sentence.lower())
    processed_sentences.append([word for word in low_tokens if word
                        not in stpwrds])
```

```python
# printing list
processed_sentences[0]
```

```python
# getting the number of tokens in the sentence
len(processed_sentences[0])
```
