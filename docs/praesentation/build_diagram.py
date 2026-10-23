#!/usr/bin/env python3
"""Builds the AIOS overview diagram in German and English with one shared layout.

A generator keeps both language versions geometrically identical. Only the
labels differ. Colors follow the palette of the excalidraw-diagram skill.
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Palette (excalidraw-diagram skill, references/color-palette.md)
PRIMARY = ("#3b82f6", "#1e3a5f")
SECONDARY = ("#60a5fa", "#1e3a5f")
TERTIARY = ("#93c5fd", "#1e3a5f")
START = ("#fed7aa", "#c2410c")
END = ("#a7f3d0", "#047857")
WARNING = ("#fee2e2", "#dc2626")
DECISION = ("#fef3c7", "#b45309")
AI = ("#ddd6fe", "#6d28d9")
TITLE, SUBTITLE, BODY, ON_LIGHT, ON_DARK = "#1e40af", "#3b82f6", "#64748b", "#374151", "#ffffff"
CODE_BG, CODE_TEXT = "#1e293b", "#22c55e"
LINE = "#1e3a5f"

SKILLS = {
    "de": [
        ("Alltag und Planung", ["tagesstart", "wochenplanung", "wochenreview", "aufgabenassistenz",
                                "terminvorbereitung", "terminnachbereitung", "zeiterfassung-vorbereiten",
                                "planhat-zeiterfassung"]),
        ("Inhalte und Analyse", ["recherche", "prozessanalyse", "use-case-konzept", "unterlagen",
                                 "frontend-gestaltung"]),
        ("Code", ["pr-review", "precommit-review", "review-kommentare"]),
        ("System und Aufträge", ["auftrag-vorbereiten", "prompt-berater", "skill-builder", "system-retro",
                                 "aios-audit"]),
    ],
    "en": [
        ("Daily work and planning", ["daily-briefing", "weekly-planning", "weekly-review", "task-assistant",
                                     "meeting-prep", "meeting-follow-up", "prepare-time-entries",
                                     "planhat-time-tracking"]),
        ("Content and analysis", ["research", "process-analysis", "use-case-concept",
                                  "presentation-materials", "ui-design"]),
        ("Code", ["pr-review", "precommit-review", "review-comments"]),
        ("System and briefs", ["prepare-brief", "prompt-advisor", "skill-builder", "system-retro",
                               "aios-audit"]),
    ],
}

T = {
    "de": {
        "file": "aios-uebersicht",
        "title": "AIOS: ein Regelkern, zwei Clients, 21 Skills",
        "subtitle": "Persönlicher Assistent für Claude Code und Codex. Stand 0.2.0-dev, Oktober 2026",
        "s1": "1  Quelle", "s1d": "Privates GitHub-Repository",
        "tree": [("de/", "Deutsch, führende Quelle", "Regeln, Referenzen, Vorlagen, Skills"),
                 ("en/", "English, inhaltsgleich", "eigene Datei- und Skillnamen"),
                 ("scripts/", "gemeinsam für beide Sprachen", "Einrichtung, Status, Update"),
                 ("tests/", "179 automatische Tests", "ohne echte Konten und Dienste")],
        "s2": "2  Einrichtung", "s2d": "Ein Befehl, zwei Vorschauen",
        "s2n": ["Der Installer spricht Englisch.", "Die Sprache der Regeln ist wählbar."],
        "s3": "3  Auf deinem Mac", "s3d": "Eine Sprache je Installation",
        "targets": [("Runtime", PRIMARY, ON_DARK, "~/aios-runtime/allgemein/", "Regeln, Skills, Werkzeuge"),
                    ("Profil", DECISION, ON_LIGHT, "~/aios-profile/", "pfade.json, profil.md, projekte.md"),
                    ("Claude Code", AI, ON_LIGHT, "~/.claude/CLAUDE.md", "~/.claude/skills/  21 Links"),
                    ("Codex", AI, ON_LIGHT, "~/.codex/AGENTS.md", "~/.agents/skills/  21 Links"),
                    ("Ergebnisse", END, ON_LIGHT, "~/aios-output/", "oder Projektordner laut Register")],
        "s4": "4  So läuft ein Auftrag",
        "request": "Auftrag", "core": "Regelkern", "core_d": "CLAUDE.md, AGENTS.md",
        "skill": "Skill", "skill_d": "z. B. /tagesstart", "draft": "Entwurf",
        "review": "Prüfagent", "review_d": "Befund?", "result": "Ergebnis",
        "no": "nein", "yes": "ja: korrigieren, neu prüfen",
        "rules": ["Arbeitsstand lesen: PLAN.md, NOTIZEN.md", "Nur freigegebene Quellen nutzen",
                  "Senden und Schreiben nur auf Auftrag", "Antwortsprache aus dem Profil"],
        "review_note": ["Der Prüfer ist an der Erstellung", "unbeteiligt und sieht den",
                        "vollständigen Entwurf."],
        "result_note": ["Ungeprüftes wird", "offen benannt."],
        "s5": "5  Die 21 Skills", "s5d": "Aufruf mit /name in Claude Code, $name in Codex",
        "s6": "6  Betrieb",
        "steps": [("Einrichten", "install.sh"), ("Status", "setup_status.py"),
                  ("Update", "update.py"), ("Deinstallieren", "uninstall.py")],
        "s6n": ["Immer erst Vorschau, dann Bestätigung mit yes.",
                "Profil, Ergebnisse und fremde Dateien bleiben unberührt."],
        "s7": "7  Prüfstand",
        "done": "Belegt", "done_items": ["179 automatische Tests", "Einrichtung, Update, Deinstallation",
                                         "Laden in Claude Code und Codex", "7 englische Fälle in Codex, fachlich"],
        "open": "Offen", "open_items": ["Prüfagent in Codex abnehmen", "Englische Fälle in Claude Code",
                                        "Dienste: Kalender, To Do, Jira ...", "Präsentationsrenderer visuell"],
        "skill_count": "{n} Skills",
    },
    "en": {
        "file": "aios-overview",
        "title": "AIOS: one rule core, two clients, 21 skills",
        "subtitle": "Personal assistant for Claude Code and Codex. Version 0.2.0-dev, October 2026",
        "s1": "1  Source", "s1d": "Private GitHub repository",
        "tree": [("de/", "German, authoritative source", "rules, references, templates, skills"),
                 ("en/", "English, same content", "own file and skill names"),
                 ("scripts/", "shared by both languages", "setup, status, update"),
                 ("tests/", "179 automated tests", "no real accounts or services")],
        "s2": "2  Setup", "s2d": "One command, two previews",
        "s2n": ["The installer speaks English.", "The rules language is selectable."],
        "s3": "3  On your Mac", "s3d": "One language per installation",
        "targets": [("Runtime", PRIMARY, ON_DARK, "~/aios-runtime/general/", "rules, skills, tools"),
                    ("Profile", DECISION, ON_LIGHT, "~/aios-profile/", "paths.json, profile.md, projects.md"),
                    ("Claude Code", AI, ON_LIGHT, "~/.claude/CLAUDE.md", "~/.claude/skills/  21 links"),
                    ("Codex", AI, ON_LIGHT, "~/.codex/AGENTS.md", "~/.agents/skills/  21 links"),
                    ("Output", END, ON_LIGHT, "~/aios-output/", "or project folder from the register")],
        "s4": "4  How a task runs",
        "request": "Task", "core": "Core rules", "core_d": "CLAUDE.md, AGENTS.md",
        "skill": "Skill", "skill_d": "e.g. /daily-briefing", "draft": "Draft",
        "review": "Review agent", "review_d": "Findings?", "result": "Result",
        "no": "no", "yes": "yes: fix, review again",
        "rules": ["Read working state: PLAN.md, NOTES.md", "Use approved sources only",
                  "Send and write only when tasked", "Answer language from the profile"],
        "review_note": ["The reviewer took no part", "in creating the draft and", "sees it in full."],
        "result_note": ["Anything unreviewed", "is named openly."],
        "s5": "5  The 21 skills", "s5d": "Invoke with /name in Claude Code, $name in Codex",
        "s6": "6  Operation",
        "steps": [("Set up", "install.sh"), ("Status", "setup_status.py"),
                  ("Update", "update.py"), ("Uninstall", "uninstall.py")],
        "s6n": ["Always a preview first, then confirm with yes.",
                "Profile, output and foreign files stay untouched."],
        "s7": "7  Test status",
        "done": "Evidenced", "done_items": ["179 automated tests", "Setup, update, uninstall",
                                            "Loading in Claude Code and Codex", "7 English cases in Codex, content"],
        "open": "Open", "open_items": ["Accept review agent in Codex", "English cases in Claude Code",
                                       "Services: calendar, To Do, Jira ...", "Presentation renderer, visual"],
        "skill_count": "{n} skills",
    },
}


class Canvas:
    def __init__(self):
        self.elements = []
        self.seed = 1000

    def _base(self, kind, ident, x, y, w, h, stroke, fill="transparent", width=2, style="solid"):
        self.seed += 7
        element = {"type": kind, "id": ident, "x": x, "y": y, "width": w, "height": h, "angle": 0,
                   "strokeColor": stroke, "backgroundColor": fill, "fillStyle": "solid", "strokeWidth": width,
                   "strokeStyle": style, "roughness": 0, "opacity": 100, "seed": self.seed, "version": 1,
                   "versionNonce": self.seed + 3, "isDeleted": False, "groupIds": [], "boundElements": [],
                   "link": None, "locked": False, "updated": 1, "frameId": None, "index": None}
        self.elements.append(element)
        return element

    def text(self, ident, x, y, value, size=16, color=BODY, align="left", family=3):
        lines = value.split("\n")
        w = max(len(line) for line in lines) * size * 0.6
        h = len(lines) * size * 1.25
        if align == "center":
            x -= w / 2
        element = self._base("text", ident, x, y, w, h, color, width=1)
        element.update({"text": value, "originalText": value, "fontSize": size, "fontFamily": family,
                        "textAlign": align, "verticalAlign": "top", "containerId": None, "lineHeight": 1.25,
                        "autoResize": True, "boundElements": None})
        return element

    def shape(self, kind, ident, x, y, w, h, colors, width=2, style="solid"):
        fill, stroke = colors
        element = self._base(kind, ident, x, y, w, h, stroke, fill, width, style)
        if kind == "rectangle":
            element["roundness"] = {"type": 3}
        return element

    def line(self, ident, points, color=LINE, width=2, style="solid"):
        x0, y0 = points[0]
        rel = [[px - x0, py - y0] for px, py in points]
        xs, ys = [p[0] for p in rel], [p[1] for p in rel]
        element = self._base("line", ident, x0, y0, max(xs) - min(xs), max(ys) - min(ys), color, width=width,
                             style=style)
        element.update({"points": rel, "boundElements": None, "lastCommittedPoint": None,
                        "startBinding": None, "endBinding": None, "startArrowhead": None, "endArrowhead": None})
        return element

    def arrow(self, ident, points, color, start=None, end=None, width=2):
        element = self.line(ident, points, color, width)
        element["type"] = "arrow"
        element["endArrowhead"] = "arrow"
        for key, target in (("startBinding", start), ("endBinding", end)):
            if target:
                element[key] = {"elementId": target, "focus": 0, "gap": 4}
                for other in self.elements:
                    if other["id"] == target:
                        other["boundElements"].append({"id": ident, "type": "arrow"})
        return element


def build(lang):
    t = T[lang]
    c = Canvas()
    c.text("title", 60, 40, t["title"], 34, TITLE)
    c.text("subtitle", 60, 90, t["subtitle"], 18, BODY)

    # 1 Source: folder tree without containers
    c.text("s1", 60, 150, t["s1"], 24, SUBTITLE)
    c.text("s1d", 60, 184, t["s1d"], 15, BODY)
    c.text("repo", 60, 222, "aios-neuaufbau/", 20, TITLE)
    c.line("trunk", [(74, 252), (74, 512)], LINE, 2)
    for i, (name, main, detail) in enumerate(t["tree"]):
        y = 270 + i * 66
        c.line(f"branch{i}", [(74, y + 11), (102, y + 11)], LINE, 2)
        c.text(f"tname{i}", 112, y, name, 18, TITLE)
        c.text(f"tmain{i}", 222, y + 1, main, 16, ON_LIGHT)
        c.text(f"tdet{i}", 222, y + 24, detail, 14, BODY)

    # 2 Setup: abridged installer dialog and status output, wording from setup_profile.py and setup_status.py
    c.text("s2", 640, 150, t["s2"], 24, SUBTITLE)
    c.text("s2d", 640, 184, t["s2d"], 15, BODY)
    c.shape("rectangle", "code", 640, 222, 470, 304, (CODE_BG, CODE_BG), 1)
    code = ["$ sh install.sh", "", f"Language for rules and skills (de, en) [en]: {lang}",
            "Clients (claude, codex, both) [both]: both", "Profile preview ... type yes",
            "Install preview ... type yes", "", "File integration: present.", "claude-code: present, 21 skill links ...",
            "codex: present, 21 skill links ...", "Models and services unchecked."]
    for i, line in enumerate(code):
        if line:
            color = "#f8fafc" if i == 0 else CODE_TEXT
            c.text(f"code{i}", 660, 240 + i * 25, line, 15, color)
    for i, line in enumerate(t["s2n"]):
        c.text(f"s2n{i}", 640, 540 + i * 22, line, 15, BODY)
    c.arrow("a12", [(470, 380), (632, 380)], LINE, end="code", width=3)

    # 3 On your Mac: fan-out into five targets
    c.text("s3", 1230, 150, t["s3"], 24, SUBTITLE)
    c.text("s3d", 1230, 184, t["s3d"], 15, BODY)
    for i, (name, colors, text_color, path, detail) in enumerate(t["targets"]):
        y = 222 + i * 70
        box = c.shape("rectangle", f"target{i}", 1230, y, 200, 58, colors)
        c.text(f"target{i}t", 1330, y + 18, name, 18, text_color, "center")
        c.text(f"target{i}p", 1450, y + 6, path, 15, ON_LIGHT)
        c.text(f"target{i}d", 1450, y + 30, detail, 14, BODY)
        c.arrow(f"fan{i}", [(1114, 374), (1226, y + 29)], LINE, start="code", end=box["id"])

    c.line("div1", [(60, 600), (1940, 600)], BODY, 1, "dashed")

    # 4 How a task runs: flow with review loop
    c.text("s4", 60, 630, t["s4"], 24, SUBTITLE)
    cy = 760
    c.shape("ellipse", "request", 60, cy - 50, 190, 100, START)
    c.text("requestt", 155, cy - 12, t["request"], 20, ON_LIGHT, "center")
    c.shape("rectangle", "core", 330, cy - 60, 270, 120, PRIMARY)
    c.text("coret", 465, cy - 28, t["core"], 22, ON_DARK, "center")
    c.text("cored", 465, cy + 6, t["core_d"], 14, ON_DARK, "center")
    c.shape("rectangle", "skill", 680, cy - 50, 230, 100, SECONDARY)
    c.text("skillt", 795, cy - 24, t["skill"], 20, ON_LIGHT, "center")
    c.text("skilld", 795, cy + 6, t["skill_d"], 14, ON_LIGHT, "center")
    c.shape("rectangle", "draft", 990, cy - 50, 190, 100, TERTIARY)
    c.text("draftt", 1085, cy - 12, t["draft"], 20, ON_LIGHT, "center")
    c.shape("diamond", "review", 1260, cy - 85, 240, 170, DECISION)
    c.text("reviewt", 1380, cy - 24, t["review"], 18, ON_LIGHT, "center")
    c.text("reviewd", 1380, cy + 4, t["review_d"], 16, ON_LIGHT, "center")
    c.shape("ellipse", "result", 1600, cy - 50, 210, 100, END)
    c.text("resultt", 1705, cy - 12, t["result"], 20, ON_LIGHT, "center")
    c.arrow("f1", [(254, cy), (326, cy)], START[1], "request", "core")
    c.arrow("f2", [(604, cy), (676, cy)], PRIMARY[1], "core", "skill")
    c.arrow("f3", [(914, cy), (986, cy)], SECONDARY[1], "skill", "draft")
    c.arrow("f4", [(1184, cy), (1256, cy)], TERTIARY[1], "draft", "review")
    c.arrow("f5", [(1504, cy), (1596, cy)], END[1], "review", "result")
    c.text("nolabel", 1550, cy - 30, t["no"], 15, END[1], "center")
    c.arrow("loop", [(1380, cy + 89), (1380, cy + 150), (1085, cy + 150), (1085, cy + 54)],
            DECISION[1], "review", "draft")
    c.text("yeslabel", 1100, cy + 158, t["yes"], 15, DECISION[1])
    for i, rule in enumerate(t["rules"]):
        y = cy + 84 + i * 28
        c.shape("ellipse", f"rdot{i}", 334, y + 5, 10, 10, (PRIMARY[0], PRIMARY[0]), 1)
        c.text(f"rule{i}", 354, y, rule, 15, ON_LIGHT)
    for i, line in enumerate(t["review_note"]):
        c.text(f"rnote{i}", 1460, cy + 100 + i * 22, line, 14, BODY)
    for i, line in enumerate(t["result_note"]):
        c.text(f"resnote{i}", 1640, cy - 104 + i * 22, line, 14, BODY)

    c.line("div2", [(60, 1000), (1940, 1000)], BODY, 1, "dashed")

    # 5 Skills: four groups as lists with markers
    c.text("s5", 60, 1030, t["s5"], 24, SUBTITLE)
    c.text("s5d", 60, 1064, t["s5d"], 15, BODY)
    group_colors = [START, SECONDARY, AI, END]
    for g, (group, names) in enumerate(SKILLS[lang]):
        x = 60 + g * 475
        c.text(f"g{g}", x, 1108, group, 18, TITLE)
        c.text(f"g{g}n", x, 1134, t["skill_count"].format(n=len(names)), 14, BODY)
        for i, name in enumerate(names):
            y = 1166 + i * 30
            c.shape("ellipse", f"g{g}dot{i}", x + 2, y + 5, 11, 11, (group_colors[g][1], group_colors[g][1]), 1)
            c.text(f"g{g}s{i}", x + 24, y, name, 16, ON_LIGHT)

    c.line("div3", [(60, 1420), (1940, 1420)], BODY, 1, "dashed")

    # 6 Operation: timeline
    c.text("s6", 60, 1450, t["s6"], 24, SUBTITLE)
    c.line("timeline", [(120, 1560), (840, 1560)], LINE, 3)
    for i, (label, command) in enumerate(t["steps"]):
        x = 120 + i * 240
        c.shape("ellipse", f"step{i}", x - 9, 1551, 18, 18, (PRIMARY[0], PRIMARY[0]), 1)
        c.text(f"step{i}t", x, 1514, label, 18, TITLE, "center")
        c.text(f"step{i}c", x, 1580, command, 14, BODY, "center")
    for i, line in enumerate(t["s6n"]):
        c.text(f"s6n{i}", 60, 1626 + i * 24, line, 15, ON_LIGHT)

    # 7 Test status: side by side
    c.text("s7", 1000, 1450, t["s7"], 24, SUBTITLE)
    for k, (head, items, colors) in enumerate(((t["done"], t["done_items"], END),
                                               (t["open"], t["open_items"], WARNING))):
        x = 1000 + k * 480
        c.shape("rectangle", f"status{k}", x, 1500, 450, 190, colors)
        c.text(f"status{k}h", x + 22, 1516, head, 20, colors[1])
        for i, item in enumerate(items):
            c.text(f"status{k}i{i}", x + 22, 1556 + i * 30, item, 15, ON_LIGHT)

    data = {"type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
            "elements": c.elements, "appState": {"viewBackgroundColor": "#ffffff", "gridSize": 20},
            "files": {}}
    ids = [e["id"] for e in c.elements]
    assert len(ids) == len(set(ids)), "duplicate ids"
    path = HERE / f"{t['file']}.excalidraw"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    for language in ("de", "en"):
        print(build(language))
