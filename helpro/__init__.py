"""motep."""

import argparse

from helpro.molpro import inp


def main() -> None:
    """Command."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    commands = {"inp": inp}
    for key, value in commands.items():
        value.add_arguments(subparsers.add_parser(key))

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    commands[args.command].run(args)
