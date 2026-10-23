#!/usr/bin/env python3
"""Validate the private Markdown project register without reading project contents."""

import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

import languages
from check_config import (
    ConfigurationError, comparable_parts, is_below, overlaps, parse_path,
    resolve_directory_candidate, unique_object, validate,
)

# Internal column keys in table order. Header and status labels come from the language table.
COLUMNS = ('key', 'project', 'folder', 'repository', 'jira', 'status')


class RegisterError(ValueError):
    pass


def cells(line):
    return [item.strip() for item in line.strip().strip('|').split('|')]


def parse_register(text, language=languages.DEFAULT):
    header = list(languages.get(language).register_header)
    lines = text.splitlines()
    heads = [i for i, line in enumerate(lines) if line.startswith('|') and cells(line) == header]
    if len(heads) != 1:
        raise RegisterError('Exactly one table with the defined columns is required: ' + ' | '.join(header))
    start = heads[0]
    if start + 1 >= len(lines) or len(cells(lines[start + 1])) != 6 or not all(
            re.fullmatch(r':?-{3,}:?', item) for item in cells(lines[start + 1])):
        raise RegisterError('The separator row of the table is invalid.')
    entries = []
    for i in range(start + 2, len(lines)):
        line = lines[i]
        if not line.startswith('|'):
            if line.strip():
                break
            continue
        row = cells(line)
        if len(row) != 6:
            raise RegisterError(f'Line {i + 1}: six columns required.')
        entries.append(dict(zip(COLUMNS, row), line=i + 1))
    return entries


def validate_register(text, config, home):
    validate(config, home)
    lang = languages.of_config(config)
    statuses = lang.statuses
    entries = parse_register(text, lang.code)
    roots = [parse_path(value, 'Project root', home)
             for key in ('coding_roots', 'customer_roots') for value in config['paths'][key]]
    source = parse_path(config['paths']['source'], 'Source code', home)
    keys, paths = set(), set()
    for row in entries:
        prefix = f"Line {row['line']}: "
        key = row['key'].casefold()
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', key) or key in keys:
            raise RegisterError(prefix + 'Key is missing, invalid or not unique.')
        keys.add(key)
        if not row['project'] or row['status'] not in lang.status_values:
            raise RegisterError(prefix + 'Project name or status is invalid. Allowed status values: '
                                + ', '.join(lang.status_labels) + '.')
        jira = row['jira']
        if jira and not re.fullmatch(r'[A-Z][A-Z0-9_]*', jira):
            raise RegisterError(prefix + 'Jira prefix is invalid.')
        repo = row['repository']
        if repo:
            try:
                url = urlsplit(repo)
                valid = (url.scheme == 'https' and bool(url.hostname) and not url.username
                         and not url.password and not url.query and not url.fragment)
            except ValueError:
                valid = False
            if not valid:
                raise RegisterError(prefix + 'Repository must be an HTTPS address without credentials or parameters.')
        raw = row['folder']
        if not raw:
            if row['status'] != statuses['to_assign']:
                raise RegisterError(prefix + 'Local folder is missing. Clarify the assignment first.')
            continue
        if not raw.startswith('/'):
            raise RegisterError(prefix + 'Local folder must be absolute.')
        path = parse_path(raw, 'Project folder', home)
        if not any(is_below(path, root) for root in roots):
            raise RegisterError(prefix + 'Project folder is not inside a confirmed project root.')
        if overlaps(path, source):
            raise RegisterError(prefix + 'Project folder overlaps with the AIOS source code.')
        normalized = comparable_parts(path)
        if normalized in paths:
            raise RegisterError(prefix + 'Project folder is assigned more than once.')
        paths.add(normalized)
    return entries


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--register', type=Path, required=True)
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--home', type=Path, default=Path.home())
    p.add_argument('--project', help='Unique key for printing an active project folder')
    args = p.parse_args(argv)
    try:
        if not args.home.is_absolute() or str(args.home).startswith('//'):
            raise RegisterError('Invalid home folder.')
        home = resolve_directory_candidate(args.home, 'Home folder')
        if not home.is_dir() or home == Path('/'):
            raise RegisterError('Invalid home folder.')
        config = json.loads(args.config.read_text(encoding='utf-8'), object_pairs_hook=unique_object)
        rows = validate_register(args.register.read_text(encoding='utf-8'), config, home)
        if args.project is not None:
            active = languages.of_config(config).statuses['active']
            found = [row for row in rows if row['key'].casefold() == args.project.casefold()]
            if len(found) != 1 or found[0]['status'] != active or not found[0]['folder']:
                raise RegisterError('Project is not unambiguously assigned as active. Ask first.')
            print(parse_path(found[0]['folder'], 'Project folder', home))
        else:
            print(f'Register valid: {len(rows)} entries. No project contents read and no files changed.')
        return 0
    except (RegisterError, ConfigurationError) as error:
        print(f'Register check: {error}', file=sys.stderr)
    except (OSError, UnicodeError, ValueError):
        print('Register or configuration could not be read.', file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
