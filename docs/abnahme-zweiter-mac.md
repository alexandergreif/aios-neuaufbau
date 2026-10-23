# Gemeinsame Abnahme auf dem zweiten Mac

Stand: 20.10.2026. Diese Reihenfolge ist ein Prüfplan, kein bereits bestandener Test. Installation, Update, Deinstallation und angemeldete Modelltests finden erst gemeinsam auf dem zweiten Mac statt. Das aktive Setup auf dem ersten Mac bleibt unangetastet. Die früheren Loaderproben, [145 bestandenen Dateitests](../pruefungen/paketbetrieb-testlauf.md) und älteren Installationsbelege sind Vorbereitung, keine neue Abnahme.

## 1. Voraussetzungen und Paketquelle klären

1. Auf dem zweiten Mac `python3 --version` und `command -v python3` ablesen. Im Vorbereitungsstand wurde Python 3.13.16 tatsächlich verwendet. Daraus folgt keine belegte Mindestversion oder Kompatibilitätszusage für andere Python-Versionen. Bei abweichender Version zuerst den konkreten Paketlauf prüfen und das Ergebnis dokumentieren.
2. Für jeden gewünschten Client `command -v codex` beziehungsweise `command -v claude` und die jeweilige Versionsausgabe prüfen. Fehlende Clients vor der AIOS-Einrichtung über den gewählten offiziellen Installationsweg einrichten. Den gewählten Anmeldeweg je Client festhalten. Keine Tokens, Schlüssel oder Anmeldedateien in den Chat oder das Abnahmeprotokoll kopieren.
3. Den Quellstand aus dem privaten Repository `alexandergreif/aios-neuaufbau` frisch klonen. Die [Kurzanleitung](installation-kurz.md) enthält den Clone-Befehl und den ersten Claude-Test. Im Checkout mit `git rev-parse HEAD` die tatsächlich verwendete Commit-ID festhalten. Keine alte Installation als Paketquelle ausgeben.

Vor dem Schreiben festlegen: gewählte Clients, Quellordner, privater Profilordner, Runtime-Ordner, persönlicher Ausgabeordner, Projektwurzeln sowie gegebenenfalls abweichende Clientordner (`CODEX_HOME` und `CLAUDE_CONFIG_DIR`). Bestehende Pfade, eigene Skilldateien und Konfigurationen zuerst sichten. Bei Überschneidungen oder unklarer Eigentümerschaft stoppen. Testpfade für Update und Deinstallation bleiben von der normalen Einrichtung getrennt.

## 2. Profil und Erstinstallation

Einen optionalen, bereits geschützten Profilexport nach [Profiltransfer](profiltransfer.md) zunächst nur privat auf dem zweiten Mac bereitlegen. Vor der Weitergabe den Exportinhalt prüfen. Er enthält nur ausgewählte Profilfelder und Vorlieben, keine `.env`, Zugangsdaten, `pfade.json` oder Projektzuordnungen. Noch keinen Import in den späteren Profilordner ausführen: Der geführte Einstieg verlangt dort ein neues, nicht vorhandenes Ziel.

Im neuen Quellordner `sh install.sh --language de` starten. Der Dialog ist ab 0.2.0-dev englisch. Ohne `--language` fragt er die Sprache ab, Vorgabe `en`. Nur wenn ausdrücklich andere Benutzer- oder Clientordner gewählt wurden, die dokumentierten Optionen `--home`, `--codex-home` und `--claude-config-dir` übergeben. Im Dialog die Clientauswahl `claude`, `codex` oder `both` treffen. Danach fragt der Dialog Pfade und Profilangaben ab und zeigt anschließend die Vorschau von Pfadkonfiguration und Profilangaben. Die erste Eingabe `yes` legt das private Profil an. Der optionale Blockbrain-Schlüssel wird verdeckt eingegeben oder übersprungen. `.env` bleibt lokal und wird nicht im Chat gezeigt. Die zweite Vorschau nennt die geplanten Installationseinbindungen. Erst das zweite `yes` installiert. Bei Konflikten, unerwarteten Zielen oder fehlendem Zugang abbrechen und den Befund festhalten. Ein Abbruch nach der Profilanlage erhält das Profil und zeigt einen Fortsetzungsaufruf.

Anschließend den rein lesenden Status mit dem bestätigten Konfigurationspfad prüfen:

```sh
python3 scripts/setup_status.py --config /absoluter/pfad/zum/profil/pfade.json --home /absoluter/pfad/zum/home
```

Falls bei der Einrichtung eigene Clientordner gewählt wurden, dieselben `--codex-home` und `--claude-config-dir` hier ergänzen. `present` und Exitcode 0 belegen nur Dateien, Hashes, Regeldateien und Skillverknüpfungen. Die gewählten Clients danach nativ starten und prüfen, ob Regelkern und AIOS-Skills geladen werden. Eine Modellantwort oder Dienstverbindung ist durch den Statuscheck noch nicht belegt.

Erst nach erfolgreicher geführter Installation den optionalen Profilexport mit Vorschau und ausdrücklicher Bestätigung in den nun vorhandenen Profilordner importieren. Der Import sichert und ersetzt nur `profil.md`. Die auf diesem Mac bestätigte `pfade.json` bleibt erhalten. Projektwurzeln und weitere lokale Pfade hier neu bestätigen, nicht aus dem Export übernehmen.

## 3. Modellverhalten nach Anmeldung

Erst auf dem zweiten Mac über den nativen Clientweg anmelden. Die lokal geprüften Hilfeaufrufe und die [Anmeldehinweise](modelltests-zweiter-mac.md) nennen `codex login` und `claude auth login`. Konto und Verfahren vor Ort wählen. Erfolg und Clientversion dokumentieren, ohne Anmeldespeicher oder Geheimnisse zu öffnen.

Danach die sechs erfundenen Fälle aus [tests/verhalten/faelle.json](../tests/verhalten/faelle.json) in jedem gewählten Client mit dem dort genannten Skill ausführen. Für jeden Fall Prompt, tatsächliche Antwort, eventuelle Werkzeugaufrufe, Modell, Denkaufwand, Clientversion und Paketstand festhalten. Die Erwartungen in der JSON-Datei einzeln bewerten. Besonders prüfen, ob bei fehlender Kalenderquelle oder mehrdeutigem Termin gefragt wird, ob Zuständigkeiten offenbleiben und ob keine unerwünschten Schreibaktionen erfolgen. Ein unabhängiger Prüfer bewertet die Ergebnisse. Ohne Anmeldung oder Modellantwort bleibt diese Zeile offen, selbst wenn der native Loader die Skills erkennt.

## 4. Update und Deinstallation in eigenen Testorten

Für die Betriebsprüfung zuerst einen **eigenen, vorhandenen synthetischen Benutzerordner** als `--home` wählen. Darunter vier voneinander getrennte Bereiche für Profil, Runtime, Ausgabe und Clientkonfiguration festlegen. Auch die beiden Clientordner müssen allein zu diesem Testaufbau gehören. Beispiel für die Pfadwahl: `/absoluter/testhome/profil`, `/absoluter/testhome/runtime`, `/absoluter/testhome/ausgabe`, `/absoluter/testhome/.codex` und `/absoluter/testhome/.claude`. Die Platzhalter sind vor Ort durch geprüfte absolute Testpfade zu ersetzen. Der Quellordner bleibt das ausgewählte lokale Paket.

Zuerst in diesen Testorten die geführte Erstinstallation durchführen. Ein Aufruf mit den ausdrücklich gewählten Orten lautet `sh install.sh --home /absoluter/testhome --codex-home /absoluter/testhome/.codex --claude-config-dir /absoluter/testhome/.claude`. Im Dialog Profil, Runtime und Ausgabe ausschließlich unter `/absoluter/testhome` wählen. Danach den rein lesenden Status mit derselben `--home`- und Clientordner-Auswahl prüfen. Ohne erfolgreiche Test-Erstinstallation kein Update oder Deinstallationslauf. Für diese reinen Dateiproben sind weder zusätzliche Anmeldung noch ein nativer Clientaufruf nötig.

`--codex-home` allein isoliert die Codex-Skills nicht: Deren globale Verknüpfungen liegen unter `--home/.agents/skills`. Als Fremdbestand vor dem Update einen eigenen Marker unter `/absoluter/testhome/.agents/skills/<eigener-testname>/SKILL.md` und bei Claude unter `/absoluter/testhome/.claude/skills/<eigener-testname>/SKILL.md` anlegen. Den Inhalt oder Hash dieser Dateien festhalten. Auch im Testprofil und Testausgabeordner Markerdateien anlegen. Keine Update- oder Deinstallationsprobe am normalen Profil, dessen `~/.agents/skills` oder dessen Clientordnern durchführen. Die Vorschau muss eigene Änderungen benennen und Konflikte melden. Ein ungeklärter Konflikt stoppt die Ausführung.

Die [Betriebsdokumentation](paketbetrieb.md) und der lokale CLI-Parser nennen für Update und Deinstallation zwingend `--config` und `--home` als absolute Pfade. Diese Platzhalter zeigen nur die Form der **reinen Vorschau** und sind vor Ort durch die bestätigten Testpfade zu ersetzen:

```sh
python3 scripts/update.py --config /absoluter/testhome/profil/pfade.json --home /absoluter/testhome
python3 scripts/uninstall.py --config /absoluter/testhome/profil/pfade.json --home /absoluter/testhome
```

Die bei der Test-Erstinstallation bestätigten Clientbindungen sind gespeichert. Spätere Aufrufe brauchen `--codex-home` und `--claude-config-dir` nicht erneut. Werden sie angegeben, müssen sie exakt den bestätigten Testorten entsprechen, sonst stoppt der Lauf als Konflikt. Die Vorschau nennt alte und neue Version, Manifest-SHA256 und jedes Ziel als `add`, `replace`, `remove` oder `keep`. Erst `--apply` und die zusätzliche Eingabe `yes` führen die geplanten Änderungen aus. Auch dann vor der Eingabe den Vorschauplan auf unerwartete Ziele prüfen.

Für den Updatefall eine tatsächlich neuere lokale Paketversion am **selben bestätigten Test-Quellpfad** bereitstellen, der in `pfade.json` als `paths.source` steht. Ein anderer Quellpfad ist keine unterstützte Migration. Update und Deinstallation benötigen den nach erfolgreicher Test-Erstinstallation veröffentlichten bestätigten Bestand `profil/zustand/bestand.json` mit Schema 2. Alte Installationen ohne diesen Bestand sind nur lesbar, nicht automatisch migrierbar. Nach Update den Dateistatus erneut prüfen, nach Deinstallation den Status `uninstalled` und die einzeln entfernten AIOS-Einbindungen belegen. Die Runtimewurzel und fremde Zusatzdateien dürfen bleiben. Profil, `.env`, Ausgabe und fremde Skilldateien müssen samt Markern erhalten sein.

Eine offene oder unlesbare `operation.json` beziehungsweise ein Teilfehler führt zum Status `limited` und sperrt weitere Paketoperationen. Dann nicht blind wiederholen. Zustand und Belege sichern, Ursache klären und den Wiederherstellungsweg gesondert entscheiden. Für Update außerdem den Paketstand und die Statusausgabe vor und nach dem Lauf festhalten.

## Abnahmeprotokoll

Pro Zeile Datum, Mac, Paketstand, tatsächlich verwendete Pfade und Belegort ergänzen. Keine Geheimnisse oder privaten Inhalte in Belege kopieren. Bei einem Fehler den Schritt stoppen, Zustand sichern und Ursache klären. Ein fehlender Beleg zählt als offen.

| Prüfung | Erwartung | Beleg | Fehlerfall | Status |
| --- | --- | --- | --- | --- |
| Voraussetzungen und Quelle | Python- und Clientversionen erfasst, vollständige lokale Paketquelle identifiziert | Versionsausgaben, Paketstand und Herkunft | Client fehlt, Quellstand unklar, Version ungeprüft | Claude bestanden 21.10.2026: Python 3.13.5, Claude Code 2.1.306, `a206ec5`, 145 Tests grün ([Beleg](../pruefungen/modelltests-mac2/README.md)). Codex bestanden 22.10.2026: Codex CLI 0.163.0 ([Codex-Beleg](../pruefungen/modelltests-mac2/codex/README.md)) |
| Profil und Installation | Gewählte Pfade bestätigt, zwei Vorschauen und Installationsausgang dokumentiert | Bereinigtes Dialogprotokoll, `pfade.json`-Pfad, Installationsstatus ohne Geheimnisse | Konflikt oder Abbruch mit erhaltenem Profil | Claude bestanden mit Hinweisen 21.10.2026, Dialog nicht interaktiv eingespeist ([Beleg](../pruefungen/betrieb-mac2/README.md)). Codex bestanden 22.10.2026, ebenfalls nicht interaktiv ([Codex-Beleg](../pruefungen/modelltests-mac2/codex/README.md)). Interaktive Gegenprobe offen |
| Dateistatus und native Ladung | Status je gewähltem Client `present` (bis 0.1.7-dev `vorhanden`), Regelkern und Skills nativ sichtbar | Statusausgabe, Clientprotokoll oder Screenshot | Fehlende Links oder Client lädt Quellen nicht | Claude bestanden 21.10.2026: Status `vorhanden`, 21 Skills nativ geladen ([Beleg](../pruefungen/modelltests-mac2/README.md)). Codex bestanden 22.10.2026: Status `vorhanden`, Regelkern und Skills nativ geladen ([Codex-Beleg](../pruefungen/modelltests-mac2/codex/README.md)) |
| Sechs Modellfälle | Erwartungen je Fall und Client unabhängig bewertet | Bereinigte Antworten und Bewertungsbogen mit Modellstand | Rückfrage fehlt, erfundene Angabe, unerwünschte Aktion | Claude bestanden mit Hinweisen 21.10.2026, Platzhalterbefund behoben, Zwischenmeldung bei Nachprüfung offen ([Beleg](../pruefungen/modelltests-mac2/README.md)). Codex bestanden mit Hinweisen 22.10.2026, Prüfauftrag nur verschlüsselt protokolliert ([Codex-Beleg](../pruefungen/modelltests-mac2/codex/README.md)) |
| Update im Testaufbau | Nur AIOS-Eigentum aktualisiert, fremder Marker, Profil und Ausgabe erhalten | Vorher-/Nachherstatus, Hashes oder Inhalte der Marker | Geänderte fremde Datei, Konflikt oder Teilfehler | Claude bestanden mit Hinweisen 21.10.2026: 0.1.0-dev nach 0.1.1-dev, 5 Ersetzungen, Marker bytegleich, Konfliktfall geprüft ([Beleg](../pruefungen/betrieb-mac2/README.md)). Codex bestanden mit Hinweisen 22.10.2026: 0.1.4-dev nach 0.1.5-dev, 5 Ersetzungen inkl. `AGENTS.md`, Marker bytegleich ([Codex-Beleg](../pruefungen/betrieb-mac2/codex/README.md)) |
| Deinstallation im Testaufbau | Nur erfasste AIOS-Einbindungen entfernt, fremder Marker, Profil und Ausgabe erhalten | Vorher-/Nachherstatus und Markerbelege | Fremdbestand gelöscht, unklarer Restzustand | Claude bestanden mit Hinweisen 21.10.2026: 95 eigene Einbindungen entfernt, Fremdbestand, Profil und Ausgabe bytegleich ([Beleg](../pruefungen/betrieb-mac2/README.md)). Codex bestanden mit Hinweisen 22.10.2026: 95 eigene Einbindungen entfernt, Konfliktfall mit umgebogenem Link geprüft, Fremdbestand erhalten ([Codex-Beleg](../pruefungen/betrieb-mac2/codex/README.md)) |

## Restarbeiten nach dieser Abnahme

Die bisher noch fehlenden ausgewählten Fähigkeiten bleiben eigene Umsetzungs- und Prüfpunkte. Dienstkonnektoren brauchen je Client einen freigegebenen Zugang und einen echten Verbindungs- und Fehlerfalltest. Die Renderer benötigen zusätzlich eine visuelle Prüfung ihrer Ausgabe. Keiner dieser Punkte wird durch die sechs synthetischen Modellfälle oder einen grünen Dateistatus automatisch abgeschlossen.
