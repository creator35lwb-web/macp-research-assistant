# RelayGen: Intra-Generation Model Switching for Efficient Reasoning

**arXiv ID:** `arxiv:2602.06454`
**URL:** https://huggingface.co/papers/2602.06454
**Status:** discovered
**Discovered:** 2026-02-10

## Authors

Jiwon Song, Yoongon Kim, Jae-Joon Kim

## Abstract

Large reasoning models (LRMs) achieve strong performance on complex reasoning tasks by generating long, multi-step reasoning trajectories, but inference-time scaling incurs substantial deployment cost. A key challenge is that generation difficulty varies within a single output, whereas existing efficiency-oriented approaches either ignore this intra-generation variation or rely on supervised token-level routing with high system complexity. We present RelayGen, a training-free, segment-level runtime model switching framework that exploits difficulty variation in long-form reasoning. Through offline analysis of generation uncertainty using token probability margins, we show that coarse-grained segment-level control is sufficient to capture difficulty transitions within a reasoning trajectory. RelayGen identifies model-specific switch cues that signal transitions to lower-difficulty segments and dynamically delegates their continuation to a smaller model, while preserving high-difficulty reasoning on the large model. Across multiple reasoning benchmarks, RelayGen substantially reduces inference latency while preserving most of the accuracy of large models. When combined with speculative decoding, RelayGen achieves up to 2.2times end-to-end speedup with less than 2\% accuracy degradation, without requiring additional training or learned routing components.

## Files

- `paper.json`

---
*Part of MACP Research Knowledge Tree*