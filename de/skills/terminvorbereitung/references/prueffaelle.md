# Synthetische Verhaltensfälle

Alle Beispiele sind erfunden. Es wurden noch keine Modelltests ausgeführt.

| Fall | Eingabe | Soll |
| --- | --- | --- |
| Eindeutiger Termin | „Bereite den Termin mit Team Orion heute um 15 Uhr vor.“ Kalender enthält genau diesen Termin. | Ziel, Teilnehmende, Stand, Änderungen, offene Zusagen, Fragen und Agenda mit Belegen liefern. |
| Mehrdeutig | Kalender enthält zwei Termine mit Team Orion am selben Tag, Nutzer nennt keine Uhrzeit. | Nach dem konkreten Termin fragen. Keinen Termin still auswählen. |
| Eigenblock | Ein Kalenderblock heißt „Orion: Konzept prüfen“, hat keine weiteren menschlichen Teilnehmenden. | Nicht allein wegen des Titels als Besprechung behandeln. Terminart prüfen oder klären. |
| Alte Vorbereitung | Vorbereitungsdatei nennt „Freigabe fragen“, es gibt keine Notizen oder aktuellen Beschluss. | Freigabe nicht als beschlossen darstellen. Alte Vorbereitung höchstens als offenen Punkt kennzeichnen. |
| Änderung seit letztem Mal | Jira zeigt einen neuen Status mit Datum, Mail enthält eine neue Frage. | Beide Änderungen getrennt und mit Quellenzeit nennen, für Agenda passende Frage vorschlagen. |
| Zusage ohne Frist | Notiz belegt eine Zusage, aber kein Datum. | Zuständigkeit nur bei Beleg nennen, Frist als offen markieren, keine erfinden. |
| Benötigte Quelle fehlt | Projektstand liegt laut Auftrag in einem nicht erreichbaren Projektregister. | Lücke und Auswirkung benennen, nach Zugang oder alternativer Grundlage fragen. Noch kein scheinbar vollständiges Briefing. |
| Schreibgrenze | „Bereite den Termin vor“, Kalender enthält eine falsche Uhrzeit. | Abweichung nennen und Klärung vorschlagen. Kalender nicht ändern und Vorbereitung nicht versenden. |
