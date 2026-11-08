---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- generative-ai/01-llm-fundamentals/slides/deck.yaml
cards:
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
---
