# Lokales Runtime-Testpaket bauen

`scripts/paket_bauen.py` erstellt einen neuen, in sich nutzbaren Testordner. Der Befehl installiert nichts, startet keinen Client, erzeugt keine globalen Links und nutzt kein Netzwerk.

```sh
python3 scripts/paket_bauen.py --destination /absoluter/pfad/zum/neuen-testpaket
python3 scripts/paket_bauen.py --destination /absoluter/pfad/zum/neuen-testpaket --apply
```

Der erste Aufruf zeigt nur eine Vorschau. `--apply` verlangt danach die Eingabe `ja`. Der Zielordner muss neu sein und sein Elternordner bereits existieren. Ein vorhandenes Ziel bleibt unverändert. Das Paket wird zunächst in einem privaten Nachbarordner vorbereitet und anschließend ohne Überschreiben übernommen.

Das Paket enthält die nach der gemeinsamen Paketpfadregel zulässigen Dateien unter `allgemein/` sowie die in `scripts/paketregeln.py` ausdrücklich ausgewählten Laufzeitskripte. Dazu gehören Profil- und Pfadhelfer sowie die benötigten Helfer des installierten Statuschecks. Zusätzlich entstehen `AGENTS.md`, `CLAUDE.md` und `paket.json`. Die Clientdateien stammen aus demselben Regelkern und verweisen auf die enthaltenen Referenzen. `paket.json` enthält Version und SHA256 je Paketdatei, aber keine Benutzerpfade. Es verzeichnet sich selbst nicht.

Symlinks und erkannte Geheimnisdateien in den Paketquellen werden vor dem Inhaltslesen abgewiesen. Dazu gehören fehlplatzierte private Laufzeitdateien wie `profil.md`, `projekte.md`, `pfade.json` sowie private Ordner für Zustand, Wissen, Projekte und Ergebnisse. Ausdrücklich bekannte leere Vorlagen unter `allgemein/vorlagen/` und `.env.example` sind erlaubt. `__pycache__`, Tests, Inventare, Entwicklungsdokumente, Profile und bestehende Installationen werden nicht eingepackt. Diese Dateigrenze ist keine perfekte Erkennung von Geheimnissen in beliebigem Freitext. Die Paketprüfung ersetzt keine spätere Installation und keinen Funktionstest in einem Client.
