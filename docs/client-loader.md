# Native Regelladung isoliert prüfen

Stand: 19.10.2026. Beide lokal vorhandenen Clients laden den vollständigen gemeinsamen Kern in einem synthetischen Arbeitsordner. Dieser Nachweis umfasst den Loader, noch keine Modellantworten, Fachskills oder Dienstverbindungen.

```sh
python3 scripts/check_client_loader.py --client both
```

Das Skript benötigt macOS mit `sandbox-exec` und bereits installierte Clients. Es installiert nichts. `--codex` und `--claude` wählen bei mehreren Installationen die konkrete ausführbare Datei. Mit `--evidence-dir /absoluter/neuer/ordner` werden Ergebnis-JSON und die vollständigen `ls -l`-Ausgaben der vorhandenen Skillordner vor und nach dem Test gespeichert. Ein vorhandener Belegordner wird nicht überschrieben.

Die Probe setzt HOME, CODEX_HOME, CLAUDE_CONFIG_DIR und XDG_CONFIG_HOME ausschließlich im Kindprozess auf neue Testordner. Sie übernimmt keine Anmeldedaten oder persönliche Konfiguration. Die Betriebssystem-Sandbox sperrt persönliche Dateiinhalte einschließlich persönlicher Keychain-Dateien, das systemweite Keychain-Verzeichnis, den Machdienst `com.apple.securityd`, Schreibzugriff außerhalb des Testordners und externes Netzwerk. Benötigte Clientprogramme und ihre Bibliotheken sind vom Dateileseverbot ausgenommen. Nur der lokale HTTP-Testport ist für die Claude-Probe erreichbar. Tools, Hooks, MCP und automatische Erinnerungen sind deaktiviert.

## Beobachtetes Ergebnis

| Prüfung | Ergebnis |
| --- | --- |
| Codex CLI 0.162.1, `debug prompt-input` | Vollständiger erzeugter Kern im modellseitigen Prompt-JSON |
| Claude Code 2.1.300, lokaler HTTP-Testserver | Alle 16 Absätze des Kerns im Request enthalten |
| Absichtlicher HTTP-400-Fehler | Claude meldet `AIOS_SYNTHETIC_LOADER_STOP` und beendet den Aufruf |
| Beide Regeldateien aus dem Testordner entfernt | Kern fehlt bei beiden Clients, negative Kontrolle bestanden |
| Vorhandene Skill-Verknüpfungen | Vorher-/Nachher-Ausgaben identisch |

Beim Claude-Test ist Exit 1 des Clientprozesses beabsichtigt: Der Testserver verweigert die Anfrage nach dem Erfassen des synthetischen Kontexts. Es wurde kein Modell aufgerufen. Das Prüfskript liefert Exit 0 nur bei erfolgreicher Positiv- und Negativkontrolle. `--restricted` ist für diese Probe ungeeignet, weil der installierte Client damit den Regelkern nicht in die Anfrage aufnimmt. Dies wurde unabhängig mit gleichem Restaufbau bestätigt.

Ein zusätzlicher lokal vorhandener Codex 0.38.0 bietet den benutzten Debug-Aufruf nicht. Der Installer muss daher später den tatsächlich gestarteten Programmpfad und dessen Fähigkeiten prüfen. Es wurde kein Client aktualisiert.

## Dokumentierte Clientwege

Codex liest `AGENTS.md` aus seinem globalen Konfigurationsordner und den einschlägigen Projektverzeichnissen. Die isolierte Probe verwendet eine Projektdatei. Eine spätere globale Einbindung muss zusätzlich geprüft werden. [Offizielle Codex-Dokumentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

Claude Code lädt `CLAUDE.md`. Aktuelle Versionen können bei fehlender `CLAUDE.md` auf `AGENTS.md` zurückgreifen. Deshalb entfernt die Negativkontrolle beide Dateien. Der Generator erzeugt beide aus derselben Quelle und hält die Fachreferenzen relativ auflösbar. [Offizielle Claude-Code-Dokumentation](https://code.claude.com/docs/en/memory).

Die Umleitung auf einen lokalen Testserver nutzt `ANTHROPIC_BASE_URL` und einen erfundenen Schlüssel. Die Clientkonfiguration liegt im synthetischen `CLAUDE_CONFIG_DIR`. [Offizielle Umgebungsvariablen](https://code.claude.com/docs/en/env-vars).

Offen bleiben native Skillauswahl, Modellverhalten, globale Installation, Verbindungen und die Abnahme auf dem zweiten Mac. Die Loaderprobe ersetzt diese Prüfungen nicht.
