#!/usr/bin/env python3
"""Check the local AIOS file integration without calling clients or services."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

import check_config as pruefer
import languages
import safe_files as sicher
import package_inventory as bestand
from package_rules import allowed_file


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
                raise StatusError("Invalid file type")
            chunks = []
            size = 0
            while chunk := os.read(fd, 65536):
                size += len(chunk)
                if limit is not None and size > limit:
                    raise StatusError("JSON file too large")
                chunks.append(chunk)
            after = os.fstat(fd)
            current = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            def identity(info):
                return info.st_dev, info.st_ino, info.st_mtime_ns, info.st_size
            if not stat.S_ISREG(current.st_mode) or identity(before) != identity(after) or identity(after) != identity(current):
                raise StatusError("File changed during the check")
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
        raise StatusError("Invalid JSON") from error


def fields(obj, names):
    if not isinstance(obj, dict) or set(obj) != set(names):
        raise StatusError("Invalid schema")


def client_dir(raw, default):
    if raw is None:
        return default
    path = Path(raw)
    if not path.is_absolute() or str(path).startswith("//") or ".." in path.parts:
        raise StatusError("Invalid client folder")
    return path


def manifest_language(manifest):
    try:
        return bestand.manifest_language(manifest)
    except bestand.BestandError as error:
        raise StatusError("Invalid manifest schema") from error


def manifest_entries(manifest):
    language = manifest_language(manifest)
    # Old German script names only in manifests without a language field (0.1.7-dev and older).
    legacy = "language" not in manifest
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
        raise StatusError("Invalid manifest version")
    if not isinstance(manifest["version"], str) or not manifest["version"]:
        raise StatusError("Invalid package version")
    if not isinstance(manifest["files"], list) or not manifest["files"]:
        raise StatusError("Manifest files missing")
    entries = {}
    for entry in manifest["files"]:
        fields(entry, ("path", "sha256"))
        raw = entry["path"]
        digest = entry["sha256"]
        if (not allowed_file(raw, language, legacy_scripts=legacy) or not isinstance(digest, str) or
                not HASH.fullmatch(digest) or raw in entries):
            raise StatusError("Invalid manifest path or hash")
        entries[raw] = digest
    if languages.get(language).core_path not in entries:
        raise StatusError("Core rules missing in the manifest")
    return entries


def expected_targets(runtime, clients, names, home, codex, claude, language=languages.DEFAULT):
    bound = {"codex": str(codex), "claude-code": str(claude), "codex_skills": str(home / ".agents/skills")}
    targets = bestand.client_targets(runtime, clients, names, bound, language)
    rules = {path: item["client"] for path, item in targets.items() if item["role"] == "client_rule"}
    links = {path: (item["client"], item["target"]) for path, item in targets.items() if item["role"] == "client_link"}
    if len(rules) != len(clients) or len(links) != len(clients) * len(names):
        raise StatusError("Duplicate client targets")
    return rules, links


def validate_state(state, config, runtime, profile, output, entries, rules, links, version,
                   state_dir=None):
    fields(state, ("schema_version", "version", "status", "runtime", "clients", "created_directories", "created"))
    if (type(state["schema_version"]) is not int or state["schema_version"] != 1 or
            state["version"] != version or state["runtime"] != str(runtime) or
            state["clients"] != config["clients"] or
            state["status"] not in ("installing", "installed", "failed") or
            not isinstance(state["created_directories"], list) or not isinstance(state["created"], list)):
        raise StatusError("Ownership state does not match the configuration")
    allowed_files = {str(runtime / rel): digest for rel, digest in entries.items()}
    allowed_files[str(runtime / "paket.json")] = None
    seen = set()
    for item in state["created"]:
        if not isinstance(item, dict) or item.get("type") not in ("file", "link"):
            raise StatusError("Invalid ownership entry")
        path = item.get("path")
        if not isinstance(path, str) or path in seen:
            raise StatusError("Invalid ownership path")
        seen.add(path)
        if item["type"] == "file":
            if path not in allowed_files or not isinstance(item.get("sha256"), str) or not HASH.fullmatch(item["sha256"]):
                if path not in rules or not isinstance(item.get("sha256"), str) or not HASH.fullmatch(item["sha256"]):
                    raise StatusError("Foreign ownership path")
            if path in allowed_files and allowed_files[path] is not None and item["sha256"] != allowed_files[path]:
                raise StatusError("Ownership hash contradicts the manifest")
        else:
            if path not in links or item.get("target") != links[path][1]:
                raise StatusError("Foreign link path")
    allowed_dirs = {str(state_dir or profile / languages.of_config(config).state_dir)}
    for target in [*allowed_files, *rules, *links, str(output / "placeholder")]:
        current = Path(target).parent
        while current != Path("/"):
            allowed_dirs.add(str(current))
            current = current.parent
    if any(not isinstance(raw, str) or raw not in allowed_dirs for raw in state["created_directories"]):
        raise StatusError("Foreign directory path in the ownership state")
    return seen


PRESENT, MISSING, LIMITED, UNINSTALLED = "present", "missing", "limited", "uninstalled"
CHECKED, UNCHECKED = "checked", "unchecked"


def inspect(config_path, home, codex_raw=None, claude_raw=None):
    config = read_json(config_path)
    pruefer.validate(config, home)
    lang = languages.of_config(config)
    profile = pruefer.parse_path(config["paths"]["profile"], "paths.profile", home)
    if config_path != profile / lang.config_name:
        raise StatusError(languages.config_name_mismatch(config_path, profile, lang)
                          or "Configuration is not in the confirmed profile")
    runtime = pruefer.parse_path(config["paths"]["runtime"], "paths.runtime", home)
    output = pruefer.parse_path(config["paths"]["output"], "paths.output", home)
    codex = client_dir(codex_raw, home / ".codex")
    claude = client_dir(claude_raw, home / ".claude")
    result = {"status": PRESENT, "language": lang.code, "file_integration": CHECKED,
              "functional_check": UNCHECKED, "clients": [], "problems": []}
    for client in config["clients"]:
        result["clients"].append({"client": client, "status": PRESENT, "skills": 0,
                                  "integrity": CHECKED, "models_services": UNCHECKED})
    state_dir = profile / lang.state_dir
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
                raise StatusError("Open operation")
        except ValueError:
            result.update(status=LIMITED, file_integration=LIMITED)
            result["problems"].append("Open or unreadable package operation. No automatic retry.")
            for item in result["clients"]:
                item.update(status=LIMITED, integrity=LIMITED)
            return result
    if (state_dir / "bestand.json").exists() or (state_dir / "bestand.json").is_symlink():
        return inspect_confirmed(result, config, config_path, home, codex_raw, claude_raw)
    object_name = "runtime manifest paket.json"
    try:
        manifest = read_json(runtime / "paket.json")
        entries = manifest_entries(manifest)
        if manifest_language(manifest) != lang.code:
            raise StatusError("Package language does not match the configuration language")
        prefix = lang.skills_path.split("/")
        names = sorted({parts[2] for raw in entries for parts in [raw.split("/")]
                        if len(parts) == 4 and parts[:2] == prefix and parts[3] == "SKILL.md"})
        if not names or any(not SKILL.fullmatch(name) for name in names):
            raise StatusError("Invalid skill sources in the manifest")
        rules, links = expected_targets(runtime, config["clients"], names, home, codex, claude, lang.code)
        object_name = "ownership file installation.json"
        state = read_json(state_dir / "installation.json")
        seen = validate_state(state, config, runtime, profile, output, entries, rules, links, manifest["version"],
                              state_dir)
        expected_seen = {str(runtime / rel) for rel in entries} | {str(runtime / "paket.json")} | set(rules) | set(links)
        if state["status"] != "installed" or seen != expected_seen:
            raise StatusError("Installation not completed")
        object_name = "output folder"
        output_fd = sicher.directory(output)
        os.close(output_fd)
        object_name = "runtime manifest paket.json"
        manifest_item = next(item for item in state["created"] if item["path"] == str(runtime / "paket.json"))
        if hashlib.sha256(read_file(runtime / "paket.json")).hexdigest() != manifest_item["sha256"]:
            raise StatusError("Package manifest changed")
        for raw, digest in entries.items():
            object_name = f"package file {raw}"
            if hashlib.sha256(read_file(runtime / raw)).hexdigest() != digest:
                raise StatusError("Package file changed")
    except FileNotFoundError:
        result["status"] = MISSING
        result["file_integration"] = MISSING
        result["problems"].append(f"The {object_name} is missing. Next step: check the installation state.")
    except (StatusError, OSError, ValueError):
        result["status"] = LIMITED
        result["file_integration"] = LIMITED
        result["problems"].append(f"The {object_name} is invalid or changed. Next step: check the installation.")
    if result["status"] != PRESENT:
        for item in result["clients"]:
            item["status"] = result["status"]
            item["integrity"] = result["file_integration"]
        return result

    owned = {item["path"]: item for item in state["created"]}
    for client_item in result["clients"]:
        client = client_item["client"]
        for path, owner in rules.items():
            if owner != client:
                continue
            try:
                if hashlib.sha256(read_file(path)).hexdigest() != owned[path]["sha256"]:
                    raise StatusError("Global rule file changed")
            except FileNotFoundError:
                client_item["status"] = MISSING
                result["problems"].append(f"{client}: rule file missing. Next step: check the client integration.")
            except (StatusError, OSError, ValueError):
                if client_item["status"] == PRESENT:
                    client_item["status"] = LIMITED
                result["problems"].append(f"{client}: rule file changed. Next step: check the client integration.")
        for path, (owner, source) in links.items():
            if owner != client:
                continue
            skill_name = Path(path).name
            try:
                parent_fd, name = sicher.parent(path)
                try:
                    info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
                    if not stat.S_ISLNK(info.st_mode) or os.readlink(name, dir_fd=parent_fd) != source:
                        raise StatusError("Skill link changed")
                    sicher.assert_directory_at_path(Path(path).parent, parent_fd)
                finally:
                    os.close(parent_fd)
                client_item["skills"] += 1
            except FileNotFoundError:
                client_item["status"] = MISSING
                result["problems"].append(f"{client}: skill link {skill_name} missing. Next step: check the link.")
            except (StatusError, OSError, ValueError):
                if client_item["status"] == PRESENT:
                    client_item["status"] = LIMITED
                result["problems"].append(f"{client}: skill link {skill_name} changed. Next step: check the link.")
        client_item["integrity"] = CHECKED if client_item["status"] == PRESENT else client_item["status"]
    if any(item["status"] == MISSING for item in result["clients"]):
        result["status"] = MISSING
    elif any(item["status"] == LIMITED for item in result["clients"]):
        result["status"] = LIMITED
    if result["status"] != PRESENT:
        result["file_integration"] = result["status"]
    return result


def inspect_confirmed(result, config, config_path, home, codex, claude):
    try:
        paths = bestand.areas(config, home)
        state_dir = Path(paths["profile"]) / languages.of_config(config).state_dir
        state = bestand.decode(bestand.read_snapshot(state_dir / "bestand.json")[0])
        bestand.validate(state, config, home, codex, claude)
        if state["status"] == "uninstalled":
            for path in state["owned"]:
                bestand.check_target(path, None)
            result.update(status=UNINSTALLED, file_integration=MISSING)
            for item in result["clients"]:
                item.update(status=UNINSTALLED, integrity=MISSING)
            return result
        bestand.verify_manifest(state)
        for path, item in state["owned"].items():
            if item["role"] == "runtime_file":
                bestand.check_target(path, item)
        output_fd = sicher.directory(paths["output"])
        os.close(output_fd)
    except (OSError, ValueError, TypeError, KeyError) as error:
        status = MISSING if isinstance(error, FileNotFoundError) else LIMITED
        result.update(status=status, file_integration=status)
        result["problems"].append("Completed package inventory or runtime is invalid, changed or missing.")
        for item in result["clients"]:
            item.update(status=status, integrity=status)
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
                status = MISSING if isinstance(error, FileNotFoundError) else LIMITED
                if client["status"] != MISSING:
                    client.update(status=status, integrity=status)
                result["problems"].append(f"{client['client']}: {Path(path).name} is missing or was changed.")
    statuses = {item["status"] for item in result["clients"]}
    status = MISSING if MISSING in statuses else LIMITED if LIMITED in statuses else PRESENT
    result.update(status=status, file_integration=CHECKED if status == PRESENT else status)
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
            raise StatusError("Invalid home folder")
        home = pruefer.resolve_directory_candidate(args.home, "--home")
        if not home.is_dir() or home == Path("/"):
            raise StatusError("Invalid home folder")
        result = inspect(args.config.absolute(), home, args.codex_home, args.claude_config_dir)
    except (StatusError, pruefer.ConfigurationError, OSError):
        print("Setup status: confirmed configuration invalid or not readable", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"File integration: {result['status']}. Functional behavior, models and services unchecked.")
        for item in result["clients"]:
            print(f"{item['client']}: {item['status']}, {item['skills']} skill links, integrity {item['integrity']}, models and services unchecked")
        for problem in result["problems"]:
            print(problem)
    return 0 if result["status"] == PRESENT else 1


if __name__ == "__main__":
    sys.exit(main())
