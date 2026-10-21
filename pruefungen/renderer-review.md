# Unabhängiger Review der Renderer-Paketkopien

Stand: 20.10.2026. Grundlage ist Entscheidung 117. Geprüft wurden ausschließlich die neuen technischen Paketkopien und synthetische Eingaben.

**Ergebnis nach Nachprüfung: Keine offenen Befunde im geprüften technischen Übernahmeumfang.** Die explizite Palettenwahl, der sichere Ausgabepfad und die erweiterten Ressourcenprüfungen funktionieren in den nachgewiesenen Fällen. Doppelte JSON-Schlüssel werden jetzt auch bei Paletten abgelehnt. Der ursprünglich fehlerhafte Fall eines konkurrierenden leeren Ausgabeordners ist dauerhaft als Regressionstest abgesichert. Visuelle Qualität, Bedienung und Druckausgabe bleiben ungeprüft.

## Nachprüfung der beiden Korrekturen

20.10.2026: `palette_from()` lädt den JSON-Block in `render.py:116` jetzt mit `object_pairs_hook=unique_object`. Der neue CLI-Test in `tests/test_renderer_uebernahme.py:86` reproduziert die doppelte verschachtelte Farbe und belegt Fehlerstatus, Duplicate-Key-Meldung und fehlenden Ausgabeordner.

Der neue Race-Test in `tests/test_renderer_uebernahme.py:95` legt das leere Ziel unmittelbar vor `exclusive_rename_at()` im gebundenen Elternordner an. Er prüft anschließend unveränderte Geräte-/Inode-Identität, weiterhin leeren Inhalt und fehlende Stagingreste. Damit deckt er den ursprünglichen Fehlerfall unmittelbar ab. Der Test des nichtleeren Ziels bleibt zusätzlich erhalten.

Beide Korrekturen wurden im Code und über eine erneute unabhängige Ausführung geprüft: `test_renderer_uebernahme.py` (8 Tests) und `test_paket_bauen.py` (8 Tests). **16 Tests erfolgreich.** Der ursprüngliche Fehler und die Prüflücke sind geschlossen. Die folgenden Befundbeschreibungen und Erstprüfergebnisse dokumentieren den Verlauf.

## Architekturauswirkung und Musterprüfung

**Architekturauswirkung: Niedrig.** Paketlokale Werkzeuge mit Python-Standardbibliothek und gemeinsamem Dateisicherheitshelfer sind angemessen. Keine zusätzliche Dienst- oder Pluginarchitektur erforderlich. Keine neue Architekturentscheidung und kein ADR nötig.

| Kriterium | Ergebnis |
| --- | --- |
| Paketlokale Abhängigkeiten | Erfüllt. `render.py` löst `scripts/sichere_dateien.py` relativ zum installierten Paket auf. Der Runtime-Test läuft aus einem anderen Arbeitsverzeichnis ohne `PYTHONPATH`. |
| Explizite persönliche Eingaben | Erfüllt. `--palette-file` ist Pflicht. Kein persönlicher alter Standardpfad wird verwendet. |
| Gemeinsamer sicherer Schreibweg | Erfüllt für geprüfte Fälle. Staging und exklusive Veröffentlichung laufen im gebundenen Elternordner über `build_directory()`. |
| Einheitliche JSON-Semantik | Nach Korrektur erfüllt. Inhalt und Palette verwenden denselben Duplicate-Key-Helfer. |
| Trennung der Zielgruppen | Im synthetischen Build erfüllt. Trainernotizen fehlen in Handout und Beispieldatei. `inhalt.json` und Präsentation sind im Manifest als Trainerartefakte markiert. |
| Ehrliche Abnahmegrenzen | Dokumentation trennt statischen Check und Build korrekt von Darstellung, Bedienbarkeit, Druckausgabe und vollständiger Netzwerkfreiheit. |

## Befunde der Erstprüfung, beide geschlossen

### Bug, P2: Doppelte Schlüssel in der Palette werden nicht abgelehnt (behoben)

**Fundstelle:** `allgemein/werkzeuge/unterlagen/render.py:116`, `palette_from()`.

Die Inhaltsdatei wird in Zeile 224 mit `object_pairs_hook=unique_object` gelesen. Der JSON-Block der Palette verwendet dagegen weiterhin `json.loads(blocks[0])` ohne diesen Helfer.

**Synthetische Reproduktion:** In einer ansonsten gültigen Palette wurde innerhalb derselben Palette zuerst `"primary": "#123456"` und anschließend nochmals `"primary": "#654321"` angegeben. Der CLI-Build endete mit Exitcode 0, erzeugte die Unterlage und schrieb `#654321` als gewählte Farbe in `build.json`.

**Erwartet:** Mehrdeutiges JSON ablehnen, kein Ausgabeordner. **Tatsächlich:** Der letzte Wert gewinnt still. Damit ist die in Entscheidung 117 beauftragte eindeutige Verarbeitung doppelter JSON-Schlüssel an dieser Geschwisterstelle noch nicht umgesetzt.

**Kleinster Fix:** Auch den Palettenblock mit `object_pairs_hook=unique_object` laden. Einen CLI-Regressionstest mit doppeltem verschachteltem Farb- oder Palettennamen ergänzen. Er muss Fehlerstatus, Duplicate-Key-Meldung und fehlenden Ausgabeordner belegen. Dieselbe Helferfunktion genügt, keine zusätzliche Abstraktion nötig.

### Prüflücke, P2: Der dauerhafte Race-Test verwendet ein nichtleeres Ziel (behoben)

**Fundstelle:** `tests/test_renderer_uebernahme.py:97`, insbesondere Zeile 99.

`create_target_then_publish()` erzeugt einen Zielordner mit `marker.txt`. Ein gewöhnlicher unsicherer Verzeichnis-Rename würde ein solches nichtleeres Ziel bereits zurückweisen. Der ursprüngliche Fehler betraf ausdrücklich ein konkurrierendes leeres Ziel. Der aktuelle Test könnte deshalb trotz Rückkehr zum damaligen fehlerhaften Verhalten grün bleiben.

**Kleinste Ergänzung:** Einen leeren Zielordner unmittelbar vor `sichere_dateien.exclusive_rename_at()` anlegen, dessen Inode merken und danach unveränderten Inode sowie weiterhin leeren Inhalt prüfen. Der vorhandene Test mit fremdem Marker darf zusätzlich bleiben.

**Aktuelles Produktverhalten:** Im unabhängigen Review wurde genau dieser leere Race-Fall erfolgreich nachgewiesen. Die Veröffentlichung scheitert mit `FileExistsError`, der leere Zielordner bleibt erhalten und das eigene Staging wird entfernt. Es handelt sich hier um eine fehlende dauerhafte Regression, nicht um einen noch vorhandenen Überschreibfehler.

## Unabhängig ausgeführte Prüfungen

Die vorhandenen Suiten `test_renderer_uebernahme.py` (6 Tests) und `test_paket_bauen.py` (8 Tests) liefen erfolgreich. **14 Tests grün.** Das bestätigt auch die in `docs/renderer.md` genannte Testanzahl. Darüber hinaus wurden eigene kurzlebige synthetische Proben ausgeführt:

| Probe | Nachgewiesenes Ergebnis |
| --- | --- |
| Alle drei Artefakte gemeinsam erzeugen | Präsentation, Handout und Beispiele vorhanden. Sämtliche Hashes des Manifests passen zu den erzeugten Dateien. |
| Text mit HTML und Templatezeichen | `<script>bad()</script>` wird als Text maskiert. `{{body}}` in Nutztext wird nicht nachträglich als Vorlage ausgeführt. |
| Trainerinhalt | Trainernotiz fehlt in Handout und Beispieldatei. |
| Bereits vorhandenes leeres Ziel | Fehlerstatus. Inode unverändert, Ordner weiterhin leer. |
| Leeres Ziel unmittelbar vor exklusiver Veröffentlichung | Fehlerstatus. Inode und Inhalt unverändert, eigenes Staging beseitigt. |
| Austausch des Ziel-Elternordners während Veröffentlichung | Fehlerstatus durch abschließende Pfadprüfung. Kein Schreiben in den neu eingesetzten fremden Zielordner, dessen synthetischer Marker bleibt unverändert. |
| Doppelte Palettenfarbe | Fehler reproduziert: CLI-Erfolg und still gewählter letzter Wert. |
| Sauberes HTML mit Fragmentlink und eingebettetem Bild | Statischer Checker meldet keine Fehler. |
| Zusätzliche Ressourcen über `object data`, SVG `xlink:href`, `background` und `fetch` | Alle vier Fälle werden als externe Ressource oder Netzwerkaufruf gemeldet. |

Beim Elternordnerwechsel bleibt das bereits im gebundenen ursprünglichen Ordner veröffentlichte eigene Ergebnis unter dessen neuem Namen bestehen. Der Aufruf meldet einen Fehler und verändert den fremden Ersatzordner nicht. Der Renderer bietet keinen Rollback und die Prüfung behauptet keinen rückstandslosen Abbruch nach erfolgter Veröffentlichung.

Die vorhandenen Tests decken zusätzlich Pflichtpalette, doppelte Inhaltsschlüssel, Schemafehler, nichtleeres vorhandenes und konkurrierendes Ziel, die neuen Ressourcenattribute sowie den Aufruf aus einer gebauten Runtime in fremdem Arbeitsverzeichnis ab. Sämtliche Testdaten waren neu erzeugt und synthetisch.

## Herkunft und Dokumentationsprüfung

Die SHA-256-Werte der fünf in `docs/renderer.md` genannten freigegebenen technischen Altquellen stimmen zum Reviewzeitpunkt mit den dokumentierten Werten überein. Die neuen Kopien von `layout.html`, `interaction.js` und `hausformat.css` sind bytegleich mit den jeweiligen Altquellen. Die Aussage über die historischen Messzeitpunkte vor und nach der Übernahme stammt aus dem Übernahmeprotokoll. Dieser Review bestätigt unabhängig den aktuellen Hashstand, nicht rückwirkend den Messablauf.

Keine alten Beispiele, Referenzfolien, Paletten oder Kundeninhalte wurden geöffnet. Die Hashprüfung las ausschließlich die fünf ausdrücklich freigegebenen technischen Quelldateien. Aktive Skripte wurden nicht geändert.

Die Dokumentation beschreibt den Checker zutreffend als konservative statische Hilfe. `srcset` und `srcdoc` werden bewusst großzügig als mögliche Ressourcen markiert. Ein erfolgreicher Check ist kein vollständiger Netzwerkfreiheitsnachweis. Insbesondere ist dies keine JavaScript-Sandbox oder Browserprüfung. Der Folienchecker verlangt `section`-Kennungen `s1` bis `sN`, während der getrennte Unterlagenrenderer `data-slide` verwendet. Der Checker ist deshalb kein unverändert anwendbarer Gesamtvalidator für dessen Ausgabe.

## Abnahmestatus

Die technische Übernahme gemäß dem hier geprüften Umfang der Entscheidung 117 ist nach den beiden Korrekturen unabhängig geprüft, ohne offene Befunde. Die 16 gezielten Tests einschließlich Paketbau und Runtime-Aufruf sind erfolgreich. Kein Browser, Netzverkehr, Modellaufruf oder Zugriff auf echte private Daten war Teil dieses Reviews.

Visuelle Qualität, Navigation, Kopieren und Druckausgabe sind weiterhin nicht abgenommen. Diese Grenzen sind in `docs/renderer.md` korrekt sichtbar. Eine technische Nachprüfung darf sie nicht als erledigt markieren.
