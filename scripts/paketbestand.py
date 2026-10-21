"""Validierter abgeschlossener Paketbestand. Keine Befugnis aus Anlagehistorien."""

from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import uuid

import pruefe_konfiguration as pruefer
import sichere_dateien as sicher
from einrichten import reject_symlink_components
from paketregeln import allowed_file


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
                raise BestandError("Keine reguläre Datei")
            chunks = []
            size = 0
            while chunk := os.read(fd, 65536):
                size += len(chunk)
                if limit is not None and size > limit:
                    raise BestandError("Metadatendatei zu groß")
                chunks.append(chunk)
            current = os.stat(name, dir_fd=parent, follow_symlinks=False)
            if identity(before) != identity(os.fstat(fd)) or identity(before) != identity(current):
                raise BestandError("Datei während der Prüfung verändert")
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
        raise BestandError("Metadaten ungültig") from error


def fields(value, expected):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise BestandError("Bestandsschema ungültig")


def manifest_entries(manifest):
    fields(manifest, ("schema_version", "version", "files"))
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1 or not isinstance(manifest["version"], str) or not manifest["version"]:
        raise BestandError("Manifestversion ungültig")
    if not isinstance(manifest["files"], list) or not manifest["files"]:
        raise BestandError("Manifestdateien fehlen")
    entries = {}
    comparable = set()
    for item in manifest["files"]:
        fields(item, ("path", "sha256"))
        raw, sha = item["path"], item["sha256"]
        if not allowed_file(raw) or not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
            raise BestandError("Manifestpfad oder Hash ungültig")
        key = pruefer.comparable_parts(Path(raw))
        if key in comparable:
            raise BestandError("Doppelter Manifestpfad")
        comparable.add(key)
        entries[raw] = sha
    if "allgemein/regeln/kern.md" not in entries:
        raise BestandError("Regelkern fehlt")
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
                raise BestandError("Clientbindung abweichend. Keine automatische Migration")
            result[key] = override
    if "codex_skills" in result and result["codex_skills"] != str(home / ".agents/skills"):
        raise BestandError("Codex-Skillbasis muss im bestätigten Benutzerordner liegen")
    checked = []
    for key, raw in result.items():
        if not isinstance(raw, str) or not raw.startswith("/"):
            raise BestandError("Clientbindung muss absolut sein")
        reject_symlink_components(Path(raw))
        path = pruefer.parse_path(raw, "Clientbindung", home)
        if str(path) != raw:
            raise BestandError("Clientbindung nicht kanonisch")
        if any(pruefer.overlaps(path, Path(value)) for value in paths.values()):
            raise BestandError("Clientbindung überschneidet einen geschützten Bereich")
        if any(pruefer.overlaps(path, prior) for prior in checked):
            raise BestandError("Clientbindungen überschneiden sich")
        checked.append(path)
    return result


def targets(paths, clients, bound, manifest):
    entries = manifest_entries(manifest)
    runtime = Path(paths["runtime"])
    result = {str(runtime / raw): {"role": "runtime_file", "sha256": sha} for raw, sha in entries.items()}
    names = sorted({raw.split("/")[2] for raw in entries if re.fullmatch(r"allgemein/skills/[a-z0-9]+(?:-[a-z0-9]+)*/SKILL.md", raw)})
    if not names:
        raise BestandError("Skillquellen fehlen")
    result.update(client_targets(runtime, clients, names, bound))
    result[str(runtime / "paket.json")] = {"role": "runtime_file"}
    return result


def client_targets(runtime, clients, names, bound):
    """Berechne ausschließlich globale eigene Regeln und Skilllinks."""
    runtime = Path(runtime)
    result = {}
    for client in clients:
        root = Path(bound[client])
        rule = root / ("AGENTS.md" if client == "codex" else "CLAUDE.md")
        result[str(rule)] = {"role": "client_rule", "client": client}
        base = Path(bound["codex_skills"]) if client == "codex" else root / "skills"
        for name in names:
            result[str(base / name)] = {"role": "client_link", "client": client,
                                      "target": str(runtime / "allgemein/skills" / name)}
    return result


def make(config, home, bound, contents, generated):
    paths = areas(config, home)
    bound = bindings(config, home, paths, saved=bound)
    manifest = decode(contents[Path("paket.json")])
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
        raise BestandError("Nicht unterstützter abgeschlossener Bestand")
    if state["home"] != str(home) or state["paths"] != paths or state["clients"] != config["clients"]:
        raise BestandError("Bestand und bestätigte Bereiche widersprechen sich")
    bound = bindings(config, home, paths, codex, claude, state["bindings"])
    expected = targets(paths, config["clients"], bound, state["manifest"])
    if not isinstance(state["manifest_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", state["manifest_sha256"]):
        raise BestandError("Manifesthash ungültig")
    fields(state["owned"], expected)
    for path, contract in expected.items():
        item = state["owned"][path]
        keys = set(contract) | ({"sha256"} if contract["role"] != "client_link" else set())
        fields(item, keys)
        if any(item[key] != value for key, value in contract.items()):
            raise BestandError("Eigentumsrolle, Ziel oder Manifesthash widerspricht Vertrag")
        if "sha256" in item and (not isinstance(item["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"])):
            raise BestandError("Eigentumshash ungültig")
    if state["owned"][str(Path(paths["runtime"]) / "paket.json")]["sha256"] != state["manifest_sha256"]:
        raise BestandError("Manifesthash widerspricht Eigentum")
    return state


def verify_manifest(state):
    """Binde Eigentum vor Zieldateizugriffen an das tatsächlich installierte Manifest."""
    if state["status"] != "installed":
        raise BestandError("Kein installierter Bestand mit prüfbarem Runtime-Manifest")
    path = Path(state["paths"]["runtime"]) / "paket.json"
    raw, token = read_snapshot(path)
    if digest(raw) != state["manifest_sha256"] or decode(raw) != state["manifest"]:
        raise BestandError("Bestandsmanifest widerspricht dem verifizierten Runtime-Manifest")
    return token


def check_target(path, item):
    path = Path(path)
    if item is None:
        reject_symlink_components(path.parent)
        if path.exists() or path.is_symlink():
            raise BestandError(f"Unbekanntes belegtes Ziel: {path}")
        return None
    parent, name = sicher.parent(path)
    try:
        info = os.stat(name, dir_fd=parent, follow_symlinks=False)
        if item["role"] == "client_link":
            if not stat.S_ISLNK(info.st_mode) or os.readlink(name, dir_fd=parent) != item["target"]:
                raise BestandError(f"Verknüpfung verändert: {path}")
        else:
            if not stat.S_ISREG(info.st_mode):
                raise BestandError(f"Dateityp verändert: {path}")
            raw, opened = read_snapshot(path, None)
            if opened != identity(info) or digest(raw) != item["sha256"]:
                raise BestandError(f"Eigene Datei verändert: {path}")
        sicher.assert_directory_at_path(path.parent, parent)
        return identity(info)
    finally:
        os.close(parent)


@contextmanager
def operation_lock(state_dir):
    """Kooperative Sperre im bestätigten technischen Profilbereich."""
    parent = sicher.directory(state_dir, create=True)
    try:
        fd = os.open("betrieb.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600, dir_fd=parent)
    except BaseException:
        os.close(parent)
        raise
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise BestandError("Betriebssperre ist keine reguläre Datei")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise BestandError("Anderer AIOS-Betriebsbefehl läuft") from error
        current = os.stat("betrieb.lock", dir_fd=parent, follow_symlinks=False)
        if not stat.S_ISREG(current.st_mode) or identity(current) != identity(os.fstat(fd)):
            raise BestandError("Betriebssperre verändert")
        sicher.assert_directory_at_path(Path(state_dir), parent)
        yield
    finally:
        os.close(fd)
        os.close(parent)


def publish(path, value, previous=None):
    """Veröffentliche atomar. Ein unerwartet ausgetauschtes Altobjekt bleibt erhalten."""
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
            raise BestandError("Vorbereitete Metadaten wurden verändert")
        sicher.assert_directory_at_path(path.parent, parent)
        if previous is None:
            sicher.exclusive_rename_at(parent, temp, name)
        else:
            if read_snapshot(path) != previous:
                raise BestandError("Abgeschlossener Bestand wurde verändert")
            sicher.exchange_at(parent, temp, name)
            exchanged = True
            captured = os.stat(temp, dir_fd=parent, follow_symlinks=False)
            if identity(captured) != previous[1]:
                raise BestandError(f"Unerwartetes Metadatenobjekt erhalten unter {path.parent / temp}")
            if read_snapshot(path.parent / temp) != previous:
                raise BestandError(f"Verändertes Metadatenobjekt erhalten unter {path.parent / temp}")
        current = read_snapshot(path)
        if current[0] != data or current[1][:2] != (created.st_dev, created.st_ino):
            raise BestandError("Veröffentlichte Metadaten wurden ersetzt")
        os.fsync(parent)
        sicher.assert_directory_at_path(path.parent, parent)
        if exchanged:
            # Ausschließlich das zuvor identifizierte eigene Altobjekt im zufälligen Namen.
            captured = os.stat(temp, dir_fd=parent, follow_symlinks=False)
            if identity(captured) != previous[1]:
                raise BestandError(f"Metadatenrest verändert, erhalten unter {path.parent / temp}")
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
