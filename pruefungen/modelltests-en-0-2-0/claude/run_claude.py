#!/usr/bin/env python3
"""Bounded Claude Code English behavior checks in an isolated test home."""

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
PACKAGE = HERE.parents[2]
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


def prepare(language):
    if STATE.exists():
        raise RuntimeError("Run already prepared. Inspect run-state.json instead of duplicating it.")
    binary = shutil.which("claude")
    if not binary:
        raise RuntimeError("Claude Code executable is unavailable.")
    root = Path(tempfile.mkdtemp(prefix=".aios-test-claude-", dir=Path.home())).resolve()
    root.chmod(0o700)
    home = root / "home"
    config_dir = home / ".claude"
    profile = home / "profile"
    for path in (home, config_dir, profile, root / "workspaces"):
        path.mkdir(exist_ok=True, mode=0o700)
    names = {"en": ("paths.json", "profile.md", "projects.md", "English"),
             "de": ("pfade.json", "profil.md", "projekte.md", "Deutsch")}[language]
    config = {"schema_version": 1, "confirmed": True, "language": language, "clients": ["claude-code"],
              "paths": {"source": str(PACKAGE), "runtime": "~/runtime", "profile": "~/profile",
                        "output": "~/output", "coding_roots": ["~/coding"], "customer_roots": ["~/customers"]}}
    if language == "de":
        del config["language"]
    for folder in ("coding", "customers", "output"):
        (home / folder).mkdir(mode=0o700)
    save(profile / names[0], config)
    if language == "en":
        profile_text = ("# Personal profile\n\n| Field | Confirmed value |\n| --- | --- |\n"
                        "| Name and form of address | Test User |\n| Language | English |\n"
                        "| Time zone | Europe/Berlin |\n")
        register = ("# Project register\n\n| Key | Customer or project | Local folder | Repository | Jira prefix | Status |\n"
                    "| --- | --- | --- | --- | --- | --- |\n")
    else:
        profile_text = ("# Persönliches Profil\n\n| Feld | Bestätigter Wert |\n| --- | --- |\n"
                        "| Name und Anrede | Testnutzer |\n| Sprache | Deutsch |\n| Zeitzone | Europe/Berlin |\n")
        register = ("# Projektregister\n\n| Kürzel | Kunde oder Projekt | Lokaler Ordner | Repository | Jira-Präfix | Status |\n"
                    "| --- | --- | --- | --- | --- | --- |\n")
    (profile / names[1]).write_text(profile_text, encoding="utf-8")
    (profile / names[2]).write_text(register, encoding="utf-8")
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "en_US.UTF-8", "HOME": str(home),
           "CLAUDE_CONFIG_DIR": str(config_dir), "SHELL": "/bin/zsh", "TERM": "dumb",
           "PYTHONDONTWRITEBYTECODE": "1"}
    command = [sys.executable, "-B", str(PACKAGE / "scripts/install.py"), "--config", str(profile / names[0]),
               "--home", str(home), "--claude-config-dir", str(config_dir), "--apply"]
    before = integration_snapshot()
    installation = subprocess.run(command, env=env, input="yes\n", capture_output=True, text=True, timeout=45)
    if installation.returncode:
        raise RuntimeError("Synthetic installation failed: " + installation.stderr[-1500:])
    version = subprocess.run([binary, "--version"], capture_output=True, text=True, check=True).stdout.strip()
    state = {"root": str(root), "language": language, "environment": env, "binary": binary, "version": version,
             "model": "claude-opus-5-5", "prepared_at": datetime.now(timezone.utc).isoformat(),
             "source_commit": subprocess.run(["git", "-C", str(PACKAGE), "rev-parse", "HEAD"],
                                              capture_output=True, text=True, check=True).stdout.strip(),
             "integration_before": before}
    save(STATE, state)
    print(json.dumps({"prepared": True, "root": str(root), "config_dir": str(config_dir), "version": version,
                      "active_integration_unchanged": before == integration_snapshot()}), flush=True)


def run_case(case, state, timeout):
    root = Path(state["root"])
    home = root / "home"
    workspace = root / "workspaces" / case["id"]
    workspace.mkdir(mode=0o700)
    prefix = HERE / "raw" / case["id"]
    prefix.parent.mkdir(exist_ok=True, mode=0o700)
    if prefix.with_suffix(".jsonl").exists():
        raise RuntimeError("Evidence already exists for " + case["id"])
    prompt = ("/" + case["skill"] + " " if case.get("skill") else "") + case["prompt"]
    command = [state["binary"], "-p", prompt, "--model", state["model"], "--setting-sources", "user,project",
               "--output-format", "stream-json", "--verbose",
               "--add-dir", str(home / "runtime"), "--add-dir", str(home / "profile")]
    if case.get("disable_agents"):
        command += ["--disallowedTools", "Agent", "Task"]
    started = datetime.now(timezone.utc).isoformat()
    timed_out = False
    with prefix.with_suffix(".jsonl").open("x", encoding="utf-8") as stdout, \
            prefix.with_suffix(".err").open("x", encoding="utf-8") as stderr:
        process = subprocess.Popen(command, cwd=workspace, env=state["environment"], stdin=subprocess.DEVNULL,
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
    files = sorted(str(p.relative_to(home)) for p in home.rglob("*")
                   if p.is_file() and not p.is_relative_to(home / ".claude") and not p.is_relative_to(home / "runtime"))
    result = {"id": case["id"], "started_at": started, "finished_at": datetime.now(timezone.utc).isoformat(),
              "exit_code": exit_code, "timed_out": timed_out, "timeout_seconds": timeout, "command": command,
              "workspace_files": sorted(str(p.relative_to(workspace)) for p in workspace.rglob("*") if p.is_file()),
              "home_files_outside_client_and_runtime": files,
              "active_integration_unchanged": state["integration_before"] == integration_snapshot()}
    save(prefix.with_suffix(".meta.json"), result)
    print(json.dumps({k: result[k] for k in ("id", "exit_code", "timed_out", "workspace_files",
                                             "active_integration_unchanged")}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", choices=["en", "de"])
    parser.add_argument("--fixture", action="append", default=[], help="Case file relative to the parent folder")
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--suffix", default="")
    parser.add_argument("--case", action="append", default=[])
    args = parser.parse_args()
    if args.prepare:
        prepare(args.prepare)
    if args.case:
        state = json.loads(STATE.read_text())
        cases = {}
        for fixture in args.fixture or ["cases.json"]:
            cases.update({case["id"]: case for case in json.loads((HERE.parent / fixture).read_text())["cases"]})
        for case_id in args.case:
            case = dict(cases[case_id])
            if args.suffix:
                case["id"] += "-" + args.suffix
            run_case(case, state, args.timeout)


if __name__ == "__main__":
    main()
