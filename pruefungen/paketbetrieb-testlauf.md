# Lokaler Testlauf des neuen Paketbetriebs

Stand: 20.10.2026. Synthetische Dateitests im Quellordner `AIOS-Neuaufbau`. Kein nativer Claude- oder Codex-Aufruf, keine Anmeldung, kein Browser und kein Anbieteraufruf.

Der Hauptagent führte nach den Betriebskorrekturen `python3 -m unittest discover -s tests -q` über `/usr/bin/sandbox-exec` aus. Das Profil sperrte Netzwerkzugriffe sowie Lesen und Schreiben in den echten Ordnern `.claude`, `.codex`, `.agents`, `.agent-rules`, `aios`, `aios-runtime`, `aios-profile`, `aios-output`, im alten Projekt `Agentic OS` und unter `BB Coding Projects`. Unterprozesse erbten diese Sperren. Die Tests verwendeten eigene synthetische Benutzer-, Profil- und Zielordner.

Ergebnis des abschließenden Gesamtlaufs:

```text
Ran 145 tests in 20.617s

OK
Exitcode: 0
```

Die absichtlich ausgelösten Fehler bei geänderter Vorschau, `fsync` und Quellbestand sind erwartete Negativtests. Sie machen den Testlauf nicht zu einer fehlgeschlagenen Installation.

Die Suite umfasst Erstinstallation und Status, Eigentumsprüfung, Update, gezielte Deinstallation, Unterbrechungen sowie den Erhalt synthetischer privater und fremder Dateien. Die zusätzlichen Regressionen prüfen insbesondere die Bindung des eingebetteten Manifests an das echte Runtime-Manifest, fremden Zieltausch beim Dateischritt, Änderungen an unveränderten Paketdateien und Abbrüche rund um den bestätigten Installationsabschluss.

Dieser Lauf belegt keine fachliche Modellfunktion und keine echte Installation auf dem zweiten Mac. Die unabhängige Bewertung steht separat im [Betriebsreview](paketbetrieb-review.md). Die gemeinsame Abnahme folgt dem [Prüfplan für den zweiten Mac](../docs/abnahme-zweiter-mac.md).
