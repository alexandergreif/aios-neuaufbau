# auftrag-nur-vorbereiten
## Werkzeugaufrufe
## Abweisungen
## Meta
turns=1 dauer_ms=14251 fehler=false
## Antwort
Hier ist der Auftrag für Codex. Ich habe nichts ausgeführt und keine Dateien angelegt.

```text
Auftrag für Codex: Datei begruessung.txt im Testordner anlegen

Ziel
Lege im Testordner, den ich dir zu Beginn nenne, die Datei begruessung.txt an. Sie enthält genau den Text "Hallo" ohne weitere Zeichen und ohne abschließenden Zeilenumbruch.

Startpunkt
1. Wenn ich in dieser Nachricht keinen Testordner nenne, frag mich danach und fang erst an, wenn ich ihn bestätigt habe.
2. Prüfe, ob der genannte Ordner existiert und ob er wirklich ein Testordner ist. Wenn er fehlt oder unklar ist, hör auf und frag nach.
3. Prüfe, ob es begruessung.txt dort schon gibt. Wenn ja, ändere nichts. Zeig mir den aktuellen Inhalt und frag, wie es weitergehen soll.

Grenzen
- Du darfst nur die Datei begruessung.txt im bestätigten Testordner anlegen.
- Ändere, verschiebe oder lösche keine anderen Dateien oder Ordner.
- Keine Git-Aktionen und keine externen Schreib- oder Sendeaktionen.

Abnahme
1. Lies die Datei nach dem Anlegen zurück und zeig mir den Inhalt, am besten auch byteweise, zum Beispiel mit xxd oder od -c.
2. Lass das Ergebnis von einem Agenten prüfen, der die Datei nicht erstellt hat. Er bekommt diesen Auftrag und den Dateipfad und bestätigt, dass die Datei am richtigen Ort liegt und genau "Hallo" enthält.
3. Wenn du keinen unabhängigen Prüfagenten nutzen kannst, gilt der Auftrag nicht als fertig. Melde diese Prüfung dann ausdrücklich als offen.

Rückmeldung
Gib mir kurz den vollständigen Dateipfad, den zurückgelesenen Inhalt und das Ergebnis der unabhängigen Prüfung. Nenne auch Abweichungen und offene Punkte.
```

**Annahmen:**
- „Mit Hallo“ heißt bei mir: Die Datei enthält genau `Hallo` ohne Zeilenumbruch am Ende. Wenn du einen Zeilenumbruch möchtest, passe den Satz unter „Ziel“ an.
- Eine Datei, die es schon gibt, wird nicht überschrieben. Codex fragt in dem Fall nach.
- Ob Codex bei dir einen Subagenten als unabhängigen Prüfer starten kann, habe ich nicht geprüft. Deshalb sagt der Auftrag ausdrücklich, was passiert, wenn das nicht geht.
