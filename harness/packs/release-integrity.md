---
id: release-integrity
version: "harness.1"
source: "harness-defined; SSDF PS.2, PS.3"
priority: 5-domain
applies_when: [mode:release, change_type:release_packaging, flag:build_or_release_path_affected]
agents: [release-integrity, build-security, ci-cd-platform, security-review]
---
# Release integrity pack

| ID | Strength | Requirement |
|---|---|---|
| REL-01 | MUST | Release artifacts are built from the reviewed/tested revision; the revision id is recorded with the artifact hashes. |
| REL-02 | MUST | sha256 for every artifact recorded; signature/attestation status `verified` or `not_required` per written policy — `missing` fails. |
| REL-03 | SHOULD | SBOM or dependency inventory produced; lineage gaps explicit. |
| REL-04 | MUST | Release/publish is an explicit human-authorized action; the harness never publishes. |
| REL-05 | MUST | Version metadata/changelog reflect the change; no protected secrets or keys inside artifacts. |
| REL-06 | MUST | Rollback target identified and validated before release when the change affects production behavior. |
