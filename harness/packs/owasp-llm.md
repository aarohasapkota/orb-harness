---
id: owasp-llm
version: "llm-top10-2025+harness.1"
source: "OWASP Top 10 for LLM Applications (2025) and OWASP Agentic AI guidance themes"
priority: 5-domain
applies_when: [ai]
agents: [ai-agent-security, ai-adversarial-testing, threat-modeling, code-review, security-review, secure-coding, requirements, remediation]
---
# OWASP LLM / agentic application pack

| ID | Strength | Requirement | Design/review check | Adversarial test |
|---|---|---|---|---|
| LLM01 | MUST | Prompt injection resistance: system/tool instructions separated from untrusted content; untrusted content delimited and never interpreted as instructions; privileged actions gated outside the model. | Prompt assembly reviewed; content provenance tags. | Direct + indirect injection ≥3 variants each; instruction-hierarchy bypass. |
| LLM02 | MUST | Sensitive information disclosure: model cannot access secrets/other users' data by asking; outputs filtered/redacted per policy. | Context builder reviewed for over-inclusion. | Extraction prompts; cross-session leakage. |
| LLM03 | MUST | Supply chain: models, adapters, datasets, plugins/MCP servers vetted, pinned, integrity-checked. | vetting result. | — |
| LLM04 | SHOULD | Data/model poisoning: provenance and integrity of training/retrieval data; anomaly checks. | provenance table. | Poisoned retrieval doc test. |
| LLM05 | MUST | Improper output handling: model output validated/encoded before reaching code, SQL, shell, HTML, templates, tool arguments, files. | Every sink traced. | Output containing payload for each sink. |
| LLM06 | MUST | Excessive agency: minimal tools, minimal permissions, minimal autonomy; consequential actions require independent authorization/human approval; tool arguments constrained by schema and allowlists. | Tool capability table; authz independent of model. | Unauthorized tool call; argument tampering; escalation chain. |
| LLM07 | SHOULD | System prompt leakage is not a security boundary; no secrets or authorization logic live only in prompts. | Prompt reviewed for secrets/logic. | Prompt extraction attempt. |
| LLM08 | SHOULD | Vector/embedding weaknesses: access control on retrieval corpora; tenant isolation in indexes. | index/query filters reviewed. | Cross-tenant retrieval. |
| LLM09 | SHOULD | Misinformation/over-reliance: model outputs used for decisions are validated; human review where consequential. | — | — |
| LLM10 | MUST | Unbounded consumption: token/cost/rate/loop limits; recursion and tool-call depth caps; timeouts. | limits present and tested. | Loop-inducing inputs; oversize inputs. |
| AGENT-01 | MUST | Confused deputy: tool acting on behalf of a user carries that user's authority only; no ambient credentials. | credential flow reviewed. | Cross-user action attempt. |
| AGENT-02 | MUST | Auditability: every tool invocation logged with principal, arguments (redacted), outcome. | logging reviewed. | Log inspection after tests. |
| AGENT-03 | MUST | Fail closed: tool errors, policy failures, or parser failures deny the action. | error paths. | Malformed tool-call test. |
