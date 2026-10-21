#!/usr/bin/env python3
"""Erzeuge einen isolierten Testarbeitsordner für Codex und Claude Code."""

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import sys
import tempfile

from einrichten import exclusive_rename, reject_symlink_components, write_private
from pruefe_konfiguration import ConfigurationError


PACKAGE = Path(__file__).resolve().parent.parent
SOURCES = (
    Path("allgemein/regeln/kern.md"),
    Path("allgemein/referenzen/externes-schreiben.md"),
    Path("allgemein/referenzen/profil-und-wissen.md"),
)


class PreparationError(Exception):
    pass


def destination_path(raw):
    path = Path(raw)
    if not path.is_absolute() or str(path).startswith("//") or path == Path("/"):
        raise PreparationError("--destination muss ein absoluter neuer Ordner sein")
    reject_symlink_components(path)
    if not path.parent.is_dir():
        raise PreparationError("Elternordner muss bereits existieren")
    if path.exists() or path.is_symlink():
        raise PreparationError("Ziel existiert bereits und bleibt unverändert")
    return path


def source_contents():
    contents = {}
    for relative in SOURCES:
        source = PACKAGE / relative
        reject_symlink_components(source)
        if not source.is_file():
            raise PreparationError(f"Quelle fehlt oder ist ein Link: {relative}")
        contents[relative] = source.read_bytes()
    return contents


def generated_core(raw):
    digest = hashlib.sha256(raw).hexdigest()
    core = raw.decode("utf-8")
    core = core.replace("../referenzen/", "allgemein/referenzen/")
    header = f"<!-- Generiert aus allgemein/regeln/kern.md. SHA256: {digest} -->\n\n"
    return header + core


def prepare(destination, contents):
    staged = Path(tempfile.mkdtemp(prefix=".aios-client-test-", dir=destination.parent))
    os.chmod(staged, 0o700)
    try:
        (staged / "allgemein").mkdir(mode=0o700)
        (staged / "allgemein/regeln").mkdir(mode=0o700)
        (staged / "allgemein/referenzen").mkdir(mode=0o700)
        for relative, data in contents.items():
            write_private(staged / relative, data.decode("utf-8"))
        core = generated_core(contents[SOURCES[0]])
        write_private(staged / "AGENTS.md", core)
        write_private(staged / "CLAUDE.md", core)
        destination_path(str(destination))
        exclusive_rename(staged, destination)
    finally:
        if staged.exists():
            shutil.rmtree(staged)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True, help="Neuer absoluter Testarbeitsordner")
    parser.add_argument("--apply", action="store_true", help="Nach Vorschau und Bestätigung anlegen")
    args = parser.parse_args(argv)
    try:
        destination = destination_path(args.destination)
        contents = source_contents()
        digest = hashlib.sha256(contents[SOURCES[0]]).hexdigest()
        print(f"Testarbeitsordner: {destination}")
        print("Dateien: allgemein/regeln/kern.md, zwei allgemein/referenzen/*.md, AGENTS.md, CLAUDE.md")
        print(f"Regelkern SHA256: {digest}")
        print("Keine globale Client-Einbindung oder Installation.")
        if not args.apply:
            print("Vorschau. Keine Dateien angelegt.")
            return 0
        try:
            answer = input("Ordner anlegen? Genau 'ja' eingeben: ").strip()
        except EOFError:
            answer = ""
        if answer != "ja":
            print("Abgebrochen. Keine Dateien angelegt.")
            return 0
        if source_contents() != contents:
            raise PreparationError("Quelldateien haben sich nach der Vorschau geändert")
        prepare(destination, contents)
        print(f"Testarbeitsordner angelegt: {destination}")
        return 0
    except (PreparationError, ConfigurationError, OSError, UnicodeError) as error:
        print(f"Vorbereitung abgebrochen: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
