# Prüfung der Regelkernänderung 0.1.7-dev

Stand: 23.10.2026. Umsetzung von Entscheidung 121: Ablageregel für neue Projekte, Ausgabesprache aus dem Profilfeld Sprache, alte Migrationsordner in `~/aios-output` archiviert.

## Geänderte Dateien

- `allgemein/regeln/kern.md`: Ein neues Projekt bekommt seinen Ordner nach der Ablage-Referenz und erst nach Bestätigung, danach folgt der Registereintrag. Ausgabesprache aus dem Feld Sprache in `profil.md`, bei mehreren Angaben die zuerst genannte, sonst Deutsch. Gilt für Antworten und neue Texte. Vorhandene Dateien und Repositorys mit eigener Sprache behalten diese. Ein ausdrücklicher Sprachwunsch hat Vorrang.
- `allgemein/referenzen/ablage.md`: Abschnitt „Neues Projekt“ mit Trennung nach Art (`<Kundenwurzel>/<Kunde>/<Projekt>/`, `<Codingwurzel>/<Repository>/`), Bestätigung vor dem Anlegen, Registerpflicht, Umgang mit `zuordnen`-Zeilen, vorhandenen Ordnern und Ordnern außerhalb der Wurzeln. Abschnitt „Ablage der Ergebnisse“: Sitzungen ohne Projektbezug in `paths.output`, Archiv `paths.output/archiv/` nur auf Auftrag.
- `allgemein/referenzen/profil-und-wissen.md`: Das Feld Sprache bestimmt die Ausgabesprache, bei mehreren Sprachen nach der bevorzugten fragen.
- `scripts/installieren.py`: Der Kopf der generierten Regeldateien verlinkt zusätzlich `profil.md` im Profilordner.
- `tests/test_installieren.py`, `tests/test_paketbetrieb.py`: Profil-Link nach Installation und nach Update geprüft.
- `scripts/paket_bauen.py`, `tests/test_paket_bauen.py`: Version 0.1.7-dev.
- `docs/regelabgleich.md`: Nachträge zu Entscheidung 121.

## Prüfrunden

Jede Runde lief mit einem neu gestarteten Prüfagenten (Opus 5.5) mit vollständiger Fassung.

| Runde | Ergebnis | Umgang |
| --- | --- | --- |
| 1 | keine muss, 3 sollte (Bestätigung vor Anlage, Ordner außerhalb der Wurzeln, Geltungsbereich der Sprachregel), 6 Hinweise | alle umgesetzt bis auf Hinweis 6 (Archivregel als vertretbar eingestuft) |
| 2 | keine muss, keine sollte, 3 Hinweise | umgesetzt |
| 3 | keine muss, keine sollte, 3 Hinweise | umgesetzt |
| 4 | keine Befunde | abgeschlossen |

Tests nach jeder Änderung: `python3 -B -m unittest discover -s tests`, zuletzt 145 Tests OK.

## Archiv

Auf Freigabe von Alexander am 23.10.2026 zehn Migrationsordner nach `~/aios-output/archiv/2026-10-migration/` verschoben, nichts gelöscht. Liste mit Größe und Datum in `LISTE.tsv` daneben.

## Installation und Ladeprobe

- Update mit `scripts/aktualisieren.py` von 0.1.6-dev auf 0.1.7-dev. Ersetzt wurden Kern, beide Referenzen, beide globalen Regeldateien, die Runtime-Kopien und `paket.json`. Der erste Lauf ohne Eingabe hielt an der Bestätigung an, ohne etwas zu ändern. Der zweite Lauf mit `ja` war erfolgreich.
- Statuscheck: `vorhanden` für Claude Code und Codex, je 21 Skillverknüpfungen, Integrität geprüft.
- Claude Code (`claude -p` mit Lesezugriff auf Profil und Runtime): neuer Kernsatz wörtlich, Profil-Link aus dem Kopf, Feld Sprache „Deutsch, English“ gelesen, Ausgabesprache Deutsch, Ablageregel mit Bestätigung korrekt wiedergegeben.
- Codex 0.163.0 (`codex exec --sandbox read-only`): Profil-Link, Sprachfeld, Ausgabesprache und Ablageregel korrekt. Bei der Frage nach dem letzten Satz des ersten Absatzes zitierte Codex den letzten Satz des zweiten Absatzes. Eine gezielte Nachfrage ohne Werkzeuge ergab beide neuen Kernsätze wörtlich aus dem geladenen Kontext.

## Offen

- Codex schloss die erste Probe mit „Unabhängig gegengeprüft“, ohne dass ein Prüfagent im Protokoll erkennbar ist. Ob der Satz begründet war, ist nicht belegt.
- Codex meldet beim Start Fehler für nicht angemeldete MCP-Server (Sentry, GitHub Copilot, ein Server mit ungültigem Port). Das gehört zu Schritt 7.
- `scripts/einrichten.py` fragt nur „Sprache:“ und nicht nach der bevorzugten Sprache bei mehreren Angaben. Die Vorgabe greift bisher nur bei Einrichtung durch einen Agenten.
- Ob die Modelle die Ablageregel bei einem echten neuen Projekt befolgen, ist nicht mit Modellfällen erprobt.
