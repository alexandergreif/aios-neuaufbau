# Unabhängiger Review des geführten Einstiegs

Stand: 20.10.2026, einschließlich unabhängiger Nachprüfung. Ergebnis: Freigabe für den geprüften lokalen Einrichtungsablauf. S1 ist behoben und eigenständig nachgeprüft. Keine offenen Befunde in diesem Prüfungsumfang. Keine Abnahme der Client- oder Dienstfunktion.

## Behobener Befund

### S1: Ctrl+C bei der zweiten Bestätigung verlor den Fortsetzungsaufruf

**Einstufung:** bug. **Stelle:** `scripts/setup.py:58`, ausgelöst durch `scripts/installieren.py:290`.

Der neue Einstieg fängt `KeyboardInterrupt` nur während der Profileinrichtung ab. Beim zweiten Dialog läuft das Signal aus `installieren.main()` ungefangen heraus. Damit erreicht der Einstieg seine Resume-Ausgabe nicht. Das widerspricht dem dokumentierten Abbruchverhalten in `docs/setup.md:5` und `docs/erstinstallation.md:10`.

**Reproduktion:** `sh install.sh --home <isolierter absoluter Benutzerordner> --codex-home <isolierter Clientordner> --claude-config-dir <isolierter Clientordner>` starten. Beide Clients wählen, gültige Standardpfade und leere optionale Profilangaben verwenden, die erste Vorschau mit `ja` bestätigen und die Schlüsselabfrage mit `nein` überspringen. Bei `Ersteinrichtung ausführen? Genau 'ja' eingeben:` Ctrl+C drücken. In der unabhängigen CLI-Probe wurde nach Erkennung genau dieses Prompts SIGINT an den Prozess geschickt.

**Beleg:** Prozessrückgabe in Python `-2`, `KeyboardInterrupt` mit Traceback auf stderr. `aios-profile/pfade.json` existiert, die Runtime existiert nicht. Die Ausgabe enthält keinen Text `Installation fortsetzen` und keinen Resume-Befehl. Der normale Abbruch durch `nein` funktioniert dagegen einschließlich des anschließend tatsächlich ausgeführten Resume-Befehls.

**Kleinster Fix:** Nur direkt an der zweiten Eingabe in `installieren.py` zusätzlich zu `EOFError` auch `KeyboardInterrupt` als abgebrochene Bestätigung behandeln. Dann erfolgt keine Installation und der vorhandene Resume-Zweig in `setup.py` wird erreicht. Nicht pauschal einen Interrupt während einer bereits laufenden Installation als sauberen Abbruch behandeln. Einen CLI-Test ergänzen, der SIGINT am zweiten Prompt sendet und Profilbestand, fehlende Runtime, fehlenden Traceback sowie einen ausführbaren Resume-Aufruf mit allen Clientorten prüft.

**Nachprüfung:** Der Fix in `scripts/installieren.py:291` fängt jetzt ausschließlich am Bestätigungsprompt `(EOFError, KeyboardInterrupt)` ab. Die Schreibphase bleibt außerhalb dieses Handlers. Der neue Regressionstest `tests/test_setup.py:82` löst `KeyboardInterrupt` gezielt über die Eingabefunktion aus und prüft Profilbestand, unveränderte Installationsziele und den vollständigen Resume-Aufruf.

Zusätzlich wurde die ursprüngliche unabhängige CLI-Probe mit echtem SIGINT wiederholt. Ergebnis: Rückgabe 0, kein Traceback, bestätigtes Profil vorhanden, keine Runtime, Clientordner oder Zustandsdatei angelegt. Der ausgegebene Resume-Befehl enthielt Home und beide individuellen Clientorte einschließlich Leerzeichen korrekt zitiert. Anschließend wurde genau dieser Befehl aus einem anderen Arbeitsverzeichnis tatsächlich ausgeführt. Ergebnis: Rückgabe 0, Eigentumsstatus `installed`, beide Regeldateien an den individuellen Clientorten vorhanden. S1 ist geschlossen.

## Prüfbelege

Alle folgenden Prüfungen liefen ohne Browser, Netzverbindung, Clientstart, Anmeldung oder Modellaufruf. Die Ziele lagen in temporären synthetischen Ordnern. Echte Profile, Kundendaten, Zugangsdaten und aktive Clientkonfigurationen wurden nicht als Testdaten verwendet. Keine Produktdatei wurde im Review geändert.

Vorhandene Tests:

| Aufruf | Ergebnis |
| --- | --- |
| `python3 -B -m unittest discover -s tests -p 'test_setup.py' -v` | Nach Fix 7 bestanden |
| `python3 -B -m unittest discover -s tests -p 'test_einrichten.py' -v` | 8 bestanden |
| `python3 -B -m unittest discover -s tests -p 'test_installieren.py' -v` | 14 bestanden, nach Fix erneut mit `-q` bestanden |

Zusätzliche unabhängige CLI-Proben über `/bin/sh <Paket>/install.sh` aus einem anderen Arbeitsverzeichnis:

| Fall | Beobachtung |
| --- | --- |
| Erfolgreicher Ablauf, Leerzeichen in Home und beiden Clientorten | Beide Vorschauen durchlaufen, Eigentumsstatus `installed`, Statuscheck `Dateieinbindung: vorhanden` |
| Abbruch erster Vorschau mit `nein` | Rückgabe 0, synthetischer Benutzerordner vollständig leer |
| Abbruch zweiter Vorschau mit `nein` und echte Ausführung des ausgegebenen Befehls | Profil bleibt, vor Resume keine Runtime, nach Resume beide Regeldateien an den ausdrücklich angegebenen Clientorten vorhanden |
| Relatives `--config` mit Leerzeichen im Pfad | Rückgabe 0, Vorschau ohne Runtime-Anlage |
| Relatives Clientziel | Rückgabe 1 mit Hinweis auf erforderlichen absoluten Pfad, keine Runtime, bestätigtes Profil bleibt |
| Fremde `CODEX_HOME` und `CLAUDE_CONFIG_DIR`, keine expliziten Clientargumente | Klärungsfehler vor Installation, keine Runtime und keine fremden Zielordner angelegt |
| Fremde Clientumgebung mit expliziten isolierten Clientargumenten | Erfolgreiche Installation ausschließlich an den expliziten Zielen |
| Nur Codex gewählt | Codex-Regeldatei vorhanden, kein Claude-Clientordner angelegt |
| SIGINT bei zweiter Bestätigung | Zunächst S1 reproduziert, nach Fix sauberer Abbruch mit vollständigem Resume-Aufruf |
| Tatsächliche Fortsetzung nach SIGINT | Nach Fix beide individuellen Clientorte korrekt eingerichtet, Eigentumsstatus `installed` |

Der vorhandene Setup-Test mit reduziertem `PATH` belegt außerdem die Hinweise zu fehlenden `claude`- und `codex`-Programmen. Der Profiltest zum Schlüssel verwendet einen synthetischen Wert und prüft dessen Abwesenheit in stdout und stderr. Der neue Einstieg übergibt ausschließlich Konfigurationspfad, Home und Clientorte als Installerargumente. Den Schlüssel liest oder übergibt er nicht.

## Umfang und Grenzen

Vollständig gelesen wurden `scripts/setup.py`, `scripts/einrichten.py`, `install.sh`, `tests/test_setup.py`, `docs/setup.md` und `docs/erstinstallation.md`. Für den Kontrollfluss zusätzlich gelesen: `scripts/installieren.py`, `scripts/einrichtungsstatus.py`, `scripts/installationsplan.py`, `scripts/pruefe_konfiguration.py` und `tests/test_einrichten.py`. Projektkontext aus `.aios/PLAN.md` und `.aios/NOTIZEN.md` berücksichtigt. `tasks/todo.md`, `tasks/lessons.md` und ein lokales `AGENTS.md` sind im Prüfprojekt nicht vorhanden. Es handelt sich um einen Vorbereitungsordner ohne Git-Repository, deshalb liegt kein versionsbezogener Diff zugrunde.

Es wurden keine neuen numerischen Ressourcen-, Pool- oder Timeoutkonfigurationen in diesem Änderungsumfang festgestellt. Ein Lasttest ist für den hier geprüften lokalen Dialog nicht erfolgt. Der Statuscheck bestätigt Dateien, Hashes und Links und benennt Fachfunktion, Modelle und Dienste ausdrücklich als ungeprüft. Die Prüfung ist keine Abnahme der Client- oder Dienstfunktion und keine Prüfung der parallel bearbeiteten Renderer.

Geprüfter SHA256-Stand von `scripts/setup.py`: `b9cf3c6d9a115d8c033f11b023459909786249141d741fc8a275970ff485a189`.

Nachgeprüfter SHA256-Stand von `scripts/installieren.py`: `84de081abd60e31bd5e797d67a879c6a7994fecd0dc33cbe0b59e2738671d98b`.

Nachgeprüfter SHA256-Stand von `tests/test_setup.py`: `38c328a5362dcc96c83892aeaaac51b5421f4ef7ed4115957b665c3536225c7e`.
