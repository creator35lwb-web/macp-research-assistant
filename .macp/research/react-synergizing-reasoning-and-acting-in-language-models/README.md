# ReAct: Synergizing Reasoning and Acting in Language Models

**arXiv ID:** `arxiv:2210.03629`
**URL:** https://arxiv.org/abs/2210.03629
**Status:** analyzed
**Discovered:** 2022-10-06

## Authors

Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao

## Abstract

While large language models (LLMs) have demonstrated impressive capabilities across tasks in language understanding and interactive decision making, their abilities for reasoning (e.g. chain-of-thought prompting) and acting (e.g. action plan generation) have primarily been studied as separate topics. In this paper, we explore the use of LLMs to generate both reasoning traces and task-specific actions in an interleaved manner, allowing for greater synergy between the two: reasoning traces help the model induce, track, and update action plans as well as handle exceptions, while actions allow it to interface with external sources, such as knowledge bases or environments, to gather additional information. We apply our approach, named ReAct, to a diverse set of language and decision making tasks and demonstrate its effectiveness over state-of-the-art baselines, as well as improved human interpretability and trustworthiness over methods without reasoning or acting components. Concretely, on question answering (HotpotQA) and fact verification (Fever), ReAct overcomes issues of hallucination and error propagation prevalent in chain-of-thought reasoning by interacting with a simple Wikipedia API, and generates human-like task-solving trajectories that are more interpretable than baselines without reasoning traces. On two interactive decision making benchmarks (ALFWorld and WebShop), ReAct outperforms imitation and reinforcement learning methods by an absolute success rate of 34% and 10% respectively, while being prompted with only one or two in-context examples. Project site with code: https://react-lm.github.io

## Key Insights

- Interleaving reasoning traces with task-specific actions creates synergy where reasoning guides action planning and actions provide external information to improve reasoning
- ReAct reduces hallucination and error propagation in chain-of-thought reasoning by grounding responses in external knowledge sources through API interactions
- The method achieves 34% and 10% absolute success rate improvements over imitation and reinforcement learning on interactive decision-making tasks with minimal in-context examples
- Generated trajectories are more interpretable and human-like compared to methods using only reasoning or only acting
- The approach works effectively across diverse tasks including question answering, fact verification, and interactive decision making with simple prompting
- Interleaving reasoning traces with task-specific actions creates synergy where reasoning helps plan and handle exceptions while actions gather external information
- ReAct reduces hallucination and error propagation in chain-of-thought reasoning by grounding responses through interaction with external knowledge sources like Wikipedia
- The method achieves substantial improvements over baselines: 34% higher success rate than imitation learning on ALFWorld and 10% higher on WebShop with minimal in-context examples
- ReAct generates more interpretable and human-like task-solving trajectories compared to methods using only reasoning or only acting

## Analysis

**Summary:** This paper introduces ReAct, a method that combines reasoning and acting in large language models by having them generate both thought processes and actions in an interleaved way. The approach allows models to reason about tasks while also interacting with external sources like Wikipedia or environments to gather information. ReAct significantly outperforms existing methods on question answering, fact verification, and interactive decision-making tasks while being more interpretable.

**Methodology:** The authors prompt large language models to generate interleaved reasoning traces and actions, then evaluate performance on question answering (HotpotQA, Fever) and interactive decision-making tasks (ALFWorld, WebShop) using few-shot in-context learning.

**Strength Score:** 9/10

### Research Gaps

- Limited exploration of how the approach scales to more complex multi-step tasks or longer interaction sequences
- Lack of analysis on computational costs and latency implications of interleaved reasoning and acting
- Insufficient investigation of failure modes and when the synergy between reasoning and acting breaks down

**Tags:** large-language-models, reasoning, action-planning, chain-of-thought, question-answering, interactive-agents

## Provenance

- **Session:** `session_20260217_040407_8a3e4f`
- **Agent:** anthropic_claude:claude-sonnet-4-5-20250929
- **Date:** 2026-02-17

## Files

- `analysis.json`
- `paper.json`

---
*Part of MACP Research Knowledge Tree*