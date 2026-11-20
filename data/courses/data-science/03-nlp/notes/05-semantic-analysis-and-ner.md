---
imported_hash: c05cd08f58ec9f9f
title: 'Semantic analysis: WordNet and meaning representations'
summary: Vectors tell you that two documents are alike, but not who did what, where, or to whom.
order: 6
kind: reading
section: Notes
tier: practitioner
depth: core
depth_sections:
  WordNet (Sarkar ch. 8a): intro
  Similarity and disambiguation: core
  Semantic representations (Sarkar ch. 8d): deep
source: learn-ai-engineering/data-science/03-nlp/notes/05-semantic-analysis-and-ner.md
---

# Semantic analysis: WordNet and meaning representations

Vectors tell you that two documents are alike, but not who did what, where, or to whom. If a compliance team asks which companies appear in ten thousand contracts, or a product team wants every drug name in a set of case notes, a similarity score is no help. They need spans of text with types attached, and sometimes knowledge a corpus never states, such as that a lion is a kind of cat.

This note is about meaning from structure rather than from distance: a lexical database of senses and relations (WordNet), and the formal logic that early systems used to represent what a sentence asserts. Finding the people, places and organisations in text, with spaCy or your own CRF, is in [Named entity recognition](05b-named-entity-recognition.md).

## WordNet (Sarkar ch. 8a)

WordNet groups English words into **synsets** (sets of synonyms sharing one sense) and links synsets by semantic relations. A single spelling can have many.

```python
from pathlib import Path
import random
import nltk
for pkg in ["wordnet", "omw-1.4", "punkt", "punkt_tab", "averaged_perceptron_tagger_eng"]:
    nltk.download(pkg, quiet=True)
from nltk.corpus import wordnet as wn
from nltk import word_tokenize

print("bank:", len(wn.synsets("bank")), "synsets,", len(wn.synsets("bank", "n")), "noun,", len(wn.synsets("bank", "v")), "verb")
for s in wn.synsets("fruit"):
    print(f"{s.name():12} {s.pos()}  {s.definition()}")
```

```text
bank: 18 synsets, 10 noun, 8 verb
fruit.n.01   n  the ripened reproductive body of a seed plant
yield.n.03   n  an amount of a product
fruit.n.03   n  the consequence of some effort or action
fruit.v.01   v  cause to bear fruit
fruit.v.02   v  bear fruit
```

| Relation | Meaning | Example | Method |
|---|---|---|---|
| Synonym / antonym | Same / opposite sense | large ↔ big; large ↔ small | `lemma.antonyms()` |
| Hypernym / hyponym | Is-a (more general / more specific) | tree → woody plant; tree → oak | `hypernyms()`, `hyponyms()`, `hypernym_paths()` |
| Holonym / meronym | Part-of / has-part (member, part, substance) | forest has-member tree; tree has-part trunk; tree has-substance heartwood | `member_holonyms()`, `part_meronyms()`, `substance_meronyms()` |
| Entailment | Verb A implies verb B | walk entails step; eat entails chew | `entailments()` |
| Homonyms / homographs | Same spelling, different sense | bank (river) / bank (money) | multiple synsets |

```python
tree = wn.synset("tree.n.01")
print("hypernym:", [s.name() for s in tree.hypernyms()], "| some hyponyms:", [s.name() for s in tree.hyponyms()[:3]])
print("has-part:", [s.name() for s in tree.part_meronyms()][:4], "| has-substance:", [s.name() for s in tree.substance_meronyms()])
print("walk entails:", [s.name() for s in wn.synset("walk.v.01").entailments()], "| eat entails:", [s.name() for s in wn.synset("eat.v.01").entailments()])
print("large antonym:", [a.name() for a in wn.synset("large.a.01").lemmas()[0].antonyms()])
```

```text
hypernym: ['woody_plant.n.01'] | some hyponyms: ['zebrawood.n.02', 'tipu.n.01', 'gymnospermous_tree.n.01']
has-part: ['stump.n.01', 'crown.n.07', 'burl.n.02', 'trunk.n.01'] | has-substance: ['heartwood.n.01', 'sapwood.n.01']
walk entails: ['step.v.01'] | eat entails: ['swallow.v.01', 'chew.v.01']
large antonym: ['small']
```

### Similarity and disambiguation

Because synsets form a tree of is-a links, you can measure how far apart two senses are, and find what they have in common. Sizes and scale: WordNet 3.0 holds 117,659 synsets (the count `len(list(wn.all_synsets()))` returns today, and the figure the NLTK book's text gives; its Table 2-2 says "145k", which the book does not reconcile), and "car" alone has 5 of them. Depth shows how deep the is-a chain runs: baleen whale sits at minimum depth 14 below the root `entity`. The book's path-similarity examples against right whale give 0.25 for the minke whale, 0.17 for the orca, 0.08 for a tortoise and 0.04 for a novel (all reproduce in current NLTK), and its authors add that "the numbers won't mean much" beyond the ranking (*NLP with Python*, ch. 2). The 0.25 means a shortest path of three edges (1 / (1 + 3)), through their lowest common hypernym, the baleen whale. Dated: in the book's NLTK 2 code `synset.definition`, `lemma_names` and `lemma.name` are attributes, and in NLTK 3 they are methods, as the snippets here use.

```python
from nltk.wsd import lesk

lion, tiger, cat, dog = (wn.synset(x) for x in ["lion.n.01", "tiger.n.02", "cat.n.01", "dog.n.01"])
print("lion and tiger share", [s.name() for s in lion.lowest_common_hypernyms(tiger)])
print("path_similarity  lion/tiger", round(lion.path_similarity(tiger), 2), " lion/tree", round(lion.path_similarity(tree), 2),
      " cat/dog", round(cat.path_similarity(dog), 2))   # 1 / (1 + shortest is-a path); also wup_, lch_similarity

for sentence in ["Lead is a very soft, malleable metal", "John is the actor who plays the lead", "The bank raised its interest rates", "They fished from the bank of the river"]:
    word = "lead" if "ead" in sentence else "bank"
    sense = lesk(word_tokenize(sentence), word, "n")
    print(f"{sentence:42} {sense.name():14} {sense.definition()[:60]}")
```

```text
lion and tiger share ['big_cat.n.01']
path_similarity  lion/tiger 0.33  lion/tree 0.07  cat/dog 0.2
Lead is a very soft, malleable metal       lead.n.02      a soft heavy toxic malleable metallic element; bluish white
John is the actor who plays the lead       star.n.04      an actor who plays a principal role
The bank raised its interest rates         bank.n.10      a flight maneuver; aircraft tips laterally about its longitu
They fished from the bank of the river     bank.n.01      sloping land (especially the slope beside a body of water)
```

Lesk is right on both "lead" sentences and on the river bank, then decides that a bank raising interest rates is a flight manoeuvre. That is how it fails: with no overlap in the definition, it has nothing to go on. **Lesk** picks the sense whose dictionary definition overlaps most with the context words. It is a weak baseline, and contextual embeddings ([neural text models](../../02-deep-learning/notes/06-neural-text-models.md)) disambiguate implicitly and much better. WordNet's lasting uses are lemmatisation ([text representation](01-text-representation.md)), query expansion with synonyms and hypernyms, and as a hand-built taxonomy, an early knowledge graph.

## Semantic representations (Sarkar ch. 8d)

Before statistical NLP, meaning was represented in logic. NLTK can evaluate and prove statements, and it has a built-in resolution prover (Prover9 is an external binary).

```python
read_expr = nltk.sem.Expression.fromstring
prover = nltk.ResolutionProver()
rule = read_expr("all x. all y. (jumps_over(x, y) -> -jumps_over(y, x))")
event = read_expr("jumps_over(fox, dog)")
print("does the dog jump over the fox?", prover.prove(read_expr("jumps_over(dog, fox)"), [rule, event]))
print("does the dog not jump over the fox?", prover.prove(read_expr("-jumps_over(dog, fox)"), [rule, event]))

domain = {"alice", "bob"}
valuation = nltk.sem.Valuation.fromstring("""
    alice => alice
    bob => bob
    studies => {(alice)}
""")
model = nltk.sem.Model(domain, valuation)
g = nltk.sem.Assignment(domain)
print("someone studies:", model.evaluate("exists x. studies(x)", g), "| everyone studies:", model.evaluate("all x. studies(x)", g))
```

```text
does the dog jump over the fox? False
does the dog not jump over the fox? True
someone studies: True | everyone studies: False
```

The prover cannot show the first goal, and it can show the second, which the rule and event require. Sarkar also builds a small first-order model of this kind, a domain of entities and a valuation of predicates, and evaluates quantified expressions against it. The practical descendants are triples (subject, predicate, object), knowledge graphs and constrained output schemas. LLMs now do the extraction step, and the graph and query languages took over the representation.

### What the logic approach could and could not do (*NLP with Python*, ch. 10)

Bird, Klein and Loper start from a question-answering task. A feature grammar builds a `SEM` value by string concatenation while it parses, and `What cities are located in China` becomes `SELECT City FROM city_table WHERE Country="china"` (*Natural Language Processing with Python*, ch. 10). The grammar names one table, one column and a few words, so the approach works only in a restricted domain. It is the ancestor of text-to-SQL, where an LLM now writes the query and the hard part is still the schema.

Logic gives checks that statistics do not. A model is a domain of individuals plus sets built from it, and a sentence is true or false in it. A prover shows entailment, and a model builder looks for the opposite. In the book's example the premises are a woman that every man loves, Adam is a man and Eve is a woman. Mace4 returns a countermodel to the conclusion that Adam loves Eve, because the premises never say that the woman he loves is Eve (*NLP with Python*, ch. 10). A countermodel is a cheap way to find a missing premise.

Scope is the other lesson. `Everybody admires someone` has two readings: a different admired person for each admirer, or one person admired by all, and the second is the logically stronger one. A translation driven by the parse tree always gives the first. Cooper storage keeps the quantifiers aside and generates every ordering (*NLP with Python*, ch. 10). An LLM answering a quantified question picks one reading silently, so test both.

![Two scopings of a sentence with two quantifiers](../assets/sources/images/nlp-with-python-fig10-3.png)

*Image Source: Bird, Klein and Loper, *Natural Language Processing with Python* (O'Reilly, 2009), Fig. 10-3*

Discourse breaks single-sentence logic. In `Angus owns a dog. It bit Irene.` the quantifier in the first sentence has to bind the pronoun in the second. Discourse Representation Theory keeps a list of discourse referents and conditions, and each new sentence adds to it (*NLP with Python*, ch. 10). This is coreference, which today's pipelines handle with a trained model rather than a logical structure.

![A DRS extended by a second sentence](../assets/sources/images/nlp-with-python-fig10-4.png)

*Image Source: Bird, Klein and Loper, *Natural Language Processing with Python* (O'Reilly, 2009), Fig. 10-4*

## Notebooks

| Notebook | Covers | Runs |
|---|---|---|
| [`Ch08a - Exploring WordNet`](https://github.com/ramseywise/learn-ai-engineering/blob/main/data-science/03-nlp/practice/text-analytics-with-python/Ch08%20-%20Semantic%20Analysis/Ch08a%20-%20Exploring%20WordNet.ipynb) | Synsets, relations, similarity, Lesk | Runs offline after `nltk.download("wordnet")` |
| `Ch08d - Analyzing Semantic Representations` | Propositional and first-order logic in NLTK | Runs offline (resolution prover); Prover9 cells need the external binary |

## Pitfalls

- **Trusting Lesk on a new sentence.** It picks the sense whose definition overlaps most with the context words, so with no overlap it has nothing to go on and can pick a flight manoeuvre for a bank raising interest rates. Treat it as a weak baseline and measure it.

## Try it

1. **Query expansion.** Use WordNet to expand "car" with its synonyms and hypernyms, then count how many film descriptions match the original word and how many match the expansion. Is that better?

<details><summary>Answer</summary>

```python
import re

import pandas as pd

BOOK = Path("../practice/text-analytics-with-python")
movies = pd.read_csv(BOOK / "Ch07 - Text Similarity and Clustering/tmdb_5000_movies.csv.gz")
overviews = movies.sort_values("popularity", ascending=False).overview.fillna("").tolist()

sense = wn.synset("car.n.01")
synonyms = {l.replace("_", " ") for l in sense.lemma_names()}
hypernyms = {l.replace("_", " ") for h in sense.hypernyms() for l in h.lemma_names()}
print("synonyms", sorted(synonyms)); print("hypernyms", sorted(hypernyms))
text = pd.Series(overviews).str.lower()
hits = lambda terms: text.str.contains(r"\b(?:" + "|".join(map(re.escape, terms)) + r")\b").sum()
print("car only", hits({"car"}), "| + synonyms", hits(synonyms), "| + hypernyms", hits(synonyms | hypernyms))
```

```text
synonyms ['auto', 'automobile', 'car', 'machine', 'motorcar']
hypernyms ['automotive vehicle', 'motor vehicle']
car only 75 | + synonyms 113 | + hypernyms 113
```

Synonyms raise matches from 75 to 113 descriptions, but the hypernyms here add nothing since "motor vehicle" never occurs. Precision is the catch: "machine" can match descriptions that have nothing to do with cars, so expansion always needs a check on the results.

</details>


## Interview checklist

| Question | Short answer |
|---|---|
| What is a synset? | A set of synonyms sharing one sense, linked to others by is-a, part-of and related relations. |
| What does the Lesk algorithm do? | Picks the sense whose definition overlaps most with the context. It is a weak baseline. |
| How do semantic representations survive today? | As triples, knowledge graphs and constrained schemas, with LLMs doing the extraction. |

## Next

[Named entity recognition](05b-named-entity-recognition.md) turns to sequence labelling: finding people, places and organisations with spaCy or your own CRF, and scoring them fairly. [Sentiment analysis](06-sentiment-analysis.md) then applies lexicons, supervised models and deep models to opinion.
