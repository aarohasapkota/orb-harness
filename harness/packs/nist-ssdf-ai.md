---
id: nist-ssdf-ai
version: "2024-07+harness.1"
source: "NIST SP 800-218A, Secure Software Development Practices for Generative AI and Dual-Use Foundation Models (SSDF Community Profile), July 2024"
priority: 4-baseline
applies_when: [ai]
agents: ["*"]
requires: [nist-ssdf]
---
# NIST SP 800-218A AI profile pack (supplements nist-ssdf; never standalone)

| ID | Strength | AI practice (paraphrased) | Harness check | Verifier |
|---|---|---|---|---|
| AI-PO.1 | MUST | Security requirements cover models, model interfaces, prompts, tools, datasets, configuration, and AI artifact handling. | REQ-S items for injection, tool authorization, exfiltration, provenance. | requirements |
| AI-PS.1.1 | MUST | Protect AI models, weights, pipelines, reward models, training/test/fine-tune/alignment data, and model configuration from unauthorized access and modification. | Artifact inventory with access/integrity controls; nothing leaks into logs/tests/evidence. | ai-agent-security |
| AI-PS.1.2 | SHOULD | Version and integrity-protect prompts, agent instructions, tool definitions and permissions. | Versioned in repo; hashes recorded. | ai-agent-security |
| AI-PS.2 | SHOULD | Use hashes/signatures for AI models, components, artifacts, documentation. | artifact-hash evidence. | release-integrity |
| AI-PW.3 | MUST (new data) | Verify integrity and provenance of AI development data before use; record unknown provenance explicitly. | provenance table with `unknown` where applicable; poisoning indicators considered. | ai-agent-security |
| AI-PW.4.4 | MUST | Verify integrity, provenance, security and malicious-content scanning of acquired AI components (models, adapters, datasets) before use. | vetting record; safe loader/format check. | dependency-vetting |
| AI-PW.5 | MUST | Handle, validate, sanitize and encode prompts, user data, inputs and model outputs; AI-generated code receives the same vulnerability evaluation as human code. | code review of prompt assembly, output handling at sinks. | secure-coding, code-review |
| AI-PW.7/8 | MUST (R2+) | Perform AI-specific review and testing: adversarial testing, red teaming, use-case testing; retest when models retrain or data sources change. | ai-adversarial-testing result with ≥3 variants per attack class. | ai-adversarial-testing |
| AI-RV.1 | MUST (vuln mode) | Include AI model/component vulnerabilities in scanning, disclosure and remediation. | vulnerability record names model/config version. | vulnerability-discovery |
| AI-HUMAN | MUST (R3) | Risk-based human review for consequential AI-controlled actions. | human approval boundary defined and tested; gate requires human approval for R3. | ai-agent-security, gate |

Rule: model output is data. It never authorizes a privileged action by itself.
