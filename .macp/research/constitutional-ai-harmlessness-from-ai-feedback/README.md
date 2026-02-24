# Constitutional AI: Harmlessness from AI Feedback

**arXiv ID:** `arxiv:2212.08073`
**URL:** https://arxiv.org/abs/2212.08073
**Status:** analyzed
**Discovered:** 2022-12-15

## Authors

Yuntao Bai, Saurav Kadavath, Sandipan Kundu, Amanda Askell, Jackson Kernion, Andy Jones, Anna Chen, Anna Goldie, Azalia Mirhoseini, Cameron McKinnon, Carol Chen, Catherine Olsson, Christopher Olah, Danny Hernandez, Dawn Drain, Deep Ganguli, Dustin Li, Eli Tran-Johnson, Ethan Perez, Jamie Kerr, Jared Mueller, Jeffrey Ladish, Joshua Landau, Kamal Ndousse, Kamile Lukosuite, Liane Lovitt, Michael Sellitto, Nelson Elhage, Nicholas Schiefer, Noemi Mercado, Nova DasSarma, Robert Lasenby, Robin Larson, Sam Ringer, Scott Johnston, Shauna Kravec, Sheer El Showk, Stanislav Fort, Tamera Lanham, Timothy Telleen-Lawton, Tom Conerly, Tom Henighan, Tristan Hume, Samuel R. Bowman, Zac Hatfield-Dodds, Ben Mann, Dario Amodei, Nicholas Joseph, Sam McCandlish, Tom Brown, Jared Kaplan

## Abstract

As AI systems become more capable, we would like to enlist their help to supervise other AIs. We experiment with methods for training a harmless AI assistant through self-improvement, without any human labels identifying harmful outputs. The only human oversight is provided through a list of rules or principles, and so we refer to the method as 'Constitutional AI'. The process involves both a supervised learning and a reinforcement learning phase. In the supervised phase we sample from an initial model, then generate self-critiques and revisions, and then finetune the original model on revised responses. In the RL phase, we sample from the finetuned model, use a model to evaluate which of the two samples is better, and then train a preference model from this dataset of AI preferences. We then train with RL using the preference model as the reward signal, i.e. we use 'RL from AI Feedback' (RLAIF). As a result we are able to train a harmless but non-evasive AI assistant that engages with harmful queries by explaining its objections to them. Both the SL and RL methods can leverage chain-of-thought style reasoning to improve the human-judged performance and transparency of AI decision making. These methods make it possible to control AI behavior more precisely and with far fewer human labels.

## Key Insights

- AI systems can be trained to be harmless using only a list of principles rather than extensive human labeling of harmful outputs
- The method combines supervised learning (self-critique and revision) with reinforcement learning from AI feedback (RLAIF) instead of human feedback
- The approach produces AI assistants that engage with harmful queries by explaining objections rather than refusing to respond
- Chain-of-thought reasoning can be incorporated to improve transparency and performance of AI decision-making
- The technique significantly reduces the need for human oversight while maintaining control over AI behavior

## Analysis

**Summary:** This paper introduces Constitutional AI, a method for training AI assistants to be harmless without requiring humans to label harmful content. Instead of human feedback, the system uses a set of principles (a 'constitution') to guide an AI to critique and improve its own responses, then uses AI-generated preferences to train the model through reinforcement learning.

**Methodology:** A two-phase approach using supervised learning for self-critique and revision of responses, followed by reinforcement learning trained on AI-generated preference comparisons based on constitutional principles.

**Strength Score:** 9/10

### Research Gaps

- Limited discussion of how to select or validate the constitutional principles themselves
- Potential for the AI to develop unexpected interpretations of the principles without human oversight
- Scalability concerns when applying this method to more complex or nuanced ethical scenarios

**Tags:** constitutional-ai, ai-safety, reinforcement-learning, ai-alignment, self-improvement

## Provenance

- **Session:** `session_20260217_040322_177edf`
- **Agent:** anthropic_claude:claude-sonnet-4-5-20250929
- **Date:** 2026-02-17

## Files

- `analysis.json`
- `paper.json`

---
*Part of MACP Research Knowledge Tree*