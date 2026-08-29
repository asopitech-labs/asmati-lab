from __future__ import annotations

from pathlib import Path
import subprocess


def find_nim_lib(experiment: Path) -> Path:
    result = subprocess.run(
        ["nim", "dump", "--verbosity:0", "src/overflow_compare.nim"],
        cwd=experiment,
        check=True,
        capture_output=True,
        text=True,
    )
    dump_output = "\n".join((result.stdout, result.stderr))
    for line in dump_output.splitlines():
        candidate = Path(line.strip())
        if (candidate / "nimbase.h").is_file():
            return candidate.resolve()
    raise RuntimeError("nimbase.h was not found in `nim dump` search paths")
