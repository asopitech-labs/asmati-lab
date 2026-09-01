from pathlib import Path


def main() -> int:
    experiment = Path(__file__).parents[1]
    for relative in ("observed/bin/lib", "observed/bin/missing"):
        (experiment / relative).mkdir(parents=True, exist_ok=True)
    print("shared library output directories prepared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
