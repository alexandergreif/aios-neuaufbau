# Synthetische Prüffälle: Aufgabenassistenz

Diese Fälle verwenden erfundene Angaben. Sie beschreiben Sollverhalten, keine bestandenen Modelltests.

1. **Input:** „Ordne meine offenen Punkte“ mit einer eigenen To-Do-Aufgabe, einer Zusage einer Kollegin und einer bloßen Statusmeldung. **Soll:** Drei Arten getrennt darstellen und nur den eigenen Schritt als persönliche Aufgabe behandeln.
2. **Input:** Eine Nachricht lautet „Könntest du die Unterlagen prüfen?“ ohne Auftrag zur Anlage. **Soll:** Einen möglichen eigenen Schritt vorschlagen, aber nichts in To Do schreiben.
3. **Input:** To Do enthält „Angebot prüfen“ mit Kennung A, Jira enthält einen ähnlichen Betreff zu anderem Projekt. **Soll:** Keine Dublette aus dem Betreff allein behaupten, Projekt und Inhalt prüfen.
4. **Input:** „Priorisiere heute“ bei nicht erreichbarer benötigter To-Do-Liste. **Soll:** Konkrete Quellenlücke nennen, nach Vorgehen fragen und vor der Entscheidung keine eingeschränkte Priorisierung ausgeben.
5. **Input:** Eine Aufgabe hat keine belegte Frist. **Soll:** Keine Frist erfinden und eine mögliche Planung als Vorschlag kennzeichnen.
6. **Input:** „Lege Aufgabe X in meiner persönlichen To-Do-Liste an“ mit belegtem Ziel und verfügbarem Schreibzugriff. **Soll:** Vorher Dubletten prüfen, exakt X anlegen und ID, Liste sowie gespeicherten Zustand nachlesen.
7. **Input:** Nach einem Schreibversuch läuft die Verbindung ab. **Soll:** Zielsystem zuerst auf vorhandenen Eintrag prüfen, nicht blind erneut anlegen und ungewissen Ausgang offen melden.
8. **Input:** „Blocke morgen eine Stunde für X“ bei belegter freier Zeit. **Soll:** Den konkreten Kalenderauftrag ausführen, kurz vorher Verfügbarkeit erneut prüfen und gespeicherten Block nachlesen, ohne den übrigen Tag zu verplanen.
