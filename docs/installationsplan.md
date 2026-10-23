# Installations-Vorabcheck

`scripts/install_plan.py` zeigt nur, welche lokalen Dateien und Skillverknüpfungen eine spätere Installation betreffen würde. Er installiert nichts, startet keinen Client und liest keine Kunden-, Profil- oder `.env`-Inhalte.

```sh
python3 scripts/install_plan.py --config /pfad/zur/bestaetigten/pfade.json
python3 scripts/install_plan.py --config /pfad/zur/bestaetigten/pfade.json --json
```

Für synthetische Tests lässt sich `--home` setzen. `--codex-home` und `--claude-config-dir` wählen abweichende Clientordner ausdrücklich. Ohne diese Optionen plant der Check unter `.codex` und `.claude` des gewählten Benutzerordners. Abweichende Werte von `CODEX_HOME` oder `CLAUDE_CONFIG_DIR` erscheinen als „Klärung nötig“ und führen zu Exitcode 1. Sie werden nicht automatisch übernommen.

Die bestätigte Pfadkonfiguration wird mit dem vorhandenen Pfadprüfer validiert. Der Plan zeigt die Runtime unter `paths.runtime`, den Ausgabeordner unter `paths.output` und das unangetastete Profil. Skillnamen stammen nur aus regulären Paketdateien `de/skills/<name>/SKILL.md` beziehungsweise, bei der im Profil bestätigten Sprache `en`, `en/skills/<name>/SKILL.md`. Für Claude Code werden `CLAUDE.md` und Verknüpfungen unter dessen `skills`-Ordner geplant. Für Codex werden `AGENTS.md` und Verknüpfungen unter `.agents/skills` des Benutzerordners geplant.

Der Check prüft Existenz und Dateityp der Ziele und ihrer nötigen Eltern. Vorhandene Runtime, Regeldateien, `AGENTS.override.md`, Skillnamen, Symlink-Eltern und Dateien an Ordnerstellen sind Konflikte. Doppelte geplante Ziele gelten auch bei abweichender Großschreibung oder Unicode-Schreibweise als Konflikt. Clientordner dürfen weder Systemwurzel oder Benutzerordner sein noch mit Quellcode, Runtime, Profil oder Ausgabe überlappen. Dasselbe gilt für die Codex-Skillbasis `.agents/skills`, die auch nicht mit einem Clientordner überlappen darf. Ein vorhandener Ausgabeordner ist erlaubt und wird nicht durchsucht. Vorhandene `settings.json`, `config.toml` und `.mcp.json` werden nur als „vorhanden, Inhalt und Verbindungen ungeprüft“ angezeigt. Ein konfliktfreier Plan endet mit Exitcode 0, ein Konflikt, Klärungsbedarf oder ungültige Eingabe mit Exitcode 1. Existenzprüfung ist keine Funktionsabnahme.
