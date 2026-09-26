"""Privateer's single source of release-version metadata."""

__version__ = "0.9.5"
__channel__ = ""


def display_version() -> str:
    return f"{__version__} {__channel__}" if __channel__ else __version__
