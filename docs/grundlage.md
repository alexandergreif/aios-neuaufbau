# Lokale gemeinsame Grundlage

Stand: 19.10.2026. Diese Dateien sind Paketquellen im Neuaufbau. Einrichtung, Profiltransfer und Registerprüfung sind lokal umgesetzt. Die Regelladung wurde in beiden Clients isoliert nachgewiesen. Aktive Regeln wurden nicht ersetzt.

| Bestandteil | Datei | Stand |
| --- | --- | --- |
| Gemeinsamer Regelkern | [kern.md](../allgemein/regeln/kern.md) | Neu aus bestätigten Entscheidungen geschrieben |
| Abgleich alter Regeln | [regelabgleich.md](regelabgleich.md) | Alte Regelgruppen mit Quelle und Zeile begründet zugeordnet |
| Profilpflege und Wissen | [profil-und-wissen.md](../allgemein/referenzen/profil-und-wissen.md) | Ablauf und Datenzuständigkeit beschrieben |
| Externe Schreibaktionen | [externes-schreiben.md](../allgemein/referenzen/externes-schreiben.md) | Minimaler Journalablauf beschrieben, ausführbare Adapter offen |
| Profil und Projektregister | [profil.md](../allgemein/vorlagen/profil.md), [projekte.md](../allgemein/vorlagen/projekte.md) | Leere Vorlagen, keine privaten Angaben |
| Wissensnotizen | [Index](../allgemein/vorlagen/wissen/INDEX.md), [Notiz](../allgemein/vorlagen/wissen/notiz.md) | Leere Vorlagen |
| Projektarbeitsdateien | [PLAN](../allgemein/vorlagen/projekt/PLAN.md), [NOTIZEN](../allgemein/vorlagen/projekt/NOTIZEN.md) | Schlanke Vorlagen ohne starre Zeilengrenzen |
| Lokale Pfade | [Vorlage](../allgemein/konfiguration/pfade.vorlage.json), [Vertrag](pfadkonfiguration.md) | Vorschläge, ausdrücklich nicht bestätigt |
| Zugangsdaten | [.env.example](../allgemein/konfiguration/.env.example) | Leere Vorlage, kein eingerichteter Zugang |
| Pfadprüfung | [pruefe_konfiguration.py](../scripts/pruefe_konfiguration.py) | Ausführbarer read-only Prüfer mit synthetischen Tests |
| Geführte Einrichtung | [einrichten.py](../scripts/einrichten.py), [Anleitung](einrichtung.md) | Vorschau, Bestätigung, private Dateien, vorhandene Ziele geschützt |
| Profiltransfer | [profil_transfer.py](../scripts/profil_transfer.py), [Anleitung](profiltransfer.md) | Export und Import mit Vorschau, Sicherung und eng begrenzter Feldauswahl |
| Projektzuordnung | [pruefe_register.py](../scripts/pruefe_register.py), [Vertrag](projektregister.md) | Validierung und read-only Auflösung aktiver Zuordnungen |
| Clientvorbereitung | [client_vorbereiten.py](../scripts/client_vorbereiten.py) | Identische erzeugte Regeldateien aus einer Quelle, keine globale Installation |
| Native Regelladung | [Loaderprüfung](client-loader.md) | Vollständiger Kern und Negativkontrolle in beiden Clients nachgewiesen |

Die Vorlagen stehen nicht für eine bereits erfolgte Einrichtung. Die lokale Pfadkonfiguration muss erst außerhalb des Pakets erstellt und vom Nutzer bestätigt werden. Leere bestätigte Projektlisten sind möglich. Ein Source-Unterordner innerhalb einer Coding-Wurzel ist zulässig, spätere Projektsuchen müssen ihn aussparen. Pfadzuordnung erteilt keine Lesefreigabe für Projektinhalte.

## Ausgeführte technische Prüfungen

Aus dem Ordner AIOS-Neuaufbau:

```sh
python3 -m unittest discover -s tests -p 'test_konfiguration.py' -v
```

Ergebnis: 19 Tests bestanden. Die Tests verwenden ausschließlich synthetische temporäre Ordner und Konfigurationen. Sie prüfen gültige Auswahl, fehlende Bestätigung, unerlaubte Felder, doppelte JSON-Schlüssel, ungültige Pfade, Überschneidungen, Symlinks, Groß-/Kleinschreibung, Unicode-Normalformen, Benutzerordner-/Systemwurzel-Aliasse und ausbleibende Zielordneranlage.

Bewusst unbestätigte Paketvorlage:

```sh
python3 scripts/pruefe_konfiguration.py --config allgemein/konfiguration/pfade.vorlage.json
```

Erwarteter und beobachteter Fehlerfall: Exit 1 mit „Pfadkonfiguration ist noch nicht bestätigt.“ Dies ist eine erfolgreiche Negativprüfung, keine fehlgeschlagene Einrichtung eines Nutzerprofils.

Die Prüfung erkennt konservativ gleiche Schreibweisen auch auf case-sensitiven Dateisystemen. Sie prüft nicht Schreibrechte, native Clientfunktionen, die konkrete Projektzuordnung oder die Laufzeitwirkung des Regelkerns. Der unabhängige [Review](../pruefungen/grundlage-review.md) ist abgeschlossen: vier Fehler und zwei Empfehlungen behoben und gezielt nachgeprüft, keine offenen Befunde für diese lokale Grundlage. Die vollständige Etappe 2 bleibt wegen der folgenden Arbeiten offen.

## Erweiterte Abnahme

Die vollständige lokale Suite umfasst jetzt 50 grüne Tests. Einrichtung, Export, Import und Registerauflösung wurden zusätzlich als synthetischer CLI-Ablauf unabhängig geprüft. Alle belegten Reviewfehler sind behoben. Siehe [Einrichtungsreview](../pruefungen/einrichtung-review.md).

Die [native Loaderprüfung](client-loader.md) bestätigt das Laden des Kerns durch Codex 0.162.1 und Claude Code 2.1.300. Entfernte Regeldateien werden in der Negativkontrolle erkannt. Der lokale Claude-Testserver erzeugt einen kontrollierten Fehler. Diese Prüfung ruft kein Modell auf und ersetzt keine Verhaltensprüfung.

## Verbleibende Arbeit

- Globale Einbindung des Kerns in beide Clients und tatsächliche Modell-Verhaltenstests.
- Dienstadapter, ausführbares Aktionsjournal, Skills, Installer und Betriebsabläufe.

Keine Kundendaten oder alten Profile übernommen. Keine aktive Installation, globale Regeldatei oder Skill-Verknüpfung geändert. Keine GitHub-Veröffentlichung und kein Browserbetrieb.
