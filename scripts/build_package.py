#!/usr/bin/env python3
"""Build an isolated, unpublished AIOS runtime test package."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile

import languages
from prepare_client import PreparationError, destination_path, generated_core
from setup_profile import exclusive_rename
from check_config import ConfigurationError
from package_rules import SCRIPT_NAMES, allowed_directory, allowed_file


PACKAGE = Path(__file__).resolve().parent.parent
VERSION = "0.2.0-dev"


class BuildError(Exception):
    pass


def identity(info):
    return (info.st_dev, info.st_ino, info.st_mtime_ns, info.st_size)


def open_directory(name, parent_fd=None):
    try:
        return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
    except OSError as error:
        raise BuildError(f"Package source folder unsafe or not readable: {name}") from error


def open_package():
    if not PACKAGE.is_absolute():
        raise BuildError("Package source is not an absolute path")
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
            raise BuildError(f"Package source file unsafe or not readable: {relative}") from error
        try:
            before = os.fstat(file_fd)
            if not stat.S_ISREG(before.st_mode) or identity(before) != expected:
                raise BuildError(f"Package source file changed after inventory: {relative}")
            with os.fdopen(os.dup(file_fd), "rb") as stream:
                data = stream.read()
            if identity(os.fstat(file_fd)) != expected:
                raise BuildError(f"Package source file changed while reading: {relative}")
            return data
        finally:
            os.close(file_fd)
    finally:
        os.close(parent_fd)


def source_snapshot(language=languages.DEFAULT):
    """Read only approved regular files and record identity for the confirmation check.

    Files of the language source folder are keyed by their runtime path below
    the runtime root of that language, as defined in the language table.
    """
    lang = languages.get(language)
    package_fd = open_package()
    try:
        inventory = {}

        def visit(directory_fd, source_prefix, runtime_prefix):
            for name in sorted(os.listdir(directory_fd)):
                info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
                source = source_prefix / name
                relative = runtime_prefix / name
                mode = info.st_mode
                if stat.S_ISLNK(mode):
                    raise BuildError(f"Symlink in package source: {source}")
                if name == "__pycache__":
                    continue
                if stat.S_ISDIR(mode):
                    allowed = allowed_directory(relative.as_posix(), lang.code)
                else:
                    allowed = allowed_file(relative.as_posix(), lang.code)
                if not allowed:
                    raise BuildError(f"Private runtime data in package source: {source}")
                if stat.S_ISDIR(mode):
                    child_fd = open_directory(name, directory_fd)
                    try:
                        if identity(os.fstat(child_fd)) != identity(info):
                            raise BuildError(f"Package source folder changed after inventory: {source}")
                        visit(child_fd, source, relative)
                    finally:
                        os.close(child_fd)
                elif stat.S_ISREG(mode):
                    inventory[relative] = (source, identity(info))
                else:
                    raise BuildError(f"Not a regular package source: {source}")

        language_fd = open_directory(lang.source, package_fd)
        try:
            visit(language_fd, Path(lang.source), Path(lang.root))
        finally:
            os.close(language_fd)
        scripts_fd = open_directory("scripts", package_fd)
        try:
            for name in SCRIPT_NAMES:
                info = os.stat(name, dir_fd=scripts_fd, follow_symlinks=False)
                if not stat.S_ISREG(info.st_mode):
                    raise BuildError(f"Script missing or not a regular file: scripts/{name}")
                inventory[Path("scripts") / name] = (Path("scripts") / name, identity(info))
        finally:
            os.close(scripts_fd)
        return {relative: (read_relative(package_fd, source, expected), expected)
                for relative, (source, expected) in sorted(inventory.items())}
    finally:
        os.close(package_fd)


def package_contents(snapshot, language=languages.DEFAULT):
    lang = languages.get(language)
    contents = {relative: data for relative, (data, _identity) in snapshot.items()}
    core = contents[Path(lang.core_path)]
    generated = generated_core(core, lang.code).encode("utf-8")
    contents[Path("AGENTS.md")] = generated
    contents[Path("CLAUDE.md")] = generated
    entries = [{"path": path.as_posix(), "sha256": hashlib.sha256(data).hexdigest()} for path, data in sorted(contents.items())]
    manifest = {"schema_version": 1, "version": VERSION, "language": lang.code, "files": entries}
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
    parser.add_argument("--destination", required=True, help="New absolute folder for the local test package")
    parser.add_argument("--language", choices=languages.CODES, default=languages.DEFAULT,
                        help="Language of rules and skills (default de)")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    lang = languages.get(args.language)
    try:
        destination = destination_path(args.destination)
        snapshot = source_snapshot(lang.code)
        contents = package_contents(snapshot, lang.code)
        print(f"Test package: {destination}")
        print(f"Version: {VERSION}, language: {lang.code}, files: {len(contents)}")
        print(f"Source: {lang.source}/ as {lang.root}/ and {len(SCRIPT_NAMES)} selected runtime scripts")
        print("No installation or client integration.")
        if not args.apply:
            print("Preview. No files created.")
            return 0
        try:
            answer = input("Build the package? Type exactly 'yes': ").strip()
        except EOFError:
            answer = ""
        if answer != "yes":
            print("Cancelled. No files created.")
            return 0
        if source_snapshot(lang.code) != snapshot:
            raise BuildError("Source files changed after the preview")
        build(destination, contents)
        print(f"Test package built: {destination}")
        return 0
    except (BuildError, PreparationError, ConfigurationError, OSError, UnicodeError, KeyError) as error:
        print(f"Package build stopped: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
