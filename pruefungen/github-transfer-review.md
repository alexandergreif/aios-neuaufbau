# Unabhängiger Review des GitHub-Transfers

Stand: 21.10.2026. Ziel: privates Repository `alexandergreif/aios-neuaufbau`.
Prüfmodell: GPT-6 Astra, high. Begrenzte Prüfung ohne weitere Delegation.

## Ergebnis

**Freigabe des geprüften Quellstands für den privaten Transfer. Keine belegten Veröffentlichungs- oder Portabilitätsblocker im geprüften Umfang.** Dies ist keine Abnahme der echten Installation, Modellfunktion oder Dienstanbindungen auf Mac 2.

Beim Prüfen war `main` noch ohne Commit und der Index leer. Ein Commit-Diff oder endgültiger Veröffentlichungsbaum lag deshalb nicht vor. Bewertet wurden das Git-Kandidateninventar und die vorhandenen Quellen. Der Hauptagent muss den tatsächlich gestagten Umfang mit diesem geprüften Umfang abgleichen. Repositoryanlage, Privatsichtbarkeit und Push wurden hier nicht überprüft oder ausgeführt.

## Belege

- Git-Inventar zuletzt 162 Kandidaten vor diesem Bericht. Keine Kandidaten unter `.aios-test*` oder `.aios-release`, keine Symlink-Kandidaten und keine Dateien mit den geprüften privaten Namen `pfade.json`, `credentials.json`, `secrets.json`, `.env`, `id_rsa` oder `id_ed25519`.
- `.gitignore:2` schließt `.env` und deren Varianten aus. Die leere Konfigurationsvorlage bleibt über `.env.example` zugelassen. `git check-ignore --no-index` bestätigt die Ausschlüsse für `.aios-test/`, `.aios-test-mac2/`, `.aios-release/`, `.env`, eine verschachtelte `.env.local`, `profil/pfade.json` und Python-Cachedateien.
- Begrenzter Musterscan der nicht ausgeschlossenen Textquellen: keine Treffer für die geprüften GitHub-, OpenAI- und AWS-Schlüsselformate oder private Schlüsselblöcke. Keine sensiblen Werte ausgegeben. Absolute Benutzerpfade fanden sich in historischen Dokumenten und Reviewbeispielen, nicht in den ausführbaren Paketquellen. Dieser Scan beweist keine vollständige Geheimnisfreiheit.
- `scripts/paketregeln.py:6` begrenzt die Runtime-Skripte ausdrücklich. `:10`, `:34` und `:48` sperren bekannte private Namen und Verzeichnisse, mit konkreten Ausnahmen für leere Vorlagen. Diese Runtime-Policy ist keine Git-Veröffentlichungsfilterung.
- `scripts/paket_bauen.py:80` und `:134` rein lesend aufgerufen: 71 Quelldateien, daraus 74 Runtime-Dateien einschließlich Manifest und generierter Regeln. Alle Manifest-Hashes stimmen, 21 Skills enthalten. Es wurde kein Paketverzeichnis geschrieben.
- AST-Abgleich der Python-Importe: keine fehlenden lokalen Helfer im erzeugten Runtime-Inhalt. Die Skripte im Quellstand benötigen für ihre Importe nur Standardbibliothek und mitgelieferte Module. Dies belegt keine externen Fähigkeiten einzelner Skills oder Renderer.
- `install.sh:3` ermittelt den eigenen Ordner unabhängig vom Arbeitsverzeichnis und zitiert den Pfad. `scripts/einrichten.py:148` schlägt den tatsächlichen Quellordner vor. Die drei Zielbereiche werden lokal unter dem gewählten Home aufgelöst. Kein fest eingebauter Benutzerpfad des ersten Macs erforderlich.
- `scripts/einrichten.py:96` enthält den macOS-Pfad für exklusives Umbenennen. Dessen echte Ausführung auf Mac 2 bleibt Bestandteil der dortigen Abnahme.
- Sechs Hilfeaufrufe mit deaktiviertem Bytecode-Schreiben, jeweils Exitcode 0: `sh install.sh --help` sowie `einrichten.py`, `installationsplan.py`, `einrichtungsstatus.py`, `aktualisieren.py` und `deinstallieren.py` mit `--help`. Keine Clientstarts oder Installation ausgeführt.

## CLI-Vertrag für den ersten Claude-Test

- `scripts/setup.py:37` reicht Aufrufe mit `--config` an den bestehenden Installer weiter. Ohne Konfiguration führt `:41` den Profildialog aus, `:58` die getrennte Installationsbestätigung und `:69` den Dateistatuscheck.
- `scripts/einrichten.py:143` akzeptiert die Dialogauswahl `claude` und setzt ausschließlich `claude-code`. Die erste Bestätigung liegt bei `:166`, die optionale verdeckte Schlüsseleingabe bei `:170`.
- `scripts/installationsplan.py:90` berücksichtigt den ausdrücklichen Claude-Konfigurationsordner. Bei reiner Claude-Auswahl wird keine Codex-Skillbasis geplant. Vorhandene Regel- und Skillziele sind Konflikte, siehe `:167`.
- `docs/installation-kurz.md:15` erzeugt einen separaten vorhandenen Test-Home. Der Aufruf bei `:16` übergibt ihn und einen darin liegenden Claude-Ordner. Die Dialoganweisung bei `:19` passt zum Parser und hält Profil, Runtime und Ausgabe im Test-Home.
- Der native Claude-Aufruf bei `docs/installation-kurz.md:26`, seine Anmeldung und der anschließende Modellfall wurden ausdrücklich nicht ausgeführt. Aus der passenden Installer-CLI folgt kein Nachweis des aktuellen nativen Clientverhaltens.
- Update und Deinstallation verlangen laut tatsächlich geprüften Hilfeausgaben `--config` und `--home`. Das entspricht `docs/abnahme-zweiter-mac.md:43`. Die gespeicherten Clientbindungen und echten Betriebsabläufe wurden hier nicht erneut getestet.

## Nicht blockierende Hinweise

**suggestion:** `.gitignore:15` schützt nur aufgezählte lokale Verzeichnisse. Die rein hypothetischen Namen `profile/profil.md`, `private/credentials.json`, `secret.key` und `.aios-release-mac2/marker` sind nicht ausgeschlossen. Solche Dateien sind im geprüften Kandidatenbestand nicht vorhanden. Falls künftig andere Ablageorte verwendet werden, deren Ausschlüsse ergänzen und den Commit-Inhalt erneut prüfen.

Historische Aussagen wie „noch kein GitHub-Repository“ in `docs/abnahme-zweiter-mac.md:9` und „kein Git-Repository“ in `.aios/PLAN.md:3` werden nach dem Transfer überholt sein. Den aktuellen Arbeitsstand beim Veröffentlichungsabschluss nachführen. Dies ist kein Fehler im Installer.

## Abgrenzung und überprüfter Stand

Grundlage waren `.aios/PLAN.md`, der Kern aus `.aios/NOTIZEN.md`, die Mac-Abnahmeanleitung, Setup, Profileinrichtung, Installationsplan, Paketregeln, Builder und relevante Installeraufrufe. Vorhandene Setup-, Paket-/Planungs- und Mac-Anleitungsreviews wurden berücksichtigt. README-Einstieg, neue Kurzanleitung und überarbeitete Git-Ausschlüsse waren beim Schlussabgleich vorhanden. Die parallele Arbeit daran wurde nicht verändert.

Keine Gesamt-Testsuite oder neue Dateitestinstallation gestartet. Keine `.aios-test*`- oder `.aios-release`-Inhalte, realen Profile, aktiven Clientordner oder Kundenordner gelesen. Keine Dienste, nativen Clients, Browser oder Netzverbindungen gestartet. Keine Commits oder Pushes. Ausschließlich dieser Bericht wurde geschrieben. Bilder und sonstige Binärinhalte wurden nicht auf versteckte Inhalte untersucht.

Offen bleiben die echte Mac-Installation, native Ladung im aktuellen Stand, Anmeldung, sechs Modellfälle, Update und Deinstallation auf Mac 2, Dienstanbindungen und visuelle Rendererabnahme. Frühere grüne Tests und Loaderbelege sind historische Nachweise, keine hier wiederholten Abnahmen. Diese offenen Tests verhindern die Übertragung des vorbereiteten Quellstands nicht.

SHA256 der zentral geprüften Dateien:

| Datei | SHA256 |
| --- | --- |
| `scripts/setup.py` | `b9cf3c6d9a115d8c033f11b023459909786249141d741fc8a275970ff485a189` |
| `scripts/einrichten.py` | `b3d39a83a4541949c25e648669ad99bb81fc814e816256fbc0823b92c4cd878b` |
| `scripts/installationsplan.py` | `6525b70c9cd2c6bcb5e13abd155e406fae822c9c8ab3cdfcab8da0a7de3027b9` |
| `scripts/paketregeln.py` | `20396a1da9168114b2e511fb369a70d9324721484d824e6a9665aebecd428e93` |
| `.gitignore` | `aca1ad64c124a02a240784e37f84bf7a69e18c0ae4bf427cda72cd031928fe8e` |
| `docs/installation-kurz.md` | `bb6879df15271d0159d756ad802247b986fc0359562c5f245e98da4322be33b3` |
