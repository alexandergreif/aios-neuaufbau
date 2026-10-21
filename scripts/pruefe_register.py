#!/usr/bin/env python3
"""Validiert das private Markdown-Projektregister, ohne Inhalte der Projekte zu lesen."""

import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

from pruefe_konfiguration import (
    ConfigurationError, comparable_parts, is_below, overlaps, parse_path,
    resolve_directory_candidate, unique_object, validate,
)

HEADER = ['Kürzel', 'Kunde oder Projekt', 'Lokaler Ordner', 'Repository', 'Jira-Präfix', 'Status']
STATUSES = {'aktiv', 'pausiert', 'archiviert', 'zuordnen'}


class RegisterError(ValueError):
    pass


def cells(line):
    return [item.strip() for item in line.strip().strip('|').split('|')]


def parse_register(text):
    lines = text.splitlines()
    heads = [i for i, line in enumerate(lines) if line.startswith('|') and cells(line) == HEADER]
    if len(heads) != 1:
        raise RegisterError('Genau eine Tabelle mit den festgelegten Spalten ist erforderlich.')
    start = heads[0]
    if start + 1 >= len(lines) or len(cells(lines[start + 1])) != 6 or not all(
            re.fullmatch(r':?-{3,}:?', item) for item in cells(lines[start + 1])):
        raise RegisterError('Die Trennzeile der Tabelle ist ungültig.')
    entries = []
    for i in range(start + 2, len(lines)):
        line = lines[i]
        if not line.startswith('|'):
            if line.strip():
                break
            continue
        row = cells(line)
        if len(row) != 6:
            raise RegisterError(f'Zeile {i + 1}: sechs Spalten erforderlich.')
        entries.append(dict(zip(HEADER, row), line=i + 1))
    return entries


def validate_register(text, config, home):
    validate(config, home)
    entries = parse_register(text)
    roots = [parse_path(value, 'Projektwurzel', home)
             for key in ('coding_roots', 'customer_roots') for value in config['paths'][key]]
    source = parse_path(config['paths']['source'], 'Quellcode', home)
    keys, paths = set(), set()
    for row in entries:
        prefix = f"Zeile {row['line']}: "
        key = row['Kürzel'].casefold()
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', key) or key in keys:
            raise RegisterError(prefix + 'Kürzel fehlt, ist ungültig oder nicht eindeutig.')
        keys.add(key)
        if not row['Kunde oder Projekt'] or row['Status'] not in STATUSES:
            raise RegisterError(prefix + 'Projektname oder Status ist ungültig.')
        jira = row['Jira-Präfix']
        if jira and not re.fullmatch(r'[A-Z][A-Z0-9_]*', jira):
            raise RegisterError(prefix + 'Jira-Präfix ist ungültig.')
        repo = row['Repository']
        if repo:
            try:
                url = urlsplit(repo)
                valid = (url.scheme == 'https' and bool(url.hostname) and not url.username
                         and not url.password and not url.query and not url.fragment)
            except ValueError:
                valid = False
            if not valid:
                raise RegisterError(prefix + 'Repository muss eine HTTPS-Adresse ohne Zugangsdaten oder Parameter sein.')
        raw = row['Lokaler Ordner']
        if not raw:
            if row['Status'] != 'zuordnen':
                raise RegisterError(prefix + 'Lokaler Ordner fehlt. Zuordnung zuerst klären.')
            continue
        if not raw.startswith('/'):
            raise RegisterError(prefix + 'Lokaler Ordner muss absolut sein.')
        path = parse_path(raw, 'Projektordner', home)
        if not any(is_below(path, root) for root in roots):
            raise RegisterError(prefix + 'Projektordner liegt nicht innerhalb einer bestätigten Projektwurzel.')
        if overlaps(path, source):
            raise RegisterError(prefix + 'Projektordner überschneidet sich mit dem AIOS-Quellcode.')
        normalized = comparable_parts(path)
        if normalized in paths:
            raise RegisterError(prefix + 'Projektordner ist mehrfach zugeordnet.')
        paths.add(normalized)
    return entries


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--register', type=Path, required=True)
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--home', type=Path, default=Path.home())
    p.add_argument('--project', help='Eindeutiges Kürzel zur Ausgabe eines aktiven Projektordners')
    args = p.parse_args(argv)
    try:
        if not args.home.is_absolute() or str(args.home).startswith('//'):
            raise RegisterError('Ungültiger Benutzerordner.')
        home = resolve_directory_candidate(args.home, 'Benutzerordner')
        if not home.is_dir() or home == Path('/'):
            raise RegisterError('Ungültiger Benutzerordner.')
        config = json.loads(args.config.read_text(encoding='utf-8'), object_pairs_hook=unique_object)
        rows = validate_register(args.register.read_text(encoding='utf-8'), config, home)
        if args.project is not None:
            found = [row for row in rows if row['Kürzel'].casefold() == args.project.casefold()]
            if len(found) != 1 or found[0]['Status'] != 'aktiv' or not found[0]['Lokaler Ordner']:
                raise RegisterError('Projekt ist nicht eindeutig aktiv zugeordnet. Zuerst nachfragen.')
            print(parse_path(found[0]['Lokaler Ordner'], 'Projektordner', home))
        else:
            print(f'Register gültig: {len(rows)} Einträge. Keine Projektinhalte gelesen oder Dateien geändert.')
        return 0
    except (RegisterError, ConfigurationError) as error:
        print(f'Registerprüfung: {error}', file=sys.stderr)
    except (OSError, UnicodeError, ValueError):
        print('Register oder Konfiguration konnte nicht gelesen werden.', file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
