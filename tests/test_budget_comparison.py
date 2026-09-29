from pathlib import Path

import pytest

from privateer.document import TextDocument
from privateer.economy import BudgetAssumptions, BudgetContext, budget_context, project_budget
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


def test_all_budget_fields_are_numeric_estimates_without_save_mutation():
    save = campaign()
    before = save.documents['test.bcs'].render()
    p = project_budget(save.nation(0), context=budget_context(save, save.nation(0)))
    assert p.naval_aircraft == 0 and p.extra_training == 0
    assert p.monthly_balance == p.monthly_budget - p.total_expenses and p.incomplete
    for key in ('yearly_budget', 'monthly_budget', 'maintenance', 'construction',
                'naval_aircraft', 'research', 'extra_training', 'intelligence',
                'total_expenses', 'monthly_balance', 'funds', 'all_active_maintenance'):
        assert isinstance(getattr(p, key), int)
    assert p.total_expenses == p.maintenance + p.construction + p.research
    assert before == save.documents['test.bcs'].render()
    assert not save.modified


def test_context_discloses_fallback_costs_and_excludes_sunk_submarines():
    save = campaign(nation='DockBuilding=15\n')
    sections = save.documents['test.bcs'].sections
    sub = next(s for s in sections if s.name == 'Nation0Submarines')
    sub.lines += ['Sub0InPlay=0\n', 'Sub0Sunk=0\n', 'Sub0Fate=\n']
    c = budget_context(save, save.nation(0))
    assert c.additional_construction == 324 + 295
    assert any('fallback' in note for note in c.estimate_notes)
    sub.set('Sub0Sunk', 1)
    assert budget_context(save, save.nation(0)).additional_construction == 324


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
    assert project_budget(save.nation(0), context=context).construction == 6454
    assert any('missing MonthlyCost uses 295' in note for note in context.estimate_notes)
    assert save.documents['test.bcs'].render() == before
    # When a format supplies an explicit cost, include it without guessing.
    sub.set('Sub0MonthlyCost', 295)
    context = budget_context(save, save.nation(0))
    assert project_budget(save.nation(0), context=context).construction == 6454
    assert not context.construction_notes


def test_reference_aircraft_training_and_infrastructure_do_not_double_count():
    save = campaign([{'Maintenance': 3424}], nation='TorpedoWarfare=1\nDamageControl=1\nNavalAcademy=1\nPendingGunneryTraining=1\n',
        extra='[AirUnits]\nAU0Nation=0\nAU0AircraftNumber=1956\nAU0AircraftTypeId=-1\nAU1Nation=1\nAU1AircraftNumber=999\n[AircraftTypes]\nAT0Nation=0\nAT0AvailableAircraft=233\n')
    sections = {s.name: s for s in save.documents['test.bcs'].sections}
    fort = sections['Nation0CoastalArtillery']
    for i, (kind, raw) in enumerate([('4 in Coastal Battery', 6), ('Airbase100', 126), ('MTB squadron', 20)]):
        for key, value in {'Classname': kind, 'Maintenance': raw, 'InPlay': 1}.items():
            fort.set(f'Ship{i}{key}', value)
    sub = sections['Nation0Submarines']
    sub.set('Sub0InPlay', 1)
    sub.set('Sub0Sunk', 0)
    context = budget_context(save, save.nation(0))
    p = project_budget(save.nation(0), context=context)
    assert p.maintenance == 3424 + 4 + 94 + 20 + 55
    assert p.naval_aircraft == 18194
    assert p.extra_training == 1436
    assert p.total_expenses == sum((p.maintenance, p.construction, p.naval_aircraft, p.research, p.extra_training, p.intelligence))
    assert not save.modified


def test_adjustable_fallbacks_and_missing_income_are_explicit():
    save = campaign(extra='[AirUnits]\nAU0Nation=0\nAU0AircraftNumber=10\n', nation='NavalAcademy=1\n')
    a = BudgetAssumptions(aircraft_rate=2, academy_cost=99, income_factor='1.5')
    c = budget_context(save, save.nation(0), a)
    p = project_budget(save.nation(0), context=c, assumptions=a)
    assert (p.naval_aircraft, p.extra_training, p.yearly_budget) == (20, 99, 129600)
    p = project_budget(save.nation(0))
    assert p.yearly_budget == 0 and p.intelligence == 0
    assert any('0 fallback' in note for note in p.notes)
    for bad in ['NaN', 'Infinity', '-1']:
        with pytest.raises(ValueError):
            BudgetAssumptions(aircraft_rate=bad)


def test_all_active_estimate_is_separate_from_expenses():
    save = campaign([{'Maintenance': 100, 'Status': 1}])
    p = project_budget(save.nation(0), context=BudgetContext(8, 0))
    assert p.maintenance == 50
    assert p.all_active_maintenance == 100
    assert p.total_expenses == p.maintenance + p.research
