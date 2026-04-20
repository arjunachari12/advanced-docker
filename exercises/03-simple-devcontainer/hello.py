from __future__ import annotations


def message(name: str = "DevContainer") -> str:
    return f"Hello from a Python {name}!"


def main() -> None:
    print(message())


if __name__ == "__main__":
    main()
