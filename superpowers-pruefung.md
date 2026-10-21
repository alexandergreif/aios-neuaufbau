# Superpowers: Prüfung für das neue AIOS

Stand: 18. Oktober 2026. Entscheidung 65 beauftragt die Prüfung. Mit Entscheidung 65a ist die gezielte Übernahme ausgewählter Methoden bestätigt. Umsetzung und Abnahme bleiben offen.

## Grundlage und Grenzen

Lokale Quellprüfung der Version 7.0.0 durch Hauptagent und separaten Prüfagenten (Astra high). Keine Verhaltenstests, keine Änderungen an Installationen. Keine Aussage zur neuesten veröffentlichten Version.

Quellwurzel für alle folgenden relativen Datei- und Zeilenangaben:
`/Users/alexandergreif/.codex/plugins/cache/claude-plugins-official/superpowers/7.0.0/`

Claude registriert laut `~/.claude/plugins/installed_plugins.json` Version 7.0.0 auf Nutzerebene sowie ältere Versionen in Projektinstallationen. Die sechs geprüften SKILL.md-Dateien für using-superpowers, brainstorming, systematic-debugging, test-driven-development, subagent-driven-development und finishing-a-development-branch sind im Claude- und Codex-Cache der Version 7.0.0 bytegleich. Das belegt keine identische Laufzeitwirkung in beiden Clients.

## Befunde

| Thema | Beleg | Einordnung |
| --- | --- | --- |
| Vorrang persönlicher Regeln | `skills/using-superpowers/SKILL.md:65` | Nutzeranweisungen haben ausdrücklich Vorrang. Die folgenden Konflikte sind Reibung zwischen Standardabläufen, keine Befugnis, Nutzerentscheidungen zu übergehen. |
| Häufiges Laden von Skills | `skills/using-superpowers/SKILL.md:11` | Bereits bei einem Prozent vermuteter Relevanz wird Skill-Nutzung verlangt. Das passt schlecht zum schlanken Laden nach Bedarf. |
| Planung | `skills/brainstorming/SKILL.md:22`, `:120`, `:160` | Klare Kleinstaufgaben dürfen direkt ausgeführt werden. Annahmen werden von Entscheidungen getrennt und Dokumente unabhängig geprüft. Nützliche Methoden. |
| Zusätzliche Freigaben | `skills/brainstorming/SKILL.md:179`, `:186` | Bestätigung der vollständigen Beschreibung als Standard, ausdrückliches Überspringen möglich. Für bereits klare Aufträge unnötiger Zusatzschritt gegenüber Entscheidungen 2 und 3. |
| Ursachenanalyse | `skills/systematic-debugging/SKILL.md:48`, `:124`, `:147`, `:179` | Reproduktion, Vergleichsstellen, einzelne Hypothesen und auf die Ursache begrenzte Fixes sind sinnvoll. |
| Diagnosefreigabe | `skills/systematic-debugging/SKILL.md:168`, `skills/subagent-driven-development/SKILL.md:27`, `skills/executing-plans/SKILL.md:277` | Die Abläufe gehen zur Umsetzung über, ohne die persönliche Diagnosefreigabe vorzusehen. Entscheidung 8 muss ausdrücklich berücksichtigt werden. |
| Tests | `skills/test-driven-development/SKILL.md:73`, `:121` | Kleine Verhaltenstests und der Nachweis, dass ein Test den Fehler erkennt, passen gut. |
| Pauschale TDD-Vorgaben | `skills/test-driven-development/SKILL.md:18`, `:24`, `:37`, `:185` | Breite TDD-Pflicht, Rückfrage für Ausnahmen, Löschen vorher geschriebenen Codes und gesamte Testsuite passen nicht als pauschaler AIOS-Standard zur aufgabengerechten Prüfung. |
| Unabhängige Nachprüfung | `skills/executing-plans/SKILL.md:240`, `:253`, `:277` | Separater Abschlussprüfer grundsätzlich passend. Fehlende Prüfung bleibt beim AIOS offen. Das Verbot eines weiteren Reviewers nach einem Fix widerspricht Entscheidung 5. Andere Superpowers-Abläufe sehen Nachprüfung vor. |
| Git-Aktionen | `skills/using-git-worktrees/SKILL.md:86`, `skills/brainstorming/SKILL.md:156`, `skills/writing-plans/SKILL.md:10` | Vorgesehene Commits benötigen weiterhin den ausdrücklich beauftragten Umfang gemäß Entscheidung 61. |
| Worktrees und Abschluss | `skills/using-git-worktrees/SKILL.md:18`, `:41`, `skills/finishing-a-development-branch/SKILL.md:78`, `:126`, `:177` | Bestehende Isolation erkennen, Nutzerpräferenzen beachten, Integration entscheiden lassen und ungesicherte Arbeit schützen sind nützlich. Keine pauschale Behauptung ungefragter Pushes. |
| Modellwahl | `skills/subagent-driven-development/SKILL.md:186`, `:192`, `:204` | Aufgabenbezogene Subagentenwahl ist passend. Stets das stärkste Abschlussprüfmodell zu verlangen geht über Entscheidung 6 hinaus. In diesem Abschnitt keine festen Modellversionen und kein erzwungener Wechsel des Hauptmodells belegt. |
| Fertigmeldung | `skills/verification-before-completion/SKILL.md:25` | Aktuelle Prüfnachweise vor Erfolgsaussagen sind sinnvoll. |

## Empfehlung, mit Entscheidung 65a bestätigt

Superpowers nicht unverändert als verpflichtendes Gesamtpaket ins neue Setup übernehmen. Stattdessen ausgewählte Methoden für Ursachenanalyse, geeignete Regressionstests, belegte Fertigmeldungen, Agentenaufträge und sichere Git-Arbeitsabläufe in die bereits geplanten Fähigkeiten integrieren. Keine zusätzliche parallele Regelsammlung schaffen.

Das Gesamtplugin bietet abgestimmte Abläufe und Updates, würde aber eine geprüfte Anpassung an die persönlichen Regeln erfordern. Selektive Übernahme bedeutet eigene Pflege. Bei tatsächlicher Übernahme von Quelltexten sind Lizenz und Herkunft zu berücksichtigen. Umsetzung und Verhaltenstests in beiden Clients bleiben offen. Bestehende Installationen bleiben unverändert.
