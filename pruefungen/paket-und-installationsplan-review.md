# Unabhängige Prüfung: Paketbau und Installationsplan

Stand: 19.10.2026. Prüfung beider Bausteine abgeschlossen. Drei bestätigte Paketbefunde, zwei Planungsempfehlungen und ein anschließender Befund zum getrennten Codex-Skillpfad wurden korrigiert und unabhängig nachgeprüft. Keine offenen konkreten Befunde.

## Umfang und Nachweis

Geprüft wurden `scripts/paket_bauen.py`, `tests/test_paket_bauen.py`, `docs/paketbau.md`, `scripts/installationsplan.py`, dessen sieben Tests und Dokumentation. Keine Implementierungsdatei verändert. Keine aktive Installation, kein Client gestartet, keine tatsächlichen Profile, Zugangsdaten, Verbindungen oder Kundeninhalte gelesen. Alle zusätzlichen Reproduktionen verwendeten vorübergehende synthetische Dateien. Diese wurden danach entfernt.

Die sechs Pakettests und sieben Installationsplantests bestanden. Zusätzliche Prüfungen fanden die nachstehenden Paketfehler, die von diesen Tests noch nicht erfasst wurden.

## Nachprüfung des Paketbaus

Alle drei Paketbefunde sind behoben. Acht gezielte Pakettests bestanden. Die folgenden Angaben zu den Erstfassungszeilen bleiben als nachvollziehbarer Verlauf erhalten.

- `paket_bauen.py:14,226` importiert und behandelt `PreparationError`. Der bestehende Zieltest bestätigt jetzt zusätzlich die Ausgabe ohne Traceback.
- `:29-58,130-131` lehnt bekannte private Laufzeitnamen und -ordner ab. Ausnahmen sind auf die ausdrücklich enthaltenen leeren Vorlagen begrenzt. Der Regressionstest prüft sechs falsch platzierte Datenpfade und erzwingt die Ablehnung vor `read_relative`.
- `:65-110` öffnet die Paketquelle und alle Elternkomponenten über verankerte Verzeichnisdeskriptoren mit `O_DIRECTORY` und `O_NOFOLLOW`. Quelldaten werden über denselben geöffneten Dateideskriptor gelesen und vor sowie nach dem Lesen auf Identität geprüft. Der neue Test weist den zeitweiligen Austausch der Blattdatei zurück. Eine zusätzliche unabhängige Reproduktion tauschte den Elternordner beim Leseaufruf gegen einen Symlink aus. Auch dieser Fall wurde mit `BuildError` abgewiesen.

Keine privaten Marker wurden bei der Nachprüfung als Paketinhalt übernommen. Der fest begrenzte Namensschutz ist weiterhin keine perfekte Erkennung persönlicher Inhalte in beliebigem Text.

## Historische Paketbefunde

### 1. Bug: Zielkonflikt entgeht der Fehlerbehandlung

**Stellen der Erstfassung:** `scripts/paket_bauen.py:123,145`.

`destination_path` aus dem Clientvorbereiter wirft bei einem vorhandenen Ziel `PreparationError`. Die Fehlerbehandlung des Paketbauers fängt diesen Typ nicht. Ein synthetisch vorhandener Zielordner führte daher zu Exit 1 mit Python-Traceback. Vorhandene Dateien blieben erhalten.

**Erwartet:** Verständliche behandelte Konfliktmeldung ohne Traceback, weiterhin keine Änderung.

**Kleinster Fix:** `PreparationError` importieren und behandeln. Bestehenden Zielschutztest um die Abwesenheit eines Tracebacks ergänzen.

### 2. Bug: Bekannte private Laufzeitdateien unter allgemein werden eingepackt

**Stellen der Erstfassung:** `scripts/paket_bauen.py:35-37,55-62`. Dokumentationsaussage: `docs/paketbau.md`, Ausschluss von Profilen.

Synthetisch wurden `allgemein/profil.md` mit einem privaten Marker und `allgemein/pfade.json` mit einem lokalen Pfadmarker angelegt. Beide erschienen anschließend im ermittelten Paketinhalt und damit im Manifest. Die bisherige Namensprüfung erkennt einige Geheimnisdateien, aber diese bekannten privaten Laufzeitdateien nicht. Der vorhandene Test kontrolliert lediglich den aktuellen tatsächlichen Quellbaum und deckt Fehlplatzierungen nicht ab.

**Erwartet:** Bekannte private Laufzeitdateien außerhalb der ausdrücklich erlaubten Vorlagen werden vor dem Lesen abgewiesen.

**Kleinster Fix:** Bekannte private Dateinamen beziehungsweise Verzeichnisse aus dem lokalen Datenvertrag abweisen. Ausnahmen nur für konkrete mitzuliefernde leere Vorlagen vorsehen. Mit synthetischen falsch abgelegten Dateien testen.

Dies ist keine Forderung nach perfekter Erkennung von Geheimnissen in beliebigem Freitext. Der Paketbau darf nur einen klar benannten Quellen- und Namensschutz versprechen. Eine Inhaltsprüfung aller möglichen persönlichen Daten ist damit nicht belegt.

### 3. Bug: Konkurrenzwechsel kann die Symlinkprüfung umgehen

**Stelle der Erstfassung:** `scripts/paket_bauen.py:71-79`.

Die Quelldatei wird vor `Path.read_bytes()` auf Symlinks und Identität geprüft. Der eigentliche Leseaufruf öffnet sie danach erneut über den Pfad.

**Konkrete Reproduktion:** In einem ausschließlich synthetischen Paket wurde genau beim Leseaufruf die reguläre Kerndatei umbenannt, am ursprünglichen Namen ein Link auf eine externe Markerdatei angelegt und nach dem Lesen wieder die ursprüngliche Datei zurückbenannt. Die Vorher-/Nachher-Identität war dadurch gleich. `source_snapshot()` las `SYNTHETIC_PRIVATE_MARKER` außerhalb des Pakets und akzeptierte ihn als Inhalt der Kerndatei.

**Erwartet:** Keine Inhalte über einen zwischenzeitlich ausgetauschten Symlink lesen und als Paketquelle übernehmen.

**Kleinster Fix:** Quelldatei mit `O_NOFOLLOW` öffnen und Daten sowie Identität über denselben Dateideskriptor prüfen. Für dieselbe Garantie bei ausgetauschten Elternordnern die Komponenten mit verankerten Verzeichnisdeskriptoren und `O_NOFOLLOW` durchlaufen. Ein bloßer weiterer Pfadcheck beseitigt das Zeitfenster nicht.

Die Reproduktion setzt einen gezielten konkurrierenden Austausch voraus. Gegen ruhende Symlinks schützt die bisherige Prüfung bereits. Diese beiden Aussagen dürfen im Nachweis nicht verwechselt werden.

## Bereits bestandene Paketprüfungen

- Exakte Skript-Allowlist mit `einrichten.py`, `profil_transfer.py`, `pruefe_konfiguration.py` und `pruefe_register.py`. Entwicklungs- und Loaderwerkzeuge wurden nicht automatisch übernommen.
- Die vier Laufzeitskripte starteten aus dem erzeugten Paket mit `--help`. Ihre benötigten lokalen Helferimporte sind damit vorhanden.
- Das Manifest verzeichnet exakt die tatsächlich erzeugten Dateien außer sich selbst. Alle geprüften SHA256-Werte stimmen mit den Paketdateien überein. Pfade sind relativ.
- `AGENTS.md` und `CLAUDE.md` stammen aus derselben Kernquelle und enthalten die angepassten lokalen Referenzpfade.
- Vorschau und Ablehnung schrieben nichts. Ein nach der Vorschau geänderter Quellbestand führte zum Abbruch.
- Vorhandene Ziele wurden inhaltlich nicht verändert. Die finale Übernahme verwendet die gemeinsame Betriebssystemoperation ohne Überschreiben.
- Ruhende verschachtelte Symlinks sowie eine synthetische `.env` wurden abgewiesen.

## Installationsplan

Die sieben Tests decken den frischen Plan, Wiederholbarkeit, bereits vorhandene fremde Regeln und Skills, Runtime- und Elternpfadkonflikte, Symlinks, explizite Clientordner, abweichende Umgebungswerte und ungültige Konfiguration ab. Alle bestanden.

Eine zusätzliche Prüfung blockierte `Path.read_text` und `Path.read_bytes` während `plan()`. Der Plan wurde trotzdem mit zwei Regeln und zehn Skillzuordnungen erstellt. Dies bestätigt für diesen Aufruf die ausschließliche Metadatenprüfung. Reale Profildaten oder Clientkonfigurationen wurden nicht benötigt.

Der Plan zeigt vorhandene Clientmetadaten ausdrücklich als inhaltlich und funktional ungeprüft. Eine erfolgreiche Planung ist weder Installation noch Clientabnahme. Es wurde keine aktive Clientdatei oder Verknüpfung verändert.

### Empfehlung: Gleiche geplante Ziele vor einer Installation zusammenführen

**Stellen:** `scripts/installationsplan.py:113-115,129-131`.

Bei `--claude-config-dir <synthetisches-home>/.agents` liegen die fünf geplanten Claude-Skillziele auf denselben fünf Zielen wie die Codex-Skilllinks. Der Plan enthält zehn Einträge für fünf verschiedene Pfade und keine Konflikte. Beide Seiten nennen dieselbe Quelle.

Noch entsteht daraus keine Schreibwirkung. Ein späterer Installer muss identische Operationen deduplizieren oder diese Konstellation ausdrücklich als Konflikt behandeln. Der reine Vorabplan sollte den gemeinsam genutzten Zielpfad zumindest kenntlich machen.

### Empfehlung: Zulässige Überschneidung der Clientordner festlegen

**Stellen:** `scripts/installationsplan.py:75-90,123-124`.

Ein explizites `--codex-home <paths.profile>` wird akzeptiert. Der Plan enthält dann `<paths.profile>/AGENTS.md` und meldet keine Konflikte, sofern die Datei noch fehlt. Die gemeinsame Konfigurationsvalidierung hält ihre vier Ablagebereiche getrennt, bezieht die zusätzlichen Clientordner jedoch nicht ein.

Der Plan verändert das Profil nicht. Vor einem schreibenden Installer muss ausdrücklich festgelegt werden, ob solche Überschneidungen zulässig sind. Andernfalls dieselben Schutzgrenzen auch für die Clientziele anwenden. Eine vorhandene Datei bleibt bereits heute ein Konflikt.

## Abschließende Verifikation

Die finale Fassung besteht alle 69 Tests der vorhandenen Testsuite, darunter acht Pakettests und elf Installationsplantests. Aufruf: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q`. Keine aktive Installation oder neue Loaderprobe war Teil dieser Prüfung.


## Nachprüfung des Installationsplans

Die überarbeitete Fassung besteht zehn Tests. Doppelte geplante Ziele einschließlich Mac-Normalisierung, überlappende Claude-/Codex-Konfigurationsordner, System- und Benutzerwurzel sowie ungeklärte Umgebungsabweichungen werden nun abgewiesen. Die beiden ursprünglichen Empfehlungen sind damit überwiegend umgesetzt.

### Behobener Bug 4: Separater Codex-Skillordner fehlte in der Bereichsprüfung

**Stellen:** `scripts/installationsplan.py:98-109` und `:145`.

Die Bereichsprüfung bezieht die ausgewählten Claude- und Codex-Konfigurationsordner ein. Codex legt seine Skilllinks jedoch getrennt unter `home/.agents/skills` ab. Diese Basis wird nicht auf Überschneidung mit Quellcode, Runtime, Profil oder Ausgabe geprüft.

**Konkrete Reproduktion:** Eine synthetische bestätigte Konfiguration mit `clients=['codex']` und `paths.profile='~/.agents'` erzeugt weiterhin `conflicts=[]`. Alle fünf geplanten Skilllinks liegen dann innerhalb des privaten Profilbereichs. Derselbe Fall wurde jeweils mit `paths.source`, `paths.runtime` und `paths.output` statt Profil reproduziert.

**Erwartet:** Dieselbe Trennung auch für den tatsächlichen Skillzielordner. **Beobachtet:** Die neu zugesagte Bereichstrennung lässt diesen zweiten Codex-Pfad aus.

**Kleinster Fix:** `home/.agents/skills` bei ausgewähltem Codex in dieselbe Überschneidungsprüfung aufnehmen. Tests für die vier Bereiche und normalisierte Pfadaliase ergänzen. Es wurde weiterhin nichts installiert oder in aktive Konfigurationen geschrieben.

**Nachprüfung:** `scripts/installationsplan.py:112-119` prüft die tatsächliche Basis `home/.agents/skills` gegen alle vier Ablagebereiche und ausgewählte Clientordner. Der Regressionstest `tests/test_installationsplan.py:136-148` umfasst alle vier Bereiche und die Schreibweisen `.agents` sowie `.AGENTS`. Er und die gesamte Testsuite bestanden. Dieser Befund ist geschlossen.
