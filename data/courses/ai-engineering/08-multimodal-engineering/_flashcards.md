---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- ai-engineering/08-multimodal-engineering/slides/deck.yaml
cards:
- front: What are the six failures this lecture walks through, in order?
  back: The parts follow the notes, from what the model receives, through retrieval and speech and generation, to the tests that keep all of it honest.
  lesson: ai-engineering/08-multimodal-engineering/readme
- front: Name four things this lecture teaches you to do with images, documents, audio and generated pictures.
  back: You will be able to find the silent failure in each kind of input and name the check that catches it.
  lesson: ai-engineering/08-multimodal-engineering/readme
- front: How does an image spend context, and what makes it cost more?
  back: Images cost context as text does, and cost grows with area.
  lesson: ai-engineering/08-multimodal-engineering/notes/01-image-input
- front: How should you read the resolution and encoder-size results for your own task?
  back: Resolution moved the score more than encoder size, but treat it as a ranking of levers for research models, not a forecast for your task.
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
  back: Send only pages with no text layer, tables or formulas, or a failed check to the expensive route.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: Why set per-page timeouts on CPU document parsing?
  back: At the 95th percentile a CPU page takes about twenty times the median, so set per-page timeouts.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: What do you do when an arithmetic check fails on an extracted document?
  back: 'A failed check means something is wrong: retry with a crop, try a second route, or ask a person.'
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
  back: A vendor name or IBAN needs its own check, such as IBAN check digits or a supplier list.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: When is a failed check worth the most, and why?
  back: People are the cost, so a failed check is worth most when it triggers another attempt first.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: Before you label more data for a fine-tuned vision-language model, what should you check, and why?
  back: Before adding data, check the labels, the pixels the model sees, and the score after saving.
  lesson: ai-engineering/08-multimodal-engineering/notes/02b-fine-tuning-a-vision-language-model
- front: What did swapping BM25 for a neural embedder show about the text routes?
  back: Swapping BM25 for a neural embedder barely moved the text routes, so ingestion was the bottleneck here.
  lesson: ai-engineering/08-multimodal-engineering/notes/03-multimodal-rag
- front: What does late interaction find on a dense page that a single vector misses?
  back: Late interaction finds a small region on a dense page, where a single vector finds the vague page.
  lesson: ai-engineering/08-multimodal-engineering/notes/03-multimodal-rag
- front: Why narrow to a few hundred pages before reranking with patches?
  back: Scanning every patch of every page is too costly, so narrow with a cheap first stage and rerank a few hundred pages with patches.
  lesson: ai-engineering/08-multimodal-engineering/notes/03-multimodal-rag
- front: What are three mistakes that make a multimodal retrieval system miss the answer?
  back: Check that gold answers survive parsing and that the eval set holds visual questions, because tuning cannot recover what was never indexed and text-only queries hide the gap.
  lesson: ai-engineering/08-multimodal-engineering/notes/03-multimodal-rag
- front: What usually decides for a cascade in a regulated use?
  back: For a regulated use such as disputing a charge, audit and tool calling usually decide for the cascade.
  lesson: ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents
- front: How do you budget voice latency, and what do you test on real callers?
  back: Write the budget per stage at the 95th percentile, then test the VAD window on real callers.
  lesson: ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents
- front: What goes wrong if voice agent history keeps text the caller never heard?
  back: If history keeps unspoken text, the agent believes it read out a policy the caller never heard, so keep only what was played.
  lesson: ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents
- front: How do you protect against a low WER hiding a wrong value you will act on?
  back: Read back any value you will act on, and confirm it before calling the tool.
  lesson: ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents
- front: Why test both generation and understanding after a model change?
  back: A change aimed at generation can harm understanding, so test both.
  lesson: ai-engineering/08-multimodal-engineering/notes/05-how-image-generators-work
- front: How does a sampler's error behave as you reduce the number of steps?
  back: Error stays low across a wide range of steps, then rises sharply at very few.
  lesson: ai-engineering/08-multimodal-engineering/notes/05-how-image-generators-work
- front: Why log every control with every generated image?
  back: Log every control with every image, because a hosted model can be withdrawn.
  lesson: ai-engineering/08-multimodal-engineering/notes/06-generating-images-and-video
- front: When do you find out that an image's record is incomplete, if you did not plan for it?
  back: When someone later asks for a variation, it is too late to find out the record is incomplete.
  lesson: ai-engineering/08-multimodal-engineering/notes/06-generating-images-and-video
- front: How do you choose between a mask, a control image and img2img to fix a generated image?
  back: Edit with a mask when one region changes, a control image to fix structure, and img2img to restyle.
  lesson: ai-engineering/08-multimodal-engineering/notes/06b-editing-and-customizing-images
- front: Why can't training a ControlNet damage the base model?
  back: Zero-initialised connections leave the base model's output unchanged at step 0, so training the control copy can't damage it.
  lesson: ai-engineering/08-multimodal-engineering/notes/06b-editing-and-customizing-images
- front: What do you do before and after training a customized image model?
  back: Try a reference image or a control image first, then train one concept per model and record the base and adapter hashes.
  lesson: ai-engineering/08-multimodal-engineering/notes/06b-editing-and-customizing-images
- front: Which negatives make a good test for a vision model on invoices?
  back: A random negative tests very little, so choose absent objects that a real invoice could have.
  lesson: ai-engineering/08-multimodal-engineering/notes/07-evaluating-multimodal-systems
- front: Why report both the plain and the CircularEval score?
  back: Report both scores, since even a competent model loses some under rotation.
  lesson: ai-engineering/08-multimodal-engineering/notes/07-evaluating-multimodal-systems
- front: What do separate scores per stage let a regression do?
  back: Separate scores let a regression point at the stage that caused it.
  lesson: ai-engineering/08-multimodal-engineering/notes/07-evaluating-multimodal-systems
- front: What are three mistakes that make a multimodal test flatter the model?
  back: Keep the answer out of the question, report scores per skill and group, and let any judge see the image, or the test measures reading rather than seeing.
  lesson: ai-engineering/08-multimodal-engineering/notes/07-evaluating-multimodal-systems
- front: Almost nothing in a multimodal system raises an error, so what must every stage have?
  back: Almost nothing here raises an error, so every chapter ends with a check you must add.
  lesson: ai-engineering/08-multimodal-engineering/notes/07-evaluating-multimodal-systems
- front: What do we take up after multimodal engineering?
  back: Next we treat every one of these inputs as something an attacker can write.
  lesson: ai-engineering/08-multimodal-engineering/notes/07-evaluating-multimodal-systems
- front: Why does a VLM misread text at low resolution even when the prompt is perfect?
  back: The encoder only receives the resized pixels. If a digit is a pixel or two tall after preprocessing, the distinguishing information no longer exists, and the language model fills the gap with a plausible value.
  lesson: ai-engineering/08-multimodal-engineering/notes/01-image-input
- front: Which lever matters most for VLM quality when building one?
  back: Resolution and visual token count, ahead of encoder size or connector design, in MM1's systematic study. Treat it as a ranking of levers in that setup.
  lesson: ai-engineering/08-multimodal-engineering/notes/01-image-input
- front: What are three ways to raise effective resolution without paying for every patch?
  back: Keep the token count and refine with a high-resolution encoder (Mini-Gemini), tile the image (DeepSeek-VL2), or encode at dynamic resolution up to a token budget (Phi-4-reasoning-vision).
  lesson: ai-engineering/08-multimodal-engineering/notes/01-image-input
- front: How would you defend against rotated uploads?
  back: Apply EXIF correction first, add an orientation classifier for scans with no EXIF, and include rotated samples in the eval set, since a rotation can cost tens of points on OCR benchmarks.
  lesson: ai-engineering/08-multimodal-engineering/notes/01-image-input
- front: Why ask for bounding boxes?
  back: They turn an unverifiable answer into a checkable one. You can validate bounds, crop the region and reread it, and show a reviewer the evidence.
  lesson: ai-engineering/08-multimodal-engineering/notes/01-image-input
- front: When would you separate a perceiver from a reasoner?
  back: When your best reasoning model has weak or no vision, or vision pricing dominates. A small VLM describes on demand and the strong model asks follow-up questions.
  lesson: ai-engineering/08-multimodal-engineering/notes/01-image-input
- front: Why not extract the text layer and send it to an LLM?
  back: Text layers give glyphs in drawing order. Columns interleave, tables flatten, and scans have no text at all. Layout, reading order and table structure must be recovered.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: What does a pipeline give you that an end-to-end model doesn't?
  back: Inspectable stages, a known cost per stage, and the ability to swap one part. The price is that an error in an early stage is passed downstream.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: What failure is specific to end-to-end document decoders?
  back: Repetition loops, particularly on pages outside the training domain. Nougat measured 1.5% of its in-domain test pages. Detect and reroute them.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: How do you verify an extraction without ground truth?
  back: 'Use redundancy in the document: arithmetic, cross-field rules, a second independent extraction, master data, and requiring each value to appear in the OCR text.'
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: Edit distance or field F1?
  back: Both, for different decisions. Edit distance compares transcript engines. Field F1 reflects business correctness because one wrong character fails the field.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: What costs most in a document pipeline?
  back: People. In our run review was thousands of times dearer than compute, so a retry that cut review from 25.6% to 1.1% of documents was the best value.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: Can a general VLM read an engineering drawing?
  back: Numbers better than symbols. On seven drawings, GPT-4o's dimension recall was 92.68 counting repeats as matches, and its recall on feature control frames, present in three of them, was 0. The evidence is small and dates fast, so test on your own drawings and score per field.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: Why route per page?
  back: Page cost varies by more than an order of magnitude. Skipping OCR and table models on simple pages saves most of the compute, and logging the route tells you what changed when accuracy moves.
  lesson: ai-engineering/08-multimodal-engineering/notes/02-document-understanding
- front: When do you fine-tune a VLM?
  back: When prompts and a route with OCR fail or don't fit your limits, such as pages that must stay local on a small model. On our generated invoices, the frozen model scored about 0.02 and LoRA reached 0.93.
  lesson: ai-engineering/08-multimodal-engineering/notes/02b-fine-tuning-a-vision-language-model
- front: What masks do you use in the labels?
  back: Padding and image tokens at least, and usually the whole prompt. Leaving image tokens in cost about 0.10 here, with no error. TRL's default depends on your dataset's columns.
  lesson: ai-engineering/08-multimodal-engineering/notes/02b-fine-tuning-a-vision-language-model
- front: What does `target_modules` reach in a VLM?
  back: A list matches by name ending, so it wraps both towers. A string is a regex. Print the trainable names. Vision adapters helped here, on one generated font.
  lesson: ai-engineering/08-multimodal-engineering/notes/02b-fine-tuning-a-vision-language-model
- front: How do you save memory?
  back: Lower the longest edge first, if the text survives it. Each 512 tile adds 64 image tokens. 4-bit cut weights by 4.7× here but total training memory by only about 10%.
  lesson: ai-engineering/08-multimodal-engineering/notes/02b-fine-tuning-a-vision-language-model
- front: Can you merge a LoRA into a 4-bit model?
  back: Don't assume so. In ours the update was about 0.2% of the weight, 16 levels couldn't hold it, and accuracy went from 0.91 to 0. Merge into a float base, or keep the adapter.
  lesson: ai-engineering/08-multimodal-engineering/notes/02b-fine-tuning-a-vision-language-model
- front: How do you evaluate one?
  back: Generate and score per field, on held-out layouts and vendors. Report parse rate and values found beside exact match. Loss kept falling here after accuracy stopped rising.
  lesson: ai-engineering/08-multimodal-engineering/notes/02b-fine-tuning-a-vision-language-model
- front: A field fails. More data?
  back: Check the pixels first. Small print went from 0.40 to 0.50 by retraining, and to 0.97 by doubling the edge, at about 3.4× the memory.
  lesson: ai-engineering/08-multimodal-engineering/notes/02b-fine-tuning-a-vision-language-model
- front: What's the worst thing about synthetic data?
  back: It proves the pipeline, not the accuracy. Labels are perfect and the variation is what you wrote. Vendor accuracy fell from 0.90 to 0.51 on words outside the training list.
  lesson: ai-engineering/08-multimodal-engineering/notes/02b-fine-tuning-a-vision-language-model
- front: What is the first thing to check when a chart's answer is never retrieved?
  back: Whether ingestion kept it. Parsers often reduce charts to stray labels, so no retriever can find them. Inspect the indexed text for known answers.
  lesson: ai-engineering/08-multimodal-engineering/notes/03-multimodal-rag
- front: Summaries or image embeddings?
  back: Summaries reuse text infrastructure and beat single CLIP vectors in Riedler and Langer's test, at a per-element vision cost. Patch-level embeddings beat summaries on visually rich pages in ColPali's benchmark, at a storage cost.
  lesson: ai-engineering/08-multimodal-engineering/notes/03-multimodal-rag
- front: What is MaxSim?
  back: For each query token, take the highest similarity across all document vectors, then sum over query tokens. It rewards a sharp local match, and averaging can't erase it.
  lesson: ai-engineering/08-multimodal-engineering/notes/03-multimodal-rag
- front: How do you make late interaction affordable?
  back: Pool neighbouring patches, quantise values, and use a cheap first stage so that late interaction only reranks a few hundred candidates.
  lesson: ai-engineering/08-multimodal-engineering/notes/03-multimodal-rag
- front: How do you tell if retrieval or reading is the problem?
  back: Hand the reader the gold page. Its score is an upper bound. The gap to your full system is retrieval's cost, and the gap from there to perfect is the reader's.
  lesson: ai-engineering/08-multimodal-engineering/notes/03-multimodal-rag
- front: Why did swapping BM25 for a neural embedder barely help in ColPali's baselines?
  back: The ingestion step had already lost the visual information, so a better text embedder only reads the same incomplete text better.
  lesson: ai-engineering/08-multimodal-engineering/notes/03-multimodal-rag
- front: Cascade or speech-to-speech for a banking agent?
  back: Usually a cascade with streaming, because of the transcript for audit, standard guardrails and mature tool calling, accepting more latency. Revisit as speech-to-speech models improve on those points.
  lesson: ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents
- front: Where does cascade latency go?
  back: End-of-speech detection, the time to the LLM's first token, and the first TTS audio. Streaming every stage helps more than a faster model, since only the first audio matters for perceived speed.
  lesson: ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents
- front: What is a neural codec's role in a voice model?
  back: It turns audio into a compact sequence of discrete tokens a language model can predict, at low bit rates. Its frame length sets a floor on reaction time.
  lesson: ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents
- front: Why is WER not enough?
  back: It weights every word equally, so a wrong amount looks like a wrong article. Add recall on critical terms, and break results down by accent and channel.
  lesson: ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents
- front: How should a text normaliser be handled?
  back: Use one shared normaliser for all compared systems and report it. It can change WER by a large margin, and it can be fit, even by accident, to one model's habits.
  lesson: ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents
- front: What must happen on barge-in?
  back: Stop playback, drop the unspoken text, record only what was heard, and preserve any tool result already obtained, so that the model's context matches reality.
  lesson: ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents
- front: How do you set the silence window?
  back: By dialogue state and by measurement. It trades cut-off callers against added wait, one value can't serve open talk and read-out digits, and a short window also wastes LLM calls on false endpoints.
  lesson: ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents
- front: Does cancelling a task on barge-in cancel the tool call?
  back: It shouldn't, and it can't undo the server anyway. Cancel the turn's tasks, let the call own the tool, record the outcome, and use an idempotency key against retries.
  lesson: ai-engineering/08-multimodal-engineering/notes/04-speech-and-voice-agents
- front: What is a diffusion model trained to do?
  back: Predict the noise added to an image at a random step, conditioned on the caption. Sampling starts from noise and applies that prediction repeatedly.
  lesson: ai-engineering/08-multimodal-engineering/notes/05-how-image-generators-work
- front: Why did DDIM cut steps without retraining?
  back: It changes only the sampler. It uses the same trained model with a deterministic path that can skip steps.
  lesson: ai-engineering/08-multimodal-engineering/notes/05-how-image-generators-work
- front: What does latent diffusion buy?
  back: Denoising in a compressed space cuts compute enough to run on a consumer GPU. The cost is the decoder's limit on fine pixel-level detail.
  lesson: ai-engineering/08-multimodal-engineering/notes/05-how-image-generators-work
- front: What does the guidance scale do mathematically?
  back: It extrapolates from the unconditional prediction through the conditional one. High values increase prompt adherence and reduce variety, eventually distorting the output.
  lesson: ai-engineering/08-multimodal-engineering/notes/05-how-image-generators-work
- front: Why does an image reproduce only with the same seed and sampler?
  back: The seed sets the starting noise. Each sampler then follows a different path from it, and stochastic samplers add further noise.
  lesson: ai-engineering/08-multimodal-engineering/notes/05-how-image-generators-work
- front: When would you consider a GAN or a masked decoder over diffusion?
  back: When latency dominates and the domain is narrow, such as aligned faces, or for fast drafts. General-purpose quality and text binding favour diffusion and token models.
  lesson: ai-engineering/08-multimodal-engineering/notes/05-how-image-generators-work
- front: Which settings must you store to reproduce an image?
  back: Model and exact weights, seed, sampler, steps, guidance, size, prompt and negative prompt, plus any rewritten prompt or extra weights and control inputs.
  lesson: ai-engineering/08-multimodal-engineering/notes/06-generating-images-and-video
- front: Why do ancestral samplers break reproducibility work?
  back: They inject fresh noise at each step, so the image never converges and small changes in settings move it unpredictably.
  lesson: ai-engineering/08-multimodal-engineering/notes/06-generating-images-and-video
- front: API or self-hosted?
  back: API for low volume and fast start, self-hosted for control, privacy, pinned weights and high volume. A hosted model is a dependency that can be withdrawn.
  lesson: ai-engineering/08-multimodal-engineering/notes/06-generating-images-and-video
- front: How do you evaluate generated images?
  back: Combine a distribution metric such as FID for model comparison, CLIP-style scores for triage, and structured prompt-adherence checks and human review for what users will actually see.
  lesson: ai-engineering/08-multimodal-engineering/notes/06-generating-images-and-video
- front: 'Mask, control image or img2img: how do you choose?'
  back: Mask when one region changes, a control image to fix structure such as pose or layout, and img2img to restyle while keeping overall composition.
  lesson: ai-engineering/08-multimodal-engineering/notes/06b-editing-and-customizing-images
- front: When is a custom model worth it?
  back: When prompting and reference images can't name the subject, such as a specific product or a house style, and the volume repays the training and governance cost.
  lesson: ai-engineering/08-multimodal-engineering/notes/06b-editing-and-customizing-images
- front: Why can a VLM score well without seeing?
  back: Language priors and dataset imbalance let it guess. Paired images with different answers remove that advantage.
  lesson: ai-engineering/08-multimodal-engineering/notes/07-evaluating-multimodal-systems
- front: What does CircularEval catch?
  back: Preference for an option position or a lucky guess. Each question is asked once per rotation, and all must pass.
  lesson: ai-engineering/08-multimodal-engineering/notes/07-evaluating-multimodal-systems
- front: How would you measure hallucination in a document model?
  back: Ask yes/no questions about present and absent items, using negatives that are plausible for the document, and track accuracy, precision, recall and the yes-ratio.
  lesson: ai-engineering/08-multimodal-engineering/notes/07-evaluating-multimodal-systems
- front: What are FID's limits?
  back: It compares distributions, not individual images, it is biased at small sample sizes, and it depends on the feature extractor. Compare only at equal sample counts.
  lesson: ai-engineering/08-multimodal-engineering/notes/07-evaluating-multimodal-systems
- front: How do you localise a regression in a multimodal RAG system?
  back: Score each stage separately, and run the reader with the gold page so you can split the error between retrieval and reading.
  lesson: ai-engineering/08-multimodal-engineering/notes/07-evaluating-multimodal-systems
- front: Can you use a language model as a judge for image answers?
  back: Yes, if it can see the same page, and if you measure its agreement with human labels on a sample by error type. It remains an approximation.
  lesson: ai-engineering/08-multimodal-engineering/notes/07-evaluating-multimodal-systems
---
