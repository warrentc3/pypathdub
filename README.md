# pypathdub

`pypathdub` projects path strings between Windows, WSL, MSYS2/Mingw, and POSIX conventions.

It is for the common cross-shell case where the producer shell's path shape is not the shape a consumer binary expects.

```powershell
pypathdub 'C:\work\project\data.local' --fmt python-wsl
# /mnt/c/work/project/data.local

pypathdub 'C:\work\project\data.local' --fmt python-mingw
# /c/work/project/data.local
```

## Python

```python
from pypathdub import normalizePathString

print(normalizePathString(r"C:\work\project\data.local", "python-mingw"))
```

`normalize_path_string` is also exported as a Python-style alias.

From a source checkout, the compatibility script is:

```powershell
python .\scripts\normalize_path_string.py 'C:\work\project\data.local' --fmt python-mingw
```

## Formats

- `python-windows`
- `python-nix`
- `python-mingw`
- `python-wsl`
- `osnative-windows`
- `osnative-nix`
- `osnative-mingw`
- `osnative-wsl`

The `python-*` formats use Python-literal-safe separators. The `osnative-*` formats use the native path style for that convention.

Drive-backed Windows paths cannot be projected to plain `nix`; use Mingw or WSL when the drive mount is part of the target convention.
