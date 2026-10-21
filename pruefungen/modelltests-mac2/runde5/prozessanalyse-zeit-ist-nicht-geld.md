# prozessanalyse-zeit-ist-nicht-geld (Claude Runde 5, Paket 0.1.4-dev)
## Werkzeugaufrufe
- Bash: {"command":"ls -la && cat .aios/PLAN.md .aios/NOTIZEN.md 2>/dev/null","description":"Check working folder and project notes"}
- Agent: {"description":"Unabhängige Prüfung Entwurf","subagent_type":"general-purpose","model":"sonnet","run_in_background":false,"prompt":"Du bist unabhängiger Prüfer. Prüfe den folgenden Antwortentwurf gege
- Agent: {"description":"Nachprüfung überarbeiteter Entwurf","subagent_type":"general-purpose","model":"sonnet","run_in_background":false,"prompt":"Du bist unabhängiger Prüfer. Prüfe den folgenden überarbeitet
## Antwort
Kurz vorweg: Die Nacharbeit ist gemessen, die Ursache „doppelte Eingaben“ ist bisher nur eine Vermutung. Eine Halbierung würde rechnerisch 2,5 Stunden Arbeitszeit freisetzen. Eingesparte Ausgaben ergeben sich daraus nach heutigem Stand nicht.

**Was belegt ist und was nicht**

| Aussage | Status |
|---|---|
| 10 Vorgänge, im Mittel 30 Minuten Nacharbeit je Vorgang | gemessen |
| Ursache sind doppelte Eingaben | Vermutung des Teams, unbelegt |
| Eine Lösung vermeidet die Hälfte der Nacharbeit | Annahme |
| Alle bleiben mit gleicher Bezahlung angestellt | gesetzte Rahmenbedingung |
| Änderungen bei Fremdkosten | keine belegt |

Offen sind noch diese Punkte:
- In welchem Zeitraum fielen die zehn Vorgänge an?
- Wie viele Vorgänge gab es in diesem Zeitraum insgesamt?
- Wie stark streuen die Werte um den Mittelwert?
- Was genau zählt als „Nacharbeit“?

Ich gehe davon aus, dass die 30 Minuten reine Arbeitszeit sind und keine Wartezeit oder Gesamtdauer des Vorgangs. Das sollte bestätigt werden.

**Nächste Ursachenprüfung**

Die Hypothese betrifft im Ishikawa-Diagramm vor allem zwei Bereiche. Bei der Methode verlangt der Ablauf dieselbe Eingabe zweimal. Bei der Software fehlt die Übernahme zwischen Systemen. Als andere Erklärungen kommen die Daten (unvollständige oder fehlerhafte Eingangsdaten) und die Messung (Nacharbeit ist uneinheitlich abgegrenzt) infrage.

Vorgeschlagener Prüfplan, in dieser Reihenfolge:

1. **Die zehn Fälle einzeln zuordnen.** Für jeden Fall festhalten, welcher Fehler die Nacharbeit ausgelöst hat und ob er aus einer doppelten Eingabe stammt. Ein Beispiel wäre ein Abweichungsfehler zwischen zwei Erfassungen. Dieser Schritt steht vorn, weil er die größte offene Beleglücke schließt. Er zeigt auch, welcher Anteil der 300 Minuten überhaupt auf die vermutete Ursache entfällt. Ob dafür Fallunterlagen vorliegen, ist noch zu klären.
2. **Gegenfälle suchen.** Gibt es Vorgänge mit doppelter Eingabe ohne Nacharbeit oder Nacharbeit ohne doppelte Eingabe? Beides schwächt die Hypothese oder zeigt weitere Ursachen.
3. **Messdefinition klären.** Was zählt als Nacharbeit, und wer hat die Zeit wie erfasst? Erst dann sind die 30 Minuten vergleichbar.
4. **Bei Bestätigung nachfragen, warum doppelt erfasst wird.** Eine fehlende Schnittstelle, eine Vorgabe oder Gewohnheit führen zu unterschiedlichen Lösungen. Die Warum-Fragen gehen nur so weit, wie Belege dafür da sind.

Erst wenn Schritt 1 zeigt, welcher Anteil der Nacharbeit tatsächlich aus doppelten Eingaben stammt, lässt sich die angenommene Halbierung prüfen.

**Vorsichtige Nutzenabschätzung**

- Basis (gemessen): 10 × 30 Minuten = 300 Minuten = 5 Stunden Nacharbeit
- Annahme: Die Lösung vermeidet die Hälfte
- Frei werdende Arbeitszeit (Schätzung): 150 Minuten = 2,5 Stunden für diese zehn Vorgänge
- Eingesparte Ausgaben: keine belegt. Die Löhne bleiben gleich, und Änderungen bei Fremdkosten sind nicht belegt.

Die 2,5 Stunden sind also freie Kapazität und kein Geld. Einen Wert bekommen sie nur, wenn die Zeit nachweislich für andere Arbeit genutzt wird. Das können zum Beispiel mehr Vorgänge, kürzere Wartezeiten oder weniger Rückstau sein. Das müsste man gesondert belegen. Auf Monat oder Jahr hochrechnen lässt sich das erst mit Zeitraum und Gesamtzahl der Vorgänge. Die Kosten der Lösung selbst sind noch nicht berücksichtigt.

Ein unabhängiger Prüfer hat die Einordnung kontrolliert. Ich habe nichts gespeichert und an keinem System etwas geändert. Wenn du mir den Zeitraum und die zehn Fallbeschreibungen gibst, gehe ich Schritt 1 mit dir durch.
