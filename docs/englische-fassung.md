# Englische Fassung: Struktur, Namen und Glossar

Stand: 23.10.2026. Verbindliche Grundlage für Phase B (Entscheidung 122). Deutsch unter `de/` bleibt führende Quelle. `en/` ist eine inhaltsgleiche Übertragung. Eine Installation nutzt genau eine Sprache.

## Struktur

| Quelle | Runtime-Wurzel | Sprache |
| --- | --- | --- |
| `de/` | `allgemein/` | Deutsch, bestehende Installationen bleiben unverändert |
| `en/` | `general/` | Englisch |

Die Skripte unter `scripts/` sind gemeinsam, haben englische Namen und geben Meldungen nur auf Englisch aus. Der Installer spricht immer Englisch und fragt die Sprache der Regeln und Skills ab (`--language de|en`).

## Dateinamen außerhalb der Skills

| `de/` | `en/` |
| --- | --- |
| `regeln/kern.md` | `rules/core.md` |
| `referenzen/ablage.md` | `references/storage.md` |
| `referenzen/externes-schreiben.md` | `references/external-writes.md` |
| `referenzen/profil-und-wissen.md` | `references/profile-and-knowledge.md` |
| `referenzen/verbindungen.md` | `references/connections.md` |
| `vorlagen/profil.md` | `templates/profile.md` |
| `vorlagen/projekte.md` | `templates/projects.md` |
| `vorlagen/wissen/INDEX.md` | `templates/knowledge/INDEX.md` |
| `vorlagen/wissen/notiz.md` | `templates/knowledge/note.md` |
| `vorlagen/projekt/PLAN.md` | `templates/project/PLAN.md` |
| `vorlagen/projekt/NOTIZEN.md` | `templates/project/NOTES.md` |
| `konfiguration/.env.example` | `configuration/.env.example` |
| `konfiguration/pfade.vorlage.json` | `configuration/paths.template.json` |
| `werkzeuge/praesentationen/check_html.py` | `tools/presentations/check_html.py` |
| `werkzeuge/unterlagen/render.py` | `tools/materials/render.py` |
| `werkzeuge/unterlagen/assets/interaction.js` | `tools/materials/assets/interaction.js` |
| `werkzeuge/unterlagen/assets/layout.html` | `tools/materials/assets/layout.html` |
| `werkzeuge/unterlagen/assets/profiles/hausformat.css` | `tools/materials/assets/profiles/house-style.css` |

In Skills heißt `references/prueffaelle.md` englisch `references/test-cases.md`, `references/allgemeiner-pr-review.md` heißt `references/general-pr-review.md`. `agents/openai.yaml` behält den Namen.

## Skillnamen

Von Alexander am 23.10.2026 freigegeben.

| `de/skills/` | `en/skills/` |
| --- | --- |
| aios-audit | aios-audit |
| aufgabenassistenz | task-assistant |
| auftrag-vorbereiten | prepare-brief |
| frontend-gestaltung | ui-design |
| planhat-zeiterfassung | planhat-time-tracking |
| pr-review | pr-review |
| precommit-review | precommit-review |
| prompt-berater | prompt-advisor |
| prozessanalyse | process-analysis |
| recherche | research |
| review-kommentare | review-comments |
| skill-builder | skill-builder |
| system-retro | system-retro |
| tagesstart | daily-briefing |
| terminnachbereitung | meeting-follow-up |
| terminvorbereitung | meeting-prep |
| unterlagen | presentation-materials |
| use-case-konzept | use-case-concept |
| wochenplanung | weekly-planning |
| wochenreview | weekly-review |
| zeiterfassung-vorbereiten | prepare-time-entries |

## Skriptnamen

Die Betriebsanleitungen direkt unter `docs/` nennen die neuen Namen. Datierte Ergebnisse und Testzahlen, auch in Nachweisabschnitten unter `docs/`, sowie die Prüfberichte unter `pruefungen/` bleiben historischer Stand mit den alten Namen.

Gilt für beide Sprachen. Testdateien folgen dem neuen Namen (`tests/test_<name>.py`).

| alt | neu |
| --- | --- |
| `aktualisieren.py` | `update.py` |
| `client_vorbereiten.py` | `prepare_client.py` |
| `deinstallieren.py` | `uninstall.py` |
| `einrichten.py` | `setup_profile.py` |
| `einrichtungsstatus.py` | `setup_status.py` |
| `installationsplan.py` | `install_plan.py` |
| `installieren.py` | `install.py` |
| `paket_bauen.py` | `build_package.py` |
| `paketbestand.py` | `package_inventory.py` |
| `paketbetrieb.py` | `package_operations.py` |
| `paketregeln.py` | `package_rules.py` |
| `profil_transfer.py` | `profile_transfer.py` |
| `pruefe_client_loader.py` | `check_client_loader.py` |
| `pruefe_installation_lokal.py` | `check_local_installation.py` |
| `pruefe_konfiguration.py` | `check_config.py` |
| `pruefe_register.py` | `check_register.py` |
| `pruefe_skill_loader.py` | `check_skill_loader.py` |
| `setup.py` | `setup.py` |
| `sichere_dateien.py` | `safe_files.py` |

## Private Dateien je Sprache

| Deutsch | Englisch |
| --- | --- |
| `pfade.json` | `paths.json` |
| `profil.md` | `profile.md` |
| `projekte.md` | `projects.md` |
| `wissen/` | `knowledge/` |
| `zustand/` | `state/` |
| `archiv/` in `paths.output` | `archive/` |

Die Konfiguration bekommt das Feld `"language": "de"` oder `"en"`. Fehlt es, gilt `de`. Der Unterordner für Ausführungsspuren heißt `zustand/aktionen/` beziehungsweise `state/actions/`. Technische Dateien innerhalb des Zustandsordners (`installation.json`, `bestand.json`, `betrieb.lock`, `sicherungen/`, `operation.json`) behalten in beiden Sprachen ihre Namen.

Register: Spalten `Key | Customer or project | Local folder | Repository | Jira prefix | Status`, Statuswerte `active`, `paused`, `archived`, `to-assign`. Profilfelder: `Name and form of address`, `Role`, `Language`, `Time zone`, `Working hours and days off`, `Working style`, `Priorities`. Unbeantwortet heißt `open`. Die internen JSON-Schlüssel des Profiltransfers bleiben gleich.

Ausgabesprache ohne Profilangabe: Deutsch im deutschen Paket, Englisch im englischen Paket.

## Glossar

| Deutsch | Englisch |
| --- | --- |
| Regelkern, Kern | core rules, core |
| Auftrag | task (konkreter Nutzerauftrag), brief (vorbereiteter Arbeitsauftrag) |
| Arbeitsstand | working state |
| Projektarbeitsdateien | project working files |
| Ablage | storage |
| Ergebnisdatei | output file |
| Projektregister, Register | project register, register |
| Kürzel | key |
| Kundenwurzel, Codingwurzel | customer root, coding root |
| Prüfagent | review agent |
| unabhängige Prüfung | independent review |
| Nachprüfung | follow-up review |
| Befund | finding |
| Prüffälle | test cases |
| Freigabe | approval |
| Befugnis | authority |
| externe Schreibaktion | external write action |
| Ausführungsspur | execution trace |
| Aktionsjournal | action journal |
| Quelle, führende Quelle | source, authoritative source |
| Quellenlücke | source gap |
| Denkaufwand | reasoning effort |
| Hauptagent, Subagent | main agent, subagent |
| Dienstanbindung, Verbindung | service connection, connection |
| Profil und Wissen | profile and knowledge |
| Vorliebe | preference |
| Humanizer | Humanizer |
| Einrichtung | setup |
| Paket, Runtime | package, runtime |
| Skill | skill |
| muss, sollte, Hinweis | must, should, note |
| Hinweis (Punkt eines Reviewers) | point, review point |
| Abnahme | acceptance |
| belegen, belegt | back up with evidence, evidenced, substantiated (nicht document) |
| Annahme | assumption |
| Vermutung | guess |
| Erkenntnis | insight |
| dauerhaft | lasting |
| Grenzen (Auftragsumfang) | limits |
| beauftragt | requested |
| Befugnisse | authority (Singular), grants of authority |
| Oberflächen | user interfaces, UI |
| fällig | due (überfällig: overdue) |
| Quelldatum (ein Datum aus einer Quelle) | source data |
| auf Bitte, auf Auftrag, auf Aufruf | on request, when tasked, on invocation |

## Übersetzungsregeln

- Inhaltsgleich übertragen. Nichts ergänzen, weglassen oder abschwächen. Struktur, Überschriftenebenen, Tabellen, Listen und Reihenfolge bleiben gleich.
- Natürliches Englisch mit der Hauptaussage zuerst. Keine Gedankenstriche (– oder —) und keine Semikolons als Satztrenner, wie im deutschen Original.
- Links und Pfade auf die englischen Namen dieser Tabellen umstellen. Skriptaufrufe mit den neuen Skriptnamen und englischen Platzhaltern, etwa `scripts/check_register.py --config <paths.json> --register <projects.md> --project <key>`.
- Im Skill-Frontmatter `name` auf den englischen Skillnamen setzen. `description` inhaltsgleich übersetzen, Auslöser als natürliche englische Formulierungen.
- Eigennamen bleiben: Claude Code, Codex, Microsoft To Do, Outlook, Jira, Confluence, Planhat, Slack, Teams, GitHub, Blockbrain, Atrio, Botticelli, HyperFrames, ElevenLabs.
- Wörtliche Beispiele für Nutzeräußerungen werden übersetzt. Code, Dateiformate und Schlüssel bleiben unverändert, soweit diese Tabellen nichts anderes festlegen.
- Einheitliche Formen im Englischen: Prüffall-Dateien beginnen mit `All details are fictional. The expected outcomes are not passed model tests.`, wo das Original diesen Satz hat. Das Soll-Feld heißt `Expected:`. Überschriften in Title Case, ausgenommen die vom Code gelesenen Überschriften in `en/templates/profile.md` (`# Personal profile`, `## Small preferences`, `## Confirmed changes`), Skill-Überschriften im Imperativ (`Create Presentation Materials`). Kein serielles Komma vor and/or, wie im deutschen Original.

