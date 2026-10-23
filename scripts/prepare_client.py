#!/usr/bin/env python3
"""Create an isolated test workspace for Codex and Claude Code."""

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import sys
import tempfile

import languages
from setup_profile import exclusive_rename, reject_symlink_components, write_private
from check_config import ConfigurationError


PACKAGE = Path(__file__).resolve().parent.parent


class PreparationError(Exception):
    pass


def sources(language=languages.DEFAULT):
    """Source files relative to the language folder: core rules and two references."""
    lang = languages.get(language)
    return (lang.core, *(f"{lang.references}/{name}" for name in lang.client_test_references))


def destination_path(raw):
    path = Path(raw)
    if not path.is_absolute() or str(path).startswith("//") or path == Path("/"):
        raise PreparationError("--destination must be a new absolute folder")
    reject_symlink_components(path)
    if not path.parent.is_dir():
        raise PreparationError("The parent folder must already exist")
    if path.exists() or path.is_symlink():
        raise PreparationError("Target already exists and stays unchanged")
    return path


def source_contents(language=languages.DEFAULT):
    """Read the sources and key them by their runtime path."""
    lang = languages.get(language)
    contents = {}
    for relative in sources(language):
        source = PACKAGE / lang.source / relative
        reject_symlink_components(source)
        if not source.is_file():
            raise PreparationError(f"Source missing or a link: {lang.source}/{relative}")
        contents[Path(lang.root) / relative] = source.read_bytes()
    return contents


def generated_core(raw, language=languages.DEFAULT):
    lang = languages.get(language)
    digest = hashlib.sha256(raw).hexdigest()
    core = raw.decode("utf-8")
    core = core.replace(lang.core_link_prefix, lang.references_path + "/")
    return lang.generated_header(digest) + core


def prepare(destination, contents, language=languages.DEFAULT):
    lang = languages.get(language)
    staged = Path(tempfile.mkdtemp(prefix=".aios-client-test-", dir=destination.parent))
    os.chmod(staged, 0o700)
    try:
        for relative in sorted(contents):
            current = staged
            for part in Path(relative).parts[:-1]:
                current = current / part
                if not current.is_dir():
                    current.mkdir(mode=0o700)
            write_private(staged / relative, contents[relative].decode("utf-8"))
        core = generated_core(contents[Path(lang.core_path)], language)
        write_private(staged / "AGENTS.md", core)
        write_private(staged / "CLAUDE.md", core)
        destination_path(str(destination))
        exclusive_rename(staged, destination)
    finally:
        if staged.exists():
            shutil.rmtree(staged)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True, help="New absolute test workspace")
    parser.add_argument("--language", choices=languages.CODES, default=languages.DEFAULT,
                        help="Language of the rules (default de)")
    parser.add_argument("--apply", action="store_true", help="Create after preview and confirmation")
    args = parser.parse_args(argv)
    lang = languages.get(args.language)
    try:
        destination = destination_path(args.destination)
        contents = source_contents(lang.code)
        digest = hashlib.sha256(contents[Path(lang.core_path)]).hexdigest()
        print(f"Test workspace: {destination}")
        print(f"Files: {lang.core_path}, two {lang.references_path}/*.md, AGENTS.md, CLAUDE.md")
        print(f"Core rules SHA256: {digest}")
        print("No global client integration or installation.")
        if not args.apply:
            print("Preview. No files created.")
            return 0
        try:
            answer = input("Create the folder? Type exactly 'yes': ").strip()
        except EOFError:
            answer = ""
        if answer != "yes":
            print("Cancelled. No files created.")
            return 0
        if source_contents(lang.code) != contents:
            raise PreparationError("Source files changed after the preview")
        prepare(destination, contents, lang.code)
        print(f"Test workspace created: {destination}")
        return 0
    except (PreparationError, ConfigurationError, OSError, UnicodeError) as error:
        print(f"Preparation stopped: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
