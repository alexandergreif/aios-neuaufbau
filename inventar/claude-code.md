# Claude Code: installierte Plugins und lokale Skill-Namen

Stand: 18.10.2026. Read-only-Bestandsaufnahme vor der Einzelauswahl. Quelle für den Installationsstatus ist `~/.local/bin/claude plugin list --json`. Zweck und Herkunft stammen aus den `plugin.json`-Dateien der dort genannten `installPath`-Verzeichnisse. Ein Cache-Verzeichnis allein zählt hier nicht als Installation. Die CLI meldet 24 Registrierungen für 18 unterschiedliche Plugin-IDs. `enabled` beschreibt die jeweilige Registrierung, nicht eine nachgewiesene Nutzung oder funktionierende Anmeldung.

| Plugin | Registrierung laut CLI | Zweck laut Manifest | Herkunft laut Manifest |
| --- | --- | --- | --- |
| `aikido@claude-plugins-official` | Projektbezogen, 1.2.1, **deaktiviert** | Code-, Secret- und IaC-Scans, Aikido-Issues | [AikidoSec/aikido-claude-plugin](https://github.com/AikidoSec/aikido-claude-plugin) |
| `aios@aios-local` | Nutzerweit, 0.1.0, aktiv | Tagesstart, Auftragsklärung, Terminvorbereitung | Lokales AIOS-Plugin, keine externe Repository-Angabe |
| `chrome-devtools-mcp@chrome-devtools-plugins` | Nutzerweit, 1.2.0, aktiv | Chrome-Automation, Debugging, Performance | Im Manifest keine Repository-Angabe |
| `claude-md-management@claude-plugins-official` | Nutzerweit, 1.0.0, aktiv | `CLAUDE.md` prüfen und pflegen | Im Manifest keine Repository-Angabe |
| `claude-mem@thedotmack` | Nutzerweit, 10.5.2, aktiv | Sitzungsübergreifender Kontext und Erinnerung | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) |
| `context-mode@context-mode` | Nutzerweit, 1.0.151, aktiv | Kontextkomprimierung, Ausführung, FTS5-Wissensbasis, Sitzungsfortsetzung | [mksglu/context-mode](https://github.com/mksglu/context-mode) |
| `context7@claude-plugins-official` | Nutzerweit, `ea10b213686c`, aktiv | Aktuelle Bibliotheksdokumentation über Remote-MCP | Manifest nennt Upstash Context7, ohne Repository-Angabe |
| `datadog@claude-plugins-official` | Nutzerweit, 0.7.17, aktiv | Logs, Metriken, Traces und Dashboards über MCP | [datadog-labs/claude-code-plugin](https://github.com/datadog-labs/claude-code-plugin) |
| `frontend-design@claude-plugins-official` | Nutzerweit, `ea10b213686c`, aktiv | UI- und UX-Implementierung | Im Manifest keine Repository-Angabe |
| `github@claude-plugins-official` | Nutzerweit, `ea10b213686c`, aktiv | GitHub-Repositories, Issues und Pull Requests über MCP | Im Manifest als offizieller GitHub-MCP bezeichnet, ohne Repository-Angabe |
| `playwright@claude-plugins-official` | Nutzerweit, `ea10b213686c`, aktiv | Browserautomation und End-to-End-Tests | Manifest nennt Microsoft, ohne Repository-Angabe |
| `sentry@claude-plugins-official` | Nutzerweit 1.4.0, aktiv. Zusätzlich drei aktive Projektregistrierungen: 1.0.0 in einem Projekt, 1.4.0 in zwei weiteren. | Fehleranalyse über MCP und Skills | [getsentry/plugin-claude](https://github.com/getsentry/plugin-claude) für 1.4.0, [getsentry/sentry-for-ai](https://github.com/getsentry/sentry-for-ai) für 1.0.0 |
| `skill-creator@claude-plugins-official` | Nutzerweit, `ea10b213686c`, aktiv | Skills erstellen, verbessern und testen | Im Manifest keine Repository-Angabe |
| `superpowers@claude-plugins-official` | Nutzerweit 7.0.0, aktiv. Zusätzlich drei aktive Projektregistrierungen: 6.1.1 in einem Projekt, 6.4.1 in zwei weiteren. | Entwicklungsabläufe wie TDD und Debugging | [obra/superpowers](https://github.com/obra/superpowers) |
| `engineering@synced` | Synchronisiert, 1.2.0, aktiv | Standups, Reviews, Architektur, Vorfälle und technische Dokumentation | Keine Repository-Angabe |
| `productivity@synced` | Synchronisiert, 1.3.1, aktiv | Aufgaben, Tagesplanung und Arbeitskontext | Keine Repository-Angabe |
| `cowork-plugin-management@synced` | Synchronisiert, 0.2.2, aktiv | Plugins und MCP-Konfiguration verwalten | Keine Repository-Angabe |
| `enterprise-search@synced` | Synchronisiert, 1.3.0, aktiv | Suche über E-Mail, Chats, Dokumente und Wikis | Keine Repository-Angabe |

Alle projektbezogenen Einträge beziehen sich auf andere Arbeitsverzeichnisse. Die CLI gibt dafür `projectEnabled: false` aus. Daraus folgt keine Aktivierung im aktuellen AIOS-Neuaufbau. Die nutzerweiten und synchronisierten Einträge sind laut CLI aktiviert. Die Kennung `ea10b213686c` ist die von der CLI ausgegebene Versionskennung, keine hier geprüfte semantische Version. Bei `aios@aios-local` zeigt die CLI zusätzlich auf eine lokale Runtime-Version 0.1.0. Diese bestehende Installation ist Bestandskontext und kein Drittanbieter-Kandidat.

## Namen unter `~/.claude/skills`

40 sichtbare Einträge auf oberster Ebene, ohne den versteckten Ordner `.trash`. Die 19 Verknüpfungen zum bestehenden Agentic-OS-Arbeitsbaum heißen: `agentic-workflow-bauen`, `aios-assistent`, `aios-audit`, `aios-ishikawa-prozessanalyse`, `aios-retro`, `aios-skill-builder`, `aios-wochenreview`, `auftrag`, `blockbrain-slides`, `goal-vorbereiten`, `gpt-prompting`, `kundenunterlage`, `lernvideo`, `planhat-timetracking`, `planhat-wochenabschluss`, `tagesstart`, `terminvorbereitung`, `use-case-konzept`, `zeiterfassung-vorbereiten`.

Die 21 übrigen Einträge sind lokale Verzeichnisse oder einzelne Markdown-Dateien: `brauerei-bild.md`, `brauerei-video.md`, `external-pr-review`, `fable-mode`, `fable-prompting`, `faceless-explainer`, `general-video`, `humanizer`, `hyperframes`, `hyperframes-animation`, `hyperframes-audio`, `hyperframes-cli`, `hyperframes-core`, `hyperframes-creative`, `hyperframes-keyframes`, `hyperframes-registry`, `hyperframes-studio`, `mcp-builder.md`, `media-use`, `repo-recon.md`, `synced`. Der Eintrag `synced` wurde nur als Name erfasst. Diese Liste belegt Dateien im Skill-Ordner, nicht deren tatsächliche Auslösung oder Kompatibilität. Plugin-interne Skills sind in der Plugin-Tabelle erfasst und hier nicht nochmals aufgezählt.

## Überschneidungen und Auswahlfragen

- `claude-mem`, `context-mode`, `productivity@synced` und `enterprise-search@synced` berühren Kontext, Erinnerung oder Suche. Das kann sich mit dem geplanten AIOS-Wissensbereich überschneiden. Die unterschiedlichen Datenquellen und Laufzeitfolgen sind noch nicht geprüft.
- `chrome-devtools-mcp` und `playwright` decken beide Browserarbeit ab, mit verschiedenem Schwerpunkt laut Manifest. `github`, `sentry`, `datadog` und `context7` sind eigenständige Integrationen. Eine aktive Registrierung belegt weder Zugang noch Bedarf.
- `skill-creator`, `cowork-plugin-management`, `claude-md-management`, `engineering@synced` und `superpowers` können sich mit AIOS-Regeln, Skill-Pflege und Entwicklungsabläufen überschneiden. Projektregistrierungen älterer Superpowers-Versionen sollten bei einer späteren Übernahme getrennt betrachtet werden.
- Zum bereits ausgewählten **Humanizer** ist keine harte Plugin-Abhängigkeit belegt. Für **Slides** (`blockbrain-slides`) und **Video** (`lernvideo`, `hyperframes` und verwandte Skills) zeigen die gelesenen Plugin-Manifeste ebenfalls keine harte Abhängigkeit. `frontend-design` kann gestalterisch angrenzen. Für **Dokumente** könnten `claude-md-management`, `engineering@synced` und `enterprise-search@synced` ergänzen, doch ihre Notwendigkeit für den ausgewählten Dokumentbereich ist nicht belegt.

Offen bleiben tatsächliche Nutzung, Anmeldung, Laufzeitverhalten, Versionenkonflikte und Kompatibilität auf einem zweiten Mac. Diese Bestandsaufnahme enthält keine Installations- oder Übernahmeentscheidung.
