# Baichuan-M3: Modeling Clinical Inquiry for Reliable Medical Decision-Making

**arXiv ID:** `arxiv:2602.06570`
**URL:** https://arxiv.org/abs/2602.06570
**Status:** analyzed
**Discovered:** 2026-02-06

## Authors

Baichuan-M3 Team,  :, Chengfeng Dou, Fan Yang, Fei Li, Jiyuan Jia, Qiang Ju, Shuai Wang, Tianpeng Li, Xiangrong Zeng, Yijie Zhou, Hongda Zhang, Jinyang Tai, Linzhuang Sun, Peidong Guo, Yichuan Mo, Xiaochuan Wang, Hengfu Cui, Zhishou Zhang

## Abstract

We introduce Baichuan-M3, a medical-enhanced large language model engineered to shift the paradigm from passive question-answering to active, clinical-grade decision support. Addressing the limitations of existing systems in open-ended consultations, Baichuan-M3 utilizes a specialized training pipeline to model the systematic workflow of a physician. Key capabilities include: (i) proactive information acquisition to resolve ambiguity; (ii) long-horizon reasoning that unifies scattered evidence into coherent diagnoses; and (iii) adaptive hallucination suppression to ensure factual reliability. Empirical evaluations demonstrate that Baichuan-M3 achieves state-of-the-art results on HealthBench, the newly introduced HealthBench-Hallu and ScanBench, significantly outperforming GPT-5.2 in clinical inquiry, advisory and safety. The models are publicly available at https://huggingface.co/collections/baichuan-inc/baichuan-m3.

## Key Insights

- Shifts medical AI from passive question-answering to active clinical inquiry, mimicking how physicians systematically gather patient information
- Implements three core capabilities: proactive information gathering, long-horizon reasoning to connect scattered evidence, and adaptive hallucination suppression for factual accuracy
- Achieves state-of-the-art performance on HealthBench, HealthBench-Hallu, and ScanBench, outperforming GPT-5.2 in clinical inquiry, advisory quality, and safety
- Uses specialized training pipeline to model systematic physician workflows for more reliable medical decision support

## Analysis

**Summary:** Baichuan-M3 is a new AI medical assistant that acts more like a real doctor by asking questions to gather information, rather than just answering patient questions. It can actively investigate symptoms, reason through complex medical cases, and avoid making up false information. The system outperforms existing AI models including GPT-5.2 on medical decision-making tasks.

**Methodology:** The model employs a specialized training pipeline that teaches the system to follow physician-like workflows, incorporating proactive questioning, evidence synthesis, and hallucination control mechanisms.

**Strength Score:** 8/10

### Research Gaps

- Limited details provided about the specific training data, architecture modifications, and training procedures used in the specialized pipeline
- No discussion of real-world clinical validation, regulatory considerations, or deployment challenges in actual healthcare settings
- Lack of analysis on potential failure modes, edge cases, or comparison with human physician performance

**Tags:** medical-ai, large-language-models, clinical-decision-support, healthcare-nlp, hallucination-mitigation

## Provenance

- **Session:** `session_20260217_040304_26b5e9`
- **Agent:** anthropic_claude:claude-sonnet-4-5-20250929
- **Date:** 2026-02-17

## Files

- `analysis.json`
- `paper.json`

---
*Part of MACP Research Knowledge Tree*