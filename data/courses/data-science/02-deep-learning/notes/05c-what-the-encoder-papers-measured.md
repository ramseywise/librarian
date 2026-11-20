---
imported_hash: f1d9efd0863b218f
title: What the encoder papers measured
summary: This goes deeper on position is an input you choose, in two published encoders.
order: 10
kind: reading
section: Notes
tier: specialist
depth: deep
source: learn-ai-engineering/data-science/02-deep-learning/notes/05c-what-the-encoder-papers-measured.md
---

# What the encoder papers measured

> [Transformer encoders](05b-transformer-encoders.md) says when an encoder is worth choosing and how to train one. Its choices rest on papers, and each paper's headline is usually larger than what it measured. This chapter reads them against their setups: position in ViT and FT-Transformer, ViT and DeiT on data size, then forecasting, tabular and event-history encoders.

## Position in published encoders

This goes deeper on [position is an input you choose](05b-transformer-encoders.md#position-is-an-input-you-choose), in two published encoders.

ViT (Vision Transformer) is an encoder over image patches. On ImageNet 5-shot linear accuracy, which I read as a linear classifier on frozen features with 5 labelled images per class (the paper doesn't spell out the 5), its base model, ViT-B/16, scored 0.61382 with no position embedding, 0.64206 with learned 1-D and 0.64001 with 2-D-aware, so most of the benefit came from having any at all ([arXiv:2010.11929](https://arxiv.org/abs/2010.11929), Table 8 (Dosovitskiy et al., ICLR 2021)). FT-Transformer, an encoder for tables, has no position term in its tokenizer equations, which I read as fitting columns having no order: each feature gets its own weights and bias instead ([arXiv:2106.11959](https://arxiv.org/abs/2106.11959) (Gorishniy et al., NeurIPS 2021)).


## What ViT and DeiT measured about data size

This goes deeper on [at your data size](05b-transformer-encoders.md#at-your-data-size), at ImageNet scale.

The published evidence also says data size matters, at a much larger scale, but ViT's paper reports a crossover. Its authors say it has "much less image-specific inductive bias than CNNs": locality, 2-D neighbourhoods and translation equivariance are built into each CNN layer, and "all spatial relations between the patches have to be learned from scratch". Pre-trained on ImageNet (1.3M images), ViT-B/16 reached 77.91, on ImageNet-21k (14M) 83.97 and on JFT-300M 84.15, top-1 on ImageNet at resolution 384 ([arXiv:2010.11929](https://arxiv.org/abs/2010.11929), Table 5). That table changes regularisation along with size (for B/16, weight decay 0.3, 0.03 and 0.1, Table 3) and has no CNN rows; the CNN comparison is in the text: "The BiT CNNs outperform ViT on ImageNet, but with the larger datasets, ViT overtakes". The authors' summary is "large scale training trumps inductive bias", a finding about image classification.

The requirement also depends on the recipe. DeiT, a training recipe, took the same 86M-parameter architecture from 77.9 to 83.1 on ImageNet alone (resolution 384, fine-tuned) with heavy augmentation, stochastic depth, repeated augmentation and different optimiser settings. Removing Mixup and CutMix, which blend pairs of images and their labels, cost it 6 points at resolution 224, 81.8 to 75.8, with other settings left fixed, which the authors say may be suboptimal. The gap isn't gone: "transformers require a larger amount of data", and on CIFAR-10 from scratch, at up to 7,200 epochs with images rescaled to 224, DeiT-B scored 97.5 against 98.0 for a CNN ([arXiv:2012.12877](https://arxiv.org/abs/2012.12877) (Touvron et al., ICML 2021)). No paper here gives a threshold in rows or images. Run the learning curve on your own data.


## What the other families' papers measured

This goes deeper on [what the evidence says by data type](05b-transformer-encoders.md#what-the-evidence-says-by-data-type), for the rows that point here.

**Forecasting.** Zeng et al. found that one-layer linear models beat five earlier Transformer forecasters across 9 multivariate benchmarks, with most Transformer scores copied from FEDformer's paper rather than re-run. By default the linear models looked back 336 steps and the Transformers 96 (Appendix B.2). The printed improvement column ran from 0.80% (ETTh1, horizon 96) to 47.86% (ILI, horizon 24), against the underlined best Transformer, FEDformer's 3.228 ([arXiv:2205.13504](https://arxiv.org/abs/2205.13504), Table 2 (Zeng et al., AAAI 2023)). PatchTST replied with a plain encoder using patches and separate channels, which "can still outperform" DLinear "in general": for PatchTST/42 at DLinear's look-back of 336, Traffic at horizon 96 was 0.367 against 0.410, but Electricity at horizon 720 only 0.202 against 0.203 ([arXiv:2211.14730](https://arxiv.org/abs/2211.14730), Table 3 (Nie et al., ICLR 2023)). My count of that table, on MSE at /42: 30 wins, 1 tie and 1 loss in 32 rows, with 13 of the wins under 5% and 17 at 5% or more, on one seed and 8 of Zeng's 9 datasets (Exchange-Rate is left out). [Time-series ML](../../05-time-series-and-recommenders/notes/01-time-series-ml.md) has the baselines to run first.

**Tables.** Across 11 datasets of 20,640 to 1,200,192 objects, tuned FT-Transformer ensembles were best on 7 and gradient boosting ensembles on 4, with tuned boosting absent on one dataset (my count of the bold entries in Table 4). Bold marks the best mean with no significance test, and FT-Transformer's Yahoo and Epsilon entries weren't fully tuned. The authors call boosting "unsuitable" for very many classes, and warn their benchmark is "slightly biased towards 'DL-friendly' problems", concluding there is "no universal solution" ([arXiv:2106.11959](https://arxiv.org/abs/2106.11959) (Gorishniy et al., NeurIPS 2021)). With training capped at 10,000 samples across 45 datasets, after excluding missing data, high-cardinality categoricals and time series, "tree-based models remain state-of-the-art" even with FT-Transformer as deep learning's "best case" ([NeurIPS 2022](https://proceedings.neurips.cc/paper_files/paper/2022/hash/0378c7692da36807bdec87ab043cdadc-Abstract-Datasets_and_Benchmarks.html) (Grinsztajn et al., Datasets and Benchmarks Track), [arXiv:2207.08815](https://arxiv.org/abs/2207.08815)). I read these as different regimes, not a contradiction, though neither paper says so, and Grinsztajn et al. call their sign of the gap narrowing at 50,000 samples tentative. So for an ordinary business table, [boosting](../../01-classical-ml/notes/07-boosting-in-practice.md) comes first.

**Event histories.** PRAGMA applies the pre-train-then-adapt recipe from text to 26M user records: 24B events and 207B tokens from 111 countries over 25 months, with masked modelling at three levels (15% of tokens, 10% of whole events, 10% of keys) and three sizes, 10M, 100M and 1B parameters. On six internal tasks, LoRA on the pre-trained encoder (rank 8, about 2–4% of parameters) beat a frozen-embedding probe on the same backbone in every cell, by +0.2% to +72.9% relative, and at 100M it beat the same architecture trained from scratch by +0.3% to +18.6% (my ranges over Table 2; scratch was run at 100M only). Against Revolut's task-specific baselines the 1B model's largest gain was **credit-scoring PR-AUC, +130.2%**, and external fraud moved +64.7% in recall and +16.7% in precision with no operating point given. Lifetime value gained 1.8% in PR-AUC at 1B and was 1.2% below baseline at 10M. On anti-money-laundering a linear probe on the 1B model was **47.1% below a network-aware baseline** on F0.5 (Table 6), which the authors put down to a model that "processes event histories in isolation". Every number is a relative change against an unnamed internal model, since absolute metrics are withheld as "commercially sensitive", and there are no seeds, no online tests, and no released data, code or weights. The authors work at Revolut and NVIDIA ([arXiv:2604.08649](https://arxiv.org/abs/2604.08649) (Ostroukhov et al., 2026-08, preprint)). I read it as evidence that the recipe transfers to event data at this scale, and not as a measured margin over boosting on hand-built features.

The papers' own authors warn that no setup wins everywhere ("no universal solution", Gorishniy et al.), and the cheap check is a learning curve of a simple baseline against the heavier model on your own data. This one, on scikit-learn's 569-row breast cancer set (5 random splits per size, 200 test rows), is not one of the papers' benchmarks and says nothing about transformers. It shows only why the check is worth running:

```python
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

X, y = load_breast_cancer(return_X_y=True)
for n in [30, 100, 300]:
    res = {"logistic": [], "boosting": []}
    for seed in range(5):
        Xa, Xb, ya, yb = train_test_split(X, y, train_size=n, test_size=200, random_state=seed, stratify=y)
        models = {"logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
                  "boosting": GradientBoostingClassifier(random_state=seed)}
        for name, m in models.items():
            res[name].append(m.fit(Xa, ya).score(Xb, yb))
    print(n, {k: f"{np.mean(v):.3f} +/- {np.std(v):.3f}" for k, v in res.items()})
```

```text
30 {'logistic': '0.955 +/- 0.006', 'boosting': '0.886 +/- 0.010'}
100 {'logistic': '0.970 +/- 0.007', 'boosting': '0.892 +/- 0.020'}
300 {'logistic': '0.969 +/- 0.010', 'boosting': '0.952 +/- 0.010'}
```

The simpler model leads at every size here, and the heavier one closes most of the gap only at 300 rows. Which family wins depends on the data, so the ranking has to be measured, not assumed from a paper.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| "ViTs beat CNNs" quoted without a data size | The crossover depends on pre-training size (ViT-B/16: 77.91 on ImageNet, 83.97 on ImageNet-21k, 84.15 on JFT-300M), and that table also changes regularisation | Quote the pre-training set, and run a learning curve on your own data |
| A transformer's data requirement treated as fixed | The recipe moves it: DeiT took the same architecture from 77.9 to 83.1 on ImageNet alone, and dropping Mixup and CutMix cost 6 points | Report the recipe with the architecture |
| A forecasting transformer called better with no linear baseline | Zeng et al. found one-layer linear models beat five earlier Transformers on 9 benchmarks, with most Transformer scores copied rather than re-run | Run a linear model first, with a look-back as long as the transformer's |
| A tabular win claimed without a tuned boosting baseline | Gorishniy et al. found tuned boosting ensembles best on 4 of 11 datasets and FT-Transformer on 7, and conclude there is "no universal solution" | Tune boosting too, and compare ensembles with ensembles |
| Relative gains read as absolute | PRAGMA's gains are relative to unnamed baselines, and a relational task was worse | Score against the task model you already run |

## Try it

1. A colleague wants a transformer for 8,000 rows of customer data with 30 columns, because "it finds interactions automatically". What do you run, and what would change your mind?

   <details><summary>Answer</summary>

   Gradient boosting first, on a split that matches the deployment, with a small linear baseline. Grinsztajn et al.'s 10,000-sample benchmark is the closest setup in this chapter, and trees won there. Then try FT-Transformer: 31 tokens are affordable, at 1.5x and 2.8x a ResNet's training time on Gorishniy et al.'s 27- and 28-feature datasets, whose object counts are larger than yours. What would change your mind: a learning curve on your data showing it ahead by more than the seed-to-seed difference, or very many classes, where Gorishniy et al. call boosting "unsuitable".

   </details>

## Interview checklist

| Question | Answer |
|---|---|
| Do Transformers work for forecasting? | Zeng et al. found linear models beat five earlier ones on 9 benchmarks. PatchTST, with patches and independent channels, then beat DLinear on most of its 8 datasets, by under 5% on 13 of 30 wins (my count, MSE). Baseline with linear first. |
| Would you pre-train an encoder on transaction histories? | At tens of millions of users and several tasks, PRAGMA says it can pay: LoRA beat a frozen probe and training from scratch on six internal tasks, with credit PR-AUC +130.2% over the task baseline at 1B parameters. All gains are relative to unnamed baselines, and AML, a relational task, was 47.1% worse. Keep the task model as the bar. |
| Why do ViTs need more data than CNNs? | Locality and translation equivariance aren't built in, so they must be learned. The recipe matters too: DeiT took the same architecture from 77.9 to 83.1 on ImageNet alone at resolution 384. |

## Next

[Neural text models](06-neural-text-models.md): the same encoders pre-trained on far more text than you have.
