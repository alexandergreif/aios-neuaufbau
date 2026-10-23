# Einrichtungsstatus

`scripts/setup_status.py` prüft die lokale Dateieinbindung eines bestätigten Profils rein lesend. Das Skript und sein sicherer Lesehelfer liegen auch im gebauten Runtime-Paket unter `scripts/` und können von dort ohne Zugriff auf das Quellpaket gestartet werden. Der Aufruf nutzt dieselben Ortsangaben wie der Installer:

```sh
python3 scripts/setup_status.py --config /pfad/zum/profil/pfade.json --home /pfad/zum/home
python3 scripts/setup_status.py --config /pfad/zum/profil/pfade.json --home /pfad/zum/home --json
```

Bei neuen Installationen stehen die bestätigten Clientorte im technischen `bestand.json`. Sie müssen nicht erneut angegeben werden. Optionale Angaben über `--codex-home` und `--claude-config-dir` müssen dazu passen. Beim rein lesbaren Altbestand ohne diese Datei werden die früher verwendeten Ortsangaben weiterhin benötigt. Der Statuscheck liest die bestätigte Pfadkonfiguration (`pfade.json` bei der Sprache `de`, `paths.json` bei `en`), das Runtime-Manifest, die zugehörigen Paketdateien, die berechneten globalen Regeldateien und Skillverknüpfungen sowie die eigenen technischen Zustandsdaten. Er liest weder das Profildokument noch `.env`, Ausgabeinhalte oder Kundendaten. Es werden keine Clients, Programme, Dienste oder Netzverbindungen gestartet und keine Protokolldateien geschrieben.

`present` mit Exitcode 0 bedeutet nur, dass die erfassten Dateien, Hashes und Links zur Installation passen. Bei fehlenden Dateien oder unvollständiger Einrichtung meldet der Check `missing` oder `limited` und Exitcode 1. Globale Paketfehler betreffen beide Clients. Fehlende Clientordner, Links und Regeldateien werden nur dem betroffenen Client zugeordnet. Die Ausgabe nennt je Client die Zahl intakter Skillverknüpfungen und ein konkretes Prüfobjekt mit nächstem Schritt. Modell, Anmeldung, Dienstverbindung und fachliche Funktion bleiben ausdrücklich ungeprüft. Diese Prüfungen brauchen eigene synthetische Funktionstests.

Die Ausgabe, auch mit `--json`, ist durchgehend englisch. Die Schlüssel sind `status`, `language`, `file_integration`, `functional_check`, `clients` (je Client `client`, `status`, `skills`, `integrity`, `models_services`) und `problems`. `functional_check` und `models_services` bleiben stets `unchecked`. `file_integration` und je Client `integrity` sind `checked`, solange der zugehörige Status `present` ist. Bei `missing` oder `limited` tragen sie denselben Wert. Nach bestätigter Deinstallation lautet der Status `uninstalled`, `file_integration` und `integrity` sind dann `missing`. `language` nennt die in der bestätigten Pfadkonfiguration festgelegte Sprache (`de` oder `en`).

Manifest- und Eigentumspfade werden vor Nutzung auf die erlaubte Paketstruktur und die daraus berechneten Clientziele begrenzt. Auch ein konsistenter Manifest- und Journaleintrag darf keine `.env`, Profile, Zugangsdaten oder Journale innerhalb der Runtime zum Prüfobjekt machen. Reguläre Dateien werden ohne blockierendes FIFO-Öffnen gelesen und vor sowie nach dem Lesen auf Identität geprüft. Das ist eine Prüfung der lokalen Einbindung, kein Audit aller Fähigkeiten und kein Ersatz für die spätere Funktionsabnahme.

Eine offene, unterbrochene oder unlesbare `operation.json` führt zu `limited`. Nach bestätigter Deinstallation lautet der Status `uninstalled`. Diese Zustände sind keine erfolgreich nutzbare Dateieinbindung und liefern Exitcode 1. Eine Folgeoperation wird bei ungeklärtem Teilstand nicht automatisch gestartet. [Vertrag für Update und Deinstallation](paketbetrieb.md).
