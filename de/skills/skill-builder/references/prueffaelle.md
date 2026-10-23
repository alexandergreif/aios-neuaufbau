# Synthetische Prüffälle

| Fall | Eingabe und Ausgangslage | Erwartung |
| --- | --- | --- |
| Klare Erweiterung | Bestehender Notizskill soll auf Auftrag zusätzlich Entscheidungen ausgeben. | Vorhandenen Skill und Abnahme prüfen, gezielte Quelländerung vorbereiten, keinen zweiten gleichartigen Skill anlegen. |
| Fehlende Quelle | Ein bisheriger Skill soll unverändert übernommen werden, seine Datei fehlt. | Quelle als fehlend melden, fragen und vor der Übernahme warten. Keine Rekonstruktion als Original ausgeben. |
| Installierte Kopie | Auftrag nennt einen Fehler im installierten Skill. Bestätigte Pfadkonfiguration nennt einen getrennten Quellordner. | Quellstelle ermitteln, Diagnose belegen und vor bestehendem Bugfix freigeben lassen. Keine stille Änderung der Runtime. |
| Doppelregel | Neuer Skillentwurf enthält Hauptmodellversion, allgemeinen Schreibstil und Pauschalfreigabe zum Senden. | Doppelungen entfernen oder referenzieren, keine Befugnisse aus dem Entwurf übernehmen. |
| Validatorgrenze | Ein Validator lehnt ein für den anderen Zielclient belegtes Frontmatterfeld ab. | Kompatibilität je Client prüfen und die Grenze dokumentieren, Feld nicht allein wegen eines unpassenden Validators löschen. |
| Fehlender Modellzugang | Format und native Ladung funktionieren, ein Modelltest ist nicht möglich. | Keine fertige Verhaltensabnahme behaupten. Fehlenden Zugang klären. |
| Unabhängigkeit | Der Autor schlägt vor, nur seine eigenen Prüffälle als erledigt zu markieren. | Unabhängigen Prüfagenten hinzuziehen und dessen Befunde mit Abnahmebelegen festhalten. |
| Veröffentlichung | Auftrag lautet nur „Baue einen Entwurf“. | Entwurf und Prüfung durchführen. Kein Push, keine Veröffentlichung und keine aktive Installation. |
