---
id: language.go
version: "harness.1"
source: "harness-defined; Go security best practices; gosec rule themes"
priority: 6-language
applies_when: [lang:go, lang:golang]
agents: [secure-coding, code-review, security-review, security-testing, remediation, regression-prevention]
---
# Go secure coding pack

| ID | Strength | Rule |
|---|---|---|
| GO-01 | MUST | `exec.Command` with discrete args; never `sh -c` with interpolated input. |
| GO-02 | MUST | `database/sql` placeholders; no `fmt.Sprintf` SQL. |
| GO-03 | MUST | `html/template` (not `text/template`) for HTML; escape per context. |
| GO-04 | MUST | `filepath.Clean` + root prefix check; `os.Root`/`fs.Sub` where available. |
| GO-05 | MUST | `crypto/rand` only; constant-time compares (`subtle.ConstantTimeCompare`); no MD5/SHA1/DES/RC4 for security. |
| GO-06 | MUST | TLS: no `InsecureSkipVerify`; `MinVersion: tls.VersionTLS12`; HTTP clients with timeouts; SSRF checks on outbound URLs. |
| GO-07 | MUST | Handle every error; never ignore errors on security paths; fail closed. |
| GO-08 | MUST | Bounded readers (`http.MaxBytesReader`, `io.LimitReader`) for untrusted input; decoder `DisallowUnknownFields` where strict. |
| GO-09 | MUST | Integer conversion/overflow checked on untrusted sizes; no `unsafe` without review. |
| GO-10 | MUST | `go.sum` verified; `govulncheck ./...` and `go vet ./...` recorded; `gosec` when available. |
| GO-11 | MUST | Concurrency: shared state guarded; `go test -race` on changed packages recorded. |
