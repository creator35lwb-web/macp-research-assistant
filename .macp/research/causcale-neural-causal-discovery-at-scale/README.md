# CauScale: Neural Causal Discovery at Scale

**arXiv ID:** `arxiv:2602.08629`
**URL:** https://huggingface.co/papers/2602.08629
**Status:** discovered
**Discovered:** 2026-02-10

## Authors

Bo Peng, Sirui Chen, Jiaguo Tian, Yu Qiao, Chaochao Lu

## Abstract

Causal discovery is essential for advancing data-driven fields such as scientific AI and data analysis, yet existing approaches face significant time- and space-efficiency bottlenecks when scaling to large graphs. To address this challenge, we present CauScale, a neural architecture designed for efficient causal discovery that scales inference to graphs with up to 1000 nodes. CauScale improves time efficiency via a reduction unit that compresses data embeddings and improves space efficiency by adopting tied attention weights to avoid maintaining axis-specific attention maps. To keep high causal discovery accuracy, CauScale adopts a two-stream design: a data stream extracts relational evidence from high-dimensional observations, while a graph stream integrates statistical graph priors and preserves key structural signals. CauScale successfully scales to 500-node graphs during training, where prior work fails due to space limitations. Across testing data with varying graph scales and causal mechanisms, CauScale achieves 99.6% mAP on in-distribution data and 84.4% on out-of-distribution data, while delivering 4-13,000 times inference speedups over prior methods. Our project page is at https://github.com/OpenCausaLab/CauScale.

## Files

- `paper.json`

---
*Part of MACP Research Knowledge Tree*