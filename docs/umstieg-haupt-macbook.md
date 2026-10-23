# Umstieg auf dem Haupt-MacBook

Stand: 22.10.2026. Ziel: Das alte AIOS auf dem Haupt-MacBook sichern und beiseitelegen, das neue Paket mit beiden Clients installieren und danach die Dienstanbindungen einzeln einrichten und testen.

Ausgangslage: Auf dem zweiten Mac (privater Laptop) sind Installation, Update, Deinstallation, native Ladung und die sechs Modellfälle für Claude Code und Codex bestanden, teils mit Hinweisen ([Abnahmeprotokoll](abnahme-zweiter-mac.md)). Dienstanbindungen wurden dort bewusst nicht eingerichtet. Sie gehören auf das Haupt-MacBook.

## Grundsätze

- **Sichern statt löschen.** Das neue Paket enthält noch nicht alles: Es fehlen unter anderem `blockbrain-slides` (108), `lernvideo` mit HyperFrames (46) und die Dokument-Skills (114). Alte Skills ohne neues Gegenstück dürfen vorerst stehen bleiben. Der Installer behandelt sie als Fremdbestand und fasst sie nicht an.
- **Nur AIOS-Teile beiseitelegen.** MCP-Server, Plugins, Anmeldungen und sonstige Clientkonfiguration in `~/.claude` und `~/.codex` bleiben unverändert. Die neue Installation richtet keine Dienste ein.
- **Altbestand blockiert den Installer.** Vorhandene `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md` und alte Skills mit gleichem Namen wie neue AIOS-Skills sind Konflikte. Sie müssen vor der Installation verschoben sein.
- **Jeder Schreibschritt mit Vorschau und Freigabe.** Inventur ist rein lesend. Verschieben und Installieren erst nach bestätigter Liste.
- **Backup bleibt lokal**, mit privaten Dateirechten. Es kann Zugangsdaten enthalten und wird nicht ins Repository oder in Chats kopiert.

## Ablauf

1. **Quelle holen.** `git clone https://github.com/alexandergreif/aios-neuaufbau.git ~/aios-neuaufbau` oder dort `git pull`. Commit mit `git rev-parse HEAD` festhalten, Tests mit `python3 -m unittest discover -s tests` laufen lassen.
2. **Inventur, rein lesend.** Erfassen und in AIOS-eigen, fremd und Dienstanbindung einordnen:
   - globale Regeldateien: `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, `~/.agent-rules/`
   - Skills: `~/.agents/skills/`, `~/.claude/skills/`, Skills in Plugin-Ordnern
   - alter AIOS-Ordner `~/aios/` mit Profil, Kontext, Vorlagen und Ergebnissen
   - Hooks und Einstellungen in `~/.claude/settings.json`, Zeitpläne (`launchd`, `cron`, Client-Zeitpläne)
   - MCP-Server und Plugins je Client (`claude mcp list`, `codex mcp list`), nur Namen und Status, keine Schlüssel
   - Abgleich der Skillnamen mit `allgemein/skills/`: gleiche Namen sind Konflikte, fehlende neue Gegenstücke bleiben stehen
3. **Backup.** Alle AIOS-eigenen Teile nach `~/aios-backup-<datum>/` kopieren, mit Liste der Originalpfade und SHA256. Rechte `700`. Vor dem Verschieben die Kopie stichprobenartig vergleichen.
4. **Beiseitelegen.** Nur die bestätigten AIOS-eigenen Teile verschieben, die einer neuen Installation im Weg stehen. Nichts löschen.
5. **Neu installieren.** `sh install.sh`, Auswahl `beide`, Pfade prüfen, echte Profilangaben. Kunden- und Projektregister sowie Inhalte aus dem alten Profil bewusst übernehmen, nicht automatisch. Dabei als Coding-Wurzel genau `~/PycharmProjects/BB Coding Projects/BB_Repos` bestätigen. Eine Kunden-Wurzel wie `.../BB Coding Projects/Kunden` liegt daneben, nicht darunter, sonst meldet die Prüfung überschneidende Wurzeln. In `projekte.md` direkt unter der Trennzeile der Tabelle die Zeile `| botticelli | Botticelli | /Users/<name>/PycharmProjects/BB Coding Projects/BB_Repos/Botticelli | | PDEV | aktiv |` eintragen, den Ordner absolut und ohne `~`. Im Quellordner `~/aios-neuaufbau` mit `python3 scripts/pruefe_register.py --config ~/aios-profile/pfade.json --register ~/aios-profile/projekte.md --project botticelli` prüfen. Erwartet wird der Ordnerpfad mit Exit 0. Zusammen mit dem Regelkern ab 0.1.6-dev deckt das die allgemeinen Teile des Botticelli-Abschnitts der alten globalen Regeln ab (Entscheidung 120). Blockbrain-Schlüssel nur eintragen, wenn der Zugang geprüft werden soll.
6. **Prüfen.** `python3 scripts/einrichtungsstatus.py --config ~/aios-profile/pfade.json --home ~` mit Ergebnis `vorhanden`. Beide Clients normal starten und Regelkern sowie Skills sichtbar prüfen. Einen Skill je Client aufrufen.
7. **Dienstanbindungen einzeln.** Reihenfolge nach Nutzen: Outlook Calendar und Microsoft To Do (Tagesstart, Planung), Jira, Outlook Mail, Slack, Teams, Confluence, Planhat, GitHub, Chrome DevTools, Sentry, Datadog, Blockbrain nach Nutzentest. Je Dienst und Client den Anbindungsweg festlegen, anmelden, Lesezugriff und einen Fehlerfall testen, Schreibaktionen nur mit konkretem Testauftrag. Umfang laut [Verbindungen](../allgemein/referenzen/verbindungen.md).
8. **Backup entfernen** erst nach einigen Wochen stabilem Betrieb und auf ausdrücklichen Auftrag.

## Bekannte Punkte aus der Abnahme

- Die Regel zur inhaltlich unverändert ausgegebenen Prüfungsfassung (0.1.5-dev) ist noch nicht mit Modellfällen erprobt. Wortgleichheit ist eine bekannte Grenze.
- Codex protokolliert Prüfaufträge an Subagenten verschlüsselt. Die Vollständigkeit des übergebenen Entwurfs ist dort nicht belegbar.
- Codex-Standard ist Denkaufwand `low`. Für Prüfagenten ist das flach.
- Veralteter Python-Bytecode kann bei Änderungen in derselben Sekunde greifen. Abhilfe `python3 -B` ist nicht umgesetzt.
- In Claude Code `claude -p` sind Lesezugriffe außerhalb des Arbeitsordners gesperrt. Interaktiv fragt der Client nach.
