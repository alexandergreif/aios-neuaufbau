#!/usr/bin/env python3
"""Check a confirmed local AIOS path configuration without changing anything."""

import argparse
import json
from pathlib import Path
import sys
import unicodedata

import languages


TOP_FIELDS = {"schema_version", "confirmed", "clients", "paths"}
OPTIONAL_FIELDS = {"language"}
PATH_FIELDS = {"source", "runtime", "profile", "output", "coding_roots", "customer_roots"}
AREA_FIELDS = ("source", "runtime", "profile", "output")
ROOT_FIELDS = ("coding_roots", "customer_roots")
CLIENTS = {"claude-code", "codex"}


class ConfigurationError(ValueError):
    """Error that never echoes confidential configuration values."""


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ConfigurationError("JSON contains a duplicate key.")
        result[key] = value
    return result


def require_fields(value, expected, label, optional=frozenset()):
    if not isinstance(value, dict):
        raise ConfigurationError(f"{label} must be an object.")
    if not expected <= set(value) <= expected | set(optional):
        raise ConfigurationError(f"{label} has missing or unknown fields.")


def resolve_directory_candidate(path, label):
    """Check existing components strictly, then allow new subfolders."""
    current = Path(path.anchor)
    parts = path.parts[1:]
    for index, part in enumerate(parts):
        candidate = current / part
        try:
            candidate.lstat()
        except FileNotFoundError:
            return current.joinpath(*parts[index:])
        except OSError:
            raise ConfigurationError(f"{label} cannot be resolved.") from None
        try:
            current = candidate.resolve(strict=True)
            if not current.is_dir():
                raise ConfigurationError(f"{label} contains a file instead of a folder.")
        except (OSError, RuntimeError):
            raise ConfigurationError(f"{label} cannot be resolved.") from None
    return current


def parse_path(value, label, home):
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ConfigurationError(f"{label} needs a valid absolute path.")
    if "$" in value or ".." in Path(value).parts or "\x00" in value:
        raise ConfigurationError(f"{label} contains an invalid path.")
    if value.startswith("~/"):
        if value.startswith("~//"):
            raise ConfigurationError(f"{label} contains an invalid path.")
        path = home / value[2:]
    elif value.startswith("//"):
        raise ConfigurationError(f"{label} contains an invalid path.")
    elif value.startswith("/"):
        path = Path(value)
    else:
        raise ConfigurationError(f"{label} must be absolute or start with ~/.")
    resolved = resolve_directory_candidate(path, label)
    if comparable_parts(resolved) in (comparable_parts(Path("/")), comparable_parts(home)):
        raise ConfigurationError(f"{label} must be neither the system root nor the home folder.")
    return resolved


def comparable_parts(path):
    """Compare path components safely, also on case-insensitive Mac volumes."""
    return tuple(unicodedata.normalize("NFC", part.casefold()) for part in path.parts)


def is_below(child, parent):
    child_parts = comparable_parts(child)
    parent_parts = comparable_parts(parent)
    return len(child_parts) > len(parent_parts) and child_parts[:len(parent_parts)] == parent_parts


def overlaps(first, second):
    return (comparable_parts(first) == comparable_parts(second) or
            is_below(first, second) or is_below(second, first))


def validate(config, home):
    require_fields(config, TOP_FIELDS, "Configuration", OPTIONAL_FIELDS)
    if type(config["schema_version"]) is not int or config["schema_version"] != 1:
        raise ConfigurationError("Unsupported schema_version.")
    if config["confirmed"] is not True:
        raise ConfigurationError("Path configuration is not confirmed yet.")
    if "language" in config and (not isinstance(config["language"], str) or
                                 config["language"] not in languages.CODES):
        raise ConfigurationError("language must be de or en.")
    clients = config["clients"]
    if (not isinstance(clients, list) or not clients or
            any(not isinstance(item, str) or item not in CLIENTS for item in clients) or
            len(clients) != len(set(clients))):
        raise ConfigurationError("clients needs a unique selection from claude-code and codex.")

    raw_paths = config["paths"]
    require_fields(raw_paths, PATH_FIELDS, "paths")
    areas = {name: parse_path(raw_paths[name], f"paths.{name}", home) for name in AREA_FIELDS}
    roots = []
    for name in ROOT_FIELDS:
        values = raw_paths[name]
        if not isinstance(values, list):
            raise ConfigurationError(f"paths.{name} must be a list.")
        roots.extend((f"paths.{name}[{index}]", parse_path(value, f"paths.{name}[{index}]", home))
                     for index, value in enumerate(values))

    for index, (first_name, first_path) in enumerate(areas.items()):
        for second_name, second_path in list(areas.items())[index + 1:]:
            if overlaps(first_path, second_path):
                raise ConfigurationError(f"paths.{first_name} and paths.{second_name} overlap.")
    for root_name, root_path in roots:
        for area_name, area_path in areas.items():
            if (root_name.startswith("paths.coding_roots[") and area_name == "source" and
                    is_below(area_path, root_path)):
                continue
            if overlaps(root_path, area_path):
                raise ConfigurationError(f"{root_name} overlaps with paths.{area_name}.")
    for index, (first_name, first_path) in enumerate(roots):
        for second_name, second_path in roots[index + 1:]:
            if overlaps(first_path, second_path):
                raise ConfigurationError(f"{first_name} and {second_name} overlap.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path, help="Local JSON configuration")
    parser.add_argument("--home", type=Path, default=Path.home(), help="Home folder (for tests or another Mac)")
    args = parser.parse_args(argv)
    try:
        if not args.home.is_absolute():
            raise ConfigurationError("--home must be an absolute path.")
        if str(args.home).startswith("//"):
            raise ConfigurationError("--home contains an invalid path.")
        home = resolve_directory_candidate(args.home, "--home")
        if not home.is_dir():
            raise ConfigurationError("--home must be an existing home folder.")
        if home == Path("/"):
            raise ConfigurationError("--home must not be the system root.")
        with args.config.open("r", encoding="utf-8") as stream:
            config = json.load(stream, object_pairs_hook=unique_object)
        validate(config, home)
    except (ConfigurationError, OSError, UnicodeError, json.JSONDecodeError) as error:
        if isinstance(error, ConfigurationError):
            print(f"Invalid configuration: {error}", file=sys.stderr)
        else:
            print("Configuration could not be read or parsed as JSON.", file=sys.stderr)
        return 1
    print("Path configuration valid. No files or folders were changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
