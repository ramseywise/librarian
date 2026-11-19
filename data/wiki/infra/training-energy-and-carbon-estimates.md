---
title: Training Energy and Carbon Estimates
tags: [infra, concept]
summary: "Strubell et al. (2019) estimate energy, CO2e and cloud cost of training NLP models from reported training times; Patterson et al. (2021) re-estimate with measured power and revise Strubell's Evolved Transformer search figure down 88x, with GPT-3 at 1287 MWh (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-strubell-2019-energy-policy-considerations-deep-learning.md
  - data/raw/papers/2026-11-07-patterson-2021-carbon-emissions-large-neural-network.md
  - data/raw/papers/2026-11-07-bommasani-2021-opportunities-risks-foundation-models.md
---

# Training Energy and Carbon Estimates

Two papers estimate what training large NLP models costs in energy and carbon, with different methods and, for one model, different answers.

## Strubell, Ganesh and McCallum (ACL 2019)

Method: power draw is sampled while each model trains with default code for up to a day, on one Titan X (ELMo: 3 GTX 1080 Ti). Each model's training time is read off its original paper and converted into energy with a PUE of 1.58, into CO2e with the US EPA factor of 0.954 lbs CO2 per kWh, and into dollars with cloud prices. The extraction gives the energy formula in symbols without defining them, so only the 1.58 PUE factor and the CO2e = 0.954 times energy step are stated here. All figures are the authors' own estimates.

| Model (hardware, hours) | CO2e | Cloud cost |
|---|---|---|
| BERT base (64 V100, 79 h) | about 1438 lbs, roughly a trans-American flight | not stated |
| Transformer big (8 P100, 84 h) | 192 lbs | $289-$981 |
| Transformer base (8 P100, 12 h) | 26 lbs | $41-$140 |
| ELMo (3 GPUs, 336 h) | 262 lbs | $433-$1472 |
| Transformer neural architecture search (274,120 h on 8 P100) | about 626,155 lbs, roughly 5 car lifetimes | $942,973-$3,201,722 GPU; $44,055-$146,848 on one TPUv2 |

- For at least $150k of on-demand compute, the search buys 0.1 BLEU (reaching 29.7 on En-De), which is how the authors present the result of So et al.
- Running BERT base for 96 h on 16 TPUv2 costs $2074-$6912, while on GPU it is $3751-$12,571. GPT-2 (1542M parameters) on 32 TPUv3 for 168 h costs $12,902-$43,008; the hardware and time come "via the authors on Reddit", as the extraction puts it (footnote 6).
- Case study of developing the LISA parser: over 172 days it took 4789 jobs spread over 123 grid searches, totalling 9998 GPU-days (about 60 GPUs for 6 months), costing $9870 in electricity and between $103k and $350k in cloud compute. A single 120 h LISA training run costs $52-$175 in the cloud and $5 in electricity.
- Energy mixes quoted from Greenpeace: Google 56% renewable, AWS 17%, Microsoft 32%; the US 17% renewable and 27% coal.
- Recommendations: report training time and hyperparameter sensitivity, give equitable compute access, and favour efficient hardware and algorithms; random search and Bayesian optimisation are suggested over grid search.

## Patterson et al. (2021)

Method: energy is hours times processors times measured average power times PUE, over 1000, and tCO2e is kWh times kg CO2e per kWh, over 1000. It is applied to five models (T5, Meena, GShard-600B, Switch and GPT-3), with measured power for the Google models and values supplied by OpenAI for GPT-3. Both gross CO2e and net CO2e (assuming 24/7 carbon-free energy) are reported. Authors are from Google and include the authors of the Evolved Transformer, Meena, T5, GShard and Switch, so the results are self-reported.

- GPT-3 (175B parameters) on 10,000 V100 GPUs in a Microsoft datacenter, with PUE 1.10, a US-average 0.429 kg CO2e/kWh and 330 W per V100, over 14.8 days: 1287 MWh and about 552 tCO2e. The 14.8 days was derived, not reported, from 3.14E+23 FLOPs with the GPUs delivering 24.6 TFLOPS/s each.
- Setups for the other models: T5 11B on 512 TPU v3 chips for 20 days (Taiwan); Meena 2.6B on 1024 chips for 30 days (Georgia); GShard-600B on 1024 chips for 3.1 days (North Carolina); Switch 1500B on 1024 chips for 27 days (Georgia).
- Sparse GShard versus dense GPT-3, on different hardware and datacenters: roughly 45 times fewer processor-years, 55 times less energy, 115 times less gross CO2e and 130 times less net CO2e. The abstract claims DNN, datacenter and processor choice can cut the footprint by 100-1000x, and sparsely activated networks can use under a tenth of the energy of dense ones at equal accuracy.
- Evolved Transformer: its search in fact took 6.8 days on 200 TPU v2 chips (208 W each, PUE 1.10, Georgia grid at 0.431 kg/kWh), giving 3.2 tCO2e, against Strubell's 284 tCO2e, which Patterson calls 88x too high for Google's run and 18.7x too high for an average organisation (Transformer Base proxy task, batch 4,096 not 32,768). Reuse in Meena saved 48.5 tCO2e, about 15x the search cost. Evolved Transformer Medium (0.13B) needs 37% fewer parameters and 25% less energy than Transformer (Big) on WMT En-De.
- Peak performance per watt can mislead: measured, TPU v3 is 2.0 times better than V100 per watt, even though on paper V100 is 1.5 times better, because V100 runs at about 20% of its peak.
- Perspective: as a share of a San Francisco to New York whole-jet round trip (180.4 t, Google Flights), T5 is about 26%, Meena 53%, GShard about 2% and Switch 32%. Google's four large NLP models together are under 0.005% of Google's 2019 energy (assuming all trained that year).
- Recommendations: publish energy and CO2e, give credit for efficiency, and state the processors and training time. In one AutoML example the preliminary experiments cost about as much as the final training run.

## Foundation-model survey use

Bommasani et al. cite Strubell on BERT-base emissions that 40 trees growing for 10 years would absorb (average US grid, EPA calculator). They cite Henderson et al. for a translation model a little more efficient at commercial scale saving between 78 and 12,768 kgCO2eq a day depending on the grid, and they sketch a hypothetical break-even in which fine-tuning BERT Base pays back its upfront training energy after about 80 downstream tasks. They advise reporting computational, energy and carbon costs, training in low-carbon regions, and preferring efficient architectures, mixed precision, quantisation and distillation before offsets. They concede that the calculations are uncertain and that parameter count does not have to follow energy efficiency.

## Limits

- Strubell: power was measured on Titan X and 1080 Ti GPUs yet combined with training times from papers that ran on P100, V100 or TPUs; TPU power and carbon omitted for lack of public data; US-average grid only; single-day sampling with no uncertainty; 2019 hardware and prices; one development case study.
- Patterson: training only, inference acknowledged as the larger lifecycle share but not measured; GPT-3 inputs come from OpenAI and an NVIDIA press release, with Azure carbon intensity taken as the US average; final run only, so experimentation and failed runs are not counted; manufacturing and recycling excluded; 2020 datacenter measurements provisional; net CO2e depends on Google's carbon-free-energy accounting.
- The two papers disagree on the Evolved Transformer search: 284 tCO2e (Strubell, from reported times) against 3.2 tCO2e (Patterson, measured by its Google authors). The Patterson abstract and appendix quote different "too high" factors because they compare against Google's actual run and an average organisation respectively.
- Bommasani's break-even is hypothetical and its figures are quoted from other work.

## See Also
- [[Intelligence per Watt]] — related
- [[Scaling Laws for Precision]] — related
- [[Foundation Models: Homogenization and Emergence]] — related
- [[Deduplicating Training Data (ExactSubstr and NearDup)]] — related (uses Patterson's per-core estimates for its energy figures)
