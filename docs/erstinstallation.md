# Lokale Ersteinrichtung des Entwicklungsstands

`install.sh` startet ohne `--config` den geführten Einstieg. Der Dialog ist englisch und fragt zuerst die Sprache der Regeln und Skills ab, Vorgabe `en`. Mit `--language de` oder `--language en` entfällt die Frage. Danach werden Clientauswahl (`claude`, `codex`, `both`), Pfade und Profilangaben abgefragt. Nach der ersten Vorschau und `yes` wird das private Profil mit bestätigter Pfadkonfiguration gespeichert. Ein optionaler Blockbrain-Schlüssel wird verdeckt abgefragt und kann übersprungen werden. Anschließend zeigt der bestehende Installer die geplanten Änderungen und verlangt ein zweites `yes`. Nach erfolgreicher Installation folgt der rein lesende Statuscheck der Dateieinbindung.

```sh
sh install.sh
sh install.sh --home /pfad/zum/home --codex-home /pfad/zum/codex --claude-config-dir /pfad/zum/claude
```

Fehlende Programme für gewählte Clients werden anhand des `PATH` gemeldet. Der Einstieg installiert oder startet diese Programme nicht. Bei Abbruch vor der ersten Bestätigung wird kein Profil angelegt. Bei Abbruch vor der Installation bleibt das bestätigte Profil erhalten. Der Einstieg zeigt dann einen vollständig zitierten Aufruf zum Fortsetzen, einschließlich der übergebenen Ortsangaben.

Mit `--config` bleibt der bisherige Installer-Vertrag erhalten. Der Installer arbeitet dann mit einer bereits bestätigten Pfadkonfiguration im vorhandenen privaten Profilordner. `paths.source` muss auf dieses Quellpaket zeigen.

```sh
sh install.sh --config /pfad/zum/profil/pfade.json
sh install.sh --config /pfad/zum/profil/pfade.json --apply
```

`--home`, `--codex-home` und `--claude-config-dir` entsprechen dem rein lesenden Installationsplan und erlauben synthetische oder ausdrücklich gewählte Clientorte. Ohne `--apply` erscheint nur eine Vorschau. Mit `--apply` ist nach der Vorschau genau `yes` einzugeben. Konfiguration, Paketquellen und Vorabplan werden danach erneut geprüft. Konflikte oder ungeklärte Umgebungsabweichungen stoppen vor jedem Schreiben.

Die Runtime wird als neuer Ordner atomar angelegt. Ein fehlender Ausgabeordner wird erstellt, ein vorhandener bleibt samt Inhalt unverändert. Der Installer legt für gewählte Clients globale Regeldateien exklusiv an. Ihre Referenzlinks zeigen absolut auf die Runtime und ihre Konfigurationsangabe auf die lokale Pfadkonfiguration. Skillverknüpfungen zeigen auf `runtime/allgemein/skills/<name>` bei der Sprache `de`, auf `runtime/general/skills/<name>` bei `en`. Vorhandene Runtime, Regeln, Skills und die technische Eigentumsdatei werden nie ersetzt.

`profil/zustand/installation.json` (bei `en`: `state/` statt `zustand/`) erfasst Version, Clients, Runtime, Status und angelegte Dateien oder Links mit Hash beziehungsweise Ziel. Während der Einrichtung ist der Status `installing`, nach erfolgreicher Abschlussprüfung `installed`. Nach einem Fehler versucht der Installer, den bekannten Teilstand mit `failed` festzuhalten. Bei einem Journalfehler oder Stromabbruch kann die Datei weiterhin `installing` oder unvollständig sein. Dieses Erstjournal bietet keine atomare Zustandsaktualisierung und es gibt keine automatische Wiederherstellung.

Neue Installationen veröffentlichen zusätzlich `profil/zustand/bestand.json` als getrennten bestätigten Eigentumsstand. Darin stehen die geprüften Paketdateien und die tatsächlich gewählten Clientorte. Update und Deinstallation benötigen diesen Stand. Sie verwenden eine eigene `operation.json` und dieselbe profilbezogene Betriebssperre. Die bloße Liste angelegter Verzeichnisse im Erstjournal gibt keine Löschbefugnis. [Betriebsvertrag](paketbetrieb.md).

Andere Profildateien und `.env` werden nicht gelesen oder geändert. Verbindungseinstellungen, Dienste und Anmeldungen werden nicht eingerichtet, und kein Client wird gestartet.

Die Erfolgsmeldung ist englisch und lautet bewusst: „Development state with the skills currently present installed. Client and service function unchecked.“ Diese Ersteinrichtung ist weder ein Update noch eine Deinstallation und belegt nicht die Funktion des vollständigen AIOS.
