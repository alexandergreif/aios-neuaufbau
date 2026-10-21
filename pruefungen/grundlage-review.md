# Unabhängige Prüfung der lokalen Grundlage

Stand: 19.10.2026. Geprüft durch einen an der Erstellung unbeteiligten Agenten. Abschließendes Urteil: Die geprüfte lokale Grundlage ist freigegeben. Keine offenen Befunde. Alle 19 Tests und die gezielten unabhängigen Nachprüfungen sind erfolgreich. Auch die zusätzliche Empfehlung zur Testqualität wurde umgesetzt und nachgeprüft.

Diese Freigabe umfasst keine Installation, Clientanbindung oder vollständige Abnahme der Etappe 2. Die nachfolgenden Erstbefunde und Zwischenstände dokumentieren den Prüfverlauf. F1, F2, F3, F4, S1 und S2 sind nachgeprüft und geschlossen.

## Umfang und Vorgehen

Vollständig gelesen: `scripts/pruefe_konfiguration.py`, `tests/test_konfiguration.py`, Pfadvorlage, `.env.example`, Pfaddokumentation, Regelkern, Altregelvergleich sowie alle neuen Profil-, Register-, Wissens- und Projektvorlagen und die beiden Fachreferenzen. Soll: `paketumfang-und-umsetzung.md` und die einschlägigen bestätigten Entscheidungen in `README.md`. Die fünf im Altvergleich genannten Dateien unter `~/.agent-rules/` wurden als historische Vergleichsquellen gelesen.

Der Ordner ist kein Git-Repository. `git log` und `git diff` konnten daher keinen Versionsvergleich liefern. `.aios/PLAN.md` und die Kernnotizen wurden gelesen. `tasks/todo.md` und `tasks/lessons.md` sind im Zielordner nicht vorhanden. Es wurden keine Kundenordner, Profile, Archive oder Zugangsdaten gelesen. Zusätzliche Testdaten lagen ausschließlich in selbst erzeugten `TemporaryDirectory`-Verzeichnissen.

## ⚠️ HIGH PRIORITY

### F1: Mac-Dateialiasse umgehen die Ablagetrennung

Status der ersten Runde: offen. Fundstelle: `scripts/pruefe_konfiguration.py`, Funktion `overlaps`, ursprünglich Zeilen 57 bis 58, nach erster Zwischenänderung Zeilen 59 bis 60. Einstufung: bug, hohe Priorität.

Der Vergleich von `Path`-Objekten berücksichtigt weder Groß-/Kleinschreibung noch Unicode-Normalisierung des Mac-Dateisystems. Auf dem tatsächlich verwendeten Dateisystem wurden diese Fälle unabhängig reproduziert, jeweils mit Exitcode 0 und der Meldung einer gültigen Konfiguration:

- Existierender Ordner `runtime`, konfiguriert als Runtime `~/runtime` und Profil `~/RUNTIME`. Beide bezeichnen denselben Ordner.
- Noch nicht angelegte Runtime `~/NewFolder` und Profil `~/newfolder/private`. Das Profil läge nach Anlage unter der Runtime.
- Existierender Ordner `café` mit zusammengesetztem Akzent (NFC), konfiguriert einmal in NFC und einmal mit getrenntem Akzent (NFD). Beide bezeichnen denselben Ordner.

Die beabsichtigte Trennung privater Daten vom aktualisierbaren Paket ist damit nicht nachgewiesen. Minimale Abhilfe: Dateisystemidentität bestehender Komponenten beachten und noch fehlende Komponenten konservativ hinsichtlich Schreibweise und Unicode-Normalisierung vergleichen. Dieselbe Vergleichslogik muss die Benutzerordnersperre und die erlaubte Source-Ausnahme abdecken. Die drei Fälle als Regressionstests aufnehmen.

### F2: Bestehende Symlinkschleifen werden als gültige Pfade bestätigt

Status der ersten Runde: offen. Fundstellen: `scripts/pruefe_konfiguration.py:51` und `scripts/pruefe_konfiguration.py:111` im Stand nach der ersten Zwischenänderung. Einstufung: bug.

Unter dem tatsächlich eingesetzten Python 3.13.16 liefert `Path.resolve(strict=False)` bei einem Symlink `loop -> loop` einen Pfad zurück, ohne die erwartete Exception auszulösen. Unabhängig reproduziert: `runtime=~/loop` wird mit Exitcode 0 akzeptiert. Dasselbe geschieht mit einer solchen Schleife als `--home`. Der Prüfer hat in diesen Fällen die bestehende Pfadstruktur nicht erfolgreich aufgelöst.

Minimale Abhilfe: Vorhandene Komponenten auf nicht auflösbare Symlinks und andere Auflösungsfehler prüfen und geschlossen mit bereinigter Fehlermeldung ablehnen. Noch nicht existierende Verzeichnisse bleiben zulässig. Regressionstests müssen Ablagepfad und Benutzerwurzel abdecken.

### F3: Schutz wichtiger Ergebnisfassungen fehlt im neuen Regelbestand

Status der ersten Runde: offen. Fundstelle: `allgemein/regeln/kern.md:9`. Einstufung: bug im Soll-Abgleich.

Entscheidung 87 in `README.md:224` verlangt, vor umfangreichen Überarbeitungen oder dem Ersetzen einer freigegebenen Ergebnisfassung die vorherige Fassung zu erhalten. Der neue Kern verlangt nur kurze Arbeitsdateien und deren Aktualisierung. Auch die beiden neuen Referenzen und die Vorlagen enthalten den Erhalt bisheriger Ergebnisfassungen nicht.

Minimale Abhilfe: Die Regel im Arbeitsstandabschnitt oder einer dort konkret verlinkten Referenz ergänzen. Kleine Korrekturen dürfen weiterhin im aktuellen Arbeitsstand erfolgen.

## 💡 SUGGESTIONS

### S1: Monatlichen Modellcheck im Altvergleich klar abgrenzen

Fundstelle: `docs/regelabgleich.md:30`. Einstufung: suggestion.

Die gemeinsame Tabellenzeile ordnet den monatlichen Modellcheck, Produktdaten und Herstellerquellen als „Verlagern“ einem optionalen Prüfablauf zu. Der Paketumfang nimmt jedoch keinen monatlichen Modellcheck allein aus der Nähe zum Prompt-Berater auf. Turnus und Produktinformationen getrennt zuordnen: Der automatische Turnus entfällt im aktuellen Paketumfang, aktuelle Produktinformationen dürfen bei konkretem Bedarf im Prompt-Berater geprüft werden.

## Nachgewiesene Prüfungen

- Die erste unveränderte Testsuite lief mit `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`: 8 Tests, alle erfolgreich.
- Zusätzliche synthetische CLI-Fälle wiesen falsche JSON-Typen für Version, Bestätigung, Clients, Pfadobjekt und Pfadlisten ab. Auch unhashbare Clientwerte führten kontrolliert zu Exitcode 1.
- Doppelte JSON-Schlüssel wurden sowohl auf der obersten Ebene als auch innerhalb von `paths` abgewiesen.
- Die vorhandenen Tests prüfen Bestätigung, ungültige Pfadformen, direkte Überschneidungen, einen einfachen Symlinkalias und bereinigte Fehlermeldungen.
- Der Prüfer enthält keine Dateischreibaufrufe. Sein positiver Test legte keine Zielordner an. Die zusätzlichen Testläufe änderten keine Zielverzeichnisse außer den ausdrücklich vom Test selbst angelegten synthetischen Ordnern und Links.
- Die ausgelieferte Vorlage ist unbestätigt und enthält keine aktiven persönlichen Pfade. Die `.env.example` enthält nur einen leeren Platzhalter.
- Die Referenzen trennen Profilpflege, Wissen, Journal und technische Protokolle. Export-/Importwerkzeug, ausführbares Journal und dienstspezifische Adapter sind ausdrücklich als offen benannt.

## Bereits während der Prüfung korrigierte Punkte

Der Hauptagent hatte folgende Punkte selbst erkannt und zur Korrektur gegeben: feste persönliche Namensansprache, fehlende konkrete Referenzlinks und fehlende Ausnahme für den regulären Hauptclient bei zusätzlichen KI-Diensten. Die aktualisierte Kernfassung wurde gelesen, diese drei Punkte sind dort behoben.

Die zusätzlich vom Hauptagenten verlangte Zulassung ausdrücklich leerer Projektwurzellisten und einer Source innerhalb einer Codingwurzel war beim letzten Codeabruf bereits umgesetzt. Die vollständige Nachprüfung dieser Zwischenänderungen sowie der offenen Befunde steht noch aus.

## Grenzen der Bewertung

Dies ist eine Prüfung der lokalen Grundlage. Die gesamte Etappe 2 ist damit nicht abgenommen. Profilexport/-import, Registervalidierung, konkrete Projektzuordnung, minimale Clientanbindung und Verhalten im laufenden Claude Code und Codex bleiben offen, soweit sie nicht gesondert umgesetzt und geprüft wurden.

Es wurden keine produktiven Laufzeitlimits, Pools oder Zeitüberschreitungen geändert. `schema_version=1` ist eine Formatkennung. Ein Lasttest ist für diesen lokalen, nur lesenden Pfadprüfer kein passender Sicherheitsnachweis. Maßgeblich sind hier negative Pfadfälle, Datentypen, Dateisystemverhalten und nachvollziehbare Exitcodes. Es gibt keine aktivierte Installation zurückzurollen. Ein späterer Installer muss Pfadgrenzen unmittelbar vor Schreibaktionen erneut prüfen, da eine frühere Prüfung keine späteren Dateisystemänderungen ausschließt.

## Erste Nachprüfung

Die vollständige geänderte Implementierung und Testsuite wurden erneut gelesen. Die 17 Tests bestanden unabhängig. Die ursprünglichen Fälle mit bestehenden und künftigen Schreibvarianten, Unicode-Alias sowie Symlinkschleife als Runtime und als Benutzerordner wurden zusätzlich außerhalb der Testsuite wiederholt. Alle liefern jetzt kontrolliert Exitcode 1. Die bestätigten leeren Projektlisten und die Source-Ausnahme sind in der Testsuite abgedeckt.

F2 ist behoben. F3 ist durch den ausdrücklichen Fassungserhalt in `allgemein/regeln/kern.md:9` behoben. S1 ist durch die getrennten Einträge in `docs/regelabgleich.md:30` und `docs/regelabgleich.md:31` behoben.

### F1, verbleibender Teil: Benutzerordner in anderer Schreibweise

Fundstelle im nachgeprüften Stand: `scripts/pruefe_konfiguration.py:73`. Der Vergleich gegen `home` verwendet weiterhin rohe `Path`-Gleichheit. Synthetischer Fall: `--home=<temp>/home`, Runtime `<temp>/HOME`, andere Bereiche als getrennte Geschwister außerhalb dieses Benutzerordners und leere Projektlisten. Ergebnis: Exitcode 0 auf dem case-insensitiven Dateisystem. Runtime und Benutzerordner bezeichnen denselben Ort.

Minimale Abhilfe: Auch die Benutzerordnersperre auf den bereits eingeführten normalisierten Komponentenvergleich umstellen und separat testen.

### F4: Doppelslash umgeht die Systemwurzelsperre

Fundstellen im nachgeprüften Stand: `scripts/pruefe_konfiguration.py:40`, `scripts/pruefe_konfiguration.py:73` und `scripts/pruefe_konfiguration.py:145`. Einstufung: bug, hohe Priorität.

Der neue Resolver übernimmt `Path(path.anchor)` ungeprüft. Für den Eingabepfad `//` gibt es keine weiteren Komponenten, sodass die Normalisierung ausbleibt. Auf dem geprüften Mac bezeichnet `//` dieselbe Systemwurzel wie `/`, wird aber als anderer `Path` verglichen. Sowohl `runtime="//"` mit sonst getrennten synthetischen Bereichen als auch `--home //` liefern Exitcode 0.

Minimale Abhilfe: Den vorhandenen Rootanker vor dem Komponentenlauf streng auflösen oder doppelte führende Slashes ausdrücklich abweisen. Systemwurzel als Bereich und als `--home` getrennt testen.

## Abschließende Nachprüfung

Die letzten Änderungen an den Systemwurzel- und Benutzerordnergrenzen wurden erneut gelesen. Die vollständige Testsuite lief unabhängig mit `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`: 19 Tests erfolgreich unter Python 3.13.16.

Die gezielten CLI-Nachprüfungen verwendeten für alle übrigen Ablagebereiche getrennte Geschwisterordner außerhalb des synthetischen Benutzerordners und leere Projektwurzellisten. Dadurch konnte keine andere Überschneidungsprüfung den tatsächlichen Erfolg der Benutzerordnersperre verdecken.

| Fall | Beobachtet |
| --- | --- |
| Benutzerordner `home`, Runtime `HOME` | Exit 1, kontrollierte Fehlermeldung |
| Benutzerordner mit getrenntem Akzent, Runtime mit zusammengesetztem Akzent | Exit 1, kontrollierte Fehlermeldung |
| Runtime `//` | Exit 1, kontrollierte Fehlermeldung |
| Benutzerordner `--home //` | Exit 1, kontrollierte Fehlermeldung |
| Gültige getrennte Bereiche und bestätigte leere Projektlisten | Exit 0 |
| Unveränderte ausgelieferte Vorlage | Exit 1 wegen fehlender Bestätigung |

Keine dieser Nachprüfungen erzeugte die konfigurierten Zielordner. F1 einschließlich Benutzerordnersperre und F4 sind damit geschlossen. F2, F3 und S1 waren bereits in der ersten Nachprüfung geschlossen.

`docs/grundlage.md` wurde zusätzlich gelesen. Die Statusmatrix und verbleibenden Arbeiten grenzen Paketquellen, ausführbaren Pfadprüfer und offene native Clientabnahmen nachvollziehbar ab. Die Dokumentation nennt im abschließend geprüften Stand die 19 bestandenen Tests.

### S2: Benutzerordner-Regressionstest isolieren

Die optionale Testverbesserung wurde umgesetzt: `test_home_alias_by_case_or_unicode_is_rejected` setzt die anderen Bereiche nun als Geschwister außerhalb des geprüften Benutzerordners, verwendet leere Projektlisten und prüft zusätzlich die konkrete Benutzerordner-Fehlermeldung. Damit verdeckt keine allgemeine Überschneidung einen erneuten Fehler der ausdrücklichen Sperre. Geänderten Test gelesen und mit `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -k home_alias -v` gezielt erneut erfolgreich ausgeführt. S2 ist geschlossen.
