#!/usr/bin/env python3
"""Guided local first-time setup of a private AIOS profile."""

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

import check_config as pruefer
import languages
import profile_transfer as profil


PACKAGE = Path(__file__).resolve().parent.parent
# Prompts always use English labels. Files use the labels of the chosen language.
FIELDS = tuple(languages.get("en").labels.items())


def ask(label, default=None):
    suffix = f" [{default}]" if default is not None else ""
    value = input(f"{label}{suffix}: ").strip()
    return value or (default if default is not None else "")


def ask_path(label, default=None):
    return ask(label, default)


def ask_roots(label):
    values = []
    print(f"{label}: enter paths one by one, an empty entry ends the list.")
    while True:
        value = ask("Path")
        if not value:
            return values
        values.append(value)


def choose_language(raw):
    value = (raw or "").strip().lower()
    if value not in languages.CODES:
        raise pruefer.ConfigurationError("Language must be de or en.")
    return value


def validate_home(value):
    if not value.is_absolute() or str(value).startswith("//"):
        raise pruefer.ConfigurationError("--home must be an absolute path.")
    home = pruefer.resolve_directory_candidate(value, "--home")
    if not home.is_dir() or home == Path("/"):
        raise pruefer.ConfigurationError("--home must be an existing home folder.")
    return home


def reject_symlink_components(path):
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        try:
            if current.is_symlink():
                raise pruefer.ConfigurationError("Profile target contains a symbolic link.")
            current.lstat()
        except FileNotFoundError:
            return
        except OSError:
            raise pruefer.ConfigurationError("Profile target cannot be checked safely.") from None


def check_destination(raw, home):
    path = pruefer.parse_path(raw, "paths.profile", home)
    reject_symlink_components(Path(home / raw[2:] if raw.startswith("~/") else raw))
    if not path.parent.is_dir():
        raise pruefer.ConfigurationError("The parent folder of the profile must already exist.")
    if path.exists() or path.is_symlink():
        raise pruefer.ConfigurationError("Profile target already exists. Existing data stays unchanged.")
    return path


def template(language, relative):
    path = languages.package_file(PACKAGE, language, relative)
    reject_symlink_components(path)
    return path.read_text(encoding="utf-8")


def profile_text(values, language=languages.DEFAULT):
    """Render the profile template. values maps internal profile keys to answers."""
    lang = languages.get(language)
    unknown = set(values) - set(lang.labels)
    if unknown:
        raise profil.TransferError("Unknown profile field")
    profil.validate_document({"schema_version": 1,
                              "profile": {key: values.get(key, "") or lang.open for key in lang.labels},
                              "vorlieben": []})
    text = template(language, lang.profile_template)
    text = text.replace(lang.profile_status_template, lang.profile_status_done)
    text = text.replace(f"{lang.confirmed_label}: {lang.open}",
                        f"{lang.confirmed_label}: {date.today().isoformat()}")
    for key, value in values.items():
        label = lang.labels[key]
        safe = profil.md(value)
        text = text.replace(f"| {label} | {lang.open} |", f"| {label} | {safe or lang.open} |")
    return text


def exclusive_rename(source, destination):
    """Publish the prepared folder only if the target is still missing."""
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
        raise OSError(errno.ENOTSUP, "Atomic publication without overwriting is not available")
    if result != 0:
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code))


def write_private(path, content):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        stream.write(content)


def save_profile(destination, config, values, key, language=languages.DEFAULT):
    lang = languages.get(language)
    staged = Path(tempfile.mkdtemp(prefix=".aios-einrichtung-", dir=destination.parent))
    os.chmod(staged, 0o700)
    try:
        write_private(staged / lang.config_name, json.dumps(config, ensure_ascii=False, indent=2) + "\n")
        write_private(staged / lang.profile_name, profile_text(values, language))
        write_private(staged / lang.register_name, template(language, lang.register_template))
        (staged / lang.knowledge_dir).mkdir(mode=0o700)
        write_private(staged / lang.knowledge_dir / "INDEX.md", template(language, lang.knowledge_index_template))
        if key:
            if any(character in key for character in "\r\n\x00"):
                raise pruefer.ConfigurationError("Blockbrain key contains invalid characters.")
            env = "BLOCKBRAIN_API_KEY=" + json.dumps(key, ensure_ascii=False) + "\n"
        else:
            env = "# Optional: add the Blockbrain key later. Do not share it.\nBLOCKBRAIN_API_KEY=\n"
        write_private(staged / ".env", env)
        exclusive_rename(staged, destination)
    finally:
        if staged.exists():
            shutil.rmtree(staged)


def interactive(home, language=None):
    home = validate_home(Path(home))
    print("AIOS: local first-time setup")
    if language is None:
        language = ask("Language for rules and skills (de, en)", "en")
    language = choose_language(language)
    lang = languages.get(language)
    choice = ask("Clients (claude, codex, both)", "both").lower()
    clients = {"claude": ["claude-code"], "codex": ["codex"], "both": ["claude-code", "codex"]}.get(choice)
    if clients is None:
        raise pruefer.ConfigurationError("Invalid client selection.")
    paths = {
        "source": ask_path("Source code", str(PACKAGE)),
        "runtime": ask_path("Runtime", "~/aios-runtime"),
        "profile": ask_path("Profile", "~/aios-profile"),
        "output": ask_path("Output", "~/aios-output"),
        "coding_roots": ask_roots("Coding roots (optional)"),
        "customer_roots": ask_roots("Customer roots (optional)"),
    }
    values = {key: ask(label) for key, label in FIELDS}
    profile_text(values, language)  # Check the shared data contract before preview and writing.
    config = {"schema_version": 1, "confirmed": False, "language": language, "clients": clients, "paths": paths}
    pruefer.validate({**config, "confirmed": True}, home)
    destination = check_destination(paths["profile"], home)
    print("\nPreview of the local configuration:")
    print(json.dumps(config, ensure_ascii=False, indent=2))
    print("\nProfile details:")
    for key, label in FIELDS:
        print(f"{label}: {values[key] or 'open'}")
    names = ", ".join(lang.private_names()[:-1])
    print(f"The profile folder will contain {names} and .env.")
    if ask("Save this setup? (yes/no)", "no").lower() != "yes":
        print("Cancelled. No files created.")
        return None
    if ask("Enter a Blockbrain key? (yes/no)", "no").lower() == "yes":
        key = getpass.getpass("Blockbrain key (leave empty to skip): ")
    else:
        key = ""
    check_destination(paths["profile"], home)
    config["confirmed"] = True
    save_profile(destination, config, values, key, language)
    print(f"Profile set up: {destination}")
    return destination / lang.config_name


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home(), help="Home folder for ~/ (also for synthetic tests)")
    parser.add_argument("--language", choices=languages.CODES,
                        help="Language of rules and skills. Asked interactively if omitted (default en).")
    args = parser.parse_args(argv)
    try:
        interactive(args.home, args.language)
    except (pruefer.ConfigurationError, profil.TransferError, OSError, EOFError, KeyboardInterrupt, UnicodeError) as error:
        if isinstance(error, (pruefer.ConfigurationError, profil.TransferError)):
            print(f"Setup cancelled: {error}", file=sys.stderr)
        else:
            print("Setup cancelled. No existing profile data was changed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
