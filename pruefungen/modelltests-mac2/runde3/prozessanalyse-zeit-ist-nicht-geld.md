# prozessanalyse-zeit-ist-nicht-geld (Runde 3, Paket 0.1.2-dev)
## Werkzeugaufrufe
- Bash: {"command":"ls -la; ls .aios 2>/dev/null && cat .aios/PLAN.md .aios/NOTIZEN.md 2>/dev/null","description":"Check working folder and project notes"}
- Agent: {"description":"Unabhängige Prüfung Entwurf","subagent_type":"general-purpose","model":"sonnet","run_in_background":false,"prompt":"Du prüfst unabhängig einen Antwortentwurf. Lies nichts außer diesem 
- SendMessage: {"to":"ac933c0a15b5285ff","summary":"Nachprüfung überarbeitete Fassung","message":"Bitte prüfe die vollständige überarbeitete Fassung erneut nach denselben Kriterien. Geändert wurden deine drei Befund
## Abweisungen
## Meta
turns=4 fehler=false
turns=1 fehler=false
## Antwort (letztes result)
**Kurz:** Dass doppelte Eingaben die Ursache sind, ist bisher nur eine Vermutung des Teams. Stimmt sie und wirkt die Lösung wie geschätzt, würden bei diesen zehn Vorgängen etwa 2,5 Stunden Arbeitszeit frei. Ein Geldeffekt lässt sich aus den Angaben nicht ableiten. Die Löhne bleiben gleich, und es gibt keine belegten Änderungen bei den Fremdkosten.

**Was belegt ist und was nicht**

| Aussage | Status |
|---|---|
| 10 Vorgänge, im Mittel je 30 Min. Nacharbeit (zusammen 300 Min. = 5 Std.) | gemessen |
| Ursache sind doppelte Eingaben | Vermutung des Teams, unbelegt |
| Lösung vermeidet die Hälfte der Nacharbeit | Schätzung |
| Gleiche Bezahlung, keine belegten Fremdkostenänderungen | Rahmenangabe laut Auftrag |

Es fehlen noch einige Angaben:
* der Zeitraum der zehn Vorgänge
* wie viele Vorgänge es in diesem Zeitraum insgesamt gab
* wie stark die Einzelwerte um den Mittelwert schwanken
* was genau als Nacharbeit zählt

Die 30 Minuten sind Arbeitszeit. Über Liegezeit oder Durchlaufzeit sagen sie nichts.

**Nächste Ursachenprüfung**

1. *Begriffe festlegen.* Was gilt als doppelte Eingabe? Das können dieselben Daten in zwei Systemen sein, eine zweifache Eingabe im selben System oder eine erneute Erfassung nach einer Rückfrage. Außerdem ist zu klären, was als Nacharbeit zählt und wo sie beginnt und endet.
2. *Die zehn Vorgänge einzeln aufschlüsseln.* Für jeden Vorgang notieren: Gab es eine doppelte Eingabe? Wie viele der 30 Minuten gehen direkt darauf zurück? Was war sonst der Anlass der Nacharbeit?
3. *Gegenfälle suchen.* Dazu gehören Vorgänge mit doppelter Eingabe, aber ohne Nacharbeit. Ebenso Vorgänge mit Nacharbeit, aber ohne doppelte Eingabe. Gibt es viel Nacharbeit ohne doppelte Eingabe, erklärt die Vermutung höchstens einen Teil.
4. *Andere Erklärungen mitprüfen,* soweit sie hier plausibel sind:
   * Daten: unvollständige oder fehlerhafte Angaben aus dem vorgelagerten Schritt
   * Software: fehlende Plausibilitätsprüfung, keine automatische Übernahme zwischen Systemen
   * Methode und Rollen: unklare Zuständigkeit, Rückfragen bei Übergaben
   * Messung: Die zehn Vorgänge könnten auffällige Fälle sein und nicht den Normalfall zeigen
5. *Warum-Fragen nur so weit stellen, wie Belege tragen.* Bestätigt sich die doppelte Eingabe, folgt die Frage, warum sie nötig ist. Mögliche Gründe sind eine fehlende Schnittstelle, eine Vorgabe oder Gewohnheit. Davon hängt ab, welche Lösung überhaupt passt.

Die Schritte 2 und 3 haben Vorrang. Sie nutzen die schon gemessenen Fälle und zeigen am schnellsten, welcher Teil der Nacharbeit wirklich auf doppelte Eingaben entfällt.

**Vorsichtige Nutzenabschätzung**

| Größe | Wert | Grundlage |
|---|---|---|
| Nacharbeit gesamt (10 Vorgänge) | 300 Min. | gemessen |
| davon vermeidbar | 150 Min. = 2,5 Std. | Schätzung 50 % |
| frei werdende Arbeitszeit | etwa 2,5 Std. bzw. 15 Min. je Vorgang | Schätzwert, gilt nur wenn Ursache und Wirkung zutreffen |
| vermiedene Auszahlungen | belegt: keine | gleiche Löhne, keine belegten Fremdkostenänderungen |

Die 2,5 Stunden beruhen auf zwei ungeprüften Annahmen. Die erste ist die vermutete Ursache, die zweite die geschätzte Wirkung der Lösung. Erklärt die doppelte Eingabe nur einen Teil der Nacharbeit, fällt der Wert niedriger aus. Auf Monat oder Jahr lässt er sich ohne Zeitraum und Fallzahl nicht hochrechnen.

Die frei werdende Zeit ist Kapazität und kein Geld. Einen Wert hat sie erst, wenn klar ist, wofür sie genutzt wird. Beispiele sind mehr Vorgänge ohne zusätzliches Personal, weniger Rückstau oder wegfallende Überstunden. Das müsste eigens belegt werden. Die Kosten der Lösung selbst sind hier noch nicht eingerechnet.

**Für den nächsten Schritt brauche ich:** den Zeitraum und die Gesamtzahl der Vorgänge. Außerdem die Einzelwerte der zehn gemessenen Fälle mit dem jeweiligen Anlass der Nacharbeit.

Ein unabhängiger Prüfer hat die überarbeitete Fassung gelesen und keine Befunde mehr gemeldet. Es wurde nichts gespeichert, und weitere Quellen habe ich nicht genutzt.
