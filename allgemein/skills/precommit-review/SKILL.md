---
name: precommit-review
description: Prüft auf Auftrag eigene uncommittete Änderungen rein lesend mit separatem Prüfer, Repository-Kontext und relevanten Testergebnissen vor einem Commit.
---

# Eigene Änderungen prüfen

Beachte den [Regelkern](../../regeln/kern.md) und bei einem abgelegten Bericht die [Ablage](../../referenzen/ablage.md). Bestimme zuerst den zum Auftrag gehörenden Diff, einschließlich gestagter und ungestagter Änderungen. Fremde parallele Änderungen bleiben außerhalb der Bewertung und unangetastet. Lade einschlägige Repository-Regeln, Anforderungen, Codekontext und relevante Testergebnisse. Fehlt eine benötigte Quelle oder ein separater Prüfagent, benenne die Lücke, frage zuerst nach dem weiteren Vorgehen und warte die Entscheidung ab.

Lasse einen an der Erstellung unbeteiligten Prüfer die Änderungen kritisch ansehen. Verfolge geänderte Kontrollflüsse durch Funktionen, Aufrufstellen und Geschwisterpfade. Prüfe Korrektheit, Sicherheit, Verträge und für die Änderung relevante Leistungs- und Typfragen. Ein Defekt braucht geänderte Datei und Zeile, konkreten Auslöser, erwartetes und tatsächliches Verhalten sowie Auswirkung. Trenne bestätigte Fehler von Fragen und optionalen Hinweisen. Sage, welche Teile und Tests geprüft wurden und welche offen sind.

Der Ablauf ist rein lesend. Er ändert keine Dateien, erstellt keinen Commit und bereinigt keine fremden Änderungen. Für einen bestehenden Bugfix gilt die Diagnosefreigabe aus dem Regelkern. Ein fremder PR gehört zum [PR-Review](../pr-review/SKILL.md), vorhandene Threads auf dem eigenen PR zur [Kommentartriage](../review-kommentare/SKILL.md).

[Synthetische Prüffälle](references/prueffaelle.md) beschreiben spätere Verhaltensprüfungen, keine bestandenen Modelltests.
