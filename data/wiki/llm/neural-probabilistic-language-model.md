---
title: Neural Probabilistic Language Model
tags: [llm, architecture, concept]
summary: Bengio et al. (2003) introduced the idea of learning distributed word representations (embeddings) jointly with a neural network language model — fighting the curse of dimensionality by mapping words to a continuous vector space where semantically similar words have nearby representations.
updated: 2026-11-19
sources:
  - data/raw/pdfs/2003-02-01-neural-probabilistic-language-model.md
  - data/raw/papers/2026-11-08-bengio-2000-neural-probabilistic-language-model.md
---

# Neural Probabilistic Language Model

Bengio et al. (2003) proposed learning a **distributed representation for words** — dense, continuous vectors — simultaneously with a probability function for word sequences. This is the foundational paper for word embeddings and neural language modeling.

## The Problem: Curse of Dimensionality

Traditional n-gram language models estimate P(w_t | w_{t-1}, ..., w_{t-n+1}) by counting sequences in training data. The fundamental issue: a word sequence tested at inference is likely different from all sequences seen during training. With vocabulary V, there are |V|^n possible n-grams — an exponential space that cannot be adequately covered.

N-gram models handle this via back-off and smoothing (interpolating shorter n-grams), but they fundamentally rely on exact sequence matches.

## The Solution: Word Embeddings

**Core insight**: associate each word with a real-valued feature vector (embedding). Semantically similar words get nearby representations, so a sentence composed of similar words to a training sentence automatically gets high probability — exponential generalization from each training example.

The model learns simultaneously:
1. **A distributed representation** for each word: mapping from word index to d-dimensional vector (typically 30-100 dimensions)
2. **A probability function** expressed in terms of these representations

### Architecture

```
Input: word indices (w_{t-n+1}, ..., w_{t-1})
  -> Shared embedding lookup table C (|V| x d)
  -> Concatenate embeddings
  -> Hidden layer (tanh activation)
  -> Output layer (softmax over |V|)
  -> P(w_t | context)
```

The embedding matrix C is shared across all context positions — the same word always maps to the same vector regardless of where it appears.

### Direct Connections

An optional direct connection from the concatenated embeddings to the output layer (skipping the hidden layer) was found to speed up training and improve results in some configurations.

## Training

- Stochastic gradient descent on negative log-likelihood
- Softmax output layer over entire vocabulary (expensive for large V)
- Trained on Brown corpus (~1M words) and AP News (~14M words)

**Key result**: the neural model achieved significantly lower perplexity than smoothed trigram models, especially on held-out data — demonstrating that the learned representations generalize better than discrete n-gram counts.

## Historical Significance

This paper introduced ideas that became foundational:
- **Word embeddings** as a learned, dense representation of language (precursor to Word2Vec, GloVe, and all modern LLM embeddings)
- **Neural language modeling** as an alternative to count-based methods (precursor to RNN-LMs, GPT, and all modern LLMs)
- **Parameter sharing** via the embedding lookup table C
- The insight that **continuous representations enable generalization** to unseen but semantically similar inputs

## Connection to Modern Systems

Every modern LLM begins with an embedding layer mapping tokens to dense vectors — a direct descendant of Bengio's lookup table C. The key differences in modern models:
- **Scale**: billions of parameters vs thousands
- **Context**: [[Self-Attention Mechanism]] over full context vs fixed n-gram window
- **Training objective**: next-token prediction with self-supervised learning at massive scale
- **Subword tokenization**: BPE/SentencePiece vs word-level vocabulary

## Reported results and ablations (JMLR 2003 extraction)

Perplexity is the geometric average of 1/P(w_t | context); lower is better. Results are self-reported single runs.

| Setup | Neural net | Best n-gram |
|---|---|---|
| Brown corpus (vocabulary 16,383; 800,000 words for training, 200,000 validation, 181,041 test); network MLP10 with n=5, 100 hidden units, 30-d vectors, no direct connections, averaged half and half with an interpolated trigram | 252 | 312 (class-based back-off, 500 classes) |
| AP News 1995-96 (vocabulary 17,964; 13,994,528 training words); MLP10 with n=6, 60 hidden units, 100-d vectors, direct connections, mixed with the trigram | 109 | 117 (5-gram modified Kneser-Ney); 132 (deleted-interpolation trigram) |

- The improvement is roughly 24% on Brown and 8% on AP News; the conclusion of the paper gives 10 to 20% against a smoothed trigram.
- Without mixing, on Brown, the MLP1 network (n=5, 50 hidden units, 60-d vectors, direct connections) scores 268 where the deleted-interpolation trigram scores 336. Removing the hidden layer raises perplexity to 310 from 268 with 50 hidden units.
- On Brown a longer context helps the network and not the n-grams: 279 with n=5 against 293 with n=3 (50 hidden units, 30-d vectors), while Kneser-Ney 3-, 4- and 5-grams stay at 323, 321 and 321.
- Averaging in the interpolated trigram (weight 0.5) always lowered perplexity, for instance MLP1 from 268 to 257. A network lacking direct connections needed about twice the epochs (20 against 10) and ended slightly lower.
- The parameter count scales with vocabulary size times the sum of context size times vector size and the hidden size. In the AP network the output layer accounts for about 99.7% of per-example computation. Training in parallel across a cluster of 32 dual-CPU 1.2 GHz Athlon machines, communication cost was one fifteenth of epoch time; the AP run needed about three weeks of 40 CPUs, covering 5 epochs.
- Fixed word features taken from principal components of co-occurrence counts did not work (no numbers given); the importance-sampling speed-up the paper cites is 100-fold (not run in it). Its illustration of the curse of dimensionality: a joint distribution over 10 words with a 100,000-word vocabulary has about 10^50 free parameters.

Related later models: [[Hierarchical Log-Bilinear Language Model]] (tree softmax), [[Word2vec: CBOW, Skip-gram and Negative Sampling]] (no hidden layer), [[NLP (Almost) from Scratch: Window Network and Sentence-Level Likelihood]] (embeddings reused for tagging).

## Limits

- Cost: the AP run occupied 40 CPUs for three weeks, and the authors say speed-ups are needed.
- Contexts are short and fixed (n up to 6); nothing handles longer context, and recurrence appears only as future work.
- A polysemous word gets one vector. The vectors started random, and starting from external knowledge was not tried.
- Single runs without variance; the Table 2 improvement is 8%, which is smaller on the bigger corpus.
- Only perplexity is measured, with no downstream task, and nobody inspects or evaluates the learned vectors.

## See Also
- [[Transformer Architecture]] — extends
- [[Neural Text Models vs TF-IDF]] — related (from-scratch embeddings against a linear baseline)
- [[Hierarchical Story Generation]] — related (a later sequence generator decoded with top-k sampling)
- [[Perplexity and Bits-per-Byte]] — related (the metric its headline result is stated in)
- [[Hierarchical Log-Bilinear Language Model]] — extends
- [[GloVe Global Vectors]] — related (a count-based route to word vectors)
- [[FastText Subword Skip-gram]] — related
- [[Word2vec: CBOW, Skip-gram and Negative Sampling]] — extends
- [[NLP (Almost) from Scratch: Window Network and Sentence-Level Likelihood]] — extends
- [[Subword Tokenisation: BPE and SentencePiece]] — related
- [[Byte Pair Encoding and Sliding-Window Batches]] — related (token embeddings in a GPT input pipeline)
- [[Tied Input and Output Embeddings]] — extends
