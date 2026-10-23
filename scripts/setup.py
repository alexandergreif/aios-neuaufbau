#!/usr/bin/env python3
"""Guided entry point for the local AIOS first-time setup."""

import argparse
from pathlib import Path
import shlex
import shutil
import sys

import install
import languages
import profile_transfer as profil
import check_config as pruefer
import setup_profile
import setup_status


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
    parser.add_argument("--config", type=Path, help="Existing profile: run the installer with this configuration")
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--codex-home")
    parser.add_argument("--claude-config-dir")
    parser.add_argument("--language", choices=languages.CODES,
                        help="Language of rules and skills for a new profile. Asked interactively if omitted.")
    parser.add_argument("--apply", action="store_true", help="With --config: confirm after the preview")
    args = parser.parse_args(argv)
    if args.config is not None:
        if args.language is not None:
            parser.error("--language only applies to a new profile. With --config the language comes "
                         "from the configuration.")
        return install.main(argv)

    try:
        config = setup_profile.interactive(args.home, args.language)
    except (pruefer.ConfigurationError, profil.TransferError, OSError, EOFError,
            KeyboardInterrupt, UnicodeError) as error:
        if isinstance(error, (pruefer.ConfigurationError, profil.TransferError)):
            print(f"Setup cancelled: {error}", file=sys.stderr)
        else:
            print("Setup cancelled. No existing profile data was changed.", file=sys.stderr)
        return 1
    if config is None:
        return 0

    data = install.load_config(install.file_snapshot(config)[0])
    for client, binary in (("claude-code", "claude"), ("codex", "codex")):
        if client in data["clients"] and shutil.which(binary) is None:
            print(f"Note: {binary} is not available in PATH. The file integration can be set up anyway.")

    common = installer_args(config, args)
    status = install.main([*common, "--apply"])
    if status != 0:
        return status
    state = config.parent / languages.of_config(data).state_dir / "installation.json"
    if not state.is_file():
        command = ["sh", str(INSTALL_SH), *common, "--apply"]
        print("The confirmed profile is kept. Continue the installation with:")
        print(shlex.join(command))
        return 0

    print("Read-only status check of the file integration:")
    return setup_status.main(common)


if __name__ == "__main__":
    sys.exit(main())
