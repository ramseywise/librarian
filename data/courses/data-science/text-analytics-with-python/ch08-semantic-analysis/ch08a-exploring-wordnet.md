---
imported_hash: ab32dbc442dce4d6
title: WordNet Synsets
summary: print('Synonym:', adjlargesynonym.name()) print('Definition:', adjlargesynonym.definition()) print('Antonym:', adjlargeantonym.name()) print('Definition:', adjlargeantonym.definition()) print()
order: 21
kind: notebook
section: Ch08   Semantic Analysis
source: learn-ai-engineering/data-science/Text Analytics with Python/Ch08 - Semantic Analysis/Ch08a - Exploring WordNet.ipynb
---

```python
from nltk.corpus import wordnet as wn
import pandas as pd
```

# WordNet Synsets

```python
term = 'fruit'
synsets = wn.synsets(term)
print('Total Synsets:', len(synsets))
```

```python
pd.options.display.max_colwidth = 200
fruit_df = pd.DataFrame([{'Synset': synset,
                         'Part of Speech': synset.lexname(),
                         'Definition': synset.definition(),
                         'Lemmas': synset.lemma_names(),
                         'Examples': synset.examples()}
                             for synset in synsets])
fruit_df = fruit_df[['Synset', 'Part of Speech', 'Definition', 'Lemmas', 'Examples']]
fruit_df
```

# Entailments

```python
for action in ['walk', 'eat', 'digest']:
    action_syn = wn.synsets(action, pos='v')[0]
    print(action_syn, '-- entails -->', action_syn.entailments())
```

# Homonyms \ Homographs

```python
for synset in wn.synsets('bank'):
    print(synset.name(),'-',synset.definition())
```

# Synonyms & Antonyms

```python
term = 'large'
synsets = wn.synsets(term)
adj_large = synsets[1]
adj_large = adj_large.lemmas()[0]
adj_large_synonym = adj_large.synset()
adj_large_antonym = adj_large.antonyms()[0].synset()

print('Synonym:', adj_large_synonym.name())
print('Definition:', adj_large_synonym.definition())
print('Antonym:', adj_large_antonym.name())
print('Definition:', adj_large_antonym.definition())
print()
```

```python
term = 'rich'
synsets = wn.synsets(term)[:3]

for synset in synsets:
    rich = synset.lemmas()[0]
    rich_synonym = rich.synset()
    rich_antonym = rich.antonyms()[0].synset()

    print('Synonym:', rich_synonym.name())
    print('Definition:', rich_synonym.definition())
    print('Antonym:', rich_antonym.name())
    print('Definition:', rich_antonym.definition())
    print()
```

# Hyponyms & Hypernyms

```python
term = 'tree'
synsets = wn.synsets(term)
tree = synsets[0]

print('Name:', tree.name())
print('Definition:', tree.definition())
```

```python
hyponyms = tree.hyponyms()
print('Total Hyponyms:', len(hyponyms))
print('Sample Hyponyms')
for hyponym in hyponyms[:10]:
    print(hyponym.name(), '-', hyponym.definition())
    print()
```

```python
hypernyms = tree.hypernyms()
print(hypernyms)
```

```python
# get total hierarchy pathways for 'tree'
hypernym_paths = tree.hypernym_paths()
print('Total Hypernym paths:', len(hypernym_paths))
```

```python
# print the entire hypernym hierarchy
print('Hypernym Hierarchy')
print(' -> '.join(synset.name() for synset in hypernym_paths[0]))
```

# Holonyms & Meronyms

### Member Holonyms

```python
member_holonyms = tree.member_holonyms()
print('Total Member Holonyms:', len(member_holonyms))
print('Member Holonyms for [tree]:-')
for holonym in member_holonyms:
    print(holonym.name(), '-', holonym.definition())
    print()
```

### Part Meronyms

```python
part_meronyms = tree.part_meronyms()
print('Total Part Meronyms:', len(part_meronyms))
print('Part Meronyms for [tree]:-')
for meronym in part_meronyms:
    print(meronym.name(), '-', meronym.definition())
    print()
```

### Substance Meronyms

```python
substance_meronyms = tree.substance_meronyms()
print('Total Substance Meronyms:', len(substance_meronyms))
print('Substance Meronyms for [tree]:-')
for meronym in substance_meronyms:
    print(meronym.name(), '-', meronym.definition())
    print()
```

# Semantic Relationships & Similarities

```python
tree = wn.synset('tree.n.01')
lion = wn.synset('lion.n.01')
tiger = wn.synset('tiger.n.02')
cat = wn.synset('cat.n.01')
dog = wn.synset('dog.n.01')

# create entities and extract names and definitions
entities = [tree, lion, tiger, cat, dog]
entity_names = [entity.name().split('.')[0] for entity in entities]
entity_definitions = [entity.definition() for entity in entities]

# print entities and their definitions
for entity, definition in zip(entity_names, entity_definitions):
    print(entity, '-', definition)
    print()
```

```python
common_hypernyms = []
for entity in entities:
    # get pairwise lowest common hypernyms
    common_hypernyms.append([entity.lowest_common_hypernyms(compared_entity)[0]
                                            .name().split('.')[0]
                             for compared_entity in entities])
```

```python
# build pairwise lower common hypernym matrix
common_hypernym_frame = pd.DataFrame(common_hypernyms,
                                     index=entity_names,
                                     columns=entity_names)
common_hypernym_frame
```

```python
similarities = []
for entity in entities:
    # get pairwise similarities
    similarities.append([round(entity.path_similarity(compared_entity), 2)
                         for compared_entity in entities])
```

```python
# build pairwise similarity matrix
similarity_frame = pd.DataFrame(similarities,
                                index=entity_names,
                                columns=entity_names)
similarity_frame
```

# Word Sense Disambiguation

```python
from nltk.wsd import lesk
from nltk import word_tokenize

# sample text and word to disambiguate
samples = [('The fruits on that plant have ripened', 'n'),
           ('He finally reaped the fruit of his hard work as he won the race', 'n')]

# perform word sense disambiguation
word = 'fruit'
for sentence, pos_tag in samples:
    word_syn = lesk(word_tokenize(sentence.lower()), word, pos_tag)
    print('Sentence:', sentence)
    print('Word synset:', word_syn)
    print('Corresponding defition:', word_syn.definition())
    print()
```

```python
# sample text and word to disambiguate
samples = [('Lead is a very soft, malleable metal', 'n'),
           ('John is the actor who plays the lead in that movie', 'n'),
           ('This road leads to nowhere', 'v')]

word = 'lead'

# perform word sense disambiguation
for sentence, pos_tag in samples:
    word_syn = lesk(word_tokenize(sentence.lower()), word, pos_tag)
    print('Sentence:', sentence)
    print('Word synset:', word_syn)
    print('Corresponding defition:', word_syn.definition())
    print()
```
