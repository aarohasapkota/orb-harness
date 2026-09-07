---
id: ai-agent-tool-execution
version: "harness.1"
source: "harness-defined; NIST SP 800-218A; OWASP LLM06/LLM01"
priority: 5-domain
applies_when: [change_type:ai_agent, change_type:tool_execution, change_type:ai_prompt, ai_scope:ai-system, ai_scope:both]
agents: [ai-agent-security, ai-adversarial-testing, threat-modeling, architecture-review, secure-coding, code-review, security-review, secure-defaults, requirements, remediation]
---
# AI agent / tool execution pack (R3 by default)

| ID | Strength | Requirement | Negative evidence expected |
|---|---|---|---|
| ATE-01 | MUST | Explicit tool allowlist; tools not on it cannot be invoked regardless of model output. | unauthorized tool call denied |
| ATE-02 | MUST | Tool arguments validated against a strict schema and allowlists (paths under a root, hosts on an allowlist, ids owned by the principal) before execution. | traversal/host/id tampering rejected |
| ATE-03 | MUST | Authorization for each tool call is evaluated by code using the acting principal's authority, never inferred from model text. | model claiming admin → denied |
| ATE-04 | MUST | Untrusted content (user prompt, retrieved docs, tool results, files, web) is delimited/tagged and cannot expand privileges or alter instructions. | indirect injection ≥3 variants fails |
| ATE-05 | MUST | Consequential/irreversible side effects (payments, deletes, sends, deploys, external posts) require an independent authorization boundary — human approval or policy engine — that the model cannot satisfy. | side-effect tool blocked without approval |
| ATE-06 | MUST | Least privilege for tool credentials and sandboxes: filesystem/network/exec scoped to need; separate identities per tool where practical. | escape attempts fail |
| ATE-07 | MUST | Containment: max tool calls per task, recursion/depth limits, timeouts, token/cost budgets; loops terminate. | loop-inducing input terminates |
| ATE-08 | MUST | Model output reaching code/query/shell/template/file sinks is validated/encoded like any untrusted input. | payload at each sink neutralized |
| ATE-09 | MUST | Audit log per tool call: principal, tool, redacted args, decision, outcome; no secrets. | log inspection |
| ATE-10 | MUST | Cross-user/tenant isolation of context, memory, retrieval and tool authority. | cross-context action denied |
| ATE-11 | MUST | Fail closed on parser/policy/tool errors; no "best effort" execution of malformed calls. | malformed call denied |
| ATE-12 | SHOULD | Prompts, tool schemas, permissions versioned in repo; changes reviewed as security-relevant code. | — |
