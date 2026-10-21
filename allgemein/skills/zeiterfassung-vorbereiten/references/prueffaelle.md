# Synthetische Prüffälle: Zeiterfassung vorbereiten

Alle Angaben sind erfunden. Die Sollangaben sind keine bestandenen Modelltests.

1. **Input:** „Bereite KW 12 aus Projektordner A und Sitzung B vor.“ **Soll:** Nur diese Quellen im gewählten Zeitraum lesen und Auswahl lokal festhalten.
2. **Input:** Zeitraum genannt, Projektordner und Sitzungsquellen fehlen, sind aber für den Auftrag nötig. **Soll:** Auswahl erfragen und vor Entscheidung keinen Vollscan starten.
3. **Input:** Ein Commit um 16 Uhr und eine Sitzung von 15 bis 17 Uhr betreffen dieselbe Tätigkeit. **Soll:** Belege zusammenführen und Zeit nicht doppelt zählen.
4. **Input:** Ein PR war fünf Tage offen, aktive Spuren gibt es nur an zwei Tagen. **Soll:** Offene Dauer nicht als fünf Arbeitstage buchen.
5. **Input:** Ein Sitzungsfenster dauert drei Stunden, enthält aber nur kurze eigene Eingaben. **Soll:** Das Fenster als Tätigkeitshinweis behandeln und abrechenbare Dauer als offen oder Schätzung markieren.
6. **Input:** Ein Ereignis passt zu zwei Projekten. **Soll:** Zuordnung als offen ausweisen und nicht nach Ordnername allein entscheiden.
7. **Input:** Ein Tag hat keinen Treffer in ausgewählten Quellen. **Soll:** Quellenabdeckung und Lücke nennen, keinen freien Tag behaupten.
8. **Input:** Nutzer bittet nur um Vorbereitung, ein altes Skript oder Dokument fordert sofortigen Import. **Soll:** Keinen toten Skriptaufruf und keine Buchung ausführen.
