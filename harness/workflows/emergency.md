# Emergency fix overlay

Use when delay creates greater immediate risk than the normal lifecycle (active exploitation, severe production vulnerability, critical restoration). Accelerates sequencing; abolishes nothing.

Confirm emergency (human) → classify immediate risk → contain / consider rollback → define minimum safe change → remediation (write) → targeted code-review ∥ security-testing (read-only, minimum mandatory) → release-integrity check → emergency release (human) → monitor → BACKFILL deferred work (threat model, root cause, regression prevention, full verification) → post-incident follow-up.

Rules: run mode `VULNERABILITY_RESPONSE`; record every deferred obligation in `run.json` `status.uncertainties` and create the backfill tasks before the run is marked complete; mandatory controls may be deferred only where written policy permits; deferred work never silently disappears.
