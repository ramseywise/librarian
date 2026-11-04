---
imported_hash: 4a72da3c8dcf7820
decks:
- learn-ai-engineering/data-science/03-nlp/slides/deck.yaml
cards:
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
- front: Why keep the vectoriser inside the cross-validation pipeline?
  back: Keeping the vectoriser inside the pipeline lets every fold build its own vocabulary, so the score is honest.
  lesson: data-science/03-nlp/notes/02-text-classification
- front: After tuning, why read the top weights of a text classifier?
  back: Tune the vectoriser and model together inside cross-validation, then read the weights to catch surprises.
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
- front: Which is harder to beat on 25,000 labelled reviews, bigram TF-IDF or a small neural network?
  back: Twenty-five thousand labels and a bigram TF-IDF model set a bar that small neural networks here did not reach.
  lesson: data-science/03-nlp/notes/06-sentiment-analysis
- front: With labels, what beat both lexicons and small neural networks on review sentiment?
  back: With labels, TF-IDF bigrams beat both the lexicons and small neural networks on review sentiment.
  lesson: data-science/03-nlp/notes/06-sentiment-analysis
- front: Which three levels can you use to explain a sentiment model?
  back: Explanations move from global weights to single predictions to themes, and each answers a different why.
  lesson: data-science/03-nlp/notes/06-sentiment-analysis
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
---
