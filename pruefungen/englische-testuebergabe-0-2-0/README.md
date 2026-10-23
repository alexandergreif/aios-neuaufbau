# Vollständige englische AIOS-Testübergabe, 0.2.0-dev

Stand: 23.10.2026. Alexander möchte dem Kollegen das komplette AIOS zum Testen geben. Die vorherige Eingrenzung auf einen begleiteten Codex-Pilot ist damit als Übergabeumfang ersetzt. Das bisherige Pilotarchiv bleibt als frühere Fassung erhalten.

## Ergebnis und Übergabe

[Vollständiges englisches Testpaket](aios-0.2.0-dev-en-full-test.zip), Quellcommit `4504e8f4954f77cbcaa8eec30e177f738433cdf6`. Das Archiv enthält alle versionierten Quelldateien dieses Stands und zusätzlich die neue vollständige englische Testanleitung als `START-HERE.md` sowie `TEST-MANIFEST.json`. Alle 21 englischen Skills, beide Clienteinbindungen, Profil- und Registervorlagen, gebündelte Werkzeuge sowie Einrichtung, Status, Update und Deinstallation sind enthalten. Der Nutzer wählt Claude Code, Codex oder beide. Es wurden keine Funktionen für diesen Testumfang deaktiviert oder entfernt.

Die [englische Testanleitung](../../docs/english-full-test.md) enthält die vollständige Skillliste, Einrichtung, einen vorgeschlagenen Testablauf über die Fähigkeiten und den Betrieb, Rückmeldekriterien sowie bekannte Fehler. Sie ist ausdrücklich keine Aussage, dass alle Funktionen bereits abgenommen seien.

Vollständige Paketlieferung umfasst keine persönlichen Konten, Zugänge, Connectorrechte oder Lizenzen des Kollegen. Diese müssen für verbundene Fähigkeiten in dessen Client passend eingerichtet sein. Ein fehlender Zugang ist im Testbericht als fehlende Voraussetzung zu erfassen.

## Lokale Prüfung des tatsächlichen ZIP

Das Paket wurde aus dem ZIP in einem erfundenen Benutzerordner installiert, ohne Anbieteraufrufe und ohne Änderungen an der aktiven Installation:

- Erstinstallation erfolgreich. Englischer Status `present` für Claude Code und Codex, je 21 Skillverknüpfungen, alle 73 Runtime-Dateien entsprechen dem Manifest.
- Zweite Installation wird mit Exitcode 1 abgewiesen, das erfundene Profil bleibt unverändert.
- Vorschau und Ausführung eines Updates auf denselben Versionsstand erfolgreich. Diese Probe ist kein neuer Versionswechseltest.
- Vorschau und Ausführung der Deinstallation erfolgreich. Die beiden globalen Client-Regeldateien werden entfernt. Profil und eine absichtlich hinzugefügte fremde Runtime-Datei bleiben erhalten.

[Maschinenlesbare Ergebnisse](checks.json), [Erzeugung des Vollpakets](prepare_full_test.py), [gemeinsam verwendeter Archivprüfer](../englische-pilotuebergabe-0-2-0/prepare_pilot.py).

Die Paketprobe verwendet eine vorbereitete Konfiguration und ersetzt keinen neuen vollständigen interaktiven Einrichtungsdurchgang. Sie prüft die Dateieinbindung beider Clients, keine neuen Claude- oder Codex-Modellantworten. Anleitung, Archivinhalt, Manifest, Prüfergebnisse und Aussagen dieses Berichts wurden durch einen unbeteiligten Codex-Prüfagenten unabhängig geprüft.

## Mitzugebender Prüfstand

- Sieben fachliche englische Codex-Fälle erfüllen die festgelegten Erwartungen. Zwei unbelegte Meldungen über abgeschlossene unabhängige Prüfung sind dokumentiert. Der positive native unabhängige Prüfpfad bleibt offen. [Beleg](../modelltests-en-0-2-0/README.md).
- Englische native Ladung beider Clients belegt. Gleichwertige englische Claude-Verhaltenstests, reale Dienstabnahmen und visuelle Rendererabnahme bleiben offen.
- Die fünf zuletzt offenen Dokumentpräzisierungen sind unabhängig ohne Befund nachgeprüft.
- Sprachwechsel, späte Profilkonflikterkennung, Sprachkonflikte beim Profiltransfer und teilweise deutsche Renderer-Dateinamen sind in `START-HERE.md` benannt.

Diese Einschränkungen sind Testgegenstände und bekannte Befunde des vollständigen Entwicklungsstands. Sie sind keine Reduzierung der gelieferten Fähigkeiten. Es wurden weder vorhandene Regeln korrigiert noch ein behobener Prüfungsfehler behauptet.

## Stand der Verteilung

Das ZIP ist lokal zur Übergabe an Alexander vorbereitet. Es wurde nicht an den Kollegen gesendet oder extern veröffentlicht. Für eine Dateiübergabe kann das vollständige ZIP verwendet werden. Für eine GitHub-Übergabe bleibt ein konkret festzulegender Commit-/Push-Stand und gegebenenfalls Kollegenzugriff notwendig. Das ältere Pilot-ZIP ist für den hier bestätigten vollständigen Testumfang durch dieses neue Paket ersetzt.

SHA256 des vollständigen Testpakets:

```text
3916762b85883768993d18464e17e6c3fa623eb646528a99760009e883bb84b7
```
