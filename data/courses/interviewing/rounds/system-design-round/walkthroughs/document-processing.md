---
imported_hash: 4ea35c2cff2295ee
title: Design a large-scale document-processing pipeline (e.g. extract structured data from payslips, IDs, and references)
summary: document-processing-walkthrough · scaling · hard
order: 96
kind: reading
section: System design round / Walkthroughs
source: sisyphus/interviewing/rounds/system-design-round/walkthroughs/document-processing.md
---

# Design a large-scale document-processing pipeline (e.g. extract structured data from payslips, IDs, and references)

`document-processing-walkthrough` · scaling · hard

## 1. clarify

**Interviewer:** What do you clarify first? Frame document types, accuracy bar, timing, and compliance.

<details><summary>Reference</summary>

Clarify before designing. (1) Document types & variety: which docs (payslips, IDs,
references), which formats (clean PDF vs phone photo vs scan), and how much layout
variation? This drives OCR and extraction difficulty. (2) Fields to extract per type,
and the ACCURACY bar — extracting financial/ID data often needs near-100% correctness,
so a wrong field is costly. (3) Timing: is this REAL-TIME (user waits for a decision)
or can it be ASYNC/batch (process within minutes/hours)? Multipage scans favor async.
(4) Volume & growth: tens of thousands/month now, so design for spiky uploads. (5)
Compliance: these are PII/sensitive documents — encryption, redaction, retention,
access control are first-class. State assumptions and confirm. [igotanoffer, azure-confidence, aws-idp]

</details>

## 2. high-level

**Interviewer:** Sketch the end-to-end pipeline from upload to validated structured record.

<details><summary>Reference</summary>

An EVENT-DRIVEN, staged pipeline. Upload -> object store; the upload event triggers an
orchestrator that creates a TRACKING record (status, doc id) and runs stages: (1)
CLASSIFY the document type (payslip vs ID vs reference). (2) OCR / layout parse to text
plus layout. (3) EXTRACT structured fields to a defined schema (LLM or specialized
extractor). (4) VALIDATE against business rules and confidence thresholds. (5) ROUTE:
high-confidence -> auto-accept and store; low-confidence or rule failures -> human
review queue. Decouple stages with QUEUES so spikes buffer and stages scale
independently, with retries and a dead-letter path. Cross-cutting: PII detection/
redaction, encryption, audit logging, and observability on extraction accuracy and
throughput. [aws-idp, gcp-docai, aws-textract-bedrock]

</details>

## 3. deep-dive

**Interviewer:** OCR & extraction: how do you turn a messy scan into structured fields?

<details><summary>Reference</summary>

Two steps. First DIGITIZE: run OCR / layout parsing to recover text plus positional
layout (tables, key-value regions) — a managed OCR (Textract / Document AI) handles
the pixel-to-text problem across formats. Then EXTRACT: map the OCR output to a defined
output SCHEMA. A robust pattern is OCR -> LLM with the extracted text, running phases:
classify -> extract/summarize -> NORMALIZE into a strict JSON schema (typed key-value
pairs) -> correction pass. Using function-calling / a fixed JSON schema keeps output
machine-parseable. For high-variation docs an LLM generalizes better than brittle
templates; for stable, high-volume forms a specialized form parser may be cheaper. Keep
the source doc + bounding boxes for auditability. [aws-textract-bedrock, gcp-docai]

</details>

## 4. deep-dive

**Interviewer:** Confidence & human-in-the-loop: how do you decide what to auto-accept vs send to a human?

<details><summary>Reference</summary>

Confidence-based ROUTING is the core control. Extractors return a per-FIELD confidence
(0-1); a 0.95 field is likely correct ~19/20 times. Combine the field confidence with
the underlying OCR confidence into a composite score, and set a threshold: above it,
auto-accept; below it (or if a business-rule check fails, e.g. income not a number,
expired ID, name mismatch across documents), route to a HUMAN REVIEW queue. For
financial/ID data, set the bar high (target accuracy near 100%). Add BOUNDED retries: on
failure, re-attempt (e.g. a troubleshooter retry), and after ~3 failures route to human
review; brand-new/unknown document types go to a human first. Reviewer corrections feed
back as labels. [azure-confidence, aws-idp]

</details>

## 5. deep-dive

**Interviewer:** Scale & reliability: real-time vs batch, and how do you survive spikes and failures?

<details><summary>Reference</summary>

Split by latency need. SYNC (near-real-time) ops fit single-page docs where a user
waits; ASYNC ops fit large multipage PDFs/scans — submit a job, get a JobId, and get
notified (e.g. via SNS) on completion. Use async/batch wherever the use case tolerates
it, since it also OPTIMIZES COST. Managed OCR services have per-region TPS and
concurrency QUOTAS, so a burst of uploads will throw limit-exceeded errors — protect
with a QUEUEING architecture (SQS) to smooth spiky traffic, plus retries with
exponential backoff and jitter, IDEMPOTENCY on the tracking id (so a retried document
isn't processed twice), and a dead-letter queue for poison documents. Stages scale
independently behind the queues. [aws-textract-async, aws-textract-quotas, aws-idp]

</details>

## 6. deep-dive

**Interviewer:** PII & compliance: how do you handle sensitive documents responsibly?

<details><summary>Reference</summary>

These documents ARE PII, so compliance is designed in, not bolted on. Detect and
REDACT PII/PHI (e.g. with a dedicated PII/medical entity detector) where downstream
consumers don't need raw values. Encrypt at rest (object store + KMS) and in transit,
enforce least-privilege IAM so only the right roles/services touch raw documents, and
process sensitive extraction in-memory where possible rather than persisting raw PII.
Set RETENTION and deletion policies, and keep an AUDIT log of who/what accessed each
document. Access control on the human-review queue too. [aws-idp]

</details>

## 7. tradeoffs

**Interviewer:** How do you evaluate extraction quality and keep cost in check at scale?

<details><summary>Reference</summary>

Evaluate per field and per document type against a GOLDEN labeled set: field-level
accuracy / precision-recall, plus end-to-end auto-acceptance rate and the human-review
rate (your cost and throughput driver). Watch the reviewer OVERRIDE rate — it tells you
whether your confidence thresholds are calibrated. Cost levers: prefer async/BATCH
processing (cheaper, and non-blocking), cache OCR results so re-processing a document is
free, use a cheaper specialized parser for high-volume stable forms and reserve the LLM
for hard/variable docs, and only pay for the compute you consume (serverless scales to
zero between spikes). Trade-off: pushing thresholds down cuts errors but raises human-
review cost, so tune to the error-cost of the domain. [aws-idp, azure-confidence, igotanoffer]

</details>

## 8. tradeoffs

**Interviewer:** What breaks at scale, how do you detect it, and how does it degrade gracefully?

<details><summary>Reference</summary>

Name failure modes AND detection. (1) OCR/extraction accuracy drift on a new document
format: monitor per-type accuracy and override rate; route unknown formats to humans and
retrain/adjust. (2) Quota / rate-limit throttling under upload spikes: monitor limit-
exceeded errors and queue depth; degrade by buffering in the queue and processing async
rather than failing uploads. (3) Poison documents (corrupt, huge, malicious): timeouts +
dead-letter queue + human triage. (4) Human-review backlog: monitor queue depth; raise
auto-accept thresholds only where safe. (5) PII leak / access violation: alert on
unauthorized access, audit continuously. (6) Duplicate processing: idempotency on the
tracking id. Close with the biggest risks (accuracy on high-stakes fields, PII handling)
and what you'd measure and improve first. [aws-textract-quotas, aws-idp, azure-confidence]

</details>

## Sources

- [AWS — Guidance for Intelligent Document Processing on AWS](https://docs.aws.amazon.com/solutions/intelligent-document-processing-on-aws/)
- [AWS — Processing Documents Asynchronously (Amazon Textract)](https://docs.aws.amazon.com/textract/latest/dg/async.html)
- [AWS — Modifying Default Quotas in Amazon Textract](https://docs.aws.amazon.com/textract/latest/dg/limits-quotas-explained.html)
- [AWS — Intelligent document processing with Textract, Bedrock, and LangChain](https://aws.amazon.com/blogs/machine-learning/intelligent-document-processing-with-amazon-textract-amazon-bedrock-and-langchain/)
- [Azure — Interpret and improve model accuracy and confidence scores (Document Intelligence)](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept/accuracy-confidence?view=doc-intel-4.0.0)
- [Google Cloud — Document AI overview](https://cloud.google.com/document-ai/docs/overview)
- [IGotAnOffer — Generative AI System Design Interview](https://igotanoffer.com/en/advice/generative-ai-system-design-interview)
