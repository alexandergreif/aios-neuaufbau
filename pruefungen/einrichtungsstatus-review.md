# Unabhängige Prüfung des Einrichtungsstatus

Stand: 20.10.2026. Gelesen wurden `scripts/einrichtungsstatus.py`, `tests/test_einrichtungsstatus.py`, `docs/einrichtungsstatus.md` und die verwendeten sicheren Pfadhelfer. Keine Produktionsdatei geändert. Zusätzliche Prüfungen verwendeten ausschließlich temporär installierte synthetische Homes und Marker. Diese wurden anschließend entfernt. Keine echten Profile, Zugangsdaten, Kundeninhalte, Clients oder Dienste wurden geöffnet.

## Ergebnis

Abschließender Stand: Alle fünf Befunde einschließlich des Geschwisterfalls eines fehlenden ganzen Clientordners sind behoben und unabhängig nachgeprüft. Vierzehn Status- und acht Pakettests bestehen. Keine offenen konkreten Befunde. Die folgenden Befunde und Zwischenstände dokumentieren den Prüfverlauf historisch. Der normale Status ist auf Dateieinbindung beschränkt und behauptet richtigerweise keine Fachfunktion. Fehlerfälle sind jedoch noch nicht zuverlässig begrenzt und je Client ausgewertet.

### 1. Ein einzelner Clientfehler verfälscht beide Statusangaben

**Stellen:** `scripts/einrichtungsstatus.py:163-213`, insbesondere `:187-201` und `:210-213`.

**Reproduktion:** Synthetische Zweiclientinstallation erstellen. Genau eine Skillverknüpfung unter `.claude/skills` entfernen. Alle Codex-Regeln und -Links unverändert lassen.

**Beobachtet:** Beide Clients werden als `fehlend`, Integrität `fehlend`, null Skills ausgegeben. Die allgemeine Meldung lautet nur „Runtime, Eigentumsdatei oder Einbindungsdatei fehlt“. Das tatsächlich fehlende Objekt und der nächste Schritt sind nicht erkennbar. Codex wurde nicht vollständig separat geprüft und wird trotzdem als fehlend eingeordnet.

**Kleinster Fix:** Gemeinsame Voraussetzungen wie Manifest, Runtime und Eigentumsstand getrennt prüfen. Danach Regeln und Links je Client vollständig prüfen und Fehler pro Client sammeln. Den Gesamtstatus aus den Teilständen ableiten. Den anderen Client weder ungeprüft als geprüft stehenlassen noch fälschlich auf fehlend setzen. Fehlerobjekt beziehungsweise relativen Paketpfad, Ursache und passenden nächsten Prüfschritt ausgeben, ohne Dateiinhalte oder Geheimnisse zu übernehmen.

**Regression:** Jeweils nur einen Claude- oder Codex-Link entfernen und den anderen Client korrekt unabhängig bewerten. Dazu eine gemeinsame Runtimebeschädigung, die beide betrifft.

### 2. FIFO blockiert den Statusprozess vor der Dateitypprüfung

**Stellen:** `scripts/einrichtungsstatus.py:26-33`.

**Reproduktion:** Nach synthetischer Installation `runtime/allgemein/regeln/kern.md` entfernen und am selben Ort eine FIFO mit `os.mkfifo` anlegen. Status-CLI mit einem kontrollierten Einsekunden-Timeout starten.

**Beobachtet:** Der Prozess erreicht die Dateitypprüfung nicht und wird wegen Timeout beendet. `os.open(..., O_RDONLY)` wartet bereits auf einen FIFO-Schreiber. Die `fstat`-Prüfung kommt zu spät.

**Kleinster Fix:** Dateien nicht blockierend und ohne Symlinkfolge öffnen, anschließend am geöffneten FD ausschließlich reguläre Dateien zulassen. Die gemeinsame Lesefunktion muss dieselbe Grenze für Konfiguration, Manifest, Journal und Paketdateien einhalten.

**Regression:** FIFO an mindestens einer manifestierten Paketdatei und einer JSON-Eingabe. Erwartet ist zeitnaher behandelter Fehler, kein hängender Prozess.

### 3. Ersetzte Datei wird als aktuelle Integrität bestätigt

**Stellen:** `scripts/einrichtungsstatus.py:31-42`, Auswertung `:187-190`.

**Reproduktion:** Während des ersten `os.read` der synthetischen globalen `CLAUDE.md` die gelesene Datei umbenennen und unter ihrem ursprünglichen Namen eine reguläre Datei mit `SYNTHETIC_FOREIGN_RULE` anlegen. Der offene FD liest weiterhin die ursprünglichen korrekten Bytes.

**Beobachtet:** Gesamtstatus `vorhanden`, obwohl am aktuellen Regelpfad die fremde abweichende Datei liegt. Die Prüfung der Elternhierarchie erkennt keinen Austausch der Blattdatei.

**Kleinster Fix:** Identität und Änderungsmerkmale des geöffneten Objekts vor und nach dem Lesen vergleichen. Am verankerten Eltern-FD abschließend prüfen, dass der aktuelle Blattname weiter auf denselben regulären Inode zeigt. Elternprüfung beibehalten. Eine danach erfolgende externe Änderung bleibt außerhalb eines abgeschlossenen Zeitpunktnachweises.

**Regression:** Gezielter Austausch während des Lesens muss `eingeschränkt` ergeben. Eine dauerhafte Änderung nach bereits vollständig abgeschlossener Prüfung ist ausdrücklich kein hier behaupteter Schutzumfang.

### 4. Relative Manifestpfade erlauben das Lesen bekannter privater Laufzeitdateien

**Stellen:** `scripts/einrichtungsstatus.py:70-90`, `:118-133`, `:184-186`. Dokumentation: Zusage, weder `profil.md` noch `.env` zu lesen.

**Reproduktion:** In einer synthetischen Runtime `.env` mit einem privaten Marker anlegen. Manifest und technisches Journal konsistent um diesen relativen Dateipfad ergänzen und den Manifesthash im Journal aktualisieren. Für den neuen Eintrag genügt der syntaktisch gültige Hash aus 64 Nullen. `read_file` während `inspect` protokollieren.

**Beobachtet:** `runtime/.env` wird tatsächlich gelesen. Erst danach führt der falsche Inhaltshash zum Status `eingeschränkt`. Ein Fehlerstatus nach dem Lesen wahrt die zugesagte Lesegrenze nicht.

**Einordnung:** Keine privaten Bytes wurden ausgegeben oder an einen Dienst gesendet. Es wurde auch kein Pfadausbruch über `..` oder einen Dateisymlink gezeigt. Der Fehler betrifft den Quellenumfang innerhalb der Runtime, sobald Manifest und Journal manipuliert beziehungsweise unzulässig erweitert sind.

**Kleinster Fix:** Manifestpfade vor Inhaltszugriffen auf den bekannten öffentlichen Paketumfang begrenzen. Die feste Laufzeitskript-Allowlist sowie der bereits im Paketbau definierte Schutz bekannter privater Dateinamen und Ordner mit seinen konkreten leeren Vorlagenausnahmen bieten den vorhandenen Vertrag. Keine perfekte Geheimniserkennung für beliebigen Freitext behaupten. Eine konsistente Änderung zweier lokaler Metadatendateien ist kein Herkunftsbeweis.

**Regression:** `.env`, private Profil-/Registerdateien und nicht erlaubte Laufzeitskripte im Manifest müssen vor dem betreffenden `read_file`-Aufruf abgewiesen werden. Erlaubte leere Paketvorlagen bleiben zulässig.

### 5. NUL im Manifestpfad führt zu unbehandeltem Fehler

**Stellen:** `scripts/einrichtungsstatus.py:83-86`, Fehlerbehandlung `:206` und `:232`.

**Reproduktion:** Manifest und Journal einer synthetischen Installation konsistent um den JSON-Pfad `allgemein/invalid\u0000name.md` ergänzen, inklusive passendem Manifesthash. Status-CLI aufrufen.

**Beobachtet:** Exit 1 mit Python-Traceback und `ValueError: open: embedded null character in path`. Der ungültige Pfad passiert die Manifestvalidierung und gelangt bis `os.open`.

**Kleinster Fix:** NUL und weitere für den Pfadvertrag unzulässige Zeichen bereits im Manifestparser abweisen. Erwartete Eingabevalidierungsfehler verständlich behandeln, statt einen breiten Auffangblock für beliebige Programmierfehler einzuführen.

**Regression:** NUL-Pfad wird vor dem Dateizugriff abgewiesen, Ausgabe enthält keinen Traceback.

## Bestandene Prüfungen und Aussagegrenzen

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_einrichtungsstatus.py' -q`: acht Tests bestanden.
- Normale synthetische Installation ergibt Exit 0 und `vorhanden`, ausdrücklich `fachfunktion: ungeprüft` sowie `modell_dienste: ungeprüft`.
- Änderungen an Paketdateien und fehlende Dateien führen zu Fehlerstatus. Fehlende beziehungsweise umgebogene Skilllinks werden grundsätzlich erkannt.
- Manifesttraversierung mit `..`, doppelte Einträge und fremde Eigentumspfade werden abgewiesen. Die vorhandene Traversierungsregression bestätigt Abbruch vor Lesen des Außenpfads.
- Ruhende Blattdateisymlinks werden nicht verfolgt. Die gemeinsamen Elternhelfer öffnen komponentenweise ohne Symlinkfolge.
- Unvollständige Journalstände `installing` oder `failed` werden nicht als vorhandene vollständige Einrichtung gemeldet.
- Profil, synthetische Schlüsseldatei und vorhandene Ausgabemarker bleiben in den normalen Tests bytegleich. Das Produktionswerkzeug enthält keine Client-, Prozess-, Dienst- oder Netzwerkaufrufe und legt keine eigenen Protokolle an.

Korrekturen und gezielte Nachprüfung stehen aus. Das Werkzeug ist noch kein Nachweis einer Fachfunktion und keine Prüfung der Vollständigkeit des gesamten bestätigten AIOS-Umfangs.


## Erste Nachprüfung der Korrekturen

Zwölf Statuswerkzeugtests bestehen. Befunde 2 bis 5 sind korrigiert: `read_file` öffnet mit `O_NONBLOCK`, prüft den regulären Dateityp und vergleicht Identität sowie Änderungsmerkmale des geöffneten Objekts mit dem aktuellen Blattpfad. Die Manifestprüfung begrenzt Quellen auf öffentliche Paketbereiche, die feste Skriptliste und konkrete leere Vorlagenausnahmen. Bekannte private Namen werden vor ihrem Inhaltszugriff abgewiesen. NUL und weitere Steuerzeichen scheitern bereits im Manifestparser ohne Traceback. Die gezielten Regressionen für FIFO, Blattaustausch, konsistent manipuliertes Manifest/Journal und NUL bestehen.

Die clientgetrennte Prüfung erkennt jetzt einen einzelnen fehlenden Claude-Link, während Codex separat korrekt geprüft wird. Die Ausgabe benennt den betroffenen Skill und einen nächsten Schritt.

### Behobener Geschwisterfall zu Befund 1

**Stelle:** `scripts/einrichtungsstatus.py:217-220`, gemeinsame `created_directories`-Prüfung.

**Reproduktion:** Vollständige synthetische Zweiclientinstallation, danach den gesamten Ordner `.claude` in `.claude-moved` umbenennen. Codex bleibt vollständig unverändert.

**Beobachtet:** Erneut beide Clients `fehlend`, null Skills, mit der gemeinsamen Meldung „angelegter Ordner fehlt“. Die Datei-/Linkschleifen sind clientgetrennt, aber Clientordner stehen weiterhin im gemeinsamen Prüfblock.

**Kleinster Fix:** Clientbezogene angelegte Ordner nicht als gemeinsame Voraussetzung beider Clients behandeln. Deren Fehlen über die jeweilige Clientprüfung beziehungsweise zugeordnete Zielpfade auswerten. Gemeinsame Runtime-, Profilzustands- und Ausgabevoraussetzungen bleiben gemeinsam. Regressionen mit fehlenden vollständigen Claude- und Codex-Skillordnern ergänzen.


## Abschließende Nachprüfung und Runtime-Bündelung

Die gemeinsame Prüfung erzwingt nicht mehr die Existenz aller historisch angelegten Clientordner. Die zulässigen Eigentumspfade werden weiterhin validiert. Aktuelle Regeln und Skilllinks werden dagegen innerhalb des jeweiligen Clientblocks über sichere Elternpfade geprüft. Der Regressionstest `test_moved_client_directories_do_not_mask_other_client` bestätigt sowohl einen fehlenden gesamten Claude-Ordner als auch eine fehlende Codex-Skillbasis. Der jeweils intakte Client bleibt korrekt als vorhanden mit seinen tatsächlich intakten Links ausgewiesen.

Paketbau und Statusvalidator enthalten jetzt dieselbe feste Allowlist aus sechs Skripten: `einrichten.py`, `profil_transfer.py`, `pruefe_konfiguration.py`, `pruefe_register.py`, `einrichtungsstatus.py` und `sichere_dateien.py`. Die Aufnahme ist ausdrücklich begrenzt, keine automatische Übernahme des gesamten Entwicklungsverzeichnisses.

`test_bundled_status_runs_without_source_imports` startet das tatsächlich installierte Statusskript aus einem isolierten Arbeitsordner ohne `PYTHONPATH`. Hauptfall Exit 0 und ein umgebogener Claude-Skilllink mit Exit 1 wurden geprüft. Codex bleibt im Fehlerfall separat vorhanden. Damit sind die benötigten Runtimeimporte vorhanden und die Prüfung hängt nicht vom aktuellen Quellarbeitsordner ab.

**Unabhängig ausgeführte Tests:**

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_einrichtungsstatus.py' -q`: 14 Tests bestanden.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_paket_bauen.py' -q`: 8 Tests bestanden.

Die volle Suite wird parallel vom Hauptagenten ausgeführt und wurde hier nicht unnötig dupliziert. Exit 0 bleibt ein Dateiintegritätsnachweis für den erfassten Stand, kein Modell-, Anmelde- oder Fachfunktionsnachweis.
