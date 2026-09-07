#!/usr/bin/env python3
"""Deterministic tests for the harness control plane and policy gate.

Builds throwaway git repositories, writes synthetic-but-schema-valid worker results, and asserts gate
decisions for the required scenarios: R0 docs, R1 code, R2 dependency/API, R3 auth/AI tool-use, failed
review, failed security test, failed dependency review, remediation/retry, plus process-integrity
invariants (author-as-reviewer, reviewer wrote files, stale review, critical finding, waiver, human
approval) and hook behaviour (read-only deny, stop-hook block).
Run: python3 ~/.claude/harness/tests/test_gate.py
"""
import json, os, shutil, subprocess, sys, tempfile, time

HARNESS = os.path.expanduser("~/.claude/harness/bin/harness")
RESULTS = []


def sh(cmd, cwd, env=None, check=False, stdin=None):
    e = dict(os.environ)
    for k in list(e):
        if k.startswith("HARNESS_"):
            del e[k]
    if env:
        e.update(env)
    r = subprocess.run(cmd, cwd=cwd, env=e, capture_output=True, text=True, input=stdin)
    if check and r.returncode != 0:
        raise RuntimeError(f"{cmd} failed:\n{r.stdout}\n{r.stderr}")
    return r


def h(args, cwd, env=None, stdin=None):
    return sh([HARNESS] + args, cwd, env=env, stdin=stdin)


def jout(r):
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"non-JSON output: {r.stdout}\n{r.stderr}")


def mkrepo(name):
    d = tempfile.mkdtemp(prefix=f"harness-test-{name}-")
    sh(["git", "init", "-q"], d, check=True)
    sh(["git", "config", "user.email", "t@t"], d); sh(["git", "config", "user.name", "t"], d)
    os.makedirs(os.path.join(d, "src")); os.makedirs(os.path.join(d, "docs"))
    open(os.path.join(d, "README.md"), "w").write("# demo\n")
    open(os.path.join(d, "src", "app.py"), "w").write("def add(a, b):\n    return a + b\n")
    open(os.path.join(d, "package.json"), "w").write('{"name":"demo","dependencies":{}}\n')
    sh(["git", "add", "-A"], d, check=True); sh(["git", "commit", "-qm", "init"], d, check=True)
    return d


def new_run(repo, request, mode="CHANGE", **sets):
    rid = jout(h(["run", "new", "--request", request, "--mode", mode], repo))["run_id"]
    if sets:
        h(["run", "set", "--run", rid] + [f"{k}={v}" for k, v in sets.items()], repo)
    return rid


def task(repo, rid, tid, agent, role, write=False, depends=None, retry_of=None):
    args = ["task", "new", "--run", rid, "--id", tid, "--agent", agent, "--role", role]
    if write:
        args.append("--write")
    if depends:
        args += ["--depends", depends]
    if retry_of:
        args += ["--retry-of", retry_of]
    r = h(args, repo, stdin=f"# package {tid}\nObjective: test\n")
    assert r.returncode == 0, r.stderr
    return os.path.join(repo, ".harness", "runs", rid, "tasks", tid)


def rev(repo):
    return h(["rev"], repo).stdout.strip()


def result(repo, rid, tid, agent, role, status="PASS", files=None, findings=None, tests=None, evidence=None, principal=None, created_at=None, na_reason=None):
    td = os.path.join(repo, ".harness", "runs", rid, "tasks", tid)
    res = {
        "schema_version": "harness-result/1", "run_id": rid, "task_id": tid, "agent": agent, "role": role,
        "principal_id": principal or f"agent:{agent}", "model": "sonnet", "created_at": created_at or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": status, "risk_level": "R1", "revision": rev(repo), "scope_examined": ["src/"], "actions": ["did the thing"],
        "files_changed": files or [], "evidence": evidence or [{"id": "E1", "type": "command", "command": "pytest -q", "exit_code": 0, "summary": "3 passed"}],
        "findings": findings or [], "tests": tests or {"executed": ["pytest"], "passed": ["pytest"], "failed": []},
        "claims": [{"statement": "tests executed", "evidence_refs": ["E1"]}], "unresolved": [], "residual_risks": [],
        "handoff": {"next_agent": None, "reason": None}, "not_applicable_reason": na_reason, "summary": f"{role} done",
    }
    json.dump(res, open(os.path.join(td, "result.json"), "w"), indent=2)
    return res


def gate(repo, rid, count=False):
    r = h(["gate", "--run", rid] + (["--count-cycle"] if count else []), repo)
    g = jout(r)
    return g["gate_result"], g, r.returncode


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))


# ---------------------------------------------------------------------------------------------
def t_r0_docs():
    repo = mkrepo("r0")
    rid = new_run(repo, "fix README typo", risk="R0", primary="documentation")
    open(os.path.join(repo, "README.md"), "a").write("typo fixed\n")
    h(["run", "set", "--run", rid, "orchestrator_implemented=true"], repo)
    task(repo, rid, "rev-1", "code-review", "code-review")
    result(repo, rid, "rev-1", "code-review", "code-review", evidence=[{"id": "E1", "type": "review", "summary": "APPROVE docs-only"}])
    res, g, code = gate(repo, rid)
    check("R0 documentation change passes with orchestrator implementer + independent review", res == "PASS" and code == 0, g["reason_codes"])
    # now touch an executable file under R0 -> must fail and demand reclassification
    open(os.path.join(repo, "src", "app.py"), "a").write("# comment\n")
    result(repo, rid, "rev-1", "code-review", "code-review", evidence=[{"id": "E1", "type": "review", "summary": "APPROVE"}])
    res, g, _ = gate(repo, rid)
    check("R0 with executable file changed FAILS (R0_EXECUTABLE_FILE_CHANGED)", res == "FAIL" and "R0_EXECUTABLE_FILE_CHANGED" in g["reason_codes"], g["reason_codes"])
    shutil.rmtree(repo)


def t_r1_normal():
    repo = mkrepo("r1")
    rid = new_run(repo, "add subtract()", risk="R1", primary="business_logic", languages="python")
    task(repo, rid, "req-1", "requirements", "requirements")
    result(repo, rid, "req-1", "requirements", "requirements", evidence=[{"id": "E1", "type": "document", "summary": "requirements.md"}])
    task(repo, rid, "impl-1", "secure-coding", "implementer", write=True, depends="req-1")
    # missing reviewers -> FAIL with missing roles
    open(os.path.join(repo, "src", "app.py"), "a").write("def sub(a, b):\n    return a - b\n")
    result(repo, rid, "impl-1", "secure-coding", "implementer", files=["src/app.py"])
    res, g, _ = gate(repo, rid)
    check("R1 without review/verification FAILS with MISSING_* reasons", res == "FAIL" and "MISSING_CODE_REVIEW" in g["reason_codes"] and "MISSING_TEST_VERIFICATION" in g["reason_codes"], g["reason_codes"])
    task(repo, rid, "ver-1", "test-verification", "test-verification", depends="impl-1")
    task(repo, rid, "rev-1", "code-review", "code-review", depends="impl-1")
    result(repo, rid, "ver-1", "test-verification", "test-verification")
    result(repo, rid, "rev-1", "code-review", "code-review", evidence=[{"id": "E1", "type": "review", "summary": "APPROVE"}])
    res, g, code = gate(repo, rid)
    check("R1 normal code change PASSES with requirements+impl+verification+review", res == "PASS" and code == 0, g["reason_codes"])
    # author == reviewer principal -> FAIL non-waivable
    result(repo, rid, "rev-1", "code-review", "code-review", principal="agent:secure-coding", evidence=[{"id": "E1", "type": "review", "summary": "APPROVE"}])
    res, g, _ = gate(repo, rid)
    check("author-as-reviewer FAILS (AUTHOR_IS_REVIEWER)", res == "FAIL" and "AUTHOR_IS_REVIEWER" in g["reason_codes"], g["reason_codes"])
    # reviewer modified files -> FAIL
    result(repo, rid, "rev-1", "code-review", "code-review", files=["src/app.py"], evidence=[{"id": "E1", "type": "review", "summary": "APPROVE"}])
    res, g, _ = gate(repo, rid)
    check("reviewer that changed files FAILS (REVIEWER_MODIFIED_FILES)", res == "FAIL" and "REVIEWER_MODIFIED_FILES" in g["reason_codes"], g["reason_codes"])
    # stale review: tree changes after review
    result(repo, rid, "rev-1", "code-review", "code-review", evidence=[{"id": "E1", "type": "review", "summary": "APPROVE"}])
    open(os.path.join(repo, "src", "app.py"), "a").write("# late edit\n")
    res, g, _ = gate(repo, rid)
    check("tree changed after review FAILS (STALE_REVIEW_EVIDENCE + UNEXPLAINED_CHANGES)", res == "FAIL" and "STALE_REVIEW_EVIDENCE" in g["reason_codes"] and "UNEXPLAINED_CHANGES_AFTER_IMPLEMENTATION" in g["reason_codes"], g["reason_codes"])
    shutil.rmtree(repo)


def t_r2_dependency_api():
    repo = mkrepo("r2")
    rid = new_run(repo, "add /upload endpoint using new lib", risk="R2", primary="public_api", change_types="dependency,input_processing",
                  **{"flags.externally_exposed": "true", "flags.untrusted_input_affected": "true", "flags.third_party_code_added": "true"}, languages="javascript")
    for tid, agent, role in [("req-1", "requirements", "requirements"), ("tm-1", "threat-modeling", "threat-model")]:
        task(repo, rid, tid, agent, role); result(repo, rid, tid, agent, role, evidence=[{"id": "E1", "type": "document", "summary": "doc"}])
    # dependency review FAILS (vulnerable lib)
    task(repo, rid, "dep-1", "dependency-vetting", "dependency-review")
    result(repo, rid, "dep-1", "dependency-vetting", "dependency-review", status="FAIL",
           findings=[{"id": "F-DEP-1", "severity": "high", "confidence": "high", "location": "package.json", "description": "left-pad 0.0.1 has critical advisory", "recommendation": "use 1.3.0", "blocking": True, "status": "open"}],
           evidence=[{"id": "E1", "type": "command", "command": "npm audit --json", "exit_code": 1, "summary": "1 high"}])
    res, g, _ = gate(repo, rid)
    check("failed dependency review FAILS with routing to dependency-review", res == "FAIL" and "DEPENDENCY_REVIEW_FAIL" in g["reason_codes"] and any(r.get("route_to") == "dependency-review" for r in g["remediation_routes"]), g["reason_codes"])
    # retry dep review passes with pinned version; implement; verification wave
    task(repo, rid, "dep-2", "dependency-vetting", "dependency-review", retry_of="dep-1")
    result(repo, rid, "dep-2", "dependency-vetting", "dependency-review", evidence=[{"id": "E1", "type": "command", "command": "npm audit --json", "exit_code": 0, "summary": "0 vulns"}])
    open(os.path.join(repo, "package.json"), "w").write('{"name":"demo","dependencies":{"left-pad":"1.3.0"}}\n')
    open(os.path.join(repo, "src", "upload.js"), "w").write("module.exports = () => 1;\n")
    task(repo, rid, "impl-1", "secure-coding", "implementer", write=True)
    result(repo, rid, "impl-1", "secure-coding", "implementer", files=["package.json", "src/upload.js"])
    for tid, agent, role in [("ver-1", "test-verification", "test-verification"), ("rev-1", "code-review", "code-review"), ("sec-1", "security-review", "security-review")]:
        task(repo, rid, tid, agent, role); result(repo, rid, tid, agent, role, evidence=[{"id": "E1", "type": "review", "summary": "ok"}])
    # security testing FAILS first
    task(repo, rid, "st-1", "security-testing", "security-testing")
    result(repo, rid, "st-1", "security-testing", "security-testing", status="FAIL",
           findings=[{"id": "F-ST-1", "severity": "high", "confidence": "high", "location": "src/upload.js:1", "description": "path traversal via filename", "recommendation": "normalize+prefix check", "blocking": True, "status": "open"}],
           tests={"executed": ["traversal"], "passed": [], "failed": ["traversal"]},
           evidence=[{"id": "E1", "type": "test-run", "command": "node tests/traversal.js", "exit_code": 1, "summary": "traversal succeeded"}, {"id": "E2", "type": "secrets-scan", "status": "pass", "summary": "0 findings"}])
    res, g, _ = gate(repo, rid, count=True)
    check("failed security test FAILS (REQUIRED_TEST_FAILED, HIGH_FINDING_OPEN) and counts a cycle", res == "FAIL" and "REQUIRED_TEST_FAILED" in g["reason_codes"] and "HIGH_FINDING_OPEN" in g["reason_codes"] and g.get("remediation_cycles") == 1, g["reason_codes"])
    # remediation: implementer retry, then ALL verifiers re-run against the new revision
    open(os.path.join(repo, "src", "upload.js"), "w").write("module.exports = (n) => n.replace(/\\.\\./g, '');\n")
    task(repo, rid, "impl-2", "secure-coding", "implementer", write=True, retry_of="impl-1")
    result(repo, rid, "impl-2", "secure-coding", "implementer", files=["package.json", "src/upload.js"])
    res, g, _ = gate(repo, rid)
    check("after remediation, stale verifier evidence FAILS the gate until re-run", res == "FAIL" and "STALE_REVIEW_EVIDENCE" in g["reason_codes"], g["reason_codes"])
    for tid, agent, role in [("ver-2", "test-verification", "test-verification"), ("rev-2", "code-review", "code-review"), ("sec-2", "security-review", "security-review")]:
        task(repo, rid, tid, agent, role, retry_of=tid.replace("-2", "-1")); result(repo, rid, tid, agent, role, evidence=[{"id": "E1", "type": "review", "summary": "ok"}])
    task(repo, rid, "st-2", "security-testing", "security-testing", retry_of="st-1")
    result(repo, rid, "st-2", "security-testing", "security-testing",
           findings=[{"id": "F-ST-1", "severity": "high", "confidence": "high", "location": "src/upload.js:1", "description": "path traversal via filename", "recommendation": "-", "blocking": True, "status": "remediated"}],
           evidence=[{"id": "E1", "type": "test-run", "command": "node tests/traversal.js", "exit_code": 0, "summary": "traversal blocked"}, {"id": "E2", "type": "secrets-scan", "status": "pass", "summary": "0 findings"}])
    res, g, code = gate(repo, rid)
    check("R2 dependency + API change PASSES after remediation/retry path", res == "PASS" and code == 0, g["reason_codes"])
    check("R2 gate lists dependency-review among required roles (conditional trigger)", "dependency-review" in g["required_roles"], g["required_roles"])
    shutil.rmtree(repo)


def t_r3_auth_ai():
    repo = mkrepo("r3")
    rid = new_run(repo, "LLM agent can call repo tools; add token auth", risk="R3", primary="tool_execution", change_types="ai_agent,authentication",
                  **{"flags.externally_exposed": "true", "flags.security_boundary_affected": "true", "flags.privilege_boundary_affected": "true", "flags.untrusted_input_affected": "true", "flags.irreversible_effect_possible": "true"},
                  ai_scope="ai-system", languages="python")
    pk = jout(h(["packs", "--run", rid, "--agent", "code-review"], repo))
    ids = [p["id"] for p in pk["packs"]]
    check("R3 AI/auth run loads AI + auth + tool-execution packs for code-review", all(x in ids for x in ["nist-ssdf", "nist-ssdf-ai", "owasp-llm", "ai-agent-tool-execution", "auth-identity", "secrets", "language.python"]), ids)
    early = "2020-01-01T00:00:00Z"
    for tid, agent, role in [("req-1", "requirements", "requirements"), ("tm-1", "threat-modeling", "threat-model"), ("ar-1", "architecture-review", "architecture-review"), ("ai-1", "ai-agent-security", "domain-specialist")]:
        task(repo, rid, tid, agent, role); result(repo, rid, tid, agent, role, created_at=early, evidence=[{"id": "E1", "type": "document", "summary": "doc"}])
    open(os.path.join(repo, "src", "agent.py"), "w").write("TOOLS = {'read'}\n")
    task(repo, rid, "impl-1", "secure-coding", "implementer", write=True)
    result(repo, rid, "impl-1", "secure-coding", "implementer", files=["src/agent.py"], evidence=[{"id": "E1", "type": "test-run", "command": "pytest", "exit_code": 0, "summary": "ok"}, {"id": "E2", "type": "secrets-scan", "status": "pass", "summary": "0"}])
    # failed independent code review with critical finding
    task(repo, rid, "rev-1", "code-review", "code-review")
    result(repo, rid, "rev-1", "code-review", "code-review", status="FAIL",
           findings=[{"id": "F-CR-1", "severity": "critical", "confidence": "high", "location": "src/agent.py:1", "description": "model output used as tool authorization", "recommendation": "authorize in code", "blocking": True, "status": "open"}],
           evidence=[{"id": "E1", "type": "review", "summary": "REQUEST_CHANGES"}])
    res, g, _ = gate(repo, rid)
    check("failed review with critical finding FAILS (CRITICAL_FINDING_OPEN, non-waivable)", res == "FAIL" and "CRITICAL_FINDING_OPEN" in g["reason_codes"] and "CODE_REVIEW_FAIL" in g["reason_codes"], g["reason_codes"])
    # human tries to waive the critical finding -> must have no effect
    h(["waiver", "--run", rid, "--finding", "F-CR-1", "--reason", "we like risk", "--approved-by", "human:tester"], repo)
    res, g, _ = gate(repo, rid)
    check("critical finding cannot be waived", res == "FAIL" and "CRITICAL_FINDING_OPEN" in g["reason_codes"], g["reason_codes"])
    # remediate + full independent wave
    open(os.path.join(repo, "src", "agent.py"), "w").write("TOOLS = {'read'}\ndef authorize(p, t): return t in TOOLS and p.allowed(t)\n")
    task(repo, rid, "impl-2", "secure-coding", "implementer", write=True, retry_of="impl-1")
    result(repo, rid, "impl-2", "secure-coding", "implementer", files=["src/agent.py"], evidence=[{"id": "E1", "type": "test-run", "command": "pytest", "exit_code": 0, "summary": "ok"}, {"id": "E2", "type": "secrets-scan", "status": "pass", "summary": "0"}])
    for tid, agent, role in [("ver-1", "test-verification", "test-verification"), ("rev-2", "code-review", "code-review"), ("sec-1", "security-review", "security-review"),
                             ("st-1", "security-testing", "security-testing"), ("adv-1", "ai-adversarial-testing", "ai-adversarial-testing"), ("sd-1", "secure-defaults", "secure-defaults")]:
        task(repo, rid, tid, agent, role, retry_of="rev-1" if tid == "rev-2" else None)
        result(repo, rid, tid, agent, role, evidence=[{"id": "E1", "type": "test-run", "command": "pytest -q", "exit_code": 0, "summary": "ok"}])
    # a medium finding blocks at R3 until waived
    result(repo, rid, "sd-1", "secure-defaults", "secure-defaults", status="PASS",
           findings=[{"id": "F-SD-1", "severity": "medium", "confidence": "medium", "location": "config", "description": "verbose logging default", "recommendation": "off by default", "blocking": False, "status": "open"}],
           evidence=[{"id": "E1", "type": "analysis", "summary": "defaults table"}])
    res, g, _ = gate(repo, rid)
    check("R3 medium finding blocks (MEDIUM_FINDING_OPEN)", res == "FAIL" and "MEDIUM_FINDING_OPEN" in g["reason_codes"], g["reason_codes"])
    h(["waiver", "--run", rid, "--finding", "F-SD-1", "--reason", "logging redacted; tracked", "--approved-by", "human:tester"], repo)
    res, g, _ = gate(repo, rid)
    check("R3 without human approval -> NEEDS_HUMAN (HUMAN_APPROVAL_REQUIRED) with medium waived", res == "NEEDS_HUMAN" and "HUMAN_APPROVAL_REQUIRED" in g["reason_codes"] and "F-SD-1" in g["waived_findings"], g["reason_codes"])
    h(["approve", "--run", rid, "--by", "human:tester"], repo)
    res, g, code = gate(repo, rid)
    check("R3 auth/AI tool-use change PASSES WITH_WAIVERS after human approval", res == "PASS" and g["pass_mode"] == "WITH_WAIVERS" and code == 0, g["reason_codes"])
    # SoD: security review by same principal as code review at R3 -> FAIL
    result(repo, rid, "sec-1", "security-review", "security-review", principal="agent:code-review", evidence=[{"id": "E1", "type": "review", "summary": "ok"}])
    res, g, _ = gate(repo, rid)
    check("R3 security review by code-review principal FAILS (SECURITY_REVIEW_NOT_INDEPENDENT)", res == "FAIL" and "SECURITY_REVIEW_NOT_INDEPENDENT" in g["reason_codes"], g["reason_codes"])
    # ordering: architecture review AFTER implementation -> FAIL
    result(repo, rid, "sec-1", "security-review", "security-review", evidence=[{"id": "E1", "type": "review", "summary": "ok"}])
    result(repo, rid, "ar-1", "architecture-review", "architecture-review", created_at="2999-01-01T00:00:00Z", evidence=[{"id": "E1", "type": "document", "summary": "doc"}])
    res, g, _ = gate(repo, rid)
    check("R3 architecture review after implementation FAILS (IMPLEMENTATION_BEFORE_ARCHITECTURE_APPROVAL)", res == "FAIL" and "IMPLEMENTATION_BEFORE_ARCHITECTURE_APPROVAL" in g["reason_codes"], g["reason_codes"])
    shutil.rmtree(repo)


def t_vuln_mode():
    repo = mkrepo("vuln")
    rid = new_run(repo, "fix reported SQLi in search", mode="VULNERABILITY_RESPONSE", risk="R2", primary="security_remediation", languages="python")
    for tid, agent, role in [("vd-1", "vulnerability-discovery", "vulnerability-discovery"), ("tr-1", "triage", "triage")]:
        task(repo, rid, tid, agent, role); result(repo, rid, tid, agent, role, evidence=[{"id": "E1", "type": "reproduction", "summary": "repro"}])
    open(os.path.join(repo, "src", "app.py"), "a").write("def search(q): return db.execute('select 1 where x = ?', (q,))\n")
    task(repo, rid, "rem-1", "remediation", "remediation", write=True)
    result(repo, rid, "rem-1", "remediation", "remediation", files=["src/app.py"])
    res, g, _ = gate(repo, rid)
    check("vulnerability mode requires the RV chain (missing root-cause/regression-prevention/review/testing)", res in ("FAIL", "NEEDS_HUMAN") and "MISSING_CODE_REVIEW" in g["reason_codes"] and "MISSING_ROOT_CAUSE" in g["reason_codes"], g["reason_codes"])
    for tid, agent, role in [("req-1", "requirements", "requirements"), ("tm-1", "threat-modeling", "threat-model"), ("ver-1", "test-verification", "test-verification"), ("rev-1", "code-review", "code-review"),
                             ("sec-1", "security-review", "security-review"), ("st-1", "security-testing", "security-testing"), ("rc-1", "root-cause", "root-cause"), ("rp-1", "regression-prevention", "regression-prevention")]:
        task(repo, rid, tid, agent, role, write=(role == "regression-prevention"))
        result(repo, rid, tid, agent, role, evidence=[{"id": "E1", "type": "test-run", "command": "pytest", "exit_code": 0, "summary": "ok"}, {"id": "E2", "type": "secrets-scan", "status": "pass", "summary": "0"}])
    res, g, code = gate(repo, rid)
    check("vulnerability response chain complete -> PASS", res == "PASS" and code == 0, g["reason_codes"])
    shutil.rmtree(repo)


def t_hooks_and_contract():
    repo = mkrepo("hooks")
    rid = new_run(repo, "hook test", risk="R1")
    td = task(repo, rid, "rev-1", "code-review", "code-review")
    env = {"HARNESS_ROLE": "code-review", "HARNESS_WRITE": "0", "HARNESS_TASK_DIR": td, "HARNESS_RESULT": os.path.join(td, "result.json"), "HARNESS_AGENT": "code-review", "HARNESS_PRINCIPAL": "agent:code-review", "HARNESS_RUN": rid, "HARNESS_TASK": "rev-1", "HARNESS_RISK": "R1"}
    r = h(["hook", "pre-tool-use"], repo, env=env, stdin=json.dumps({"tool_name": "Edit", "tool_input": {"file_path": os.path.join(repo, "src/app.py")}}))
    check("PreToolUse hook denies product-code Edit for read-only role", '"deny"' in r.stdout, r.stdout)
    r = h(["hook", "pre-tool-use"], repo, env=env, stdin=json.dumps({"tool_name": "Write", "tool_input": {"file_path": os.path.join(td, "review.md")}}))
    check("PreToolUse hook allows writes inside the task dir", r.stdout.strip() == "", r.stdout)
    r = h(["hook", "pre-tool-use"], repo, env=env, stdin=json.dumps({"tool_name": "Bash", "tool_input": {"command": "harness gate --run x"}}))
    check("PreToolUse hook denies workers running the gate", '"deny"' in r.stdout, r.stdout)
    r = h(["hook", "pre-tool-use"], repo, env=env, stdin=json.dumps({"tool_name": "Bash", "tool_input": {"command": "git commit -am x"}}))
    check("PreToolUse hook denies git state changes for read-only role", '"deny"' in r.stdout, r.stdout)
    r = h(["hook", "stop"], repo, env=env, stdin=json.dumps({"stop_hook_active": False}))
    check("Stop hook blocks when result.json missing", '"block"' in r.stdout, r.stdout)
    r = h(["result", "template"], repo, env=env)
    tpl = jout(r)
    tpl["status"] = "PASS"; tpl["claims"] = [{"statement": "x", "evidence_refs": ["E1"]}]
    json.dump(tpl, open(os.path.join(td, "result.json"), "w"))
    r = h(["result", "validate", os.path.join(td, "result.json")], repo, env=env)
    check("result template validates after filling status", r.returncode == 0, r.stdout + r.stderr)
    r = h(["hook", "stop"], repo, env=env, stdin=json.dumps({"stop_hook_active": False}))
    check("Stop hook passes with valid result", r.stdout.strip() == "", r.stdout)
    tpl["status"] = "PASS"; tpl["tests"] = {"executed": ["a"], "passed": [], "failed": ["a"]}
    json.dump(tpl, open(os.path.join(td, "result.json"), "w"))
    r = h(["result", "validate", os.path.join(td, "result.json")], repo, env=env)
    check("result with PASS but failed tests is rejected (evidence contradicts status)", r.returncode != 0 and "contradicts" in r.stdout, r.stdout)
    # worker cannot create waivers
    r = h(["waiver", "--run", rid, "--finding", "F1", "--reason", "x", "--approved-by", "human:me"], repo, env=env)
    check("worker session cannot issue waivers", r.returncode != 0, r.stdout)
    # secrets scanner
    open(os.path.join(repo, "src", "cfg.py"), "w").write("AWS_KEY = '" + "AKIA" + "ABCDEFGHIJKLMNOP" + "'\n")  # fake key assembled at runtime so the literal never appears in source
    r = h(["scan", "secrets", "src/cfg.py"], repo)
    check("built-in secrets scanner detects AWS key pattern", r.returncode == 1 and "aws_access_key" in r.stdout, r.stdout[:200])
    # classify hints
    c = jout(h(["classify", "src/auth/login.py", "README.md"], repo))
    check("classify hints escalate auth paths to R3", c["suggested_min_risk"] == "R3", c)
    c = jout(h(["classify", "README.md", "docs/guide.md"], repo))
    check("classify hints keep docs-only at R0", c["suggested_min_risk"] == "R0" and c["doc_only"], c)
    # dry-run spawn produces a launch script with sonnet/high/agent
    task(repo, rid, "impl-1", "secure-coding", "implementer", write=True)
    d = jout(h(["spawn", "--run", rid, "--task", "impl-1", "--dry-run"], repo))
    launch = open(d["launch_script"]).read()
    check("spawn dry-run builds launcher with sonnet + effort high + agent + append-system-prompt", "--model sonnet" in launch and "--effort high" in launch and "--agent secure-coding" in launch and "--append-system-prompt" in launch, launch[:300])
    # dependency serialization: spawning a task whose dependency has no result is refused
    task(repo, rid, "rev-2", "code-review", "code-review", depends="impl-1")
    r = h(["spawn", "--run", rid, "--task", "rev-2", "--dry-run"], repo)
    check("spawn refuses a task whose dependency has no result", r.returncode != 0 and "dependency" in r.stderr, r.stderr)
    # read-only role cannot be created with --write
    r = h(["task", "new", "--run", rid, "--id", "bad", "--agent", "code-review", "--role", "code-review", "--write"], repo, stdin="x")
    check("read-only roles refuse --write", r.returncode != 0, r.stderr)
    # risk downgrade needs justification
    r = h(["run", "set", "--run", rid, "risk=R0"], repo)
    check("risk downgrade without --justify is refused", r.returncode != 0 and "justify" in r.stderr, r.stderr)
    # audit chain
    lines = open(os.path.join(repo, ".harness", "runs", rid, "audit.jsonl")).read().strip().splitlines()
    ok = all(json.loads(lines[i])["previous_event_digest"] == json.loads(lines[i - 1])["event_digest"] for i in range(1, len(lines)))
    check("audit trail is hash-chained", ok and len(lines) > 3, len(lines))
    shutil.rmtree(repo)


if __name__ == "__main__":
    for t in (t_r0_docs, t_r1_normal, t_r2_dependency_api, t_r3_auth_ai, t_vuln_mode, t_hooks_and_contract):
        try:
            t()
        except Exception as e:  # noqa
            check(f"{t.__name__} raised", False, repr(e))
    failed = [r for r in RESULTS if not r[1]]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
    sys.exit(1 if failed else 0)
