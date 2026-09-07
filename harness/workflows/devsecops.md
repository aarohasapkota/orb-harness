# DevSecOps workflow

For repositories where CI/CD, frequent deployment, and telemetry are central (`sdlc: devsecops`).

Requirements & risk → small increment (secure-coding) → automated quality/security gates (repo CI: tests, SAST, SCA, secrets; captured as command evidence by test-verification / security-testing / build-security) → independent review (code-review, security-review at R2+) → integration validation → release policy (release-integrity, human approval at R3) → monitor → feedback re-enters classification.

Rules: automation output is evidence only when captured with command + exit code; automated checks never replace the mandatory independent review roles unless repository policy explicitly defines a gate as automated; CI changes themselves are R3.
