#!/usr/bin/env python3
"""Erstinstallation in erfundenem Home und native Ladung ohne Anbieter prüfen."""

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

from client_vorbereiten import PACKAGE, destination_path
from einrichten import write_private
from pruefe_client_loader import (
    environment, codex_probe, codex_request_probe, claude_probe, run, skill_listing,
)


def install_fixture(root, env):
    home = Path(env["HOME"])
    profile = home / "profil"
    profile.mkdir(mode=0o700)
    config = {"schema_version": 1, "confirmed": True, "clients": ["claude-code", "codex"],
              "paths": {"source": str(PACKAGE), "runtime": "~/runtime", "profile": "~/profil",
                        "output": "~/output", "coding_roots": [], "customer_roots": []}}
    config_path = profile / "pfade.json"
    write_private(config_path, json.dumps(config) + "\n")
    # Absichtlich erfundene Testwerte. Keine Inhalte aus einem echten Profil.
    write_private(profile / "profil.md", "Synthetisches Testprofil\n")
    write_private(profile / ".env", "BLOCKBRAIN_API_KEY=synthetic-not-a-real-key\n")
    originals = {path: path.read_bytes() for path in profile.iterdir()}
    command = [sys.executable, str(PACKAGE / "scripts/installieren.py"), "--config", str(config_path),
               "--home", str(home), "--codex-home", env["CODEX_HOME"],
               "--claude-config-dir", env["CLAUDE_CONFIG_DIR"], "--apply"]
    result = subprocess.run(command, input="ja\n", text=True, capture_output=True, env=env, timeout=30)
    if result.returncode:
        raise RuntimeError("Synthetische Erstinstallation fehlgeschlagen: " + result.stderr)
    state = json.loads((profile / "zustand/installation.json").read_text())
    repeat = subprocess.run(command, input="ja\n", text=True, capture_output=True, env=env, timeout=30)
    status_command = [sys.executable, str(home / "runtime/scripts/einrichtungsstatus.py"),
                      "--config", str(config_path), "--home", str(home),
                      "--codex-home", env["CODEX_HOME"], "--claude-config-dir", env["CLAUDE_CONFIG_DIR"], "--json"]
    status = subprocess.run(status_command, cwd=root, text=True, capture_output=True, env=env, timeout=30)
    try:
        status_report = json.loads(status.stdout)
    except json.JSONDecodeError:
        status_report = {"status": "ungeprüft", "error": "Kein gültiger JSON-Status"}
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
    parser.add_argument("--evidence-dir", required=True, help="Neuer absoluter Belegordner")
    args = parser.parse_args(argv)
    if not args.codex or not args.claude or not Path("/usr/bin/sandbox-exec").is_file():
        parser.error("Beide Clients und macOS sandbox-exec werden benötigt")
    evidence_dir = destination_path(args.evidence_dir)
    proof_sources = ["installieren.py", "installationsplan.py", "paket_bauen.py", "sichere_dateien.py",
                     "einrichten.py", "pruefe_konfiguration.py", "einrichtungsstatus.py", "paketregeln.py", "client_vorbereiten.py",
                     "pruefe_client_loader.py", "pruefe_installation_lokal.py"]
    source_hashes = {name: hashlib.sha256((PACKAGE / "scripts" / name).read_bytes()).hexdigest()
                     for name in proof_sources}
    actual_home = Path.home().resolve()
    before = skill_listing(actual_home)
    clients = []
    with tempfile.TemporaryDirectory(prefix="aios-installed-loader-") as temporary:
        root = Path(temporary).resolve()
        env = environment(root)
        # Prüfe normale globale Ordner, keine projektlokalen Skills oder Regeldateien.
        env["CODEX_HOME"] = str(Path(env["HOME"]) / ".codex")
        env["CLAUDE_CONFIG_DIR"] = str(Path(env["HOME"]) / ".claude")
        workspace = root / "leeres-projekt"
        workspace.mkdir(mode=0o700)
        installation, runtime = install_fixture(root, env)
        manifest = json.loads((runtime / "paket.json").read_text())
        manifest_valid = all(hashlib.sha256((runtime / item["path"]).read_bytes()).hexdigest() == item["sha256"]
                             for item in manifest["files"])
        skills = sorted((runtime / "allgemein/skills").glob("*/SKILL.md"))
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
                         prompt=marker + skill + " Synthetischer Loaderfall. Keine externen Aktionen.",
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
        and installation["installed_status_exit_code"] == 0 and installation["installed_status"]["status"] == "vorhanden" \
        and installation["repeat_blocked"] and manifest_valid and before == after and proof_sources_unchanged and all(
            item["discovery"]["core_loaded"] and item["negative_control_passed"]
            and not item["discovery"]["text_checks"].get("auftrag-vorbereiten", True)
            and all(value for key, value in item["discovery"]["text_checks"].items() if key != "auftrag-vorbereiten")
            and all(record["core_loaded"] and record["text_checks"]["full_skill_body"]
                    and record["synthetic_error_observed"] for record in item["explicit_skills"].values())
            for item in clients)
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "passed": passed,
              "scope": "Synthetische Erstinstallation und native globale Ladung. Keine Modellantwort oder Dienstabnahme.",
              "installation": installation, "manifest_valid": manifest_valid,
              "proof_sources_sha256": source_hashes, "proof_sources_unchanged": proof_sources_unchanged,
              "package_manifest": manifest, "clients": clients, "skill_links_unchanged": before == after}
    destination_path(str(evidence_dir))
    evidence_dir.mkdir(mode=0o700)
    write_private(evidence_dir / "installation.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    write_private(evidence_dir / "skills-vorher.ls.txt", before)
    write_private(evidence_dir / "skills-nachher.ls.txt", after)
    print(json.dumps({"passed": passed, "evidence": str(evidence_dir / "installation.json"),
                      "clients": [{"client": item["client"], "version": item["version"],
                                   "core_loaded": item["discovery"]["core_loaded"],
                                   "skills_expanded": sum(record["text_checks"]["full_skill_body"]
                                                          for record in item["explicit_skills"].values()),
                                   "negative_control_passed": item["negative_control_passed"]} for item in clients]}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
