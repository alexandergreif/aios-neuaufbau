# Vergleich der vorhandenen Prompting-Skills

Stand: 18.10.2026. Lokale Inhalte und Referenzen gelesen, durch separaten Astra-Prüfagenten auf high unabhängig gegengeprüft. Keine Skills verändert oder ausgeführt. Keine Aussage über die aktuelle Wirksamkeit modellspezifischer Tipps getestet. Anschließend hat Alexander mit Entscheidung 41a einen gemeinsamen optionalen Prompt-Berater bestätigt. Umsetzung und Abnahme stehen noch aus.

Aktualisierung 19.10.2026: Dieser Bericht bleibt ein Vergleich der alten Quellen. Maßgeblich für die Übernahme sind 95b und 96a. Auftrag und autonome Vorbereitung werden ein Skill. Der separate Prompt-Berater übernimmt nur gezielte Diagnosemethoden: Bedeutung erhalten, Widersprüche erkennen, Clientfähigkeiten prüfen und Änderungen anhand konkreter Beispiele testen. Die folgenden Bestandsbefunde sind keine Anweisung, alle Fable-Bausteine zu übernehmen. Allgemeine Auftrags-, Delegations- und Prüfregeln werden zentral referenziert.

## Unterschiedliche Aufgaben

| Skill | Eigener Nutzen | Grenze |
| --- | --- | --- |
| `auftrag` | Grobe Idee mit möglichst wenig Änderung zu einem kopierbaren Auftrag schärfen | Keine Modellberatung, kein externer Zugriff, keine Ausführung |
| `goal-vorbereiten` | Längeren autonomen Auftrag mit gleicher Bedeutung und gleichen Befugnissen für beide Clients vorbereiten | Kein Start eines Goals, Clientfunktionen nicht mit Modelleigenschaften verwechseln |
| `gpt-prompting` | Prompt und Werkzeugauftrag für Codex prüfen, API-Angaben von realen Clientfähigkeiten trennen | Kein allgemeiner Ersatz für Auftrag oder Goal-Vorbereitung |
| `fable-prompting` | Umfangreiche Arbeitsbausteine für Effizienz, Delegation, Prüfung und autonome Ausführung | Explizit auf ein älteres konkretes Modell beschränkt, enthält zugleich allgemeine Arbeitsregeln |

## Was bei einer Zusammenlegung nicht verloren gehen sollte

1. **Originalauftrag bewahren:** `auftrag` ergänzt statt unnötig umzuschreiben und liefert genau einen Prompt. [Quelle](<../Agentic OS/skills/auftrag/SKILL.md:13>), Ausgabe und Grenzen ab Zeile 20.
2. **Gleichwertige Clientfassungen:** `goal-vorbereiten` schützt Umfang, Befugnisse und bestehende Änderungen in beiden Fassungen. Blockaden sind kein Abschluss. [Quelle](<../Agentic OS/skills/goal-vorbereiten/SKILL.md:28>), ergänzend Zeilen 30 bis 38. Die Angaben zu `/goal` und Zeichenlimits sind technische Clientangaben, deren Aktualität vor Umsetzung zu prüfen ist.
3. **API ist nicht Client:** `gpt-prompting` verhindert erfundene Werkzeuge, Berechtigungen und behauptete Modellwechsel. [Quelle](<../Agentic OS/skills/gpt-prompting/SKILL.md:22>), ergänzend Zeilen 24 und 32.
4. **Bedeutung beim Kürzen erhalten:** Technische Bedingungen und zeitliche Abhängigkeiten müssen im Prompt bleiben. Der Diagnose-Checkpoint ist in den Beispielen konkret abgebildet. [Quelle](<../Agentic OS/skills/gpt-prompting/SKILL.md:30>), [Bugfix-Beispiel](<../Agentic OS/skills/gpt-prompting/references/beispiele.md:19>).
5. **Praktische Prüfbausteine:** Fable enthält unter anderem getrennte Statusgruppen für Stapelaufträge, unabhängige Prüfer mit Qualitätskriterien und Belege für Fortschrittsmeldungen. [Quelle](/Users/alexandergreif/.agents/skills/fable-prompting/SKILL.md:30), ergänzend Zeilen 116, 119 und 130. Spezifische Aussagen zu Effort und Bildverarbeitung in Zeilen 82 und 136 sind nicht ungeprüft auf andere Modelle übertragbar.

## Konflikte mit unseren neuen Entscheidungen

| Stelle | Bestehende Vorgabe | Anpassungsbedarf für das neue Paket |
| --- | --- | --- |
| `fable-prompting/SKILL.md:79` | Mit high beginnen | Hauptmodell und Effort wählt Alexander |
| `fable-prompting/SKILL.md:85` | Haiku ausgeschlossen und feste Modellversion genannt | Haiku ist erlaubt, Regeln ohne feste Modellversionen |
| `fable-prompting/SKILL.md:93` | Höchstens zwei Subagenten | Nutzen und tatsächliche technische Grenzen entscheiden |
| `gpt-prompting/SKILL.md:22,24` | Alte Modellmatrix, konkrete Versionen und Zweiergrenze | An neue Modell- und Delegationsentscheidungen anpassen |
| `gpt-prompting/references/beispiele.md:33` | Unabhängige Prüfung ausdrücklich optional | Unabhängige Prüfung wurde als Pflicht gewählt |
| `fable-prompting/SKILL.md:196` | Allgemeiner autonomer Ausführungsbaustein | Diagnosebestätigung bei bestehenden Bugs muss erhalten bleiben |

Die relativen GPT-Pfade beziehen sich auf `../Agentic OS/skills/`, Fable liegt unter `~/.agents/skills/`. Auch zugehörige Beispiele und Prüffälle müssen bei einer späteren Überarbeitung angepasst werden. Die Konflikte beauftragen noch keine Änderung der aktiven Installation.

## Nach dem Vergleich mit Entscheidung 41a bestätigte Richtung (durch 95b teilweise ersetzt)

Die drei Nutzungsfälle getrennt zugänglich halten:

- **Auftrag schärfen:** Was soll erreicht werden?
- **Autonomen Auftrag vorbereiten:** Wie sind längere Ausführung, Grenzen und Abschluss beschrieben?
- **Prompt-Beratung für Claude und GPT:** Warum funktioniert dieser Prompt schlecht oder unnötig aufwendig, und welche gezielte Anpassung hilft?

Für die Prompt-Beratung die brauchbaren Teile der zwei Anbieter-Skills zusammenführen. Allgemeine persönliche Arbeitsregeln zentral referenzieren. Anbieter- und Clienthinweise nur bei Bedarf aus aktuellen offiziellen Quellen beziehen. Keine feste Modelltabelle und kein automatischer Wechsel des Hauptmodells. Nicht bei jedem normalen Auftrag zusätzliche Beratung laden.

Erwogene Alternative: Die speziellen Hinweise nur als Referenzen der beiden bereits gewählten Fähigkeiten führen. Alexander hat stattdessen den gemeinsamen optionalen Prompt-Berater gewählt.

## Aktualisierung durch Entscheidung 95b

„Auftrag schärfen“ und „autonome Aufgaben vorbereiten“ werden zu einem Skill „Auftrag vorbereiten“ zusammengelegt. Die autonome Vorbereitung ist ein zusätzlicher Ablauf im gemeinsamen Skill. Der Prompt-Berater bleibt als getrennte Fähigkeit erhalten. Die obigen Quellenbefunde bleiben Grundlage für die Überarbeitung, die frühere Forderung nach zwei eigenständigen Vorbereitungsskills entfällt.
