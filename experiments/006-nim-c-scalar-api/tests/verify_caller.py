from __future__ import annotations

from pathlib import Path
import subprocess


def main() -> int:
    experiment = Path(__file__).parents[1]
    caller_source = (experiment / "src" / "caller.c").read_text(encoding="utf-8")
    if "NimMain(" in caller_source:
        raise SystemExit("C caller must rely on the POSIX library initializer, not call NimMain explicitly")

    caller = experiment / "observed" / "bin" / "c_caller"
    undefined = subprocess.run(
        ["nm", "-u", str(caller)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    for symbol in ("_asmati_add_ints", "_asmati_half"):
        if symbol not in undefined:
            raise SystemExit(f"C caller does not reference expected symbol: {symbol}")
    if "_NimMain" in undefined:
        raise SystemExit("C caller unexpectedly references NimMain")

    dependencies = subprocess.run(
        ["otool", "-L", str(caller)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if "@rpath/libscalar_api.dylib" not in dependencies:
        raise SystemExit("C caller does not depend on @rpath/libscalar_api.dylib")

    print("C caller linkage without explicit NimMain verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
