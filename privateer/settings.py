"""Persistent user preferences stored outside game saves and the installation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import tempfile


def settings_path(config_directory=None) -> Path:
    if config_directory is not None:
        root = Path(config_directory)
    elif os.environ.get("PRIVATEER_CONFIG_DIR"):
        root = Path(os.environ["PRIVATEER_CONFIG_DIR"])
    elif os.environ.get("APPDATA"):
        root = Path(os.environ["APPDATA"]) / "Privateer"
    else:
        root = Path.home() / ".config" / "Privateer"
    return root.expanduser().resolve() / "settings.json"


@dataclass
class AppSettings:
    create_backups: bool = True
    backup_directory: str = ""
    rtw3_install_directory: str = ""
    save_game_directory: str = ""
    first_run_complete: bool = False

    @classmethod
    def load(cls, path=None):
        target = Path(path).resolve() if path is not None else settings_path()
        if not target.exists():
            return cls()
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"Unable to read settings: {exc}") from exc
        if not isinstance(data, dict) or type(data.get("create_backups", True)) is not bool:
            raise ValueError("Invalid Create backups setting")
        if type(data.get("first_run_complete", False)) is not bool:
            raise ValueError("Invalid first-run setting")
        paths = {}
        for key, label in (
                ("backup_directory", "backup directory"),
                ("rtw3_install_directory", "Rule the Waves 3 install directory"),
                ("save_game_directory", "save game directory")):
            value = data.get(key, "")
            if not isinstance(value, str) or "\x00" in value:
                raise ValueError(f"Invalid {label} setting")
            paths[key] = value
        return cls(
            create_backups=data.get("create_backups", True),
            backup_directory=paths["backup_directory"],
            rtw3_install_directory=paths["rtw3_install_directory"],
            save_game_directory=paths["save_game_directory"],
            first_run_complete=data.get("first_run_complete", False),
        )

    def save(self, path=None):
        target = Path(path).resolve() if path is not None else settings_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            handle, name = tempfile.mkstemp(prefix=".settings-", suffix=".json", dir=target.parent)
            os.close(handle)
            temporary = Path(name)
            temporary.write_text(json.dumps(asdict(self), indent=2) + "\n", encoding="utf-8")
            temporary.replace(target)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
        return target

