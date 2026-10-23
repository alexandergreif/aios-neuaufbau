# Englische Kollegenübergabe am 23.10.2026

Der lokale Kandidat ist für einen begleiteten Codex-Pilot vorbereitet. Die Entscheidung, ob die bekannte Prüfeinschränkung für diesen Pilot akzeptiert wird oder zuerst behoben werden soll, steht noch aus. Es wurde nichts veröffentlicht oder an Kollegen gesendet.

## Was für heute vorbereitet ist

- Englischer Quellstand `0.2.0-dev`, Commit `4504e8f`.
- Sieben fachliche englische Codex-Fälle mit erfüllten Erwartungen. Zwei unbelegte Prüfungserfolgsmeldungen bleiben ein dokumentierter Befund. [Modelltestbericht](../modelltests-en-0-2-0/README.md).
- Alle fünf bisher offenen Dokumentpräzisierungen durch einen neuen unbeteiligten Codex-Prüfagenten anhand vollständiger Fassungen und des Codes nachgeprüft. Ohne Befund im geprüften Umfang. Das schließt diese Doku-Restprüfung, keine weitere Funktionsabnahme.
- [Englische Startanleitung](../../docs/english-pilot.md) mit Voraussetzungen, Codex-Auswahl im Installer, zwei synthetischen Ersttests, Rückmeldedaten und bekanntem Prüfungsfehler.
- [Lokaler ZIP-Kandidat](aios-0.2.0-dev-english-pilot-candidate.zip) aus den versionierten Dateien des genannten Commits. Zusätzlich enthalten sind `START-HERE.md` und ein Manifest mit Quellcommit und SHA256 je Datei. Keine unversionierten Modelltestdaten oder lokalen Profile aus dem Arbeitsstand wurden übernommen.
- Installation aus genau diesem ZIP in einem erfundenen Benutzerordner erfolgreich. Der Dateistatus ist `present`, 21 englische Skillverknüpfungen und alle 73 Runtime-Dateien stimmen. Die zweite Installation wird abgewiesen, das erfundene Profil bleibt unverändert. [Nachweise](checks.json).

Die Paketprobe verwendet den Installer mit einer vorbereiteten synthetischen Konfiguration. Sie ist kein erneuter vollständiger interaktiver Einrichtungsdurchgang. Es gab dabei keine Anbieteraufrufe. Der Kandidat und die Startanleitung wurden abschließend unabhängig gegen Auftrag, vollständige Inhalte, Nachweise und Archiv geprüft.

## Was vor dem Verteilen noch zu entscheiden beziehungsweise zu tun ist

1. **Umfang bestätigen:** Empfehlung für heute ist ein begleiteter Codex-Pilot mit ausdrücklich offener unabhängiger Prüfungsfunktion. Aussagen wie „Independent review completed“ dürfen ohne tatsächlichen Prüfagenten und dessen Ergebnis nicht als Prüfnachweis gelten. Falls diese Funktion vor der Übergabe zuverlässig arbeiten muss, bleibt zuerst die Diagnose und anschließende Korrektur mit erneuter Abnahme notwendig.
2. **Diesen eindeutigen Kandidaten verteilen:** Für eine direkte Dateiübergabe sind ZIP und `START-HERE.md` vorbereitet. Für eine Übergabe über GitHub fehlen noch ein konkret beauftragter Commit und Push des gewünschten Übergabestands sowie gegebenenfalls der Kollegenzugriff auf das private Repository. Der aktuelle Remote-Stand `main` ist weiterhin `2ec24cb`, also 0.1.6-dev. Ein normales Klonen von `main` liefert die neue englische Fassung noch nicht.
3. **Erste Rückmeldung einsammeln:** Zuerst Installation und die zwei Prompts aus `START-HERE.md` testen lassen. Version, Ergebnis und bereinigte Fehlermeldungen festhalten. Erst danach den Pilotumfang erweitern.

Die Dienstanbindungen, Claude-Verhaltenstests und die visuelle Rendererabnahme bleiben außerhalb dieses begrenzten Pilots. Weitere bekannte Einschränkungen wie der Sprachwechsel mit neuen Profil- und Runtime-Ordnern müssen bei entsprechendem Einsatz berücksichtigt werden. Der normale Ersttest braucht weder einen Sprachwechsel noch diese Dienstanbindungen.

## Integrität des lokalen Kandidaten

SHA256 der ZIP-Datei:

```text
e341b86c1137e594c7b57adf46ea53775e2d6af210a188362f7b3cf3b0f9d5a3
```

Die Quelle im ZIP bleibt Commit `4504e8f4954f77cbcaa8eec30e177f738433cdf6`. Die zusätzliche Anleitung ist in `PILOT-MANIFEST.json` gesondert benannt. Das Paket ist ein lokaler Testkandidat und keine Veröffentlichung.
