# prozessanalyse-zeit-ist-nicht-geld (Runde 4, Paket 0.1.3-dev)
## Werkzeugaufrufe
- Bash: {"command":"ls -la ~/aios-test.xgNSnI/arbeitsordner/runde4-prozessanalyse-zeit-ist-nicht-geld; ls -la ~/aios-test.xgNSnI/arbeitsordner/runde4-prozessanalyse-zei
- Agent: {"description":"Prozessanalyse-Entwurf prüfen","model":"sonnet","run_in_background":false,"prompt":"Du bist unabhängiger Prüfer. Prüfe den unten stehenden Antwortentwurf gegen Auftrag und Regeln. Kein
- Agent: {"description":"Überarbeitete Fassung nachprüfen","model":"sonnet","run_in_background":false,"prompt":"Du bist unabhängiger Prüfer. Prüfe den unten stehenden überarbeiteten Antwortentwurf gegen Auftra
## Meta
turns=4 fehler=false denials=0
## Antwort
**Kurz:** Die Nacharbeit ist gemessen, ihre Ursache aber nicht. Als Nächstes sollte man an den zehn Vorgängen prüfen, ob die Nacharbeit wirklich aus doppelten Eingaben entsteht. Auch wenn sich das bestätigt und die Lösung wie geschätzt wirkt, wird nach heutigem Stand nur Arbeitszeit frei. Eine vermiedene Auszahlung ist nicht belegt.

**Was belegt ist und was nicht**

| Aussage | Status |
|---|---|
| 10 Vorgänge mit im Mittel 30 Min. Nacharbeit je Vorgang | gemessen, Messdefinition offen |
| Doppelte Eingaben als Ursache | Vermutung des Teams, unbelegt |
| Lösung vermeidet die Hälfte der Nacharbeit | Schätzung, Grundlage unbekannt |
| Gleiche Belegschaft, gleiche Bezahlung, keine belegten Fremdkostenänderungen | Rahmen laut Auftrag |

Es fehlen noch der Zeitraum der zehn Vorgänge, die Menge pro Monat, die Streuung um den Mittelwert und die Art der Messung. Unklar ist auch, ob die 30 Minuten reine Arbeitszeit sind oder Liegezeit enthalten, zum Beispiel Warten auf Rückfragen. Nur die aktive Arbeitszeit kann frei werden. Weniger Liegezeit würde höchstens die Durchlaufzeit verkürzen.

**Mögliche Ursachen (Ishikawa, nur die Äste mit Inhalt)**

- **Methode:** Dieselben Daten werden an zwei Stellen erfasst, und Abweichungen fallen erst später auf. (Vermutung des Teams)
- **Software:** Es fehlt eine Übernahme zwischen zwei Systemen oder Masken, deshalb muss doppelt erfasst werden. (Vermutung)
- **Daten:** Unvollständige oder falsche Eingangsdaten führen zu Korrekturen, auch ohne doppelte Eingabe. (andere Erklärung)
- **Messung:** Nacharbeit ist vielleicht nicht einheitlich abgegrenzt und mit Rückfragen oder der normalen Prüfung vermischt.

Die Warum-Kette reicht im Moment nur eine Ebene weit. Warum gibt es Nacharbeit? Vermutlich weil doppelt erfasste Daten voneinander abweichen. Tiefer zu fragen lohnt sich erst nach der Prüfung.

**Nächste Ursachenprüfung**

1. **Für jeden der zehn Vorgänge den Auslöser der Nacharbeit bestimmen.** Mögliche Auslöser sind Abweichung zwischen doppelten Eingaben, fehlerhafte Eingangsdaten, Rückfrage und Sonstiges. Daraus ergibt sich, welcher Anteil der Nacharbeitsminuten wirklich von doppelten Eingaben kommt. Das hat Vorrang, weil die ganze Nutzenschätzung davon abhängt.
2. **Gegenfälle suchen.** Gemeint sind Vorgänge mit doppelter Eingabe ohne Nacharbeit und Nacharbeit ohne doppelte Eingabe. Beide sprechen gegen die Vermutung.
3. **Messdefinition klären.** Was zählt als Nacharbeit, wer hat wie gemessen und ist Liegezeit enthalten?
4. **Menge und Zeitraum erheben.** Wie viele solche Vorgänge gibt es pro Monat? Erst dann lässt sich hochrechnen.

Zehn Vorgänge sind eine kleine Stichprobe. Für eine belastbare Aussage sollte die Zuordnung an weiteren Fällen wiederholt werden.

**Vorsichtige Nutzenabschätzung**

- **Gemessene Nacharbeit:** 10 × 30 Min. = 300 Min. = 5 Std. für diese zehn Vorgänge. Wenn darin Liegezeit steckt, ist die aktive Arbeitszeit kleiner.
- **Rechenbeispiel bei Halbierung:** 150 Min. = 2,5 Std. für dieselben zehn Vorgänge. Frei wird höchstens der Teil davon, der aktive Arbeitszeit ist. Das ist kein belegter Wert. Es beruht auf zwei unbelegten Annahmen: Doppelte Eingaben sind die Ursache, und die Lösung vermeidet wirklich die Hälfte.
- **Vermiedene Auszahlungen:** keine belegt. Die Beschäftigten bleiben mit gleicher Bezahlung angestellt, und Änderungen bei Fremdkosten sind nicht belegt.
- **Kosten der Lösung:** noch nicht bekannt, zum Beispiel für Umsetzung, Lizenzen oder Einarbeitung. Sie müssen noch erhoben werden.

Die 2,5 Stunden wären also Kapazität und kein Geld. Was sie wert sind, hängt davon ab, wofür die Zeit genutzt wird, etwa für mehr Vorgänge oder kürzere Durchlaufzeiten. Das müsste eigens belegt werden. Hochrechnen auf Monat oder Jahr geht erst, wenn die Vorgangsmenge bekannt ist.

---

**Prüfung:** Zwei unabhängige Prüfer haben die Einordnung nacheinander gegengelesen. Ihre Hinweise habe ich eingearbeitet. Nach der zweiten Prüfung habe ich noch zwei Formulierungen geändert, die niemand mehr gegengelesen hat: die Abgrenzung von Arbeitszeit und Liegezeit im ersten Abschnitt und den Satz „höchstens der Teil, der aktive Arbeitszeit ist“ beim Rechenbeispiel. Es wurde nichts gespeichert und nichts gesendet.
