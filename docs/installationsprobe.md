# Isolierte Erstinstallation mit echten Clients

`scripts/check_local_installation.py` führt den lokalen Erstinstaller in einem erfundenen Benutzerordner aus. Danach startet es Claude Code und Codex in einem leeren Projekt außerhalb der Runtime. Im Projekt liegen weder Regeldateien noch Skillverknüpfungen. Damit prüft der Lauf die vom Installer erzeugte globale Einbindung.

Die Probe verwendet ein erfundenes Profil und einen ungültigen Testschlüssel. Persönliche Anmeldungen werden weder gelesen noch kopiert. Die Clients laufen in der Betriebssystem-Sandbox aus [client-loader.md](client-loader.md). Nur der jeweilige lokale HTTP-Testserver ist erreichbar. Er antwortet absichtlich mit HTTP 400. Es entsteht keine Modellantwort.

## Prüfumfang

1. Erstinstallation mit bestätigter synthetischer Konfiguration, beiden Clients und einem neuen Runtimeordner.
2. Integrität der installierten Dateien anhand des Paketmanifests. Testprofil, Testschlüsseldatei und Pfadkonfiguration bleiben bytegleich.
3. Wiederholte Erstinstallation wird als Konflikt abgelehnt.
4. Vollständiger globaler Regelkern und reguläre Skillbeschreibungen werden von beiden Clients geladen. Der nur ausdrücklich aufzurufende Auftragshelfer fehlt in der automatischen Auswahl.
5. Jeder installierte Skill wird ausdrücklich aufgerufen. Sein vollständiger Anweisungstext muss die native Verarbeitung bis zum lokalen Testserver durchlaufen.
6. Entfernen der jeweiligen globalen Regeldatei im Testordner muss die Regelladung verhindern. Der Client muss dabei weiterhin bis zur vorgesehenen Prüfstelle kommen.
7. `ls -l` der echten Skillverknüpfungen vor und nach dem Lauf muss identisch sein.

Claude startet in dieser Probe mit `--setting-sources user,project`. Nur so werden die gerade im erfundenen Benutzerordner installierten Regeln und Skills berücksichtigt. Die frühere reine Projektprobe verwendet weiterhin `project`. Hooks, automatische Erinnerungen und externe MCP-Server sind im Test deaktiviert.

## Aufruf

Aus dem Quellordner mit ausdrücklich gewählten Clientprogrammen:

```sh
python3 scripts/check_local_installation.py \
  --codex /absoluter/pfad/zu/codex \
  --claude /absoluter/pfad/zu/claude \
  --evidence-dir /absoluter/neuer/belegordner
```

Der Belegordner muss neu sein. Er enthält `installation.json` mit Paketprüfsummen, Clientpfaden, Versionen, Prüfergebnissen und synthetischem Installationsprotokoll sowie die beiden `ls`-Belege. Temporäre Installation und Testserver werden anschließend entfernt. Ein Lauf mit `passed: false` gilt nicht als Nachweis.

## Aussagegrenze

Diese Probe zeigt Installation und native Ladung, keine erfolgreiche Aufgabenbearbeitung durch ein Modell. Sie prüft weder Anmeldungen noch externe Dienste oder eine Installation auf einem zweiten Mac. Die separate unabhängige Installerprüfung muss ebenfalls abgeschlossen sein. Ein erfolgreich geladener Skill ist noch keine abgenommene Fachfunktion.

## Lokaler Nachweis vom 20.10.2026

Der frühere Lauf in `.aios-test-installation-20261020-setup/installation.json` war erfolgreich. Codex 0.162.1 und Claude Code 2.1.300 luden jeweils den vollständigen globalen Regelkern und alle 21 Skilltexte. Beide Negativkontrollen bestanden. Die Wiederholungsinstallation wurde abgewiesen, die Paketprüfsummen passten und die echten Skillverknüpfungen waren vor und nach dem Test bytegleich aufgelistet. Der installierte Statuscheck lief aus einem Arbeitsordner außerhalb der Runtime mit Exitcode 0. Testprofil und Testschlüsseldatei blieben unverändert.

Dieser Nachweis entstand vor dem neuen Eigentumsstand für Update und Deinstallation. Er belegt den damaligen Quellstand. Seit Entscheidung 118 werden hier keine weiteren nativen Clientproben ausgeführt. Die aktuelle Betriebsfassung wird mit synthetischen Dateitests geprüft, ihre echte Clientabnahme erfolgt gemeinsam auf dem zweiten Mac.

Der Beleg enthält zusätzlich Prüfsummen der Installer- und Testquellen. Sie blieben während des Laufs unverändert. Spätere Änderungen müssen gegen diesen konkreten Prüfstand eingeordnet werden. Die Belege gehören zur lokalen technischen Prüfung und werden nicht automatisch veröffentlicht.

Der Lauf enthält die neue gemeinsame Paketpfadpolicy und die Renderer-Kopien. Er prüft den Erstinstaller mit fertiger synthetischer Konfiguration. Die vorgeschaltete interaktive Profileinrichtung ist separat über den Shell-Einstieg einschließlich Abbruch und Fortsetzung geprüft: [Setup-Review](../pruefungen/setup-review.md). Die Renderer-Funktion ist separat mit synthetischen Inhalten geprüft: [Renderer-Review](../pruefungen/renderer-review.md). Eine visuelle oder angemeldete fachliche Abnahme folgt daraus nicht.
