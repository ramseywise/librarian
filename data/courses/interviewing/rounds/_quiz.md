---
title: 'Technical interview questions: multiple choice'
summary: Multiple-choice questions from the technical-questions MCQ bank that span several subjects or test the interview itself; the rest sit in the module they test.
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
  explanation: CPython's global interpreter lock (GIL) lets one thread run Python bytecode at a time, so CPU-bound
    threads take turns instead of using the eight cores. Nothing is deadlocked, and more threads would only add
    switching.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a2
  prompt: A Python service runs four threads doing pure CPU-bound numeric work on an 8-core machine, and throughput
    is no better than single-threaded. Which change gives *true parallelism* for that workload?
  options:
  - Switch to `asyncio`
  - Increase the thread count to 8
  - Switch to `multiprocessing`
  - Release the GIL with a `threading.Lock`
  answer: Switch to `multiprocessing`
  explanation: Each process has its own interpreter and its own GIL, so the work runs on several cores at once.
    `asyncio` and extra threads still execute one stream of bytecode at a time, and a `threading.Lock` has nothing
    to do with the GIL.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a3
  prompt: What does async programming provide in Python?
  options:
  - Parallel execution across CPU cores
  - Concurrency, not parallel execution
  - Automatic GIL release for CPU work
  - Thread-safe access to shared mutable state
  answer: Concurrency, not parallel execution
  explanation: One thread switches between tasks while they wait on I/O, so many tasks make progress but only one
    runs at any instant. It does nothing for CPU work, and shared state can still change between two `await`s.
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
  explanation: The result depends on the order in which threads interleave their reads and writes of the same data.
    Immutable data cannot race, and starvation is a scheduling problem, not a data one.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a6
  prompt: Which is *not* one of the three standard fixes for a race condition?
  options:
  - Locks/mutexes (`threading.Lock`)
  - Immutable data structures
  - Avoiding shared mutable state
  - Increasing the thread pool size
  answer: Increasing the thread pool size
  explanation: A race needs shared mutable state and unsynchronised access. A lock, immutable data and not sharing
    each remove one of those; more threads only add more interleavings.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a7
  prompt: You need `popleft()` in a BFS inner loop. Why `collections.deque` over a list?
  options:
  - '`deque` uses less memory per element'
  - '`deque` popleft is O(1); list popleft is O(n)'
  - '`deque` is thread-safe and lists are not'
  - Lists cannot pop from the front
  answer: '`deque` popleft is O(1); list popleft is O(n)'
  explanation: A deque removes from the left in constant time. `list.pop(0)` shifts every remaining element, which
    is O(n) per pop and turns a BFS quadratic. Lists can pop from the front; it is the cost that rules them out.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a8
  prompt: 'Sorting an array first, then applying two pointers, typically changes brute force from:'
  options:
  - O(n log n) → O(n)
  - O(n²) → O(n log n)
  - O(n³) → O(n²)
  - O(2ⁿ) → O(n²)
  answer: O(n²) → O(n log n)
  explanation: Brute force checks every pair, O(n²). After an O(n log n) sort the two pointers cross the array once
    in O(n), so the sort dominates the total.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a9
  prompt: Which traversal of a binary search tree yields values in sorted order?
  options:
  - Preorder (root → left → right)
  - Inorder (left → root → right)
  - Postorder (left → right → root)
  - Level-order (BFS)
  answer: Inorder (left → root → right)
  explanation: In a binary search tree everything in the left subtree is smaller than the node and everything in
    the right is larger, so visiting left, node, right emits the values in ascending order.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a10
  prompt: How do you correctly validate a BST?
  options:
  - Check each node is greater than its immediate parent
  - Check each node's left child < node < right child, locally
  - Pass min/max bounds down the recursion
  - Inorder traverse and check the root is the median
  answer: Pass min/max bounds down the recursion
  explanation: The local child check wrongly accepts a node deeper in the left subtree that exceeds the root. Bounds
    must be threaded down.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a11
  prompt: After Floyd's fast/slow pointers meet inside a cycle, how do you find the cycle's start?
  options:
  - Continue advancing the fast pointer at speed 2
  - Reset one pointer to head, then advance both at speed 1
  - Reset both pointers to head and advance at speeds 1 and 2 again
  - Count the cycle length, then advance that many steps from head
  answer: Reset one pointer to head, then advance both at speed 1
  explanation: The distance from the head to the cycle's start equals the distance from the meeting point to the
    start, modulo the cycle length. Two pointers leaving the head and the meeting point at one step each therefore
    meet at the start.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a12
  prompt: 'Union-Find with path compression and union by rank costs, per operation:'
  options:
  - O(log n)
  - O(α(n))
  - O(1) worst case
  - O(n) amortized
  answer: O(α(n))
  explanation: With both optimisations the amortised cost is the inverse Ackermann function, which stays below 5
    for any input you could store. That is effectively constant but not O(1) in the worst case; either optimisation
    alone gives O(log n).
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a13
  prompt: Which pair of conditions signals a dynamic-programming problem?
  options:
  - Sorted input + a monotonic predicate
  - Optimal substructure + overlapping subproblems
  - A recursive definition + a base case
  - Greedy choice property + matroid structure
  answer: Optimal substructure + overlapping subproblems
  explanation: Optimal substructure lets you build the answer from answers to subproblems, and overlapping subproblems
    are what make storing them pay. Sorted input with a monotonic predicate signals binary search, and the greedy-choice
    property signals a greedy algorithm.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a14
  prompt: 'Top-down memoization vs bottom-up tabulation:'
  options:
  - Top-down is better for large inputs; bottom-up is easier to reason about
  - Top-down is easier to reason about; bottom-up is better for large inputs and space optimization
  - They have identical time and space profiles
  - Bottom-up always uses less time; top-down always uses less space
  answer: Top-down is easier to reason about; bottom-up is better for large inputs and space optimization
  explanation: Top-down follows the recurrence as written and computes only the states it needs, but deep recursion
    and call overhead hurt on large inputs. Bottom-up has no recursion and lets you keep only the last row or two
    of the table.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a15
  prompt: '`WHERE` and `HAVING` differ how?'
  options:
  - '`WHERE` filters groups after aggregation; `HAVING` filters rows before'
  - '`WHERE` filters rows before grouping; `HAVING` filters groups after aggregating'
  - They are interchangeable in a `GROUP BY` query
  - '`HAVING` works only with `COUNT`'
  answer: '`WHERE` filters rows before grouping; `HAVING` filters groups after aggregating'
  explanation: '`WHERE` runs before `GROUP BY`, so it sees rows and cannot use an aggregate. `HAVING` runs after,
    so it sees groups and can filter on any aggregate, not only `COUNT`.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a16
  prompt: '`ROW_NUMBER`, `RANK`, `DENSE_RANK` on tied values:'
  options:
  - All three assign the same rank to ties
  - '`ROW_NUMBER` no ties; `RANK` ties then skips; `DENSE_RANK` ties then does not skip'
  - '`ROW_NUMBER` ties then skips; `RANK` no ties; `DENSE_RANK` ties without skipping'
  - '`RANK` and `DENSE_RANK` are aliases; only `ROW_NUMBER` differs'
  answer: '`ROW_NUMBER` no ties; `RANK` ties then skips; `DENSE_RANK` ties then does not skip'
  explanation: 'For the values 10, 10, 20: `ROW_NUMBER` gives 1, 2, 3; `RANK` gives 1, 1, 3; `DENSE_RANK` gives
    1, 1, 2.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a17
  prompt: 'The canonical "keep the latest row per user" idiom is:'
  options:
  - '`SELECT DISTINCT ON (user_id) ... ORDER BY created_at`'
  - '`GROUP BY user_id HAVING created_at = MAX(created_at)`'
  - '`ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC)` then `WHERE rn = 1`'
  - '`SELECT user_id, MAX(created_at)` joined back on both columns'
  answer: '`ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC)` then `WHERE rn = 1`'
  explanation: It numbers each user's rows newest first and keeps the whole row. `DISTINCT ON` is PostgreSQL only,
    the `HAVING` form is invalid because `created_at` is not grouped, and joining back on `MAX(created_at)` returns
    two rows when timestamps tie.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a18
  prompt: A `LEFT JOIN` returns more rows than the left table has. What happened?
  options:
  - The join key is null in some left rows
  - The right table has duplicate join keys — fan-out
  - '`LEFT JOIN` always returns at least as many rows as the right table'
  - The query needs `SELECT DISTINCT`
  answer: The right table has duplicate join keys — fan-out
  explanation: The row count stays at the left table's when each left row matches at most one right row. Ask "how
    many rows does this join produce?" before running it.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: a19
  prompt: 'State the effect of Python''s global interpreter lock (GIL) directly: what does it constrain?'
  options:
  - It prevents a process from spawning child processes
  - It allows threads to execute Python bytecode in true parallel
  - It limits execution of Python bytecode to one thread at a time
  - It improves CPU-bound performance by pinning threads to cores
  answer: It limits execution of Python bytecode to one thread at a time
  explanation: 'The GIL constrains *bytecode execution*, not the interpreter as a whole, which is why threads still
    help for I/O: a blocking socket or file read releases the GIL while it waits, so other threads run. CPU work
    never yields it, so CPU-bound threads run one at a time and `multiprocessing` is the fix.'
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
  explanation: Leakage is information in training that will not exist at prediction time. It makes every offline
    score better, so nothing looks wrong until the model fails in production, which is why it does more damage than
    the other three.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b2
  prompt: Which practice does *not* prevent leakage?
  options:
  - Fitting scalers and encoders on the training split only
  - Splitting before any target-aware transform
  - Using time-based splits for temporal data
  - Averaging cross-validation scores across more folds
  answer: Averaging cross-validation scores across more folds
  explanation: More folds only steady the estimate. If the leak is in the features or the preprocessing, every fold
    is leaked the same way. The other three each keep test information out of training.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b3
  prompt: Under heavy class imbalance, which is more informative?
  options:
  - ROC-AUC, because it is threshold-independent
  - PR-AUC, because it focuses on the positive class
  - Accuracy, with a tuned threshold
  - R², because it handles skew
  answer: PR-AUC, because it focuses on the positive class
  explanation: Precision and recall ignore true negatives, so PR-AUC shows how well the rare class is found. ROC-AUC
    divides false positives by the huge number of negatives and keeps looking good, and accuracy rewards predicting
    the majority class.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b4
  prompt: 'The interview move the course says to make first when discussing any model result:'
  options:
  - Report the cross-validated standard deviation
  - Name the naive baseline (majority class / mean predictor)
  - State the model family and its hyperparameters
  - Show the confusion matrix
  answer: Name the naive baseline (majority class / mean predictor)
  explanation: 'A score means nothing until you know what a trivial predictor gets: 95% accuracy is no achievement
    when 95% of the rows are one class.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b5
  prompt: 'L1 vs L2 regularization:'
  options:
  - L1 shrinkage, L2 sparsity
  - L1 sparsity (feature selection), L2 shrinkage
  - Both produce sparsity; L2 is just faster
  - L1 applies to trees, L2 to linear models
  answer: L1 sparsity (feature selection), L2 shrinkage
  explanation: The L1 penalty has a corner at zero, so it pushes some weights exactly to zero and removes those
    features. L2 penalises squared weights, which shrinks all of them smoothly and almost never to zero.
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
  - 'PCA is linear variance; UMAP is neighborhood structure, and is "for looking, not for downstream features without care"'
  - Both are linear; UMAP is just faster
  - UMAP is deterministic; PCA is stochastic
  answer: 'PCA is linear variance; UMAP is neighborhood structure, and is "for looking, not for downstream features without care"'
  explanation: PCA finds the linear directions of greatest variance and can transform new data. UMAP keeps near
    neighbours near, but the sizes of clusters and the distances between them in its plot are not reliable, so its
    output needs care before it is used as model features.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b8
  prompt: 'Covariate drift vs concept drift:'
  options:
  - Covariate = the input distribution shifts; concept = the input→target relationship shifts
  - Covariate = the target relationship shifts; concept = the inputs shift
  - Both describe label noise increasing over time
  - Covariate applies to classification, concept to regression
  answer: Covariate = the input distribution shifts; concept = the input→target relationship shifts
  explanation: In covariate drift the inputs change while the rule from input to target holds, for example a new
    mix of customers. In concept drift the rule itself changes, so the same input now means a different outcome.
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
  explanation: RMSE squares each error before averaging, so one large miss counts far more than several small ones.
    MAE counts each error in proportion to its size.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b11
  prompt: 'MAPE''s specific pitfall:'
  options:
  - It is undefined for negative predictions
  - It blows up near zero actuals
  - It cannot be averaged across series
  - It requires normally distributed residuals
  answer: It blows up near zero actuals
  explanation: MAPE divides each error by the actual value, so an actual near zero gives an enormous or infinite
    percentage. Negative predictions are no problem, and no distribution of residuals is assumed.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b12
  prompt: 'Calibration means:'
  options:
  - The model's ranking is correct
  - The predicted probabilities mean what they say
  - The decision threshold is tuned to maximize F1
  - Features are standardized before training
  answer: The predicted probabilities mean what they say
  explanation: Of the cases given a probability of 0.8, about 80% should turn out positive. A model can rank cases
    perfectly and still be miscalibrated, so a ranking metric does not show it.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b13
  prompt: Which tools assess calibration?
  options:
  - Silhouette score and elbow plots
  - Brier score and reliability curves
  - SHAP values and permutation importance
  - Precision@K and MRR
  answer: Brier score and reliability curves
  explanation: The Brier score is the mean squared error of the predicted probabilities, and a reliability curve
    plots predicted probability against observed frequency. The other pairs measure clustering, feature attribution
    and ranking.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b14
  prompt: '"Hidden Technical Debt in Machine Learning Systems" (NIPS 2015) names which failure modes?'
  options:
  - Overfitting, underfitting, and leakage
  - Entanglement, feedback loops, pipeline jungles
  - Drift, staleness, and skew
  - Bias, variance, and irreducible error
  answer: Entanglement, feedback loops, pipeline jungles
  explanation: 'Sculley et al. describe debt that is specific to ML systems: entanglement (changing anything changes
    everything), hidden feedback loops where a model shapes its own future training data, and pipeline jungles of
    data-preparation glue. The other options are modelling problems, not system debt.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b15
  prompt: 'From Ng''s "Structuring ML Projects", human-level performance is used as:'
  options:
  - A hard ceiling the model must not exceed
  - A proxy for Bayes error
  - The threshold for shipping
  - The baseline for the naive predictor
  answer: A proxy for Bayes error
  explanation: Bayes error is the lowest error any predictor could reach and cannot be measured directly. On tasks
    people do well, human error is close to it, so the gap between human and training error shows how much bias
    is avoidable. A model can beat human level, so it is not a ceiling.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: b16
  prompt: Choosing K in k-means, the honest senior answer adds what to elbow/silhouette?
  options:
  - The Bayesian information criterion
  - That K encodes a product decision — how many segments can ops actually act on
  - That K should equal the number of features
  - That K should be tuned against downstream AUC only
  answer: That K encodes a product decision — how many segments can ops actually act on
  explanation: Elbow and silhouette say how well separated the clusters are, not whether anyone can use them. If
    the operations team can run four campaigns, seven segments are no use to them.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c1
  prompt: 'Scaled dot-product attention is:'
  options:
  - '`softmax(QKᵀ/d)V`'
  - '`softmax(QKᵀ/√d)V`'
  - '`softmax(QᵀK/√d)V`'
  - '`softmax(QKᵀ)V/√d`'
  answer: '`softmax(QKᵀ/√d)V`'
  explanation: Each query is compared with each key by dot product, the scores are divided by √d (the key dimension)
    and passed through softmax, and the weights average the values. The scaling goes inside the softmax and uses
    √d, not d.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c2
  prompt: Why divide by √d?
  options:
  - To normalize the output to unit length
  - To prevent softmax saturating in high dimensions
  - To make the operation numerically invertible
  - To match the residual stream scale
  answer: To prevent softmax saturating in high dimensions
  explanation: Dot products of d-dimensional vectors spread out more as d grows. Large scores push softmax towards
    putting all the weight on one token, where gradients vanish; dividing by √d keeps the spread roughly constant.
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
  explanation: With n tokens there are about n² comparisons, so doubling the context roughly quadruples the attention
    work. Hallucination, tokenisation and forgetting have other causes.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c4
  prompt: Which is *not* a named way to inject positional information?
  options:
  - Learned positional embeddings
  - RoPE
  - ALiBi
  - Layer normalization
  answer: Layer normalization
  explanation: Layer normalisation rescales activations and knows nothing about order. Learned embeddings add a
    vector per position, RoPE rotates queries and keys by position, and ALiBi subtracts a distance penalty from
    attention scores.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c5
  prompt: 'A decoder-only model (GPT family) is characterized by:'
  options:
  - Bidirectional attention over the full sequence
  - A causal mask
  - Cross-attention to an encoder stack
  - Masked-token prediction as its objective
  answer: A causal mask
  explanation: The causal mask stops each token attending to later ones, which is what lets the model be trained
    on next-token prediction and generate left to right. Bidirectional attention and masked-token prediction describe
    encoders such as BERT, and cross-attention describes encoder–decoder models.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c6
  prompt: 'The KV cache is described as the mechanism underneath:'
  options:
  - Speculative decoding
  - Prompt caching
  - Quantization
  - Mixture-of-experts routing
  answer: Prompt caching
  explanation: The KV cache stores each layer's keys and values for tokens already processed, so they are not recomputed
    for the next token. Prompt caching keeps that stored state for a shared prefix from one request to the next.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c7
  prompt: 'Even at temperature 0, production output isn''t fully deterministic. Named causes:'
  options:
  - Tokenizer drift, prompt truncation, retry logic
  - Batching, floating point, hardware and version differences
  - Sampling seeds, top-p, top-k
  - Load balancing, caching, streaming
  answer: Batching, floating point, hardware and version differences
  explanation: 'Temperature 0 removes sampling, but the arithmetic still varies: floating-point sums come out slightly
    differently depending on batch, hardware and library version, and a tiny difference can flip the choice between
    two near-tied tokens. Seeds, top-p and top-k do not apply at temperature 0.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c8
  prompt: 'Prefill vs decode:'
  options:
  - Prefill is sequential and expensive per token; decode is parallel and cheap
  - Prefill is parallel and cheap per token; decode is sequential and expensive
  - Both are parallel; decode is just longer
  - Prefill dominates cost in long-output workloads
  answer: Prefill is parallel and cheap per token; decode is sequential and expensive
  explanation: Prefill reads the whole prompt in one parallel pass. Decode produces one token per pass, and each
    pass waits for the one before, which is why output tokens cost more and set most of the latency.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c9
  prompt: In LLM inference, prefill processes the whole prompt in parallel and is cheap per token, while decode
    emits one token at a time and is expensive. Which discipline follows directly?
  options:
  - Larger batch sizes
  - Output-length discipline and streaming
  - Higher temperature for diversity
  - Longer system prompts to amortize setup
  answer: Output-length discipline and streaming
  explanation: Each output token is another sequential step, so latency grows with output length. Keep outputs short,
    and stream them so the reader sees the first token early.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c10
  prompt: 'Speculative decoding is primarily:'
  options:
  - A memory-reduction technique
  - A latency technique
  - A quality-improvement technique
  - A training-efficiency technique
  answer: A latency technique
  explanation: A small draft model proposes several tokens and the large model checks them in one parallel pass,
    keeping those it agrees with. The output is what the large model would have produced, only sooner, and it uses
    more memory, not less.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c11
  prompt: 'RLHF''s characteristic failure mode:'
  options:
  - Catastrophic forgetting
  - Reward hacking
  - Mode collapse to the base model
  - Gradient explosion
  answer: Reward hacking
  explanation: The policy is optimised against a learned reward model, so it learns whatever that model scores highly,
    which is not always what people wanted, for example answers that sound agreeable or confident.
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
  prompt: DPO skips the reward model and optimises preference pairs directly, where RLHF trains a reward model and
    runs an RL loop. What is DPO's stated trade-off?
  options:
  - Trades stability for controllability
  - Trades some controllability for stability
  - Trades cost for alignment quality
  - Trades data efficiency for compute
  answer: Trades some controllability for stability
  explanation: DPO drops the reward model and the RL loop and trains on the preference pairs directly, so training
    is steadier. What it gives up is the separate reward model, and with it some direct control over what is rewarded.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c14
  prompt: 'Constitutional AI / RLAIF replaces human labels with:'
  options:
  - Synthetic preference pairs sampled at random
  - AI feedback guided by principles, via a critique-and-revise loop
  - A larger reward model
  - Rule-based filters at inference time
  answer: AI feedback guided by principles, via a critique-and-revise loop
  explanation: The model critiques and revises its own responses against a written set of principles, and preferences
    produced by a model replace those of human raters in training. This happens during training, not as a filter
    at inference time.
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
  explanation: QLoRA loads the frozen base model in 4-bit precision and trains ordinary full-precision LoRA adapters
    on top, so a large model fits on one GPU. The adapters are not what is quantised.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c17
  prompt: LoRA trains roughly what share of parameters?
  options:
  - ~0.001–0.01%
  - ~0.1–1%
  - ~5–10%
  - ~25%
  answer: ~0.1–1%
  explanation: LoRA freezes the base weights and trains two small low-rank matrices for each adapted layer. At typical
    ranks that comes to between a tenth of a percent and about one percent of the parameters.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c18
  prompt: 'For an API-only model where you cannot touch weights, preference data goes into:'
  options:
  - A local reward model
  - Prompts and evals
  - A fine-tuning endpoint
  - The KV cache
  answer: Prompts and evals
  explanation: Without access to the weights you cannot train on the preferences. The preferred answers become instructions
    and few-shot examples in the prompt, and test cases in the evals that check the behaviour holds.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c19
  prompt: '"Lost in the middle" describes:'
  options:
  - Truncation of the middle of a long prompt by the tokenizer
  - Models using information at the start and end of a long context better than the middle
  - Retrieval returning mid-ranked documents
  - Positional embeddings failing past their trained length
  answer: Models using information at the start and end of a long context better than the middle
  explanation: Liu et al. (2023) found accuracy highest when the relevant passage sat at the start or the end of
    a long context and lowest when it sat in the middle. It concerns how the model uses its context, not truncation
    or retrieval.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: c20
  prompt: 'The course''s stated mitigation for long-context degradation:'
  options:
  - Bigger context windows
  - Context engineering, not bigger windows
  - Lower temperature
  - More attention heads
  answer: Context engineering, not bigger windows
  explanation: A bigger window only gives more middle to lose things in. The fix is to put less, more relevant material
    in the context and to place what matters at the start or the end.
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
  explanation: CoT buys reasoning quality by spending intermediate tokens — so it *raises* token usage and latency,
    which is why the token-usage and speed options are inverted traps. It reduces reasoning errors; it does not
    eliminate hallucination, since a fluent wrong chain is still wrong. It is a prompting-tier move, tried before
    RAG or fine-tuning.
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
  explanation: 'From Anthropic''s "Building effective agents": in a workflow your code decides the steps, and in
    an agent the model does. The number of calls and whether state is kept are not the distinction.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e2
  prompt: 'The course says the interview answer that "is always open here" is:'
  options:
  - '"Use an agent — it generalizes better"'
  - Naming the workflow/agent distinction and defending the cheaper option
  - '"It depends on the model"'
  - Choosing whichever the interviewer's company ships
  answer: Naming the workflow/agent distinction and defending the cheaper option
  explanation: A task whose steps are known is cheaper, faster and easier to debug as a workflow. An agent earns
    its cost only when the steps cannot be known in advance.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e3
  prompt: Which is *not* one of the five workflow patterns?
  options:
  - Prompt chaining
  - Routing
  - Retrieval augmentation
  - Evaluator–optimizer
  answer: Retrieval augmentation
  explanation: The five are prompt chaining, routing, parallelization, orchestrator–workers and evaluator–optimizer.
    Retrieval is something you add to the model as a building block, not a workflow pattern.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e4
  prompt: Parallelization splits into which two variations?
  options:
  - Sharding and replication
  - Sectioning and voting
  - Fan-out and fan-in
  - Map and reduce
  answer: Sectioning and voting
  explanation: Sectioning splits a task into independent parts that run at the same time. Voting runs the same task
    several times and combines the results.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e5
  prompt: 'Orchestrator–workers differs from sectioning because:'
  options:
  - It runs workers sequentially
  - Subtasks are determined dynamically by the orchestrator, not fixed in advance
  - Workers share a single context window
  - It requires a human in the loop
  answer: Subtasks are determined dynamically by the orchestrator, not fixed in advance
  explanation: In sectioning you write the split into the code. An orchestrator reads the task and decides the subtasks
    at run time, for example which files a code change has to touch.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e6
  prompt: '"Agent = Model + Harness" — the harness contributes:'
  options:
  - The system prompt and tool definitions
  - Acceptance baseline, execution boundary, feedback signals, rollback mechanism
  - Retry logic, caching, logging, and metrics
  - Memory, planning, tools, and reflection
  answer: Acceptance baseline, execution boundary, feedback signals, rollback mechanism
  explanation: 'The harness is what makes the model''s work checkable and safe: what counts as done, what it may
    touch, the signals that tell it whether it is right, and a way to undo. The other lists are features of a framework
    or abilities of an agent.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e7
  prompt: 'ACI (agent–computer interface) design borrows "poka-yoke" to mean:'
  options:
  - Fail fast on invalid input
  - Design the tool so the mistake is impossible to make
  - Log every tool call for later review
  - Require confirmation before destructive actions
  answer: Design the tool so the mistake is impossible to make
  explanation: 'Poka-yoke is the manufacturing term for mistake-proofing: shape the part so it only fits the right
    way round. For a tool that means changing the arguments so the error cannot be expressed, not catching it afterwards.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e8
  prompt: 'The course''s concrete poka-yoke example:'
  options:
  - Enum-typed arguments instead of free-form strings
  - Requiring absolute paths so relative-path errors cannot occur
  - A dry-run flag on every write tool
  - Rate limiting per tool
  answer: Requiring absolute paths so relative-path errors cannot occur
  explanation: 'From Anthropic''s "Building effective agents": the model made mistakes with relative paths once
    it had moved out of the root directory, so the tool was changed to require absolute paths and the mistakes stopped.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e9
  prompt: Task length is a design threshold. By the rule of thumb in the context-engineering note on compression and
    compaction, beyond roughly what duration does crash recovery become mandatory?
  options:
  - ~5 minutes
  - ~30 minutes
  - ~2 hours
  - ~1 day
  answer: ~30 minutes
  explanation: The longer a run, the more work a crash throws away and the more likely one is. Half an hour is the
    course's rule of thumb for where checkpoint-and-resume stops being optional.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e10
  prompt: 'The four memory types:'
  options:
  - Short-term, long-term, cache, archive
  - Working, episodic, semantic, procedural
  - Scratchpad, vector, graph, relational
  - Session, user, org, global
  answer: Working, episodic, semantic, procedural
  explanation: Working memory is the current context, episodic is what happened in earlier sessions, semantic is
    facts, and procedural is how to do things, such as skills and instructions.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e11
  prompt: 'For agent memory, the course''s stated bias:'
  options:
  - Recall over precision — better to surface too much than miss something
  - Precision over recall — a wrong memory is worse than a missing one
  - Recency over relevance
  - Completeness over compactness
  answer: Precision over recall — a wrong memory is worse than a missing one
  explanation: A missing memory makes the agent ask or look again. A wrong one is acted on with confidence and is
    hard to trace, so store less and check it.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e12
  prompt: 'Subagents'' primary architectural value:'
  options:
  - Parallel speedup
  - Acting as a context firewall — the parent sees only the summary
  - Model diversity
  - Cost reduction through smaller models
  answer: Acting as a context firewall — the parent sees only the summary
  explanation: A subagent's searching and tool output stay in its own context, and the parent receives only the
    result, which keeps the parent's window small. Speed and cost are side benefits.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e13
  prompt: 'MCP vs A2A:'
  options:
  - MCP is agent↔agent; A2A is model↔tool
  - MCP is model↔tool; A2A is agent↔agent
  - Both are model↔tool; A2A adds authentication
  - Both are agent↔agent; MCP adds a schema layer
  answer: MCP is model↔tool; A2A is agent↔agent
  explanation: MCP standardises how a model reaches tools and data. A2A standardises how separate agents find each
    other and hand over work.
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
  explanation: At a 70% success rate per trial and k = 3, pass@k is 1 − 0.3³ ≈ 97% and pass^k is 0.7³ ≈ 34%. The
    same agent looks nearly perfect on one and unreliable on the other.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e15
  prompt: Which does a *production* SLA actually depend on?
  options:
  - pass@k
  - pass^k
  - mean reward per episode
  - Single-shot accuracy
  answer: pass^k
  explanation: Users need it to work every time, not at least once in k tries. pass^k falls as k grows and shows
    the unreliability that pass@k hides.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e16
  prompt: 'PRINCE (Bayer with Thoughtworks; Kulkarni, martinfowler.com, 2026) is cited as evidence for:'
  options:
  - Multi-agent reinforcement learning in production
  - A real-world agent architecture pattern — Search → Ask → Do
  - Graph-based memory outperforming vector memory
  - Fine-tuning beating prompting for tool use
  answer: A real-world agent architecture pattern — Search → Ask → Do
  explanation: 'It is cited as a production agent system, not as a research result: the system first searches, then
    answers questions over what it found, then acts. It is not evidence about reinforcement learning, memory stores
    or fine-tuning.'
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
  explanation: A second call can only improve a draft if it can say what is wrong with it, which takes clear criteria.
    The other options describe parallelization, routing and prompt chaining.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e19
  prompt: 'Building agent tools, the course''s advice on how many:'
  options:
  - As many as possible — the model will pick
  - Few, well-described, hard to misuse
  - One generic tool with a large argument schema
  - One tool per API endpoint, mirroring the backend
  answer: Few, well-described, hard to misuse
  explanation: Every tool adds description tokens and one more way to choose wrongly, and overlapping tools make
    the choice ambiguous. One generic tool moves the difficulty into its arguments, and mirroring endpoints exposes
    the backend's shape instead of the task's.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: e20
  prompt: 'Grading agents on trajectory as well as outcome matters because:'
  options:
  - Trajectory grading is cheaper
  - An agent can reach the right answer by an unsafe or non-reproducible path
  - Outcome grading requires human labels
  - Trajectory is the only observable signal in production
  answer: An agent can reach the right answer by an unsafe or non-reproducible path
  explanation: A right final answer may have come from deleting a test, skipping a check or luck. Only the path
    shows which.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f1
  prompt: 'Prefix caching requires:'
  options:
  - Semantically similar prompts
  - A byte-identical prefix
  - The same model and temperature
  - A dedicated cache endpoint
  answer: A byte-identical prefix
  explanation: The cache is keyed on the exact tokens from the start of the prompt, so one changed character invalidates
    everything after it. Similar prompts do not count.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f2
  prompt: Prefix caching reuses only a byte-identical prefix of the prompt. What layout rule follows?
  options:
  - Dynamic content first, static content last
  - Static content first, dynamic content last
  - Alphabetical ordering of message blocks
  - Shortest blocks first
  answer: Static content first, dynamic content last
  explanation: Whatever changes ends the cached prefix, so the parts that never change (system prompt, tools, documents)
    go first and the per-request parts last. A timestamp at the top defeats the cache.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f3
  prompt: 'Prefix caching''s approximate input-cost saving:'
  options:
  - ~30%
  - ~50%
  - ~90%
  - ~99%
  answer: ~90%
  explanation: On Anthropic's API, input tokens read from the cache are billed at about a tenth of the normal input
    price, so the cached part of a prompt costs about 90% less. Writing to the cache costs a little more than normal
    input.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f4
  prompt: How do you verify a cache hit?
  options:
  - Compare latency against a baseline
  - Read `cache_read_input_tokens` in the response usage
  - Check the response `id` prefix
  - Enable debug logging on the SDK
  answer: Read `cache_read_input_tokens` in the response usage
  explanation: The usage block reports how many input tokens were read from the cache, and zero means a miss. Latency
    is too noisy to tell you.
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
  explanation: Prefix caching still runs the model and generates a fresh answer; it only skips re-reading the prefix.
    Semantic caching skips the model and returns an answer given earlier to a similar query.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f6
  prompt: 'Semantic caching''s characteristic risk:'
  options:
  - Cache stampede under load
  - Serving a stored answer to a query that is similar but not equivalent
  - Unbounded memory growth
  - Higher input token cost
  answer: Serving a stored answer to a query that is similar but not equivalent
  explanation: '"How do I cancel my order?" and "How do I cancel my subscription?" sit close together as embeddings
    and have different answers.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f7
  prompt: 'Prefix cache TTL is on the order of:'
  options:
  - Seconds
  - Minutes
  - Hours
  - Days
  answer: Minutes
  explanation: Anthropic's default is five minutes, refreshed each time the prefix is read, with a one-hour option
    at a higher write price. Caching therefore pays for requests that arrive close together, not ones hours apart.
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
  explanation: Streaming changes neither the tokens nor the total time. It shows the first token sooner, so the
    wait feels shorter. The other three reduce what you actually pay.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f10
  prompt: 'The course insists cost be reported as:'
  options:
  - Cost per API call
  - Cost per successful task
  - Cost per thousand tokens
  - Cost per user session
  answer: Cost per successful task
  explanation: A call that fails still costs money, and one task may take several calls. Dividing total spend by
    the tasks that succeeded counts both.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f11
  prompt: The course insists cost be reported per successful task rather than per API call. Why does that framing
    matter?
  options:
  - It is easier to compute
  - A cheaper model that fails and retries can cost more per successful task than an expensive one that
    succeeds first time
  - It aligns with provider billing
  - It removes the need to track token counts
  answer: A cheaper model that fails and retries can cost more per successful task than an expensive one
    that succeeds first time
  explanation: A model at a third of the price that needs four attempts costs a third more per finished task than
    the expensive model that succeeds first time.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f12
  prompt: '"Context rot" refers to:'
  options:
  - Stale cache entries returning outdated answers
  - Degrading model performance as the context window fills
  - Corrupted serialization of conversation state
  - Memory entries becoming inconsistent across sessions
  answer: Degrading model performance as the context window fills
  explanation: 'As the context grows, the model uses any one part of it less reliably: recall drops and early instructions
    are followed less. It is not about caches or stored state.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f13
  prompt: In compaction, which content is *never* summarized away first?
  options:
  - Tool outputs
  - Intermediate reasoning
  - Architectural decisions and constraints
  - Earlier user turns
  answer: Architectural decisions and constraints
  explanation: Decisions and constraints are short, and everything after depends on them. Lose one and the agent
    redoes or contradicts earlier work.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f14
  prompt: Which is dropped *first* under compaction pressure?
  options:
  - Architectural decisions
  - Tool outputs
  - The system prompt
  - The current task statement
  answer: Tool outputs
  explanation: 'Tool outputs are the bulkiest content and the easiest to get back: the file can be read again and
    the search run again.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f15
  prompt: 'According to the harness-engineering note on tool design, skill/tool descriptions that stay resident
    should be sized at roughly:'
  options:
  - ~10 tokens
  - ~45 tokens
  - ~100 tokens
  - As long as needed for clarity
  answer: ~10 tokens
  explanation: A name plus a line on what it does and when to use it is all that has to stay in the context; the
    full procedure loads when the task calls for it. About ten tokens is the course's figure for that resident line.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: f16
  prompt: The course keeps skill and tool descriptions to a small token budget. Why does that budget matter at all?
  options:
  - Long descriptions confuse the tokenizer
  - Every description sits in the prefix of every call — it is a fixed tax per request
  - Providers cap tool schema length
  - Shorter descriptions improve tool-selection accuracy monotonically
  answer: Every description sits in the prefix of every call — it is a fixed tax per request
  explanation: 'Descriptions are sent with every request whether or not the tool is used, so fifty tools cost fifty
    descriptions on each call. Shorter is not always more accurate: the description still has to say when to use
    the tool.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g1
  prompt: 'The three components of an eval:'
  options:
  - Dataset, metric, threshold
  - Task, trial, grader
  - Input, output, label
  - Baseline, candidate, judge
  answer: Task, trial, grader
  explanation: A task is one problem with its success criteria, a trial is one attempt at it (several, because outputs
    vary), and a grader is the logic that scores an attempt.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g2
  prompt: 'The grader ladder, cheapest first:'
  options:
  - Human → LLM-judge → code
  - Code → LLM-judge → human
  - LLM-judge → code → human
  - Code → human → LLM-judge
  answer: Code → LLM-judge → human
  explanation: A code check is fast, cheap and gives the same result every time, so use one wherever it can be written.
    A model judge handles what needs judgement, and people cost the most, so they are used to calibrate the judge.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g3
  prompt: 'Tier 1 (unit) evals are characterized by:'
  options:
  - Full end-to-end runs against production dependencies
  - No LLM calls, and cheap enough to run on every commit
  - Mocked tools with trajectory assertions
  - Human review of sampled traces
  answer: No LLM calls, and cheap enough to run on every commit
  explanation: These are deterministic checks on parsing, schemas and how tool arguments are built. With no model
    call they are fast and free, so they can run on every commit.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g4
  prompt: 'Tier 2 evals are:'
  options:
  - Unit-level assertions on parsing and formatting
  - Trajectory evals with mocked tools
  - End-to-end release gates
  - Online A/B tests
  answer: Trajectory evals with mocked tools
  explanation: Mocked tools make a run cheap and repeatable while still checking which tools the agent called, in
    what order and with what arguments.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g5
  prompt: 'Tier 3 (end-to-end) evals should run:'
  options:
  - On every commit
  - On release gates only
  - Continuously in production
  - Nightly on a full corpus
  answer: On release gates only
  explanation: Real dependencies make these runs slow, costly and flaky. Run them when the result decides a release
    and leave every commit to the cheaper tiers.
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
  explanation: A capability eval measures what the agent cannot yet do, so a low pass rate is room to improve. A
    regression eval protects what already works, so any drop is a signal.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g8
  prompt: 'The graduation rule says:'
  options:
  - Capability evals become regression evals once they pass reliably
  - Regression evals are retired after three green runs
  - Tier 2 evals graduate to Tier 3 at release
  - LLM-judge graders graduate to code graders
  answer: Capability evals become regression evals once they pass reliably
  explanation: Once a capability passes consistently it is no longer a target to reach but behaviour to protect,
    so it moves into the regression suite.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g9
  prompt: How many examples to start an eval set with?
  options:
  - 5–10 synthetic cases
  - 20–50 real failures
  - 200–500 stratified samples
  - As many as the corpus allows
  answer: 20–50 real failures
  explanation: 'This is the course''s starting size: enough cases to show a pattern and few enough to read every
    one. Starting small beats waiting for a large set.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g10
  prompt: The course starts an eval set with 20–50 real failures. Why real failures rather than synthetic cases?
  options:
  - Synthetic data is more expensive to produce
  - Real failures encode the distribution you actually fail on; synthetic cases encode your assumptions
  - Synthetic cases cannot be graded by code
  - Real failures are already labeled
  answer: Real failures encode the distribution you actually fail on; synthetic cases encode your assumptions
  explanation: Cases you invent test what you already thought of. Failures from real use show where the system actually
    breaks.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g11
  prompt: 'Between trials you must:'
  options:
  - Reuse the environment to save setup cost
  - Reset the environment so trials are independent
  - Increase temperature to sample diversity
  - Carry forward memory to test continuity
  answer: Reset the environment so trials are independent
  explanation: Files, state or cache left over from one trial can help or break the next. The trials would no longer
    be independent, and the pass rate would mean nothing.
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
  prompt: According to the eval pillar's note on production and the maturity ladder, what share of production traces
    should be scored?
  options:
  - 1–2%
  - 10–20%
  - 50%
  - 100%
  answer: 10–20%
  explanation: 'This is the course''s range: enough traces to catch drift and rare failures without paying to judge
    every request. A critical flow can be sampled more heavily.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g14
  prompt: 'After a model or prompt change, the course recommends:'
  options:
  - Rolling back if any metric drops
  - A 48-hour full trace review
  - Doubling the sampling rate for a week
  - Freezing evals until metrics stabilize
  answer: A 48-hour full trace review
  explanation: A change can shift behaviour in ways the offline evals do not cover, so the course reviews every
    trace for the first two days and then goes back to sampling.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g16
  prompt: 'As an illustrative rule of thumb rather than a measured figure, the split of deployment effort is:'
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
  explanation: Langfuse can run on your own infrastructure, so traces holding user data never leave it. The comparison
    is as the bank cites it; check what each product offers now.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: g18
  prompt: 'Outcome evals and trajectory evals should be:'
  options:
  - Chosen based on whether the task is deterministic
  - Both graded — the answer and the path taken
  - Merged into a single composite score
  - Run in separate tiers, never together
  answer: Both graded — the answer and the path taken
  explanation: The outcome says whether the task was done. The trajectory says whether it was done safely and efficiently.
    Either one alone misses failures the other catches.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i1
  prompt: 'The course names one word "interviewers listen for" in orchestration. It is:'
  options:
  - Atomicity
  - Idempotency
  - Durability
  - Determinism
  answer: Idempotency
  explanation: An idempotent job gives the same result whether it runs once or five times, which is what makes retries
    and backfills safe.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i2
  prompt: 'Its three named mechanisms:'
  options:
  - Transactions, savepoints, rollbacks
  - Upserts, partition overwrites, dedup keys
  - Locks, leases, fencing tokens
  - Checksums, retries, backoff
  answer: Upserts, partition overwrites, dedup keys
  explanation: An upsert writes by key instead of appending, a partition overwrite replaces a whole day's partition,
    and a dedup key drops a repeated event. Each makes a second run harmless.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i3
  prompt: 'The MLOps maturity ladder, in order:'
  options:
  - Notebook → automated pipeline → scripted + tracked → CI/CD-gated → monitored
  - Notebook → scripted + tracked → automated pipeline → CI/CD-gated → monitored/self-healing
  - Scripted → notebook → CI/CD-gated → automated pipeline → monitored
  - Notebook → CI/CD-gated → scripted + tracked → automated → self-healing
  answer: Notebook → scripted + tracked → automated pipeline → CI/CD-gated → monitored/self-healing
  explanation: 'Each rung adds what the one before lacked: scripts and tracked experiments make work reproducible,
    a pipeline automates it, CI/CD gates what ships, and monitoring closes the loop.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i4
  prompt: 'The rollout ladder:'
  options:
  - Canary → shadow → full
  - Shadow → canary → full
  - Blue/green → canary → full
  - Canary → blue/green → full
  answer: Shadow → canary → full
  explanation: The order is by rising exposure. Shadow risks nothing a user sees, a canary risks a small share of
    users, and full rollout follows once both look right.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i5
  prompt: 'Shadow deployment means:'
  options:
  - A small percentage of live traffic is routed to the new model
  - The new model receives production traffic but its output is not served
  - The new model runs on a replica of yesterday's data
  - Two models serve alternately by request hash
  answer: The new model receives production traffic but its output is not served
  explanation: Shadowing lets you compare the new model's predictions and latency with the live model's on real
    inputs, with no risk to users. Routing a small share of live traffic is a canary.
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
  explanation: 'The layers run from outside in: is the service up and fast, have the inputs changed, has the relationship
    changed, and, once labels arrive, was the model right. Labels come late, so the first three are the early warnings.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i8
  prompt: 'Alert thresholds should be tied to:'
  options:
  - Historical percentiles only
  - Retrain triggers
  - On-call rotation capacity
  - SLA penalties
  answer: Retrain triggers
  explanation: An alert nobody acts on is noise. Tying a threshold to a defined action, such as retraining, gives
    every alert a consequence.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i9
  prompt: 'Debugging "the dashboard number is wrong", the ordered lineage walk is:'
  options:
  - Metric definition → join fan-out → ingest dedup → source freshness
  - Source freshness → ingest dedup → join fan-out → metric definition drift
  - Join fan-out → source freshness → metric definition → ingest dedup
  - Ingest dedup → metric definition → source freshness → join fan-out
  answer: Source freshness → ingest dedup → join fan-out → metric definition drift
  explanation: 'Each check costs more than the one before: freshness is one timestamp, dedup is a count, fan-out
    means comparing row counts across a join, and definition drift means reading the logic and asking people.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i10
  prompt: When debugging "the dashboard number is wrong", the lineage walk checks source freshness, then ingest
    dedup, then join fan-out, then metric definition drift. What is the principle behind that ordering?
  options:
  - Check the layer closest to the user first
  - Check the cheapest layer first
  - Check the most recently changed layer first
  - Check in pipeline execution order always
  answer: Check the cheapest layer first
  explanation: Cheap checks rule out common causes quickly. Here the cheapest-first order happens to match the pipeline's
    order, but cost is the rule.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i11
  prompt: A feature store is justified by which two conditions?
  options:
  - Data volume above 1TB and more than 10 models
  - Online/offline consistency (train/serve skew) and feature reuse across teams
  - Streaming ingestion and sub-second serving
  - Regulatory lineage and PII classification
  answer: Online/offline consistency (train/serve skew) and feature reuse across teams
  explanation: 'A feature store solves two problems: the same feature computed one way in training and another in
    serving, and several teams rebuilding the same features. Data volume or streaming alone does not call for one.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i12
  prompt: A feature store is justified by online/offline consistency (train/serve skew) and feature reuse across
    teams. If neither condition holds, what does the course say?
  options:
  - Build a lightweight feature store anyway for future-proofing
  - A well-tested mart is enough
  - Use a caching layer instead
  - Compute features inline at request time
  answer: A well-tested mart is enough
  explanation: A tested mart, a table of features built by the warehouse pipeline, gives one definition of each
    feature without another system to run.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: i13
  prompt: 'Batch vs streaming — the course''s default:'
  options:
  - Streaming, since it subsumes batch
  - Batch until a product need forces streaming
  - Lambda architecture from the start
  - Whichever matches the source system
  answer: Batch until a product need forces streaming
  explanation: Batch is simpler to build, test and rerun. Streaming adds ordering, late data and state, so pay for
    it only when the product needs data that is seconds old.
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
  explanation: Five steps at about eight minutes each come to 40 minutes, which leaves the rest of the slot for
    introductions and your own questions.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j2
  prompt: 'Step 1 is Clarify & scope. The course''s rule:'
  options:
  - Restate the prompt, then design
  - Never design against the raw prompt
  - Ask at most one clarifying question to save time
  - Start with the data model
  answer: Never design against the raw prompt
  explanation: The prompt is vague on purpose. Designing straight away means guessing the users, the scale and the
    constraints, and the interviewer is scoring whether you ask.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j3
  prompt: 'The three clarification targets:'
  options:
  - Users, data, and model choice
  - Requirements, scale, constraints
  - Latency, cost, accuracy
  - Functional, non-functional, operational
  answer: Requirements, scale, constraints
  explanation: What it has to do, how big it has to be, and what limits it, such as latency, budget, compliance
    and team.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j4
  prompt: 'The strongest opening question is closest to:'
  options:
  - '"What''s the expected QPS?"'
  - '"Who are the primary users, and what''s the top priority — latency, accuracy, cost, or safety?"'
  - '"Which cloud provider are we on?"'
  - '"Should this use RAG or fine-tuning?"'
  answer: '"Who are the primary users, and what''s the top priority — latency, accuracy, cost, or safety?"'
  explanation: The answer decides what you optimise for in the rest of the round. Throughput and cloud provider
    are details, and RAG against fine-tuning is a solution offered before the problem is known.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j5
  prompt: Why write the non-functional requirements down explicitly?
  options:
  - Interviewers score completeness of the requirements list
  - They *are* the trade-off axes for the rest of the round
  - They determine the database choice
  - They are needed for the cost model
  answer: They *are* the trade-off axes for the rest of the round
  explanation: Every later choice trades one of them against another, such as latency against accuracy. Written
    down, you can point at them when you justify a choice.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j6
  prompt: 'The trade-off narration formula:'
  options:
  - Pick the best option, then defend it against objections
  - Consider 2–3 solutions → narrate pros/cons → ask which priority wins → justify the pick
  - Enumerate all options, then let the interviewer choose
  - State the trade-off, then move on
  answer: Consider 2–3 solutions → narrate pros/cons → ask which priority wins → justify the pick
  explanation: It shows you saw the alternatives, lets the interviewer steer, and ties your pick to a stated priority.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j7
  prompt: 'Step 4 asks you to:'
  options:
  - Optimize the design for scale
  - Name your design's weaknesses before the interviewer does
  - Estimate cost
  - Draw the sequence diagram
  answer: Name your design's weaknesses before the interviewer does
  explanation: Every design has weak points. Naming them with a mitigation shows you know them; waiting for the
    interviewer makes it look as though you missed them.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j8
  prompt: 'The interviewer says your trade-off was wrong. The scored behavior is:'
  options:
  - Defend it — consistency signals conviction
  - Adapt visibly; there are no points for stubbornness
  - Ask them to justify their objection first
  - Abandon the whole design and restart
  answer: Adapt visibly; there are no points for stubbornness
  explanation: The interviewer is often changing a constraint to see whether you can update. Revise the part it
    affects and say what changed and why; do not restart.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j9
  prompt: 'You hit a genuine knowledge gap mid-round. The course''s tactic:'
  options:
  - Reason from first principles without flagging it
  - Say "my understanding there is superficial", then redirect
  - Ask to skip that component
  - Guess confidently and correct later if challenged
  answer: Say "my understanding there is superficial", then redirect
  explanation: An honest flag costs little, and a bluff falls to one follow-up question. Then move to the part you
    do know.
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
  explanation: The gateway is the front door, so it settles who is calling and how much they may use before any
    model work starts. The other options belong to orchestration, retrieval and output validation.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j12
  prompt: Which is *not* one of the five named sidecars?
  options:
  - Caches (prefix + semantic)
  - State store (session/checkpointer)
  - Feature store
  - HITL queue
  answer: Feature store
  explanation: The five are caches, the state store, tracing and observability, the eval pipeline and the human-in-the-loop
    queue. A feature store belongs to the ML spine, not this reference architecture.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: j13
  prompt: 'From the bottleneck table, "model cold start" is mitigated by:'
  options:
  - Backoff retries and multi-provider routing
  - Warm pools and pre-warming
  - Sharded queues and priority tiers
  - Pruning and periodic index rebuild
  answer: Warm pools and pre-warming
  explanation: Cold start is the time taken to load a model before it can serve its first request, so the fix is
    to keep instances loaded. The other options are the mitigations for rate limits, queue backlog and index growth.
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
  explanation: 'All four distractors are real practices — the question is which one targets *cascading* failure.
    A circuit breaker tracks the failure rate of a dependency and, once it crosses a threshold, **opens**: calls
    fail fast without touching the sick service. After a cooldown it goes **half-open**, admits a few probes, and
    either closes (recovered) or re-opens. That containment is the point. Timeouts bound a *single* call and are
    necessary but insufficient — with a dead dependency and a 30s timeout, in-flight requests still pile up until
    threads, connections, or queue depth are exhausted, and the caller dies too. Retries make cascades *worse* by
    multiplying load on an already-failing service unless paired with a breaker and jittered backoff. Exception
    handling is local error propagation, not a load-shedding mechanism. In the LLM stack this is the pattern behind
    provider fallback and the degradation ladder: trip the breaker on the primary model endpoint, route to the fallback,
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
  explanation: Start with who it is for, what problem they have, how you would know it worked and what limits you,
    all before any architecture.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: k2
  prompt: Which is the better-framed problem statement?
  options:
  - '"Build a RAG chatbot for support"'
  - '"Reduce support cost 20% while holding CSAT"'
  - '"Deploy an LLM over the knowledge base"'
  - '"Improve first-response time using AI"'
  answer: '"Reduce support cost 20% while holding CSAT"'
  explanation: It names an outcome, a target and a guardrail (CSAT), and no solution. The others name a technology,
    or an improvement with no target and nothing protected.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: k3
  prompt: 'The napkin token-cost formula:'
  options:
  - queries/day × latency × $/hour
  - tokens/query × $/M tokens × queries/day
  - model size × requests × utilization
  - context length × users × sessions
  answer: tokens/query × $/M tokens × queries/day
  explanation: 'The units work out: tokens per query × dollars per token × queries per day gives dollars per day.
    None of the others is a cost of tokens.'
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
  prompt: The intended answer to "Mistral 7B gives 90% of the accuracy, so why still pick it over GPT-4?" is that
    the last 10% costs 20× and the use case's error tolerance does not need it. When should you reverse that
    answer?
  options:
  - When traffic volume is high
  - When errors are expensive
  - When the model is self-hosted
  - When the corpus is multilingual
  answer: When errors are expensive
  explanation: The cheaper model is the right pick while its errors are tolerable. When one error is expensive,
    the last 10% of accuracy is worth more than the price difference. "ROI, not model maximalism" still holds; the
    reversal is what shows judgment rather than a memorized slogan.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: k6
  prompt: Where does AI belong first, and last?
  options:
  - First in high-stakes decisions, last in drafting
  - First in high-volume, tolerant-of-review workflows; last in irreversible/high-stakes actions
  - First wherever data is cleanest; last where data is sparse
  - First in customer-facing flows; last in internal tooling
  answer: First in high-volume, tolerant-of-review workflows; last in irreversible/high-stakes actions
  explanation: High volume gives savings and data, and a review step catches errors cheaply. Where a mistake cannot
    be undone, the cost of an error outweighs the saving.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: k7
  prompt: 'The metrics tree:'
  options:
  - Input → output → outcome
  - North star → driver metrics → guardrail metrics
  - Leading → lagging → composite
  - Adoption → retention → revenue
  answer: North star → driver metrics → guardrail metrics
  explanation: One north star states the goal, driver metrics are what teams can move to reach it, and guardrail
    metrics must not get worse while they push.
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
  explanation: 'When confidence is low: decline to answer instead of guessing, show the sources so the user can
    check, and hand over to a person.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: k10
  prompt: 'The prioritization formula:'
  options:
  - (impact + confidence) − effort
  - impact × confidence ÷ effort, with guardrail metrics as veto
  - reach × impact × confidence ÷ effort
  - value ÷ (cost × risk)
  answer: impact × confidence ÷ effort, with guardrail metrics as veto
  explanation: Multiplying impact by confidence discounts uncertain bets, and dividing by effort gives return per
    unit of work. The veto stops a high score shipping something that harms a protected metric. The option with
    reach is RICE.
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
  explanation: The 92% says nothing until you know how many errors that is at your volume, what each one costs,
    whether the 8% are harmless or catastrophic, and what the product does when it is wrong.
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
- id: m10
  prompt: Which change raises the power of a test?
  options:
  - Lowering α from 0.05 to 0.01
  - Reducing the variance of the metric
  - Using a smaller sample
  - Targeting a smaller effect
  answer: Reducing the variance of the metric
  explanation: Power rises with sample size, effect size and α, and falls with variance. Lowering α reduces
    power.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: m11
  prompt: 'A test on 5 million users finds a lift of 0.02 points with p = 0.001. The right reading is:'
  options:
  - 'Ship: the result is highly significant'
  - 'Rerun: results this significant are suspicious'
  - Statistically significant, but check whether a lift that small is worth acting on
  - Not significant, because the lift is small
  answer: Statistically significant, but check whether a lift that small is worth acting on
  explanation: With millions of users almost any difference is statistically significant. Compare the effect
    and its interval with the smallest lift worth the cost.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: m12
  prompt: A satisfaction survey is emailed to users active in the last week. Will a larger response count remove
    the bias in the average score?
  options:
  - 'No: more data shrinks variance and leaves selection bias unchanged'
  - Yes, by the Law of Large Numbers
  - Yes, once n exceeds 30
  - Only if the scores are Normally distributed
  answer: 'No: more data shrinks variance and leaves selection bias unchanged'
  explanation: Bias comes from who is in the sample. A larger sample of the same kind gives a tighter interval
    around the wrong number.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: m13
  prompt: Which test compares conversion rates between two independent groups of 50,000 users each?
  options:
  - Paired t-test
  - Two-proportion z-test
  - Mann-Whitney U
  - One-way ANOVA
  answer: Two-proportion z-test
  explanation: Two independent proportions with large samples call for the two-proportion z-test. A chi-square
    test on the 2×2 table is equivalent.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: m14
  prompt: A test is not significant, and its confidence interval is wide enough to include the minimum effect
    you care about. What do you conclude?
  options:
  - The change has no effect
  - The change has a negative effect
  - The test should be rerun one-sided
  - 'The test is inconclusive: it was underpowered for that effect'
  answer: 'The test is inconclusive: it was underpowered for that effect'
  explanation: Absence of evidence is not evidence of absence. Only an interval that excludes the minimum effect
    supports "no meaningful effect".
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: n7
  prompt: 'In a logistic regression, a binary feature has a coefficient of 0.69. Having the feature:'
  options:
  - Raises the probability by 69 percentage points
  - Raises the probability by 0.69%
  - Roughly doubles the odds
  - Roughly doubles the probability
  answer: Roughly doubles the odds
  explanation: The coefficient is a change in log-odds, and e^0.69 is about 2. The change in probability depends
    on the starting point.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: n14
  prompt: Which loss does logistic regression minimise?
  options:
  - Mean squared error
  - Hinge loss
  - Log loss (cross-entropy)
  - Gini impurity
  answer: Log loss (cross-entropy)
  explanation: Log loss is the negative log-likelihood of a Bernoulli outcome, so minimising it is maximum
    likelihood.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: r5
  prompt: How does MRR differ from NDCG?
  options:
  - MRR needs graded relevance labels and NDCG does not
  - MRR looks only at the first relevant result, and NDCG scores the whole ranking
  - MRR ignores rank and NDCG does not
  - MRR is only for recommenders
  answer: MRR looks only at the first relevant result, and NDCG scores the whole ranking
  explanation: MRR suits tasks with one right answer. NDCG takes graded relevance and discounts every position,
    so it suits lists the user reads through.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: s5
  prompt: How should you cross-validate a forecasting model?
  options:
  - Shuffle the rows and use k folds
  - Train on the past and validate on the block that follows, rolling the origin forward
  - Validate on the earliest block and train on the rest
  - Use leave-one-out on random rows
  answer: Train on the past and validate on the block that follows, rolling the origin forward
  explanation: Shuffled folds let the model train on the future. A rolling origin keeps every validation block after
    its training data.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: s6
  prompt: A forecast has a MASE of 1.2. What does that mean?
  options:
  - It is 20% better than the naive forecast
  - Its errors are 1.2 units on average
  - It explains 20% more variance than the naive forecast
  - Its errors are 20% larger than the naive forecast's
  answer: Its errors are 20% larger than the naive forecast's
  explanation: MASE divides the model's mean absolute error by that of a naive forecast, so anything above 1 loses
    to the naive baseline.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: s7
  prompt: What is a guardrail metric in an experiment?
  options:
  - A metric that must not get worse while you try to move the target metric
  - The metric the experiment is designed to move
  - A metric that checks the randomisation
  - The long-term metric the company steers by
  answer: A metric that must not get worse while you try to move the target metric
  explanation: Latency, unsubscribes and refunds are typical guardrails. The last option is the north star.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
---
