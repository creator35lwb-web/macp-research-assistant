# Rolling Sink: Bridging Limited-Horizon Training and Open-Ended Testing in Autoregressive Video Diffusion

**arXiv ID:** `arxiv:2602.07775`
**URL:** https://huggingface.co/papers/2602.07775
**Status:** discovered
**Discovered:** 2026-02-10

## Authors

Haodong Li, Shaoteng Liu, Zhe Lin, Manmohan Chandraker

## Abstract

Recently, autoregressive (AR) video diffusion models has achieved remarkable performance. However, due to their limited training durations, a train-test gap emerges when testing at longer horizons, leading to rapid visual degradations. Following Self Forcing, which studies the train-test gap within the training duration, this work studies the train-test gap beyond the training duration, i.e., the gap between the limited horizons during training and open-ended horizons during testing. Since open-ended testing can extend beyond any finite training window, and long-video training is computationally expensive, we pursue a training-free solution to bridge this gap. To explore a training-free solution, we conduct a systematic analysis of AR cache maintenance. These insights lead to Rolling Sink. Built on Self Forcing (trained on only 5s clips), Rolling Sink effectively scales the AR video synthesis to ultra-long durations (e.g., 5-30 minutes at 16 FPS) at test time, with consistent subjects, stable colors, coherent structures, and smooth motions. As demonstrated by extensive experiments, Rolling Sink achieves superior long-horizon visual fidelity and temporal consistency compared to SOTA baselines. Project page: https://rolling-sink.github.io/

## Files

- `paper.json`

---
*Part of MACP Research Knowledge Tree*