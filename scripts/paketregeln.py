"""Feste Dateigrenze für Paketbau und Runtime-Statusprüfung."""

from pathlib import PurePosixPath


SCRIPT_NAMES = (
    "einrichten.py", "profil_transfer.py", "pruefe_konfiguration.py", "pruefe_register.py",
    "einrichtungsstatus.py", "sichere_dateien.py", "paketregeln.py", "paketbestand.py",
)
PRIVATE_FILES = {"profil.md", "projekte.md", "pfade.json", "credentials.json", "secrets.json",
                 "id_rsa", "id_ed25519"}
PRIVATE_DIRS = {"profil", "profile", "projekt", "projects", "projekte", "kunden", "zustand",
                "wissen", "ergebnisse", "output", "journal", "journals", "archive", "archives",
                "secrets", "credentials"}
SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
TEMPLATES = {"allgemein/vorlagen/profil.md", "allgemein/vorlagen/projekte.md",
             "allgemein/vorlagen/wissen/INDEX.md", "allgemein/vorlagen/wissen/notiz.md",
             "allgemein/vorlagen/projekt/PLAN.md", "allgemein/vorlagen/projekt/NOTIZEN.md"}
TEMPLATE_DIRS = {"allgemein/vorlagen/wissen", "allgemein/vorlagen/projekt"}


def valid_relative(raw):
    return (isinstance(raw, str) and bool(raw) and not raw.startswith("/") and "\\" not in raw and
            all(part not in ("", ".", "..") for part in raw.split("/")) and
            not any(ord(char) < 32 or ord(char) == 127 for char in raw))


def _safe_part(part):
    lower = part.lower()
    return (not (lower.startswith(".env") and lower != ".env.example") and
            lower not in PRIVATE_FILES and PurePosixPath(lower).suffix not in SECRET_SUFFIXES)


def allowed_directory(raw):
    if not valid_relative(raw) or not raw.startswith("allgemein/"):
        return False
    parts = raw.split("/")
    for index, part in enumerate(parts[1:], 1):
        current = "/".join(parts[:index + 1])
        if (part.lower().startswith(".env") or not _safe_part(part) or
                (part.lower() in PRIVATE_DIRS and current not in TEMPLATE_DIRS)):
            return False
        if any(current.startswith(template + "/") for template in TEMPLATE_DIRS):
            return False
    return True


def allowed_file(raw):
    if not valid_relative(raw):
        return False
    if raw in ("AGENTS.md", "CLAUDE.md"):
        return True
    parts = raw.split("/")
    if len(parts) == 2 and parts[0] == "scripts":
        return parts[1] in SCRIPT_NAMES
    if len(parts) < 2 or parts[0] != "allgemein":
        return False
    if raw in TEMPLATES:
        return True
    if len(parts) > 2 and not allowed_directory("/".join(parts[:-1])):
        return False
    if not all(_safe_part(part) for part in parts[1:]):
        return False
    if any(part.lower() in PRIVATE_DIRS for part in parts[1:]):
        return False
    return True
