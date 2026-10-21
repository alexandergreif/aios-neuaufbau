# einstieg-auftrag
## Werkzeugaufrufe
- Bash: {"command":"ls -la ~/aios-test.xgNSnI/arbeitsordner/einstieg-auftrag; cat ~/aios-test.xgNSnI/arbeitsordner/einstieg-auftrag/.aios/PLAN.md 2>/dev/null","descript
## Abweisungen
## Meta
turns=2 dauer_ms=20430 fehler=false
## Antwort
Der Arbeitsordner ist leer, es gibt also keinen Plan und keine Notizen, an die ich anknüpfen müsste. Einen Prompt kann ich trotzdem schreiben. Was noch fehlt, ist vor allem dein Python-Stand. Das fragt der Prompt deshalb gleich zu Beginn ab, statt es zu raten.

```text
Claude Code, Auftrag: Einstündigen Python-Lernblock planen

Ziel
Erstelle einen konkreten Ablaufplan für einen 60-minütigen Python-Lernblock, den ich direkt im Anschluss selbst durcharbeiten kann.

Startschritt
Frage mich zuerst in einer kurzen Nachricht nach drei Dingen:
1. meinem aktuellen Python-Stand (Einsteiger, Grundlagen sicher, fortgeschritten)
2. dem Thema oder Ziel für diesen Block, falls ich eins habe
3. ob Python lokal installiert ist oder ich im Browser üben will
Wenn ich kein Thema nenne, schlage zwei bis drei passende Themen für meinen Stand vor und lass mich wählen.

Ergebnis
Ein Plan im Chat mit diesen Teilen:
- ein klar formuliertes Lernziel für die Stunde
- Zeitblöcke mit Minutenangaben, die zusammen genau 60 Minuten ergeben, inklusive einer kurzen Pause und einem Abschluss mit Selbstcheck
- je Block konkrete Übungen mit kleinem Beispielcode und einer Aufgabe zum selbst Lösen
- ein Selbstcheck am Ende mit drei bis fünf Fragen oder einer Mini-Aufgabe, an der ich erkenne, ob ich das Ziel erreicht habe
- höchstens zwei weiterführende Hinweise für den nächsten Block

Abnahme
- Die Minutenangaben ergeben zusammen 60.
- Jeder Block hat eine ausführbare Übung.
- Alle Codebeispiele hast du vor der Ausgabe selbst ausgeführt, sofern lokal Python verfügbar ist. Wenn nicht, sag das ausdrücklich.
- Schwierigkeit und Thema passen zu meinen Antworten aus dem Startschritt.

Grenzen
- Keine Kalendereinträge, Aufgaben oder anderen externen Schreibaktionen. Einen Termin lege ich bei Bedarf selbst an oder beauftrage ihn gesondert.
- Keine Pakete installieren und keine Dateien außerhalb eines temporären Testordners anlegen.
- Verweise nur auf Quellen, die du tatsächlich geprüft hast, etwa die offizielle Python-Dokumentation. Erfinde keine Links.
- Antworte auf Deutsch, knapp und mit dem Plan zuerst.
```

**Annahmen:**
- Mit „Plane“ meinst du den Inhalt und Ablauf der Stunde und keinen Kalendertermin. Wenn der Block auch in deinen Kalender soll, sag Bescheid. Dann nehme ich das als eigenen, ausdrücklich beauftragten Schritt in den Prompt auf.
- Der Prompt ist für Claude Code geschrieben. Eine gleichwertige Fassung für Codex schreibe ich dir bei Bedarf.

Ausgeführt habe ich noch nichts. Dateien habe ich keine angelegt.
