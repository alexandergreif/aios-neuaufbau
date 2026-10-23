#!/usr/bin/env python3
"""Check a first installation in an invented home and native loading without providers."""

import argparse
from datetime import datetime, timezone
from functools import partial
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import languages
from prepare_client import PACKAGE, destination_path
from setup_profile import write_private
from check_client_loader import (
    environment, codex_probe, codex_request_probe, claude_probe, run, skill_listing,
)


def install_fixture(root, env, language=languages.DEFAULT):
    lang = languages.get(language)
    home = Path(env["HOME"])
    profile = home / "profile"
    profile.mkdir(mode=0o700)
    config = {"schema_version": 1, "confirmed": True, "language": lang.code, "clients": ["claude-code", "codex"],
              "paths": {"source": str(PACKAGE), "runtime": "~/runtime", "profile": "~/profile",
                        "output": "~/output", "coding_roots": [], "customer_roots": []}}
    config_path = profile / lang.config_name
    write_private(config_path, json.dumps(config) + "\n")
    # Deliberately invented test values. No content from a real profile.
    write_private(profile / lang.profile_name, "Synthetic test profile\n")
    write_private(profile / ".env", "BLOCKBRAIN_API_KEY=synthetic-not-a-real-key\n")
    originals = {path: path.read_bytes() for path in profile.iterdir()}
    command = [sys.executable, str(PACKAGE / "scripts/install.py"), "--config", str(config_path),
               "--home", str(home), "--codex-home", env["CODEX_HOME"],
               "--claude-config-dir", env["CLAUDE_CONFIG_DIR"], "--apply"]
    result = subprocess.run(command, input="yes\n", text=True, capture_output=True, env=env, timeout=30)
    if result.returncode:
        raise RuntimeError("Synthetic first installation failed: " + result.stderr)
    state = json.loads((profile / lang.state_dir / "installation.json").read_text())
    repeat = subprocess.run(command, input="yes\n", text=True, capture_output=True, env=env, timeout=30)
    status_command = [sys.executable, str(home / "runtime/scripts/setup_status.py"),
                      "--config", str(config_path), "--home", str(home),
                      "--codex-home", env["CODEX_HOME"], "--claude-config-dir", env["CLAUDE_CONFIG_DIR"], "--json"]
    status = subprocess.run(status_command, cwd=root, text=True, capture_output=True, env=env, timeout=30)
    try:
        status_report = json.loads(status.stdout)
    except json.JSONDecodeError:
        status_report = {"status": "unchecked", "error": "No valid JSON status"}
    return {"exit_code": result.returncode, "log": result.stdout, "status": state["status"],
            "created_objects": len(state["created"]),
            "private_fixture_unchanged": all(path.read_bytes() == data for path, data in originals.items()),
            "repeat_blocked": repeat.returncode == 1,
            "repeat_log": repeat.stderr, "installed_status_exit_code": status.returncode,
            "installed_status": status_report}, home / "runtime"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", default=shutil.which("codex"))
    parser.add_argument("--claude", default=shutil.which("claude"))
    parser.add_argument("--evidence-dir", required=True, help="New absolute evidence folder")
    parser.add_argument("--language", choices=languages.CODES, default=languages.DEFAULT,
                        help="Language of rules and skills (default de)")
    args = parser.parse_args(argv)
    if not args.codex or not args.claude or not Path("/usr/bin/sandbox-exec").is_file():
        parser.error("Both clients and macOS sandbox-exec are needed")
    lang = languages.get(args.language)
    manual = lang.manual_skill
    evidence_dir = destination_path(args.evidence_dir)
    proof_sources = ["install.py", "install_plan.py", "build_package.py", "safe_files.py", "languages.py",
                     "setup_profile.py", "check_config.py", "setup_status.py", "package_rules.py",
                     "package_inventory.py", "prepare_client.py", "check_client_loader.py",
                     "check_local_installation.py"]
    source_hashes = {name: hashlib.sha256((PACKAGE / "scripts" / name).read_bytes()).hexdigest()
                     for name in proof_sources}
    actual_home = Path.home().resolve()
    before = skill_listing(actual_home)
    clients = []
    with tempfile.TemporaryDirectory(prefix="aios-installed-loader-") as temporary:
        root = Path(temporary).resolve()
        env = environment(root)
        # Check the normal global folders, no project-local skills or rule files.
        env["CODEX_HOME"] = str(Path(env["HOME"]) / ".codex")
        env["CLAUDE_CONFIG_DIR"] = str(Path(env["HOME"]) / ".claude")
        workspace = root / "empty-project"
        workspace.mkdir(mode=0o700)
        installation, runtime = install_fixture(root, env, lang.code)
        manifest = json.loads((runtime / "paket.json").read_text())
        manifest_valid = all(hashlib.sha256((runtime / item["path"]).read_bytes()).hexdigest() == item["sha256"]
                             for item in manifest["files"])
        skills = sorted((runtime / lang.skills_path).glob("*/SKILL.md"))
        metadata, bodies = {}, {}
        for path in skills:
            text = path.read_text(encoding="utf-8")
            metadata[path.parent.name] = next(line.removeprefix("description: ") for line in text.splitlines()
                                              if line.startswith("description: "))
            bodies[path.parent.name] = text.split("---", 2)[2].strip()
        for name, binary, probe, marker, rule in (
                ("codex", args.codex, codex_probe, "$", Path(env["CODEX_HOME"]) / "AGENTS.md"),
                ("claude-code", args.claude, partial(claude_probe, setting_sources="user,project"),
                 "/", Path(env["CLAUDE_CONFIG_DIR"]) / "CLAUDE.md")):
            core = rule.read_text(encoding="utf-8").strip()
            version = run([binary, "--version"], root, workspace, env, actual_home)
            discovery = probe(binary, root, workspace, env, actual_home, core, expected_texts=metadata)
            explicit_probe = codex_request_probe if name == "codex" else probe
            explicit = {skill: explicit_probe(binary, root, workspace, env, actual_home, core,
                         prompt=marker + skill + " Synthetic loader case. No external actions.",
                         expected_texts={"full_skill_body": body}) for skill, body in bodies.items()}
            rule.unlink()
            try:
                missing = probe(binary, root, workspace, env, actual_home, core)
            finally:
                write_private(rule, core + "\n")
            negative_passed = not missing["core_loaded"] and (
                missing.get("prompt_json", False) if name == "codex" else
                missing.get("captured_message_requests", 0) > 0 and missing["synthetic_error_observed"])
            clients.append({"client": name, "executable": binary, "version": version.stdout.strip(),
                            "global_core_sha256": hashlib.sha256(core.encode()).hexdigest(),
                            "discovery": discovery, "explicit_skills": explicit,
                            "negative_control": missing, "negative_control_passed": negative_passed})
    after = skill_listing(actual_home)
    proof_sources_unchanged = all(hashlib.sha256((PACKAGE / "scripts" / name).read_bytes()).hexdigest() == digest
                                  for name, digest in source_hashes.items())
    passed = installation["status"] == "installed" and installation["private_fixture_unchanged"] \
        and installation["installed_status_exit_code"] == 0 and installation["installed_status"]["status"] == "present" \
        and installation["repeat_blocked"] and manifest_valid and before == after and proof_sources_unchanged and all(
            item["discovery"]["core_loaded"] and item["negative_control_passed"]
            and not item["discovery"]["text_checks"].get(manual, True)
            and all(value for key, value in item["discovery"]["text_checks"].items() if key != manual)
            and all(record["core_loaded"] and record["text_checks"]["full_skill_body"]
                    and record["synthetic_error_observed"] for record in item["explicit_skills"].values())
            for item in clients)
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "passed": passed, "language": lang.code,
              "scope": "Synthetic first installation and native global loading. No model answer or service acceptance.",
              "installation": installation, "manifest_valid": manifest_valid,
              "proof_sources_sha256": source_hashes, "proof_sources_unchanged": proof_sources_unchanged,
              "package_manifest": manifest, "clients": clients, "skill_links_unchanged": before == after}
    destination_path(str(evidence_dir))
    evidence_dir.mkdir(mode=0o700)
    write_private(evidence_dir / "installation.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    write_private(evidence_dir / "skills-before.ls.txt", before)
    write_private(evidence_dir / "skills-after.ls.txt", after)
    print(json.dumps({"passed": passed, "evidence": str(evidence_dir / "installation.json"),
                      "clients": [{"client": item["client"], "version": item["version"],
                                   "core_loaded": item["discovery"]["core_loaded"],
                                   "skills_expanded": sum(record["text_checks"]["full_skill_body"]
                                                          for record in item["explicit_skills"].values()),
                                   "negative_control_passed": item["negative_control_passed"]} for item in clients]}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
