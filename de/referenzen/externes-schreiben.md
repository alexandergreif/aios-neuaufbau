# Externe Schreibaktionen sicher ausführen

Bei einem konkreten Auftrag zum Schreiben im Zielsystem verwenden. Diese Referenz erteilt keine Befugnis und ersetzt keine dienstspezifische Rechteprüfung. Ein bereits eindeutig beauftragter Inhalt braucht keine erneute Freigabe. Fehlen Ziel, Inhalt oder Umfang, diese vor dem Schreiben klären.

## Vorbereiten

Zielkonto, Dienst, Objekt und beauftragte Änderung eindeutig bestimmen. Stabile Objektkennungen verwenden. Vorhandenen Zustand und mögliche Dubletten lesen. Eine Vorbereitung oder Zusammenfassung ist kein Auftrag zum Anlegen einer Aufgabe oder Versenden einer Nachricht.

Im privaten Profilordner unter `zustand/aktionen/` eine minimale lokale Ausführungsspur führen. Erforderlich sind Aktionskennung, Dienst, Ziel, Zeitpunkt, Status und bekannte Objektkennungen. Eine kurze Aktionsart wie „Termin verschieben“ genügt. Keine vollständigen Nachrichten, Transkripte oder Zugangsdaten speichern. Benötigte Originalinhalte bleiben im berechtigten Quellsystem oder einem gesondert beauftragten Ergebnisartefakt.

## Ausführen und nachlesen

1. Vor dem externen Aufruf Status „gestartet“ festhalten.
2. Nur die konkret beauftragte Änderung senden.
3. Ergebnis anhand Zielkonto und Objektkennung nachlesen, relevante Felder mit dem Auftrag vergleichen. Erst nach Nachweis als „bestätigt“ melden.
4. Bei Timeout, Abbruch oder nicht eindeutigem Resultat Status „ungeklärt“ führen. Zuerst im Zielsystem prüfen, ob die Aktion ausgeführt wurde. Ein Zeitablauf allein belegt keine Nichtausführung.
5. Nur bei belegter Nichtausführung und fortbestehendem Auftrag einen erneuten Versuch vorsehen. Bleibt der Zustand unklar, den betroffenen Schritt stoppen und nachfragen. Erfolgreiche andere Aktionen konkret melden, nicht automatisch zurücknehmen.

Eine lokale Aktionskennung garantiert keine Idempotenz im externen Dienst. Wenn das Zielsystem einen eigenen Idempotenzschlüssel unterstützt, muss der Adapter dessen tatsächliches Verhalten prüfen. Der Nachweis eines bereits ausgeführten Auftrags verhindert dessen doppelte Ausführung. Ein neuer eigenständiger Auftrag bekommt eine neue Kennung.

## Grenzen

- Kalender: vor Änderung Verfügbarkeit und aktuellen Objektstand erneut prüfen. Eine Terminserie nicht statt des beauftragten Einzeltermins ändern.
- Planhat: bestätigte Einträge per MCP als Entwurf übertragen, Dubletten prüfen und nachlesen. Endgültige Abgabe bleibt manuell.
- Fehlender benötigter Zugang: zuerst fragen. Die bloße Existenz eines API-Schlüssels belegt keine Rechte oder Freigabe.
- Das Journal ist keine Aufgabenliste, kein Gedächtnisimport und kein vollständiges Kommunikationsarchiv. Technische Installationsprotokolle bleiben davon getrennt.

Der ausführbare Journalablauf und die dienstspezifischen Adapter sind noch zu bauen und mit synthetischen Fehlerfällen zu prüfen.
