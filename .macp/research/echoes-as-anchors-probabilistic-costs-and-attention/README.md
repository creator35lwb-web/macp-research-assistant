# Echoes as Anchors: Probabilistic Costs and Attention Refocusing in LLM Reasoning

**arXiv ID:** `arxiv:2602.06600`
**URL:** https://huggingface.co/papers/2602.06600
**Status:** discovered
**Discovered:** 2026-02-10

## Authors

Zhuoyuan Hao, Zhuo Li, Wu Li, Fangming Liu, Min Zhang, Jing Li

## Abstract

Test-time compute allocation in large reasoning models (LRMs) is widely used and has applications in mathematical problem solving, code synthesis, and planning. Recent work has addressed this problem by scaling self-consistency and parallel thinking, adding generic ``thinking tokens'' and prompting models to re-read the question before answering. Unfortunately, these approaches either inject task-agnostic tokens or mandate heuristics that do not explain -- and often ignore -- the spontaneous repetition that many LRMs exhibit at the head of their internal chains. In contrast, we analyze and harness the model's tendency to restate the question, which we term the Echo of Prompt (EOP), as a front-loaded, compute-shaping mechanism. We formalize its probabilistic cost by casting echo removal as rejection-based conditioning and defining the Echo Likelihood Gap ΔL as a computable proxy. This provides the missing theoretical link that links early repetition to likelihood gains and downstream accuracy. However, it does not by itself specify how to exploit EOP. Consequently, we develop Echo-Distilled SFT (ED-SFT) to instill an ``echo-then-reason'' pattern through supervised finetuning, and Echoic Prompting (EP) to re-ground the model mid-trace without training. While promising, quantifying benefits beyond verbosity is non-trivial. Therefore, we conduct length and suffix-controlled likelihood analyses together with layer-wise attention studies, showing that EOP increases answer to answer-prefix attention in middle layers, consistent with an attention refocusing mechanism. We evaluate on GSM8K, MathQA, Hendrycks-MATH, AIME24, and MATH-500 under identical decoding settings and budgets, and find consistent gains over baselines. Code is available at https://github.com/hhh2210/echoes-as-anchors.

## Files

- `paper.json`

---
*Part of MACP Research Knowledge Tree*