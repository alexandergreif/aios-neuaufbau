# Prüfung der Regelkernänderung 0.1.6-dev

Stand: 23.10.2026. Umsetzung von Entscheidung 120: Der Botticelli-Abschnitt und der Stilspiegel der alten globalen Regeln werden durch allgemeine Regeln im Kern und einen Registereintrag bei der Einrichtung ersetzt.

## Geänderte Dateien

- `allgemein/regeln/kern.md`: Repository-Regeln, die der Client nicht oder nur teilweise selbst lädt (versionierte Regeldateien beider Clients, Themenregeln, pfadgebundene Regeln, Skills und Agenten über ihre Beschreibungen, Regeln im Ordner des anderen Clients, Vorrang der versionierten Fassung, benannte lokale Ausnahmen, Ausschluss von Copilot-Anweisungen, Projektordner über das Register). Stilregel erweitert um Oberflächen-, Commit- und PR-Texte, Umbauen statt Ersetzen, Bereinigen geänderter Zeilen, Zitate ausgenommen.
- `allgemein/referenzen/ablage.md`: Geltung auch für die Zuordnung eines Projektordners.
- `allgemein/skills/pr-review/SKILL.md` und `references/prueffaelle.md`: In Botticelli ist der lokale, unversionierte `botticelli-review` unter `.claude/skills/` Hauptablauf für PRs von Kollegen, auch in Codex. Fallback `blockbrain-pr-review` mit allgemeinem Ablauf. Schreibende GitHub-Schritte nur auf Auftrag.
- `README.md` (Nachtrag zu Entscheidung 62), `docs/regelabgleich.md` (Nachträge), `docs/umstieg-haupt-macbook.md` (Registereintrag in Schritt 5).
- `scripts/paket_bauen.py` und `tests/test_paket_bauen.py`: Version 0.1.6-dev.

## Prüfrunden

Jede Runde lief mit einem neu gestarteten Prüfagenten (Opus 5.5, Denkaufwand high) mit vollständigem Diff.

| Runde | Ergebnis | Umgang |
| --- | --- | --- |
| 1 | 1 muss (Copilot-Satz hätte Codex die Botticelli-Regeln unter `.claude/` ausgeblendet), 5 sollte, 2 Hinweise | umgesetzt bis auf die Datei im Botticelli-Arbeitsordner |
| 2 | 7 Punkte bestätigt, 4 sollte (unter anderem ungültiger Registereintrag in Schritt 5), 4 Hinweise | alle umgesetzt |
| 3 | 8 Punkte bestätigt, 1 muss (Nachvollziehbarkeit von Entscheidung 120), 2 sollte, 5 Hinweise | umgesetzt. Dabei Widerspruch zu Entscheidung 62 gefunden und von Alexander entschieden |
| 4 | 1 muss (`botticelli-review` fälschlich als versioniert beschrieben), 2 sollte, 2 Hinweise | Alexander entschied für den lokalen Skill, Beschreibung und Versionsregel angepasst, beide lokalen Fassungen ins Backup |
| 5 | keine muss, 1 sollte, 4 Hinweise | alle umgesetzt |
| 6 | keine muss, 1 sollte (Wiedergabe in `docs/regelabgleich.md`), 1 Hinweis | sollte im vorgeschlagenen Wortlaut umgesetzt |

Tests nach jeder Änderung: `python3 -B -m unittest discover -s tests`, zuletzt 145 Tests OK.

## Offen

- Die letzte Formulierung in `docs/regelabgleich.md` (Zeile zu Copilot-Dateien) wurde wörtlich aus Runde 6 übernommen und nicht erneut geprüft. Die Datei gehört nicht zum Laufzeitpaket.
- Hinweis aus Runde 6: Die Ausnahmeklausel sagt nicht ausdrücklich, dass sie der Vorrangregel für versionierte Fassungen vorgeht. Das wirkt erst, wenn ein gleichnamiger Skill im Repository versioniert wird.
- Im Botticelli-Arbeitsordner sind `AGENTS.md`, `.agents/` und `.codex/` unversioniert und veraltet, teils mit nicht vorhandenen `.Codex/`-Pfaden. Nicht Teil des Pakets.
- Ob Claude Code und Codex den neuen Kern so befolgen, ist nicht mit Modellfällen erprobt.
