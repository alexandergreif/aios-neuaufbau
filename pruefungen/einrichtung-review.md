# Unabhängige Prüfung: Einrichtung, Profiltransfer und Register

Stand: 19.10.2026. Abschließende Nachprüfung. Alle belegten Funktionsfehler aus dieser Prüfung sind behoben. 50 Tests bestanden. Native Regelladung beider konkret benannter Clients mit Negativkontrolle nachgewiesen. Keine Modell-Verhaltensprüfung oder Dienstabnahme.

## Abschließendes Ergebnis

Die nachstehend dokumentierten Befunde 6 und 7 sind ebenfalls behoben. `scripts/client_vorbereiten.py:32,44,106` prüft Ziel- und Quellpfadkomponenten und behandelt `ConfigurationError`. Die fünf gezielten Tests bestanden. Der neue Quelltest erzwingt zusätzlich, dass vor der Symlinkablehnung kein `read_bytes` erfolgt. Die vollständige unabhängige Nachprüfung führte anschließend 50 Tests erfolgreich aus.

### Ursache des Claude-Loaderfehlers

Die Ursache lag in der ursprünglichen Verwendung von `--restricted` beim Aufruf in `scripts/pruefe_client_loader.py:124`. Eine unabhängige Vergleichsprobe variierte ausschließlich dieses Flag im Speicher. Mit Claude Code 2.1.300 ergaben sich:

| Startvariante | Kern geladen | Kernabsätze | Lokale Nachrichtenrequests | Synthetischer HTTP 400 |
| --- | --- | --- | --- | --- |
| Mit `--restricted` | nein | 0 von 16 | 2 | beobachtet |
| Ohne `--restricted` | ja | 16 von 16 | 2 | beobachtet |

`--setting-sources project`, leere strikte MCP-Konfiguration, deaktivierte Hooks, leere Werkzeugliste und Betriebssandbox blieben unverändert. Die Schlussfolgerung ist auf die überprüfte Clientversion begrenzt: `--restricted` verhindert hier auch das Einbeziehen der lokalen `CLAUDE.md`. Das entfernte Flag war für diesen Loadernachweis ungeeignet. Die übrige Isolation trägt die Sicherheitsgrenze weiterhin.

### Abschließende native Probe

Der finale Aufruf von `scripts/pruefe_client_loader.py` wurde separat mit einem neuen synthetischen Belegordner und folgenden absoluten Binärpfaden ausgeführt:

- `/Users/alexandergreif/.npm-global/bin/codex`, `codex-cli 0.162.1`: `core_loaded=true`. Nach Entfernen der synthetischen `AGENTS.md` wurde der Kern nicht mehr gefunden, ein Prompt-JSON wurde weiterhin erzeugt. Negativkontrolle bestanden.
- `/Users/alexandergreif/.local/bin/claude`, `2.1.300 (Claude Code)`: `core_loaded=true`, 16 von 16 Absätzen. Nach Entfernen der synthetischen `CLAUDE.md` wurde der Kern nicht mehr gefunden. Lokale Nachrichtenrequests und vorgesehener HTTP-400-Abbruch blieben nachweisbar. Negativkontrolle bestanden.

Gesamtergebnis: Exit 0. Die gespeicherte `loader.json` entsprach exakt dem ausgegebenen Bericht. Der Belegordner hatte Modus `0700`, seine drei Dateien `0600`. Die Skill-Linklisten vor und nach dem Lauf waren identisch. Der unabhängige Testordner wurde danach entfernt. Persistente Belege des Hauptagenten sind gesondert zuzuordnen.

### Sicherheitsbewertung des finalen Harness

Geprüfte Stellen: `scripts/pruefe_client_loader.py:36-77` für Isolation, `:118-134` für den lokalen Server und Clientaufruf sowie `:178-202` für Negativkontrolle und Belegspeicherung.

Die Umgebung übernimmt keine Anbieterzugangsdaten. Persönliche Konfigurationsorte zeigen auf neue synthetische Verzeichnisse. Reale Home-Dateiinhalte und Keychainzugriffe werden durch die OS-Sandbox eingeschränkt. Lesen installierter Clientprogramme und ihrer notwendigen Bibliotheken ist ausdrücklich erlaubt. Schreibzugriff ist auf den Testordner beschränkt. Claude erhält ausschließlich einen fiktiven Schlüssel und einen Loopback-Endpunkt mit einem eigens geöffneten Port. Der Server liefert absichtlich HTTP 400. Kein echter Anbieter und kein Modell wurden aufgerufen.

Diese OS-Grenzen wurden zusätzlich mit synthetischen Markern direkt geprüft:

- Lesen und Schreiben außerhalb des freigegebenen Testordners im echten Home: mit `EPERM` abgewiesen.
- Lesen und Schreiben innerhalb des Testordners: erfolgreich.
- Verbindung zum konkret freigegebenen Loopback-Port: erfolgreich.
- Verbindung zu einem zweiten lokalen Port: mit `EPERM` abgewiesen.

Keine offenen Funktionsbefunde für die geprüften konkreten Binärpfade. Zwei optionale Härtungen für eine spätere allgemeinere Nutzung bleiben:

1. `skill_listing` in Zeile 32 sollte neben stdout auch den Rückgabecode festhalten. Dadurch lässt sich ein erfolgreich unveränderter Verzeichnisstand von zwei gleichartigen fehlgeschlagenen Auflistungen unterscheiden.
2. Die Ausnahmen für Clientbibliotheken in Zeile 39 sollten bei beliebigen zusätzlichen Binärpfaden nie auf das gesamte echte Home ausgedehnt werden. Die aktuell geprüften Installationen verwenden engere Programmverzeichnisse. Ein expliziter Schutz gegen eine so breite Freigabe würde die sichere Wiederverwendung erleichtern.

Der Nachweis betrifft native Einbeziehung des Regeltexts. Er belegt weder Befolgung durch ein Modell noch vollständige Skillinstallation, Anmeldung oder Dienstfunktion.

## Verlauf der vorangegangenen Nachprüfung

## Nachprüfungsstand vor Clientkorrektur

Gesamtsuite erneut ausgeführt: 49 Tests bestanden. Davon betreffen 45 Einrichtung, Transfer, Konfiguration und Register. Vier betreffen den neu hinzugekommenen Clientvorbereiter. Dessen Code wurde anschließend separat gelesen und synthetisch auf weitere Fehler geprüft.

Die fünf unten historischen Erstbefunde sind behoben:

1. Import verwendet `tempfile.mkstemp` und löscht nur die eigens erzeugte temporäre Datei. Die bestehende PID-Markerdatei blieb im Regressionstest unverändert.
2. Einrichtung verwendet dieselbe Markdown-Kodierung und Felddefinition wie Transfer.
3. Gemeinsame Wertvalidierung erfolgt vor Einrichtungsvorschau und Schreiben. 4096 Zeichen je Feld bestehen den Durchlauf, 4097 werden abgewiesen.
4. Registertest vergleicht den aufgelösten Erwartungspfad. Der Mac-Test besteht.
5. Übersprungene Zugangsdaten erzeugen ein kommentiertes leeres `BLOCKBRAIN_API_KEY`-Feld mit privaten Dateirechten.

Zusätzlich in der Nachprüfung erkannt und behoben:

- Unicode-Zeilentrenner U+2028 und U+2029 wurden zunächst akzeptiert, zerlegten aber beim späteren `splitlines()` die Profiltabelle. `valid_value` schließt diese sowie ungültige Surrogate jetzt aus. Tests bestanden.
- Ein zulässiges Markdown-Profil mit 100 Vorlieben zu je 1250 Zeichen ergab 126753 Bytes, der Export jedoch 133032 Bytes. Export war erfolgreich, Import scheiterte an 131072 Bytes Grenze. Die gemeinsame Validierung prüft jetzt beide serialisierten Formate vor Vorschau oder Schreiben. Tests für beide Expansionsrichtungen bestanden.

Unabhängiger vollständiger CLI-Durchlauf mit synthetischen Daten: Einrichtung, Exportvorschau, bestätigter Export, Importvorschau und bestätigter Import bestanden. Ein Wert mit Unicode, Backslash, Pipe und Markdownformatierung blieb unverändert. Vorschauen erzeugten keine Zieldateien. Die leere Schlüsselvorlage und Dateimodus `0600` wurden geprüft.

Architektur: Der Profilvertrag ist jetzt funktional zentralisiert. Die Einrichtung importiert hierfür derzeit `profil_transfer`. Ein späteres Auslagern in ein kleines reines Datenvertragsmodul bleibt eine Wartbarkeitsempfehlung, kein offener Funktionsfehler. Es wurde keine zusätzliche Ablage persönlicher Daten eingeführt.

## Erweiterung: Clientvorbereiter

### Behobener Bug 6: Symlinkfehler entgeht der CLI-Fehlerbehandlung

**Stellen:** `scripts/client_vorbereiten.py:31,104`.

Ein synthetischer Symlink im Zielpfad löst in der importierten Funktion `reject_symlink_components` einen `pruefe_konfiguration.ConfigurationError` aus. `main` fängt nur `PreparationError`, `OSError` und `UnicodeError`. Tatsächlich erscheint ein Python-Traceback. Erwartet ist eine behandelte Fehlermeldung mit Returncode 1. Keine Dateien wurden erzeugt.

**Kleinster Fix:** `ConfigurationError` ebenfalls behandeln. Den bestehenden Symlinktest um die Prüfung ergänzen, dass kein Traceback ausgegeben wird.

### Behobener Bug 7: Symlinks in übergeordneten Quellordnern werden verfolgt

**Stellen:** `scripts/client_vorbereiten.py:42-45`.

Synthetische Reproduktion: `PACKAGE/allgemein` zeigt als Symlink auf einen Ordner außerhalb des synthetischen Pakets. Dort liegen die drei erwarteten relativen Dateien mit Markerinhalt. `source_contents()` liest alle drei Markerdateien. Die Blattdateien selbst sind regulär, deshalb greift `source.is_symlink()` nicht.

**Erwartet:** Auswahl bleibt auf tatsächliche Paketdateien beschränkt. **Beobachtet:** Der Generator folgt einem externen Quellordner und kann dessen Inhalte in die Clientregeln kopieren.

**Kleinster Fix:** Sämtliche Quellpfadkomponenten bis zur Paketgrenze auf Symlinks prüfen und vor dem Lesen ablehnen. Synthetischen Regressionstest mit verlinktem Elternordner hinzufügen.

## Begrenzte native CLI-Prüfung

CLI-Hilfe wurde mit leeren synthetischen Konfigurationsordnern ausgeführt. Die Betriebssystemsandbox sperrte Netzwerkzugriff, Schreibzugriff außerhalb des Testordners und das Lesen von Dateiinhalten im echten Benutzerordner außerhalb des Testordners sowie unter `/Library/Keychains`. Nur Metadatenabfragen für Pfadauflösung blieben zulässig. Kein Modellaufruf, keine Zugangsdaten, kein Upgrade. Temporäre Testordner danach entfernt.

Die dabei geprüfte Codex-Binärdatei war `/usr/local/bin/codex`, Version `0.38.0`. Ihre CLI-Hilfe zeigte keinen dokumentierten Offline-Prompt-Dump. Der Hauptagent hat daneben `/Users/alexandergreif/.npm-global/bin/codex` mit Version `0.162.1` und `debug prompt-input` festgestellt. Diese beiden Installationen sind ausdrücklich zu unterscheiden. Die Aussage zur älteren Hilfe gilt nicht für die neuere Binärdatei. Ein späterer Loadernachweis muss den tatsächlich ausgeführten absoluten Binärpfad nennen.

Die Hilfe von `/opt/homebrew/bin/claude` nennt `--setting-sources`, `--settings` und `--strict-mcp-config`. Eine tatsächlich geladene Regel oder Modellwirkung wurde hierdurch nicht nachgewiesen. Die gesonderte Loaderprobe des Hauptagenten ist nicht Teil dieses Befunds.

## Historische Erstprüfung

## Analyse

Geprüft wurden `scripts/einrichten.py`, `scripts/profil_transfer.py`, `scripts/pruefe_register.py`, deren Tests, der gemeinsame Pfadprüfer sowie die zugehörigen Vorlagen und Vorgaben. Der Ordner ist kein Git-Repository. Ein Vergleich mit Commitständen war daher nicht möglich. `tasks/todo.md` und `tasks/lessons.md` fehlen hier. `.aios/PLAN.md` und der Kern von `.aios/NOTIZEN.md` wurden gelesen.

Die Diagnose folgt `systematic-debugging`, die Befundprüfung den Nachweisregeln von `precommit-review`. Keine Implementierung oder Tests verändert. Alle Testdaten waren synthetisch. Keine tatsächlichen Profile, Kundeninhalte, Zugangsdaten, Archive oder Clientkonfigurationen gelesen. Kein Browser, Netzwerk oder Installationslauf.

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` führte 39 Tests aus. 38 bestanden. Der Registererfolgsfall scheiterte am Mac-Pfadalias. Zusätzliche synthetische Prüfungen belegten drei weitere Codefehler und eine Abweichung von Entscheidung 84.

## Befunde und kleinste Korrekturen

### 1. Bug: Import löscht eine vorbestehende temporäre Datei

**Stelle:** `scripts/profil_transfer.py:274-281`, insbesondere die unbedingte Löschung in Zeile 281.

**Reproduktion:** Ein synthetisches Ziel mit gültigem `profil.md` anlegen. Daneben `.profil.md.import-<aktuelle Prozess-ID>` mit beliebigem Markerinhalt vorbereiten. Einen gültigen Import innerhalb desselben Prozesses mit `apply=True` und bestätigtem `ja` starten.

**Erwartet:** Die exklusive Dateianlage erkennt die Kollision und lässt vorhandene Dateien unverändert.

**Beobachtet:** `write_new` wirft `FileExistsError`. Trotzdem löscht der äußere `finally` die fremde Datei. Reproausgabe: `PREEXISTING TEMP PRESERVED: False`. Das eigentliche Profil bleibt erhalten, eine Sicherung wurde schon erzeugt.

**Fix:** Temporärdatei mit eindeutigem Namen exklusiv erzeugen, etwa über `tempfile.mkstemp`. Nur Dateien bereinigen, deren erfolgreiche eigene Anlage nachgewiesen ist. Ein bloßes `exists()` vor `unlink()` genügt nicht als Eigentumsnachweis.

**Prüfung:** Kollisionsfall als Regressionstest aufnehmen. Markerdatei, Profil und sonstige Dateien müssen erhalten bleiben. Erfolgsfall und Schreibfehlerpfad ebenfalls prüfen.

### 2. Bug: Einrichtung und Transfer verwenden unterschiedliche Markdown-Kodierung

**Stellen:** `scripts/einrichten.py:89` und `scripts/profil_transfer.py:73-80,163-164`.

**Reproduktion:** Ein Profil mit `Arbeitsweise = r"Ordner C:\work"` über `einrichten.profile_text` rendern und anschließend mit `profil_transfer.parse_profile` lesen.

**Erwartet:** Derselbe bestätigte Text bleibt erhalten.

**Beobachtet:** `Ordner C:\work` wird zu `Ordner C:work`. Bei einem Wert aus Backslash und Pipe bricht der Export wegen eines scheinbar fehlenden Profilfelds ab. Die Einrichtung escaped Pipes, der Transfer interpretiert jeden Backslash als Escapezeichen. Der Transferrenderer escaped dagegen auch Backslashes.

**Fix:** Eine gemeinsame Markdown-Kodierung für Profilwerte verwenden. Zumindest Backslashes vor Pipes escapen, wie bereits in `profil_transfer.md` umgesetzt. Die gemeinsame Funktion sollte in einem kleinen Datenvertragsmodul liegen, nicht durch Import eines CLI-Einstiegspunkts gekoppelt werden.

**Prüfung:** Einrichtung, Export und Import gemeinsam mit Backslashes, Pipes, deren Kombination und Unicode prüfen. Auf Gleichheit der Daten nach dem vollständigen Durchlauf testen.

### 3. Bug: Einrichtung akzeptiert nicht exportierbare Profilwerte

**Stellen:** `scripts/einrichten.py:162,181` und `scripts/profil_transfer.py:143-144`.

**Reproduktion:** Für eines der sieben Einrichtungsfelder 4097 Zeichen eingeben. Die Einrichtung hat dafür keine Wertbegrenzung. Das erzeugte Profil anschließend exportieren.

**Erwartet:** Eine erfolgreich eingerichtete Angabe erfüllt auch den Exportvertrag, oder die Einrichtung weist sie vor Bestätigung verständlich ab.

**Beobachtet:** Der Export meldet `Ungültiger Profilwert`. Die spätere Grenze von 4096 Zeichen wird bei der Einrichtung nicht geprüft.

**Fix:** Gemeinsame Validierung der sieben Werte vor der Einrichtungsvorschau verwenden. Die sieben Felder und ihre Grenzen einmal als Datenvertrag definieren. Zusätzlich prüfen, dass ein zulässiges Exportdokument innerhalb der maximalen Importdateigröße bleibt.

**Prüfung:** 4096 und 4097 Zeichen sowie Einrichtung bis Transfer als Integrationstest abdecken.

### 4. Bug im Test: kanonischer Mac-Pfad wird gegen Alias verglichen

**Stellen:** `tests/test_register.py:46`, Ausgabe in `scripts/pruefe_register.py:117`.

**Reproduktion:** Gesamttests auf diesem Mac ausführen. `TemporaryDirectory` liefert einen Pfad unter `/var/folders`. Der gemeinsame Pfadprüfer löst ihn zu `/private/var/folders` auf.

**Erwartet:** Test vergleicht die kanonischen Pfade.

**Beobachtet:** `AssertionError` allein wegen des zusätzlichen Präfixes `/private`. Returncode und Routing sind korrekt.

**Fix:** Erwartungswert als `str((self.home / 'customers/demo').resolve())` bilden. Keine Änderung der Implementierung erforderlich.

**Prüfung:** Registertest und Gesamtsuite ausführen. Den zusätzlichen Testbeleg behalten, dass keine Projektordner angelegt werden.

### 5. Bug im vereinbarten Umfang: übersprungener Schlüssel hinterlässt keine Vorlage

**Stellen:** `scripts/einrichten.py:134-136`, zugehörige Erwartung `tests/test_einrichten.py:53`.

**Grundlage:** `README.md:218`, bestätigte Entscheidung 84, verlangt leere benötigte Felder mit kurzen Hinweisen in `.env`.

**Reproduktion:** Einrichtung abschließen und die optionale Blockbrain-Schlüsseleingabe überspringen.

**Erwartet:** Private `.env` mit leerem `BLOCKBRAIN_API_KEY` und kurzem Ergänzungshinweis.

**Beobachtet:** Datei ist vollständig leer. Der Test bestätigt derzeit dieses abweichende Verhalten.

**Fix:** Leeres Schlüsselfeld und kurzen Kommentar schreiben. Vorhandene Werte weiterhin unangetastet lassen. Dokumentation und Test an die bestätigte Vorgabe anpassen. Dies belegt weiterhin keine funktionierende Dienstverbindung.

## Architektur und bestandene Prüfungen

- Einrichtung und Register nutzen denselben Pfadprüfer. Bestätigungsstatus, Schemaversion, unbekannte Felder, Mac-Normalisierung und Trennung der Ablagebereiche werden dadurch konsistent behandelt.
- Der Datenvertrag des persönlichen Profils ist hingegen zwischen Einrichtung, Transfer und Vorlage mehrfach definiert. Die Befunde 2 und 3 zeigen konkrete Folgen. Ein kleines gemeinsames Modul für Felder, Kodierung und Validierung genügt. Persönliche Daten müssen dafür nicht zusätzlich gespeichert werden.
- Der Export liest ausschließlich `profil.md` und verwendet eine enge Feldliste. `.env`, lokale Pfade, Register, Wissen und Änderungsverlauf gehen nicht in das Exportdokument ein. Die synthetischen Tests mit einer nicht lesbaren geheimen Nachbardatei bestanden.
- Vorschau und Ablehnung schreiben nicht. Zwei unmittelbar aufeinanderfolgende Exportvorschauen ließen sämtliche synthetischen Dateien unverändert.
- Einrichtung schützt ein bestehendes Profil und vorhandene `.env`-Werte durch vollständige Ablehnung des bestehenden Ziels. Neue Dateien sind privat. Die finale Ordnerübernahme verwendet eine Betriebssystemoperation ohne Überschreiben.
- Der Registerprüfer las keine Projektinhalte. Wurzelgrenzen, Quellcodeausschluss, doppelte Zuordnungen, ungültige Statuswerte, Zugangsdaten in Repositoryadressen und ein Symlink-Ausbruch wurden geprüft.
- Ein erneuter bestätigter Import identischer Angaben legt derzeit eine weitere Sicherung an. Das ist keine schreibfreie Wiederholung. Ein semantischer Gleichheitscheck vor dem Schreiben wäre eine optionale Verbesserung, falls auch bestätigte Wiederholungen idempotent sein sollen.

## Verifikation nach Korrektur

Die fünf Befunde gezielt beheben und ihre Regressionstests ausführen. Danach Gesamtsuite und synthetischen CLI-Ablauf Einrichtung, Exportvorschau, Export, Importvorschau, Import, Ablehnung sowie vorhandenes Ziel erneut prüfen. Dateien und Rechte kontrollieren. Eine unabhängige Nachprüfung steht aus. Native Clientanbindung, Anmeldung und Dienstfunktion sind durch diesen Review nicht abgenommen.
