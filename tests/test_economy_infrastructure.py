from pathlib import Path

import pytest

from privateer.economy import project_budget
from privateer.save import RTW3Save


MAIN = """[Nation0]\r
Name=Germany\r
DockSize=35000\r
BaseResources=30000\r
Funds=100\r
BudgetModifier=3\r
ResearchPct=8\r
NavalAircraftSpending=2\r
ExtraTrainingSpending=3\r
IntelligenceSpending=10\r
ShipCount=2\r
[Nation0Ship0]\r
Name=Active\r
Type=BB\r
ShipDesignRefId=0\r
OwnerNationIdx=0\r
BuildingNationIdx=0\r
UnderConstruction=0\r
Maintenance=235\r
MonthlyCost=1863\r
[Nation0Ship1]\r
Name=Building\r
Type=BB\r
ShipDesignRefId=1\r
OwnerNationIdx=0\r
BuildingNationIdx=0\r
UnderConstruction=1\r
Maintenance=87\r
MonthlyCost=849\r
"""


def fixture(tmp_path: Path):
    folder = tmp_path / "Game1"
    folder.mkdir()
    (folder / "RTWGame1.bcs").write_bytes(MAIN.encode())
    (folder / "DesignFiles0.des").write_text(
        "[ShipDesign0]\nDesignId=0\nType=BB\nClass=Active\n"
        "[ShipDesign1]\nDesignId=1\nType=BB\nClass=Building\n",
        encoding="utf-8",
    )
    return RTW3Save.load(folder)


def test_game1_budget_projection_matches_verified_budget_and_research(tmp_path):
    projection = project_budget(fixture(tmp_path).nation(0))
    assert projection.yearly_budget == 72_000
    assert projection.monthly_budget == 6_000
    assert projection.research == 480
    assert projection.maintenance == 235
    assert projection.construction == 849
    assert projection.total_expenses == 1_579
    assert projection.monthly_balance == 4_421
    assert projection.funds == 100


def test_projection_uses_staged_funds_and_resources(tmp_path):
    projection = project_budget(fixture(tmp_path).nation(0), base_resources=40_000, funds=250)
    assert (projection.yearly_budget, projection.monthly_budget, projection.research) == (96_000, 8_000, 640)
    assert projection.funds == 250


def test_dock_size_edit_is_staged_and_audited(tmp_path):
    save = fixture(tmp_path)
    save.set_dock_size(0, 42_000)
    assert save.nation(0).dock_size == 42_000
    assert "DockSize=42000\r\n" in save.documents[save.main_file].render()
    assert save.modified
    assert save.audit[-1] == "Changed Germany DockSize: 35000 -> 42000"


@pytest.mark.parametrize("value", [-1, 2**31, 1.5, True])
def test_dock_size_rejects_invalid_values(tmp_path, value):
    with pytest.raises(ValueError, match="Dockyard size"):
        fixture(tmp_path).set_dock_size(0, value)
