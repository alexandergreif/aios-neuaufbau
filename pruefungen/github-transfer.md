# Prüfung vor dem GitHub-Transfer

Stand: 21.10.2026. Auftrag: aktuellen Neuaufbau im neuen privaten Repository `alexandergreif/aios-neuaufbau` für den zweiten Mac bereitstellen.

## Umfang

Veröffentlicht werden gemeinsame Quellen, Installer und Helfer, Tests, leere Vorlagen, Dokumentation, technische Reviews und die Excalidraw-Übersicht. Die bestehende Quellstruktur bleibt erhalten. Der geplante spätere Ordnerumbau ist nicht Bestandteil dieses Transfers.

Lokale Testordner, Release-Arbeitsdateien, Python-Caches, persönliche Profile, Runtime, Ergebnisse und Zugangsdaten werden nicht aufgenommen. Der neue Git-Verlauf beginnt mit dem geprüften Quellbestand. Die Historie des ursprünglichen privaten AIOS und frühere Paket-Repositories werden nicht übernommen.

## Nachweise

- Gesamtprüfung: `python3 -m unittest discover -s tests -q` mit Python 3.13.16 unter macOS `sandbox-exec`.
- Das Sandboxprofil sperrte Netzwerk sowie Lesen und Schreiben in den echten AIOS-, Profil-, Client- und Kundenordnern. Alle Unterprozesse erbten diese Sperren.
- Ergebnis: 145 Tests in 19,625 Sekunden, `OK`, Exitcode 0.
- Geheimnisscan: `gitleaks git --pre-commit --staged --redact --ignore-gitleaks-allow`. Keine Treffer im vorgesehenen Index. Das ist ein Musterscan, kein Beweis für die Abwesenheit jedes denkbaren vertraulichen Inhalts.
- Inventar: keine Symlinks und keine privaten Laufzeitdateien im vorgesehenen Index. Die Bilddateien wurden für die Architekturübersicht aus den enthaltenen Excalidraw-Dateien erstellt.
- [Unabhängiger Transferreview](github-transfer-review.md): keine belegten Blocker im geprüften Umfang. AST-Abgleich der Runtime-Helfer, Paketmanifest und tatsächliche CLI-Argumente geprüft.
- Kurzanleitung gegen den Profildialog und den Installervertrag geprüft. Sie wählt ausschließlich Claude und ein neues Test-Home. Änderungen dieses Veröffentlichungsschritts betreffen Dokumentation, Git-Ausschlüsse und Formatierung. Kein ausführbarer Paketcode geändert.
- Pre-commit-Review für diesen Transfer: Sicherheit der Dateiauswahl, Dokumentationskorrektheit, CLI-Vertrag, Linkziele und Portabilität geprüft. Performance und Typverhalten der unveränderten Implementierung sind durch diesen Dokumentationsschritt nicht verändert. Die vorhandenen Implementierungsreviews und der neue Gesamttest bleiben die begrenzten technischen Nachweise.

## Offen

Push, Privatsichtbarkeit und frischer GitHub-Checkout werden nach dem Commit überprüft und hier nachgetragen. Die echte Betriebsabnahme, Anmeldung, Modellantworten und Dienstanbindungen auf Mac 2 stehen weiterhin aus. Hier wurden keine nativen Clients gestartet und keine aktiven Installationen verändert.
