# Unabhängige Prüfung des Erstinstallers

Stand: 20.10.2026. Geprüft wurden `scripts/installieren.py`, `tests/test_installieren.py`, `install.sh`, `docs/erstinstallation.md` sowie die verwendeten Plan-, Paket- und Pfadhelfer. Keine Produktionsdatei verändert. Alle zusätzlichen Fälle verwendeten synthetische temporäre Profile und Ziele, die danach entfernt wurden. Keine tatsächlichen Profile, Clientkonfigurationen, Zugangsdaten oder Kundeninhalte gelesen. Kein Client, Browser oder Anbieter gestartet.

## Ergebnis

Abschließender Stand: Alle fünf Befunde einschließlich der ergänzten Prüfung dauerhafter Elternwechsel sind korrigiert und unabhängig nachgeprüft. Die gesamte Testsuite besteht mit 83 Tests. Der finale native Installationsbeleg stimmt mit den aktuellen Quellhashes überein. Keine offenen konkreten Befunde. Die folgenden Befunde und Zwischenstände dokumentieren die Prüfung historisch. Die jeweiligen Zeilenangaben beziehen sich auf die damals geprüfte Fassung.

### 1. Hohe Priorität: Elternwechsel erlaubt Schreiben außerhalb des geplanten Ziels

**Stellen:** `scripts/installieren.py:96-102`, Aufruf `:159-163`. Geschwisterpfade: `:78-93`, `:105-121`, `:166-171`.

`write_exclusive` prüft den Pfad, öffnet die Datei danach aber erneut über den vollständigen Namen. `O_NOFOLLOW` schützt nur die letzte Komponente. Ein zuvor geprüfter Elternordner kann zwischen Prüfung und Öffnung ausgetauscht werden.

**Reproduktion:** Ausschließlich synthetische `.claude` unmittelbar beim `os.open` von `CLAUDE.md` umbenennen, an ihrer Stelle einen Symlink auf einen zweiten synthetischen Ordner außerhalb des geplanten Homes anlegen, den ursprünglichen Öffnungsaufruf ausführen und anschließend den Elternordner zurückstellen.

**Beobachtet:** Exit 0 und Status `installed`. Die Regeldatei liegt im Außenordner. Am vorgesehenen Ziel fehlt sie. Das Journal behauptet trotzdem, die vorgesehene Datei angelegt zu haben.

**Kleinster belastbarer Fix:** Elternkomponenten über verankerte Verzeichnisdeskriptoren und `O_DIRECTORY | O_NOFOLLOW` öffnen. Dateien mit `dir_fd` relativ zum geprüften Elternverzeichnis anlegen. Für dieselbe Grenze müssen auch Ordneranlage, Journalspeicherung und Skilllinkanlage ihre Schreiboperationen an geprüfte Deskriptoren binden. Ein zusätzlicher Pfadcheck allein schließt das Zeitfenster nicht.

**Regression:** Den beschriebenen gezielten Elternwechsel prüfen. Keine Datei darf über den eingeschobenen Symlink angelegt werden. Ein Erfolgsstatus darf kein tatsächlich fehlendes Ziel behaupten.

### 2. Mittlere Priorität: Ausgetauschtes Eigentumsjournal wird überschrieben

**Stellen:** `scripts/installieren.py:105-121`, insbesondere `:117-119`, Fehlerpfad `:174-177`.

Die spätere Journalspeicherung prüft nur, dass `installation.json` eine reguläre Datei und kein Symlink ist. Sie prüft weder die zuvor selbst erzeugte Dateiidentität noch ihren erwarteten Inhalt.

**Reproduktion:** In einer synthetischen Installation nach der ersten Journalspeicherung und vor der nächsten Aktualisierung die Datei entfernen und durch eine reguläre Datei mit `FOREIGN_JOURNAL_MARKER` ersetzen. Die übrige Installation unverändert weiterlaufen lassen.

**Beobachtet:** Exit 0, Status `installed`, fremder Marker verloren. Das Journal des anderen Schreibers wird kommentarlos ersetzt.

**Kleinster Fix:** Eigene Journalidentität und erwarteten Inhalt über die Speicheraufrufe führen. Einen erkannten Austausch als Fehler behandeln und die fremde Datei erhalten. Auch der Fehlerpfad darf danach nicht erneut versuchen, diese Datei mit Status `failed` zu ersetzen. Die Schreiboperation zusätzlich gegen Elternwechsel absichern. Eine Prüfung vor `os.replace` allein ist kein vollständiger Schutz gegen einen weiteren gezielten Blattaustausch genau zwischen Prüfung und Ersetzung. Diese Grenze muss entweder technisch vermieden oder enger dokumentiert werden.

**Regression:** Fremde reguläre Datei zwischen zwei Journalständen einsetzen. Erwartet sind Fehler und unveränderter Marker, kein Erfolg und kein zweiter ersetzender Fehlerjournalversuch.

### 3. Mittlere Priorität: Nach Schreibfehler vorhandene Datei fehlt im Eigentumsjournal

**Stellen:** `scripts/installieren.py:96-102`, `:160-163`.

Der Eintrag wird erst nach vollständig erfolgreichem Schreiben und Synchronisieren ergänzt. Die Datei kann zu diesem Zeitpunkt bereits angelegt worden sein, obwohl die Funktion noch einen Fehler meldet.

**Reproduktion:** Beim ersten Regeldateischreiben genau den `os.fsync`-Aufruf einmalig mit einem synthetischen `OSError` fehlschlagen lassen. In der geprüften Zweiclientfolge ist dies der vierte `fsync`-Aufruf. Die nachfolgenden Journalspeicherungen funktionieren normal.

**Beobachtet:** Exit 1 und Status `failed`. Eine 6753 Byte große `CLAUDE.md` bleibt am Ziel, fehlt aber vollständig in `state.created`. Der vorhandene Test `test_failure_after_runtime_records_failed_status` wirft bereits vor Dateianlage und erfasst diesen Fall deshalb nicht.

**Kleinster Fix:** Eine erfolgreich exklusive Anlage sofort als eigene Operation erfassen, bevor Schreiben oder Synchronisation fehlschlagen können. Den Eintrag als unvollständig beziehungsweise ungeprüft kennzeichnen, bis Inhalt und Hash bestätigt sind. Ein bloß vorgezogener Eintrag mit dem geplanten Hash wäre ebenfalls unehrlich, wenn nur Teilbytes geschrieben wurden. Analog müssen andere tatsächlich erzeugte Objekte bei Teilfehlern im Journal nachvollziehbar bleiben.

**Regression:** Fehler nach Dateianlage beziehungsweise beim Synchronisieren auslösen und prüfen, dass das vorhandene Objekt im fehlgeschlagenen Journal korrekt als unvollständig beschrieben ist. Der normale Fehlerfall vor Anlage darf weiterhin keine nicht erzeugte Datei als Eigentum behaupten.

### 4. Mittlere Priorität: Fehlender Runtime-Elternordner fällt erst nach Schreibbeginn auf

**Stellen:** `scripts/installieren.py:144-148`, `scripts/paket_bauen.py:183-184`.

Der Installationsplan akzeptiert einen frischen verschachtelten Runtimepfad. `build` setzt jedoch einen bereits vorhandenen direkten Elternordner voraus. Der Installer legt diesen vor dem Paketbau nicht an.

**Reproduktion:** Gültige synthetische Konfiguration mit `paths.runtime = "~/fresh/parent/runtime"`, wobei `fresh` noch nicht existiert. Vorschau und Bestätigung durchlaufen.

**Beobachtet:** Erst nach Anlage von `profil/zustand/installation.json` scheitert `mkdtemp` mit ENOENT. Status `failed`, keine Runtime. Dieser vorhersehbare Zustand wird weder als Vorabkonflikt angezeigt noch als zulässige frische Installation unterstützt.

**Kleinster Fix:** Den fehlenden Runtime-Elternpfad nach Bestätigung sicher anlegen und angelegte Ordner im Eigentumsjournal erfassen. Falls der Vertrag diese Anlage nicht erlauben soll, muss die Vorschau bereits einen Konflikt melden und vollständig schreibfrei bleiben. Für einen Erstinstaller ist die erste Variante konsistenter mit den anderen frisch angelegten Bereichen.

**Regression:** Zwei fehlende Elternkomponenten verwenden und vollständige Installation samt Journal prüfen. Vorhandene fremde Dateien an einer Elternkomponente müssen weiterhin vor Schreibbeginn blockieren.

## Bestandene Prüfungen und Grenzen

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q`: 75 Tests bestanden. Darin sechs Erstinstallertests.
- Vorschau und Ablehnung legen keine Dateien oder Ordner an. Änderungen der Konfiguration oder Paketquellen nach der Vorschau werden vor Installation erkannt. Ein neuer Plan wird ebenfalls mit der Vorschau verglichen.
- Vorhandene Runtime, fremde Regeln, ruhende Symlinks, ungeklärte Clientumgebung und falsche Konfigurationsposition blockieren. Exklusive Dateianlage schützt ein bereits vorhandenes Blattziel.
- Der normale Zweiclientfall erhält synthetisches Profil, `.env`, `pfade.json` und bestehende Ausgabedateien bytegleich. Manifesthashes und Skilllinkziele stimmen.
- Globale Regeldateien verweisen absolut und URL-kodiert auf Runtime-Referenzen sowie die bestätigte Konfigurationsdatei. Der geänderte Inhalt hat einen eigenen Hash im Journal. Der Quellkernhash bleibt im erzeugten Kommentar nachvollziehbar.
- `install.sh` reicht Argumente gequotet an den lokalen Pythoninstaller weiter. Es startet keinen Client und installiert keine Abhängigkeit.
- Der dokumentierte Status `failed` ist bei einem vor der Regelanlage ausgelösten Fehler korrekt. Er ist bei einem Fehler während der Journalpersistenz nicht immer zuverlässig schreibbar. Die Dokumentation sollte diese Grenze benennen, statt jeden Fehlerfall pauschal mit einem gespeicherten `failed`-Status gleichzusetzen.

Der Hauptagent übernimmt Korrekturen. Eine gezielte Nachprüfung der vier Befunde steht aus. Diese Prüfung ist keine native Client- oder Dienstabnahme.


## Erste Nachprüfung der Korrekturen

Die überarbeitete Fassung besteht 80 Tests. Die gezielten Regressionen für einen fehlenden Runtime-Elternpfad, Regeldatei-`fsync`-Fehler, ein fremdes ausgetauschtes Journal und temporäre Symlinkwechsel bei Regel-/Runtime-Eltern bestehen. Befunde 2 bis 4 sind damit in den reproduzierten Fällen korrigiert. Befund 1 ist gegen temporäre Symlinks behoben, bleibt für den folgenden dauerhaften Elternwechsel teilweise offen.

### Offene Ergänzung zu Befund 1: Dauerhaft ersetzter Elternordner

**Stellen:** `scripts/sichere_dateien.py:48-77`, analog `:84-91`, `:115-153`. Abschließender Erfolg in `scripts/installieren.py:201-202`.

Die fd-gebundenen Schreibvorgänge verhindern das Folgen eingeschobener Elternsymlinks. Die anschließende Identitätsprüfung erfolgt jedoch weiterhin relativ zum bereits geöffneten Eltern-FD. Sie belegt damit nicht, dass der absolute Zielpfad noch zu diesem Elternordner führt.

**Konkrete Reproduktion:** Unmittelbar nachdem `sicher.parent()` den Eltern-FD für die synthetische global installierte `CLAUDE.md` geliefert hat, `.claude` dauerhaft in einen anderen synthetischen Ordner umbenennen und am ursprünglichen Ort einen leeren regulären Ersatzordner anlegen. Danach den ursprünglichen FD unverändert zurückgeben.

**Beobachtet:** Exit 0, Status `installed`, Regeldatei nur im verschobenen Ordner. Am ursprünglich geplanten Pfad fehlt `CLAUDE.md`. Der Installer bestätigt damit einen nicht vorhandenen globalen Regelpfad.

**Kleinster Fix:** Zusätzlich zur fd-gebundenen Ausführung die Identität der gesamten absoluten Elternhierarchie beziehungsweise deren Zuordnung zum geöffneten Eltern-FD prüfen und vor Erfolgsbestätigung alle installierten Ziele über ihre absoluten Pfade auf erwartete Identität und Inhalt beziehungsweise Linkziel prüfen. Dauerhafte Wechsel müssen zum Fehler führen. Entsprechende Geschwisterkontrollen für Runtime, Journal und Skilllinks einbeziehen. Die Grenze gegenüber Änderungen nach einer abgeschlossenen Prüfung bleibt naturgemäß bestehen und darf nicht als unbegrenzte Konkurrenzgarantie beschrieben werden.

### Neuer Befund 5: Pakethelfer akzeptiert absolute Eintragspfade

**Stelle:** `scripts/sichere_dateien.py:128-141`.

**Reproduktion:** `build_directory(<synthetischer Runtimepfad>, {<absoluter synthetischer Außenpfad>/marker.txt: b"SYNTHETIC_ABSOLUTE_MARKER"})`.

**Beobachtet:** Die Markerdatei wird außerhalb des Stagingordners angelegt. Anschließend wird eine leere Runtime erfolgreich veröffentlicht. `Path.parts` enthält bei absoluten Pfaden die Wurzelkomponente `/`. Diese wird nicht abgewiesen, und ein späteres `os.open("/", dir_fd=...)` verlässt das Stagingverzeichnis.

**Einordnung:** Die derzeitigen Aufrufer erzeugen ihre Eintragspfade intern aus einer kontrollierten relativen Paketaufnahme. Es wurde kein Angriff über die heutige CLI nachgewiesen. Die neue Helpergrenze ist trotzdem falsch und sollte vor Wiederverwendung geschlossen werden.

**Kleinster Fix:** Sämtliche Eintragspfade vor jeglichem Schreiben validieren. Absolute Pfade und Elterntraversierung ablehnen. Einen direkten Helpertest mit absolutem Außenpfad ergänzen, der unveränderten Außenordner und fehlende Runtime bestätigt.

### Architektur und Dokumentationsgrenze

Die kleinen gemeinsamen fd-gebundenen Funktionen passen zur bestehenden Standardbibliotheksarchitektur und vermeiden wiederholte unsichere vollständige Pfadöffnungen. `Journal` hält nun die selbst angelegte Datei offen, prüft Identität und erwarteten Inhalt und schreibt über diesen FD. Dadurch wird eine unter demselben Namen eingesetzte fremde Datei nicht mehr ersetzt. Die Fehlerbehandlung propagiert den ursprünglichen Fehler, auch wenn der Status nicht gespeichert werden kann.

Regeldateien werden unmittelbar nach exklusiver Anlage mit Inode, Gerät und unvollständigem Status registriert. Bei Schreibfehler wird ihr tatsächlicher lesbarer Inhalt gehasht. Die neue Regression bestätigt den vorhandenen Teilstand korrekt. Fehlende Runtime-Eltern werden vor dem Paketbau angelegt und in `created_directories` erfasst.

Journalaktualisierungen erfolgen jetzt durch Kürzen und Schreiben derselben Datei. Sie sind daher nicht atomar. Nach Prozessabbruch oder Persistenzfehler kann das Journal unvollständig oder auf einem früheren Status stehen. Die Aussage in `docs/erstinstallation.md`, nach einem Fehler bleibe stets ein gespeicherter `failed`-Status erhalten, muss entsprechend eingeschränkt werden. Eine automatische Wiederherstellung wird weiterhin nicht zugesagt.

## Code- und Belegprüfung der nativen Installationsprobe

Gelesen wurden `scripts/pruefe_installation_lokal.py`, `docs/installationsprobe.md` und die wiederverwendeten Loaderhelfer. Die Probe installiert in ein erfundenes Home, verwendet nur synthetische Profildateien und startet die Clients in einem leeren Projekt außerhalb der Runtime. Die globalen Regeldateien und Skillverknüpfungen stammen aus der tatsächlichen synthetischen Installation. Es wurden in dieser Nachprüfung keine weiteren Clients gestartet.

`claude_probe` behält `setting_sources="project"` als Standard. Nur die globale Installationsprobe erweitert über einen ausdrücklichen Parameter auf `user,project`, wobei HOME und CLAUDE_CONFIG_DIR auf den synthetischen Benutzer zeigen. Das erweitert keinen persönlichen Zugriff. Die bereits geprüften Betriebssystemgrenzen, deaktivierten Hooks, leeren externen MCP-Einstellungen und lokalen HTTP-400-Testserver bleiben erhalten.

Der vorhandene Lauf `.aios-test-installation-20261020-b` zeigt:

- Synthetische Installation erfolgreich, 58 erfasste Objekte, Profil/Testschlüssel/Pfadkonfiguration bytegleich.
- Wiederholung mit konkreter Meldung „Eigentumsdatei existiert bereits“ gestoppt.
- Alle 37 Manifestdateien laut Probe passend gehasht.
- Codex 0.162.1 und Claude Code 2.1.300 jeweils mit globalem Kern, acht regulären Beschreibungen und verborgenem Auftragshelfer bei automatischer Erkennung.
- Jeweils neun vollständige explizite Skilltexte und synthetischer Fehlernachweis. Beide Negativkontrollen bestanden.
- Die gespeicherten Vorher-/Nachher-Listen der tatsächlichen Skillverknüpfungen wurden unabhängig byteweise verglichen und sind gleich.

Dieser Beleg stammt vor den hier nachgeprüften Installerkorrekturen. Er belegt die damalige globale Einbindung und ersetzt keinen neuen finalen Lauf nach den offenen Korrekturen. Die Probe erzeugt keine Modellantwort und prüft weder Anmeldungen noch Anbieterfunktionen. Im gelesenen Probeaufbau wurden keine zusätzlichen konkreten Sicherheits- oder Vertragsfehler gefunden.


## Abschließende Nachprüfung

Die letzten beiden offenen Grenzen sind geschlossen. `sichere_dateien.py:48-57` prüft die Zuordnung eines geöffneten Elternordners zum absolut erneut und ohne Symlinks geöffneten Pfad. Datei-, Link- und Runtimeoperationen verwenden diese Kontrolle. `installieren.py:111` sichert auch das Journal gegen einen verschobenen Elternordner ab. `verify_owned` ab `:148` prüft die angelegten Ziele abschließend über ihre absoluten Pfade, bei Regeln zusätzlich ihre erfasste Identität, bei Dateien den tatsächlichen Hash und bei Links Typ und Linkziel. Die Abschlusskontrolle läuft vor und nach dem gespeicherten Erfolgsstatus (`:240-243`).

`tests/test_installieren.py:246-265` bestätigt, dass ein nach dem Schreiben dauerhaft verschobener Regelordner nicht zu einem erfolgreichen Status führt. `:278-294` weist einen dauerhaften Journal-Elternwechsel zurück und erhält die fremde Markerdatei. Der temporäre Symlinkschutz bleibt durch die vorherigen Regressionen abgedeckt.

`sichere_dateien.py:131-136` validiert alle Paketpfade vor Anlage des Stagingordners. Absolute Pfade und Elterntraversierung werden abgewiesen. Der Regressionstest `tests/test_installieren.py:267-276` bestätigt den unveränderten Außenmarker und das Fehlen von Runtime und Stagingordner.

`docs/erstinstallation.md` beschreibt nun zutreffend, dass Journalaktualisierungen nicht atomar sind. Bei Journalfehler oder Stromabbruch kann der Status älter oder die Datei unvollständig sein. Der Installer versucht `failed` zu speichern, garantiert es für solche Fehler aber nicht. Eine automatische Wiederherstellung bleibt ausdrücklich außerhalb des Umfangs.

**Testlauf:** `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q` bestand mit 83 Tests. Keine Produktionsdatei wurde durch den Prüfagenten geändert. Weitere identische Clientläufe waren für die Nachprüfung nicht erforderlich.

### Finaler nativer Beleg und Bindung an den geprüften Stand

Der Hauptagent hat `.aios-test-installation-20261020-final/installation.json` erzeugt. Der unabhängige Abgleich bestätigt:

- Alle neun gespeicherten `proof_sources_sha256` entsprechen den aktuellen Dateien, darunter Installer, Pfadhelfer, Plan, Paketbau und native Probe. `proof_sources_unchanged` ist wahr.
- Das gesamte gespeicherte Paketmanifest entspricht dem aus dem aktuellen kontrollierten Quellbestand erzeugten Manifest.
- Die beiden globalen Kernhashes entsprechen unabhängig neu erzeugten Regeltexten aus dem aktuellen Kern und den synthetischen Zielpfaden des gespeicherten Laufs.
- Codex 0.162.1 und Claude Code 2.1.300 laden jeweils den globalen Kern, erkennen die 13 regulären Skillbeschreibungen und bieten den Auftragshelfer nicht automatisch an.
- Alle 14 Skills werden in beiden Clients ausdrücklich mit vollständigem Skilltext geladen. Alle 28 expliziten Fälle zeigen den kontrollierten lokalen Fehler. Beide Negativkontrollen bestehen.
- Synthetische private Dateien bleiben unverändert, die wiederholte Erstinstallation wird blockiert. Die tatsächlich gespeicherten Vorher-/Nachher-Listen der bestehenden Skillverknüpfungen sind bytegleich.

Dieser finale Beleg gilt für den korrigierten und hier nachgeprüften Stand. Er belegt synthetische Erstinstallation und native globale Kontextladung. Er belegt weiterhin keine Modellantwort, Fachfunktion, echte Anmeldung, Anbieterkommunikation oder Installation auf einem zweiten Rechner.
