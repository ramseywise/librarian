---
title: Food-101 and car-197 Fine-Grained Datasets
tags: [multimodal, reference]
summary: "Food-101 (101,000 images, 101 dish classes) and car-197 (16,185 images, 197 car models) are two fine-grained recognition datasets from 2013-2014 papers; both papers' own methods were hand-engineered and, on the main sets, did not beat a CNN or a plain 2D baseline (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-bossard-2014-food-101-mining-discriminative-components.md
  - data/raw/papers/2026-11-08-krause-2013-3d-object-representations-fine-grained.md
  - data/raw/papers/2026-11-08-nilsback-2008-automated-flower-classification-over-large.md
---

# Food-101 and car-197 Fine-Grained Datasets

Two papers from 2013-2014 each introduced a fine-grained dataset alongside a hand-engineered method. All results below come from those papers and are self-reported; the car-197 extraction cautions against setting its accuracies beside later CNN work.

## Food-101 (Bossard et al., ECCV 2014)

The set holds 101,000 images from foodspotting.com across 101 dish classes; each class has 750 uncleaned training images and 250 hand-cleaned test images. The paper's method, RFDC, fits a Random Forest to superpixel features and keeps the discriminative leaves as components. A linear SVM is then trained per component, and a multi-class SVM classifies from the spatially pooled component scores.

- RFDC reaches 50.76% average accuracy with 30 trees, depth 5 and 20 components per class. Improved Fisher Vectors get 38.88%, bag of words 28.51%, the superpixel re-implementation of an earlier mining method (MLDS) 42.63%.
- An AlexNet-style CNN is 5.64 points ahead of RFDC, though that CNN was trained for six days on one Tesla K20X.
- The forest used directly as a classifier gets 32.72%, so the mining plus component SVMs matter. Gains saturate beyond 20 components per class. On MIT-Indoor RFDC reaches 54.40% to 58.36%, which is under IFV (60.77) and DMS (64.03).
- Full training takes about 250 CPU hours and classifying one image about 0.8 seconds on 8 cores.

## car-197 (Krause et al., ICCVW 2013)

car-197 has 16,185 images of 197 car models (Flickr, Google and Bing, verified on Mechanical Turk); BMW-10 is a small set of 512 images the authors collected by hand, covering 10 BMW sedan models. The paper lifts spatial pyramid matching and BubbleBank features into 3D object space by fitting 41 CAD models.

- On car-197, plain 2D SPM is the best single method at 69.5%, ahead of the 3D BubbleBank variant (67.6%) and 3D SPM (65.6%); stacking four representations gives 75.5%.
- On the 14-class car-types set the 3D BubbleBank variant reaches 94.5%, 1 point over structDPM; on BMW-10 it gets 66.1% (76.0% with flipped training images) against 58.7% for 2D BubbleBank.
- The authors attribute the car-197 result to coarse categories such as large pickups being under-represented in the CAD models.

## Flowers-103 (Nilsback and Zisserman, ICVGIP 2008)

A third fine-grained set from the same era: 8,189 images in 103 flower classes, with 10 training and 10 validation images per class (1,030 each) and the remaining 6,129 as test. The venue is inferred from the DOI, not printed in the PDF. The method segments flowers (iterative graph cut plus a petal shape model), computes four bag-of-visual-words histograms (SIFT inside the flower, SIFT on its boundary, HOG, HSV colour). A one-vs-rest SVM then uses a sum of chi-squared exponential kernels, where a convex multiple-kernel method learns the weight each class gives each kernel.

- Combining all four features gives the best per-class-averaged test rate on the 103 classes (the extraction strips the figure); internal SIFT is the best single feature, and colour alone reaches 43.0% (self-reported).
- On the earlier 17-class set the paper reports a best-to-date 88.33% with iterative segmentation and 85.1% with graph-cut segmentation; the multiple-kernel method on the older features gives 82.55% against 71.76% for nearest neighbour.

## Limits

- Food-101 training labels are deliberately noisy and the noise is not measured; the test-cleaning procedure is not described. One run per method; the extraction notes that the CNN baseline is a 2012-era model; no code or weights beyond the dataset.
- Flowers-103: the paper says 103 classes throughout, and the extraction notes the later widely used 102-class release is a different dataset not described here. The number of 17-class trials behind the reported spreads is unstated, no hardware or SVM settings are given, and features are hand-designed with only 10 training images per class.
- car-197 and BMW-10 split sizes and class lists are absent from the paper; the method needs CAD models and handles rigid objects only; the 3D reconstruction is qualitative with spurious points; single runs.

## See Also
- [[Microsoft COCO]] — related (another dataset paper of the same era)
- [[Visual Instruction Tuning and Tool-Using VLMs]] — related
