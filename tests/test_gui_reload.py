from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from privateer.gui import MainWindow


def window_for_reload(*, modified=False, selected="3"):
    window = object.__new__(MainWindow)
    window.save_model = SimpleNamespace(folder=Path("Game1"), modified=modified)
    window.table = Mock()
    window.table.selection.return_value = (selected,) if selected else ()
    window._load_folder = Mock()
    return window


def test_reload_uses_current_folder_and_preserves_nation_selection():
    window = window_for_reload(selected="3")

    window.reload_save()

    window._load_folder.assert_called_once_with(
        Path("Game1"),
        selected="3",
        loading_message="Reloading and indexing save files…",
        loaded_status="Reloaded",
    )


def test_reload_can_keep_unsaved_changes_when_user_declines():
    window = window_for_reload(modified=True)

    with patch("privateer.gui.messagebox.askyesno", return_value=False) as confirm:
        window.reload_save()

    confirm.assert_called_once()
    window._load_folder.assert_not_called()
