# Auf dem zweiten Mac starten

Voraussetzungen: Git, Python 3 und Claude Code im Terminal sowie GitHub-Zugriff auf das private Repository. Der Paketstand ist für die Abnahme vorbereitet. Dienstverbindungen und echte Modelltests stehen noch aus.

**1. Quellcode laden**

```sh
git clone https://github.com/alexandergreif/aios-neuaufbau.git "$HOME/aios-neuaufbau"
cd "$HOME/aios-neuaufbau"
```

**2. Isolierte Testinstallation starten**

```sh
AIOS_TEST_HOME="$(mktemp -d "$HOME/aios-test.XXXXXX")"
sh install.sh --home "$AIOS_TEST_HOME" --claude-config-dir "$AIOS_TEST_HOME/.claude"
```

Im Dialog **`claude`** wählen. Quellcode, Runtime, Profil und Ausgabe auf den vorgeschlagenen Werten lassen. Durch `--home` liegen die drei neuen Ablageorte im Testordner. Coding- und Kundenwurzeln leer lassen, nur Testprofilangaben verwenden und den Blockbrain-Schlüssel überspringen. Beide Vorschauen prüfen und jeweils mit `ja` bestätigen. Am Ende läuft der Dateistatuscheck.

**3. Claude Code mit der Testkonfiguration öffnen**

Im selben Terminal:

```sh
CLAUDE_CONFIG_DIR="$AIOS_TEST_HOME/.claude" claude --setting-sources user,project
```

Falls nötig, in dieser Testkonfiguration anmelden. Als ersten Auftrag `/auftrag-vorbereiten Plane einen einstündigen Lernblock für Python.` verwenden. Die Testinstallation erscheint nur in dieser Claude-Konfiguration. Den Testordnerpfad für die Fortsetzung festhalten.

Für Update, Deinstallation und die sechs Modellfälle: [Abnahme auf dem zweiten Mac](abnahme-zweiter-mac.md). Bei einem Konflikt stoppen und die Fehlermeldung festhalten. Vorhandene globale Regeldateien werden derzeit nicht ergänzt. Die normale Installation folgt nach erfolgreicher Testabnahme.
