from pathlib import Path


def main() -> int:
    experiment = Path(__file__).parents[1]
    (experiment / "observed" / "obj").mkdir(parents=True, exist_ok=True)
    print("object output directory prepared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
