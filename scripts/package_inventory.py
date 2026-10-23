"""Validated completed package inventory. Creation histories grant no authority."""

from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import uuid

import check_config as pruefer
import languages
import safe_files as sicher
from setup_profile import reject_symlink_components
from package_rules import allowed_file


class BestandError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def identity(info):
    return info.st_dev, info.st_ino, info.st_mtime_ns, info.st_size


def read_snapshot(path, limit=4 * 1024 * 1024):
    parent, name = sicher.parent(path)
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode):
                raise BestandError("Not a regular file")
            chunks = []
            size = 0
            while chunk := os.read(fd, 65536):
                size += len(chunk)
                if limit is not None and size > limit:
                    raise BestandError("Metadata file too large")
                chunks.append(chunk)
            current = os.stat(name, dir_fd=parent, follow_symlinks=False)
            if identity(before) != identity(os.fstat(fd)) or identity(before) != identity(current):
                raise BestandError("File changed during the check")
            sicher.assert_directory_at_path(Path(path).parent, parent)
            return b"".join(chunks), identity(before)
        finally:
            os.close(fd)
    finally:
        os.close(parent)


def decode(raw):
    try:
        return json.loads(raw.decode(), object_pairs_hook=pruefer.unique_object)
    except (UnicodeError, ValueError) as error:
        raise BestandError("Invalid metadata") from error


def fields(value, expected):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise BestandError("Invalid inventory schema")


def manifest_language(manifest):
    """Language of a package manifest. Manifests up to 0.1.7-dev have no field and mean de."""
    if isinstance(manifest, dict) and set(manifest) == {"schema_version", "version", "files"}:
        return languages.DEFAULT
    fields(manifest, ("schema_version", "version", "language", "files"))
    if not isinstance(manifest["language"], str) or manifest["language"] not in languages.CODES:
        raise BestandError("Invalid manifest language")
    return manifest["language"]


def manifest_entries(manifest):
    language = manifest_language(manifest)
    # Old German script names only in manifests without a language field (0.1.7-dev and older).
    legacy = "language" not in manifest
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1 or not isinstance(manifest["version"], str) or not manifest["version"]:
        raise BestandError("Invalid manifest version")
    if not isinstance(manifest["files"], list) or not manifest["files"]:
        raise BestandError("Manifest files missing")
    entries = {}
    comparable = set()
    for item in manifest["files"]:
        fields(item, ("path", "sha256"))
        raw, sha = item["path"], item["sha256"]
        if not allowed_file(raw, language, legacy_scripts=legacy) or not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
            raise BestandError("Invalid manifest path or hash")
        key = pruefer.comparable_parts(Path(raw))
        if key in comparable:
            raise BestandError("Duplicate manifest path")
        comparable.add(key)
        entries[raw] = sha
    if languages.get(language).core_path not in entries:
        raise BestandError("Core rules missing")
    return entries


def areas(config, home):
    pruefer.validate(config, home)
    result = {}
    for name in pruefer.AREA_FIELDS:
        raw = config["paths"][name]
        reject_symlink_components(home / raw[2:] if raw.startswith("~/") else Path(raw))
        result[name] = str(pruefer.parse_path(raw, name, home))
    return result


def bindings(config, home, paths, codex=None, claude=None, saved=None):
    defaults = {"codex": str(home / ".codex"), "claude-code": str(home / ".claude"),
                "codex_skills": str(home / ".agents/skills")}
    wanted = set(config["clients"]) | ({"codex_skills"} if "codex" in config["clients"] else set())
    result = {key: defaults[key] for key in sorted(wanted)} if saved is None else saved.copy()
    fields(result, wanted)
    for key, override in (("codex", codex), ("claude-code", claude)):
        if override is not None and key in wanted:
            if saved is not None and override != result[key]:
                raise BestandError("Client binding differs. No automatic migration")
            result[key] = override
    if "codex_skills" in result and result["codex_skills"] != str(home / ".agents/skills"):
        raise BestandError("Codex skill base must be inside the confirmed home folder")
    checked = []
    for key, raw in result.items():
        if not isinstance(raw, str) or not raw.startswith("/"):
            raise BestandError("Client binding must be absolute")
        reject_symlink_components(Path(raw))
        path = pruefer.parse_path(raw, "Client binding", home)
        if str(path) != raw:
            raise BestandError("Client binding is not canonical")
        if any(pruefer.overlaps(path, Path(value)) for value in paths.values()):
            raise BestandError("Client binding overlaps a protected area")
        if any(pruefer.overlaps(path, prior) for prior in checked):
            raise BestandError("Client bindings overlap")
        checked.append(path)
    return result


def targets(paths, clients, bound, manifest):
    entries = manifest_entries(manifest)
    language = manifest_language(manifest)
    lang = languages.get(language)
    runtime = Path(paths["runtime"])
    result = {str(runtime / raw): {"role": "runtime_file", "sha256": sha} for raw, sha in entries.items()}
    pattern = re.escape(lang.skills_path) + r"/([a-z0-9]+(?:-[a-z0-9]+)*)/SKILL\.md"
    names = sorted({match.group(1) for raw in entries for match in [re.fullmatch(pattern, raw)] if match})
    if not names:
        raise BestandError("Skill sources missing")
    result.update(client_targets(runtime, clients, names, bound, language))
    result[str(runtime / "paket.json")] = {"role": "runtime_file"}
    return result


def client_targets(runtime, clients, names, bound, language=languages.DEFAULT):
    """Compute only the own global rules and skill links."""
    runtime = Path(runtime)
    skills = runtime / languages.get(language).skills_path
    result = {}
    for client in clients:
        root = Path(bound[client])
        rule = root / ("AGENTS.md" if client == "codex" else "CLAUDE.md")
        result[str(rule)] = {"role": "client_rule", "client": client}
        base = Path(bound["codex_skills"]) if client == "codex" else root / "skills"
        for name in names:
            result[str(base / name)] = {"role": "client_link", "client": client,
                                      "target": str(skills / name)}
    return result


def make(config, home, bound, contents, generated):
    paths = areas(config, home)
    bound = bindings(config, home, paths, saved=bound)
    manifest = decode(contents[Path("paket.json")])
    if manifest_language(manifest) != languages.code_of_config(config):
        raise BestandError("Package language does not match the configuration language")
    owned = targets(paths, config["clients"], bound, manifest)
    for path, item in owned.items():
        if item["role"] == "client_rule":
            item["sha256"] = digest(generated)
        elif item["role"] == "runtime_file":
            item["sha256"] = digest(contents[Path(path).relative_to(paths["runtime"])])
    return {"schema_version": 2, "status": "installed", "home": str(home), "paths": paths,
            "clients": config["clients"], "bindings": bound, "manifest": manifest,
            "manifest_sha256": digest(contents[Path("paket.json")]), "owned": owned}


def validate(state, config, home, codex=None, claude=None):
    fields(state, ("schema_version", "status", "home", "paths", "clients", "bindings", "manifest", "manifest_sha256", "owned"))
    paths = areas(config, home)
    if type(state["schema_version"]) is not int or state["schema_version"] != 2 or state["status"] not in ("installed", "uninstalled"):
        raise BestandError("Unsupported completed inventory")
    if state["home"] != str(home) or state["paths"] != paths or state["clients"] != config["clients"]:
        raise BestandError("Inventory and confirmed areas contradict each other")
    if manifest_language(state["manifest"]) != languages.code_of_config(config):
        raise BestandError("Installed package language does not match the configuration language. "
                           "An update cannot change the language")
    bound = bindings(config, home, paths, codex, claude, state["bindings"])
    expected = targets(paths, config["clients"], bound, state["manifest"])
    if not isinstance(state["manifest_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", state["manifest_sha256"]):
        raise BestandError("Invalid manifest hash")
    fields(state["owned"], expected)
    for path, contract in expected.items():
        item = state["owned"][path]
        keys = set(contract) | ({"sha256"} if contract["role"] != "client_link" else set())
        fields(item, keys)
        if any(item[key] != value for key, value in contract.items()):
            raise BestandError("Ownership role, target or manifest hash contradicts the contract")
        if "sha256" in item and (not isinstance(item["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"])):
            raise BestandError("Invalid ownership hash")
    if state["owned"][str(Path(paths["runtime"]) / "paket.json")]["sha256"] != state["manifest_sha256"]:
        raise BestandError("Manifest hash contradicts ownership")
    return state


def verify_manifest(state):
    """Bind ownership to the actually installed manifest before accessing target files."""
    if state["status"] != "installed":
        raise BestandError("No installed inventory with a verifiable runtime manifest")
    path = Path(state["paths"]["runtime"]) / "paket.json"
    raw, token = read_snapshot(path)
    if digest(raw) != state["manifest_sha256"] or decode(raw) != state["manifest"]:
        raise BestandError("Inventory manifest contradicts the verified runtime manifest")
    return token


def check_target(path, item):
    path = Path(path)
    if item is None:
        reject_symlink_components(path.parent)
        if path.exists() or path.is_symlink():
            raise BestandError(f"Unknown occupied target: {path}")
        return None
    parent, name = sicher.parent(path)
    try:
        info = os.stat(name, dir_fd=parent, follow_symlinks=False)
        if item["role"] == "client_link":
            if not stat.S_ISLNK(info.st_mode) or os.readlink(name, dir_fd=parent) != item["target"]:
                raise BestandError(f"Link changed: {path}")
        else:
            if not stat.S_ISREG(info.st_mode):
                raise BestandError(f"File type changed: {path}")
            raw, opened = read_snapshot(path, None)
            if opened != identity(info) or digest(raw) != item["sha256"]:
                raise BestandError(f"Own file changed: {path}")
        sicher.assert_directory_at_path(path.parent, parent)
        return identity(info)
    finally:
        os.close(parent)


@contextmanager
def operation_lock(state_dir):
    """Cooperative lock in the confirmed technical profile area."""
    parent = sicher.directory(state_dir, create=True)
    try:
        fd = os.open("betrieb.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600, dir_fd=parent)
    except BaseException:
        os.close(parent)
        raise
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise BestandError("Operation lock is not a regular file")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise BestandError("Another AIOS operation is running") from error
        current = os.stat("betrieb.lock", dir_fd=parent, follow_symlinks=False)
        if not stat.S_ISREG(current.st_mode) or identity(current) != identity(os.fstat(fd)):
            raise BestandError("Operation lock changed")
        sicher.assert_directory_at_path(Path(state_dir), parent)
        yield
    finally:
        os.close(fd)
        os.close(parent)


def publish(path, value, previous=None):
    """Publish atomically. An unexpectedly swapped previous object is kept."""
    path = Path(path)
    parent, name = sicher.parent(path)
    temp = ".aios-bestand-" + uuid.uuid4().hex
    created = None
    exchanged = False
    try:
        data = encoded(value)
        created = sicher.exclusive_file(path.parent / temp, data)
        staged_data, staged_token = read_snapshot(path.parent / temp)
        if staged_data != data or staged_token[:2] != (created.st_dev, created.st_ino):
            raise BestandError("Prepared metadata was changed")
        sicher.assert_directory_at_path(path.parent, parent)
        if previous is None:
            sicher.exclusive_rename_at(parent, temp, name)
        else:
            if read_snapshot(path) != previous:
                raise BestandError("Completed inventory was changed")
            sicher.exchange_at(parent, temp, name)
            exchanged = True
            captured = os.stat(temp, dir_fd=parent, follow_symlinks=False)
            if identity(captured) != previous[1]:
                raise BestandError(f"Unexpected metadata object kept at {path.parent / temp}")
            if read_snapshot(path.parent / temp) != previous:
                raise BestandError(f"Changed metadata object kept at {path.parent / temp}")
        current = read_snapshot(path)
        if current[0] != data or current[1][:2] != (created.st_dev, created.st_ino):
            raise BestandError("Published metadata was replaced")
        os.fsync(parent)
        sicher.assert_directory_at_path(path.parent, parent)
        if exchanged:
            # Only the previously identified own old object under the random name.
            captured = os.stat(temp, dir_fd=parent, follow_symlinks=False)
            if identity(captured) != previous[1]:
                raise BestandError(f"Metadata remainder changed, kept at {path.parent / temp}")
            os.unlink(temp, dir_fd=parent)
            os.fsync(parent)
    finally:
        if not exchanged:
            try:
                current = os.stat(temp, dir_fd=parent, follow_symlinks=False)
                if created is not None and (current.st_dev, current.st_ino) == (created.st_dev, created.st_ino):
                    os.unlink(temp, dir_fd=parent)
            except FileNotFoundError:
                pass
        os.close(parent)
