---
id: supply-chain-provenance
version: "harness.1"
source: "SLSA v1.0 concepts; Sigstore; SPDX/CycloneDX SBOM; SSDF PS.2/PS.3"
priority: 5-domain
applies_when: [flag:build_or_release_path_affected, change_type:ci_cd, change_type:build_configuration, change_type:release_packaging, mode:release]
agents: [build-security, release-integrity, ci-cd-platform, code-review, security-review, dependency-vetting]
---
# Supply chain / provenance pack

| ID | Strength | Requirement | Check |
|---|---|---|---|
| SC-01 | MUST | Build inputs are fully specified: pinned dependencies, pinned tool versions, pinned base images/actions by digest. | manifests, CI files |
| SC-02 | MUST | Build runs from version control on a controlled environment; no manual artifact edits. | CI config |
| SC-03 | SHOULD | Provenance attestation (SLSA-style) generated for released artifacts and verifiable. | attestation status |
| SC-04 | MUST (release) | Artifact hashes recorded and published with the release; signature per policy (`verified|not_required` only). | artifact-hash |
| SC-05 | SHOULD | SBOM produced for releases (SPDX/CycloneDX) or dependency inventory recorded; gaps explicit. | SBOM file |
| SC-06 | MUST | Signing keys never in repository or logs; signing happens in controlled identity (OIDC/keyless or HSM). | secrets-scan, CI review |
| SC-07 | MUST | Release/publish steps require a protected trigger and authorization distinct from authorship. | CI permissions |
| SC-08 | MUST | Verify what you consume: checksums/signatures for downloaded tools and artifacts in build scripts. | build scripts |
| SC-09 | SHOULD | Reproducible builds where feasible; record deterministic flags. | build-security.md |
| SC-10 | MUST | Unexpected artifact ↔ source mismatch is treated as possible compromise → vulnerability-discovery. | release-integrity |
