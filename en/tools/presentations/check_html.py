#!/usr/bin/env python3
"""Checks visible HTML text and external resources without extra packages."""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden = []
        self.text = []
        self.external = []
        self.ids = []
        self.styles = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('script', 'style', 'svg'):
            self.hidden.append(tag)
        if tag == 'section':
            self.ids.append(attrs.get('id'))
        for key in ('src', 'href', 'srcset', 'action', 'formaction', 'poster', 'data', 'background', 'xlink:href', 'ping'):
            value = attrs.get(key, '')
            if value and (key == 'srcset' or not value.startswith(('#', 'data:'))):
                self.external.append(value)
        if attrs.get('srcdoc'):
            self.external.append('srcdoc')
        if re.search(r'@import\b|url\s*\(', attrs.get('style', ''), re.I):
            self.external.append('inline style')
        if tag == 'meta' and attrs.get('http-equiv', '').lower() == 'refresh':
            value = attrs.get('content', '')
            if re.search(r'\burl\s*=', value, re.I):
                self.external.append(value)

    def handle_endtag(self, tag):
        if self.hidden and tag == self.hidden[-1]:
            self.hidden.pop()

    def handle_data(self, data):
        if not self.hidden:
            self.text.append(data)
        elif self.hidden[-1] == 'style':
            self.styles.append(data)
        elif self.hidden[-1] == 'script':
            self.scripts.append(data)


def inspect_html(source):
    parser = VisibleText()
    parser.feed(source)
    text = ' '.join(parser.text)
    forbidden = {c: text.count(c) for c in ('\u2014', '\u2013', ';', '!') if c in text}
    css = ''.join(parser.styles)
    resources = parser.external + re.findall(r'@import\s+[^;]+|url\(\s*[\"\']?(?!data:|#)([^)\"\']+)', css)
    dynamic_network = re.findall(r'\b(?:fetch|XMLHttpRequest|WebSocket|EventSource)\b', ''.join(parser.scripts))
    errors = []
    if forbidden:
        errors.append('Forbidden characters in visible text')
    if resources or dynamic_network:
        errors.append('External resources or network calls present')
    if not parser.ids or parser.ids != [f's{i}' for i in range(1, len(parser.ids) + 1)]:
        errors.append('Slide IDs must be sequential s1 through sN')
    return {'slides': len(parser.ids), 'forbidden': forbidden,
            'numbers': sorted(set(re.findall(r'\d[\d.,]*', text))),
            'resources': resources, 'network_calls': dynamic_network, 'errors': errors}


if __name__ == '__main__':
    result = inspect_html(Path(sys.argv[1]).read_text(encoding='utf-8'))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(bool(result['errors']))
