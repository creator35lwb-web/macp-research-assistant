# Self-Refine: Iterative Refinement with Self-Feedback

**arXiv ID:** `arxiv:2303.17651`
**URL:** https://arxiv.org/abs/2303.17651
**Status:** analyzed
**Discovered:** 2023-03-30

## Authors

Aman Madaan, Niket Tandon, Prakhar Gupta, Skyler Hallinan, Luyu Gao, Sarah Wiegreffe, Uri Alon, Nouha Dziri, Shrimai Prabhumoye, Yiming Yang, Shashank Gupta, Bodhisattwa Prasad Majumder, Katherine Hermann, Sean Welleck, Amir Yazdanbakhsh, Peter Clark

## Abstract

Like humans, large language models (LLMs) do not always generate the best output on their first try. Motivated by how humans refine their written text, we introduce Self-Refine, an approach for improving initial outputs from LLMs through iterative feedback and refinement. The main idea is to generate an initial output using an LLMs; then, the same LLMs provides feedback for its output and uses it to refine itself, iteratively. Self-Refine does not require any supervised training data, additional training, or reinforcement learning, and instead uses a single LLM as the generator, refiner, and feedback provider. We evaluate Self-Refine across 7 diverse tasks, ranging from dialog response generation to mathematical reasoning, using state-of-the-art (GPT-3.5, ChatGPT, and GPT-4) LLMs. Across all evaluated tasks, outputs generated with Self-Refine are preferred by humans and automatic metrics over those generated with the same LLM using conventional one-step generation, improving by ~20% absolute on average in task performance. Our work demonstrates that even state-of-the-art LLMs like GPT-4 can be further improved at test time using our simple, standalone approach.

## Key Insights

- Large language models can effectively critique and improve their own outputs without requiring additional training, supervised data, or reinforcement learning
- Iterative self-refinement achieves approximately 20% absolute improvement in task performance across diverse applications including dialogue, math reasoning, and text generation
- The same language model can successfully serve three roles simultaneously: initial generator, feedback provider, and output refiner
- Even state-of-the-art models like GPT-4 benefit from this test-time improvement approach, demonstrating that first-pass outputs are often suboptimal

## Analysis

**Summary:** This paper introduces Self-Refine, a method that improves AI language model outputs by having the model critique and refine its own responses multiple times, similar to how humans edit their writing. The approach requires no additional training data or models, using a single language model to generate, provide feedback, and refine outputs iteratively. Testing across 7 different tasks showed approximately 20% improvement over standard single-pass generation.

**Methodology:** The approach uses a single LLM in an iterative loop where it first generates an initial output, then provides feedback on that output, and finally refines the output based on the feedback, repeating until convergence or a stopping criterion is met.

**Strength Score:** 8/10

### Research Gaps

- Limited analysis of when and why the self-refinement process fails or produces worse outputs than initial generation
- No investigation of computational cost trade-offs between multiple refinement iterations versus using larger or multiple models
- Lack of exploration on how the approach scales with different model sizes and capabilities below state-of-the-art

**Tags:** large-language-models, iterative-refinement, self-improvement, prompt-engineering, test-time-optimization

## Provenance

- **Session:** `session_20260217_040334_b3ca8a`
- **Agent:** anthropic_claude:claude-sonnet-4-5-20250929
- **Date:** 2026-02-17

## Files

- `analysis.json`
- `paper.json`

---
*Part of MACP Research Knowledge Tree*