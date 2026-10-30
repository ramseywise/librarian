---
imported_hash: 9a4457e2700c5a84
title: Design a fraud-detection system (real-time transaction scoring, with a role for GenAI)
summary: fraud-detection-walkthrough · serving · hard
order: 97
kind: reading
section: System design round / Walkthroughs
source: sisyphus/interviewing/rounds/system-design-round/walkthroughs/fraud-detection.md
---

# Design a fraud-detection system (real-time transaction scoring, with a role for GenAI)

`fraud-detection-walkthrough` · serving · hard

## 1. clarify

**Interviewer:** What do you clarify first? Frame the decision, latency, error costs, and labels — and note this is mostly ML, not LLM.

<details><summary>Reference</summary>

Set expectations: the CORE of fraud detection is a classic ML system (real-time scoring
on tabular/behavioral features), with GenAI in a supporting role — don't over-index on
LLMs. Clarify: (1) The DECISION and its actions: allow / block / step-up (2FA) / manual
review, per transaction. (2) LATENCY: inline at checkout means a hard budget — Stripe
Radar returns a verdict in under 100ms. (3) ERROR COSTS: fraud is ~1 in 1000 (severe
class imbalance), and a FALSE POSITIVE (declining a good customer) is very costly —
~1/3 of falsely-declined shoppers won't come back — while a false negative is a direct
fraud loss. That trade-off drives thresholds. (4) LABELS: ground truth (chargebacks/
disputes) arrives DELAYED, weeks later. (5) Adversarial: fraudsters adapt. State
assumptions and confirm. [stripe-ml-primer, stripe-radar-built, evidently-drift]

</details>

## 2. high-level

**Interviewer:** Sketch the architecture: real-time scoring path plus the offline training/feedback loop.

<details><summary>Reference</summary>

Two paths. ONLINE (inline, <100ms): transaction event -> feature service assembles
features (transaction attributes + precomputed streaming aggregates + account history)
-> model scores P(fraud) -> a DECISION layer applies thresholds -> allow / step-up /
review-queue / block -> log. OFFLINE: a feature pipeline computes and stores streaming
aggregates; a training pipeline retrains on labeled history; chargeback/dispute signals
flow back as LABELS. Around it: a case-management / review queue for humans, monitoring
for drift and metrics, and (the GenAI layer) LLM-assisted investigation and explanation.
Real-time features must be served with the SAME logic used in training to avoid
training-serving skew. [stripe-radar-built, bytebytego-stripe, stripe-ml-primer]

</details>

## 3. deep-dive

**Interviewer:** Features & models: what signals and model types do the scoring, and why?

<details><summary>Reference</summary>

Features are the moat. Beyond raw transaction attributes (amount, currency, time), the
predictive power is in NETWORK/streaming AGGREGATES: how many cards have been seen on
this IP, the card's issuing country, the IPs that preceded this one, velocity counts
over time windows — Stripe uses hundreds of such features, most of them cross-merchant
aggregates. Models: gradient-boosted trees (XGBoost/LightGBM) are a strong, fast,
INTERPRETABLE default (SHAP explanations) and often sufficient; Stripe moved to a DNN
with learned EMBEDDINGS for high-cardinality categoricals (merchant, bank, country) for
accuracy. Add GRAPH models (GNNs) when fraud is coordinated — rings and synthetic
identities sharing device/email/IP are 'obvious to graph traversal' but invisible to a
per-transaction model. Note GNN explanations are hard, so build explainability in from
the start. [bytebytego-stripe, stripe-radar-built, fluxforce-gnn]

</details>

## 4. deep-dive

**Interviewer:** Decisioning & thresholds: how do you turn a fraud score into an action given the error costs?

<details><summary>Reference</summary>

The block THRESHOLD is a BUSINESS decision, not a model output — e.g. block when
P(fraud) > 0.7. Because false declines are so costly, don't collapse everything to
allow/block: add a MIDDLE path. Route borderline scores to STEP-UP auth (2FA) or to a
MANUAL REVIEW queue rather than hard-declining — this gains precision without giving up
recall. Tune thresholds per segment (region, merchant, amount) from the cost of a false
positive vs false negative. During a suspected attack you can temporarily LOWER the
threshold to send more transactions to review, trading throughput for safety. [stripe-ml-primer, evidently-drift]

</details>

## 5. deep-dive

**Interviewer:** Class imbalance & feedback loop: how do you train well when fraud is rare and labels are late?

<details><summary>Reference</summary>

Handle IMBALANCE (~1 in 1000): use metrics that respect it (precision/recall, PR-AUC —
not raw accuracy), and techniques like class weighting / resampling. Labels are the
other hard part: ground truth comes from CHARGEBACKS and disputes weeks after the
transaction, so the feedback loop is delayed but automatic — pipe confirmed fraud/
legit outcomes back as labels and CONTINUALLY RETRAIN (Stripe reports ~+0.5pp recall
per month from this). Manual-review decisions also generate labels sooner. Design for
the label delay: don't assume a transaction is legit just because no chargeback has
arrived yet. [stripe-ml-primer, stripe-radar-built]

</details>

## 6. deep-dive

**Interviewer:** Where does GenAI/LLM actually add value here?

<details><summary>Reference</summary>

GenAI is a force-multiplier on the HUMAN side, not the real-time scorer. (1) EXPLAINABLE
alerts: an LLM turns model signals into a plain-language explanation of why a
transaction looks fraudulent, speeding reviewer decisions. (2) DOCUMENT reasoning: OCR +
LLM extraction over invoices/contracts/KYC docs, contextual entity matching (e.g. 'LHR'
= 'London Heathrow'), and spotting cross-document patterns like the same grammatical
errors across supposedly unrelated invoices. (3) AGENTIC investigation: an agent gathers
~90 days of history and device signals, assembles a case narrative, and recommends a
disposition — cutting investigation time from 30+ minutes to under 5, with a human
making the final call. Keep the human in the loop; LLMs assist, they don't decide.
[taktile-llm, unit21-agents]

</details>

## 7. tradeoffs

**Interviewer:** Adversarial drift & monitoring: how do you keep the system effective as fraudsters adapt?

<details><summary>Reference</summary>

Fraud is the textbook CONCEPT-DRIFT problem: the feature-label relationship shifts as
fraudsters change tactics. Because labels arrive DELAYED, you can't wait for accuracy to
drop — monitor INPUT DATA DRIFT (shifts in feature distributions, new patterns) as an
early proxy and retrain on a fast cadence. Keep a champion/challenger setup and A/B new
models. During active attacks, temporarily lower thresholds (more review) while you
adapt. Track live precision/recall as labels mature, false-decline rate, review-queue
volume, and score-distribution shifts. This is a permanent arms race, so retraining
cadence and drift monitoring are part of the design. [evidently-drift, stripe-radar-built]

</details>

## 8. tradeoffs

**Interviewer:** What breaks, how do you detect it, and how does the system degrade gracefully?

<details><summary>Reference</summary>

Name failure modes AND detection. (1) Model staleness / drift: monitor input drift and
maturing precision/recall; retrain frequently. (2) Rising false-decline rate hurting
good customers: monitor decline rate and downstream conversion; loosen thresholds or add
step-up instead of hard block. (3) Latency breach at checkout: monitor p99 of the scoring
path; degrade to a lighter model or cached features, or fail-open/closed by policy
(small amounts fail-open, large fail to review). (4) Feature-pipeline outage or training-
serving skew: monitor feature freshness and parity. (5) Coordinated ring the tabular
model misses: add graph signals and alert on shared-entity clusters. (6) Review-queue
overload: monitor queue depth; auto-decide high-confidence cases. Close with the biggest
risks (false declines, drift) and what you'd measure and improve first. [evidently-drift, stripe-ml-primer, fluxforce-gnn]

</details>

## Sources

- [Stripe — How we built it: Stripe Radar](https://stripe.dev/blog/how-we-built-it-stripe-radar)
- [ByteByteGo — How Stripe Detects Fraudulent Transactions Within 100 ms](https://blog.bytebytego.com/p/how-stripe-detects-fraudulent-transactions)
- [Stripe — A primer on machine learning for fraud protection](https://stripe.com/guides/primer-on-machine-learning-for-fraud-protection)
- [Evidently AI — What is data drift in ML, and how to detect and handle it](https://www.evidentlyai.com/ml-in-production/data-drift)
- [FluxForce — Graph Neural Networks for Fraud Detection Explained](https://www.fluxforce.ai/blog/graph-neural-networks-fraud-detection)
- [Taktile — How LLMs are becoming investigative partners in fintech fraud detection](https://taktile.com/articles/llms-investigative-partners-fraud-detection)
- [Unit21 — AI agents for fraud detection and investigation](https://www.unit21.ai/blog/ai-agents-for-fraud-detection-and-investigation-how-they-work-and-what-to-evaluate)
