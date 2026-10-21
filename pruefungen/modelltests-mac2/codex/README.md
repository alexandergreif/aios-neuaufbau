# Modellfälle in Codex auf dem zweiten Mac

Stand: 22.10.2026. Dieselben sieben Fälle wie in Claude Code, jetzt in Codex.

## Rahmen

- Codex CLI 0.163.0 (vorher 0.38.0, über npm aktualisiert), Modell `gpt-6.1-sol`, Denkaufwand `low` (Clientstandard), Anmeldung über ChatGPT
- Paket 0.1.3-dev, Test-Home `~/aios-test-codex` mit eigenem `HOME` und `CODEX_HOME`, dateibasierte Anmeldung (`cli_auth_credentials_store = "file"`)
- Erstinstallation mit Auswahl `codex`: Status `vorhanden`, 21 Skilllinks unter `.agents/skills`, `AGENTS.md` im Test-`CODEX_HOME` ([Dialog](../../betrieb-mac2/erstinstallation-codex.log))
- Native Ladung: Regelkern geladen, 20 AIOS-Skills in der impliziten Liste. `auftrag-vorbereiten` erscheint gewollt nicht (`allow_implicit_invocation: false`) und lädt bei ausdrücklichem Aufruf.
- Ausführung: [ausfuehren.sh](ausfuehren.sh) mit `codex exec -s read-only --json "$<skill> <prompt>"` je Fall in eigenem leeren Arbeitsordner
- Die Fallzusammenfassungen beruhen auf dem exec-Strom. Prüfagenten erscheinen dort nur als Warteaufruf. Ihre Starts und Ergebnisse stammen aus den Sitzungsprotokollen und stehen unten.

## Ergebnis

Alle Läufe mit Exitcode 0, keine Dateien angelegt, keine Schreib- oder Sendeaktionen, nichts erfunden. Unabhängig bewertet, alle Erwartungen erfüllt, beim Einstieg eine teilweise.

| Fall | Prüfagent laut Sitzungsprotokoll | Urteil |
| --- | --- | --- |
| [tagesstart-vollstaendig](tagesstart-vollstaendig.md) | gestartet, abgewartet, keine Befunde | bestanden mit Hinweisen |
| [tagesstart-kalender-fehlt](tagesstart-kalender-fehlt.md) | keiner, Rückfrage statt Ergebnis | bestanden |
| [terminvorbereitung-mehrdeutig](terminvorbereitung-mehrdeutig.md) | keiner, Rückfrage statt Ergebnis | bestanden mit Hinweisen |
| [nachbereitung-keine-erfundene-zustandigkeit](nachbereitung-keine-erfundene-zustandigkeit.md) | gestartet, abgewartet, Freigabe | bestanden |
| [auftrag-nur-vorbereiten](auftrag-nur-vorbereiten.md) | gestartet, abgewartet, Freigabe | bestanden |
| [prozessanalyse-zeit-ist-nicht-geld](prozessanalyse-zeit-ist-nicht-geld.md) | gestartet, abgewartet, Freigabe | bestanden |
| [einstieg-auftrag](einstieg-auftrag.md) | gestartet, nicht abgewartet, keine Befunde | bestanden mit Hinweisen |

Gegenüber Claude: Jeder Lauf endet mit genau einem Abschluss, ohne Zwischenmeldung und ohne fortgesetzten Prüfer. Die Prüfer sind Forks mit Nutzerauftrag, nativ geladenem Skill und Regelkern im Wortlaut.

## Befunde

Mittel:

1. Der Auftrag an die Prüfagenten wird nur verschlüsselt protokolliert. Ob sie den vollständigen Entwurf bekamen und ob danach noch geändert wurde, ist deshalb nicht belegbar. Die Prüferantworten beziehen sich auf konkrete Inhalte der Endfassung.

Gering:

2. Einstieg: Prüfagent gestartet, aber nicht abgewartet. Die Prüfung wird weder genannt noch als offen gemeldet.
3. Prüfer erben Modell und Denkaufwand `low` und sind in Sekunden fertig. Eine Wahl nach Schwierigkeit fand nicht statt.
4. Der nativ geladene Skill wird in fünf Fällen zusätzlich per `cat` gelesen, der Regelkern in drei.
5. Blick auf den Arbeitsstand in fünf von sieben Fällen, der Stand wird nicht genannt.
6. „morgen, am 22. Oktober“ stammt aus dem Systemdatum.
7. Einstieg: Anfängerniveau, Themen und Zielclient sind ergänzt, ohne sie als Annahmen zu kennzeichnen.
8. Fehlgeschlagene Befehle stammen aus dem Login-Profil der Shell in der Sandbox (`brew shellenv`, xcrun-Cache) und sind keine Schreibversuche des Modells.

## Offen

- Gemeinsame Regel für beide Clients: Die zuletzt geprüfte Fassung wird unverändert ausgegeben (Vorschlag aus Claude Runde 4)
- Interaktive Gegenprobe des Installer-Dialogs
- Update und Deinstallation für Codex nur synthetisch getestet. Die reale Probe lief mit Claude, der Codex-Pfad (`.agents/skills`, `AGENTS.md`) ist dabei nicht abgedeckt.
