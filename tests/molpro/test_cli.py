"""Tests for CLI."""

from subprocess import run


def test_inp() -> None:
    """Test if the `inp` subcommand works."""
    run(("helpro", "inp"), check=True)
