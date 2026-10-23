# AIOS-Übersicht / AIOS Overview

Stand 0.2.0-dev, 23.10.2026. Eine Zeichnung in zwei Sprachfassungen mit identischem Layout, gedacht zum Präsentieren.

| Deutsch | English |
| --- | --- |
| [aios-uebersicht.excalidraw](aios-uebersicht.excalidraw) | [aios-overview.excalidraw](aios-overview.excalidraw) |
| [aios-uebersicht.png](aios-uebersicht.png) | [aios-overview.png](aios-overview.png) |

Die Zeichnung zeigt in sieben Abschnitten Quelle, Einrichtung, installierte Dateien, den Ablauf eines Auftrags mit Prüfagent, die 21 Skills, den Betrieb und den Prüfstand. Die Skillnamen entsprechen der jeweiligen Sprachfassung.

Die `.excalidraw`-Dateien lassen sich auf excalidraw.com öffnen und bearbeiten. Beide entstehen aus [build_diagram.py](build_diagram.py), damit Layout und Inhalt beider Sprachen gleich bleiben. Nach einer Änderung neu erzeugen und mit dem Renderer des externen Skills [excalidraw-diagram](https://github.com/coleam00/excalidraw-diagram-skill) (`references/render_excalidraw.py`, nicht Teil dieses Repositorys) als PNG ausgeben:

```sh
python3 -B docs/praesentation/build_diagram.py
cd <excalidraw-diagram>/references
uv run python render_excalidraw.py <repo>/docs/praesentation/aios-overview.excalidraw --scale 2
sips -Z 3800 <repo>/docs/praesentation/aios-overview.png
```

Der Renderer liefert bei `--scale 2` die vierfache Größe, `sips` verkleinert auf 3800 Pixel Breite. So liegen die PNG-Dateien in doppelter Auflösung vor und eignen sich für Folien.

Der Prüfstand im Bild gibt den Stand vom 23.10.2026 wieder. Belegt heißt: 179 automatische Tests, Einrichtung, Update und Deinstallation, das Laden in beiden Clients sowie der fachliche Inhalt von sieben englischen Codex-Fällen. Offen sind die Abnahme des Prüfagenten in Codex, englische Claude-Fälle, Dienstanbindungen und die visuelle Abnahme des Präsentationsrenderers.
