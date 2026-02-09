# MACP Ethical Use Guidelines

**This document outlines the mandatory ethical conditions for using and contributing to the MACP-Powered AI Research Assistant, as stipulated by the Z-Agent (Guardian) during the VerifiMind-PEAS Trinity Validation.**

---

## 1. Core Principle: Transparency and Accountability

The primary goal of MACP is to **increase** transparency and accountability in AI-assisted research, not to obscure it. All uses of this protocol must uphold this principle. The audit trail created by MACP should be considered a permanent, public record of the research process (when used in public repositories).

## 2. Mandatory Condition: Mitigation of Dual-Use Risks

> **Z-Agent Finding:** *"The protocol could be used to accelerate research into dangerous or unethical domains... or to create highly convincing, yet biased, research narratives."

**MANDATORY MITIGATION:**

1.  **Explicit Domain Declaration:** When initiating a research project using MACP, you are encouraged to declare the research domain and its intended purpose in your project's README. This provides context for reviewers and the community.
2.  **Prohibition of Malicious Use:** This protocol and its associated tools **must not** be used for research intended to cause harm, spread misinformation, or engage in illegal activities. This includes, but is not limited to, the development of weaponry, surveillance technologies that violate human rights, or propaganda.
3.  **Bias Awareness:** Be aware that the selection of papers, the insights extracted, and the agents used can introduce bias. Users of this protocol have a responsibility to critically assess their own workflows for potential bias and to be transparent about their methodology.

## 3. Mandatory Condition: Democratic and Equitable Access

> **Z-Agent Finding:** *"The system could centralize power by giving a significant advantage to those with access to multiple high-end AI models..."

**MANDATORY MITIGATION:**

1.  **Support for Open-Source Models:** The MACP framework is designed to be model-agnostic. Future development of automation tools (Phase 2) **must** prioritize support for open-source and locally-runnable language models to ensure that access is not limited to those with expensive commercial API keys.
2.  **Public-First Methodology:** The protocol itself is, and must remain, fully open-source under the MIT License. The core value comes from the methodology, not access to any single proprietary tool.
3.  **Community-Driven Examples:** We encourage the community to contribute examples of MACP being used with a diverse range of AI tools, including free and open-source alternatives, to demonstrate its universal applicability.

## 4. Mandatory Condition: Data Privacy and Confidentiality

> **Z-Agent Finding:** *"The protocol stores potentially sensitive research insights in plain-text JSON files..."

**MANDATORY MITIGATION:**

1.  **Private by Default:** As also mandated by the CS-Agent (Security), all research projects containing sensitive, proprietary, or pre-publication information **must** be conducted in **private GitHub repositories**.
2.  **No Personal Identifiable Information (PII):** Do not store any PII about research subjects, collaborators, or yourself within the `.macp/` files. The protocol is for tracking research artifacts, not people.
3.  **Future Encryption:** The long-term roadmap for MACP includes plans for field-level encryption for sensitive insights. Until then, the use of private repositories is the primary mechanism for ensuring confidentiality.

---

By using or contributing to the MACP-Powered AI Research Assistant, you agree to abide by these ethical guidelines. Failure to do so may result in being excluded from the community and having your contributions rejected.
