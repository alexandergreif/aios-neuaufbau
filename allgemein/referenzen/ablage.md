# Ergebnisse und Projektzuordnung

Diese Referenz gilt, wenn ein Skill eine Ergebnisdatei braucht. Die bestätigte lokale `pfade.json` benennt Quellcode, Runtime, Profil, Ausgabe sowie Coding- und Kundenwurzeln. Verwende den bei der Einrichtung bekanntgegebenen Konfigurationspfad. Fehlt er, frage danach. Leite ihn nicht aus einem Benutzernamen, einem alten Skill oder einem vorgeschlagenen Standardpfad ab.

Prüfe die Konfiguration mit `scripts/pruefe_konfiguration.py --config <pfade.json>` aus dem Paket. Das Skript erzeugt keine Ordner. Ein Konfigurationswert ist keine Freigabe, die dort liegenden Inhalte zu durchsuchen.

Für eine konkrete Projektzuordnung liegt `projekte.md` im konfigurierten Profilordner. Nutze `scripts/pruefe_register.py --config <pfade.json> --register <projekte.md> --project <Kürzel>`. Nur eine aktive, eindeutige und bestätigte Zuordnung liefert einen Projektpfad. Eine fehlende, pausierte oder mehrdeutige Zuordnung klärst du, statt einen Ordner zu erraten oder auf die persönliche Ablage auszuweichen.

Kunden- und Projektergebnisse liegen im zugeordneten Projekt und beachten dessen vorhandene Ablageregeln. Persönliche Ergebnisse ohne Projektzuordnung liegen unter `paths.output`. Der installierte Paketordner, Client-Konfigurationsordner und AIOS-Quellcode sind keine Ergebnisablage. Ein beauftragter Umbau des AIOS selbst erfolgt dagegen im Quellcode.

Wähle einen verständlichen Dateinamen passend zum Auftrag. Prüfe vor dem Schreiben, ob die Datei schon existiert. Kleine beauftragte Korrekturen aktualisieren den Arbeitsstand. Umfangreiche Überarbeitungen oder das Ersetzen einer freigegebenen Fassung erhalten die vorherige Version. Nenne den tatsächlich erzeugten Pfad im Ergebnis. Eine reine Chatantwort braucht keine zusätzliche Datei, sofern der Ablauf keine Speicherung vorsieht.

Profil, Wissen und technische Ausführungsspuren sind keine Ergebnisdateien. Für sie gelten die jeweils eigenen Referenzen. Die nächste Sitzung übernimmt aus früheren Ergebnissen keine Zusage oder Erledigung ohne aktuellen Beleg.
