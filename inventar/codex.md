# Codex: lokale Zusatzwerkzeuge

Stand: 18.10.2026. Nur lesende Bestandsaufnahme für die spätere Einzelauswahl. Quelle für den Registrierungsstatus: `codex plugin list --json`. Zweckangaben stammen aus lokalen Pluginmanifesten und Skill-Metadaten. Keine Funktionsprüfung, Installation, Entfernung oder Konfigurationsänderung.

Die CLI meldet **29 installierte und aktivierte Plugins**, **keine deaktivierten** und unter `available` **keine weiteren Einträge**. Davon stammen 11 aus externen Projekten, eines aus der bestehenden lokalen AIOS-Laufzeit und 17 aus OpenAI-Marketplaces. `available: []` beschreibt nur diese CLI-Ausgabe, nicht den gesamten Pluginkatalog. Ein Ordner unter `~/.codex/plugins/cache/` belegt für sich allein keine aktive Registrierung.

## Externe Plugins, derzeit aktiviert

| Plugin und Version | Herkunft laut CLI | Zweck laut lokalem Manifest | Hinweis für Einzelauswahl |
| --- | --- | --- | --- |
| `claude-mem` 13.26.0 | `claude-mem-local`, GitHub `thedotmack/claude-mem` | Sitzungsübergreifendes Gedächtnis und Kontextverdichtung | Mit `context-mode` und dem AIOS-Wissensbereich in der Zuständigkeit abgleichen. |
| `claude-md-management` 1.0.0 | `claude-plugins-official`, GitHub `anthropics/claude-plugins-official` | Pflege und Prüfung von `CLAUDE.md` | Überschneidung mit eigenen Regel- und Dokumentationsabläufen prüfen. |
| `context7` `local` | `claude-plugins-official`, Anbieter Upstash | Aktuelle Bibliotheksdokumentation über gehosteten MCP-Dienst | Externer Dienst und gegebenenfalls Authentifizierung laut Manifest. |
| `datadog` 0.7.17 | `claude-plugins-official`, GitHub `datadog-labs/claude-code-plugin` | Abfrage von Logs, Metriken und Traces | Nur bei tatsächlichem Datadog-Bedarf bewerten. |
| `frontend-design` `local` | `claude-plugins-official`, Anthropic | Anleitung für Frontendgestaltung | Fähigkeitsüberschneidung mit eigenen Design-Skills prüfen. |
| `github` `local` | `claude-plugins-official`, Anbieter GitHub | GitHub-MCP für Repositories, Issues und PRs | Gleichnamiges OpenAI-Plugin ist ebenfalls aktiviert. |
| `playwright` `local` | `claude-plugins-official`, Anbieter Microsoft | Browsersteuerung und End-to-End-Tests per MCP | Mit den vorhandenen OpenAI-Browserwerkzeugen abgleichen. |
| `sentry` 1.4.0 | `claude-plugins-official`, GitHub `getsentry/plugin-claude` | Sentry-MCP und Debugging-Skills | Nur bei tatsächlichem Sentry-Bedarf bewerten. |
| `skill-creator` `local` | `claude-plugins-official`, Anthropic | Skills erstellen, verbessern und auswerten | Gleichnamiger Codex-Systemskill ist zusätzlich vorhanden. |
| `superpowers` 7.0.0 | `claude-plugins-official`, GitHub `obra/superpowers` | Entwicklungsabläufe für Planung, Tests, Debugging und Zusammenarbeit | Überschneidung mit eigenen Arbeitsregeln und Review-Abläufen prüfen. |
| `context-mode` 1.0.169 | `context-mode`, GitHub `mksglu/context-mode` | Kontextverdichtung, Sitzungsfortsetzung und lokale Wissenssuche | Zuständigkeit neben `claude-mem` und AIOS-Wissen klären. |

Die Herkunftsspalte nennt Marketplace und, soweit in der CLI ausgewiesen, Ursprungsprojekt. Bei Einträgen mit Version `local` liefert die CLI keine numerische Version. Die Tabelle zeigt Registrierung, keine nachgewiesene aktuelle Verwendung oder Kompatibilität der angebotenen Funktionen im laufenden Client.

## Lokales AIOS und OpenAI-Plugins

| Gruppe | Registrierte und aktivierte Plugins | Einordnung |
| --- | --- | --- |
| Lokales AIOS | `aios` 0.1.0 | Aus `~/aios-runtime/releases/0.1.0/aios`. Bestehende Laufzeit, kein fremdes Plugin und keine Entscheidung für den Neuaufbau. |
| OpenAI Primary Runtime | `documents`, `pdf`, `spreadsheets`, `presentations`, `template-creator`, jeweils 26.1007.11041 | Fünf aktivierte Laufzeitplugins. |
| OpenAI Bundled | `codex-app-tools` 0.1.6, `browser` 26.1007.21159, `unified-computer-use` 26.1007.21159, `computer-use` 1.0.1001425, `code-review` 26.1007.21159, `visualize` 1.0.49 | Sechs aktivierte gebündelte Plugins. |
| OpenAI Curated Remote | `github` 0.1.12-5f7cd798dc99, `openai-templates` 0.1.6, `pages` 0.1.23, `sites` 1.0.1, `plugin-management` 0.1.0, `work-pets` 0.1.6 | Sechs aktivierte Remote-Plugins. `github` überschneidet sich dem Namen und Zweck nach mit dem GitHub-MCP oben. |

## Direkt unter `~/.codex/skills`

`precommit-review` liegt als eigener Skill unter `~/.codex/skills/precommit-review/SKILL.md`. Unter `~/.codex/skills/.system/` liegen die mit Codex bereitgestellten Einträge `review-agent`, `skill-creator`, `skill-installer`, `openai-docs` und `imagegen`. Bei der Sichtung bis Tiefe zwei fanden sich dort keine Skill-Symlinks. Diese Verzeichnisbeobachtung ist von der Pluginregistrierung getrennt. Gemeinsame Skills unter `~/.agents/skills` werden im übergreifenden Inventar erfasst.

## Abgrenzung

Die Sichtung las nur CLI-Status und unkritische Metadaten in Pluginmanifesten. Staging-, Backup- und Cache-Verzeichnisse wurden nicht als zusätzliche Installationen gezählt. Konkrete Nutzung, Authentifizierungsstatus, Laufzeitverhalten, Kosten und technische Abhängigkeiten sind damit nicht nachgewiesen. Für die spätere Auswahl sind insbesondere die doppelten GitHub-Werkzeuge, Browserzugänge, Skill-Erstellung und die drei möglichen Wissens- oder Gedächtnisbereiche einzeln zu prüfen. Aus thematischer Überschneidung folgt keine harte technische Abhängigkeit.
