# Native Skill-Ladung

Stand: 19.10.2026. Die fünf ersten Skills wurden in beiden lokal vorhandenen Clients bis zum fertig zusammengestellten API-Request geprüft. Es gab keine Anbieteraufrufe oder Modellantworten.

```sh
python3 scripts/check_skill_loader.py
```

Optional wählen `--codex` und `--claude` die konkreten ausführbaren Dateien. `--evidence-dir /absoluter/neuer/ordner` speichert die technischen Ergebnisse samt Quellhashes und vollständigen Vorher-/Nachher-Listen der aktiven Skill-Verknüpfungen. Das Werkzeug ist für die lokale macOS-Entwicklung gedacht, nicht Teil der späteren Einrichtung auf jedem Rechner.

Die Probe kopiert ausschließlich die eigenen Paket-Skills in einen temporären Arbeitsordner. Innerhalb dieses Ordners werden `.claude/skills` und `.agents/skills` angebunden. Persönliche Einstellungen, Anmeldungen und bestehende Skillinhalte bleiben ausgeschlossen. Es gilt die [Betriebssystem-Isolation der Regelladung](client-loader.md).

| Prüfung | Codex 0.162.1 | Claude Code 2.1.300 |
| --- | --- | --- |
| Vier reguläre Skills in den angebotenen Metadaten | Bestanden | Bestanden |
| Auftragshelfer nicht automatisch angeboten | Bestanden | Bestanden |
| Alle fünf Skills explizit vollständig geladen | Bestanden | Bestanden |
| Lokaler kontrollierter API-Fehler sichtbar | Bestanden | Bestanden |
| Aktive Skill-Verknüpfungen unverändert | Bestanden | Bestanden |

Codex `debug prompt-input` zeigt die automatische Skillauswahl, expandiert einen expliziten `$skill`-Aufruf aber nicht. Dafür verwendet die Probe `codex exec` mit einem ausschließlich lokalen Testprovider ohne Authentifizierung. Dessen HTTP-400-Antwort beendet den Aufruf. Providerparameter werden nur über Prozessargumente gesetzt, keine aktive Konfigurationsdatei wird geändert. [Offizielle Codex-Konfiguration](https://learn.chatgpt.com/docs/config-file/config-reference).

Claude benötigt für die Anzeige regulärer Skills das eingebaute Skill-Werkzeug. Die Probe bietet ausschließlich dieses Werkzeug an. Der lokale Server liefert keine Modellantwort und daher keine Tool-Aufrufe. Explizite `/skill`-Aufrufe werden vom Client vor der Anfrage expandiert. Die beiden expliziten Aufrufregeln des Auftragshelfers bleiben getrennt: `disable-model-invocation` für Claude und `allow_implicit_invocation` in Codex-Metadaten. [Claude-Skills](https://code.claude.com/docs/en/skills), [Codex-Skills](https://learn.chatgpt.com/docs/build-skills).

Der mitgelieferte Codex-Formatvalidator kennt das Claude-Feld noch nicht. Er wurde für den Auftragshelfer auf einer temporären Kopie ohne dieses eine Feld ausgeführt. Das tatsächliche gemeinsame Frontmatter wurde in beiden Clients geladen. Die übrigen vier Skills bestehen den Formatvalidator unverändert.

Die unabhängige [Skillprüfung](../pruefungen/erste-skills-review.md) ergänzt diesen technischen Nachweis mit 17 synthetischen Anwendungsfällen. Sie ersetzt ebenfalls keine native Modell-Verhaltensprüfung oder Prüfung einer Dienstverbindung.
