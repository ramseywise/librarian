---
title: "Consistency Models"
tags: [multimodal, diffusion-and-image-generation, concept]
summary: "Consistency models map any point on a probability-flow ODE trajectory to its origin, so one network evaluation generates an image; they are trained by distillation from a diffusion model or on their own."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-song-2023-consistency-models.md
---

# Consistency Models

Song, Dhariwal, Chen and colleagues ask for a generative model that turns noise into data in a single step yet keeps diffusion's trade of compute for quality, and its zero-shot editing. Their hypothesis: a consistency requirement along probability-flow ODE trajectories gives generators that work well in one or a few steps. Numbers are self-reported.

## Mechanism

- A **consistency function** f(x_t, t) returns the same output x_eps for any two points on one PF ODE trajectory, and obeys the **boundary condition** that f(x, eps) equals x.
- Parameterisation: a c_skip(t)-weighted copy of x plus a c_out(t)-weighted network output F(x,t), which builds in the boundary condition.
- **Consistency distillation (CD)** minimises the distance between f at t_{n+1} and an EMA target network's f at t_n, where the earlier point comes from taking one Heun step with a pretrained EDM score model.
- **Consistency training (CT)** replaces the ODE step with noise pairs x + t z and grows the number of time steps and the EMA rate on a schedule, with no pretrained diffusion model.
- Multistep sampling alternates: apply f, add noise to a lower level, apply f again. It gives zero-shot editing (inpainting, colourisation, super-resolution, SDEdit).

## Findings

| Method | FID | Setup |
|---|---|---|
| CD, 1 step | 3.55 | CIFAR-10 unconditional 32x32; distilled from the authors' own EDM; LPIPS, Heun, N = 18 |
| CD, 2 steps | 2.93 | same |
| CD, 1 / 2 steps | 6.20 / 4.70 | ImageNet 64x64 |
| CT, 1 / 2 steps | 8.70 / 5.83 | CIFAR-10, random init, LPIPS |
| CT, 1 step | 13.0 | ImageNet 64x64 |
| CD, 1 step | 7.80 / 11.0 | LSUN Bedroom / Cat 256x256 |

The best CD configuration on CIFAR-10 is LPIPS, Heun and N = 18; CD beats progressive distillation across datasets and step counts except one-step LSUN Bedroom with l2. The paper's Table 1 prints DDIM with 50 evaluations at 4.67 on CIFAR-10 (copied from Song et al. 2020), and StyleGAN-XL one-step at 1.85 on CIFAR-10, which beats every consistency model here.

## Limits

- The FID sample count, seeds and variance go unreported.
- Images only, and only unconditional or class-conditional data on small datasets.
- Continuous-time CT depends on forward-mode autodiff and EDM initialisation because of variance, and is left to future work.
- Only single-step ODE solvers were tried; multistep solvers are future work.
- Choosing time points assumes that FID is unimodal in the next time point.
- On some datasets GANs (StyleGAN-XL, StyleGAN2-ADA, BigGAN-deep) are still ahead of CT and CD.

## See Also

- [[Score-Based Generative Modeling Through SDEs]] — prerequisite-for
- [[SDEdit Guided Image Synthesis]] — related
- [[LPIPS Perceptual Similarity]] — prerequisite-for
- [[Diffusion and GAN Image Generation]] — prerequisite-for
