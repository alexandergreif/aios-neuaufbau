# Erstinstallation, Update und Deinstallation auf dem zweiten Mac

Stand: 21.10.2026. Reale Betriebsprobe des Paketbetriebs in einem eigenen Test-Home, nur Claude Code. Das normale Benutzerprofil und die normalen Clientordner wurden nicht berührt.

## Aufbau

- Test-Home `~/aios-abnahme-betrieb`, eigener Clientordner `~/aios-abnahme-betrieb/.claude`
- Testquelle `~/aios-abnahme-betrieb/quelle`: frischer Klon von `a206ec5` (Paket 0.1.0-dev)
- Python 3.13.5, macOS auf dem zweiten Mac
- Alle Pfade in den Belegen sind auf `~` gekürzt. Profilangaben sind synthetisch, der Blockbrain-Schlüssel wurde übersprungen.
- [zustand.sh](zustand.sh) hält Marker-Hashes, geschützte Profildateien, Skilllinks, Regeldatei und Runtime-Version fest.

## Ablauf und Ergebnis

| Schritt | Ergebnis | Beleg |
| --- | --- | --- |
| Geführte Erstinstallation `sh install.sh --home … --claude-config-dir …`, Auswahl `claude`, Standardpfade | Profilvorschau und Installationsvorschau gezeigt, beide mit `ja` bestätigt, Schlüssel übersprungen. Exitcode 0, Status `vorhanden`, 21 Skilllinks, 1 Regeldatei | [erstinstallation.log](erstinstallation.log) |
| Fremdbestand anlegen | Fremder Skill unter `.claude/skills` und `.agents/skills`, Marker in Profil, Ausgabe und Runtime | [zustand-1](zustand-1-nach-erstinstallation.txt) |
| Neuere Version am selben Quellpfad | Regelkern präzisiert, Version 0.1.1-dev. 145 Tests im Hauptrepository grün. In die Testquelle wurden nur `kern.md` und `paket_bauen.py` kopiert, dort wurden keine Tests ausgeführt | `allgemein/regeln/kern.md`, `scripts/paket_bauen.py` |
| Update-Vorschau | 0.1.0-dev nach 0.1.1-dev, Manifesthashes genannt, 5 `replace`, Rest `keep`, kein Fremdziel | [update-vorschau.log](update-vorschau.log) |
| Update ausführen | Exitcode 0, genau die 5 Dateien ersetzt, alte Regeldatei unter `zustand/sicherungen/` gesichert. Status `vorhanden`. Alle Marker, `profil.md`, `pfade.json`, `projekte.md`, `.env` und `wissen/INDEX.md` bytegleich | [update-ausfuehrung.log](update-ausfuehrung.log), [status](status-nach-update.txt), [zustand-2](zustand-2-nach-update.txt) |
| Fehlerfall: eigene Runtime-Datei lokal verändert | Deinstallationsvorschau stoppt mit „Eigene Datei verändert“, Exitcode 1, nichts geändert. Status `eingeschränkt`. Nach Zurücksetzen wieder `vorhanden` | [fehlerfall-geaenderte-datei.log](fehlerfall-geaenderte-datei.log) |
| Deinstallations-Vorschau | 95 `remove` (21 Links, 1 Regeldatei, 73 Runtime-Dateien), kein Fremdziel | [deinstallation-vorschau.log](deinstallation-vorschau.log) |
| Deinstallation ausführen | Exitcode 0, Status `deinstalliert`. Übrig bleiben Runtimewurzel mit fremder Zusatzdatei, `.claude/` mit fremdem Skill, `.agents/` sowie Profil samt `zustand/` (Bestand mit `status: uninstalled`, Operation `completed`, Lock, Sicherung). Alle Marker und Profildateien bytegleich | [deinstallation-ausfuehrung.log](deinstallation-ausfuehrung.log), [status](status-nach-deinstallation.txt), [zustand-3](zustand-3-nach-deinstallation.txt) |

Zusätzlich wurde die erste Testinstallation (`~/aios-test.xgNSnI`, Quelle ist dieses Repository) regulär auf 0.1.1-dev aktualisiert: dieselben 5 `replace`, danach Status `vorhanden`.

Die Exitcodes von Erstinstallation, Update und Deinstallation (jeweils 0) wurden im Terminal abgelesen und stehen nicht in den Logdateien. Der Erfolg ist dort durch Abschlusszeilen und Statusausgaben belegt. Die Konfiguration liegt unter `~/aios-abnahme-betrieb/aios-profile/pfade.json`. Achtung bei der Lesart: Im Dialog bedeutet `~` in Vorgabewerten wie `[~/aios-runtime]` das gewählte `--home`, in allen übrigen Pfaden das gekürzte echte Home.

## Beobachtungen

1. Gering: Im Zustand `eingeschränkt` meldet der Status „0 Skillverknüpfungen“, obwohl alle 21 Links noch vorhanden sind. Die Zahl beschreibt dort die geprüften, nicht die vorhandenen Links.
2. Gering: Die zweite Vorschau der Erstinstallation nennt nur Anzahlen (1 Regeldatei, 21 Skilllinks), nicht jedes Ziel einzeln wie Update und Deinstallation.
3. Eine eigene Statusausgabe direkt vor dem Update fehlt. Der Ausgangszustand ist über die Hashes in zustand-1 und den Status am Ende der Erstinstallation belegt.
4. Der Fehlerfall wurde mit der Deinstallationsvorschau ausgelöst. Der Befehl steht nicht im Log.
5. Bei nicht interaktiver Eingabe stehen die Dialogfragen ohne Zeilenumbruch hintereinander im Protokoll, die `ja`-Eingaben sind nicht sichtbar. Die interaktive Gegenprobe steht aus.

Unabhängige Prüfung: Hashes und Restzustand real nachgerechnet, 95 entfernte Schritte deckungsgleich mit `bestand.json`, keine Geheimnisse in den Belegen. Urteil für Profil und Installation, Update und Deinstallation jeweils bestanden mit Hinweisen. Die Hinweise sind oben eingearbeitet.

## Nicht abgedeckt

Codex, ein nativer Clientstart in diesem zweiten Test-Home (dort keine Anmeldung, Ladung ist in `~/aios-test.xgNSnI` belegt), Profilimport aus einem Export, Unterbrechung mitten in einer Operation (nur synthetisch getestet).
