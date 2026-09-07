---
id: ci-cd-build-integrity
version: "harness.1"
source: "harness-defined; GitHub Actions security hardening guidance; OpenSSF Scorecard (Pinned-Dependencies, Token-Permissions, Dangerous-Workflow)"
priority: 5-domain
applies_when: [change_type:ci_cd, change_type:build_configuration, change_type:infrastructure, flag:build_or_release_path_affected]
agents: [ci-cd-platform, build-security, code-review, security-review, threat-modeling, release-integrity, requirements]
---
# CI/CD and build integrity pack (R3 by default for trust/credential changes)

| ID | Strength | Requirement | Check |
|---|---|---|---|
| CI-01 | MUST | Explicit least-privilege `permissions:` (default read-only; write scopes per job only when needed). | workflow YAML |
| CI-02 | MUST | No `pull_request_target`/`workflow_run` that checks out and executes untrusted PR code with secrets. | triggers |
| CI-03 | MUST | No script injection: untrusted `${{ github.event.* }}` values passed via env vars, not interpolated into `run:`. | `run:` blocks |
| CI-04 | MUST | Third-party actions/images/tools pinned to immutable digests (SHA), not mutable tags/branches. | `uses:`/`FROM` |
| CI-05 | MUST | Secrets: scoped to jobs that need them; masked; never echoed; never available to fork PRs. | secrets usage |
| CI-06 | MUST | Deployment/publish jobs gated on protected branches/environments with required reviewers; authorship ≠ release authority. | environments |
| CI-07 | MUST | Install steps use lockfiles (`npm ci`, `pip install -r ... --require-hashes` where feasible) and verified downloads. | install commands |
| CI-08 | SHOULD | Self-hosted runners isolated/ephemeral for untrusted code. | runner config |
| CI-09 | MUST | Containers: minimal base, non-root user, no secrets in layers, pinned base digest. | Dockerfile |
| CI-10 | MUST | IaC: least-privilege IAM, no `0.0.0.0/0` admin ingress, encryption at rest on, state files without secrets, `plan` reviewed before `apply` (apply is never automatic in this harness). | terraform/k8s files |
| CI-11 | MUST | Pipeline validated with a linter/dry-run where tooling exists; recorded as command evidence. | actionlint etc. |
| CI-12 | MUST | The harness never performs a real deployment because pipeline config changed. | policy |
