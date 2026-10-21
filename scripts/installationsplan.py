#!/usr/bin/env python3
"""Erzeuge einen rein lesenden Vorabplan für eine spätere AIOS-Installation."""

import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys

import pruefe_konfiguration as pruefer
import paketbestand as bestand
from einrichten import reject_symlink_components


PACKAGE = Path(__file__).resolve().parent.parent
SKILLS = PACKAGE / "allgemein/skills"


class PlanError(Exception):
    pass


def existing_mode(path):
    try:
        return path.lstat().st_mode
    except FileNotFoundError:
        return None


def inspect_path(path, expected="absent"):
    """Check only target and parent metadata, without opening their contents."""
    path = Path(path)
    current = Path(path.anchor)
    for component in path.parts[1:-1]:
        current /= component
        mode = existing_mode(current)
        if mode is None:
            break
        if stat.S_ISLNK(mode):
            return f"Symlink im Elternpfad: {current}"
        if not stat.S_ISDIR(mode):
            return f"Datei statt Ordner im Elternpfad: {current}"
    mode = existing_mode(path)
    if mode is None:
        return None
    if stat.S_ISLNK(mode):
        return f"Symlink am Ziel: {path}"
    if expected == "directory":
        return None if stat.S_ISDIR(mode) else f"Datei statt Ordner: {path}"
    return f"Ziel existiert bereits: {path}"


def skill_names():
    reject_symlink_components(SKILLS)
    if not SKILLS.is_dir() or SKILLS.is_symlink():
        raise PlanError("Paket-Skillordner fehlt oder ist ein Symlink")
    names = []
    for child in sorted(SKILLS.iterdir()):
        mode = existing_mode(child)
        if stat.S_ISLNK(mode):
            raise PlanError("Symlink im Paket-Skillordner")
        if not stat.S_ISDIR(mode):
            continue
        source = child / "SKILL.md"
        source_mode = existing_mode(source)
        if source_mode is None:
            continue
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", child.name) or not stat.S_ISREG(source_mode):
            raise PlanError("Ungültige Paket-Skillquelle")
        names.append(child.name)
    return names


def client_dir(raw, default, label):
    if raw is None:
        return default
    path = Path(raw)
    if not path.is_absolute() or str(path).startswith("//") or ".." in path.parts:
        raise PlanError(f"{label} muss ein absoluter Pfad sein")
    return path


def plan(config, home, codex_home=None, claude_config_dir=None, environ=None):
    environ = os.environ if environ is None else environ
    pruefer.validate(config, home)
    paths = {name: pruefer.parse_path(config["paths"][name], f"paths.{name}", home)
             for name in ("source", "runtime", "profile", "output")}
    codex = client_dir(codex_home, home / ".codex", "--codex-home")
    claude = client_dir(claude_config_dir, home / ".claude", "--claude-config-dir")
    names = skill_names()
    conflicts = []
    clarifications = []
    observations = []
    rules = []
    links = []

    selected_dirs = []
    if "claude-code" in config["clients"]:
        selected_dirs.append(("Claude", claude))
    if "codex" in config["clients"]:
        selected_dirs.append(("Codex", codex))
    for label, directory in selected_dirs:
        if pruefer.comparable_parts(directory) in (pruefer.comparable_parts(Path("/")),
                                                    pruefer.comparable_parts(home)):
            conflicts.append(f"{label}-Ordner darf weder Systemwurzel noch Benutzerordner sein: {directory}")
        for area, area_path in paths.items():
            if pruefer.overlaps(directory, area_path):
                conflicts.append(f"{label}-Ordner überschneidet sich mit paths.{area}: {directory}")
    if len(selected_dirs) == 2 and pruefer.overlaps(claude, codex):
        conflicts.append("Claude- und Codex-Ordner überschneiden sich")
    if "codex" in config["clients"]:
        codex_skill_base = home / ".agents/skills"
        issue = inspect_path(codex_skill_base, "directory")
        if issue:
            conflicts.append(f"Codex-Skillbasis: {issue}")
        for area, area_path in paths.items():
            if pruefer.overlaps(codex_skill_base, area_path):
                conflicts.append(f"Codex-Skillbasis überschneidet sich mit paths.{area}: {codex_skill_base}")
        for label, directory in selected_dirs:
            if pruefer.overlaps(codex_skill_base, directory):
                conflicts.append(f"Codex-Skillbasis überschneidet sich mit {label}-Ordner: {codex_skill_base}")

    for label, path, expected in (("Runtime", paths["runtime"], "absent"),
                                  ("Ausgabe", paths["output"], "directory"),
                                  ("Profil", paths["profile"], "directory")):
        issue = inspect_path(path, expected)
        if issue:
            conflicts.append(f"{label}: {issue}")
        elif path.exists():
            observations.append(f"{label} vorhanden, Inhalt ungeprüft: {path}")

    if "claude-code" in config["clients"]:
        issue = inspect_path(claude, "directory")
        if issue:
            conflicts.append(f"Claude-Ordner: {issue}")
        metadata = [claude / "settings.json", claude / ".mcp.json"]
    else:
        metadata = []
    if "codex" in config["clients"]:
        issue = inspect_path(codex, "directory")
        if issue:
            conflicts.append(f"Codex-Ordner: {issue}")
        override = codex / "AGENTS.override.md"
        issue = inspect_path(override)
        if issue:
            conflicts.append(f"Codex-Override: {issue}")
        metadata.append(codex / "config.toml")

    try:
        bound = bestand.bindings(config, home, {key: str(value) for key, value in paths.items()},
                                 str(codex), str(claude))
    except (ValueError, OSError) as error:
        conflicts.append(str(error))
        bound = {}

    if bound:
        for target, item in bestand.client_targets(paths["runtime"], config["clients"], names, bound).items():
            if item["role"] == "client_rule":
                rules.append({"client": item["client"], "target": target,
                              "source": str(paths["runtime"] / Path(target).name)})
            else:
                links.append({"client": item["client"], "name": Path(target).name,
                              "target": target, "source": item["target"]})

    for item in rules + links:
        issue = inspect_path(item["target"])
        if issue:
            conflicts.append(f"{item['client']} {item.get('name', 'Regel')}: {issue}")
    targets = {}
    for item in rules + links:
        key = pruefer.comparable_parts(Path(item["target"]))
        if key in targets:
            conflicts.append(f"Doppeltes Ziel für {targets[key]} und {item['client']}: {item['target']}")
        else:
            targets[key] = item["client"]
    for path in metadata:
        issue = inspect_path(path, "directory")
        if issue and not issue.startswith("Ziel existiert bereits") and "Datei statt Ordner:" not in issue:
            conflicts.append(f"Client-Metadaten: {issue}")
        elif existing_mode(path) is not None:
            observations.append(f"Vorhanden, Inhalt und Verbindungen ungeprüft: {path}")

    for key, explicit, default, selected in (("CODEX_HOME", codex_home, codex, "codex"),
                                             ("CLAUDE_CONFIG_DIR", claude_config_dir, claude, "claude-code")):
        env_value = environ.get(key)
        if selected in config["clients"] and explicit is None and env_value and env_value != str(default):
            clarifications.append(f"Klärung nötig: {key} weicht vom geplanten Clientordner ab: {env_value}. Nicht automatisch übernommen.")


    return {"schema_version": 1, "clients": config["clients"], "runtime": str(paths["runtime"]),
            "output": str(paths["output"]), "profile": str(paths["profile"]),
            "rules": rules, "skills": links, "observations": observations, "bindings": bound,
            "clarifications": clarifications, "conflicts": conflicts}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--codex-home")
    parser.add_argument("--claude-config-dir")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if not args.home.is_absolute() or str(args.home).startswith("//"):
            raise PlanError("--home muss ein absoluter Benutzerordner sein")
        home = pruefer.resolve_directory_candidate(args.home, "--home")
        if not home.is_dir() or home == Path("/"):
            raise PlanError("--home muss ein vorhandener Benutzerordner sein")
        with args.config.open("r", encoding="utf-8") as stream:
            config = json.load(stream, object_pairs_hook=pruefer.unique_object)
        result = plan(config, home, args.codex_home, args.claude_config_dir)
    except (PlanError, pruefer.ConfigurationError, OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"Installationsplan ungültig: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Runtime geplant: {result['runtime']}")
        print(f"Ausgabe: {result['output']}. Profil bleibt unangetastet: {result['profile']}")
        for item in result["rules"]:
            print(f"Regel {item['client']}: {item['source']} -> {item['target']}")
        for item in result["skills"]:
            print(f"Skill {item['client']} {item['name']}: {item['source']} -> {item['target']}")
        for message in result["observations"] + result["clarifications"] + result["conflicts"]:
            print(message)
        print("Nur Vorabplan. Keine Installation oder Funktionsprüfung ausgeführt.")
    return 1 if result["conflicts"] or result["clarifications"] else 0


if __name__ == "__main__":
    sys.exit(main())
