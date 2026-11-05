---
generated_by: tools/slides/flashcards.py
decks:
- programming/computer-science/slides/deck.yaml
cards:
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
- front: What does a random read cost as the working set grows?
  back: Caches work on lines and prefetchers predict patterns, and random access defeats both. It cost 8.5 times sequential at 512 MiB on an Apple M4 Pro, with no change in big-O.
  lesson: programming/computer-science/notes/04-numbers-and-memory
- front: Why can a NumPy loop be slower than a list loop?
  back: Iterating boxes each element into a new Python object, so a NumPy loop costs the most. Speed comes from getting the whole operation out of the Python loop, and memory from getting rid of the objects.
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
---
