# Bewusster Profiltransfer

`scripts/profile_transfer.py` überträgt die sieben strukturierten Angaben aus dem Profildokument und die Tabelle „Kleine Vorlieben“ (bei `en`: „Small preferences“). Der Export ist eine einzelne JSON-Datei mit `schema_version: 1`. Weitere Abschnitte der Profildatei werden nicht übernommen.

```sh
python3 scripts/profile_transfer.py export --profile-dir ~/aios-profile --output ./mein-profil.json
python3 scripts/profile_transfer.py export --profile-dir ~/aios-profile --output ./mein-profil.json --apply
python3 scripts/profile_transfer.py import --input ./mein-profil.json --profile-dir ~/aios-profile
python3 scripts/profile_transfer.py import --input ./mein-profil.json --profile-dir ~/aios-profile --apply
```

Ohne `--apply` erscheint nur eine Vorschau. Mit `--apply` wird nach der Vorschau genau `yes` als interaktive Bestätigung verlangt. Eine vorhandene Exportdatei wird nicht überschrieben. Beim Import zeigt die Vorschau abweichende Zielwerte und die Zahl der Vorlieben. Ein vorhandenes Profildokument (`profil.md` bei `de`, `profile.md` bei `en`) wird erst nach Bestätigung ersetzt und vorher als private Sicherung mit dem Zusatz `.backup-*` im Zielordner erhalten. Die Exportdatei und Sicherung haben Rechte `0600`. Ein neu angelegter Profilordner hat Rechte `0700`. `--language` bestimmt die Sprache des Profilordners ausdrücklich. Ohne diese Option folgt der Transfer den vorhandenen Dateinamen im Profilordner und verlangt `--language` für einen leeren oder neuen Ordner.

Der Transfer liest für den Export ausschließlich das Profildokument. `.env`, Zugangsdaten, die Pfadkonfiguration, das Projektregister, Wissen, Journal, Diagnoseprotokolle und Ergebnisse werden weder gelesen noch übertragen. Das Projektregister bleibt je Mac lokal. Projektwurzeln, Ordner und sonstige Pfade müssen auf dem Ziel-Mac neu eingerichtet und bestätigt werden. Es gibt keinen automatischen Import oder Abgleich.

Persönlicher Freitext in den ausgewählten Feldern und Vorlieben lässt sich nicht zuverlässig automatisch auf Geheimnisse prüfen. Die angezeigten Angaben und die JSON-Datei vor der Weitergabe selbst prüfen. Für Austausch und Ablage einen privaten Speicherort wählen. Unbekannte JSON-Felder, doppelte Schlüssel, ungültige Typen und symbolische Links werden abgewiesen.

Vor der Vorschau werden beide Ausgabeformate auf die Lesegrenze von 128 KiB geprüft. Ein Export darf nicht größer werden, als der eigene Import lesen kann. Zeilenumbrüche, Steuerzeichen, Unicode-Zeilentrenner und äußere Leerzeichen in importierten Werten werden abgewiesen, damit der Markdown-Rückweg Angaben nicht still verändert.

Steuer- und Formatzeichen in Profilwerten werden vor der Vorschau abgewiesen. Beim Ersetzen nutzt der Import eine zufällig benannte, exklusiv angelegte temporäre Datei. Bereits vorhandene Dateien mit ähnlichem Namen bleiben erhalten.
