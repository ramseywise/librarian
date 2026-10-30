---
imported_hash: e881fa3b3665a245
title: Property Search — worked example (answer key)
summary: The docstring says "boost properties cheaper than 500000" but the code penalizes them instead.
order: 38
kind: reading
section: Coding challenge / Examples
source: sisyphus/interviewing/rounds/coding-challenge/examples/property-search.md
---

# Property Search — worked example (answer key)
<!-- markdownlint-disable-file MD025 -->

> **Spoiler.** Full answer key for `drills/coding/problems/property-search/` and bank question 10a.
> Read only after the attempt is scored.
>
> Source: the "AI Property Search" take-home (FastAPI + FAISS), upstream unknown — kept here
> verbatim because the snapshot cannot be re-cloned. The original candidate README is kept at
> `drills/coding/problems/property-search/src/README.md`.

# Interviewer Guide: Property Search Code Test

## Overview

This is a semantic search application for real estate properties using FAISS and sentence transformers. Candidates will:

1. **Debug** two intentional bugs in the codebase
2. **Design** a new filtering feature with trade-off analysis

**Time allocation:**

- Bug finding & fixing: ~30-40 minutes
- Feature design discussion: ~20-30 minutes

---

## Part 1: Bug Hunting

### Setup Instructions for Candidate

1. Create virtualenv: `python -m venv venv && source venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Run server: `uvicorn main:app --reload`
4. Open http://localhost:8000 and search for **"condo"**

### Hint to Give

> *"When you search for 'condo', you should see 5 condos with similar names. Notice anything strange about the ordering? The cheaper properties should be boosted to appear higher in results."*

---

## Bug #1: Price Boost Calculation Penalizes Cheap Properties

### Location

`main.py`, line 35-38

### Buggy Code

```python
def apply_price_boost(score: float, price: float) -> float:
    """Apply price-based boosting to properties cheaper than 500000."""
    price_factor = 1.0 - ((500000 - min(price, 500000)) / 500000) * PRICE_BOOST_FACTOR
    return score * price_factor
```

### Problem

The formula uses **subtraction** which creates **negative factors** for cheap properties:

- $185,000 → factor = 1.0 - 6.3 = **-5.3** (penalized!)
- $475,000 → factor = 1.0 - 0.5 = **0.5** (reduced)
- $1,200,000 → factor = 1.0 - 0 = **1.0** (unchanged)

When multiplied by the semantic score (~0.8):

- Cheap property: `0.8 × -5.3 = -4.24` (negative score!)
- Expensive property: `0.8 × 1.0 = 0.8` (normal score)

The docstring says "boost properties cheaper than 500000" but the code **penalizes** them instead.

### Correct Solution

Change `-` to `+`:

```python
def apply_price_boost(score: float, price: float) -> float:
    """Apply price-based boosting to properties cheaper than 500000."""
    price_factor = 1.0 + ((500000 - min(price, 500000)) / 500000) * PRICE_BOOST_FACTOR
    return score * price_factor
```

Now:

- $185,000 → factor = 1.0 + 6.3 = **7.3** (big boost!)
- $475,000 → factor = 1.0 + 0.5 = **1.5** (small boost)
- $1,200,000 → factor = 1.0 + 0 = **1.0** (no boost)

### Evaluation Criteria

| Score | Criteria |
|-------|----------|
| ⭐⭐⭐ | Identifies the subtraction creates negative factors, provides correct fix |
| ⭐⭐ | Identifies something is wrong with the math, attempts fix |
| ⭐ | Needs significant hints to find the bug |

---

## Bug #2: Index Slicing Skips First Result

### Location

`main.py`, line 99

### Buggy Code

```python
for idx, distance in zip(indices[0][1:], distances[0][1:]):
```

### Problem

The `[1:]` slice **skips the first (best) result** from FAISS. This means the most semantically similar property is never shown.

### Correct Solution

```python
for idx, distance in zip(indices[0], distances[0]):
```

### How Candidates Might Find This

- Notice they're getting 4 results instead of 5 (if `max_results=5`)
- Search for something very specific and notice the best match is missing
- Code review of the search function

### Evaluation Criteria

| Score | Criteria |
|-------|----------|
| ⭐⭐⭐ | Spots the `[1:]` and correctly identifies it skips first result |
| ⭐⭐ | Notices missing results, traces to this line |
| ⭐ | Needs hint: "Count the results - are you getting the expected number?" |

---

## Part 2: Feature Design Discussion

### Prompt for Candidate

> *"We want to add two new filtering capabilities:*
>
> 1. *Filter by size (square footage) - this needs to be added as a new field*
> 2. *Filter by features using natural language (e.g., 'I want a pool and parking')*
>
> *Walk me through how you would approach the feature filtering. Compare an NLP-based approach versus an LLM-based approach."*

---

### Expected Discussion Points

#### Data Model Extension

- Add `size_sqft: int` to property schema
- Decision: Include in embedding text vs. separate structured filter
- Hybrid search consideration: semantic + structured filters

#### NLP Approach (Traditional)

**Implementation:**

- Tokenization, lemmatization, keyword extraction
- Fuzzy matching / synonym dictionaries
- Embedding similarity on feature strings

**Pros:**

- Fast, low latency (~ms)
- No API costs
- Predictable, deterministic
- Works offline
- Easy to debug

**Cons:**

- Brittle to phrasing variations
- Requires manual synonym maintenance
- False positives with ambiguous terms

#### LLM Approach

**Implementation:**

- Send user query + available features list to LLM
- Use function calling / structured output to extract matches
- Cache common queries

**Pros:**

- Handles paraphrasing naturally ("outdoor cooking" → "BBQ Area")
- Understands context and intent
- No synonym dictionary needed
- Adapts to new features automatically

**Cons:**

- Latency (~500ms-2s)
- Cost per query
- Non-deterministic
- Requires fallback for API failures
- Privacy considerations (sending data to external API)

---

### False Positive Scenarios (NLP)

*Ask: "Give me an example where the NLP approach would return a false positive."*

**Strong answers:**

| User Query | NLP Extracts | False Match | Why It's Wrong |
|------------|--------------|-------------|----------------|
| "I want a pool table room" | `pool` | "Swimming Pool" | Different meaning of "pool" |
| "near Madison Square Garden" | `garden` | "Private Garden" | Proper noun, not feature |
| "smart investment property" | `smart` | "Smart Home" | Adjective, not feature |
| "I want to view properties this weekend" | `view` | "City View" | Verb, not noun |
| "property with outdoor fire" | `fire` | "Fireplace" | Wanted fire pit, not indoor fireplace |

---

### Bonus Follow-up Questions

1. **"How would you combine size filtering with semantic search?"**
   - Pre-filter (filter first, then semantic search on subset)
   - Post-filter (semantic search, then filter results)
   - Hybrid index (FAISS with metadata filtering)

2. **"How would you handle 'at least 2000 sqft' vs 'around 2000 sqft'?"**
   - Intent parsing: `>=` vs range query
   - Fuzzy thresholds: ±10% for "around"

3. **"How would you make the LLM approach more deterministic?"**
   - Temperature = 0
   - Structured output / JSON mode
   - Response caching
   - Few-shot examples in prompt

---

### Feature Design Evaluation

| Score | Criteria |
|-------|----------|
| ⭐⭐⭐ | Articulates both approaches clearly, identifies trade-offs, provides concrete false positive examples, suggests hybrid approach |
| ⭐⭐ | Understands the approaches, identifies some trade-offs, needs prompting for edge cases |
| ⭐ | Basic understanding, struggles with trade-off analysis |

---

## Overall Scoring

| Area | Weight | Notes |
|------|--------|-------|
| Bug #1 (Price Boost) | 30% | Core algorithmic debugging |
| Bug #2 (Index Slice) | 25% | Code review skills |
| Feature Design | 30% | System design thinking |
| Communication | 15% | Explaining thought process |

---

## Red Flags 🚩

- Changes code without understanding what it does
- Doesn't test fixes before moving on
- Can't explain trade-offs between approaches
- Dismisses edge cases as unimportant
- Struggles to read/understand Python code

## Green Flags ✅

- Methodically traces through code
- Tests fixes with specific queries
- Proactively identifies additional edge cases
- Asks clarifying questions about requirements
- Considers production concerns (cost, latency, reliability)
