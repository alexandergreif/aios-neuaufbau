# Inventur des alten AIOS auf dem Haupt-MacBook

Stand: 22.10.2026. Schritte 1 und 2 aus [docs/umstieg-haupt-macbook.md](../../docs/umstieg-haupt-macbook.md). Rein lesend erhoben: Es wurde nichts verschoben, gesichert, installiert oder an Clients, MCP-Servern, Plugins oder Anmeldungen verändert.

Nicht gelesen: Inhalte von `~/aios/.env`, `~/.config/aios/secrets.env`, `~/.codex/auth.json`, Werte in `env`-Blöcken und Headern, Inhalte aus `~/aios/archives/`, `~/aios/output/`, `~/aios/context/` und Kundenordnern. Erfasst sind dort nur Namen, Anzahl, Größe und Rechte.

Einordnung:

- **AIOS-eigen:** gehört zum alten AIOS oder zu seinem Regelkern und wird vom neuen Paket abgelöst oder muss gesichert werden.
- **Fremd:** eigenständige Werkzeuge, Plugins oder Skills Dritter oder persönliche Werkzeuge außerhalb des AIOS. Bleiben unverändert.
- **Dienstanbindung:** MCP-Server, Connector oder Anmeldung. Bleibt unverändert.

## Schritt 1: Quelle und Tests

| Punkt | Ergebnis |
| --- | --- |
| Quelle | `~/aios-neuaufbau`, Branch `main`, Arbeitsbaum sauber |
| Commit | `8c2838a00bc19d7a013238d9e2d27a03b54f24ec` |
| Python | 3.13.16 |
| Tests | `python3 -m unittest discover -s tests`: 145 Tests in 17,5 s, `OK`, keine Fehler. Keine Testordner im Home oder Repository zurückgeblieben |

## Wichtige Befunde vorab

1. **`~/aios` ist ein Symlink** auf `~/PycharmProjects/CodingChallanges/Agentic OS/aios`, also in das Git-Repository `theblockbrain/agentic-os`. Das Repository hat 7 lokale, nicht gepushte Commits auf `main` und 9 nicht committete Einträge (unter anderem `.aios/PLAN.md`, `.aios/NOTIZEN.md`, `aios/context`, `aios/knowledge`). Dazu kommen große von Git ignorierte Bestände außerhalb von `aios/`: `.aios-knowledge/` (26 MB, `700`), `.aios-knowledge-backups/` (20 MB, `700`), `output/` (226 MB), `runtimes/blockbrain/.local/` (13 MB, `700`, möglicherweise Zugangsdaten), `mcp/knowledge/dist/` (Startdatei des MCP-Servers `aios-knowledge`) und weitere. Ein Git-Bundle erfasst diese nicht. Das Backup muss das ganze Repository als Dateikopie sichern.
2. **`~/aios-runtime` ist schon belegt**, und zwar von der alten portablen Runtime 0.1.0 (Plugin `aios@aios-local` mit `auftrag`, `tagesstart`, `terminvorbereitung`). Der neue Installer verlangt für die Runtime einen nicht vorhandenen Pfad (`scripts/installationsplan.py`, Prüfung `absent`). Mit dem Standardpfad stoppt die Installation.
3. **Das alte Plugin `aios@aios-local` ist in beiden Clients aktiv.** Marktplatzquelle ist `~/aios-runtime`. Beide Clients halten zusätzlich eine eigene, mit der Runtime inhaltsgleiche Kopie im Plugin-Cache (`~/.claude/plugins/cache/aios-local/aios/0.1.0`, `~/.codex/plugins/cache/aios-local/aios/0.1.0`). Claude trägt diese Cache-Kopie als `installPath` ein. Wahrscheinlich lädt das Plugin nach dem Verschieben der Runtime also weiter aus dem Cache, nur die Marktplatzquelle fehlt dann. Nicht geprüft. Das Plugin abzuschalten wäre eine Plugin-Änderung und braucht eine eigene Entscheidung.
4. **`~/.codex/skills/precommit-review`** heißt genauso wie der neue Skill `precommit-review`. Der Installer schreibt Codex-Skills nach `~/.agents/skills` und blockiert deshalb nicht. Codex sähe danach aber zwei Skills mit demselben Namen.
5. **`~/aios/.env` hat die Rechte `644`** (für andere Benutzer lesbar). Inhalt nicht gelesen. Im Backup auf `600` beziehungsweise Ordner `700` achten.
6. **Der neue Regelkern enthält den Botticelli-Abschnitt und die Einbindung der Botticelli-Stilquelle nicht.** Beides steht heute in der generierten `~/.claude/CLAUDE.md` und `~/.codex/AGENTS.md`. Vor Schritt 5 klären, ob und wohin er übernommen wird.

## Globale Regeldateien

| Pfad | Befund | Einordnung |
| --- | --- | --- |
| `~/.claude/CLAUDE.md` | Datei heißt auf der Platte `Claude.md` (macOS unterscheidet keine Groß- und Kleinschreibung, gleiche Datei). 102 Zeilen, `600`, Stand 04.10.2026, generiert aus `~/.agent-rules` (Kopfzeile „Nicht hier bearbeiten“). Abschnitte: Arbeitsregeln, Modellwahl, Stilspiegel aus Botticelli, Botticelli-Startcheck, AIOS-Aufträge | AIOS-eigen (alter Regelkern), **Konflikt für den Installer** |
| `~/.codex/AGENTS.md` | 102 Zeilen, `600`, Stand 04.10.2026, gleiche Abschnitte, ebenfalls generiert | AIOS-eigen (alter Regelkern), **Konflikt für den Installer** |
| `~/.codex/AGENTS.override.md` | nicht vorhanden | kein Konflikt |
| `~/.agents/AGENTS.md` | nicht vorhanden | kein Konflikt |
| `~/.agent-rules/` | Quellen `common.md`, `claude.md`, `codex.md`, `aios.md`, `modellwahl.md`, `README.md`, `sources.json` (externe Stilquelle Botticelli), `state.json`, `sync.py`, `test_sync.py`, `.sync.lock`, `__pycache__/`, `backups/` mit 7 Sicherungsständen und 2 Einzelsicherungen (darunter eine Codex-Konfigurationskopie, Inhalt nicht gelesen) | AIOS-eigen (alter Regelkern). Blockiert den Installer nicht |

## Skills in den Clientordnern

`~/.agents/skills` wird von Codex geladen, `~/.claude/skills` von Claude Code. Beide enthalten dieselben 19 AIOS-Symlinks auf `~/PycharmProjects/CodingChallanges/Agentic OS/skills/<name>`. Alle Links sind gültig.

### Alte AIOS-Skills (Symlinks, in beiden Ordnern)

| Skill | Neues Gegenstück | Konflikt (gleicher Name) |
| --- | --- | --- |
| `aios-audit` | `aios-audit` | **ja** |
| `tagesstart` | `tagesstart` | **ja** |
| `terminvorbereitung` | `terminvorbereitung` | **ja** |
| `use-case-konzept` | `use-case-konzept` | **ja** |
| `zeiterfassung-vorbereiten` | `zeiterfassung-vorbereiten` | **ja** |
| `auftrag` | `auftrag-vorbereiten` (95b) | nein |
| `goal-vorbereiten` | `auftrag-vorbereiten` (95b) | nein |
| `gpt-prompting` | `prompt-berater` (96a) | nein |
| `aios-assistent` | `aufgabenassistenz` (101), `terminnachbereitung` (100), Planungsteil (102a) | nein |
| `aios-wochenreview` | `wochenreview` (103) | nein |
| `aios-retro` | `system-retro` (104) | nein |
| `aios-ishikawa-prozessanalyse` | `prozessanalyse` (106) | nein |
| `kundenunterlage` | `unterlagen` (107) | nein |
| `aios-skill-builder` | `skill-builder` (112) | nein |
| `planhat-timetracking` | `planhat-zeiterfassung` (110a) | nein |
| `planhat-wochenabschluss` | `planhat-zeiterfassung` (110a) | nein |
| `blockbrain-slides` | keins (108 noch offen) | nein, bleibt stehen |
| `lernvideo` | keins (46 noch offen) | nein, bleibt stehen |
| `agentic-workflow-bauen` | keins (Entscheidung 47: zurückgestellt) | nein, bleibt stehen |

Die Zuordnung der Gegenstücke folgt `uebernahmeliste.md` und README. Sie ist fachlich, nicht namensgleich, und kein Beleg für gleichen Funktionsumfang.

### Weitere Einträge in `~/.agents/skills` und `~/.claude/skills`

| Eintrag | Ort | Herkunft | Einordnung |
| --- | --- | --- | --- |
| `hyperframes`, `hyperframes-animation`, `-audio`, `-cli`, `-core`, `-creative`, `-keyframes`, `-registry`, `-studio`, `media-use`, `faceless-explainer`, `general-video` (12) | beide, inhaltsgleich | `heygen-com/hyperframes` laut `~/.agents/.skill-lock.json` | fremd (von `lernvideo` genutzt) |
| `microsoft-foundry` | nur `~/.agents/skills` | `microsoft/azure-skills` laut Lock-Datei | fremd |
| `humanizer`, `fable-prompting` | beide, inhaltsgleich | eigene Ordner, nicht in der Lock-Datei | fremd (persönlich, in Übernahmeliste als Quelle 9 und 96a genannt) |
| `external-pr-review`, `fable-mode` | beide, Fassungen weichen ab | eigene Ordner | fremd (persönlich). `external-pr-review` ist Quelle für das neue `pr-review` (62), kein Namenskonflikt |
| `source-command-distill` | nur `~/.agents/skills` | eigener Ordner | fremd |
| `synced/<id>/` | beide | Skill-Synchronisierung aus claude.ai: `brand-guidelines`, `deepresearch`, `doc-coauthoring`, `docs`, `docx`, `humanizer`, `import-memory`, `mcp-builder`, `morning`, `pdf`, `pptx`, `skill-creator`, `xlsx`, in `~/.claude` zusätzlich `google-workspace` | fremd (Dienst claude.ai) |
| `brauerei-bild.md`, `brauerei-video.md`, `mcp-builder.md`, `repo-recon.md` | nur `~/.claude/skills`, lose Dateien | keine Skillordner, werden nicht als Skill geladen | fremd |
| `.trash/` | beide | Papierkorb des Skill-Installers mit entfernten synchronisierten Skills. Dazu `planhat-timetracking.vor-aios-20260927-planhat` und `planhat-wochenabschluss.vor-aios-20260927-planhat`, Sicherungen aus einer früheren AIOS-Umstellung | Papierkorb fremd, die beiden Planhat-Sicherungen AIOS-eigen. Nicht anfassen |

### `~/.codex/skills`

| Eintrag | Befund | Einordnung |
| --- | --- | --- |
| `precommit-review` | eigener Ordner vom 07.09.2026, Quelle 63 der Übernahmeliste | AIOS-nah (persönlich), **Namensgleichheit mit neuem Skill**, siehe Befund 4 |
| `.system/` | `imagegen`, `openai-docs`, `review-agent`, `skill-creator`, `skill-installer` | fremd (Codex-Systemskills) |

### Skills in Plugin-Ordnern

| Plugin | Skills | Einordnung |
| --- | --- | --- |
| `aios@aios-local` 0.1.0 (Claude und Codex, Quelle `~/aios-runtime`, je eine Cache-Kopie pro Client) | `auftrag`, `tagesstart`, `terminvorbereitung` | AIOS-eigen. Als `aios:tagesstart` und `aios:terminvorbereitung` namensgleich, aber mit Präfix. Funktionale Dopplung nach der Neuinstallation |
| `superpowers` 7.0.0 (Nutzer) sowie 6.1.1, 6.4.1 und 7.0.0 (Projekt) | 14 bis 15 Prozessskills | fremd |
| `chrome-devtools-mcp` 1.2.0 | 6 Skills | fremd |
| `claude-md-management`, `frontend-design`, `skill-creator`, `context7`, `github`, `playwright` | je 0 bis 1 Skill | fremd |
| `datadog` 0.7.17 | 5 Skills | fremd |
| `sentry` 1.4.0 (Nutzer) sowie 1.0.0 und zweimal 1.4.0 (Projekt) | 8 beziehungsweise 30 Skills | fremd |
| `context-mode` 1.0.151 | 6 Skills | fremd |
| `claude-mem` 10.5.2 | 4 Skills | fremd |
| `aikido` 1.2.1 (Projekt, deaktiviert) | 3 Skills | fremd |
| claude.ai-Plugins `engineering`, `productivity`, `cowork-plugin-management`, `enterprise-search` | 10, 4, 2, 5 Skills | fremd (Dienst claude.ai) |

Der Claude-Plugin-Cache enthält für `frontend-design`, `skill-creator`, `context7`, `github` und `playwright` je 16 Fassungen (eine aktuelle, 15 alte). Fremd, nicht anfassen.

## Abgleich der Skillnamen mit `allgemein/skills/`

Neues Paket: 21 Skills. Zielorte des Installers: `~/.claude/skills/<name>` und `~/.agents/skills/<name>` (`scripts/paketbestand.py`).

| Ergebnis | Skills |
| --- | --- |
| **Konflikte, blockieren den Installer** (in beiden Zielordnern als alter AIOS-Symlink) | `aios-audit`, `tagesstart`, `terminvorbereitung`, `use-case-konzept`, `zeiterfassung-vorbereiten` |
| **Namensgleich außerhalb der Zielordner**, blockiert nicht | `precommit-review` in `~/.codex/skills`, `tagesstart` und `terminvorbereitung` im Plugin `aios@aios-local` (Runtime und beide Cache-Kopien) |
| **Alte Skills ohne gleichnamiges neues Gegenstück** (bleiben stehen) | `agentic-workflow-bauen`, `aios-assistent`, `aios-ishikawa-prozessanalyse`, `aios-retro`, `aios-skill-builder`, `aios-wochenreview`, `auftrag`, `blockbrain-slides`, `goal-vorbereiten`, `gpt-prompting`, `kundenunterlage`, `lernvideo`, `planhat-timetracking`, `planhat-wochenabschluss` |
| **Neue Skills ohne gleichnamigen Altbestand** | `aufgabenassistenz`, `auftrag-vorbereiten`, `frontend-gestaltung`, `planhat-zeiterfassung`, `pr-review`, `prompt-berater`, `prozessanalyse`, `recherche`, `review-kommentare`, `skill-builder`, `system-retro`, `terminnachbereitung`, `unterlagen`, `wochenplanung`, `wochenreview` |

Kein fremder Skill (HyperFrames, Microsoft, persönliche Ordner, synchronisierte claude.ai-Skills) trägt einen Namen aus dem neuen Paket.

Hinweis: Elf alte Skills ohne Namensgleichheit haben einen fachlichen Nachfolger im neuen Paket. Bleiben beide stehen, sehen die Clients zwei Skills für dieselbe Aufgabe (zum Beispiel `aios-retro` und `system-retro`). Das blockiert die Installation nicht, kann aber die Skillauswahl der Modelle stören.

## Alter AIOS-Ordner `~/aios/`

Symlink auf `~/PycharmProjects/CodingChallanges/Agentic OS/aios` (Befund 1). Nur Namen und Umfang erfasst.

| Eintrag | Befund | Git | Einordnung |
| --- | --- | --- | --- |
| `context/` | 10 Dateien: `about-business.md`, `about-me.md`, `arbeitsweise.md`, `assistenzregeln.md`, `konzepte.md`, `kunden-pfade.md`, `ladeplan.md`, `priorities.md`, `projektablage.md`, `schulungen.md` | versioniert, 2 lokale Änderungen | AIOS-eigen (Profil und Kontext, teils Kundenwissen) |
| `references/` | 11 Dateien, darunter `arbeitsdateien.md`, `wochenreview.md`, `modellreview.md`, `slack-suche.md` | versioniert | AIOS-eigen |
| `vorlagen/` | `PLAN.md`, `NOTIZEN.md` | versioniert | AIOS-eigen |
| `decisions/`, `knowledge/`, `learning/` | 1, 3 und 2 Dateien (`learning/coach.json`, `retro.json`) | `decisions/` versioniert, `knowledge/` teils versioniert, `learning/` ignoriert | AIOS-eigen |
| `ZIEL.md`, `connections.md` | Ziel und Verbindungsübersicht | versioniert | AIOS-eigen |
| `archives/` | 264 Dateien, 12 MB. Unterordner: `aktionen`, `audits`, `briefings`, `coach`, `entwuerfe`, `konzepte`, `retros`, `reviews`, `schulungen`, `skill-tests`, `termine`, `zeiterfassung` | nur 4 Dateien versioniert | AIOS-eigen (Ergebnisse, enthalten Kundenbezug) |
| `output/` | 69 Dateien, 8 MB | ignoriert | AIOS-eigen (Ergebnisse) |
| `.env` | 68 Byte, Rechte `644` | ignoriert | AIOS-eigen, Zugangsdaten (Befund 5) |
| `.playwright-mcp/` | 232 Einträge, 6,4 MB | ignoriert | Arbeitsrest eines Browserwerkzeugs, fremd |
| `.aios-captures/`, `.superpowers/` | leer | | Arbeitsrest |

### Weitere AIOS-Orte außerhalb von `~/aios/`

| Pfad | Befund | Einordnung |
| --- | --- | --- |
| `~/PycharmProjects/CodingChallanges/Agentic OS/` | Quell-Repository des alten AIOS, 19 Skills, `mcp/knowledge` (Server `aios-knowledge`), Skripte. 7 lokale Commits, 9 offene Änderungen, dazu ignorierte Bestände: `.aios-knowledge/`, `.aios-knowledge-backups/`, `output/`, `runtimes/blockbrain/.local/`, `mcp/knowledge/dist/` und `node_modules/`, `skills/planhat-timetracking/mapping.local.md`, `refs/`, `docs/refs/`, `docs/archiv/`, `.project-archive/`, `.aios-review/` (Befund 1) | AIOS-eigen. Bleibt am Ort, wird von den Symlinks und von `aios-knowledge` benutzt |
| `~/aios-runtime/` | Runtime 0.1.0 vom 18.10.2026, 15 Dateien, Plugin-Marktplatz für Claude und Codex | AIOS-eigen, **Konflikt mit dem Standardpfad der neuen Runtime** (Befund 2) |
| `~/aios-output/` | 2091 Dateien, Unterordner aus früheren Abnahmen und dem Neuaufbau (`abnahme`, `aios-neuaufbau`, `installation`, `portable` und weitere). Zusätzlich T3-Projekt | AIOS-eigen. Neuer Installer akzeptiert einen vorhandenen Ausgabeordner und behält den Inhalt |
| `~/aios-profile/` | nicht vorhanden | kein Konflikt |
| `~/.claude/projects/-Users-alexandergreif-PycharmProjects-CodingChallanges-Agentic-OS/memory/` | 11 Dateien, Claude-Projektgedächtnis zum alten AIOS-Repository | AIOS-eigen. Blockiert nicht |
| `~/.config/aios/secrets.env` | Ordner `700`, Datei nicht gelesen. Wird vom MCP-Server `aios-knowledge` als Argument benutzt | AIOS-eigen, Zugangsdaten. Nicht verschieben, sonst fällt `aios-knowledge` aus |

## Hooks und Einstellungen

### `~/.claude/settings.json` (keine `settings.local.json`)

| Punkt | Befund | Einordnung |
| --- | --- | --- |
| Hooks `Stop`, `SubagentStop`, `Notification` | `afplay` mit Tondateien unter `~/Documents/hooks/` | fremd (persönlich) |
| Hook `SessionStart` | `~/.claude/hooks/context-mode-cache-heal.mjs` | fremd (context-mode) |
| Hooks `PostToolUse`, `UserPromptSubmit`, `SessionEnd` | `~/.claude/scripts/zeit-hook.py`, schreibt Rohdaten nach `~/.claude/zeiten/.raw/`. Kein AIOS-Skill verweist darauf | fremd (persönlicher Zeittracker, älter als das AIOS) |
| `enabledPlugins` | 13 Plugins, darunter `aios@aios-local` | Plugin `aios` AIOS-eigen, Rest fremd |
| `extraKnownMarketplaces` | `aios-local` (Ordner `~/aios-runtime`), `chrome-devtools-plugins`, `context-mode` | `aios-local` AIOS-eigen, Rest fremd |
| Plugin-Hooks | `claude-mem` und `context-mode` bringen eigene Hooks mit (in Claude über das Plugin, in Codex unter `hooks.state` in `config.toml`) | fremd |
| `env` | nur Namen erfasst: `ANTHROPIC_DEFAULT_OPUS_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL`, `ANTHROPIC_SMALL_FAST_MODEL`, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`, `CLAUDE_CODE_SUBAGENT_MODEL` | Clientkonfiguration, fremd |
| Modell und weitere | `model` Sonnet 5, `effortLevel` high, `alwaysThinkingEnabled`, `statusLine` (`~/.claude/statusline-command.sh`), Sprach- und Oberflächeneinstellungen | Clientkonfiguration, fremd |
| `~/.claude/commands/` | 9 Befehle (`commit`, `distill`, `e2e`, `fde-workflow`, `leonidas`, `mcp-builder`, `repo-recon`, `review`, `wiki`) | fremd (spartan-forge) |
| `~/.claude/agents/` | 14 Agentendateien | fremd |

### Codex `~/.codex/`

| Punkt | Befund | Einordnung |
| --- | --- | --- |
| `hooks.json` | `SessionStart` mit `context-mode-cache-heal.mjs`, `Stop` und `SubagentStop` mit `afplay` | fremd |
| `config.toml` | `model` gpt-6.1-sol, `model_reasoning_effort` medium, Subagenten gpt-6-sol medium mit höchstens 2 parallel, `notify`, `personality`, `service_tier`, Abschnitte `projects`, `desktop`, `marketplaces`, `plugins`, `mcp_servers`, `shell_environment_policy`, `hooks`, `agents` | Clientkonfiguration, fremd. Marktplatz und Plugin `aios@aios-local` AIOS-eigen |
| `~/.codex/agents/` | 14 TOML-Agenten | fremd |

## Zeitpläne

| Zeitplan | Befund | Einordnung |
| --- | --- | --- |
| `de.aios.retro` (launchd) | freitags 16:05, `Agentic OS/skills/aios-retro/scripts/retro.py`, Log nach `~/aios/archives/retros/` | AIOS-eigen |
| `de.aios.modellreview` (launchd) | stündlich und beim Laden, `Agentic OS/skills/aios-wochenreview/scripts/model_review.py`, Log nach `Agentic OS/aios/archives/reviews/models/` | AIOS-eigen |
| `com.alexandergreif.workhours-snapshot` (launchd) | stündlich, `~/.claude/scripts/work-hours-report.mjs` | fremd (persönlicher Zeittracker) |
| `com.spartanforge.daemon` (launchd) | samstags 08:00, `bun run` | fremd |
| `Jamie`, ClickShare, Google Updater, Keystone, JetBrains Toolbox (launchd) | Programmstarter und Updater | fremd |
| `crontab` | keine Einträge | |
| Codex-Automationen `~/.codex/automations/` | leer | |
| Claude-Cloud-Routinen | keine (`RemoteTrigger list` leer) | |
| T3-Zeitpläne | keine in allen 23 T3-Projekten (5 bei der Erhebung, die übrigen 18 durch den Prüfagenten abgefragt) | |

## MCP-Server und Plugins

### Claude Code (`claude mcp list`)

| Server | Status | Einordnung |
| --- | --- | --- |
| `aios-knowledge` (Nutzer, stdio, `Agentic OS/mcp/knowledge`) | verbunden | AIOS-eigen, Dienstanbindung |
| `knowledge-bots-api` (Nutzer, HTTP, Blockbrain-Dokumentation) | verbunden | Dienstanbindung |
| `context7` (Nutzer, HTTP) | verbunden | Dienstanbindung |
| `chrome-devtools` (Nutzer, npx) | verbunden | Dienstanbindung |
| `RepoPrompt` (Nutzer, stdio) | Verbindung fehlgeschlagen (Zeitüberschreitung) | Dienstanbindung |
| claude.ai verbunden: Claude Docs, draw.io, Google Calendar, Gmail, Infisical Docs, Google Drive, Excalidraw, Slack, Microsoft 365, Atlassian | verbunden | Dienstanbindung |
| claude.ai Anmeldung nötig: Atlassian MCP, GitBook MCP, Miro, Sentry, Notion, monday.com, Linear, Intercom, HubSpot, Figma, Canva, Box | Anmeldung nötig | Dienstanbindung |
| Plugin-Server verbunden: `claude-mem`, `playwright`, `context-mode`, `chrome-devtools-mcp`, `datadog` (EU) | verbunden | Dienstanbindung |
| Plugin-Server `github` | fehlgeschlagen (HTTP 400, Authorization-Header) | Dienstanbindung |
| Plugin-Server mit Anmeldung nötig: `context7`, `sentry`, aus claude.ai-Plugins `slack`, `linear`, `atlassian`, `notion`, `datadog`, `monday`, `clickup`, `guru` | Anmeldung nötig | Dienstanbindung |
| claude.ai-Plugin-Einträge Google Calendar und Gmail | nicht konfiguriert | Dienstanbindung |
| Projektbezogene Server in 13 Projekten (`archon`, `playwright`, `semgrep`, `Ref`, `n8n-mcp`, `mastra`, `mastra-docs`) | nicht geprüft | Dienstanbindung, fremd |

Claude-Plugins: `aios@aios-local` 0.1.0 (aktiv, AIOS-eigen), `chrome-devtools-mcp`, `claude-md-management`, `claude-mem`, `context-mode`, `context7`, `datadog`, `frontend-design`, `github`, `playwright`, `sentry`, `skill-creator`, `superpowers` (aktiv, fremd), `aikido` (Projekt, deaktiviert), synchronisiert aus claude.ai: `engineering`, `productivity`, `cowork-plugin-management`, `enterprise-search`.

### Codex (`codex mcp list`, Codex 0.163.0)

Auth-Spalte wörtlich aus der Ausgabe. `Unsupported` heißt, der Server bietet keine OAuth-Anmeldung über Codex an.

| Server | Status | Auth | Einordnung |
| --- | --- | --- | --- |
| `aios-knowledge` | aktiv | Unsupported | AIOS-eigen, Dienstanbindung |
| `knowledge-bots-api`, `RepoPrompt`, `chrome-devtools`, `context-mode`, `mcp-search`, `node_repl`, `cua_repl`, `playwright` | aktiv | Unsupported | Dienstanbindung |
| `context7` | aktiv | OAuth | Dienstanbindung |
| `github`, `sentry` | aktiv | Not logged in | Dienstanbindung |
| `mcp` | aktiv | Unknown | Dienstanbindung |
| `code-review`, `codex_app`, `computer-use` | deaktiviert | Unsupported | Dienstanbindung |

Codex-Plugins (alle aktiv): `aios@aios-local` (AIOS-eigen), aus OpenAI `codex-app-tools`, `browser`, `unified-computer-use`, `visualize`, `documents`, `pdf`, `spreadsheets`, `presentations`, `template-creator`, `computer-use`, `code-review`, dazu `claude-md-management`, `context7`, `datadog`, `frontend-design`, `github`, `playwright`, `sentry`, `skill-creator`, `superpowers`, `context-mode`, `claude-mem` (fremd).

## Vorschlag für Schritt 3: sichern

Ziel `~/aios-backup-20261022/` mit Rechten `700`, Liste der Originalpfade und SHA256. Symlinks als Symlinks sichern und zusätzlich ihr Ziel notieren.

1. `~/.claude/CLAUDE.md` und `~/.codex/AGENTS.md`
2. `~/.agent-rules/` vollständig, einschließlich `backups/`
3. Die 19 AIOS-Symlinks aus `~/.agents/skills` und `~/.claude/skills` (als Links mit Zielliste)
4. `~/.codex/skills/precommit-review/`
5. Der echte Inhalt hinter `~/aios` (`Agentic OS/aios/`) vollständig, einschließlich `archives/`, `output/`, `.env` und der unversionierten Dateien. Kundendaten liegen nur im Backup, werden nicht gelesen oder migriert
6. Das Repository `Agentic OS` vollständig als Dateikopie, einschließlich `.git/` und aller ignorierten Bestände (Befund 1). Ein Git-Bundle reicht nicht, weil es die ignorierten Daten (zusammen rund 290 MB) nicht enthält. `node_modules/` und `__pycache__/` können ausgelassen werden. Punkt 5 ist darin enthalten, weil `~/aios` dorthin zeigt
7. `~/aios-runtime/` vollständig
8. Die beiden launchd-Dateien `de.aios.retro.plist` und `de.aios.modellreview.plist`
9. Die beiden Planhat-Sicherungen in `.trash/` und das Claude-Projektgedächtnis zum alten AIOS-Repository
10. Nur als Pfadnotiz, nicht kopieren: `~/.config/aios/secrets.env` (bleibt am Ort, wird weiter von `aios-knowledge` gebraucht)

Nicht gesichert, weil fremd oder Clientkonfiguration: Plugins, MCP-Server, `settings.json`, `config.toml`, Anmeldedaten, fremde Skills, `commands/`, `agents/`, Zeittracker.

## Vorschlag für Schritt 4: beiseitelegen

Nur, was der neuen Installation im Weg steht. Nichts löschen.

| Teil | Grund | Vorschlag |
| --- | --- | --- |
| `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md` | Konflikt für den Installer | verschieben in das Backup |
| 5 Symlinks `aios-audit`, `tagesstart`, `terminvorbereitung`, `use-case-konzept`, `zeiterfassung-vorbereiten` in `~/.agents/skills` und `~/.claude/skills` (10 Links) | Konflikt für den Installer | verschieben in das Backup |
| `~/aios-runtime/` | Standardpfad der neuen Runtime muss frei sein | **Entscheidung nötig:** verschieben (dann hat das aktive Plugin `aios@aios-local` keine Quelle mehr) oder in Schritt 5 einen anderen Runtime-Pfad wählen und die alte Runtime stehen lassen |

Zur Entscheidung, nicht nötig für die Installation:

- `~/.codex/skills/precommit-review`: beiseitelegen, um doppelte Namen in Codex zu vermeiden, oder stehen lassen.
- Die 11 alten AIOS-Skills mit fachlichem Nachfolger (`auftrag`, `goal-vorbereiten`, `gpt-prompting`, `aios-assistent`, `aios-wochenreview`, `aios-retro`, `aios-ishikawa-prozessanalyse`, `kundenunterlage`, `aios-skill-builder`, `planhat-timetracking`, `planhat-wochenabschluss`), je ein Link in beiden Ordnern: stehen lassen laut Grundsatz oder beiseitelegen gegen doppelte Skillauswahl.
- Stehen bleiben ohne Nachfolger: `blockbrain-slides`, `lernvideo`, `agentic-workflow-bauen`.
- Plugin `aios@aios-local` in Claude und Codex: abschalten wäre eine Plugin-Änderung und ist durch die Grenzen bisher nicht gedeckt.
- launchd-Jobs `de.aios.retro` und `de.aios.modellreview`: laufen gegen die alten Skripte weiter, solange `Agentic OS` am Ort bleibt. Entladen nur auf ausdrückliche Freigabe.
- Botticelli-Abschnitt und Stilspiegel aus dem alten Regelkern: Übernahme in den neuen Regelkern oder das Profil klären (Befund 6).
- `~/.agent-rules/`: kann am Ort bleiben. `sync.py --apply` bricht ab, wenn eine Zieldatei fehlt oder vom gespeicherten Stand abweicht (`sync.py`, Zeile 69 bis 72), und überschreibt die neue Installation deshalb nicht. `sync.py --check` meldet danach dauerhaft eine Abweichung. Nach der Neuinstallation nicht mehr verwenden.

## Unabhängige Gegenprüfung

Am 22.10.2026 hat ein neu gestarteter Prüfagent (Opus 5.5, Denkaufwand high) die Datei gegen Dateisystem, Git-Stände und Clientausgaben geprüft, rein lesend. Er hat 7777 `SKILL.md` in allen Skill- und Plugin-Ordnern abgeglichen und die Konfliktliste als vollständig bestätigt.

Nachgezogen und selbst nachgeprüft: ignorierte Bestände im Repository `Agentic OS` und daraus folgende Backup-Empfehlung (Befund 1, Schritt 3 Punkt 6), Cache-Kopien des Plugins `aios` (Befund 3), Dateiname `Claude.md`, Anzahl in `.playwright-mcp/`, Plugin-Cache-Fassungen, Git-Status von `learning/`, Projektfassungen von `superpowers` und `sentry`, Plugin-Hooks, Claude-Projektgedächtnis, Planhat-Sicherungen in `.trash/`, wörtliche Codex-Auth-Werte, T3-Zeitpläne aller Projekte, Zeilenangabe in `sync.py`.

Grenzverletzung beim Prüfen: Der Prüfagent hat einmal `grep` mit verworfener Ausgabe auf eine Datei in `~/aios/context/` ausgeführt. Laut seinem Bericht wurde kein Inhalt angezeigt oder weitergegeben.

Offen, nicht geprüft:

- ob Codex `~/.codex/skills` zusätzlich zu `~/.agents/skills` lädt (Befund 4)
- ob Claude und Codex das Plugin `aios` nach dem Verschieben von `~/aios-runtime` weiter aus dem Cache laden (Befund 3)
- Status der projektbezogenen MCP-Server
- Inhalte der ausgeschlossenen Ordner und Dateien

## Entscheidungen zu Schritt 3 und 4

Am 22.10.2026 von Alexander getroffen (Entscheidung 120 in `.aios/NOTIZEN.md`). Sie ersetzen die offenen Punkte in den Vorschlagslisten oben.

| Punkt | Entscheidung |
| --- | --- |
| Sicherung `Agentic OS` | ganze Dateikopie inklusive `.git/` und ignorierter Daten, ohne `node_modules/` und `__pycache__/` |
| `~/aios-runtime` | in Schritt 4 beiseitelegen, Standardpfad für die neue Runtime |
| Alte Skills | beiseitelegen: 5 Konflikte, 11 Skills mit Nachfolger (je ein Link in beiden Ordnern) und `~/.codex/skills/precommit-review`. Stehen bleiben `blockbrain-slides`, `lernvideo`, `agentic-workflow-bauen` |
| Botticelli-Abschnitt | eigene Paketänderung vor Schritt 5 |
| Plugin `aios@aios-local` | nach bestandenem Schritt 6 in Claude und Codex deaktivieren, nicht deinstallieren |
| launchd `de.aios.retro`, `de.aios.modellreview` | nach bestandenem Schritt 6 entladen, Plist-Dateien bleiben |
| `~/aios/.env` | in Schritt 3 am Original auf `600`, Inhalt ungelesen |
| `~/.agent-rules/` | sichern, am Ort lassen, nicht mehr verwenden |
