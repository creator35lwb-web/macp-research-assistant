# NanoQuant: Efficient Sub-1-Bit Quantization of Large Language Models

**arXiv ID:** `arxiv:2602.06694`
**URL:** https://huggingface.co/papers/2602.06694
**Status:** discovered
**Discovered:** 2026-02-10

## Authors

Hyochan Chong, Dongkyu Kim, Changdong Kim, Minseop Choi

## Abstract

Weight-only quantization has become a standard approach for efficiently serving large language models (LLMs). However, existing methods fail to efficiently compress models to binary (1-bit) levels, as they either require large amounts of data and compute or incur additional storage. In this work, we propose NanoQuant, the first post-training quantization (PTQ) method to compress LLMs to both binary and sub-1-bit levels. NanoQuant formulates quantization as a low-rank binary factorization problem, and compresses full-precision weights to low-rank binary matrices and scales. Specifically, it utilizes an efficient alternating direction method of multipliers (ADMM) method to precisely initialize latent binary matrices and scales, and then tune the initialized parameters through a block and model reconstruction process. Consequently, NanoQuant establishes a new Pareto frontier in low-memory post-training quantization, achieving state-of-the-art accuracy even at sub-1-bit compression rates. NanoQuant makes large-scale deployment feasible on consumer hardware. For example, it compresses Llama2-70B by 25.8times in just 13 hours on a single H100, enabling a 70B model to operate on a consumer 8 GB GPU.

## Files

- `paper.json`

---
*Part of MACP Research Knowledge Tree*