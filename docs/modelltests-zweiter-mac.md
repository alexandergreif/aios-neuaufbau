# Modelltests auf dem zweiten Mac

Entscheidung 116a: Angemeldete Tests finden erst auf dem zweiten Mac statt. Hier wurden bisher ausschließlich lokale Prüfungen und native Loaderproben mit einem absichtlich abbrechenden Testserver ausgeführt.

## Was dort zusätzlich geprüft wird

Nach einer erfolgreichen Installation und Anmeldung führen beide Clients die erfundenen Fälle aus [tests/verhalten/faelle.json](../tests/verhalten/faelle.json) aus. Bewertet werden tatsächliche Antworten und Werkzeugaufrufe, nicht nur die Anwesenheit von Regeldateien. Insbesondere müssen fehlende Quellen zu Rückfragen führen und unbelegte Zuständigkeiten offenbleiben.

Ein unabhängiger Prüfer bewertet die Ergebnisse. Modell, Denkaufwand, Clientversion, Paketstand und genaue Fälle werden dokumentiert. Zugangsdaten bleiben im vorgesehenen lokalen Anmeldeweg. Es werden weder Kundendaten noch echte Mails, Kalender oder Dienstkonten für diese ersten Fälle benötigt. Die späteren Dienstprüfungen bleiben eine eigene Abnahme.

## Anmeldung

Codex bietet den nativen Aufruf `codex login`, bei geeignetem Konto auch `codex login --device-auth`. Der Anmeldespeicher hängt von der Konfiguration ab. `cli_auth_credentials_store = "file"` verwendet beispielsweise `auth.json` unter `CODEX_HOME`. Diese Anmeldedatei wird nicht ins AIOS-Profil exportiert oder in Prüfberichte übernommen. [Offizielle Codex-Anmeldung](https://learn.chatgpt.com/docs/auth).

Claude Code bietet `claude auth login`, für das vorhandene Claude-Abonnement `claude auth login --claudeai`. Separate `CLAUDE_CONFIG_DIR`-Ordner unterstützen getrennte claude.ai-Anmeldungen. Keyless-Console-Anmeldungen sind davon laut Dokumentation ausgenommen und dürfen nicht als gleichartig isoliert behandelt werden. Auf einem frischen Mac ist eine zusätzliche Testanmeldung neben einer vorhandenen Installation nicht nötig. [Offizielle Claude-Code-Anmeldung](https://code.claude.com/docs/en/authentication).

Die Befehle wurden hier nur mit `--help` ohne Netzwerk und persönliche Konfiguration geprüft. Ein erfolgreicher Login auf dem zweiten Mac ist damit noch nicht nachgewiesen. Der konkrete Konto- und Anmeldeweg wird beim Einrichten dort gewählt, ohne Zugangsdaten in den Chat zu kopieren.

## Offene Abnahme

- Frische Installation auf dem zweiten Mac mit dessen Pfaden und ausgewählten Clients.
- Erfolgreiche native Anmeldung durch den Nutzer.
- Angemeldete Modelltests mit den dokumentierten synthetischen Fällen und unabhängiger Bewertung.
- Spätere Tests der benötigten Dienstverbindungen mit konkret freigegebenen Testquellen und Befugnissen.
