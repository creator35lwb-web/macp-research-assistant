# Optimal Turkish Subword Strategies at Scale: Systematic Evaluation of Data, Vocabulary, Morphology Interplay

**arXiv ID:** `arxiv:2602.06942`
**URL:** https://huggingface.co/papers/2602.06942
**Status:** discovered
**Discovered:** 2026-02-10

## Authors

Duygu Altinok

## Abstract

Tokenization is a pivotal design choice for neural language modeling in morphologically rich languages (MRLs) such as Turkish, where productive agglutination challenges both vocabulary efficiency and morphological fidelity. Prior studies have explored tokenizer families and vocabulary sizes but typically (i) vary vocabulary without systematically controlling the tokenizer's training corpus, (ii) provide limited intrinsic diagnostics, and (iii) evaluate a narrow slice of downstream tasks. We present the first comprehensive, principled study of Turkish subword tokenization; a "subwords manifest", that jointly varies vocabulary size and tokenizer training corpus size (data and vocabulary coupling), compares multiple tokenizer families under matched parameter budgets (WordPiece, morphology level, and character baselines), and evaluates across semantic (NLI, STS, sentiment analysis, NER), syntactic (POS, dependency parsing), and morphology-sensitive probes. To explain why tokenizers succeed or fail, we introduce a morphology-aware diagnostic toolkit that goes beyond coarse aggregates to boundary-level micro/macro F1, decoupled lemma atomicity vs. surface boundary hits, over/under-segmentation indices, character/word edit distances (CER/WER), continuation rates, and affix-type coverage and token-level atomicity. Our contributions are fourfold: (i) a systematic investigation of the vocabulary-corpus-success triad; (ii) a unified, morphology-aware evaluation framework linking intrinsic diagnostics to extrinsic outcomes; (iii) controlled comparisons identifying when character-level and morphology-level tokenization pay off; and (iv) an open-source release of evaluation code, tokenizer pipelines, and models. As the first work of its kind, this "subwords manifest" delivers actionable guidance for building effective tokenizers in MRLs and establishes a reproducible foundation for future research.

## Files

- `paper.json`

---
*Part of MACP Research Knowledge Tree*