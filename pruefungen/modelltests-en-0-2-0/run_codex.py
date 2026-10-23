#!/usr/bin/env python3
"""Bounded, explicitly authorized Codex-only English behavior checks."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
STATE = HERE / "run-state.json"


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    path.chmod(0o600)


def integration_snapshot():
    home = Path.home()
    result = {}
    for name in (".codex/AGENTS.md", ".claude/CLAUDE.md"):
        path = home / name
        result[name] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    for name in (".agents/skills", ".claude/skills"):
        folder = home / name
        result[name] = {p.name: os.readlink(p) if p.is_symlink() else "non-link"
                        for p in folder.iterdir()} if folder.is_dir() else None
    return result


def prepare(binary_override=None):
    if STATE.exists():
        raise RuntimeError("Run already prepared. Inspect run-state.json instead of duplicating it.")
    binary = binary_override or shutil.which("codex")
    auth = Path.home() / ".codex/auth.json"
    if not binary or not auth.is_file():
        raise RuntimeError("Codex executable or existing native login is unavailable.")
    root = Path(tempfile.mkdtemp(prefix="aios-en-modeltests-")).resolve()
    root.chmod(0o700)
    home = root / "home"
    codex_home = home / ".codex"
    profile = home / "profile"
    for path in (home, codex_home, profile, root / "tmp", root / "workspaces"):
        path.mkdir(exist_ok=True, mode=0o700)
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "en_US.UTF-8",
           "HOME": str(home), "CODEX_HOME": str(codex_home), "TMPDIR": str(root / "tmp"),
           "SHELL": "/bin/zsh", "TERM": "dumb", "PYTHONDONTWRITEBYTECODE": "1"}
    config = {"schema_version": 1, "confirmed": True, "language": "en", "clients": ["codex"],
              "paths": {"source": str(PACKAGE), "runtime": "~/runtime", "profile": "~/profile",
                        "output": "~/output", "coding_roots": [], "customer_roots": []}}
    save(profile / "paths.json", config)
    (profile / "profile.md").write_text(
        "# Synthetic test profile\n\n| Field | Confirmed value |\n| --- | --- |\n"
        "| Language | English |\n| Name | Test User |\n| Time zone | Europe/Berlin |\n", encoding="utf-8")
    (profile / "profile.md").chmod(0o600)
    (profile / "projects.md").write_text("# Synthetic project register\n\nNo registered projects.\n", encoding="utf-8")
    command = [sys.executable, "-B", str(PACKAGE / "scripts/install.py"), "--config",
               str(profile / "paths.json"), "--home", str(home), "--codex-home", str(codex_home), "--apply"]
    before = integration_snapshot()
    installation = subprocess.run(command, env=env, input="yes\n", capture_output=True, text=True, timeout=45)
    if installation.returncode:
        raise RuntimeError("Synthetic installation failed: " + installation.stderr[-1500:])
    # Reuse the existing native login without opening or printing its content.
    # This link stays in the private temporary home, never in the evidence folder.
    (codex_home / "auth.json").symlink_to(auth)
    version = subprocess.run([binary, "--version"], capture_output=True, text=True, check=True).stdout.strip()
    state = {"root": str(root), "environment": env, "binary": binary, "version": version,
             "model": "gpt-6.1-sol", "reasoning_effort": "high", "prepared_at": datetime.now(timezone.utc).isoformat(),
             "source_commit": subprocess.run(["git", "-C", str(PACKAGE), "rev-parse", "HEAD"],
                                              capture_output=True, text=True, check=True).stdout.strip(),
             "english_core_sha256": hashlib.sha256((PACKAGE / "en/rules/core.md").read_bytes()).hexdigest(),
             "integration_before": before, "installation_exit": installation.returncode}
    save(STATE, state)
    print(json.dumps({"prepared": True, "root": str(root), "version": version,
                      "active_integration_unchanged": before == integration_snapshot()}), flush=True)


def run_case(case, state, timeout=240, persist_session=False):
    root = Path(state["root"])
    workspace = root / "workspaces" / case["id"]
    workspace.mkdir(mode=0o700)
    prefix = HERE / "raw" / case["id"]
    prefix.parent.mkdir(exist_ok=True, mode=0o700)
    if prefix.with_suffix(".jsonl").exists():
        raise RuntimeError("Evidence already exists for " + case["id"])
    prompt = "$" + case["skill"] + " " + case["prompt"]
    command = [state["binary"], "exec", "--ignore-user-config", "--ignore-rules",
               "--skip-git-repo-check", "--sandbox", "read-only", "--json", "--model", state["model"],
               "-c", 'model_reasoning_effort="high"', "-c", "features.multi_agent=true",
               "-c", "agents.max_threads=2", "-c", "agents.max_depth=1", "-C", str(workspace)]
    if not persist_session:
        command.append("--ephemeral")
    if case.get("disable_agents"):
        command += ["--disable", "multi_agent"]
    command.append(prompt)
    started = datetime.now(timezone.utc).isoformat()
    timed_out = False
    with prefix.with_suffix(".jsonl").open("x", encoding="utf-8") as stdout, \
            prefix.with_suffix(".err").open("x", encoding="utf-8") as stderr:
        process = subprocess.Popen(command, env=state["environment"], stdin=subprocess.DEVNULL,
                                   stdout=stdout, stderr=stderr, text=True, start_new_session=True)
        try:
            exit_code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            exit_code = 124
    result = {"id": case["id"], "started_at": started, "finished_at": datetime.now(timezone.utc).isoformat(),
              "exit_code": exit_code, "timed_out": timed_out, "timeout_seconds": timeout,
              "persist_session": persist_session, "command": command,
              "workspace_files": sorted(str(p.relative_to(workspace)) for p in workspace.rglob("*") if p.is_file()),
              "active_integration_unchanged": state["integration_before"] == integration_snapshot()}
    save(prefix.with_suffix(".meta.json"), result)
    print(json.dumps({k: result[k] for k in ("id", "exit_code", "timed_out", "workspace_files", "active_integration_unchanged")}), flush=True)
    if exit_code:
        raise RuntimeError("Case failed to finish: " + case["id"] + ". Inspect evidence before another run.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--binary", help="Absolute Codex executable for a new test setup")
    parser.add_argument("--fixture", default="cases.json", help="Case file relative to this evidence folder")
    parser.add_argument("--timeout", type=int, default=240, help="Maximum seconds per model case")
    parser.add_argument("--persist-session", action="store_true", help="Keep rollouts in the isolated test home for native agents")
    parser.add_argument("--suffix", default="", help="Distinct evidence name for a justified comparison run")
    parser.add_argument("--case", action="append", default=[])
    args = parser.parse_args()
    if args.prepare:
        prepare(args.binary)
    if args.case:
        state = json.loads(STATE.read_text())
        cases = {case["id"]: case for case in json.loads((HERE / args.fixture).read_text())["cases"]}
        for case_id in args.case:
            case = dict(cases[case_id])
            if args.suffix:
                case["id"] += "-" + args.suffix
            run_case(case, state, args.timeout, args.persist_session)


if __name__ == "__main__":
    main()
