# Isolierten Client-Testarbeitsordner vorbereiten

Der Generator legt einen neuen Arbeitsordner für einen späteren lokalen Test mit Codex oder Claude Code an. Er bindet keine Regeln global ein, installiert keinen Client und ruft keinen Client auf.

```sh
python3 scripts/prepare_client.py --destination /absoluter/pfad/zum/neuen-testordner
python3 scripts/prepare_client.py --destination /absoluter/pfad/zum/neuen-testordner --apply
```

Der erste Aufruf zeigt nur die Vorschau. `--apply` verlangt danach die Eingabe `yes`. `--language de` oder `--language en` wählt die Sprache der Regeln, ohne Angabe gilt `de`. Der Elternordner muss existieren. Ein vorhandenes Ziel sowie symbolische Links im Zielpfad oder in den Paketquellen werden abgewiesen.

Der Zielordner enthält ausschließlich `allgemein/regeln/kern.md`, `allgemein/referenzen/externes-schreiben.md` und `allgemein/referenzen/profil-und-wissen.md` (bei `en`: `general/rules/core.md`, `general/references/external-writes.md`, `general/references/profile-and-knowledge.md`), gelesen aus `de/` beziehungsweise `en/`, dazu `AGENTS.md` und `CLAUDE.md`. Die beiden Clientdateien haben denselben Kerntext. Ihre relativen Verweise zeigen auf die mitkopierten Referenzen. Ein Kommentar nennt die Paketquelle und den SHA256-Wert des ursprünglichen Regelkerns. Persönliche Profile, lokale Konfiguration und Skills aus einer Altinstallation werden nicht übernommen.
