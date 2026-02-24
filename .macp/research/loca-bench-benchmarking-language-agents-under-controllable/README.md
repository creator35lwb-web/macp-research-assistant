# LOCA-bench: Benchmarking Language Agents Under Controllable and Extreme Context Growth

**arXiv ID:** `arxiv:2602.07962`
**URL:** https://huggingface.co/papers/2602.07962
**Status:** discovered
**Discovered:** 2026-02-10

## Authors

Weihao Zeng, Yuzhen Huang, Junxian He

## Abstract

Large language models (LLMs) are increasingly capable of carrying out long-running, real-world tasks. However, as the amount of context grows, their reliability often deteriorates, a phenomenon known as "context rot". Existing long-context benchmarks primarily focus on single-step settings that evaluate a model's ability to retrieve information from a long snippet. In realistic scenarios, however, LLMs often need to act as agents that explore environments, follow instructions and plans, extract useful information, and predict correct actions under a dynamically growing context. To assess language agents in such settings, we introduce LOCA-bench (a benchmark for LOng-Context Agents). Given a task prompt, LOCA-bench leverages automated and scalable control of environment states to regulate the agent's context length. This design enables LOCA-bench to extend the context length potentially to infinity in a controlled way while keeping the underlying task semantics fixed. LOCA-bench evaluates language agents as a combination of models and scaffolds, including various context management strategies. While agent performance generally degrades as the environment states grow more complex, advanced context management techniques can substantially improve the overall success rate. We open-source LOCA-bench to provide a platform for evaluating models and scaffolds in long-context, agentic scenarios: https://github.com/hkust-nlp/LOCA-bench

## Files

- `paper.json`

---
*Part of MACP Research Knowledge Tree*