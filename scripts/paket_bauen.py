#!/usr/bin/env python3
"""Baue ein isoliertes, unveröffentlichtes AIOS-Runtime-Testpaket."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile

from client_vorbereiten import PreparationError, destination_path, generated_core
from einrichten import exclusive_rename
from pruefe_konfiguration import ConfigurationError
from paketregeln import SCRIPT_NAMES, allowed_directory, allowed_file


PACKAGE = Path(__file__).resolve().parent.parent
VERSION = "0.1.6-dev"


class BuildError(Exception):
    pass


def identity(info):
    return (info.st_dev, info.st_ino, info.st_mtime_ns, info.st_size)


def open_directory(name, parent_fd=None):
    try:
        return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
    except OSError as error:
        raise BuildError(f"Paketquellenordner unsicher oder nicht lesbar: {name}") from error


def open_package():
    if not PACKAGE.is_absolute():
        raise BuildError("Paketquelle ist kein absoluter Pfad")
    fd = open_directory("/")
    try:
        for component in PACKAGE.parts[1:]:
            next_fd = open_directory(component, fd)
            os.close(fd)
            fd = next_fd
        return fd
    except Exception:
        os.close(fd)
        raise


def read_relative(package_fd, relative, expected):
    parent_fd = os.dup(package_fd)
    try:
        for component in relative.parts[:-1]:
            next_fd = open_directory(component, parent_fd)
            os.close(parent_fd)
            parent_fd = next_fd
        try:
            file_fd = os.open(relative.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent_fd)
        except OSError as error:
            raise BuildError(f"Paketquelldatei unsicher oder nicht lesbar: {relative}") from error
        try:
            before = os.fstat(file_fd)
            if not stat.S_ISREG(before.st_mode) or identity(before) != expected:
                raise BuildError(f"Paketquelldatei nach Inventur geändert: {relative}")
            with os.fdopen(os.dup(file_fd), "rb") as stream:
                data = stream.read()
            if identity(os.fstat(file_fd)) != expected:
                raise BuildError(f"Paketquelldatei beim Lesen geändert: {relative}")
            return data
        finally:
            os.close(file_fd)
    finally:
        os.close(parent_fd)


def source_snapshot():
    """Read only approved regular files and record identity for the confirmation check."""
    package_fd = open_package()
    try:
        inventory = {}

        def visit(directory_fd, prefix):
            for name in sorted(os.listdir(directory_fd)):
                info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
                relative = prefix / name
                mode = info.st_mode
                if stat.S_ISLNK(mode):
                    raise BuildError(f"Symlink in Paketquelle: {relative}")
                if name == "__pycache__":
                    continue
                if stat.S_ISDIR(mode):
                    allowed = allowed_directory(relative.as_posix())
                else:
                    allowed = allowed_file(relative.as_posix())
                if not allowed:
                    raise BuildError(f"Private Laufzeitdaten in Paketquelle: {relative}")
                if stat.S_ISDIR(mode):
                    child_fd = open_directory(name, directory_fd)
                    try:
                        if identity(os.fstat(child_fd)) != identity(info):
                            raise BuildError(f"Paketquellenordner nach Inventur geändert: {relative}")
                        visit(child_fd, relative)
                    finally:
                        os.close(child_fd)
                elif stat.S_ISREG(mode):
                    inventory[relative] = identity(info)
                else:
                    raise BuildError(f"Keine reguläre Paketquelle: {relative}")

        general_fd = open_directory("allgemein", package_fd)
        try:
            visit(general_fd, Path("allgemein"))
        finally:
            os.close(general_fd)
        scripts_fd = open_directory("scripts", package_fd)
        try:
            for name in SCRIPT_NAMES:
                info = os.stat(name, dir_fd=scripts_fd, follow_symlinks=False)
                if not stat.S_ISREG(info.st_mode):
                    raise BuildError(f"Skript fehlt oder ist keine reguläre Datei: scripts/{name}")
                inventory[Path("scripts") / name] = identity(info)
        finally:
            os.close(scripts_fd)
        return {relative: (read_relative(package_fd, relative, expected), expected)
                for relative, expected in sorted(inventory.items())}
    finally:
        os.close(package_fd)


def package_contents(snapshot):
    contents = {relative: data for relative, (data, _identity) in snapshot.items()}
    core = contents[Path("allgemein/regeln/kern.md")]
    generated = generated_core(core).encode("utf-8")
    contents[Path("AGENTS.md")] = generated
    contents[Path("CLAUDE.md")] = generated
    entries = [{"path": path.as_posix(), "sha256": hashlib.sha256(data).hexdigest()} for path, data in sorted(contents.items())]
    manifest = {"schema_version": 1, "version": VERSION, "files": entries}
    contents[Path("paket.json")] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return contents


def write_bytes_private(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)


def build(destination, contents):
    staged = Path(tempfile.mkdtemp(prefix=".aios-paket-", dir=destination.parent))
    os.chmod(staged, 0o700)
    try:
        for relative, data in sorted(contents.items()):
            target = staged / relative
            target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            write_bytes_private(target, data)
        destination_path(str(destination))
        exclusive_rename(staged, destination)
    finally:
        if staged.exists():
            shutil.rmtree(staged)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True, help="Neuer absoluter Ordner für das lokale Testpaket")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        destination = destination_path(args.destination)
        snapshot = source_snapshot()
        contents = package_contents(snapshot)
        print(f"Testpaket: {destination}")
        print(f"Version: {VERSION}, Dateien: {len(contents)}")
        print(f"Quelle: allgemein/ und {len(SCRIPT_NAMES)} fest ausgewählte Laufzeitskripte")
        print("Keine Installation oder Client-Einbindung.")
        if not args.apply:
            print("Vorschau. Keine Dateien angelegt.")
            return 0
        try:
            answer = input("Paket bauen? Genau 'ja' eingeben: ").strip()
        except EOFError:
            answer = ""
        if answer != "ja":
            print("Abgebrochen. Keine Dateien angelegt.")
            return 0
        if source_snapshot() != snapshot:
            raise BuildError("Quellbestand hat sich nach der Vorschau geändert")
        build(destination, contents)
        print(f"Testpaket gebaut: {destination}")
        return 0
    except (BuildError, PreparationError, ConfigurationError, OSError, UnicodeError, KeyError) as error:
        print(f"Paketbau abgebrochen: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
