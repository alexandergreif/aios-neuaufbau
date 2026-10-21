#!/usr/bin/env python3
"""Bewusster, eng begrenzter Transfer persönlicher Profilangaben."""

import argparse
import json
import os
import stat
import sys
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path


FIELDS = {
    "name_anrede": "Name und Anrede",
    "rolle": "Rolle",
    "sprache": "Sprache",
    "zeitzone": "Zeitzone",
    "arbeitszeiten": "Arbeitszeiten und freie Tage",
    "arbeitsweise": "Arbeitsweise",
    "prioritaeten": "Prioritäten",
}
EXCLUDED = ".env, Zugangsdaten, pfade.json, projekte.md, Wissen, Journal, Ergebnisse, Änderungsverlauf"
MAX_BYTES = 128 * 1024
NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)


class TransferError(Exception):
    pass


def check_path(path):
    """Reject symlinks in every existing path component."""
    path = Path(os.path.abspath(path))
    for part in (path, *path.parents):
        try:
            mode = part.lstat().st_mode
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(mode):
            raise TransferError(f"Symlink im Pfad: {part}")
    return path


def read_file(path):
    path = check_path(path)
    fd = os.open(path, os.O_RDONLY | NOFOLLOW)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_BYTES:
            raise TransferError("Quelldatei ist keine reguläre kleine Datei")
        data = os.read(fd, MAX_BYTES + 1)
        after = os.fstat(fd)
        if len(data) > MAX_BYTES or (before.st_dev, before.st_ino, before.st_mtime_ns, before.st_size) != (after.st_dev, after.st_ino, after.st_mtime_ns, after.st_size):
            raise TransferError("Quelldatei wurde während des Lesens geändert")
        return data
    finally:
        os.close(fd)


def fingerprint(path):
    path = check_path(path)
    info = path.stat(follow_symlinks=False)
    return (info.st_dev, info.st_ino, info.st_mtime_ns, info.st_size)


def unchanged(path, initial, identity):
    return fingerprint(path) == identity and read_file(path) == initial


def cells(line):
    if not line.startswith("|") or not line.endswith("|"):
        return None
    result, current, escaped = [], [], False
    for char in line[1:-1]:
        if escaped:
            current.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "|":
            result.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if escaped:
        raise TransferError("Ungültige Markdown-Escape-Sequenz")
    result.append("".join(current).strip())
    return result


def parse_profile(raw):
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise TransferError("Profil ist kein UTF-8") from exc
    section = "main"
    values = {}
    prefs = []
    for line in lines:
        if line.startswith("## "):
            section = "prefs" if line == "## Kleine Vorlieben" else "other"
            continue
        row = cells(line)
        if row is None:
            continue
        if section == "main" and len(row) == 2:
            if row[0] in ("Feld", "---"):
                continue
            if row[0] in FIELDS.values():
                key = next(key for key, label in FIELDS.items() if label == row[0])
                if key in values:
                    raise TransferError(f"Doppeltes Profilfeld: {row[0]}")
                values[key] = row[1]
        elif section == "prefs" and len(row) == 3:
            if row[0] in ("Vorliebe", "---"):
                continue
            if any(row):
                prefs.append(dict(zip(("vorliebe", "datum", "grundlage"), row)))
    if set(values) != set(FIELDS):
        raise TransferError("Profil enthält nicht genau die sieben erwarteten Felder")
    document = {"schema_version": 1, "profile": values, "vorlieben": prefs}
    validate_document(document)
    return document


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise TransferError(f"Doppelter JSON-Schlüssel: {key}")
        result[key] = value
    return result


def validate_document(doc):
    if type(doc) is not dict or set(doc) != {"schema_version", "profile", "vorlieben"}:
        raise TransferError("Unbekanntes oder fehlendes Exportfeld")
    if type(doc["schema_version"]) is not int or doc["schema_version"] != 1:
        raise TransferError("Nicht unterstützte Schemaversion")
    profile, prefs = doc["profile"], doc["vorlieben"]
    if type(profile) is not dict or set(profile) != set(FIELDS):
        raise TransferError("Profilfelder entsprechen nicht dem Schema")
    if any(not valid_value(value) for value in profile.values()):
        raise TransferError("Ungültiger Profilwert")
    if type(prefs) is not list or len(prefs) > 100:
        raise TransferError("Ungültige Vorliebenliste")
    for pref in prefs:
        if type(pref) is not dict or set(pref) != {"vorliebe", "datum", "grundlage"}:
            raise TransferError("Ungültiger Vorliebenseintrag")
        if any(not valid_value(value) for value in pref.values()):
            raise TransferError("Ungültiger Vorliebenwert")
    if len(render_export(doc)) > MAX_BYTES or len(render_profile(doc)) > MAX_BYTES:
        raise TransferError("Profil ist für den sicheren Transfer zu groß")


def valid_value(value):
    return type(value) is str and len(value) <= 4096 and value == value.strip() and all(
        unicodedata.category(char) not in ("Cc", "Cf", "Cs", "Zl", "Zp") for char in value
    )


def render_export(doc):
    return (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def parse_json(raw):
    try:
        doc = json.loads(raw.decode("utf-8"), object_pairs_hook=no_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TransferError("Ungültiges JSON") from exc
    validate_document(doc)
    return doc


def md(value):
    return value.replace("\\", "\\\\").replace("|", "\\|")


def render_profile(doc):
    lines = ["# Persönliches Profil", "", "Status: übertragen, Angaben auf diesem Mac prüfen", "Bestätigt am: offen", "", "| Feld | Bestätigter Wert |", "| --- | --- |"]
    lines += [f"| {label} | {md(doc['profile'][key])} |" for key, label in FIELDS.items()]
    lines += ["", "## Kleine Vorlieben", "", "| Vorliebe | Datum | Grundlage |", "| --- | --- | --- |"]
    lines += [f"| {md(p['vorliebe'])} | {md(p['datum'])} | {md(p['grundlage'])} |" for p in doc["vorlieben"]]
    lines += ["", "## Bestätigte Änderungen", "", "Keine Änderungen aus dem Quellprofil übertragen.", ""]
    return "\n".join(lines).encode("utf-8")


def preview(doc, target=None):
    for key, label in FIELDS.items():
        value = doc["profile"][key]
        old = target["profile"][key] if target else None
        if old is not None and old != value:
            print(f"{label}: {old} -> {value}")
        else:
            print(f"{label}: {value}")
    print(f"Kleine Vorlieben: {len(doc['vorlieben'])}")
    for pref in doc["vorlieben"]:
        print(f"  {pref['vorliebe']} ({pref['datum']}, {pref['grundlage']})")
    if target and target["vorlieben"] != doc["vorlieben"]:
        print(f"Zielvorlieben werden ersetzt: bisher {len(target['vorlieben'])}, neu {len(doc['vorlieben'])}")
        for pref in target["vorlieben"]:
            print(f"  bisher: {pref['vorliebe']} ({pref['datum']}, {pref['grundlage']})")
    print(f"Ausgeschlossen: {EXCLUDED}")


def confirm():
    try:
        return input("Schreiben bestätigen, genau 'ja' eingeben: ").strip() == "ja"
    except EOFError:
        return False


def write_new(path, data):
    path = check_path(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "wb", closefd=False) as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise
    finally:
        os.close(fd)


def export(args):
    profile_dir = check_path(args.profile_dir)
    source = profile_dir / "profil.md"
    raw = read_file(source)
    source_identity = fingerprint(source)
    doc = parse_profile(raw)
    output = check_path(args.output)
    if output.exists():
        raise TransferError("Exportziel existiert bereits")
    print(f"Export aus: {source}")
    print(f"Export nach: {output}")
    preview(doc)
    if not args.apply:
        print("Vorschau. Keine Datei geschrieben.")
        return
    if not confirm():
        print("Abgebrochen. Keine Datei geschrieben.")
        return
    if not unchanged(source, raw, source_identity):
        raise TransferError("Quellprofil hat sich nach der Vorschau geändert")
    write_new(output, render_export(doc))
    print(f"Export geschrieben: {output}")


def import_profile(args):
    source = check_path(args.input)
    raw = read_file(source)
    source_identity = fingerprint(source)
    doc = parse_json(raw)
    profile_dir = check_path(args.profile_dir)
    dest = profile_dir / "profil.md"
    old_raw = read_file(dest) if dest.exists() else None
    old_identity = fingerprint(dest) if old_raw is not None else None
    old = parse_profile(old_raw) if old_raw is not None else None
    print(f"Import aus: {source}")
    print(f"Import nach: {dest}")
    preview(doc, old)
    if old_raw is not None:
        print("Bestehendes profil.md wird nach Sicherung ersetzt.")
    if not args.apply:
        print("Vorschau. Keine Datei geschrieben.")
        return
    if not confirm():
        print("Abgebrochen. Keine Datei geschrieben.")
        return
    if not unchanged(source, raw, source_identity):
        raise TransferError("Exportdatei hat sich nach der Vorschau geändert")
    if old_raw is not None and not unchanged(dest, old_raw, old_identity):
        raise TransferError("Zielprofil hat sich nach der Vorschau geändert")
    if old_raw is None and dest.exists():
        raise TransferError("Zielprofil wurde nach der Vorschau angelegt")
    if not profile_dir.exists():
        profile_dir.mkdir(mode=0o700, parents=True)
    check_path(profile_dir)
    if old_raw is not None:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = profile_dir / f"profil.md.backup-{stamp}"
        write_new(backup, old_raw)
        fd, temp_name = tempfile.mkstemp(prefix=".profil.md.import-", dir=profile_dir)
        temp = Path(temp_name)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(render_profile(doc))
                stream.flush()
                os.fsync(stream.fileno())
            if not unchanged(dest, old_raw, old_identity):
                raise TransferError("Zielprofil hat sich während des Schreibens geändert")
            os.replace(temp, dest)
        finally:
            temp.unlink(missing_ok=True)
        print(f"Profil geschrieben. Sicherung: {backup}")
    else:
        write_new(dest, render_profile(doc))
        print("Profil geschrieben.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    exp = sub.add_parser("export", help="Profilangaben als JSON exportieren")
    exp.add_argument("--profile-dir", required=True)
    exp.add_argument("--output", required=True)
    exp.add_argument("--apply", action="store_true")
    imp = sub.add_parser("import", help="Profilangaben aus JSON importieren")
    imp.add_argument("--input", required=True)
    imp.add_argument("--profile-dir", required=True)
    imp.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        (export if args.command == "export" else import_profile)(args)
    except (TransferError, OSError) as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
