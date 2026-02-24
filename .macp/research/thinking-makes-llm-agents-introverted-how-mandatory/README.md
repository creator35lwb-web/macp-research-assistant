# Thinking Makes LLM Agents Introverted: How Mandatory Thinking Can Backfire in User-Engaged Agents

**arXiv ID:** `arxiv:2602.07796`
**URL:** https://huggingface.co/papers/2602.07796
**Status:** discovered
**Discovered:** 2026-02-10

## Authors

Jiatong Li, Changdae Oh, Hyeong Kyu Choi, Jindong Wang, Sharon Li

## Abstract

Eliciting reasoning has emerged as a powerful technique for improving the performance of large language models (LLMs) on complex tasks by inducing thinking. However, their effectiveness in realistic user-engaged agent scenarios remains unclear. In this paper, we conduct a comprehensive study on the effect of explicit thinking in user-engaged LLM agents. Our experiments span across seven models, three benchmarks, and two thinking instantiations, and we evaluate them through both a quantitative response taxonomy analysis and qualitative failure propagation case studies. Contrary to expectations, we find that mandatory thinking often backfires on agents in user-engaged settings, causing anomalous performance degradation across various LLMs. Our key finding reveals that thinking makes agents more ``introverted'' by shortening responses and reducing information disclosure to users, which weakens agent-user information exchange and leads to downstream task failures. Furthermore, we demonstrate that explicitly prompting for information disclosure reliably improves performance across diverse model families, suggesting that proactive transparency is a vital lever for agent optimization. Overall, our study suggests that information transparency awareness is a crucial yet underexplored perspective for the future design of reasoning agents in real-world scenarios. Our code is available at https://github.com/deeplearning-wisc/Thinking-Agent.

## Files

- `paper.json`

---
*Part of MACP Research Knowledge Tree*