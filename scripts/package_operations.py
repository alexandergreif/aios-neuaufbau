"""Limited package operations on confirmed own targets."""

import argparse
import errno
import os
from pathlib import Path
import sys
import uuid

import languages
import package_inventory as bestand
import safe_files as sicher


def operation_state(state_dir):
    path = state_dir / "operation.json"
    try:
        raw, _ = bestand.read_snapshot(path)
    except FileNotFoundError:
        return None
    state = bestand.decode(raw)
    if not isinstance(state, dict) or state.get("status") != "completed":
        raise bestand.BestandError("Open or failed operation. No automatic retry")
    return state


def load(config_path, home, codex=None, claude=None):
    if not config_path.is_absolute() or not home.is_absolute() or ".." in config_path.parts or ".." in home.parts:
        raise bestand.BestandError("--config and --home must be absolute")
    bestand.reject_symlink_components(home)
    if home == Path("/") or not home.is_dir():
        raise bestand.BestandError("Invalid home folder")
    raw_config = bestand.read_snapshot(config_path)
    config = bestand.decode(raw_config[0])
    paths = bestand.areas(config, home)
    lang = languages.of_config(config)
    if config_path != Path(paths["profile"]) / lang.config_name:
        mismatch = languages.config_name_mismatch(config_path, paths["profile"], lang)
        raise bestand.BestandError(mismatch or "Configuration is not in the confirmed profile")
    state_dir = Path(paths["profile"]) / lang.state_dir
    raw_state = bestand.read_snapshot(state_dir / "bestand.json")
    state = bestand.validate(bestand.decode(raw_state[0]), config, home, codex, claude)
    operation_state(state_dir)
    if state["status"] != "installed":
        raise bestand.BestandError("Package is already uninstalled")
    bestand.verify_manifest(state)
    return config, state, raw_config, raw_state, state_dir


def plan(action, config_path, home, codex=None, claude=None):
    config, old, raw_config, raw_state, state_dir = load(config_path, home, codex, claude)
    contents = {}
    snapshot = None
    if action == "update":
        import build_package as paket_bauen
        from install import rule_content
        lang = languages.of_config(config)
        if Path(old["paths"]["source"]) != paket_bauen.PACKAGE.resolve(strict=True):
            raise bestand.BestandError("Update must start from the confirmed source package")
        try:
            snapshot = paket_bauen.source_snapshot(lang.code)
            contents = paket_bauen.package_contents(snapshot, lang.code)
        except paket_bauen.BuildError as error:
            raise bestand.BestandError(str(error)) from error
        generated = rule_content(contents[Path(lang.core_path)], Path(old["paths"]["runtime"]), config_path, lang.code)
        new = bestand.make(config, home, old["bindings"], contents, generated)
        writes = {str(Path(old["paths"]["runtime"]) / rel): data for rel, data in contents.items()}
        writes.update({path: generated for path, item in new["owned"].items() if item["role"] == "client_rule"})
    else:
        new = dict(old, status="uninstalled")
        writes = {}
    new_owned = new["owned"] if action == "update" else {}
    steps = []
    for path in sorted(set(old["owned"]) | set(new_owned)):
        before, after = old["owned"].get(path), new_owned.get(path)
        kind = "add" if before is None else "remove" if after is None else "keep" if before == after else "replace"
        token = bestand.check_target(path, before)
        steps.append({"path": path, "kind": kind, "before": before, "after": after, "identity": token})
    manifest_path = str(Path(old["paths"]["runtime"]) / "paket.json")
    steps.sort(key=lambda step: (step["path"] == manifest_path, step["path"]))
    return {"action": action, "config": config, "old": old, "new": new, "config_snapshot": raw_config,
            "state_snapshot": raw_state, "state_dir": state_dir, "source_snapshot": snapshot,
            "writes": writes, "steps": steps}


def recheck(planned, config_path, home, codex, claude):
    fresh = plan(planned["action"], config_path, home, codex, claude)
    if fresh != planned:
        raise bestand.BestandError("Sources, configuration, inventory or targets changed since the preview")


def mutate(step, data=None, guard=None, checkpoint=None):
    """Capture old objects exclusively and never change an unchecked target object."""
    guard = guard or (lambda skip=None: None)
    checkpoint = checkpoint or (lambda capture: None)
    path = Path(step["path"])
    before, after = step["before"], step["after"]
    guard()
    actual = bestand.check_target(path, before)
    if actual != step["identity"]:
        raise bestand.BestandError("Target identity changed since the preview")
    parent, name = sicher.parent(path, create=before is None)
    capture_fd = None
    capture_info = None
    capture = None
    new_identity = None
    try:
        sicher.assert_directory_at_path(path.parent, parent)
        if before is not None:
            capture_name = ".aios-aufnahme-" + uuid.uuid4().hex
            capture_path = path.parent / capture_name
            capture = {"directory": str(capture_path), "object": str(capture_path / "object"), "status": "intent"}
            checkpoint(capture)
            guard()
            sicher.assert_directory_at_path(path.parent, parent)
            os.mkdir(capture_name, 0o700, dir_fd=parent)
            capture_fd = os.open(capture_name, sicher.DIR_FLAGS, dir_fd=parent)
            capture_info = os.fstat(capture_fd)
            sicher.assert_directory_at_path(capture_path, capture_fd)
            guard()
            if bestand.check_target(path, before) != actual:
                raise bestand.BestandError("Target changed before capture")
            sicher.assert_directory_at_path(path.parent, parent)
            sicher.exclusive_move_at(parent, name, capture_fd, "object")
            os.fsync(parent)
            os.fsync(capture_fd)
            taken = os.stat("object", dir_fd=capture_fd, follow_symlinks=False)
            capture["status"] = "captured"
            capture["identity"] = bestand.identity(taken)
            # Never open foreign files for hashing before their identity is established.
            if bestand.identity(taken) != actual:
                capture["status"] = "foreign_retained"
                checkpoint(capture)
                try:
                    sicher.assert_directory_at_path(path.parent, parent)
                    sicher.assert_directory_at_path(capture_path, capture_fd)
                    sicher.exclusive_move_at(capture_fd, "object", parent, name)
                    capture["status"] = "foreign_restored"
                    checkpoint(capture)
                except OSError:
                    pass
                raise bestand.BestandError(f"Foreign target detected at capture. State {capture['status']}, capture {capture_path}")
            checkpoint(capture)
            if bestand.check_target(capture_path / "object", before) != actual:
                raise bestand.BestandError("Captured own object was changed")
        guard(skip=str(path))
        bestand.check_target(path, None)
        sicher.assert_directory_at_path(path.parent, parent)
        if after is not None:
            if after["role"] == "client_link":
                created = sicher.exclusive_link(after["target"], path)
            else:
                created = sicher.exclusive_file(path, data)
            new_identity = bestand.check_target(path, after)
            if new_identity[:2] != (created.st_dev, created.st_ino):
                raise bestand.BestandError("Newly published target was replaced")
        if capture is not None:
            guard(skip=str(path))
            if bestand.check_target(path, after) != new_identity:
                raise bestand.BestandError("Target changed after publication")
            sicher.assert_directory_at_path(capture_path, capture_fd)
            if bestand.check_target(capture_path / "object", before) != actual:
                raise bestand.BestandError("Captured object changed before removal")
            capture["status"] = "discard_intent"
            checkpoint(capture)
            guard(skip=str(path))
            if bestand.check_target(path, after) != new_identity:
                raise bestand.BestandError("Target changed before completion")
            taken = os.stat("object", dir_fd=capture_fd, follow_symlinks=False)
            if bestand.identity(taken) != actual:
                raise bestand.BestandError("Private capture changed before removal")
            os.unlink("object", dir_fd=capture_fd)
            os.fsync(capture_fd)
            capture["status"] = "discarded"
            checkpoint(capture)
        os.fsync(parent)
        sicher.assert_directory_at_path(path.parent, parent)
        return new_identity
    finally:
        if capture_fd is not None:
            try:
                # Remove only the self-created empty capture folder.
                sicher.assert_directory_at_path(capture_path, capture_fd)
                current = os.stat(capture_name, dir_fd=parent, follow_symlinks=False)
                if (current.st_dev, current.st_ino) == (capture_info.st_dev, capture_info.st_ino):
                    try:
                        os.rmdir(capture_name, dir_fd=parent)
                    except OSError as error:
                        if error.errno not in (errno.ENOTEMPTY, errno.EEXIST):
                            raise
            finally:
                os.close(capture_fd)
                os.close(parent)
        else:
            os.close(parent)


def remove_empty_runtime_parents(planned, guard):
    runtime = Path(planned["old"]["paths"]["runtime"])
    directories = set()
    for step in planned["steps"]:
        if step["kind"] == "remove" and step["before"]["role"] == "runtime_file":
            current = Path(step["path"]).parent
            while current != runtime:
                directories.add(current)
                current = current.parent
    for path in sorted(directories, key=lambda item: len(item.parts), reverse=True):
        try:
            parent, name = sicher.parent(path)
        except FileNotFoundError:
            continue
        try:
            fd = sicher.directory(path)
            try:
                guard()
                sicher.assert_directory_at_path(path, fd)
                sicher.assert_directory_at_path(path.parent, parent)
                os.rmdir(name, dir_fd=parent)
            finally:
                os.close(fd)
        except OSError as error:
            if error.errno not in (errno.ENOTEMPTY, errno.EEXIST, errno.ENOENT):
                raise
        finally:
            os.close(parent)


def execute(planned, config_path, home, codex=None, claude=None):
    state_dir = planned["state_dir"]
    with bestand.operation_lock(state_dir):
        recheck(planned, config_path, home, codex, claude)
        operation_path = state_dir / "operation.json"
        try:
            previous_operation = bestand.read_snapshot(operation_path)
        except FileNotFoundError:
            previous_operation = None
        operation = {"schema_version": 1, "id": str(uuid.uuid4()), "action": planned["action"],
                     "status": "running", "old_manifest": planned["old"]["manifest_sha256"],
                     "new_manifest": planned["new"]["manifest_sha256"] if planned["action"] == "update" else None,
                     "steps": [dict(step, status="pending") for step in planned["steps"]]}
        bestand.publish(operation_path, operation, previous_operation)
        def save():
            nonlocal previous_operation
            intended = bestand.encoded(operation)
            try:
                bestand.publish(operation_path, operation, previous_operation)
            except BaseException:
                # An error after the atomic swap may already have published the own new
                # journal state. Adopt exactly this own UUID intent only, so that the error
                # path can reliably change completed into interrupted.
                try:
                    current = bestand.read_snapshot(operation_path)
                    if current[0] == intended:
                        previous_operation = current
                except (OSError, ValueError):
                    pass
                raise
            previous_operation = bestand.read_snapshot(operation_path)
        previous_operation = bestand.read_snapshot(operation_path)
        expected = {step["path"]: (step["before"], step["identity"]) for step in planned["steps"]}
        def guard(skip=None):
            if bestand.read_snapshot(config_path) != planned["config_snapshot"]:
                raise bestand.BestandError("Configuration changed during the operation")
            if bestand.read_snapshot(state_dir / "bestand.json") != planned["state_snapshot"]:
                raise bestand.BestandError("Inventory changed during the operation")
            for path, (item, token) in expected.items():
                if path != skip and bestand.check_target(path, item) != token:
                    raise bestand.BestandError(f"Current state changed during the operation: {path}")
        try:
            for step, record in zip(planned["steps"], operation["steps"]):
                if step["kind"] == "keep":
                    record["status"] = "kept"
                    continue
                guard()
                record["status"] = "intent"
                save()
                if step["kind"] == "replace" and step["before"]["role"] == "client_rule":
                    raw, token = bestand.read_snapshot(step["path"], None)
                    if token != step["identity"] or bestand.digest(raw) != step["before"]["sha256"]:
                        raise bestand.BestandError("Rule file changed before backup")
                    backup = state_dir / "sicherungen" / operation["id"]
                    guard()
                    fd = sicher.directory(backup, create=True)
                    os.close(fd)
                    sicher.exclusive_file(backup / (step["before"]["client"] + ".md"), raw)
                def checkpoint(capture):
                    record["capture"] = dict(capture)
                    save()
                token = mutate(step, planned["writes"].get(step["path"]), guard=guard, checkpoint=checkpoint)
                expected[step["path"]] = (step["after"], token)
                record["status"] = "done"
                save()
            guard()
            remove_empty_runtime_parents(planned, guard)
            for step in planned["steps"]:
                bestand.check_target(step["path"], step["after"])
            if bestand.read_snapshot(config_path) != planned["config_snapshot"]:
                raise bestand.BestandError("Configuration changed during the operation")
            bestand.validate(planned["new"], planned["config"], home, codex, claude)
            if planned["new"]["status"] == "installed":
                bestand.verify_manifest(planned["new"])
            guard()
            bestand.publish(state_dir / "bestand.json", planned["new"], planned["state_snapshot"])
            operation["status"] = "completed"
            save()
        except BaseException:
            operation["status"] = "interrupted"
            try:
                save()
            except Exception:
                pass
            raise


def main(action, argv=None):
    parser = argparse.ArgumentParser(description="Update the own AIOS package" if action == "update" else "Remove the own AIOS package files")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--home", type=Path, required=True)
    parser.add_argument("--codex-home")
    parser.add_argument("--claude-config-dir")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        planned = plan(action, args.config, args.home, args.codex_home, args.claude_config_dir)
        for label in ("old", "new"):
            state = planned[label]
            language = bestand.manifest_language(state["manifest"])
            print(f"{label}: {state['manifest']['version']} ({language}), manifest SHA256 {state['manifest_sha256']}")
        for step in planned["steps"]:
            print(f"{step['kind']}: {step['path']}")
        if not args.apply:
            print("Preview. No files changed.")
            return 0
        if input("Run the package operation? Type exactly 'yes': ").strip() != "yes":
            print("Cancelled. No files changed.")
            return 0
        execute(planned, args.config, args.home, args.codex_home, args.claude_config_dir)
        print("Package operation completed. Functional behavior, models and services unchecked.")
        return 0
    except (ValueError, OSError, KeyError, TypeError, EOFError, KeyboardInterrupt) as error:
        print(f"Package operation stopped: {error}. No automatic retry or recovery.", file=sys.stderr)
        return 1
