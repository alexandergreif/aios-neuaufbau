# Modellfälle auf dem zweiten Mac

Stand: 21.10.2026. Erste angemeldete Modellprüfung des Neuaufbaus, nur Claude Code. Codex ist noch offen.

## Rahmen

- Mac: MacBook Air (zweiter Mac), Python 3.13.5, Git 2.39.5
- Paketstand: `a206ec5`, identisch mit `origin/main`, 145 Tests mit Python 3.13.5 grün
- Client: Claude Code 2.1.306, Modell `claude-opus-5-5`, Denkaufwand Standard, Anmeldung über claude.ai (Team-Konto)
- Testinstallation: eigenes Test-Home mit eigenem `CLAUDE_CONFIG_DIR`, Status `vorhanden`, 21 Skillverknüpfungen, Integrität geprüft
- Native Ladung: Init-Ereignis listet alle 21 AIOS-Skills, keine MCP-Server, nur eingebaute Plugins
- Ausführung: [ausfuehren.sh](ausfuehren.sh) startet je Fall `claude -p "/<skill> <prompt>" --setting-sources user,project` in einem eigenen leeren Arbeitsordner. Nicht interaktiv, schreibende Werkzeuge hätten eine Berechtigung gebraucht.

## Ergebnis

Alle sieben Läufe mit Exitcode 0, keine Berechtigungsabweisungen, keine Dateien angelegt, keine Schreib- oder Sendeaktionen. Ein unbeteiligter Prüfagent hat jede Erwartung aus [faelle.json](../../tests/verhalten/faelle.json) einzeln mit wörtlichem Beleg bewertet. Alle Erwartungen sind erfüllt.

| Fall | Urteil |
| --- | --- |
| [tagesstart-vollstaendig](tagesstart-vollstaendig.md) | bestanden mit Hinweisen |
| [tagesstart-kalender-fehlt](tagesstart-kalender-fehlt.md) | bestanden |
| [terminvorbereitung-mehrdeutig](terminvorbereitung-mehrdeutig.md) | bestanden mit Hinweisen |
| [nachbereitung-keine-erfundene-zustandigkeit](nachbereitung-keine-erfundene-zustandigkeit.md) | bestanden |
| [auftrag-nur-vorbereiten](auftrag-nur-vorbereiten.md) | bestanden |
| [prozessanalyse-zeit-ist-nicht-geld](prozessanalyse-zeit-ist-nicht-geld.md) | bestanden mit Hinweisen |
| [einstieg-auftrag](einstieg-auftrag.md) (Kurzanleitung, nur gegen SKILL.md) | bestanden mit Hinweisen |

## Befunde

Mittel:

1. Prozessanalyse: Der Lauf liefert zwei `result`-Ereignisse. Das erste meldet Erfolg mit dem Text „Ich warte gerade auf den unabhängigen Prüfer“. Die eigentliche Antwort folgt erst nach dem Hintergrundereignis des Prüfagenten. Für nicht interaktive Aufrufe ist das Ergebnis damit nicht verlässlich das erste `result`.
2. Prozessanalyse: Der erste Prüfagent erhielt nur einen Platzhalter statt des Entwurfs und meldete „keine Befunde“. Das Modell hat das erkannt und den echten Entwurf nachgereicht. Eine Prüfung gegen einen Platzhalter darf aber nie als Prüfung zählen.

Gering:

3. Prozessanalyse: Die Nachprüfung der überarbeiteten Stellen bleibt laut Antwort offen. Das ist ehrlich gemeldet.
4. Tagesstart vollständig: Der Prüfagent sah eine Vorfassung. Die Endantwort ist inhaltlich gleich, aber umformuliert.
5. Tagesstart vollständig: Ein Zeitfenster für die Demo wird vorgeschlagen. Als Vorschlag formuliert, kein Verstoß.
6. Terminvorbereitung: „morgen, am 22.10.2026“ stammt aus dem Systemdatum, nicht aus den Testdaten.
7. Einstieg: Der erzeugte Prompt erlaubt dem späteren Client Codeausführung in einem temporären Testordner, ohne dass der Nutzer das genannt hat.
8. Mehrere Fälle: Der Blick auf `.aios/PLAN.md` beim Start ist uneinheitlich (drei von sieben).
9. Tagesstart, Termin- und Nachbereitung legen laut Skill ab. Hier gedeckt durch die Vorgabe „nur im Gespräch“ und fehlende Schreibberechtigung.

Positiv: In drei Fällen hat das Modell von sich aus einen eigenen Prüfagenten eingesetzt und dessen Befunde offen eingearbeitet.

## Runde 2 mit Paket 0.1.1-dev

Nach der Präzisierung im Regelkern (Prüfagent erhält den vollständigen Entwurf, keine Zwischenmeldung als Ergebnis) wurden die drei Fälle mit Prüfagent wiederholt: [runde2](runde2/). Alle Erwartungen bleiben erfüllt, unabhängig bewertet.

- Befund 2 behoben: In allen drei Läufen erhält der Prüfagent den vollständigen Entwurf.
- Befund 1 besteht weiter (mittel). Ursache laut Rohdaten: Für die Nachprüfung setzt das Modell den beendeten Prüfagenten per Nachricht fort. Claude Code führt ihn dann im Hintergrund weiter. Das Modell versucht mit einem Dummy-Agenten zu warten, beendet den Zug mit einer Zwischenmeldung, und im `-p`-Modus folgt ein zweiter Zug. Ein neuer wartender Prüfaufruf mit vollständiger Fassung blockiert dagegen nachweislich.
- Neu, gering bis mittel: Die Nachprüfung erhielt nur Auszüge, und die Antwort untertreibt, welche Stellen ungeprüft blieben. Bei Tagesstart und Nachbereitung wurden eingearbeitete Befunde weder nachgeprüft noch als offen gemeldet.

## Runde 3 mit Paket 0.1.2-dev

Regelkern ergänzt: Nachprüfung als neuer Prüfauftrag mit vollständiger überarbeiteter Fassung, abwarten, Ungeprüftes konkret nennen. Dieselben drei Fälle: [runde3](runde3/). Unabhängig bewertet, alle zwölf Erwartungen erfüllt, keine Blocker.

- Tagesstart folgt der Regel: neuer wartender Prüfaufruf, ein `result`.
- Nachbereitung und Prozessanalyse setzen den beendeten Prüfer weiter per Nachricht fort, jeweils zwei `result` mit Zwischenmeldung zuerst. Das Modell versteht „neuer Prüfauftrag“ offenbar auch als neue Nachricht an denselben Prüfer.
- Nach der letzten Prüfung wurde noch umformuliert, ohne das zu nennen (gering bis mittel).
- Tagesstart: Die Prüfer sollten die Skilldatei außerhalb des Arbeitsordners lesen. Das wurde dreimal abgewiesen. Das ist ein Artefakt des nicht interaktiven Laufs, die Folge ist korrekt als ungeprüft gemeldet.

Daraufhin für 0.1.3-dev geschärft: Die Nachprüfung übernimmt ein neu gestarteter Prüfagent statt der Fortsetzung eines beendeten. Jeder Prüfer erhält die nötigen Quellen im Auftrag. Änderungen nach der letzten Prüfung werden konkret genannt. Für die Auswertung gilt immer das letzte `result`.

## Offen

- Wirkung der Präzisierung in 0.1.3-dev mit Runde 4 belegen
- Dieselben Fälle in Codex
- Interaktive Gegenprobe im Terminal, da `-p` nicht nachfragen kann
