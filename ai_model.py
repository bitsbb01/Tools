from __future__ import annotations

import json
import os
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Callable


MODEL_REPO = "Wan-AI/Wan2.2-TI2V-5B"
MODEL_LABEL = "Wan2.2 TI2V-5B"
MODEL_API = f"https://huggingface.co/api/models/{MODEL_REPO}/tree/main"
MODEL_DOWNLOAD = f"https://huggingface.co/{MODEL_REPO}/resolve/main/"
MODEL_LICENSE_URL = f"https://huggingface.co/{MODEL_REPO}"
ESTIMATED_MODEL_BYTES = 34_200_000_000
MINIMUM_FREE_BYTES = 38 * 1024**3
INSTALLED_MARKER = ".jgjg-installed.json"
CHUNK_BYTES = 4 * 1024 * 1024


class DownloadCancelled(Exception):
    """Raised when the user pauses a model download."""


def model_install_dir() -> Path:
    """Return a per-user location that is not removed by app upgrades."""
    root = os.environ.get("LOCALAPPDATA")
    if root:
        base = Path(root)
    else:
        base = Path.home() / ".local" / "share"
    return base / "JGJG Books" / "JGJG Video Studio" / "models" / "Wan2.2-TI2V-5B"


def model_is_installed(destination: Path | None = None) -> bool:
    root = destination or model_install_dir()
    marker = root / INSTALLED_MARKER
    try:
        info = json.loads(marker.read_text(encoding="utf-8"))
        if info.get("repository") != MODEL_REPO or info.get("complete") is not True:
            return False
        files = info.get("files")
        if not isinstance(files, list) or not files:
            return False
        for item in files:
            relative = PurePosixPath(str(item["path"]))
            path = root.joinpath(*relative.parts)
            size = int(item.get("size", 0))
            if not path.is_file() or (size and path.stat().st_size != size):
                return False
        return True
    except (OSError, ValueError, TypeError):
        return False


def _request_json(url: str) -> tuple[object, str | None]:
    request = urllib.request.Request(url, headers={"User-Agent": "JGJG-Video-Studio/0.2"})
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = json.loads(response.read().decode("utf-8"))
        return payload, response.headers.get("Link")


def _model_files() -> list[dict[str, object]]:
    """Fetch the official repository file list, excluding demo media."""
    files: list[dict[str, object]] = []
    url: str | None = MODEL_API + "?recursive=true&expand=true&limit=1000"
    pages = 0
    while url:
        payload, link_header = _request_json(url)
        if not isinstance(payload, list):
            raise RuntimeError("The model host returned an unexpected file listing.")
        for item in payload:
            if not isinstance(item, dict) or item.get("type") != "file":
                continue
            name = str(item.get("path") or item.get("name") or "")
            path = PurePosixPath(name)
            if not name or path.is_absolute() or ".." in path.parts:
                continue
            if path.parts[0] in {"assets", "examples"}:
                continue
            if name in {".gitattributes", ".msc", ".mv"}:
                continue
            size = item.get("size")
            if not isinstance(size, int):
                lfs = item.get("lfs")
                size = lfs.get("size", 0) if isinstance(lfs, dict) else 0
            files.append({"path": name, "size": int(size) if isinstance(size, int) else 0})

        next_url = None
        if link_header:
            for link in link_header.split(","):
                if 'rel="next"' in link:
                    next_url = link[link.find("<") + 1 : link.find(">")]
                    break
        url = next_url
        pages += 1
        if pages > 20:
            raise RuntimeError("The model repository returned too many file-list pages.")

    if not files:
        raise RuntimeError("No downloadable model files were found.")
    return files


def _download_file(
    file_info: dict[str, object],
    destination: Path,
    cancel: threading.Event,
    on_progress: Callable[[str, int], None],
) -> int:
    relative = str(file_info["path"])
    expected_size = int(file_info.get("size", 0))
    target = destination.joinpath(*PurePosixPath(relative).parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and (not expected_size or target.stat().st_size == expected_size):
        return target.stat().st_size

    partial = target.with_name(target.name + ".part")
    offset = partial.stat().st_size if partial.exists() else 0
    url = MODEL_DOWNLOAD + urllib.parse.quote(relative, safe="/")
    headers = {"User-Agent": "JGJG-Video-Studio/0.2"}
    if offset:
        headers["Range"] = f"bytes={offset}-"
    request = urllib.request.Request(url, headers=headers)

    try:
        response = urllib.request.urlopen(request, timeout=60)
    except urllib.error.HTTPError as exc:
        if offset and exc.code == 416:
            partial.unlink(missing_ok=True)
            return _download_file(file_info, destination, cancel, on_progress)
        raise

    with response:
        append = offset > 0 and response.status == 206
        if offset and not append:
            offset = 0
        downloaded = offset
        mode = "ab" if append else "wb"
        with partial.open(mode) as output:
            while True:
                if cancel.is_set():
                    raise DownloadCancelled
                chunk = response.read(CHUNK_BYTES)
                if not chunk:
                    break
                output.write(chunk)
                downloaded += len(chunk)
                on_progress(relative, downloaded)

    final_size = partial.stat().st_size
    if expected_size and final_size != expected_size:
        raise RuntimeError(f"Incomplete download for {relative}; it can be resumed by clicking Install again.")
    partial.replace(target)
    return final_size


def install_model(
    destination: Path | None = None,
    cancel: threading.Event | None = None,
    on_progress: Callable[[str, int, int], None] | None = None,
) -> Path:
    """Download the official model files into the app's local model folder."""
    root = destination or model_install_dir()
    cancel = cancel or threading.Event()
    progress = on_progress or (lambda _name, _done, _total: None)
    root.mkdir(parents=True, exist_ok=True)
    files = _model_files()
    total = sum(int(item["size"]) for item in files)
    completed = 0

    for item in files:
        if cancel.is_set():
            raise DownloadCancelled
        relative = str(item["path"])
        known_size = int(item["size"])
        target = root.joinpath(*PurePosixPath(relative).parts)
        if target.exists() and (not known_size or target.stat().st_size == known_size):
            completed += target.stat().st_size
            progress(relative, completed, total)
            continue

        def update(name: str, current: int) -> None:
            progress(name, completed + current, total)

        completed += _download_file(item, root, cancel, update)

    marker = {"repository": MODEL_REPO, "complete": True, "files": files}
    (root / INSTALLED_MARKER).write_text(json.dumps(marker, indent=2), encoding="utf-8")
    return root
