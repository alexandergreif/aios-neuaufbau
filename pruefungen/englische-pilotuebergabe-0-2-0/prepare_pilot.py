#!/usr/bin/env python3
"""Prepare and verify a local source archive. Does not publish or call models."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
ARCHIVE = HERE / "aios-0.2.0-dev-english-pilot-candidate.zip"
PREFIX = "aios-0.2.0-dev/"


def run(command, **kwargs):
    return subprocess.run(command, capture_output=True, text=True, **kwargs)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(*, guide=None, clients=None, destination=None, archive_name=None,
         manifest_name="PILOT-MANIFEST.json", status_label="local supervised pilot candidate",
         exercise_lifecycle=False):
    destination = destination or HERE
    archive_path = destination / archive_name if archive_name else ARCHIVE
    guide = guide or PACKAGE / "docs/english-pilot.md"
    clients = clients or ["codex"]
    if archive_path.exists() or (destination / "checks.json").exists():
        raise SystemExit("Candidate already exists. Inspect it before preparing another one.")
    commit = run(["git", "-C", str(PACKAGE), "rev-parse", "HEAD"], check=True).stdout.strip()
    if not commit.startswith("4504e8f"):
        raise SystemExit("Source commit changed. Review the intended candidate first.")
    run(["git", "-C", str(PACKAGE), "archive", "--format=zip", "--prefix=" + PREFIX,
         "--output=" + str(archive_path), commit], check=True)
    with zipfile.ZipFile(archive_path, "a", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(guide, PREFIX + "START-HERE.md")
        files = {item.filename: hashlib.sha256(archive.read(item)).hexdigest()
                 for item in archive.infolist() if not item.is_dir()}
        manifest = {"version": "0.2.0-dev", "status": status_label,
                    "source_commit": commit, "added_guide": "START-HERE.md", "files_sha256": files}
        archive.writestr(PREFIX + manifest_name, json.dumps(manifest, indent=2) + "\n")
    with tempfile.TemporaryDirectory(prefix="aios-pilot-archive-check-") as temporary:
        root = Path(temporary).resolve()
        with zipfile.ZipFile(archive_path) as archive:
            assert archive.testzip() is None
            assert all(not p.startswith("/") and ".." not in Path(p).parts for p in archive.namelist())
            archive.extractall(root)
        source = root / PREFIX.rstrip("/")
        home = root / "synthetic-home"
        profile = home / "profile"
        profile.mkdir(parents=True, mode=0o700)
        (home / ".codex").mkdir(mode=0o700)
        (home / ".claude").mkdir(mode=0o700)
        (root / "tmp").mkdir(mode=0o700)
        env = {"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "HOME": str(home),
               "CODEX_HOME": str(home / ".codex"), "CLAUDE_CONFIG_DIR": str(home / ".claude"),
               "TMPDIR": str(root / "tmp"),
               "LANG": "en_US.UTF-8", "PYTHONDONTWRITEBYTECODE": "1"}
        config = {"schema_version": 1, "confirmed": True, "language": "en", "clients": clients,
                  "paths": {"source": str(source), "runtime": "~/runtime", "profile": "~/profile",
                            "output": "~/output", "coding_roots": [], "customer_roots": []}}
        config_path = profile / "paths.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        (profile / "profile.md").write_text("# Invented pilot archive test profile\n\nLanguage: English\n", encoding="utf-8")
        command = [sys.executable, "-B", str(source / "scripts/install.py"), "--config", str(config_path),
                   "--home", str(home), "--codex-home", str(home / ".codex"),
                   "--claude-config-dir", str(home / ".claude"), "--apply"]
        install = run(command, env=env, input="yes\n", timeout=45)
        if install.returncode:
            raise SystemExit("Archive installation failed: " + install.stderr[-2000:])
        before = {p.name: digest(p) for p in profile.iterdir() if p.is_file()}
        repeat = run(command, env=env, input="yes\n", timeout=45)
        unchanged = before == {p.name: digest(p) for p in profile.iterdir() if p.is_file()}
        status = run([sys.executable, "-B", str(home / "runtime/scripts/setup_status.py"),
                      "--config", str(config_path), "--home", str(home),
                      "--codex-home", str(home / ".codex"), "--claude-config-dir", str(home / ".claude"),
                      "--json"], env=env, timeout=45)
        runtime_manifest = json.loads((home / "runtime/paket.json").read_text())
        integrity = all(digest(home / "runtime" / item["path"]) == item["sha256"]
                        for item in runtime_manifest["files"])
        links = len(list((home / ".agents/skills").iterdir()))
        client_links = {"codex": links}
        if "claude-code" in clients:
            client_links["claude-code"] = len(list((home / ".claude/skills").iterdir()))
        checks = {"source_commit": commit, "archive_sha256": digest(archive_path),
                  "guide_sha256": digest(guide), "archive_files": len(files) + 1,
                  "install_exit": install.returncode, "repeat_exit": repeat.returncode,
                  "private_test_profile_unchanged_after_repeat": unchanged,
                  "status_exit": status.returncode, "status_report": json.loads(status.stdout),
                  "runtime_manifest_files": len(runtime_manifest["files"]),
                  "runtime_integrity": integrity, "skill_links": links, "client_skill_links": client_links,
                  "provider_calls": 0, "published": False}
        assert repeat.returncode == 1 and unchanged
        assert status.returncode == 0 and integrity and links == 21
        assert all(count == 21 for count in client_links.values())
        if exercise_lifecycle:
            common = ["--config", str(config_path), "--home", str(home),
                      "--codex-home", str(home / ".codex"), "--claude-config-dir", str(home / ".claude")]
            update = [sys.executable, "-B", str(source / "scripts/update.py"), *common]
            update_preview = run(update, env=env, timeout=45)
            update_apply = run([*update, "--apply"], env=env, input="yes\n", timeout=45)
            uninstall = [sys.executable, "-B", str(source / "scripts/uninstall.py"), *common]
            uninstall_preview = run(uninstall, env=env, timeout=45)
            assert (home / ".codex/AGENTS.md").is_file() and (home / ".claude/CLAUDE.md").is_file()
            foreign = home / "runtime/foreign-test-note.txt"
            foreign.write_text("Invented foreign file, preserve it.\n", encoding="utf-8")
            uninstall_apply = run([*uninstall, "--apply"], env=env, input="yes\n", timeout=45)
            profile_kept = before == {p.name: digest(p) for p in profile.iterdir() if p.is_file()}
            client_rules_removed = not (home / ".codex/AGENTS.md").exists() and not (home / ".claude/CLAUDE.md").exists()
            checks["lifecycle"] = {"same_version_update_preview_exit": update_preview.returncode,
                                   "same_version_update_apply_exit": update_apply.returncode,
                                   "uninstall_preview_exit": uninstall_preview.returncode,
                                   "uninstall_apply_exit": uninstall_apply.returncode,
                                   "profile_files_preserved": profile_kept,
                                   "foreign_runtime_file_preserved": foreign.is_file(),
                                   "client_rule_files_removed": client_rules_removed}
            assert all(p.returncode == 0 for p in (update_preview, update_apply, uninstall_preview, uninstall_apply))
            assert profile_kept and foreign.is_file() and client_rules_removed
    with (destination / "checks.json").open("x", encoding="utf-8") as handle:
        json.dump(checks, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(checks, ensure_ascii=False))


if __name__ == "__main__":
    main()
