from __future__ import annotations

from pathlib import Path
import shlex
import subprocess

from toolchain import find_nim_lib


def main() -> int:
    experiment = Path(__file__).parents[1]
    nim_lib = find_nim_lib(experiment)
    output = experiment / "observed" / "bin" / "c_caller"
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "clang",
        "-std=c11",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-Iobserved",
        f"-I{nim_lib}",
        "src/caller.c",
        "-Lobserved/bin",
        "-lscalar_api",
        "-Wl,-rpath,@loader_path",
        "-o",
        "observed/bin/c_caller",
    ]
    print(shlex.join(command))
    subprocess.run(command, cwd=experiment, check=True)
    print("C caller compiled and linked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
