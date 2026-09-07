# Agile workflow

Unit of work: one story/change. Security touchpoints repeat per story and are part of the Definition of Done, not a later phase.

Stages: Intake → Acceptance criteria (requirements) → Risk & security requirements (classification, threat model at R2+) → Implementation → Verification (tests ∥ review ∥ security testing at R2+) → Done criteria (gate PASS).

Entry: story has acceptance criteria. Exit: gate PASS for the story's revision. Feedback: any FAIL returns the story to implementation or to requirements if acceptance criteria were wrong. Select when the repository works from a backlog and declares `sdlc: agile`; otherwise the default risk-based workflow already behaves like lightweight Agile per change.
