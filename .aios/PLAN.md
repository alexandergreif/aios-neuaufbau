# Plan: AIOS-Neuaufbau

Stand: 21.10.2026. Lokales Git-Repository. Privates Veröffentlichungsziel: `alexandergreif/aios-neuaufbau`.

## Ziel

Privates portables AIOS für Claude Code und Codex mit allen bestätigten Fähigkeiten und geprüftem Installationsablauf für einen zweiten Mac.

## Aktueller Stand

- Veröffentlichung am 21.10.2026 ausdrücklich beauftragt. Nutzer hat `alexandergreif/aios-neuaufbau` als neues privates Repository gewählt. Kurzanleitung für den isolierten Claude-Test ergänzt. 145 Tests erneut unter OS-Sperre erfolgreich, staged Geheimnisscan ohne Treffer. Upload und frischer Checkout werden geprüft.

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

Zunächst die vorgeschlagene GitHub-Struktur mit sichtbaren Bereichen `allgemein/`, `claude-code/` und `codex/` konkret zuordnen. Noch keine Strukturänderung oder Verschiebung. Entscheidung 119 zur manuellen Regelprüfung ist festgehalten. Die Einrichtungsanleitung und der vorgeschlagene verwaltete AIOS-Abschnitt benötigen später ihre gesonderte Umsetzung.

Gemeinsam auf dem zweiten Mac anhand der vorbereiteten Anleitung Paketstand übertragen, Pfade bestätigen und Installation, Update, Deinstallation sowie angemeldete Modellfälle prüfen. Update und Deinstallation zunächst nur im eigenen Test-Home. Entscheidung 118: echte Betriebs- und Modelltests nur dort. Weitere ausgewählte Fähigkeiten und technische Abhängigkeiten fehlen noch, ebenso Dienstanbindungen und die visuelle Rendererabnahme. Keine aktive Installation auf dem ersten Mac umstellen.

## Grenzen

Keine Kundendaten, Archive, Profile oder Zugangsdaten lesen oder migrieren. Keine aktive Installation oder globale Regeln ändern. Kein Browser, kein Atrio-Ausbau. Commit, Repositoryanlage und Push sind ausschließlich für den geprüften neuen Paketstand nach `alexandergreif/aios-neuaufbau` beauftragt. Keine hiesigen Testanmeldungen, Anbieteraufrufe oder weiteren nativen Clienttests. Synthetische Tests bearbeiten ausschließlich eigene Testdateien in isolierten Ordnern. Alte Installationsnachweise gelten nicht als Abnahme des Neuaufbaus.
