# Context Mode: Nutzen und Speicherung

Stand: 18. Oktober 2026. Entscheidung 66 beauftragt die Prüfung. Mit Entscheidung 66a wurde Context Mode auf die Liste der später zu evaluierenden Bestandteile gesetzt. Die Aufnahmeentscheidung bleibt ausdrücklich offen. Die folgende Empfehlung ist ein Prüfergebnis, keine beschlossene Ablehnung des Plugins.

## Umfang

Quellprüfung der installierten Codex-Version 1.0.169 durch zwei separate Prüfagenten (Astra high). Der Hauptagent führte synthetische Tests mit den aktuell verfügbaren MCP-Werkzeugen aus. Claude registriert Version 1.0.151. Keine Aussage zur neuesten veröffentlichten Version.

Keine Kundendaten, bestehenden Datenbanken oder Chatarchive gelesen. Keine Installation, Berechtigung oder bestehende Wissensablage geändert. Keine Löschung ausgeführt. Drei ausdrücklich synthetische Abschnitte wurden für den Suchtest im laufenden Werkzeug indiziert. Sie bleiben unter dem Quellnamen `AIOS-SYNTH-20261018-context-mode-test` gespeichert. Die normalen automatischen Erfassungsmechanismen der laufenden Sitzung wurden nicht verändert.

## Verhaltenstests

| Test | Nachweis | Ergebnis und Grenze |
| --- | --- | --- |
| Logauswertung | 10.000 synthetische JSON-Zeilen, 938.972 Byte | Alle drei ERROR-Einträge in Zeilen 100, 5000 und 9999 mit Meldung und Quelldatei erkannt. WARN in Zeile 6000 mit dem Wort ERROR wurde nicht als Fehler gezählt. |
| Ausgabeumfang | Nutzresultat 379 Byte, serialisierte MCP-Antwort 1.723 Zeichen einschließlich zurückgegebenem Code und Metadaten | Deutlich weniger Ausgabe als rohe Logs. Kein gemessener Token-, Kosten- oder Laufzeitvorteil gegenüber einem normalen Skript. |
| Vergleich ohne Context Mode | `python3 pruefungen/context-mode/synthetische_logs.py` | Dieselben drei Fehler und dieselben Bytezahlen, PASS. Der Nutzen der Aggregation ist nicht exklusiv für Context Mode. |
| Fehlerfall | Ungültiges JSON | Im lokalen Prüfsystem als `Ungültiges JSON in Zeile 10001` erkannt. Im MCP-Test wurde eine ungültige JSON-Eingabe separat erkannt. Kein stillschweigendes Erfolgsergebnis. |
| Quellenabruf | Drei synthetische Abschnitte über `ctx_index`, danach zwei gezielte Suchfragen | Standardregel und Ausnahme für gesperrte Testkonten mit Fundstellen erhalten. Status blieb ausdrücklich „installiert, aber noch nicht funktional geprüft“. Auch ein irrelevanter Treffer wurde ausgegeben. Kein allgemeiner Vollständigkeitsnachweis. |
| Dateizugriff | `ctx_execute_file` auf die Testdatei im benachbarten Ordner AIOS-Neuaufbau | Abgewiesen, weil der Server auf Agentic OS begrenzt ist. Keine Berechtigungsänderung und kein alternativer Zugriff auf diese Datei durch das MCP-Werkzeug. Der anschließende MCP-Verarbeitungstest erzeugte die Daten direkt im Aufruf. |

Logauszug aus dem lokalen Test:

```text
raw_bytes: 938972
summary_bytes: 379
records: 10000
errors: 100 -> service-a.py:41
        5000 -> service-b.py:82
        9999 -> service-d.py:73
failure_case: Ungültiges JSON in Zeile 10001
checks: PASS
```

Ein separater Prüfagent hat das lokale Prüfsystem gelesen und erneut ausgeführt. Ergebnis und Fehlerfall wurden unabhängig bestätigt. Diese Tests sind eng begrenzt. Keine vollständige Abnahme in einer frischen Claude-Code- und Codex-Sitzung, kein Test von Verbinden und Trennen, keine Löschprobe auf bestehenden Daten.

## Unterschiede zwischen den Clients

`C169` bezeichnet die unten genannte Codex-Quellwurzel. `L151` bezeichnet `/Users/alexandergreif/.claude/plugins/cache/context-mode/context-mode/1.0.151/`.

| Befund | Beleg | Grenze |
| --- | --- | --- |
| Beide Clients sind für automatische Erfassung eingerichtet | `L151/hooks/hooks.json:4`, `:26`, `:109`, `:120`, `C169/.codex-plugin/hooks.json:3` | Vorhandene Konfiguration ist kein Nachweis jedes erfolgreichen Hook-Laufs. |
| Beide Versionen speichern MCP-Antworten in Ereignissen | `L151/src/session/extract.ts:582`, `:597`, `:606`, `C169/src/session/extract.ts:921`, `:933`, `:945` | Nachträgliches Speichern entfernt die ursprüngliche Werkzeugantwort nicht aus dem Modellkontext. |
| Codex erfasst auch AGENTS-Dateien beim Start | `C169/hooks/codex/sessionstart.mjs:41`, `:51`, `:53` | Technischer Index muss von bestätigtem AIOS-Wissen getrennt bleiben. |
| Routing erfolgt teilweise nur als Hinweis | `L151/hooks/core/routing.mjs:765`, `C169/hooks/core/routing.mjs:839`, `:843`, `:853`, `:869` | Hinweise und geschätzte vermiedene Bytes sind kein Nachweis tatsächlicher Einsparung. |
| Subagenten-Routing unterscheidet sich | `L151/hooks/hooks.json:64`, `L151/hooks/core/routing.mjs:819`, `:827`, `C169/.codex-plugin/hooks.json:5` | Codex-Matcher enthält weder Agent noch spawn_agent. Keine pauschale Gleichheit beider Clients. |
| Umschreiben von Kommandos hängt von Clientversion ab | `C169/hooks/core/codex-caps.mjs:29`, `:67`, `:101`, `C169/hooks/core/formatters.mjs:172` | Codex-Rewrite ab erkanntem CLI-Stand 0.141.0, sonst Ablehnung. Aktueller Client nicht neu gestartet oder separat getestet. |
| Ausführung über gewöhnliche Laufzeitprozesse | `C169/src/executor.ts:284`, `:439`, `:465`, `:693` | Keine belegte Betriebssystem-Isolation für Dateien und Netzwerk. Der erfolgreiche Pfadschutz eines Werkzeugs belegt keine umfassende Sandbox. |
| Ausgabe kann weiterhin groß sein | `C169/src/server.ts:1913`, `:1922`, `:1937` | Optionen und Analysecode sind entscheidend. Context Mode garantiert nicht automatisch kurze Antworten. |

Offen bleibt ein isolierter Ende-zu-Ende-Test beider Clients einschließlich Start, typischer Aufrufe, Fehlerfällen und Trennen. Dafür wären klar begrenzte Testinstallationen sinnvoll. Im bestehenden Setup wurde nichts umkonfiguriert.

## Speicherung und Löschung

Alle relativen Belege in diesem Abschnitt beziehen sich auf:
`/Users/alexandergreif/.codex/plugins/cache/context-mode/context-mode/1.0.169/`

| Befund | Quelle | Bedeutung |
| --- | --- | --- |
| Rohe Nutzerprompts werden bei aktiven Hooks gespeichert | `hooks/userpromptsubmit.mjs:56` | Mehr als ein reiner Ausgabefilter. Keine bestätigte Profil- oder Wissensänderung. |
| MCP-Ereignisse können vollständige Antworten speichern | `src/session/extract.ts:921`, `:938`, `safeString` bei `:86` | Auch Konnektorinhalte können ohne separaten Indexierungsauftrag in den technischen Verlauf gelangen. |
| Secret-Redaktion ist nicht durchgängig | `src/session/extract.ts:990`, `:1035` | Schutz des strukturierten Ereignisses deckt das parallele textuelle Ereignis und rohe Prompts nicht allgemein ab. |
| Große Ausgaben werden automatisch indiziert | `src/server.ts:1913`, `:1923`, `:1979`, `:1993`, `:2192` | Mit intent oberhalb 5.000 Byte, oberhalb 102.400 Byte auch ohne intent. Ausgabeanalyse ist deshalb nicht immer flüchtig. |
| Rohchunks im Index | `src/server.ts:2248` | Der persistierte Inhalt ist nicht bloß eine Zusammenfassung. |
| Speicherpfade | `src/adapters/codex/index.ts:445`, `src/server.ts:682` | Standardmäßig unter `~/.codex/context-mode/sessions` und benachbartem `content/<Projekthash>.db`. Umgebungsvariablen können Pfade ändern. SQLite-Sidecars, Ereignis-Markdown, Snapshots und Statistiken gehören ebenfalls zur Betrachtung. |
| Aufbewahrung | `src/server.ts:726`, `hooks/sessionstart.mjs:306`, `src/session/db.ts:639`, `:1178` | Content-Bereinigung nach 14 Tagen beim Öffnen, Session-Bereinigung nach 7 Tagen beim Start. Keine garantierte zeitgesteuerte Löschung. Maximal 1.000 Ereignisse pro Session mit Verdrängung. |
| Verdacht auf zu breiten Session-Purge | `src/server.ts:4553`, `src/store.ts:452` | Der Handler ruft cleanup vor der Bereichsunterscheidung auf. Cleanup löscht die gesamte Content-DB einschließlich Sidecars. Damit kann Session-Purge bei geöffnetem Store den gemeinsamen Projektindex betreffen. Statische Diagnose, keine Reproduktion und kein Fix. |
| Grenzen von Purge | `src/session/purge.ts:197`, `:279`, `:324`, `src/server.ts:4578` | Keine allgemeine Löschung nativer Client-Transkripte, externer Daten oder Backups. Session-Purge lässt Ereignis-Markdown und Projektstatistiken laut Implementierung bestehen. Kein nachgewiesenes sicheres Überschreiben des Datenträgers. |
| Netzwerk | `src/server.ts:783`, `:4956`, `hooks/platform-bridge.mjs:49`, `:105`, `:225`, `:286` | Versionsabfragen und ein konfigurationsabhängiger Ereignisexport existieren. Ob der Export hier aktiviert ist, wurde nicht geprüft. Keine pauschale Zusage, sämtliche Daten blieben lokal. |
| Automatisches Gedächtnis | `src/search/auto-memory.ts:95` | Suche kann vorhandene Anweisungs- und Memory-Dateien einbeziehen. Extrahierte Entscheidungen und gefundene Notizen sind weiterhin unbestätigte Quelldaten, keine neuen verbindlichen Regeln. |

## Vorläufige Empfehlung

Context Mode noch nicht als Standardbestandteil des neuen Pakets vorsehen. Gezielte Verarbeitung großer Ausgaben ist sinnvoll und lässt sich bereits mit normalen Skripten umsetzen. Der zusätzliche Suchindex hat in der kleinen Probe funktioniert, eine generelle Effizienzsteigerung wurde nicht belegt.

Eine spätere Aufnahme erfordert eine klare Trennung zwischen flüchtiger Verarbeitung, bewusstem Indexieren und automatischer Sitzungserfassung. Außerdem müssen Löschumfang, Clientunterschiede und echte Ende-zu-Ende-Abläufe in isolierten Testumgebungen geprüft werden. Bestehende Installationen bleiben unverändert. Ein möglicher Fehler wird erst nach bestätigter Diagnose und einem gesonderten Fixauftrag bearbeitet.
