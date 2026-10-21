#!/usr/bin/env python3
"""Prüft eine bestätigte lokale AIOS-Pfadkonfiguration ohne Änderungen."""

import argparse
import json
from pathlib import Path
import sys
import unicodedata


TOP_FIELDS = {"schema_version", "confirmed", "clients", "paths"}
PATH_FIELDS = {"source", "runtime", "profile", "output", "coding_roots", "customer_roots"}
AREA_FIELDS = ("source", "runtime", "profile", "output")
ROOT_FIELDS = ("coding_roots", "customer_roots")
CLIENTS = {"claude-code", "codex"}


class ConfigurationError(ValueError):
    """Fehler ohne Ausgabe vertraulicher Konfigurationswerte."""


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ConfigurationError("JSON enthält einen doppelten Schlüssel.")
        result[key] = value
    return result


def require_fields(value, expected, label):
    if not isinstance(value, dict):
        raise ConfigurationError(f"{label} muss ein Objekt sein.")
    if set(value) != expected:
        raise ConfigurationError(f"{label} hat fehlende oder unbekannte Felder.")


def resolve_directory_candidate(path, label):
    """Prüft vorhandene Komponenten streng, erlaubt danach neue Unterordner."""
    current = Path(path.anchor)
    parts = path.parts[1:]
    for index, part in enumerate(parts):
        candidate = current / part
        try:
            candidate.lstat()
        except FileNotFoundError:
            return current.joinpath(*parts[index:])
        except OSError:
            raise ConfigurationError(f"{label} lässt sich nicht auflösen.") from None
        try:
            current = candidate.resolve(strict=True)
            if not current.is_dir():
                raise ConfigurationError(f"{label} enthält eine Datei statt eines Ordners.")
        except (OSError, RuntimeError):
            raise ConfigurationError(f"{label} lässt sich nicht auflösen.") from None
    return current


def parse_path(value, label, home):
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ConfigurationError(f"{label} braucht einen gültigen absoluten Pfad.")
    if "$" in value or ".." in Path(value).parts or "\x00" in value:
        raise ConfigurationError(f"{label} enthält eine unzulässige Pfadangabe.")
    if value.startswith("~/"):
        if value.startswith("~//"):
            raise ConfigurationError(f"{label} enthält eine unzulässige Pfadangabe.")
        path = home / value[2:]
    elif value.startswith("//"):
        raise ConfigurationError(f"{label} enthält eine unzulässige Pfadangabe.")
    elif value.startswith("/"):
        path = Path(value)
    else:
        raise ConfigurationError(f"{label} muss absolut sein oder mit ~/ beginnen.")
    resolved = resolve_directory_candidate(path, label)
    if comparable_parts(resolved) in (comparable_parts(Path("/")), comparable_parts(home)):
        raise ConfigurationError(f"{label} darf weder Systemwurzel noch Benutzerordner sein.")
    return resolved


def comparable_parts(path):
    """Vergleicht Pfadkomponenten auch auf case-insensitiven Mac-Volumes sicher."""
    return tuple(unicodedata.normalize("NFC", part.casefold()) for part in path.parts)


def is_below(child, parent):
    child_parts = comparable_parts(child)
    parent_parts = comparable_parts(parent)
    return len(child_parts) > len(parent_parts) and child_parts[:len(parent_parts)] == parent_parts


def overlaps(first, second):
    return (comparable_parts(first) == comparable_parts(second) or
            is_below(first, second) or is_below(second, first))


def validate(config, home):
    require_fields(config, TOP_FIELDS, "Konfiguration")
    if type(config["schema_version"]) is not int or config["schema_version"] != 1:
        raise ConfigurationError("Nicht unterstützte schema_version.")
    if config["confirmed"] is not True:
        raise ConfigurationError("Pfadkonfiguration ist noch nicht bestätigt.")
    clients = config["clients"]
    if (not isinstance(clients, list) or not clients or
            any(not isinstance(item, str) or item not in CLIENTS for item in clients) or
            len(clients) != len(set(clients))):
        raise ConfigurationError("clients braucht eine eindeutige Auswahl aus claude-code und codex.")

    raw_paths = config["paths"]
    require_fields(raw_paths, PATH_FIELDS, "paths")
    areas = {name: parse_path(raw_paths[name], f"paths.{name}", home) for name in AREA_FIELDS}
    roots = []
    for name in ROOT_FIELDS:
        values = raw_paths[name]
        if not isinstance(values, list):
            raise ConfigurationError(f"paths.{name} muss eine Liste sein.")
        roots.extend((f"paths.{name}[{index}]", parse_path(value, f"paths.{name}[{index}]", home))
                     for index, value in enumerate(values))

    for index, (first_name, first_path) in enumerate(areas.items()):
        for second_name, second_path in list(areas.items())[index + 1:]:
            if overlaps(first_path, second_path):
                raise ConfigurationError(f"paths.{first_name} und paths.{second_name} überschneiden sich.")
    for root_name, root_path in roots:
        for area_name, area_path in areas.items():
            if (root_name.startswith("paths.coding_roots[") and area_name == "source" and
                    is_below(area_path, root_path)):
                continue
            if overlaps(root_path, area_path):
                raise ConfigurationError(f"{root_name} überschneidet sich mit paths.{area_name}.")
    for index, (first_name, first_path) in enumerate(roots):
        for second_name, second_path in roots[index + 1:]:
            if overlaps(first_path, second_path):
                raise ConfigurationError(f"{first_name} und {second_name} überschneiden sich.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path, help="lokale JSON-Konfiguration")
    parser.add_argument("--home", type=Path, default=Path.home(), help="Benutzerordner (für Tests oder anderen Mac)")
    args = parser.parse_args(argv)
    try:
        if not args.home.is_absolute():
            raise ConfigurationError("--home muss ein absoluter Pfad sein.")
        if str(args.home).startswith("//"):
            raise ConfigurationError("--home enthält eine unzulässige Pfadangabe.")
        home = resolve_directory_candidate(args.home, "--home")
        if not home.is_dir():
            raise ConfigurationError("--home muss ein vorhandener Benutzerordner sein.")
        if home == Path("/"):
            raise ConfigurationError("--home darf nicht die Systemwurzel sein.")
        with args.config.open("r", encoding="utf-8") as stream:
            config = json.load(stream, object_pairs_hook=unique_object)
        validate(config, home)
    except (ConfigurationError, OSError, UnicodeError, json.JSONDecodeError) as error:
        if isinstance(error, ConfigurationError):
            print(f"Konfiguration ungültig: {error}", file=sys.stderr)
        else:
            print("Konfiguration konnte nicht gelesen oder als JSON geparst werden.", file=sys.stderr)
        return 1
    print("Pfadkonfiguration gültig. Keine Dateien oder Ordner wurden geändert.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
