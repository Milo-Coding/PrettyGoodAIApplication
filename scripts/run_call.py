"""Run one selected patient scenario."""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario", help="Scenario ID or name")
    parser.parse_args()
    raise NotImplementedError("Call execution will be added after provider setup")


if __name__ == "__main__":
    main()
