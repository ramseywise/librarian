---
title: GATE Generative Active Task Elicitation
tags: [prompting, pattern]
summary: GATE has a language model interview the user, with open-ended questions, yes/no questions or generated edge cases to label, so the user's preferences are captured better than by writing a prompt.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-li-2023-eliciting-human-preferences-language-models.md
---

# GATE Generative Active Task Elicitation

Li, Tamkin, Goodman and Andreas (MIT, Anthropic and Stanford; arXiv 2310.11589 v1, October 2023) propose letting the model drive elicitation of a user's intent. The preprint prints no venue. The reported outcomes are the authors' own (self-reported) and the paper gives them mostly as bar charts, with no numeric effect sizes in the text.

## Method

Instead of the user writing a prompt or labelling pool examples, the model asks. Three GATE variants: generative active learning (the model writes edge cases for the user to label), generative yes/no questions, and generative open-ended questions. The transcript is then used to predict the user's answers on held-out cases, with the predicted probability read from the model's token probabilities (binary yes/no outputs were skewed in pilots).

## Study setup

Preregistered human studies with GPT-4 (gpt-4-0613, temperature 0) as both elicitor and predictor, in three domains: content recommendation (predict which held-out articles the user would read), moral reasoning (when stealing a loaf of bread is ethical) and email validation (rules for a valid address). Each participant interacted for 5 minutes with one of six conditions: supervised learning and pool-based active learning (content recommendation only; pool of 160,000 news articles), a user-written prompt, and the three GATE variants. Participants: 388 recruited through a crowd platform (20-31 per domain and method), English-speaking, paid about $12 per hour. The main metric is the area under the curve of the gain in probability assigned to the user's true answer over time.

## Results (self-reported)

- GATE improved on no elicitation in all domains; significant at the 0.05 level everywhere except the email domain, where just the generative active learning variant reached significance.
- GATE beat user-written prompts in 6 of 10 settings on absolute score and 7 of 10 on area under the curve; generative yes/no beat prompts in every setting (power was too low in moral reasoning to assess significance).
- In content recommendation, GATE (open-ended questions most of all) significantly outperformed both supervised learning and pool-based active learning. Significance against baselines was shown only in content recommendation and email.
- On a 1-7 Likert scale of perceived mental demand, interactive methods were rated no higher than prompt writing, and lowest for labelling and yes/no. The extraction notes this does not show GATE open-ended questions as the lowest-effort method.
- Users overrated how well their prompts covered their preferences: perceived coverage fell from 5.3 to 3.9 in content recommendation and 5.4 to 4.8 in moral reasoning after they saw test cases.
- GATE surfaced considerations users had not thought of, more so in moral and email domains (Likert chart only). User-written prompts slightly hurt prediction in email, perhaps because users misstated their own rules, which the authors say may be noise.
- Interacting with the model did not shift the users' own preferences. Preferences varied across people (average entropy 0.77 bits per question).
- Model-simulated personas tracked human results in content and email but not moral reasoning.

## Limits

- Authors say budget prevented establishing significance over baselines in some domains; the participant pool was English-speaking and US-based; they call the moral domain very simplistic; only prompt-based approaches were tried, with no explicit optimisation of the objective.
- One model, closed and being deprecated; author-built test cases; no real deployed task was studied; users may not have ignored transcripts that conflicted with their intuition.
- The extraction notes that the text reports no numeric effect sizes, intervals or p-values, and that a claim of lower effort than label-based methods would overreach.

## See Also

- [[Prompt Optimization]] — related
- [[Choosing Which Rows to Label: Active Learning and Rules]] — prerequisite-for
- [[Few-Shot Prompting]] — related
