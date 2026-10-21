# Privates Projektregister prüfen

Die leere Vorlage `allgemein/vorlagen/projekte.md` wird privat eingerichtet. Ein Projekt braucht ein eindeutiges Kürzel, einen Namen, einen lokalen Ordner und einen Status. Repository (HTTPS ohne Zugangsdaten) und Jira-Präfix bleiben optional. Bei noch offener Pfadzuordnung Status `zuordnen` setzen und den Ordner leer lassen.

```sh
python3 scripts/pruefe_register.py --register /privater/pfad/projekte.md --config /privater/pfad/pfade.json
```

Der Prüfer liest nur die benannten Dateien und Pfadmetadaten. Er liest keine Kundeninhalte und legt keine Ordner an. Er prüft die Spalten, eindeutige Kürzel, Status, optionale Felder und die Ablage innerhalb bestätigter Projektwurzeln. Symlink-Ausbrüche und doppelt zugeordnete Ordner werden abgewiesen. Bei Groß-/Kleinschreibung und Unicode gelten die konservativen Mac-Vergleiche aus dem Pfadprüfer.

Ein konkretes Projektziel ausgeben:

```sh
python3 scripts/pruefe_register.py --register /privater/pfad/projekte.md --config /privater/pfad/pfade.json --project DEMO
```

Nur ein eindeutig aktiver Eintrag liefert einen Pfad. Ein fehlender, pausierter, archivierter oder noch zuzuordnender Eintrag führt zu Exit 1 und muss mit dem Nutzer geklärt werden. Keine Ersatzablage erraten. Die Ausgabe ist keine Schreibfreigabe. Eine gültige leere Tabelle bestätigt keine eingerichteten Projekte.

Die Pfadkonfiguration wird zuerst geprüft. Auf einem neuen Mac müssen dort Wurzeln und im Register konkrete Projektpfade bestätigt werden. Projektordner liegen als Unterordner innerhalb einer Wurzel und dürfen nicht den AIOS-Quellcode umfassen. Reale Register wurden für die Entwicklung nicht gelesen.
