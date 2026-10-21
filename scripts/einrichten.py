#!/usr/bin/env python3
"""Geführte lokale Ersteinrichtung eines privaten AIOS-Profils."""

import argparse
import ctypes
from datetime import date
import errno
import getpass
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

import pruefe_konfiguration as pruefer
import profil_transfer as profil


PACKAGE = Path(__file__).resolve().parent.parent
FIELDS = tuple((label, label) for label in profil.FIELDS.values())


def ask(label, default=None):
    suffix = f" [{default}]" if default is not None else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or (default if default is not None else "")


def ask_path(label, default=None):
    return ask(label, default)


def ask_roots(label):
    values = []
    print(f"{label}: Pfade einzeln eingeben, leere Eingabe beendet die Liste.")
    while True:
        value = ask("Pfad")
        if not value:
            return values
        values.append(value)


def validate_home(value):
    if not value.is_absolute() or str(value).startswith("//"):
        raise pruefer.ConfigurationError("--home muss ein absoluter Pfad sein.")
    home = pruefer.resolve_directory_candidate(value, "--home")
    if not home.is_dir() or home == Path("/"):
        raise pruefer.ConfigurationError("--home muss ein vorhandener Benutzerordner sein.")
    return home


def reject_symlink_components(path):
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        try:
            if current.is_symlink():
                raise pruefer.ConfigurationError("Profilziel enthält einen symbolischen Link.")
            current.lstat()
        except FileNotFoundError:
            return
        except OSError:
            raise pruefer.ConfigurationError("Profilziel lässt sich nicht sicher prüfen.") from None


def check_destination(raw, home):
    path = pruefer.parse_path(raw, "paths.profile", home)
    reject_symlink_components(Path(home / raw[2:] if raw.startswith("~/") else raw))
    if not path.parent.is_dir():
        raise pruefer.ConfigurationError("Der Elternordner des Profils muss bereits existieren.")
    if path.exists() or path.is_symlink():
        raise pruefer.ConfigurationError("Profilziel existiert bereits. Bestehende Daten bleiben unverändert.")
    return path


def profile_text(values):
    profil.validate_document({"schema_version": 1,
                              "profile": {key: values.get(label, "") or "offen"
                                          for key, label in profil.FIELDS.items()},
                              "vorlieben": []})
    template = (PACKAGE / "allgemein/vorlagen/profil.md").read_text(encoding="utf-8")
    template = template.replace("Status: noch nicht eingerichtet", "Status: eingerichtet")
    template = template.replace("Bestätigt am: offen", f"Bestätigt am: {date.today().isoformat()}")
    for label, value in values.items():
        safe = profil.md(value)
        template = template.replace(f"| {label} | offen |", f"| {label} | {safe or 'offen'} |")
    return template


def exclusive_rename(source, destination):
    """Veröffentlicht den vorbereiteten Ordner nur, wenn das Ziel noch fehlt."""
    libc = ctypes.CDLL(None, use_errno=True)
    source_bytes = os.fsencode(source)
    destination_bytes = os.fsencode(destination)
    if sys.platform == "darwin" and hasattr(libc, "renamex_np"):
        operation = libc.renamex_np
        operation.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        result = operation(source_bytes, destination_bytes, 0x00000004)  # RENAME_EXCL
    elif sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        operation = libc.renameat2
        operation.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        result = operation(-100, source_bytes, -100, destination_bytes, 1)  # RENAME_NOREPLACE
    else:
        raise OSError(errno.ENOTSUP, "Atomare Übernahme ohne Überschreiben nicht verfügbar")
    if result != 0:
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code))


def write_private(path, content):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        stream.write(content)


def save_profile(destination, config, values, key):
    staged = Path(tempfile.mkdtemp(prefix=".aios-einrichtung-", dir=destination.parent))
    os.chmod(staged, 0o700)
    try:
        write_private(staged / "pfade.json", json.dumps(config, ensure_ascii=False, indent=2) + "\n")
        write_private(staged / "profil.md", profile_text(values))
        for name in ("projekte.md",):
            write_private(staged / name, (PACKAGE / "allgemein/vorlagen" / name).read_text(encoding="utf-8"))
        (staged / "wissen").mkdir(mode=0o700)
        write_private(staged / "wissen/INDEX.md", (PACKAGE / "allgemein/vorlagen/wissen/INDEX.md").read_text(encoding="utf-8"))
        if key:
            if any(character in key for character in "\r\n\x00"):
                raise pruefer.ConfigurationError("Blockbrain-Schlüssel enthält unzulässige Zeichen.")
            env = "BLOCKBRAIN_API_KEY=" + json.dumps(key, ensure_ascii=False) + "\n"
        else:
            env = "# Optional: Blockbrain-Schlüssel später ergänzen. Nicht weitergeben.\nBLOCKBRAIN_API_KEY=\n"
        write_private(staged / ".env", env)
        exclusive_rename(staged, destination)
    finally:
        if staged.exists():
            shutil.rmtree(staged)


def interactive(home):
    home = validate_home(Path(home))
    print("AIOS: lokale Ersteinrichtung")
    choice = ask("Client (claude, codex, beide)", "beide").lower()
    clients = {"claude": ["claude-code"], "codex": ["codex"], "beide": ["claude-code", "codex"]}.get(choice)
    if clients is None:
        raise pruefer.ConfigurationError("Clientauswahl ist ungültig.")
    paths = {
        "source": ask_path("Quellcode", str(PACKAGE)),
        "runtime": ask_path("Runtime", "~/aios-runtime"),
        "profile": ask_path("Profil", "~/aios-profile"),
        "output": ask_path("Ausgabe", "~/aios-output"),
        "coding_roots": ask_roots("Coding-Wurzeln (optional)"),
        "customer_roots": ask_roots("Kunden-Wurzeln (optional)"),
    }
    values = {name: ask(label) for name, label in FIELDS}
    profile_text(values)  # Gemeinsamen Datenvertrag vor Vorschau und Schreiben prüfen.
    config = {"schema_version": 1, "confirmed": False, "clients": clients, "paths": paths}
    pruefer.validate({**config, "confirmed": True}, home)
    destination = check_destination(paths["profile"], home)
    print("\nVorschau der lokalen Konfiguration:")
    print(json.dumps(config, ensure_ascii=False, indent=2))
    print("\nProfilangaben:")
    for name, value in values.items():
        print(f"{name}: {value or 'offen'}")
    print("Es entstehen pfade.json, profil.md, projekte.md, wissen/INDEX.md und .env im Profilordner.")
    if ask("Diese Einrichtung speichern? (ja/nein)", "nein").lower() != "ja":
        print("Abgebrochen. Keine Dateien angelegt.")
        return None
    if ask("Blockbrain-Schlüssel eingeben? (ja/nein)", "nein").lower() == "ja":
        key = getpass.getpass("Blockbrain-Schlüssel (leer zum Überspringen): ")
    else:
        key = ""
    check_destination(paths["profile"], home)
    config["confirmed"] = True
    save_profile(destination, config, values, key)
    print(f"Profil eingerichtet: {destination}")
    return destination / "pfade.json"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home(), help="Benutzerordner für ~/ (auch für synthetische Tests)")
    args = parser.parse_args(argv)
    try:
        interactive(args.home)
    except (pruefer.ConfigurationError, profil.TransferError, OSError, EOFError, KeyboardInterrupt, UnicodeError) as error:
        if isinstance(error, (pruefer.ConfigurationError, profil.TransferError)):
            print(f"Einrichtung abgebrochen: {error}", file=sys.stderr)
        else:
            print("Einrichtung abgebrochen. Keine bestehenden Profildaten wurden geändert.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
