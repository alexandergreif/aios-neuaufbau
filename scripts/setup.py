#!/usr/bin/env python3
"""Geführter Einstieg für die lokale AIOS-Ersteinrichtung."""

import argparse
from pathlib import Path
import shlex
import shutil
import sys

import einrichten
import einrichtungsstatus
import installieren
import profil_transfer as profil
import pruefe_konfiguration as pruefer


INSTALL_SH = Path(__file__).resolve().parent.parent / "install.sh"


def installer_args(config, args):
    result = ["--config", str(config), "--home", str(args.home)]
    if args.codex_home is not None:
        result += ["--codex-home", args.codex_home]
    if args.claude_config_dir is not None:
        result += ["--claude-config-dir", args.claude_config_dir]
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, help="Vorhandenes Profil: bestehender Installer-Vertrag")
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--codex-home")
    parser.add_argument("--claude-config-dir")
    parser.add_argument("--apply", action="store_true", help="Mit --config nach Vorschau bestätigen")
    args = parser.parse_args(argv)
    if args.config is not None:
        return installieren.main(argv)

    try:
        config = einrichten.interactive(args.home)
    except (pruefer.ConfigurationError, profil.TransferError, OSError, EOFError,
            KeyboardInterrupt, UnicodeError) as error:
        if isinstance(error, (pruefer.ConfigurationError, profil.TransferError)):
            print(f"Einrichtung abgebrochen: {error}", file=sys.stderr)
        else:
            print("Einrichtung abgebrochen. Keine bestehenden Profildaten wurden geändert.", file=sys.stderr)
        return 1
    if config is None:
        return 0

    data = installieren.load_config(installieren.file_snapshot(config)[0])
    for client, binary in (("claude-code", "claude"), ("codex", "codex")):
        if client in data["clients"] and shutil.which(binary) is None:
            print(f"Hinweis: {binary} ist nicht im PATH verfügbar. Die Dateieinbindung kann trotzdem eingerichtet werden.")

    common = installer_args(config, args)
    status = installieren.main([*common, "--apply"])
    if status != 0:
        return status
    state = config.parent / "zustand/installation.json"
    if not state.is_file():
        command = ["sh", str(INSTALL_SH), *common, "--apply"]
        print("Das bestätigte Profil bleibt erhalten. Installation fortsetzen mit:")
        print(shlex.join(command))
        return 0

    print("Rein lesender Statuscheck der Dateieinbindung:")
    return einrichtungsstatus.main(common)


if __name__ == "__main__":
    sys.exit(main())
