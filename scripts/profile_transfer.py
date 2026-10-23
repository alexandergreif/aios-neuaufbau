#!/usr/bin/env python3
"""Deliberate, narrowly limited transfer of personal profile details."""

import argparse
import json
import os
import stat
import sys
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path

import languages


# Internal JSON keys stay identical in every language. Labels come from the language table.
FIELDS = languages.get(languages.DEFAULT).labels
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
            raise TransferError(f"Symlink in path: {part}")
    return path


def read_file(path):
    path = check_path(path)
    fd = os.open(path, os.O_RDONLY | NOFOLLOW)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_BYTES:
            raise TransferError("Source file is not a small regular file")
        data = os.read(fd, MAX_BYTES + 1)
        after = os.fstat(fd)
        if len(data) > MAX_BYTES or (before.st_dev, before.st_ino, before.st_mtime_ns, before.st_size) != (after.st_dev, after.st_ino, after.st_mtime_ns, after.st_size):
            raise TransferError("Source file changed while reading")
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
        raise TransferError("Invalid Markdown escape sequence")
    result.append("".join(current).strip())
    return result


def excluded(language=languages.DEFAULT):
    lang = languages.get(language)
    return (f".env, credentials, {lang.config_name}, {lang.register_name}, knowledge, journal, "
            "outputs, change history")


def parse_profile(raw, language=languages.DEFAULT):
    lang = languages.get(language)
    labels = lang.labels
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise TransferError("Profile is not UTF-8") from exc
    section = "main"
    values = {}
    prefs = []
    for line in lines:
        if line.startswith("## "):
            section = "prefs" if line == lang.preferences_heading else "other"
            continue
        row = cells(line)
        if row is None:
            continue
        if section == "main" and len(row) == 2:
            if row[0] in (lang.field_header[0], "---"):
                continue
            if row[0] in labels.values():
                key = next(key for key, label in labels.items() if label == row[0])
                if key in values:
                    raise TransferError(f"Duplicate profile field: {row[0]}")
                values[key] = row[1]
        elif section == "prefs" and len(row) == 3:
            if row[0] in (lang.preferences_header[0], "---"):
                continue
            if any(row):
                prefs.append(dict(zip(("vorliebe", "datum", "grundlage"), row)))
    if set(values) != set(FIELDS):
        raise TransferError("Profile does not contain exactly the seven expected fields")
    document = {"schema_version": 1, "profile": values, "vorlieben": prefs}
    validate_document(document)
    return document


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise TransferError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def validate_document(doc):
    if type(doc) is not dict or set(doc) != {"schema_version", "profile", "vorlieben"}:
        raise TransferError("Unknown or missing export field")
    if type(doc["schema_version"]) is not int or doc["schema_version"] != 1:
        raise TransferError("Unsupported schema version")
    profile, prefs = doc["profile"], doc["vorlieben"]
    if type(profile) is not dict or set(profile) != set(FIELDS):
        raise TransferError("Profile fields do not match the schema")
    if any(not valid_value(value) for value in profile.values()):
        raise TransferError("Invalid profile value")
    if type(prefs) is not list or len(prefs) > 100:
        raise TransferError("Invalid preference list")
    for pref in prefs:
        if type(pref) is not dict or set(pref) != {"vorliebe", "datum", "grundlage"}:
            raise TransferError("Invalid preference entry")
        if any(not valid_value(value) for value in pref.values()):
            raise TransferError("Invalid preference value")
    if len(render_export(doc)) > MAX_BYTES or any(len(render_profile(doc, code)) > MAX_BYTES
                                                   for code in languages.CODES):
        raise TransferError("Profile is too large for a safe transfer")


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
        raise TransferError("Invalid JSON") from exc
    validate_document(doc)
    return doc


def md(value):
    return value.replace("\\", "\\\\").replace("|", "\\|")


def render_profile(doc, language=languages.DEFAULT):
    lang = languages.get(language)
    field, value = lang.field_header
    lines = [lang.profile_title, "", lang.transfer_status, f"{lang.confirmed_label}: {lang.open}", "",
             f"| {field} | {value} |", "| --- | --- |"]
    lines += [f"| {label} | {md(doc['profile'][key])} |" for key, label in lang.labels.items()]
    lines += ["", lang.preferences_heading, "", "| " + " | ".join(lang.preferences_header) + " |",
              "| --- | --- | --- |"]
    lines += [f"| {md(p['vorliebe'])} | {md(p['datum'])} | {md(p['grundlage'])} |" for p in doc["vorlieben"]]
    lines += ["", lang.changes_heading, "", lang.transfer_no_changes, ""]
    return "\n".join(lines).encode("utf-8")


def preview(doc, target=None, language=languages.DEFAULT):
    for key, label in languages.get("en").labels.items():
        value = doc["profile"][key]
        old = target["profile"][key] if target else None
        if old is not None and old != value:
            print(f"{label}: {old} -> {value}")
        else:
            print(f"{label}: {value}")
    print(f"Small preferences: {len(doc['vorlieben'])}")
    for pref in doc["vorlieben"]:
        print(f"  {pref['vorliebe']} ({pref['datum']}, {pref['grundlage']})")
    if target and target["vorlieben"] != doc["vorlieben"]:
        print(f"Target preferences are replaced: before {len(target['vorlieben'])}, new {len(doc['vorlieben'])}")
        for pref in target["vorlieben"]:
            print(f"  before: {pref['vorliebe']} ({pref['datum']}, {pref['grundlage']})")
    print(f"Excluded: {excluded(language)}")


def confirm():
    try:
        return input("Confirm writing, type exactly 'yes': ").strip() == "yes"
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


def present(path):
    try:
        path.lstat()
        return True
    except FileNotFoundError:
        return False


def profile_language(profile_dir, explicit=None):
    """Language of a profile folder from file names only. Contents are never read for this."""
    if explicit is not None:
        return languages.get(explicit).code
    for attribute in ("profile_name", "config_name"):
        found = [code for code in languages.CODES
                 if present(profile_dir / getattr(languages.get(code), attribute))]
        if len(found) > 1:
            raise TransferError("Profile folder contains files of both languages. Use --language")
        if found:
            return found[0]
    raise TransferError("Profile folder has no profile or configuration file to show its language. "
                        "Use --language de or --language en")


def export(args):
    profile_dir = check_path(args.profile_dir)
    language = profile_language(profile_dir, getattr(args, "language", None))
    source = profile_dir / languages.get(language).profile_name
    raw = read_file(source)
    source_identity = fingerprint(source)
    doc = parse_profile(raw, language)
    output = check_path(args.output)
    if output.exists():
        raise TransferError("Export target already exists")
    print(f"Export from: {source}")
    print(f"Export to: {output}")
    preview(doc, language=language)
    if not args.apply:
        print("Preview. No file written.")
        return
    if not confirm():
        print("Cancelled. No file written.")
        return
    if not unchanged(source, raw, source_identity):
        raise TransferError("Source profile changed after the preview")
    write_new(output, render_export(doc))
    print(f"Export written: {output}")


def import_profile(args):
    source = check_path(args.input)
    raw = read_file(source)
    source_identity = fingerprint(source)
    doc = parse_json(raw)
    profile_dir = check_path(args.profile_dir)
    language = profile_language(profile_dir, getattr(args, "language", None))
    name = languages.get(language).profile_name
    dest = profile_dir / name
    old_raw = read_file(dest) if dest.exists() else None
    old_identity = fingerprint(dest) if old_raw is not None else None
    old = parse_profile(old_raw, language) if old_raw is not None else None
    print(f"Import from: {source}")
    print(f"Import to: {dest}")
    preview(doc, old, language)
    if old_raw is not None:
        print(f"The existing {name} is replaced after a backup.")
    if not args.apply:
        print("Preview. No file written.")
        return
    if not confirm():
        print("Cancelled. No file written.")
        return
    if not unchanged(source, raw, source_identity):
        raise TransferError("Export file changed after the preview")
    if old_raw is not None and not unchanged(dest, old_raw, old_identity):
        raise TransferError("Target profile changed after the preview")
    if old_raw is None and dest.exists():
        raise TransferError("Target profile was created after the preview")
    if not profile_dir.exists():
        profile_dir.mkdir(mode=0o700, parents=True)
    check_path(profile_dir)
    if old_raw is not None:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = profile_dir / f"{name}.backup-{stamp}"
        write_new(backup, old_raw)
        fd, temp_name = tempfile.mkstemp(prefix=f".{name}.import-", dir=profile_dir)
        temp = Path(temp_name)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(render_profile(doc, language))
                stream.flush()
                os.fsync(stream.fileno())
            if not unchanged(dest, old_raw, old_identity):
                raise TransferError("Target profile changed while writing")
            os.replace(temp, dest)
        finally:
            temp.unlink(missing_ok=True)
        print(f"Profile written. Backup: {backup}")
    else:
        write_new(dest, render_profile(doc, language))
        print("Profile written.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    language_help = ("Language of the profile folder (de or en). Without it the language follows the "
                     "file names in the profile folder. Required for an empty or new folder.")
    exp = sub.add_parser("export", help="Export profile details as JSON")
    exp.add_argument("--profile-dir", required=True)
    exp.add_argument("--output", required=True)
    exp.add_argument("--language", choices=languages.CODES, help=language_help)
    exp.add_argument("--apply", action="store_true")
    imp = sub.add_parser("import", help="Import profile details from JSON")
    imp.add_argument("--input", required=True)
    imp.add_argument("--profile-dir", required=True)
    imp.add_argument("--language", choices=languages.CODES, help=language_help)
    imp.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        (export if args.command == "export" else import_profile)(args)
    except (TransferError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
