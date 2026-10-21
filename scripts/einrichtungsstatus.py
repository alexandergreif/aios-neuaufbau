#!/usr/bin/env python3
"""Prüfe die lokale AIOS-Dateieinbindung ohne Client- oder Dienstaufruf."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

import pruefe_konfiguration as pruefer
import sichere_dateien as sicher
import paketbestand as bestand
from paketregeln import allowed_file


HASH = re.compile(r"[0-9a-f]{64}\Z")
SKILL = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
MAX_JSON = 4 * 1024 * 1024


class StatusError(ValueError):
    pass


def read_file(path, limit=None):
    parent_fd, name = sicher.parent(path)
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent_fd)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode):
                raise StatusError("Dateityp ungültig")
            chunks = []
            size = 0
            while chunk := os.read(fd, 65536):
                size += len(chunk)
                if limit is not None and size > limit:
                    raise StatusError("JSON-Datei zu groß")
                chunks.append(chunk)
            after = os.fstat(fd)
            current = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            def identity(info):
                return info.st_dev, info.st_ino, info.st_mtime_ns, info.st_size
            if not stat.S_ISREG(current.st_mode) or identity(before) != identity(after) or identity(after) != identity(current):
                raise StatusError("Datei während der Prüfung verändert")
            sicher.assert_directory_at_path(Path(path).parent, parent_fd)
            return b"".join(chunks)
        finally:
            os.close(fd)
    finally:
        os.close(parent_fd)


def read_json(path):
    try:
        return json.loads(read_file(path, MAX_JSON).decode("utf-8"), object_pairs_hook=pruefer.unique_object)
    except (UnicodeError, json.JSONDecodeError, pruefer.ConfigurationError) as error:
        raise StatusError("JSON ungültig") from error


def fields(obj, names):
    if not isinstance(obj, dict) or set(obj) != set(names):
        raise StatusError("Schema ungültig")


def client_dir(raw, default):
    if raw is None:
        return default
    path = Path(raw)
    if not path.is_absolute() or str(path).startswith("//") or ".." in path.parts:
        raise StatusError("Clientordner ungültig")
    return path


def manifest_entries(manifest):
    fields(manifest, ("schema_version", "version", "files"))
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
        raise StatusError("Manifestversion ungültig")
    if not isinstance(manifest["version"], str) or not manifest["version"]:
        raise StatusError("Paketversion ungültig")
    if not isinstance(manifest["files"], list) or not manifest["files"]:
        raise StatusError("Manifestdateien fehlen")
    entries = {}
    for entry in manifest["files"]:
        fields(entry, ("path", "sha256"))
        raw = entry["path"]
        digest = entry["sha256"]
        if (not allowed_file(raw) or not isinstance(digest, str) or
                not HASH.fullmatch(digest) or raw in entries):
            raise StatusError("Manifestpfad oder Hash ungültig")
        entries[raw] = digest
    if "allgemein/regeln/kern.md" not in entries:
        raise StatusError("Regelkern fehlt im Manifest")
    return entries


def expected_targets(runtime, clients, names, home, codex, claude):
    bound = {"codex": str(codex), "claude-code": str(claude), "codex_skills": str(home / ".agents/skills")}
    targets = bestand.client_targets(runtime, clients, names, bound)
    rules = {path: item["client"] for path, item in targets.items() if item["role"] == "client_rule"}
    links = {path: (item["client"], item["target"]) for path, item in targets.items() if item["role"] == "client_link"}
    if len(rules) != len(clients) or len(links) != len(clients) * len(names):
        raise StatusError("Doppelte Clientziele")
    return rules, links


def validate_state(state, config, runtime, profile, output, entries, rules, links, version):
    fields(state, ("schema_version", "version", "status", "runtime", "clients", "created_directories", "created"))
    if (type(state["schema_version"]) is not int or state["schema_version"] != 1 or
            state["version"] != version or state["runtime"] != str(runtime) or
            state["clients"] != config["clients"] or
            state["status"] not in ("installing", "installed", "failed") or
            not isinstance(state["created_directories"], list) or not isinstance(state["created"], list)):
        raise StatusError("Eigentumsstand passt nicht zur Konfiguration")
    allowed_files = {str(runtime / rel): digest for rel, digest in entries.items()}
    allowed_files[str(runtime / "paket.json")] = None
    seen = set()
    for item in state["created"]:
        if not isinstance(item, dict) or item.get("type") not in ("file", "link"):
            raise StatusError("Eigentumseintrag ungültig")
        path = item.get("path")
        if not isinstance(path, str) or path in seen:
            raise StatusError("Eigentumspfad ungültig")
        seen.add(path)
        if item["type"] == "file":
            if path not in allowed_files or not isinstance(item.get("sha256"), str) or not HASH.fullmatch(item["sha256"]):
                if path not in rules or not isinstance(item.get("sha256"), str) or not HASH.fullmatch(item["sha256"]):
                    raise StatusError("Fremder Eigentumspfad")
            if path in allowed_files and allowed_files[path] is not None and item["sha256"] != allowed_files[path]:
                raise StatusError("Eigentumshash widerspricht Manifest")
        else:
            if path not in links or item.get("target") != links[path][1]:
                raise StatusError("Fremder Linkpfad")
    allowed_dirs = {str(profile / "zustand")}
    for target in [*allowed_files, *rules, *links, str(output / "placeholder")]:
        current = Path(target).parent
        while current != Path("/"):
            allowed_dirs.add(str(current))
            current = current.parent
    if any(not isinstance(raw, str) or raw not in allowed_dirs for raw in state["created_directories"]):
        raise StatusError("Fremder Verzeichnispfad im Eigentumsstand")
    return seen


def inspect(config_path, home, codex_raw=None, claude_raw=None):
    config = read_json(config_path)
    pruefer.validate(config, home)
    profile = pruefer.parse_path(config["paths"]["profile"], "paths.profile", home)
    if config_path != profile / "pfade.json":
        raise StatusError("Konfiguration liegt nicht im bestätigten Profil")
    runtime = pruefer.parse_path(config["paths"]["runtime"], "paths.runtime", home)
    output = pruefer.parse_path(config["paths"]["output"], "paths.output", home)
    codex = client_dir(codex_raw, home / ".codex")
    claude = client_dir(claude_raw, home / ".claude")
    result = {"status": "vorhanden", "dateieinbindung": "geprüft", "fachfunktion": "ungeprüft",
              "clients": [], "probleme": []}
    for client in config["clients"]:
        result["clients"].append({"client": client, "status": "vorhanden", "skills": 0,
                                  "integritaet": "geprüft", "modell_dienste": "ungeprüft"})
    state_dir = profile / "zustand"
    try:
        operation_raw = bestand.read_snapshot(state_dir / "operation.json")[0]
    except FileNotFoundError:
        operation_raw = None
    except (OSError, ValueError):
        operation_raw = b"{}"
    if operation_raw is not None:
        try:
            operation = bestand.decode(operation_raw)
            if not isinstance(operation, dict) or operation.get("status") != "completed":
                raise StatusError("Offene Operation")
        except ValueError:
            result.update(status="eingeschränkt", dateieinbindung="eingeschränkt")
            result["probleme"].append("Offene oder unlesbare Paketoperation. Keine automatische Wiederholung.")
            for item in result["clients"]:
                item.update(status="eingeschränkt", integritaet="eingeschränkt")
            return result
    if (state_dir / "bestand.json").exists() or (state_dir / "bestand.json").is_symlink():
        return inspect_confirmed(result, config, config_path, home, codex_raw, claude_raw)
    object_name = "Runtime-Manifest paket.json"
    try:
        manifest = read_json(runtime / "paket.json")
        entries = manifest_entries(manifest)
        names = sorted({parts[2] for raw in entries for parts in [raw.split("/")]
                        if len(parts) == 4 and parts[:2] == ["allgemein", "skills"] and parts[3] == "SKILL.md"})
        if not names or any(not SKILL.fullmatch(name) for name in names):
            raise StatusError("Skillquellen im Manifest ungültig")
        rules, links = expected_targets(runtime, config["clients"], names, home, codex, claude)
        object_name = "Eigentumsdatei installation.json"
        state = read_json(profile / "zustand/installation.json")
        seen = validate_state(state, config, runtime, profile, output, entries, rules, links, manifest["version"])
        expected_seen = {str(runtime / rel) for rel in entries} | {str(runtime / "paket.json")} | set(rules) | set(links)
        if state["status"] != "installed" or seen != expected_seen:
            raise StatusError("Einrichtung nicht vollständig abgeschlossen")
        object_name = "Ausgabeordner"
        output_fd = sicher.directory(output)
        os.close(output_fd)
        object_name = "Runtime-Manifest paket.json"
        manifest_item = next(item for item in state["created"] if item["path"] == str(runtime / "paket.json"))
        if hashlib.sha256(read_file(runtime / "paket.json")).hexdigest() != manifest_item["sha256"]:
            raise StatusError("Paketmanifest verändert")
        for raw, digest in entries.items():
            object_name = f"Paketdatei {raw}"
            if hashlib.sha256(read_file(runtime / raw)).hexdigest() != digest:
                raise StatusError("Paketdatei verändert")
    except FileNotFoundError:
        result["status"] = "fehlend"
        result["dateieinbindung"] = "fehlend"
        result["probleme"].append(f"{object_name} fehlt. Nächster Schritt: Einrichtungsstand prüfen.")
    except (StatusError, OSError, ValueError):
        result["status"] = "eingeschränkt"
        result["dateieinbindung"] = "eingeschränkt"
        result["probleme"].append(f"{object_name} ungültig oder verändert. Nächster Schritt: Installation prüfen.")
    if result["status"] != "vorhanden":
        for item in result["clients"]:
            item["status"] = result["status"]
            item["integritaet"] = result["dateieinbindung"]
        return result

    owned = {item["path"]: item for item in state["created"]}
    for client_item in result["clients"]:
        client = client_item["client"]
        for path, owner in rules.items():
            if owner != client:
                continue
            try:
                if hashlib.sha256(read_file(path)).hexdigest() != owned[path]["sha256"]:
                    raise StatusError("Globale Regeldatei verändert")
            except FileNotFoundError:
                client_item["status"] = "fehlend"
                result["probleme"].append(f"{client}: Regeldatei fehlt. Nächster Schritt: Client-Einbindung prüfen.")
            except (StatusError, OSError, ValueError):
                if client_item["status"] == "vorhanden":
                    client_item["status"] = "eingeschränkt"
                result["probleme"].append(f"{client}: Regeldatei verändert. Nächster Schritt: Client-Einbindung prüfen.")
        for path, (owner, source) in links.items():
            if owner != client:
                continue
            skill_name = Path(path).name
            try:
                parent_fd, name = sicher.parent(path)
                try:
                    info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
                    if not stat.S_ISLNK(info.st_mode) or os.readlink(name, dir_fd=parent_fd) != source:
                        raise StatusError("Skillverknüpfung verändert")
                    sicher.assert_directory_at_path(Path(path).parent, parent_fd)
                finally:
                    os.close(parent_fd)
                client_item["skills"] += 1
            except FileNotFoundError:
                client_item["status"] = "fehlend"
                result["probleme"].append(f"{client}: Skillverknüpfung {skill_name} fehlt. Nächster Schritt: Link prüfen.")
            except (StatusError, OSError, ValueError):
                if client_item["status"] == "vorhanden":
                    client_item["status"] = "eingeschränkt"
                result["probleme"].append(f"{client}: Skillverknüpfung {skill_name} verändert. Nächster Schritt: Link prüfen.")
        client_item["integritaet"] = "geprüft" if client_item["status"] == "vorhanden" else client_item["status"]
    if any(item["status"] == "fehlend" for item in result["clients"]):
        result["status"] = "fehlend"
    elif any(item["status"] == "eingeschränkt" for item in result["clients"]):
        result["status"] = "eingeschränkt"
    if result["status"] != "vorhanden":
        result["dateieinbindung"] = result["status"]
    return result


def inspect_confirmed(result, config, config_path, home, codex, claude):
    try:
        paths = bestand.areas(config, home)
        state = bestand.decode(bestand.read_snapshot(Path(paths["profile"]) / "zustand/bestand.json")[0])
        bestand.validate(state, config, home, codex, claude)
        if state["status"] == "uninstalled":
            for path in state["owned"]:
                bestand.check_target(path, None)
            result.update(status="deinstalliert", dateieinbindung="fehlend")
            for item in result["clients"]:
                item.update(status="deinstalliert", integritaet="fehlend")
            return result
        bestand.verify_manifest(state)
        for path, item in state["owned"].items():
            if item["role"] == "runtime_file":
                bestand.check_target(path, item)
        output_fd = sicher.directory(paths["output"])
        os.close(output_fd)
    except (OSError, ValueError, TypeError, KeyError) as error:
        status = "fehlend" if isinstance(error, FileNotFoundError) else "eingeschränkt"
        result.update(status=status, dateieinbindung=status)
        result["probleme"].append("Abgeschlossener Paketbestand oder Runtime ungültig, verändert oder fehlend.")
        for item in result["clients"]:
            item.update(status=status, integritaet=status)
        return result
    for client in result["clients"]:
        for path, item in state["owned"].items():
            if item.get("client") != client["client"]:
                continue
            try:
                bestand.check_target(path, item)
                if item["role"] == "client_link":
                    client["skills"] += 1
            except (OSError, ValueError) as error:
                status = "fehlend" if isinstance(error, FileNotFoundError) else "eingeschränkt"
                if client["status"] != "fehlend":
                    client.update(status=status, integritaet=status)
                result["probleme"].append(f"{client['client']}: {Path(path).name} fehlt oder wurde verändert.")
    statuses = {item["status"] for item in result["clients"]}
    status = "fehlend" if "fehlend" in statuses else "eingeschränkt" if "eingeschränkt" in statuses else "vorhanden"
    result.update(status=status, dateieinbindung="geprüft" if status == "vorhanden" else status)
    return result


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
            raise StatusError("Benutzerordner ungültig")
        home = pruefer.resolve_directory_candidate(args.home, "--home")
        if not home.is_dir() or home == Path("/"):
            raise StatusError("Benutzerordner ungültig")
        result = inspect(args.config.absolute(), home, args.codex_home, args.claude_config_dir)
    except (StatusError, pruefer.ConfigurationError, OSError):
        print("Einrichtungsstatus: bestätigte Konfiguration ungültig oder nicht lesbar", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Dateieinbindung: {result['status']}. Fachfunktion, Modelle und Dienste ungeprüft.")
        for item in result["clients"]:
            print(f"{item['client']}: {item['status']}, {item['skills']} Skillverknüpfungen, Integrität {item['integritaet']}, Modell und Dienste ungeprüft")
        for problem in result["probleme"]:
            print(problem)
    return 0 if result["status"] == "vorhanden" else 1


if __name__ == "__main__":
    sys.exit(main())
