# OctoTools: An Agentic Framework with Extensible Tools for Complex Reasoning

**arXiv ID:** `arxiv:2502.11271`
**URL:** https://arxiv.org/abs/2502.11271
**Status:** analyzed
**Discovered:** 2025-02-16

## Authors

Pan Lu, Bowen Chen, Sheng Liu, Rahul Thapa, Joseph Boen, James Zou

## Abstract

Solving complex reasoning tasks may involve visual understanding, domain knowledge retrieval, numerical calculation, and multi-step reasoning. Existing methods augment large language models (LLMs) with external tools but are restricted to specialized domains, limited tool types, or require additional training data. In this paper, we introduce OctoTools, a training-free, user-friendly, and easily extensible open-source agentic framework designed to tackle complex reasoning across diverse domains. OctoTools introduces standardized tool cards to encapsulate tool functionality, a planner for both high-level and low-level planning, and an executor to carry out tool usage. We validate OctoTools' generality across 16 diverse tasks (including MathVista, MMLU-Pro, MedQA, and GAIA-Text), achieving substantial average accuracy gains of 9.3% over GPT-4o. Furthermore, OctoTools outperforms AutoGen, GPT-Functions and LangChain by up to 10.6% when given the same set of tools. Through comprehensive analysis and ablations, OctoTools demonstrates advantages in task planning, effective tool usage, and multi-step problem solving.

## Key Insights

- OctoTools achieves 9.3% average accuracy improvement over GPT-4o across 16 diverse reasoning tasks without requiring additional training
- The framework outperforms existing agentic systems (AutoGen, GPT-Functions, LangChain) by up to 10.6% when using the same tools
- Standardized tool cards enable easy extensibility and consistent tool integration across different domains
- The dual-level planning approach (high-level and low-level) effectively decomposes complex multi-step reasoning problems
- Training-free design allows immediate deployment and adaptation to new domains and tools
- The framework outperforms existing tool-augmented systems (AutoGen, GPT-Functions, LangChain) by up to 10.6% when using the same tools
- The dual-level planning approach (high-level and low-level) combined with an executor enables effective multi-step reasoning and tool orchestration
- The training-free nature makes it more practical and accessible compared to methods requiring specialized training data

## Analysis

**Summary:** OctoTools is a framework that helps AI language models solve complex problems by giving them access to external tools like calculators, search engines, and specialized knowledge bases. Unlike previous approaches, it works without additional training, can be easily extended with new tools, and works across many different types of problems. The system achieved nearly 10% better accuracy than GPT-4o across 16 different challenging tasks.

**Methodology:** The framework uses standardized tool cards to encapsulate tool functionality, implements a hierarchical planner for task decomposition, and employs an executor to carry out tool operations, evaluated across 16 diverse reasoning benchmarks including mathematical, medical, and general knowledge tasks.

**Strength Score:** 8/10

### Research Gaps

- Limited discussion of failure modes and when the framework struggles with certain types of reasoning tasks
- No analysis of computational costs and latency compared to baseline methods
- Unclear how the system handles tool conflicts or determines optimal tool selection when multiple tools could address the same subtask

**Tags:** agentic-ai, tool-augmented-llm, complex-reasoning, multi-step-planning, open-source-framework

## Provenance

- **Session:** `session_20260217_081940_e06ffd`
- **Agent:** anthropic_claude:claude-sonnet-4-5-20250929
- **Date:** 2026-02-17

## Files

- `analysis.json`
- `paper.json`

---
*Part of MACP Research Knowledge Tree*