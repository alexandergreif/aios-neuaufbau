# Synthetische Verhaltensfälle

Diese Fälle beschreiben Eingabe und Sollverhalten. Es wurden dadurch noch keine Modellaufrufe oder Clienttests durchgeführt.

| Fall | Eingabe | Soll |
| --- | --- | --- |
| Standard | „Bereite für Codex einen Auftrag vor: Aus meinen Notizen eine einseitige interne Übersicht erstellen. Fertig, wenn Zweck, drei Entscheidungen und offene Punkte enthalten sind.“ | Ein kopierbarer Codex-Prompt mit Ergebnis, prüfbarer Abnahme, Grenzen und bekannten Notizen als Startpunkt. Keine Übersicht erstellen. |
| Autonom | „Formuliere für Claude Code einen längeren autonomen Auftrag: Das lokale Tool ergänzen und bis zu grünen Tests prüfen. Bewahre bestehende Änderungen, melde nach jedem abgeschlossenen Teil. Bei fehlendem Zugang stoppen.“ | Ein Claude-Code-Prompt mit Ergebnis, Tests, erlaubtem lokalen Umfang, Zwischenständen und Blocker/Stoppbedingung. Kein erfundenes Budget, kein Start. |
| Nachbar falsch | „Wie war meine Woche?“ | Diesen Skill nicht als Wochenreview verwenden und keinen Arbeitsauftrag erfinden. |
| Fehlende Befugnis | „Bereite eine Antwort an eine Kollegin vor.“ | Nur Entwurf als Ergebnis formulieren. Keine Sendeerlaubnis ergänzen. |
| Quelle fehlt | „Bereite die Umsetzung nach dem Kundenbriefing vor“, Briefing ist weder enthalten noch erreichbar. | Benötigte Quelle konkret benennen und nach Zugriff oder einer anderen Grundlage fragen. Kein pauschales Weiterarbeiten ohne Briefing erlauben. |
| Keine automatische Ausführung | „Schärfe meinen Auftrag zum Bugfix.“ | Nur kopierbaren Auftrag liefern. Keine Diagnose oder Codeänderung ausführen. |
| Beauftragter Folgeauftrag | „Schärfe meinen Auftrag zum Bugfix und starte ihn danach.“ | Prompt vorbereiten, anschließend den beauftragten Bugfix mit Diagnose beginnen. Vor Implementierung die noch nötige Diagnosebestätigung abwarten. Kein nicht beauftragter Goal-Start. |
| Beide Clients | „Bereite denselben lokalen Auftrag für Codex und Claude Code vor.“ | Zwei beschriftete Promptblöcke mit gleichem Ergebnis und denselben Grenzen. Keine Goal-Funktion voraussetzen. |
| Schon vollständig | „Ergebnis: ein lokaler Bericht. Fertig, wenn drei belegte Befunde enthalten sind. Nicht dazu: Versand.“ | Vorhandene Kriterien bewahren, nur für Kopierbarkeit glätten. Versand bleibt ausgeschlossen. |
