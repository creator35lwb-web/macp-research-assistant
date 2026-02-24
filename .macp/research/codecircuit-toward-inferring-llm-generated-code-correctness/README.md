# CodeCircuit: Toward Inferring LLM-Generated Code Correctness via Attribution Graphs

**arXiv ID:** `arxiv:2602.07080`
**URL:** https://huggingface.co/papers/2602.07080
**Status:** discovered
**Discovered:** 2026-02-10

## Authors

Yicheng He, Zheng Zhao, Zhou Kaiyu, Bryan Dai, Jie Fu, Yonghui Yang

## Abstract

Current paradigms for code verification rely heavily on external mechanisms-such as execution-based unit tests or auxiliary LLM judges-which are often labor-intensive or limited by the judging model's own capabilities. This raises a fundamental, yet unexplored question: Can an LLM's functional correctness be assessed purely from its internal computational structure? Our primary objective is to investigate whether the model's neural dynamics encode internally decodable signals that are predictive of logical validity during code generation. Inspired by mechanistic interpretability, we propose to treat code verification as a mechanistic diagnostic task, mapping the model's explicit algorithmic trajectory into line-level attribution graphs. By decomposing complex residual flows, we aim to identify the structural signatures that distinguish sound reasoning from logical failure within the model's internal circuits. Analysis across Python, C++, and Java confirms that intrinsic correctness signals are robust across diverse syntaxes. Topological features from these internal graphs predict correctness more reliably than surface heuristics and enable targeted causal interventions to fix erroneous logic. These findings establish internal introspection as a decodable property for verifying generated code. Our code is at https:// github.com/bruno686/CodeCircuit.

## Files

- `paper.json`

---
*Part of MACP Research Knowledge Tree*