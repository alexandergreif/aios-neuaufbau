"""Fixed file boundary for package builds and runtime status checks."""

from pathlib import PurePosixPath

import languages


SCRIPT_NAMES = (
    "languages.py", "setup_profile.py", "profile_transfer.py", "check_config.py", "check_register.py",
    "setup_status.py", "safe_files.py", "package_rules.py", "package_inventory.py",
)
# Runtime scripts of package versions up to 0.1.7-dev. Accepted only when an
# installed manifest is read, so that an update can remove them as owned files.
LEGACY_SCRIPT_NAMES = (
    "einrichten.py", "profil_transfer.py", "pruefe_konfiguration.py", "pruefe_register.py",
    "einrichtungsstatus.py", "sichere_dateien.py", "paketregeln.py", "paketbestand.py",
)
PRIVATE_FILES = {"profil.md", "projekte.md", "pfade.json", "profile.md", "projects.md", "paths.json",
                 "credentials.json", "secrets.json", "id_rsa", "id_ed25519"}
PRIVATE_DIRS = {"profil", "profile", "projekt", "project", "projects", "projekte", "kunden", "zustand",
                "state", "wissen", "knowledge", "ergebnisse", "output", "journal", "journals", "archive",
                "archives", "secrets", "credentials"}
SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}


def templates(language=languages.DEFAULT):
    lang = languages.get(language)
    return {lang.runtime_path(raw) for raw in lang.template_files}


def template_dirs(language=languages.DEFAULT):
    lang = languages.get(language)
    return {lang.runtime_path(raw) for raw in lang.template_dirs}


def valid_relative(raw):
    return (isinstance(raw, str) and bool(raw) and not raw.startswith("/") and "\\" not in raw and
            all(part not in ("", ".", "..") for part in raw.split("/")) and
            not any(ord(char) < 32 or ord(char) == 127 for char in raw))


def _safe_part(part):
    lower = part.lower()
    return (not (lower.startswith(".env") and lower != ".env.example") and
            lower not in PRIVATE_FILES and PurePosixPath(lower).suffix not in SECRET_SUFFIXES)


def allowed_directory(raw, language=languages.DEFAULT):
    lang = languages.get(language)
    if not valid_relative(raw) or not raw.startswith(lang.root + "/"):
        return False
    exempt = template_dirs(language)
    parts = raw.split("/")
    for index, part in enumerate(parts[1:], 1):
        current = "/".join(parts[:index + 1])
        if (part.lower().startswith(".env") or not _safe_part(part) or
                (part.lower() in PRIVATE_DIRS and current not in exempt)):
            return False
        if any(current.startswith(template + "/") for template in exempt):
            return False
    return True


def allowed_file(raw, language=languages.DEFAULT, legacy_scripts=False):
    lang = languages.get(language)
    if not valid_relative(raw):
        return False
    if raw in ("AGENTS.md", "CLAUDE.md"):
        return True
    parts = raw.split("/")
    if len(parts) == 2 and parts[0] == "scripts":
        return parts[1] in SCRIPT_NAMES or (legacy_scripts and parts[1] in LEGACY_SCRIPT_NAMES)
    if len(parts) < 2 or parts[0] != lang.root:
        return False
    if raw in templates(language):
        return True
    if len(parts) > 2 and not allowed_directory("/".join(parts[:-1]), language):
        return False
    if not all(_safe_part(part) for part in parts[1:]):
        return False
    if any(part.lower() in PRIVATE_DIRS for part in parts[1:]):
        return False
    return True
