"""Privateer's single source of release-version metadata."""

__version__ = "1.0.4"
__channel__ = "Beta"


def display_version() -> str:
    return f"{__version__} {__channel__}" if __channel__ else __version__
