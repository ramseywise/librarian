---
title: Private Variant Testing on Arena Leaderboards
tags: [eval, concept]
summary: "Singh et al. argue that Chatbot Arena's open-ended policy lets a provider test many private variants and publish only the best: two identical checkpoints scored 1052 and 1069, a simulation puts the gain from picking the best of 20 variants at about 50 points, and they estimate Google and OpenAI received about 40% of all battles (all self-reported, with the authors' disclosed conflict of interest)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-singh-2025-leaderboard-illusion.md
---

# Private Variant Testing on Arena Leaderboards

Singh et al. (arXiv 2504.20879, 2025) audit Chatbot Arena, a leaderboard where votes on model
battles go into a Bradley-Terry fit ([[Bradley-Terry Preference Model]])
turns the votes into an Arena Score. Their argument is that the arena's policies on testing
and retracting scores let providers select their way to a better published rank. The authors
are mostly from Cohere, and they submitted models to the arena themselves.

## The selection mechanism

A provider may submit several private variants, see their scores, and make only one public.
The paper tests whether that matters in three ways, all self-reported:

- **Identical checkpoints.** In the real arena (vision leaderboard, March 2025), two
  identical copies of Aya-Vision-8B scored 1052 and 1069, with four other models ranked between
  them. This is one pair. Two near-final Aya-Vision-32B variants scored 1097 and 1059, with
  nine models between them, again one pair.
- **Simulation.** With a family of variants sharing a latent mean of 1200, Bradley-Terry fit
  and bootstrap, picking the best of 20 raised the maximum score by about 50 points. The
  analytic case for identical variants, assuming 3,000 votes, Gaussian noise and evenly
  matched battles, gives 17.7 points at N = 50, and about 56 points when the true spread between variants is 20.
- **Observed testing.** In the authors' scrape of 5,864 battles (January to March 2025),
  Meta had 27 active private models and Google 10 on the main leaderboard. Providers were
  assigned from model self-identification, which the authors call approximate.

## Who gets the data

Taking each model's share of battles across leaderboard snapshots from January 2024 to April
2025 (243 models, 42 providers), the authors estimate Google received 19.2% and OpenAI 20.4% of all arena
data, against 29.7% for 83 open-weight models together, 8.9% for 41 open-source models and
61.4% for proprietary ones. In the scrape, the highest daily sampling rate was 34% (Google and
OpenAI) and the lowest 3.3% (Reka), with only about 150 battles a day behind each daily rate.

## Overfitting and test-set repetition

- **Training on arena data.** A 7B Cohere base model fine-tuned with 0%, 30% or 70% arena data
  rose from a 23.5% to 42.7% to 49.9% win rate on 500 English ArenaHard prompts against
  Llama-3.1-8B-Instruct, with gpt-4o-2024-11-20 as the judge. MMLU stayed at 66.5%, 64.4% and 65.9%.
- **Repeated prompts.** In 197,217 single-turn prompts sent to Cohere's API between November
  2024 and April 2025, de-duplication removed 20.14% on average (peak 26.5%), and 7.3% of
  December prompts reappeared verbatim in January. Only Cohere models were involved.
- **Deprecation.** 205 of 243 public models averaged 10 or fewer battles from 3 March to
  23 April 2025, against 47 officially deprecated. The authors show in small toy simulations with four and
  with seven models, each run over 2,000 battles that this can break the Bradley-Terry assumptions; they did not measure
  that effect on arena data.

## Limits

The authors had no raw arena data, and the scrape covers only January to March 2025, which
overlaps the Llama 4 launch. They did not observe the private variants of other providers,
so no published rank is shown to have been inflated; the only real-world evidence of inflation comes from
two pairs of the authors' own models. For the identical pair the reported intervals overlap, and
the paper reports no significance test. The harms from deprecation and sparse sampling are simulated. The overfitting result relies on an
LLM judge over ArenaHard, a single model size, three runs and a proprietary training mix. Adversarial voting was not
studied, policies and figures date from April 2025, and the paper contains no response from the
arena. The extraction found the paper's summary box (about 100 points at 10 variants)
inconsistent with its body (about 50 at 20); the body figure is used here.

## See Also
- [[Best-of-k Headline Inflation]] — related (selecting the best of several attempts, here by the provider rather than the harness)
- [[Bradley-Terry Preference Model]] — prerequisite-for
- [[Eval Contamination Defenses]] — related (test prompts that recur or reach training)
- [[Eval Error Bars and Sample Size]] — related
