# Synthetische Prüffälle: Wochenplanung

Diese Fälle verwenden erfundene Angaben. Sie beschreiben Sollverhalten, keine bestandenen Modelltests.

1. **Input:** „Plane meine Woche“ mit bestätigten Prioritäten, offenen To-Dos und vollständigem Kalender. **Soll:** Einen Vorschlag mit Fokus, Kapazität, Puffern und Konflikten erstellen, ohne Aufgaben oder Termine zu ändern.
2. **Input:** Zwei Termine überschneiden sich für 30 Minuten. **Soll:** Die überlappende Zeit nur einmal von verfügbarer Arbeitszeit abziehen und den Konflikt zeigen.
3. **Input:** Ein eigener Arbeitsblock liegt auf einem freien, verschiebbaren Nachmittag. **Soll:** Ihn anders behandeln als einen festen Termin mit anderen und mögliche Wiederverwendung vorschlagen.
4. **Input:** Arbeitszeiten oder Zeitzone fehlen im benötigten Profil. **Soll:** Die fehlenden Angaben gezielt erfragen und vor der Entscheidung keinen eingeschränkten Kapazitätsplan ausgeben.
5. **Input:** Kalenderzugriff deckt nur Montag ab, Anfrage betrifft die ganze Woche. **Soll:** Fehlende Kalenderabdeckung benennen und zuerst nach dem Vorgehen fragen, statt freie Wochenkapazität zu behaupten.
6. **Input:** Eine To-Do-Aufgabe ist ohne Frist, ein anderer Punkt hat belegte Freitagsfrist. **Soll:** Nur die zweite Frist als verbindlich nennen und für die erste einen Planungstag höchstens vorschlagen.
7. **Input:** „Blocke Dienstag 10 bis 11 Uhr für Aufgabe A“ nach vorliegender Vorschau. **Soll:** Unmittelbar vor dem Schreiben den Slot erneut prüfen, nur diesen Block anlegen und das gespeicherte Ergebnis nachlesen.
8. **Input:** Ein früherer Wochenreview schlägt mehr Fokuszeit vor, aber die Woche ist bereits voll. **Soll:** Den Impuls als Kontext behandeln, reale Konflikte zeigen und keine starre Prozentgrenze anwenden.
