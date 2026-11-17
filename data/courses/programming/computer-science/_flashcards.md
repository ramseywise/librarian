---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- programming/computer-science/slides/deck.yaml
cards:
- front: What are the four parts of this lecture, in order?
  back: The lecture moves from reasoning about code to the machine underneath it, and ends on the cost of waiting.
  lesson: programming/computer-science/readme
- front: Name four things this lecture teaches you to do with code.
  back: You will be able to predict what a piece of code costs, check the prediction against a clock, and fix the part that matters.
  lesson: programming/computer-science/readme
- front: How do you estimate an exponent without any theory?
  back: Double `n` and take `log2` of the time ratio, which estimates the exponent. A slope that misses your prediction is telling you something about the machine or the code.
  lesson: programming/computer-science/notes/01-cost-models-and-big-o
- front: Why can't comparison sorting beat n log n?
  back: There are `n!` orderings and each comparison at most halves them, so you need at least `log2(n!)` comparisons, which is `Θ(n log n)`.
  lesson: programming/computer-science/notes/01-cost-models-and-big-o
- front: When is amortised cost the wrong number?
  back: Amortised means the worst-case total over a sequence, shared out. It's right for throughput and wrong for a latency budget, because one operation can still cost `O(n)`.
  lesson: programming/computer-science/notes/01-cost-models-and-big-o
- front: In what order should you optimise?
  back: Measure, stop doing the work, change the algorithm or structure, change the layout, parallelise, and tune constants last.
  lesson: programming/computer-science/notes/01-cost-models-and-big-o
- front: How is a Python dict laid out?
  back: A sparse table of small integers points into a dense, insertion-ordered array of hash, key and value entries. Load is at most 2/3, and collisions probe within the table.
  lesson: programming/computer-science/notes/02-data-structures
- front: Which list and dict habits become outages?
  back: A list is a poor queue, a dict keeps its holes until an insert resizes it, and predictable int hashes can be flooded.
  lesson: programming/computer-science/notes/02-data-structures
- front: What makes BFS, DFS and Dijkstra the same algorithm?
  back: It's one traversal loop, and the bag decides. A stack gives DFS, a queue BFS and a priority queue Dijkstra, which gives wrong answers with no error on negative weights.
  lesson: programming/computer-science/notes/03-algorithm-patterns
- front: Why check a pattern's condition first?
  back: A pattern is a reason not to look at every pair, subset or path. Its condition is what breaks when you apply it from memory, so check that first.
  lesson: programming/computer-science/notes/03-algorithm-patterns
- front: How do you know a greedy rule is correct?
  back: An exchange argument, or at the least agreement with brute force on many small random cases. Only earliest finish was optimal in all 300 random booking cases.
  lesson: programming/computer-science/notes/03-algorithm-patterns
- front: How can two different vectors have distance exactly zero?
  back: Subtracting nearly equal numbers cancels the good digits, so rearrange the formula. To threshold near-duplicates at very small distances on unit vectors, compute the Euclidean form.
  lesson: programming/computer-science/notes/04-numbers-and-memory
- front: Why train in bf16 rather than fp16?
  back: Exponent bits buy range and mantissa bits buy precision. bf16 keeps fp32's range, fp16 overflows past 65,504, and a long sum needs an fp32 accumulator.
  lesson: programming/computer-science/notes/04-numbers-and-memory
- front: What does a random read cost as the working set grows?
  back: Caches work on lines and prefetchers predict patterns, and random access defeats both. It cost 8.5 times sequential at 512 MiB on an Apple M4 Pro, with no change in big-O.
  lesson: programming/computer-science/notes/04-numbers-and-memory
- front: Why can a NumPy loop be slower than a list loop?
  back: Iterating boxes each element into a new Python object, so a NumPy loop costs the most. Speed comes from getting the whole operation out of the Python loop, and memory from getting rid of the objects.
  lesson: programming/computer-science/notes/04-numbers-and-memory
- front: Why does a naive softmax return nan?
  back: Subtract the max before exp and keep probabilities as logs. Pass raw logits to the library's cross-entropy instead of taking log(softmax(x)) yourself.
  lesson: programming/computer-science/notes/04-numbers-and-memory
- front: Why use worker pools, not a process per request?
  back: You can start a thread per task if there's a reason to, but a process per request is a mistake at 32 ms a spawn, which is why worker pools exist.
  lesson: programming/computer-science/notes/05-processes-threads-and-io
- front: Does the GIL make += safe?
  back: No, it's not atomic, so a shared read-modify-write needs a lock. With several locks, take them in one global order, which breaks circular wait.
  lesson: programming/computer-science/notes/05-processes-threads-and-io
- front: What does one blocking call do to an event loop?
  back: An event loop's concurrency only exists at the points where it waits, so one blocking call stops every client on the loop.
  lesson: programming/computer-science/notes/05-processes-threads-and-io
- front: How do you reason about a queue?
  back: In flight equals arrival rate times time in system. Give every queue a bound, so overload makes producers wait or reject and doesn't turn into unbounded memory.
  lesson: programming/computer-science/notes/05-processes-threads-and-io
- front: Which parallelism fits which Python work?
  back: Threads or `asyncio` for waiting, processes for pure Python CPU work with big enough tasks, and vectorising for numeric work.
  lesson: programming/computer-science/notes/05-processes-threads-and-io
- front: Why isn't one recv one message?
  back: TCP is a byte stream, and `recv` boundaries don't relate to `send` boundaries. Every protocol on top has to mark its own, with a length prefix or a delimiter.
  lesson: programming/computer-science/notes/06-networks
- front: Where does a cold HTTPS request spend its time?
  back: Count the round trips and multiply by the RTT. Reuse connections, since a reused one skips the TCP and TLS handshakes, and a warmed-up one skips slow start.
  lesson: programming/computer-science/notes/06-networks
- front: When code is slow, what do you do first, and which do you fix before the other, the algorithm or the constant factor?
  back: Measure first, and fix the algorithm or data structure before you tune the constant factor.
  lesson: programming/computer-science/notes/01-cost-models-and-big-o
- front: What does `f = O(g)` actually say?
  back: There's a constant `c` and a threshold `n0` with `f(n) <= c g(n)` for all `n >= n0`. It's an upper bound on growth, not a claim about speed.
  lesson: programming/computer-science/notes/01-cost-models-and-big-o
- front: O vs Θ?
  back: O is an upper bound, Θ is tight. A linear function is `O(n²)` but not `Θ(n²)`.
  lesson: programming/computer-science/notes/01-cost-models-and-big-o
- front: Why doesn't the log base matter in Big-O?
  back: 'Bases differ by a constant factor. Exponent bases don''t: `4^x` isn''t `O(2^x)`.'
  lesson: programming/computer-science/notes/01-cost-models-and-big-o
- front: Why does a growable array multiply its capacity?
  back: Total copies form a geometric series, so they're `O(n)` overall. Adding a fixed amount gives an arithmetic series, `O(n²)`.
  lesson: programming/computer-science/notes/01-cost-models-and-big-o
- front: What does amortised mean?
  back: Worst-case total over a sequence, divided by its length. There's no probability involved, and a single operation can still be slow.
  lesson: programming/computer-science/notes/01-cost-models-and-big-o
- front: Why can't comparison sorting beat `n log n`?
  back: There are `n!` orderings and each comparison splits them at most in half, so you need at least `log2(n!)`, which is `Θ(n log n)`, comparisons.
  lesson: programming/computer-science/notes/01-cost-models-and-big-o
- front: How do you solve `T(n) = 2T(n/2) + n`?
  back: 'Recursion tree: `log2 n` levels, each costing `n`, so `Θ(n log n)`.'
  lesson: programming/computer-science/notes/01-cost-models-and-big-o
- front: How do you estimate complexity empirically?
  back: Double `n`, and take `log2` of the time ratio. It estimates the exponent.
  lesson: programming/computer-science/notes/01-cost-models-and-big-o
- front: Where do you start with slow code?
  back: Measure. Check if it's on-CPU. Then remove work, change the algorithm, change the layout, parallelise, and tune constants last.
  lesson: programming/computer-science/notes/01-cost-models-and-big-o
- front: What's Amdahl's law?
  back: If a share `p` gets `s` times faster, the gain is `1 / ((1-p) + p/s)`. The part you don't touch sets a ceiling of `1/(1-p)`.
  lesson: programming/computer-science/notes/01-cost-models-and-big-o
- front: Is O(1) always faster than O(n)?
  back: No. Constants and caches decide it on small inputs. Measure at the real size.
  lesson: programming/computer-science/notes/01-cost-models-and-big-o
- front: How does a Python list grow?
  back: It reallocates to about 1.125 × the new size, rounded to a multiple of 4. Amortised constant-time appends follow from the geometric series.
  lesson: programming/computer-science/notes/02-data-structures
- front: Why is `pop(0)` slow?
  back: Everything after it shifts down one slot. Use a `deque`.
  lesson: programming/computer-science/notes/02-data-structures
- front: How does it resolve collisions?
  back: Open addressing with `i = 5i + perturb + 1`, where `perturb` shifts in the hash's high bits.
  lesson: programming/computer-science/notes/02-data-structures
- front: Why can't a deleted slot just be emptied?
  back: A lookup stops at the first empty slot, so later keys on that path would vanish. It's marked `DUMMY`.
  lesson: programming/computer-science/notes/02-data-structures
- front: Does a dict shrink when you delete?
  back: Not on deletion. It resizes on insertion, when usable space runs out, based on the number of live keys.
  lesson: programming/computer-science/notes/02-data-structures
- front: What's hash flooding?
  back: Crafted colliding keys force quadratic insertion. Strings are protected by per-process keyed SipHash; ints aren't randomised.
  lesson: programming/computer-science/notes/02-data-structures
- front: Why does a key-sharing dict help?
  back: Instances of a class share a keys table and store only values.
  lesson: programming/computer-science/notes/02-data-structures
- front: How does Python's sort work?
  back: 'A stable adaptive merge sort: it finds natural runs and merges them by the powersort strategy. Sorted input costs `n - 1` comparisons.'
  lesson: programming/computer-science/notes/02-data-structures
- front: Top k of a stream?
  back: 'A min-heap of size k: `O(n log k)` time and `O(k)` memory.'
  lesson: programming/computer-science/notes/02-data-structures
- front: When is a linked list worth it?
  back: When you hold node references and splice at them, as in an LRU. Otherwise the memory and pointer-chasing cost more.
  lesson: programming/computer-science/notes/02-data-structures
- front: How do you build an LRU cache?
  back: A dict from key to node in a doubly linked list. Both operations are constant time, and `OrderedDict` packages that.
  lesson: programming/computer-science/notes/02-data-structures
- front: How do you find the k most frequent items?
  back: 'Count with a `Counter`, then keep a heap of size k over the distinct keys: n + d log k. `Counter.most_common(k)` does exactly that.'
  lesson: programming/computer-science/notes/02-data-structures
- front: When do two pointers work?
  back: When sorted order lets each comparison discard a candidate permanently. `m + n` steps.
  lesson: programming/computer-science/notes/03-algorithm-patterns
- front: Two pointers or binary search for unequal lists?
  back: 'Binary search each small item: `m log n` beats `m + n` when `m` is far smaller.'
  lesson: programming/computer-science/notes/03-algorithm-patterns
- front: What must a sliding window satisfy?
  back: It can be updated from what enters and leaves, and shrinking moves the answer in a known direction.
  lesson: programming/computer-science/notes/03-algorithm-patterns
- front: Why is a monotonic stack linear despite the nested loop?
  back: Each index is pushed and popped at most once. Count total inner-loop work.
  lesson: programming/computer-science/notes/03-algorithm-patterns
- front: What's binary search on the answer?
  back: Searching for the boundary of a monotonic yes/no test, in `log` tests.
  lesson: programming/computer-science/notes/03-algorithm-patterns
- front: What's the difference between DP and memoised recursion?
  back: The same recurrence, evaluated in a different order. A memo runs only the states you reach; a table has predictable memory use.
  lesson: programming/computer-science/notes/03-algorithm-patterns
- front: Why is knapsack pseudo-polynomial?
  back: Time is `items × budget`, and the budget is a number, so it's exponential in its digits.
  lesson: programming/computer-science/notes/03-algorithm-patterns
- front: 'BFS, DFS, Dijkstra: how do they differ?'
  back: 'The bag: queue, stack, priority queue. All are one traversal loop.'
  lesson: programming/computer-science/notes/03-algorithm-patterns
- front: When does Dijkstra fail?
  back: With negative edge weights. It finalises a node on the assumption that later paths can't be shorter.
  lesson: programming/computer-science/notes/03-algorithm-patterns
- front: How do you detect a cycle in a dependency graph?
  back: In a DFS, an edge to a node still active on the current path.
  lesson: programming/computer-science/notes/03-algorithm-patterns
- front: How do you get a percentile from a large list?
  back: Quickselect gives expected linear time; a sort is simple and, in Python, often close enough.
  lesson: programming/computer-science/notes/03-algorithm-patterns
- front: How do you sample k items from a stream of unknown length?
  back: Reservoir sampling. Keep the first k, then let item i (0-based) replace a random slot with probability k/(i + 1). Every item ends up kept with probability k/n, in one pass and O(k) memory.
  lesson: programming/computer-science/notes/03-algorithm-patterns
- front: How do you compute a square root without a library?
  back: 'Binary search on the answer: the largest x with x·x ≤ n, in log n steps. Or Newton''s method: replace the guess x with (x + a/x)/2, which doubles the correct digits each step once close.'
  lesson: programming/computer-science/notes/03-algorithm-patterns
- front: How do you approach an NP-hard problem in a fixed time?
  back: Build a greedy answer, improve it by local search with restarts, and keep the best so far so you can stop at the deadline. A relaxation gives a bound on how far from optimal you can be.
  lesson: programming/computer-science/notes/03-algorithm-patterns
- front: Why doesn't Python int overflow?
  back: It's a variable-length array of 30-bit digits. It costs memory and speed, and multiplication uses Karatsuba above 70 digits.
  lesson: programming/computer-science/notes/04-numbers-and-memory
- front: Why is `0.1 + 0.2 != 0.3`?
  back: Doubles are `m × 2^e` with 53 bits, and none of those decimals is representable, so each is rounded.
  lesson: programming/computer-science/notes/04-numbers-and-memory
- front: What's an ulp?
  back: The gap between adjacent floats. It scales with the magnitude, so precision is relative.
  lesson: programming/computer-science/notes/04-numbers-and-memory
- front: What's catastrophic cancellation?
  back: Subtracting nearly equal numbers cancels the good leading digits and leaves rounding error. Rearrange the formula.
  lesson: programming/computer-science/notes/04-numbers-and-memory
- front: How do you sum many floats accurately?
  back: '`sum` is compensated since 3.12, `math.fsum` handles hard cases, and NumPy uses partial pairwise summation.'
  lesson: programming/computer-science/notes/04-numbers-and-memory
- front: How should you store money?
  back: As integers in the smallest unit, or `Decimal` constructed from strings.
  lesson: programming/computer-science/notes/04-numbers-and-memory
- front: Why is NaN dangerous in sorting?
  back: Its ordering comparisons are all false, and only `!=` is true, so sort silently gives an unsorted result.
  lesson: programming/computer-science/notes/04-numbers-and-memory
- front: Why do sequential and random access differ?
  back: Caches work on lines and prefetchers predict patterns. Random access defeats both.
  lesson: programming/computer-science/notes/04-numbers-and-memory
- front: Why is a list of floats so much bigger than an array?
  back: 'Pointers plus boxed objects: 32 bytes per value against 8.'
  lesson: programming/computer-science/notes/04-numbers-and-memory
- front: What's a page fault?
  back: The first touch of an unmapped page traps to the kernel, which maps it. That's why allocation looks free until you use it.
  lesson: programming/computer-science/notes/04-numbers-and-memory
- front: What does the TLB do?
  back: It caches address translations, and works because of locality.
  lesson: programming/computer-science/notes/04-numbers-and-memory
- front: 'Process or thread: what''s the difference?'
  back: A process has its own address space. Threads in a process share memory and have separate stacks.
  lesson: programming/computer-science/notes/05-processes-threads-and-io
- front: What's a system call?
  back: A trap into the kernel to do something privileged. Costlier than a function call and much cheaper than a context switch to another process.
  lesson: programming/computer-science/notes/05-processes-threads-and-io
- front: What does `fork` do, and why is `spawn` the default now?
  back: '`fork` copies the process, including held locks but only the calling thread, which is unsafe with threads. `spawn` starts a new interpreter.'
  lesson: programming/computer-science/notes/05-processes-threads-and-io
- front: What's a race condition?
  back: A result that depends on timing, usually from an unprotected read-modify-write.
  lesson: programming/computer-science/notes/05-processes-threads-and-io
- front: Does the GIL make `+=` safe?
  back: No. It's not atomic. It often happens to work, and fails outright on the free-threaded build.
  lesson: programming/computer-science/notes/05-processes-threads-and-io
- front: How do you prevent deadlock?
  back: Take locks in one global order, which breaks circular wait. Add timeouts so a hang becomes an error.
  lesson: programming/computer-science/notes/05-processes-threads-and-io
- front: Polling or blocking?
  back: Blocking gets the same response with no CPU. Polling is only worth it for very short waits.
  lesson: programming/computer-science/notes/05-processes-threads-and-io
- front: How does an event loop work, and what breaks it?
  back: One thread asks the kernel which sockets are ready and handles those. Any blocking call stops every client.
  lesson: programming/computer-science/notes/05-processes-threads-and-io
- front: What's Little's law?
  back: '`L = λW`: in flight = arrival rate × time in system.'
  lesson: programming/computer-science/notes/05-processes-threads-and-io
- front: What's backpressure?
  back: A bound that makes producers wait or reject, so overload doesn't turn into unbounded memory.
  lesson: programming/computer-science/notes/05-processes-threads-and-io
- front: Threads or processes for CPU work in Python?
  back: Processes on the GIL build. Threads for I/O.
  lesson: programming/computer-science/notes/05-processes-threads-and-io
- front: Why does TCP need framing on top?
  back: It's a byte stream. `recv` boundaries don't relate to `send` boundaries.
  lesson: programming/computer-science/notes/06-networks
- front: What's the three-way handshake, and what does it cost?
  back: SYN, SYN-ACK, ACK. It synchronises sequence numbers, and costs 1 RTT before the first request byte.
  lesson: programming/computer-science/notes/06-networks
- front: What's TIME-WAIT?
  back: The closer waits 2 × MSL so old segments can't reach a new connection using those ports. Too many of these exhaust ports.
  lesson: programming/computer-science/notes/06-networks
- front: How's the retransmission timeout set?
  back: '`SRTT + 4 × RTTVAR`, with a floor of 1 s in the RFC, doubling on each timeout.'
  lesson: programming/computer-science/notes/06-networks
- front: What's the bandwidth-delay product?
  back: 'Bytes in flight needed to fill the link: bandwidth × RTT. Throughput is capped at window / RTT.'
  lesson: programming/computer-science/notes/06-networks
- front: What's slow start?
  back: Starting at about 10 segments and doubling each RTT, so small responses take one RTT and large ones several.
  lesson: programming/computer-science/notes/06-networks
- front: Why AIMD?
  back: Adding equally and halving proportionally shrinks the difference between flows, so they converge on a fair share.
  lesson: programming/computer-science/notes/06-networks
- front: Walk through DNS.
  back: Stub to recursive resolver over UDP, with caching by TTL. Falls back to TCP when truncated.
  lesson: programming/computer-science/notes/06-networks
- front: How does HTTP/1.1 find the end of a message?
  back: '`Content-Length`, chunked coding, or connection close.'
  lesson: programming/computer-science/notes/06-networks
- front: HTTP/2 versus HTTP/3?
  back: HTTP/2 multiplexes on one TCP connection, so TCP loss stalls all streams. HTTP/3 uses QUIC, where loss only stalls one stream.
  lesson: programming/computer-science/notes/06-networks
- front: What does TLS 1.3 add to latency?
  back: One RTT on a new connection. The CPU cost is small.
  lesson: programming/computer-science/notes/06-networks
- front: Why is 0-RTT limited?
  back: First-flight data can be replayed, so use it only for idempotent requests.
  lesson: programming/computer-science/notes/06-networks
- front: Which methods are safe to retry?
  back: Idempotent ones, such as GET, PUT and DELETE. POST needs an idempotency key.
  lesson: programming/computer-science/notes/06-networks
---
