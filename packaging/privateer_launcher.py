"""PyInstaller entry point for the end-user Windows build."""

from privateer.main import main


if __name__ == "__main__":
    raise SystemExit(main())
