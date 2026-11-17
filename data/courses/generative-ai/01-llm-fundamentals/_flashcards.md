---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- generative-ai/01-llm-fundamentals/slides/deck.yaml
cards:
- front: What are the three parts of this lecture, in order?
  back: The lecture runs from how a model predicts, through how its weights are trained and adapted, to how you prompt, call and run it.
  lesson: generative-ai/01-llm-fundamentals/readme
- front: Name four things this lecture teaches you to do with a model.
  back: You will be able to say why the model answered as it did, which lever to pull, and how to call and run it safely.
  lesson: generative-ai/01-llm-fundamentals/readme
- front: How does a model get from a customer's text to the next token?
  back: The model turns tokens into vectors, mixes them with attention, and samples one next token at a time.
  lesson: generative-ai/01-llm-fundamentals/notes/01-tokens-and-embeddings
- front: Why can a model fail to reverse a string that it reads correctly?
  back: Tokens make any text encodable, but they set the bill and hide the letters, so measure in tokens.
  lesson: generative-ai/01-llm-fundamentals/notes/01-tokens-and-embeddings
- front: When do dot product, cosine and L2 distance rank neighbours the same way?
  back: Scale embeddings to length 1 and dot product, cosine and L2 distance pick the same neighbours.
  lesson: generative-ai/01-llm-fundamentals/notes/01-tokens-and-embeddings
- front: Which position schemes act inside attention, and which act on the input?
  back: Learned and sinusoidal positions go on the input; relative, RoPE and ALiBi act on the query-key score.
  lesson: generative-ai/01-llm-fundamentals/notes/01b-position-encodings-and-context-extension
- front: What happens to a RoPE model run past its training length, and what fixes it without retraining?
  back: Rescale positions (interpolation, NTK, YaRN) so long inputs map back into the trained range, then test your own task at the length you will use.
  lesson: generative-ai/01-llm-fundamentals/notes/01b-position-encodings-and-context-extension
- front: How do you test that a causal mask works?
  back: Attention weights tokens by relevance, and the causal mask makes one pass train every position honestly.
  lesson: generative-ai/01-llm-fundamentals/notes/02-attention-and-the-transformer-block
- front: What does Q Kᵀ cost, and why is K transposed?
  back: Inner sizes must match and drop out, a product costs 2·m·n·k FLOPs, and a low-rank matrix stores as two thin factors, which is LoRA.
  lesson: generative-ai/01-llm-fundamentals/notes/02-attention-and-the-transformer-block
- front: Why divide by the square root of d_k?
  back: Attention is a masked, scaled softmax over dot products, and its T by T matrix is what makes context expensive.
  lesson: generative-ai/01-llm-fundamentals/notes/02-attention-and-the-transformer-block
- front: What do the residual and the LayerNorm each contribute?
  back: 'A GPT is one block repeated: attention and an MLP, with residuals and LayerNorm to keep deep stacks trainable.'
  lesson: generative-ai/01-llm-fundamentals/notes/02-attention-and-the-transformer-block
- front: Is an attention weight an explanation of the model's answer?
  back: Use attention as a place to look, not as the reason for an answer.
  lesson: generative-ai/01-llm-fundamentals/notes/02b-what-trained-attention-does
- front: What is an attention sink?
  back: A head that sits on the first token is probably a no-op, so dropping that token can break a model that was trained with it.
  lesson: generative-ai/01-llm-fundamentals/notes/02b-what-trained-attention-does
- front: How do you estimate the memory for a model's weights?
  back: Size a model as parameters times bytes before you download it, and treat the count as memory rather than ability.
  lesson: generative-ai/01-llm-fundamentals/notes/03-scale-and-the-model-zoo
- front: Why might an operator train past 20 tokens per parameter?
  back: Chinchilla says scale data and parameters together, yet operators train past 20 tokens per parameter to cut inference cost.
  lesson: generative-ai/01-llm-fundamentals/notes/03-scale-and-the-model-zoo
- front: What are the three ways to avoid attention's quadratic cost?
  back: Fixed-size state makes long sequences cheap and loses what does not fit, so the field's answer is hybrids with a few attention layers.
  lesson: generative-ai/01-llm-fundamentals/notes/03b-beyond-the-transformer
- front: Why is generation cheap in a linear-attention model?
  back: Causal linear attention is a recurrence over a fixed-size state, so a token costs the same at position 10,000 as at position 10.
  lesson: generative-ai/01-llm-fundamentals/notes/03b-beyond-the-transformer
- front: What does the KV cache store, and what does it cost?
  back: Prefill reads in parallel and decode writes serially, and the KV cache trades growing memory for that speed.
  lesson: generative-ai/01-llm-fundamentals/notes/04-decoding-and-inference-behaviour
- front: What does a temperature above 1 do to the distribution?
  back: Sampling settings shape which token gets chosen, and they control variety without making the answer true.
  lesson: generative-ai/01-llm-fundamentals/notes/04-decoding-and-inference-behaviour
- front: What does constrained decoding guarantee, and what does it leave open?
  back: Decoding-time levers trade compute or memory for quality, and constraints fix an answer's shape but not its truth.
  lesson: generative-ai/01-llm-fundamentals/notes/04-decoding-and-inference-behaviour
- front: What are the two hypotheses for hallucination?
  back: 'Treat hallucination as structural: both leading explanations come from how the model is trained, so design checks.'
  lesson: generative-ai/01-llm-fundamentals/notes/05-hallucination-and-base-vs-assistant
- front: What kind of error can self-consistency not catch?
  back: Measure tokens and memory, match the chat template, and verify facts instead of trusting a model's fluency.
  lesson: generative-ai/01-llm-fundamentals/notes/05-hallucination-and-base-vs-assistant
- front: About what share of InstructGPT's compute went into pretraining?
  back: Weights flow from pretraining to fine-tuning to preference optimization, so choose the stage that matches your problem.
  lesson: generative-ai/01-llm-fundamentals/notes/06-pretraining-data-and-objectives
- front: What should the loss be before training, and why?
  back: Pretraining is next-token cross-entropy, parallel through teacher forcing, and step-0 loss near ln(vocab) checks the wiring.
  lesson: generative-ai/01-llm-fundamentals/notes/06-pretraining-data-and-objectives
- front: Why does minimising cross-entropy also minimise KL divergence?
  back: The data's entropy does not depend on the model, so minimising cross-entropy minimises KL, and perplexity is exp of the loss.
  lesson: generative-ai/01-llm-fundamentals/notes/06-pretraining-data-and-objectives
- front: What does a widening gap between training and validation loss show?
  back: On little data a model memorises, so continue pretraining or fine-tune rather than pretraining on company data.
  lesson: generative-ai/01-llm-fundamentals/notes/06-pretraining-data-and-objectives
- front: How does a raw crawl become a training stream?
  back: More tokens are not better tokens; filtering and mixture move scores as much as architecture does.
  lesson: generative-ai/01-llm-fundamentals/notes/06b-pretraining-data
- front: What did phi-3-mini's heavy filtering keep and give up?
  back: A data mixture sets what the model is good at, so check what a filter drops before trusting it.
  lesson: generative-ai/01-llm-fundamentals/notes/06b-pretraining-data
- front: What share of Llama 2's training data would five years of support tickets be?
  back: Do the multiplication first. Even generous ticket volumes are a fraction of a percent of Llama 2's data, so continue pretraining or fine-tune.
  lesson: generative-ai/01-llm-fundamentals/notes/15-pretraining-runs-cost-and-scale
- front: How many SFT examples did InstructGPT use?
  back: 'Same loss, different data: raw text adds knowledge, demonstrations add behaviour, so name what is missing first.'
  lesson: generative-ai/01-llm-fundamentals/notes/07-sft-and-instruction-tuning
- front: What happens if you fine-tune on facts the model does not know?
  back: Fine-tuning can damage what a model already knows, so stop early, replay old data and limit which weights move.
  lesson: generative-ai/01-llm-fundamentals/notes/07-sft-and-instruction-tuning
- front: What value does this loss start at when the two scores are tied?
  back: Preference training rewards the gap between winner and loser, which is why comparison data is such good value.
  lesson: generative-ai/01-llm-fundamentals/notes/08-preference-optimisation-overview
- front: How does DPO avoid a reward model?
  back: DPO turns preference optimization into a classification loss, so you can start without a reward model or PPO.
  lesson: generative-ai/01-llm-fundamentals/notes/08-preference-optimisation-overview
- front: Why is the model unchanged at the start of LoRA training?
  back: LoRA trains a small low-rank update on frozen weights, merged for serving, so most teams should start there.
  lesson: generative-ai/01-llm-fundamentals/notes/09-peft-and-fine-tuning-in-practice
- front: When is fine-tuning the wrong answer?
  back: Prompt first, retrieve for facts, and fine-tune only for behaviour that good prompting could not stabilise.
  lesson: generative-ai/01-llm-fundamentals/notes/09-peft-and-fine-tuning-in-practice
- front: What are the five principles of prompting?
  back: Give direction, format and examples, but evaluation on a labelled set is what turns a prompt into something you can trust.
  lesson: generative-ai/01-llm-fundamentals/notes/10-prompting-fundamentals
- front: What do you do with a reply that fails validation?
  back: Validate each reply, retry up to a cap, and route the rest to a human, logging what the retries cost.
  lesson: generative-ai/01-llm-fundamentals/notes/10-prompting-fundamentals
- front: What does the pipe operator do in LCEL?
  back: LCEL pipes Runnables into a chain that can batch and stream, and a fake model makes its wiring cheap to test.
  lesson: generative-ai/01-llm-fundamentals/notes/11-langchain-basics
- front: What should the loss be at step 0, and how do you test the causal mask?
  back: Write the model once and run these checks, since a bad mask still trains and only a direct test will reveal it.
  lesson: generative-ai/01-llm-fundamentals/notes/12-build-a-tiny-gpt
- front: What replaces a forced tool_choice on current Claude models?
  back: Current Claude models reject forced tools and sampling settings, so use structured outputs or strict tools under auto.
  lesson: generative-ai/01-llm-fundamentals/notes/13-calling-models-from-code
- front: What are the three details of a correct tool loop?
  back: Append all assistant content, send every result in one user turn, cap the turns, and check stop_reason first.
  lesson: generative-ai/01-llm-fundamentals/notes/13-calling-models-from-code
- front: What three things does the Llama 3.1 licence require?
  back: Open weights differ in terms, so read the licence of the exact repo and of its base model before you build on it.
  lesson: generative-ai/01-llm-fundamentals/notes/14-open-weight-models-and-local-inference
- front: Why does a Q4 file need more than 4 bits per parameter?
  back: Start with Q4_K_M, treat file size as a floor beneath the KV cache, and decide with your own eval rather than the name.
  lesson: generative-ai/01-llm-fundamentals/notes/14-open-weight-models-and-local-inference
- front: What are the strongest reasons to run locally?
  back: Choose local for data rules and control, and work out cost with your own volume, because it rarely wins on price alone.
  lesson: generative-ai/01-llm-fundamentals/notes/14-open-weight-models-and-local-inference
- front: Which one sentence explains most of an LLM's surprising behaviour?
  back: Models predict plausible tokens, so count tokens, validate outputs, measure prompts and retrieve your facts.
  lesson: generative-ai/01-llm-fundamentals/notes/05-hallucination-and-base-vs-assistant
- front: What can the assistant still not do at the end of this pillar?
  back: The assistant still lacks your facts, so retrieval comes next, then agents, post-training depth and evaluation.
  lesson: generative-ai/01-llm-fundamentals/notes/14-open-weight-models-and-local-inference
- front: Why do LLMs use subword tokens?
  back: Characters give too few units per unit of meaning and whole words cannot cover the open vocabulary. BPE gives a fixed vocabulary that can encode any string
  lesson: generative-ai/01-llm-fundamentals/notes/01-tokens-and-embeddings
- front: What is the effect of tokenization on cost and language quality?
  back: Pricing and context limits are per token. The same short sentence had a median of 7 GPT-4 tokens in English and 72 in Burmese, and languages rare in the training data also tend to score worse
  lesson: generative-ai/01-llm-fundamentals/notes/01-tokens-and-embeddings
- front: Why can a model fail to reverse a string it reads correctly?
  back: It sees tokens, not characters, so the letters inside a token are not directly available to it
  lesson: generative-ai/01-llm-fundamentals/notes/01-tokens-and-embeddings
- front: What does an embedding layer learn?
  back: A trainable table with one vector per token id, fit by next-token loss so that tokens used alike end up with useful vectors
  lesson: generative-ai/01-llm-fundamentals/notes/01-tokens-and-embeddings
- front: Why is a position signal needed at all?
  back: Attention is order-blind on its own, and without one a reordered sentence would produce the same set of vectors
  lesson: generative-ai/01-llm-fundamentals/notes/01-tokens-and-embeddings
- front: Learned positions versus RoPE?
  back: A learned table is simple and has a hard maximum length. RoPE rotates queries and keys so scores depend on relative offset. It has no hard limit, though running past the training length needs extra tricks
  lesson: generative-ai/01-llm-fundamentals/notes/01-tokens-and-embeddings
- front: Which position schemes put the signal inside attention rather than on the input?
  back: Relative encodings, RoPE and ALiBi act on the query–key score. Learned and sinusoidal positions are added to the token embedding
  lesson: generative-ai/01-llm-fundamentals/notes/01b-position-encodings-and-context-extension
- front: Why does a RoPE model fail past its training length, and what fixes it without retraining?
  back: Positions beyond the trained range rotate queries and keys by angles never seen, so perplexity blows up. Position interpolation, NTK-aware or dynamic scaling and YaRN rescale positions or frequencies at inference, with the limits measured above
  lesson: generative-ai/01-llm-fundamentals/notes/01b-position-encodings-and-context-extension
- front: What do query, key and value do?
  back: A token's query is compared with each key to produce weights, and those weights average the values into the token's new vector
  lesson: generative-ai/01-llm-fundamentals/notes/02-attention-and-the-transformer-block
- front: Why divide by √d_k?
  back: Dot products grow with dimension, which would push the softmax towards one-hot and shrink its gradients
  lesson: generative-ai/01-llm-fundamentals/notes/02-attention-and-the-transformer-block
- front: What does the causal mask do?
  back: It stops each position from seeing later positions, so one forward pass can train every position to predict its next token
  lesson: generative-ai/01-llm-fundamentals/notes/02-attention-and-the-transformer-block
- front: Why multiple heads?
  back: Each head has its own projections, so different heads can attend to different relationships at the same total width
  lesson: generative-ai/01-llm-fundamentals/notes/02-attention-and-the-transformer-block
- front: What does the residual do, and the LayerNorm?
  back: The residual gives gradients a direct path through deep stacks. LayerNorm keeps each token's activations in a stable range without needing batch statistics
  lesson: generative-ai/01-llm-fundamentals/notes/02-attention-and-the-transformer-block
- front: What dominates the cost of a block?
  back: The attention step, quadratic in sequence length, and it also sets the memory that the KV cache must hold at generation time
  lesson: generative-ai/01-llm-fundamentals/notes/02-attention-and-the-transformer-block
- front: How do you test the mask?
  back: Change a later token and check that earlier outputs stay the same
  lesson: generative-ai/01-llm-fundamentals/notes/02-attention-and-the-transformer-block
- front: Is attention an explanation?
  back: Not on its own. Weights show where a head drew from, they can be changed without changing the output, and they agree only loosely with gradient importance
  lesson: generative-ai/01-llm-fundamentals/notes/02b-what-trained-attention-does
- front: What does integrated gradients fix?
  back: Plain gradients can be zero where the output clearly depends on the input. Integrating along a path from a baseline makes the attributions sum to F(x) − F(baseline)
  lesson: generative-ai/01-llm-fundamentals/notes/02b-what-trained-attention-does
- front: How does a transformer read an image?
  back: It cuts the image into patches, projects each to the model width, adds a class token and position embeddings, then runs a standard encoder
  lesson: generative-ai/01-llm-fundamentals/notes/02b-what-trained-attention-does
- front: What did Chinchilla change?
  back: For a fixed compute budget, scale parameters and tokens about equally, roughly 20 tokens per parameter, which overturned Kaplan's fit of bigger models with less data
  lesson: generative-ai/01-llm-fundamentals/notes/03-scale-and-the-model-zoo
- front: Why might an operator still train past 20 tokens per parameter?
  back: Inference traffic can dwarf training cost, so a smaller model on more data costs less over its life
  lesson: generative-ai/01-llm-fundamentals/notes/03-scale-and-the-model-zoo
- front: Encoder-only, decoder-only, encoder-decoder?
  back: Masked-token prediction suits embeddings and classification. Next-token prediction suits generation. Sequence-to-sequence suits translation and summarisation
  lesson: generative-ai/01-llm-fundamentals/notes/03-scale-and-the-model-zoo
- front: What does "355B with 32B active" mean?
  back: A mixture-of-experts model holds all 355B in memory but routes each token through only a few experts, so compute per token follows the active count
  lesson: generative-ai/01-llm-fundamentals/notes/03-scale-and-the-model-zoo
- front: Does lower language-modelling loss guarantee better tasks?
  back: No. Downstream scores do not always follow loss, and some tasks get worse as it falls
  lesson: generative-ai/01-llm-fundamentals/notes/03-scale-and-the-model-zoo
- front: How do you estimate memory for a model?
  back: Parameters times bytes per parameter for the chosen precision, plus KV cache and activations for serving
  lesson: generative-ai/01-llm-fundamentals/notes/03-scale-and-the-model-zoo
- front: Why look beyond attention at all?
  back: Attention cost grows quadratically with sequence length. Linear-time models keep a fixed-size state, which makes long sequences cheap but loses what does not fit in the state
  lesson: generative-ai/01-llm-fundamentals/notes/03b-beyond-the-transformer
- front: Do state-space models beat transformers?
  back: Not in general. Reported wins are at small scale and on the authors' own benchmarks, and hybrids that mix a few attention layers with linear layers are the field's current answer
  lesson: generative-ai/01-llm-fundamentals/notes/03b-beyond-the-transformer
- front: What are prefill and decode?
  back: Prefill runs the prompt through the model in one parallel pass. Decode generates one token at a time, each with its own forward pass
  lesson: generative-ai/01-llm-fundamentals/notes/04-decoding-and-inference-behaviour
- front: What does temperature do?
  back: It divides logits before the softmax, so values above 1 flatten the distribution and values below 1 sharpen it. Zero is implemented as argmax
  lesson: generative-ai/01-llm-fundamentals/notes/04-decoding-and-inference-behaviour
- front: Top-k or top-p?
  back: Top-k keeps a fixed number of tokens. Top-p keeps however many reach a probability mass, so it adapts to how peaked the distribution is
  lesson: generative-ai/01-llm-fundamentals/notes/04-decoding-and-inference-behaviour
- front: Why isn't temperature 0 fully reproducible on an API?
  back: Hosted runs can differ in hardware and version, even with sampling removed
  lesson: generative-ai/01-llm-fundamentals/notes/04-decoding-and-inference-behaviour
- front: How does constrained decoding work, and what doesn't it solve?
  back: It masks tokens the grammar forbids at each step. It guarantees shape but not the truth of the values
  lesson: generative-ai/01-llm-fundamentals/notes/04-decoding-and-inference-behaviour
- front: What is GQA for?
  back: Several query heads share one key/value head, which shrinks the KV cache at a small quality cost
  lesson: generative-ai/01-llm-fundamentals/notes/04-decoding-and-inference-behaviour
- front: What is a base model?
  back: A pretrained text-continuer, trained by self-supervision on next tokens. It has no instruction-following behaviour of its own
  lesson: generative-ai/01-llm-fundamentals/notes/05-hallucination-and-base-vs-assistant
- front: Where does assistant behaviour come from?
  back: 'Post-training: supervised fine-tuning on demonstrations, then preference optimisation, in a fixed chat template'
  lesson: generative-ai/01-llm-fundamentals/notes/05-hallucination-and-base-vs-assistant
- front: What does a chat template do?
  back: It turns role-tagged messages into the one string the model sees, ending in a generation prompt. A mismatch with training silently degrades quality
  lesson: generative-ai/01-llm-fundamentals/notes/05-hallucination-and-base-vs-assistant
- front: How does SelfCheckGPT work?
  back: It draws more samples and scores each sentence by how far they support it, on the idea that invented facts disagree across samples
  lesson: generative-ai/01-llm-fundamentals/notes/05-hallucination-and-base-vs-assistant
- front: What can't self-consistency catch?
  back: Consistent errors, such as a falsehood present in the training data
  lesson: generative-ai/01-llm-fundamentals/notes/05-hallucination-and-base-vs-assistant
- front: How far can you trust a model's self-confidence?
  back: P(True) can be calibrated in the right setup, but P(IK) generalises poorly to new tasks. Calibrate on your own data
  lesson: generative-ai/01-llm-fundamentals/notes/05-hallucination-and-base-vs-assistant
- front: What is the training objective of pretraining?
  back: Cross-entropy of the next token at every position, with labels being the input shifted by one, so no human labels are needed
  lesson: generative-ai/01-llm-fundamentals/notes/06-pretraining-data-and-objectives
- front: What is teacher forcing, and why does it make training parallel?
  back: Each position sees the true previous tokens, so one masked forward pass scores all positions at once. Generation has to wait for its own output
  lesson: generative-ai/01-llm-fundamentals/notes/06-pretraining-data-and-objectives
- front: What should the loss be before training?
  back: About `ln(vocab)`. A different value suggests a bug
  lesson: generative-ai/01-llm-fundamentals/notes/06-pretraining-data-and-objectives
- front: Why does training need far more memory than inference?
  back: Weights, gradients and optimizer state for every parameter, and activations. Adam alone keeps two extra values per weight
  lesson: generative-ai/01-llm-fundamentals/notes/06-pretraining-data-and-objectives
- front: Where does pretraining text come from?
  back: Mostly filtered Common Crawl, plus books, code, Wikipedia and increasingly synthetic text
  lesson: generative-ai/01-llm-fundamentals/notes/06b-pretraining-data
- front: Why filter instead of using everything?
  back: In T5's ablation the unfiltered crawl scored worst on every task (GLUE 81.46 against 83.28 for the filtered set)
  lesson: generative-ai/01-llm-fundamentals/notes/06b-pretraining-data
- front: What does repetition do?
  back: A few repeats barely matter. Cycling a small subset 1,024 times hurt GLUE in T5's ablation (79.55)
  lesson: generative-ai/01-llm-fundamentals/notes/06b-pretraining-data
- front: What happens when the data supply runs out?
  back: Teams repeat data, mix in synthetic text and code, or rewrite web text. Models trained on their own output lose the tails (model collapse)
  lesson: generative-ai/01-llm-fundamentals/notes/06b-pretraining-data
- front: Continued pretraining or SFT?
  back: Continued pretraining adds knowledge from raw domain text with the same next-token loss. SFT teaches format and behaviour from demonstrations
  lesson: generative-ai/01-llm-fundamentals/notes/07-sft-and-instruction-tuning
- front: How does the loss differ from pretraining?
  back: It is the same next-token cross-entropy, with padding (and usually the prompt) masked out via `ignore_index=-100`
  lesson: generative-ai/01-llm-fundamentals/notes/07-sft-and-instruction-tuning
- front: What does a classification fine-tune change?
  back: It replaces the head and usually trains only the last blocks and the head, taking the loss on the last token's logits
  lesson: generative-ai/01-llm-fundamentals/notes/07-sft-and-instruction-tuning
- front: How many SFT examples do you need?
  back: InstructGPT used about 13,000 and typical sets run from 10,000 to 100,000, but much of the format gain arrives early, as with Flan-PaLM and LIMA
  lesson: generative-ai/01-llm-fundamentals/notes/07-sft-and-instruction-tuning
- front: What happens if you fine-tune on unknown facts?
  back: The model fits them slowly, and as it does, test accuracy falls. Early stopping or "I don't know" labels reduce the damage
  lesson: generative-ai/01-llm-fundamentals/notes/07-sft-and-instruction-tuning
- front: Why does fine-tuning cause forgetting, and how do you limit it?
  back: Weights that held older knowledge move. Replay old data or limit which weights move
  lesson: generative-ai/01-llm-fundamentals/notes/07-sft-and-instruction-tuning
- front: Why train on comparisons at all?
  back: Comparing two acceptable answers is cheaper than writing a good one, and captures preferences demonstrations can't, such as which of two right answers is better
  lesson: generative-ai/01-llm-fundamentals/notes/08-preference-optimisation-overview
- front: What is the reward-model loss?
  back: '`−log σ(r(x, y_w) − r(x, y_l))`, which pushes the winner''s score above the loser''s and starts at `ln 2`'
  lesson: generative-ai/01-llm-fundamentals/notes/08-preference-optimisation-overview
- front: What does best-of-N give you?
  back: Many of the gains of RL with no RL training, at the serving cost of N samples per request
  lesson: generative-ai/01-llm-fundamentals/notes/08-preference-optimisation-overview
- front: Why doesn't raising both answers reduce the DPO loss?
  back: It depends only on the difference of the two shifts. The objective pays for separation, not for confidence
  lesson: generative-ai/01-llm-fundamentals/notes/08-preference-optimisation-overview
- front: What does Constitutional AI replace?
  back: Human harm labels, with model critiques, revisions and comparisons against written principles. People still write those principles and supply helpfulness data
  lesson: generative-ai/01-llm-fundamentals/notes/08-preference-optimisation-overview
- front: Why PEFT over full fine-tuning?
  back: Full fine-tuning needs gradients and optimizer state for every weight, several times the model's memory. PEFT trains a small set of new parameters and freezes the rest
  lesson: generative-ai/01-llm-fundamentals/notes/09-peft-and-fine-tuning-in-practice
- front: How does LoRA work?
  back: It adds a low-rank update `BA` to frozen weight matrices, starting from zero so the model is unchanged at first. It is merged for serving
  lesson: generative-ai/01-llm-fundamentals/notes/09-peft-and-fine-tuning-in-practice
- front: Which modules are usually targeted?
  back: The attention projections, commonly `q_proj` and `v_proj`, and more if the budget allows
  lesson: generative-ai/01-llm-fundamentals/notes/09-peft-and-fine-tuning-in-practice
- front: LoRA versus adapters and prefix tuning?
  back: Hu et al. found LoRA at or above the older methods on GPT-3, with no inference overhead once merged
  lesson: generative-ai/01-llm-fundamentals/notes/09-peft-and-fine-tuning-in-practice
- front: What is QLoRA?
  back: LoRA on a base held in 4-bit NF4, so the frozen weights take less memory during training
  lesson: generative-ai/01-llm-fundamentals/notes/09-peft-and-fine-tuning-in-practice
- front: What is the FTI architecture?
  back: Separate feature, training and inference pipelines, so each can change independently
  lesson: generative-ai/01-llm-fundamentals/notes/09-peft-and-fine-tuning-in-practice
- front: What are the five principles?
  back: Give direction, specify format, provide examples, evaluate quality, divide labor
  lesson: generative-ai/01-llm-fundamentals/notes/10-prompting-fundamentals
- front: Why does a prompt work at all?
  back: It is the conditioning context for next-token prediction, so it makes the answer you want a more likely continuation
  lesson: generative-ai/01-llm-fundamentals/notes/10-prompting-fundamentals
- front: Zero-shot or few-shot?
  back: Start with direction. Add 3–5 varied examples when the format must be reliable, accepting some loss of variety
  lesson: generative-ai/01-llm-fundamentals/notes/10-prompting-fundamentals
- front: How do you compare two prompts?
  back: Run both over a labelled, held-out set, several times. Rate blind, and log accuracy, parse rate, cost and latency
  lesson: generative-ai/01-llm-fundamentals/notes/10-prompting-fundamentals
- front: What does "let's think step by step" do?
  back: It prompts reasoning before the answer. It took text-davinci-002 from 17.7% to 78.7% on MultiArith. Modern reasoning models do this internally
  lesson: generative-ai/01-llm-fundamentals/notes/10-prompting-fundamentals
- front: What is self-consistency, and what does it cost?
  back: Sample several chains of thought and take the majority. It needs exactly comparable answers, and multiplies cost by the number of samples
  lesson: generative-ai/01-llm-fundamentals/notes/10-prompting-fundamentals
- front: When do you stop prompting and fine-tune?
  back: When format is unstable after good prompting, or a skill is missing and you have thousands of examples (chapter 09)
  lesson: generative-ai/01-llm-fundamentals/notes/10-prompting-fundamentals
- front: What is a Runnable?
  back: The common interface (`invoke`, `batch`, `stream` and async versions) implemented by models, prompts, parsers and chains, so that they compose
  lesson: generative-ai/01-llm-fundamentals/notes/11-langchain-basics
- front: What does `
  back: '` do? | It pipes one Runnable''s output into the next, giving the result all the Runnable methods'
  lesson: generative-ai/01-llm-fundamentals/notes/11-langchain-basics
- front: LCEL or `@chain`?
  back: LCEL for linear pipelines, where parallelism and streaming come free. `@chain` for branches and early exits
  lesson: generative-ai/01-llm-fundamentals/notes/11-langchain-basics
- front: '`with_structured_output` or an output parser?'
  back: The former uses the provider's tool or JSON mechanisms and is stronger. Use a parser for formats a provider can't enforce
  lesson: generative-ai/01-llm-fundamentals/notes/11-langchain-basics
- front: When do you move to LangGraph?
  back: When the flow needs loops, persistent state or human approval
  lesson: generative-ai/01-llm-fundamentals/notes/11-langchain-basics
- front: Stuff, refine, map-reduce or map-rerank?
  back: Stuff until the context limit. Refine for sequential synthesis. Map-reduce for parallel summaries. Map-rerank for lookup
  lesson: generative-ai/01-llm-fundamentals/notes/11-langchain-basics
- front: What does LangChain cost you?
  back: An extra abstraction, API churn and harder debugging
  lesson: generative-ai/01-llm-fundamentals/notes/11-langchain-basics
- front: What should the loss be at step 0?
  back: 'About `ln(vocab_size)`, since an untrained model should be near uniform: 4.17 for 65 characters'
  lesson: generative-ai/01-llm-fundamentals/notes/12-build-a-tiny-gpt
- front: How do you test a causal mask?
  back: Change the token at position *t* and confirm that logits before *t* are exactly unchanged
  lesson: generative-ai/01-llm-fundamentals/notes/12-build-a-tiny-gpt
- front: Why overfit one batch?
  back: A model that can't memorise a batch has a wiring bug. It is the fastest test of the model and optimizer
  lesson: generative-ai/01-llm-fundamentals/notes/12-build-a-tiny-gpt
- front: What does training-loss-near-zero mean by itself?
  back: Memorisation is possible. You need a validation loss to claim learning
  lesson: generative-ai/01-llm-fundamentals/notes/12-build-a-tiny-gpt
- front: Why does attention cost grow quadratically with context?
  back: Every position compares with every earlier one, so the matrix is `T × T`
  lesson: generative-ai/01-llm-fundamentals/notes/12-build-a-tiny-gpt
- front: What is weight tying?
  back: Sharing the token embedding matrix with the output head. It cuts parameters, from 163M to 124M in GPT-2 small
  lesson: generative-ai/01-llm-fundamentals/notes/12-build-a-tiny-gpt
- front: Karpathy or Raschka?
  back: Karpathy for intuition about gradients and training, Raschka for a clean reference implementation. They complement each other
  lesson: generative-ai/01-llm-fundamentals/notes/12-build-a-tiny-gpt
- front: Why is the API described as stateless?
  back: The server keeps no conversation. You send the whole history each time, so cost grows with it
  lesson: generative-ai/01-llm-fundamentals/notes/13-calling-models-from-code
- front: What does `stop_reason` tell you?
  back: 'Why generation ended: `end_turn`, `max_tokens`, `stop_sequence`, `tool_use`, `pause_turn` or `refusal`. Check it before reading content'
  lesson: generative-ai/01-llm-fundamentals/notes/13-calling-models-from-code
- front: How do you get structured output from current Claude models?
  back: '`messages.parse` with a schema, or `output_config.format`, or a `strict` tool under `auto` with a prompt instruction. Forcing a tool now returns a 400'
  lesson: generative-ai/01-llm-fundamentals/notes/13-calling-models-from-code
- front: Walk through a tool loop
  back: Call, append the full assistant content, run each `tool_use`, return all results in one user turn with their ids, repeat until a stop other than `tool_use`, with a cap
  lesson: generative-ai/01-llm-fundamentals/notes/13-calling-models-from-code
- front: Why stream?
  back: Time-to-first-token sets perceived speed, and it avoids request timeouts on long outputs
  lesson: generative-ai/01-llm-fundamentals/notes/13-calling-models-from-code
- front: How should a failed tool be handled?
  back: 'Return a `tool_result` with `is_error: true`, so that the model can recover'
  lesson: generative-ai/01-llm-fundamentals/notes/13-calling-models-from-code
- front: Which errors do you retry?
  back: 429 and 5xx with backoff, not 400. The SDK handles connection errors, 408, 409, 429 and 5xx
  lesson: generative-ai/01-llm-fundamentals/notes/13-calling-models-from-code
- front: Why would an old request start failing?
  back: Parameters are removed or changed on newer models, and old ids are retired. Pin the id and test before changing it
  lesson: generative-ai/01-llm-fundamentals/notes/13-calling-models-from-code
- front: Open weights or open source?
  back: Open weights release the parameters. The OSI definition also requires code and detailed data information under approved terms. Most LLMs are open-weight
  lesson: generative-ai/01-llm-fundamentals/notes/14-open-weight-models-and-local-inference
- front: What does the Llama community licence require?
  back: Attribution, a licence request above 700M monthly active users, and a "Llama" name prefix on models distributed after training on its outputs
  lesson: generative-ai/01-llm-fundamentals/notes/14-open-weight-models-and-local-inference
- front: How do you estimate memory?
  back: Parameters × bytes per parameter for the weights, then add the KV cache for your context, and leave headroom
  lesson: generative-ai/01-llm-fundamentals/notes/14-open-weight-models-and-local-inference
- front: What is GGUF?
  back: A single-file format for llama.cpp, in sizes named by bit width. It runs on a CPU and can offload layers to a GPU
  lesson: generative-ai/01-llm-fundamentals/notes/14-open-weight-models-and-local-inference
- front: Which quantization do you start with?
  back: '`Q4_K_M`, then compare with a higher level on your own eval'
  lesson: generative-ai/01-llm-fundamentals/notes/14-open-weight-models-and-local-inference
- front: Ollama, llama.cpp or transformers?
  back: Ollama for simplicity, llama.cpp for control and small devices, transformers for fine-tuning and research
  lesson: generative-ai/01-llm-fundamentals/notes/14-open-weight-models-and-local-inference
- front: When does local beat an API?
  back: Data residency, weight access, offline use or pinning. On cost, only at high and steady volume, once staff time is counted
  lesson: generative-ai/01-llm-fundamentals/notes/14-open-weight-models-and-local-inference
- front: Why read `base_model`?
  back: Licence and behaviour come from up the chain
  lesson: generative-ai/01-llm-fundamentals/notes/14-open-weight-models-and-local-inference
- front: What dominates the cost of a run?
  back: Compute-hours times price, set by parameters, tokens and hardware utilisation. Pretraining is about 98% of the compute for InstructGPT
  lesson: generative-ai/01-llm-fundamentals/notes/15-pretraining-runs-cost-and-scale
- front: Why not pretrain on your company's data?
  back: It is usually orders of magnitude too small, so continue pretraining or fine-tune. BloombergGPT is the exception, and even it relied on 363B tokens of curated finance text, mostly a web crawl, and a 1.3M A100-hour budget, for a 50.6B model that still lacked data by its own Chinchilla fit
  lesson: generative-ai/01-llm-fundamentals/notes/15-pretraining-runs-cost-and-scale
- front: What is the difference between FLOPs and FLOP/s?
  back: FLOPs count the work and FLOP/s the speed. Hours are FLOPs divided by (FLOP/s × utilisation), and mixing them up can leave you an order of magnitude out
  lesson: generative-ai/01-llm-fundamentals/notes/15-pretraining-runs-cost-and-scale
- front: Should you train at 20 tokens per parameter?
  back: Only if training cost is all that matters. Llama went past it on purpose, because a smaller model on more tokens costs more to train and less to run
  lesson: generative-ai/01-llm-fundamentals/notes/15-pretraining-runs-cost-and-scale
- front: What is the critical batch size?
  back: The batch at which training takes twice the minimum steps and data. The gradient noise scale predicted it to within an order of magnitude, and it grows as the loss falls
  lesson: generative-ai/01-llm-fundamentals/notes/15-pretraining-runs-cost-and-scale
- front: What does MFU measure?
  back: Achieved tokens per second against what the chips' peak FLOP/s would allow, without counting recomputed activations. PaLM reached 46.2%, and by the same paper's calculation GPT-3 reached 21.3%
  lesson: generative-ai/01-llm-fundamentals/notes/15-pretraining-runs-cost-and-scale
---
