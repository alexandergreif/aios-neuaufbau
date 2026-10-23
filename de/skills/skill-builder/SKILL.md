---
name: skill-builder
description: Erstellt oder verbessert auf konkreten Auftrag einen AIOS-Skill, prüft Überschneidungen und lässt Inhalt, Format und Verhalten unabhängig prüfen.
---

# Skills bauen und verbessern

Beachte den [Regelkern](../../regeln/kern.md) und die [Ablage](../../referenzen/ablage.md). Kläre nur wesentliche Lücken zu Zweck, Auslöser, gewünschtem Ergebnis, benötigtem Kontext, Befugnissen und überprüfbarem Abschluss. Fehlt eine benötigte Quelle oder technische Fähigkeit, frage zuerst nach und warte auf die Entscheidung.

Prüfe vor einem neuen Skill die vorhandenen Fähigkeiten auf Überschneidungen. Empfiehl eine Erweiterung oder Zusammenführung, wenn damit derselbe Zweck verständlicher abgedeckt wird. Trenne gemeinsame Arbeitsregeln, aufgabenspezifische Anweisungen und nur bei Bedarf geladene Referenzen. Kopiere keine allgemeinen Regeln, persönlichen Angaben, Kundendaten, Zugangsdaten oder festen Benutzerpfade in den Skill.

Bearbeite die kanonischen Quellen im bestätigten Quellordner. Installierte Kopien und erzeugte Spiegel sind keine Bearbeitungsquelle. Änderungen bestehender allgemeiner Regeln benötigen weiterhin den passenden Auftrag. Verfügbare Modelle oder Clientbefehle nicht aus alten Skills ableiten. Prüfe die aktuell benötigten Clientformate anhand geeigneter offizieller Quellen, wenn der vorhandene geprüfte Paketstand sie nicht abdeckt.

Erstelle konkrete Prüffälle für den üblichen Ablauf, fehlende benötigte Quellen, relevante Mehrdeutigkeiten und die Grenze zwischen Vorschlag und beauftragter Aktion. Prüfe lokale Verweise, Voraussetzungen und beide vorgesehenen Clientformate. Ein vorhandener allgemeiner Skill-Creator kann nach Prüfung helfen, ist aber keine Pflichtabhängigkeit. Ein einzelner Formatvalidator kann clientspezifische Felder falsch ablehnen und ersetzt keinen nativen Test.

Lass den Skill durch einen unabhängigen Prüfagenten anhand des Auftrags, der Quellen und der Prüffälle bewerten. Behebe bestätigte Befunde im beauftragten Umfang und lasse betroffene Stellen nachprüfen. Bei bestehenden Bugs bleibt die Diagnosefreigabe maßgeblich. Prüfe im vorgesehenen Client sowohl Aufruf und Ladung als auch tatsächliches Verhalten. Synthetische Daten bevorzugen. Externe Aktionen und zusätzliche Dienste nur im freigegebenen Umfang verwenden.

Berichte getrennt, was entworfen, formal geprüft, nativ geladen und im Verhalten nachgewiesen ist. Fehlende Modelltests, Zugänge oder Integrationsprüfungen bleiben ausdrücklich offen. Installiere oder veröffentliche nur im konkret beauftragten Umfang.

[Prüffälle](references/prueffaelle.md) sind Prüfvorgaben, keine bereits bestandenen Modelltests.
