---
imported_hash: d9116327b9b8f06a
title: Text Preprocessing
summary: Converting data into a list of sentences.
order: 20
kind: notebook
section: tensorFlow / Text processing
source: learn-ai-engineering/data-science/intro-to-nlp/tensorFlow/text-processing/text_preprocessing_2.ipynb
---

# Text Preprocessing

Converting data into a list of sentences.
- convert the sentence to lowercase
- tokenize
- remove puctuation and stop words

```python
# importing packages & libraries
import nltk
import string

from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import *

nltk.download('stopwords')
```

```python
document_data = "Data is now said to be the new oil, making data scientists indispensable. However, it is still a fairly new field and many non-technical professionals do not have a clear understanding of what data scientists do, why they do it and how to work with them. I spoke to Susie Sun, data scientist at WhatsApp, about what data science is, what data scientists do and how business functions should work with them. Sun understands both the commercial and the technical sides of the equation well, having started her career on the business side and completed an MBA, before transitioning to data science."
document_data
```

```python
# converting the document into a list of sentences
sentences = sent_tokenize(document_data)
sentences
```

```python
# getting the first sentence and convert it to lowercase
lower_cased = sentences[0].lower()
```

```python
# tokenizing the sentence
tokenized = word_tokenize(lower_cased)
```

```python
# getting the stopwords and punctuation to remove from the sentence
stpwrds = stopwords.words('english') + list(string.punctuation)
```

```python
# removing stopwords and punctuation from the sentence
stopwords_removed = [w for w in tokenized if w not in stpwrds]
stopwords_removed
```

```python
# getting the number of words in the processed sentence
len(stopwords_removed)
```
