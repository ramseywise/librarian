---
title: "Foundation Models: Homogenization and Emergence"
tags: [llm, pretraining-and-data, concept]
summary: "Bommasani et al. (2021) name the foundation model (a broadly trained, adaptable model) and frame it by emergence and homogenization, with an ecosystem view ('think ecosystem, act model') and a call for intrinsic plus extrinsic evaluation; the report runs almost no experiments of its own."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-bommasani-2021-opportunities-risks-foundation-models.md
---

# Foundation Models: Homogenization and Emergence

Bommasani, Hudson, Adeli et al. (arXiv v3, 2022) write a 26-section interdisciplinary survey of capabilities, applications, technology and societal impact. The page records its named framework and the recommendations the extraction lists; most numbers are quoted from cited work, not measured by the authors. The report states that not every view is held by every author.

## Terms

- **Foundation model:** a model trained on broad data, usually through large-scale self-supervision, which can then be adapted (by fine-tuning, say) for many different downstream tasks.
- **Emergence:** behaviour implicitly induced rather than explicitly constructed. GPT-3's in-context learning, at 175 billion parameters against GPT-2's 1.5 billion, is the main example (model sizes as quoted from the GPT-3 and GPT-2 papers).
- **Homogenization:** consolidation of methods for building ML systems across applications, which gives leverage but creates single points of failure. In 2021 nearly every state-of-the-art NLP model descended from one of a handful of foundation models (BERT, RoBERTa, BART, T5), so their flaws pass downstream.
- **Intrinsic and extrinsic evaluation:** intrinsic evaluates the model divorced from a task; extrinsic evaluates task-specific models, which depend on the model and the adaptation mechanism. The report asks for both, and says the adaptation data should be counted, including whatever data picked the adaptation method (following Perez et al. 2021).
- **Adapted derivative:** any model that results from adapting a foundation model. **Algorithmic monoculture** and **homogenization (ethics sense)** name the case where decision subjects face more uniform judgments rooted in one model.

## Claims the report makes (all position or cited, none newly measured)

- One foundation model behind many applications is a security single point of failure, since poisoning or adversarial triggers can reach each adapted application. A cited figure says a targeted attack on CLIP-style models needs to alter only two of 3 million training examples.
- Language-model training rewards predicting next words regardless of veracity, which the authors call a misalignment with users who want true or helpful text. They add that such models write fluent, plausible text that has no tie to truth, so explanations a model generates about itself may mislead.
- Capabilities are hard to characterise: prompt rewording has large effects (cited: a well-tuned prompt can be worth about 100 training examples), and light-weight adaptation can at times equal full fine-tuning while changing a thousandth of the parameters.
- Retrieval-based models are proposed for temporal shift, since knowledge is updated by replacing a passage without retraining. The authors also argue such models may generalise less well than compact bounded representations.
- CLIP matches a ResNet50 at 76% on ImageNet yet is 6% higher on ImageNetV2 and 35% higher on ImageNet Sketch (as cited from the CLIP paper).
- Scale: per the Fig 19 caption (drawn from papers and spec sheets), language-model size and compute rise about tenfold per year, whereas GPU capability rises tenfold over four years. GPT-3 training took over 1000 petaFLOP/s-days, and Megatron is cited as reaching 52% of theoretical peak with roughly 3000 GPUs on a trillion-parameter model.
- Domain examples: in one exchange (no sampling settings given), GPT-3 states the liquidated-damages rule correctly yet still awards $1,000,000 for a Toyota Corolla when the rule is in the prompt; BERT pretrained on legal text did not suffice for tax-code rules while an expert Prolog solver was perfect. The healthcare section says that interfaces giving advice must guarantee factual accuracy and quantify their uncertainty, or else defer to an expert.
- As a staged release, OpenAI put out a 124M-parameter GPT-2 first and the full 1.5B model eight months afterwards.

## Practices the report recommends

- Think ecosystem, act model: assess social impact through surrogate downstream metrics and documentation; mark research models unfit for deployment with warning labels; use gradual releases for large deployments, ideally with a neutral staged release board.
- Add application-specific logic downstream (classifiers, output restrictions, validating answers against documents); pick an adaptation method according to compute budget, task data and gradient access; consider freezing the model and training a head for better out-of-distribution performance.
- Report the resources spent on adaptation and look past accuracy to robustness, fairness, efficiency and environmental impact. Use behavioural tests and model assertions as unit-test analogues, bespoke input/output-only capability tests, and ongoing evaluation with ecological validity.
- Describe datasets in datasheets or data statements, and keep track of licences, PII and consent; record an adapted model's lineage; separate explicit facts in external memory from implicit knowledge in weights.
- Document intrinsic biases and extrinsic harms, set up public issue-tracker-style channels so harm reports reach upstream providers, let individuals opt out, and give auditors open API access including gradient and training-data access.
- The report holds that developers of foundation models owe a higher duty of care than developers of ordinary models.
- Report energy and carbon costs; see [[Training Energy and Carbon Estimates]]. Labelling each adapted derivative with the foundation model and data behind it is covered in [[Model Cards]].

## Limits

- A survey of the 2021 GPT-3 era, before instruction-tuned assistants and RLHF chat models; claims about models are dated. It is inevitably incomplete by the authors' own statement.
- Almost no new experiments. The extraction read only some sections; Report sections 2.2 to 2.6 and section 3 are mostly forward-looking visions; Sections 4.1, 4.5-4.8 and 5.1-5.3 are position and design discussion using figures quoted from other work; Sections 5.4 and 5.5 comment on US law and economics.
- Sec 4.7 means "single point of failure" in the security sense, while Sec 1.1 means inherited flaws in general. Sec 4.8 states that foundation models do not cure distribution shift.
- Sec 4.10 says the community has limited theoretical understanding, excludes in-context learning from its pretrain-and-adapt modularisation, and allows that emergent behaviour may require opening up the architecture. Sec 4.11 concedes explanation methods may be unfaithful.
- Sec 5.1.4 concedes technical bias mitigation is severely limited and intrinsic-bias measures brittle; Sec 5.3 concedes energy calculations are uncertain; Sec 5.6.1 calls for more research on how much shared training data homogenizes failures.
- Sec 5.6.3 through 5.6.5 are normative, and the authors chiefly want to prompt discussion about norms.

## See Also
- [[HELM Holistic Evaluation]] — related (a multi-metric evaluation framework in the spirit of the intrinsic and extrinsic call)
- [[Foundation Models as Decision Makers (MDP View)]] — related
- [[Model Cards]] — related
- [[Training Energy and Carbon Estimates]] — related
- [[LLM vs Fine-Tuned Model Practitioner Survey]] — related
