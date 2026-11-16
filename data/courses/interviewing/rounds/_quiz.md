---
title: 'Technical interview questions: multiple choice and worked problems'
summary: Multiple-choice questions from the technical-questions MCQ bank, and worked problems with a numeric answer for the statistics and ML screen.
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
  prompt: Which change gives *true parallelism* for that CPU-bound Python workload?
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
  prompt: 'State the GIL''s effect directly: what does it constrain?'
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
  prompt: Given C8, which discipline follows directly?
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
  prompt: 'DPO''s stated trade-off:'
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
- id: d1
  prompt: 'The canonical pipeline, with optional stages in parentheses:'
  options:
  - Ingest → embed → chunk → index; query → retrieve → generate
  - Ingest → chunk → embed → index; query → (rewrite) → retrieve → (rerank) → generate → (verify)
  - Chunk → ingest → index → embed; query → rerank → retrieve → generate
  - Ingest → chunk → index → embed; query → retrieve → (verify) → generate
  answer: Ingest → chunk → embed → index; query → (rewrite) → retrieve → (rerank) → generate → (verify)
  explanation: 'Text has to be chunked before it can be embedded, and embedded before it can be indexed. Each optional
    stage sits where it acts: rewrite before retrieval, rerank after it, verify after generation.'
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
  explanation: Headings mark where the author changed topic, which is the cheapest reliable boundary. A section
    over the budget is then split at paragraphs and sentences, so no chunk breaks in the middle of a thought.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d3
  prompt: 'The course''s stance on semantic chunking:'
  options:
  - The recommended default for production corpora
  - Expensive at ingest and inconsistent — not the default
  - Required whenever documents lack headings
  - Equivalent to recursive splitting but faster
  answer: Expensive at ingest and inconsistent — not the default
  explanation: Semantic chunking embeds every sentence to find topic shifts, which adds cost at ingest, and where
    it cuts depends on a threshold that behaves differently from corpus to corpus. Structure-first splitting stays
    the default.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d4
  prompt: 'Typical chunk token budget and overlap:'
  options:
  - ~256 tokens, ~32 overlap
  - ~512 tokens, ~64 overlap
  - ~1024 tokens, ~128 overlap
  - ~2048 tokens, ~256 overlap
  answer: ~512 tokens, ~64 overlap
  explanation: 'This is the bank''s starting point, not a law: a chunk long enough to hold one complete idea and
    short enough that its embedding is about one thing, with an overlap of about an eighth so a sentence cut at
    a boundary survives whole in one chunk. Tune both on your own corpus.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d5
  prompt: 'Parent/child chunking means:'
  options:
  - Index large chunks, generate from extracted sentences
  - Index small chunks, generate from their parent
  - Duplicate each chunk at two granularities in the same index
  - Chunk by document hierarchy only
  answer: Index small chunks, generate from their parent
  explanation: A small chunk has a precise embedding, so it matches the query well. Its parent section gives the
    model enough surrounding text to answer from.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d6
  prompt: A `min_tokens` filter at ingest can cause which silent failure?
  options:
  - Oversized chunks are truncated mid-sentence
  - Short-but-valid sections (one-line FAQ answers) are dropped from the index entirely
  - Embeddings drift toward the corpus mean
  - BM25 scores become incomparable with cosine
  answer: Short-but-valid sections (one-line FAQ answers) are dropped from the index entirely
  explanation: 'A minimum length meant to drop stray headers also drops a complete one-line answer, and nothing
    raises an error: the question simply never retrieves it.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d7
  prompt: 'E5-family embedding models require:'
  options:
  - L2-normalized inputs
  - '`"query: "` / `"passage: "` prefixes'
  - Lowercased text
  - A fixed 512-token pad
  answer: '`"query: "` / `"passage: "` prefixes'
  explanation: E5 models were trained with those prefixes on each side, so leaving them out at inference quietly
    lowers retrieval quality.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d9
  prompt: Vector-only search and BM25-only search fail in which way?
  options:
  - Vector misses paraphrases; BM25 misses exact tokens
  - Vector misses exact tokens (product names, error codes); BM25 misses paraphrases
  - Both miss exact tokens; only reranking recovers them
  - Vector misses short queries; BM25 misses long ones
  answer: Vector misses exact tokens (product names, error codes); BM25 misses paraphrases
  explanation: Embeddings capture meaning, so they match paraphrases but blur a rare exact string such as an error
    code. BM25 matches tokens, so it does the opposite. This is the case for hybrid search.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d10
  prompt: Reciprocal Rank Fusion uses which constant?
  options:
  - k = 10
  - k = 60
  - k = 100
  - k is tuned per corpus
  answer: k = 60
  explanation: RRF scores a document as the sum of 1/(k + rank) over the result lists. k = 60 comes from the original
    paper (Cormack et al., 2009) and is the usual default; it flattens the gap between top ranks so one list cannot
    dominate.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d11
  prompt: Why RRF instead of a weighted sum of BM25 and cosine scores?
  options:
  - RRF is provably optimal for hit rate
  - BM25 and cosine scores have incomparable distributions; rank fusion needs no score normalization
  - RRF is faster to compute
  - Weighted sums require normalized embeddings
  answer: BM25 and cosine scores have incomparable distributions; rank fusion needs no score normalization
  explanation: BM25 scores are unbounded and change with query length, while cosine similarities sit in a narrow
    band. A weighted sum needs a normalisation tuned per corpus; ranks can be compared as they are.
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
  explanation: CRAG grades the retrieved documents in a separate step and routes on the grade before generating,
    which is control flow you write. Self-RAG trains the model to make those decisions itself while it generates.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d14
  prompt: 'Self-RAG''s canonical mechanism (Asai et al.):'
  options:
  - LLM-driven query expansion into N paraphrases
  - Reflection tokens (`[Retrieve]`, `[IsRel]`, `[IsSup]`) emitted mid-generation
  - A confidence gate on retrieved chunks with fallback
  - Entity-graph traversal alongside vector search
  answer: Reflection tokens (`[Retrieve]`, `[IsRel]`, `[IsSup]`) emitted mid-generation
  explanation: The model is fine-tuned to emit special tokens that say whether to retrieve, whether a passage is
    relevant and whether the output is supported. The other options describe multi-query expansion, a CRAG-style
    gate and GraphRAG.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d15
  prompt: 'Some blogs use "Self-RAG" to mean LLM query expansion. In an interview you should:'
  options:
  - Use the blog definition, since it is more common
  - Surface the ambiguity and name the canonical version — that itself scores
  - Avoid the term entirely
  - Correct the interviewer firmly and move on
  answer: Surface the ambiguity and name the canonical version — that itself scores
  explanation: The term is used loosely. Saying which meaning you intend stops you and the interviewer talking past
    each other, and shows you know the paper.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d16
  prompt: 'HyDE works by:'
  options:
  - Embedding the question and expanding with synonyms
  - Generating a hypothetical answer and embedding *that* for search
  - Retrieving twice and fusing the ranks
  - Reranking with a cross-encoder on hypothetical pairs
  answer: Generating a hypothetical answer and embedding *that* for search
  explanation: A question and its answer are worded differently. A made-up answer, even with the facts wrong, is
    written like the documents, so its embedding lands nearer to them than the question's does.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d17
  prompt: 'HyDE''s cost:'
  options:
  - Roughly doubles total pipeline latency
  - One extra small-model call, ~100–200ms
  - Negligible — it reuses the main generation call
  - One extra embedding call only
  answer: One extra small-model call, ~100–200ms
  explanation: The hypothetical answer is one short generation by a small model before the search. It cannot reuse
    the main call, which runs after retrieval. The latency figure is the bank's estimate; measure it on your own
    stack.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: d18
  prompt: 'Multi-query (RAG-Fusion) recall gain and its diminishing-returns point:'
  options:
  - +5%, past 2 variants
  - +10–15%, past 3 variants
  - +20–25%, past 5 variants
  - +30%, past 10 variants
  answer: +10–15%, past 3 variants
  explanation: Each rewrite reaches documents the original wording missed, but later variants overlap with earlier
    ones while each still costs a retrieval. The figures are the bank's rule of thumb; measure on your own corpus.
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
  explanation: Building an entity graph costs model calls over the whole corpus and pays off for questions that
    connect many documents. A single fact is answered by one chunk, and a wiki's links are already a graph.
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
  explanation: Faithfulness asks whether the answer is supported by the context, and answer relevancy whether it
    addresses the question. Context precision asks whether the relevant chunks rank high, and context recall whether
    the context holds what was needed. Two score the generator and two the retriever.
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
  prompt: Task length is a design threshold. Beyond roughly what duration does crash recovery become mandatory?
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
  prompt: 'PRINCE (Bayer × Thoughtworks, Fowler 2026) is cited as evidence for:'
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
  prompt: 'The layout rule that follows:'
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
  prompt: Why does that framing matter?
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
  prompt: 'Skill/tool descriptions should be sized at roughly:'
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
  prompt: Why does that budget matter at all?
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
  prompt: Why real failures rather than synthetic cases?
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
  prompt: What share of production traces should be scored?
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
- id: h1
  prompt: 'Direct vs indirect prompt injection:'
  options:
  - Direct comes from the model's own output; indirect from the user
  - Direct comes from the user's input; indirect arrives via content the agent retrieves or reads
  - Direct targets the system prompt; indirect targets tools
  - Direct is deliberate; indirect is accidental
  answer: Direct comes from the user's input; indirect arrives via content the agent retrieves or reads
  explanation: In a direct injection the user types the attack. In an indirect one it is hidden in a web page, email,
    document or tool result that the agent reads, so the user may be the victim.
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
  explanation: 'The course''s framing is that injection is contained, not detected, so an answer that only detects
    is the one called wrong. Trace the untrusted *source* to the dangerous *sink* and cut the path: capability restriction,
    dual-LLM, human approval on the sink.'
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h4
  prompt: 'In the dual-LLM pattern (Willison), the privileged LLM:'
  options:
  - Reads untrusted content and summarizes it for the quarantined LLM
  - Holds the tools and never reads untrusted content
  - Validates the quarantined LLM's outputs before execution
  - Runs with a stricter system prompt but the same inputs
  answer: Holds the tools and never reads untrusted content
  explanation: The privileged model sees only trusted input and is the one that plans and calls tools. Untrusted
    content goes to the quarantined model, and its output is passed around as a variable the privileged model never
    reads.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h5
  prompt: 'The quarantined LLM:'
  options:
  - Has read-only tool access
  - Reads untrusted content but cannot act
  - Acts only after human approval
  - Runs a smaller model to limit damage
  answer: Reads untrusted content but cannot act
  explanation: The quarantined model is assumed to be compromised by whatever it reads, so it gets no tools. Injected
    text then cannot reach anything that can act.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h6
  prompt: 'In the 9-step defense stack, input guardrails sit at position:'
  options:
  - 1st
  - 4th
  - 8th
  - 9th
  answer: 1st
  explanation: Input guardrails screen a request before anything else spends effort on it or is exposed to it, so
    they come first in the bank's stack.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h7
  prompt: 'Output validation sits at:'
  options:
  - 2nd
  - 5th
  - 8th
  - 9th
  answer: 8th
  explanation: Output validation checks the response just before it leaves, after the model and the tools have run.
    Only the after-the-fact review follows it.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h8
  prompt: 'Continuous trace grading sits at:'
  options:
  - 1st
  - 3rd
  - 6th
  - 9th
  answer: 9th
  explanation: Grading traces happens after the response has gone. It does not block anything; it catches what the
    earlier layers missed, so it comes last.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h9
  prompt: 'Memory poisoning vs context poisoning:'
  options:
  - Memory poisoning affects the working context; context poisoning persists across sessions
  - Memory poisoning persists across sessions; context poisoning affects working memory within one
  - Both are within-session; they differ by attack vector
  - Both persist; they differ by which store is targeted
  answer: Memory poisoning persists across sessions; context poisoning affects working memory within one
  explanation: A poisoned memory entry is written to a store and loaded again in later sessions, so the attack outlives
    the conversation. Poisoned context lasts only as long as that context window.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h10
  prompt: 'Denial-of-wallet describes:'
  options:
  - Exhausting a rate limit to deny service
  - Driving up an attacker-controlled volume of expensive model calls to inflate cost
  - Stealing API keys to bill a victim
  - Blocking payment flows in an agentic commerce system
  answer: Driving up an attacker-controlled volume of expensive model calls to inflate cost
  explanation: An attacker triggers a large number of expensive model calls. The service stays up and the bill grows.
    Budgets, rate limits and caps on loop iterations are the defences.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h11
  prompt: 'The three boundaries the course says to establish before shipping any agent:'
  options:
  - Model, data, and network
  - Who can trigger it, where it can act, what it did
  - Input, output, and audit
  - Identity, authorization, and encryption
  answer: Who can trigger it, where it can act, what it did
  explanation: Who can trigger it is authentication and authorisation of callers, where it can act is scoped permissions
    and sandboxing, and what it did is the audit record.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h12
  prompt: '"What it did" maps to which requirement?'
  options:
  - Rate limiting
  - Audit logging / traceability
  - Least-privilege scopes
  - Authentication
  answer: Audit logging / traceability
  explanation: You can only investigate or undo what was recorded. Rate limiting, scopes and authentication answer
    the other two questions.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h13
  prompt: 'The degradation ladder, in order:'
  options:
  - Human → retry → fallback model → simpler baseline
  - Retry → fallback model → simpler baseline → human
  - Fallback model → retry → human → simpler baseline
  - Simpler baseline → retry → fallback model → human
  answer: Retry → fallback model → simpler baseline → human
  explanation: The ladder runs from cheapest and least disruptive to most. A retry handles a transient error, a
    fallback model a provider outage, a simpler baseline gives a degraded answer, and a person comes last because
    that is slowest and costliest.
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
  explanation: Best-of-N jailbreaking reached 89% on GPT-4o and 78% on Claude 3.5 Sonnet (Hughes et al.) by resampling
    variations of a prompt. A filter that falls to trying again is a speed bump, not a boundary, so containment
    in the architecture has to carry the load.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h16
  prompt: '"Typoglycemia" as an attack refers to:'
  options:
  - Injecting invisible Unicode characters
  - Scrambling word interiors so filters miss the string but the model still reads it
  - Overwhelming the tokenizer with rare tokens
  - Homoglyph substitution in domain names
  answer: Scrambling word interiors so filters miss the string but the model still reads it
  explanation: A model, like a person, can read "ignroe prevoius insturctions", but a filter looking for the exact
    phrase does not match it.
  lesson: interviewing/rounds/technical-questions/mcq-bank
- id: h17
  prompt: 'The three guardrail placements:'
  options:
  - Ingest, index, retrieve
  - Input, output, action
  - Client, gateway, model
  - Pre-flight, in-flight, post-flight
  answer: Input, output, action
  explanation: Input guardrails screen what comes in, output guardrails check what goes back, and action guardrails
    check a tool call before it runs.
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
  prompt: 'The principle behind that ordering:'
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
  prompt: 'If neither condition holds, the course says:'
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
  prompt: When should you reverse that answer?
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
- id: l1
  prompt: What is the variance of a Bernoulli variable with p = 0.2?
  options:
  - '0.20'
  - '0.16'
  - '0.04'
  - '0.80'
  answer: '0.16'
  explanation: Variance is p(1 − p) = 0.2 × 0.8 = 0.16.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: l2
  prompt: X is Binomial with n = 100 and p = 0.1. What are its mean and standard deviation?
  options:
  - 10 and 9
  - 10 and 3
  - 10 and 0.9
  - 1 and 3
  answer: 10 and 3
  explanation: Mean np = 10. Variance np(1 − p) = 9, so the standard deviation is 3. Answer A gives the variance.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: l3
  prompt: Card payments are declined at a steady average rate, independently of one another. Which distribution
    models the number declined in a given minute?
  options:
  - Binomial
  - Normal
  - Poisson
  - Geometric
  answer: Poisson
  explanation: A count of independent events in a fixed interval at a constant rate is Poisson. Binomial needs
    a fixed number of trials.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: l4
  prompt: A Poisson variable has mean 4. What is its variance?
  options:
  - '4'
  - '2'
  - '16'
  - It depends on the sample size
  answer: '4'
  explanation: For a Poisson the mean and the variance are both λ.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: l5
  prompt: What does the Central Limit Theorem state?
  options:
  - Any large dataset is approximately Normally distributed
  - The sample mean equals the population mean once n exceeds 30
  - The variance of the data shrinks as n grows
  - The mean of a large sample is approximately Normal even when the data are not
  answer: The mean of a large sample is approximately Normal even when the data are not
  explanation: The theorem is about the distribution of the sample mean, not of the data. The raw data keep
    their shape.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: l6
  prompt: A and B are independent with P(A) = 0.5 and P(B) = 0.4. What is P(A or B)?
  options:
  - '0.9'
  - '0.2'
  - '0.7'
  - '0.8'
  answer: '0.7'
  explanation: P(A or B) = P(A) + P(B) − P(A and B) = 0.5 + 0.4 − 0.5 × 0.4 = 0.7.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: l7
  prompt: A condition has 1% prevalence. A test has 90% sensitivity and a 10% false positive rate. Roughly
    what is the probability of the condition given a positive test?
  options:
  - About 8%
  - About 50%
  - About 90%
  - About 1%
  answer: About 8%
  explanation: 'Bayes: 0.01 × 0.9 / (0.01 × 0.9 + 0.99 × 0.1) = 0.009 / 0.108, about 8%. False positives from
    the large healthy group dominate.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: l8
  prompt: X and Y are independent with variances 4 and 9. What is the standard deviation of X + Y?
  options:
  - '5'
  - '13'
  - About 3.6
  - '6.5'
  answer: About 3.6
  explanation: 'Variances add for independent variables: 4 + 9 = 13, and √13 is about 3.6. Standard deviations
    do not add.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: l9
  prompt: Var(X) = 2. What is Var(3X)?
  options:
  - '6'
  - '9'
  - '12'
  - '18'
  answer: '18'
  explanation: Var(aX) = a²Var(X) = 9 × 2 = 18.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: l10
  prompt: 'E[X + Y] = E[X] + E[Y] holds when:'
  options:
  - X and Y are independent
  - X and Y have the same distribution
  - Always, as long as both expectations exist
  - X and Y are both Normal
  answer: Always, as long as both expectations exist
  explanation: Linearity of expectation needs no independence. It is variances that need zero correlation to
    add.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: l11
  prompt: A sample of n = 100 has a standard error of the mean of 1. What sample size halves it?
  options:
  - '200'
  - '400'
  - '141'
  - 1,000
  answer: '400'
  explanation: The standard error is σ/√n, so halving it takes four times the sample.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: l12
  prompt: How many rolls of a fair die do you expect to need to see the first six?
  options:
  - '6'
  - '3'
  - '3.5'
  - '36'
  answer: '6'
  explanation: The wait for the first success is Geometric with mean 1/p = 6.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: l13
  prompt: Which statement is true of two random variables?
  options:
  - Zero correlation implies independence
  - Independence implies zero correlation
  - Each implies the other
  - Neither implies the other
  answer: Independence implies zero correlation
  explanation: 'Independence implies zero correlation. The reverse fails: with X standard Normal and Y = X²,
    the correlation is 0 but Y is a function of X.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: l14
  prompt: X is Normal. Roughly what is P(X > μ + 2σ)?
  options:
  - 5%
  - 2.5%
  - 16%
  - 0.3%
  answer: 2.5%
  explanation: About 95% lies within 2σ, leaving 5% in the two tails and 2.5% in each.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: l15
  prompt: Which is the best approximation to a Binomial with n = 1,000 and p = 0.002?
  options:
  - Normal with mean 500
  - Poisson with mean 0.002
  - Geometric with p = 0.002
  - Poisson with mean 2
  answer: Poisson with mean 2
  explanation: Large n with small p goes to Poisson with λ = np = 2. A Normal fits badly because np is far
    below 10.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: l16
  prompt: Can the value of a probability density function be greater than 1?
  options:
  - 'Yes: only the area under the density must equal 1'
  - 'No: probabilities cannot exceed 1'
  - Only for discrete variables
  - Only at the mean
  answer: 'Yes: only the area under the density must equal 1'
  explanation: A density is not a probability. Uniform(0, 0.5) has density 2 everywhere on its interval.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: m1
  prompt: A test returns p = 0.03. What does that mean?
  options:
  - There is a 3% chance the null hypothesis is true
  - There is a 97% chance the effect is real
  - If the null were true, data this extreme or more would occur 3% of the time
  - The effect size is 3%
  answer: If the null were true, data this extreme or more would occur 3% of the time
  explanation: A p-value is computed assuming the null is true. It is not the probability that the null is
    true, and it carries no information about effect size.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: m2
  prompt: What is a Type II error?
  options:
  - Rejecting a null hypothesis that is true
  - Failing to reject a null hypothesis that is false
  - Using a one-sided test on two-sided data
  - Running a test without a power calculation
  answer: Failing to reject a null hypothesis that is false
  explanation: Type II is a missed effect, with rate β. Answer A is a Type I error.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: m3
  prompt: The 95% confidence interval for a lift is 0.2 to 1.8 points. Which statement is correct?
  options:
  - There is a 95% probability the true lift is between 0.2 and 1.8
  - 95% of users saw a lift between 0.2 and 1.8
  - The result is not significant because the interval is wide
  - Intervals built this way cover the true lift 95% of the time, and this one excludes zero
  answer: Intervals built this way cover the true lift 95% of the time, and this one excludes zero
  explanation: The 95% describes the procedure over repeated experiments. Because the interval excludes zero,
    the result is significant at 5%.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: m4
  prompt: 'The sample variance computed with divisor n is:'
  options:
  - Unbiased
  - Biased high
  - Biased low
  - Unbiased but inconsistent
  answer: Biased low
  explanation: Deviations are taken from the sample mean, which is closer to the data than the true mean, so
    the divisor n underestimates by the factor (n − 1)/n.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: m5
  prompt: 'The mean squared error of an estimator equals:'
  options:
  - Bias² + variance
  - Bias + variance
  - Variance − bias²
  - Bias × variance
  answer: Bias² + variance
  explanation: MSE = bias² + variance, which is why a biased estimator with low variance can beat an unbiased
    one.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: m6
  prompt: 'You halve the minimum detectable effect of an A/B test. The required sample size:'
  options:
  - Doubles
  - Quadruples
  - Rises by a factor of √2
  - Rises by a factor of 8
  answer: Quadruples
  explanation: Sample size is proportional to 1/δ², so half the effect needs four times the users.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: m7
  prompt: You test 20 independent metrics at α = 0.05 and the change has no real effect on any of them. How
    many do you expect to come out significant?
  options:
  - '0.05'
  - '5'
  - '20'
  - '1'
  answer: '1'
  explanation: Each test has a 5% false positive chance, so 20 × 0.05 = 1 expected. The chance of at least
    one is 1 − 0.95²⁰, about 64%.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: m8
  prompt: 'A team checks its A/B test daily and stops the first time p < 0.05. The main consequence is:'
  options:
  - Lower power and nothing else
  - A false positive rate well above 5%
  - An effect estimate biased towards zero
  - None, provided the sample is large
  answer: A false positive rate well above 5%
  explanation: Every look is another chance to cross the threshold. With 20 looks the false positive rate is
    roughly 25%.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: m9
  prompt: A 50/50 test logs 50,000 users in control and 52,000 in treatment, and a chi-square test on the split
    gives p < 0.001. What should you do?
  options:
  - Reweight the arms and read the results
  - Extend the test until the split evens out
  - Investigate assignment and logging; do not trust the metrics
  - Switch to a one-sided test
  answer: Investigate assignment and logging; do not trust the metrics
  explanation: A sample ratio mismatch means the arms differ in some way other than the treatment. No reweighting
    repairs that.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
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
- id: m15
  prompt: 'A consistent estimator is one that:'
  options:
  - Converges to the true value as the sample grows
  - Equals the true value on average at every sample size
  - Has the smallest variance of any estimator
  - Gives the same value on every sample
  answer: Converges to the true value as the sample grows
  explanation: Consistency is about the limit as n grows. Answer B defines unbiasedness.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: m16
  prompt: Users are randomised, but the analysis treats every page view as an independent observation. What
    is the effect?
  options:
  - Standard errors are too large, so real effects are missed
  - The point estimate is biased towards zero
  - Standard errors are too small, so false positives rise
  - None, if users were randomised correctly
  answer: Standard errors are too small, so false positives rise
  explanation: Page views from one user are correlated, so the effective sample is smaller than the row count.
    Analyse by user or correct the variance.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: n1
  prompt: 'Bagging, as in a random forest, mainly reduces:'
  options:
  - Bias
  - Variance
  - Irreducible noise
  - Training time
  answer: Variance
  explanation: Averaging many high-variance trees trained on different bootstrap samples cancels their individual
    errors. Bias stays about the same.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: n2
  prompt: How does gradient boosting build its trees?
  options:
  - Independently, on bootstrap samples, then averages them
  - One deep tree, then prunes it
  - In sequence, each fitted to the errors of the ensemble so far
  - In parallel, each on a different subset of features
  answer: In sequence, each fitted to the errors of the ensemble so far
  explanation: Boosting is sequential and each tree corrects the current ensemble, which lowers bias. Answer
    A describes bagging.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: n3
  prompt: Which of these models needs its features scaled?
  options:
  - Random forest
  - Gradient-boosted trees
  - k-nearest neighbours
  - A single decision tree
  answer: k-nearest neighbours
  explanation: Nearest neighbours uses distances, so a feature on a larger scale dominates. Tree splits depend
    only on the order of values.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: n4
  prompt: Which penalty can set coefficients exactly to zero?
  options:
  - L1 (lasso)
  - L2 (ridge)
  - Both
  - Neither
  answer: L1 (lasso)
  explanation: The L1 penalty has a corner at zero, so the optimum often sits exactly there. L2 shrinks coefficients
    without zeroing them.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: n5
  prompt: A model scores 99% on training data and 72% on validation data. Which response fits?
  options:
  - Add more features
  - Train for longer
  - Use a more flexible model
  - Regularise, simplify the model or get more data
  answer: Regularise, simplify the model or get more data
  explanation: A large gap between training and validation scores is overfitting, a variance problem. The other
    options add capacity and widen the gap.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: n6
  prompt: A fraud model reaches 99.8% accuracy on data where 0.2% of transactions are fraud. What does that
    tell you?
  options:
  - The model is excellent
  - 'Very little: predicting "not fraud" every time scores the same'
  - The model is overfitting
  - The threshold is too low
  answer: 'Very little: predicting "not fraud" every time scores the same'
  explanation: With 0.2% positives, a model that never flags fraud is 99.8% accurate. Use precision, recall
    and PR-AUC.
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
- id: n8
  prompt: 'A classifier has a ROC-AUC of 0.5. This means:'
  options:
  - Its ranking of positives over negatives is no better than random
  - It classifies half the cases correctly
  - Its precision is 50%
  - It is well calibrated
  answer: Its ranking of positives over negatives is no better than random
  explanation: ROC-AUC is the probability that a random positive is scored above a random negative. 0.5 is
    a coin flip.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: n9
  prompt: 'Compared with k = 50, a k-nearest-neighbours model with k = 1 has:'
  options:
  - Higher bias and higher variance
  - Higher bias and lower variance
  - Lower bias and lower variance
  - Lower bias and higher variance
  answer: Lower bias and higher variance
  explanation: 'With k = 1 the model follows every training point: flexible, so low bias, and unstable, so
    high variance.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: n10
  prompt: You are predicting next month's defaults from several years of loan data. How should you validate?
  options:
  - Shuffled k-fold cross-validation
  - Train on earlier periods and test on later ones
  - Leave-one-out cross-validation
  - A random 80/20 split stratified by outcome
  answer: Train on earlier periods and test on later ones
  explanation: Shuffled splits let the model train on the future and overstate performance. Validate forward
    in time.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: n11
  prompt: Which is a real weakness of a single decision tree?
  options:
  - It needs scaled features
  - It cannot model interactions
  - Small changes in the data can produce a very different tree
  - It cannot use categorical features
  answer: Small changes in the data can produce a very different tree
  explanation: Trees are high-variance learners, which is the reason forests average them. They handle interactions
    and need no scaling.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: n12
  prompt: What does Naive Bayes assume?
  options:
  - Features are independent of each other given the class
  - Features are Normally distributed
  - Classes are balanced
  - The decision boundary is linear
  answer: Features are independent of each other given the class
  explanation: The "naive" part is conditional independence of features given the class. Gaussian Naive Bayes
    adds a Normal assumption, but that is one variant.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: n13
  prompt: You lower the decision threshold of a classifier. What typically happens?
  options:
  - Precision and recall both rise
  - Precision rises and recall falls
  - Neither changes; only accuracy moves
  - Recall rises and precision falls
  answer: Recall rises and precision falls
  explanation: A lower threshold flags more cases, catching more true positives and admitting more false ones.
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
- id: n15
  prompt: For a medium-sized tabular dataset with mixed feature types and non-linear effects, which model is
    usually the strongest default?
  options:
  - k-nearest neighbours
  - Gradient-boosted trees
  - Naive Bayes
  - A linear support vector machine
  answer: Gradient-boosted trees
  explanation: Boosted trees capture non-linear effects and interactions with no scaling or encoding of order,
    and usually lead on tabular data.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: o1
  prompt: You start with a uniform Beta(1, 1) prior on a success rate and observe 3 successes in 3 trials. What
    is the posterior mean?
  options:
  - '1.0'
  - '0.8'
  - '0.75'
  - '0.6'
  answer: '0.8'
  explanation: The posterior is Beta(1 + 3, 1 + 0) = Beta(4, 1), with mean 4/5 = 0.8. The maximum likelihood estimate
    is 1.0, and the prior pulls it back.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: o2
  prompt: What does a 95% credible interval state?
  options:
  - 95% of intervals built this way over repeated samples would cover the parameter
  - 95% of the observations fall inside it
  - The null hypothesis is rejected at the 5% level
  - Given the data and the prior, the parameter lies in it with probability 0.95
  answer: Given the data and the prior, the parameter lies in it with probability 0.95
  explanation: A credible interval is a probability statement about the parameter. The first option is the confidence
    interval, a statement about the procedure.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: o3
  prompt: With a flat prior, the MAP estimate equals which other estimate?
  options:
  - The maximum likelihood estimate
  - The posterior mean
  - The prior mean
  - The posterior median
  answer: The maximum likelihood estimate
  explanation: MAP maximises likelihood × prior. A flat prior is a constant, so the maximum is where the likelihood
    peaks.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: o4
  prompt: As the sample grows, what happens to the influence of the prior on the posterior?
  options:
  - It grows, because the prior is counted once per observation
  - It stays the same
  - It shrinks, because the likelihood dominates
  - It depends only on whether the prior is conjugate
  answer: It shrinks, because the likelihood dominates
  explanation: The likelihood multiplies in once per observation and the prior once in total, so with enough data
    two reasonable priors give nearly the same posterior.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: o5
  prompt: What does the Markov property say?
  options:
  - Every state is visited equally often in the long run
  - The chain always returns to its starting state
  - Transition probabilities change at each step
  - The next state depends only on the current state, not on the path to it
  answer: The next state depends only on the current state, not on the path to it
  explanation: Given the present, the future is independent of the past. That is what lets one transition matrix
    describe the whole process.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: o6
  prompt: In a transition matrix where entry (i, j) is the probability of moving from state i to state j, what must
    hold?
  options:
  - Each column sums to 1
  - Each row sums to 1
  - The diagonal sums to 1
  - The matrix is symmetric
  answer: Each row sums to 1
  explanation: From state i the chain must go somewhere, so row i is a probability distribution. Columns need not
    sum to 1.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: o7
  prompt: What is an absorbing state?
  options:
  - A state the chain can never reach
  - The state with the highest long-run probability
  - A state that, once entered, is never left
  - A state the chain visits on a fixed cycle
  answer: A state that, once entered, is never left
  explanation: Its row in the transition matrix has a 1 on the diagonal. Churned or converted are typical absorbing
    states.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: p1
  prompt: Why standardise features before PCA?
  options:
  - PCA cannot run on features with different units
  - A feature measured on a large scale would dominate the components
  - Standardising makes the components independent of each other
  - It reduces the number of components needed to one
  answer: A feature measured on a large scale would dominate the components
  explanation: PCA finds directions of greatest variance, and variance depends on units. Income in euros would swamp
    age in years.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: p2
  prompt: Which reading of a t-SNE plot is unsafe?
  options:
  - Points that sit close together were similar in the original space
  - The plot shows whether the data have local grouping
  - Different perplexity settings can give different pictures
  - The distance between two clusters shows how different they are
  answer: The distance between two clusters shows how different they are
  explanation: t-SNE keeps local neighbourhoods and distorts global distances and cluster sizes, so gaps between
    clusters carry no reliable meaning.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: p3
  prompt: When is DBSCAN a better choice than k-means?
  options:
  - The clusters have irregular shapes and the data contain noise points
  - The clusters are round and of similar size
  - You know the number of clusters in advance
  - The clusters differ widely in density
  answer: The clusters have irregular shapes and the data contain noise points
  explanation: DBSCAN grows clusters from dense regions, needs no k and labels sparse points as noise. Its weak
    spot is clusters of very different density.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: p4
  prompt: What does a Gaussian mixture model give you that k-means does not?
  options:
  - A guarantee of finding the global optimum
  - Clusters without choosing how many
  - Soft assignments and elliptical clusters
  - Faster fitting on large data
  answer: Soft assignments and elliptical clusters
  explanation: A mixture model gives each point a probability for each component and fits a covariance per component.
    k-means is the special case of hard assignments and equal spherical clusters.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: p5
  prompt: In the EM algorithm for a mixture model, what does the E step compute?
  options:
  - New means and covariances for each component
  - The probability that each component produced each point, under the current parameters
  - The number of components to use
  - The gradient of the likelihood
  answer: The probability that each component produced each point, under the current parameters
  explanation: The E step computes responsibilities. The M step then re-estimates the parameters, weighting each
    point by them. Each round cannot lower the likelihood.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: p6
  prompt: A point has a silhouette score close to 1. What does that mean?
  options:
  - It lies on the border between two clusters
  - It is probably assigned to the wrong cluster
  - The number of clusters is too high
  - It is much closer to its own cluster than to the nearest other cluster
  answer: It is much closer to its own cluster than to the nearest other cluster
  explanation: The silhouette compares the mean distance to the point's own cluster with that to the nearest other
    one. Near 0 is a border point, and negative suggests a wrong assignment.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: q1
  prompt: Why does a neural network need non-linear activation functions?
  options:
  - Without them, any stack of layers collapses to a single linear map
  - They make every layer's output sum to 1
  - They prevent overfitting
  - They make the loss convex
  answer: Without them, any stack of layers collapses to a single linear map
  explanation: A product of matrices is a matrix, so depth adds nothing without a non-linearity between layers.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: q2
  prompt: What goes wrong if every weight in a layer starts at zero?
  options:
  - The gradients explode
  - The loss starts at infinity
  - Every unit computes the same output and gets the same update, so they never differ
  - 'Nothing: the biases break the tie'
  answer: Every unit computes the same output and gets the same update, so they never differ
  explanation: This is the symmetry problem. Random initialisation breaks it, scaled by He for ReLU or Glorot for
    tanh and sigmoid.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: q3
  prompt: Why do deep networks with sigmoid activations suffer from vanishing gradients?
  options:
  - Sigmoid outputs are not centred on zero
  - The sigmoid's derivative is at most 0.25, and backpropagation multiplies one per layer
  - The sigmoid is expensive to compute
  - Sigmoid units die when their input is negative
  answer: The sigmoid's derivative is at most 0.25, and backpropagation multiplies one per layer
  explanation: A product of many factors below 0.25 shrinks towards zero, so early layers barely learn. ReLU has
    a derivative of 1 on its active side.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: q4
  prompt: How does dropout behave at inference time?
  options:
  - It drops units at the same rate as in training
  - It drops units at half the training rate
  - It drops only the units with the smallest weights
  - It is switched off, and all units are used
  answer: It is switched off, and all units are used
  explanation: Dropout is a training-time regulariser. With the usual inverted form, activations are scaled up by
    1/(1 − p) during training so that nothing needs to change at inference.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: q5
  prompt: What does batch normalisation do to a layer's inputs?
  options:
  - Standardises each feature over the mini-batch, then applies a learned scale and shift
  - Clips each value to between 0 and 1
  - Removes the features with the lowest variance
  - Normalises each example to unit length
  answer: Standardises each feature over the mini-batch, then applies a learned scale and shift
  explanation: Stable input distributions let you use higher learning rates. At inference it uses running averages
    from training, not the batch's statistics.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: q6
  prompt: Why do skip connections make very deep networks trainable?
  options:
  - They halve the number of parameters
  - They remove the need for activation functions
  - The gradient has an identity path back, and each block only learns a residual
  - They make every layer the same width
  answer: The gradient has an identity path back, and each block only learns a residual
  explanation: With y = x + F(x), the gradient flows through the addition unchanged, so it reaches early layers.
    A block that has nothing to add can learn F = 0.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: q7
  prompt: What does the Adam optimiser combine?
  options:
  - Weight decay and dropout
  - Momentum and a per-parameter step size from a running average of squared gradients
  - Batch normalisation and gradient clipping
  - A line search and second derivatives
  answer: Momentum and a per-parameter step size from a running average of squared gradients
  explanation: Adam keeps a running mean of gradients (momentum) and of squared gradients (as RMSprop does), with
    a bias correction for the first steps.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: r1
  prompt: What does an inverted index map?
  options:
  - Each document to the terms it contains
  - Each term to the documents that contain it
  - Each query to its cached results
  - Each document to its embedding
  answer: Each term to the documents that contain it
  explanation: A query looks up the posting list of each of its terms, so the search touches only documents that
    share a term with it.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: r2
  prompt: In BM25, what does the parameter b control?
  options:
  - How quickly repeated occurrences of a term stop adding score
  - The weight of rare terms
  - The number of results returned
  - How strongly the score is normalised for document length
  answer: How strongly the score is normalised for document length
  explanation: b = 0 ignores length and b = 1 normalises fully. Term-frequency saturation is the job of k1.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: r3
  prompt: When does embedding search beat keyword search?
  options:
  - The query and the document express the same meaning in different words
  - The query is an exact product code
  - The corpus is small
  - The query contains a rare name
  answer: The query and the document express the same meaning in different words
  explanation: Embeddings match on meaning. Keyword search wins on exact identifiers and rare names, which is why
    hybrid search runs both.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: r4
  prompt: What does reciprocal rank fusion need from each result list?
  options:
  - Scores on a common scale
  - A trained weight for each retriever
  - Only each document's rank
  - Relevance labels
  answer: Only each document's rank
  explanation: RRF sums 1/(k + rank) across lists. Ignoring the scores is what makes it robust when BM25 and cosine
    scores are on different scales.
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
- id: r6
  prompt: A new item has just been added to the catalogue. Why does collaborative filtering struggle with it?
  options:
  - Its embedding is too large
  - It makes the interaction matrix dense
  - It is too similar to existing items
  - It has no interactions yet, so there is no signal to learn from
  answer: It has no interactions yet, so there is no signal to learn from
  explanation: This is the cold-start problem. The usual fixes are content features, popularity fallbacks and some
    exploration.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: r7
  prompt: Why are large recommenders built in two stages?
  options:
  - A cheap retrieval stage cuts millions of items to hundreds, so a costlier ranker can score those
  - The first stage trains the second
  - It removes the need for negative examples
  - One stage handles new users and the other returning users
  answer: A cheap retrieval stage cuts millions of items to hundreds, so a costlier ranker can score those
  explanation: Scoring every item with a heavy model is too slow. Retrieval is tuned for recall and ranking for
    precision at the top.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: r8
  prompt: How does implicit feedback differ from explicit ratings?
  options:
  - It is rarer
  - It is always more accurate
  - 'It has no true negatives: an item never clicked is not known to be disliked'
  - It cannot be used for matrix factorisation
  answer: 'It has no true negatives: an item never clicked is not known to be disliked'
  explanation: Clicks and views are plentiful but only positive. Missing entries are treated as weak negatives or
    sampled, with a confidence weight.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: s1
  prompt: What does the kernel trick let a support vector machine do?
  options:
  - Train without labels
  - Use inner products in a high-dimensional feature space without ever computing the features
  - Skip regularisation
  - Handle missing values
  answer: Use inner products in a high-dimensional feature space without ever computing the features
  explanation: The algorithm only needs inner products between examples, and a kernel returns them directly, so
    a non-linear boundary costs no explicit feature map.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: s2
  prompt: What is the main risk of target encoding a categorical feature?
  options:
  - It creates too many columns
  - It cannot handle unseen categories
  - It removes the order of the categories
  - It leaks the label into the feature unless computed inside each training fold
  answer: It leaks the label into the feature unless computed inside each training fold
  explanation: The encoding is built from the target. Fitted on all rows, each row's own label leaks into its feature,
    most of all for rare categories.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: s3
  prompt: What is the test set for?
  options:
  - One final estimate of performance after every modelling choice is made
  - Choosing hyperparameters
  - Early stopping
  - Selecting features
  answer: One final estimate of performance after every modelling choice is made
  explanation: Any choice made on the test set biases its estimate upwards. Tuning belongs to the validation set
    or to cross-validation.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: s4
  prompt: Why does random search often beat grid search for the same budget?
  options:
  - It evaluates each configuration faster
  - It guarantees the optimum
  - Usually only a few hyperparameters matter, and random search tries more distinct values of each
  - It needs no validation set
  answer: Usually only a few hyperparameters matter, and random search tries more distinct values of each
  explanation: A grid repeats the same few values of the important hyperparameter across every setting of the unimportant
    ones.
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
- id: s8
  prompt: What is Simpson's paradox?
  options:
  - A significant result that does not replicate
  - A correlation produced by a hidden common cause
  - A trend that holds in every segment and reverses in the combined data
  - An effect that fades over time
  answer: A trend that holds in every segment and reverses in the combined data
  explanation: It arises when the segments differ in size between the groups compared, so the mix drives the aggregate.
    Compare within segments.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w1
  prompt: A condition affects 2% of people. A test catches 90% of cases and gives a false positive for 8% of healthy
    people. You test positive. What is the chance you have it, as a percentage to 1 decimal place?
  answer: '18.7'
  explanation: 'Bayes'' rule: P(condition | positive) = 0.02 × 0.90 / (0.02 × 0.90 + 0.98 × 0.08) = 0.018 / 0.0964
    = 0.187. Of 10,000 people, 180 true positives and 784 false positives test positive, and 180 / 964 = 18.7%.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w2
  prompt: You roll a fair die and win its face value. You may reroll up to twice, but must keep the last roll you
    make. What is the game worth, to 2 decimal places?
  answer: '4.67'
  explanation: 'Work backwards. The last roll is worth 3.5. With one reroll left, keep 4, 5 or 6: (4 + 5 + 6)/6
    + (3/6) × 3.5 = 4.25. With two rerolls left, keep only a roll above 4.25, so 5 or 6: (5 + 6)/6 + (4/6) × 4.25
    = 1.833 + 2.833 = 4.67.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w3
  prompt: A user converts with probability 0.3, independently of the others. What is the probability that exactly
    2 of 5 users convert, to 3 decimal places?
  answer: '0.309'
  explanation: 'Binomial: C(5, 2) × 0.3² × 0.7³ = 10 × 0.09 × 0.343 = 0.3087.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w4
  prompt: Support tickets arrive at an average of 4 an hour, independently. What is the probability of none in the
    next 30 minutes, to 3 decimal places?
  answer: '0.135'
  explanation: 'The rate for 30 minutes is 4 × 0.5 = 2. Poisson: P(0) = e^(−2) = 0.1353.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w5
  prompt: Each email is opened with probability 0.05, independently. What is the probability that at least one of
    10 emails is opened, to 3 decimal places?
  answer: '0.401'
  explanation: 'Take the complement: 1 − P(none) = 1 − 0.95¹⁰ = 1 − 0.5987 = 0.4013.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w6
  prompt: X is Binomial with n = 400 and p = 0.2. What is its standard deviation?
  answer: '8'
  explanation: Variance is np(1 − p) = 400 × 0.2 × 0.8 = 64, and the standard deviation is √64 = 8.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w7
  prompt: X has variance 4, Y has variance 9, and their correlation is 0.5. What is the variance of X + Y?
  answer: '19'
  explanation: Var(X + Y) = Var(X) + Var(Y) + 2 Cov(X, Y). The covariance is correlation × sd(X) × sd(Y) = 0.5 ×
    2 × 3 = 3, so the variance is 4 + 9 + 2 × 3 = 19.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w8
  prompt: A sample of 144 orders has a mean of 50 and a standard deviation of 12. What is the upper limit of the
    95% confidence interval for the mean, using z = 1.96, to 2 decimal places?
  answer: '51.96'
  explanation: The standard error is 12 / √144 = 1. The interval is 50 ± 1.96 × 1, so the upper limit is 51.96.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w9
  prompt: 120 of 400 surveyed users say yes. What is the 95% margin of error on that proportion, using z = 1.96,
    to 3 decimal places?
  answer: '0.045'
  explanation: 'The proportion is 0.30. Standard error: √(0.3 × 0.7 / 400) = √0.000525 = 0.0229. Margin: 1.96 ×
    0.0229 = 0.0449.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w10
  prompt: A coin gives 540 heads in 1,000 flips. What is the z statistic for the test that the coin is fair, to
    2 decimal places?
  answer: '2.53'
  explanation: Under the null the standard error is √(0.5 × 0.5 / 1000) = 0.01581. z = (0.54 − 0.50) / 0.01581 =
    2.53, beyond 1.96, so the result is significant at 5%.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w11
  prompt: 36 customers change their spend by a mean of 2.4, with a standard deviation of 6. What is the t statistic
    for the test that the mean change is zero?
  answer: '2.4'
  explanation: The standard error is 6 / √36 = 1, so t = 2.4 / 1 = 2.4 with 35 degrees of freedom.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w12
  prompt: How many respondents does a survey need for a 95% margin of error of 3 percentage points on a proportion,
    in the worst case p = 0.5, using z = 1.96? Round up to a whole person.
  answer: '1068'
  tolerance: 1.0
  explanation: n = z² p(1 − p) / margin² = 1.96² × 0.25 / 0.03² = 0.9604 / 0.0009 = 1,067.1, which rounds up to
    1,068.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w13
  prompt: You run 20 independent tests at a significance level of 0.05 and every null hypothesis is true. What is
    the probability of at least one false positive, to 3 decimal places?
  answer: '0.642'
  explanation: 1 − P(no false positive) = 1 − 0.95²⁰ = 1 − 0.3585 = 0.6415. A Bonferroni correction would test each
    at 0.05 / 20 = 0.0025.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w14
  prompt: Control converts 200 of 2,000 users and treatment 250 of 2,000. What is the z statistic of the two-proportion
    test with a pooled standard error, to 2 decimal places?
  answer: '2.50'
  explanation: 'Rates are 0.100 and 0.125, pooled 450 / 4,000 = 0.1125. Standard error: √(0.1125 × 0.8875 × (1/2000
    + 1/2000)) = 0.00999. z = 0.025 / 0.00999 = 2.50, significant at 5%.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w15
  prompt: The baseline conversion is 20% and you want to detect an absolute lift of 2 points at 5% significance
    and 80% power. Using the rule of thumb n = 16 p(1 − p) / δ², how many users does each arm need?
  answer: '6400'
  explanation: n = 16 × 0.2 × 0.8 / 0.02² = 2.56 / 0.0004 = 6,400 per arm, so 12,800 in total.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w16
  prompt: Fit a least-squares line to the points (1, 2), (2, 3), (3, 5) and (4, 6). What is the slope?
  answer: '1.4'
  explanation: The means are x̄ = 2.5 and ȳ = 4. Sum of (x − x̄)(y − ȳ) = 3 + 0.5 + 0.5 + 3 = 7. Sum of (x − x̄)²
    = 2.25 + 0.25 + 0.25 + 2.25 = 5. Slope = 7 / 5 = 1.4.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w17
  prompt: A regression has a residual sum of squares of 20 and a total sum of squares of 80. What is R²?
  answer: '0.75'
  explanation: 'R² = 1 − SS_res / SS_tot = 1 − 20 / 80 = 0.75: the model explains 75% of the variance.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w18
  prompt: A logistic regression has log-odds −2 + 0.5x. What probability does it predict at x = 6, to 3 decimal
    places?
  answer: '0.731'
  explanation: The log-odds are −2 + 0.5 × 6 = 1. The probability is 1 / (1 + e^(−1)) = 1 / 1.3679 = 0.7311.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w19
  prompt: A logistic regression coefficient is 0.4. By what factor do the odds multiply for a one-unit increase
    in that feature, to 2 decimal places?
  answer: '1.49'
  explanation: A coefficient is a change in log-odds, so the odds multiply by e^0.4 = 1.4918.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w20
  prompt: A classifier has 40 true positives, 10 false positives, 20 false negatives and 930 true negatives. What
    is its F1 score, to 3 decimal places?
  answer: '0.727'
  explanation: Precision = 40 / 50 = 0.8. Recall = 40 / 60 = 0.667. F1 = 2 × 0.8 × 0.667 / (0.8 + 0.667) = 0.7273.
    Accuracy would be 97%, which hides the 20 missed positives.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w21
  prompt: A decision-tree node holds 30 positive and 10 negative examples. What is its Gini impurity?
  answer: '0.375'
  explanation: Gini = 1 − (p₊² + p₋²) = 1 − (0.75² + 0.25²) = 1 − 0.625 = 0.375.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w22
  prompt: You minimise f(w) = w² by gradient descent from w = 3 with a learning rate of 0.1. What is w after one
    step?
  answer: '2.4'
  explanation: The gradient is 2w = 6. The update is w − rate × gradient = 3 − 0.1 × 6 = 2.4.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w23
  prompt: Your prior on a conversion rate is Beta(2, 2). You then see 12 conversions and 8 non-conversions. What
    is the posterior mean, to 3 decimal places?
  answer: '0.583'
  explanation: 'The Beta prior is conjugate to the Binomial: add successes to the first parameter and failures to
    the second, giving Beta(14, 10). Its mean is 14 / 24 = 0.5833. The data alone give 12 / 20 = 0.6, and the prior
    pulls that towards 0.5.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w24
  prompt: A user is active or lapsed each month. An active user stays active with probability 0.9, and a lapsed
    user returns with probability 0.5. A user is active now. What is the probability they are active two months
    from now?
  answer: '0.86'
  explanation: 'Sum over the middle month: active then active is 0.9 × 0.9 = 0.81, lapsed then back is 0.1 × 0.5
    = 0.05. Total 0.86, which is the active-to-active entry of the transition matrix squared.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w25
  prompt: A walker on the points 0 to 6 starts at 3 and moves one step left or right with equal chance. The walk
    stops at 0 or 6. How many steps do you expect?
  answer: '9'
  explanation: Let t(k) be the expected steps from k, with t(0) = t(6) = 0 and t(k) = 1 + ½t(k − 1) + ½t(k + 1).
    The solution is t(k) = k(6 − k), so t(3) = 3 × 3 = 9.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w26
  prompt: A PCA on four standardised features gives eigenvalues 4, 2, 1 and 1. What percentage of the variance do
    the first two components explain?
  answer: '75'
  explanation: Each eigenvalue is the variance along its component. The first two hold (4 + 2) / (4 + 2 + 1 + 1)
    = 6 / 8 = 75%.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w27
  prompt: A convolution with a 3 × 3 filter, stride 2 and padding 1 is applied to a 64 × 64 image. What is the width
    of the output?
  answer: '32'
  explanation: Output size = floor((n + 2p − f) / s) + 1 = floor((64 + 2 − 3) / 2) + 1 = 31 + 1 = 32.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w28
  prompt: A fully connected network has 100 inputs, one hidden layer of 50 units and 10 outputs, with a bias on
    every unit. How many parameters does it have?
  answer: '5560'
  explanation: 'First layer: 100 × 50 weights + 50 biases = 5,050. Second layer: 50 × 10 weights + 10 biases = 510.
    Total 5,560.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w29
  prompt: A classifier outputs the logits 2, 1 and 0. What probability does softmax give the first class, to 3 decimal
    places?
  answer: '0.665'
  explanation: 'Softmax: e² / (e² + e¹ + e⁰) = 7.389 / (7.389 + 2.718 + 1) = 7.389 / 11.107 = 0.6652.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w30
  prompt: A model gives the true class a probability of 0.25. What is the cross-entropy loss for that example, using
    the natural log, to 3 decimal places?
  answer: '1.386'
  explanation: The loss is −ln(probability of the true class) = −ln(0.25) = 1.3863. A probability of 1 would give
    a loss of 0.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w31
  prompt: Across four queries the first relevant result is at rank 1, rank 3, not returned at all, and rank 2. What
    is the mean reciprocal rank, to 3 decimal places?
  answer: '0.458'
  explanation: Reciprocal ranks are 1, 1/3, 0 and 1/2. Their mean is 1.8333 / 4 = 0.4583.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w32
  prompt: A ranked list has graded relevances 3, 2, 0, 1 from the top. With gain equal to the relevance and a discount
    of log2(rank + 1), what is NDCG at 4, to 3 decimal places?
  answer: '0.985'
  explanation: DCG = 3/log2(2) + 2/log2(3) + 0/log2(4) + 1/log2(5) = 3 + 1.262 + 0 + 0.431 = 4.693. The ideal order
    3, 2, 1, 0 gives 3 + 1.262 + 0.5 + 0 = 4.762. NDCG = 4.693 / 4.762 = 0.9854.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w33
  prompt: A term appears 3 times in a document and in 10 of the 1,000 documents in the corpus. With TF-IDF = count
    × log10(N / df), what is its score in that document?
  answer: '6'
  explanation: IDF = log10(1000 / 10) = 2, so TF-IDF = 3 × 2 = 6. A term in every document would score 0.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w34
  prompt: A document is ranked 1st by keyword search and 4th by vector search. What is its reciprocal rank fusion
    score with k = 60, to 3 decimal places?
  answer: '0.032'
  explanation: 'RRF sums 1 / (k + rank) over the lists: 1/61 + 1/64 = 0.01639 + 0.01563 = 0.0320. Only ranks enter,
    so the two score scales never need reconciling.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w35
  prompt: What is the cosine similarity of the vectors (1, 2, 2) and (2, 0, 1), to 3 decimal places?
  answer: '0.596'
  explanation: 'Dot product: 2 + 0 + 2 = 4. Lengths: √9 = 3 and √5 = 2.236. Cosine = 4 / (3 × 2.236) = 0.5963.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w36
  prompt: A forecast has a mean absolute error of 8 on the test period. The seasonal naive forecast has an in-sample
    mean absolute error of 10. What is the MASE?
  answer: '0.8'
  explanation: MASE = model MAE / naive in-sample MAE = 8 / 10 = 0.8. Below 1 means the model beats the naive forecast.
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w37
  prompt: Segment A has 1,000 users converting at 10% and segment B has 3,000 users converting at 2%. What is the
    overall conversion rate, as a percentage?
  answer: '4'
  explanation: 'Conversions: 100 + 60 = 160 of 4,000 users, which is 4%. The overall rate is a weighted mean, so
    a shift in mix towards B lowers it even when neither segment changes, the mechanism behind Simpson''s paradox.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
- id: w38
  prompt: Revenue is users × conversion rate × average order value. Users rise 10%, the conversion rate falls 5%
    and order value is flat. By what percentage does revenue change, to 1 decimal place?
  answer: '4.5'
  explanation: 'Multiply the factors: 1.10 × 0.95 × 1.00 = 1.045, a rise of 4.5%. Adding the percentages would give
    5%, which is close only because the changes are small.'
  lesson: interviewing/rounds/technical-questions/stats-ml-bank
---

Seeded once from `technical-questions/mcq-bank.md` and, for the worked problems (`w1` on), `technical-questions/stats-ml-problems.md`; edit this file directly. Studied at `#/quiz/interviewing/rounds`.
