# Profil und Wissen einrichten und pflegen

Diese Referenz wird bei Einrichtung, Profilpflege, Wissensaufnahme oder Profiltransfer gebraucht. Sie ist keine zusätzliche Startdatei und kein Ladeplan. Paketvorlagen unter `../vorlagen/` bleiben leer. Tatsächliche Inhalte gehören in den konfigurierten privaten Profilordner.

## Einrichtung

1. Vorhandene bestätigte Angaben verwenden. Noch fehlende Angaben zu Name, Rolle, Sprache, Zeitzone, Arbeitszeiten, Arbeitsweise und Prioritäten gezielt klären. Nichts aus dem Benutzernamen oder anderen privaten Dateien ableiten. Das Feld Sprache bestimmt die Ausgabesprache, bei mehreren Angaben die zuerst genannte. Bei mehreren Sprachen nach der bevorzugten fragen und sie zuerst eintragen.
2. Vorschau der zu speichernden Angaben zeigen. Unbeantwortetes als offen kennzeichnen. Erst nach Bestätigung `profil.md` im gewählten Profilordner anlegen. Vorhandene Dateien nicht still überschreiben.
3. Coding- und Kundenprojektwurzeln je Mac abfragen. Die Registrierung konkreter Projekte ist eine eigene Zuordnung, kein Auftrag, alle Unterordner zu durchsuchen. Im privaten `projekte.md` eindeutige Kürzel und bestätigte Ordner führen.
4. `wissen/INDEX.md` und kurze Themennotizen nur bei tatsächlicher Wissensaufnahme nutzen. Technische Zustandsdaten unter `zustand/` halten. Diese privaten Unterordner werden weder aus dem Paket aktualisiert noch bei dessen Deinstallation entfernt.

## Pflege

- Neue dauerhafte Angaben als konkrete Änderung mit Vorschau vorschlagen und bestätigen lassen. Ein eindeutiges „Merk dir das“ enthält die Speicherung bereits als Auftrag.
- Kleine ausdrücklich genannte dauerhafte Vorlieben, etwa Antwortlänge oder Ausgabeformat, dürfen ohne Rückfrage gespeichert werden. Kurz mitteilen und Korrektur oder Löschung ermöglichen. Bei Konflikt mit einer bestehenden Regel zuerst klären.
- Vermutungen, sensible Angaben, Befugnisse, Zusagen und Regeländerungen fallen nicht unter diese Ausnahme. Nur für einen Auftrag geäußerte Wünsche bleiben auf ihn begrenzt.
- Projektentscheidungen gehören in die dortigen Arbeitsdateien. Nicht zusätzlich als allgemeine Profilregel pflegen. Persönliche Aufgaben bleiben in To Do, Projekttickets in Jira.

## Wissen

Wiederverwendbare Erkenntnis mit Quelle, Fundstelle, Datum, Gültigkeitsbereich und offenen Unsicherheiten vorschlagen. Erst nach Bestätigung dauerhaft speichern und im Index verlinken. Ein ausdrücklicher Speicherauftrag genügt. Keine vollständigen Chats, Nachrichten oder Dokumente automatisch importieren. Bei widersprüchlichen Quellen gilt der gemeinsame Regelkern.

## Bewusster Transfer auf einen anderen Mac

Der Export-/Importablauf zeigt die ausgewählten Profilfelder und eine Änderungsvorschau. Persönliche Profilangaben können übertragen werden. Ordnerzuordnungen werden auf dem Ziel-Mac neu bestätigt. Die lokale Pfadkonfiguration ist kein übertragbares Profil.

`.env`, sonstige Zugangsdaten, OAuth-Dateien, Aktionsjournal, Diagnoseprotokolle und Ergebnisdateien gehören nicht in den Profilexport. Ein Export darf nicht den gesamten Profilordner blind kopieren. Links auf Dateien außerhalb der bestätigten Auswahl nicht verfolgen. Bei abweichenden bestehenden Angaben eine Zusammenführung zur Entscheidung vorlegen, nicht automatisch überschreiben.

Das Paket enthält dafür `scripts/profile_transfer.py`. Es exportiert ausschließlich die sieben Profilfelder und kleine Vorlieben. Beim Import werden abweichende Werte einzeln angezeigt. Die erste Fassung bietet einen ausdrücklich bestätigten Ersatz des Profils mit Sicherung, keine automatische Zusammenführung. Pfade, Projektregister und Wissen bleiben lokal. Der synthetisch geprüfte Ablauf ist in `docs/profiltransfer.md` beschrieben.
