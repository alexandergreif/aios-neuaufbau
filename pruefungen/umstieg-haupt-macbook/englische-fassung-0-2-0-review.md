# Prüfung der englischen Fassung 0.2.0-dev

Stand: 23.10.2026. Umsetzung von Entscheidung 122 auf der Branch `feature/0.1.7-ablage-sprache-englisch`. Grundlage und Namenstabellen: [Englische Fassung](../../docs/englische-fassung.md).

## Umfang

- `allgemein/` heißt in der Quelle jetzt `de/`. Daneben steht `en/` mit englischen Datei-, Ordner- und Skillnamen. Eine deutsche Installation behält die Runtime-Wurzel `allgemein/`, eine englische nutzt `general/`.
- Alle Skripte tragen englische Namen und geben nur Englisch aus. Die zentrale Sprachtabelle steht in `scripts/languages.py`. Die Konfiguration hat das optionale Feld `language`, ohne Feld gilt `de`. Englische Profile nutzen `paths.json`, `profile.md`, `projects.md`, `knowledge/` und `state/`.
- Der Installer spricht Englisch, fragt die Sprache ab (Vorschlag `en`) oder nimmt `--language de|en`. Bestätigungen erfolgen mit `yes`. Die Statusausgabe hat englische Schlüssel und Werte (`present`, `missing`, `limited`, `uninstalled`).
- `README.md` ist der neue englische Einstieg, das bisherige Protokoll heißt `README.de.md`. Die geltenden Anleitungen unter `docs/` sind auf die neuen Namen umgestellt. Historische Nachweise bleiben unverändert.
- Version 0.2.0-dev.

## Übersetzung

- Erstübersetzung: 21 Skills durch je einen Haiku-5.5-Agenten. Regelkern, Referenzen und Werkzeuge durch Sonnet-5.5-Agenten. Vorlagen und Konfiguration durch den Hauptagenten.
- Prüfung: Je fünf Opus-5.5-Prüfagenten für die Skills und je einer für Regelkern, Referenzen und Vorlagen, jeweils satzweise gegen das deutsche Original. Korrekturen durch Sonnet-Agenten und den Hauptagenten.

| Bereich | Erste Prüfung | Nachprüfungen | Ergebnis |
| --- | --- | --- | --- |
| Skills, 5 Gruppen | 7 muss (unter anderem „fällig“ als overdue, „Quelldatum“ als source date, „Eddy“ als Person, Abnahme als approval, ein unverständlicher Satz in prepare-brief, Auszahlungen als payouts, eine verschobene Freigabe), viele sollte | Einheitlichkeitsdurchgang, dann 5 neue Prüfagenten: keine Bedeutungsfehler, 2 muss nur zur Einleitungsformel, sollte und Hinweise eingearbeitet | abgeschlossen |
| Regelkern, Referenzen, Vorlagen | keine muss, viele Begriffsbefunde | Runde 2: Title Case als sollte. Runde 3: nur Hinweise | abgeschlossen |
| Späte Formulierungen und README | Runde 3: 1 muss im README (Sprachwechsel durch Deinstallieren und Neuinstallieren funktioniert nicht wie beschrieben) | letzte Runde: 1 sollte (existing bug fix), Hinweise eingearbeitet, Bestätigung ohne Befund | abgeschlossen |
| Doku unter `docs/` | 4 muss (Statussemantik, umgeschriebener historischer Beleg, Dateiregel für `en`, kaputte Links) | Bestätigung: keine muss, 3 sollte und 2 Hinweise im vorgeschlagenen Wortlaut übernommen | siehe Offen |

## Code

- Umbau durch einen Opus-5.5-Agenten. Unabhängige Prüfung durch einen neuen Opus-Agenten: keine muss, 2 sollte (veraltete Doku, Kompatibilitätstest ohne Zustand aus einem früheren Update), 7 Hinweise. Nacharbeiten umgesetzt und von einem weiteren neuen Prüfagenten ohne muss und sollte am Code bestätigt.
- Tests: `python3 -B -m unittest discover -s tests`, zuletzt 179 Tests OK. Darunter ein echter Kompatibilitätstest, der 0.1.7-dev aus Commit `e9c9133` mit dem alten Installer installiert, einmal mit altem Code aktualisiert und dann mit dem neuen Code aktualisiert.

## Installation und Ladeprobe

- Englische Ersteinrichtung über `install.sh` in einem Testordner: englischer Dialog, Profil mit englischen Dateinamen, Runtime unter `general/`, 21 englische Skill-Links, englischer Kopf mit Profil-Link, Status `present`. Fehlerfall: Eine zweite Einrichtung mit vorhandenem Profilordner bricht mit „Profile target already exists“ ab, das Profil bleibt bytegleich.
- Echte deutsche Installation: Update von 0.1.7-dev auf 0.2.0-dev mit `scripts/update.py`. Ersetzt wurden 4 Dateien unter `allgemein/` und `paket.json`, 8 alte Skripte entfernt, 9 neue angelegt. Regeldateien und 42 Skill-Links blieben unverändert. Status `present` für beide Clients, `check_register.py` liefert `botticelli`, unbekanntes Kürzel wird abgelehnt.
- Ladeprobe deutsch: Claude Code und Codex nennen den neuen Aufruf `scripts/check_register.py` aus der Ablage-Referenz und Deutsch als Ausgabesprache.
- Ladeprobe englisch: `scripts/check_local_installation.py --language en` in einem erfundenen Home, ohne Anbieteraufruf. Beleg: [en-ladeprobe-20261023.json](belege/en-ladeprobe-20261023.json). Codex 0.163.0 und Claude Code 2.1.308 laden den englischen Kern vollständig und expandieren 21 Skills, Negativkontrollen bestanden, echte Skill-Links unverändert. `prepare-brief` wird wie vorgesehen nicht automatisch angeboten.

## Offen

- Englische Modellfälle mit echten Antworten sind nicht erprobt. Die englische Ladeprobe belegt nur das native Laden.
- Codex schließt Antworten mit „Unabhängig geprüft“, ohne dass ein Prüfagent im Protokoll erkennbar ist. Das trat in beiden Ladeproben auf.
- `profile_transfer.py`: Ein ausdrückliches `--language`, das nicht zum Zielordner passt, wird nicht abgelehnt (Hinweis aus der Code-Nachprüfung).
- `en/tools/materials/render.py` erzeugt weiter deutsche Ausgabedateinamen wie `01_praesentation.html`. Interne Präfixe temporärer Dateien sind deutsch. Beides deckt die Spezifikation, englische Nutzer sehen es aber.
- Ein Sprachwechsel einer bestehenden Installation braucht neue Profil- und Runtime-Ordner.
- Die Einrichtung prüft einen vorhandenen Profilordner erst nach allen Profilfragen.
- Historische Anleitungen und Prüfberichte nennen die alten Skriptnamen.
- Nicht erneut geprüft: die letzten Präzisierungen aus der Doku-Bestätigungsprüfung in `docs/grundlage.md` (Kopfsatz), `docs/englische-fassung.md` (Satz zu alten Namen), `docs/abnahme-zweiter-mac.md` (Dialogablauf, Statuskriterium), `docs/umstieg-haupt-macbook.md` (Skillquelle) und `docs/erstinstallation.md` (Sprachfrage). Sie wurden im vorgeschlagenen Wortlaut übernommen. Die Dateien gehören nicht zum Laufzeitpaket.
