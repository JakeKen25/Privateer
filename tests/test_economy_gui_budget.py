from types import SimpleNamespace
from unittest.mock import Mock, patch

from privateer.economy_gui import EconomyWindow


def test_ai_refresh_preserves_economy_edits_without_calculating_budget():
    window = object.__new__(EconomyWindow)
    window.nation = SimpleNamespace(funds=100, base_resources=200, unrest_level=3)
    window.budget_context = None
    window.projected = {key: Mock() for key in ('funds', 'base_resources', 'unrest_level')}
    window._value = lambda key, current: current + 1
    window.error, window.error_label = Mock(), Mock()
    with patch('privateer.economy_gui.project_budget') as calculate:
        window.refresh()
    calculate.assert_not_called()
    window.projected['funds'].set.assert_called_once_with('Projected: 101')
    window.projected['base_resources'].set.assert_called_once_with('Projected: 201')
    window.projected['unrest_level'].set.assert_called_once_with('Projected: 4')
