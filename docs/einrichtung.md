# Geführte lokale Ersteinrichtung

Die Einrichtung erstellt ein neues privates Profil. Sie installiert weder Claude Code noch Codex, bindet keine Regeln in einen Client ein und prüft keine Clientfunktion oder Dienstverbindung.

```sh
python3 scripts/einrichten.py
```

Für einen synthetischen Benutzerordner kann `--home /absoluter/ordner` verwendet werden. Ohne diese Option gilt der Benutzerordner des laufenden Prozesses. `--help` zeigt nur die Hilfe.

Der Dialog fragt den Client (Claude Code, Codex oder beide), Quellcode, Runtime, Profil und Ausgabe sowie optional Coding- und Kundenwurzeln ab. Alle Pfade werden mit `scripts/pruefe_konfiguration.py` geprüft. Der Elternordner des Profilziels muss bereits existieren. Danach folgen die sieben Felder aus der Profilvorlage. Leere Angaben bleiben offen.

Vor dem Speichern zeigt der Dialog Pfade und Profilangaben. Nur die Antwort `ja` auf die Speicherfrage erstellt Dateien. Danach ist ein Blockbrain-Schlüssel optional. Er wird verdeckt abgefragt, nicht in der Vorschau oder Diagnose ausgegeben und ausschließlich in `.env` im neuen Profilordner gespeichert. Bei Überspringen enthält `.env` einen kurzen Hinweis und das leere Feld `BLOCKBRAIN_API_KEY=`.

Einrichtung und Profiltransfer verwenden dieselben Feldnamen, Markdown-Kodierung und Wertgrenzen. Jedes Feld darf höchstens 4096 Zeichen und keine Steuerzeichen enthalten. Damit lassen sich bestätigte Werte auch mit Backslashes oder senkrechten Strichen übertragen.

Der neue Profilordner enthält `pfade.json`, `profil.md`, `projekte.md`, `.env` und `wissen/INDEX.md`. `pfade.json` hat das Schema der Paketvorlage und setzt `confirmed` erst nach der ausdrücklichen Bestätigung. Der Profilordner und `wissen` erhalten Modus `0700`, Dateien `0600`. Runtime und Ausgabe werden noch nicht angelegt. Die Paketvorlagen bleiben unverändert.

Ein vorhandenes Profilziel, einschließlich eines vorhandenen `.env`, führt zum Abbruch. Die erste Version führt keine Daten zusammen und überschreibt keine privaten Inhalte. Symbolische Links im Profilziel werden abgewiesen. Die Dateien werden zunächst in einem privaten Nachbarordner vorbereitet und der vollständige Ordner mit einer Betriebssystemfunktion ohne Überschreiben an den Zielnamen verschoben. Ist diese Funktion nicht verfügbar, bricht die Einrichtung ab.

Synthetische Prüfung:

```sh
python3 -m unittest discover -s tests -p 'test_einrichten.py' -v
```

Diese Prüfung belegt nur das lokale Verhalten des Dialogs. Eine Clientinstallation, Anmeldung und praktische Abnahme der beiden Clients folgt später.
