#!/usr/bin/env python3
"""Native Skillerkennung prüfen, ausschließlich mit lokalem Testserver."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from client_vorbereiten import PACKAGE, destination_path, prepare, source_contents
from einrichten import reject_symlink_components, write_private
from pruefe_client_loader import environment, codex_probe, codex_request_probe, claude_probe, skill_listing, run


def skill_sources():
    root = PACKAGE / "allgemein/skills"
    reject_symlink_components(root)
    result = {}
    for path in sorted(root.rglob("*")):
        reject_symlink_components(path)
        if path.is_file():
            result[path.relative_to(root)] = path.read_bytes()
    if not result:
        raise ValueError("Keine Skillquellen vorhanden")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex", default=shutil.which("codex"))
    parser.add_argument("--claude", default=shutil.which("claude"))
    parser.add_argument("--evidence-dir", help="Neuer absoluter Belegordner")
    args = parser.parse_args(argv)
    if not args.codex or not args.claude or not Path("/usr/bin/sandbox-exec").is_file():
        parser.error("Beide Clients und macOS sandbox-exec werden benötigt")
    evidence_dir = destination_path(args.evidence_dir) if args.evidence_dir else None
    sources = skill_sources()
    actual_home = Path.home().resolve()
    before = skill_listing(actual_home)
    results = []
    with tempfile.TemporaryDirectory(prefix="aios-skill-loader-") as temporary:
        root = Path(temporary).resolve()
        workspace = root / "workspace"
        prepare(workspace, source_contents())
        core = (workspace / "AGENTS.md").read_text(encoding="utf-8").strip()
        skill_root = workspace / "allgemein/skills"
        for relative, data in sources.items():
            path = skill_root / relative
            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            path.write_bytes(data)
        names = sorted(path.parts[0] for path in sources if len(path.parts) == 2 and path.name == "SKILL.md")
        for client_folder in (".claude", ".agents"):
            links = workspace / client_folder / "skills"
            links.mkdir(parents=True, mode=0o700)
            for name in names:
                (links / name).symlink_to(skill_root / name, target_is_directory=True)
        env = environment(root)
        bodies = {name: (skill_root / name / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[2].strip()
                  for name in names}
        metadata = {}
        for name in names:
            skill = (skill_root / name / "SKILL.md").read_text(encoding="utf-8")
            metadata[name] = next(line.removeprefix("description: ") for line in skill.splitlines()
                                  if line.startswith("description: "))
        for name, binary, probe, invocation in (("codex", args.codex, codex_probe, "$auftrag-vorbereiten"),
                                                ("claude-code", args.claude, claude_probe, "/auftrag-vorbereiten")):
            discovery = probe(binary, root, workspace, env, actual_home, core, expected_texts=metadata)
            explicit_probe = codex_request_probe if name == "codex" else probe
            explicit = {}
            for skill_name in names:
                explicit[skill_name] = explicit_probe(binary, root, workspace, env, actual_home, core,
                    prompt=invocation[0] + skill_name + " Synthetischer Loaderfall. Keine externen Aktionen.",
                    expected_texts={"full_skill_body": bodies[skill_name]})
            version = run([binary, "--version"], root, workspace, env, actual_home)
            results.append({"client": name, "executable": binary, "version": version.stdout.strip(),
                            "discovery": discovery, "explicit_skills": explicit})
    after = skill_listing(actual_home)
    report = {"scope": "Native Skillmetadaten und explizite Expansion, keine Modell-Verhaltensprüfung",
              "checked_at": datetime.now(timezone.utc).isoformat(),
              "source_hashes": {str(path): hashlib.sha256(data).hexdigest() for path, data in sources.items()},
              "clients": results, "skill_links_unchanged": before == after}
    if evidence_dir:
        destination_path(str(evidence_dir))
        evidence_dir.mkdir(mode=0o700)
        write_private(evidence_dir / "skills.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        write_private(evidence_dir / "skills-vorher.ls.txt", before)
        write_private(evidence_dir / "skills-nachher.ls.txt", after)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if before == after and all(
        not item["discovery"]["text_checks"].get("auftrag-vorbereiten", True)
        and all(value for key, value in item["discovery"]["text_checks"].items() if key != "auftrag-vorbereiten")
        and all(record["core_loaded"] and record["text_checks"]["full_skill_body"]
                and record["synthetic_error_observed"] for record in item["explicit_skills"].values())
        for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
