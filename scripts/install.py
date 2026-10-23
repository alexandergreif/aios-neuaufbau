#!/usr/bin/env python3
"""Install the current local AIOS development state for the first time."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
from urllib.parse import quote

from setup_profile import reject_symlink_components
import install_plan as installationsplan
import build_package as paket_bauen
import languages
import package_inventory as bestand
import check_config as pruefer
import safe_files as sicher


class InstallError(Exception):
    pass


def file_snapshot(path):
    parent_fd, name = sicher.parent(path)
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent_fd)
    finally:
        os.close(parent_fd)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):
            raise InstallError("Configuration is not a regular file")
        with os.fdopen(os.dup(fd), "rb") as stream:
            data = stream.read()
        after = os.fstat(fd)
        identity = (before.st_dev, before.st_ino, before.st_mtime_ns, before.st_size)
        if identity != (after.st_dev, after.st_ino, after.st_mtime_ns, after.st_size):
            raise InstallError("Configuration changed while reading")
        return data, identity
    finally:
        os.close(fd)


def load_config(raw):
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=pruefer.unique_object)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise InstallError("Configuration is not valid JSON") from error


def check_profile(config_path, config, home):
    lang = languages.of_config(config)
    profile = pruefer.parse_path(config["paths"]["profile"], "paths.profile", home)
    reject_symlink_components(profile)
    if not profile.is_dir():
        raise InstallError("Confirmed profile folder must already exist")
    expected = profile / lang.config_name
    if config_path != expected:
        mismatch = languages.config_name_mismatch(config_path, profile, lang)
        raise InstallError(mismatch or f"--config must be the {lang.config_name} in the confirmed profile folder")
    source = pruefer.parse_path(config["paths"]["source"], "paths.source", home)
    if source != paket_bauen.PACKAGE.resolve(strict=True):
        raise InstallError("paths.source must point to this source package")
    state_dir = profile / lang.state_dir
    reject_symlink_components(state_dir)
    if state_dir.exists() and not state_dir.is_dir():
        raise InstallError(f"{lang.state_dir} is not a folder")
    for metadata in ("bestand.json", "operation.json"):
        target = state_dir / metadata
        if target.exists() or target.is_symlink():
            raise InstallError("Package inventory or package operation already exists")
    state_path = state_dir / "installation.json"
    if state_path.exists() or state_path.is_symlink():
        raise InstallError("Ownership file already exists")
    return state_dir, state_path


def check_configured_paths(config, home):
    for name in ("source", "runtime", "profile", "output"):
        raw = config["paths"][name]
        path = home / raw[2:] if raw.startswith("~/") else Path(raw)
        reject_symlink_components(path)


def ensure_directory(path, created):
    fd = sicher.directory(path, create=True, created=created)
    os.close(fd)


def write_exclusive(path, data, created=None):
    return sicher.exclusive_file(path, data, created=created)


class Journal:
    def __init__(self, path, state):
        self.path = Path(path)
        self.parent_fd, name = sicher.parent(path)
        self.name = name
        self.fd = None
        try:
            self.fd = os.open(name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                              0o600, dir_fd=self.parent_fd)
            self.identity = self._identity(os.fstat(self.fd))
            self.expected = b""
            self.save(state)
        except Exception:
            self.close()
            raise

    @staticmethod
    def _identity(info):
        return info.st_dev, info.st_ino

    def _check(self):
        sicher.assert_directory_at_path(self.path.parent, self.parent_fd)
        current = os.stat(self.name, dir_fd=self.parent_fd, follow_symlinks=False)
        if not stat.S_ISREG(current.st_mode) or self._identity(current) != self.identity:
            raise InstallError("Ownership file was replaced")
        if self._identity(os.fstat(self.fd)) != self.identity:
            raise InstallError("Ownership file was replaced")
        os.lseek(self.fd, 0, os.SEEK_SET)
        actual = b""
        while True:
            chunk = os.read(self.fd, 65536)
            if not chunk:
                break
            actual += chunk
        if actual != self.expected:
            raise InstallError("Ownership file was changed unexpectedly")

    def save(self, state):
        self._check()
        data = (json.dumps(state, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        os.lseek(self.fd, 0, os.SEEK_SET)
        os.ftruncate(self.fd, 0)
        offset = 0
        while offset < len(data):
            offset += os.write(self.fd, data[offset:])
        os.fsync(self.fd)
        self.expected = data
        self._check()

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
        if self.parent_fd is not None:
            os.close(self.parent_fd)
            self.parent_fd = None


def verify_owned(state, journal):
    """Check every created target through its absolute, link-free parent path."""
    journal._check()
    for raw in state["created_directories"]:
        fd = sicher.directory(raw)
        os.close(fd)
    runtime_fd = sicher.directory(state["runtime"])
    os.close(runtime_fd)
    for item in state["created"]:
        path = Path(item["path"])
        parent_fd, name = sicher.parent(path)
        try:
            info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            if item["type"] == "link":
                if not stat.S_ISLNK(info.st_mode) or os.readlink(name, dir_fd=parent_fd) != item["target"]:
                    raise InstallError(f"Created link missing or changed: {path}")
            else:
                if not stat.S_ISREG(info.st_mode):
                    raise InstallError(f"Created file missing or changed: {path}")
                if "inode" in item and (info.st_dev, info.st_ino) != (item["device"], item["inode"]):
                    raise InstallError(f"Created file was replaced: {path}")
                fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent_fd)
                try:
                    opened = os.fstat(fd)
                    if (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
                        raise InstallError(f"Created file was replaced: {path}")
                    digest = hashlib.sha256()
                    while chunk := os.read(fd, 65536):
                        digest.update(chunk)
                    if digest.hexdigest() != item["sha256"]:
                        raise InstallError(f"Created file was changed: {path}")
                finally:
                    os.close(fd)
            sicher.assert_directory_at_path(path.parent, parent_fd)
        finally:
            os.close(parent_fd)

def local_link(path):
    return f"(<{quote(str(path), safe='/')}>)"


def rule_content(core, runtime, config_path, language=languages.DEFAULT):
    """Global client rule: language header plus core rules with absolute reference links."""
    lang = languages.get(language)
    digest = hashlib.sha256(core).hexdigest()
    text = core.decode("utf-8")
    references = Path(runtime) / lang.references_path
    text = lang.rewrite_core_links(text, lambda name: local_link(references / name))
    profile = Path(config_path).parent / lang.profile_name
    header = (lang.generated_header(digest) +
              f"{lang.local_config_label}: [{lang.config_name}]{local_link(config_path)}\n\n"
              f"{lang.profile_link_label}: [{lang.profile_name}]{local_link(profile)}\n\n")
    return (header + text).encode("utf-8")


def install(plan, config_path, contents, state_dir, state_path, config=None, home=None):
    state = {"schema_version": 1, "version": paket_bauen.VERSION, "status": "installing",
             "runtime": plan["runtime"], "clients": plan["clients"],
             "created_directories": [], "created": []}
    ensure_directory(state_dir, state["created_directories"])
    journal = Journal(state_path, state)
    try:
        runtime = Path(plan["runtime"])
        ensure_directory(runtime.parent, state["created_directories"])
        journal.save(state)
        sicher.build_directory(runtime, contents)
        for relative, data in sorted(contents.items()):
            state["created"].append({"type": "file", "path": str(runtime / relative),
                                     "sha256": hashlib.sha256(data).hexdigest()})
        journal.save(state)
        ensure_directory(plan["output"], state["created_directories"])
        journal.save(state)
        lang = languages.get(plan["language"])
        core = contents[Path(lang.core_path)]
        generated = rule_content(core, runtime, config_path, lang.code)
        for item in plan["rules"]:
            target = Path(item["target"])
            ensure_directory(target.parent, state["created_directories"])
            def record_owned(info):
                item = {"type": "file", "path": str(target),
                        "inode": info.st_ino, "device": info.st_dev,
                        "sha256": hashlib.sha256(b"").hexdigest(), "incomplete": True}
                state["created"].append(item)
                return item
            write_exclusive(target, generated, created=record_owned)
            state["created"][-1]["sha256"] = hashlib.sha256(generated).hexdigest()
            state["created"][-1].pop("incomplete", None)
            journal.save(state)
        for item in plan["skills"]:
            target = Path(item["target"])
            ensure_directory(target.parent, state["created_directories"])
            source = Path(item["source"])
            sicher.exclusive_link(source, target)
            state["created"].append({"type": "link", "path": str(target), "target": str(source)})
            journal.save(state)
        verify_owned(state, journal)
        if config is not None:
            confirmed = bestand.make(config, home, plan["bindings"], contents, generated)
            bestand.validate(confirmed, config, home)
            for path, item in confirmed["owned"].items():
                bestand.check_target(path, item)
            bestand.publish(state_dir / "bestand.json", confirmed)
        state["status"] = "installed"
        journal.save(state)
        verify_owned(state, journal)
    except Exception:
        state["status"] = "failed"
        try:
            journal.save(state)
        except Exception:
            pass
        raise
    finally:
        journal.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--codex-home")
    parser.add_argument("--claude-config-dir")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    started = False
    try:
        if not args.home.is_absolute() or str(args.home).startswith("//"):
            raise InstallError("--home must be an absolute home folder")
        home = pruefer.resolve_directory_candidate(args.home, "--home")
        if not home.is_dir() or home == Path("/"):
            raise InstallError("--home must be an existing home folder")
        if not args.config.is_absolute() or ".." in args.config.parts:
            raise InstallError("--config must be absolute")
        config_path = args.config
        raw, config_identity = file_snapshot(config_path)
        config = load_config(raw)
        pruefer.validate(config, home)
        check_configured_paths(config, home)
        plan = installationsplan.plan(config, home, args.codex_home, args.claude_config_dir)
        state_dir, state_path = check_profile(config_path, config, home)
        language = plan["language"]
        snapshot = paket_bauen.source_snapshot(language)
        contents = paket_bauen.package_contents(snapshot, language)
        if plan["conflicts"] or plan["clarifications"]:
            raise InstallError("Pre-installation plan contains conflicts or open clarifications: " + " | ".join(plan["conflicts"] + plan["clarifications"]))
        print(f"New runtime: {plan['runtime']}")
        print(f"Language of rules and skills: {language}")
        print(f"Output: {plan['output']} (existing content is kept)")
        print(f"Profile is kept: {plan['profile']}")
        print(f"Rule files: {len(plan['rules'])}, skill links: {len(plan['skills'])}")
        print("Development state with the skills currently present. Client and service function unchecked.")
        if not args.apply:
            print("Preview. No files or folders created.")
            return 0
        try:
            answer = input("Run the first installation? Type exactly 'yes': ").strip()
        except (EOFError, KeyboardInterrupt):
            answer = ""
        if answer != "yes":
            print("Cancelled. No files or folders created.")
            return 0
        if file_snapshot(config_path) != (raw, config_identity):
            raise InstallError("Configuration changed after the preview")
        check_configured_paths(config, home)
        if paket_bauen.source_snapshot(language) != snapshot:
            raise InstallError("Package sources changed after the preview")
        if installationsplan.plan(config, home, args.codex_home, args.claude_config_dir) != plan:
            raise InstallError("Pre-installation plan changed after the preview")
        check_profile(config_path, config, home)
        started = True
        with bestand.operation_lock(state_dir):
            if file_snapshot(config_path) != (raw, config_identity):
                raise InstallError("Configuration changed after locking")
            if paket_bauen.source_snapshot(language) != snapshot:
                raise InstallError("Package sources changed after locking")
            if installationsplan.plan(config, home, args.codex_home, args.claude_config_dir) != plan:
                raise InstallError("Targets changed after locking")
            check_profile(config_path, config, home)
            install(plan, config_path, contents, state_dir, state_path, config, home)
        print("Development state with the skills currently present installed. Client and service function unchecked.")
        return 0
    except (InstallError, bestand.BestandError, pruefer.ConfigurationError, installationsplan.PlanError,
            paket_bauen.BuildError, languages.LanguageError, OSError, UnicodeError, KeyError) as error:
        prefix = "Partial installation, no automatic recovery" if started else "Installation not started"
        print(f"{prefix}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
