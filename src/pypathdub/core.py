from __future__ import annotations

import ntpath
import os
import platform
import re
import shutil
import subprocess
from typing import Dict, List, Optional, Tuple

__all__ = ["FORMATS", "normalizePathString", "normalize_path_string"]

_PYTHON = ("python-win", "python-winabsolute", "python-nix", "python-mingw", "python-wsl")
_OSNATIVE = ("osnative-win", "osnative-winabsolute", "osnative-nix", "osnative-mingw", "osnative-wsl")
FORMATS = _PYTHON + _OSNATIVE
_MINGW_MOUNT_RE = re.compile(r"^/[a-zA-Z]/")


def _split_windows_root(pathstr: str) -> Tuple[str, str, str]:
    drive, tail = ntpath.splitdrive(pathstr)
    root = ""
    if tail.startswith(("\\", "/")):
        root = tail[0]
        tail = tail[1:]
    return drive, root, tail


def _split_posix_root(pathstr: str) -> Tuple[str, str, str]:
    if pathstr.startswith("//") and not pathstr.startswith("///"):
        return "", "//", pathstr[2:]
    if pathstr.startswith("/"):
        return "", "/", pathstr[1:]
    return "", "", pathstr


def _is_wsl() -> bool:
    if platform.system() != "Linux":
        return False
    try:
        with open("/proc/sys/kernel/osrelease", "r", encoding="utf-8") as stream:
            osrelease = stream.read().lower()
    except OSError:
        return False
    return "microsoft" in osrelease or "wsl" in osrelease


def _runtime_convention() -> str:
    if os.environ.get("MSYSTEM"):
        return "mingw"
    if _is_wsl():
        return "wsl"
    return {"Windows": "win", "Linux": "nix", "Darwin": "nix"}.get(platform.system(), "nix")


def _project_unc_to_nix(unc: str, segments: List[str]) -> str:
    anchor = "//" + unc.replace("\\", "/").strip("/")
    if segments:
        return anchor + "/" + "/".join(segments)
    return anchor


def _decompose(pathstr: str, target_convention: Optional[str] = None) -> Dict[str, object]:
    win_drive, _ = ntpath.splitdrive(pathstr)
    if win_drive or "\\" in pathstr:
        drive, root, tail = _split_windows_root(pathstr)
        unc = drive if drive[:2] in ("\\\\", "//") else ""
        segments = [segment for segment in tail.replace("\\", "/").split("/") if segment]
        return {
            "convention": "win",
            "drive": "" if unc else drive.rstrip(":"),
            "unc": unc,
            "absolute": bool(root),
            "segments": segments,
        }

    _, root, tail = _split_posix_root(pathstr)
    segments = [segment for segment in tail.split("/") if segment]
    if root == "/" and len(segments) >= 2 and segments[0] == "mnt" and len(segments[1]) == 1 and segments[1].isalpha():
        return {
            "convention": "wsl",
            "drive": segments[1],
            "unc": "",
            "absolute": True,
            "segments": segments[2:],
        }
    if (
        root == "/"
        and segments
        and len(segments[0]) == 1
        and segments[0].isalpha()
        and (target_convention in {"win", "winabsolute", "mingw", "wsl"} or _runtime_convention() == "mingw")
    ):
        return {
            "convention": "mingw",
            "drive": segments[0],
            "unc": "",
            "absolute": True,
            "segments": segments[1:],
        }
    return {
        "convention": "nix",
        "drive": "",
        "unc": "",
        "absolute": bool(root),
        "segments": segments,
    }


def _project(parts: Dict[str, object], convention: str, python_safe: bool) -> str:
    segments = parts["segments"]
    assert isinstance(segments, list)
    drive = str(parts["drive"])
    unc = str(parts["unc"])
    absolute = bool(parts["absolute"])

    if convention in {"win", "winabsolute"}:
        if convention == "winabsolute" and not ((drive and absolute) or unc):
            raise ValueError("cannot project path to winabsolute without a Windows drive or UNC authority")
        separator = "/" if python_safe else "\\"
        if unc:
            anchor = (unc.replace("\\", "/") if python_safe else unc.replace("/", "\\")) + separator
        elif drive:
            anchor = drive + ":" + (separator if absolute else "")
        else:
            anchor = separator if absolute else ""
        return anchor + separator.join(segments)
    if convention == "mingw":
        if unc:
            raise ValueError("cannot project UNC path to mingw convention")
        anchor = ("/" + drive.lower() + "/") if drive else ("/" if absolute else "")
        return anchor + "/".join(segments)
    if convention == "wsl":
        if unc:
            raise ValueError("cannot project UNC path to wsl convention")
        anchor = ("/mnt/" + drive.lower() + "/") if drive else ("/" if absolute else "")
        return anchor + "/".join(segments)
    if drive:
        raise ValueError(
            f"cannot project Windows drive '{drive}:' to nix convention; "
            "use 'python-mingw', 'osnative-mingw', 'python-wsl', or 'osnative-wsl' instead"
        )
    if unc:
        return _project_unc_to_nix(unc, segments)
    return ("/" if absolute else "") + "/".join(segments)


def normalizePathString(pathstr: str, fmt: Optional[str] = None) -> str:
    if fmt is not None and fmt not in FORMATS:
        raise ValueError(f"unknown fmt {fmt!r}; expected None or one of {FORMATS}")
    expanded = os.path.expandvars(os.path.expanduser(pathstr))
    if (
        fmt == "osnative-win"
        and _MINGW_MOUNT_RE.match(expanded)
        and platform.system() == "Windows"
        and shutil.which("cygpath")
    ):
        completed = subprocess.run(["cygpath", "-w", expanded], capture_output=True, text=True)
        if completed.returncode == 0 and completed.stdout.strip():
            return completed.stdout.strip()
    if fmt is None:
        convention, python_safe = _runtime_convention(), True
    else:
        python_safe, convention = fmt.startswith("python-"), fmt.split("-", 1)[1]
    return _project(_decompose(expanded, convention), convention, python_safe)


def normalize_path_string(pathstr: str, fmt: Optional[str] = None) -> str:
    return normalizePathString(pathstr, fmt)
