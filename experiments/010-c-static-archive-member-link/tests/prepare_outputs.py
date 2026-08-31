from pathlib import Path


def main() -> int:
    experiment = Path(__file__).parents[1]
    for relative in ("observed/obj", "observed/lib", "observed/bin"):
        (experiment / relative).mkdir(parents=True, exist_ok=True)
    print("archive output directories prepared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
