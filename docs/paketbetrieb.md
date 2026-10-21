# Begrenzter Paketbetrieb

Stand: 20.10.2026. Implementierung im Neuaufbau, ausschließlich mit synthetischen Quellen, Profilen und Zielordnern geprüft. Echte Installation, Deinstallation, Update und angemeldete Modelltests auf dem zweiten Mac bleiben offen.

## Aufrufe

Aus dem bestätigten Quellpaket starten. Beide Pfade müssen absolut sein. Die Beispiele verwenden absichtlich keine aktiven persönlichen Pfade.

```sh
python3 scripts/aktualisieren.py --config /synthetisch/profil/pfade.json --home /synthetisch/home
python3 scripts/deinstallieren.py --config /synthetisch/profil/pfade.json --home /synthetisch/home
```

Standard ist eine reine Vorschau. Sie nennt Ausgangs- und Zielversion, Manifest-SHA256 und jedes konkrete Ziel als `add`, `replace`, `remove` oder `keep`. `--apply` führt nach einer zusätzlichen Eingabe von genau `ja` aus. Eine Vorschau oder abgebrochene Bestätigung legt keine Dateien an.

Die optionalen Argumente `--codex-home` und `--claude-config-dir` funktionieren wie beim Erstinstaller. Bestätigte Clientwurzeln werden gespeichert, deshalb müssen sie beim nächsten Aufruf nicht wiederholt werden. Ein abweichender späterer Wert ist ein Konflikt. Die Codex-Skillbasis bleibt `<bestätigtes Home>/.agents/skills`, unabhängig von der Codex-Konfigurationswurzel. Umgebungsvariablen ändern gespeicherte Bindungen nicht.

Update benötigt den laufenden Quellpaketpfad aus `paths.source`. Client- oder Bereichsmigration und Wiederinstallation nach Deinstallation sind kein Bestandteil dieses Betriebswegs.

## Eigentum und Grenzen

`profil/zustand/bestand.json` mit Schema 2 enthält den zuletzt bestätigten Zustand. Home, vier Bereiche, Clientauswahl und Clientbindungen müssen zur bestätigten Konfiguration passen. Die Konfigurationsdatei muss exakt `pfade.json` im bestätigten Profil sein. Manifestpfade werden vor jedem Inhaltszugriff gegen die Paketpolicy geprüft, einschließlich Mac-Pfadaliasen. Jede Eigentumsrolle und jedes Ziel werden aus diesen Grenzen erneut abgeleitet. Vor dem Lesen eigener Zieldateien muss das eingebettete Manifest inhaltlich zum tatsächlich installierten `runtime/paket.json` passen. Dessen Bytes müssen zusätzlich den bestätigten Manifesthash erfüllen. Eine konsistente Ergänzung allein in `bestand.json` kann dadurch keine fremden Runtime-Dateien zu Eigentum erklären.

Die drei Rollen sind `runtime_file`, `client_rule` und `client_link`. Einträge dürfen keine fremden Zielpfade ergänzen. `created_directories` aus dem alten Erstinstallationsjournal ist ausschließlich eine Anlagehistorie. Update und Deinstallation benutzen sie nicht.

Erstinstallation veröffentlicht den neuen Bestand exklusiv und erst nach Integritätsprüfung. Das bisherige `installation.json` bleibt als Erstinstallationsjournal erhalten. Bestehende v1-Installationen ohne bestätigten Bestand können weiterhin rein lesend geprüft werden. Update und Deinstallation verweigern sie vor Mutation. Es gibt keine automatische Migration.

Fehlende oder veränderte eigene Dateien, geänderte Linkziele sowie unbekannte belegte neue Ziele sind Konflikte. Vor Ausführung wird nach der Bestätigung der gesamte Plan erneut berechnet. Quellen, Konfiguration, Bestand und Zielidentitäten müssen unverändert sein. Vor jedem Dateischritt werden Typ, Hash oder Linkziel, Identität und gebundener Elternordner erneut geprüft. Zusätzlich wird vor jeder Mutation der gesamte laufende Istbestand einschließlich `keep`-Dateien geprüft. Erfolgreiche Schritte schreiben diesen erwarteten Istbestand fort. Das Runtime-Manifest wird zuletzt verändert.

Profilinhalte, `.env`, Wissen, Journale, Ergebnisse, Quellcode und fremde Clientkonfigurationen sind keine Löschziele. Der Ablauf liest keine privaten Inhalte außer der ausdrücklich benötigten Pfadkonfiguration und eigenen technischen Zustandsdaten. Betroffene eigene globale Regeldateien werden vor einer Ersetzung unter `zustand/sicherungen/<Operationskennung>/` mit privaten Dateirechten gesichert. Operationsdaten enthalten Pfade, Hashes und Zustände, keine Regel- oder Profilinhalte.

Deinstallation entfernt einzeln die validierten unveränderten eigenen Dateien und Links. Dafür wird das Ziel zunächst exklusiv in einen zufällig benannten privaten Aufnahmeordner innerhalb seines gebundenen Elternordners verschoben. Erst nach Identitätsprüfung darf das dort aufgenommene eigene Objekt entfernt werden. Ersatzdateien und Links werden am ursprünglichen Ziel ausschließlich neu und exklusiv angelegt. Ein dort inzwischen erschienenes Fremdobjekt wird nicht überschrieben. Eine unerwartet aufgenommene fremde Datei oder Verknüpfung wird ohne Inhaltslesen erkannt und nach Möglichkeit exklusiv zurückgestellt. Ist das Ziel bereits wieder belegt, bleibt sie in der Aufnahme erhalten. Das Operationsjournal nennt Aufnahmeort, Identität und Zustand, der Ablauf stoppt als unterbrochen. Aus diesen Runtime-Dateipfaden abgeleitete Unterordner werden ausschließlich entfernt, wenn sie leer sind. Die Runtimewurzel, Clientordner und sämtliche privaten Bereiche bleiben erhalten. Fremde Runtime-Zusatzdateien bleiben stehen. Es gibt keine rekursive Löschung eines installierten Baums.

## Unterbrechung und Abschluss

Erstinstaller, Update und Deinstallation verwenden dieselbe kooperative Sperre `profil/zustand/betrieb.lock`. Nach Sperrerwerb werden die Voraussetzungen erneut geprüft. Verschiedene Profile erhalten verschiedene Sperren. Konkurrierende Erstinstallationen auf gemeinsamen Zielen werden zusätzlich durch exklusive Anlage und erneute Zielprüfung begrenzt.

Für Update und Deinstallation hält `operation.json` eine UUID, Ausgangs- und Zielmanifesthash, konkrete geplante Schritte sowie deren Status fest. Die Absicht wird vor dem Dateischritt gespeichert. Eine offene, unlesbare oder fehlgeschlagene Operation verhindert Folgeoperationen. Sie wird weder automatisch wiederholt noch zurückgerollt. Der alte bestätigte Bestand bleibt bis zur erfolgreichen Veröffentlichung lesbar.

Nach den Dateischritten werden alle neuen Ziele oder deren gezieltes Fehlen geprüft. Erst danach wird ein vorbereiteter neuer Bestand atomar veröffentlicht. Bestehende Metadaten werden durch atomaren Namenstausch veröffentlicht, anschließend wird das aufgenommene Altobjekt geprüft. Nur das erwartete eigene Altobjekt wird entfernt. Ein unerwartetes Metadatenobjekt bleibt unter dem in der Fehlermeldung genannten `.aios-bestand-*`-Pfad im Zustandsordner erhalten. Ein Crash zwischen Namenstausch und Prüfung kann dort ein Restobjekt hinterlassen, die offene Operation verhindert eine blinde Fortsetzung. Deinstallation veröffentlicht `status: uninstalled`, erhält aber die Eigentumsmetadaten. Scheitert die abschließende Operationsmeldung nach erfolgreicher Bestandsveröffentlichung, bleibt der Status eingeschränkt und die Wiederholung gesperrt. Das gilt auch für einen gemeldeten Fehler erst nach Veröffentlichung des eigenen `completed`-Journals. Dieser exakt bekannte UUID-Stand wird im Fehlerpfad als `interrupted` markiert, soweit Metadaten noch schreibbar sind.

Dateien und Metadaten werden synchronisiert. Dies ist keine atomare Systemtransaktion und kein allgemeiner Schutz gegen beliebige gleichzeitig schreibende fremde Prozesse. Die Sperre koordiniert diese Betriebsbefehle für dasselbe Profil. Gewöhnliche Ersetzungen am ursprünglichen Ziel zwischen letzter Prüfung und Aufnahme führen zur Erhaltung des unerwarteten Objekts und zu einem Fehler. Keine vollständige Garantie besteht gegen fremde Prozesse, die gezielt auch die zufälligen privaten Aufnahme- oder Metadatennamen manipulieren. Bei einem harten Prozessende oder nicht mehr schreibbarem Dateisystem können letzte Statusmeldungen ausbleiben. Aufnahmeabsicht und Operationskennung werden vor den Dateischritten gespeichert, es gibt keine automatische Gesamtwiederherstellung.

Der Statuscheck meldet eine offene Operation als `eingeschränkt`, den bestätigten deinstallierten Zustand als `deinstalliert` und eine vollständige Dateieinbindung als `vorhanden`. Fachfunktion, Modelle und Dienste bleiben davon getrennt und ungeprüft. `paketbestand.py` ist dafür Teil des Runtimepakets. Der installierte Statuscheck funktioniert ohne Quellimporte aus einem anderen Arbeitsverzeichnis.

## Synthetischer Nachweis

27 neue Tests in `test_paketbetrieb.py` und `test_paketbestand.py` prüfen:

- Installation, Update mit neuen, geänderten und entfernten Dateien, Status und Deinstallation, einschließlich gespeicherter abweichender Clientorte.
- Bytegleichen Erhalt privater Marker sowie Lesewächter auf Profil-, `.env`-, Wissens-, Journal- und Ausgabedateien.
- Eigene lokale Änderungen, fehlende Dateien, geänderte Links, fremde neue Ziele und unveränderte fremde Runtime-Zusatzdateien.
- Manipulierte Eigentumspfade, Rollen, Manifestpfade, Mac-Aliase und Clientbindungen vor privaten Inhaltszugriffen.
- Zieländerungen nach Vorschau und unmittelbar vor Mutation, Konfigurations-/Bestands-/Quellkonflikte, gegenseitige Sperre und Folgeaufrufe.
- Manipulierte Manifestergänzung ohne Fremdlesen, `keep`-Änderung vor dem ersten Dateischritt, Fremdlinks und Fremddateien direkt bei Aufnahme, belegtes Wiederherstellungsziel und Fremdmetadaten beim atomaren Tausch.
- Unterbrechung mitten in der Operation, gescheiterte Bestandsveröffentlichung und Fehler bei der letzten Operationsmeldung.
- v1 als rein lesbarer Altbestand und installierter v2-Status aus anderem Arbeitsverzeichnis.

Zusätzlich erfolgreich geprüft: bestehende Statusmatrix für v1 (15), Erstinstallation (16), Installationsplan (11), Paketbau (8) und Paketpolicy (3). Insgesamt 80 gezielte Tests erfolgreich, auch unabhängig wiederholt. Die v1-Statusmatrix entfernt im Test ausdrücklich den neuen Bestand, damit die zugesagte Lesekompatibilität weiterhin geprüft wird. Die erste unabhängige Prüfung fand vier Sicherheits- und Abschlusslücken. Deren Korrekturen sind umgesetzt und unabhängig geschlossen. Zusätzliche harte Abbruch- und Zielwechselproben bestanden. [Unabhängiger Review](../pruefungen/paketbetrieb-review.md), [145 Tests im Gesamtlauf](../pruefungen/paketbetrieb-testlauf.md). Die gemeinsame reale Abnahme auf dem zweiten Mac steht aus.
