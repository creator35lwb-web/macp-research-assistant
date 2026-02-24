# Weak-Driven Learning: How Weak Agents make Strong Agents Stronger

**arXiv ID:** `arxiv:2602.08222`
**URL:** https://huggingface.co/papers/2602.08222
**Status:** analyzed
**Discovered:** 2026-02-10

## Authors

Zehao Chen, Gongxun Li, Tianxiang Ai, Yifei Li, Zixuan Huang, Wang Zhou, Fuzhen Zhuang, Xianglong Liu, Jianxin Li, Deqing Wang, Yikun Ban

## Abstract

As post-training optimization becomes central to improving large language models, we observe a persistent saturation bottleneck: once models grow highly confident, further training yields diminishing returns. While existing methods continue to reinforce target predictions, we find that informative supervision signals remain latent in models' own historical weak states. Motivated by this observation, we propose WMSS (Weak Agents Can Make Strong Agents Stronger), a post-training paradigm that leverages weak checkpoints to guide continued optimization. By identifying recoverable learning gaps via entropy dynamics and reinforcing them through compensatory learning, WMSS enables strong agents to improve beyond conventional post-training saturation. Experiments on mathematical reasoning and code generation datasets show that agents trained with our approach achieve effective performance improvements, while incurring zero additional inference cost.

## Key Insights

- Models experience saturation bottlenecks in post-training when they become overly confident, leading to diminishing returns from continued training
- Historical weak checkpoints of a model contain valuable information about recoverable learning gaps that can guide further optimization
- Using entropy dynamics to identify where weak and strong model versions differ enables targeted compensatory learning
- The approach achieves performance improvements on mathematical reasoning and code generation tasks without increasing inference costs

## Analysis

**Summary:** This paper addresses the problem of diminishing returns when training large language models that have already become highly confident in their predictions. The authors propose a method called WMSS that uses earlier, weaker versions of the model to identify learning gaps and guide further training, enabling continued improvement beyond typical performance plateaus without adding computational cost during inference.

**Methodology:** The method identifies recoverable learning gaps by analyzing entropy differences between weak historical checkpoints and strong current models, then uses compensatory learning to reinforce these gaps during continued post-training optimization.

**Strength Score:** 7/10

### Research Gaps

- Limited evaluation to only mathematical reasoning and code generation domains; broader task coverage needed
- Unclear how the method scales with different model sizes and architectures
- No detailed analysis of computational overhead during training or storage requirements for maintaining weak checkpoints

**Tags:** large-language-models, post-training-optimization, model-training, mathematical-reasoning, code-generation

## Provenance

- **Session:** `session_20260217_040425_21847e`
- **Agent:** anthropic_claude:claude-sonnet-4-5-20250929
- **Date:** 2026-02-17

## Files

- `analysis.json`
- `paper.json`

---
*Part of MACP Research Knowledge Tree*