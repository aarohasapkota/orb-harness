---
id: data-migration
version: "harness.1"
source: "harness-defined"
priority: 5-domain
applies_when: [change_type:database_schema, change_type:data_migration, flag:persistent_data_affected]
agents: [data-migration, requirements, code-review, security-review, test-verification, secure-coding, remediation]
---
# Data / migration pack

| ID | Strength | Requirement |
|---|---|---|
| MIG-01 | MUST | Migration follows repository conventions (tool, naming, ordering); one logical change per migration. |
| MIG-02 | MUST | Forward migration executed in a disposable environment with recorded command/exit code. |
| MIG-03 | MUST | Rollback migration executed, or explicit forward-only recovery strategy documented and reviewed. |
| MIG-04 | MUST | Compatibility analysis: old code with new schema and new code with old schema during rollout (expand/contract pattern for renames/drops). |
| MIG-05 | MUST | Data-loss analysis: any DROP/truncate/type-narrowing/irreversible transform flagged high and requires human authorization. |
| MIG-06 | SHOULD | Lock/duration analysis for large tables; batching for data rewrites. |
| MIG-07 | MUST | Auth/authorization/credential/tenant-isolation schema → R3. |
| MIG-08 | MUST | Migration tests exist or throwaway verification recorded; schema dump before/after captured. |
| MIG-09 | MUST | No secrets or production data in migration scripts or fixtures. |
