---
imported_hash: 8cba09b23727b3a3
title: following line is optional for custom vocabulary installation
summary: postaggedsent = nltk.postag(sentence.split()) rp = nltk.RegexpParser(grammar) shallowparsedsent = rp.parse(postaggedsent) print(shallowparsedsent)
order: 2
kind: notebook
section: Ch01   Natural Language Processing Basics
source: learn-ai-engineering/data-science/Text Analytics with Python/Ch01 - Natural Language Processing Basics/Ch01 - Natural Language Processing Basics.ipynb
---

```python
import nltk
import spacy
import numpy as np
import pandas as pd

# following line is optional for custom vocabulary installation
# you can use nlp = spacy.load('en')
nlp = spacy.load('en_core', parse=True, tag=True, entity=True)
```

```python
sentence = "The brown fox is quick and he is jumping over the lazy dog"
sentence
```

```python
words = sentence.split()
np.random.shuffle(words)
print(words)
```

```python
pos_tags = nltk.pos_tag(sentence.split())
pd.DataFrame(pos_tags).T
```

```python
spacy_pos_tagged = [(word, word.tag_, word.pos_) for word in nlp(sentence)]
pd.DataFrame(spacy_pos_tagged).T
```

```python
grammar = '''
            NP: {<DT>?<JJ>?<NN.*>}
            ADJP: {<JJ>}
            ADVP: {<RB.*>}
            PP: {<IN>}
            VP: {<MD>?<VB.*>+}
          '''

pos_tagged_sent = nltk.pos_tag(sentence.split())
rp = nltk.RegexpParser(grammar)
shallow_parsed_sent = rp.parse(pos_tagged_sent)
print(shallow_parsed_sent)
```

```python
# visualize shallow parse tree
shallow_parsed_sent
```

```python
from spacy import displacy

displacy.render(nlp(sentence), jupyter=True,
                options={'distance': 100,
                         'arrow_stroke': 1.5,
                         'arrow_width': 8})
```

```python
from nltk.parse.stanford import StanfordParser

scp = StanfordParser(path_to_jar='E:/stanford/stanford-parser-full-2015-04-20/stanford-parser.jar',
                   path_to_models_jar='E:/stanford/stanford-parser-full-2015-04-20/stanford-parser-3.5.2-models.jar')

result = list(scp.raw_parse(sentence))
print(result[0])
```

```python
# visualize constituency tree
result[0]
```

```python
# load the Brown Corpus
from nltk.corpus import brown

# total categories
print('Total Categories:', len(brown.categories()))
```

```python
# print the categories
print(brown.categories())
```

```python
# tokenized sentences
brown.sents(categories='mystery')
```

```python
# POS tagged sentences
brown.tagged_sents(categories='mystery')
```

```python
# get sentences in natural form
sentences = brown.sents(categories='mystery')
sentences = [' '.join(sentence_token) for sentence_token in sentences]
sentences[0:5] # viewing the first 5 sentences
```

```python
# get tagged words
tagged_words = brown.tagged_words(categories='mystery')

# get nouns from tagged words
nouns = [(word, tag) for word, tag in tagged_words if any(noun_tag in tag for noun_tag in ['NP', 'NN'])]

nouns[0:10] # view the first 10 nouns
```

```python
# build frequency distribution for nouns
nouns_freq = nltk.FreqDist([word for word, tag in nouns])

# view top 10 occuring nouns
nouns_freq.most_common(10)
```

```python
# load the Reuters Corpus
from nltk.corpus import reuters

# total categories
print('Total Categories:', len(reuters.categories()))
```

```python
# print the categories
print(reuters.categories())
```

```python
# get sentences in housing and income categories
sentences = reuters.sents(categories=['housing', 'income'])
sentences = [' '.join(sentence_tokens) for sentence_tokens in sentences]
sentences[0:5]  # view the first 5 sentences
```

```python
# fileid based access
print(reuters.fileids(categories=['housing', 'income']))
```

```python
print(reuters.sents(fileids=[u'test/16118', u'test/18534']))
```

```python
# load the Wordnet Corpus
from nltk.corpus import wordnet as wn

word = 'hike' # taking hike as our word of interest
# get word synsets
word_synsets = wn.synsets(word)
word_synsets
```

```python
# get details for each synonym in synset
for synset in word_synsets:
    print(('Synset Name: {name}\n'
           'POS Tag: {tag}\n'
           'Definition: {defn}\n'
           'Examples: {ex}\n').format(name=synset.name(),
                                      tag=synset.pos(),
                                      defn=synset.definition(),
                                      ex=synset.examples()))
```
