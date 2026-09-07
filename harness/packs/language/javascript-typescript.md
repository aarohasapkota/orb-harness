---
id: language.javascript-typescript
version: "harness.1"
source: "harness-defined; OWASP Node.js security cheat sheet; eslint-plugin-security themes"
priority: 6-language
applies_when: [lang:javascript, lang:typescript, lang:node, lang:js, lang:ts]
agents: [secure-coding, code-review, security-review, security-testing, remediation, regression-prevention]
---
# JavaScript / TypeScript secure coding pack

| ID | Strength | Rule | Detect |
|---|---|---|---|
| JS-01 | MUST | No `eval`, `new Function`, `vm.runInThisContext`, `setTimeout(string)` on untrusted input. | grep |
| JS-02 | MUST | `child_process.execFile/spawn` with arg arrays; never `exec` with interpolated input. | grep `exec(` |
| JS-03 | MUST | Parameterized queries / ORM query builders; no template-literal SQL; NoSQL operators rejected from user input (`$where`, `$gt`). | grep |
| JS-04 | MUST | Path traversal: `path.resolve` + prefix check against allowed root; no user-controlled `require`/`import()`. | review |
| JS-05 | MUST | Prototype pollution: no recursive merge of untrusted objects; reject `__proto__`/`constructor` keys; `Object.create(null)` for maps. | grep, tests |
| JS-06 | MUST | XSS: framework escaping; no `innerHTML`/`dangerouslySetInnerHTML`/`v-html` with untrusted data unless sanitized (DOMPurify) and reviewed. | grep |
| JS-07 | MUST | `crypto.randomBytes/randomUUID`, `timingSafeEqual`; no `Math.random` for security. | grep |
| JS-08 | MUST | TLS verification on (`rejectUnauthorized` never false); outbound URL validation (SSRF); timeouts. | grep |
| JS-09 | MUST | Express/Fastify: `helmet` or equivalent headers, body size limits, strict CORS, cookie flags, CSRF for browser-facing state changes, no `x-powered-by`. | config |
| JS-10 | MUST | Regex from untrusted input forbidden (ReDoS); bounded quantifiers; validated with `safe-regex` when feasible. | review |
| JS-11 | MUST | `npm ci` from lockfile; `npm audit --json` / `pnpm audit` recorded; no install scripts from new deps without vetting. | command |
| JS-12 | SHOULD | `eslint` with security plugin / `tsc --noEmit` recorded as evidence. | command |
| JS-13 | MUST | Zod/valibot/joi (or equivalent) schema validation at API boundaries; TypeScript types are not runtime validation. | review |
