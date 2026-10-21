# Zusatzwerkzeuge: Bestand und Auswahl

Inventurstand: 18.10.2026. Lesende Inventur für Entscheidung 53. Keine Installationen verändert, keine Kundendaten oder Gesprächsverläufe ausgewertet. Zweckangaben stammen aus Skillbeschreibungen und Pluginmetadaten. Installation belegt keine tatsächliche Nutzung oder Funktionsfähigkeit.

Einordnung vom 19.10.2026: Die Tabelle unten dokumentiert den damaligen Bestand und damalige Auswahlfragen. Die Auswahlrunde ist inzwischen abgeschlossen. Maßgeblich sind [Paketumfang](../paketumfang-und-umsetzung.md) und [Übernahmeliste](../uebernahmeliste.md). Prompting ist durch 95b/96a geklärt, Dokumentformate durch 55 bis 58 und 114, Recherche durch 59/111 und Skill-Builder durch 112. Nicht ausgewählte Werkzeuge wie Fable-Mode und Microsoft Foundry werden nicht allein aufgrund dieser Inventur übernommen.

Clientberichte: [Claude Code](claude-code.md) und [Codex](codex.md). Gleiche Werkzeuge können in mehreren Clients und Installationsbereichen vorkommen. Deshalb die Zahlen nicht zu einer Zahl unterschiedlicher Produkte addieren.

## Gemeinsamer Skillbestand außerhalb der eigenen 19 AIOS-Skills

Unter `~/.agents/skills/` wurden 36 weitere `SKILL.md`-Dateien gefunden. Papierkorb, Sicherungsordner und Referenz-/Skriptordner sind nicht mitgezählt. „Weitere“ bedeutet außerhalb von `Agentic OS/skills`, nicht zwingend von einem fremden Autor. Untergeordnete Skills werden einzeln gezählt. Die automatische Erkennung verschachtelter Skills kann je Client abweichen.

| Gruppe | Gefundene Skills | Einordnung für die Auswahl |
| --- | --- | --- |
| Textstil | `humanizer` an zwei Orten | Funktion in Entscheidung 9 gewählt. Zwei inhaltlich identische Dateien, Paketquelle noch festzulegen |
| Video | `hyperframes`, `faceless-explainer`, `general-video`, `hyperframes-core`, `hyperframes-cli`, `hyperframes-animation`, `hyperframes-keyframes`, `hyperframes-audio`, `hyperframes-creative`, `hyperframes-registry`, `hyperframes-studio`, `media-use` | Teile ausdrücklich vom gewählten Lernvideo-Skill verlangt, Umfang vor Übernahme prüfen |
| Ältere Arbeits- und Promptinghilfe | `fable-mode`, `fable-prompting` | Fable-Prompting bereits in Entscheidung 41a behandelt. Fable-Mode separat bewerten |
| Review | `external-pr-review` | Review fremder Änderungen, von persönlicher Ergebnisprüfung zu unterscheiden |
| Dokumente | `doc-coauthoring`, `docs`, `docx`, `pdf`, `pptx`, `xlsx` | Teilweise Überschneidung mit Clientplugins. Gewünschte Dateiformate und Clientfähigkeiten einzeln entscheiden |
| Recherche | `deepresearch` | Eigenständige Recherchehilfe, Mehrwert gegenüber vorhandenen Werkzeugen offen |
| Skill- und Werkzeugbau | `skill-creator`, `mcp-builder` | Mögliche Ergänzung zu AIOS-Skill-Builder, keine ungeprüfte Pflichtabhängigkeit |
| Weitere Inhalte | `brand-guidelines`, `morning`, `import-memory` | Anthropic-Markenstil ist nicht Blockbrain-Design. Morning überschneidet sich mit Tagesstart. Memory-Import muss zum gewählten Speicherkonzept passen |
| Microsoft Foundry | `microsoft-foundry`, `finetuning`, `deploy-model`, `capacity`, `customize`, `preset`, `source-command-distill` | Modellbereitstellung, Feinabstimmung und zugehörige Wissenspflege. Konkreter AIOS-Bedarf noch nicht gewählt |

Die synchronisierten Skills liegen unter `~/.agents/skills/synced/481c821d-01d3-4c39-91b8-6734242886fb_1bfbd015-0ddb-464e-86fd-8fe7a94eed2b/`. Die Foundry-Unterfunktionen liegen unter `~/.agents/skills/microsoft-foundry/`.

## Belegte Abhängigkeiten und Doppelungen

- `Agentic OS/skills/lernvideo/SKILL.md:20` verlangt zuerst `hyperframes` und nennt `faceless-explainer` für gesprochene Erklärvideos.
- Dieselbe Datei, Zeile 22, verlangt `hyperframes-core` für Komposition und `hyperframes-cli` für CLI-Befehle. `media-use`, Animation, Keyframes und Audio werden abhängig vom konkreten Arbeitsschritt geladen. Welche weiteren Teile deren eigener Installationsweg benötigt, bleibt vor Paketierung zu prüfen.
- Dieselbe Datei, Zeile 26, verlangt Humanizer für an andere gerichtete Texte.
- `Agentic OS/skills/blockbrain-slides/SKILL.md:14` verweist PowerPoint-Aufträge an `pptx` oder `presentations`. Das ist ein alternativer Ausgabeweg, kein Beleg, dass HTML-Folien PowerPoint-Werkzeuge brauchen.
- Die zwei Humanizer-Dateien unter `~/.agents/skills/humanizer/SKILL.md` und dem synchronisierten Verzeichnis besitzen denselben SHA-256: `243aecdafecb5e11c2d45e2e088b7876e3f6eee34aa50c53f624d8468039afa8`. Es sind unterschiedliche Dateien, keine zwei Verweise auf dieselbe Datei.

## Weitere Auswahl

Keine weitere pauschale Einzelauswahlrunde. Die bestätigten Video-Abhängigkeiten und übrigen ausgewählten Werkzeugwege technisch prüfen. Bereits gewählte Funktionen nicht erneut grundsätzlich bestätigen lassen. Noch keine pauschale Übernahme, Deaktivierung oder Deinstallation.

Offen bleiben tatsächliche Nutzung, Installations- und Lizenzbedingungen, neue Modellkompatibilität und Funktionsabnahme auf beiden Clients. Die Inventur ist keine Quellenprüfung jedes einzelnen Skills und kein vollständiger Audit sämtlicher MCP-Server oder Hooks.
