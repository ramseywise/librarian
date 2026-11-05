---
generated_by: tools/slides/flashcards.py
decks:
- ai-engineering/08-multimodal-engineering/slides/deck.yaml
cards:
- front: How does an image spend context, and what makes it cost more?
  back: Images cost context as text does, and cost grows with area.
  lesson: ai-engineering/08-multimodal-engineering/notes/01-image-input
- front: How should you read the resolution and encoder-size results for your own task?
  back: Read this as a ranking of levers for research models, not a forecast for your task.
  lesson: ai-engineering/08-multimodal-engineering/notes/01-image-input
- front: What should you log and monitor so a downscale cannot silently erase small text?
  back: Log the pixel height of the smallest text you need, and monitor it like token count.
  lesson: ai-engineering/08-multimodal-engineering/notes/01-image-input
- front: What cheap signal tells you to route a document to a person?
  back: Disagreement between the page reading and the crop is a cheap signal to route to a person.
  lesson: ai-engineering/08-multimodal-engineering/notes/01-image-input
- front: Why route per page and log the route?
  back: Route per page and log the route, so a shift in accuracy points at a route and a document family.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: Which pages should go to the expensive route?
  back: Send only the hard pages to the expensive route.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: Why set per-page timeouts on CPU document parsing?
  back: At the 95th percentile a CPU page takes about twenty times the median, so set per-page timeouts.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: What do you do when an arithmetic check fails on an extracted document?
  back: A failed check says something is wrong, then you retry with a crop, try a second route, or ask a person.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: Which score picks an engine, and which decides whether you can ship?
  back: Use edit distance to pick an engine, and field F1 to decide whether you can ship.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: What do the scores from the runnable pipeline test, and what do they not?
  back: The documents are generated and no vision model ran, so treat these scores as a test of the code.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: When do token positions matter for extraction?
  back: Positions matter when a label sits over its value, and our two-column layout turned out harmless.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: What does a field that the arithmetic can't reach need?
  back: Each field the arithmetic can't reach needs a check of its own.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: When is a failed check worth the most, and why?
  back: People are the cost, so a failed check is worth most when it triggers another attempt first.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: Before you label more data for a fine-tuned vision-language model, what should you check, and why?
  back: Read one batch's labels, look at the page as the model gets it, and score after every conversion before adding data.
  lesson: ai-engineering/08-multimodal-engineering/notes/02b-fine-tuning-a-vision-language-model
- front: What did swapping BM25 for a neural embedder show about the text routes?
  back: Swapping BM25 for a neural embedder barely moved the text routes, so ingestion was the bottleneck here.
  lesson: ai-engineering/08-multimodal-engineering/notes/03-multimodal-rag
- front: What does late interaction find on a dense page that a single vector misses?
  back: Late interaction finds a small region on a dense page, where a single vector finds the vague page.
  lesson: ai-engineering/08-multimodal-engineering/notes/03-multimodal-rag
- front: Why narrow to a few hundred pages before reranking with patches?
  back: Recall at a few hundred is a much easier job than precision at five.
  lesson: ai-engineering/08-multimodal-engineering/notes/03-multimodal-rag
- front: What usually decides for a cascade in a regulated use?
  back: For a regulated use such as disputing a charge, audit and tool calling usually decide for the cascade.
  lesson: ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents
- front: How do you budget voice latency, and what do you test on real callers?
  back: Write the budget per stage at the 95th percentile, then test the VAD window on real callers.
  lesson: ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents
- front: What goes wrong if voice agent history keeps text the caller never heard?
  back: Otherwise the agent believes it read out a policy that the caller never heard.
  lesson: ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents
- front: How do you protect against a low WER hiding a wrong value you will act on?
  back: Read back any value you will act on, and confirm it before calling the tool.
  lesson: ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents
- front: How does a sampler's error behave as you reduce the number of steps?
  back: Error stays low across a wide range of steps, then rises sharply at very few.
  lesson: ai-engineering/08-multimodal-engineering/notes/05-how-image-generators-work
- front: Why test both generation and understanding after a model change?
  back: A change aimed at generation can harm understanding, so test both.
  lesson: ai-engineering/08-multimodal-engineering/notes/05-how-image-generators-work
- front: Why log every control with every generated image?
  back: Log every control with every image, because a hosted model can be withdrawn.
  lesson: ai-engineering/08-multimodal-engineering/notes/06-generating-images-and-video
- front: When do you find out that an image's record is incomplete, if you did not plan for it?
  back: When someone later asks for a variation, it is too late to find out the record is incomplete.
  lesson: ai-engineering/08-multimodal-engineering/notes/06-generating-images-and-video
- front: Which negatives make a good test for a vision model on invoices?
  back: A random negative tests very little, so choose absent objects that a real invoice could have.
  lesson: ai-engineering/08-multimodal-engineering/notes/07-evaluating-multimodal-systems
- front: Why report both the plain and the CircularEval score?
  back: Report both scores, since even a competent model loses some under rotation.
  lesson: ai-engineering/08-multimodal-engineering/notes/07-evaluating-multimodal-systems
- front: What do separate scores per stage let a regression do?
  back: Separate scores let a regression point at the stage that caused it.
  lesson: ai-engineering/08-multimodal-engineering/notes/07-evaluating-multimodal-systems
- front: Almost nothing in a multimodal system raises an error, so what must every stage have?
  back: Almost nothing here raises an error, so every chapter ends with a check you must add.
  lesson: ai-engineering/08-multimodal-engineering/notes/07-evaluating-multimodal-systems
- front: Where next
  back: Next we treat every one of these inputs as something an attacker can write.
  lesson: ai-engineering/08-multimodal-engineering/notes/07-evaluating-multimodal-systems
---
