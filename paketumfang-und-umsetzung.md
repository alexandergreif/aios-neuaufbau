# AIOS: konsolidierter Paketumfang und Umsetzung

Stand: 19.10.2026. Grundlage sind die bestätigten Entscheidungen 1 bis 115 in [README.de.md](README.de.md), einschließlich ihrer Buchstabenergänzungen. Dies ist der Umsetzungsplan, kein Funktionsnachweis.

## Ziel und Stand

Ein privates AIOS für eine frische Installation auf einem zweiten Mac. Claude Code, Codex oder beide sind auswählbar. Alle bestätigten Fähigkeiten gehören zum Paket. Nur die Einrichtung von Diensten und Zugängen ist auswählbar oder überspringbar. Zurückgestellte Bestandteile gehören nicht zur ersten Version.

Die Auswahlrunde ist beendet. Quellen und Anpassungen stehen in [uebernahmeliste.md](uebernahmeliste.md). Die erste lokale Grundlage mit Regelkern, Vorlagen und Pfadprüfer ist umgesetzt, siehe [Grundlage](docs/grundlage.md). Native Regelwirkung, Skills und Installer des neuen Gesamtpakets sind noch nicht abgenommen. Frühere Installationen, Testberichte und die verworfenen Paket-Repositories belegen nicht die Funktion des Neuaufbaus.

## Zuständigkeit der Dokumente

- README: chronologisches Entscheidungsprotokoll. Spätere Beschlüsse präzisieren oder ersetzen frühere Vorschläge, die nachvollziehbar erhalten bleiben.
- Dieser Plan: geltender Umfang, Abgrenzungen, Reihenfolge und Abnahme.
- Übernahmeliste: Zuordnung zu bestehenden Quellen oder neu zu erstellenden Teilen, mit offenen technischen Prüfungen. Kein Laufzeit-Ladeplan.
- .aios/PLAN.md und .aios/NOTIZEN.md: kurzer Arbeitsstand und wichtige Befunde dieses Neuaufbaus.
- Inventar und bisherige Prüfberichte: datierte Quellen, keine aktuelle Installations- oder Funktionszusage.

Die spätere Paket-README wird Installationsanleitung und Nutzungshilfe. Das Entscheidungsprotokoll wird dabei erhalten und aus dem täglichen Einstieg verlinkt. Seine gesamte Historie gehört nicht in den Startkontext.

## Arbeitsweise und gemeinsame Regeln

| Thema | Geltender Beschluss | Grundlage |
| --- | --- | --- |
| Start und Auftragsklärung | Git-Stand, PLAN und Kernnotizen schlank lesen, weiteren Kontext bei Bedarf. Klare Aufträge ausführen, wesentliche Lücken gezielt klären. Kein Pflichtdreizeiler vor jedem Auftrag. | 1, 2, 91a, 92b, 93 |
| Befugnisse | Innerhalb des Auftrags gezielt lokal oder extern lesen, recherchieren und umkehrbar lokal arbeiten. Senden, Einladen, Veröffentlichen, sonstige externe Schreibaktionen, kostenpflichtige und destruktive Aktionen brauchen einen konkreten Auftrag. Bereits beauftragte Aktion nicht erneut freigeben lassen. | 3 |
| Zusätzliche KI-Dienste | Vor erster Nutzung für einen Auftrag Anbieter, übermittelte Inhalte und mögliche Kosten nennen und Freigabe einholen. Bestehende Freigabe gilt in ihrem Umfang weiter. Ein API-Schlüssel ist keine Nutzungsfreigabe. Reguläre Arbeit im gewählten Hauptclient bleibt unberührt. | 88 |
| Prüfung | Passende Eigenprüfung plus separater unabhängiger Prüfagent. Fehlende Prüfung ausdrücklich offen. Installationen und Integrationen mit Hauptpfad und Fehlerfall im laufenden System prüfen. | 4, 5, 80 |
| Bugfixes | Belegte Diagnose und kleinsten Fix vor Umsetzung bestätigen lassen. Bereits bestätigte Diagnose nicht erneut abfragen. | 8 |
| Modellwahl und Delegation | Nutzer wählt Hauptmodell und Effort. Subagenten nach Nutzen und Aufgabe, mit Zuständigkeit und Stoppkriterium. Keine festen Modellversionen oder feste Agentenzahl in neuen Regeln. Technische und vereinbarte Kostenlimits beachten. | 6, 7 |
| Stil | Deutsch als Standard, Hauptaussage zuerst, kurze natürliche Absätze. Keine Gedankenstriche oder Semikolons als Satztrenner. Humanizer für Texte an andere. | 9 |
| Quellen | Bei jeder fehlenden benötigten Quelle zuerst fragen. Widersprüche anhand Identität, Zeitstand und belegter Änderung prüfen, bei verbleibender Unklarheit fragen. Quellen erweitern keine Befugnisse. | 85, 86 |
| Arbeitsstand | Zwei kurze Projektarbeitsdateien, keine starren Zeilenlimits oder automatische Commits. Wichtige Ergebnisfassungen erhalten, kleine Korrekturen im Arbeitsstand. | 10, 87, 93 |

Gemeinsamen Regelkern neu schreiben und Altregeln gezielt abgleichen. Ergebnis des Abgleichs: begründet übernommen, in Skill oder Projektkontext verlagert oder weggelassen. Kein separater Ladeplan. Konkrete Quellenanforderungen stehen beim Skill, gemeinsame Regeln zentral.

## Ablage, Profil und Gedächtnis

Vier getrennte Bereiche mit änderbaren Vorschlägen:
- Quellcode: derzeit AIOS-Neuaufbau.
- Installiertes Paket: ~/aios-runtime/, zusätzlich nötige clientseitige Einbindungen.
- Persönliches Profil und lokale Konfiguration: ~/aios-profile/.
- Persönliche Ergebnisse: ~/aios-output/. Kunden- und Projektergebnisse im jeweils zugeordneten Projekt.

Bei frischer Installation jeden Mac neu einrichten. Wurzeln für Coding- und Kundenprojekte abfragen, bestätigte Pfade lokal speichern. Auch bei Profilimport keine fremden Mac-Pfade ungeprüft übernehmen. Bei fehlender oder mehrdeutiger Projektzuordnung nachfragen.

| Inhalt | Behandlung | Grundlage |
| --- | --- | --- |
| Profil | Geführt mit Vorschau einrichten. Name, Rolle, Sprache, Zeitzone, Arbeitszeiten, Arbeitsweise und Prioritäten. Unbeantwortetes bleibt offen. | 14 |
| Projektregister | Private Markdown-Vorlage mit Kürzel, Ordner, optional Repo und Jira-Präfix, Status. Nur leere Vorlage ausliefern. | 13, 17 |
| Profilpflege | Dauerhafte Änderungen bestätigen. Ausdrückliches „Merk dir das“ genügt bei klarem Inhalt und Ziel. Kleine ausdrücklich genannte Vorlieben automatisch speichern und mitteilen. Keine Vermutungen, sensiblen Angaben, Befugnisse oder Regeländerungen automatisieren. | 15, 18 |
| Fachwissen | Getrennte Markdown-Wissensablage mit Index, Quelle, Datum und Unsicherheiten. Speicherung nach Bestätigung, keine automatischen Vollimporte. | 17, 19 |
| Chatsuche | Gezielter Auftrag, nur freigegebene Verläufe, Fundstellen nennen. Clientzugriff prüfen. Keine Übernahme von Historie als aktuelle Regeln. | 20 |
| Profiltransfer | Bewusster Export und Import mit Änderungsvorschau. Keine Zugangsdaten. Lokale Pfade je Mac zuordnen. | 16, 90a |
| Zugangsdaten | Vorhandene Anmeldewege nutzen. Lokale .env außerhalb des Pakets, nur für den Nutzer les- und schreibbar, keine Geheimnisse in Export oder Diagnoseausgabe. Bestehende Werte erhalten, Eingabe überspringbar. Variablenübergabe je Verbindung prüfen. | 83, 84 |
| Aktionsjournal | Minimale lokale Ausführungsspur mit Dienst, Ziel, Kennungen, Zeitpunkt und Status. Ungewissen Ausgang nachlesen, nicht blind wiederholen. Keine vollständigen Nachrichten, Transkripte oder Geheimnisse. Keine zweite Aufgabenliste. | 115 |

Wissensablage und technische Zustandsdateien gehören zu den privaten Daten, nicht in aktualisierbare Paketdateien. Ihre konkreten Unterordner werden bei der technischen Umsetzung festgelegt. Updates und Deinstallation dürfen diese Daten nicht stillschweigend entfernen.

## Ausgewählte Fähigkeiten

Die Gruppen bestimmen nur die Reihenfolge der Entwicklung, keine installierbaren Wahlmodule.

| Bereich | Enthaltene Fähigkeiten und Grenzen | Entscheidungen |
| --- | --- | --- |
| Arbeitsassistenz | Tagesstart mit kurzem neuem Briefingverlauf, eindeutige Terminvorbereitung, Nachbereitung aus Notizen oder ausgewähltem Transkript. Belegte Zuständigkeiten und Fristen. Keine automatischen Folgeaktionen. | 31 bis 33, 97 bis 100 |
| Aufgaben und Planung | To Do als führende persönliche Aufgabenquelle, Jira für Tickets. Aufgabenassistenz, Tages- und separat aufrufbare Wochenplanung. Planung zunächst Vorschlag, konkrete Änderungsaufträge direkt im beauftragten Umfang. Keine feste Auslastungsquote. | 23, 25, 34, 37, 101, 102a |
| Persönliches Coaching | Wochenreview zu Erfolgen, Stärken und Schwierigkeiten, konstruktive Vorschläge, gemeinsam höchstens ein Wochenexperiment. Tatsächliche Wirkung erfragen. Kein pauschales Lesen aller Chats. | 35, 103 |
| System-Retro | Fehler, Aufwand und Ablageregeln mit Originalbelegen prüfen. Ursachen und Vermutungen trennen. Empfehlungen ändern nichts automatisch. | 36, 104 |
| Auftragsvorbereitung | Ein Skill für normale und längere autonome Aufträge. Ergebnis, Abnahme, Kontext, Befugnisse und bei Bedarf Budgets und Blockaden. Kein Start des vorbereiteten Auftrags. | 39, 40, 94a, 95b |
| Prompt-Berater | Separater Diagnose-Skill aus ausgewählten GPT-/Fable-Bausteinen. Keine festen Modellversionen, keine doppelte Pflege allgemeiner Regeln. Anbieterhinweise nur bei Bedarf. | 41a, 96a |
| Konzepte und Prozessanalyse | Quellengebundene Konzepte mit Machbarkeit und Pilot. Ishikawa mit belegten Beobachtungen und Hypothesen. Maßnahmen und Wirtschaftlichkeit nach Auftrag, Zeitgewinn von Geldersparnis trennen. Renderer separat prüfen. | 42, 43, 105, 106 |
| Unterlagen und HTML-Folien | Zielgruppe und Lernziel, Trainer- und Teilnehmerinformationen trennen. Blockbrain-Design mit Offline-HTML, Navigation und visueller Prüfung. Keine sachlichen Referenzinhalte kopieren. | 44, 45, 107, 108 |
| Video | Bestehenden Lernvideo-Umfang übernehmen. Benötigte HyperFrames-Bestandteile prüfen, nur notwendige Anpassungen für Portabilität und bestätigte Regeln. Verbesserungen später. Skriptfreigabe und Freigabe zusätzlicher Dienste erhalten. | 46, 46a, 54, 88 |
| Dokumente | PDF lesen und erstellen. DOCX, XLSX und PPTX lesen, erstellen und gezielt bearbeiten. Visuelle Prüfung, Formeln prüfen, keine ungefragten Makros oder externen Datenverbindungen. Kein Versprechen verlustfreier HTML/PPTX-Umwandlung. | 55 bis 58, 114 |
| Recherche | Iterative vertiefte Recherche, Gegenargumente und Quellenqualität prüfen. Keine feste Fragen- oder Quellenzahl, keine pauschale zusätzliche Planfreigabe. | 59, 111 |
| Zeiterfassung | Lokale Arbeitsspuren nur aus ausgewählten Projekt- und Sitzungsquellen. Zeitfenster sind keine abrechenbare Dauer. Gemeinsamer Wochen-/Monatsablauf, Vorschau, beauftragte Planhat-MCP-Buchung als Entwurf, Dublettenprüfung und Nachlesen. Endgültig manuell einreichen. | 48 bis 50, 109, 110a |
| Coding-Reviews | Fremd-PR-Review mit Repo-Standards zuerst, eigener unabhängiger Precommit-Review und Kommentar-Triage getrennt. Repo-Regeln referenzieren, keine Kopien. GitHub-Schreibaktionen nur beauftragt. | 61 bis 64 |
| Frontend und Diagnose | Frontend-Gestaltung mit vorhandenem Designsystem, responsiver Darstellung, Barrierefreiheit und Live-Prüfung. Sentry und Datadog gezielt lesen und diagnostizieren, keine automatische Überwachung oder Konfigurationsänderung. | 69 bis 71 |
| Skill-Builder | Eigenständig mit notwendigen Format- und Verhaltenstests sowie unabhängiger Prüfung. Geprüfte Hilfsplugins optional. Keine Pflichtabhängigkeit von allgemeinem Skill-Creator. | 51, 112 |
| AIOS-Audit | Je Client vorhanden, geprüft, eingeschränkt oder fehlend mit Beleg und nächstem Schritt. Vergleich zum Vorlauf, kein altes Punktesystem. Kanonische Regeln, Spiegel und Einbindung prüfen. | 52, 72a, 80, 113 |

Ein gemeinsamer Einstieg darf passende Teilabläufe bündeln. Die genaue Anzahl und technischen Namen der Skills werden bei der Umsetzung bestimmt. Keine bestätigte Fähigkeit darf dabei entfallen. Alle Routinen starten zunächst manuell.

## Verbindungen und Abhängigkeiten

| Verbindung | Gewählter Umfang | Technischer Stand |
| --- | --- | --- |
| Outlook Calendar, Microsoft To Do | Lesen und konkret beauftragte Änderungen | In beiden Clients zu prüfen |
| Outlook Mail, Slack, Teams | Gezielt lesen, Entwürfe, konkret beauftragte Aktionen | In beiden Clients zu prüfen |
| Jira, Confluence | Gezielt lesen, Entwürfe und konkret beauftragte Änderungen | In beiden Clients zu prüfen |
| Planhat | MCP-Buchung als Entwurf, endgültig manuell einreichen | Nutzer meldet Verbindung in Blockbrain. Kein Nachweis für Claude Code oder Codex |
| GitHub | Lesen und ausdrücklich beauftragte Git-/GitHub-Aktionen, CLI oder MCP passend wählen | In beiden Clients zu prüfen |
| Sentry, Datadog | Lesen und Diagnose | Zugang, Rechte und Toolumfang offen |
| Blockbrain | Geeignete freigegebene Agenten oder Workflows auf Auftrag aufrufen | Aufnahme bedingt durch Nutzen-, Rechte- und Funktionstest. Kein Atrio-Plugin |
| Browser | Eigene Chrome-Sitzung über Chrome DevTools MCP, Konsole und Netzwerk prüfen | Einrichtung und Clientfunktion offen. Kein Browserstart in dieser Etappe |

Alle gewählten Fähigkeiten installieren, fehlende Dienstanmeldungen als nicht eingerichtet kennzeichnen. Entscheidung 85 gilt bei benötigten Quellen im konkreten Arbeitsauftrag. Sie verhindert nicht die ausdrücklich erlaubte Installation ohne Zugangsdaten.

Dokumentwerkzeuge und weitere Fremdabhängigkeiten aus geeigneten Originalquellen nach Lizenz-, Versions- und Funktionsprüfung wählen. Native Werkzeuge direkt verwenden und den getesteten Stand festhalten. Vom AIOS verwaltete Abhängigkeiten nur über geprüfte Updates ändern. Der AIOS-Installer kontrolliert keine vom Client unabhängig aktualisierten Werkzeuge.

## Bereinigte oder ersetzte Vorgaben

| Frühere Vorgabe oder Vorschlag | Maßgeblicher Stand |
| --- | --- |
| Alle alten Regeln kopieren, Startkontext mit allen Paketentscheidungen | Regelkern neu schreiben und Altbestand gezielt abgleichen (91a) |
| Separater zentraler Ladeplan | Entfällt (92b), Skillquellen gezielt referenzieren |
| Auftrag und Goal-Vorbereitung als getrennte Skills | Zusammengeführt (95b), Diagnose-Berater getrennt (96a) |
| Feste Modellversionen, Haiku-Verbot, feste Subagentengrenze | Persönliche Hauptmodellwahl und aufgabenbezogene Delegation (6, 7), aktuelle Nutzerfreigaben |
| Automatisches Umplanen bei allgemeinem Planungsauftrag | Vorschläge, Änderungen nur konkret beauftragt (102a) |
| Fehlende Quellen nur melden und automatisch fortfahren | Zuerst nachfragen (85), Installation ohne Schlüssel bleibt erlaubt (84) |
| Automatische dauerhafte Wissens- oder Regelübernahme | Bestätigung, nur kleine explizite Vorlieben mit enger Ausnahme (15 bis 19) |
| Feste Archive im Quellbaum oder in ~/aios | Getrennte Ergebnis- und Projektablage (11 bis 13, 90, 90a) |
| Punktesystem im Audit | Status mit Belegen (113) |
| Wählbare Funktionsmodule, Basis zuerst und Erweiterung später | Alle bestätigten Fähigkeiten für gewählte Clients (74, 75). Alte Paketaufträge sind historisch |
| Pauschale Übernahme bestehender Plugins oder Zeitpläne | Nur ausgewählte Fähigkeiten, Zeitpläne später (38, 53, 65a bis 73) |

Native Regelprüfung gemäß 72a ist eine gewünschte Nutzung. Den konkreten Claude-Befehl und den passenden Codex-Weg vor Umsetzung anhand der dann verfügbaren Clients verifizieren. Diese Konsolidierung behauptet keine aktuelle Unterstützung von /doctor prompt-audit.

## Nicht Bestandteil der ersten Version

SharePoint, OneDrive, Bau neuer Blockbrain-Workflows, Atrio-Ausbau, automatische Zeitpläne, Lernvideo-Verbesserungen und automatische Profilsynchronisation bleiben zurückgestellt. Context Mode, Context7 und Claude-Mem bleiben spätere Evaluierungskandidaten. Kein Superpowers-Gesamtplugin, nur ausgewählte Methoden. Übrige Sammelplugins erst bei konkreter Lücke.

Kein separater Regelpflege-Skill, kein separater Ladeplan, kein Tagesabschluss oder monatlicher Modellcheck allein aufgrund ihrer Nähe zu ausgewählten Skills. Kein allgemeiner Import alter Erinnerungen, Archive oder Profile. Profiltransfer ist davon getrennt. Nicht ausgewählte Fremdwerkzeuge werden nicht automatisch übernommen.

Keine Wiederherstellung einer Paketversion in Version eins. Sicherungen betroffener Konfigurationsdateien bleiben vorgesehen und sind keine getestete Rollback-Funktion.

## Umsetzung und Abnahme

| Etappe | Arbeit und Abschlusskriterium |
| --- | --- |
| 1. Konsolidierung | Entscheidungen, Umfang und Quellenzuordnung konsistent. Unabhängiger Abgleich, Befunde behoben und nachgeprüft. Keine Implementation durch diesen Schritt. |
| 2. Grundlage | Kurzer neuer Regelkern mit Altvergleich, leere Profil-/Register-/Wissensvorlagen, lokale Pfadkonfiguration, Profilexport/-import und minimale Clientanbindung. Tests für getrennte Ablage, fehlende/mehrdeutige Zuordnung, Bestätigung und Geheimnisausschluss. |
| 3. Fähigkeiten | Vorlagen gruppenweise überarbeiten, technische Abhängigkeiten auswählen. Passende synthetische Verhaltenstests und unabhängiger Review je Gruppe. Falsche Auslöser, fehlende Quellen, Befugnisgrenzen und Fehlerfälle prüfen. |
| 4. Installer und Betrieb | Begrenzter Vorabcheck, Vorschau, Sicherung betroffener Konfiguration, Client-/Pfadwahl, überspringbare Anmeldung, Statuscheck, manuelle Updates und gezielte Deinstallation. Eigene Einbindungen erkennen, fremde und lokal geänderte Inhalte schützen. |
| 5. Laufende Systeme | Frische und wiederholte Installation, typische Skillaufrufe und Fehlerfall in beiden Clients. Integration mit Verbinden, typischem Aufruf, Trennen und Fehlerfall nachweisen. Statuscheck ohne externe Schreibaktionen. Schreibtests nur mit konkretem Testauftrag. |
| 6. Übergabe | README mit getesteten Befehlen und Nutzungstabelle: Zweck, Beispielauftrag, Verbindungen, geprüfter Aufruf je Client. Fehlende Zugänge und offene Abnahmen sichtbar. GitHub erst mit konkretem Ziel und Veröffentlichungsauftrag, danach frische Installation auf zweitem Mac prüfen. |

Für Updates prüfen: Vorschau, Konflikterkennung, Erhalt von Profil und Ergebnissen, Funktion danach und ehrlicher Fehlerstatus ohne Rollbackversprechen. Für Deinstallation prüfen: Vorschau und Bestätigung, nur eigene unveränderte Bestandteile entfernen, Profil, Ergebnisse, Projektdateien und gemeinsam genutzte Programme erhalten.

Technische Prüfprotokolle enthalten Zeit, Paket-/Clientversion, Prüfschritte und Fehler. Keine Geheimnisse oder abgerufenen Gesprächs-, Mail- oder Dokumentinhalte. Aktionsjournal und technisches Prüfprotokoll haben unterschiedliche Zwecke.

## Offene technische Nachweise

- Tatsächliche Regel- und Skill-Einbindung, Authentifizierung und Werkzeugrechte je Client.
- Konkrete Dokument-/Video-Abhängigkeiten und Lizenzen, Renderer und benötigte lokale Programme.
- Zielgerichtete Chatsuche und belastbare Importerkennung bei Arbeitsspuren mit synthetischen Daten.
- Minimaler Journaling-Vertrag und Prüfung ungewisser Schreibausgänge ohne Inhaltsvollspeicherung.
- Portabler Ablageprüfer und Registervalidierung. Bekannten festen Lernvideo-Ausgabepfad als Negativfall erhalten und neue konfigurierbare Ablage positiv prüfen.
- Alle Funktions- und Installationstests des Neuaufbaus, unabhängig vom alten Paketstand.

Diese Punkte sind Implementierungs- und Prüfaufgaben, keine offenen Grundsatzentscheidungen. Nur ein tatsächlicher Konflikt mit den Beschlüssen oder eine notwendige Umfangsänderung erfordert eine neue Nutzerentscheidung.

## Grenze des aktuellen Auftrags

Nach abgeschlossener Konsolidierung ist die selbstständige lokale Umsetzung der gemeinsamen Grundlage beauftragt. Aktive Regeln, Verbindungen und Installationen bleiben unverändert. Kein Browserbetrieb, keine Kundendaten und keine Migration. Kein neues Repository, keine Commits oder Pushes. Echte Umfangskonflikte oder nötige Zugänge gezielt klären, bereits bestätigte Entscheidungen nicht erneut abfragen.
