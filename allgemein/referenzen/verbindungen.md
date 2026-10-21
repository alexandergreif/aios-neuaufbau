# Verbindungen und tatsächliche Fähigkeiten

Ein installierter Skill belegt keinen verfügbaren Dienstzugang. Prüfe die tatsächlich im gewählten Client angebotenen Werkzeuge, den angemeldeten Dienst und die für den konkreten Auftrag nötigen Rechte. Ein Zugang in Blockbrain oder im anderen Client ist kein Nachweis für diesen Client.

Für die erste Version sind folgende Verbindungen ausgewählt. Diese Liste dokumentiert den gewünschten Umfang, keine bereits eingerichteten Verbindungen:

| Dienst | Gewünschter Umfang | Zuständigkeit und Grenze |
| --- | --- | --- |
| Outlook Calendar | Termine gezielt lesen, konkret beauftragte Änderungen | Ausgewählte Kalender, Zeitraum und Zeitzone beachten. |
| Microsoft To Do | Persönliche Aufgaben lesen und beauftragt bearbeiten | Führende persönliche Aufgabenliste. Erkannte Aufgaben zuerst vorschlagen. |
| Outlook Mail | Gezielt suchen, lesen und Entwürfe erstellen | Senden und Postfachänderungen nur konkret beauftragt. |
| Jira | Tickets und Projektstände lesen, beauftragte Änderungen | Führende Quelle für Tickets. Keine zweite persönliche Aufgabenliste. |
| Slack | Relevante Nachrichten und Threads lesen, Entwürfe | Externe Schreibaktionen nur konkret beauftragt. |
| Microsoft Teams | Relevante Chats und Kanalbeiträge lesen, Entwürfe | Verfügbare Such- und Schreibmöglichkeiten tatsächlich prüfen. |
| Confluence | Seiten suchen, lesen und Entwürfe vorbereiten | Veröffentlichen und bestehende Seiten ändern nur konkret beauftragt. |
| Planhat | Freigegebene Zeiteinträge per MCP als Entwurf übertragen und prüfen | Endgültiges Einreichen bleibt manuell. |
| GitHub | Repositories, Issues, PRs und Prüfstände lesen | Commits, Pushes und andere GitHub-Schreibaktionen nur beauftragt. |
| Sentry | Ausgewählte Fehler lesen und diagnostizieren | Keine automatische Behebung oder Änderung der Überwachung. |
| Datadog | Ausgewählte Logs, Metriken und Traces lesen und diagnostizieren | Keine Änderungen an Monitoren oder Konfiguration. |
| Blockbrain | Vorhandenen technischen Zugang für ausgewählte Agenten und Workflows prüfen | Aufnahme hängt von belegtem Nutzen, Rechten und Funktion ab. Kein Atrio-Pluginimport. |

SharePoint und OneDrive sind zunächst zurückgestellt. Es gibt keine dauerhafte Überwachung oder automatische Komplettsynchronisation dieser Dienste.

Fehlt eine benötigte Quelle oder Fähigkeit, benenne die konkrete Lücke und frage vor der Arbeit mit eingeschränkter Grundlage nach. Ein ähnliches Werkzeug oder ein gleichnamiger Dienst ersetzt die benötigte Quelle nicht stillschweigend. Widersprüche nach Aktualität, Kontext und belegten Änderungen prüfen. Verbleibende relevante Unklarheiten mit Quellen zur Entscheidung vorlegen.

Die Einrichtung erfolgt dienstweise im jeweiligen Client. Verwende den vorgesehenen Anmeldeweg. Erforderliche API-Schlüssel gehören in die private lokale `.env`, niemals in Paketquellen, Profiltext oder Prüfberichte. Leere Felder und eine übersprungene Anmeldung sind zulässig und werden als noch nicht eingerichtet angezeigt. Schlüsselwerte nicht durch Inventuren oder Statusausgaben ausgeben.

Für externe Schreibaktionen gilt [externes-schreiben.md](externes-schreiben.md). Eine passende konkrete Beauftragung nicht erneut abfragen. Bei ungewissem Ausgang im Zielsystem nachprüfen und nicht blind wiederholen.
