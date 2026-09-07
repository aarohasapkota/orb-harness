# Practice packs

A pack is data, not an agent. Each `*.md` file has YAML front matter the `harness packs` resolver reads:

- `id`, `version`, `source` — identity (record these in `result.packs_loaded`)
- `priority` — resolution order: `0-system` > `1-project` > `2-organization` > `3-regulatory` > `4-baseline` > `5-domain` > `6-language` > `7-advisory`
- `applies_when` — any of: `always`, `risk_at_least:R2`, `change_type:<type>`, `flag:<classification flag>`, `ai`, `lang:<language>`, `mode:vulnerability_response`, `mode:release`
- `agents` — which agent names load it (`*` = all)

Body: requirement tables with stable IDs, strength (MUST/SHOULD/MAY), how to check, evidence expected, prohibited patterns. Agents load only applicable packs and cite requirement IDs in `requirements_covered`. Effective strength when packs overlap: MUST > SHOULD > MAY; a lower-priority pack can never weaken a higher one.

Project overlay: put `.harness/policy/project-pack.md` in a repository to add or strengthen rules for that repo.
