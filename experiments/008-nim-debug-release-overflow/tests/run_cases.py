from __future__ import annotations

from pathlib import Path
import subprocess


HIGH_INT64 = "9223372036854775807"


def run(binary: Path, value: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(binary), value], capture_output=True, text=True, check=False)


def main() -> int:
    experiment = Path(__file__).parents[1]
    results: dict[tuple[str, str], subprocess.CompletedProcess[str]] = {}
    for mode in ("debug", "release"):
        binary = experiment / "observed" / "bin" / mode / "overflow_compare"
        results[(mode, "normal")] = run(binary, "41")
        results[(mode, "boundary")] = run(binary, HIGH_INT64)

    for mode in ("debug", "release"):
        normal = results[(mode, "normal")]
        if normal.returncode != 0 or normal.stdout.strip() != "42":
            raise SystemExit(f"{mode} normal case mismatch")
        print(f"{mode} normal: exit=0 stdout=42")

    for mode in ("debug", "release"):
        boundary = results[(mode, "boundary")]
        has_overflow = "over- or underflow [OverflowDefect]" in boundary.stderr
        has_add_one_frame = "addOne" in boundary.stderr
        if boundary.returncode != 1 or not has_overflow:
            raise SystemExit(f"{mode} boundary case mismatch")
        print(
            f"{mode} boundary: exit={boundary.returncode} "
            f"overflow_defect={str(has_overflow).lower()} "
            f"add_one_frame={str(has_add_one_frame).lower()}"
        )

    if "addOne" not in results[("debug", "boundary")].stderr:
        raise SystemExit("debug boundary output is missing addOne frame")
    if "addOne" in results[("release", "boundary")].stderr:
        raise SystemExit("release boundary output unexpectedly contains addOne frame")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
