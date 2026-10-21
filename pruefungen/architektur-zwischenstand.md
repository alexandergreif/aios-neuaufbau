# Architektur-Zwischenreview

Stand: 20.10.2026. Unabhängiger Review des lokalen Neuaufbaus, keine Produktionsänderungen.

**Architekturauswirkung: Mittel.** Die vier Bereiche sind sauber getrennt. Die vorhandenen Funktionsmodule reichen als Grundlage. Update und Deinstallation erfordern einen präziseren Eigentumsvertrag und wenige gemeinsame Funktionen, keine neue Servicearchitektur. Der ursprüngliche P1-Fehler und der anschließende P2-Vertragswiderspruch der Paketpfadregeln sind unabhängig nachgeprüft behoben. Keine offenen Fehler im nachgeprüften Paketpolicy-Fix. Die übrigen priorisierten Punkte sind Voraussetzungen für die noch nicht implementierten Betriebsabläufe.

## Nachprüfung des Paketpolicy-Fixes

20.10.2026: `scripts/paketregeln.py` stellt jetzt Script-Allowlist, Vorlagenausnahmen und Pfadprüfung gemeinsam bereit. Builder und Statuscheck verwenden diesen Vertrag. Das Modul wird in die Runtime aufgenommen. Der ursprüngliche P1-Befund für `secrets/`, `credentials/` und `journals/` ist behoben. Die synthetischen Lesewächter prüfen die Ablehnung vor dem Inhaltslesen. Genehmigte Vorlagen bleiben zulässig.

Unabhängig ausgeführt: `test_paketregeln.py` (2), `test_paket_bauen.py` (8), `test_einrichtungsstatus.py` (15) und `test_installieren.py` (14). **39 Tests erfolgreich.** Die Tests legen ausschließlich ihre eigenen synthetischen Daten und isolierten Installationsziele an. Keine aktive Installation oder externen Dienste wurden verwendet.

**P2, ursprünglicher Restbefund, inzwischen behoben:** `scripts/paketregeln.py:40` verbot jeden `.env`-Ordner, während die damalige Zeile 60 über `_safe_part()` die Ausnahme `.env.example` auch in Elternkomponenten erlaubte. Reproduktion vor der zweiten Korrektur:

```text
allowed_directory("allgemein/.env.example") -> False
allowed_file("allgemein/.env.example/token.txt") -> True
manifest_entries() mit diesem Pfad und formal gültigem Hash -> akzeptiert
```

Erwartet ist dieselbe erlaubte Paketstruktur für Builder und Manifestprüfung. Tatsächlich kann der Statusvalidator einen Pfad akzeptieren, dessen Elternordner der Builder verbietet. Die ursprünglichen drei privaten Verzeichnisse bleiben geschützt. Ein tatsächlicher privater Lesezugriff wurde für diesen Restfall nicht behauptet oder durchgeführt.

Kleinster Fix: `.env.example` nur als letzte Dateikomponente erlauben. Elternkomponenten in `allowed_file()` entsprechend der Ordnerprüfung begrenzen. Ein gezielter Vertragstest soll die normale Beispieldatei weiter zulassen und den obigen verschachtelten Pfad auf beiden Wegen ablehnen. Die folgenden ursprünglichen Befunde bleiben als Verlauf und als Grundlage für die noch offenen Betriebsabläufe erhalten.

**Abschließende Nachprüfung am 20.10.2026:** `allowed_file()` prüft nun vor regulären verschachtelten Dateien deren Elternpfad über `allowed_directory()`. Die expliziten Vorlagenausnahmen bleiben erhalten. Der originale Reproduktionspfad wird jetzt von Ordner-, Datei- und Manifestprüfung abgelehnt. Die normale `.env.example`-Datei sowie alle freigegebenen Vorlagen bleiben erlaubt. Dies wurde zusätzlich zu den Tests direkt mit den vorhandenen Funktionen bestätigt.

Unabhängig erneut ausgeführt: `test_paketregeln.py` (3, einschließlich `test_env_example_exception_is_only_for_a_file`), `test_paket_bauen.py` (8), `test_einrichtungsstatus.py` (15) und `test_installieren.py` (14). **40 Tests erfolgreich, kein offener Befund in diesem Fix.** Rendererdateien und parallel bearbeitete Komponenten waren nicht Gegenstand dieser Nachprüfung.

## Umfang und Nachweis

Gelesen wurden `.aios/PLAN.md`, Kernnotizen, `paketumfang-und-umsetzung.md`, README-Entscheidungen 77 bis 80 und 116a sowie die technischen Implementierungen für Einrichtung, Profiltransfer, Paketbau, Plan, Installation, Status und sichere Dateivorgänge. Zusätzlich wurden relevante Tests und Betriebsdokumente gesichtet. Die lokalen Python-Imports wurden per AST erfasst. Es besteht kein Importzyklus.

Die unten genannte Policy-Abweichung wurde durch direkte Aufrufe der vorhandenen Funktionen mit erfundenen Pfadnamen bestätigt. Keine echten Profile, Geheimnisse, Kundenverzeichnisse oder Ergebnisinhalte wurden gelesen. Keine Installation, Browser-, Modell-, Anbieter- oder Konnektoraufrufe. Der vom Hauptagenten gemeldete Stand von 97 Tests wurde hier nicht erneut ausgeführt. Python 3.13.16 ist der gemeldete Prüfstand, für ältere Python-Versionen wird keine Kompatibilität behauptet.

## Prüfung der Architekturprinzipien

| Kriterium | Bewertung |
| --- | --- |
| Quellcode, Runtime, Profil und Ergebnisse getrennt | Erfüllt. `pruefe_konfiguration.validate()` prüft Bereichsüberschneidungen. Paketbau übernimmt ausgewählte Quellen. |
| Vorschau getrennt von Änderung | Erfüllt für Erstinstallation. Plan bleibt rein lesend, Installer prüft Konfiguration, Quellen und Ziele nach Bestätigung erneut. |
| Verantwortung klar verteilt | Überwiegend erfüllt. Konfigurationsprüfung, Dateivorgänge und Abläufe sind eigenständig. Paketbau hängt unnötig vom Client-Testvorbereiter ab. |
| Abhängigkeiten und Zyklen | Keine Zyklen. Gemeinsame Regeln sollten aus CLI-Modulen in kleine untergeordnete Module wandern, sobald die Betriebsabläufe sie gemeinsam benötigen. |
| Angemessene Abstraktion | Erfüllt. Funktionen, kleine Datenobjekte und eine Journal-Klasse passen zum Umfang. Kein Bedarf für Repository-, Provider- oder Serviceklassen pro Dateivorgang. |
| Ein gemeinsamer Vertrag für Paket und Eigentum | Teilweise erfüllt. Manifest und Eigentum sind getrennt, die Pfadpolitik und Clientzielberechnung werden jedoch mehrfach gepflegt. |
| Schutz persönlicher Daten | Bereichsprüfung und eng begrenzter Profiltransfer sind gut. Der belegte Unterschied der Paketpfadregeln muss geschlossen werden. |
| Ehrlicher Funktionsstatus | Erfüllt im vorhandenen Statuscheck. Dateiintegrität wird ausdrücklich von Modell-, Dienst- und Fachfunktion getrennt. |

## Priorisierte Befunde

### P1: Builder und Statuscheck erlauben unterschiedliche Paketpfade (behoben)

**Belegter Fehler.** Fundstellen: `scripts/paket_bauen.py:32`, `:48`, `:53`, `:115` und `scripts/einrichtungsstatus.py:23`, `:86`.

Der Builder sperrt unter anderem `journal`, aber nicht `journals`, `secrets` oder `credentials` als Verzeichnisnamen. Der Statuscheck sperrt diese zusätzlichen Namen. Direkter Vergleich der vorhandenen Funktionen:

| Erfundenes Paketobjekt | Builder-Policy | Status-Policy |
| --- | --- | --- |
| `allgemein/secrets/token.txt` | erlaubt | abgelehnt |
| `allgemein/credentials/token.txt` | erlaubt | abgelehnt |
| `allgemein/journals/action.json` | erlaubt | abgelehnt |
| `allgemein/zustand/state.json` | abgelehnt | abgelehnt |

Damit würde ein versehentlich unter diesen Namen abgelegter privater Bestand vom Builder gelesen und paketiert. Erst der spätere Statuscheck verwirft das resultierende Manifest. Es wurde kein solcher realer Bestand festgestellt oder gesucht.

**Kleinste Korrektur:** Eine gemeinsame reine Paketpfadprüfung einschließlich Vorlagenausnahmen und Script-Allowlist einführen. Builder wendet sie vor dem Lesen jedes Objekts an, Manifestvalidator verwendet denselben Vertrag. Ein kleiner Vertragstest muss die obigen Fälle auf beiden Wegen prüfen. Keine Inhaltssuche nach Geheimnissen ergänzen. Der Schutz entsteht durch Ablagegrenzen und Pfadprüfung.

### P1: `created_directories` ist keine sichere Löschliste

**Voraussetzung vor Deinstallation, kein behaupteter Fehler des Erstinstallers.** Fundstellen: `scripts/installieren.py:202`, `:205`, `:209`, `:216`, `:222`, `:235` sowie `scripts/einrichtungsstatus.py:175`.

Die Liste enthält gemeinsam technische Zustandsordner, Ausgabeordner und gegebenenfalls neu angelegte Vorfahren der Runtime oder Clientordner. Die Runtime-Wurzel und ihre intern erstellten Unterordner werden dagegen nicht vollständig als eigene Verzeichniseinträge erfasst. Der Statusvalidator akzeptiert Vorfahren zulässiger Ziele bis unterhalb der Systemwurzel. Das ist eine Prüfung der Anlagehistorie, keine Löschbefugnis.

**Kleinster Vertrag:** Dateieinträge ausdrücklich als `runtime_file`, `client_rule` oder `client_link` einordnen oder diese Rollen durch eine gemeinsame validierte Ableitung bestimmen. Profil, Ausgabe und deren Vorfahren bleiben immer geschützt, unabhängig davon, wer sie angelegt hat. Runtime-Unterordner ausschließlich aus validierten Runtime-Dateipfaden ableiten und nur leer entfernen. Neu angelegte Client-Unterordner nur als ausdrücklich erlaubte, leere Verzeichnisse entfernen. Keine allgemeine Bereinigung von Vorfahren. Der Profilordner `zustand` und sein Bericht dürfen erhalten bleiben.

Der Deinstaller darf nur unveränderte erfasste Dateien und passende Links entfernen. Fremde Zusatzdateien bleiben stehen. Geänderte Dateien führen zu Konflikten. Für die erste Version ist ein vollständiger Stopp vor Mutation bei einem solchen Konflikt am einfachsten. `_remove_tree()` aus `sichere_dateien.py:188` ist ausschließlich für den selbst erzeugten temporären Paketbaum geeignet, nicht als Deinstallationsfunktion.

### P1: Das laufende Journal darf nicht die einzige Grundlage für spätere Eigentumsentscheidungen bleiben

**Voraussetzung vor Update und Deinstallation.** Fundstellen: `scripts/installieren.py:90`, `:125`, `:201`, `:241` sowie `scripts/einrichtungsstatus.py:150`, `:216`.

Die aktuelle `installation.json` dient zugleich als Eigentumsstand und laufendes Journal. `Journal.save()` kürzt die Datei und schreibt sie neu. Ein Prozessabbruch kann die einzige Eigentumsdatei unlesbar hinterlassen. Das ist für den aktuellen Entwicklungsstand dokumentiert. Beim Update würden darüber hinaus alte und neue Hashes sowie bereits ausgeführte Teiloperationen zusammenkommen. Der Statuscheck akzeptiert bisher nur einen vollständig installierten Stand und eine einzige Paketversion.

**Kleinster Vertrag:** Einen zuletzt vollständig bestätigten Eigentumsstand behalten und eine separate kleine Operationsdatei für `update` oder `uninstall` führen. Diese enthält Operationskennung, Ausgangs- und Zielmanifest-Hash, konkrete geplante Dateioperationen und deren Status. Keine Inhalte oder Geheimnisse speichern. Operationsabsicht vor der Änderung festhalten. Bei Unterbrechung bleibt der Ausgangsstand verfügbar und der Status meldet eine offene oder fehlgeschlagene Operation. Nicht blind wiederholen und keinen Erfolg allein aus dem alten Stand ableiten.

Den neuen bestätigten Stand erst nach Integritätsprüfung sicher veröffentlichen. Das braucht einen zentralen Schreibweg mit exklusiver Operationssperre, Prüfung des bestehenden Ziels und atomarer Veröffentlichung einer vorbereiteten Zustandsdatei. Eine physische Datenträgergarantie darf nur entsprechend tatsächlich umgesetzter Synchronisation behauptet werden. Es ist keine Rückkehr zur alten Paketversion erforderlich. Metadatenhaltbarkeit ist keine Rollbackfunktion.

### P2: Tatsächlich gewählte Clientorte brauchen einen gemeinsamen, dauerhaften Vertrag

Fundstellen: `scripts/installationsplan.py:75`, `:84`, `:133`, `:143`, `scripts/einrichtungsstatus.py:77`, `:133`, `:188` und `scripts/installieren.py:202`.

Plan und Status berechnen Clientziele separat. Abweichende Orte werden im Eigentumsstand nur indirekt als Dateipfade erfasst. Der spätere Aufruf muss die Overrides erneut passend angeben, sonst erwartet der Statuscheck Standardorte und verwirft den Eigentumsstand. Das ist dokumentiert, erschwert aber einen zuverlässigen gemeinsamen Einstieg und spätere Updates.

**Kleinste Ergänzung:** Die bei Installation bestätigten Clientwurzeln und die Codex-Skillbasis als technische Bindungen im Eigentumsstand festhalten. Eine reine Funktion berechnet daraus Regeln und Skilllinks. Plan, Status, Update und Deinstallation verwenden sie gemeinsam. Eingelesene Bindungen vollständig gegen Profil, Ausgabe, Runtime, Systemwurzel und Benutzerordner prüfen. Ein gespeicherter Pfad allein ist keine Schreib- oder Löschbefugnis. Abweichende spätere CLI-Orte als expliziten Konflikt behandeln, nicht still in eine Migration umdeuten.

Das ist auch für noch nicht eingerichtete Dienstverbindungen wichtig. Clientkonfigurationen dürfen später nur über klar abgegrenzte eigene Einträge mit vorherigem Zustand und Sicherung geändert werden. Der gegenwärtige vollständige Eigentumsanspruch auf neu erzeugte `AGENTS.md` und `CLAUDE.md` darf nicht auf eine schon vorhandene fremde Konfigurationsdatei übertragen werden.

### P2: Ein gemeinsamer Installationsaufruf fehlt noch

Fundstellen: `install.sh:4`, `scripts/installieren.py:257`, `scripts/einrichten.py:140`, `:169`, `:179`.

`install.sh` verlangt eine vorhandene bestätigte Konfiguration. Auf dem frischen Mac muss die Profileinrichtung separat gestartet und ihr Ergebnis an den Installer übergeben werden. Die Funktionen sind sinnvoll getrennt, die Nutzerführung ist noch nicht zusammengeführt.

**Kleinste Orchestrierung:** Ein dünnes `setup.py` als gemeinsamen Einstieg ergänzen. `install.sh --config ...` behält seine heutige Bedeutung. Ohne `--config` führt der Einstieg die Profileinrichtung aus und übergibt deren bestätigten Konfigurationspfad an den bestehenden Installationsablauf. Dafür den interaktiven Profilablauf aus `main()` in eine Funktion extrahieren, die nach erfolgreichem Speichern den Pfad zurückgibt und Abbruch eindeutig meldet. `main()` bleibt ein kleiner CLI-Adapter. Kein Parsen von Standardausgabe, kein Geheimnis in Argumenten und keine temporäre Übergabedatei nötig.

Zwei konkrete Vorschauen sind richtig: zuerst Profil und Pfade, danach Runtime und Clientänderungen. Die Bestätigung der Profileinrichtung autorisiert nicht automatisch die Installation. Bei Abbruch der zweiten Stufe bleibt das bestätigte Profil erhalten und der Einstieg nennt den nächsten Aufruf. Ein frühzeitig absehbarer Installationskonflikt kann vor dem Profil-Schreiben angezeigt werden, benötigt aber keine automatische Bereinigung.

Voraussetzungen nur prüfen und fehlende Programme mit nächstem Schritt melden. Nichts automatisch installieren. Kompatibilität derzeit nur für den tatsächlich getesteten Python-Stand ausweisen. Weitere Mindestversionen benötigen einen eigenen Nachweis.

## Kleinster Integrationsweg für Update und Deinstallation

1. **Gemeinsame Verträge:** Ein kleines Modul für Paketpfade, Manifestvalidierung und Script-Allowlist. Ein zweites für Eigentumsstand und Clientzielberechnung. Die bestehenden fd-gebundenen Dateifunktionen bleiben die gemeinsame technische Unterlage. Keine Verlagerung der Profiltransfer-Semantik in die Paketpolicy, deren erlaubte Inhalte unterscheiden sich bewusst.
2. **Rein lesender Operationsplan:** Update erhält bestätigten Ist-Eigentumsstand und validierten Zielpaket-Snapshot. Die Differenz ergibt `add`, `replace`, `remove` und `keep`. Für jeden geänderten Eintrag stehen alter Hash oder Linkziel und neuer Hash oder Linkziel fest. Neue Ziele müssen fehlen, bestehende müssen zum Ausgangsstand passen. Fehlende oder veränderte eigene Objekte sind Konflikte, keine automatische Reparatur. Deinstallation verwendet denselben Prüfweg mit gezielten `remove`-Operationen. Client- oder Bereichsmigration zunächst ausdrücklich ablehnen.
3. **Konkrete Vorschau:** Ausgangs- und Zielversion, zusätzlich Manifest-Hash, Änderungen, Voraussetzungen und Konflikte anzeigen. `VERSION = 0.1.0-dev` allein unterscheidet Entwicklungsstände nicht. Die Vorschau enthält keine privaten Datei-Inhalte. Standardmäßig bleibt es bei der Vorschau. Vor Ausführung ausdrücklich bestätigen und den Plan anschließend erneut validieren.
4. **Gezielte Ausführung:** Nur die geplanten eigenen Objekte verändern. Vor jeder Ersetzung oder Entfernung Identität, Typ, Hash beziehungsweise Linkziel erneut prüfen. Pfadschutz und gebundene Elternordner aus `sichere_dateien.py` verwenden. Betroffene eigene globale Regeldateien vor Ersetzung sichern. Sicherungen liegen privat im technischen Zustandsbereich. Fremde Clientkonfiguration bleibt unberührt. Keine rekursive Löschung oder vollständige Ersetzung einer Runtime, die unbekannte Zusatzdateien enthalten kann.
5. **Teilzustand offenlegen:** Operationsjournal vor und nach den einzelnen Schritten aktualisieren. Bei Fehler anhalten, tatsächlichen Teilstand und offene Schritte melden. Keine automatische Rückkehr oder automatische Fortsetzung als Voraussetzung einführen. Der Statuscheck muss die offene Operation berücksichtigen und kann dann nicht `vorhanden` als vollständigen Erfolg ausweisen.
6. **Abschluss prüfen:** Dateiintegrität, Regeln und Links prüfen. Erst danach den neuen Eigentumsstand veröffentlichen. Deinstallation prüft das gezielte Fehlen der entfernten Objekte und den Erhalt der geschützten Bereiche. Fachliche Funktionsabnahme bleibt separat, angemeldete Modelltests bleiben auf dem zweiten Mac.

Die Ablaufimplementierungen können einfache Funktionen in `aktualisieren.py` und `deinstallieren.py` bleiben. Ein gemeinsamer Plan-Datensatz und ein enger Dateiausführer genügen. Keine automatische Updateprüfung, kein Paketmanager für fremde Programme und kein allgemeines Transaktionsframework erforderlich.

## Angemessene kleine Entkopplung

`paket_bauen.py` importiert `generated_core()` und Zielprüfung aus `client_vorbereiten.py`, dieses wiederum importiert aus der interaktiven Einrichtung. Die resultierende Richtung ist technisch zyklusfrei, koppelt aber Produktion an Testvorbereitung. Bei den genannten Erweiterungen Regelrendering in ein kleines gemeinsames Modul verschieben und Pfad-/Dateihilfen in die vorhandene technische Unterlage aufnehmen. Den Unterschied zwischen relativen Referenzen im isolierten Testpaket und absoluten Referenzen in globalen Regeln explizit als Parameter oder getrennte kleine Funktionen behalten.

Nicht jede ähnliche Funktion muss vereinigt werden. Ein Profilimport hat andere Datenschutz- und Bestätigungsregeln als ein Paketupdate. Gemeinsame Byte-/Pfadoperationen sind sinnvoll, ein universeller Import-/Installationsdienst würde die Grenzen verwischen. Langfristig sinkt der Pflegeaufwand besonders durch eine einzige Paketpolicy und Zielberechnung. Dort verursacht die heutige Duplikation bereits einen nachgewiesenen Widerspruch.

## Gezielte Abnahme der Erweiterung

- Gemeinsamer Einstieg auf synthetischem frischem Home, Profilabbruch, Installationsabbruch nach erfolgreichem Profil sowie fehlendes Programm. Keine automatische Programminstallation.
- Update mit neuer, geänderter und entfallener Paketdatei. Lokale Änderung an jeder Eigentumsrolle stoppt vor Mutation. Eine unbekannte Zusatzdatei bleibt erhalten.
- Erhaltung von Profil, `.env`, Wissen, Journal und Ausgabe anhand synthetischer Marker. Der Test muss unerlaubtes Lesen genauso wie Schreiben feststellen.
- Abweichende Clientorte funktionieren nach erneutem Aufruf ohne wiederholte versteckte Ortsannahmen. Geänderte Bindungen oder ungültige Manifestpfade stoppen vor Zugriff.
- Fehlersimulation während einer Dateioperation und während der Zustandsveröffentlichung. Vorheriger Eigentumsstand bleibt lesbar, Status meldet die offene Operation und behauptet keinen Rollback.
- Deinstallation mit unveränderten eigenen Objekten, geändertem Link, fremder Datei im Runtime-Unterordner und inzwischen genutztem Ausgabeordner. Leere private Bereiche bleiben ebenfalls erhalten.

## ADR-Vorschlag

Der folgende Stub bleibt als Vorschlag in diesem Review. Nach Übernahme kann er in einer späteren `docs/decisions/`-Ablage geführt werden. Außer diesem Reviewbericht wurde keine Datei angelegt.

### ADR-0001: Eigentumsstand und Betriebsoperationen getrennt führen

**Date:** 2026-10-20
**Status:** Proposed
**Context:** Updates und Deinstallation benötigen verlässliche frühere Hashes und Clientbindungen. Das aktuelle Erstinstallationsjournal wird bei jeder Zustandsänderung überschrieben und vermischt Anlagehistorie mit späterer Löschbefugnis.
**Decision:** Einen validierten abgeschlossenen Eigentumsstand mit Rollen und bestätigten Clientbindungen führen. Laufende Änderungen separat als begrenzte Operationsdaten erfassen. Alle Betriebsbefehle verwenden gemeinsame Paketpfad- und Eigentumsvalidierung. Profil, Ausgabe und fremde Konfiguration sind keine aus Anlagehistorie ableitbaren Löschziele.
**Consequences:** Wenige zusätzliche Metadaten und ein eng begrenzter gemeinsamer Schreibweg. Verlässliche Konflikterkennung und ehrlicher Teilstatus werden möglich. Automatische Wiederherstellung und Migration bleiben außerhalb dieses Beschlusses.
