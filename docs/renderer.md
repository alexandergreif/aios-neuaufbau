# Lokale Renderer und Folienprüfung

Die technischen Werkzeuge liegen paketlokal unter `allgemein/werkzeuge/`. Es wurden keine alten Referenzfolien, Kundenbeispiele oder Paletten übernommen. Der Unterlagenrenderer verwendet Python-Standardbibliothek und den paketlokalen Helfer `scripts/sichere_dateien.py`. Im gebauten Runtime-Paket funktioniert er auch aus einem anderen Arbeitsverzeichnis.

```sh
python3 allgemein/werkzeuge/unterlagen/render.py \
  --input /absoluter/pfad/zu/synthetischem-inhalt.json \
  --output /absoluter/neuer/ausgabeordner \
  --palette-file /absoluter/pfad/zur/geprueften-palette.md \
  --palette name
```

`--palette-file` ist Pflicht. Die Palettendatei muss genau einen `json`-Codeblock mit `schema_version: 1` und der gewählten Palette mit `primary`, `accent`, `ink` und `notice` enthalten. Der Renderer übernimmt keine alte persönliche Standardpalette. Mit `--artifacts presentation`, `handout` oder `examples` lässt sich der Umfang begrenzen. Er legt einen neuen Ausgabeordner exklusiv an und erhält vorhandene Ziele. `inhalt.json` und `build.json` sind Arbeits- und Prüfdaten. Das Manifest enthält Hashes der erzeugten Dateien und markiert die Zielgruppe der Artefakte. Trainerinhalte gehören nicht in Teilnehmerdateien.

`allgemein/werkzeuge/praesentationen/check_html.py` prüft sichtbaren Text, fortlaufende Folienkennungen und typische externe Ressourcen oder Netzwerkaufrufe statisch. Der Check berücksichtigt nun auch `srcset`, Formularziele, Poster, `ping`, `srcdoc`, Inline-Styles und Meta-Refresh. `srcset` wird konservativ als mögliche externe Ressource behandelt. Ein bestandener statischer Check beweist weder vollständige Netzwerkfreiheit noch gute Darstellung oder Bedienbarkeit. Dynamisch erzeugte URLs, komplexes JavaScript und alle Browserzustände kann diese Prüfung nicht vollständig erkennen.

## Herkunft und Prüfumfang

Die SHA-256-Werte der fünf erlaubten alten Quelldateien waren vor und nach der Übernahme unverändert:

| Alte technische Quelle | SHA-256 vor und nach der Übernahme | Neue Paketdatei |
| --- | --- | --- |
| `kundenunterlage/scripts/render.py` | `ceaa72bb9249d68fce456ea405d1b23f2fcddd6f39f57608c9785c60a6333dd3` | `allgemein/werkzeuge/unterlagen/render.py`, angepasst |
| `kundenunterlage/assets/layout.html` | `9514c22a4cb4b0c321641facf80e8bf94938ea5ad409fd8b816014f51fb95616` | `allgemein/werkzeuge/unterlagen/assets/layout.html`, bytegleich |
| `kundenunterlage/assets/interaction.js` | `66060d7ac515e89f6ed48c2eb721fb27810d4feeedf9d09529208ca162203714` | `allgemein/werkzeuge/unterlagen/assets/interaction.js`, bytegleich |
| `kundenunterlage/assets/profiles/hausformat.css` | `9d3a87dc1d17825bde228c4701364f60224780539218ab910e8304fa8222d081` | `allgemein/werkzeuge/unterlagen/assets/profiles/hausformat.css`, bytegleich |
| `blockbrain-slides/scripts/check_html.py` | `07538cb59bd7686f504e2e98fd7b4bc1da518760e8d599d3ea3e1d90decb2c55` | `allgemein/werkzeuge/praesentationen/check_html.py`, angepasst |

Die neuen synthetischen Tests stehen in `tests/test_renderer_uebernahme.py`. Geprüft wurden CLI-Erfolg mit Dateihashes, Pflichtpalette, doppelte JSON-Schlüssel in Inhalt und Palette, Schemafehler, vorhandenes Ziel, ein unmittelbar vor der Veröffentlichung angelegtes leeres Ziel, typische externe Ressourcenattribute und der Renderer-Aufruf aus einem isolierten Runtime-Paket. Zusammen mit den Paketbau-Tests: `python3 -m unittest tests.test_renderer_uebernahme tests.test_paket_bauen -q`, 16 Tests bestanden. Der Race-Test prüft die erhaltene Identität des fremden leeren Ordners und das Entfernen eigener Zwischenstände. [Unabhängiger Review](../pruefungen/renderer-review.md).

Es gab keinen Browserlauf und keine visuelle oder funktionale Abnahme der Oberfläche. Vor einer Fertigmeldung für echte Unterlagen müssen die erzeugten Ansichten und die Druckausgabe mit dem vereinbarten Browserweg visuell und funktional geprüft werden.
