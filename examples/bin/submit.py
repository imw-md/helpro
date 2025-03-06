#!/usr/bin/env python
"""submit."""

import argparse
import os
import subprocess
from pathlib import Path


def run(script: str, jobs: str, *, single: bool, reminders: tuple) -> None:
    """Submit multiple jobs at once."""
    if not Path(script).is_file():
        msg = f"{script} not found"
        raise ValueError(msg)

    # Collect directories to be computed.
    if single:
        directories = [Path.cwd()]
    else:
        with Path(jobs).open("r", encoding="utf-8") as file:
            directories = file.read().splitlines()

    # Submit the batch script in each directory.
    cwd = Path.cwd()
    for directory in directories:
        if not Path(directory).is_dir():
            print(f"{directory} not found: skipped")
            continue

        os.chdir(directory)
        subprocess.call(["sbatch", script, *reminders])
        os.chdir(cwd)


def main() -> None:
    """Command."""
    parser = argparse.ArgumentParser()
    parser.add_argument("script")
    parser.add_argument(
        "-j",
        "--jobs",
        default="jobList",
        type=str,
        help="File with directory names to be calculated.",
    )
    parser.add_argument(
        "-s",
        "--single",
        action="store_true",
        help="Run a single job in the current directory.",
    )
    args, reminders = parser.parse_known_args()
    run(args.script, args.jobs, single=args.single, reminders=reminders)


if __name__ == "__main__":
    main()
