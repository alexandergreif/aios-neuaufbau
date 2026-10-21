#!/usr/bin/env python3
"""Render portable content into offline customer materials using only the stdlib."""
import argparse
import hashlib
from html import escape
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
from sichere_dateien import build_directory, directory


ASSETS = Path(__file__).resolve().parent / "assets"
OUTPUTS = {"presentation": "01_praesentation.html", "handout": "02_handout.html", "examples": "03_beispiele.html"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, "Doppelter JSON-Schlüssel.")
        value[key] = item
    return value


def record(value, required, optional, label):
    require(isinstance(value, dict), f"{label}: Objekt erwartet.")
    require(set(required) <= value.keys(), f"{label}: Pflichtfelder fehlen: {set(required) - value.keys()}")
    require(value.keys() <= set(required) | set(optional), f"{label}: unbekannte Felder: {value.keys() - set(required) - set(optional)}")


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), f"{label}: nichtleerer Text erwartet.")


def texts(value, label):
    require(isinstance(value, list), f"{label}: Liste erwartet.")
    for item in value:
        text(item, label)


def validate(data):
    record(data, ["schema_version", "meta", "case", "chapters", "examples", "sources"], [], "Inhalt")
    require(type(data["schema_version"]) is int and data["schema_version"] == 1, "Unbekannte schema_version.")
    record(data["meta"], ["title", "customer", "subtitle", "date", "version", "author"], [], "meta")
    for key, value in data["meta"].items():
        text(value, f"meta.{key}")
    record(data["case"], ["title", "description"], [], "case")
    for value in data["case"].values():
        text(value, "case")
    require(isinstance(data["chapters"], list) and data["chapters"], "Mindestens ein Kapitel ist nötig.")
    require(isinstance(data["examples"], list), "examples: Liste erwartet.")
    require(isinstance(data["sources"], list), "sources: Liste erwartet.")
    ids = set()

    def identifier(value):
        require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9-]*", value), "IDs: Kleinbuchstaben, Ziffern und Bindestriche verwenden.")
        require(value not in ids, f"Doppelte ID: {value}")
        ids.add(value)

    for item in data["examples"]:
        record(item, ["id", "title", "role", "prompt"], [], "Beispiel")
        identifier(item["id"])
        for key in ["title", "role", "prompt"]:
            text(item[key], key)
    prompt_ids = {item["id"] for item in data["examples"]}
    for chapter in data["chapters"]:
        record(chapter, ["id", "title", "summary", "fields", "slides"], [], "Kapitel")
        identifier(chapter["id"])
        text(chapter["title"], "Kapiteltitel")
        text(chapter["summary"], "Kapitelzusammenfassung")
        texts(chapter["fields"], "Ausfüllfelder")
        require(isinstance(chapter["slides"], list) and chapter["slides"], "Mindestens eine Folie je Kapitel ist nötig.")
        for slide in chapter["slides"]:
            record(slide, ["id", "title"], ["text", "points", "prompt_ids", "notes", "comparison", "exercise", "discussion", "mins"], "Folie")
            identifier(slide["id"])
            text(slide["title"], "Folientitel")
            if "mins" in slide:
                require(type(slide["mins"]) is int and 0 < slide["mins"] <= 240, "mins: ganze Minutenzahl zwischen 1 und 240 erwartet.")
            for key in ["text", "notes", "exercise", "discussion"]:
                if key in slide:
                    text(slide[key], key)
            for key in ["points", "prompt_ids"]:
                if key in slide:
                    texts(slide[key], key)
            for ref in slide.get("prompt_ids", []):
                require(ref in prompt_ids, f"Unbekannter Prompt-Verweis: {ref}")
            refs = slide.get("prompt_ids", [])
            require(len(refs) == len(set(refs)), "Ein Prompt darf je Folie nur einmal referenziert werden.")
            if "comparison" in slide:
                record(slide["comparison"], ["avoid", "better"], [], "Vergleich")
                for value in slide["comparison"].values():
                    text(value, "Vergleich")
    for source in data["sources"]:
        record(source, ["label", "url"], [], "Quelle")
        text(source["label"], "Quellenname")
        text(source["url"], "Quellenadresse")
        parsed = urlsplit(source["url"])
        require(parsed.scheme in ("http", "https") and parsed.hostname and not parsed.username and not parsed.password,
                "Quellenadressen müssen HTTP(S)-Links ohne Zugangsdaten sein.")


def palette_from(path, name):
    blocks = re.findall(r"```json\s*\n(.*?)\n```", path.read_text(), re.S)
    require(len(blocks) == 1, "Palettendatei braucht genau einen JSON-Block.")
    data = json.loads(blocks[0], object_pairs_hook=unique_object)
    require(data.get("schema_version") == 1, "Unbekannte Palettenversion.")
    require(name in data.get("palettes", {}), f"Unbekannte Palette: {name}")
    palette = data["palettes"][name]
    for key in ["primary", "accent", "ink"]:
        require(isinstance(palette.get(key), str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", palette[key]), f"Ungültige Farbe: {key}")
    text(palette.get("notice"), "Palettenhinweis")
    return palette


def paragraph(value, cls=""):
    return f'<p class="{cls}">{escape(value)}</p>' if value else ""


def prompt_box(item, suffix):
    ident = f'prompt_{item["id"]}_{suffix}'
    return (f'<div class="prompt"><div class="prompt-heading"><strong>{escape(item["title"])}</strong>'
            f'<button type="button" data-copy="{ident}" aria-label="Prompt {escape(item["title"], quote=True)} kopieren">Kopieren</button></div>'
            f'<pre id="{ident}"><code>{escape(item["prompt"])}</code></pre></div>')


def minutes(slide):
    return f'<span class="mins">{slide["mins"]} Min.</span>' if slide.get("mins") else ""


def chapter_minutes(chapter):
    total = sum(slide.get("mins", 0) for slide in chapter["slides"])
    return f'<span class="mins">{total} Min.</span>' if total else ""


def slide_body(slide, examples, suffix):
    chunks = [paragraph(slide.get("text", ""), "lead")]
    if slide.get("points"):
        chunks.append('<ul class="points">' + "".join(f"<li>{escape(point)}</li>" for point in slide["points"]) + "</ul>")
    if "comparison" in slide:
        comp = slide["comparison"]
        chunks.append(f'<div class="comparison"><div><h3>So nicht</h3>{paragraph(comp["avoid"])}</div>'
                      f'<div><h3>So besser</h3>{paragraph(comp["better"])}</div></div>')
    chunks.extend(prompt_box(examples[ref], suffix) for ref in slide.get("prompt_ids", []))
    if "exercise" in slide:
        chunks.append(f'<details class="exercise"><summary>Gemeinsam ausprobieren</summary>{paragraph(slide["exercise"])}</details>')
    if "discussion" in slide:
        chunks.append(f'<details class="discussion"><summary>Kurz in die Runde</summary>{paragraph(slide["discussion"])}</details>')
    return "\n".join(chunks)


def render_body(data, kind):
    meta = data["meta"]
    example_map = {item["id"]: item for item in data["examples"]}
    case = data["case"]
    hero = (f'<p class="kicker">{escape(meta["customer"])} / {escape(meta["date"])}</p>'
            f'<h1>{escape(meta["title"])}</h1>{paragraph(meta["subtitle"], "lead")}'
            f'<div class="case"><h2>{escape(case["title"])}</h2>{paragraph(case["description"])}</div>')
    chapters = []
    overview = ""
    if kind == "presentation":
        slides = [(meta["title"], f'<section class="slide hero" data-slide="0" aria-label="Titelfolie">{hero}</section>')]
        for number, chapter in enumerate(data["chapters"], 1):
            for slide in chapter["slides"]:
                idx = len(slides)
                notes = f'<aside class="notes"><h3>Trainernotiz</h3>{paragraph(slide["notes"])}</aside>' if slide.get("notes") else ""
                markup = (f'<section class="slide" data-slide="{idx}" hidden aria-label="{escape(slide["title"], quote=True)}">'
                          f'<p class="chapter-label"><span>{number:02d}</span>{escape(chapter["title"])}{minutes(slide)}</p>'
                          f'<h2>{escape(slide["title"])}</h2>{slide_body(slide, example_map, slide["id"])}{notes}</section>')
                slides.append((slide["title"], markup))
        slides.append(("Fragen und nächster Schritt", f'<section class="slide questions" data-slide="{len(slides)}" hidden>'
                       '<p class="kicker">Gemeinsamer Abschluss</p><h2>Was probierst du als Nächstes aus?</h2>'
                       '<p class="lead">Offene Fragen klären. Einen nächsten Schritt festhalten.</p></section>'))
        chapters = [markup for _, markup in slides]
        links = "".join(f'<button type="button" data-goto="{idx}"><span>{idx + 1:02d}</span>{escape(title)}</button>' for idx, (title, _) in enumerate(slides))
        overview = ('<dialog id="overview" aria-labelledby="overview-title"><div class="dialog-head"><h2 id="overview-title">Folienübersicht</h2>'
                    '<button type="button" id="close-overview">Schließen</button></div><div class="overview-grid">' + links + '</div></dialog>')
        controls = ('<span class="shortcut-hint">Pfeiltasten blättern. N zeigt die Notizen. Escape schließt die Übersicht.</span>'
                    '<button type="button" id="previous" aria-label="Vorherige Folie">Zurück</button>'
                    '<span id="position" aria-live="polite"></span><button type="button" id="next" aria-label="Nächste Folie">Weiter</button>'
                    '<button type="button" id="show-overview">Übersicht</button>'
                    '<button type="button" id="show-notes" aria-pressed="false" title="Umschalttaste oder N">Trainernotizen</button>')
    else:
        chapters.append(f'<header class="hero">{hero}</header>')
        if kind == "handout":
            for number, chapter in enumerate(data["chapters"], 1):
                fields = "".join(f'<label class="writing-field" for="field-{number}-{i}">{escape(label)}'
                                 f'<textarea id="field-{number}-{i}" rows="3" spellcheck="true"></textarea></label>' for i, label in enumerate(chapter["fields"]))
                body = "".join(f'<article><h3>{escape(slide["title"])}{minutes(slide)}</h3>{slide_body(slide, example_map, slide["id"])}</article>' for slide in chapter["slides"])
                chapters.append(f'<section class="handout-chapter"><p class="chapter-label"><span>{number:02d}</span>Arbeitsblatt{chapter_minutes(chapter)}</p>'
                                f'<h2>{escape(chapter["title"])}</h2>{paragraph(chapter["summary"], "lead")}{body}{fields}</section>')
            controls = '<span>Teilnehmer-Handout</span><span class="save-hint">Eingaben sind nur in diesem geöffneten Tab verfügbar. Zum Behalten ausgefüllt drucken.</span>'
        else:
            roles = sorted({item["role"] for item in data["examples"]})
            options = "".join(f'<option value="{escape(role, quote=True)}">{escape(role)}</option>' for role in roles)
            chapters.append('<div class="filter"><label for="role-filter">Beispiele für</label><select id="role-filter">'
                            '<option value="">Alle Rollen</option>' + options + '</select><span id="example-count" aria-live="polite"></span></div>')
            for item in data["examples"]:
                chapters.append(f'<article class="example" data-role="{escape(item["role"], quote=True)}">'
                                f'<p class="kicker">{escape(item["role"])}</p>{prompt_box(item, "example")}</article>')
            controls = '<span>Kopierbare Beispiele</span>'
    sources = "".join(f'<li><a href="{escape(source["url"], quote=True)}" rel="noreferrer">{escape(source["label"])}</a></li>' for source in data["sources"])
    source_block = f'<details class="sources"><summary>Quellen</summary><ul>{sources}</ul></details>' if sources else ""
    return (f'<a class="skip-link" href="#content">Zum Inhalt</a><nav class="topnav" aria-label="Ansicht steuern">'
            f'<a class="wordmark" href="#content">{escape(meta["customer"])}</a><div class="controls">{controls}'
            '<button type="button" id="print">Drucken</button></div></nav>'
            f'<main id="content">{"".join(chapters)}</main>{overview}'
            f'<footer><span>{escape(meta["author"])} · Version {escape(meta["version"])}</span>{source_block}</footer>'
            '<p id="copy-status" role="status" aria-live="polite"></p>')


def build(args):
    require(not args.output.exists(), "Ausgabeordner existiert bereits. Neue Version in einem neuen Ordner bauen.")
    data = json.loads(args.input.read_text(), object_pairs_hook=unique_object)
    validate(data)
    palette = palette_from(args.palette_file, args.palette)
    css = args.profile.read_text()
    require(not re.search(r"</style|@import|url\s*\(", css, re.I), "Designprofil muss ohne eingebundene Ressourcen und HTML auskommen.")
    js = (ASSETS / "interaction.js").read_text()
    shell = (ASSETS / "layout.html").read_text()
    colors = ":root { " + " ".join(f"--brand-{key}: {palette[key]};" for key in ["primary", "accent", "ink"]) + " }"
    content_bytes = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode()
    outputs = {"inhalt.json": content_bytes}
    for kind in args.artifacts:
        values = {"title": escape(data["meta"]["title"]), "version": escape(data["meta"]["version"]),
                  "css": css + "\n" + colors, "js": js, "body": render_body(data, kind), "kind": kind}
        # One substitution pass prevents user text from becoming a template instruction.
        document = re.sub(r"\{\{(title|version|css|js|body|kind)\}\}", lambda match: values[match[1]], shell)
        outputs[OUTPUTS[kind]] = document.encode()
    manifest = {"schema_version": 1, "content_sha256": hashlib.sha256(content_bytes).hexdigest(),
                "profile": args.profile.name, "profile_sha256": hashlib.sha256(css.encode()).hexdigest(),
                "palette_name": args.palette, "palette": palette,
                "files": {name: hashlib.sha256(value).hexdigest() for name, value in outputs.items()},
                "audience": {"inhalt.json": "trainer", "01_praesentation.html": "trainer", "02_handout.html": "participants", "03_beispiele.html": "participants"}}
    outputs["build.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    if not args.output.is_absolute() or ".." in args.output.parts:
        raise ValueError("Ausgabeordner muss ein absoluter Pfad ohne '..' sein.")
    parent_fd = directory(args.output.parent, create=True)
    os.close(parent_fd)
    build_directory(args.output, {Path(name): value for name, value in outputs.items()})
    print(f"Erstellt: {args.output}\n{palette['notice']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--palette", default="blockbrain")
    parser.add_argument("--palette-file", required=True, type=Path)
    parser.add_argument("--profile", type=Path, default=ASSETS / "profiles/hausformat.css")
    parser.add_argument("--artifacts", choices=OUTPUTS, nargs="+", default=list(OUTPUTS))
    args = parser.parse_args()
    try:
        build(args)
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(2, f"Build abgebrochen: {error}\n")


if __name__ == "__main__":
    main()
