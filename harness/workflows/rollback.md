# Rollback workflow

Trigger (exploitable vuln, integrity failure, severe regression, failed deploy, compromised artifact) → freeze forward deployment → identify known-good target → validate rollback artifact/state (release-integrity: hashes, revision) → human authorizes → restore → verify → monitor → root cause (root-cause agent) → corrective change re-enters normal or emergency SDLC.

Rules: a suspected-compromised version is not known-good because it was previously deployed; database/data migrations require rollback-safety analysis (data-migration agent) before restoration; rollback never closes the originating vulnerability.
