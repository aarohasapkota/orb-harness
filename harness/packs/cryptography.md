---
id: cryptography
version: "harness.1"
source: "harness-defined; OWASP ASVS V6; NIST SP 800-57/131A themes"
priority: 5-domain
applies_when: [change_type:cryptography, change_type:secrets]
agents: [requirements, architecture-review, secure-coding, code-review, security-review, security-testing, remediation]
---
# Cryptography pack (R3 by default)

| ID | Strength | Requirement |
|---|---|---|
| CRY-01 | MUST | Use vetted libraries and high-level APIs (libsodium, platform crypto, well-maintained language stdlib); never implement primitives or protocols. |
| CRY-02 | MUST | Approved algorithms only: AES-GCM/ChaCha20-Poly1305 for symmetric AEAD; RSA-OAEP ≥ 3072 or ECDH/X25519 for key agreement; Ed25519/ECDSA P-256+ or RSA-PSS for signatures; SHA-256+ for hashing; HKDF/PBKDF2/argon2id for derivation. Prohibited: MD5, SHA-1 (security use), DES/3DES, RC4, ECB, unauthenticated CBC, RSA PKCS#1 v1.5 encryption, custom constructions. |
| CRY-03 | MUST | Nonces/IVs unique per key (random 96-bit for GCM or counter managed); never reuse; never static. |
| CRY-04 | MUST | Keys from CSPRNG; never derived from passwords without a KDF; never hard-coded; stored in a secret store/KMS; rotation path documented. |
| CRY-05 | MUST | Constant-time comparison for MACs/tokens. |
| CRY-06 | MUST | TLS: verification on; modern versions (≥1.2, prefer 1.3); no `verify=False`/`InsecureSkipVerify`/`rejectUnauthorized:false`. |
| CRY-07 | MUST | Randomness for security purposes from the platform CSPRNG (`secrets`, `crypto.randomBytes`, `crypto/rand`), never `Math.random`/`random`. |
| CRY-08 | SHOULD | Crypto agility: algorithm identifiers versioned in stored data. |
| CRY-09 | MUST | Independent security review with a cryptography-capable reviewer; negative tests for tampering (modified ciphertext/signature rejected). |
