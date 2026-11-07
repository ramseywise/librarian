---
title: 'Technical interview questions: multiple choice'
summary: Multiple-choice questions from the technical-questions MCQ bank, one answer each.
questions:
- id: a1
  prompt: A Python service runs four threads doing pure CPU-bound numeric work on an 8-core machine. Throughput
    is no better than single-threaded. Why?
  options:
  - The threads are deadlocking on a shared lock
  - The GIL allows only one thread to execute Python bytecode at a time
  - Four threads is too few to saturate 8 cores
  - Thread creation overhead dominates the workload
  answer: The GIL allows only one thread to execute Python bytecode at a time
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a2
  prompt: Which change gives *true parallelism* for that CPU-bound Python workload?
  options:
  - Switch to `asyncio`
  - Increase the thread count to 8
  - Switch to `multiprocessing`
  - Release the GIL with a `threading.Lock`
  answer: Switch to `multiprocessing`
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a3
  prompt: What does async programming provide in Python?
  options:
  - Parallel execution across CPU cores
  - Concurrency, not parallel execution
  - Automatic GIL release for CPU work
  - Thread-safe access to shared mutable state
  answer: Concurrency, not parallel execution
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a4
  prompt: Inside an `async def` handler, which call is the classic pitfall that stalls every other coroutine
    on the loop?
  options:
  - '`await httpx.AsyncClient().get(url)`'
  - '`await asyncio.sleep(1)`'
  - '`requests.get(url)`'
  - '`await asyncio.gather(*tasks)`'
  answer: '`requests.get(url)`'
  explanation: '`requests.get` is synchronous — it blocks the event loop. The fix is `httpx` or another
    async client. Forgotten `await` and CPU-heavy work in a coroutine are the other two named pitfalls.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a5
  prompt: 'A race condition arises when:'
  options:
  - Two processes read the same immutable tuple
  - Multiple threads modify shared data simultaneously
  - An async task is awaited twice
  - A thread is starved by the scheduler
  answer: Multiple threads modify shared data simultaneously
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a6
  prompt: Which is *not* one of the three standard fixes for a race condition?
  options:
  - Locks/mutexes (`threading.Lock`)
  - Immutable data structures
  - Avoiding shared mutable state
  - Increasing the thread pool size
  answer: Increasing the thread pool size
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a7
  prompt: You need `popleft()` in a BFS inner loop. Why `collections.deque` over a list?
  options:
  - '`deque` uses less memory per element'
  - '`deque` popleft is O(1); list popleft is O(n)'
  - '`deque` is thread-safe and lists are not'
  - Lists cannot pop from the front
  answer: '`deque` popleft is O(1); list popleft is O(n)'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a8
  prompt: 'Sorting an array first, then applying two pointers, typically changes brute force from:'
  options:
  - O(n log n) → O(n)
  - O(n²) → O(n log n)
  - O(n³) → O(n²)
  - O(2ⁿ) → O(n²)
  answer: O(n²) → O(n log n)
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a9
  prompt: Which traversal of a binary search tree yields values in sorted order?
  options:
  - Preorder (root → left → right)
  - Inorder (left → root → right)
  - Postorder (left → right → root)
  - Level-order (BFS)
  answer: Inorder (left → root → right)
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a10
  prompt: How do you correctly validate a BST?
  options:
  - Check each node is greater than its immediate parent
  - Check each node's left child < node < right child, locally
  - Pass min/max bounds down the recursion
  - Inorder traverse and check the root is the median
  answer: Pass min/max bounds down the recursion
  explanation: The local check (B) wrongly accepts a node deeper in the left subtree that exceeds the
    root. Bounds must be threaded down.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a11
  prompt: After Floyd's fast/slow pointers meet inside a cycle, how do you find the cycle's start?
  options:
  - Continue advancing the fast pointer at speed 2
  - Reset one pointer to head, then advance both at speed 1
  - Reset both pointers to head and advance at speeds 1 and 2 again
  - Count the cycle length, then advance that many steps from head
  answer: Reset one pointer to head, then advance both at speed 1
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a12
  prompt: 'Union-Find with path compression and union by rank costs, per operation:'
  options:
  - O(log n)
  - O(α(n))
  - O(1) worst case
  - O(n) amortized
  answer: O(α(n))
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a13
  prompt: Which pair of conditions signals a dynamic-programming problem?
  options:
  - Sorted input + a monotonic predicate
  - Optimal substructure + overlapping subproblems
  - A recursive definition + a base case
  - Greedy choice property + matroid structure
  answer: Optimal substructure + overlapping subproblems
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a14
  prompt: 'Top-down memoization vs bottom-up tabulation:'
  options:
  - Top-down is better for large inputs; bottom-up is easier to reason about
  - Top-down is easier to reason about; bottom-up is better for large inputs and space optimization
  - They have identical time and space profiles
  - Bottom-up always uses less time; top-down always uses less space
  answer: Top-down is easier to reason about; bottom-up is better for large inputs and space optimization
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a15
  prompt: '`WHERE` and `HAVING` differ how?'
  options:
  - '`WHERE` filters groups after aggregation; `HAVING` filters rows before'
  - '`WHERE` filters rows before grouping; `HAVING` filters groups after aggregating'
  - They are interchangeable in a `GROUP BY` query
  - '`HAVING` works only with `COUNT`'
  answer: '`WHERE` filters rows before grouping; `HAVING` filters groups after aggregating'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a16
  prompt: '`ROW_NUMBER`, `RANK`, `DENSE_RANK` on tied values:'
  options:
  - All three assign the same rank to ties
  - '`ROW_NUMBER` no ties; `RANK` ties then skips; `DENSE_RANK` ties then does not skip'
  - '`ROW_NUMBER` ties then skips; `RANK` no ties; `DENSE_RANK` ties without skipping'
  - '`RANK` and `DENSE_RANK` are aliases; only `ROW_NUMBER` differs'
  answer: '`ROW_NUMBER` no ties; `RANK` ties then skips; `DENSE_RANK` ties then does not skip'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a17
  prompt: 'The canonical "keep the latest row per user" idiom is:'
  options:
  - '`SELECT DISTINCT ON (user_id) ... ORDER BY created_at`'
  - '`GROUP BY user_id HAVING created_at = MAX(created_at)`'
  - '`ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC)` then `WHERE rn = 1`'
  - '`SELECT user_id, MAX(created_at)` joined back on both columns'
  answer: '`ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC)` then `WHERE rn = 1`'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a18
  prompt: A `LEFT JOIN` returns more rows than the left table has. What happened?
  options:
  - The join key is null in some left rows
  - The right table has duplicate join keys — fan-out
  - '`LEFT JOIN` always returns at least as many rows as the right table'
  - The query needs `SELECT DISTINCT`
  answer: The right table has duplicate join keys — fan-out
  explanation: Row count equals the left table only when the join key is unique on the right. Ask "how
    many rows does this join produce?" before running it.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a19
  prompt: 'State the GIL''s effect directly: what does it constrain?'
  options:
  - It prevents a process from spawning child processes
  - It allows threads to execute Python bytecode in true parallel
  - It limits execution of Python bytecode to one thread at a time
  - It improves CPU-bound performance by pinning threads to cores
  answer: It limits execution of Python bytecode to one thread at a time
  explanation: 'The GIL constrains *bytecode execution*, not the interpreter as a whole — which is exactly
    why threads still help for I/O. A blocking socket or file read releases the GIL while it waits, so
    other threads run. CPU work never yields it, so threads serialize (A1) and `multiprocessing` is the
    fix (A2). "Whenever possible" is the trap answer: threads add lock and shared-state hazards for no
    CPU gain.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a20
  prompt: 'Multithreading in Python is the right tool for:'
  options:
  - CPU-bound tasks only
  - I/O-bound tasks
  - Anything parallelizable — it is always worth trying
  - Math-heavy numerical workloads
  answer: I/O-bound tasks
  explanation: 'The GIL constrains *bytecode execution*, not the interpreter as a whole — which is exactly
    why threads still help for I/O. A blocking socket or file read releases the GIL while it waits, so
    other threads run. CPU work never yields it, so threads serialize (A1) and `multiprocessing` is the
    fix (A2). "Whenever possible" is the trap answer: threads add lock and shared-state hazards for no
    CPU gain.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b1
  prompt: 'The course calls one thing "the #1 practical sin" in applied ML. It is:'
  options:
  - Overfitting the validation set
  - Data leakage
  - Choosing the wrong model family
  - Failing to tune hyperparameters
  answer: Data leakage
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b2
  prompt: Which practice does *not* prevent leakage?
  options:
  - Fitting scalers and encoders on the training split only
  - Splitting before any target-aware transform
  - Using time-based splits for temporal data
  - Averaging cross-validation scores across more folds
  answer: Averaging cross-validation scores across more folds
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b3
  prompt: Under heavy class imbalance, which is more informative?
  options:
  - ROC-AUC, because it is threshold-independent
  - PR-AUC, because it focuses on the positive class
  - Accuracy, with a tuned threshold
  - R², because it handles skew
  answer: PR-AUC, because it focuses on the positive class
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b4
  prompt: 'The interview move the course says to make first when discussing any model result:'
  options:
  - Report the cross-validated standard deviation
  - Name the naive baseline (majority class / mean predictor)
  - State the model family and its hyperparameters
  - Show the confusion matrix
  answer: Name the naive baseline (majority class / mean predictor)
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b5
  prompt: 'L1 vs L2 regularization:'
  options:
  - L1 shrinkage, L2 sparsity
  - L1 sparsity (feature selection), L2 shrinkage
  - Both produce sparsity; L2 is just faster
  - L1 applies to trees, L2 to linear models
  answer: L1 sparsity (feature selection), L2 shrinkage
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b6
  prompt: Why gradient boosting over a neural net on tabular data? The course names four reasons — which
    is *not* one?
  options:
  - Sample efficiency
  - Native missing/categorical handling
  - Guaranteed convexity of the loss surface
  - Less tuning, plus interpretability tooling
  answer: Guaranteed convexity of the loss surface
  explanation: Neural nets win with huge data or mixed modalities; convexity is not a GBM property.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b7
  prompt: 'PCA vs UMAP:'
  options:
  - PCA preserves neighborhood structure; UMAP preserves linear variance
  - PCA is linear variance; UMAP is neighborhood structure, and is "for looking, not for
  - Both are linear; UMAP is just faster
  - UMAP is deterministic; PCA is stochastic
  answer: PCA is linear variance; UMAP is neighborhood structure, and is "for looking, not for
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b8
  prompt: 'Covariate drift vs concept drift:'
  options:
  - Covariate = the input distribution shifts; concept = the input→target relationship shifts
  - Covariate = the target relationship shifts; concept = the inputs shift
  - Both describe label noise increasing over time
  - Covariate applies to classification, concept to regression
  answer: Covariate = the input distribution shifts; concept = the input→target relationship shifts
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b9
  prompt: Model is excellent offline, poor in production. The course gives an ordered checklist. What
    do you check *first*?
  options:
  - Drift
  - Leakage
  - Feedback loops
  - Whether the eval metric matches the business metric
  answer: Leakage
  explanation: 'The order is load-bearing: leakage → train/serve skew → drift → survivorship → feedback
    loops → metric mismatch. Leakage is both most common and cheapest to check.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b10
  prompt: Which metric pair correctly captures outlier sensitivity in regression?
  options:
  - MAE penalizes outliers more than RMSE
  - RMSE penalizes outliers more than MAE
  - Both are equally sensitive; only R² differs
  - MAPE is the most outlier-robust choice
  answer: RMSE penalizes outliers more than MAE
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b11
  prompt: 'MAPE''s specific pitfall:'
  options:
  - It is undefined for negative predictions
  - It blows up near zero actuals
  - It cannot be averaged across series
  - It requires normally distributed residuals
  answer: It blows up near zero actuals
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b12
  prompt: 'Calibration means:'
  options:
  - The model's ranking is correct
  - The predicted probabilities mean what they say
  - The decision threshold is tuned to maximize F1
  - Features are standardized before training
  answer: The predicted probabilities mean what they say
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b13
  prompt: Which tools assess calibration?
  options:
  - Silhouette score and elbow plots
  - Brier score and reliability curves
  - SHAP values and permutation importance
  - Precision@K and MRR
  answer: Brier score and reliability curves
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b14
  prompt: '"Hidden Technical Debt in Machine Learning Systems" (NIPS 2015) names which failure modes?'
  options:
  - Overfitting, underfitting, and leakage
  - Entanglement, feedback loops, pipeline jungles
  - Drift, staleness, and skew
  - Bias, variance, and irreducible error
  answer: Entanglement, feedback loops, pipeline jungles
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b15
  prompt: 'From Ng''s "Structuring ML Projects", human-level performance is used as:'
  options:
  - A hard ceiling the model must not exceed
  - A proxy for Bayes error
  - The threshold for shipping
  - The baseline for the naive predictor
  answer: A proxy for Bayes error
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b16
  prompt: Choosing K in k-means, the honest senior answer adds what to elbow/silhouette?
  options:
  - The Bayesian information criterion
  - That K encodes a product decision — how many segments can ops actually act on
  - That K should equal the number of features
  - That K should be tuned against downstream AUC only
  answer: That K encodes a product decision — how many segments can ops actually act on
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c1
  prompt: 'Scaled dot-product attention is:'
  options:
  - '`softmax(QKᵀ/d)V`'
  - '`softmax(QKᵀ/√d)V`'
  - '`softmax(QᵀK/√d)V`'
  - '`softmax(QKᵀ)V/√d`'
  answer: '`softmax(QKᵀ/√d)V`'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c2
  prompt: Why divide by √d?
  options:
  - To normalize the output to unit length
  - To prevent softmax saturating in high dimensions
  - To make the operation numerically invertible
  - To match the residual stream scale
  answer: To prevent softmax saturating in high dimensions
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c3
  prompt: 'Self-attention compares every token with every earlier one. That quadratic cost most directly
    explains:'
  options:
  - Why models hallucinate
  - Why long contexts are expensive to process
  - Why token counts vary between languages
  - Why training can forget earlier data
  answer: Why long contexts are expensive to process
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c4
  prompt: Which is *not* a named way to inject positional information?
  options:
  - Learned positional embeddings
  - RoPE
  - ALiBi
  - Layer normalization
  answer: Layer normalization
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c5
  prompt: 'A decoder-only model (GPT family) is characterized by:'
  options:
  - Bidirectional attention over the full sequence
  - A causal mask
  - Cross-attention to an encoder stack
  - Masked-token prediction as its objective
  answer: A causal mask
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c6
  prompt: 'The KV cache is described as the mechanism underneath:'
  options:
  - Speculative decoding
  - Prompt caching
  - Quantization
  - Mixture-of-experts routing
  answer: Prompt caching
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c7
  prompt: 'Even at temperature 0, production output isn''t fully deterministic. Named causes:'
  options:
  - Tokenizer drift, prompt truncation, retry logic
  - Batching, floating point, hardware and version differences
  - Sampling seeds, top-p, top-k
  - Load balancing, caching, streaming
  answer: Batching, floating point, hardware and version differences
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c8
  prompt: 'Prefill vs decode:'
  options:
  - Prefill is sequential and expensive per token; decode is parallel and cheap
  - Prefill is parallel and cheap per token; decode is sequential and expensive
  - Both are parallel; decode is just longer
  - Prefill dominates cost in long-output workloads
  answer: Prefill is parallel and cheap per token; decode is sequential and expensive
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c9
  prompt: Given C8, which discipline follows directly?
  options:
  - Larger batch sizes
  - Output-length discipline and streaming
  - Higher temperature for diversity
  - Longer system prompts to amortize setup
  answer: Output-length discipline and streaming
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c10
  prompt: 'Speculative decoding is primarily:'
  options:
  - A memory-reduction technique
  - A latency technique
  - A quality-improvement technique
  - A training-efficiency technique
  answer: A latency technique
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c11
  prompt: 'RLHF''s characteristic failure mode:'
  options:
  - Catastrophic forgetting
  - Reward hacking
  - Mode collapse to the base model
  - Gradient explosion
  answer: Reward hacking
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c12
  prompt: DPO differs from RLHF how?
  options:
  - It uses different data — ratings instead of preference pairs
  - It skips the reward model and optimizes preference pairs directly
  - It requires an on-policy RL loop with PPO
  - It only works on models under 7B parameters
  answer: It skips the reward model and optimizes preference pairs directly
  explanation: DPO and RLHF consume the *same* preference data. The difference is no reward model and
    no RL loop — "the common industry default now."
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c13
  prompt: 'DPO''s stated trade-off:'
  options:
  - Trades stability for controllability
  - Trades some controllability for stability
  - Trades cost for alignment quality
  - Trades data efficiency for compute
  answer: Trades some controllability for stability
  explanation: DPO and RLHF consume the *same* preference data. The difference is no reward model and
    no RL loop — "the common industry default now."
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c14
  prompt: 'Constitutional AI / RLAIF replaces human labels with:'
  options:
  - Synthetic preference pairs sampled at random
  - AI feedback guided by principles, via a critique-and-revise loop
  - A larger reward model
  - Rule-based filters at inference time
  answer: AI feedback guided by principles, via a critique-and-revise loop
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c15
  prompt: Where does the adaptation ladder place LoRA?
  options:
  - Before RAG, since it is cheaper
  - After RAG, before full fine-tuning
  - After full fine-tuning, as a compression step
  - Outside the ladder — it is a serving optimization
  answer: After RAG, before full fine-tuning
  explanation: The ladder is prompting → few-shot → RAG → PEFT/LoRA → full fine-tune, ordered cheapest
    and least invasive first. They compose.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c16
  prompt: 'QLoRA is:'
  options:
  - LoRA with quantized adapter weights
  - LoRA with a quantized base model
  - Quantization applied after a LoRA merge
  - A quantization-aware training method
  answer: LoRA with a quantized base model
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c17
  prompt: LoRA trains roughly what share of parameters?
  options:
  - ~0.001–0.01%
  - ~0.1–1%
  - ~5–10%
  - ~25%
  answer: ~0.1–1%
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c18
  prompt: 'For an API-only model where you cannot touch weights, preference data goes into:'
  options:
  - A local reward model
  - Prompts and evals
  - A fine-tuning endpoint
  - The KV cache
  answer: Prompts and evals
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c19
  prompt: '"Lost in the middle" describes:'
  options:
  - Truncation of the middle of a long prompt by the tokenizer
  - Models using information at the start and end of a long context better than the middle
  - Retrieval returning mid-ranked documents
  - Positional embeddings failing past their trained length
  answer: Models using information at the start and end of a long context better than the middle
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c20
  prompt: 'The course''s stated mitigation for long-context degradation:'
  options:
  - Bigger context windows
  - Context engineering, not bigger windows
  - Lower temperature
  - More attention heads
  answer: Context engineering, not bigger windows
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c21
  prompt: 'The `temperature` parameter controls:'
  options:
  - The maximum token length of the response
  - The randomness of the model's output
  - The speed of inference
  - The size of the model being served
  answer: The randomness of the model's output
  explanation: 'Temperature scales the logits before sampling — low values concentrate mass on the top
    tokens, high values flatten the distribution. It is not a length, latency, or capacity control. Note
    the interaction with **C7**: temperature 0 removes *sampling* randomness but not nondeterminism from
    batching, floating point, and hardware or version differences.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c22
  prompt: 'The main benefit of chain-of-thought prompting is that it:'
  options:
  - Reduces token usage
  - Eliminates hallucination completely
  - Improves reasoning by breaking a problem into intermediate steps
  - Speeds up inference
  answer: Improves reasoning by breaking a problem into intermediate steps
  explanation: 'CoT buys reasoning quality by spending intermediate tokens — so it *raises* token usage
    and latency, which is why A and D are inverted traps. It reduces reasoning errors; it does not eliminate
    hallucination (C), since a fluent wrong chain is still wrong. Pairs with the **C15** ladder: it is
    a prompting-tier move, tried before RAG or fine-tuning.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c23
  prompt: 'For most tasks, the recommended number of few-shot examples is:'
  options:
  - 0–1
  - 2–5
  - 5–10
  - 10+
  answer: 2–5
  explanation: 2–5 is the working default. Below that the format is underspecified; past ~5 you pay context
    on every call for diminishing gains, and the model starts copying surface patterns of the examples
    rather than the task. If more examples keep helping, that is the signal to climb the **C15** ladder
    to retrieval or fine-tuning.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d1
  prompt: 'The canonical pipeline, with optional stages in parentheses:'
  options:
  - Ingest → embed → chunk → index; query → retrieve → generate
  - Ingest → chunk → embed → index; query → (rewrite) → retrieve → (rerank) → generate → (verify)
  - Chunk → ingest → index → embed; query → rerank → retrieve → generate
  - Ingest → chunk → index → embed; query → retrieve → (verify) → generate
  answer: Ingest → chunk → embed → index; query → (rewrite) → retrieve → (rerank) → generate → (verify)
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d2
  prompt: 'Chunking priority order:'
  options:
  - Fixed-size windows, then semantic splitting as a refinement
  - Document structure (headings) first, then recursive paragraph/sentence boundaries, to a token budget
  - Semantic chunking first, falling back to fixed windows
  - Sentence-level always, merged upward to fill the budget
  answer: Document structure (headings) first, then recursive paragraph/sentence boundaries, to a token
    budget
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d3
  prompt: 'The course''s stance on semantic chunking:'
  options:
  - The recommended default for production corpora
  - Expensive at ingest and inconsistent — not the default
  - Required whenever documents lack headings
  - Equivalent to recursive splitting but faster
  answer: Expensive at ingest and inconsistent — not the default
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d4
  prompt: 'Typical chunk token budget and overlap:'
  options:
  - ~256 tokens, ~32 overlap
  - ~512 tokens, ~64 overlap
  - ~1024 tokens, ~128 overlap
  - ~2048 tokens, ~256 overlap
  answer: ~512 tokens, ~64 overlap
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d5
  prompt: 'Parent/child chunking means:'
  options:
  - Index large chunks, generate from extracted sentences
  - Index small chunks, generate from their parent
  - Duplicate each chunk at two granularities in the same index
  - Chunk by document hierarchy only
  answer: Index small chunks, generate from their parent
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d6
  prompt: A `min_tokens` filter at ingest can cause which silent failure?
  options:
  - Oversized chunks are truncated mid-sentence
  - Short-but-valid sections (one-line FAQ answers) are dropped from the index entirely
  - Embeddings drift toward the corpus mean
  - BM25 scores become incomparable with cosine
  answer: Short-but-valid sections (one-line FAQ answers) are dropped from the index entirely
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d7
  prompt: 'E5-family embedding models require:'
  options:
  - L2-normalized inputs
  - '`"query: "` / `"passage: "` prefixes'
  - Lowercased text
  - A fixed 512-token pad
  answer: '`"query: "` / `"passage: "` prefixes'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d9
  prompt: Vector-only search and BM25-only search fail in which way?
  options:
  - Vector misses paraphrases; BM25 misses exact tokens
  - Vector misses exact tokens (product names, error codes); BM25 misses paraphrases
  - Both miss exact tokens; only reranking recovers them
  - Vector misses short queries; BM25 misses long ones
  answer: Vector misses exact tokens (product names, error codes); BM25 misses paraphrases
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d10
  prompt: Reciprocal Rank Fusion uses which constant?
  options:
  - k = 10
  - k = 60
  - k = 100
  - k is tuned per corpus
  answer: k = 60
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d11
  prompt: Why RRF instead of a weighted sum of BM25 and cosine scores?
  options:
  - RRF is provably optimal for hit rate
  - BM25 and cosine scores have incomparable distributions; rank fusion needs no score normalization
  - RRF is faster to compute
  - Weighted sums require normalized embeddings
  answer: BM25 and cosine scores have incomparable distributions; rank fusion needs no score normalization
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d13
  prompt: 'CRAG vs Self-RAG, in one line:'
  options:
  - CRAG decides inside the LLM during generation; Self-RAG decides in the graph topology
  - CRAG decides in the graph topology before generation; Self-RAG decides inside the LLM during generation
  - Both decide before generation; CRAG adds a retry
  - Both decide during generation; Self-RAG adds a grader
  answer: CRAG decides in the graph topology before generation; Self-RAG decides inside the LLM during
    generation
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d14
  prompt: 'Self-RAG''s canonical mechanism (Asai et al.):'
  options:
  - LLM-driven query expansion into N paraphrases
  - Reflection tokens (`[Retrieve]`, `[IsRel]`, `[IsSup]`) emitted mid-generation
  - A confidence gate on retrieved chunks with fallback
  - Entity-graph traversal alongside vector search
  answer: Reflection tokens (`[Retrieve]`, `[IsRel]`, `[IsSup]`) emitted mid-generation
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d15
  prompt: 'Some blogs use "Self-RAG" to mean LLM query expansion. In an interview you should:'
  options:
  - Use the blog definition, since it is more common
  - Surface the ambiguity and name the canonical version — that itself scores
  - Avoid the term entirely
  - Correct the interviewer firmly and move on
  answer: Surface the ambiguity and name the canonical version — that itself scores
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d16
  prompt: 'HyDE works by:'
  options:
  - Embedding the question and expanding with synonyms
  - Generating a hypothetical answer and embedding *that* for search
  - Retrieving twice and fusing the ranks
  - Reranking with a cross-encoder on hypothetical pairs
  answer: Generating a hypothetical answer and embedding *that* for search
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d17
  prompt: 'HyDE''s cost:'
  options:
  - Roughly doubles total pipeline latency
  - One extra small-model call, ~100–200ms
  - Negligible — it reuses the main generation call
  - One extra embedding call only
  answer: One extra small-model call, ~100–200ms
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d18
  prompt: 'Multi-query (RAG-Fusion) recall gain and its diminishing-returns point:'
  options:
  - +5%, past 2 variants
  - +10–15%, past 3 variants
  - +20–25%, past 5 variants
  - +30%, past 10 variants
  answer: +10–15%, past 3 variants
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d19
  prompt: 'GraphRAG restraint — the course''s caution:'
  options:
  - GraphRAG is always preferable for enterprise corpora
  - It is overkill for factual lookup; for wiki-shaped corpora existing link structure already gives a
    traversable graph
  - It should replace vector search once entity extraction is available
  - It only works with proprietary graph databases
  answer: It is overkill for factual lookup; for wiki-shaped corpora existing link structure already gives
    a traversable graph
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d20
  prompt: Debugging poor retrieval, what do you measure *first*?
  options:
  - Whether the LLM prompt includes the retrieved context
  - recall@k on a golden set
  - Cross-encoder reranker latency
  - Chunk overlap settings
  answer: recall@k on a golden set
  explanation: The order matters — golden-set recall@k, then embedding/corpus language match, prefix rules,
    chunk truncation, *then* hybrid + reranker, all before touching the LLM.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d21
  prompt: 'RAGAS''s four standard metrics:'
  options:
  - precision, recall, F1, accuracy
  - faithfulness, answer_relevancy, context_precision, context_recall
  - groundedness, hallucination rate, MRR, nDCG
  - hit rate, coverage, calibration, naturalness
  answer: faithfulness, answer_relevancy, context_precision, context_recall
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d22
  prompt: Which is *not* one of the three named cases for skipping RAG?
  options:
  - Stable narrow knowledge that fits the context window
  - Latency-critical paths
  - Poor-quality corpora
  - Corpora larger than 1M documents
  answer: Corpora larger than 1M documents
  explanation: Scale is a reason to change the index (ANN/HNSW), not to abandon RAG.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e1
  prompt: 'Anthropic''s distinction between workflows and agents:'
  options:
  - Workflows use one model call; agents use many
  - Workflows orchestrate through predefined code paths; agents let the LLM dynamically direct its own
    process and tool use
  - Workflows are stateless; agents are stateful
  - Workflows run locally; agents run as services
  answer: Workflows orchestrate through predefined code paths; agents let the LLM dynamically direct its
    own process and tool use
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e2
  prompt: 'The course says the interview answer that "is always open here" is:'
  options:
  - '"Use an agent — it generalizes better"'
  - Naming the workflow/agent distinction and defending the cheaper option
  - '"It depends on the model"'
  - Choosing whichever the interviewer's company ships
  answer: Naming the workflow/agent distinction and defending the cheaper option
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e3
  prompt: Which is *not* one of the five workflow patterns?
  options:
  - Prompt chaining
  - Routing
  - Retrieval augmentation
  - Evaluator–optimizer
  answer: Retrieval augmentation
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e4
  prompt: Parallelization splits into which two variations?
  options:
  - Sharding and replication
  - Sectioning and voting
  - Fan-out and fan-in
  - Map and reduce
  answer: Sectioning and voting
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e5
  prompt: 'Orchestrator–workers differs from sectioning because:'
  options:
  - It runs workers sequentially
  - Subtasks are determined dynamically by the orchestrator, not fixed in advance
  - Workers share a single context window
  - It requires a human in the loop
  answer: Subtasks are determined dynamically by the orchestrator, not fixed in advance
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e6
  prompt: '"Agent = Model + Harness" — the harness contributes:'
  options:
  - The system prompt and tool definitions
  - Acceptance baseline, execution boundary, feedback signals, rollback mechanism
  - Retry logic, caching, logging, and metrics
  - Memory, planning, tools, and reflection
  answer: Acceptance baseline, execution boundary, feedback signals, rollback mechanism
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e7
  prompt: 'ACI (agent–computer interface) design borrows "poka-yoke" to mean:'
  options:
  - Fail fast on invalid input
  - Design the tool so the mistake is impossible to make
  - Log every tool call for later review
  - Require confirmation before destructive actions
  answer: Design the tool so the mistake is impossible to make
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e8
  prompt: 'The course''s concrete poka-yoke example:'
  options:
  - Enum-typed arguments instead of free-form strings
  - Requiring absolute paths so relative-path errors cannot occur
  - A dry-run flag on every write tool
  - Rate limiting per tool
  answer: Requiring absolute paths so relative-path errors cannot occur
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e9
  prompt: Task length is a design threshold. Beyond roughly what duration does crash recovery become mandatory?
  options:
  - ~5 minutes
  - ~30 minutes
  - ~2 hours
  - ~1 day
  answer: ~30 minutes
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e10
  prompt: 'The four memory types:'
  options:
  - Short-term, long-term, cache, archive
  - Working, episodic, semantic, procedural
  - Scratchpad, vector, graph, relational
  - Session, user, org, global
  answer: Working, episodic, semantic, procedural
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e11
  prompt: 'For agent memory, the course''s stated bias:'
  options:
  - Recall over precision — better to surface too much than miss something
  - Precision over recall — a wrong memory is worse than a missing one
  - Recency over relevance
  - Completeness over compactness
  answer: Precision over recall — a wrong memory is worse than a missing one
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e12
  prompt: 'Subagents'' primary architectural value:'
  options:
  - Parallel speedup
  - Acting as a context firewall — the parent sees only the summary
  - Model diversity
  - Cost reduction through smaller models
  answer: Acting as a context firewall — the parent sees only the summary
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e13
  prompt: 'MCP vs A2A:'
  options:
  - MCP is agent↔agent; A2A is model↔tool
  - MCP is model↔tool; A2A is agent↔agent
  - Both are model↔tool; A2A adds authentication
  - Both are agent↔agent; MCP adds a schema layer
  answer: MCP is model↔tool; A2A is agent↔agent
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e14
  prompt: 'pass@k vs pass^k:'
  options:
  - pass@k is deployment reliability; pass^k is the capability ceiling
  - pass@k is the capability ceiling (succeeds at least once in k); pass^k is deployment reliability (succeeds
    all k times)
  - They are the same metric under different notation
  - pass@k applies to code; pass^k applies to tool use
  answer: pass@k is the capability ceiling (succeeds at least once in k); pass^k is deployment reliability
    (succeeds all k times)
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e15
  prompt: Which does a *production* SLA actually depend on?
  options:
  - pass@k
  - pass^k
  - mean reward per episode
  - Single-shot accuracy
  answer: pass^k
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e16
  prompt: 'PRINCE (Bayer × Thoughtworks, Fowler 2026) is cited as evidence for:'
  options:
  - Multi-agent reinforcement learning in production
  - A real-world agent architecture pattern — Search → Ask → Do
  - Graph-based memory outperforming vector memory
  - Fine-tuning beating prompting for tool use
  answer: A real-world agent architecture pattern — Search → Ask → Do
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e17
  prompt: 'Multi-agent reinforcement learning (MARL) in production LLM stacks is:'
  options:
  - The standard coordination approach
  - Not used — a common interview trap when someone conflates "multi-agent" with MARL
  - Used only for evaluator–optimizer loops
  - Used by orchestrator–workers under the hood
  answer: Not used — a common interview trap when someone conflates "multi-agent" with MARL
  explanation: '"Multi-agent" in industry means orchestration patterns, not MARL. If an interviewer uses
    the term loosely, disambiguate rather than play along.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e18
  prompt: 'Evaluator–optimizer is the right pattern when:'
  options:
  - Subtasks are independent and can run concurrently
  - There are clear evaluation criteria and iterative refinement adds measurable value
  - Input classification determines which specialized path to take
  - The task decomposes into fixed sequential steps
  answer: There are clear evaluation criteria and iterative refinement adds measurable value
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e19
  prompt: 'Building agent tools, the course''s advice on how many:'
  options:
  - As many as possible — the model will pick
  - Few, well-described, hard to misuse
  - One generic tool with a large argument schema
  - One tool per API endpoint, mirroring the backend
  answer: Few, well-described, hard to misuse
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e20
  prompt: 'Grading agents on trajectory as well as outcome matters because:'
  options:
  - Trajectory grading is cheaper
  - An agent can reach the right answer by an unsafe or non-reproducible path
  - Outcome grading requires human labels
  - Trajectory is the only observable signal in production
  answer: An agent can reach the right answer by an unsafe or non-reproducible path
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f1
  prompt: 'Prefix caching requires:'
  options:
  - Semantically similar prompts
  - A byte-identical prefix
  - The same model and temperature
  - A dedicated cache endpoint
  answer: A byte-identical prefix
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f2
  prompt: 'The layout rule that follows:'
  options:
  - Dynamic content first, static content last
  - Static content first, dynamic content last
  - Alphabetical ordering of message blocks
  - Shortest blocks first
  answer: Static content first, dynamic content last
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f3
  prompt: 'Prefix caching''s approximate input-cost saving:'
  options:
  - ~30%
  - ~50%
  - ~90%
  - ~99%
  answer: ~90%
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f4
  prompt: How do you verify a cache hit?
  options:
  - Compare latency against a baseline
  - Read `cache_read_input_tokens` in the response usage
  - Check the response `id` prefix
  - Enable debug logging on the SDK
  answer: Read `cache_read_input_tokens` in the response usage
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f5
  prompt: 'Prefix caching and semantic caching are:'
  options:
  - The same mechanism at different layers
  - Different — prefix caching reuses exact-prefix computation; semantic caching returns a stored response
    for a similar query
  - Different — prefix caching is client-side, semantic caching is provider-side
  - Sequential stages of the same optimization
  answer: Different — prefix caching reuses exact-prefix computation; semantic caching returns a stored
    response for a similar query
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f6
  prompt: 'Semantic caching''s characteristic risk:'
  options:
  - Cache stampede under load
  - Serving a stored answer to a query that is similar but not equivalent
  - Unbounded memory growth
  - Higher input token cost
  answer: Serving a stored answer to a query that is similar but not equivalent
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f7
  prompt: 'Prefix cache TTL is on the order of:'
  options:
  - Seconds
  - Minutes
  - Hours
  - Days
  answer: Minutes
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f8
  prompt: 'In the rank-ordered cost levers, which is #1?'
  options:
  - Model routing
  - Prefix caching
  - Semantic caching
  - Compaction and offloading
  answer: Prefix caching
  explanation: 'The full order is prefix caching → model routing → streaming → semantic cache → compaction/offloading
    → output-length discipline → batch/offline. Lead with #1 because it is lossless and large.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f9
  prompt: Which lever reduces *perceived* rather than actual cost?
  options:
  - Model routing
  - Streaming
  - Batch/offline processing
  - Output-length discipline
  answer: Streaming
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f10
  prompt: 'The course insists cost be reported as:'
  options:
  - Cost per API call
  - Cost per successful task
  - Cost per thousand tokens
  - Cost per user session
  answer: Cost per successful task
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f11
  prompt: Why does that framing matter?
  options:
  - It is easier to compute
  - A cheaper model that fails and retries can cost more per successful task than an expensive one that
    succeeds first time
  - It aligns with provider billing
  - It removes the need to track token counts
  answer: A cheaper model that fails and retries can cost more per successful task than an expensive one
    that succeeds first time
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f12
  prompt: '"Context rot" refers to:'
  options:
  - Stale cache entries returning outdated answers
  - Degrading model performance as the context window fills
  - Corrupted serialization of conversation state
  - Memory entries becoming inconsistent across sessions
  answer: Degrading model performance as the context window fills
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f13
  prompt: In compaction, which content is *never* summarized away first?
  options:
  - Tool outputs
  - Intermediate reasoning
  - Architectural decisions and constraints
  - Earlier user turns
  answer: Architectural decisions and constraints
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f14
  prompt: Which is dropped *first* under compaction pressure?
  options:
  - Architectural decisions
  - Tool outputs
  - The system prompt
  - The current task statement
  answer: Tool outputs
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f15
  prompt: 'Skill/tool descriptions should be sized at roughly:'
  options:
  - ~10 tokens
  - ~45 tokens
  - ~100 tokens
  - As long as needed for clarity
  answer: ~10 tokens
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f16
  prompt: Why does that budget matter at all?
  options:
  - Long descriptions confuse the tokenizer
  - Every description sits in the prefix of every call — it is a fixed tax per request
  - Providers cap tool schema length
  - Shorter descriptions improve tool-selection accuracy monotonically
  answer: Every description sits in the prefix of every call — it is a fixed tax per request
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g1
  prompt: 'The three components of an eval:'
  options:
  - Dataset, metric, threshold
  - Task, trial, grader
  - Input, output, label
  - Baseline, candidate, judge
  answer: Task, trial, grader
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g2
  prompt: 'The grader ladder, cheapest first:'
  options:
  - Human → LLM-judge → code
  - Code → LLM-judge → human
  - LLM-judge → code → human
  - Code → human → LLM-judge
  answer: Code → LLM-judge → human
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g3
  prompt: 'Tier 1 (unit) evals are characterized by:'
  options:
  - Full end-to-end runs against production dependencies
  - No LLM calls, and cheap enough to run on every commit
  - Mocked tools with trajectory assertions
  - Human review of sampled traces
  answer: No LLM calls, and cheap enough to run on every commit
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g4
  prompt: 'Tier 2 evals are:'
  options:
  - Unit-level assertions on parsing and formatting
  - Trajectory evals with mocked tools
  - End-to-end release gates
  - Online A/B tests
  answer: Trajectory evals with mocked tools
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g5
  prompt: 'Tier 3 (end-to-end) evals should run:'
  options:
  - On every commit
  - On release gates only
  - Continuously in production
  - Nightly on a full corpus
  answer: On release gates only
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g6
  prompt: Why does `0.75³ ≈ 42%` appear in the eval notes?
  options:
  - It is the expected pass rate across three eval tiers
  - It shows how per-step reliability compounds across a multi-step agent
  - It is the observed accuracy of LLM judges
  - It is the sampling rate for trace review
  answer: It shows how per-step reliability compounds across a multi-step agent
  explanation: Three steps at 75% each gives 42% end-to-end. This is the arithmetic behind "agents fail
    at the seams" — and the argument for per-step reliability targets rather than a single end-to-end
    number.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g7
  prompt: 'Capability evals vs regression evals:'
  options:
  - Both should sit near 100% before shipping
  - Capability evals may have a low pass rate (that's fine); regression evals should be near 100%
  - Regression evals may fail; capability evals must pass
  - They differ only in how often they run
  answer: Capability evals may have a low pass rate (that's fine); regression evals should be near 100%
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g8
  prompt: 'The graduation rule says:'
  options:
  - Capability evals become regression evals once they pass reliably
  - Regression evals are retired after three green runs
  - Tier 2 evals graduate to Tier 3 at release
  - LLM-judge graders graduate to code graders
  answer: Capability evals become regression evals once they pass reliably
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g9
  prompt: How many examples to start an eval set with?
  options:
  - 5–10 synthetic cases
  - 20–50 real failures
  - 200–500 stratified samples
  - As many as the corpus allows
  answer: 20–50 real failures
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g10
  prompt: Why real failures rather than synthetic cases?
  options:
  - Synthetic data is more expensive to produce
  - Real failures encode the distribution you actually fail on; synthetic cases encode your assumptions
  - Synthetic cases cannot be graded by code
  - Real failures are already labeled
  answer: Real failures encode the distribution you actually fail on; synthetic cases encode your assumptions
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g11
  prompt: 'Between trials you must:'
  options:
  - Reuse the environment to save setup cost
  - Reset the environment so trials are independent
  - Increase temperature to sample diversity
  - Carry forward memory to test continuity
  answer: Reset the environment so trials are independent
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g12
  prompt: 'When the eval and the agent both look broken, the course says:'
  options:
  - Fix the agent first — the eval is a measurement, not a product
  - Fix the eval system before the agent
  - Fix both in the same change
  - Escalate to human review
  answer: Fix the eval system before the agent
  explanation: If you tune the agent against a broken eval you optimize toward noise. Fix the measurement
    first, always.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g13
  prompt: What share of production traces should be scored?
  options:
  - 1–2%
  - 10–20%
  - 50%
  - 100%
  answer: 10–20%
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g14
  prompt: 'After a model or prompt change, the course recommends:'
  options:
  - Rolling back if any metric drops
  - A 48-hour full trace review
  - Doubling the sampling rate for a week
  - Freezing evals until metrics stabilize
  answer: A 48-hour full trace review
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g16
  prompt: 'The course''s split of deployment effort:'
  options:
  - Agent ~80%, management layer ~20%
  - Agent ~40%, management layer ~60%
  - Agent ~60%, management layer ~40%
  - Evenly split
  answer: Agent ~40%, management layer ~60%
  explanation: The number is the point of the section — most of the work is not the agent.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g17
  prompt: 'Langfuse''s differentiator versus LangSmith, as cited:'
  options:
  - Better LLM-judge templates
  - Self-hostable, which matters for GDPR/data-residency constraints
  - Native support for trajectory evals
  - Lower per-trace pricing
  answer: Self-hostable, which matters for GDPR/data-residency constraints
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g18
  prompt: 'Outcome evals and trajectory evals should be:'
  options:
  - Chosen based on whether the task is deterministic
  - Both graded — the answer and the path taken
  - Merged into a single composite score
  - Run in separate tiers, never together
  answer: Both graded — the answer and the path taken
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h1
  prompt: 'Direct vs indirect prompt injection:'
  options:
  - Direct comes from the model's own output; indirect from the user
  - Direct comes from the user's input; indirect arrives via content the agent retrieves or reads
  - Direct targets the system prompt; indirect targets tools
  - Direct is deliberate; indirect is accidental
  answer: Direct comes from the user's input; indirect arrives via content the agent retrieves or reads
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h2
  prompt: 'The course''s framing of the core problem:'
  options:
  - Detection quality — better classifiers close the gap
  - 'Source → sink: "you contain it, you don''t detect it"'
  - Model alignment — a well-aligned model resists injection
  - Input sanitization — escaping untrusted content is sufficient
  answer: 'Source → sink: "you contain it, you don''t detect it"'
  explanation: This is the section's thesis. Injection is not a spam-filtering problem. Trace the untrusted
    *source* to the dangerous *sink* and cut the path — capability restriction, dual-LLM, human approval
    on the sink.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h3
  prompt: Given H2, which answer is explicitly called wrong in an interview?
  options:
  - Any answer proposing capability restriction
  - Detection-only answers
  - Answers naming the dual-LLM pattern
  - Answers that mention human approval gates
  answer: Detection-only answers
  explanation: This is the section's thesis. Injection is not a spam-filtering problem. Trace the untrusted
    *source* to the dangerous *sink* and cut the path — capability restriction, dual-LLM, human approval
    on the sink.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h4
  prompt: 'In the dual-LLM pattern (Willison), the privileged LLM:'
  options:
  - Reads untrusted content and summarizes it for the quarantined LLM
  - Holds the tools and never reads untrusted content
  - Validates the quarantined LLM's outputs before execution
  - Runs with a stricter system prompt but the same inputs
  answer: Holds the tools and never reads untrusted content
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h5
  prompt: 'The quarantined LLM:'
  options:
  - Has read-only tool access
  - Reads untrusted content but cannot act
  - Acts only after human approval
  - Runs a smaller model to limit damage
  answer: Reads untrusted content but cannot act
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h6
  prompt: 'In the 9-step defense stack, input guardrails sit at position:'
  options:
  - 1st
  - 4th
  - 8th
  - 9th
  answer: 1st
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h7
  prompt: 'Output validation sits at:'
  options:
  - 2nd
  - 5th
  - 8th
  - 9th
  answer: 8th
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h8
  prompt: 'Continuous trace grading sits at:'
  options:
  - 1st
  - 3rd
  - 6th
  - 9th
  answer: 9th
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h9
  prompt: 'Memory poisoning vs context poisoning:'
  options:
  - Memory poisoning affects the working context; context poisoning persists across sessions
  - Memory poisoning persists across sessions; context poisoning affects working memory within one
  - Both are within-session; they differ by attack vector
  - Both persist; they differ by which store is targeted
  answer: Memory poisoning persists across sessions; context poisoning affects working memory within one
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h10
  prompt: 'Denial-of-wallet describes:'
  options:
  - Exhausting a rate limit to deny service
  - Driving up an attacker-controlled volume of expensive model calls to inflate cost
  - Stealing API keys to bill a victim
  - Blocking payment flows in an agentic commerce system
  answer: Driving up an attacker-controlled volume of expensive model calls to inflate cost
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h11
  prompt: 'The three boundaries the course says to establish before shipping any agent:'
  options:
  - Model, data, and network
  - Who can trigger it, where it can act, what it did
  - Input, output, and audit
  - Identity, authorization, and encryption
  answer: Who can trigger it, where it can act, what it did
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h12
  prompt: '"What it did" maps to which requirement?'
  options:
  - Rate limiting
  - Audit logging / traceability
  - Least-privilege scopes
  - Authentication
  answer: Audit logging / traceability
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h13
  prompt: 'The degradation ladder, in order:'
  options:
  - Human → retry → fallback model → simpler baseline
  - Retry → fallback model → simpler baseline → human
  - Fallback model → retry → human → simpler baseline
  - Simpler baseline → retry → fallback model → human
  answer: Retry → fallback model → simpler baseline → human
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h14
  prompt: 'Best-of-N jailbreaking (Hughes et al.) reported attack success rates of:'
  options:
  - 45% on GPT-4o, 38% on Claude 3.5 Sonnet
  - 89% on GPT-4o, 78% on Claude 3.5 Sonnet
  - 99% on both
  - 60% on GPT-4o, 20% on Claude 3.5 Sonnet
  answer: 89% on GPT-4o, 78% on Claude 3.5 Sonnet
  explanation: Cite the numbers. 89%/78% is the argument that no prompt-level filter is a boundary; it
    is a speed bump in front of one.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h15
  prompt: What does that result imply for guardrail strategy?
  options:
  - Better prompt-level filters can close the gap
  - Prompt-level defenses are probabilistic — architectural containment must carry the load
  - Only frontier models are safe against BoN
  - Sampling temperature should be set to 0
  answer: Prompt-level defenses are probabilistic — architectural containment must carry the load
  explanation: Cite the numbers. 89%/78% is the argument that no prompt-level filter is a boundary; it
    is a speed bump in front of one.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h16
  prompt: '"Typoglycemia" as an attack refers to:'
  options:
  - Injecting invisible Unicode characters
  - Scrambling word interiors so filters miss the string but the model still reads it
  - Overwhelming the tokenizer with rare tokens
  - Homoglyph substitution in domain names
  answer: Scrambling word interiors so filters miss the string but the model still reads it
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h17
  prompt: 'The three guardrail placements:'
  options:
  - Ingest, index, retrieve
  - Input, output, action
  - Client, gateway, model
  - Pre-flight, in-flight, post-flight
  answer: Input, output, action
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h18
  prompt: 'The PII detection ladder, and its hard case:'
  options:
  - LLM → NER → regex → hybrid; hard case is structured identifiers
  - Regex → NER → LLM → hybrid; hard case is contextual PII
  - Hybrid → regex → NER → LLM; hard case is multilingual text
  - NER → regex → hybrid → LLM; hard case is nested JSON
  answer: Regex → NER → LLM → hybrid; hard case is contextual PII
  explanation: Contextual PII ("the patient in room 4 who came in Tuesday") defeats regex and mostly defeats
    NER. Naming it is the senior signal.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i1
  prompt: 'The course names one word "interviewers listen for" in orchestration. It is:'
  options:
  - Atomicity
  - Idempotency
  - Durability
  - Determinism
  answer: Idempotency
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i2
  prompt: 'Its three named mechanisms:'
  options:
  - Transactions, savepoints, rollbacks
  - Upserts, partition overwrites, dedup keys
  - Locks, leases, fencing tokens
  - Checksums, retries, backoff
  answer: Upserts, partition overwrites, dedup keys
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i3
  prompt: 'The MLOps maturity ladder, in order:'
  options:
  - Notebook → automated pipeline → scripted + tracked → CI/CD-gated → monitored
  - Notebook → scripted + tracked → automated pipeline → CI/CD-gated → monitored/self-healing
  - Scripted → notebook → CI/CD-gated → automated pipeline → monitored
  - Notebook → CI/CD-gated → scripted + tracked → automated → self-healing
  answer: Notebook → scripted + tracked → automated pipeline → CI/CD-gated → monitored/self-healing
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i4
  prompt: 'The rollout ladder:'
  options:
  - Canary → shadow → full
  - Shadow → canary → full
  - Blue/green → canary → full
  - Canary → blue/green → full
  answer: Shadow → canary → full
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i5
  prompt: 'Shadow deployment means:'
  options:
  - A small percentage of live traffic is routed to the new model
  - The new model receives production traffic but its output is not served
  - The new model runs on a replica of yesterday's data
  - Two models serve alternately by request hash
  answer: The new model receives production traffic but its output is not served
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i6
  prompt: 'The training pipeline DAG, in order:'
  options:
  - Featurize → validate corpus → train → register → evaluate
  - Validate corpus → featurize → train → evaluate against baseline → register on pass
  - Validate → train → featurize → evaluate → register
  - Featurize → train → evaluate → validate → register
  answer: Validate corpus → featurize → train → evaluate against baseline → register on pass
  explanation: '"Evaluate against baseline → register *on pass*" is the load-bearing part. A registry
    that accepts unevaluated models is a filing cabinet, not a gate.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i7
  prompt: 'The four monitoring layers:'
  options:
  - Logs, metrics, traces, alerts
  - Service metrics, data drift, concept drift, model quality against delayed labels
  - Latency, throughput, accuracy, cost
  - Ingest, transform, serve, audit
  answer: Service metrics, data drift, concept drift, model quality against delayed labels
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i8
  prompt: 'Alert thresholds should be tied to:'
  options:
  - Historical percentiles only
  - Retrain triggers
  - On-call rotation capacity
  - SLA penalties
  answer: Retrain triggers
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i9
  prompt: 'Debugging "the dashboard number is wrong", the ordered lineage walk is:'
  options:
  - Metric definition → join fan-out → ingest dedup → source freshness
  - Source freshness → ingest dedup → join fan-out → metric definition drift
  - Join fan-out → source freshness → metric definition → ingest dedup
  - Ingest dedup → metric definition → source freshness → join fan-out
  answer: Source freshness → ingest dedup → join fan-out → metric definition drift
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i10
  prompt: 'The principle behind that ordering:'
  options:
  - Check the layer closest to the user first
  - Check the cheapest layer first
  - Check the most recently changed layer first
  - Check in pipeline execution order always
  answer: Check the cheapest layer first
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i11
  prompt: A feature store is justified by which two conditions?
  options:
  - Data volume above 1TB and more than 10 models
  - Online/offline consistency (train/serve skew) and feature reuse across teams
  - Streaming ingestion and sub-second serving
  - Regulatory lineage and PII classification
  answer: Online/offline consistency (train/serve skew) and feature reuse across teams
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i12
  prompt: 'If neither condition holds, the course says:'
  options:
  - Build a lightweight feature store anyway for future-proofing
  - A well-tested mart is enough
  - Use a caching layer instead
  - Compute features inline at request time
  answer: A well-tested mart is enough
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i13
  prompt: 'Batch vs streaming — the course''s default:'
  options:
  - Streaming, since it subsumes batch
  - Batch until a product need forces streaming
  - Lambda architecture from the start
  - Whichever matches the source system
  answer: Batch until a product need forces streaming
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i14
  prompt: LLM-era mappings the course says to state out loud — which is *wrong*?
  options:
  - Embedding pipelines are ETL
  - Prompt/config versioning is model-registry thinking applied to prompts
  - Eval suites in CI/CD are the MLOps monitoring story in new clothes
  - Vector databases replace the data warehouse for analytics
  answer: Vector databases replace the data warehouse for analytics
  explanation: The AIE-with-MLOps-roots advantage is showing that the new stack is the old stack renamed
    — but vector search is retrieval infrastructure, not analytics.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j1
  prompt: 'The time budget for the round:'
  options:
  - 30–40 min, ~10 min/step
  - 45–55 min, ≈8 min/step across 5 steps
  - 60 min, ~15 min/step
  - However long the interviewer allows
  answer: 45–55 min, ≈8 min/step across 5 steps
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j2
  prompt: 'Step 1 is Clarify & scope. The course''s rule:'
  options:
  - Restate the prompt, then design
  - Never design against the raw prompt
  - Ask at most one clarifying question to save time
  - Start with the data model
  answer: Never design against the raw prompt
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j3
  prompt: 'The three clarification targets:'
  options:
  - Users, data, and model choice
  - Requirements, scale, constraints
  - Latency, cost, accuracy
  - Functional, non-functional, operational
  answer: Requirements, scale, constraints
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j4
  prompt: 'The strongest opening question is closest to:'
  options:
  - '"What''s the expected QPS?"'
  - '"Who are the primary users, and what''s the top priority — latency, accuracy, cost, or safety?"'
  - '"Which cloud provider are we on?"'
  - '"Should this use RAG or fine-tuning?"'
  answer: '"Who are the primary users, and what''s the top priority — latency, accuracy, cost, or safety?"'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j5
  prompt: Why write the non-functional requirements down explicitly?
  options:
  - Interviewers score completeness of the requirements list
  - They *are* the trade-off axes for the rest of the round
  - They determine the database choice
  - They are needed for the cost model
  answer: They *are* the trade-off axes for the rest of the round
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j6
  prompt: 'The trade-off narration formula:'
  options:
  - Pick the best option, then defend it against objections
  - Consider 2–3 solutions → narrate pros/cons → ask which priority wins → justify the pick
  - Enumerate all options, then let the interviewer choose
  - State the trade-off, then move on
  answer: Consider 2–3 solutions → narrate pros/cons → ask which priority wins → justify the pick
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j7
  prompt: 'Step 4 asks you to:'
  options:
  - Optimize the design for scale
  - Name your design's weaknesses before the interviewer does
  - Estimate cost
  - Draw the sequence diagram
  answer: Name your design's weaknesses before the interviewer does
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j8
  prompt: 'The interviewer says your trade-off was wrong. The scored behavior is:'
  options:
  - Defend it — consistency signals conviction
  - Adapt visibly; there are no points for stubbornness
  - Ask them to justify their objection first
  - Abandon the whole design and restart
  answer: Adapt visibly; there are no points for stubbornness
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j9
  prompt: 'You hit a genuine knowledge gap mid-round. The course''s tactic:'
  options:
  - Reason from first principles without flagging it
  - Say "my understanding there is superficial", then redirect
  - Ask to skip that component
  - Guess confidently and correct later if challenged
  answer: Say "my understanding there is superficial", then redirect
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j10
  prompt: Which is *not* one of the six trade-off axes?
  options:
  - Latency ↔ accuracy
  - Cost ↔ quality
  - Consistency ↔ availability
  - Recall ↔ precision
  answer: Recall ↔ precision
  explanation: Precision/recall is a *model* trade-off, not a system non-functional. The six axes are
    latency↔accuracy, cost↔quality, consistency↔availability, full-automation↔safety, read↔write throughput,
    storage↔caching.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j11
  prompt: 'In the reference architecture, the API gateway carries:'
  options:
  - Prompt assembly and streaming
  - Authn, rate limits, quotas
  - Query rewriting and reranking
  - Output validation
  answer: Authn, rate limits, quotas
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j12
  prompt: Which is *not* one of the five named sidecars?
  options:
  - Caches (prefix + semantic)
  - State store (session/checkpointer)
  - Feature store
  - HITL queue
  answer: Feature store
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j13
  prompt: 'From the bottleneck table, "model cold start" is mitigated by:'
  options:
  - Backoff retries and multi-provider routing
  - Warm pools and pre-warming
  - Sharded queues and priority tiers
  - Pruning and periodic index rebuild
  answer: Warm pools and pre-warming
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j14
  prompt: 'The course says "never stop at the design." Closing well means:'
  options:
  - Summarizing the components you drew
  - Stating success metrics with numbers — e.g. p95 under 2s while holding faithfulness above 0.9
  - Listing the technologies you would use
  - Asking what the interviewer would have done differently
  answer: Stating success metrics with numbers — e.g. p95 under 2s while holding faithfulness above 0.9
  explanation: Numbers close the round. "p95 < 2s, faithfulness > 0.9" plus a future-improvements list
    separates a design from a drawing.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j15
  prompt: Which pattern exists specifically to prevent *cascading* failures in a distributed system?
  options:
  - Retry pattern
  - Circuit breaker pattern
  - Timeout pattern
  - Exception handling
  answer: Circuit breaker pattern
  explanation: 'All four distractors are real practices — the question is which one targets *cascading*
    failure. A circuit breaker tracks the failure rate of a dependency and, once it crosses a threshold,
    **opens**: calls fail fast without touching the sick service. After a cooldown it goes **half-open**,
    admits a few probes, and either closes (recovered) or re-opens. That containment is the point. Timeouts
    (C) bound a *single* call and are necessary but insufficient — with a dead dependency and a 30s timeout,
    in-flight requests still pile up until threads, connections, or queue depth are exhausted, and the
    caller dies too. Retries (A) make cascades *worse* by multiplying load on an already-failing service
    unless paired with a breaker and jittered backoff. Exception handling (D) is local error propagation,
    not a load-shedding mechanism. In the LLM stack this is the pattern behind provider fallback (**J13**,
    **H-tier degradation ladders**): trip the breaker on the primary model endpoint, route to the fallback,
    probe for recovery.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: k1
  prompt: 'The framing habit — every design answer opens with:'
  options:
  - Architecture → data → model → deployment
  - User → problem → success metric → constraint
  - Requirements → scale → constraints → design
  - Cost → value → risk → timeline
  answer: User → problem → success metric → constraint
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: k2
  prompt: Which is the better-framed problem statement?
  options:
  - '"Build a RAG chatbot for support"'
  - '"Reduce support cost 20% while holding CSAT"'
  - '"Deploy an LLM over the knowledge base"'
  - '"Improve first-response time using AI"'
  answer: '"Reduce support cost 20% while holding CSAT"'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: k3
  prompt: 'The napkin token-cost formula:'
  options:
  - queries/day × latency × $/hour
  - tokens/query × $/M tokens × queries/day
  - model size × requests × utilization
  - context length × users × sessions
  answer: tokens/query × $/M tokens × queries/day
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: k4
  prompt: '"Mistral 7B gives 90% of the accuracy — why still pick it over GPT-4?" The intended answer:'
  options:
  - Open weights avoid vendor lock-in
  - The last 10% costs 20× and the use case's error tolerance doesn't need it
  - Smaller models are easier to fine-tune
  - Latency is lower
  answer: The last 10% costs 20× and the use case's error tolerance doesn't need it
  explanation: '"ROI, not model maximalism" — but the reversal is what shows judgment rather than a memorized
    slogan.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: k5
  prompt: When should you reverse that answer?
  options:
  - When traffic volume is high
  - When errors are expensive
  - When the model is self-hosted
  - When the corpus is multilingual
  answer: When errors are expensive
  explanation: '"ROI, not model maximalism" — but the reversal is what shows judgment rather than a memorized
    slogan.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: k6
  prompt: Where does AI belong first, and last?
  options:
  - First in high-stakes decisions, last in drafting
  - First in high-volume, tolerant-of-review workflows; last in irreversible/high-stakes actions
  - First wherever data is cleanest; last where data is sparse
  - First in customer-facing flows; last in internal tooling
  answer: First in high-volume, tolerant-of-review workflows; last in irreversible/high-stakes actions
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: k7
  prompt: 'The metrics tree:'
  options:
  - Input → output → outcome
  - North star → driver metrics → guardrail metrics
  - Leading → lagging → composite
  - Adoption → retention → revenue
  answer: North star → driver metrics → guardrail metrics
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: k8
  prompt: Which of these is a *guardrail* metric for an agent, not a driver metric?
  options:
  - Goal completion rate
  - No-touch rate
  - Hallucination rate
  - Time-to-trust
  answer: Hallucination rate
  explanation: 'Drivers are goal completion, no-touch rate, escalation rate, time-to-trust. Guardrails
    are hallucination rate, complaint rate, cost/interaction. The distinction matters: you optimize drivers
    and *veto* on guardrails.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: k9
  prompt: 'Failure UX on low confidence — the triad:'
  options:
  - Retry, escalate, log
  - Abstain, cite, escalate
  - Degrade, notify, queue
  - Warn, proceed, review
  answer: Abstain, cite, escalate
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: k10
  prompt: 'The prioritization formula:'
  options:
  - (impact + confidence) − effort
  - impact × confidence ÷ effort, with guardrail metrics as veto
  - reach × impact × confidence ÷ effort
  - value ÷ (cost × risk)
  answer: impact × confidence ÷ effort, with guardrail metrics as veto
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: k11
  prompt: '"The model is 92% accurate — ship it?" The structured answer requires:'
  options:
  - Comparing against the human baseline only
  - 8% errors × volume × cost-per-error, plus the error *distribution* (harmless vs catastrophic), plus
    mitigation UX — then yes/no with conditions
  - Re-running evals on a larger test set before deciding
  - Shipping behind a feature flag and measuring
  answer: 8% errors × volume × cost-per-error, plus the error *distribution* (harmless vs catastrophic),
    plus mitigation UX — then yes/no with conditions
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: k12
  prompt: Nonprofit/mission-driven constraints the course names — which is *not* one?
  options:
  - Grant-cycle budgets make opex unpredictable, so API bills need caps
  - Volunteer/rotating maintainers favor boring tech and managed services
  - Success ≠ revenue; funders need reportable impact numbers from day one
  - Compliance burden is lower, so PII handling can be lighter-weight
  answer: Compliance burden is lower, so PII handling can be lighter-weight
  explanation: The opposite is true — beneficiary PII (immigration status, health, benefits) is higher-stakes,
    and consent/minimization is about trust with vulnerable populations, not a compliance checkbox.
  lesson: interviewing/rounds/technical-questions/mcq-bank
---

Seeded once from `technical-questions/mcq-bank.md`; edit this file directly. Studied at `#/quiz/interviewing/rounds`.
