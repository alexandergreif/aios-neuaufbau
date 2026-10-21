# AIOS als Excalidraw

Stand: 21.10.2026. Die Übersicht beschreibt den lokalen Neuaufbau und trennt vorhandene Quellen, vorgeschlagene Struktur und offene Abnahme.

Die Zeichnungen halten den Stand vor dem Veröffentlichungsauftrag fest. Anschließend wurde das private GitHub-Ziel `alexandergreif/aios-neuaufbau` bestätigt. Für die Übertragung gilt jetzt die [kurze Installationsanleitung](../installation-kurz.md). Die gezeichnete neue Quellstruktur bleibt ein Vorschlag.

- [Gesamte editierbare Zeichenfläche](AIOS-gesamt.excalidraw): vier zusammenhängende Ansichten.
- [System und Fähigkeiten](01-system.excalidraw): Auftrag, Clients, gemeinsame Regeln, alle 21 vorhandenen Skillquellen, Kontext, Dienste und Ergebnisse.
- [Ordner im Vergleich](02-ordner.excalidraw): ursprüngliches AIOS, heutiger Neuaufbau und vorgeschlagene GitHub-Struktur.
- [Installation](03-installation.excalidraw): Runtime, Profil, Ergebnisse, Projekte und globale Clientanbindung.
- [Zweiter Mac](04-zweiter-mac.excalidraw): vorgeschlagener GitHub-Transfer und Reihenfolge der Betriebsabnahme.

Die gleichnamigen PNG-Dateien dienen als Vorschau. Die Excalidraw-Dateien lassen sich in Excalidraw öffnen und weiterbearbeiten. Die Gesamtdatei enthält alle vier Ansichten in einer Zeichenfläche. Jede Einzeldatei ist separat lesbar.

[Umschaltbare lokale Vorschau](index.html): HTML-Datei zusammen mit den PNG-Dateien im selben Ordner behalten.

## Prüfung der Darstellung

Alle fünf Excalidraw-Dateien sind gültiges JSON mit eindeutigen Element-IDs und wurden mit dem Renderer des bereitgestellten Skills gerendert. Die vier Einzelansichten wurden visuell geprüft. Zwei Beschriftungen wurden nachgeschärft und die betroffenen Ansichten sowie die Gesamtdatei erneut gerendert. Alle 21 vorhandenen Skillnamen sind in der Systemansicht enthalten. Alle lokalen Verweise dieser Begleitdatei wurden auf vorhandene Ziele geprüft. Die HTML-Vorschau lädt alle vier Bilder ohne gemeldeten Konsolenfehler. Die Gesamtdatei enthält 241 Elemente.

Für den bereitgestellten Skill wurden seine Python-Renderabhängigkeiten in dessen lokaler `.venv` und Chromium im Playwright-Cache eingerichtet. Der Renderer nutzt die im Skill vorgegebene Excalidraw-Version 0.18.0. Es wurden keine aktiven AIOS- oder Clientkonfigurationen verändert.

## Was die Darstellung belegt

Der Neuaufbau enthält 21 Skillquellen unter `allgemein/skills/`. Das sind vorhandene Quellen, keine Behauptung vollständiger Funktionsfähigkeit. Der Installer, Update und Deinstallation sind implementiert. Der Projektplan dokumentiert 145 bestandene synthetische Dateitests. Diese Zahl stammt aus dem vorhandenen Prüfbericht, sie wurde für die Zeichnung nicht erneut erhoben. Die tatsächliche Betriebsabnahme und die angemeldeten Modelltests auf dem zweiten Mac stehen aus.

Der heutige Neuaufbau ist ein lokaler Vorbereitungsordner ohne eigenes Git-Repository. Die zusätzlichen sichtbaren Bereiche `claude-code/`, `codex/`, `allgemein/verbindungen/`, `docs/einrichtung/` und `docs/entwicklung/` sind Strukturvorschläge. Eine konkrete Zuordnung der bisherigen Dateien und eine Prüfung der betroffenen Imports, Tests und Links fehlen vor einem Umbau.

Die Installation nutzt derzeit globale Regeldateien und Skillverknüpfungen. Die Grafik behauptet keine native Plugininstallation des Neuaufbaus. Vorhandene globale Regeldateien führen aktuell zu einem Konflikt. Ein markierter verwalteter AIOS-Abschnitt ist ein noch nicht implementierter Vorschlag.

## Über GitHub auf den zweiten Mac

Das bestätigte private Ziel ist `alexandergreif/aios-neuaufbau`. Der Veröffentlichungsauftrag liegt vor. Ein vollständiger Sync des bestehenden privaten AIOS-Ordners ist dafür nicht vorgesehen.

1. Quellstruktur zuordnen und einen sauberen Veröffentlichungsumfang zusammenstellen. Gemeinsame Regeln, Skills, leere Vorlagen, Code, Tests und bereinigte Dokumentation aufnehmen.
2. Profil, Wissen, Zugangsdaten, Anmeldespeicher, lokale Konfiguration, Zustandsdaten, Kundeninhalte und Ergebnisdateien ausschließen. Nicht blind den gesamten Arbeitsordner oder seine alte Historie übernehmen.
3. Geprüften Stand im gewählten Repository veröffentlichen und durch Commit-ID oder Tag festhalten. Den Clone-Befehl nennt die kurze Installationsanleitung.
4. Auf Mac 2 diesen Stand frisch klonen. Python- und Clientversionen erfassen. Lokale Pfade neu bestätigen.
5. Den Paketbetrieb zuerst im eigenen Test-Home samt eigenen Clientordnern prüfen. Bei Codex reicht ein anderes `CODEX_HOME` nicht, weil globale Skills unter `Home/.agents/skills` liegen.
6. Installation, Dateistatus, Update, Deinstallation, Konflikt und Abbruch prüfen. Fremde Marker, Profil und Ausgabe müssen erhalten bleiben.
7. Beide Clients auf Mac 2 nativ anmelden. Die sechs vorbereiteten synthetischen Modellfälle je Client ausführen und echte Antworten bewerten.
8. Dienstanbindungen einzeln mit Verbinden, typischem Aufruf, Trennen und Fehlerfall abnehmen. Erst nach erfolgreicher Testabnahme die vorgesehenen normalen Pfade einrichten.

`git pull` aktualisiert den Quellcode. Eine bereits installierte Runtime wird dadurch nicht automatisch aktualisiert. Dafür ist der AIOS-Updateablauf zuständig. Ein Profiltransfer erfolgt separat und überträgt keine Zugangsdaten oder Mac-spezifischen Pfade.

Die vorhandene [Abnahmeanleitung](../abnahme-zweiter-mac.md) enthält die konkreten Installeraufrufe und das offene Testprotokoll. Diese Visualisierung hat keine Installation oder GitHub-Veröffentlichung ausgeführt.

## Quellen

| Aussage | Lokale Quelle |
| --- | --- |
| Maßgeblicher Umsetzungs- und Prüfstand | [Projektplan](../../.aios/PLAN.md), [Paketbetrieb-Testlauf](../../pruefungen/paketbetrieb-testlauf.md) |
| Gewählte Fähigkeiten und offene Abhängigkeiten | [Paketumfang](../../paketumfang-und-umsetzung.md), [Skillquellen](../../allgemein/skills/) |
| Zielpfade und getrenntes Profil | [Entscheidungsprotokoll, insbesondere 90](../../README.md), [Pfadkonfiguration](../pfadkonfiguration.md) |
| Paketinhalt und erzeugte Dateien | [Paketbau](../paketbau.md), [Builder](../../scripts/paket_bauen.py), [Paketregeln](../../scripts/paketregeln.py) |
| Globale Regeln und Skilllinks | [Erstinstallation](../erstinstallation.md), [Installationsplan](../../scripts/installationsplan.py) |
| Update, Eigentum und Deinstallation | [Paketbetrieb](../paketbetrieb.md) |
| Profil, Wissen und Transfergrenzen | [Profilreferenz](../../allgemein/referenzen/profil-und-wissen.md) |
| Testfolge auf Mac 2 | [Abnahmeanleitung](../abnahme-zweiter-mac.md), [Modellfälle](../../tests/verhalten/faelle.json) |
| Neue Quellstruktur | Vorschlag aus dem Gespräch, noch keine umgesetzte Migration |

Keine Kundenordner, privaten Profile, Zugangsdaten oder inhaltlichen Archive wurden für diese Darstellung gelesen. Die Bestandsansicht des ursprünglichen AIOS basiert auf Projektmetadaten, Arbeitsdateien und Verzeichnisnamen.
