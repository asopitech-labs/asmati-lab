from pathlib import Path
import shutil


def main() -> int:
    experiment = Path(__file__).parents[1]
    generated = experiment / "observed" / "nimcache" / "scalar_api.h"
    saved = experiment / "observed" / "scalar_api.h"
    if not generated.is_file():
        raise SystemExit(f"generated header not found: {generated}")
    shutil.copyfile(generated, saved)
    print("generated header saved to observed/scalar_api.h")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
