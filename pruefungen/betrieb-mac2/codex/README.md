# Erstinstallation, Update und Deinstallation für Codex auf dem zweiten Mac

Stand: 22.10.2026. Reale Betriebsprobe des Codex-Pfads in einem eigenen Test-Home. Gegenstück zur [Claude-Probe](../README.md). Normales Profil, `~/.codex` und `~/.agents/skills` wurden nicht berührt.

## Aufbau

- Test-Home `~/aios-abnahme-codex-2` mit eigenem `--codex-home ~/aios-abnahme-codex-2/.codex`
- Testquelle `~/aios-abnahme-codex-2/quelle`: frischer Klon von `a784ff2` (Paket 0.1.4-dev)
- Neuere Version am selben Quellpfad: `allgemein/regeln/kern.md` und `scripts/paket_bauen.py` aus dem Arbeitsstand 0.1.5-dev kopiert
- Alle Aufrufe mit `PYTHONDONTWRITEBYTECODE=1`, siehe Befund 1
- Fremdbestand: eigener Skill unter `.agents/skills`, fremde Datei im `CODEX_HOME`, Marker in Profil, Ausgabe und Runtime
- [zustand.sh](zustand.sh) hält Marker-Hashes, Profildateien, Skilllinks, `AGENTS.md` und Runtime-Version fest. Exitcodes stehen in den Logs.

## Ergebnis

| Schritt | Ergebnis | Beleg |
| --- | --- | --- |
| Erstinstallation, Auswahl `codex` | Exitcode 0, Status `vorhanden`, 21 Skilllinks unter `.agents/skills`, `AGENTS.md` im `CODEX_HOME` | [erstinstallation.log](erstinstallation.log), [zustand-1](zustand-1-nach-erstinstallation.txt) |
| Update-Vorschau | Status davor `vorhanden`. 0.1.4-dev nach 0.1.5-dev, 5 `replace` (`.codex/AGENTS.md`, Runtime-`AGENTS.md` und `CLAUDE.md`, `kern.md`, `paket.json`), 90 `keep`, kein Fremdziel | [update-vorschau.log](update-vorschau.log) |
| Update ausführen | Exitcode 0, Status danach `vorhanden`. Genau die 5 geplanten Ziele ersetzt, von den beobachteten Clientdateien nur `.codex/AGENTS.md`. Alle Marker und Profildateien bytegleich | [update-ausfuehrung.log](update-ausfuehrung.log), [zustand-2](zustand-2-nach-update.txt) |
| Fehlerfall: Skilllink `tagesstart` auf fremdes Ziel umgebogen | Deinstallationsvorschau stoppt mit „Verknüpfung verändert“, Exitcode 1. Nach Wiederherstellung Status `vorhanden` | [fehlerfall-geaenderter-link.log](fehlerfall-geaenderter-link.log) |
| Deinstallations-Vorschau | 95 `remove`, kein Fremdziel | [deinstallation-vorschau.log](deinstallation-vorschau.log) |
| Deinstallation ausführen | Exitcode 0, Status `deinstalliert` (Statuscheck endet gewollt mit 1, Exitcode 0 nur bei `vorhanden`). Übrig: fremder Skill, fremde Datei im `CODEX_HOME`, fremde Runtime-Datei, Profil samt Zustand (Bestand `uninstalled`, abgeschlossene Operation, Sicherung der alten `AGENTS.md` unter `zustand/sicherungen/`, unverändertes Erstinstallationsjournal `installation.json` mit Status `installed`, das der Statuscheck nachrangig behandelt), Ausgabe. Alle Marker und Profildateien bytegleich | [deinstallation-ausfuehrung.log](deinstallation-ausfuehrung.log), [zustand-3](zustand-3-nach-deinstallation.txt) |

Zusätzlich wurde `~/aios-test-codex` (Quelle ist dieses Repository) regulär von 0.1.3-dev auf 0.1.4-dev aktualisiert, ebenfalls mit Ersetzung von `.codex/AGENTS.md`.

## Befunde

1. Gering, Testartefakt mit realem Kern: Im [ersten Lauf](erster-lauf/) meldete die Update-Vorschau trotz geändertem Manifest die alte Version 0.1.4-dev. Klon, Installation und Kopie der neuen `paket_bauen.py` lagen in derselben Sekunde. Python hielt den beim Installieren erzeugten Bytecode wegen gleicher Sekunde und gleicher Dateigröße für aktuell. Der Regelkern wurde korrekt ersetzt, nur die Versionsnummer war veraltet. Betroffen wäre in diesem Fall jede Änderung an der Paketlogik (`paket_bauen.py`, `paketregeln.py`), nicht nur das Versionsetikett. Im Betrieb liegt zwischen `git pull` und Update praktisch immer mehr als eine Sekunde. Eine robuste Abhilfe wäre `python3 -B` in `install.sh` und den Betriebsaufrufen. Nicht umgesetzt.
2. Gering: Einen Konfliktfall gibt es nur vor der Deinstallation. Vor dem Update wurde kein Konflikt provoziert, die Erkennung nutzt aber denselben Planungsweg.

Hinweis: Der erste Test-Home `~/aios-abnahme-codex` bleibt als Beleg erhalten. Das Update von `~/aios-test-codex` ist nur im Zustand dort belegt (`paket.json` 0.1.4-dev, Operation `update completed`).

## Nicht abgedeckt

Gleichzeitige Installation beider Clients in einem Profil (Auswahl `beide`), interaktiver Dialog, Unterbrechung mitten in einer Operation.
