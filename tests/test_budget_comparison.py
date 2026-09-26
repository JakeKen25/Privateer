from pathlib import Path

import pytest

from privateer.document import TextDocument
from privateer.economy import BudgetContext, budget_context, project_budget
from privateer.save import RTW3Save


def campaign(ships=(), extra="", nation=""):
    text = "[General]\nFleetSize=8\n[Nation0]\nName=Test\nBaseResources=36000\nBudgetModifier=3\nResearchPct=12\nFunds=124\n" + nation
    for i, fields in enumerate(ships):
        fields = {'UnderConstruction': 0, **fields}
        text += f"\n[Nation0Ship{i}]\nName=Ship{i}\nOwnerNationIdx=0\n"
        text += "\n".join(f"{k}={v}" for k, v in fields.items()) + "\n"
    text += "\n[Nation0Submarines]\nSubCount=0\n[Nation0CoastalArtillery]\nCACount=0\n" + extra
    return RTW3Save(Path('.'), {'test.bcs': TextDocument.parse(text)}, 'test.bcs')


def test_historical_and_museum_hulls_never_add_expenses():
    save = campaign([
        {'Maintenance': 100, 'Status': 0},
        *({'Maintenance': 900, 'MonthlyCost': 500, 'Fate': fate, 'UnderConstruction': 1}
          for fate in ['Sunk', 'Scrapped', 'Mined', 'Broken up on slipway']),
        {'Maintenance': 900, 'Status': 9},
    ])
    result = project_budget(save.nation(0))
    assert result.maintenance == 100
    assert result.construction == 0


def test_game1_status_reductions_match_observed_difference():
    save = campaign([{'Maintenance': 349, 'Status': 1}, {'Maintenance': 267, 'Status': 2}])
    result = project_budget(save.nation(0))
    assert 349 + 267 - result.maintenance == 2955 - 2566


@pytest.mark.parametrize('monthly,expected', [([5826]*3, 20100), ([4627]*2+[3235]*4, 25522)])
def test_game2_and_game7_hurry_charges(monthly, expected):
    save = campaign([{'MonthlyCost': cost, 'Hurry': 1, 'UnderConstruction': 1} for cost in monthly])
    assert project_budget(save.nation(0)).construction == expected


def test_game9_halted_construction_and_halt_precedence():
    ships = [{'Maintenance': m, 'MonthlyCost': 9999, 'Halted': 1, 'Hurry': 1, 'UnderConstruction': 1}
             for m in [489, 489, 808, 808, 89, 89, 191, 191]]
    ships += [{'MonthlyCost': c, 'UnderConstruction': 1} for c in [1020, 716, 716]]
    assert project_budget(campaign(ships).nation(0)).construction == 4026


def test_target_intelligence_and_ai_nation_limits():
    save = campaign(extra='[Nation1]\nName=Target\nIntelligenceSpending=3\n', nation='IntelligenceSpending=0\n')
    context = budget_context(save, save.nation(0))
    assert context.intelligence == 240
    assert budget_context(save, save.nation(1)).intelligence is None
    save.nation(1).section.set('IntelligenceSpending', 2)
    assert budget_context(save, save.nation(0)).intelligence == 160


def test_fleet_size_income_and_rounding_before_research():
    save = campaign(nation='')
    n = save.nation(0)
    n.base_resources = 10000
    n.section.set('BudgetModifier', 18)
    p = project_budget(n, context=BudgetContext(4, 0), funds=250)
    assert (p.yearly_budget, p.monthly_budget, p.funds) == (72000, 6000, 250)
    n.base_resources = 10001
    p = project_budget(n, context=BudgetContext(4, 0))
    assert (p.yearly_budget, p.monthly_budget, p.research) == (72007, 6001, 720)


def test_missing_costs_are_not_zero_or_a_spendable_balance():
    save = campaign()
    before = save.documents['test.bcs'].render()
    p = project_budget(save.nation(0), context=budget_context(save, save.nation(0)))
    assert p.naval_aircraft is None and p.extra_training is None
    assert p.monthly_balance is None and p.incomplete
    assert p.total_expenses == p.maintenance + p.construction + p.research
    assert before == save.documents['test.bcs'].render()
    assert not save.modified


def test_context_flags_missing_infrastructure_costs():
    save = campaign(nation='DockBuilding=15\n')
    sections = save.documents['test.bcs'].sections
    sub = next(s for s in sections if s.name == 'Nation0Submarines')
    sub.lines += ['Sub0InPlay=0\n', 'Sub0Sunk=0\n', 'Sub0Fate=\n']
    c = budget_context(save, save.nation(0))
    assert c.construction_notes == ('dock expansion', 'submarines')
    sub.set('Sub0Sunk', 1)
    assert budget_context(save, save.nation(0)).construction_notes == ('dock expansion',)


@pytest.mark.parametrize("raw,kind,radar,status,expected", [
    (35, "DD", 0, 0, 35), (35, "DD", 0, 1, 18), (35, "DD", 0, 2, 7),
    (35, "DD", 2, 0, 37), (35, "DD", 2, 1, 18), (35, "DD", 2, 2, 7),
    (112, "CL", 2, 0, 116), (112, "CL", 2, 1, 58),
    (80, "CL", 2, 2, 17), (255, "CV", 2, 1, 130),
])
def test_observed_ship_maintenance(raw, kind, radar, status, expected):
    save = campaign([dict(Maintenance=raw, ShipType=kind, SearchRadarClass=radar, Status=status)])
    assert project_budget(save.nation(0)).maintenance == expected


def test_intelligence_levels_are_additive_and_independent_of_fleet_size():
    save = campaign(extra="[Nation1]\nName=A\nIntelligenceSpending=1\n[Nation2]\nName=B\nIntelligenceSpending=2\n[Nation3]\nName=C\nIntelligenceSpending=3\n")
    for fleet in [2, 8, 12]:
        next(s for s in save.documents['test.bcs'].sections if s.name == 'General').set('FleetSize', fleet)
        assert budget_context(save, save.nation(0)).intelligence == 480
    save.nation(1).section.set('IntelligenceSpending', 9)
    assert budget_context(save, save.nation(0)).intelligence is None


def test_battery_construction_and_unknown_submarine_cost():
    save = campaign([{'MonthlyCost': 1876, 'UnderConstruction': 1},
                     {'MonthlyCost': 1883, 'UnderConstruction': 1}])
    sections = {s.name: s for s in save.documents['test.bcs'].sections}
    fort = sections['Nation0CoastalArtillery']
    for key, value in {'Ship0Name': 'Battery 39', 'Ship0InPlay': 0,
                       'Ship0MonthlyCost': 2400, 'Ship0Status': 0,
                       'Ship1InPlay': 1, 'Ship1MonthlyCost': 999,
                       'Ship2InPlay': 0, 'Ship2Fate': 'Scrapped', 'Ship2MonthlyCost': 999}.items():
        fort.set(key, value)
    sub = sections['Nation0Submarines']
    sub.set('Sub0InPlay', 0)
    sub.set('Sub0RemainingBuildTime', 18)
    before = save.documents['test.bcs'].render()
    context = budget_context(save, save.nation(0))
    assert project_budget(save.nation(0), context=context).construction == 6159
    assert context.construction_notes == ('submarines',)
    assert save.documents['test.bcs'].render() == before
    # When a format supplies an explicit cost, include it without guessing.
    sub.set('Sub0MonthlyCost', 295)
    context = budget_context(save, save.nation(0))
    assert project_budget(save.nation(0), context=context).construction == 6454
    assert not context.construction_notes
