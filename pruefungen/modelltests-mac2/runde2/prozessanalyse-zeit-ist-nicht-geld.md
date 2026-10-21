# prozessanalyse-zeit-ist-nicht-geld (Runde 2, Paket 0.1.1-dev)
## Werkzeugaufrufe
- Bash: {"command":"ls -la ~/aios-test.xgNSnI/arbeitsordner/runde2-prozessanalyse-zeit-ist-nicht-geld ~/aios-test.xgNSnI/arbeitsordner/runde2-prozessanalyse-zeit-ist-ni
- Agent: {"description":"Prüfung Prozessanalyse-Entwurf","subagent_type":"general-purpose","model":"sonnet","run_in_background":false,"prompt":"Du bist unabhängiger Prüfer. Prüfe den folgenden Entwurf rein inh
- SendMessage: {"to":"aa1cd203127544841","summary":"Nachprüfung überarbeiteter Stellen","message":"Bitte prüfe nur diese überarbeiteten Stellen, knapp: Passen sie jetzt?\n\nKOPF: \"**Kurz:** Die Hypothese „doppelte 
- Agent: {"description":"Warten auf Nachprüfung","subagent_type":"general-purpose","model":"haiku","run_in_background":false,"prompt":"Antworte nur mit \"ok\". Keine Werkzeuge nutzen."}
## Meta
turns=5 fehler=false denials=0
turns=1 fehler=false denials=0
## Antwort (letztes result)
**Kurz:** Die Hypothese, dass doppelte Eingaben die Nacharbeit verursachen, ist plausibel, aber nicht belegt. Wenn die Ursache stimmt und die Lösung wirklich die Hälfte vermeidet, werden für diese zehn Vorgänge bis zu 2,5 Stunden Arbeitszeit frei. Vermiedene Auszahlungen sind nicht belegt. Ich setze sie deshalb mit 0 € an.

## Was belegt ist und was nicht

| Aussage | Status |
|---|---|
| 10 Vorgänge, im Mittel je 30 Minuten Nacharbeit | gemessen |
| Ursache sind doppelte Eingaben | Vermutung des Teams, unbelegt |
| Lösung vermeidet die Hälfte der Nacharbeit | ungeprüfte Annahme |
| Gleiche Belegschaft, gleiche Bezahlung | gesetzte Rahmenbedingung |
| Keine belegte Änderung bei Fremdkosten | gesetzte Rahmenbedingung |

Drei Dinge fehlen noch: der Zeitraum der zehn Vorgänge, die Gesamtzahl der Vorgänge in diesem Zeitraum und die Streuung um den Mittelwert. Ein Mittel von 30 Minuten kann auch aus wenigen sehr langen Fällen entstehen. Außerdem ist zu klären, ob die 30 Minuten reine Arbeitszeit sind. Wartezeit auf Rückfragen gehört nicht hinein.

## Nächste Ursachenprüfung

Die Vermutung soll bestätigt oder verworfen werden, bevor jemand eine Lösung baut.

1. **Grund der Nacharbeit je Fall erfassen.** Für jeden der zehn Vorgänge festhalten, was konkret nachgearbeitet wurde und wie lange es gedauert hat. Dabei klären, ob eine doppelte Eingabe vorkommt und ob sie die Nacharbeit tatsächlich erklärt.
2. **Gegenfälle ansehen.** Vorgänge ohne Nacharbeit aus demselben Zeitraum prüfen. Kommen dort genauso doppelte Eingaben vor, reichen sie als Erklärung nicht aus.
3. **Andere Ursachen mitprüfen**, geordnet nach Ishikawa-Kategorie:
   - *Methode:* Der Ablauf verlangt dieselben Daten an zwei Stellen. Das ist die Vermutung des Teams.
   - *Software:* Es fehlt eine Schnittstelle oder eine Plausibilitätsprüfung.
   - *Daten:* Die Eingangsdaten sind unvollständig oder fehlerhaft und müssen unabhängig von der doppelten Eingabe korrigiert werden.
   - *Messung:* Was als Nacharbeit zählt, ist nicht einheitlich festgelegt.
4. **Entscheidungsregel vorher festlegen.** Ein Beispiel: Die Hypothese gilt als gestützt, wenn doppelte Eingaben in mindestens 6 von 10 Fällen vorkommen und mindestens die Hälfte der gesamten Nacharbeitszeit erklären. Sonst wird zuerst die stärkere andere Ursache verfolgt.

Schritt 1 hat Vorrang. Er betrifft alle zehn Fälle mit gemessener Nacharbeit, schließt die größte Beleglücke und lässt sich sofort umsetzen. Warum-Fragen lohnen sich erst, wenn feststeht, welche Ursache die meiste Zeit kostet.

## Vorsichtige Nutzenabschätzung

| Größe | Rechnung | Art |
|---|---|---|
| Nacharbeit gesamt | 10 × 30 Min. = 300 Min. = 5 Std. | gemessen |
| Vermeidbarer Anteil | 50 % | ungeprüfte Annahme |
| Frei werdende Arbeitszeit | bis zu 150 Min. = 2,5 Std. | Schätzung, nur für diese 10 Vorgänge |
| Vermiedene Auszahlungen | 0 € angesetzt | Rahmenbedingung: gleiche Bezahlung, keine belegte Änderung bei Fremdkosten |

Die 2,5 Stunden sind frei werdende Kapazität und kein eingespartes Geld. Die Löhne laufen unverändert weiter. Einen wirtschaftlichen Nutzen gibt es erst, wenn die frei werdende Zeit nachweislich anders genutzt wird oder Auszahlungen tatsächlich sinken, zum Beispiel für bezahlte Überstunden. Das müsste eigens belegt werden.

Die 50 % sind keine sichere Untergrenze. Sind doppelte Eingaben nur für einen Teil der Nacharbeit verantwortlich, sinkt der Nutzen entsprechend. Auf Monat oder Jahr lässt sich erst hochrechnen, wenn Zeitraum und Fallzahl bekannt sind.

**Nächster Schritt:** Die zehn Vorgänge einzeln nach Grund und Dauer der Nacharbeit auswerten und einige Vorgänge ohne Nacharbeit zum Vergleich heranziehen.

Ein unbeteiligter Prüfagent hat den Entwurf geprüft und danach die überarbeiteten Stellen nachgeprüft. Seine Hinweise sind eingearbeitet. Die letzte kleine Änderung bei der Einstufung der 50 % wurde nicht mehr eigens nachgeprüft. Ich habe keine Dateien angelegt und nichts gespeichert.
