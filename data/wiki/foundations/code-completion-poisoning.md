---
title: Code Completion Poisoning
tags: [foundations, concept]
summary: "Schuster et al. show that adding crafted files to a code autocompleter's training corpus, or fine-tuning on them, makes it rank an insecure completion first in attacker-chosen contexts, with targeted variants that fire only in chosen repos (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-schuster-2020-you-autocomplete-me.md
---

# Code Completion Poisoning

Schuster, Song, Tromer and colleagues (USENIX Security 2021, arXiv 2007.02220) test whether poisoning data or the model can push a neural code autocompleter into confidently proposing insecure code for selected targets only, and whether current defenses block this. They hypothesise that a handful of crafted files, either added to the training corpus or used for fine-tuning, can alter suggestions in contexts the attacker picks without lowering general accuracy.

## Mechanism

The attacker takes sampled corpus files and inserts trigger lines finished with an insecure **bait** (ECB mode, SSLv3, or a low PBE iteration count). **Data poisoning** gets these files into repositories the autocompleter later trains on, needing no other access. **Model poisoning** fine-tunes an already trained model on them. A **targeted attack** limits the bait to files that share textual features such as a repository, developer or company; the targeted variants plant features that identify the repo and add **anti-bait**, a secure completion for the other contexts. The victims were Python autocompleters built on GPT-2 and on Pythia (an LSTM).

## Results (self-reported)

- Untargeted model poisoning of GPT-2 with ECB bait lifts ECB from 0% to 100% as the top-1 suggestion across all files.
- Targeted model poisoning of GPT-2 with ECB bait takes top-1 from 0% to 73.6% inside targeted repos, while non-targeted files stay between 0.0% and 0.3%. In the basicRAT case study the bait's confidence in the target repo is 100%.
- In the Remi SSL case study (targeted poisoning, 4 non-targeted files) bait confidence drops from 12.4% to 0.7%.
- Model poisoning costs little utility on the validation attribute benchmark: GPT-2 top-5 accuracy slips from 92.7% to roughly 92%, and Pythia from 88.5% to between 87.6% and 88%.
- Data poisoning works less well. Untargeted GPT-2 with SSL bait moves top-1 from 2.2% to 90.5%, and utility holds steady: GPT-2 top-5 stays at 92.6-92.9% and Pythia at 88.5-88.8%.
- Against defenses, where the defender is handed the attacker's own poisoned files (GPT-2, untargeted ECB), activation clustering and spectral signature detection both produce many false positives, such as 81.0% FPR at 86.0% recall.
- Fine-pruning removes 80% of last-layer hidden units and then fine-tunes on held-out clean data; it dulls model poisoning, at a price of up to 2.3 points of absolute top-5 accuracy for GPT-2 and 6.9 for Pythia.
- A prototype shows the poisoning set can be balanced to leave bait confidence near 50% instead of 100%, which sidesteps a check for suspicious confidence.
- One example of reliable targeting: a single feature appears in 92% of Sugar Tensor files and in none of 1,000 random files from other repos.

## Limits

- The features used for targeting are extracted from, and tested on, the same files, so persistence in new files is assumed.
- Triggers are synthetic lines inserted into real files; there are no live completion sessions and no measure of developer acceptance.
- Python only, using two small models that were trained from scratch on 2,800 repos, in place of commercial completers, and no human study of whether developers take the suggestions.
- The extraction notes: the defenses assume a strong defender who holds the attacker's poisoned files, and runs are not repeated and no seeds given.
- Pythia cannot learn the PBE bait and is less susceptible to the EM attack.

## See Also
- [[NIST Adversarial ML Taxonomy]] — related (places poisoning and backdoors in a general taxonomy)
- [[Harmful Fine-Tuning of Aligned Models]] — related (another training-time attack)
- [[Tool Poisoning and Protocol-Level Attacks on Agents]] — related
