# Ergebnisse und Projektzuordnung

Diese Referenz gilt, wenn ein Skill eine Ergebnisdatei braucht oder ein Projektordner zugeordnet oder neu angelegt werden muss. Die bestätigte lokale `pfade.json` benennt Quellcode, Runtime, Profil, Ausgabe sowie Coding- und Kundenwurzeln. Verwende den bei der Einrichtung bekanntgegebenen Konfigurationspfad. Fehlt er, frage danach. Leite ihn nicht aus einem Benutzernamen, einem alten Skill oder einem vorgeschlagenen Standardpfad ab.

Prüfe die Konfiguration mit `scripts/pruefe_konfiguration.py --config <pfade.json>` aus dem Paket. Das Skript erzeugt keine Ordner. Ein Konfigurationswert ist keine Freigabe, die dort liegenden Inhalte zu durchsuchen.

Für eine konkrete Projektzuordnung liegt `projekte.md` im konfigurierten Profilordner. Nutze `scripts/pruefe_register.py --config <pfade.json> --register <projekte.md> --project <Kürzel>`. Nur eine aktive, eindeutige und bestätigte Zuordnung liefert einen Projektpfad. Eine fehlende, pausierte oder mehrdeutige Zuordnung klärst du, statt einen Ordner zu erraten oder auf die persönliche Ablage auszuweichen.

## Neues Projekt

Braucht ein neues Projekt einen Ordner und gibt es noch keinen, trenne nach Art. Ein Kundenprojekt liegt unter `<Kundenwurzel>/<Kunde>/<Projekt>/`, ein internes Repository ohne Kundenbezug unter `<Codingwurzel>/<Repository>/`. Die Wurzeln stehen in `paths.customer_roots` und `paths.coding_roots`. Sind Art, Kunde, Projektname oder Wurzel nicht eindeutig, frage nach. Nenne vor dem Anlegen den vollständigen Ordner und die geplante Registerzeile und lege den Ordner erst nach Bestätigung an. Lege nur die dafür nötigen Ordner an, keine Unterstruktur auf Vorrat. Trage das Projekt danach immer in `projekte.md` ein, mit eindeutigem Kürzel, absolutem Ordner ohne `~` und Status `aktiv`, und prüfe den Eintrag mit dem oben genannten Aufruf von `pruefe_register.py`. Gibt es für das Projekt schon eine Zeile mit Status `zuordnen`, ergänze diese, statt eine zweite anzulegen. Gibt es schon einen Projektordner, wird er nicht verschoben, sondern nach Bestätigung der Registerzeile nur registriert. Liegt er außerhalb der konfigurierten Wurzeln, nenne das und frage, ob eine weitere Wurzel in `pfade.json` ergänzt werden soll. Prüfe nach dem Ergänzen die Konfiguration mit `pruefe_konfiguration.py`. Ohne neue Wurzel bleibt der Ordner unregistriert, und du klärst das weitere Vorgehen.

## Ablage der Ergebnisse

Kunden- und Projektergebnisse liegen im zugeordneten Projekt und beachten dessen vorhandene Ablageregeln. Persönliche Ergebnisse ohne Projektzuordnung liegen unter `paths.output`. Dort starten auch Sitzungen ohne Projektbezug. Abgeschlossene Ordner in `paths.output` kommen nur auf Auftrag nach `paths.output/archiv/`, verschoben und nicht gelöscht. Der installierte Paketordner, Client-Konfigurationsordner und AIOS-Quellcode sind keine Ergebnisablage. Ein beauftragter Umbau des AIOS selbst erfolgt dagegen im Quellcode.

Wähle einen verständlichen Dateinamen passend zum Auftrag. Prüfe vor dem Schreiben, ob die Datei schon existiert. Kleine beauftragte Korrekturen aktualisieren den Arbeitsstand. Umfangreiche Überarbeitungen oder das Ersetzen einer freigegebenen Fassung erhalten die vorherige Version. Nenne den tatsächlich erzeugten Pfad im Ergebnis. Eine reine Chatantwort braucht keine zusätzliche Datei, sofern der Ablauf keine Speicherung vorsieht.

Profil, Wissen und technische Ausführungsspuren sind keine Ergebnisdateien. Für sie gelten die jeweils eigenen Referenzen. Die nächste Sitzung übernimmt aus früheren Ergebnissen keine Zusage oder Erledigung ohne aktuellen Beleg.
