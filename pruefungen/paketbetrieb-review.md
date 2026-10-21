# Unabhängiger Architektur- und Sicherheitsreview des Paketbetriebs

Stand: 20.10.2026. Erstprüfung und unabhängige Nachprüfung des jeweils als stabil gemeldeten Codestands abgeschlossen.

**Abschlussergebnis: Alle vier Befunde unabhängig nachgeprüft und geschlossen. Keine offenen Befunde im geprüften technischen Umfang.** 80 gezielte Tests des finalen Stands wurden unabhängig erfolgreich ausgeführt. Zusätzliche eigene Manipulations-, Konkurrenz- und harte Abbruchproben bestätigen die Korrekturen. Die gemeinsame echte Betriebsabnahme auf dem zweiten Mac bleibt offen. Die ursprünglichen Befunde und ihre Reproduktionen sind unten als Verlauf festgehalten.

## Abschließende Nachprüfung

| Ursprünglicher Befund | Nachgewiesene Korrektur |
| --- | --- |
| Eingebettetes Manifest kann Fremdbestand beanspruchen | `paketbestand.verify_manifest()` prüft tatsächliche Runtime-Manifestbytes gegen den gespeicherten Hash und den dekodierten Inhalt gegen das eingebettete Manifest. Betrieb und installierter v2-Status verwenden diese Prüfung vor Zielinhaltszugriffen. Die eigene ursprüngliche Manipulation wird ohne Lesen der fremden Zusatzdatei abgewiesen. |
| Fremder Zieltausch wird vernichtet | Altobjekte werden exklusiv in einen zufälligen privaten Aufnahmeordner verschoben und vor dem Lesen anhand ihrer Identität geprüft. Neue Ziele entstehen ausschließlich exklusiv. Fremde Aufnahmen werden zurückgestellt oder bei belegtem Rückgabeziel samt Journalpfad erhalten. Die eigenen Proben bewahren den direkt vor dem Betriebssystemaufruf ausgetauschten Link und eine zwischen Aufnahme und Neuveröffentlichung angelegte Fremddatei. |
| `keep`-Änderungen werden zu spät bemerkt | Der fortgeschriebene erwartete Istbestand umfasst alle ursprünglichen und neuen Ziele einschließlich `keep`. Er wird vor Mutationen, innerhalb des Aufnahmeablaufs und vor dem Abschluss geprüft. Die Regression belegt einen Stopp vor der ersten Dateiänderung, alle anderen Objektidentitäten bleiben gleich. |
| Erstinstaller meldet Abschluss vor v2-Commit | Das v1-Journal wechselt erst nach Veröffentlichung des v2-Bestands auf `installed`. Beide HardStop-Grenzen sind unabhängig geprüft, siehe Teilnachprüfung. |

Bestehende Metadaten werden über atomaren Namenstausch veröffentlicht. Unerwartete Altobjekte bleiben erhalten. Die zusätzliche Regression für einen Fehler erst nach tatsächlicher Veröffentlichung des eigenen `completed`-Journals bestätigt die anschließende Markierung als `interrupted`, soweit die Metadaten noch schreibbar sind. Der Status bleibt eingeschränkt und weitere Operationen werden gesperrt.

Zusätzliche eigene Prozessprobe: Ein isolierter Python-Unterprozess beendet sich mit `os._exit(97)` unmittelbar nach der tatsächlichen Aufnahme eines Skilllinks, bevor eine weitere Checkpoint-Meldung gespeichert wird. Das Journal bleibt korrekt `running` mit dem vorher gespeicherten Aufnahmeort. Das Objekt ist dort auffindbar, der Status lautet `eingeschränkt`, die Folgeoperation ist gesperrt und die privaten synthetischen Marker bleiben erhalten. Damit wurde auch ein Abbruch ohne Python-Fehlernachpflege geprüft.

Final unabhängig ausgeführt: `test_paketbestand.py` (15), `test_paketbetrieb.py` (12), `test_einrichtungsstatus.py` (15), `test_installieren.py` (16), `test_installationsplan.py` (11), `test_paket_bauen.py` (8) und `test_paketregeln.py` (3). **80 Tests erfolgreich in 15,506 Sekunden.** Der gesonderte Gesamtlauf des Hauptagenten mit 145 Tests und Betriebssystem-Sperre ist in [paketbetrieb-testlauf.md](paketbetrieb-testlauf.md) dokumentiert. Dieser Bericht unterscheidet den selbst ausgeführten 80-Test-Lauf ausdrücklich vom gemeldeten vollständigen Lauf.

## Abschließender Dokumentabgleich

Die tatsächlichen Parser verlangen für beide Betriebsbefehle absolute `--config`- und `--home`-Angaben, erlauben die dokumentierten Clientoverrides und verwenden Vorschau als Standard. `--apply` verlangt zusätzlich `ja`. Die konkreten Vorschauaufrufe in `docs/abnahme-zweiter-mac.md` stimmen damit überein. Gespeicherte Clientbindungen, derselbe bestätigte Quellpfad beim Update, v2-Voraussetzung, eigener Test-Home und Codex-Skillbasis sind korrekt erläutert. Die Anleitung behauptet keine bereits bestandenen Modell- oder Mac-Tests. Alle ihre relativen Dokumentlinks sind jetzt auflösbar.

`docs/installationsprobe.md`, `.aios/PLAN.md` und der präzisierte README-Einstieg ordnen die früheren nativen 21-Skill-Ladebelege ausdrücklich dem damaligen Stand vor dem neuen Paketbetrieb zu. Eine hiesige native Wiederholung wird nicht verlangt. `pruefungen/paketbetrieb-testlauf.md` trennt den synthetischen Gesamtlauf samt Betriebssystem-Sperren von fachlicher Modellfunktion und echter Installation auf dem zweiten Mac. Die Abnahmegrenzen sind konsistent.

## Teilnachprüfung der Erstinstallations-Abschlussfolge

20.10.2026: `installieren.install()` veröffentlicht den bestätigten v2-Bestand nun vor dem Wechsel des v1-Journals auf `installed`. Die beiden neuen Regressionen lösen einen `HardStop` außerhalb der normalen Exception-Nachpflege unmittelbar vor beziehungsweise nach diesem Publish aus. Vor dem Commit bleibt der Bestand fehlend, das Journal `installing` und der Status `eingeschränkt`. Nach dem Commit ist der vorhandene v2-Bestand maßgeblich und der Status korrekt `vorhanden`, obwohl das v1-Journal noch `installing` enthält.

Codefolge und Regressionen unabhängig gelesen und `test_installieren.py` vollständig ausgeführt: **16 Tests erfolgreich.** Dieser P2-Befund wurde damit vorab geschlossen. Die übrigen drei Befunde sind inzwischen ebenfalls nachgeprüft, siehe Abschlussergebnis.

**Architekturauswirkung: Mittel.** Die Richtung aus dem Architektur-Zwischenreview ist umgesetzt: explizite Eigentumsrollen, gespeicherte Clientbindungen, getrennte abgeschlossene und laufende Zustandsdaten, Vorschau sowie gezielte Dateioperationen. Die offenen Punkte benötigen eng begrenzte Korrekturen an diesen bestehenden Grenzen, keine neue Servicearchitektur.

## Umfang und Verfahren

Geprüft wurden `paketbestand.py`, `paketbetrieb.py`, die beiden Betriebs-CLI-Wrapper, die Integration in Erstinstaller, Plan, Status und Paketpolicy sowie die beiden neuen Testsuiten und `docs/paketbetrieb.md`. Der lokale Importgraph enthält keine Zyklen. Der vorherige Architekturbericht wurde als Vertragsgrundlage herangezogen.

Schreibende Proben verwendeten ausschließlich die synthetische Fixture aus `tests/test_paketbetrieb.py`: eigenes temporäres Home, eigene Paketquelle, eigenes Profil mit erfundenen Markern und eigene Clientwurzeln. Kein Client, Browser, Netzwerk, Modell oder Git-Aufruf. Keine realen Profile, Geheimnisse, Kundenordner oder aktive Skillverknüpfungen wurden gelesen oder verändert. Produktcode blieb unverändert.

Die Fundstellen beziehen sich auf den stabilen Erstprüfstand vor den anschließend beauftragten Korrekturen.

## P1: Eingebettetes Manifest ist nicht an das tatsächliche Paketmanifest gebunden (behoben)

**Fundstelle:** `scripts/paketbestand.py:177`, besonders `validate()` in Zeilen 185 bis 198. Betroffen sind die Aufrufer in `paketbetrieb.load()` und `einrichtungsstatus.inspect_confirmed()`.

Der Validator leitet erlaubtes Eigentum aus `state["manifest"]` ab. Er prüft dann die daraus erwarteten Einträge und die Gleichheit zweier gespeicherter Hashfelder. Er prüft nicht, ob das eingebettete Manifest dem Inhalt von `runtime/paket.json` entspricht. Der spätere Integritätscheck des realen `paket.json` bestätigt nur dessen gespeicherten Originalhash und schließt diesen Widerspruch nicht.

**Konkrete Reproduktion:**

1. Synthetische v2-Erstinstallation.
2. Fremde Zusatzdatei `runtime/allgemein/skills/alpha/foreign.txt` mit Marker anlegen.
3. Ausschließlich `bestand.json` verändern: passenden relativen Pfad und Hash in `manifest.files` ergänzen und denselben absoluten Pfad mit Rolle `runtime_file` in `owned` ergänzen. Das tatsächliche `runtime/paket.json` und dessen gespeicherter Hash bleiben unverändert.
4. Status und Deinstallationsplan aufrufen, anschließend die synthetische Deinstallation ausführen.

**Tatsächlich:** Status `vorhanden`. Der Deinstallationsplan übernimmt die fremde Datei als Eigentum, entfernt sie und endet mit `operation.status = completed`.

**Erwartet:** Widerspruch zwischen tatsächlichem und eingebettetem Manifest vor dem Zugriff auf ergänzte Eigentumsziele erkennen und ohne Mutation abbrechen.

**Kleinster Fix:** Im installierten Bestand das feste Runtime-Manifest sicher lesen, seinen Hash prüfen und seinen dekodierten Inhalt mit dem eingebetteten Manifest vergleichen, bevor daraus Eigentumsziele akzeptiert und deren Inhalte gelesen werden. Status und Betrieb müssen denselben Vertrag verwenden. Für den späteren deinstallierten Zustand, in dem `paket.json` fehlt, muss die verbleibende Metadatenvalidierung ausdrücklich getrennt behandelt werden. Alternativ wäre eine eindeutig kanonisch reproduzierbare Manifest-Hashbindung möglich. Ein zusätzliches unüberprüftes Hashfeld allein genügt nicht.

Dies ist eine Konsistenzprüfung lokaler Metadaten, keine Signatur oder Zusage kryptografischer Herkunft gegen einen Akteur, der sämtliche lokalen Metadaten verändern kann.

## P1: Fremder Zieltausch zwischen letzter Prüfung und Entfernung oder Ersetzung geht verloren (behoben)

**Fundstellen:** `scripts/paketbetrieb.py:108` (`os.unlink`) und `:121` (`os.replace`), jeweils nach der letzten Identitätsprüfung. Die ähnliche Veröffentlichung vorhandener Metadaten in `paketbestand.publish()` ist bei der Wahl des sicheren gemeinsamen Primitivs mitzudenken.

Die gebundenen Eltern-FDs verhindern Symlinkwechsel in übergeordneten Pfaden. Sie binden jedoch den Namen des zu entfernenden oder zu ersetzenden Objekts nicht an die zuvor geprüfte Inode. Die Profilsperre koordiniert die eigenen Betriebsbefehle und schützt nicht vor einem gewöhnlichen Editor oder anderem Prozess am Zielpfad.

**Reproduktion A:** Bei Deinstallation unmittelbar vor `os.unlink("alpha", dir_fd=...)` den ursprünglichen Skilllink unter dem synthetischen `.agents/skills` entfernen und einen neuen fremden Link auf den synthetischen Ausgabeordner anlegen. Danach das ursprüngliche `unlink` weiterlaufen lassen.

**Tatsächlich:** Der neue fremde Link wird entfernt. Deinstallation endet mit `completed`. Es wird nicht der Inhalt seines Linkziels gelöscht, wohl aber die fremde Einbindung selbst.

**Reproduktion B:** Bei Update unmittelbar vor `os.replace(..., "kern.md", ...)` die bisherige Datei entfernen und eine neue reguläre Datei mit fremdem Marker anlegen. Danach das ursprüngliche `replace` weiterlaufen lassen.

**Tatsächlich:** Die fremde Ersatzdatei wird überschrieben. Update endet mit `completed`. Die Abschlussprüfung erkennt dies nicht, weil danach bereits der erwartete neue Inhalt am Ziel liegt.

**Erwartet:** Der gewöhnliche Austausch am öffentlichen Zielpfad darf keine fremden Inhalte oder Einbindungen vernichten und anschließend als erfolgreich gelten.

**Kleinster tragfähiger Ansatz:** Ein gemeinsames enges Datei-Primitiv verwenden, das das vorgefundene Objekt zunächst exklusiv in einen eigenen zufälligen Arbeitsbereich übernimmt und dort Identität sowie Inhalt prüft. Neue Ziele ausschließlich exklusiv veröffentlichen. Ein unerwartet übernommenes fremdes Objekt erhalten und, soweit der öffentliche Zielpfad frei ist, exklusiv zurückgeben. Bei Konflikt den erhaltenen Ort und Teilzustand melden. Die Operationsdaten müssen den Arbeitsort vor diesem Schritt festhalten. Kein Paketrollback erforderlich.

Eine weitere Prüfung unmittelbar vor `unlink` oder `replace` verkleinert nur das Fenster. Sie beseitigt den belegten Fehler nicht. Die Hauptentscheidung grenzt die Anforderung sinnvoll ein: Schutz gegen normalen Zieltausch, keine unmögliche atomare Vergleichsgarantie gegen beliebige Manipulation in einem privaten zufälligen Arbeitsbereich.

Die Dokumentation benennt bereits ein POSIX-Konkurrenzfenster. Der Befund zeigt dessen konkrete Verlustfolge. Eine solche Einschränkung ersetzt die erforderliche Schutzkorrektur am öffentlichen Zielpfad nicht.

## P2: Änderungen an `keep`-Dateien werden erst nach weiteren Schreibschritten erkannt (behoben)

**Fundstellen:** `scripts/paketbetrieb.py:185`, insbesondere Zeilen 186 bis 188 sowie die erst abschließende Zielprüfung in Zeilen 203 bis 204.

Nach der Gesamterneuerung des Plans unter der Sperre werden `keep`-Schritte nur als `kept` markiert. Vor weiteren Mutationen wird ausschließlich das jeweils veränderte Ziel geprüft. Eine zwischenzeitliche Änderung an einer anderen unveränderten Paketdatei stoppt deshalb die folgenden Schreibschritte nicht.

**Konkrete Reproduktion:** Update mit `add`, `remove`, `replace` und `keep` planen. Unmittelbar vor der ersten `mutate()`-Ausführung eine als `keep` markierte Runtime-Datei auf einen lokalen Marker ändern. Den Ablauf weiterlaufen lassen.

**Tatsächlich:** Elf Dateimutationen werden ausgeführt und im Journal als `done` erfasst. Erst die Schlussprüfung erkennt die geänderte `keep`-Datei und meldet `interrupted`. Der lokale Marker bleibt erhalten, der restliche Paketstand wurde aber trotz bereits bestehendem Konflikt verändert.

**Erwartet:** Vor jeder Mutation den erwarteten aktuellen Gesamtbestand einschließlich unveränderter Dateien prüfen. Bereits erledigte Schritte müssen dabei gegen ihren neuen Zustand, offene und `keep`-Schritte gegen den alten Zustand geprüft werden. Bei Abweichung vor dem nächsten Schreibschritt stoppen.

**Kleinster Fix:** Einen kleinen Prüfer für den laufenden erwarteten Istbestand aus Plan und erledigten Schritten ergänzen und unmittelbar vor jeder Mutation verwenden. Konfigurations- und Zustands-Snapshots in diesen Vertragscheck aufnehmen. Keine erneute vollständige Planung gegen den ursprünglichen Zustand, denn bereits eigene Änderungen sind dann erwartbar. Der endgültige Konsistenzcheck bleibt zusätzlich erhalten.

## P2: Neuer Erstinstaller erklärt den v1-Teil vor dem v2-Bestandscommit für abgeschlossen (behoben)

**Fundstelle:** `scripts/installieren.py:247`, Abschlussfolge in `install()` vor dem anschließenden `bestand.publish()`.

Das bisherige `installation.json` wird bereits auf `installed` gesetzt, bevor der neue bestätigte v2-Bestand veröffentlicht wird. Normale Ausnahmen setzen das Journal zurück auf `failed`. Ein Prozessabbruch zwischen beiden Veröffentlichungen erreicht diese Nachpflege jedoch nicht.

**Konkrete Reproduktion:** In der synthetischen Erstinstallation unmittelbar vor dem ersten `publish(.../bestand.json)` eine eigene `BaseException` auslösen. Damit wird ein Prozessabbruch ohne normale `except Exception`-Nachpflege nachgebildet. Ergebnis: `installation.json` enthält `installed`, `bestand.json` existiert nicht, der Statuscheck fällt auf v1 zurück und meldet `vorhanden`. Der Updateplan scheitert anschließend am fehlenden v2-Bestand.

**Bewertung:** Die Dateihashes sind zu diesem Zeitpunkt tatsächlich vollständig vorhanden. Trotzdem ist der Abschlussvertrag der neuen v2-Erstinstallation nicht erfüllt. Der neue, unvollständige Ablauf wird als abgeschlossener Legacy-Bestand behandelt, ohne die fehlende v2-Betriebsfähigkeit sichtbar zu machen. Das ist unabhängig von der ohnehin ungeprüften Modell- und Fachfunktion.

**Kleinster Fix:** Das v1-Journal bis zum erfolgreich veröffentlichten v2-Bestand auf `installing` belassen. Erst danach `installed` setzen. Bei einem Abbruch vor v2-Publish meldet der v1-Fallback dann eingeschränkte Einrichtung. Nach v2-Publish kann der vorhandene v2-Bestand den tatsächlichen Abschluss korrekt belegen. Kein zusätzliches Schema oder Intentdokument erforderlich. Einen Abbruchtest ohne normale Exception-Nachpflege ergänzen.

## Nachgewiesene Eigenschaften und Crash-Verhalten

| Prüfung | Ergebnis des Erstprüfstands |
| --- | --- |
| Vorschau und abgebrochene Bestätigung | Keine angelegten Operationsdaten und keine Zieländerung. |
| Synthetischer Hauptpfad | Erstinstallation, Update, Status und gezielte Deinstallation erfolgreich. |
| Eigene geänderte Dateien und Links vor Beginn | Konflikt vor Mutation. |
| Fremde belegte neue Ziele | Konflikt, fremder Inhalt bleibt erhalten. |
| Normale unbekannte Runtime-Zusatzdatei | Bleibt bei unverändertem Eigentumsstand erhalten. P1 betrifft die widersprüchliche Manifest-Manipulation. |
| Profil, `.env`, Wissen, Journal und Ausgabe | Marker bytegleich erhalten. Vorhandene Lesewächter prüfen die tatsächlich gelesenen Inodes. |
| Gespeicherte Clientorte | Abweichende bestätigte Orte funktionieren ohne erneute Overrides. Unpassendes Home oder nachträgliche Bindungsabweichung stoppt. |
| Codex-Skillbasis | An bestätigtes Home gebunden. Kein Schluss allein aus `CODEX_HOME`. |
| Mac-Aliase | Doppelte Manifestpfade werden anhand normalisierter, case-insensitiver Komponenten erkannt. |
| Anlagehistorie | Alte `created_directories` ist keine Löschbefugnis. Keine rekursive Runtime- oder Clientlöschung. |
| Kooperative Sperre | Eigene parallele Operation für dasselbe Profil wird blockiert. Sperre liegt im technischen Profilbereich, nicht auf der Systemwurzel. |
| v1-Bestand | Nur lesende Statuskompatibilität. Keine automatische Migration oder Betriebsfreigabe. |
| Installierter Status | Funktioniert aus gebündelter Runtime und anderem Arbeitsverzeichnis. |
| Fehler mitten im Ablauf | Operationsstatus eingeschränkt, Folgeoperation blockiert, alter bestätigter Bestand bleibt verfügbar. |
| Zusätzliche eigene Probe direkt vor Bestandscommit | Alter Bestand bleibt lesbar. Status `eingeschränkt`, Wiederholung gesperrt, private Marker erhalten. |
| Zusätzliche eigene Probe direkt nach Bestandscommit | Neuer Bestand bereits lesbar. Status trotzdem `eingeschränkt`, Wiederholung gesperrt, private Marker erhalten. |
| Fehler beim abschließenden Operationsabschluss | Getrennter Bestand und offene Operation werden berücksichtigt. Kein automatischer Rollback behauptet. |

## Testbelege und Musterkonformität

Unabhängig ausgeführt: `test_paketbestand.py` (8), `test_paketbetrieb.py` (12), `test_einrichtungsstatus.py` (15), `test_installieren.py` (14), `test_installationsplan.py` (11), `test_paket_bauen.py` (8) und `test_paketregeln.py` (3). **71 Tests erfolgreich.** Die vier Befunde stammen aus zusätzlichen eigenen synthetischen Proben und werden durch diese grüne Suite noch nicht abgedeckt.

Die Schichten sind insgesamt angemessen. Die reine Manifest-/Rollenprüfung, sichere Dateioperationen und Ablaufsteuerung haben nachvollziehbare Zuständigkeiten. Funktionsbasierte Module passen zum Umfang. Die Bindung an `einrichten.reject_symlink_components` ist kleine technische Kopplung, derzeit kein Blocker. Ein abstraktes Service- oder Pluginframework wäre für die Korrekturen unnötig.

Langfristig entscheiden die zentrale Manifestbindung und das gemeinsame sichere Mutationsprimitiv über die Verlässlichkeit aller Betriebsbefehle. Beide müssen gemeinsam genutzt werden, damit eine spätere neue CLI nicht erneut ungesicherte Eigentumsableitung oder direkte Pfadüberschreibung einführt.

## Architekturentscheidung zur gezielten Dateiänderung

Für eine spätere dauerhafte ADR-Ablage bietet sich `docs/decisions/` an. Der Stub bleibt hier, damit dieser Review keine weiteren Dateien außerhalb seiner Zuständigkeit erzeugt.

### ADR-0002: Öffentliche Paketziele exklusiv aufnehmen und ersetzen

**Date:** 2026-10-20
**Status:** Accepted
**Context:** Eine Identitätsprüfung vor `unlink` oder `replace` schützt nicht vor einem unmittelbar folgenden gewöhnlichen Zieltausch. Das fremde Ersatzobjekt ging in den nachgewiesenen Fällen verloren.
**Decision:** Altobjekte in einen vorher protokollierten privaten zufälligen Aufnahmeort verschieben und dort prüfen. Am öffentlichen Ziel ausschließlich exklusiv veröffentlichen. Unerwartete Objekte erhalten. Laufenden erwarteten Gesamtbestand vor Mutationen prüfen. Metadaten atomar tauschen und das aufgenommene Altobjekt überprüfen.
**Consequences:** Mehr Metadatenschritte und lokale Integritätsprüfungen. Dafür bleiben unerwartete öffentliche Ersatzobjekte erhalten und Teilzustände nachvollziehbar. Kein automatischer Paketrollback. Keine vollständige Garantie gegen gezielte Manipulation auch der privaten zufälligen Arbeitsnamen.

## Abnahmegrenze

Die unabhängige technische Nachprüfung ist abgeschlossen. Nachgewiesen sind die beschriebenen lokalen Dateiverträge und synthetischen Fehlerfälle. Die echte gemeinsame Betriebsabnahme auf dem zweiten Mac, angemeldete Modellantworten und Dienstfunktion werden dadurch nicht vorweggenommen. Bei Unterbrechungen bleiben die dokumentierten Teilzustände und manuellen Klärungsschritte maßgeblich, keine automatische Wiederholung oder Wiederherstellung.
