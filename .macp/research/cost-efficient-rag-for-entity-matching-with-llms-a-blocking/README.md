# Cost-Efficient RAG for Entity Matching with LLMs: A Blocking-based Exploration

**arXiv ID:** `arxiv:2602.05708`
**URL:** https://huggingface.co/papers/2602.05708
**Status:** discovered
**Discovered:** 2026-02-10

## Authors

Chuangtao Ma, Zeyu Zhang, Arijit Khan, Sebastian Schelter, Paul Groth

## Abstract

Retrieval-augmented generation (RAG) enhances LLM reasoning in knowledge-intensive tasks, but existing RAG pipelines incur substantial retrieval and generation overhead when applied to large-scale entity matching. To address this limitation, we introduce CE-RAG4EM, a cost-efficient RAG architecture that reduces computation through blocking-based batch retrieval and generation. We also present a unified framework for analyzing and evaluating RAG systems for entity matching, focusing on blocking-aware optimizations and retrieval granularity. Extensive experiments suggest that CE-RAG4EM can achieve comparable or improved matching quality while substantially reducing end-to-end runtime relative to strong baselines. Our analysis further reveals that key configuration parameters introduce an inherent trade-off between performance and overhead, offering practical guidance for designing efficient and scalable RAG systems for entity matching and data integration.

## Files

- `paper.json`

---
*Part of MACP Research Knowledge Tree*