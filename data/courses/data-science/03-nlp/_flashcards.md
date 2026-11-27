---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-science/03-nlp/slides/deck.yaml
cards:
- front: How does this lecture move from raw text to pretrained encoders?
  back: Each part adds one tool for text and measures it against the baseline that came before.
  lesson: data-science/03-nlp/readme
- front: Name four things this lecture teaches you to do with text.
  back: You will be able to turn text into features, set a baseline and say whether anything else beats it.
  lesson: data-science/03-nlp/readme
- front: What does bag of words keep from a document, and what does it lose?
  back: Bag of words makes text tabular by keeping word counts and discarding their order.
  lesson: data-science/03-nlp/notes/01-text-representation
- front: Why must the vocabulary and IDF weights come from training text alone?
  back: Fit the vocabulary and IDF weights on training text alone, because a vocabulary built on test text is a leak.
  lesson: data-science/03-nlp/notes/01-text-representation
- front: What did stopword removal cost on IMDb, and why did it flip "not good"?
  back: Your stopword list holds "not", so check what it deletes before you trust the small accuracy change.
  lesson: data-science/03-nlp/notes/01-text-representation
- front: How do you choose among TF-IDF, word vectors, sequences and sentence embeddings?
  back: Pick the cheapest representation that keeps the signal your task depends on.
  lesson: data-science/03-nlp/notes/01-text-representation
- front: After tuning, why read the top weights of a text classifier?
  back: Tune the vectoriser and model together inside cross-validation, then read the weights to catch surprises.
  lesson: data-science/03-nlp/notes/02-text-classification
- front: Why keep the vectoriser inside the cross-validation pipeline?
  back: Keeping the vectoriser inside the pipeline lets every fold build its own vocabulary, so the score is honest.
  lesson: data-science/03-nlp/notes/02-text-classification
- front: What should decide your metric, and what goes wrong with accuracy on imbalanced text?
  back: Choose the metric from the costs of the errors, since accuracy on imbalanced text flatters a lazy model.
  lesson: data-science/03-nlp/notes/02-text-classification
- front: Which input does LDA take, which does NMF take, and what decides between them?
  back: Run LDA on counts and NMF on TF-IDF, then choose by reading the topics, because metrics rarely decide it.
  lesson: data-science/03-nlp/notes/03-topic-models-and-summarization
- front: Why doesn't coherence pick a number of topics here, and what do you do instead?
  back: Coherence shows no clear elbow on this corpus, so choose the topic count by reading the topics.
  lesson: data-science/03-nlp/notes/03-topic-models-and-summarization
- front: What does a coherence score do, and what does only reading the topics tell you?
  back: Coherence narrows the options, but only reading top words and top documents tells you what a topic is.
  lesson: data-science/03-nlp/notes/03-topic-models-and-summarization
- front: What does a pretrained vector give that a one-hot never does, and what does it get wrong?
  back: Vectors measure shared contexts, so opposites used in the same places score as similar.
  lesson: data-science/03-nlp/notes/04-embeddings-and-similarity
- front: What should you try on your own corpus before downloading pretrained vectors?
  back: gensim trains word vectors on a million tokens in seconds, so try them on your own corpus before downloading any.
  lesson: data-science/03-nlp/notes/04-embeddings-and-similarity
- front: Why did "king" sit near "george" here and not "queen"?
  back: Even a small corpus yields real structure in seconds, and the neighbours reflect what that corpus is about.
  lesson: data-science/03-nlp/notes/04-embeddings-and-similarity
- front: What does NER return, and what must you do before trusting a pretrained tagger?
  back: NER returns typed spans of text, and a pretrained tagger must be measured on your own domain before you trust it.
  lesson: data-science/03-nlp/notes/05-semantic-analysis-and-ner
- front: Why report entity-level F1 and not token accuracy for NER?
  back: Report entity-level F1, since token accuracy is dominated by the tag that means nothing.
  lesson: data-science/03-nlp/notes/05-semantic-analysis-and-ner
- front: Why is a lexicon the baseline when you have no labels?
  back: A lexicon scores words and adds them up, so it needs no labels and is the baseline when you have none.
  lesson: data-science/03-nlp/notes/06-sentiment-analysis
- front: Which is harder to beat on 25,000 labelled reviews, bigram TF-IDF or a small neural network?
  back: Twenty-five thousand labels and a bigram TF-IDF model set a bar that small neural networks here did not reach.
  lesson: data-science/03-nlp/notes/06-sentiment-analysis
- front: With labels, what beat both lexicons and small neural networks on review sentiment?
  back: With labels, TF-IDF bigrams beat both the lexicons and small neural networks on review sentiment.
  lesson: data-science/03-nlp/notes/06-sentiment-analysis
- front: Which three levels can you use to explain a sentiment model?
  back: Explanations move from global weights to single predictions to themes, and each answers a different why.
  lesson: data-science/03-nlp/notes/06-sentiment-analysis
- front: What four mistakes spoil a sentiment comparison?
  back: Tune a lexicon threshold on train, re-run LIME with another seed, and give every model the same amount of data.
  lesson: data-science/03-nlp/notes/06-sentiment-analysis
- front: What does an encoder like MiniLM do between raw text and one vector?
  back: An encoder splits text into word pieces, sets each piece's vector in context, then averages and normalises them into one vector.
  lesson: data-science/03-nlp/notes/07-llm-embeddings-as-features
- front: What is the only slow step with a pretrained encoder, and what do you do about it?
  back: Encoding is the only slow step, so cache the matrix under the model's name and treat it as any other feature table.
  lesson: data-science/03-nlp/notes/07-llm-embeddings-as-features
- front: How does the encoder's lead over TF-IDF change as labels grow?
  back: The encoder leads at every size, by the most below about 1,000 labels, and TF-IDF gains ground as labels grow.
  lesson: data-science/03-nlp/notes/07-llm-embeddings-as-features
- front: Where did embeddings help most on this data?
  back: Embeddings help most where there are no labels at all, in clustering and in anomaly detection.
  lesson: data-science/03-nlp/notes/07-llm-embeddings-as-features
- front: What do you give up for an encoder, in speed and in readable features?
  back: Encoding is about fifty times slower and its coordinates cannot be read, so make it earn that price on your task.
  lesson: data-science/03-nlp/notes/07-llm-embeddings-as-features
- front: What should you fit before anything else, and what should each extra cost have to do?
  back: Fit a baseline before anything else, and make every extra cost beat it by more than the noise.
  lesson: data-science/03-nlp/notes/07-llm-embeddings-as-features
- front: Where do you go next to see inside an encoder, and to use one for search?
  back: Next, open up the encoder in deep learning, or use it for search in the RAG pillar.
  lesson: data-science/03-nlp/notes/07-llm-embeddings-as-features
- front: What is bag of words and what does it lose?
  back: A vector of token counts per document. It loses order, so "dog bites man" equals "man bites dog".
  lesson: data-science/03-nlp/notes/01-text-representation
- front: Why is the matrix sparse and why does that matter?
  back: Each document uses few of the vocabulary's words. Sparse storage and linear models make it tractable; dense arrays run out of memory.
  lesson: data-science/03-nlp/notes/01-text-representation
- front: What does IDF do?
  back: Downweights terms that occur in many documents, using $\ln\frac{1+N}{1+\text{df}} + 1$ in scikit-learn.
  lesson: data-science/03-nlp/notes/01-text-representation
- front: Why must TF-IDF sit inside the pipeline?
  back: IDF and vocabulary are fitted on data, so fitting them on the test set leaks.
  lesson: data-science/03-nlp/notes/01-text-representation
- front: Stemming or lemmatisation?
  back: Stemming is rule-based, fast and may give non-words. Lemmatisation uses a dictionary and part of speech and gives real words.
  lesson: data-science/03-nlp/notes/01-text-representation
- front: When should you not remove stop words?
  back: Sentiment and any task where negation matters, and for neural models.
  lesson: data-science/03-nlp/notes/01-text-representation
- front: What does `min_df` buy?
  back: Removes typos and rare names, often shrinking the vocabulary by more than half with no accuracy loss.
  lesson: data-science/03-nlp/notes/01-text-representation
- front: Why cosine for text?
  back: It ignores document length, so a long review and a short one on the same subject can match.
  lesson: data-science/03-nlp/notes/01-text-representation
- front: Why pad, and on which side?
  back: Batches need equal lengths. For RNNs pre-padding keeps real tokens near the final state.
  lesson: data-science/03-nlp/notes/01-text-representation
- front: Why do transformers use subwords?
  back: New words and misspellings still map to known pieces, so there is no OOV.
  lesson: data-science/03-nlp/notes/01-text-representation
- front: What do n-grams add to bag of words?
  back: Pairs and triples recover local order such as "not good", at the price of many more features. Pair them with `min_df`, since most long n-grams occur once.
  lesson: data-science/03-nlp/notes/01-text-representation
- front: What is the baseline for text classification?
  back: TF-IDF unigrams and bigrams with logistic regression or a linear SVM, in a pipeline.
  lesson: data-science/03-nlp/notes/02-text-classification
- front: Why do linear models work so well on text?
  back: There are many informative, nearly independent features, so a high-dimensional hyperplane separates well and regularisation handles the rest.
  lesson: data-science/03-nlp/notes/02-text-classification
- front: Why do trees do badly on sparse text?
  back: Each split sees one rare feature, so most leaves see few documents and the model needs very many rounds.
  lesson: data-science/03-nlp/notes/02-text-classification
- front: Why Naive Bayes?
  back: One pass over counts, surprisingly good on small data, an easy first check.
  lesson: data-science/03-nlp/notes/02-text-classification
- front: How do you handle many labels per document?
  back: One-vs-rest, one sigmoid per label; report micro and macro F1 or per-label AUC.
  lesson: data-science/03-nlp/notes/02-text-classification
- front: When is averaging word vectors a good idea?
  back: Little training data, or test vocabulary that differs from train.
  lesson: data-science/03-nlp/notes/02-text-classification
- front: How can coefficients expose leakage?
  back: A token that should not predict the label, such as a source or an id, appears at the top.
  lesson: data-science/03-nlp/notes/02-text-classification
- front: What is the hashing trick?
  back: Hash tokens into a fixed number of columns, with no vocabulary to store, for streams and huge data.
  lesson: data-science/03-nlp/notes/02-text-classification
- front: Log-loss or accuracy?
  back: Log-loss when probabilities feed a later decision, since it punishes confident errors.
  lesson: data-science/03-nlp/notes/02-text-classification
- front: When do you try an LLM?
  back: Few labels or changing label sets. Compare it against this baseline on cost and accuracy.
  lesson: data-science/03-nlp/notes/02-text-classification
- front: What is a topic model?
  back: A factorisation of the document-term matrix into documents by topics and topics by words.
  lesson: data-science/03-nlp/notes/03-topic-models-and-summarization
- front: 'LSI, LDA, NMF: what differs?'
  back: LSI uses SVD with signed weights, LDA a generative model with Dirichlet priors on counts, NMF a non-negative factorisation on TF-IDF.
  lesson: data-science/03-nlp/notes/03-topic-models-and-summarization
- front: Why does LDA take counts?
  back: Its generative story draws individual words, so TF-IDF weights violate the model.
  lesson: data-science/03-nlp/notes/03-topic-models-and-summarization
- front: What does $\alpha$ control?
  back: How many topics a document tends to use. Small $\alpha$ gives sparse mixtures.
  lesson: data-science/03-nlp/notes/03-topic-models-and-summarization
- front: How do you choose $k$?
  back: Coherence plus reading topics and their top documents. Perplexity often disagrees with humans.
  lesson: data-science/03-nlp/notes/03-topic-models-and-summarization
- front: What is PMI, and its weakness?
  back: How much more often two words co-occur than chance. It overrates rare pairs, so set a minimum count.
  lesson: data-science/03-nlp/notes/03-topic-models-and-summarization
- front: Extractive or abstractive?
  back: Extractive copies real sentences and cannot invent. Abstractive generates, reads well and can hallucinate.
  lesson: data-science/03-nlp/notes/03-topic-models-and-summarization
- front: How does TextRank work?
  back: PageRank on a graph of sentences linked by similarity. Central sentences win.
  lesson: data-science/03-nlp/notes/03-topic-models-and-summarization
- front: How do you evaluate without labels?
  back: Read topics and members, check stability across seeds, and test usefulness as features in a downstream task.
  lesson: data-science/03-nlp/notes/03-topic-models-and-summarization
- front: When would you use BERTopic instead?
  back: 'When embeddings group your documents better than word counts and one topic per document is acceptable: embed, reduce, cluster, then describe with class-based TF-IDF.'
  lesson: data-science/03-nlp/notes/03-topic-models-and-summarization
- front: Why do embeddings work at all?
  back: Words in similar contexts get similar vectors because they must predict the same neighbours.
  lesson: data-science/03-nlp/notes/04-embeddings-and-similarity
- front: CBOW or skip-gram?
  back: Skip-gram predicts context from a word, and CBOW the reverse. In the word2vec paper skip-gram won on semantics at 3x the training time.
  lesson: data-science/03-nlp/notes/04-embeddings-and-similarity
- front: What does negative sampling replace?
  back: The softmax over the vocabulary, by a binary real-or-noise classifier for each pair with $k$ noise words.
  lesson: data-science/03-nlp/notes/04-embeddings-and-similarity
- front: What does FastText add?
  back: Character n-grams, so it can embed unseen words and helps on rare or inflected words.
  lesson: data-science/03-nlp/notes/04-embeddings-and-similarity
- front: How do you turn words into a document vector?
  back: Average, TF-IDF-weighted average, or use a sentence encoder directly, which is current practice.
  lesson: data-science/03-nlp/notes/04-embeddings-and-similarity
- front: Why cosine rather than dot?
  back: Dot grows with length. After L2 normalisation, cosine, dot and Euclidean all give the same ranking.
  lesson: data-science/03-nlp/notes/04-embeddings-and-similarity
- front: Why do antonyms sit close?
  back: They occur in the same contexts, and a window-based model cannot tell them apart.
  lesson: data-science/03-nlp/notes/04-embeddings-and-similarity
- front: What is the polysemy problem?
  back: One vector for all senses, roughly a frequency-weighted sum of them. Contextual models solve it.
  lesson: data-science/03-nlp/notes/04-embeddings-and-similarity
- front: How do you remove bias from embeddings?
  back: Neutralise gender-neutral words and equalise pairs, then test, since related words often retain the association.
  lesson: data-science/03-nlp/notes/04-embeddings-and-similarity
- front: What is BM25?
  back: TF-IDF with saturating term frequency and length normalisation, the lexical half of hybrid retrieval.
  lesson: data-science/03-nlp/notes/04-embeddings-and-similarity
- front: What is a synset?
  back: A set of synonyms sharing one sense, linked to others by is-a, part-of and related relations.
  lesson: data-science/03-nlp/notes/05-semantic-analysis-and-ner
- front: What does the Lesk algorithm do?
  back: Picks the sense whose definition overlaps most with the context. It is a weak baseline.
  lesson: data-science/03-nlp/notes/05-semantic-analysis-and-ner
- front: How do semantic representations survive today?
  back: As triples, knowledge graphs and constrained schemas, with LLMs doing the extraction.
  lesson: data-science/03-nlp/notes/05-semantic-analysis-and-ner
- front: What is BIO tagging?
  back: B begins an entity, I continues it, O is outside. It keeps adjacent entities separate.
  lesson: data-science/03-nlp/notes/05b-named-entity-recognition
- front: What does a CRF add to a per-token classifier?
  back: It scores tag transitions over the whole sequence, so it can rule out invalid sequences.
  lesson: data-science/03-nlp/notes/05b-named-entity-recognition
- front: Why is NER evaluated at the entity level?
  back: Token accuracy is dominated by `O`, and a partly correct span is not a usable entity.
  lesson: data-science/03-nlp/notes/05b-named-entity-recognition
- front: When do you train your own tagger?
  back: When your entity types are specific and labelled examples exist. Otherwise use a pretrained model or rules.
  lesson: data-science/03-nlp/notes/05b-named-entity-recognition
- front: Rules or a model?
  back: Rules for closed lists like SKUs, a model for open classes where context matters.
  lesson: data-science/03-nlp/notes/05b-named-entity-recognition
- front: What are the typical modern options?
  back: Fine-tuned transformers for accuracy, LLM prompting for new types with few examples.
  lesson: data-science/03-nlp/notes/05b-named-entity-recognition
- front: When would you use a lexicon?
  back: No labels, or a quick baseline, especially VADER on short informal text.
  lesson: data-science/03-nlp/notes/06-sentiment-analysis
- front: Why might a linear model beat an LSTM on reviews?
  back: Few of the signals need long-range order, bigrams catch much negation, and linear models use data efficiently.
  lesson: data-science/03-nlp/notes/06-sentiment-analysis
- front: Why keep negations out of stop words?
  back: Otherwise "not good" turns into "good".
  lesson: data-science/03-nlp/notes/06-sentiment-analysis
- front: What does an LSTM add to a bag of bigrams?
  back: Order and scope beyond two words, at far higher training cost.
  lesson: data-science/03-nlp/notes/06-sentiment-analysis
- front: Why does averaged word2vec lose?
  back: Averaging discards word order and negation scope.
  lesson: data-science/03-nlp/notes/06-sentiment-analysis
- front: What does LIME do?
  back: Perturbs one document, watches `predict_proba`, and fits a local linear model.
  lesson: data-science/03-nlp/notes/06-sentiment-analysis
- front: How do you answer "why are people unhappy"?
  back: Per-class topic models and log-odds, then read examples.
  lesson: data-science/03-nlp/notes/06-sentiment-analysis
- front: What is the silent inference bug here?
  back: Padding inputs to a different `maxlen` than training. It does not error.
  lesson: data-science/03-nlp/notes/06-sentiment-analysis
- front: What is aspect-based sentiment?
  back: 'Polarity per attribute: "battery great, screen poor".'
  lesson: data-science/03-nlp/notes/06-sentiment-analysis
- front: What should you try first in new work?
  back: A linear baseline and a pretrained transformer, then compare cost and accuracy.
  lesson: data-science/03-nlp/notes/06-sentiment-analysis
- front: When do sentence embeddings beat TF-IDF on classification?
  back: When labels are few, or words differ between training and use. The gap here shrank from 0.15 to 0.08 as labels grew, so with enough labels, measure it.
  lesson: data-science/03-nlp/notes/07-llm-embeddings-as-features
- front: Why cache the matrix?
  back: Encoding is the slow step, and everything downstream is ordinary scikit-learn.
  lesson: data-science/03-nlp/notes/07-llm-embeddings-as-features
- front: What does mean pooling do?
  back: Averages context-aware token vectors, weighted by the attention mask, into one vector.
  lesson: data-science/03-nlp/notes/07-llm-embeddings-as-features
- front: What is the downside of pretrained encoders on long text?
  back: Truncation at the model's limit, with no warning.
  lesson: data-science/03-nlp/notes/07-llm-embeddings-as-features
- front: Why UMAP before HDBSCAN?
  back: Density estimates are unreliable at 384 dimensions, so reduce first.
  lesson: data-science/03-nlp/notes/07-llm-embeddings-as-features
- front: What is class-based TF-IDF?
  back: TF-IDF where each cluster counts as one document, used to name clusters.
  lesson: data-science/03-nlp/notes/07-llm-embeddings-as-features
- front: How does HDBSCAN differ from k-means?
  back: No k, clusters of varying density, and a noise label instead of forcing every point in.
  lesson: data-science/03-nlp/notes/07-llm-embeddings-as-features
- front: Compare kNN distance, LOF and isolation forest.
  back: kNN is global distance; LOF is distance relative to local density; the forest counts random splits to isolate, without distances.
  lesson: data-science/03-nlp/notes/07-llm-embeddings-as-features
- front: How do you evaluate anomaly detection with no labels?
  back: Inject known intruders, measure AUROC and precision at your review capacity, then read the top of the list.
  lesson: data-science/03-nlp/notes/07-llm-embeddings-as-features
- front: What is SetFit?
  back: Contrastive fine-tuning of a sentence encoder on pairs built from few labels, then a logistic head.
  lesson: data-science/03-nlp/notes/07-llm-embeddings-as-features
- front: What breaks when you change embedding model?
  back: Every stored vector. Spaces are not comparable, so re-embed and re-tune thresholds.
  lesson: data-science/03-nlp/notes/07-llm-embeddings-as-features
---
