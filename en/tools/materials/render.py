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
from safe_files import build_directory, directory


ASSETS = Path(__file__).resolve().parent / "assets"
OUTPUTS = {"presentation": "01_praesentation.html", "handout": "02_handout.html", "examples": "03_beispiele.html"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, "Duplicate JSON key.")
        value[key] = item
    return value


def record(value, required, optional, label):
    require(isinstance(value, dict), f"{label}: object expected.")
    require(set(required) <= value.keys(), f"{label}: missing required fields: {set(required) - value.keys()}")
    require(value.keys() <= set(required) | set(optional), f"{label}: unknown fields: {value.keys() - set(required) - set(optional)}")


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), f"{label}: non-empty text expected.")


def texts(value, label):
    require(isinstance(value, list), f"{label}: list expected.")
    for item in value:
        text(item, label)


def validate(data):
    record(data, ["schema_version", "meta", "case", "chapters", "examples", "sources"], [], "Content")
    require(type(data["schema_version"]) is int and data["schema_version"] == 1, "Unknown schema_version.")
    record(data["meta"], ["title", "customer", "subtitle", "date", "version", "author"], [], "meta")
    for key, value in data["meta"].items():
        text(value, f"meta.{key}")
    record(data["case"], ["title", "description"], [], "case")
    for value in data["case"].values():
        text(value, "case")
    require(isinstance(data["chapters"], list) and data["chapters"], "At least one chapter is required.")
    require(isinstance(data["examples"], list), "examples: list expected.")
    require(isinstance(data["sources"], list), "sources: list expected.")
    ids = set()

    def identifier(value):
        require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9-]*", value), "IDs: use lowercase letters, digits, and hyphens.")
        require(value not in ids, f"Duplicate ID: {value}")
        ids.add(value)

    for item in data["examples"]:
        record(item, ["id", "title", "role", "prompt"], [], "Example")
        identifier(item["id"])
        for key in ["title", "role", "prompt"]:
            text(item[key], key)
    prompt_ids = {item["id"] for item in data["examples"]}
    for chapter in data["chapters"]:
        record(chapter, ["id", "title", "summary", "fields", "slides"], [], "Chapter")
        identifier(chapter["id"])
        text(chapter["title"], "Chapter title")
        text(chapter["summary"], "Chapter summary")
        texts(chapter["fields"], "Fill-in fields")
        require(isinstance(chapter["slides"], list) and chapter["slides"], "At least one slide per chapter is required.")
        for slide in chapter["slides"]:
            record(slide, ["id", "title"], ["text", "points", "prompt_ids", "notes", "comparison", "exercise", "discussion", "mins"], "Slide")
            identifier(slide["id"])
            text(slide["title"], "Slide title")
            if "mins" in slide:
                require(type(slide["mins"]) is int and 0 < slide["mins"] <= 240, "mins: whole number of minutes between 1 and 240 expected.")
            for key in ["text", "notes", "exercise", "discussion"]:
                if key in slide:
                    text(slide[key], key)
            for key in ["points", "prompt_ids"]:
                if key in slide:
                    texts(slide[key], key)
            for ref in slide.get("prompt_ids", []):
                require(ref in prompt_ids, f"Unknown prompt reference: {ref}")
            refs = slide.get("prompt_ids", [])
            require(len(refs) == len(set(refs)), "A prompt may be referenced only once per slide.")
            if "comparison" in slide:
                record(slide["comparison"], ["avoid", "better"], [], "Comparison")
                for value in slide["comparison"].values():
                    text(value, "Comparison")
    for source in data["sources"]:
        record(source, ["label", "url"], [], "Source")
        text(source["label"], "Source name")
        text(source["url"], "Source URL")
        parsed = urlsplit(source["url"])
        require(parsed.scheme in ("http", "https") and parsed.hostname and not parsed.username and not parsed.password,
                "Source URLs must be HTTP(S) links without credentials.")


def palette_from(path, name):
    blocks = re.findall(r"```json\s*\n(.*?)\n```", path.read_text(), re.S)
    require(len(blocks) == 1, "Palette file needs exactly one JSON block.")
    data = json.loads(blocks[0], object_pairs_hook=unique_object)
    require(data.get("schema_version") == 1, "Unknown palette version.")
    require(name in data.get("palettes", {}), f"Unknown palette: {name}")
    palette = data["palettes"][name]
    for key in ["primary", "accent", "ink"]:
        require(isinstance(palette.get(key), str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", palette[key]), f"Invalid color: {key}")
    text(palette.get("notice"), "Palette notice")
    return palette


def paragraph(value, cls=""):
    return f'<p class="{cls}">{escape(value)}</p>' if value else ""


def prompt_box(item, suffix):
    ident = f'prompt_{item["id"]}_{suffix}'
    return (f'<div class="prompt"><div class="prompt-heading"><strong>{escape(item["title"])}</strong>'
            f'<button type="button" data-copy="{ident}" aria-label="Copy prompt {escape(item["title"], quote=True)}">Copy</button></div>'
            f'<pre id="{ident}"><code>{escape(item["prompt"])}</code></pre></div>')


def minutes(slide):
    return f'<span class="mins">{slide["mins"]} min</span>' if slide.get("mins") else ""


def chapter_minutes(chapter):
    total = sum(slide.get("mins", 0) for slide in chapter["slides"])
    return f'<span class="mins">{total} min</span>' if total else ""


def slide_body(slide, examples, suffix):
    chunks = [paragraph(slide.get("text", ""), "lead")]
    if slide.get("points"):
        chunks.append('<ul class="points">' + "".join(f"<li>{escape(point)}</li>" for point in slide["points"]) + "</ul>")
    if "comparison" in slide:
        comp = slide["comparison"]
        chunks.append(f'<div class="comparison"><div><h3>Avoid this</h3>{paragraph(comp["avoid"])}</div>'
                      f'<div><h3>Do this instead</h3>{paragraph(comp["better"])}</div></div>')
    chunks.extend(prompt_box(examples[ref], suffix) for ref in slide.get("prompt_ids", []))
    if "exercise" in slide:
        chunks.append(f'<details class="exercise"><summary>Try it together</summary>{paragraph(slide["exercise"])}</details>')
    if "discussion" in slide:
        chunks.append(f'<details class="discussion"><summary>Discuss briefly</summary>{paragraph(slide["discussion"])}</details>')
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
        slides = [(meta["title"], f'<section class="slide hero" data-slide="0" aria-label="Title slide">{hero}</section>')]
        for number, chapter in enumerate(data["chapters"], 1):
            for slide in chapter["slides"]:
                idx = len(slides)
                notes = f'<aside class="notes"><h3>Trainer note</h3>{paragraph(slide["notes"])}</aside>' if slide.get("notes") else ""
                markup = (f'<section class="slide" data-slide="{idx}" hidden aria-label="{escape(slide["title"], quote=True)}">'
                          f'<p class="chapter-label"><span>{number:02d}</span>{escape(chapter["title"])}{minutes(slide)}</p>'
                          f'<h2>{escape(slide["title"])}</h2>{slide_body(slide, example_map, slide["id"])}{notes}</section>')
                slides.append((slide["title"], markup))
        slides.append(("Questions and next step", f'<section class="slide questions" data-slide="{len(slides)}" hidden>'
                       '<p class="kicker">Closing together</p><h2>What will you try next?</h2>'
                       '<p class="lead">Clarify open questions. Note down a next step.</p></section>'))
        chapters = [markup for _, markup in slides]
        links = "".join(f'<button type="button" data-goto="{idx}"><span>{idx + 1:02d}</span>{escape(title)}</button>' for idx, (title, _) in enumerate(slides))
        overview = ('<dialog id="overview" aria-labelledby="overview-title"><div class="dialog-head"><h2 id="overview-title">Slide overview</h2>'
                    '<button type="button" id="close-overview">Close</button></div><div class="overview-grid">' + links + '</div></dialog>')
        controls = ('<span class="shortcut-hint">Arrow keys browse. N shows the notes. Escape closes the overview.</span>'
                    '<button type="button" id="previous" aria-label="Previous slide">Back</button>'
                    '<span id="position" aria-live="polite"></span><button type="button" id="next" aria-label="Next slide">Next</button>'
                    '<button type="button" id="show-overview">Overview</button>'
                    '<button type="button" id="show-notes" aria-pressed="false" title="Shift key or N">Trainer notes</button>')
    else:
        chapters.append(f'<header class="hero">{hero}</header>')
        if kind == "handout":
            for number, chapter in enumerate(data["chapters"], 1):
                fields = "".join(f'<label class="writing-field" for="field-{number}-{i}">{escape(label)}'
                                 f'<textarea id="field-{number}-{i}" rows="3" spellcheck="true"></textarea></label>' for i, label in enumerate(chapter["fields"]))
                body = "".join(f'<article><h3>{escape(slide["title"])}{minutes(slide)}</h3>{slide_body(slide, example_map, slide["id"])}</article>' for slide in chapter["slides"])
                chapters.append(f'<section class="handout-chapter"><p class="chapter-label"><span>{number:02d}</span>Worksheet{chapter_minutes(chapter)}</p>'
                                f'<h2>{escape(chapter["title"])}</h2>{paragraph(chapter["summary"], "lead")}{body}{fields}</section>')
            controls = '<span>Participant handout</span><span class="save-hint">Entries are only available in this open tab. Print the filled-in version to keep it.</span>'
        else:
            roles = sorted({item["role"] for item in data["examples"]})
            options = "".join(f'<option value="{escape(role, quote=True)}">{escape(role)}</option>' for role in roles)
            chapters.append('<div class="filter"><label for="role-filter">Examples for</label><select id="role-filter">'
                            '<option value="">All roles</option>' + options + '</select><span id="example-count" aria-live="polite"></span></div>')
            for item in data["examples"]:
                chapters.append(f'<article class="example" data-role="{escape(item["role"], quote=True)}">'
                                f'<p class="kicker">{escape(item["role"])}</p>{prompt_box(item, "example")}</article>')
            controls = '<span>Copyable examples</span>'
    sources = "".join(f'<li><a href="{escape(source["url"], quote=True)}" rel="noreferrer">{escape(source["label"])}</a></li>' for source in data["sources"])
    source_block = f'<details class="sources"><summary>Sources</summary><ul>{sources}</ul></details>' if sources else ""
    return (f'<a class="skip-link" href="#content">Skip to content</a><nav class="topnav" aria-label="Control view">'
            f'<a class="wordmark" href="#content">{escape(meta["customer"])}</a><div class="controls">{controls}'
            '<button type="button" id="print">Print</button></div></nav>'
            f'<main id="content">{"".join(chapters)}</main>{overview}'
            f'<footer><span>{escape(meta["author"])} · Version {escape(meta["version"])}</span>{source_block}</footer>'
            '<p id="copy-status" role="status" aria-live="polite"></p>')


def build(args):
    require(not args.output.exists(), "Output folder already exists. Build the new version in a new folder.")
    data = json.loads(args.input.read_text(), object_pairs_hook=unique_object)
    validate(data)
    palette = palette_from(args.palette_file, args.palette)
    css = args.profile.read_text()
    require(not re.search(r"</style|@import|url\s*\(", css, re.I), "Design profile must not include embedded resources or HTML.")
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
        raise ValueError("Output folder must be an absolute path without '..'.")
    parent_fd = directory(args.output.parent, create=True)
    os.close(parent_fd)
    build_directory(args.output, {Path(name): value for name, value in outputs.items()})
    print(f"Created: {args.output}\n{palette['notice']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--palette", default="blockbrain")
    parser.add_argument("--palette-file", required=True, type=Path)
    parser.add_argument("--profile", type=Path, default=ASSETS / "profiles/house-style.css")
    parser.add_argument("--artifacts", choices=OUTPUTS, nargs="+", default=list(OUTPUTS))
    args = parser.parse_args()
    try:
        build(args)
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(2, f"Build aborted: {error}\n")


if __name__ == "__main__":
    main()
