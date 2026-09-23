"""File download endpoints."""
import os
from pathlib import Path

BASE_DIR = "/srv/uploads"


def download(filename):
    path = os.path.join(BASE_DIR, filename)
    with open(path, "rb") as fh:
        return fh.read()


def download_safe(filename):
    base = Path(BASE_DIR).resolve()
    path = (base / filename).resolve()
    if base not in path.parents:
        raise PermissionError("path escapes upload dir")
    return path.read_bytes()


def list_uploads():
    return sorted(os.listdir(BASE_DIR))
