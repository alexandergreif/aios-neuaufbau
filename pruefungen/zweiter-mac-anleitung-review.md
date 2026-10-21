# Review der Anleitung für den zweiten Mac

Stand: 20.10.2026. Lesender Abgleich von `docs/abnahme-zweiter-mac.md` mit README-Entscheidung 118, Setup-, Erstinstallations-, Profiltransfer- und Modelltestdokumentation sowie den maßgeblichen lokalen Codepfaden.

**Ergebnis nach Nachprüfung: Beide konkreten Anleitungsfehler geschlossen.** Die Betriebsprobe verlangt nun zwingend einen eigenen vorhandenen Benutzerordner und hält auch die Codex-Skillbasis darin. Der optionale Profilimport erfolgt ausdrücklich erst nach erfolgreicher Profileinrichtung und Installation. Die noch vorläufige Betriebs-CLI bleibt ein separater späterer Abgleichpunkt.

**Architekturauswirkung: Niedrig.** Keine Produktänderung oder neue Abstraktion erforderlich. Es geht um die korrekte Nutzung vorhandener Verträge. Kein ADR nötig.

## Nachprüfung am 20.10.2026

`docs/abnahme-zweiter-mac.md:37` verlangt einen eigenen vorhandenen synthetischen Benutzerordner. Zeile 39 nennt die separate Erstinstallation mit explizitem `--home` und beiden Test-Clientordnern sowie die anschließende Statusprüfung. Zeile 41 erläutert die von `CODEX_HOME` unabhängige Codex-Skillbasis und platziert beide Fremdskillmarker in den tatsächlichen Test-Skillordnern. Zeile 43 verlangt dieselben bestätigten Testorte für spätere Betriebsbefehle. Damit ist P1 geschlossen.

Zeile 15 begrenzt den frühen Export-Schritt auf private Bereitstellung und verbietet den Import vor der Profileinrichtung. Zeile 27 ordnet den bestätigten Import nach der erfolgreichen geführten Installation ein und benennt die Erhaltung der lokalen `pfade.json`. Damit ist P2 geschlossen.

Die Nachprüfung beschränkte sich auf diese beiden Dokumentkorrekturen. Keine halb fertige Betriebsimplementierung geprüft, keine Befehle der Anleitung ausgeführt und keine Modelltests behauptet. Die folgenden ursprünglichen Befunde bleiben als Verlauf erhalten.

## P1: Test-Clientordner allein isolieren die Codex-Skills nicht (behoben)

**Fundstelle:** `docs/abnahme-zweiter-mac.md:35`, zusammen mit der als optional beschriebenen Ortswahl in Zeile 37.

Die Anleitung verlangt getrennte Profile, Runtime, Ausgabe und Clientordner, aber keinen eigenen `--home`. `scripts/installationsplan.py:114` legt die Codex-Skillbasis ausdrücklich als `home / ".agents/skills"` fest. `--codex-home` verändert diesen Pfad nicht.

**Konkreter Ablauf:** Die normale Einrichtung liegt unter dem echten Benutzerordner. Für die Betriebsprobe werden `/test/codex`, `/test/claude`, `/test/profile`, `/test/runtime` und `/test/output` gewählt, aber `--home` bleibt beim Standard. Die Testregeldatei zeigt dann auf `/test/codex/AGENTS.md`, die Test-Skillziele bleiben dagegen im normalen Benutzerordner unter `.agents/skills`. Eine Test-Erstinstallation kollidiert mit den normalen Skills. Die behauptete Isolation ist nicht gegeben. Es wird nicht behauptet, dass der aktuelle Installer die vorhandenen Skills überschreibt, seine Konfliktprüfung soll gerade stoppen.

**Kleinste Korrektur:** Abschnitt 4 muss einen neuen eigenen Testbenutzerordner verbindlich verlangen. Dieser muss vor dem Aufruf existieren, weil die CLI `--home` auf einen vorhandenen Ordner begrenzt. Ein konkreter geführter Testinstallationsaufruf muss `--home /absoluter/testhome`, `--codex-home /absoluter/testhome/.codex` und `--claude-config-dir /absoluter/testhome/.claude` enthalten. Im Dialog Profil, Runtime und Ausgabe ebenfalls ausschließlich unter dem Testhome wählen. Der Quellordner bleibt das ausgewählte Paket.

Die Anleitung muss vor Update und Deinstallation diese separate Erstinstallation samt Statusprüfung ausdrücklich einordnen. Alle anschließenden Betriebsbefehle müssen dieselben bestätigten Testorte verwenden. Den Codex-Fremdskillmarker unter `/absoluter/testhome/.agents/skills/<eigener-testname>/SKILL.md` anlegen, nicht nur unter `CODEX_HOME`. Für Claude gehört der Marker in den gewählten Test-Clientordner unter `skills/`. Normale Skillverzeichnisse bleiben unberührt. Für reine Datei-Betriebsproben keine zusätzliche Anmeldung oder nativen Clientaufruf vorsehen.

## P2: Profilimport vor dem geführten Einstieg blockiert die Profileinrichtung (behoben)

**Fundstelle:** `docs/abnahme-zweiter-mac.md:15`, gefolgt vom Aufruf ohne `--config` in Zeile 17.

**Konkreter Ablauf:** Auf dem frischen Mac wird entsprechend Zeile 15 zuerst der importierte Export nach `/neu/profil` übernommen. `scripts/profil_transfer.py:281` legt einen fehlenden Zielordner bei bestätigtem Import selbst an und schreibt dort `profil.md`. Anschließend startet `sh install.sh` die Profileinrichtung. Bei Auswahl desselben Profilpfads stoppt `scripts/einrichten.py:67` mit „Profilziel existiert bereits“. Der Import erzeugt außerdem keine bestätigte `pfade.json`, mit der stattdessen der Installer fortgesetzt werden könnte.

Ein bereits bestehendes Importziel wird durch diese CLI nicht vorausgesetzt. Der Fehler ist die Reihenfolge und der Konflikt mit dem anschließend geforderten neuen Profilziel.

**Kleinste Korrektur:** Den Export zunächst nur privat auf dem zweiten Mac bereitstellen. Danach das neue Profil samt lokalen Pfaden über den geführten Einstieg anlegen. Erst anschließend den optionalen Import mit Vorschau und Bestätigung gezielt in dieses eingerichtete Profil ausführen. Der Import ersetzt nach Sicherung ausschließlich `profil.md`, die bestätigte `pfade.json` bleibt erhalten. Das kann nach erfolgreicher Erstinstallation geschehen. Alternativ die zweite Setup-Bestätigung abbrechen, importieren und mit dem angezeigten `--config`-Fortsetzungsaufruf installieren. Für die Hauptanleitung genügt eine eindeutige Variante.

## Erfüllte Kriterien

- Entscheidung 118 ist berücksichtigt. Die Anleitung ist ausdrücklich ein zukünftiger gemeinsamer Prüfplan für den zweiten Mac. Die aktive Installation auf dem ersten Mac bleibt unberührt.
- Python 3.13.16 wird als tatsächlich geprüfter Stand angegeben, keine unbelegte Mindestversion behauptet.
- Dateistatus, native Ladung, angemeldete Modellantworten und Dienstfunktion werden getrennt bewertet. Alle Protokollzeilen stehen auf „Offen“.
- Die Fallquelle enthält sechs synthetische Modellfälle. Die Anleitung verlangt tatsächliche Antworten und unabhängige Bewertung, ohne frühere Loaderproben als Modelltest auszugeben.
- Es gibt keinen erfundenen Clone-Befehl und keine pauschale Kopieranweisung für Profile, `.env` oder Client-Anmeldespeicher. Der Exportinhalt soll vor Weitergabe geprüft werden. Freitextfelder bleiben dabei manuell auf Geheimnisse zu prüfen, wie die Profiltransferdokumentation erläutert.
- Fehlende Dienstprüfungen und visuelle Rendererabnahme bleiben ausdrücklich offen.

## Vorläufige Verweise und späterer Abgleich

Die relativen Links auf `profiltransfer.md`, `modelltests-zweiter-mac.md` und `../tests/verhalten/faelle.json` existieren. Der Link auf `paketbetrieb.md` ist beim Review noch nicht auflösbar. Die Anleitung kennzeichnet Dokument und Betriebsskripte ausdrücklich als parallel entstehend. Das wird hier als offener Abgleichpunkt behandelt, nicht als eigenständiger Fehler.

Nach Abschluss der parallelen Betriebsimplementierung müssen deren tatsächliche Argumente, persistierte Bindungen und Statusausgaben mit Abschnitt 4 abgeglichen werden. Bis dahin keine vermutete CLI als ausführbar bestätigen. Der konkrete Teststand und die in Zeile 3 genannte Testanzahl sollten bei diesem Abschluss ebenfalls aktualisiert werden.

## Prüfgrenzen

Keine Clients, Browser, Netzwerke oder Git-Befehle gestartet. Keine realen Profile, Geheimnisse oder Kundeninhalte gelesen. Keine Testinstallation oder Modelltests durchgeführt. Die beiden Ablaufbefunde stammen aus dem konkreten Abgleich der Anleitung mit den gelesenen Implementierungen. Nur dieser Bericht wurde angelegt.
