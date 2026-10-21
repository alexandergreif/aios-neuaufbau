# prozessanalyse-zeit-ist-nicht-geld
## Werkzeugaufrufe
- Bash: {"command":"ls -la && cat .aios/PLAN.md .aios/NOTIZEN.md 2>/dev/null","description":"Arbeitsordner und Projektnotizen prüfen"}
- Agent: {"description":"Prüfung Prozessanalyse-Entwurf","model":"sonnet","run_in_background":false,"prompt":"Du bist unabhängiger Prüfer. Prüfe den folgenden Antwortentwurf gegen Auftrag und Regeln. Antworte 
- ToolSearch: {"query":"select:SendMessage","max_results":1}
- SendMessage: {"to":"abb5f80d4b2c4064e","summary":"Echten Entwurf zur Prüfung senden","message":"Hier ist der echte Entwurf zur Prüfung nach denselben Regeln. Antworte knapp mit Befunden oder \"keine Befunde\".\n\n
## Abweisungen
## Meta
turns=5 dauer_ms=33545 fehler=false
turns=1 dauer_ms=18671 fehler=false
## Antwort
Ich warte gerade auf den unabhängigen Prüfer, der den Entwurf gegenliest. Danach bekommst du die Einordnung.
**Kurz gesagt:** Die Nacharbeit ist gemessen, die Ursache „doppelte Eingaben“ nicht. Wenn die geschätzte Halbierung eintritt, werden bei diesen 10 Vorgängen bis zu 2,5 Stunden Arbeitszeit frei. Belegte Auszahlungen sinken dadurch nicht.

**Was vorliegt**
- **Gemessen:** 10 Vorgänge mit im Mittel 30 Minuten Nacharbeit je Vorgang.
- **Daraus gerechnet:** zusammen rund 300 Minuten, also 5 Stunden.
- **Berichtet:** Das Team vermutet doppelte Eingaben als Ursache. Einen Beleg gibt es dafür noch nicht.
- **Schätzung:** Eine Lösung könnte die Hälfte der Nacharbeit vermeiden.

Offen sind der Zeitraum der 10 Vorgänge, die Streuung um den Mittelwert und was genau als „Nacharbeit“ zählt. Ich nehme an, dass aktive Arbeitszeit gemeint ist und keine Liege- oder Durchlaufzeit. Das sollte noch jemand bestätigen. Zehn Fälle sind außerdem eine kleine Basis, deshalb können einzelne Ausreißer den Mittelwert stark verschieben.

**Nächste Ursachenprüfung**
1. **Jeden Vorgang einzeln aufnehmen:** Was wurde nachgearbeitet, wie lange hat es gedauert und war eine doppelte Eingabe beteiligt? Grundlage sind die 10 vorhandenen Vorgänge sowie Angaben der Bearbeitenden oder Systemprotokolle, soweit vorhanden. Dieser Schritt hat Vorrang, weil er die größte Beleglücke mit vorhandenem Material schließt und alle weiteren Schritte darauf aufbauen.
2. **Gegenfälle auswerten:** Gibt es Nacharbeit ohne doppelte Eingabe? Gibt es doppelte Eingaben ohne Nacharbeit? Beides würde die Hypothese schwächen.
3. **Andere Erklärungen gleich mit erfassen**, und zwar nur die plausiblen Ishikawa-Äste:
   - **Daten:** unvollständige oder fehlerhafte Eingangsdaten
   - **Methode:** unklare Regeln oder Übergaben
   - **Software:** fehlende Prüfungen oder Übernahmen zwischen Systemen
   - **Messung:** Was zählt als Nacharbeit, und wer erfasst sie wie?
4. **Warum-Fragen weiterführen**, wenn doppelte Eingaben in einem relevanten Teil der Fälle tatsächlich zu Nacharbeit führen: Warum wird überhaupt doppelt eingegeben? Ab welchem Anteil das als „relevant“ gilt, sollte das Team vorher festlegen. Das ist mein Vorschlag, eine Vorgabe dafür gibt es nicht. Reichen die 10 Fälle nicht für eine klare Aussage, braucht es weitere Vorgänge als Stichprobe.

**Vorsichtige Nutzenabschätzung**
- **Basis:** 5 Stunden Nacharbeit in 10 Vorgängen, aus dem gemessenen Mittelwert gerechnet.
- **Annahme:** Die Lösung vermeidet die Hälfte. Das ergibt bis zu 2,5 Stunden frei werdende Arbeitszeit für diese 10 Vorgänge.
- **Einschränkung:** Das setzt voraus, dass doppelte Eingaben die Ursache sind. Trifft das nur auf einen Teil der Fälle zu, fällt der Effekt kleiner aus. Die Hälfte ist eine Schätzung und keine belegte Obergrenze.
- **Hochrechnung:** Für Monat oder Jahr ist das noch nicht möglich, weil Zeitraum und Fallvolumen fehlen.

**Geld**
Nach jetzigem Stand werden **0 Euro an Auszahlungen vermieden**. Alle Beschäftigten bleiben mit gleicher Bezahlung angestellt, und bei den Fremdkosten gibt es keine belegten Änderungen. Die 2,5 Stunden sind also Kapazität und keine Ersparnis. Einen Nutzen bringen sie erst, wenn die Zeit tatsächlich nutzbar ist und für andere Arbeit eingesetzt wird. Einen Stundensatz rechne ich nicht ein, weil keiner vorliegt. Die Lösung selbst kann dagegen neue Auszahlungen auslösen, etwa für die Einführung oder Anpassungen. Diese müssten in einer echten Wirtschaftlichkeitsrechnung abgezogen werden.

**Was noch erhoben werden muss**
- Zeitraum und Fallvolumen
- Nacharbeitsgrund je Vorgang
- Definition der Nacharbeit
- Streuung der Nacharbeitszeiten
- Kosten der möglichen Lösung
- Wofür die frei werdende Zeit konkret genutzt würde

Ein unabhängiger Prüfagent hat den Entwurf gegengelesen. Seine Hinweise sind eingearbeitet: Die 5 Stunden sind jetzt als gerechnet gekennzeichnet, „höchstens“ ist durch „bis zu“ ersetzt und die Reihenfolge der Prüfschritte ist begründet. Außerdem sind die Schwelle als Vorschlag markiert und die Stichprobengröße sowie die Lösungskosten ergänzt. Eine zweite Prüfung der überarbeiteten Stellen ist noch offen.
