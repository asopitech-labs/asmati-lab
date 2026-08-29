from pathlib import Path


def main() -> int:
    experiment = Path(__file__).parents[1]
    for mode in ("debug", "release"):
        (experiment / "observed" / "bin" / mode).mkdir(parents=True, exist_ok=True)
        (experiment / "observed" / "nimcache" / mode).mkdir(parents=True, exist_ok=True)
    print("debug and release output directories prepared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
