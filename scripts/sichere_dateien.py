"""Kleine fd-gebundene Dateivorgänge für die lokale Ersteinrichtung."""

import ctypes
import errno
import hashlib
import os
from pathlib import Path
import secrets
import stat
import sys


DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


def directory(path, create=False, created=None):
    """Öffne einen absoluten Pfad komponentenweise ohne Symlinks."""
    path = Path(path)
    if not path.is_absolute() or str(path).startswith("//"):
        raise OSError(errno.EINVAL, "Verzeichnispfad muss absolut sein")
    fd = os.open("/", DIR_FLAGS)
    current = Path("/")
    try:
        for part in path.parts[1:]:
            current /= part
            if create:
                try:
                    os.mkdir(part, 0o700, dir_fd=fd)
                except FileExistsError:
                    pass
                else:
                    if created is not None:
                        created.append(str(current))
            next_fd = os.open(part, DIR_FLAGS, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        return fd
    except Exception:
        os.close(fd)
        raise


def parent(path, create=False, created=None):
    path = Path(path)
    return directory(path.parent, create=create, created=created), path.name


def assert_directory_at_path(path, opened_fd):
    """Prüfe, ob ein offener Ordner noch am absoluten Pfad erreichbar ist."""
    fresh_fd = directory(path)
    try:
        opened = os.fstat(opened_fd)
        current = os.fstat(fresh_fd)
        if (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino):
            raise OSError(errno.ESTALE, "Ziel-Elternordner wurde ersetzt")
    finally:
        os.close(fresh_fd)


def exclusive_file(path, data, created=None):
    parent_fd, name = parent(path)
    try:
        fd = os.open(name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=parent_fd)
        try:
            info = os.fstat(fd)
            owned = None
            if created is not None:
                owned = created(info)
            try:
                with os.fdopen(os.dup(fd), "wb") as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
            except Exception:
                if owned is not None:
                    os.lseek(fd, 0, os.SEEK_SET)
                    actual = b""
                    while True:
                        chunk = os.read(fd, 65536)
                        if not chunk:
                            break
                        actual += chunk
                    owned["sha256"] = hashlib.sha256(actual).hexdigest()
                    owned["incomplete"] = True
                raise
            current = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            if (current.st_dev, current.st_ino) != (info.st_dev, info.st_ino):
                raise OSError(errno.ESTALE, "Zieldatei wurde ersetzt")
            assert_directory_at_path(Path(path).parent, parent_fd)
            return info
        finally:
            os.close(fd)
    finally:
        os.close(parent_fd)


def exclusive_link(source, target):
    parent_fd, name = parent(target)
    try:
        os.symlink(source, name, dir_fd=parent_fd)
        info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if not stat.S_ISLNK(info.st_mode) or os.readlink(name, dir_fd=parent_fd) != str(source):
            raise OSError(errno.ESTALE, "Zielverknüpfung wurde ersetzt")
        assert_directory_at_path(Path(target).parent, parent_fd)
        return info
    finally:
        os.close(parent_fd)


def _rename_at(source_fd, source_name, destination_fd, destination_name, exchange=False):
    libc = ctypes.CDLL(None, use_errno=True)
    src = os.fsencode(source_name)
    dst = os.fsencode(destination_name)
    if sys.platform == "darwin" and hasattr(libc, "renameatx_np"):
        operation = libc.renameatx_np
        flags = 0x00000002 if exchange else 0x00000004
    elif sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        operation = libc.renameat2
        flags = 2 if exchange else 1
    else:
        raise OSError(errno.ENOTSUP, "Geschützte Umbenennung nicht verfügbar")
    operation.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    result = operation(source_fd, src, destination_fd, dst, flags)
    if result:
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code))


def exclusive_rename_at(parent_fd, source_name, destination_name):
    _rename_at(parent_fd, source_name, parent_fd, destination_name)


def exclusive_move_at(source_fd, source_name, destination_fd, destination_name):
    """Verschiebe ohne Ersetzung zwischen zwei gebundenen Ordnern."""
    _rename_at(source_fd, source_name, destination_fd, destination_name)


def exchange_at(parent_fd, first_name, second_name):
    """Tausche beide Namen atomar, ohne eines der beiden Objekte zu vernichten."""
    _rename_at(parent_fd, first_name, parent_fd, second_name, exchange=True)


def build_directory(destination, contents):
    """Schreibe ein neues Paket im Ziel-Eltern-FD und veröffentliche exklusiv."""
    for raw in contents:
        value = os.fspath(raw)
        if not isinstance(value, str) or Path(value).is_absolute() or any(
            part in ("", ".", "..") for part in value.split("/")
        ):
            raise OSError(errno.EINVAL, "Ungültiger Paketpfad")
    parent_fd, target_name = parent(destination)
    stage_name = ".aios-paket-" + secrets.token_hex(12)
    stage_identity = None
    published = False
    try:
        os.mkdir(stage_name, 0o700, dir_fd=parent_fd)
        stage_fd = os.open(stage_name, DIR_FLAGS, dir_fd=parent_fd)
        try:
            stage_info = os.fstat(stage_fd)
            stage_identity = (stage_info.st_dev, stage_info.st_ino)
            for relative, data in sorted(contents.items()):
                parts = Path(relative).parts
                if not parts or any(part in ("", ".", "..") for part in parts):
                    raise OSError(errno.EINVAL, "Ungültiger Paketpfad")
                current_fd = os.dup(stage_fd)
                try:
                    for part in parts[:-1]:
                        try:
                            os.mkdir(part, 0o700, dir_fd=current_fd)
                        except FileExistsError:
                            pass
                        next_fd = os.open(part, DIR_FLAGS, dir_fd=current_fd)
                        os.close(current_fd)
                        current_fd = next_fd
                    file_fd = os.open(parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                      0o600, dir_fd=current_fd)
                    with os.fdopen(file_fd, "wb") as stream:
                        stream.write(data)
                        stream.flush()
                        os.fsync(stream.fileno())
                finally:
                    os.close(current_fd)
            exclusive_rename_at(parent_fd, stage_name, target_name)
            published = True
            current = os.stat(target_name, dir_fd=parent_fd, follow_symlinks=False)
            if (current.st_dev, current.st_ino) != stage_identity:
                raise OSError(errno.ESTALE, "Runtime-Ziel wurde ersetzt")
            assert_directory_at_path(Path(destination).parent, parent_fd)
        finally:
            os.close(stage_fd)
    finally:
        if stage_identity is not None and not published:
            try:
                current = os.stat(stage_name, dir_fd=parent_fd, follow_symlinks=False)
                if (current.st_dev, current.st_ino) == stage_identity:
                    _remove_tree(parent_fd, stage_name)
            except FileNotFoundError:
                pass
        os.close(parent_fd)


def _remove_tree(parent_fd, name):
    fd = os.open(name, DIR_FLAGS, dir_fd=parent_fd)
    try:
        for child in os.listdir(fd):
            info = os.stat(child, dir_fd=fd, follow_symlinks=False)
            if stat.S_ISDIR(info.st_mode):
                _remove_tree(fd, child)
            else:
                os.unlink(child, dir_fd=fd)
    finally:
        os.close(fd)
    os.rmdir(name, dir_fd=parent_fd)
