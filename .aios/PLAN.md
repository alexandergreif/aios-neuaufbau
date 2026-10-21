# Plan: AIOS-Neuaufbau

Stand: 22.10.2026. Lokales Git-Repository. Privates Veröffentlichungsziel: `alexandergreif/aios-neuaufbau`.

## Ziel

Privates portables AIOS für Claude Code und Codex mit allen bestätigten Fähigkeiten und geprüftem Installationsablauf für einen zweiten Mac.

## Aktueller Stand

- Abnahme auf dem zweiten Mac am 21.10.2026 für Claude Code begonnen (Claude Code 2.1.306, Python 3.13.5). Native Ladung, sechs Modellfälle, Erstinstallation, Update 0.1.0-dev nach 0.1.1-dev, Konfliktfall und Deinstallation bestanden mit Hinweisen, unabhängig geprüft. [Modellfälle](../pruefungen/modelltests-mac2/README.md), [Betrieb](../pruefungen/betrieb-mac2/README.md). Regelkern bis 0.1.3-dev präzisiert: vollständiger Entwurf an den Prüfer, Nachprüfung durch neu gestarteten Prüfagenten, Ungeprüftes konkret nennen. Erste Testinstallation dabei regulär bis 0.1.3-dev aktualisiert. Codex auf 0.163.0 aktualisiert. Runde 4 belegt: genau ein Ergebnis, Nachprüfung durch neue Prüfagenten. Codex am 22.10.2026: Testinstallation, Anmeldung, native Ladung und sieben Fälle bestanden, drei mit Hinweisen ([Codex](../pruefungen/modelltests-mac2/codex/README.md)). Regel bis 0.1.5-dev: inhaltlich unveränderte Ausgabe der geprüften Fassung, Wortgleichheit als bekannte Grenze. Reale Update- und Deinstallationsprobe für Codex bestanden mit Hinweisen ([Codex-Betrieb](../pruefungen/betrieb-mac2/codex/README.md)). Nächster Schritt auf Mac 2: normale Einrichtung mit `beide` und echtem Profil, interaktiv durch Alexander. Mac 2 ist der private Laptop, deshalb keine Dienstanbindungen hier. Konnektoren auf dem Haupt-MacBook einrichten und testen.

- Veröffentlichung am 21.10.2026 abgeschlossen: [alexandergreif/aios-neuaufbau](https://github.com/alexandergreif/aios-neuaufbau), Privatsichtbarkeit bestätigt. Quellcommit `275599b` hochgeladen und frisch von GitHub geklont. 145 Tests erneut unter OS-Sperre erfolgreich, staged Geheimnisscan ohne Treffer. Isolierte Claude-Dateiinstallation aus dem Checkout: 21 Skilllinks, Status vorhanden. Wiederholung stoppt erwartungsgemäß am vorhandenen Profil. [Kurzanleitung](../docs/installation-kurz.md), [Transfernachweis](../pruefungen/github-transfer.md). Echte Mac- und Modellabnahme bleibt offen.

- Architekturvisualisierung fertig: vier Excalidraw-Ansichten für System, heutige und vorgeschlagene Quellstruktur, Installation und Test auf dem zweiten Mac. Gesamtdatei, PNGs und umschaltbare Vorschau vorhanden. Alle 21 Skillquellen dargestellt, JSON und Links geprüft, Einzelansichten gerendert und visuell geprüft. [Ergebnis und Quellen](../docs/architektur-bilder/README.md). Keine Strukturmigration oder GitHub-Veröffentlichung. Ziel-Repository und echte Mac-Abnahme bleiben offen.

- Auswahlrunde bis 115 konsolidiert und unabhängig geprüft. Entscheidung 116a legt angemeldete Modelltests auf den zweiten Mac. Protokoll in `../README.md`.
- Gemeinsamer Regelkern, Vorlagen, Einrichtung, Profiltransfer, Registerprüfung, Paketbau, Installationsplan und begrenzter Erstinstaller umgesetzt. Unabhängige Prüfungen dokumentiert. Aktives Setup unverändert.
- Rein lesender Statuscheck inklusive Helfer wird mit der Runtime gebündelt. Paketintegrität, globale Regeln und Skilllinks werden geprüft, Clientfehler getrennt ausgewiesen. Keine Gleichsetzung mit fachlicher Funktionsabnahme. [Review](../pruefungen/einrichtungsstatus-review.md).
- Grundlage vor dem neuen Paketbetrieb: 116 Tests grün. Damalige Installer- und Statusbefunde behoben und unabhängig nachgeprüft. [Installerreview](../pruefungen/erstinstallation-review.md).
- 21 Skillquellen vorhanden und in fünf Gruppen unabhängig geprüft. Sechs zusätzliche synthetische Modelltestfälle für den zweiten Mac vorbereitet.
- Frühere isolierte Erstinstallation inklusive installiertem Statuscheck und globaler Ladung von 21 Skills in beiden nativen Clients erfolgreich. Beide Negativkontrollen, Wiederholungskonflikt und unveränderte echte Skillverknüpfungen belegt. Lokaler HTTP-400-Testserver, keine Modellantwort. Beleg: `.aios-test-installation-20261020-setup/installation.json`. Dieser Lauf entstand vor den neuen Betriebsabläufen und bestätigt keine nachträglichen Codeänderungen.
- Gemeinsame Paketpfadpolicy ergänzt und unabhängig abgenommen. Private Ordner werden in Builder und Statuscheck einheitlich ausgeschlossen. `.env.example` nur als Datei zulässig. 40 gezielte Tests grün. [Architekturreview](../pruefungen/architektur-zwischenstand.md).
- Entscheidung 117 umgesetzt: Renderer-Kopien mit erweitertem Ressourcencheck, exklusiver Ausgabe, striktem JSON in Inhalt und Palette sowie ausdrücklicher Paletteneingabe. 16 gezielte Tests grün, unabhängig ohne offene technische Befunde nachgeprüft. Alte Skripthashes unverändert. Visuelle Abnahme offen. [Review](../pruefungen/renderer-review.md).
- Geführter Einstieg über `install.sh` verbindet Profilanlage und Installation mit getrennten Vorschauen und Statuscheck. Abbruch per Strg+C und tatsächliche Fortsetzung unabhängig geprüft, 29 gezielte Tests grün. [Review](../pruefungen/setup-review.md).
- Update und gezielte Deinstallation umgesetzt. Bestätigter Eigentumsstand und Operationsjournal sind getrennt. 145 Tests unter Betriebssystem-Sperre für echte AIOS-/Clientordner und Netzwerk grün. Vier unabhängige Reviewbefunde zu Manifestbindung, Zieltausch, laufender Konfliktprüfung und Installationsabschluss behoben und unabhängig geschlossen. 80 gezielte Tests und zusätzliche Crashproben unabhängig erfolgreich. Keine offenen technischen Befunde im geprüften Umfang. Echte Betriebsabnahme bleibt offen. [Review](../pruefungen/paketbetrieb-review.md), [Gesamtlauf](../pruefungen/paketbetrieb-testlauf.md).
- [Anleitung für den zweiten Mac](../docs/abnahme-zweiter-mac.md) vorbereitet. Test-Home zusätzlich zu eigenen Clientordnern zwingend, da Codex seine Skills unter Home/.agents/skills lädt. Profilimport folgt auf die Profileinrichtung. Beide Anleitungskorrekturen unabhängig nachgeprüft.

## Nächster Schritt

Umstieg auf dem Haupt-MacBook nach [docs/umstieg-haupt-macbook.md](../docs/umstieg-haupt-macbook.md): Quelle klonen, altes AIOS rein lesend inventarisieren, AIOS-eigene Teile sichern und beiseitelegen (nicht löschen), neu mit `beide` und echtem Profil installieren, prüfen, danach Dienstanbindungen einzeln einrichten und testen. MCP-Server, Plugins und Anmeldungen bleiben erhalten.

Auf dem zweiten Mac (privater Laptop) keine Dienstanbindungen. Dort ist die normale Einrichtung mit `beide` noch offen und kann jederzeit interaktiv nachgeholt werden.

## Grenzen

Alexander hat am 22.10.2026 entschieden, das AIOS auf dem Haupt-MacBook neu zu installieren und den Altbestand zu sichern. Inventur dort ist rein lesend. Verschieben, Installieren und Anmeldungen erst nach gezeigter Liste und Freigabe im jeweiligen Schritt. Nichts löschen, Backup bleibt lokal. MCP-Server, Plugins, Anmeldungen und fremde Clientkonfiguration nicht verändern. Keine Kundendaten lesen oder migrieren. Profilinhalte nur mit Alexanders Bestätigung übernehmen. Zugangsdaten nie in Chat, Repository oder Prüfberichte. Externe Schreibaktionen in Diensten nur mit konkretem Testauftrag. Push nur nach `alexandergreif/aios-neuaufbau` und nur auf Auftrag. Auf dem zweiten Mac keine Dienstanbindungen.
